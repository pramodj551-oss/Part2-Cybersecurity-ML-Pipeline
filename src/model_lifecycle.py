"""STEP 22: automated retraining decision and safe model promotion."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.config import (
    BEST_MODEL_FILE,
    MODEL_METADATA_FILE,
    OUTPUT_DIR,
    PREPROCESSOR_FILE,
    RANDOM_STATE,
    TARGET_COLUMN,
)

RETRAINING_DECISION_FILE = OUTPUT_DIR / "retraining_decision.json"
MODEL_REGISTRY_FILE = OUTPUT_DIR / "model_registry.json"
LIFECYCLE_COMPARISON_FILE = OUTPUT_DIR / "model_lifecycle_comparison.csv"
MIN_CV_IMPROVEMENT = 0.0


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Required JSON artifact not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def retraining_required(drift_report: dict, threshold: float = 0.20) -> tuple[bool, list[str]]:
    """Return whether drift policy requires a retraining attempt."""
    reasons: list[str] = []
    if not 0 < threshold <= 1:
        raise ValueError("threshold must be in (0, 1].")
    feature_count = int(drift_report.get("features_with_drift", 0))
    prediction_drift = bool(drift_report.get("prediction_drift", {}).get("drift_detected", False))
    if feature_count > 0:
        reasons.append(f"{feature_count} monitored feature(s) exceeded drift threshold")
    if prediction_drift:
        reasons.append("prediction drift exceeded threshold")
    return bool(reasons), reasons


def compare_models(current_metadata: dict, candidate_name: str, candidate_report: pd.DataFrame) -> dict:
    """Compare candidate against the currently promoted model using CV evidence."""
    if candidate_report.empty:
        raise ValueError("Candidate report cannot be empty.")
    row = candidate_report.loc[candidate_report["Model"] == candidate_name]
    if row.empty:
        raise ValueError(f"Candidate model '{candidate_name}' not found in report.")
    candidate = row.iloc[0]
    current_cv = float(current_metadata.get("cv_mean", float("nan")))
    candidate_cv = float(candidate["CV Mean"])
    if pd.isna(current_cv):
        raise ValueError("Current model metadata must contain numeric cv_mean.")
    improvement = candidate_cv - current_cv
    return {
        "current_model": current_metadata.get("model_name"),
        "current_cv_mean": current_cv,
        "candidate_model": candidate_name,
        "candidate_cv_mean": candidate_cv,
        "cv_improvement": float(improvement),
        "candidate_test_r2": float(candidate["R2 Score"]),
        "candidate_test_rmse": float(candidate["RMSE"]),
        "candidate_test_mae": float(candidate["MAE"]),
        "promotion_eligible": bool(improvement > MIN_CV_IMPROVEMENT),
    }


def promote_candidate(model_path: Path, metadata: dict, selected_features: list[str]) -> None:
    """Atomically replace the promoted model and metadata after policy approval."""
    if not model_path.exists():
        raise FileNotFoundError(f"Candidate model not found: {model_path}")
    BEST_MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_model = BEST_MODEL_FILE.with_suffix(".candidate.pkl")
    shutil.copy2(model_path, temp_model)
    temp_model.replace(BEST_MODEL_FILE)

    promoted = dict(metadata)
    promoted.update(
        {
            "lifecycle_status": "promoted",
            "promotion_timestamp": datetime.now(timezone.utc).isoformat(),
            "selected_feature_names": list(selected_features),
            "random_state": RANDOM_STATE,
        }
    )
    MODEL_METADATA_FILE.write_text(json.dumps(promoted, indent=2), encoding="utf-8")


def write_registry(current_metadata: dict, decision: dict, status: str) -> dict:
    """Write an auditable model registry snapshot without storing model binaries."""
    registry = {
        "registry_version": 1,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "target_column": TARGET_COLUMN,
        "model": {
            "name": current_metadata.get("model_name"),
            "status": status,
            "cv_mean": current_metadata.get("cv_mean"),
            "cv_std": current_metadata.get("cv_std"),
            "r2_score": current_metadata.get("r2_score"),
            "rmse": current_metadata.get("rmse"),
            "mae": current_metadata.get("mae"),
            "training_timestamp": current_metadata.get("training_timestamp"),
        },
        "decision": decision,
        "artifacts": {
            "model": str(BEST_MODEL_FILE),
            "preprocessor": str(PREPROCESSOR_FILE),
            "metadata": str(MODEL_METADATA_FILE),
        },
    }
    MODEL_REGISTRY_FILE.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    return registry


def save_comparison(comparison: dict) -> None:
    pd.DataFrame([comparison]).to_csv(LIFECYCLE_COMPARISON_FILE, index=False)
