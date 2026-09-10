# H2 — Live Deployment Evidence Contract

**Status: IN PROGRESS — live deployment and rollback gates have been executed; final repository traceability is being consolidated. H2 PASS is not declared until every required gate is backed by recorded evidence.**

## Evidence gates

| Gate | Current state |
| --- | --- |
| Part 2 release | PASS — existing STEP 38 evidence |
| Part 2 rollback | PASS — existing STEP 38 evidence |
| Part 3 target + runtime artifacts | PASS — canonical Streamlit target; 6/6 runtime artifacts verified |
| Part 3 prediction + Dataset Explorer smoke | PASS — 1,600 × 16 dataset; prediction and exploration completed |
| Part 3 health/readiness | PASS — recorded runtime response tied to `c97963eca1b078663bc7c60daa9506285404a4e7` |
| Part 3 actual rollback target | PASS — user-confirmed |
| Part 3 rollback smoke | PASS — user-confirmed; prediction, Dataset Explorer/EDA, health/readiness, restoration, and current-version smoke completed |
| Part 4 target deployment | PASS — Render Web Service `part4-ai-cybersecurity-api`; `https://part4-ai-cybersecurity-api.onrender.com`; deployment ID `dep-dagk5u0ae00c73bulro0`; source `f11f16c0202bf6d9571ba6e888987b101ac058ea` |
| Part 4 readiness | PASS — `/health` 200 and `/ready` ready v1.5.0 |
| Part 4 authenticated query | PASS — `POST /v1/query` 200 |
| Part 4 Streamlit UI smoke | PASS — Version 1.5.0 loaded; one session document indexed; memory `0/5 turns` |
| Part 4 secret safety | PASS — supplied sanitized Render startup log showed no API-key/token/cookie/authorization values or sensitive payloads |
| Part 4 rollback | PASS — user-confirmed rollback to previous known-good `0adf18a`, rollback smoke passed, and current `f11f16c` restored |
| Cross-repo target evidence | PASS for executed target/smoke gates; final repository traceability is being consolidated |

## Part 3 live runtime evidence

Canonical dashboard target:

`https://part3-cybersecurity-dashboard.streamlit.app/`

Deployed/restored runtime commit:

`c97963eca1b078663bc7c60daa9506285404a4e7`

Six-artifact runtime contract: **6/6 verified**.

Verified artifact identities remain as previously recorded:

- `models/best_model.pkl` — `ca26113983a882b1b72ff619eb3c7eb64a379352a96521e3ca9c1845c1823c62`
- `models/preprocessor.pkl` — `5edeced95052788e42d8ea4324ff24d2d58afc4886897c2effc87ebf9ce348ba`
- `models/feature_columns.pkl` — `67582cd2c06082b290350a54177032410428b1b48a6e1f2d2067e53f8c2f5aff`
- `outputs/evaluation_report.json` — `83e2bd6fc191eb14257f44c8c76340e0bf92af13af0ed9ba24a5815b7a3ec59d`
- `outputs/metrics.json` — `d26201cbebd7321343619c09e6d384adef2ca4d7411d9eb757fda59a203f13eb`
- `outputs/feature_importance.csv` — `a5dbba7dab6a86ac184d84e450ce6ef4873774f8a7a3706485720995abe6ca16`

Health/readiness evidence recorded:

```json
{
  "status": "ready",
  "contract_version": "1",
  "runtime_commit": "c97963eca1b078663bc7c60daa9506285404a4e7",
  "liveness": {"status": "ok", "check": "liveness", "contract_version": "1"},
  "readiness": {
    "status": "ready",
    "check": "readiness",
    "contract_version": "1",
    "runtime_commit": "c97963eca1b078663bc7c60daa9506285404a4e7",
    "artifacts": {"status": "ready", "identity_verified": true, "verified_files": 6},
    "model": {"status": "ready", "model_predict_callable": true, "preprocessor_transform_callable": true, "feature_columns": 20}
  },
  "duration_ms": 13.695
}
```

Functional smoke:

- Prediction smoke: PASS.
- Input dataset: `cybersecurity_incident_reports.csv`.
- Dataset size: 1,600 rows × 16 columns.
- Observed severity score: `4.669436934238102`.
- Dataset Explorer smoke: PASS.
- Missing values: 0.
- Duplicate records: 0.

Part 3 rollback smoke: **PASS — user-confirmed**. The user reported rollback target selection, rollback completion, prediction smoke, Dataset Explorer smoke, health/readiness, restoration of `c97963...`, and current-version smoke. The exact previous deployment identifier is still not recorded in the repository document; therefore this remains a traceability caveat even though the execution gate was reported PASS.

## Part 4 live deployment evidence

Deployment platform: **Render Web Service + Docker**.

Service: `part4-ai-cybersecurity-api`.

Public API target:

`https://part4-ai-cybersecurity-api.onrender.com`

Immutable deployment ID:

`dep-dagk5u0ae00c73bulro0`

Deployment source commit:

`f11f16c0202bf6d9571ba6e888987b101ac058ea`

Recorded runtime evidence:

```text
Docker image export/push: completed
Uvicorn running on http://0.0.0.0:10000
GET /health HTTP/1.1" 200 OK
Your service is live
POST /v1/query HTTP/1.1" 200 OK
```

`/ready` returned:

```json
{"status":"ready","version":"1.5.0"}
```

### Part 4 Streamlit UI

Live Version 1.5.0 UI evidence includes Incident Knowledge Assistant, Semantic Search, FAISS, Sentence Transformers, Groq LLM and Streamlit UI indicators. `cybersecurity_incident_reports.csv` was uploaded and indexed as 1 ephemeral session document; memory displayed `0/5 turns`; query input was available.

### Memory evidence boundary

Render Free-plan metrics do not expose exact observed peak memory. Successful startup and smoke do not justify an exact 512 MiB claim. No exact peak-memory value is claimed.

## Secret-safety gate

No secret values are recorded here.

The supplied sanitized Render startup log contained generic platform messages including:

```text
Environment variables injected ...
Application loading
```

Review result:

**Secret Safety: PASS — no API-key values, bearer tokens, authorization credentials, cookies, or sensitive request/response payloads were observed in the supplied log.**

The generic phrase `Environment variables injected` is not itself a credential disclosure.

## Rollback evidence

### Part 2

Previous-image rollback remains **PASS** under STEP 38 evidence.

### Part 3

**PASS — user-confirmed.** Rollback smoke was reported complete, including prediction, Dataset Explorer/EDA, health/readiness, restoration of current `c97963...`, and current-version smoke. Exact previous deployment target identifier remains the only repository traceability caveat.

### Part 4

**PASS — user-confirmed.** Previous known-good target: `0adf18a`. Current restored target: `f11f16c`. The user confirmed rollback completion, rollback smoke, `/health`, `/ready`, authenticated `/v1/query`, functional smoke, and restoration of the current version.

## H2 acceptance rule

H2 is **PASS** only when the target deployment evidence is attached through sanitized CI logs/artifacts or a documented external deployment record, the actual target smoke tests pass, and the rollback targets are traceable.

**Current overall state: IN PROGRESS** because the exact Part 3 previous rollback deployment identifier has not yet been recorded in this repository evidence document.

## Final execution sequence

1. Consolidate evidence on `feature/h2-final-evidence`.
2. Run CI and require **ALL GREEN**.
3. Create PR to `main`.
4. Verify review/comments gate.
5. Merge only after CI is green and the review/comments gate is clear.
6. Verify post-merge CI on the merge SHA.
7. Declare H2 **PASS** only after the post-merge verification and final traceability gate are closed.
