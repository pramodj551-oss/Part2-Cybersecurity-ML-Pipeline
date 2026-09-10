"""H3.1 cross-repository integration contract tests.

These tests validate the producer/consumer contract from Part 2 without
importing implementation details from Part 3 or Part 4 repositories.
"""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "H3_1_CROSS_REPOSITORY_INTEGRATION_CONTRACT.md"

REQUIRED_RUNTIME_ARTIFACTS = {
    "models/best_model.pkl",
    "models/preprocessor.pkl",
    "models/feature_columns.pkl",
    "outputs/evaluation_report.json",
    "outputs/metrics.json",
    "outputs/feature_importance.csv",
}

PREDICTION_INPUT_FIELDS = {
    "records_affected",
    "detection_time_hours",
    "ransom_demand_usd",
    "sector",
    "region",
    "attack_type",
    "threat_actor",
    "data_exfiltration",
    "zero_day_used",
}


def test_h3_1_contract_exists_and_declares_runtime_bundle():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "H3.1" in text
    for artifact in REQUIRED_RUNTIME_ARTIFACTS:
        assert artifact in text


def test_h3_1_prediction_contract_is_explicit():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "Target output: `severity_score`." in text
    for field in PREDICTION_INPUT_FIELDS:
        assert field in text
    assert "must not retrain the model or refit preprocessing" in text


def test_h3_1_part3_target_identity_is_traceable():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "https://part3-cybersecurity-dashboard.streamlit.app/" in text
    assert "c97963eca1b078663bc7c60daa9506285404a4e7" in text
    assert "6/6 artifacts verified" in text


def test_h3_1_part4_boundary_is_independent_and_traceable():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "https://part4-ai-cybersecurity-api.onrender.com" in text
    assert "part4-ai-cybersecurity-api" in text
    assert "dep-dagk5u0ae00c73bulro0" in text
    assert "f11f16c0202bf6d9571ba6e888987b101ac058ea" in text
    assert "Part 4 remains independently deployable" in text
    assert "must not read Part 2 internal files directly" in text


def test_h3_1_secret_boundary_is_explicit():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "Credentials, API keys, bearer tokens, cookies" in text
    assert "never part of this contract" in text
