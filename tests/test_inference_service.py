import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.inference_service import app, runtime
from src.config import BEST_MODEL_FILE, PREPROCESSOR_FILE, MODEL_METADATA_FILE

client = TestClient(app)

VALID_KEY = "step23-test-secret"


def test_health_is_public():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_protected_endpoint_rejects_missing_server_configuration(monkeypatch):
    monkeypatch.delenv("INFERENCE_API_KEY", raising=False)
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json()["detail"] == "Inference API authentication is not configured"


def test_protected_endpoint_rejects_missing_client_key(monkeypatch):
    monkeypatch.setenv("INFERENCE_API_KEY", VALID_KEY)
    response = client.get("/ready")
    assert response.status_code == 401


def test_protected_endpoint_rejects_invalid_client_key(monkeypatch):
    monkeypatch.setenv("INFERENCE_API_KEY", VALID_KEY)
    response = client.get("/ready", headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 401


def test_ready_matches_artifacts_with_valid_key(monkeypatch):
    monkeypatch.setenv("INFERENCE_API_KEY", VALID_KEY)
    response = client.get("/ready", headers={"X-API-Key": VALID_KEY})
    expected = BEST_MODEL_FILE.exists() and PREPROCESSOR_FILE.exists() and MODEL_METADATA_FILE.exists()
    assert response.status_code == (200 if expected else 503)


def test_model_info_contract_when_ready(monkeypatch):
    if not runtime.ready():
        pytest.skip("Model artifacts are not available")
    monkeypatch.setenv("INFERENCE_API_KEY", VALID_KEY)
    response = client.get("/model-info", headers={"X-API-Key": VALID_KEY})
    assert response.status_code == 200
    assert set(response.json()["required_features"]) == {
        "records_affected",
        "detection_time_hours",
        "ransom_demand_usd",
        "sector",
        "region",
        "attack_type",
        "threat_actor",
        "data_exfiltration",
        "zero_day_used",
    }


def test_predict_rejects_unknown_field(monkeypatch):
    monkeypatch.setenv("INFERENCE_API_KEY", VALID_KEY)
    payload = {
        "records_affected": 1,
        "detection_time_hours": 1,
        "ransom_demand_usd": 0,
        "sector": "finance",
        "region": "APAC",
        "attack_type": "phishing",
        "threat_actor": "unknown",
        "data_exfiltration": "No",
        "zero_day_used": "No",
        "extra": 1,
    }
    assert client.post("/predict", json=payload, headers={"X-API-Key": VALID_KEY}).status_code == 422
