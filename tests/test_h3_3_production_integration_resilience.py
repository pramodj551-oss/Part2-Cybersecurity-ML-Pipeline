from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "H3_3_PRODUCTION_INTEGRATION_RESILIENCE.md"

ARTIFACTS = {
    "models/best_model.pkl",
    "models/preprocessor.pkl",
    "models/feature_columns.pkl",
    "outputs/evaluation_report.json",
    "outputs/metrics.json",
    "outputs/feature_importance.csv",
}


def test_h3_3_contract_exists():
    assert CONTRACT.is_file()


def test_h3_3_immutable_runtime_bundle_is_explicit():
    text = CONTRACT.read_text(encoding="utf-8")
    for artifact in ARTIFACTS:
        assert artifact in text
    assert "must reject missing or invalid runtime assets" in text


def test_h3_3_failure_modes_are_explicit():
    text = CONTRACT.read_text(encoding="utf-8")
    required = (
        "Missing runtime artifacts",
        "Invalid artifact identity/integrity",
        "Dependency/API failures",
        "Timeout/retry behavior",
        "Health and readiness",
        "Rollback recovery",
    )
    for item in required:
        assert item in text


def test_h3_3_retry_and_recovery_are_bounded():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "bounded" in text
    assert "unbounded retry loop" in text
    assert "previously known-good identity" in text


def test_h3_3_part4_boundary_remains_independent():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "Part 4 remains independently deployable" in text
    assert "must not import Part 2 internals" in text


def test_h3_3_secret_boundary_is_enforced():
    text = CONTRACT.read_text(encoding="utf-8")
    for term in ("API keys", "bearer tokens", "cookies", "credentials"):
        assert term in text
    assert "are never committed" in text


def test_h3_3_validation_matrix_is_present():
    text = CONTRACT.read_text(encoding="utf-8")
    for scenario in (
        "Healthy runtime",
        "Missing model artifact",
        "Invalid artifact identity",
        "Downstream/API failure",
        "Timeout/retry condition",
        "Readiness dependency failure",
        "Rollback recovery",
        "Secret emission",
    ):
        assert scenario in text
