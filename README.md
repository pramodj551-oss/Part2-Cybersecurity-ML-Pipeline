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

CI uploads the key ML audit artifacts so generated values can be inspected independently of the source repository:

```text
metrics.json
model_comparison.csv
prediction_results.csv
evaluation_report.json
evaluation_summary.json
residual_report.csv
predictions.csv
prediction_summary.json
model_metadata.json
EDA_executed.ipynb
```

## MLOps Capabilities

Beyond the core regression pipeline, the project includes a set of production MLOps controls, each implemented as a standalone, independently tested module:

- **Feature engineering & ablation** (`src/feature_engineering.py`) — reproducible feature engineering with an ablation study measuring the impact of removing feature groups on model performance.
- **Hyperparameter optimization** (`src/hyperparameter_optimization.py`) — deterministic `RandomizedSearchCV` over the top regression models, with preprocessing kept inside the CV pipeline so every fold only learns from its own training rows.
- **Model calibration** (`src/model_calibration.py`) — calibration and decision-threshold optimization.
- **Model explainability** (`src/model_explainability.py`) — feature-importance and local prediction explanations.
- **Drift monitoring** (`src/model_monitoring.py`) — Population Stability Index (PSI) for numeric feature/prediction drift and total-variation-distance drift scoring for categorical features, with configurable thresholds.
- **Automated retraining & lifecycle** (`src/model_lifecycle.py`) — drift-based retraining triggers, CV-based candidate-vs-production model comparison, and an atomic promote/rollback transaction that keeps a model and its preprocessor in sync (staged copy → backup → atomic swap → automatic rollback on failure).
- **Governance / policy-as-code** (`src/governance.py`) — policy-gated promotion decisions (tests, security, drift, canary must all pass), SHA-256 artifact fingerprinting, and an append-only audit log.
- **Production operations** (`src/production_operations.py`) and **production intelligence** (`src/production_intelligence.py`) — operational and resilience/decisioning controls for running the model in production.
- **Inference service** (`src/inference_service.py`) — a FastAPI service with distributed rate limiting and Prometheus metrics, served via the Dockerfile's `uvicorn` entrypoint.

## Repository Structure

```text
Part2-Cybersecurity-ML-Pipeline/
├── data/raw/cybersecurity_incident_reports.csv
├── notebooks/EDA.ipynb
├── src/
│   ├── config.py
│   ├── data_loader.py
│   ├── feature_engineering.py
│   ├── feature_selection.py
│   ├── governance.py
│   ├── hyperparameter_optimization.py
│   ├── inference_service.py
│   ├── logger.py
│   ├── model_calibration.py
│   ├── model_evaluation.py
│   ├── model_explainability.py
│   ├── model_lifecycle.py
│   ├── model_monitoring.py
│   ├── model_training.py
│   ├── pipeline.py
│   ├── predict.py
│   ├── preprocessing.py
│   ├── production_intelligence.py
│   ├── production_operations.py
│   ├── run_pipeline.py
│   └── utils.py
├── scripts/
│   ├── run_sql_queries.py
│   ├── run_step19.py
│   ├── run_step20.py
│   ├── run_step21.py
│   ├── run_step22.py
│   └── smoke_step31.py
├── tests/
│   ├── test_smoke.py
│   ├── test_feature_engineering.py
│   ├── test_hyperparameter_optimization.py
│   ├── test_inference_service.py
│   ├── test_model_calibration.py
│   ├── test_model_explainability.py
│   ├── test_model_lifecycle.py
│   ├── test_model_monitoring.py
│   ├── test_step24_security.py
│   ├── test_step25_monitoring.py
│   ├── test_step26_lifecycle.py
│   ├── test_step27_cd.py
│   ├── test_step28_release.py
│   ├── test_step29_e2e_mlops.py
│   ├── test_step31_production_scale.py
│   ├── test_step32_production_operations.py
│   ├── test_step33_governance.py
│   ├── test_step34_production_intelligence.py
│   └── test_step35_artifact_consistency.py
├── .github/workflows/
│   ├── ci.yml
│   ├── step27-cd.yml
│   ├── step28-release.yml
│   ├── step29-e2e.yml
│   ├── step30-final-audit.yml
│   ├── step31-production-scale.yml
│   ├── step32-production-operations.yml
│   ├── step33-advanced-governance.yml
│   └── step34-production-intelligence.yml
├── deploy/release.env.example
├── docs/
│   ├── STEP32_RUNBOOK.md
│   ├── STEP33_GOVERNANCE.md
│   └── STEP34_PRODUCTION_INTELLIGENCE.md
├── Dockerfile
├── docker-compose.production.yml
├── queries.sql
├── run_pipeline.py
├── requirements.txt
├── LICENSE
├── CHANGELOG.md
└── .gitignore
```

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run_pipeline.py
```

Windows activation:

```text
venv\Scripts\activate
```

## Reproducibility and Security

- `RANDOM_STATE=42` and `CV_FOLDS=5` are centralized in `src/config.py`.
- Cross-validation is performed only on training data.
- The fitted preprocessor is reused during inference.
- The selected feature names are persisted in model metadata and validated during prediction.
- Post-incident fields are excluded from the prediction-time feature contract to reduce leakage risk.
- `.env` files, model binaries, generated outputs, processed datasets, logs, and local databases are ignored by Git.

## CI/CD and Production Validation

The project uses GitHub Actions across nine workflow files (`.github/workflows/`), each covering a distinct stage of validation:

| Workflow | Covers |
| --- | --- |
| `ci.yml` | Python compilation, `pytest`, the full ML pipeline, feature engineering/ablation (STEP 17), hyperparameter optimization (STEP 18), calibration (STEP 19), explainability (STEP 20), drift monitoring (STEP 21), lifecycle/retraining (STEP 22), EDA notebook execution, 29 SQL analytics queries, and runtime-artifact verification for ~24 generated outputs |
| `step27-cd.yml` | Continuous delivery checks |
| `step28-release.yml` | Release validation |
| `step29-e2e.yml` | End-to-end MLOps checks |
| `step30-final-audit.yml` | Final production-readiness audit, including the leakage-guard configuration check |
| `step31-production-scale.yml` | Production scale/smoke tests |
| `step32-production-operations.yml` | Production operations controls |
| `step33-advanced-governance.yml` | Governance / policy-as-code checks |
| `step34-production-intelligence.yml` | Production intelligence and resilience checks |

Docker/CD validation includes image metadata, the container `/health` endpoint, smoke tests, and confirmation that the container runs as a non-root user (see `Dockerfile`).

## Release

**v1.0.0 — Production-Ready Cybersecurity ML Pipeline**

This release represents the first portfolio-ready milestone after completing the ML quality, artifact consistency, CI/CD, monitoring, governance, and production-container validation work.

## Status

**Production-ready regression pipeline with automated security, Docker, CI/CD, monitoring, reproducibility, governance, and rollback-readiness validation.**

Production deployment should still be preceded by environment-specific operational approval and confirmation that all prediction inputs are available at inference time.
