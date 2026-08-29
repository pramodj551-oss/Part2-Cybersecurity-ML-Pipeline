"""Runtime entry point for STEP 21 monitoring."""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from src.config import CATEGORICAL_FEATURES, NUMERICAL_FEATURES, RAW_DATA_FILE, TARGET_COLUMN
from src.model_monitoring import build_monitoring_report, monitor_features, monitor_predictions, save_monitoring_outputs


def main() -> int:
    df = pd.read_csv(RAW_DATA_FILE)
    reference = df.iloc[: len(df) // 2].copy()
    current = df.iloc[len(df) // 2 :].copy()
    features = [c for c in NUMERICAL_FEATURES if c in df.columns]
    categorical = [c for c in CATEGORICAL_FEATURES if c in df.columns]
    results = monitor_features(reference, current, features, categorical)
    prediction_result = monitor_predictions(reference[TARGET_COLUMN], current[TARGET_COLUMN])
    report = build_monitoring_report(results, prediction_result, len(reference), len(current))
    save_monitoring_outputs(results, prediction_result, report)
    print("STEP 21 model monitoring completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
