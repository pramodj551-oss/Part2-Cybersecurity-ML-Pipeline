"""STEP 22 runtime entry point: retraining, comparison, promotion, registry."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from src.config import (
    FEATURE_SELECTION_TOP_N,
    RAW_DATA_FILE,
    TARGET_COLUMN,
    MODEL_METADATA_FILE,
    MODEL_DIR,
    CV_FOLDS,
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
)
from src.feature_selection import FeatureSelector
from src.model_lifecycle import (
    RETRAINING_DECISION_FILE,
    compare_models,
    load_json,
    promote_candidate,
    retraining_required,
    save_comparison,
    write_registry,
)
from src.model_training import ModelTrainer
from src.preprocessing import Preprocessor
from src.utils import save_model

CANDIDATE_MODEL_FILE = MODEL_DIR / "candidate_model.pkl"


def main() -> int:
    drift_report = load_json(Path("outputs/drift_report.json"))
    current_metadata = load_json(MODEL_METADATA_FILE)
    required, reasons = retraining_required(drift_report)

    decision = {
        "step": 22,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "retraining_required": required,
        "reasons": reasons,
        "trigger_source": "STEP 21 drift report",
        "promotion_policy": "candidate CV Mean must strictly exceed current promoted model CV Mean",
    }

    if not required:
        decision["action"] = "no_retraining"
        decision["promotion"] = "not_applicable"
        RETRAINING_DECISION_FILE.write_text(json.dumps(decision, indent=2), encoding="utf-8")
        write_registry(current_metadata, decision, "active")
        print("STEP 22: no retraining required; current model remains active.")
        return 0

    df = pd.read_csv(RAW_DATA_FILE)
    preprocessor = Preprocessor()
    X_train, X_test, y_train, y_test, fitted_preprocessor = preprocessor.run(df)
    raw_train_df = preprocessor.train_df_before_imputation_
    if raw_train_df is None:
        raise RuntimeError("Fold-safe retraining requires the pre-imputation training split.")

    selector = FeatureSelector()
    names = list(fitted_preprocessor.get_feature_names_out())
    X_train_selected, selected_features, _ = selector.run(
        X_train, y_train, feature_names=names, top_n=FEATURE_SELECTION_TOP_N
    )
    X_test_selected = X_test[:, selector.selected_feature_indices_]

    trainer = ModelTrainer()
    results = trainer.train_all_models(
        X_train_selected,
        y_train,
        X_test_selected,
        y_test,
        raw_train_df=raw_train_df,
        top_n=len(selected_features),
    )
    trainer.select_best_model(results)
    candidate_name = trainer.best_model_name
    candidate_report = trainer.model_comparison_report(results)

    save_model(trainer.best_model, CANDIDATE_MODEL_FILE)
    comparison = compare_models(current_metadata, candidate_name, candidate_report)
    save_comparison(comparison)

    decision.update(
        {
            "action": "retrain_candidate",
            "candidate_model": candidate_name,
            "candidate_cv_mean": comparison["candidate_cv_mean"],
            "current_cv_mean": comparison["current_cv_mean"],
            "cv_improvement": comparison["cv_improvement"],
            "promotion": "approved" if comparison["promotion_eligible"] else "rejected",
        }
    )

    if comparison["promotion_eligible"]:
        candidate_row = candidate_report.loc[candidate_report["Model"] == candidate_name].iloc[0]
        candidate_metadata = {
            "model_name": candidate_name,
            "training_timestamp": datetime.now(timezone.utc).isoformat(),
            "r2_score": float(candidate_row["R2 Score"]),
            "rmse": float(candidate_row["RMSE"]),
            "mae": float(candidate_row["MAE"]),
            "cv_mean": float(candidate_row["CV Mean"]),
            "cv_std": float(candidate_row["CV Std"]),
            "cv_method": "fold_safe_preprocessing_and_feature_selection",
            "cv_folds": CV_FOLDS,
            "prediction_features": [
                c for c in NUMERICAL_FEATURES + CATEGORICAL_FEATURES if c in df.columns
            ],
            "target_column": TARGET_COLUMN,
        }
        promote_candidate(CANDIDATE_MODEL_FILE, candidate_metadata, selected_features)
        registry_status = "promoted"
    else:
        registry_status = "active"

    RETRAINING_DECISION_FILE.write_text(json.dumps(decision, indent=2), encoding="utf-8")
    registry_metadata = load_json(MODEL_METADATA_FILE) if registry_status == "promoted" else current_metadata
    write_registry(registry_metadata, decision, registry_status)
    print(f"STEP 22 completed: {decision['promotion']} ({candidate_name}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
