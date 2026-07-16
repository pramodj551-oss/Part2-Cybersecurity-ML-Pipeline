"""
==========================================================
AI-Powered Cybersecurity ML Pipeline
Part 2 - Prediction Module

Author : Pramod Prakash Jadhav
Python : 3.11+
==========================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.config import (
    BEST_MODEL_FILE,
    PREPROCESSOR_FILE,
)

from src.logger import (
    logger,
    log_section,
    log_success,
)

from src.utils import (
    load_model,
)


class Predictor:
    """
    Production-ready prediction module.

    Responsibilities
    ----------------
    - Load trained model
    - Load fitted preprocessor
    - Validate prediction input
    - Generate predictions
    """

    def __init__(
        self,
        model_path: Path = BEST_MODEL_FILE,
        preprocessor_path: Path = PREPROCESSOR_FILE,
    ) -> None:

        self.model_path = model_path

        self.preprocessor_path = preprocessor_path

        self.model = None

        self.preprocessor = None

        logger.info(
            "Predictor initialized."
        )

    # ======================================================
    # LOAD TRAINED MODEL
    # ======================================================

    def load_trained_model(self):
        """
        Load trained ML model.
        """

        log_section(
            "Loading Trained Model"
        )

        self.model = load_model(
            self.model_path
        )

        logger.info(
            "Model loaded successfully."
        )

        log_success(
            "Model loading completed."
        )

        return self.model

    # ======================================================
    # LOAD PREPROCESSOR
    # ======================================================

    def load_preprocessor(self):
        """
        Load fitted preprocessing pipeline.
        """

        log_section(
            "Loading Preprocessor"
        )

        self.preprocessor = load_model(
            self.preprocessor_path
        )

        logger.info(
            "Preprocessor loaded successfully."
        )

        log_success(
            "Preprocessor loading completed."
        )

        return self.preprocessor

    # ======================================================
    # LOAD ALL ARTIFACTS
    # ======================================================

    def load_artifacts(self):
        """
        Load model and preprocessor.
        """

        self.load_trained_model()

        self.load_preprocessor()

        logger.info(
            "Prediction artifacts loaded successfully."
        )

    # ======================================================
    # VALIDATE INPUT DATA
    # ======================================================

    @staticmethod
    def validate_input(
        data: pd.DataFrame,
    ) -> None:
        """
        Validate prediction input.
        """

        if data is None:

            raise ValueError(
                "Input data cannot be None."
            )

        if data.empty:

            raise ValueError(
                "Input DataFrame is empty."
            )

        logger.info(
            "Prediction input validated."
    )
      # ======================================================
    # PREPROCESS INPUT DATA
    # ======================================================

    def preprocess_input(
        self,
        data: pd.DataFrame,
    ):
        """
        Transform input data using the fitted preprocessor.
        """

        log_section(
            "Preprocessing Input Data"
        )

        self.validate_input(data)

        if self.preprocessor is None:

            raise ValueError(
                "Preprocessor has not been loaded."
            )

        transformed_data = (
            self.preprocessor.transform(data)
        )

        logger.info(
            "Input preprocessing completed."
        )

        log_success(
            "Input data transformed successfully."
        )

        return transformed_data


    # ======================================================
    # SINGLE PREDICTION
    # ======================================================

    def predict_single(
        self,
        sample: pd.DataFrame,
    ) -> float:
        """
        Predict for a single input record.
        """

        log_section(
            "Single Prediction"
        )

        processed_sample = (
            self.preprocess_input(sample)
        )

        if self.model is None:

            raise ValueError(
                "Model has not been loaded."
            )

        prediction = self.model.predict(
            processed_sample
        )[0]

        logger.info(
            "Prediction generated successfully."
        )

        log_success(
            "Single prediction completed."
        )

        return float(prediction)


    # ======================================================
    # BATCH PREDICTION
    # ======================================================

    def predict_batch(
        self,
        data: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Generate predictions for multiple records.
        """

        log_section(
            "Batch Prediction"
        )

        processed_data = (
            self.preprocess_input(data)
        )

        if self.model is None:

            raise ValueError(
                "Model has not been loaded."
            )

        predictions = self.model.predict(
            processed_data
        )

        results = data.copy()

        results["prediction"] = predictions

        logger.info(
            "%d predictions generated.",
            len(results),
        )

        log_success(
            "Batch prediction completed."
        )

        return results


    # ======================================================
    # PREDICTION STATISTICS
    # ======================================================

    def prediction_statistics(
        self,
        predictions: pd.DataFrame,
    ) -> dict:
        """
        Generate prediction summary statistics.
        """

        if "prediction" not in predictions.columns:

            raise ValueError(
                "Prediction column not found."
            )

        summary = {

            "total_predictions":
                int(len(predictions)),

            "minimum_prediction":
                float(
                    predictions[
                        "prediction"
                    ].min()
                ),

            "maximum_prediction":
                float(
                    predictions[
                        "prediction"
                    ].max()
                ),

            "mean_prediction":
                float(
                    predictions[
                        "prediction"
                    ].mean()
                ),

            "standard_deviation":
                float(
                    predictions[
                        "prediction"
                    ].std()
                ),

        }

        logger.info(
            "Prediction statistics generated."
        )

        return summary
      from datetime import datetime

from src.config import (
    PREDICTION_OUTPUT_FILE,
    PREDICTION_COLUMN,
)


    # ======================================================
    # CREATE PREDICTION REPORT
    # ======================================================

    def create_prediction_report(
        self,
        predictions: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Create a prediction report with metadata.
        """

        log_section(
            "Creating Prediction Report"
        )

        self.validate_input(predictions)

        report = predictions.copy()

        report["prediction_timestamp"] = (
            datetime.now().isoformat()
        )

        report["prediction_id"] = range(
            1,
            len(report) + 1,
        )

        logger.info(
            "Prediction report created."
        )

        log_success(
            "Prediction report generation completed."
        )

        return report


    # ======================================================
    # EXPORT PREDICTIONS
    # ======================================================

    def export_predictions(
        self,
        report: pd.DataFrame,
    ) -> None:
        """
        Export prediction results to CSV.
        """

        log_section(
            "Exporting Predictions"
        )

        report.to_csv(
            PREDICTION_OUTPUT_FILE,
            index=False,
        )

        logger.info(
            "Predictions exported to %s",
            PREDICTION_OUTPUT_FILE,
        )

        log_success(
            "Prediction export completed."
        )


    # ======================================================
    # FILTER HIGH-RISK PREDICTIONS
    # ======================================================

    def filter_high_risk_predictions(
        self,
        predictions: pd.DataFrame,
        threshold: float,
    ) -> pd.DataFrame:
        """
        Filter predictions above a threshold.
        """

        if PREDICTION_COLUMN not in predictions.columns:

            raise ValueError(
                "Prediction column not found."
            )

        high_risk = predictions[
            predictions[
                PREDICTION_COLUMN
            ] >= threshold
        ].copy()

        logger.info(
            "%d high-risk predictions identified.",
            len(high_risk),
        )

        return high_risk


    # ======================================================
    # DISPLAY PREDICTION SUMMARY
    # ======================================================

    def display_prediction_summary(
        self,
        summary: dict,
    ) -> None:
        """
        Display prediction statistics.
        """

        log_section(
            "Prediction Summary"
        )

        logger.info(
            "Total Predictions : %d",
            summary["total_predictions"],
        )

        logger.info(
            "Minimum Prediction : %.4f",
            summary["minimum_prediction"],
        )

        logger.info(
            "Maximum Prediction : %.4f",
            summary["maximum_prediction"],
        )

        logger.info(
            "Mean Prediction : %.4f",
            summary["mean_prediction"],
        )

        logger.info(
            "Standard Deviation : %.4f",
            summary["standard_deviation"],
        )

        log_success(
            "Prediction summary displayed."
  )
      import json
from datetime import datetime

from src.config import (
    PREDICTION_SUMMARY_FILE,
)


    # ======================================================
    # SAVE PREDICTION SUMMARY
    # ======================================================

    def save_prediction_summary(
        self,
        summary: dict,
    ) -> None:
        """
        Save prediction summary as JSON.
        """

        log_section(
            "Saving Prediction Summary"
        )

        summary["generated_at"] = (
            datetime.now().isoformat()
        )

        with open(
            PREDICTION_SUMMARY_FILE,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                summary,
                file,
                indent=4,
            )

        logger.info(
            "Prediction summary saved to %s",
            PREDICTION_SUMMARY_FILE,
        )

        log_success(
            "Prediction summary exported."
        )


    # ======================================================
    # DISPLAY PREDICTION SAMPLE
    # ======================================================

    def display_predictions(
        self,
        predictions: pd.DataFrame,
        rows: int = 5,
    ) -> None:
        """
        Display sample prediction results.
        """

        log_section(
            "Prediction Preview"
        )

        logger.info(
            "\n%s",
            predictions.head(rows),
        )

        log_success(
            "Prediction preview displayed."
        )


    # ======================================================
    # RESET PREDICTOR
    # ======================================================

    def reset(
        self,
    ) -> None:
        """
        Reset loaded artifacts.
        """

        self.model = None

        self.preprocessor = None

        logger.info(
            "Predictor state reset."
        )


    # ======================================================
    # HEALTH CHECK
    # ======================================================

    def health_check(
        self,
    ) -> bool:
        """
        Verify that prediction artifacts
        are loaded correctly.
        """

        status = (
            self.model is not None
            and
            self.preprocessor is not None
        )

        if status:

            logger.info(
                "Prediction service is ready."
            )

        else:

            logger.warning(
                "Prediction service is not ready."
            )

        return status


    # ======================================================
    # LOAD IF REQUIRED
    # ======================================================

    def ensure_loaded(
        self,
    ) -> None:
        """
        Automatically load artifacts
        if not already loaded.
        """

        if self.model is None:

            self.load_trained_model()

        if self.preprocessor is None:

            self.load_preprocessor()

        logger.info(
            "Prediction artifacts verified."
      )
      # ======================================================
    # COMPLETE PREDICTION PIPELINE
    # ======================================================

    def run(
        self,
        input_data: pd.DataFrame,
    ) -> tuple[pd.DataFrame, dict]:
        """
        Execute the complete prediction pipeline.
        """

        log_section(
            "Starting Prediction Pipeline"
        )

        try:

            # Step 1
            self.ensure_loaded()

            # Step 2
            predictions = self.predict_batch(
                input_data
            )

            # Step 3
            report = self.create_prediction_report(
                predictions
            )

            # Step 4
            self.export_predictions(
                report
            )

            # Step 5
            summary = self.prediction_statistics(
                report
            )

            # Step 6
            self.save_prediction_summary(
                summary
            )

            # Step 7
            self.display_prediction_summary(
                summary
            )

            # Step 8
            self.display_predictions(
                report
            )

            log_success(
                "Prediction pipeline completed successfully."
            )

            return (
                report,
                summary,
            )

        except Exception:

            logger.exception(
                "Prediction pipeline failed."
            )

            raise


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    from src.data_loader import DataLoader

    try:

        log_section(
            "Prediction Module"
        )

        # Load input data
        loader = DataLoader()

        dataframe = loader.run()

        predictor = Predictor()

        prediction_report, summary = (
            predictor.run(
                dataframe
            )
        )

        logger.info(
            "Prediction pipeline executed successfully."
        )

    except Exception:

        logger.exception(
            "Prediction module execution failed."
        )

        raise
      
