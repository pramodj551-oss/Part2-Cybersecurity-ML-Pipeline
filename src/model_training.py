"""Model training for the cybersecurity severity-score regression pipeline."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.feature_selection import VarianceThreshold
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold
from sklearn.tree import DecisionTreeRegressor

from src.config import (
    BEST_MODEL_FILE,
    CATEGORICAL_FEATURES,
    CV_FOLDS,
    CV_SCORING,
    FEATURE_SELECTION_TOP_N,
    GRADIENT_BOOSTING_MAX_DEPTH,
    GRADIENT_BOOSTING_N_ESTIMATORS,
    MAX_DEPTH,
    METRICS_FILE,
    MIN_SAMPLES_LEAF,
    MIN_SAMPLES_SPLIT,
    MODEL_METADATA_FILE,
    N_ESTIMATORS,
    NUMERICAL_FEATURES,
    OUTPUT_DIR,
    RANDOM_STATE,
    TARGET_COLUMN,
    VARIANCE_THRESHOLD,
)
from src.logger import log_success
from src.preprocessing import Preprocessor
from src.utils import save_model


class ModelTrainer:
    """Train regression models with leakage-safe cross-validation."""

    def __init__(self) -> None:
        self.models = {
            "Linear Regression": LinearRegression(),
            "Decision Tree": DecisionTreeRegressor(
                random_state=RANDOM_STATE,
                max_depth=MAX_DEPTH,
                min_samples_split=MIN_SAMPLES_SPLIT,
                min_samples_leaf=MIN_SAMPLES_LEAF,
            ),
            "Random Forest": RandomForestRegressor(
                n_estimators=N_ESTIMATORS,
                random_state=RANDOM_STATE,
                max_depth=MAX_DEPTH,
                min_samples_split=MIN_SAMPLES_SPLIT,
                min_samples_leaf=MIN_SAMPLES_LEAF,
                n_jobs=-1,
            ),
            "Gradient Boosting": GradientBoostingRegressor(
                random_state=RANDOM_STATE,
                n_estimators=GRADIENT_BOOSTING_N_ESTIMATORS,
                max_depth=GRADIENT_BOOSTING_MAX_DEPTH,
            ),
        }
        self.best_model_name = None
        self.best_model = None
        self.training_results = []
        self.selected_features: list[str] = []
        self.cv_is_fold_safe = False

    def list_models(self):
        return list(self.models)

    def get_model(self, model_name):
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")
        return self.models[model_name]

    def train_model(self, model_name, X_train, y_train):
        model = clone(self.get_model(model_name))
        model.fit(X_train, y_train)
        return model

    @staticmethod
    def _fold_transform(train_df: pd.DataFrame, validation_df: pd.DataFrame):
        """Fit preprocessing only on a fold's training rows."""
        preprocessor = Preprocessor()
        train_processed = train_df.copy()
        validation_processed = validation_df.copy()

        # The caller supplies the cleaned training frame.  Imputation and
        # one-hot encoding are still fitted independently inside this fold.
        train_processed = preprocessor.handle_missing_values(train_processed)
        validation_processed = preprocessor.transform_missing_values(validation_processed)

        X_train, y_train, fitted_preprocessor = preprocessor.fit_transform(train_processed)
        X_validation, y_validation = preprocessor.transform(validation_processed, fitted_preprocessor)
        return X_train, y_train, X_validation, y_validation, fitted_preprocessor

    @staticmethod
    def _select_fold_features(X_train, y_train, X_validation, feature_names, top_n):
        """Fit variance filtering and feature importance only on fold-train."""
        variance_selector = VarianceThreshold(threshold=VARIANCE_THRESHOLD)
        X_train_filtered = variance_selector.fit_transform(X_train)
        X_validation_filtered = variance_selector.transform(X_validation)
        mask = variance_selector.get_support()
        filtered_names = [name for name, keep in zip(feature_names, mask) if keep]

        if not filtered_names:
            raise ValueError("Variance filtering removed all features in a CV fold.")

        selector = RandomForestRegressor(
            n_estimators=N_ESTIMATORS,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )
        selector.fit(X_train_filtered, y_train)
        importance = pd.DataFrame(
            {"feature": filtered_names, "importance": selector.feature_importances_}
        ).sort_values("importance", ascending=False)
        selected_names = importance.head(top_n)["feature"].tolist()
        selected_indices = [filtered_names.index(name) for name in selected_names]
        return (
            X_train_filtered[:, selected_indices],
            X_validation_filtered[:, selected_indices],
            selected_names,
        )

    def fold_safe_cv_scores(self, raw_train_df: pd.DataFrame, top_n: int = FEATURE_SELECTION_TOP_N):
        """Return leakage-safe CV R2 scores for every configured model.

        Every fold independently fits imputers, encoders/scalers, variance
        filtering, feature selection, and the estimator using fold-training
        rows only. Validation rows are transformed, never fitted.
        """
        if TARGET_COLUMN not in raw_train_df.columns:
            raise ValueError(f"Raw training data must contain '{TARGET_COLUMN}'.")
        if len(raw_train_df) < CV_FOLDS:
            raise ValueError("Training data must contain at least CV_FOLDS rows.")

        splitter = KFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
        scores = {name: [] for name in self.list_models()}

        X_raw = raw_train_df.drop(columns=[TARGET_COLUMN]).reset_index(drop=True)
        y_raw = raw_train_df[TARGET_COLUMN].reset_index(drop=True)

        # Keep only the configured prediction columns plus the target so that
        # fold preprocessing cannot accidentally consume excluded post-incident
        # columns or identifiers.
        allowed = [c for c in NUMERICAL_FEATURES + CATEGORICAL_FEATURES if c in X_raw.columns]
        X_raw = X_raw[allowed]
        fold_df = X_raw.copy()
        fold_df[TARGET_COLUMN] = y_raw

        for train_idx, validation_idx in splitter.split(fold_df):
            fold_train = fold_df.iloc[train_idx].copy()
            fold_validation = fold_df.iloc[validation_idx].copy()
            X_fold, y_fold, X_val, y_val, fitted_preprocessor = self._fold_transform(
                fold_train, fold_validation
            )
            feature_names = list(fitted_preprocessor.get_feature_names_out())
            X_fold, X_val, _ = self._select_fold_features(
                X_fold, y_fold, X_val, feature_names, top_n
            )

            for name in self.list_models():
                model = clone(self.get_model(name))
                model.fit(X_fold, y_fold)
                predictions = model.predict(X_val)
                if CV_SCORING == "r2":
                    score = r2_score(y_val, predictions)
                else:
                    raise ValueError(f"Unsupported CV scoring: {CV_SCORING}")
                scores[name].append(float(score))

        self.cv_is_fold_safe = True
        return scores

    def evaluate_model(self, model_name, model, X_test, y_test, cv_scores=None):
        predictions = model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        rmse = mean_squared_error(y_test, predictions) ** 0.5
        r2 = r2_score(y_test, predictions)
        if cv_scores is None:
            raise ValueError("Fold-safe CV scores are required for model evaluation.")
        return {
            "Model": model_name,
            "MAE": round(mae, 4),
            "RMSE": round(rmse, 4),
            "R2 Score": round(r2, 4),
            "CV Mean": round(float(np.mean(cv_scores)), 4),
            "CV Std": round(float(np.std(cv_scores)), 4),
            "Model Object": model,
        }

    def train_all_models(self, X_train, y_train, X_test, y_test, raw_train_df=None, top_n=FEATURE_SELECTION_TOP_N):
        self.training_results = []
        if raw_train_df is None:
            raise ValueError("raw_train_df is required for leakage-safe cross-validation.")

        cv_scores = self.fold_safe_cv_scores(raw_train_df, top_n=top_n)
        for name in self.list_models():
            model = self.train_model(name, X_train, y_train)
            self.training_results.append(
                self.evaluate_model(name, model, X_test, y_test, cv_scores[name])
            )
        return pd.DataFrame(self.training_results)

    def select_best_model(self, results_df):
        if results_df.empty:
            raise ValueError("No model results available.")
        ranked = results_df.sort_values(
            ["CV Mean", "CV Std", "RMSE"],
            ascending=[False, True, True],
        ).reset_index(drop=True)
        best = ranked.iloc[0]
        self.best_model_name = best["Model"]
        self.best_model = best["Model Object"]
        return self.best_model

    def model_comparison_report(self, results_df):
        return results_df.drop(columns=["Model Object"], errors="ignore").sort_values(
            "CV Mean", ascending=False
        ).reset_index(drop=True)

    def save_comparison_report(self, report):
        report.to_csv(OUTPUT_DIR / "model_comparison.csv", index=False)

    def save_best_model(self):
        if self.best_model is None:
            raise ValueError("No trained model available.")
        save_model(self.best_model, BEST_MODEL_FILE)

    def save_metrics(self, report):
        with open(METRICS_FILE, "w", encoding="utf-8") as file:
            json.dump(report.to_dict(orient="records"), file, indent=4)

    def save_model_metadata(self, report, selected_features=None):
        if report.empty:
            raise ValueError("Cannot save metadata from an empty report.")
        best = report.iloc[0]
        metadata = {
            "model_name": self.best_model_name,
            "training_timestamp": datetime.now(timezone.utc).isoformat(),
            "r2_score": float(best["R2 Score"]),
            "rmse": float(best["RMSE"]),
            "mae": float(best["MAE"]),
            "cv_mean": float(best["CV Mean"]),
            "cv_std": float(best["CV Std"]),
            "cv_method": "fold_safe_preprocessing_and_feature_selection",
            "cv_folds": CV_FOLDS,
            "selected_feature_names": list(selected_features or self.selected_features),
            "python_version": sys.version.split()[0],
        }
        with open(MODEL_METADATA_FILE, "w", encoding="utf-8") as file:
            json.dump(metadata, file, indent=4)

    def run(self, X_train, y_train, X_test, y_test, selected_features=None, raw_train_df=None, top_n=FEATURE_SELECTION_TOP_N):
        self.selected_features = list(selected_features or [])
        results = self.train_all_models(
            X_train,
            y_train,
            X_test,
            y_test,
            raw_train_df=raw_train_df,
            top_n=top_n,
        )
        self.select_best_model(results)
        report = self.model_comparison_report(results)
        self.save_comparison_report(report)
        self.save_best_model()
        self.save_metrics(report)
        self.save_model_metadata(report, self.selected_features)
        log_success("Model training pipeline completed successfully with fold-safe CV.")
        return self.best_model, report
