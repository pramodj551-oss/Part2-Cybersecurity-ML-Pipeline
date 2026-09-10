"""Deterministic H4 final production-readiness and portfolio release gate."""
from __future__ import annotations

from dataclasses import dataclass
import re

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

REQUIRED_RUNTIME_ARTIFACTS = (
    "models/best_model.pkl",
    "models/preprocessor.pkl",
    "models/feature_columns.pkl",
    "outputs/evaluation_report.json",
    "outputs/metrics.json",
    "outputs/feature_importance.csv",
)

REQUIRED_H3_CONTRACTS = (
    "H3_1_CROSS_REPOSITORY_INTEGRATION_CONTRACT.md",
    "H3_2_INTEGRATION_RUNTIME_VALIDATION.md",
    "H3_3_PRODUCTION_INTEGRATION_RESILIENCE.md",
    "H3_4_PRODUCTION_OBSERVABILITY_AUTOMATED_RECOVERY.md",
    "H3_5_PRODUCTION_GOVERNANCE_SECURITY_COMPLIANCE.md",
)


@dataclass(frozen=True)
class ProductionReadinessEvidence:
    h3_1: bool
    h3_2: bool
    h3_3: bool
    h3_4: bool
    h3_5: bool
    runtime_artifacts: bool
    deployment_evidence: bool
    security_compliance: bool
    reproducibility: bool
    rollback_ready: bool
    immutable_release: bool
    portfolio_boundaries: bool

    def failed_gates(self) -> list[str]:
        values = {
            "h3.1": self.h3_1,
            "h3.2": self.h3_2,
            "h3.3": self.h3_3,
            "h3.4": self.h3_4,
            "h3.5": self.h3_5,
            "runtime_artifacts": self.runtime_artifacts,
            "deployment_evidence": self.deployment_evidence,
            "security_compliance": self.security_compliance,
            "reproducibility": self.reproducibility,
            "rollback_ready": self.rollback_ready,
            "immutable_release": self.immutable_release,
            "portfolio_boundaries": self.portfolio_boundaries,
        }
        return [name for name, ok in values.items() if not ok]


def final_decision(evidence: ProductionReadinessEvidence) -> dict[str, object]:
    failed = evidence.failed_gates()
    return {
        "decision": "PASS" if not failed else "BLOCKED",
        "failed_gates": failed,
        "gate_count": 12,
    }


def valid_sha256(value: str) -> bool:
    return bool(SHA256_RE.fullmatch(value))


def validate_runtime_artifacts(paths: list[str]) -> bool:
    return set(REQUIRED_RUNTIME_ARTIFACTS).issubset(paths)


def validate_immutable_release(*, release_id: str, source_commit: str) -> bool:
    return bool(release_id and source_commit and len(source_commit) >= 7)


def validate_portfolio_boundaries(*, internal_imports: list[str], evidence_text: str) -> bool:
    if internal_imports:
        return False
    forbidden = (
        "Authorization: " + "Bearer",
        "P8_API_KEY" + "=",
        "P8_ADMIN_API_KEY" + "=",
        "GROQ_API_KEY" + "=",
    )
    return not any(token in evidence_text for token in forbidden)
