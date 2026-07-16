"""
==========================================================
AI-Powered Cybersecurity ML Pipeline
Part 2 - End-to-End ML Pipeline

Author : Pramod Prakash Jadhav
Python : 3.11+
==========================================================
"""

from __future__ import annotations

from datetime import datetime
import time

from src.logger import (
    logger,
    log_section,
    log_success,
)

from src.data_loader import DataLoader
from src.preprocessing import Preprocessor
from src.feature_selection import FeatureSelector
from src.model_training import ModelTrainer
from src.model_evaluation import ModelEvaluator
from src.predict import Predictor


class MLPipeline:
    """
    End-to-End Machine Learning Pipeline.

    Responsibilities
    ----------------
    1. Load data
    2. Preprocess data
    3. Select features
    4. Train models
    5. Evaluate best model
    6. Generate predictions
    7. Export reports
    """

    def __init__(self) -> None:
        """
        Initialize all pipeline modules.
        """

        log_section(
            "Initializing ML Pipeline"
        )

        self.data_loader = DataLoader()

        self.preprocessor = Preprocessor()

        self.feature_selector = FeatureSelector()

        self.model_trainer = ModelTrainer()

        self.model_evaluator = ModelEvaluator()

        self.predictor = Predictor()

        self.pipeline_start_time = None

        self.pipeline_end_time = None

        self.pipeline_summary = {}

        logger.info(
            "All pipeline modules initialized."
        )

        log_success(
            "ML Pipeline initialized successfully."
        )

    # ======================================================
    # START PIPELINE TIMER
    # ======================================================

    def start_pipeline(self) -> None:
        """
        Start execution timer.
        """

        self.pipeline_start_time = time.time()

        logger.info(
            "Pipeline started at %s",
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        )

    # ======================================================
    # STOP PIPELINE TIMER
    # ======================================================

    def stop_pipeline(self) -> None:
        """
        Stop execution timer.
        """

        self.pipeline_end_time = time.time()

        execution_time = (
            self.pipeline_end_time
            - self.pipeline_start_time
        )

        self.pipeline_summary[
            "execution_time_seconds"
        ] = round(
            execution_time,
            2,
        )

        logger.info(
            "Pipeline execution time: %.2f seconds",
            execution_time,
        )

    # ======================================================
    # PIPELINE HEALTH CHECK
    # ======================================================

    def health_check(self) -> bool:
        """
        Verify that all pipeline modules
        are initialized correctly.
        """

        modules = [

            self.data_loader,

            self.preprocessor,

            self.feature_selector,

            self.model_trainer,

            self.model_evaluator,

            self.predictor,

        ]

        status = all(
            module is not None
            for module in modules
        )

        if status:

            logger.info(
                "Pipeline health check passed."
            )

        else:

            logger.error(
                "Pipeline health check failed."
            )

        return status
      # ======================================================
    # LOAD DATA
    # ======================================================

    def load_data(self):
        """
        Load raw dataset.
        """

        log_section(
            "Loading Dataset"
        )

        dataframe = self.data_loader.run()

        self.pipeline_summary[
            "total_records"
        ] = len(dataframe)

        self.pipeline_summary[
            "total_columns"
        ] = len(dataframe.columns)

        logger.info(
            "Dataset loaded successfully."
        )

        log_success(
            "Data loading completed."
        )

        return dataframe


    # ======================================================
    # PREPROCESS DATA
    # ======================================================

    def preprocess_data(
        self,
        dataframe,
    ):
        """
        Execute preprocessing pipeline.
        """

        log_section(
            "Preprocessing Dataset"
        )

        (
            X_train,
            X_test,
            y_train,
            y_test,
            fitted_preprocessor,
        ) = self.preprocessor.run(
            dataframe
        )

        logger.info(
            "Preprocessing completed successfully."
        )

        log_success(
            "Dataset preprocessing completed."
        )

        return (
            X_train,
            X_test,
            y_train,
            y_test,
            fitted_preprocessor,
        )


    # ======================================================
    # FEATURE SELECTION
    # ======================================================

    def select_features(
        self,
        X_train,
        X_test,
        y_train,
        fitted_preprocessor,
        top_n: int = 20,
    ):
        """
        Perform feature selection.
        """

        log_section(
            "Selecting Features"
        )

        feature_names = list(
            fitted_preprocessor.get_feature_names_out()
        )

        (
            X_train_selected,
            selected_features,
            feature_importance,
        ) = self.feature_selector.run(
            X_train=X_train,
            y_train=y_train,
            feature_names=feature_names,
            top_n=top_n,
        )

        # --------------------------------------------------
        # Apply the same selected features to X_test
        # --------------------------------------------------

        if hasattr(
            self.feature_selector,
            "selected_feature_indices_",
        ):

            X_test_selected = X_test[
                :,
                self.feature_selector.selected_feature_indices_,
            ]

        else:

            logger.warning(
                "Selected feature indices not found. "
                "Using original X_test."
            )

            X_test_selected = X_test

        self.pipeline_summary[
            "selected_features"
        ] = len(
            selected_features
        )

        logger.info(
            "%d features selected.",
            len(selected_features),
        )

        log_success(
            "Feature selection completed."
        )

        return (
            X_train_selected,
            X_test_selected,
            selected_features,
            feature_importance,
  )
      # ======================================================
    # MODEL TRAINING
    # ======================================================

    def train_model(
        self,
        X_train,
        X_test,
        y_train,
        y_test,
    ):
        """
        Train machine learning models and
        select the best performing model.
        """

        log_section(
            "Training Machine Learning Models"
        )

        best_model, training_report = (
            self.model_trainer.run(
                X_train,
                y_train,
                X_test,
                y_test,
            )
        )

        self.pipeline_summary[
            "best_model"
        ] = self.model_trainer.best_model_name

        self.pipeline_summary[
            "models_trained"
        ] = len(training_report)

        logger.info(
            "Best model selected: %s",
            self.model_trainer.best_model_name,
        )

        log_success(
            "Model training completed."
        )

        return (
            best_model,
            training_report,
        )


    # ======================================================
    # MODEL EVALUATION
    # ======================================================

    def evaluate_model(
        self,
        model,
        X_test,
        y_test,
    ):
        """
        Evaluate the trained model.
        """

        log_section(
            "Evaluating Best Model"
        )

        (
            prediction_report,
            evaluation_summary,
        ) = self.model_evaluator.run(
            model,
            X_test,
            y_test,
        )

        self.pipeline_summary[
            "r2_score"
        ] = (
            evaluation_summary["metrics"]
            ["R2 Score"]
        )

        self.pipeline_summary[
            "rmse"
        ] = (
            evaluation_summary["metrics"]
            ["RMSE"]
        )

        self.pipeline_summary[
            "mae"
        ] = (
            evaluation_summary["metrics"]
            ["MAE"]
        )

        logger.info(
            "Model evaluation completed successfully."
        )

        log_success(
            "Evaluation pipeline completed."
        )

        return (
            prediction_report,
            evaluation_summary,
        )


    # ======================================================
    # DISPLAY TRAINING SUMMARY
    # ======================================================

    def display_training_summary(
        self,
    ) -> None:
        """
        Display model training and evaluation summary.
        """

        log_section(
            "Training Summary"
        )

        logger.info(
            "Best Model : %s",
            self.pipeline_summary.get(
                "best_model",
                "N/A",
            ),
        )

        logger.info(
            "Models Trained : %s",
            self.pipeline_summary.get(
                "models_trained",
                "N/A",
            ),
        )

        logger.info(
            "R² Score : %.4f",
            self.pipeline_summary.get(
                "r2_score",
                0.0,
            ),
        )

        logger.info(
            "RMSE : %.4f",
            self.pipeline_summary.get(
                "rmse",
                0.0,
            ),
        )

        logger.info(
            "MAE : %.4f",
            self.pipeline_summary.get(
                "mae",
                0.0,
            ),
        )

        log_success(
            "Training summary displayed."
  )
      # ======================================================
    # PREDICTION PIPELINE
    # ======================================================

    def generate_predictions(
        self,
        dataframe,
    ):
        """
        Generate predictions using the trained model.
        """

        log_section(
            "Generating Predictions"
        )

        prediction_report, prediction_summary = (
            self.predictor.run(
                dataframe
            )
        )

        self.pipeline_summary[
            "total_predictions"
        ] = prediction_summary[
            "total_predictions"
        ]

        logger.info(
            "Prediction pipeline completed."
        )

        log_success(
            "Predictions generated successfully."
        )

        return (
            prediction_report,
            prediction_summary,
        )


    # ======================================================
    # VERIFY GENERATED ARTIFACTS
    # ======================================================

    def verify_artifacts(
        self,
    ) -> bool:
        """
        Verify that required model artifacts exist.
        """

        log_section(
            "Verifying Pipeline Artifacts"
        )

        artifacts = [

            self.predictor.model_path,

            self.predictor.preprocessor_path,

        ]

        missing = []

        for artifact in artifacts:

            if not artifact.exists():

                missing.append(str(artifact))

        if missing:

            logger.error(
                "Missing artifacts: %s",
                ", ".join(missing),
            )

            return False

        logger.info(
            "All required artifacts verified."
        )

        log_success(
            "Artifact verification completed."
        )

        return True


    # ======================================================
    # PIPELINE SUMMARY REPORT
    # ======================================================

    def pipeline_report(
        self,
    ) -> dict:
        """
        Return pipeline execution summary.
        """

        log_section(
            "Pipeline Summary"
        )

        logger.info(
            "Summary: %s",
            self.pipeline_summary,
        )

        return self.pipeline_summary


    # ======================================================
    # DISPLAY PIPELINE SUMMARY
    # ======================================================

    def display_pipeline_summary(
        self,
    ) -> None:
        """
        Display end-to-end pipeline summary.
        """

        log_section(
            "End-to-End Pipeline Summary"
        )

        for key, value in self.pipeline_summary.items():

            logger.info(
                "%s : %s",
                key,
                value,
            )

        log_success(
            "Pipeline summary displayed."
      )
      # ======================================================
    # COMPLETE END-TO-END PIPELINE
    # ======================================================

    def run(self) -> dict:
        """
        Execute the complete machine learning pipeline.
        """

        log_section(
            "Starting End-to-End ML Pipeline"
        )

        try:

            self.start_pipeline()

            if not self.health_check():

                raise RuntimeError(
                    "Pipeline health check failed."
                )

            # ---------------------------------------------
            # Step 1 : Load Data
            # ---------------------------------------------

            dataframe = self.load_data()

            # ---------------------------------------------
            # Step 2 : Preprocessing
            # ---------------------------------------------

            (
                X_train,
                X_test,
                y_train,
                y_test,
                fitted_preprocessor,
            ) = self.preprocess_data(
                dataframe
            )

            # ---------------------------------------------
            # Step 3 : Feature Selection
            # ---------------------------------------------

            (
                X_train_selected,
                X_test_selected,
                selected_features,
                feature_importance,
            ) = self.select_features(
                X_train,
                X_test,
                y_train,
                fitted_preprocessor,
            )

            # ---------------------------------------------
            # Step 4 : Model Training
            # ---------------------------------------------

            (
                best_model,
                training_report,
            ) = self.train_model(
                X_train_selected,
                X_test_selected,
                y_train,
                y_test,
            )

            # ---------------------------------------------
            # Step 5 : Model Evaluation
            # ---------------------------------------------

            (
                prediction_report,
                evaluation_summary,
            ) = self.evaluate_model(
                best_model,
                X_test_selected,
                y_test,
            )

            # ---------------------------------------------
            # Step 6 : Prediction
            # ---------------------------------------------

            prediction_results, prediction_summary = (
                self.generate_predictions(
                    dataframe
                )
            )

            # ---------------------------------------------
            # Step 7 : Verify Artifacts
            # ---------------------------------------------

            self.verify_artifacts()

            # ---------------------------------------------
            # Step 8 : Stop Timer
            # ---------------------------------------------

            self.stop_pipeline()

            # ---------------------------------------------
            # Step 9 : Display Summary
            # ---------------------------------------------

            self.display_training_summary()

            self.display_pipeline_summary()

            log_success(
                "End-to-End ML Pipeline completed successfully."
            )

            return self.pipeline_summary

        except Exception:

            logger.exception(
                "Pipeline execution failed."
            )

            raise


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    try:

        pipeline = MLPipeline()

        summary = pipeline.run()

        logger.info(
            "Pipeline executed successfully."
        )

        logger.info(
            "Execution Summary: %s",
            summary,
        )

    except Exception:

        logger.exception(
            "Pipeline execution aborted."
        )

        raise
      
