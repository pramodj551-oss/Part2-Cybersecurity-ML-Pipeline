# H2 — Live Deployment Evidence Contract

**Status: IN PROGRESS — evidence is being consolidated from real target environments; H2 PASS is not declared until every required gate has actual evidence.**

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
| Part 3 target deployment | Actual deployed dashboard URL/target | PASS — canonical Streamlit target recorded: `https://part3-cybersecurity-dashboard.streamlit.app/` |
| Part 3 artifact access | Target uses the verified six-artifact runtime contract | PASS — 6/6 runtime artifacts matched the manifest; identity verification succeeded |
| Part 3 prediction smoke | Real target prediction request succeeds | PASS — prediction smoke completed against `cybersecurity_incident_reports.csv` (1,600 × 16); observed severity score `4.669436934238102` |
| Part 3 Dataset Explorer smoke | Real target dataset exploration succeeds | PASS — 1,600 × 16; missing values 0; duplicate records 0; preview/column information loaded |
| Part 3 health/readiness | Target `/health` and `/ready` evidence | PASS — recorded runtime response below |
| Part 4 target deployment | Actual deployed API target + immutable deployment identity | PARTIAL — Render service `part4-ai-cybersecurity-api` is live, but exact public API URL and platform deployment ID are not yet recorded here |
| Part 4 readiness | `/health` and `/ready` pass on the target | PASS — Render deployment log shows `/health` HTTP 200; `/ready` returned `{"status":"ready","version":"1.5.0"}` |
| Part 4 authenticated query | Protected endpoint succeeds with deployment-managed secret | PASS — Render deployment log shows `POST /v1/query` HTTP 200 |
| Part 4 secret safety | No credential leakage in deployment logs | PENDING — explicit sanitized log review record still required |
| Cross-repo integration | Part 2 → Part 3 contract and Part 4 boundary verified | PARTIAL — Part 3 artifact contract and Part 4 API boundary are evidenced; final consolidated cross-repo target record remains pending |
| Part 3 rollback | Target can return to previous known-good version | PENDING — no actual target rollback smoke evidence recorded |
| Part 4 rollback | Target can return to previous known-good version | PENDING — no actual Render rollback smoke evidence recorded |

## Part 3 live runtime evidence

### Target

Canonical dashboard target:

`https://part3-cybersecurity-dashboard.streamlit.app/`

### Runtime identity

- deployed runtime commit: `c97963eca1b078663bc7c60daa9506285404a4e7`
- six-artifact runtime contract: **6/6 verified**
- runtime artifact identity: **verified**

Verified artifact SHA-256 identities:

| Artifact | SHA-256 |
| --- | --- |
| `models/best_model.pkl` | `ca26113983a882b1b72ff619eb3c7eb64a379352a96521e3ca9c1845c1823c62` |
| `models/preprocessor.pkl` | `5edeced95052788e42d8ea4324ff24d2d58afc4886897c2effc87ebf9ce348ba` |
| `models/feature_columns.pkl` | `67582cd2c06082b290350a54177032410428b1b48a6e1f2d2067e53f8c2f5aff` |
| `outputs/evaluation_report.json` | `83e2bd6fc191eb14257f44c8c76340e0bf92af13af0ed9ba24a5815b7a3ec59d` |
| `outputs/metrics.json` | `d26201cbebd7321343619c09e6d384adef2ca4d7411d9eb757fda59a203f13eb` |
| `outputs/feature_importance.csv` | `a5dbba7dab6a86ac184d84e450ce6ef4873774f8a7a3706485720995abe6ca16` |

### Health/readiness runtime response

Recorded target response:

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

### Functional smoke evidence

- Prediction smoke: PASS.
- Input dataset: `cybersecurity_incident_reports.csv`.
- Dataset size: 1,600 rows × 16 columns.
- Observed severity score: `4.669436934238102`.
- Dataset Explorer smoke: PASS.
- Missing values: 0.
- Duplicate records: 0.

## Part 4 live deployment evidence

### Deployment target

Deployment platform: **Render Web Service + Docker**.

Render service identifier: `part4-ai-cybersecurity-api`.

The repository-side deployment contract is version-controlled in `render.yaml` and uses Docker with `/health` as the health-check path. The dedicated FastAPI service is separate from the Streamlit UI.

### Deployment/runtime evidence recorded

The actual Render deployment log records:

```text
Docker image export/push: completed
Deploying...
Uvicorn running on http://0.0.0.0:10000
GET /health HTTP/1.1" 200 OK
GET /health HTTP/1.1" 200 OK
Your service is live
```

The same deployment runtime recorded:

```json
{"status":"ready","version":"1.5.0"}
```

for `/ready`, and the deployment log recorded:

```text
POST /v1/query HTTP/1.1" 200 OK
```

These are treated as actual target-environment runtime evidence, not as CI-only evidence.

### Memory evidence boundary

Render application metrics on the Free plan do not expose the exact observed peak memory value. The runtime deployment did start successfully and passed `/health`, `/ready`, and authenticated `/v1/query`, so the prior startup OOM did not recur in the recorded deployment. **No exact peak-memory value or 512 MiB threshold PASS is claimed.**

## Secret-safety gate

No secret values are recorded in this document.

The deployment contract requires `P8_API_KEY`, `P8_ADMIN_API_KEY`, and `GROQ_API_KEY` to remain external to source control. The repository-side Blueprint uses secret placeholders rather than values.

**H2 gate state: PENDING** until a sanitized deployment-log review explicitly records that no credential/API-key/token/cookie values were exposed in the target deployment logs.

## Rollback evidence

### Part 2

Part 2 previous-image rollback is already covered by STEP 38 and remains **PASS**.

### Part 3

No actual target-environment rollback smoke result is currently recorded in this document. **PENDING.**

### Part 4

No actual Render rollback deployment identifier plus post-rollback `/health`/`/ready`/functional smoke result is currently recorded in this document. **PENDING.**

## Cross-repo integration state

Current evidence establishes:

- Part 2 has an immutable release/rollback baseline.
- Part 3 is running a verified six-artifact runtime bundle and has successful target functional smoke evidence.
- Part 3 has recorded health/readiness runtime evidence tied to its deployed commit.
- Part 4 has a dedicated Render FastAPI deployment with successful `/health`, `/ready`, and authenticated `/v1/query` runtime evidence.

The final cross-repo H2 gate remains open until deployment identities/targets are fully recorded and the secret-safety and Part 3/Part 4 rollback evidence are attached.

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

## H2 acceptance rule

H2 is **PASS** only when the target deployment evidence above is attached to the repository through sanitized CI logs/artifacts or a documented external deployment record, and the actual target smoke tests pass.

Current overall state is **IN PROGRESS** because the following gates are still open:

1. Part 4 exact public API target URL and immutable platform deployment identifier.
2. Explicit sanitized secret-safety log review.
3. Part 3 actual rollback target + rollback smoke evidence.
4. Part 4 actual rollback target + rollback smoke evidence.
5. Final consolidated cross-repo target record.

Until these are complete, portfolio wording must distinguish:

- **Source/CI production hardening:** demonstrated.
- **Release/runtime verification:** demonstrated where evidence exists.
- **Live deployment:** demonstrated only for the specific target evidence recorded above.
- **Portfolio-wide H2 PASS:** not yet claimed.

## Next execution step

Capture the remaining real target-environment records, append them to this document through a feature branch and PR, run CI, review the evidence, and declare H2 **PASS** only after every required gate is backed by actual evidence. No deployment result is fabricated.
