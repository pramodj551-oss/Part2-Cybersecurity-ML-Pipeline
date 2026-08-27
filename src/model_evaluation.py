"""Model evaluation utilities for the cybersecurity ML pipeline."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    explained_variance_score,
    max_error,
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    r2_score,
)

from src.config import (
    EVALUATION_REPORT_FILE,
    EVALUATION_SUMMARY_FILE,
    PREDICTION_RESULTS_FILE,
    RESIDUAL_REPORT_FILE,
)
from src.logger import logger, log_section, log_success


class ModelEvaluator:
    """Production-ready regression model evaluator."""

    def __init__(self) -> None:
        self.predictions_: np.ndarray | None = None
        self.metrics_: dict[str, float] = {}
        self.residuals_: np.ndarray | None = None
        logger.info("ModelEvaluator initialized.")

    @staticmethod
    def validate_model(model: Any) -> None:
        """Validate that a trained model exposes predict()."""
        if model is None:
            raise ValueError("Model cannot be None.")
        if not hasattr(model, "predict"):
            raise TypeError("Model must implement predict().")

    def predict(self, model: Any, X_test: Any) -> np.ndarray:
        """Generate predictions from a trained model."""
        log_section("Generating Predictions")
        self.validate_model(model)
        predictions = np.asarray(model.predict(X_test))
        self.predictions_ = predictions
        logger.info("Generated %d predictions.", len(predictions))
        log_success("Prediction generation completed.")
        return predictions

    @staticmethod
    def validate_targets(y_true: Any, y_pred: Any) -> None:
        """Validate prediction arrays."""
        if len(y_true) != len(y_pred):
            raise ValueError("Target and prediction lengths do not match.")
        logger.info("Prediction arrays validated.")

    def calculate_metrics(self, y_true: Any, y_pred: Any) -> dict[str, float]:
        """Calculate regression evaluation metrics."""
        log_section("Calculating Evaluation Metrics")
        self.validate_targets(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        metrics = {
            "MAE": float(mean_absolute_error(y_true, y_pred)),
            "MSE": float(mse),
            "RMSE": float(np.sqrt(mse)),
            "R2 Score": float(r2_score(y_true, y_pred)),
            "MAPE": float(mean_absolute_percentage_error(y_true, y_pred)),
            "Explained Variance": float(explained_variance_score(y_true, y_pred)),
            "Max Error": float(max_error(y_true, y_pred)),
        }
        self.metrics_ = metrics
        log_success("Evaluation metrics completed.")
        return metrics

    def calculate_residuals(self, y_true: Any, y_pred: Any) -> np.ndarray:
        """Calculate prediction residuals."""
        log_section("Residual Analysis")
        self.validate_targets(y_true, y_pred)
        residuals = np.asarray(y_true) - np.asarray(y_pred)
        self.residuals_ = residuals
        log_success("Residual calculation completed.")
        return residuals

    def error_statistics(self) -> dict[str, float]:
        """Return summary statistics for residuals."""
        if self.residuals_ is None:
            raise ValueError("Residuals have not been calculated.")
        return {
            "Mean Error": float(np.mean(self.residuals_)),
            "Median Error": float(np.median(self.residuals_)),
            "Std Error": float(np.std(self.residuals_)),
            "Min Error": float(np.min(self.residuals_)),
            "Max Error": float(np.max(self.residuals_)),
        }

    def create_prediction_report(self, y_true: Any, y_pred: Any) -> pd.DataFrame:
        """Create a prediction-level report."""
        self.validate_targets(y_true, y_pred)
        actual = np.asarray(y_true)
        predicted = np.asarray(y_pred)
        return pd.DataFrame({
            "Actual": actual,
            "Predicted": predicted,
            "Residual": actual - predicted,
            "Absolute Error": np.abs(actual - predicted),
        })

    def create_residual_report(self) -> pd.DataFrame:
        """Create a residual report."""
        if self.residuals_ is None:
            raise ValueError("Residuals have not been calculated.")
        return pd.DataFrame({"Residual": self.residuals_})

    def export_reports(
        self,
        prediction_report: pd.DataFrame,
        residual_report: pd.DataFrame,
    ) -> None:
        """Export prediction, residual, and metric reports."""
        prediction_report.to_csv(PREDICTION_RESULTS_FILE, index=False)
        residual_report.to_csv(RESIDUAL_REPORT_FILE, index=False)
        metrics_df = pd.DataFrame(
            [{"Metric": key, "Value": value} for key, value in self.metrics_.items()]
        )
        metrics_df.to_csv(EVALUATION_REPORT_FILE, index=False)
        log_success("All evaluation reports exported successfully.")

    def create_evaluation_summary(self) -> dict:
        """Create the complete evaluation summary."""
        if not self.metrics_:
            raise ValueError("Evaluation metrics are not available.")
        if self.residuals_ is None:
            raise ValueError("Residuals have not been calculated.")
        return {
            "evaluation_timestamp": datetime.now().isoformat(),
            "metrics": self.metrics_,
            "residual_statistics": self.error_statistics(),
            "total_predictions": int(len(self.residuals_)),
            "mean_absolute_residual": float(np.mean(np.abs(self.residuals_))),
            "maximum_absolute_residual": float(np.max(np.abs(self.residuals_))),
        }

    def save_summary(self, summary: dict) -> None:
        """Save evaluation summary as JSON."""
        with open(EVALUATION_SUMMARY_FILE, "w", encoding="utf-8") as file:
            json.dump(summary, file, indent=4)
        log_success("JSON summary exported.")

    def display_summary(self, summary: dict) -> None:
        """Log the key evaluation metrics."""
        metrics = summary["metrics"]
        logger.info("MAE : %.4f", metrics["MAE"])
        logger.info("RMSE : %.4f", metrics["RMSE"])
        logger.info("R² Score : %.4f", metrics["R2 Score"])
        logger.info("MAPE : %.4f", metrics["MAPE"])
        logger.info("Predictions : %d", summary["total_predictions"])

    def visualization_data(self, y_true: Any, y_pred: Any) -> pd.DataFrame:
        """Create visualization-ready evaluation data."""
        self.validate_targets(y_true, y_pred)
        return pd.DataFrame({
            "Actual": y_true,
            "Predicted": y_pred,
            "Residual": np.asarray(y_true) - np.asarray(y_pred),
        })

    def run(self, model: Any, X_test: Any, y_test: Any) -> tuple[pd.DataFrame, dict]:
        """Execute the complete model evaluation pipeline."""
        log_section("Starting Model Evaluation Pipeline")
        predictions = self.predict(model, X_test)
        self.calculate_metrics(y_test, predictions)
        self.calculate_residuals(y_test, predictions)
        prediction_report = self.create_prediction_report(y_test, predictions)
        residual_report = self.create_residual_report()
        self.export_reports(prediction_report, residual_report)
        summary = self.create_evaluation_summary()
        self.save_summary(summary)
        self.display_summary(summary)
        log_success("Model evaluation pipeline completed successfully.")
        return prediction_report, summary


if __name__ == "__main__":
    logger.info("Model evaluation module loaded successfully.")
