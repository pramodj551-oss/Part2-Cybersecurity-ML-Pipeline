from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_h3_2_evidence_document_excludes_secret_material():
    text = (ROOT / "docs" / "H3_2_INTEGRATION_RUNTIME_VALIDATION.md").read_text(encoding="utf-8")
    assert "API keys" in text
    assert "bearer tokens" in text
    assert "cookies" in text
    assert "credentials" in text
    assert "are never committed" in text


def test_h3_2_evidence_uses_immutable_runtime_identity():
    text = (ROOT / "docs" / "H3_2_INTEGRATION_RUNTIME_VALIDATION.md").read_text(encoding="utf-8")
    assert "dep-dagk5u0ae00c73bulro0" in text
    assert "f11f16c0202bf6d9571ba6e888987b101ac058ea" in text
    assert "c97963eca1b078663bc7c60daa9506285404a4e7" in text
