# H3.4 — Production Integration Observability & Automated Recovery Validation

**Status: IMPLEMENTATION / TESTING**

## Objective

Validate deterministic production observability and bounded automated recovery semantics across the portfolio without requiring production credentials or live mutation of deployed services.

## Observability contract

H3.4 builds on STEP 39 production monitoring. Operational decisions use sanitized signals only:

- request count, error count, error rate, latency, and status distribution;
- prediction PSI and target drift;
- health and readiness probe state;
- immutable current and known-good runtime identities;
- explicit alert state and recovery state.

The observability layer must not record API keys, bearer tokens, cookies, credentials, or sensitive request payloads.

## Automated recovery contract

1. `healthy` means health is `ok`, readiness is `ready`, and no alert is active.
2. `degraded` means health remains live but readiness is not ready or an alert is active.
3. `failed` means the health probe is not `ok` or bounded recovery attempts are exhausted.
4. Recovery may target only an explicitly known-good immutable identity.
5. Recovery attempts are bounded by `max_recovery_attempts`; no unbounded retry loop is permitted.
6. A runtime is considered restored only after a successful post-recovery health/readiness check.
7. Failed recovery does not claim restoration and does not fabricate deployment success.
8. Recovery evidence contains state, sanitized identities, attempt count, and probe status only.

## Failure and recovery matrix

| Scenario | Expected result |
|---|---|
| Healthy runtime | No recovery action |
| Alert with healthy liveness | Degraded state; recovery eligible |
| Readiness failure | Degraded state; liveness remains distinct |
| Health failure | Failed state |
| Recovery succeeds | Known-good identity restored |
| Recovery attempts exhausted | Failed state; no false restoration |
| Missing runtime identity | Deterministic validation error |
| Secret material in evidence | Rejected by evidence policy |

## Evidence boundary

Tests use synthetic identities such as `release-bad` and `release-good`. They never contain production API keys, bearer tokens, cookies, credentials, or sensitive payloads. H3.4 does not claim that a CI test performed a live rollback; live deployment/rollback evidence remains deployment-managed.

## H3.4 gate

PASS requires:

- observability signals validated deterministically;
- health/readiness distinction validated;
- alert evaluation validated;
- bounded automated recovery validated;
- known-good identity requirement validated;
- safe failed-recovery behavior validated;
- secret-safe evidence boundary validated;
- GitHub Actions ALL GREEN;
- PR review/comments gate clear;
- post-merge CI green on the merge SHA.
