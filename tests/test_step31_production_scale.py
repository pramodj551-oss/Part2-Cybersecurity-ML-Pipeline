import os

from fastapi.testclient import TestClient

import src.inference_service as service

client = TestClient(service.app)


def test_prometheus_metrics_are_exposed():
    response = client.get("/health")
    assert response.status_code == 200
    response = client.get("/metrics", headers={"X-API-Key": os.getenv("INFERENCE_API_KEY")} )
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "inference_http_requests_total" in response.text


def test_memory_rate_limit_fallback(monkeypatch):
    monkeypatch.setattr(service, "REDIS_URL", None)
    monkeypatch.setattr(service, "RATE_LIMIT", 1)
    service._local_requests.clear()
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
    }
    monkeypatch.setattr(service, "API_KEY", "step31-test")
    try:
        first = client.post("/predict", json=payload, headers={"X-API-Key": "step31-test"})
        second = client.post("/predict", json=payload, headers={"X-API-Key": "step31-test"})
        assert first.status_code != 429
        assert second.status_code == 429
    finally:
        service._local_requests.clear()
        monkeypatch.setattr(service, "API_KEY", os.getenv("INFERENCE_API_KEY"))
