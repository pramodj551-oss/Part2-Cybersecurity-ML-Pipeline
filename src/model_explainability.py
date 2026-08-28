"""STEP 20: model explainability and feature-importance analysis."""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error

from src.config import BEST_MODEL_FILE, FEATURE_COLUMNS_FILE, MODEL_METADATA_FILE, OUTPUT_DIR, PREPROCESSOR_FILE, TARGET_COLUMN, TEST_DATA_FILE


class ModelExplainability:
    """Generate global and local explanations from persisted model artifacts."""

    def __init__(self, output_dir: str | Path = OUTPUT_DIR) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _selected_feature_names() -> list[str]:
        metadata = json.loads(MODEL_METADATA_FILE.read_text(encoding="utf-8"))
        names = metadata.get("selected_feature_names", [])
        if not names:
            raise ValueError("model_metadata.json does not contain selected_feature_names.")
        return [str(name) for name in names]

    @staticmethod
    def _load_test_data() -> tuple[pd.DataFrame, pd.Series]:
        df = pd.read_csv(TEST_DATA_FILE)
        if TARGET_COLUMN not in df.columns:
            raise ValueError(f"Test data must contain '{TARGET_COLUMN}'.")
        return df.drop(columns=[TARGET_COLUMN]), df[TARGET_COLUMN]

    @staticmethod
    def _select_columns(X: np.ndarray, all_names: list[str], selected_names: list[str]) -> np.ndarray:
        positions = {name: idx for idx, name in enumerate(all_names)}
        missing = [name for name in selected_names if name not in positions]
        if missing:
            raise ValueError(f"Selected features missing from preprocessor output: {missing}")
        return X[:, [positions[name] for name in selected_names]]

    def run(self) -> dict:
        model = joblib.load(BEST_MODEL_FILE)
        preprocessor = joblib.load(PREPROCESSOR_FILE)
        X_raw, y = self._load_test_data()
        X_transformed = preprocessor.transform(X_raw)
        all_names = list(preprocessor.get_feature_names_out())
        selected_names = self._selected_feature_names()
        X = self._select_columns(X_transformed, all_names, selected_names)

        baseline = model.predict(X)
        baseline_mae = mean_absolute_error(y, baseline)
        permutation = permutation_importance(
            model, X, y, scoring="neg_mean_absolute_error", n_repeats=10,
            random_state=42, n_jobs=-1,
        )
        native = getattr(model, "feature_importances_", None)
        if native is None:
            native = np.abs(getattr(model, "coef_", np.zeros(X.shape[1]))).ravel()
        native = np.asarray(native, dtype=float)
        if native.shape[0] != len(selected_names):
            native = np.zeros(len(selected_names), dtype=float)

        importance = pd.DataFrame({
            "feature": selected_names,
            "native_importance": native,
            "permutation_importance_mean": permutation.importances_mean,
            "permutation_importance_std": permutation.importances_std,
        })
        importance["importance_rank"] = importance["permutation_importance_mean"].rank(
            method="dense", ascending=False
        ).astype(int)
        importance = importance.sort_values(
            ["permutation_importance_mean", "native_importance"], ascending=[False, False]
        ).reset_index(drop=True)
        importance.to_csv(self.output_dir / "explainability_feature_importance.csv", index=False)

        # Local explanation: replace one feature at a time by its held-out median.
        reference_idx = 0
        reference = X[reference_idx].copy()
        reference_prediction = float(baseline[reference_idx])
        medians = np.median(X, axis=0)
        local_rows = []
        for idx, feature in enumerate(selected_names):
            perturbed = reference.copy()
            perturbed[idx] = medians[idx]
            changed = float(model.predict(perturbed.reshape(1, -1))[0])
            local_rows.append({
                "feature": feature,
                "reference_prediction": reference_prediction,
                "prediction_after_median_replacement": changed,
                "prediction_change": changed - reference_prediction,
                "absolute_change": abs(changed - reference_prediction),
            })
        local = pd.DataFrame(local_rows).sort_values("absolute_change", ascending=False).reset_index(drop=True)
        local.to_csv(self.output_dir / "local_prediction_explanation.csv", index=False)

        report = {
            "step": 20,
            "model_explainability": {
                "model_type": type(model).__name__,
                "test_rows": int(len(y)),
                "feature_count": int(len(selected_names)),
                "baseline_mae": float(baseline_mae),
                "importance_method": "native_importance_plus_10_repeat_permutation_importance",
                "local_explanation_method": "median_replacement_sensitivity",
            },
            "top_features": importance.head(10).to_dict(orient="records"),
            "reference_prediction": reference_prediction,
        }
        (self.output_dir / "model_explainability_report.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )
        return report


if __name__ == "__main__":
    print(json.dumps(ModelExplainability().run(), indent=2))
