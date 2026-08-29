"""STEP 21: deterministic data and prediction drift monitoring utilities."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import OUTPUT_DIR, RANDOM_STATE


DEFAULT_THRESHOLD = 0.20


def _validate_columns(reference: pd.DataFrame, current: pd.DataFrame, columns: list[str]) -> None:
    missing = [c for c in columns if c not in reference.columns or c not in current.columns]
    if missing:
        raise ValueError(f"Missing monitoring columns: {missing}")


def population_stability_index(reference: pd.Series, current: pd.Series, bins: int = 10) -> float:
    """Compute PSI for numeric data using reference quantile bins."""
    ref = pd.to_numeric(reference, errors="coerce").dropna().to_numpy(dtype=float)
    cur = pd.to_numeric(current, errors="coerce").dropna().to_numpy(dtype=float)
    if ref.size == 0 or cur.size == 0:
        raise ValueError("PSI requires non-empty numeric samples.")
    if np.allclose(ref, ref[0]) and np.allclose(cur, cur[0]):
        return 0.0 if np.isclose(ref[0], cur[0]) else float("inf")

    quantiles = np.linspace(0.0, 1.0, bins + 1)
    edges = np.unique(np.quantile(ref, quantiles))
    if edges.size < 2:
        edges = np.array([ref.min() - 1e-9, ref.max() + 1e-9])
    else:
        edges[0] = -np.inf
        edges[-1] = np.inf

    ref_counts, _ = np.histogram(ref, bins=edges)
    cur_counts, _ = np.histogram(cur, bins=edges)
    eps = 1e-6
    ref_pct = np.maximum(ref_counts / ref.size, eps)
    cur_pct = np.maximum(cur_counts / cur.size, eps)
    return float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)))


def categorical_drift(reference: pd.Series, current: pd.Series) -> float:
    """Return total variation distance between categorical distributions."""
    ref_pct = reference.astype(str).value_counts(normalize=True)
    cur_pct = current.astype(str).value_counts(normalize=True)
    categories = ref_pct.index.union(cur_pct.index)
    return float(0.5 * np.abs(ref_pct.reindex(categories, fill_value=0) - cur_pct.reindex(categories, fill_value=0)).sum())


def monitor_features(
    reference: pd.DataFrame,
    current: pd.DataFrame,
    numeric_columns: list[str],
    categorical_columns: list[str],
    threshold: float = DEFAULT_THRESHOLD,
) -> pd.DataFrame:
    """Build per-feature drift results without mutating input frames."""
    if not 0 < threshold <= 1:
        raise ValueError("threshold must be in (0, 1].")
    _validate_columns(reference, current, numeric_columns + categorical_columns)
    rows: list[dict[str, object]] = []
    for column in numeric_columns:
        score = population_stability_index(reference[column], current[column])
        rows.append({
            "feature": column,
            "feature_type": "numeric",
            "drift_score": score,
            "threshold": threshold,
            "drift_detected": bool(score >= threshold),
        })
    for column in categorical_columns:
        score = categorical_drift(reference[column], current[column])
        rows.append({
            "feature": column,
            "feature_type": "categorical",
            "drift_score": score,
            "threshold": threshold,
            "drift_detected": bool(score >= threshold),
        })
    return pd.DataFrame(rows).sort_values("drift_score", ascending=False).reset_index(drop=True)


def monitor_predictions(
    reference: pd.Series,
    current: pd.Series,
    threshold: float = DEFAULT_THRESHOLD,
) -> dict[str, float | bool]:
    """Monitor numeric prediction drift using PSI."""
    score = population_stability_index(reference, current)
    return {
        "psi": score,
        "threshold": threshold,
        "drift_detected": bool(score >= threshold),
        "reference_mean": float(pd.to_numeric(reference).mean()),
        "current_mean": float(pd.to_numeric(current).mean()),
    }


def build_monitoring_report(feature_results: pd.DataFrame, prediction_result: dict[str, object], reference_rows: int, current_rows: int) -> dict[str, object]:
    """Create a JSON-serializable monitoring summary."""
    feature_drift_count = int(feature_results["drift_detected"].sum()) if not feature_results.empty else 0
    return {
        "step": 21,
        "random_state": RANDOM_STATE,
        "reference_rows": reference_rows,
        "current_rows": current_rows,
        "features_monitored": int(len(feature_results)),
        "features_with_drift": feature_drift_count,
        "prediction_drift": prediction_result,
        "overall_drift_detected": bool(feature_drift_count > 0 or prediction_result["drift_detected"]),
    }


def save_monitoring_outputs(feature_results: pd.DataFrame, prediction_result: dict[str, object], report: dict[str, object]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    feature_results.to_csv(OUTPUT_DIR / "drift_results.csv", index=False)
    (OUTPUT_DIR / "prediction_drift.json").write_text(json.dumps(prediction_result, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "drift_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary = {
        "overall_drift_detected": report["overall_drift_detected"],
        "features_with_drift": report["features_with_drift"],
        "features_monitored": report["features_monitored"],
        "prediction_drift_detected": prediction_result["drift_detected"],
    }
    (OUTPUT_DIR / "drift_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
