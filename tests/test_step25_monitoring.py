from fastapi.testclient import TestClient
import src.inference_service as service

client=TestClient(service.app)

def test_metrics_endpoint():
    service.API_KEY=None
    service.METRICS.clear(); service.LATENCIES.clear()
    client.get('/health')
    response=client.get('/metrics')
    assert response.status_code==200
    body=response.json()['metrics']
    assert 'inference_requests_total' in body
    assert 'inference_latency_ms_avg' in body

def test_prediction_counter_increments(monkeypatch):
    service.API_KEY=None
    monkeypatch.setattr(service.runtime,'predict',lambda payload: 1.0)
    before=service.METRICS['predictions_total']
    payload={'records_affected':1,'detection_time_hours':1,'ransom_demand_usd':0,'sector':'finance','region':'APAC','attack_type':'phishing','threat_actor':'unknown','data_exfiltration':'No','zero_day_used':'No'}
    assert client.post('/predict',json=payload).status_code==200
    assert service.METRICS['predictions_total']==before+1

def test_metrics_requires_api_key_when_configured(monkeypatch):
    monkeypatch.setattr(service,'API_KEY','secret')
    assert client.get('/metrics').status_code==401
    assert client.get('/metrics',headers={'X-API-Key':'secret'}).status_code==200
    monkeypatch.setattr(service,'API_KEY',None)
