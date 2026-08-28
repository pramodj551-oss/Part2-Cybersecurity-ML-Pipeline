"""Configuration for the cybersecurity severity-score regression pipeline."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODEL_DIR = PROJECT_ROOT / "models"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
NOTEBOOK_DIR = PROJECT_ROOT / "notebooks"
TEST_DIR = PROJECT_ROOT / "tests"

RAW_DATA_FILE = RAW_DATA_DIR / "cybersecurity_incident_reports.csv"
PROCESSED_DATA_FILE = PROCESSED_DATA_DIR / "processed_incidents.csv"
TRAIN_DATA_FILE = PROCESSED_DATA_DIR / "train_dataset.csv"
TEST_DATA_FILE = PROCESSED_DATA_DIR / "test_dataset.csv"

MODEL_FILE = MODEL_DIR / "best_model.pkl"
BEST_MODEL_FILE = MODEL_FILE
PREPROCESSOR_FILE = MODEL_DIR / "preprocessor.pkl"
FEATURE_COLUMNS_FILE = MODEL_DIR / "feature_columns.pkl"
MODEL_METADATA_FILE = MODEL_DIR / "model_metadata.json"

METRICS_FILE = OUTPUT_DIR / "metrics.json"
FEATURE_IMPORTANCE_FILE = OUTPUT_DIR / "feature_importance.csv"
TRAINING_LOG_FILE = OUTPUT_DIR / "training.log"
EVALUATION_REPORT_FILE = OUTPUT_DIR / "evaluation_report.json"
EVALUATION_SUMMARY_FILE = OUTPUT_DIR / "evaluation_summary.json"
PREDICTION_RESULTS_FILE = OUTPUT_DIR / "prediction_results.csv"
RESIDUAL_REPORT_FILE = OUTPUT_DIR / "residual_report.csv"
PREDICTION_OUTPUT_FILE = OUTPUT_DIR / "predictions.csv"
PREDICTION_SUMMARY_FILE = OUTPUT_DIR / "prediction_summary.json"

PREDICTION_COLUMN = "predicted_severity_score"
TARGET_COLUMN = "severity_score"
ID_COLUMN = "incident_id"
DATE_COLUMN = "incident_date"

NUMERICAL_FEATURES = [
    "records_affected", "detection_time_hours", "ransom_demand_usd",
]
CATEGORICAL_FEATURES = [
    "sector", "region", "attack_type", "threat_actor",
    "data_exfiltration", "zero_day_used",
]

# Excluded from prediction because they can be known only after incident response:
# downtime_hours, response_team_size, regulatory_fine_usd, resolved_within_7_days.
# These fields are retained in the raw dataset for historical analysis only.

TEST_SIZE = 0.20
RANDOM_STATE = 42
CV_FOLDS = 5
N_ESTIMATORS = 200
MAX_DEPTH = 10
MIN_SAMPLES_SPLIT = 5
MIN_SAMPLES_LEAF = 2

for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODEL_DIR, OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
