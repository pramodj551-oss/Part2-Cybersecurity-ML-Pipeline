"""STEP 18 — Automated Hyperparameter Optimization.

Runs a small, deterministic RandomizedSearchCV experiment over the strongest
configured regression models. Preprocessing is kept inside the sklearn
Pipeline so every CV fold learns transformations from its training rows only.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.model_selection import RandomizedSearchCV, KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import (
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    RANDOM_STATE,
    TARGET_COLUMN,
    OUTPUT_DIR,
    CV_FOLDS,
)


class HyperparameterOptimization:
    """Perform reproducible, leakage-safe hyperparameter optimization."""

    def __init__(self, random_state: int = RANDOM_STATE, cv_folds: int = CV_FOLDS) -> None:
        self.random_state = random_state
        self.cv_folds = cv_folds

    def _preprocessor(self, frame: pd.DataFrame) -> ColumnTransformer:
        numeric = [c for c in NUMERICAL_FEATURES if c in frame.columns]
        categorical = [c for c in CATEGORICAL_FEATURES if c in frame.columns]
        return ColumnTransformer(
            [
                ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric),
                ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), categorical),
            ],
            remainder="drop",
        )

    def _search_spaces(self) -> dict[str, tuple[object, dict[str, list[object]]]]:
        return {
            "Random Forest": (
                RandomForestRegressor(random_state=self.random_state, n_jobs=-1),
                {
                    "model__n_estimators": [100, 150, 200],
                    "model__max_depth": [None, 6, 10, 14],
                    "model__min_samples_leaf": [1, 2, 4],
                    "model__min_samples_split": [2, 5, 10],
                },
            ),
            "Gradient Boosting": (
                GradientBoostingRegressor(random_state=self.random_state),
                {
                    "model__n_estimators": [100, 150, 200],
                    "model__learning_rate": [0.03, 0.05, 0.1],
                    "model__max_depth": [2, 3, 4],
                    "model__min_samples_leaf": [1, 2, 4],
                },
            ),
        }

    def run(self, dataframe: pd.DataFrame, output_dir: str | Path = OUTPUT_DIR) -> pd.DataFrame:
        if TARGET_COLUMN not in dataframe.columns:
            raise ValueError(f"Target column '{TARGET_COLUMN}' not found.")
        if len(dataframe) < self.cv_folds:
            raise ValueError("Not enough rows for configured cross-validation folds.")

        allowed = [c for c in NUMERICAL_FEATURES + CATEGORICAL_FEATURES if c in dataframe.columns]
        X = dataframe[allowed].copy()
        y = pd.to_numeric(dataframe[TARGET_COLUMN], errors="coerce")
        if y.isna().any():
            raise ValueError("Target contains non-numeric or missing values.")

        splitter = KFold(n_splits=self.cv_folds, shuffle=True, random_state=self.random_state)
        rows: list[dict[str, object]] = []
        for name, (estimator, params) in self._search_spaces().items():
            pipeline = Pipeline([
                ("preprocessor", self._preprocessor(X)),
                ("model", estimator),
            ])
            search = RandomizedSearchCV(
                pipeline,
                param_distributions=params,
                n_iter=4,
                scoring="r2",
                cv=splitter,
                random_state=self.random_state,
                n_jobs=-1,
                refit=True,
            )
            search.fit(X, y)
            rows.append({
                "model": name,
                "best_cv_r2": float(search.best_score_),
                "best_params": json.dumps(search.best_params_, sort_keys=True),
                "cv_folds": self.cv_folds,
                "n_iter": 4,
            })

        results = pd.DataFrame(rows).sort_values("best_cv_r2", ascending=False).reset_index(drop=True)
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        results.to_csv(out / "hyperparameter_optimization.csv", index=False)
        (out / "hyperparameter_optimization_report.json").write_text(
            json.dumps({
                "step": 18,
                "method": "RandomizedSearchCV",
                "scoring": "r2",
                "cv_folds": self.cv_folds,
                "n_iter_per_model": 4,
                "best_model": results.iloc[0].to_dict(),
                "results": results.to_dict(orient="records"),
            }, indent=2),
            encoding="utf-8",
        )
        return results


if __name__ == "__main__":
    from src.data_loader import DataLoader
    print(HyperparameterOptimization().run(DataLoader().run()).to_string(index=False))
