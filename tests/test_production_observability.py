"""Tests for STEP 39 production observability."""
import pytest

from src.production_observability import AlertThresholds, RequestMetrics, evaluate_alerts


def test_request_metrics_snapshot_and_error_rate():
    metrics = RequestMetrics()
    metrics.observe(200, 0.10)
    metrics.observe(503, 0.30)
    snapshot = metrics.snapshot()
    assert snapshot["requests_total"] == 2
    assert snapshot["errors_total"] == 1
    assert snapshot["error_rate"] == pytest.approx(0.5)
    assert snapshot["average_latency_seconds"] == pytest.approx(0.2)
    assert snapshot["status_counts"] == {200: 1, 503: 1}


def test_alerts_trigger_on_error_latency_and_drift():
    result = evaluate_alerts(
        {"error_rate": 0.10, "average_latency_seconds": 3.0},
        prediction_psi=0.25,
        target_drift=0.30,
    )
    assert result["alert"] is True
    assert all(result["alerts"].values())


def test_alerts_clear_below_thresholds():
    result = evaluate_alerts(
        {"error_rate": 0.01, "average_latency_seconds": 0.2},
        prediction_psi=0.05,
        target_drift=0.05,
    )
    assert result["alert"] is False
    assert not any(result["alerts"].values())


def test_thresholds_reject_invalid_values():
    with pytest.raises(ValueError):
        AlertThresholds(max_error_rate=1.1)
    with pytest.raises(ValueError):
        AlertThresholds(max_average_latency_seconds=-1)


def test_negative_latency_rejected():
    metrics = RequestMetrics()
    with pytest.raises(ValueError):
        metrics.observe(200, -0.1)
