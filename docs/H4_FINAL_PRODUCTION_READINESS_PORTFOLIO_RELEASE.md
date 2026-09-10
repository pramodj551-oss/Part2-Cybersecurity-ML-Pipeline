# H4 — Final Production Readiness / Portfolio Release Validation

**Status: IMPLEMENTATION + TESTING**

H4 is the final deterministic gate for declaring the Part 2 portfolio production-ready.

## Required gates

1. H3.1 cross-repository integration contract
2. H3.2 integration runtime validation
3. H3.3 production integration and failure-resilience validation
4. H3.4 production observability and bounded automated recovery
5. H3.5 production governance, security and compliance
6. Part 2 → Part 3 six-file runtime artifact contract
7. Part 3 live deployment evidence and health/readiness baseline
8. Part 4 deployment boundary and authenticated runtime evidence
9. Security, secret-safety and compliance evidence
10. Reproducibility controls (random state 42, CV folds 5)
11. Rollback readiness with a known-good immutable identity
12. Immutable release identity and portfolio boundary integrity

## Runtime bundle

The required Part 3 runtime bundle is exactly:

- `models/best_model.pkl`
- `models/preprocessor.pkl`
- `models/feature_columns.pkl`
- `outputs/evaluation_report.json`
- `outputs/metrics.json`
- `outputs/feature_importance.csv`

## Recorded deployment baselines

Part 3 target: `https://part3-cybersecurity-dashboard.streamlit.app/`

Part 3 runtime commit: `c97963eca1b078663bc7c60daa9506285404a4e7`

Part 4 API target: `https://part4-ai-cybersecurity-api.onrender.com`

Part 4 service: `part4-ai-cybersecurity-api`

Part 4 immutable deployment: `dep-dagk5u0ae00c73bulro0`

Part 4 source commit: `f11f16c0202bf6d9571ba6e888987b101ac058ea`

## Security evidence boundary

H4 source and evidence must never contain API keys, bearer tokens, cookies, passwords, or sensitive request payloads. Deployment-managed secrets are represented only by safe configuration names.

## Release and rollback

A production-ready release must have an immutable release identity tied to a source commit. Rollback must identify a previously known-good immutable version and must not claim restoration until health/readiness validation succeeds.

## CI and merge policy

H4 requires dedicated automated tests plus the existing full CI pipeline. The feature branch must pass CI before PR creation where possible. PR review/comments must be clear. Merge is allowed only after all checks are green. Post-merge CI on the merge SHA is required before H4 can be declared PASS.

**H4 PASS is prohibited on partial or documentation-only evidence.**
