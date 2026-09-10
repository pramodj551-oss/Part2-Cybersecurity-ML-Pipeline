from src.final_production_readiness import (
    REQUIRED_RUNTIME_ARTIFACTS,
    ProductionReadinessEvidence,
    final_decision,
    validate_immutable_release,
    validate_portfolio_boundaries,
    validate_runtime_artifacts,
    valid_sha256,
)


def passing_evidence() -> ProductionReadinessEvidence:
    return ProductionReadinessEvidence(
        h3_1=True, h3_2=True, h3_3=True, h3_4=True, h3_5=True,
        runtime_artifacts=True, deployment_evidence=True,
        security_compliance=True, reproducibility=True,
        rollback_ready=True, immutable_release=True,
        portfolio_boundaries=True,
    )


def test_h4_pass_requires_all_twelve_gates() -> None:
    result = final_decision(passing_evidence())
    assert result == {"decision": "PASS", "failed_gates": [], "gate_count": 12}


def test_h4_blocks_when_any_gate_fails() -> None:
    evidence = passing_evidence()
    blocked = ProductionReadinessEvidence(**{**evidence.__dict__, "rollback_ready": False})
    result = final_decision(blocked)
    assert result["decision"] == "BLOCKED"
    assert result["failed_gates"] == ["rollback_ready"]


def test_required_runtime_bundle_is_exactly_declared() -> None:
    assert len(REQUIRED_RUNTIME_ARTIFACTS) == 6
    assert validate_runtime_artifacts(list(REQUIRED_RUNTIME_ARTIFACTS))
    assert not validate_runtime_artifacts(list(REQUIRED_RUNTIME_ARTIFACTS)[:5])


def test_sha256_identity_is_strict() -> None:
    assert valid_sha256("a" * 64)
    assert not valid_sha256("a" * 63)
    assert not valid_sha256("g" * 64)


def test_immutable_release_requires_release_and_source_identity() -> None:
    assert validate_immutable_release(release_id="part2-runtime-34455293918", source_commit="634d408bc1ea7ed")
    assert not validate_immutable_release(release_id="", source_commit="634d408")


def test_portfolio_boundary_rejects_internal_imports_and_secret_evidence() -> None:
    assert validate_portfolio_boundaries(internal_imports=[], evidence_text="health=ok readiness=ready release=known-good")
    assert not validate_portfolio_boundaries(internal_imports=["part3.internal"], evidence_text="safe")
    assert not validate_portfolio_boundaries(internal_imports=[], evidence_text="Authorization: Bearer secret")


def test_h4_is_not_promoted_by_partial_evidence() -> None:
    evidence = passing_evidence()
    partial = ProductionReadinessEvidence(**{**evidence.__dict__, "h3_5": False, "immutable_release": False})
    result = final_decision(partial)
    assert result["decision"] == "BLOCKED"
    assert set(result["failed_gates"]) == {"h3.5", "immutable_release"}
