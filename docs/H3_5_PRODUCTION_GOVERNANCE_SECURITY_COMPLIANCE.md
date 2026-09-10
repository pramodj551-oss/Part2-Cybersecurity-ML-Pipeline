# H3.5 — Production Governance, Security & Compliance Validation

## Objective

Provide deterministic, auditable production governance, security and compliance validation without storing or emitting credentials.

## Governance controls

- Explicit promotion/rejection decision.
- Required tests, security, drift and canary gates.
- Immutable runtime/release identity required for promotion.
- SHA-256 artifact fingerprinting for integrity evidence.
- Policy version recorded with the decision.

## Security controls

- Detect common API-key, bearer-token, password and secret patterns in operational evidence.
- Never print or persist credential values.
- Keep evidence limited to sanitized status, identity and outcome fields.
- Failed security evidence must reject promotion.

## Compliance controls

- Reproducibility requires `RANDOM_STATE=42` and `CV_FOLDS=5`.
- Audit evidence requires an explicit timestamp.
- Governance decisions expose failed checks deterministically.
- Runtime identities must be immutable identifiers, not mutable aliases.

## Testing contract

`tests/test_h3_5_governance_security_compliance.py` validates:

1. all governance/compliance gates promote when satisfied;
2. security failure rejects promotion;
3. missing immutable identity rejects promotion;
4. reproducibility configuration;
5. deterministic artifact SHA-256 fingerprints;
6. secret-pattern detection without exposing values;
7. sanitized operational evidence;
8. invalid policy configuration.

## CI gate

The dedicated H3.5 test must pass together with the existing full regression/security, ML pipeline, artifact, observability, and integration checks.

H3.5 is PASS only after Actions are ALL GREEN, PR review/comments are clear, merge succeeds, and post-merge CI is verified.
