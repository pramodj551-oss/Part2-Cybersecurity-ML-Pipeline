"""Model training for the cybersecurity severity-score regression pipeline."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeRegressor

from src.config import (BEST_MODEL_FILE, CV_FOLDS, MAX_DEPTH, METRICS_FILE, MIN_SAMPLES_LEAF,
                        MIN_SAMPLES_SPLIT, MODEL_METADATA_FILE, N_ESTIMATORS, OUTPUT_DIR, RANDOM_STATE)
from src.logger import logger, log_section, log_success
from src.utils import save_model


class ModelTrainer:
    def __init__(self) -> None:
        self.models = {
            "Linear Regression": LinearRegression(),
            "Decision Tree": DecisionTreeRegressor(random_state=RANDOM_STATE, max_depth=MAX_DEPTH, min_samples_split=MIN_SAMPLES_SPLIT, min_samples_leaf=MIN_SAMPLES_LEAF),
            "Random Forest": RandomForestRegressor(n_estimators=N_ESTIMATORS, random_state=RANDOM_STATE, max_depth=MAX_DEPTH, min_samples_split=MIN_SAMPLES_SPLIT, min_samples_leaf=MIN_SAMPLES_LEAF, n_jobs=-1),
            "Gradient Boosting": GradientBoostingRegressor(random_state=RANDOM_STATE, n_estimators=150, max_depth=3),
        }
        self.best_model_name = None
        self.best_model = None
        self.training_results = []
        self.selected_features: list[str] = []

    def list_models(self):
        return list(self.models)

    def get_model(self, model_name):
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")
        return self.models[model_name]

    def train_model(self, model_name, X_train, y_train):
        model = self.get_model(model_name)
        model.fit(X_train, y_train)
        return model

    def evaluate_model(self, model_name, model, X_train, y_train, X_test, y_test):
        predictions = model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        rmse = mean_squared_error(y_test, predictions) ** 0.5
        r2 = r2_score(y_test, predictions)
        cv_scores = cross_val_score(model, X_train, y_train, cv=CV_FOLDS, scoring="r2", n_jobs=-1)
        return {"Model": model_name, "MAE": round(mae, 4), "RMSE": round(rmse, 4), "R2 Score": round(r2, 4), "CV Mean": round(cv_scores.mean(), 4), "CV Std": round(cv_scores.std(), 4), "Model Object": model}

    def train_all_models(self, X_train, y_train, X_test, y_test):
        self.training_results = []
        for name in self.list_models():
            model = self.train_model(name, X_train, y_train)
            self.training_results.append(self.evaluate_model(name, model, X_train, y_train, X_test, y_test))
        return pd.DataFrame(self.training_results)

    def select_best_model(self, results_df):
        if results_df.empty:
            raise ValueError("No model results available.")
        ranked = results_df.sort_values(["CV Mean", "CV Std", "RMSE"], ascending=[False, True, True]).reset_index(drop=True)
        best = ranked.iloc[0]
        self.best_model_name = best["Model"]
        self.best_model = best["Model Object"]
        return self.best_model

    def model_comparison_report(self, results_df):
        return results_df.drop(columns=["Model Object"], errors="ignore").sort_values("CV Mean", ascending=False).reset_index(drop=True)

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
        metadata = {"model_name": self.best_model_name, "training_timestamp": datetime.now(timezone.utc).isoformat(),
                    "r2_score": float(best["R2 Score"]), "rmse": float(best["RMSE"]), "mae": float(best["MAE"]),
                    "cv_mean": float(best["CV Mean"]), "cv_std": float(best["CV Std"]),
                    "selected_feature_names": list(selected_features or self.selected_features),
                    "python_version": sys.version.split()[0]}
        with open(MODEL_METADATA_FILE, "w", encoding="utf-8") as file:
            json.dump(metadata, file, indent=4)

    def run(self, X_train, y_train, X_test, y_test, selected_features=None):
        self.selected_features = list(selected_features or [])
        results = self.train_all_models(X_train, y_train, X_test, y_test)
        self.select_best_model(results)
        report = self.model_comparison_report(results)
        self.save_comparison_report(report)
        self.save_best_model()
        self.save_metrics(report)
        self.save_model_metadata(report, self.selected_features)
        log_success("Model training pipeline completed successfully.")
        return self.best_model, report
