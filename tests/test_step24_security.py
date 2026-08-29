from fastapi.testclient import TestClient
from src.inference_service import app

client = TestClient(app)


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


def test_invalid_api_key_is_rejected_when_configured(monkeypatch):
    monkeypatch.setattr('src.inference_service.API_KEY', 'secret')
    assert client.get('/ready', headers={'X-API-Key': 'wrong'}).status_code == 401
    monkeypatch.setattr('src.inference_service.API_KEY', None)


def test_security_headers():
    response = client.get('/health')
    assert response.headers['X-Content-Type-Options'] == 'nosniff'
    assert response.headers['X-Frame-Options'] == 'DENY'
    assert response.headers['Cache-Control'] == 'no-store'


def test_rate_limit(monkeypatch):
    import src.inference_service as service
    monkeypatch.setattr(service, 'RATE_LIMIT', 1)
    service._requests.clear()
    try:
        first = client.post('/predict', json=_valid_payload())
        second = client.post('/predict', json=_valid_payload())
        assert first.status_code != 429
        assert second.status_code == 429
    finally:
        service._requests.clear()
