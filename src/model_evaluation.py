"""
==========================================================
AI-Powered Cybersecurity ML Pipeline
Part 2 - Model Evaluation

Author : Pramod Prakash Jadhav
Python : 3.11+
==========================================================
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    mean_absolute_percentage_error,
    r2_score,
    explained_variance_score,
    max_error,
)

from src.logger import (
    logger,
    log_section,
    log_success,
)


class ModelEvaluator:
    """
    Production-ready regression model evaluator.

    Responsibilities
    ----------------
    - Generate predictions
    - Calculate evaluation metrics
    - Residual analysis
    - Prediction reports
    - Evaluation summary
    """

    def __init__(self) -> None:

        self.predictions_: np.ndarray | None = None

        self.metrics_: dict[str, float] = {}

        self.residuals_: np.ndarray | None = None

        logger.info(
            "ModelEvaluator initialized."
        )

    # ======================================================
    # VALIDATE MODEL
    # ======================================================

    @staticmethod
    def validate_model(
        model: Any,
    ) -> None:
        """
        Validate trained model.
        """

        if model is None:

            raise ValueError(
                "Model cannot be None."
            )

        if not hasattr(model, "predict"):

            raise TypeError(
                "Model must implement predict()."
            )

    # ======================================================
    # GENERATE PREDICTIONS
    # ======================================================

    def predict(
        self,
        model,
        X_test,
    ) -> np.ndarray:
        """
        Generate predictions.
        """

        log_section(
            "Generating Predictions"
        )

        self.validate_model(model)

        predictions = model.predict(
            X_test
        )

        self.predictions_ = predictions

        logger.info(
            "Generated %d predictions.",
            len(predictions),
        )

        log_success(
            "Prediction generation completed."
        )

        return predictions

    # ======================================================
    # VALIDATE TARGETS
    # ======================================================

    @staticmethod
    def validate_targets(
        y_true,
        y_pred,
    ) -> None:
        """
        Validate prediction arrays.
        """

        if len(y_true) != len(y_pred):

            raise ValueError(
                "Target and prediction lengths do not match."
            )

        logger.info(
            "Prediction arrays validated."
      )
      # ======================================================
    # CALCULATE REGRESSION METRICS
    # ======================================================

    def calculate_metrics(
        self,
        y_true,
        y_pred,
    ) -> dict[str, float]:
        """
        Calculate regression evaluation metrics.

        Parameters
        ----------
        y_true : array-like
            Actual target values.

        y_pred : array-like
            Predicted target values.

        Returns
        -------
        dict
            Dictionary containing evaluation metrics.
        """

        log_section(
            "Calculating Evaluation Metrics"
        )

        self.validate_targets(
            y_true,
            y_pred,
        )

        mse = mean_squared_error(
            y_true,
            y_pred,
        )

        metrics = {

            "MAE": float(
                mean_absolute_error(
                    y_true,
                    y_pred,
                )
            ),

            "MSE": float(mse),

            "RMSE": float(
                np.sqrt(mse)
            ),

            "R2 Score": float(
                r2_score(
                    y_true,
                    y_pred,
                )
            ),

            "MAPE": float(
                mean_absolute_percentage_error(
                    y_true,
                    y_pred,
                )
            ),

            "Explained Variance": float(
                explained_variance_score(
                    y_true,
                    y_pred,
                )
            ),

            "Max Error": float(
                max_error(
                    y_true,
                    y_pred,
                )
            ),

        }

        self.metrics_ = metrics

        logger.info(
            "Regression metrics calculated successfully."
        )

        log_success(
            "Evaluation metrics completed."
        )

        return metrics


    # ======================================================
    # CALCULATE RESIDUALS
    # ======================================================

    def calculate_residuals(
        self,
        y_true,
        y_pred,
    ) -> np.ndarray:
        """
        Calculate prediction residuals.
        """

        log_section(
            "Residual Analysis"
        )

        self.validate_targets(
            y_true,
            y_pred,
        )

        residuals = (
            np.asarray(y_true)
            - np.asarray(y_pred)
        )

        self.residuals_ = residuals

        logger.info(
            "Residuals calculated successfully."
        )

        log_success(
            "Residual calculation completed."
        )

        return residuals


    # ======================================================
    # ERROR STATISTICS
    # ======================================================

    def error_statistics(
        self,
    ) -> dict[str, float]:
        """
        Generate summary statistics for residuals.
        """

        if self.residuals_ is None:

            raise ValueError(
                "Residuals have not been calculated."
            )

        stats = {

            "Mean Error": float(
                np.mean(self.residuals_)
            ),

            "Median Error": float(
                np.median(self.residuals_)
            ),

            "Std Error": float(
                np.std(self.residuals_)
            ),

            "Min Error": float(
                np.min(self.residuals_)
            ),

            "Max Error": float(
                np.max(self.residuals_)
            ),

        }

        logger.info(
            "Residual statistics generated."
        )

        return stats
      from src.config import (
    PREDICTION_RESULTS_FILE,
    RESIDUAL_REPORT_FILE,
    EVALUATION_REPORT_FILE,
)

    # ======================================================
    # PREDICTION REPORT
    # ======================================================

    def create_prediction_report(
        self,
        y_true,
        y_pred,
    ) -> pd.DataFrame:
        """
        Create prediction report.
        """

        log_section(
            "Creating Prediction Report"
        )

        self.validate_targets(
            y_true,
            y_pred,
        )

        report = pd.DataFrame(
            {
                "Actual": y_true,
                "Predicted": y_pred,
                "Residual": (
                    np.asarray(y_true)
                    - np.asarray(y_pred)
                ),
                "Absolute Error": np.abs(
                    np.asarray(y_true)
                    - np.asarray(y_pred)
                ),
            }
        )

        logger.info(
            "Prediction report created with %d rows.",
            len(report),
        )

        log_success(
            "Prediction report generated."
        )

        return report


    # ======================================================
    # RESIDUAL REPORT
    # ======================================================

    def create_residual_report(
        self,
    ) -> pd.DataFrame:
        """
        Create residual report.
        """

        if self.residuals_ is None:

            raise ValueError(
                "Residuals have not been calculated."
            )

        residual_df = pd.DataFrame(
            {
                "Residual": self.residuals_,
            }
        )

        logger.info(
            "Residual report generated."
        )

        return residual_df


    # ======================================================
    # EXPORT REPORTS
    # ======================================================

    def export_reports(
        self,
        prediction_report: pd.DataFrame,
        residual_report: pd.DataFrame,
    ) -> None:
        """
        Export evaluation reports to CSV.
        """

        log_section(
            "Exporting Evaluation Reports"
        )

        prediction_report.to_csv(
            PREDICTION_RESULTS_FILE,
            index=False,
        )

        residual_report.to_csv(
            RESIDUAL_REPORT_FILE,
            index=False,
        )

        metrics_df = pd.DataFrame(
            [
                {
                    "Metric": key,
                    "Value": value,
                }
                for key, value
                in self.metrics_.items()
            ]
        )

        metrics_df.to_csv(
            EVALUATION_REPORT_FILE,
            index=False,
        )

        logger.info(
            "Prediction report saved: %s",
            PREDICTION_RESULTS_FILE,
        )

        logger.info(
            "Residual report saved: %s",
            RESIDUAL_REPORT_FILE,
        )

        logger.info(
            "Evaluation metrics saved: %s",
            EVALUATION_REPORT_FILE,
        )

        log_success(
            "All evaluation reports exported successfully."
)
      import json
from datetime import datetime

from src.config import (
    EVALUATION_SUMMARY_FILE,
)

    # ======================================================
    # CREATE EVALUATION SUMMARY
    # ======================================================

    def create_evaluation_summary(
        self,
    ) -> dict:
        """
        Create a comprehensive evaluation summary.

        Returns
        -------
        dict
            Evaluation summary.
        """

        log_section(
            "Creating Evaluation Summary"
        )

        if not self.metrics_:

            raise ValueError(
                "Evaluation metrics are not available."
            )

        if self.residuals_ is None:

            raise ValueError(
                "Residuals have not been calculated."
            )

        summary = {

            "evaluation_timestamp":
                datetime.now().isoformat(),

            "metrics":
                self.metrics_,

            "residual_statistics":
                self.error_statistics(),

            "total_predictions":
                int(len(self.residuals_)),

            "mean_absolute_residual":
                float(
                    np.mean(
                        np.abs(
                            self.residuals_
                        )
                    )
                ),

            "maximum_absolute_residual":
                float(
                    np.max(
                        np.abs(
                            self.residuals_
                        )
                    )
                ),

        }

        logger.info(
            "Evaluation summary created successfully."
        )

        log_success(
            "Evaluation summary completed."
        )

        return summary


    # ======================================================
    # SAVE JSON SUMMARY
    # ======================================================

    def save_summary(
        self,
        summary: dict,
    ) -> None:
        """
        Save evaluation summary as JSON.
        """

        log_section(
            "Saving Evaluation Summary"
        )

        with open(
            EVALUATION_SUMMARY_FILE,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                summary,
                file,
                indent=4,
            )

        logger.info(
            "Evaluation summary saved to %s",
            EVALUATION_SUMMARY_FILE,
        )

        log_success(
            "JSON summary exported."
        )


    # ======================================================
    # DISPLAY SUMMARY
    # ======================================================

    def display_summary(
        self,
        summary: dict,
    ) -> None:
        """
        Display evaluation summary.
        """

        log_section(
            "Evaluation Summary"
        )

        metrics = summary["metrics"]

        logger.info(
            "MAE : %.4f",
            metrics["MAE"],
        )

        logger.info(
            "RMSE : %.4f",
            metrics["RMSE"],
        )

        logger.info(
            "R² Score : %.4f",
            metrics["R2 Score"],
        )

        logger.info(
            "MAPE : %.4f",
            metrics["MAPE"],
        )

        logger.info(
            "Predictions : %d",
            summary["total_predictions"],
        )

        log_success(
            "Evaluation summary displayed."
        )


    # ======================================================
    # VISUALIZATION DATA
    # ======================================================

    def visualization_data(
        self,
        y_true,
        y_pred,
    ) -> pd.DataFrame:
        """
        Create visualization-ready dataset.
        """

        self.validate_targets(
            y_true,
            y_pred,
        )

        visualization_df = pd.DataFrame(
            {
                "Actual": y_true,
                "Predicted": y_pred,
                "Residual": (
                    np.asarray(y_true)
                    - np.asarray(y_pred)
                ),
            }
        )

        logger.info(
            "Visualization dataset created."
        )

        return visualization_df
      # ======================================================
    # COMPLETE MODEL EVALUATION PIPELINE
    # ======================================================

    def run(
        self,
        model,
        X_test,
        y_test,
    ) -> tuple[pd.DataFrame, dict]:
        """
        Execute the complete model evaluation pipeline.

        Parameters
        ----------
        model
            Trained regression model.

        X_test
            Test feature matrix.

        y_test
            Actual target values.

        Returns
        -------
        tuple
            Prediction report and evaluation summary.
        """

        log_section(
            "Starting Model Evaluation Pipeline"
        )

        try:

            # Step 1
            predictions = self.predict(
                model,
                X_test,
            )

            # Step 2
            self.calculate_metrics(
                y_test,
                predictions,
            )

            # Step 3
            self.calculate_residuals(
                y_test,
                predictions,
            )

            # Step 4
            prediction_report = (
                self.create_prediction_report(
                    y_test,
                    predictions,
                )
            )

            # Step 5
            residual_report = (
                self.create_residual_report()
            )

            # Step 6
            self.export_reports(
                prediction_report,
                residual_report,
            )

            # Step 7
            summary = (
                self.create_evaluation_summary()
            )

            # Step 8
            self.save_summary(
                summary,
            )

            # Step 9
            self.display_summary(
                summary,
            )

            log_success(
                "Model evaluation pipeline completed successfully."
            )

            return (
                prediction_report,
                summary,
            )

        except Exception:

            logger.exception(
                "Model evaluation pipeline failed."
            )

            raise


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    from src.data_loader import DataLoader
    from src.preprocessing import Preprocessor
    from src.feature_selection import FeatureSelector
    from src.model_training import ModelTrainer

    try:

        log_section(
            "Model Evaluation Module"
        )

        # Load data
        loader = DataLoader()
        dataframe = loader.run()

        # Preprocess data
        preprocessor = Preprocessor()

        (
            X_train,
            X_test,
            y_train,
            y_test,
            fitted_preprocessor,
        ) = preprocessor.run(dataframe)

        # Feature selection
        feature_names = list(
            fitted_preprocessor.get_feature_names_out()
        )

        selector = FeatureSelector()

        (
            X_train_selected,
            selected_features,
            importance_report,
        ) = selector.run(
            X_train,
            y_train,
            feature_names,
            top_n=20,
        )

        # NOTE:
        # Apply the same selected feature indices
        # to X_test before evaluation.

        trainer = ModelTrainer()

        best_model, training_report = trainer.run(
            X_train_selected,
            y_train,
            X_test,
            y_test,
        )

        evaluator = ModelEvaluator()

        prediction_report, summary = (
            evaluator.run(
                best_model,
                X_test,
                y_test,
            )
        )

        logger.info(
            "Model evaluation completed successfully."
        )

    except Exception:

        logger.exception(
            "Model evaluation execution failed."
        )

        raise
