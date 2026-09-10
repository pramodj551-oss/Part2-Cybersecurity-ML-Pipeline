from src.production_observability import AlertThresholds, RequestMetrics, evaluate_alerts
from src.production_recovery import RecoveryPolicy, RecoveryState, classify_runtime, recover_to_known_good


def test_observability_metrics_and_alerts_are_deterministic():
    metrics = RequestMetrics()
    metrics.observe(200, 0.10)
    metrics.observe(503, 0.30)
    result = evaluate_alerts(metrics.snapshot(), prediction_psi=0.25, target_drift=0.25)
    assert result["alert"] is True
    assert result["alerts"] == {
        "error_rate": True,
        "latency": False,
        "prediction_drift": True,
        "target_drift": True,
    }


def test_observability_thresholds_reject_invalid_configuration():
    for kwargs in (
        {"max_error_rate": -0.1},
        {"max_error_rate": 1.1},
        {"max_average_latency_seconds": -1},
        {"max_prediction_psi": -1},
        {"max_target_drift": -1},
    ):
        try:
            AlertThresholds(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid threshold accepted")


def test_runtime_classification_distinguishes_health_and_readiness():
    assert classify_runtime(health="ok", readiness="ready", alert=False) is RecoveryState.HEALTHY
    assert classify_runtime(health="ok", readiness="not_ready", alert=False) is RecoveryState.DEGRADED
    assert classify_runtime(health="ok", readiness="ready", alert=True) is RecoveryState.DEGRADED
    assert classify_runtime(health="failed", readiness="ready", alert=False) is RecoveryState.FAILED


def test_recovery_restores_known_good_identity_after_bounded_attempts():
    result = recover_to_known_good(
        current_identity="release-bad",
        known_good_identity="release-good",
        health_checks=[False, True, True],
        policy=RecoveryPolicy(max_recovery_attempts=2),
    )
    assert result["state"] == "restored"
    assert result["restored_identity"] == "release-good"
    assert result["attempts"] == 2


def test_recovery_fails_without_unbounded_retry():
    result = recover_to_known_good(
        current_identity="release-bad",
        known_good_identity="release-good",
        health_checks=[False, False, True, True],
        policy=RecoveryPolicy(max_recovery_attempts=2),
    )
    assert result["state"] == "failed"
    assert result["restored_identity"] is None
    assert result["attempts"] == 2


def test_recovery_requires_runtime_identities():
    try:
        recover_to_known_good(current_identity="", known_good_identity="release-good", health_checks=[True])
    except ValueError:
        pass
    else:
        raise AssertionError("missing runtime identity accepted")
