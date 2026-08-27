"""
AI-Powered Cybersecurity ML Pipeline - Prediction Module
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.config import (
    BEST_MODEL_FILE,
    FEATURE_IMPORTANCE_FILE,
    PREPROCESSOR_FILE,
    PREDICTION_OUTPUT_FILE,
    PREDICTION_COLUMN,
    PREDICTION_SUMMARY_FILE,
)
from src.logger import logger, log_section, log_success
from src.utils import load_model


class Predictor:
    """Production-ready prediction module."""

    def __init__(
        self,
        model_path: Path = BEST_MODEL_FILE,
        preprocessor_path: Path = PREPROCESSOR_FILE,
    ) -> None:
        self.model_path = model_path
        self.preprocessor_path = preprocessor_path
        self.model = None
        self.preprocessor = None
        logger.info("Predictor initialized.")

    def load_trained_model(self):
        """Load the trained ML model."""
        log_section("Loading Trained Model")
        self.model = load_model(self.model_path)
        logger.info("Model loaded successfully.")
        log_success("Model loading completed.")
        return self.model

    def load_preprocessor(self):
        """Load the fitted preprocessing pipeline."""
        log_section("Loading Preprocessor")
        self.preprocessor = load_model(self.preprocessor_path)
        logger.info("Preprocessor loaded successfully.")
        log_success("Preprocessor loading completed.")
        return self.preprocessor

    def load_artifacts(self):
        """Load model and preprocessor artifacts."""
        self.load_trained_model()
        self.load_preprocessor()
        logger.info("Prediction artifacts loaded successfully.")

    @staticmethod
    def validate_input(data: pd.DataFrame) -> None:
        """Validate prediction input."""
        if data is None:
            raise ValueError("Input data cannot be None.")
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Input data must be a pandas DataFrame.")
        if data.empty:
            raise ValueError("Input DataFrame is empty.")
        logger.info("Prediction input validated.")

    def _align_selected_features(self, transformed_data):
        """Apply the same top features used during model training."""
        if self.model is None:
            raise ValueError("Model has not been loaded.")
        if self.preprocessor is None:
            raise ValueError("Preprocessor has not been loaded.")

        expected_features = getattr(self.model, "n_features_in_", None)
        if expected_features is None:
            return transformed_data

        actual_features = transformed_data.shape[1]
        if actual_features == expected_features:
            return transformed_data
        if actual_features < expected_features:
            raise ValueError(
                f"Preprocessed input has {actual_features} features, "
                f"but model expects {expected_features}."
            )

        if not FEATURE_IMPORTANCE_FILE.exists():
            raise FileNotFoundError(
                "Feature importance artifact is required to reproduce "
                "the training-time feature selection."
            )

        importance = pd.read_csv(FEATURE_IMPORTANCE_FILE)
        if "feature" not in importance.columns:
            raise ValueError("Feature importance artifact has no 'feature' column.")

        selected_names = importance.head(expected_features)["feature"].tolist()
        feature_names = list(self.preprocessor.get_feature_names_out())
        feature_indices = []
        missing = []
        for name in selected_names:
            if name in feature_names:
                feature_indices.append(feature_names.index(name))
            else:
                missing.append(name)

        if missing:
            raise ValueError(
                "Selected training features are missing from the prediction "
                f"preprocessor output: {missing}"
            )
        if len(feature_indices) != expected_features:
            raise ValueError(
                f"Unable to reproduce {expected_features} training features; "
                f"resolved {len(feature_indices)}."
            )

        logger.info(
            "Applying training-time feature selection: %d -> %d features.",
            actual_features,
            len(feature_indices),
        )
        return transformed_data[:, feature_indices]

    def preprocess_input(self, data: pd.DataFrame):
        """Transform input data using the fitted preprocessor."""
        log_section("Preprocessing Input Data")
        self.validate_input(data)
        if self.preprocessor is None:
            raise ValueError("Preprocessor has not been loaded.")
        transformed_data = self.preprocessor.transform(data)
        transformed_data = self._align_selected_features(transformed_data)
        logger.info("Input preprocessing completed.")
        log_success("Input data transformed successfully.")
        return transformed_data

    def predict_single(self, sample: pd.DataFrame) -> float:
        """Predict for a single input record."""
        log_section("Single Prediction")
        processed_sample = self.preprocess_input(sample)
        if self.model is None:
            raise ValueError("Model has not been loaded.")
        prediction = self.model.predict(processed_sample)[0]
        logger.info("Prediction generated successfully.")
        log_success("Single prediction completed.")
        return float(prediction)

    def predict_batch(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate predictions for multiple records."""
        log_section("Batch Prediction")
        processed_data = self.preprocess_input(data)
        if self.model is None:
            raise ValueError("Model has not been loaded.")
        predictions = self.model.predict(processed_data)
        results = data.copy()
        results[PREDICTION_COLUMN] = predictions
        logger.info("%d predictions generated.", len(results))
        log_success("Batch prediction completed.")
        return results

    def prediction_statistics(self, predictions: pd.DataFrame) -> dict:
        """Generate prediction summary statistics."""
        if PREDICTION_COLUMN not in predictions.columns:
            raise ValueError("Prediction column not found.")
        values = predictions[PREDICTION_COLUMN]
        summary = {
            "total_predictions": int(len(predictions)),
            "minimum_prediction": float(values.min()),
            "maximum_prediction": float(values.max()),
            "mean_prediction": float(values.mean()),
            "standard_deviation": float(values.std()),
        }
        logger.info("Prediction statistics generated.")
        return summary

    def create_prediction_report(self, predictions: pd.DataFrame) -> pd.DataFrame:
        """Create a prediction report with metadata."""
        log_section("Creating Prediction Report")
        self.validate_input(predictions)
        report = predictions.copy()
        report["prediction_timestamp"] = datetime.now().isoformat()
        report["prediction_id"] = range(1, len(report) + 1)
        logger.info("Prediction report created.")
        log_success("Prediction report generation completed.")
        return report

    def export_predictions(self, report: pd.DataFrame) -> None:
        """Export prediction results to CSV."""
        log_section("Exporting Predictions")
        report.to_csv(PREDICTION_OUTPUT_FILE, index=False)
        logger.info("Predictions exported to %s", PREDICTION_OUTPUT_FILE)
        log_success("Prediction export completed.")

    def filter_high_risk_predictions(
        self,
        predictions: pd.DataFrame,
        threshold: float,
    ) -> pd.DataFrame:
        """Filter predictions above a threshold."""
        if PREDICTION_COLUMN not in predictions.columns:
            raise ValueError("Prediction column not found.")
        high_risk = predictions[predictions[PREDICTION_COLUMN] >= threshold].copy()
        logger.info("%d high-risk predictions identified.", len(high_risk))
        return high_risk

    def display_prediction_summary(self, summary: dict) -> None:
        """Display prediction statistics."""
        log_section("Prediction Summary")
        logger.info("Total Predictions : %d", summary["total_predictions"])
        logger.info("Minimum Prediction : %.4f", summary["minimum_prediction"])
        logger.info("Maximum Prediction : %.4f", summary["maximum_prediction"])
        logger.info("Mean Prediction : %.4f", summary["mean_prediction"])
        logger.info("Standard Deviation : %.4f", summary["standard_deviation"])
        log_success("Prediction summary displayed.")

    def save_prediction_summary(self, summary: dict) -> None:
        """Save prediction summary as JSON."""
        log_section("Saving Prediction Summary")
        payload = dict(summary)
        payload["generated_at"] = datetime.now().isoformat()
        with open(PREDICTION_SUMMARY_FILE, "w", encoding="utf-8") as file:
            json.dump(payload, file, indent=4)
        logger.info("Prediction summary saved to %s", PREDICTION_SUMMARY_FILE)
        log_success("Prediction summary exported.")

    def display_predictions(self, predictions: pd.DataFrame, rows: int = 5) -> None:
        """Display sample prediction results."""
        log_section("Prediction Preview")
        logger.info("\n%s", predictions.head(rows))
        log_success("Prediction preview displayed.")

    def reset(self) -> None:
        """Reset loaded artifacts."""
        self.model = None
        self.preprocessor = None
        logger.info("Predictor state reset.")

    def health_check(self) -> bool:
        """Verify that prediction artifacts are loaded correctly."""
        status = self.model is not None and self.preprocessor is not None
        if status:
            logger.info("Prediction service is ready.")
        else:
            logger.warning("Prediction service is not ready.")
        return status

    def ensure_loaded(self) -> None:
        """Load artifacts if they are not already loaded."""
        if self.model is None:
            self.load_trained_model()
        if self.preprocessor is None:
            self.load_preprocessor()
        logger.info("Prediction artifacts verified.")

    def run(self, input_data: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        """Execute the complete prediction pipeline."""
        log_section("Starting Prediction Pipeline")
        try:
            self.ensure_loaded()
            predictions = self.predict_batch(input_data)
            report = self.create_prediction_report(predictions)
            self.export_predictions(report)
            summary = self.prediction_statistics(report)
            self.save_prediction_summary(summary)
            self.display_prediction_summary(summary)
            self.display_predictions(report)
            log_success("Prediction pipeline completed successfully.")
            return report, summary
        except Exception:
            logger.exception("Prediction pipeline failed.")
            raise


if __name__ == "__main__":
    from src.data_loader import DataLoader

    try:
        log_section("Prediction Module")
        dataframe = DataLoader().run()
        predictor = Predictor()
        prediction_report, summary = predictor.run(dataframe)
        logger.info("Prediction pipeline executed successfully.")
    except Exception:
        logger.exception("Prediction module execution failed.")
        raise
