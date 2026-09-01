# 🤖 AI-Powered Cybersecurity ML Pipeline

**Part 2 of the End-to-End Applied AI & ML Data Product Capstone Project**

A modular, reproducible cybersecurity **regression** pipeline that predicts `severity_score` from historical incident data.

## ⭐ Project Highlights

- End-to-end regression pipeline from raw cybersecurity incidents to production-ready inference.
- Leakage-aware train/test workflow with training-only preprocessing and 5-fold cross-validation.
- Model comparison across Linear Regression, Decision Tree, Random Forest, and Gradient Boosting.
- Persisted model, preprocessor, feature contract, evaluation, prediction, residual, drift, and lifecycle artifacts.
- Automated CI validation covering `compileall`, `pytest`, the complete ML pipeline, EDA execution, SQL analytics, and runtime artifact verification.
- Automated ML audit artifact upload for reproducible inspection of metrics and prediction outputs.
- Production Docker/CD validation including image metadata, health endpoint, smoke tests, and non-root container verification.
- MLOps capabilities covering monitoring, drift detection, automated retraining decisions, model lifecycle/registry controls, governance, and rollback-readiness checks.
- STEP 38 post-release verification of the published `v1.1.0` GHCR image, secret-based authentication, non-root runtime, and real `v1.0.0` rollback.
- STEP 39 production monitoring and observability for request/error metrics, latency, prediction drift, target drift, deterministic alerts, and secret-emission protection.

## Project Overview

The pipeline covers data loading and schema validation, train/test splitting, training-only missing-value fitting, encoding/scaling, variance filtering, model-based feature selection, regression model comparison, holdout evaluation, artifact persistence, and inference.

## Target and Model Type

- **Target:** `severity_score`
- **Problem type:** Regression
- **Models:** Linear Regression, Decision Tree Regressor, Random Forest Regressor, Gradient Boosting Regressor
- **Model selection:** 5-fold cross-validation on the training set; the test set is reserved for final holdout evaluation.

## Dataset

The repository contains the raw dataset at:

```text
data/raw/cybersecurity_incident_reports.csv
```

The target is `severity_score`. The current implementation uses the configured numerical and categorical incident fields in `src/config.py`.

## Workflow

```text
Raw Dataset
   ↓
Schema Validation
   ↓
Train/Test Split
   ↓
Train-only Imputation
   ↓
Fitted Preprocessor
   ↓
Feature Selection (train only)
   ↓
5-fold CV on Training Data
   ↓
Best Regression Model
   ↓
Final Holdout Evaluation on Test Data
   ↓
Model + Preprocessor + Feature Contract
   ↓
Prediction
```

## Prediction-time feature contract

The production prediction contract uses only features declared in `src/config.py` under `NUMERICAL_FEATURES` and `CATEGORICAL_FEATURES`. Post-incident response fields such as `downtime_hours`, `response_team_size`, `regulatory_fine_usd`, and `resolved_within_7_days` are explicitly excluded from prediction because they are not guaranteed to be available at prediction time.

The STEP 30 audit workflow verifies that this exclusion remains present in the source configuration, providing an automated guard against accidental leakage into the inference contract. Business owners should still confirm that every production input is operationally available at the point of prediction.

## Generated Artifacts

The pipeline generates model, metadata, feature-importance, comparison, evaluation, prediction, residual, monitoring, lifecycle, and logging outputs under the configured `models/` and `outputs/` directories. Runtime model/output artifacts are intentionally ignored by Git.

CI uploads key ML audit artifacts so generated values can be inspected independently from source code.

## MLOps Capabilities

Beyond the core regression pipeline, the project includes independently tested production MLOps controls:

- **Feature engineering & ablation** (`src/feature_engineering.py`)
- **Hyperparameter optimization** (`src/hyperparameter_optimization.py`)
- **Model calibration** (`src/model_calibration.py`)
- **Model explainability** (`src/model_explainability.py`)
- **Drift monitoring** (`src/model_monitoring.py`)
- **Automated retraining & lifecycle** (`src/model_lifecycle.py`)
- **Governance / policy-as-code** (`src/governance.py`)
- **Production operations** (`src/production_operations.py`)
- **Production intelligence** (`src/production_intelligence.py`)
- **Inference service** (`src/inference_service.py`)
- **Production observability** (`src/production_observability.py`) — request/error metrics, latency, HTTP status distribution, prediction PSI, target drift, and deterministic alert thresholds.

## STEP 38 — Post-Release Verification

Workflow: `.github/workflows/step38-post-release-verification.yml`

STEP 38 verifies the published production image:

```text
ghcr.io/pramodj551-oss/cybersecurity-ml-pipeline:v1.1.0
```

It performs an actual GHCR pull and image inspection, uses the repository secret `STEP28_SMOKE_API_KEY` for authenticated smoke tests, validates protected endpoints, confirms non-root runtime, and pulls and runs the previous known-good `v1.0.0` image for rollback validation.

Existing regression and security tests remain part of CI and are not replaced by STEP 38.

## STEP 39 — Production Monitoring & Observability

Workflow: `.github/workflows/step39-production-monitoring.yml`

Implementation: `src/production_observability.py`

Tests: `tests/test_production_observability.py`

STEP 39 provides deterministic production observability for request totals, error rate, average latency, HTTP status distribution, prediction PSI, target drift, and alert thresholds. The monitoring implementation is also checked for accidental emission of API secrets.

The STEP 39 workflow runs on pushes and pull requests targeting `main` and supports manual dispatch. It retains the full regression/security suite and the existing model-monitoring tests.

## CI/CD and Production Validation

GitHub Actions provides the authoritative execution evidence. README claims are documentation only; release and production gates are considered validated only when their actual workflow runs and logs pass.

The reproducibility contract requires the documented training seed **`RANDOM_STATE=42`**. This value is part of the CI documentation contract and must remain aligned with the implementation/tests.

| Workflow | Covers |
| --- | --- |
| `ci.yml` | Python compilation, full `pytest`, complete ML pipeline, EDA, SQL analytics, and runtime artifact verification |
| `step27-cd.yml` | Continuous delivery checks |
| `step28-release.yml` | Release validation, GHCR build/push, secret-based smoke, and rollback validation |
| `step29-e2e.yml` | End-to-end MLOps checks |
| `step30-final-audit.yml` | Final production-readiness and leakage-guard audit |
| `step31-production-scale.yml` | Production scale/smoke tests |
| `step32-production-operations.yml` | Production operations controls |
| `step33-advanced-governance.yml` | Governance / policy-as-code checks |
| `step34-production-intelligence.yml` | Production intelligence and resilience checks |
| `step38-post-release-verification.yml` | Published v1.1.0 GHCR runtime and real v1.0.0 rollback verification |
| `step39-production-monitoring.yml` | Production monitoring, drift, alert, and observability validation |

## Release Baseline and Current Main

**v1.1.0** is the published production-release baseline. Its Git tag points to commit `ec95e88f154dcc8c552ef4914fec30ce7baa2dd5`.

`main` may advance after a release. STEP 39 monitoring/observability was merged after the `v1.1.0` release baseline. Therefore, `v1.1.0` must not be interpreted as containing later `main` commits unless a later release is published.

This distinction is intentional: a release tag identifies an immutable release baseline, while `main` represents the current integration state.

## Release

**v1.1.0 — Production Release 🚀**

The v1.1.0 release completed the production release gates for Docker/GHCR, API-key enforcement, non-root container execution, regression/security validation, and real previous-image rollback.

## Status

**Production-ready cybersecurity ML pipeline with automated security, Docker, CI/CD, monitoring, reproducibility, governance, and rollback-readiness validation.**

Production deployment should still be preceded by environment-specific operational approval and confirmation that all prediction inputs are available at inference time.
