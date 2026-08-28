"""Generate STEP 19 audit outputs from a deterministic synthetic evaluation split."""
from pathlib import Path
import json
import sys

# Keep direct script execution compatible with GitHub Actions and local shells.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from src.model_calibration import calibrate_classifier, optimize_threshold, evaluate_probabilities

OUT = PROJECT_ROOT / "outputs"
OUT.mkdir(exist_ok=True)
X, y = make_classification(n_samples=400, n_features=10, n_informative=6, weights=[0.65, 0.35], random_state=42)
X_train, X_eval, y_train, y_eval = train_test_split(X, y, test_size=.25, stratify=y, random_state=42)
model = calibrate_classifier(LogisticRegression(max_iter=1000, random_state=42), X_train, y_train, cv=5)
prob = model.predict_proba(X_eval)[:, 1]
result = optimize_threshold(y_eval, prob, beta=1.0, step=.01)
metrics = evaluate_probabilities(y_eval, prob, result.threshold)

rows = []
for threshold in np.arange(.01, 1.001, .01):
    rows.append(evaluate_probabilities(y_eval, prob, float(threshold)))
pd.DataFrame(rows).to_csv(OUT / "threshold_optimization.csv", index=False)
pd.DataFrame([metrics]).to_csv(OUT / "calibration_results.csv", index=False)
report = {"step": 19, "method": "sigmoid", "cv": 5, "optimal_threshold": result.threshold, "metrics": metrics}
(OUT / "calibration_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
