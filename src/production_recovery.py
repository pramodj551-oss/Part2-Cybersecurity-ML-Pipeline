"""H3.4 deterministic observability-driven recovery helpers."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RecoveryState(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    RECOVERING = "recovering"
    RESTORED = "restored"
    FAILED = "failed"


@dataclass(frozen=True)
class RecoveryPolicy:
    max_recovery_attempts: int = 2
    required_health: str = "ok"
    required_readiness: str = "ready"

    def __post_init__(self) -> None:
        if self.max_recovery_attempts < 1:
            raise ValueError("max_recovery_attempts must be >= 1")


def classify_runtime(*, health: str, readiness: str, alert: bool) -> RecoveryState:
    """Classify runtime from sanitized probe/alert state only."""
    if health != "ok":
        return RecoveryState.FAILED
    if readiness != "ready" or alert:
        return RecoveryState.DEGRADED
    return RecoveryState.HEALTHY


def recover_to_known_good(
    *,
    current_identity: str,
    known_good_identity: str,
    health_checks: list[bool],
    policy: RecoveryPolicy = RecoveryPolicy(),
) -> dict[str, object]:
    """Bound recovery attempts and restore only after successful health checks."""
    if not current_identity or not known_good_identity:
        raise ValueError("runtime identities are required")
    attempts = 0
    for check_ok in health_checks[: policy.max_recovery_attempts]:
        attempts += 1
        if check_ok:
            return {
                "state": RecoveryState.RESTORED.value,
                "from_identity": current_identity,
                "restored_identity": known_good_identity,
                "attempts": attempts,
                "health": policy.required_health,
                "readiness": policy.required_readiness,
            }
    return {
        "state": RecoveryState.FAILED.value,
        "from_identity": current_identity,
        "restored_identity": None,
        "attempts": attempts,
        "health": "failed",
        "readiness": "not_ready",
    }
