"""STEP 33 model governance and policy-as-code controls."""
from __future__ import annotations
import hashlib, json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_STATUSES = {"candidate", "canary", "production", "archived"}

def utc_now():
    return datetime.now(timezone.utc).isoformat()

@dataclass(frozen=True)
class GovernanceDecision:
    model_version: str
    decision: str
    reason: str
    decided_at: str
    policy_version: str = "step33-v1"


def evaluate_promotion(*, model_version: str, status: str, tests_passed: bool, security_passed: bool, drift_ok: bool, canary_ok: bool) -> GovernanceDecision:
    if status not in ALLOWED_STATUSES:
        return GovernanceDecision(model_version, "reject", "invalid_lifecycle_status", utc_now())
    if not all((tests_passed, security_passed, drift_ok, canary_ok)):
        reasons = [name for name, ok in (("tests", tests_passed), ("security", security_passed), ("drift", drift_ok), ("canary", canary_ok)) if not ok]
        return GovernanceDecision(model_version, "reject", ",".join(reasons), utc_now())
    return GovernanceDecision(model_version, "promote", "all_policy_gates_passed", utc_now())


def artifact_fingerprint(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def append_audit_event(path: Path, decision: GovernanceDecision, artifact_sha256: str | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    event = asdict(decision)
    if artifact_sha256:
        event["artifact_sha256"] = artifact_sha256
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")
    return path
