# H2 — Live Deployment Evidence Contract

**Status: IN PROGRESS — deployment evidence must be collected from real target environments before portfolio-wide live-deployment readiness is claimed.**

## Objective

H2 establishes a reproducible evidence contract for proving that the three-part cybersecurity AI portfolio works across real deployment boundaries:

```text
Part 2 ML release
      ↓
Part 3 runtime/dashboard
      ↓
Part 4 RAG/API service
      ↓
Authenticated smoke tests + health/readiness
      ↓
Deployment evidence + rollback evidence
```

CI success, artifact publication, or a Docker build alone is **not** considered live deployment evidence.

## Evidence gates

| Gate | Evidence required | Current state |
| --- | --- | --- |
| Part 2 release | Immutable published image/release + runtime verification | PASS — existing STEP 38 evidence |
| Part 2 rollback | Previous known-good image successfully restored | PASS — existing STEP 38 evidence |
| Part 3 target deployment | Actual deployed dashboard URL/target | PENDING |
| Part 3 artifact access | Target uses the verified six-artifact runtime contract | PENDING |
| Part 3 prediction smoke | Real target prediction request succeeds | PENDING |
| Part 4 target deployment | Actual deployed API/UI URL/target | PENDING |
| Part 4 readiness | `/health` and `/ready` pass on the target | PENDING |
| Part 4 authenticated query | Protected endpoint succeeds with deployment-managed secret | PENDING |
| Part 4 secret safety | No credential leakage in deployment logs | PENDING |
| Cross-repo integration | Part 2 → Part 3 contract and Part 4 boundary verified | PENDING |
| Rollback | Target can return to the previous known-good version | PENDING |

## Required evidence record

For each target environment, record:

- deployment platform/environment name
- immutable release identifier (image digest, commit SHA, or platform deployment ID)
- deployment timestamp
- public/private target URL or endpoint identifier (do not commit credentials)
- `/health` result
- `/ready` result
- authenticated functional smoke-test result
- runtime artifact identity where applicable
- log/telemetry secret-safety check
- rollback target identifier
- rollback smoke-test result

Secrets, API keys, bearer tokens, cookies, and sensitive request payloads must never be committed to this document.

## Part 2 baseline already available

Part 2 has existing release evidence for the published `v1.1.0` GHCR image and a real previous-image rollback validation. This is useful as the ML release baseline, but it does **not** prove that Part 3 or Part 4 are live-deployed.

## H2 acceptance rule

H2 is **PASS** only when the target deployment evidence above is attached to the repository through sanitized CI logs/artifacts or a documented external deployment record, and the actual target smoke tests pass.

Until then, portfolio wording must distinguish:

- **Source/CI production hardening:** demonstrated.
- **Release/runtime verification:** demonstrated where existing workflow evidence exists.
- **Live deployment:** not claimed without target-environment evidence.

## Next execution step

Deploy Part 3 and Part 4 to selected target environments, capture immutable deployment identifiers, execute health/readiness/authenticated smoke tests, capture rollback evidence, and then update this contract from `PENDING` to `PASS` only for gates with real evidence.
