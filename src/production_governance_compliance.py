"""H3.5 deterministic production governance, security and compliance controls."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

SECRET_PATTERNS = (
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+"),
    re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*[^\s,;]+"),
)


@dataclass(frozen=True)
class CompliancePolicy:
    policy_version: str = "h3.5-v1"
    required_seed: int = 42
    required_cv_folds: int = 5
    require_immutable_identity: bool = True
    require_audit_timestamp: bool = True

    def __post_init__(self) -> None:
        if self.required_cv_folds < 2:
            raise ValueError("required_cv_folds must be >= 2")
        if self.require_immutable_identity and not self.policy_version:
            raise ValueError("policy_version is required")


def evaluate_governance_compliance(
    *,
    tests_passed: bool,
    security_passed: bool,
    drift_ok: bool,
    canary_ok: bool,
    reproducible: bool,
    immutable_identity: str | None,
    audit_timestamp: str | None,
    policy: CompliancePolicy = CompliancePolicy(),
) -> dict[str, object]:
    """Return a deterministic promotion decision from governance evidence only."""
    checks = {
        "tests": bool(tests_passed),
        "security": bool(security_passed),
        "drift": bool(drift_ok),
        "canary": bool(canary_ok),
        "reproducibility": bool(reproducible),
        "immutable_identity": bool(immutable_identity) if policy.require_immutable_identity else True,
        "audit_timestamp": bool(audit_timestamp) if policy.require_audit_timestamp else True,
    }
    failed = [name for name, ok in checks.items() if not ok]
    return {
        "decision": "promote" if not failed else "reject",
        "policy_version": policy.policy_version,
        "checks": checks,
        "failed_checks": failed,
    }


def artifact_sha256(path: Path) -> str:
    """Return SHA-256 for an immutable artifact identity check."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def secrets_detected(text: str) -> bool:
    """Detect common credential/token patterns without returning their values."""
    return any(pattern.search(text) for pattern in SECRET_PATTERNS)


def validate_reproducibility(*, random_state: int, cv_folds: int, policy: CompliancePolicy = CompliancePolicy()) -> bool:
    return random_state == policy.required_seed and cv_folds == policy.required_cv_folds
