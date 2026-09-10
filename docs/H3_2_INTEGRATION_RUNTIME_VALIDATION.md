# H3.2 — Integration Runtime Validation

**Status: IMPLEMENTED — deterministic runtime validation contract for the cross-repository portfolio.**

## Objective

Validate that the documented Part-2 → Part-3 runtime contract and the independent Part-4 runtime boundary are operationally coherent without importing internal implementation details from another repository.

## Runtime validation scope

### Part 2 → Part 3

Validate the six-file immutable runtime bundle declared by H3.1:

```text
models/best_model.pkl
models/preprocessor.pkl
models/feature_columns.pkl
outputs/evaluation_report.json
outputs/metrics.json
outputs/feature_importance.csv
```

Validate the prediction-time feature contract and `severity_score` output semantics. Part 3 must consume verified artifacts and must not retrain or refit them.

### Part 3 runtime baseline

Canonical target: `https://part3-cybersecurity-dashboard.streamlit.app/`

Recorded runtime commit: `c97963eca1b078663bc7c60daa9506285404a4e7`

Recorded baseline: health/readiness ready, six runtime artifacts verified, prediction smoke PASS, Dataset Explorer smoke PASS.

### Part 4 runtime boundary

Part 4 remains independently deployable and does not consume Part-2 internal files.

Recorded API target: `https://part4-ai-cybersecurity-api.onrender.com`

Recorded service: `part4-ai-cybersecurity-api`

Recorded immutable deployment: `dep-dagk5u0ae00c73bulro0`

Recorded source commit: `f11f16c0202bf6d9571ba6e888987b101ac058ea`

Recorded baseline: `/health` HTTP 200, `/ready` ready, authenticated `/v1/query` HTTP 200.

## Evidence boundary

Runtime validation evidence must contain only sanitized status, endpoint identifiers, release/deployment identities, artifact identities, and pass/fail outcomes. API keys, bearer tokens, cookies, credentials, and sensitive request payloads are never committed.

## H3.2 gate

H3.2 PASS requires:

- runtime validation tests present and passing;
- six-file Part-2 → Part-3 contract explicitly validated;
- Part-3 target/runtime identity traceable;
- Part-4 boundary/deployment identity traceable;
- no secret material in repository evidence;
- GitHub Actions ALL GREEN;
- PR review/comments gate clear;
- post-merge CI green on the merge SHA.
