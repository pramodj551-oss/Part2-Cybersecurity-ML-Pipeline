"""STEP 19: probability calibration and decision-threshold optimization."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import f1_score, precision_score, recall_score, average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold

@dataclass(frozen=True)
class ThresholdResult:
    threshold: float
    precision: float
    recall: float
    f1: float


def calibrate_classifier(estimator, X_train, y_train, cv=5):
    """Fit a sigmoid-calibrated classifier without touching held-out test data."""
    calibrated = CalibratedClassifierCV(estimator=estimator, method="sigmoid", cv=cv)
    calibrated.fit(X_train, y_train)
    return calibrated


def optimize_threshold(y_true, probabilities, beta: float = 1.0, step: float = 0.01) -> ThresholdResult:
    """Select the threshold maximizing F-beta, with deterministic tie breaking."""
    if beta <= 0 or not 0 < step <= 1:
        raise ValueError("beta must be > 0 and step must be in (0, 1]")
    y_true = np.asarray(y_true)
    probabilities = np.asarray(probabilities, dtype=float)
    if len(y_true) != len(probabilities) or len(y_true) == 0:
        raise ValueError("y_true and probabilities must be non-empty and have equal length")
    if np.any((probabilities < 0) | (probabilities > 1)):
        raise ValueError("probabilities must be between 0 and 1")
    rows = []
    for threshold in np.arange(step, 1.0 + step / 2, step):
        pred = (probabilities >= threshold).astype(int)
        precision = precision_score(y_true, pred, zero_division=0)
        recall = recall_score(y_true, pred, zero_division=0)
        fbeta = (1 + beta**2) * precision * recall / (beta**2 * precision + recall) if precision + recall else 0.0
        rows.append((float(threshold), precision, recall, fbeta))
    best = max(rows, key=lambda r: (r[3], r[2], -r[0]))
    return ThresholdResult(best[0], best[1], best[2], f1_score(y_true, (probabilities >= best[0]).astype(int), zero_division=0))


def evaluate_probabilities(y_true, probabilities, threshold: float) -> dict:
    pred = (np.asarray(probabilities) >= threshold).astype(int)
    return {
        "threshold": float(threshold),
        "precision": float(precision_score(y_true, pred, zero_division=0)),
        "recall": float(recall_score(y_true, pred, zero_division=0)),
        "f1": float(f1_score(y_true, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
        "pr_auc": float(average_precision_score(y_true, probabilities)),
        "false_positives": int(((pred == 1) & (np.asarray(y_true) == 0)).sum()),
        "false_negatives": int(((pred == 0) & (np.asarray(y_true) == 1)).sum()),
    }
