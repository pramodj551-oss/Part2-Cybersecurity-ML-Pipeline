# STEP 38–39 Post-Release Verification

## Release baseline

The `v1.1.0` GitHub Release is the production-release baseline. The `v1.1.0` tag points to commit `ec95e88f154dcc8c552ef4914fec30ce7baa2dd5`.

The current `main` branch may advance beyond the release tag. STEP 39 monitoring/observability changes were merged to `main` after the `v1.1.0` release baseline; therefore `v1.1.0` is not claimed to contain every later `main` commit.

## STEP 38 — Post-release verification

Workflow: `.github/workflows/step38-post-release-verification.yml`

The workflow verifies the published `v1.1.0` GHCR image, including GHCR authentication, image pull/inspection, secret-based API-key smoke testing, `/health`, protected endpoint authentication, non-root runtime validation, and real `v1.0.0` rollback validation.

Existing regression and security coverage is retained and is not replaced by STEP 38.

## STEP 39 — Production monitoring & observability

Workflow: `.github/workflows/step39-production-monitoring.yml`

Production observability is implemented in `src/production_observability.py` and tested by `tests/test_production_observability.py`.

Monitoring covers request totals, error rate, latency, HTTP status distribution, prediction PSI drift, target drift, deterministic alert thresholds, and protection against emitting API secrets.

STEP 39 runs on pushes and pull requests targeting `main`, and can also be manually dispatched.

## Evidence

The project treats actual GitHub Actions execution evidence—not README claims alone—as the authoritative validation evidence. STEP 38 verifies the release artifact by actually pulling and running the `v1.1.0` GHCR image. STEP 39 validates the monitoring implementation on merged `main`.
