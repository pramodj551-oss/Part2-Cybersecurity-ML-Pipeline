from pathlib import Path

import pytest

from src.production_governance_compliance import (
    CompliancePolicy,
    artifact_sha256,
    evaluate_governance_compliance,
    secrets_detected,
    validate_reproducibility,
)


def test_all_h35_gates_promote() -> None:
    result = evaluate_governance_compliance(
        tests_passed=True,
        security_passed=True,
        drift_ok=True,
        canary_ok=True,
        reproducible=True,
        immutable_identity="release-2026-09-10",
        audit_timestamp="2026-09-10T10:00:00Z",
    )
    assert result["decision"] == "promote"
    assert result["failed_checks"] == []
    assert result["policy_version"] == "h3.5-v1"


def test_failed_security_gate_rejects() -> None:
    result = evaluate_governance_compliance(
        tests_passed=True,
        security_passed=False,
        drift_ok=True,
        canary_ok=True,
        reproducible=True,
        immutable_identity="release-good",
        audit_timestamp="2026-09-10T10:00:00Z",
    )
    assert result["decision"] == "reject"
    assert "security" in result["failed_checks"]


def test_missing_immutable_identity_rejects() -> None:
    result = evaluate_governance_compliance(
        tests_passed=True,
        security_passed=True,
        drift_ok=True,
        canary_ok=True,
        reproducible=True,
        immutable_identity=None,
        audit_timestamp="2026-09-10T10:00:00Z",
    )
    assert result["decision"] == "reject"
    assert "immutable_identity" in result["failed_checks"]


def test_reproducibility_contract() -> None:
    assert validate_reproducibility(random_state=42, cv_folds=5)
    assert not validate_reproducibility(random_state=7, cv_folds=5)
    assert not validate_reproducibility(random_state=42, cv_folds=3)


def test_artifact_sha256_is_deterministic(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.bin"
    artifact.write_bytes(b"immutable-runtime-artifact")
    first = artifact_sha256(artifact)
    second = artifact_sha256(artifact)
    assert first == second
    assert len(first) == 64


@pytest.mark.parametrize(
    "text",
    [
        "Authorization: Bearer abc.def.ghi",
        "P8_API_KEY=not-a-real-secret",
        "password: example-value",
        "token=example-token",
    ],
)
def test_secret_patterns_are_detected_without_exposing_values(text: str) -> None:
    assert secrets_detected(text)


def test_sanitized_operational_text_is_allowed() -> None:
    text = "health=ok readiness=ready release_id=release-good status=200"
    assert not secrets_detected(text)


def test_policy_rejects_invalid_cv_configuration() -> None:
    with pytest.raises(ValueError):
        CompliancePolicy(required_cv_folds=1)
