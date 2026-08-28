"""End-to-end orchestration for the cybersecurity regression pipeline."""
from __future__ import annotations

import time
from datetime import datetime, timezone

from src.config import FEATURE_SELECTION_TOP_N
from src.data_loader import DataLoader
from src.preprocessing import Preprocessor
from src.feature_selection import FeatureSelector
from src.model_training import ModelTrainer
from src.model_evaluation import ModelEvaluator
from src.predict import Predictor
from src.logger import logger, log_success


class MLPipeline:
    def __init__(self):
        self.data_loader = DataLoader()
        self.preprocessor = Preprocessor()
        self.feature_selector = FeatureSelector()
        self.model_trainer = ModelTrainer()
        self.model_evaluator = ModelEvaluator()
        self.predictor = Predictor()
        self.pipeline_summary = {}
        self.pipeline_start_time = None
        self.pipeline_end_time = None

    def health_check(self):
        return all(x is not None for x in [
            self.data_loader, self.preprocessor, self.feature_selector,
            self.model_trainer, self.model_evaluator, self.predictor,
        ])

    def load_data(self):
        df = self.data_loader.run()
        self.pipeline_summary.update(total_records=len(df), total_columns=len(df.columns))
        return df

    def preprocess_data(self, dataframe):
        return self.preprocessor.run(dataframe)

    def select_features(self, X_train, X_test, y_train, fitted_preprocessor, top_n=FEATURE_SELECTION_TOP_N):
        names = list(fitted_preprocessor.get_feature_names_out())
        X_train_selected, selected, importance = self.feature_selector.run(
            X=X_train, y=y_train, feature_names=names, top_n=top_n
        )
        if not self.feature_selector.selected_feature_indices_:
            raise RuntimeError("Feature selection produced no selected feature indices.")
        X_test_selected = X_test[:, self.feature_selector.selected_feature_indices_]
        self.pipeline_summary["selected_features"] = len(selected)
        return X_train_selected, X_test_selected, selected, importance

    def train_model(self, X_train, X_test, y_train, y_test, selected_features=None, raw_train_df=None):
        best, report = self.model_trainer.run(
            X_train,
            y_train,
            X_test,
            y_test,
            selected_features=selected_features,
            raw_train_df=raw_train_df,
            top_n=len(selected_features or []),
        )
        self.pipeline_summary.update(
            best_model=self.model_trainer.best_model_name,
            models_trained=len(report),
            cv_method="fold_safe_preprocessing_and_feature_selection",
        )
        return best, report

    def evaluate_model(self, model, X_test, y_test):
        result, summary = self.model_evaluator.run(model, X_test, y_test)
        self.pipeline_summary.update(
            r2_score=summary["metrics"]["R2 Score"],
            rmse=summary["metrics"]["RMSE"],
            mae=summary["metrics"]["MAE"],
        )
        return result, summary

    def generate_predictions(self, dataframe, model=None, preprocessor=None, selected_features=None):
        if model is not None:
            self.predictor.model = model
        if preprocessor is not None:
            self.predictor.preprocessor = preprocessor
        if selected_features is not None:
            self.predictor.selected_feature_names = list(selected_features)
        report, summary = self.predictor.run(dataframe)
        self.pipeline_summary["total_predictions"] = summary["total_predictions"]
        return report, summary

    def verify_artifacts(self):
        required = [self.predictor.model_path, self.predictor.preprocessor_path]
        required.append(self.predictor.model_path.parent / "model_metadata.json")
        missing = [str(p) for p in required if not p.exists()]
        if missing:
            raise FileNotFoundError("Missing required artifacts: " + ", ".join(missing))
        return True

    def run(self):
        if not self.health_check():
            raise RuntimeError("Pipeline health check failed.")
        self.pipeline_start_time = time.perf_counter()
        try:
            df = self.load_data()
            X_train, X_test, y_train, y_test, preprocessor = self.preprocess_data(df)

            # Use the exact cleaned train split before global imputation so
            # every CV fold can fit its own preprocessing from fold-train rows.
            raw_train_df = self.preprocessor.train_df_before_imputation_
            if raw_train_df is None:
                raise RuntimeError("Fold-safe CV requires the pre-imputation training split.")

            Xtr, Xte, selected, _ = self.select_features(
                X_train, X_test, y_train, preprocessor, top_n=FEATURE_SELECTION_TOP_N
            )
            best, report = self.train_model(
                Xtr,
                Xte,
                y_train,
                y_test,
                selected_features=selected,
                raw_train_df=raw_train_df,
            )
            self.evaluate_model(best, Xte, y_test)
            self.generate_predictions(
                df,
                model=best,
                preprocessor=preprocessor,
                selected_features=selected,
            )
            self.verify_artifacts()
            self.pipeline_end_time = time.perf_counter()
            self.pipeline_summary["execution_time_seconds"] = round(
                self.pipeline_end_time - self.pipeline_start_time, 2
            )
            self.pipeline_summary["completed_at"] = datetime.now(timezone.utc).isoformat()
            log_success("End-to-End ML Pipeline completed successfully with fold-safe CV.")
            return self.pipeline_summary
        except Exception:
            logger.exception("Pipeline execution failed.")
            raise
