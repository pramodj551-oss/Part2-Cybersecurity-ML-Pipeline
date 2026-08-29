import json
from pathlib import Path
from fastapi.testclient import TestClient
from src.inference_service import app, runtime
from src.config import BEST_MODEL_FILE, PREPROCESSOR_FILE, MODEL_METADATA_FILE

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_ready_matches_artifacts():
    response = client.get("/ready")
    expected = BEST_MODEL_FILE.exists() and PREPROCESSOR_FILE.exists() and MODEL_METADATA_FILE.exists()
    assert response.status_code == (200 if expected else 503)

def test_model_info_contract_when_ready():
    if not runtime.ready(): return
    response = client.get("/model-info")
    assert response.status_code == 200
    assert set(response.json()["required_features"]) == {"records_affected","detection_time_hours","ransom_demand_usd","sector","region","attack_type","threat_actor","data_exfiltration","zero_day_used"}

def test_predict_rejects_unknown_field():
    payload = {"records_affected":1,"detection_time_hours":1,"ransom_demand_usd":0,"sector":"finance","region":"APAC","attack_type":"phishing","threat_actor":"unknown","data_exfiltration":"No","zero_day_used":"No","extra":1}
    assert client.post("/predict", json=payload).status_code == 422
