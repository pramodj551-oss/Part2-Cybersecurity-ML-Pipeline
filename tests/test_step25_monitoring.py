from fastapi.testclient import TestClient
import src.inference_service as service

client = TestClient(service.app)
TEST_KEY = "ci-step25-test-key"


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


def test_metrics_endpoint_requires_auth(monkeypatch):
    monkeypatch.setenv("INFERENCE_API_KEY", TEST_KEY)
    service.METRICS.clear()
    service.LATENCIES.clear()
    client.get('/health')
    assert client.get('/metrics?format=json').status_code == 401
    response = client.get('/metrics?format=json', headers={'X-API-Key': TEST_KEY})
    assert response.status_code == 200
    body = response.json()['metrics']
    assert 'inference_requests_total' in body
    assert 'inference_latency_ms_avg' in body


def test_prediction_counter_increments(monkeypatch):
    monkeypatch.setenv("INFERENCE_API_KEY", TEST_KEY)
    monkeypatch.setattr(service.runtime, 'predict', lambda payload: 1.0)
    before = service.METRICS['predictions_total']
    response = client.post('/predict', json=_valid_payload(), headers={'X-API-Key': TEST_KEY})
    assert response.status_code == 200
    assert service.METRICS['predictions_total'] == before + 1
