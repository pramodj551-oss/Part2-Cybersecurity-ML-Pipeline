"""STEP 23 production inference service."""
from __future__ import annotations
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from src.config import BEST_MODEL_FILE, PREPROCESSOR_FILE, MODEL_METADATA_FILE, NUMERICAL_FEATURES, CATEGORICAL_FEATURES

logger = logging.getLogger("inference")
app = FastAPI(title="Cybersecurity ML Inference Service", version="23.0")
REQUIRED_FEATURES = NUMERICAL_FEATURES + CATEGORICAL_FEATURES

class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    records_affected: float = Field(ge=0)
    detection_time_hours: float = Field(ge=0)
    ransom_demand_usd: float = Field(ge=0)
    sector: str
    region: str
    attack_type: str
    threat_actor: str
    data_exfiltration: str | int | bool
    zero_day_used: str | int | bool

class ModelRuntime:
    def __init__(self):
        self.model = None; self.preprocessor = None; self.metadata = {}
    def ready(self) -> bool:
        return BEST_MODEL_FILE.exists() and PREPROCESSOR_FILE.exists() and MODEL_METADATA_FILE.exists()
    def load(self):
        if not self.ready():
            raise FileNotFoundError("Required model artifacts are not available.")
        self.model = joblib.load(BEST_MODEL_FILE)
        self.preprocessor = joblib.load(PREPROCESSOR_FILE)
        self.metadata = json.loads(Path(MODEL_METADATA_FILE).read_text(encoding="utf-8"))
        return self
    def predict(self, payload: dict) -> float:
        if self.model is None: self.load()
        frame = pd.DataFrame([payload], columns=REQUIRED_FEATURES)
        transformed = self.preprocessor.transform(frame)
        names = list(self.preprocessor.get_feature_names_out())
        selected = self.metadata.get("selected_feature_names", [])
        if selected:
            missing = [name for name in selected if name not in names]
            if missing: raise ValueError(f"Model contract mismatch: missing selected features {missing}")
            indices = [names.index(name) for name in selected]
            transformed = transformed[:, indices]
        return float(np.asarray(self.model.predict(transformed)).reshape(-1)[0])

runtime = ModelRuntime()

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/ready")
def ready():
    if not runtime.ready(): raise HTTPException(status_code=503, detail="Model artifacts are not ready")
    return {"status": "ready"}

@app.get("/model-info")
def model_info():
    if not runtime.ready(): raise HTTPException(status_code=503, detail="Model artifacts are not ready")
    metadata = json.loads(Path(MODEL_METADATA_FILE).read_text(encoding="utf-8"))
    return {"model": metadata.get("model_name"), "metrics": {k: metadata.get(k) for k in ("r2_score","rmse","mae","cv_mean")}, "required_features": REQUIRED_FEATURES}

@app.post("/predict")
def predict(request: PredictionRequest):
    try:
        score = runtime.predict(request.model_dump())
        logger.info(json.dumps({"event":"prediction","model":runtime.metadata.get("model_name"),"timestamp":datetime.now(timezone.utc).isoformat()}))
        return {"prediction": score, "model": runtime.metadata.get("model_name")}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("prediction_failed")
        raise HTTPException(status_code=500, detail="Prediction failed") from exc
