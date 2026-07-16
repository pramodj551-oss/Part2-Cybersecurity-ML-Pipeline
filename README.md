# 🤖 AI-Powered Cybersecurity ML Pipeline

**Part 2 of the End-to-End Applied AI & ML Data Product Capstone Project**

A production-ready, modular Machine Learning pipeline for cybersecurity incident analysis, preprocessing, feature engineering, model training, evaluation, and prediction. This project demonstrates an end-to-end ML workflow built using software engineering best practices, making it suitable for real-world applications and portfolio showcase.

---

## Project Overview

Cybersecurity organizations generate large volumes of incident data every day. Transforming this raw data into meaningful insights requires a structured, reproducible machine learning pipeline.

This repository answers the second analytics question in the capstone series — **Predictive Analytics: What is likely to happen?** — by learning patterns from historical incidents to classify future incident severity/risk, so analysts can focus on the most critical events first.

The trained model produced here feeds directly into the interactive dashboard (Part 3) and the AI-powered assistant (Part 4).

The pipeline covers:

- Data loading and validation
- Exploratory Data Analysis (EDA)
- Data preprocessing and missing value handling
- Feature engineering and feature selection
- Machine learning model training
- Model evaluation and comparison
- Model persistence and prediction pipeline
- Logging and configuration management
- Reproducible, modular project structure

---

## Business Problem

Cybersecurity teams receive thousands of security alerts every day. Historical reports explain what has already happened — but organizations also need to anticipate future risk. Manual prioritization is slow and inconsistent, making it difficult to flag high-risk incidents early.

This project trains a Machine Learning model on historical cybersecurity incident data to predict incident severity, helping analysts prioritize the most critical events first.

---

## Analytics Objectives

This project aims to answer:

- Which cybersecurity incidents are likely to become high risk?
- Can incident severity be predicted from historical patterns?
- Which features contribute most to cybersecurity risk?
- Which Machine Learning algorithm performs best?
- How accurately can future incidents be classified?

---

## Dataset

This project uses the cleaned, feature-engineered cybersecurity incident dataset produced in **Part 1**.

**Location:**
```text
data/processed/engineered_incidents.csv
```

If unavailable, regenerate it by running the Part 1 ETL pipeline.

**Key fields:**

| Field | Description |
|---|---|
| Incident ID | Unique identifier for each incident |
| Incident Date | Date the incident occurred |
| Attack Type | Category of cyberattack |
| Severity Score | Target variable — incident severity/risk level |
| Industry Sector | Sector affected |
| Region | Geographic region |
| Threat Actor | Source/type of threat actor |
| Records Affected | Number of records compromised |
| Downtime Hours | System downtime caused by the incident |
| Financial Impact | Estimated financial loss |
| Regulatory Fine | Fine imposed, if any |
| Response Team Size | Size of the incident response team |
| Engineered Features | Additional features derived in Part 1 |

---

## Machine Learning Workflow

1. Data Loading
2. Data Validation
3. Feature Encoding
4. Missing Value Handling
5. Feature Scaling (where required)
6. Feature Selection
7. Train/Test Split
8. Model Training
9. Model Evaluation
10. Model Comparison
11. Best Model Selection
12. Model Saving

The final trained model is a **Random Forest classifier**, saved for future inference and dashboard integration.

---

## Key Features

- End-to-end, production-ready ML pipeline
- Modular Python architecture for maintainability and scalability
- Comprehensive EDA notebook (25 production-quality cells)
- Data validation, cleaning, and missing value handling
- Feature engineering and feature selection
- Random Forest classification model
- Evaluation with standard classification metrics
- Standalone prediction pipeline
- Logging support and centralized configuration management
- Exportable reports
- Easy to extend and maintain

---

## Repository Structure

```text
Part2-Cybersecurity-ML-Pipeline/
│
├── data/                # Raw and processed datasets
├── notebooks/           # EDA and experimentation notebooks
├── outputs/             # Reports, plots, exported artifacts
├── src/                 # Modular pipeline source code
├── models/              # Saved/trained models
├── logs/                # Pipeline run logs
├── README.md
├── requirements.txt
├── LICENSE
├── CHANGELOG.md
└── run_pipeline.py      # Entry point to run the full pipeline
```

---

## Getting Started

```bash
# Clone the repository
git clone https://github.com/<your-username>/Part2-Cybersecurity-ML-Pipeline.git
cd Part2-Cybersecurity-ML-Pipeline

# Install dependencies
pip install -r requirements.txt

# Run the pipeline
python run_pipeline.py
```

---

## Project Metadata

| | |
|---|---|
| **Version** | 2.2 |
| **Project Type** | End-to-End Machine Learning Pipeline |
| **Domain** | Cybersecurity Analytics |
| **Model Type** | Classification (Severity Prediction) |
| **Status** | Production Ready 🚀 |

---

## License

See [LICENSE](LICENSE) for details.
Technology Stack

This project is built using modern Python libraries and machine learning tools.

Category| Technology
Programming Language| Python 3.10+
Data Processing| Pandas, NumPy
Data Visualization| Matplotlib
Machine Learning| Scikit-learn
Notebook Environment| Jupyter Notebook / Google Colab
Logging| Python Logging Module
Configuration| Python Configuration Module
Version Control| Git & GitHub

---

Project Architecture

The project follows a modular architecture where each component has a dedicated responsibility.

                 +----------------------+
                 |   Raw Cybersecurity  |
                 |       Dataset        |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 |    Data Loader       |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 |   Preprocessing      |
                 | Validation           |
                 | Missing Values       |
                 | Encoding             |
                 | Scaling              |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 |  Feature Selection   |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 |   Model Training     |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 | Model Evaluation     |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 | Prediction Pipeline  |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 | Saved Model & Output |
                 +----------------------+

---

Project Folder Structure

Part2-Cybersecurity-ML-Pipeline/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   └── EDA.ipynb
│
├── models/
│   └── random_forest_model.pkl
│
├── outputs/
│   ├── eda_summary.csv
│   ├── descriptive_statistics.csv
│   ├── feature_importance.csv
│   └── evaluation_report.csv
│
├── logs/
│   └── pipeline.log
│
├── src/
│   ├── config.py
│   ├── logger.py
│   ├── utils.py
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── feature_selection.py
│   ├── model_training.py
│   ├── model_evaluation.py
│   ├── predict.py
│   └── pipeline.py
│
├── run_pipeline.py
├── requirements.txt
├── LICENSE
├── CHANGELOG.md
├── .gitignore
└── README.md

---

Installation Guide

1. Clone the Repository

git clone https://github.com/pramodj551-oss/Part2-Cybersecurity-ML-Pipeline.git
cd Part2-Cybersecurity-ML-Pipeline

2. Create a Virtual Environment

python -m venv venv

Windows

venv\Scripts\activate

Linux / macOS

source venv/bin/activate

3. Install Required Packages

pip install -r requirements.txt

4. Run the Complete Pipeline

python run_pipeline.py

5. Launch the EDA Notebook

jupyter notebook notebooks/EDA.ipynb

---

Expected Outputs

After running the project successfully, the following artifacts will be generated:

- Trained Machine Learning Model
- Cleaned Dataset
- Feature Importance Report
- Model Evaluation Report
- Prediction Results
- EDA Summary Report
- Pipeline Log File

---

Reproducibility

This project is designed to be reproducible.

To reproduce the results:

1. Clone the repository.
2. Install all dependencies.
3. Place the dataset inside the "data/" directory.
4. Run "run_pipeline.py".
5. Execute "EDA.ipynb" if exploratory analysis is required.

Following these steps should generate the same outputs, provided the same dataset and library versions are used.
