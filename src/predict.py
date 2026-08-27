"""Production prediction module with an explicit training feature contract."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
from src.config import BEST_MODEL_FILE, FEATURE_IMPORTANCE_FILE, MODEL_METADATA_FILE, PREPROCESSOR_FILE, PREDICTION_OUTPUT_FILE, PREDICTION_COLUMN, PREDICTION_SUMMARY_FILE
from src.logger import logger, log_success
from src.utils import load_model


class Predictor:
    def __init__(self, model_path: Path = BEST_MODEL_FILE, preprocessor_path: Path = PREPROCESSOR_FILE):
        self.model_path, self.preprocessor_path = model_path, preprocessor_path
        self.model = None
        self.preprocessor = None
        self.selected_feature_names: list[str] = []

    def load_trained_model(self):
        self.model = load_model(self.model_path)
        return self.model

    def load_preprocessor(self):
        self.preprocessor = load_model(self.preprocessor_path)
        return self.preprocessor

    def load_feature_contract(self):
        if not MODEL_METADATA_FILE.exists():
            raise FileNotFoundError("Model metadata is required to load the training feature contract.")
        with open(MODEL_METADATA_FILE, "r", encoding="utf-8") as file:
            metadata = json.load(file)
        names = metadata.get("selected_feature_names")
        if not isinstance(names, list) or not names:
            raise ValueError("Model metadata does not contain selected_feature_names.")
        self.selected_feature_names = names

    def load_artifacts(self):
        self.load_trained_model(); self.load_preprocessor(); self.load_feature_contract()

    @staticmethod
    def validate_input(data):
        if not isinstance(data, pd.DataFrame) or data.empty:
            raise ValueError("Prediction input must be a non-empty pandas DataFrame.")

    def _align_selected_features(self, transformed_data):
        if self.preprocessor is None or self.model is None:
            raise ValueError("Prediction artifacts are not loaded.")
        if not self.selected_feature_names:
            raise ValueError("Training feature contract is not loaded.")
        names = list(self.preprocessor.get_feature_names_out())
        missing = [name for name in self.selected_feature_names if name not in names]
        if missing:
            raise ValueError(f"Selected training features are missing from prediction preprocessor output: {missing}")
        indices = [names.index(name) for name in self.selected_feature_names]
        if len(indices) != getattr(self.model, "n_features_in_", len(indices)):
            raise ValueError("Training feature contract does not match model feature count.")
        return transformed_data[:, indices]

    def preprocess_input(self, data):
        self.validate_input(data)
        if self.preprocessor is None:
            raise ValueError("Preprocessor has not been loaded.")
        transformed = self.preprocessor.transform(data)
        return self._align_selected_features(transformed)

    def predict_batch(self, data):
        processed = self.preprocess_input(data)
        predictions = np.asarray(self.model.predict(processed), dtype=float)
        if not np.isfinite(predictions).all():
            raise ValueError("Model produced non-finite predictions.")
        result = data.copy(); result[PREDICTION_COLUMN] = predictions
        return result

    def prediction_statistics(self, predictions):
        values = predictions[PREDICTION_COLUMN]
        if values.empty or not np.isfinite(values.to_numpy(dtype=float)).all():
            raise ValueError("Prediction values must be finite and non-empty.")
        return {"total_predictions": int(len(values)), "minimum_prediction": float(values.min()), "maximum_prediction": float(values.max()), "mean_prediction": float(values.mean()), "standard_deviation": float(values.std())}

    def create_prediction_report(self, predictions):
        report = predictions.copy(); report["prediction_timestamp"] = datetime.now(timezone.utc).isoformat(); report["prediction_id"] = range(1, len(report) + 1); return report

    def export_predictions(self, report):
        report.to_csv(PREDICTION_OUTPUT_FILE, index=False)

    def save_prediction_summary(self, summary):
        payload = dict(summary); payload["generated_at"] = datetime.now(timezone.utc).isoformat()
        with open(PREDICTION_SUMMARY_FILE, "w", encoding="utf-8") as file: json.dump(payload, file, indent=4)

    def reset(self):
        self.model = self.preprocessor = None; self.selected_feature_names = []

    def health_check(self):
        return self.model is not None and self.preprocessor is not None and bool(self.selected_feature_names)

    def ensure_loaded(self):
        if self.model is None or self.preprocessor is None or not self.selected_feature_names: self.load_artifacts()

    def run(self, input_data):
        self.ensure_loaded(); predictions = self.predict_batch(input_data); report = self.create_prediction_report(predictions); self.export_predictions(report); summary = self.prediction_statistics(report); self.save_prediction_summary(summary); log_success("Prediction pipeline completed successfully."); return report, summary
