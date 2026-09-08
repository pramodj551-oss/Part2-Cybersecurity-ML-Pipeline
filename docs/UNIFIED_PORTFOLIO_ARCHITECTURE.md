# Unified Portfolio Architecture

## Purpose

This document defines the cross-repository architecture and ownership boundaries for the cybersecurity AI/ML portfolio:

- **Part 2 — Cybersecurity ML Pipeline:** model/data/MLOps intelligence engine.
- **Part 3 — Cybersecurity Dashboard:** presentation and analyst-facing inference layer consuming verified Part 2 runtime artifacts.
- **Part 4 — AI/LLM Integration:** incident knowledge assistant providing RAG, LLM reasoning, conversational context, secure document ingestion, and authenticated API access.

The repositories are intentionally complementary. Shared security concepts are implemented independently where the runtime boundary requires them; they are not treated as duplicated implementations unless they provide the same responsibility at the same boundary.

## System Context

```text
                         Cybersecurity AI Portfolio
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
      ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
      │   Part 2     │     │   Part 3     │     │   Part 4     │
      │ ML + MLOps   │────▶│ Dashboard    │     │ RAG + LLM    │
      │ Intelligence │     │ Presentation │     │ Knowledge    │
      └──────┬───────┘     └──────────────┘     └──────┬───────┘
             │                                          │
             │ verified model/runtime artifacts         │ incident knowledge
             │                                          │ + retrieval context
             └──────────────────┐       ┌───────────────┘
                                ▼       ▼
                         Analyst / Application Layer
                                  │
                         Security Intelligence
```

## Repository Ownership

| Repository | Primary responsibility | Must own | Must not own |
|---|---|---|---|
| Part 2 | ML intelligence and MLOps | data contract, training, evaluation, feature engineering, model lifecycle, model monitoring, inference contract, model artifacts | dashboard UI or LLM/RAG orchestration |
| Part 3 | analyst dashboard and presentation | Streamlit UI, visualization, dashboard validation, verified runtime artifact loading, prediction presentation | model retraining, preprocessing refit, LLM orchestration |
| Part 4 | RAG/LLM intelligence service | retrieval, relevance guardrails, prompt/output safety, session memory, document ingestion, authenticated API, LLM resilience | Part 2 model training or Part 3 dashboard artifact ownership |

## Part 2 → Part 3 Contract

Part 3 is a consumer of the Part 2 prediction-time runtime contract.

### Required prediction inputs

The shared prediction schema is:

- `records_affected`
- `detection_time_hours`
- `ransom_demand_usd`
- `sector`
- `region`
- `attack_type`
- `threat_actor`
- `data_exfiltration`
- `zero_day_used`

Target: `severity_score`.

Post-incident response/outcome fields such as `downtime_hours`, `response_team_size`, `regulatory_fine_usd`, and `resolved_within_7_days` are excluded from prediction-time input.

### Runtime artifacts

Part 3 requires the verified Part 2 runtime bundle:

```text
models/best_model.pkl
models/preprocessor.pkl
models/feature_columns.pkl
outputs/evaluation_report.json
outputs/metrics.json
outputs/feature_importance.csv
```

The consumer must validate artifact identity/integrity before inference. Part 3 must not retrain the model or refit preprocessing.

### Contract change policy

Any change to prediction feature names/types, preprocessing behavior, model serialization format, required artifacts, or output semantics is a **breaking contract change**. The producer and consumer documentation/tests must be updated together before merge.

## Part 2 → Part 4 Relationship

Part 4 is **not** a direct runtime consumer of the Part 2 regression model in the current architecture. It is a separate incident-knowledge intelligence path.

Part 4 owns:

```text
incident documents
      ↓
embeddings
      ↓
FAISS retrieval
      ↓
relevance guardrail
      ↓
bounded session context
      ↓
prompt-grounded LLM
      ↓
safe response
```

A future integration may expose Part 2 model outputs to Part 4 as trusted structured context, but such an integration must define a versioned API/schema rather than reading another repository's internal files directly.

## Cross-Repository Data Boundaries

```text
Part 2 raw incident data
        │
        ├── training/evaluation only inside Part 2
        │
        ▼
verified ML runtime bundle
        │
        └──────────────▶ Part 3

Part 4 incident knowledge base
        │
        ▼
FAISS + JSON document store
        │
        ▼
RAG/LLM service
```

No repository should silently become the source of truth for another repository's private implementation details.

## Shared Security Baseline

All three repositories should preserve these portfolio-level principles:

1. Validate external input at the boundary.
2. Fail closed for invalid or unverifiable runtime artifacts/configuration.
3. Never commit real credentials or deployment secrets.
4. Avoid raw sensitive request content in telemetry.
5. Keep health/readiness semantics deterministic.
6. Maintain regression tests for security controls.
7. Require CI to pass before merge.
8. Treat deployment evidence separately from source-code readiness.

Controls remain repository-local when their trust boundary differs. Examples include Part 3 artifact hash enforcement and Part 4 API-key/RAG guardrails.

## Observability Ownership

| Concern | Part 2 | Part 3 | Part 4 |
|---|---|---|---|
| model/prediction monitoring | owner | consumer/presentation | optional future consumer |
| dashboard/runtime health | — | owner | — |
| RAG/retrieval quality | — | — | owner |
| API/request telemetry | inference service | dashboard runtime | authenticated API |
| cross-service observability | future portfolio layer | future portfolio layer | future portfolio layer |

Process-local metrics must not be represented as a distributed production monitoring system. A future enterprise deployment may introduce shared Prometheus/OpenTelemetry and coordination infrastructure.

## Duplicate / Overlap Policy

The following are intentionally repeated because they protect different trust boundaries:

- **Authentication:** Part 2 protects ML inference; Part 4 protects the RAG API.
- **Health/readiness:** each deployable runtime needs its own probe.
- **Observability:** each service records service-local operational signals.
- **Input/resource validation:** each application validates its own external inputs.
- **Artifact integrity:** Part 2 manages model lifecycle; Part 3 verifies the runtime bundle it consumes.

The following should be centralized or standardized at portfolio level where practical:

- architecture terminology
- security baseline language
- API/error conventions
- version/release documentation conventions
- cross-repository contract versioning
- deployment evidence format

## Portfolio Verification Gates

Before declaring the integrated portfolio production-ready:

### Gate A — Architecture

- Repository ownership boundaries are documented.
- Cross-repository contracts are versioned or explicitly identified as stable.
- No repository relies on undocumented internal files from another repository.

### Gate B — Runtime Integration

- Part 3 consumes a verified Part 2 runtime bundle.
- Target deployment has access to the required artifacts.
- Real prediction smoke test passes in the target environment.

### Gate C — AI/LLM Runtime

- Part 4 health/readiness checks pass.
- Authenticated API smoke test passes.
- RAG relevance and output guardrails pass.
- Deployment secrets are supplied by the environment/secret manager.

### Gate D — Operational Resilience

- Deployment health and rollback evidence exists.
- Monitoring/alerting is available at the target deployment boundary.
- Distributed infrastructure is used when multiple workers/replicas require shared state.

## Current Status

This H1 document establishes the portfolio architecture and contract baseline. It does **not** claim live deployment evidence. H2 is responsible for proving target-environment deployment, artifact access, authenticated smoke tests, and rollback behavior.

## Change Management

Architecture changes should be made in the repository that owns the affected boundary and cross-referenced in the other affected repository documentation. Breaking contract changes require synchronized tests and documentation before merge.
