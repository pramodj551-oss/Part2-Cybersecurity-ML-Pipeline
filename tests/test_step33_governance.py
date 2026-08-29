from src.governance import evaluate_promotion

def test_promotion_requires_all_gates():
    d = evaluate_promotion(model_version="v1", status="candidate", tests_passed=True, security_passed=True, drift_ok=True, canary_ok=True)
    assert d.decision == "promote"

def test_failed_gate_rejects():
    d = evaluate_promotion(model_version="v1", status="candidate", tests_passed=True, security_passed=False, drift_ok=True, canary_ok=True)
    assert d.decision == "reject"
    assert "security" in d.reason

def test_invalid_status_rejects():
    d = evaluate_promotion(model_version="v1", status="unknown", tests_passed=True, security_passed=True, drift_ok=True, canary_ok=True)
    assert d.decision == "reject"
