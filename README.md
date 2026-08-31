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

## Repository Structure

```text
Part2-Cybersecurity-ML-Pipeline/
├── data/raw/cybersecurity_incident_reports.csv
├── notebooks/EDA.ipynb
├── src/
│   ├── config.py
│   ├── data_loader.py
│   ├── feature_selection.py
│   ├── logger.py
│   ├── model_evaluation.py
│   ├── model_training.py
│   ├── pipeline.py
│   ├── predict.py
│   ├── preprocessing.py
│   └── utils.py
├── tests/test_smoke.py
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

The project uses GitHub Actions for automated quality and production checks. The validated pipeline includes Python compilation, tests, the complete ML pipeline, EDA, SQL analytics, runtime artifact checks, ML audit artifact upload, and production Docker/CD smoke validation.

The production validation also checks the container health endpoint and verifies that the application does not run as root.

## Release

**v1.0.0 — Production-Ready Cybersecurity ML Pipeline**

This release represents the first portfolio-ready milestone after completing the ML quality, artifact consistency, CI/CD, monitoring, governance, and production-container validation work.

## Status

**Production-ready regression pipeline with automated security, Docker, CI/CD, monitoring, reproducibility, governance, and rollback-readiness validation.**

Production deployment should still be preceded by environment-specific operational approval and confirmation that all prediction inputs are available at inference time.
