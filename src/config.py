"""
==========================================================
AI-Powered Cybersecurity ML Pipeline
Part 2 - Configuration File
Author : Pramod Prakash Jadhav
Python : 3.11+
==========================================================
"""

from pathlib import Path

# ==========================================================
# PROJECT ROOT
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ==========================================================
# DIRECTORIES
# ==========================================================

DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"

PROCESSED_DATA_DIR = DATA_DIR / "processed"

MODEL_DIR = PROJECT_ROOT / "models"

OUTPUT_DIR = PROJECT_ROOT / "outputs"

NOTEBOOK_DIR = PROJECT_ROOT / "notebooks"

TEST_DIR = PROJECT_ROOT / "tests"

# ==========================================================
# DATA FILES
# ==========================================================

RAW_DATA_FILE = RAW_DATA_DIR / "cybersecurity_incident_reports.csv"

PROCESSED_DATA_FILE = (
    PROCESSED_DATA_DIR / "processed_incidents.csv"
)

TRAIN_DATA_FILE = (
    PROCESSED_DATA_DIR / "train_dataset.csv"
)

TEST_DATA_FILE = (
    PROCESSED_DATA_DIR / "test_dataset.csv"
)

# ==========================================================
# MODEL FILES
# ==========================================================

MODEL_FILE = MODEL_DIR / "best_model.pkl"

SCALER_FILE = MODEL_DIR / "scaler.pkl"

ENCODER_FILE = MODEL_DIR / "label_encoder.pkl"

FEATURE_COLUMNS_FILE = (
    MODEL_DIR / "feature_columns.pkl"
)

# ==========================================================
# OUTPUT FILES
# ==========================================================

METRICS_FILE = OUTPUT_DIR / "metrics.json"

FEATURE_IMPORTANCE_FILE = (
    OUTPUT_DIR / "feature_importance.csv"
)

CLASSIFICATION_REPORT_FILE = (
    OUTPUT_DIR / "classification_report.txt"
)

CONFUSION_MATRIX_FILE = (
    OUTPUT_DIR / "confusion_matrix.png"
)

ROC_CURVE_FILE = (
    OUTPUT_DIR / "roc_curve.png"
)

TRAINING_LOG_FILE = (
    OUTPUT_DIR / "training.log"
)

# ==========================================================
# DATASET CONFIGURATION
# ==========================================================

TARGET_COLUMN = "severity_score"

ID_COLUMN = "incident_id"

DATE_COLUMN = "incident_date"

# ==========================================================
# FEATURE COLUMNS
# ==========================================================

NUMERICAL_FEATURES = [

    "records_affected",

    "downtime_hours",

    "ransom_demand_usd",

    "detection_time_hours",

    "response_team_size",

    "regulatory_fine_usd"

]

CATEGORICAL_FEATURES = [

    "sector",

    "region",

    "attack_type",

    "threat_actor",

    "resolved_within_7_days",

    "data_exfiltration",

    "zero_day_used"

]

# ==========================================================
# TRAINING CONFIGURATION
# ==========================================================

TEST_SIZE = 0.20

RANDOM_STATE = 42

CV_FOLDS = 5

# ==========================================================
# RANDOM FOREST DEFAULT PARAMETERS
# ==========================================================

N_ESTIMATORS = 200

MAX_DEPTH = 10

MIN_SAMPLES_SPLIT = 5

MIN_SAMPLES_LEAF = 2

# ==========================================================
# CREATE REQUIRED DIRECTORIES
# ==========================================================

for directory in [

    RAW_DATA_DIR,

    PROCESSED_DATA_DIR,

    MODEL_DIR,

    OUTPUT_DIR

]:
    directory.mkdir(
        parents=True,
        exist_ok=True
)
