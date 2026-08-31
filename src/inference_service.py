"""Production inference service with mandatory API-key authentication, rate limiting and Prometheus metrics."""
from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client.exposition import CONTENT_TYPE_LATEST
from pydantic import BaseModel, ConfigDict, Field
from starlette.responses import Response

from src.config import (
    BEST_MODEL_FILE, PREPROCESSOR_FILE, MODEL_METADATA_FILE,
    NUMERICAL_FEATURES, CATEGORICAL_FEATURES,
)

logger = logging.getLogger("inference")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(message)s")

app = FastAPI(title="Cybersecurity ML Inference Service", version="31.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key", "Content-Type"],
)

REQUIRED_FEATURES = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
REDIS_URL = os.getenv("REDIS_URL")
RATE_LIMIT_PREFIX = os.getenv("RATE_LIMIT_PREFIX", "cybersecurity_ml:rate_limit")
RATE_LIMIT_MODE = os.getenv("RATE_LIMIT_MODE", "auto").lower()
# Backward-compatible module attribute for existing tests/integrations. Runtime
# authentication still prefers the current environment variable when present.
API_KEY = os.getenv("INFERENCE_API_KEY")
_redis_client = None
_local_requests: dict[str, list[float]] = {}
_requests = _local_requests

class MetricsDict(dict):
    _defaults = {"requests_total": 0, "errors_total": 0, "predictions_total": 0}
    def __getitem__(self, key):
        return super().get(key, 0)
    def clear(self):
        super().clear()
        super().update(self._defaults)

METRICS = MetricsDict(MetricsDict._defaults)

def _metric_value(name: str) -> int:
    return METRICS.setdefault(name, 0)
LATENCIES: list[float] = []

REQUEST_COUNT = Counter("inference_http_requests_total", "HTTP requests processed", ["method", "path", "status"])
REQUEST_LATENCY = Histogram("inference_http_request_duration_seconds", "HTTP request latency", ["method", "path"])
ERROR_COUNT = Counter("inference_errors_total", "Inference service errors", ["type"])
PREDICTION_COUNT = Counter("inference_predictions_total", "Predictions completed", ["outcome"])
RATE_LIMIT_COUNT = Counter("inference_rate_limit_exceeded_total", "Rate-limit rejections", ["backend"])


def _redis():
    global _redis_client
    if not REDIS_URL:
        return None
    if _redis_client is None:
        import redis
        _redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=1, socket_timeout=1)
    return _redis_client


def _allow_request(client_id: str) -> tuple[bool, str]:
    now = int(time.time())
    window = now // 60
    key = f"{RATE_LIMIT_PREFIX}:{client_id}:{window}"
    try:
        client = _redis()
        if client is not None:
            count = int(client.incr(key))
            if count == 1:
                client.expire(key, 61)
            return count <= RATE_LIMIT, "redis"
    except Exception as exc:
        logger.warning(json.dumps({"event": "redis_rate_limit_unavailable", "error": type(exc).__name__}))
        if RATE_LIMIT_MODE == "redis":
            raise HTTPException(503, "Rate limiting backend unavailable") from exc
    bucket = [stamp for stamp in _local_requests.get(client_id, []) if now - stamp < 60]
    allowed = len(bucket) < RATE_LIMIT
    if allowed:
        bucket.append(now)
    _local_requests[client_id] = bucket
    return allowed, "memory"


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
        self.model = None
        self.preprocessor = None
        self.metadata: dict[str, Any] = {}

    def ready(self):
        return BEST_MODEL_FILE.exists() and PREPROCESSOR_FILE.exists() and MODEL_METADATA_FILE.exists()

    def load(self):
        if not self.ready():
            raise FileNotFoundError("Required model artifacts are not available.")
        self.model = joblib.load(BEST_MODEL_FILE)
        self.preprocessor = joblib.load(PREPROCESSOR_FILE)
        self.metadata = json.loads(Path(MODEL_METADATA_FILE).read_text(encoding="utf-8"))
        return self

    def predict(self, payload):
        if self.model is None:
            self.load()
        frame = pd.DataFrame([payload], columns=REQUIRED_FEATURES)
        transformed = self.preprocessor.transform(frame)
        names = list(self.preprocessor.get_feature_names_out())
        selected = self.metadata.get("selected_feature_names", [])
        if selected:
            missing = [name for name in selected if name not in names]
            if missing:
                raise ValueError(f"Model contract mismatch: missing selected features {missing}")
            transformed = transformed[:, [names.index(name) for name in selected]]
        return float(np.asarray(self.model.predict(transformed)).reshape(-1)[0])

runtime = ModelRuntime()


def audit(event, request, **extra):
    logger.info(json.dumps({
        "event": event,
        "method": request.method,
        "path": request.url.path,
        "client": request.client.host if request.client else None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **extra,
    }))


def require_api_key(request: Request, api_key: str | None) -> None:
    configured_key = os.getenv("INFERENCE_API_KEY")
    # Preserve test/integration compatibility with the historical module
    # attribute while keeping the deployment environment as the source of truth.
    expected = configured_key if configured_key is not None else API_KEY
    if not expected:
        ERROR_COUNT.labels(type="authentication_configuration").inc()
        audit("authentication_configuration_missing", request)
        raise HTTPException(503, "Inference API authentication is not configured")
    if api_key != expected:
        ERROR_COUNT.labels(type="authentication").inc()
        audit("authentication_failed", request)
        raise HTTPException(401, "Unauthorized")


def protected(request: Request, api_key: str | None):
    require_api_key(request, api_key)
    if request.url.path == "/predict":
        client_id = request.client.host if request.client else "unknown"
        allowed, backend = _allow_request(client_id)
        if not allowed:
            ERROR_COUNT.labels(type="rate_limit").inc()
            RATE_LIMIT_COUNT.labels(backend=backend).inc()
            audit("rate_limit_exceeded", request, backend=backend)
            raise HTTPException(429, "Rate limit exceeded")


@app.middleware("http")
async def observe(request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        ERROR_COUNT.labels(type="unhandled").inc()
        raise
    elapsed = time.perf_counter() - start
    REQUEST_COUNT.labels(request.method, request.url.path, str(response.status_code)).inc()
    METRICS["requests_total"] = _metric_value("requests_total") + 1
    if response.status_code >= 400:
        METRICS["errors_total"] = _metric_value("errors_total") + 1
    REQUEST_LATENCY.labels(request.method, request.url.path).observe(elapsed)
    LATENCIES.append(elapsed)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Cache-Control"] = "no-store"
    audit("request", request, status_code=response.status_code, duration_ms=round(elapsed * 1000, 2))
    return response


@app.get("/health")
def health(request: Request):
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/ready")
def ready(request: Request, x_api_key: str | None = Header(default=None)):
    protected(request, x_api_key)
    if not runtime.ready():
        raise HTTPException(503, "Model artifacts are not ready")
    return {"status": "ready"}


@app.get("/metrics", include_in_schema=False)
def metrics(request: Request, x_api_key: str | None = Header(default=None)):
    protected(request, x_api_key)
    if request.query_params.get("format") == "json":
        for key in ("requests_total", "errors_total", "predictions_total"):
            _metric_value(key)
        avg_ms = (sum(LATENCIES) / len(LATENCIES) * 1000) if LATENCIES else 0.0
        return {"metrics": {"inference_requests_total": METRICS.get("requests_total", 0), "inference_errors_total": METRICS.get("errors_total", 0), "inference_predictions_total": METRICS.get("predictions_total", 0), "inference_latency_ms_avg": avg_ms}}
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/model-info")
def model_info(request: Request, x_api_key: str | None = Header(default=None)):
    protected(request, x_api_key)
    if not runtime.ready():
        raise HTTPException(503, "Model artifacts are not ready")
    metadata = json.loads(Path(MODEL_METADATA_FILE).read_text(encoding="utf-8"))
    return {"model": metadata.get("model_name"), "metrics": {key: metadata.get(key) for key in ("r2_score", "rmse", "mae", "cv_mean")}, "required_features": REQUIRED_FEATURES}


@app.post("/predict")
def predict(request: Request, payload: PredictionRequest, x_api_key: str | None = Header(default=None)):
    protected(request, x_api_key)
    try:
        score = runtime.predict(payload.model_dump())
        PREDICTION_COUNT.labels(outcome="success").inc()
        METRICS["predictions_total"] = _metric_value("predictions_total") + 1
        audit("prediction", request, model=runtime.metadata.get("model_name"))
        return {"prediction": score, "model": runtime.metadata.get("model_name")}
    except FileNotFoundError as exc:
        ERROR_COUNT.labels(type="artifacts").inc()
        PREDICTION_COUNT.labels(outcome="error").inc()
        raise HTTPException(503, str(exc)) from exc
    except ValueError as exc:
        ERROR_COUNT.labels(type="validation").inc()
        PREDICTION_COUNT.labels(outcome="error").inc()
        raise HTTPException(422, str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        ERROR_COUNT.labels(type="prediction").inc()
        PREDICTION_COUNT.labels(outcome="error").inc()
        logger.exception("prediction_failed")
        raise HTTPException(500, "Prediction failed") from exc
