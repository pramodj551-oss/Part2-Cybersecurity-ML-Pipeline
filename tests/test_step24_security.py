from fastapi.testclient import TestClient

import src.inference_service as service

client = TestClient(service.app)
TEST_KEY = "ci-step24-test-key"


def _valid_payload():
    return {
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


def test_health_is_public():
    assert client.get('/health').status_code == 200


def test_missing_server_configuration_returns_503(monkeypatch):
    monkeypatch.delenv("INFERENCE_API_KEY", raising=False)
    assert client.get('/ready').status_code == 503


def test_invalid_api_key_is_rejected(monkeypatch):
    monkeypatch.setenv("INFERENCE_API_KEY", TEST_KEY)
    assert client.get('/ready', headers={'X-API-Key': 'wrong'}).status_code == 401


def test_rate_limit(monkeypatch):
    monkeypatch.setenv("INFERENCE_API_KEY", TEST_KEY)
    monkeypatch.setattr(service, 'RATE_LIMIT', 1)
    service._local_requests.clear()
    try:
        first = client.post('/predict', json=_valid_payload(), headers={'X-API-Key': TEST_KEY})
        second = client.post('/predict', json=_valid_payload(), headers={'X-API-Key': TEST_KEY})
        assert first.status_code != 429
        assert second.status_code == 429
    finally:
        service._local_requests.clear()
