"""
==========================================================
AI-Powered Cybersecurity ML Pipeline
Part 2 - Model Training

Author : Pramod Prakash Jadhav
Python : 3.11+
==========================================================
"""

from __future__ import annotations

from typing import Dict

import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
)
from sklearn.model_selection import cross_val_score

from src.config import (
    RANDOM_STATE,
    N_ESTIMATORS,
    MAX_DEPTH,
    MIN_SAMPLES_SPLIT,
    MIN_SAMPLES_LEAF,
)

from src.logger import (
    logger,
    log_section,
    log_success,
)


class ModelTrainer:
    """
    Train, compare and select the best
    regression model.
    """

    def __init__(self) -> None:

        self.models: Dict[str, object] = {

            "Linear Regression":

                LinearRegression(),

            "Decision Tree":

                DecisionTreeRegressor(

                    random_state=RANDOM_STATE,

                    max_depth=MAX_DEPTH,

                    min_samples_split=MIN_SAMPLES_SPLIT,

                    min_samples_leaf=MIN_SAMPLES_LEAF,

                ),

            "Random Forest":

                RandomForestRegressor(

                    n_estimators=N_ESTIMATORS,

                    random_state=RANDOM_STATE,

                    max_depth=MAX_DEPTH,

                    min_samples_split=MIN_SAMPLES_SPLIT,

                    min_samples_leaf=MIN_SAMPLES_LEAF,

                    n_jobs=-1,

                ),

            "Gradient Boosting":

                GradientBoostingRegressor(

                    random_state=RANDOM_STATE,

                    n_estimators=150,

                    max_depth=3,

                ),

        }

        self.best_model_name: str | None = None

        self.best_model = None

        self.training_results = []

        logger.info(
            "%d models initialized.",
            len(self.models),
        )

    # ======================================================
    # LIST AVAILABLE MODELS
    # ======================================================

    def list_models(self) -> list[str]:
        """
        Return all available model names.
        """

        return list(self.models.keys())

    # ======================================================
    # GET MODEL
    # ======================================================

    def get_model(
        self,
        model_name: str,
    ):
        """
        Return a model by name.
        """

        if model_name not in self.models:

            raise ValueError(
                f"Unknown model: {model_name}"
            )

        return self.models[model_name]

    # ======================================================
    # MODEL SUMMARY
    # ======================================================

    def model_summary(self) -> None:
        """
        Display all configured models.
        """

        log_section(
            "Configured ML Models"
        )

        for name in self.models:

            logger.info(name)

        log_success(
            "Model configuration loaded."
)
      from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from src.config import CV_FOLDS


    # ======================================================
    # TRAIN SINGLE MODEL
    # ======================================================

    def train_model(
        self,
        model_name: str,
        X_train,
        y_train,
    ):
        """
        Train a single regression model.
        """

        log_section(
            f"Training : {model_name}"
        )

        model = self.get_model(model_name)

        model.fit(
            X_train,
            y_train,
        )

        logger.info(
            "%s training completed.",
            model_name,
        )

        return model


    # ======================================================
    # EVALUATE MODEL
    # ======================================================

    def evaluate_model(
        self,
        model_name: str,
        model,
        X_test,
        y_test,
    ) -> dict:
        """
        Evaluate a trained model.
        """

        predictions = model.predict(X_test)

        mae = mean_absolute_error(
            y_test,
            predictions,
        )

        rmse = mean_squared_error(
            y_test,
            predictions,
            squared=False,
        )

        r2 = r2_score(
            y_test,
            predictions,
        )

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

            "CV Mean": round(
                cv_scores.mean(),
                4,
            ),

            "CV Std": round(
                cv_scores.std(),
                4,
            ),

        }

        logger.info(
            "%s | MAE=%.4f | RMSE=%.4f | R²=%.4f",
            model_name,
            mae,
            rmse,
            r2,
        )

        return results


    # ======================================================
    # TRAIN ALL MODELS
    # ======================================================

    def train_all_models(
        self,
        X_train,
        y_train,
        X_test,
        y_test,
    ) -> pd.DataFrame:
        """
        Train and evaluate all configured models.
        """

        log_section(
            "Training All Models"
        )

        self.training_results.clear()

        for model_name in self.list_models():

            model = self.train_model(
                model_name,
                X_train,
                y_train,
            )

            metrics = self.evaluate_model(
                model_name,
                model,
                X_test,
                y_test,
            )

            metrics["Model Object"] = model

            self.training_results.append(
                metrics
            )

        results_df = pd.DataFrame(
            self.training_results
        )

        logger.info(
            "Successfully trained %d models.",
            len(results_df),
        )

        log_success(
            "Model training completed."
        )

        return results_df
      from src.config import OUTPUT_DIR

# ======================================================
# SELECT BEST MODEL
# ======================================================

    def select_best_model(
        self,
        results_df: pd.DataFrame,
    ):
        """
        Select the best model based on
        R² Score and RMSE.
        """

        log_section(
            "Selecting Best Model"
        )

        ranked = results_df.sort_values(
            by=["R2 Score", "RMSE"],
            ascending=[False, True],
        ).reset_index(drop=True)

        best_result = ranked.iloc[0]

        self.best_model_name = best_result["Model"]

        self.best_model = best_result["Model Object"]

        logger.info(
            "Best Model : %s",
            self.best_model_name,
        )

        logger.info(
            "Best R² Score : %.4f",
            best_result["R2 Score"],
        )

        logger.info(
            "Best RMSE : %.4f",
            best_result["RMSE"],
        )

        log_success(
            "Best model selected successfully."
        )

        return self.best_model


    # ======================================================
    # MODEL COMPARISON REPORT
    # ======================================================

    def model_comparison_report(
        self,
        results_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Create a sorted model comparison report.
        """

        report = (
            results_df
            .drop(columns=["Model Object"])
            .sort_values(
                by="R2 Score",
                ascending=False,
            )
            .reset_index(drop=True)
        )

        logger.info(
            "Model comparison report generated."
        )

        return report


    # ======================================================
    # DISPLAY RESULTS
    # ======================================================

    def display_results(
        self,
        report: pd.DataFrame,
    ) -> None:
        """
        Display model comparison summary.
        """

        log_section(
            "Model Comparison Results"
        )

        for _, row in report.iterrows():

            logger.info(
                "%s | R²=%.4f | RMSE=%.4f | MAE=%.4f",
                row["Model"],
                row["R2 Score"],
                row["RMSE"],
                row["MAE"],
            )

        log_success(
            "Comparison results displayed."
        )


    # ======================================================
    # EXPORT COMPARISON REPORT
    # ======================================================

    def save_comparison_report(
        self,
        report: pd.DataFrame,
    ) -> None:
        """
        Save comparison report as CSV.
        """

        report_file = (
            OUTPUT_DIR /
            "model_comparison.csv"
        )

        report.to_csv(
            report_file,
            index=False,
        )

        logger.info(
            "Comparison report saved: %s",
            report_file,
        )

        log_success(
            "Model comparison report exported."
)
      import json
from datetime import datetime

from src.config import (
    BEST_MODEL_FILE,
    METRICS_FILE,
    MODEL_METADATA_FILE,
)

from src.utils import save_model


    # ======================================================
    # SAVE BEST MODEL
    # ======================================================

    def save_best_model(
        self,
    ) -> None:
        """
        Save the best trained model.
        """

        log_section(
            "Saving Best Model"
        )

        if self.best_model is None:

            raise ValueError(
                "No trained model available."
            )

        save_model(
            self.best_model,
            BEST_MODEL_FILE,
        )

        logger.info(
            "Best model saved to %s",
            BEST_MODEL_FILE,
        )

        log_success(
            "Best model saved successfully."
        )


    # ======================================================
    # SAVE METRICS
    # ======================================================

    def save_metrics(
        self,
        report: pd.DataFrame,
    ) -> None:
        """
        Save model evaluation metrics.
        """

        metrics = (
            report.to_dict(
                orient="records"
            )
        )

        with open(
            METRICS_FILE,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                metrics,
                file,
                indent=4,
            )

        logger.info(
            "Metrics saved to %s",
            METRICS_FILE,
        )

        log_success(
            "Metrics exported successfully."
        )


    # ======================================================
    # SAVE MODEL METADATA
    # ======================================================

    def save_model_metadata(
        self,
        report: pd.DataFrame,
    ) -> None:
        """
        Save metadata about the best model.
        """

        best = report.iloc[0]

        metadata = {

            "model_name":
                self.best_model_name,

            "training_timestamp":
                datetime.now().isoformat(),

            "r2_score":
                float(best["R2 Score"]),

            "rmse":
                float(best["RMSE"]),

            "mae":
                float(best["MAE"]),

            "python_version":
                "3.11+",

        }

        with open(
            MODEL_METADATA_FILE,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                metadata,
                file,
                indent=4,
            )

        logger.info(
            "Model metadata saved."
        )

        log_success(
            "Metadata generation completed."
        )


    # ======================================================
    # TRAINING SUMMARY
    # ======================================================

    def training_summary(
        self,
        report: pd.DataFrame,
    ) -> None:
        """
        Display final training summary.
        """

        log_section(
            "Training Summary"
        )

        logger.info(
            "Models Trained : %d",
            len(report),
        )

        logger.info(
            "Best Model : %s",
            self.best_model_name,
        )

        logger.info(
            "Best R² Score : %.4f",
            report.iloc[0]["R2 Score"],
        )

        logger.info(
            "Best RMSE : %.4f",
            report.iloc[0]["RMSE"],
        )

        logger.info(
            "Best MAE : %.4f",
            report.iloc[0]["MAE"],
        )

        log_success(
            "Training summary generated."
)
   # ======================================================
    # COMPLETE MODEL TRAINING PIPELINE
    # ======================================================

    def run(
        self,
        X_train,
        y_train,
        X_test,
        y_test,
    ):
        """
        Execute the complete model training pipeline.
        """

        log_section(
            "Starting Model Training Pipeline"
        )

        try:

            # Step 1
            results_df = self.train_all_models(
                X_train,
                y_train,
                X_test,
                y_test,
            )

            # Step 2
            self.select_best_model(results_df)

            # Step 3
            report = self.model_comparison_report(
                results_df
            )

            # Step 4
            self.display_results(report)

            # Step 5
            self.save_comparison_report(report)

            # Step 6
            self.save_best_model()

            # Step 7
            self.save_metrics(report)

            # Step 8
            self.save_model_metadata(report)

            # Step 9
            self.training_summary(report)

            log_success(
                "Model training pipeline completed successfully."
            )

            return (
                self.best_model,
                report,
            )

        except Exception:

            logger.exception(
                "Model training pipeline failed."
            )

            raise


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    from src.data_loader import DataLoader
    from src.preprocessing import Preprocessor
    from src.feature_selection import FeatureSelector

    try:

        log_section(
            "Model Training Module"
        )

        # Load data
        loader = DataLoader()
        dataframe = loader.run()

        # Preprocessing
        preprocessor = Preprocessor()

        (
            X_train,
            X_test,
            y_train,
            y_test,
            fitted_preprocessor,
        ) = preprocessor.run(dataframe)

        # Feature Selection
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
        # X_test should also be transformed using
        # the same selected feature indices before
        # evaluation.

        trainer = ModelTrainer()

        best_model, report = trainer.run(
            X_train_selected,
            y_train,
            X_test,
            y_test,
        )

        logger.info(
            "Best Model : %s",
            trainer.best_model_name,
        )

        logger.info(
            "Training completed successfully."
        )

    except Exception:

        logger.exception(
            "Model training execution failed."
        )

        raise   
