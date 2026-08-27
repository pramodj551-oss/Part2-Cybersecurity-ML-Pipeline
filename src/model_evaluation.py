"""Regression model evaluation utilities."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (explained_variance_score, max_error, mean_absolute_error,
                             mean_absolute_percentage_error, mean_squared_error, r2_score)
from src.config import EVALUATION_REPORT_FILE, EVALUATION_SUMMARY_FILE, PREDICTION_RESULTS_FILE, RESIDUAL_REPORT_FILE
from src.logger import logger, log_success


class ModelEvaluator:
    def __init__(self):
        self.predictions_ = None
        self.metrics_ = {}
        self.residuals_ = None

    @staticmethod
    def validate_model(model):
        if model is None or not hasattr(model, "predict"):
            raise TypeError("Model must implement predict().")

    @staticmethod
    def validate_targets(y_true, y_pred):
        if len(y_true) != len(y_pred):
            raise ValueError("Target and prediction lengths do not match.")
        if not np.isfinite(np.asarray(y_true, dtype=float)).all() or not np.isfinite(np.asarray(y_pred, dtype=float)).all():
            raise ValueError("Targets and predictions must contain only finite values.")

    def predict(self, model: Any, X_test):
        self.validate_model(model)
        self.predictions_ = np.asarray(model.predict(X_test))
        return self.predictions_

    def calculate_metrics(self, y_true, y_pred):
        self.validate_targets(y_true, y_pred)
        y_true_arr = np.asarray(y_true, dtype=float)
        y_pred_arr = np.asarray(y_pred, dtype=float)
        mse = mean_squared_error(y_true_arr, y_pred_arr)
        metrics = {"MAE": float(mean_absolute_error(y_true_arr, y_pred_arr)), "MSE": float(mse), "RMSE": float(np.sqrt(mse)),
                   "R2 Score": float(r2_score(y_true_arr, y_pred_arr)),
                   "MAPE": float(mean_absolute_percentage_error(y_true_arr, y_pred_arr)),
                   "Explained Variance": float(explained_variance_score(y_true_arr, y_pred_arr)), "Max Error": float(max_error(y_true_arr, y_pred_arr))}
        self.metrics_ = metrics
        return metrics

    def calculate_residuals(self, y_true, y_pred):
        self.validate_targets(y_true, y_pred)
        self.residuals_ = np.asarray(y_true, dtype=float) - np.asarray(y_pred, dtype=float)
        return self.residuals_

    def error_statistics(self):
        if self.residuals_ is None:
            raise ValueError("Residuals have not been calculated.")
        return {"Mean Error": float(np.mean(self.residuals_)), "Median Error": float(np.median(self.residuals_)),
                "Std Error": float(np.std(self.residuals_)), "Min Error": float(np.min(self.residuals_)), "Max Error": float(np.max(self.residuals_))}

    def create_prediction_report(self, y_true, y_pred):
        self.validate_targets(y_true, y_pred)
        actual, predicted = np.asarray(y_true), np.asarray(y_pred)
        return pd.DataFrame({"Actual": actual, "Predicted": predicted, "Residual": actual - predicted, "Absolute Error": np.abs(actual - predicted)})

    def create_residual_report(self):
        if self.residuals_ is None:
            raise ValueError("Residuals have not been calculated.")
        return pd.DataFrame({"Residual": self.residuals_})

    def export_reports(self, prediction_report, residual_report):
        prediction_report.to_csv(PREDICTION_RESULTS_FILE, index=False)
        residual_report.to_csv(RESIDUAL_REPORT_FILE, index=False)
        pd.DataFrame([{"Metric": k, "Value": v} for k, v in self.metrics_.items()]).to_csv(EVALUATION_REPORT_FILE, index=False)

    def create_evaluation_summary(self):
        if not self.metrics_ or self.residuals_ is None:
            raise ValueError("Evaluation results are incomplete.")
        return {"evaluation_timestamp": datetime.now(timezone.utc).isoformat(), "metrics": self.metrics_,
                "residual_statistics": self.error_statistics(), "total_predictions": int(len(self.residuals_)),
                "mean_absolute_residual": float(np.mean(np.abs(self.residuals_))),
                "maximum_absolute_residual": float(np.max(np.abs(self.residuals_)))}

    def save_summary(self, summary):
        with open(EVALUATION_SUMMARY_FILE, "w", encoding="utf-8") as file:
            json.dump(summary, file, indent=4)

    def display_summary(self, summary):
        logger.info("MAE=%.4f | RMSE=%.4f | R²=%.4f | MAPE=%.4f | Predictions=%d", summary["metrics"]["MAE"], summary["metrics"]["RMSE"], summary["metrics"]["R2 Score"], summary["metrics"]["MAPE"], summary["total_predictions"])

    def visualization_data(self, y_true, y_pred):
        self.validate_targets(y_true, y_pred)
        return pd.DataFrame({"Actual": y_true, "Predicted": y_pred, "Residual": np.asarray(y_true) - np.asarray(y_pred)})

    def run(self, model, X_test, y_test):
        predictions = self.predict(model, X_test)
        self.calculate_metrics(y_test, predictions)
        self.calculate_residuals(y_test, predictions)
        prediction_report = self.create_prediction_report(y_test, predictions)
        self.export_reports(prediction_report, self.create_residual_report())
        summary = self.create_evaluation_summary()
        self.save_summary(summary)
        self.display_summary(summary)
        log_success("Model evaluation pipeline completed successfully.")
        return prediction_report, summary
