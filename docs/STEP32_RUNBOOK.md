# STEP 32 Production Operations Runbook

## SLOs
Availability >= 99.5%, P95 latency <= 500 ms, error rate <= 1%.

## Incident response
Confirm the alert, check health/readiness/metrics, roll back a failing canary, preserve evidence, and document follow-up actions.

## Retraining
Drift or performance degradation creates a retraining decision. Candidates require validation and canary approval before promotion.

## Security
Secrets are environment-provided; CI performs continuous validation.
