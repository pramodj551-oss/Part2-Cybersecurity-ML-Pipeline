# STEP 34 — Production Intelligence

## Decision states
- **healthy**: observe and continue normal operation.
- **degraded**: alert/investigate and hold model promotion.
- **critical**: stop rollout, rollback, and page on-call.

## Signals
Availability, P95 latency, error rate, and drift score are evaluated together. Thresholds are intentionally conservative and should be tuned against production SLOs.

## Resilience
Automated actions never bypass governance gates. Critical conditions use the existing rollback path; degraded conditions prevent promotion until investigated.
