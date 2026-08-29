from pathlib import Path
from src.production_operations import build_alerts,evaluate_slo,register_model,retraining_trigger,validate_canary
def test_slo_and_alerting():
 r=evaluate_slo({"availability":0.90,"p95_latency_ms":100,"error_rate":0}); assert not r["healthy"]; assert build_alerts(r)[0]["severity"]=="critical"
def test_retraining_trigger():
 assert retraining_trigger({"overall_drift_detected":True},{"r2_score":0.8},0.5)["trigger"]
def test_registry_hash(tmp_path:Path):
 p=tmp_path/"model.bin"; p.write_bytes(b"model"); assert len(register_model("v1",p,"canary").artifact_sha256)==64
def test_canary():
 assert validate_canary({"error_rate":.01,"p95_latency_ms":100},{"error_rate":.012,"p95_latency_ms":105})["promote"]
