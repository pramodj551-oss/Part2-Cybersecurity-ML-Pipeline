# 🤖 AI-Powered Cybersecurity ML Pipeline

**Part 2 of the End-to-End Applied AI & ML Data Product Capstone Project**

A modular, reproducible cybersecurity **regression** pipeline that predicts `severity_score` from historical incident data.

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

## Generated Artifacts

The pipeline generates model, metadata, feature-importance, comparison, evaluation, prediction, and logging outputs under the configured `models/` and `outputs/` directories. Runtime model/output artifacts are intentionally ignored by Git.

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
- `.env` files, model binaries, generated outputs, processed datasets, logs, and local databases are ignored by Git.

## Status

**Production-ready regression pipeline — subject to validation of business-time feature availability for `severity_score`.**
