# H3.1 — Cross-Repository Integration Contract

**Status: IMPLEMENTED — contract baseline for Part 2 → Part 3 and Part 4 boundary verification.**

## Purpose

H3.1 defines a machine-testable cross-repository integration contract without coupling repositories through undocumented internal files.

## Ownership

- **Part 2 — Cybersecurity ML Pipeline:** producer of the verified prediction-time runtime bundle and ML inference contract.
- **Part 3 — Cybersecurity Dashboard:** consumer/presentation layer for the verified Part 2 runtime bundle.
- **Part 4 — AI/LLM Integration:** independent RAG/LLM intelligence path; it is not a direct consumer of Part 2 model internals.

## Part 2 → Part 3 contract

Prediction-time input fields:

```text
records_affected
detection_time_hours
ransom_demand_usd
sector
region
attack_type
threat_actor
data_exfiltration
zero_day_used
```

Target output: `severity_score`.

Required immutable runtime bundle:

```text
models/best_model.pkl
models/preprocessor.pkl
models/feature_columns.pkl
outputs/evaluation_report.json
outputs/metrics.json
outputs/feature_importance.csv
```

Part 3 must verify artifact identity/integrity before inference and must not retrain the model or refit preprocessing.

## Part 3 target verification baseline

Canonical target:

`https://part3-cybersecurity-dashboard.streamlit.app/`

Recorded runtime commit:

`c97963eca1b078663bc7c60daa9506285404a4e7`

Recorded runtime state: 6/6 artifacts verified, health/readiness ready, prediction smoke PASS, Dataset Explorer smoke PASS.

The exact previous rollback deployment identifier remains a traceability caveat in H2; H3.1 does not fabricate it.

## Part 4 boundary contract

Part 4 is a separate incident-knowledge path:

```text
incident documents → embeddings → FAISS retrieval → relevance guardrail
→ bounded session context → prompt-grounded LLM → safe response
```

Part 4 must expose and protect its own API/runtime boundary. It must not read Part 2 internal files directly.

Recorded target baseline:

- platform: Render Web Service + Docker
- service: `part4-ai-cybersecurity-api`
- public API: `https://part4-ai-cybersecurity-api.onrender.com`
- immutable deployment: `dep-dagk5u0ae00c73bulro0`
- source commit: `f11f16c0202bf6d9571ba6e888987b101ac058ea`
- `/health`: HTTP 200
- `/ready`: `{"status":"ready","version":"1.5.0"}`
- authenticated `/v1/query`: HTTP 200

Secrets remain deployment-managed and are never part of this contract.

## Integration invariants

1. Part 3 consumes only the declared six-file Part 2 runtime bundle.
2. Artifact identity must be verified before Part 3 inference.
3. Prediction-time fields and output semantics remain versioned and stable.
4. Part 3 does not retrain or refit Part 2 assets.
5. Part 4 remains independently deployable and does not depend on Part 2 internal files.
6. Cross-repository integration uses documented contracts rather than repository-internal imports.
7. Credentials, API keys, bearer tokens, cookies, and sensitive request payloads are excluded from repository evidence.
8. CI is required before merge; deployment evidence is distinct from source-code verification.

## Change policy

A change to feature names/types, preprocessing behavior, model serialization, required runtime artifacts, or output semantics is a breaking contract change. Producer and consumer documentation/tests must be updated together before merge.

## H3.1 verification gate

H3.1 PASS requires:

- contract document present;
- automated invariants pass;
- Part 3 and Part 4 baseline identities/targets are traceable;
- no secrets committed;
- GitHub Actions ALL GREEN;
- PR review/comments gate clear;
- post-merge CI green on the merge SHA.
