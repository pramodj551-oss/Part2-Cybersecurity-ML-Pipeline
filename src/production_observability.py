"""STEP 39: deterministic production monitoring and observability helpers."""
from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from time import monotonic
from typing import Any


@dataclass
class RequestMetrics:
    """In-process request metrics suitable for exposing through an API."""
    requests_total: int = 0
    errors_total: int = 0
    latency_seconds_total: float = 0.0
    status_counts: dict[int, int] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock, repr=False)

    def observe(self, status_code: int, latency_seconds: float) -> None:
        if latency_seconds < 0:
            raise ValueError("latency_seconds must be non-negative")
        with self._lock:
            self.requests_total += 1
            self.latency_seconds_total += float(latency_seconds)
            self.status_counts[status_code] = self.status_counts.get(status_code, 0) + 1
            if status_code >= 500:
                self.errors_total += 1

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            total = self.requests_total
            return {
                "requests_total": total,
                "errors_total": self.errors_total,
                "error_rate": self.errors_total / total if total else 0.0,
                "latency_seconds_total": self.latency_seconds_total,
                "average_latency_seconds": self.latency_seconds_total / total if total else 0.0,
                "status_counts": dict(self.status_counts),
            }


@dataclass(frozen=True)
class AlertThresholds:
    """Operational thresholds; values are deliberately explicit and testable."""
    max_error_rate: float = 0.05
    max_average_latency_seconds: float = 2.0
    max_prediction_psi: float = 0.20
    max_target_drift: float = 0.20

    def __post_init__(self) -> None:
        if not 0 <= self.max_error_rate <= 1:
            raise ValueError("max_error_rate must be in [0, 1]")
        if self.max_average_latency_seconds < 0:
            raise ValueError("max_average_latency_seconds must be non-negative")
        if self.max_prediction_psi < 0 or self.max_target_drift < 0:
            raise ValueError("drift thresholds must be non-negative")


def evaluate_alerts(
    metrics: dict[str, Any],
    prediction_psi: float,
    target_drift: float,
    thresholds: AlertThresholds = AlertThresholds(),
) -> dict[str, Any]:
    """Return deterministic alert state without logging sensitive request payloads."""
    error_rate = float(metrics.get("error_rate", 0.0))
    average_latency = float(metrics.get("average_latency_seconds", 0.0))
    alerts = {
        "error_rate": error_rate > thresholds.max_error_rate,
        "latency": average_latency > thresholds.max_average_latency_seconds,
        "prediction_drift": prediction_psi >= thresholds.max_prediction_psi,
        "target_drift": target_drift >= thresholds.max_target_drift,
    }
    return {
        "alert": any(alerts.values()),
        "alerts": alerts,
        "error_rate": error_rate,
        "average_latency_seconds": average_latency,
        "prediction_psi": float(prediction_psi),
        "target_drift": float(target_drift),
    }


def time_request(metrics: RequestMetrics, status_code: int, start: float) -> float:
    """Observe elapsed monotonic time and return it for callers/tests."""
    elapsed = monotonic() - start
    metrics.observe(status_code, elapsed)
    return elapsed
