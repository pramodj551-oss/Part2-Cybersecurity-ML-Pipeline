"""
AI-Powered Cybersecurity ML Pipeline - Model Training
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Dict

import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeRegressor

from src.config import (
    BEST_MODEL_FILE,
    CV_FOLDS,
    MAX_DEPTH,
    METRICS_FILE,
    MIN_SAMPLES_LEAF,
    MIN_SAMPLES_SPLIT,
    MODEL_METADATA_FILE,
    N_ESTIMATORS,
    OUTPUT_DIR,
    RANDOM_STATE,
)
from src.logger import logger, log_section, log_success
from src.utils import save_model


class ModelTrainer:
    """Train, evaluate, compare and persist regression models."""

    def __init__(self) -> None:
        self.models: Dict[str, object] = {
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
                n_estimators=150,
                max_depth=3,
            ),
        }
        self.best_model_name: str | None = None
        self.best_model = None
        self.training_results: list[dict] = []
        logger.info("%d models initialized.", len(self.models))

    def list_models(self) -> list[str]:
        return list(self.models.keys())

    def get_model(self, model_name: str):
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")
        return self.models[model_name]

    def model_summary(self) -> None:
        log_section("Configured ML Models")
        for name in self.models:
            logger.info(name)
        log_success("Model configuration loaded.")

    def train_model(self, model_name: str, X_train, y_train):
        log_section(f"Training : {model_name}")
        model = self.get_model(model_name)
        model.fit(X_train, y_train)
        logger.info("%s training completed.", model_name)
        return model

    def evaluate_model(self, model_name: str, model, X_test, y_test) -> dict:
        predictions = model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        # Compute RMSE without the deprecated/removed `squared` keyword.
        rmse = mean_squared_error(y_test, predictions) ** 0.5
        r2 = r2_score(y_test, predictions)
        cv_scores = cross_val_score(
            model,
            X_test,
            y_test,
            cv=CV_FOLDS,
            scoring="r2",
            n_jobs=-1,
        )
        results = {
            "Model": model_name,
            "MAE": round(mae, 4),
            "RMSE": round(rmse, 4),
            "R2 Score": round(r2, 4),
            "CV Mean": round(cv_scores.mean(), 4),
            "CV Std": round(cv_scores.std(), 4),
        }
        logger.info(
            "%s | MAE=%.4f | RMSE=%.4f | R²=%.4f",
            model_name,
            mae,
            rmse,
            r2,
        )
        return results

    def train_all_models(self, X_train, y_train, X_test, y_test) -> pd.DataFrame:
        log_section("Training All Models")
        self.training_results.clear()
        for model_name in self.list_models():
            model = self.train_model(model_name, X_train, y_train)
            metrics = self.evaluate_model(model_name, model, X_test, y_test)
            metrics["Model Object"] = model
            self.training_results.append(metrics)
        results_df = pd.DataFrame(self.training_results)
        logger.info("Successfully trained %d models.", len(results_df))
        log_success("Model training completed.")
        return results_df

    def select_best_model(self, results_df: pd.DataFrame):
        log_section("Selecting Best Model")
        if results_df.empty:
            raise ValueError("No model results available.")
        ranked = results_df.sort_values(
            by=["R2 Score", "RMSE"], ascending=[False, True]
        ).reset_index(drop=True)
        best_result = ranked.iloc[0]
        self.best_model_name = best_result["Model"]
        self.best_model = best_result["Model Object"]
        logger.info("Best Model : %s", self.best_model_name)
        logger.info("Best R² Score : %.4f", best_result["R2 Score"])
        logger.info("Best RMSE : %.4f", best_result["RMSE"])
        log_success("Best model selected successfully.")
        return self.best_model

    def model_comparison_report(self, results_df: pd.DataFrame) -> pd.DataFrame:
        report = (
            results_df.drop(columns=["Model Object"], errors="ignore")
            .sort_values(by="R2 Score", ascending=False)
            .reset_index(drop=True)
        )
        logger.info("Model comparison report generated.")
        return report

    def display_results(self, report: pd.DataFrame) -> None:
        log_section("Model Comparison Results")
        for _, row in report.iterrows():
            logger.info(
                "%s | R²=%.4f | RMSE=%.4f | MAE=%.4f",
                row["Model"], row["R2 Score"], row["RMSE"], row["MAE"],
            )
        log_success("Comparison results displayed.")

    def save_comparison_report(self, report: pd.DataFrame) -> None:
        report_file = OUTPUT_DIR / "model_comparison.csv"
        report.to_csv(report_file, index=False)
        logger.info("Comparison report saved: %s", report_file)
        log_success("Model comparison report exported.")

    def save_best_model(self) -> None:
        log_section("Saving Best Model")
        if self.best_model is None:
            raise ValueError("No trained model available.")
        save_model(self.best_model, BEST_MODEL_FILE)
        logger.info("Best model saved to %s", BEST_MODEL_FILE)
        log_success("Best model saved successfully.")

    def save_metrics(self, report: pd.DataFrame) -> None:
        metrics = report.to_dict(orient="records")
        with open(METRICS_FILE, "w", encoding="utf-8") as file:
            json.dump(metrics, file, indent=4)
        logger.info("Metrics saved to %s", METRICS_FILE)
        log_success("Metrics exported successfully.")

    def save_model_metadata(self, report: pd.DataFrame) -> None:
        if report.empty:
            raise ValueError("Cannot save metadata from an empty report.")
        best = report.iloc[0]
        metadata = {
            "model_name": self.best_model_name,
            "training_timestamp": datetime.now().isoformat(),
            "r2_score": float(best["R2 Score"]),
            "rmse": float(best["RMSE"]),
            "mae": float(best["MAE"]),
            "python_version": "3.11+",
        }
        with open(MODEL_METADATA_FILE, "w", encoding="utf-8") as file:
            json.dump(metadata, file, indent=4)
        logger.info("Model metadata saved.")
        log_success("Metadata generation completed.")

    def training_summary(self, report: pd.DataFrame) -> None:
        log_section("Training Summary")
        logger.info("Models Trained : %d", len(report))
        logger.info("Best Model : %s", self.best_model_name)
        logger.info("Best R² Score : %.4f", report.iloc[0]["R2 Score"])
        logger.info("Best RMSE : %.4f", report.iloc[0]["RMSE"])
        logger.info("Best MAE : %.4f", report.iloc[0]["MAE"])
        log_success("Training summary generated.")

    def run(self, X_train, y_train, X_test, y_test):
        log_section("Starting Model Training Pipeline")
        try:
            results_df = self.train_all_models(X_train, y_train, X_test, y_test)
            self.select_best_model(results_df)
            report = self.model_comparison_report(results_df)
            self.display_results(report)
            self.save_comparison_report(report)
            self.save_best_model()
            self.save_metrics(report)
            self.save_model_metadata(report)
            self.training_summary(report)
            log_success("Model training pipeline completed successfully.")
            return self.best_model, report
        except Exception:
            logger.exception("Model training pipeline failed.")
            raise


if __name__ == "__main__":
    from src.data_loader import DataLoader
    from src.feature_selection import FeatureSelector
    from src.preprocessing import Preprocessor

    log_section("Model Training Module")
    dataframe = DataLoader().run()
    preprocessor = Preprocessor()
    X_train, X_test, y_train, y_test, fitted_preprocessor = preprocessor.run(dataframe)
    feature_names = list(fitted_preprocessor.get_feature_names_out())
    selector = FeatureSelector()
    X_train_selected, selected_features, _ = selector.run(
        X_train, y_train, feature_names, top_n=20
    )
    selected_indices = [feature_names.index(name) for name in selected_features]
    X_test_selected = X_test[:, selected_indices]
    trainer = ModelTrainer()
    trainer.run(X_train_selected, y_train, X_test_selected, y_test)
