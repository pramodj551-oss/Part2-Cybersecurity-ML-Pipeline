from fastapi.testclient import TestClient
from src.inference_service import app

client = TestClient(app)

def test_health_is_public():
    assert client.get('/health').status_code == 200

def test_invalid_api_key_is_rejected_when_configured(monkeypatch):
    monkeypatch.setattr('src.inference_service.API_KEY', 'secret')
    assert client.get('/ready', headers={'X-API-Key':'wrong'}).status_code == 401
    monkeypatch.setattr('src.inference_service.API_KEY', None)

def test_security_headers():
    response = client.get('/health')
    assert response.headers['X-Content-Type-Options'] == 'nosniff'
    assert response.headers['X-Frame-Options'] == 'DENY'
    assert response.headers['Cache-Control'] == 'no-store'

def test_rate_limit():
    import src.inference_service as service
    old = service.RATE_LIMIT
    service.RATE_LIMIT = 1
    service._requests.clear()
    try:
        assert client.post('/predict', json={}).status_code == 422
        assert client.post('/predict', json={}).status_code == 429
    finally:
        service.RATE_LIMIT = old
        service._requests.clear()
