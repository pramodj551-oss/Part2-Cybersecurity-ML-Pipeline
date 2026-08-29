"""STEP 32: production operations and continuous improvement controls."""
from __future__ import annotations
import hashlib, json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from src.config import OUTPUT_DIR
OPS_DIR=OUTPUT_DIR/"operations"
DEFAULT_SLO={"availability":0.995,"p95_latency_ms":500.0,"error_rate":0.01}
def utc_now(): return datetime.now(timezone.utc).isoformat()
def evaluate_slo(metrics:dict[str,float],slo:dict[str,float]|None=None)->dict[str,Any]:
    slo={**DEFAULT_SLO,**(slo or {})}
    checks={"availability":metrics.get("availability",0)>=slo["availability"],"p95_latency_ms":metrics.get("p95_latency_ms",float("inf"))<=slo["p95_latency_ms"],"error_rate":metrics.get("error_rate",1)<=slo["error_rate"]}
    return {"timestamp":utc_now(),"slo":slo,"metrics":metrics,"checks":checks,"healthy":all(checks.values())}
def build_alerts(result):
    return [{"name":"slo_"+k,"severity":"critical" if k=="availability" else "warning","status":"firing"} for k,v in result["checks"].items() if not v]
def retraining_trigger(drift_report,performance,min_r2=0.0):
    reasons=[]
    if drift_report.get("overall_drift_detected"): reasons.append("drift_detected")
    if performance.get("r2_score",min_r2)<min_r2: reasons.append("performance_below_threshold")
    return {"trigger":bool(reasons),"reasons":reasons,"timestamp":utc_now()}
@dataclass(frozen=True)
class ModelVersion: version:str; status:str; artifact_sha256:str; created_at:str
def artifact_sha256(path:Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(65536),b""): h.update(chunk)
    return h.hexdigest()
def register_model(version,artifact:Path,status="candidate"):
    if status not in {"candidate","canary","production","archived"}: raise ValueError("Unsupported model lifecycle status")
    return ModelVersion(version,status,artifact_sha256(artifact),utc_now())
def validate_canary(baseline,canary,max_error_increase=0.005,max_latency_ratio=1.10):
    error_ok=canary.get("error_rate",1)<=baseline.get("error_rate",0)+max_error_increase
    latency_ok=canary.get("p95_latency_ms",float("inf"))<=baseline.get("p95_latency_ms",1)*max_latency_ratio
    return {"error_ok":error_ok,"latency_ok":latency_ok,"promote":error_ok and latency_ok}
def write_operations_report(slo_result,alerts,retraining,canary):
    OPS_DIR.mkdir(parents=True,exist_ok=True); path=OPS_DIR/"production_operations_report.json"
    path.write_text(json.dumps({"step":32,"generated_at":utc_now(),"slo":slo_result,"alerts":alerts,"retraining":retraining,"canary":canary},indent=2),encoding="utf-8"); return path
