from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "H3_2_INTEGRATION_RUNTIME_VALIDATION.md"
H3_1 = ROOT / "docs" / "H3_1_CROSS_REPOSITORY_INTEGRATION_CONTRACT.md"

ARTIFACTS = {
    "models/best_model.pkl",
    "models/preprocessor.pkl",
    "models/feature_columns.pkl",
    "outputs/evaluation_report.json",
    "outputs/metrics.json",
    "outputs/feature_importance.csv",
}

INPUT_FIELDS = {
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


def test_h3_2_runtime_validation_contract_exists():
    assert CONTRACT.is_file()
    assert H3_1.is_file()


def test_h3_2_part2_part3_runtime_bundle_is_explicit():
    text = CONTRACT.read_text(encoding="utf-8")
    for artifact in ARTIFACTS:
        assert artifact in text
    assert "severity_score" in text
    assert "must not retrain or refit" in text


def test_h3_2_prediction_contract_fields_are_traceable_to_h3_1():
    text = H3_1.read_text(encoding="utf-8")
    for field in INPUT_FIELDS:
        assert field in text
    assert "Target output: `severity_score`." in text


def test_h3_2_part3_runtime_identity_is_traceable():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "https://part3-cybersecurity-dashboard.streamlit.app/" in text
    assert "c97963eca1b078663bc7c60daa9506285404a4e7" in text
    assert "six runtime artifacts verified" in text


def test_h3_2_part4_runtime_boundary_is_traceable_and_independent():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "https://part4-ai-cybersecurity-api.onrender.com" in text
    assert "part4-ai-cybersecurity-api" in text
    assert "dep-dagk5u0ae00c73bulro0" in text
    assert "f11f16c0202bf6d9571ba6e888987b101ac058ea" in text
    assert "does not consume Part-2 internal files" in text


def test_h3_2_secret_evidence_boundary_is_enforced():
    text = CONTRACT.read_text(encoding="utf-8")
    for secret_term in ("API keys", "bearer tokens", "cookies", "credentials"):
        assert secret_term in text
    assert "are never committed" in text
