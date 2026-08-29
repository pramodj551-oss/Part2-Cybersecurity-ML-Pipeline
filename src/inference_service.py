"""STEP 24 API security, observability and production hardening."""
from __future__ import annotations
import json
import logging
import os
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from src.config import BEST_MODEL_FILE, PREPROCESSOR_FILE, MODEL_METADATA_FILE, NUMERICAL_FEATURES, CATEGORICAL_FEATURES

logger = logging.getLogger("inference")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(message)s")
app = FastAPI(title="Cybersecurity ML Inference Service", version="24.0", docs_url=None if os.getenv("DISABLE_DOCS", "false").lower()=="true" else "/docs")
app.add_middleware(CORSMiddleware, allow_origins=[], allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["X-API-Key", "Content-Type"])
REQUIRED_FEATURES = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
API_KEY = os.getenv("INFERENCE_API_KEY")
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
_requests: dict[str, deque[float]] = defaultdict(deque)

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
    def __init__(self): self.model=None; self.preprocessor=None; self.metadata={}
    def ready(self): return BEST_MODEL_FILE.exists() and PREPROCESSOR_FILE.exists() and MODEL_METADATA_FILE.exists()
    def load(self):
        if not self.ready(): raise FileNotFoundError("Required model artifacts are not available.")
        self.model=joblib.load(BEST_MODEL_FILE); self.preprocessor=joblib.load(PREPROCESSOR_FILE)
        self.metadata=json.loads(Path(MODEL_METADATA_FILE).read_text(encoding="utf-8")); return self
    def predict(self,payload):
        if self.model is None: self.load()
        frame=pd.DataFrame([payload],columns=REQUIRED_FEATURES); transformed=self.preprocessor.transform(frame)
        names=list(self.preprocessor.get_feature_names_out()); selected=self.metadata.get("selected_feature_names",[])
        if selected:
            missing=[n for n in selected if n not in names]
            if missing: raise ValueError(f"Model contract mismatch: missing selected features {missing}")
            transformed=transformed[:,[names.index(n) for n in selected]]
        return float(np.asarray(self.model.predict(transformed)).reshape(-1)[0])

runtime=ModelRuntime()

def audit(event, request: Request, **extra):
    logger.info(json.dumps({"event":event,"method":request.method,"path":request.url.path,"client":request.client.host if request.client else None,"timestamp":datetime.now(timezone.utc).isoformat(),**extra}))

def protected(request: Request, api_key: str | None):
    if API_KEY and api_key != API_KEY:
        audit("authentication_failed", request); raise HTTPException(status_code=401, detail="Unauthorized")
    if request.url.path == "/predict":
        now=time.monotonic(); bucket=_requests[request.client.host if request.client else "unknown"]
        while bucket and now-bucket[0] >= 60: bucket.popleft()
        if len(bucket) >= RATE_LIMIT:
            audit("rate_limit_exceeded", request); raise HTTPException(status_code=429, detail="Rate limit exceeded")
        bucket.append(now)

@app.middleware("http")
async def security_headers(request: Request, call_next):
    start=time.perf_counter(); response=await call_next(request)
    response.headers["X-Content-Type-Options"]="nosniff"; response.headers["X-Frame-Options"]="DENY"; response.headers["Cache-Control"]="no-store"
    audit("request",request,status_code=response.status_code,duration_ms=round((time.perf_counter()-start)*1000,2))
    return response

@app.get("/health")
def health(request: Request): return {"status":"ok","timestamp":datetime.now(timezone.utc).isoformat()}
@app.get("/ready")
def ready(request: Request, x_api_key: str | None = Header(default=None)):
    protected(request,x_api_key)
    if not runtime.ready(): raise HTTPException(status_code=503,detail="Model artifacts are not ready")
    return {"status":"ready"}
@app.get("/model-info")
def model_info(request: Request, x_api_key: str | None = Header(default=None)):
    protected(request,x_api_key)
    if not runtime.ready(): raise HTTPException(status_code=503,detail="Model artifacts are not ready")
    metadata=json.loads(Path(MODEL_METADATA_FILE).read_text(encoding="utf-8"))
    return {"model":metadata.get("model_name"),"metrics":{k:metadata.get(k) for k in ("r2_score","rmse","mae","cv_mean")},"required_features":REQUIRED_FEATURES}
@app.post("/predict")
def predict(request: Request, payload: PredictionRequest, x_api_key: str | None = Header(default=None)):
    protected(request,x_api_key)
    try:
        score=runtime.predict(payload.model_dump()); audit("prediction",request,model=runtime.metadata.get("model_name")); return {"prediction":score,"model":runtime.metadata.get("model_name")}
    except FileNotFoundError as exc: raise HTTPException(status_code=503,detail=str(exc)) from exc
    except ValueError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc
    except Exception as exc: logger.exception("prediction_failed"); raise HTTPException(status_code=500,detail="Prediction failed") from exc
