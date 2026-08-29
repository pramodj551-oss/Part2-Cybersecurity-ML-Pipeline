"""Tests for STEP 21 model monitoring and drift detection."""
import json

import numpy as np
import pandas as pd
import pytest

from src.model_monitoring import (
    categorical_drift,
    monitor_features,
    monitor_predictions,
    population_stability_index,
    save_monitoring_outputs,
)


def test_identical_numeric_samples_have_zero_psi():
    s = pd.Series([1, 2, 3, 4, 5] * 10)
    assert population_stability_index(s, s.copy()) == pytest.approx(0.0)


def test_shifted_numeric_samples_have_positive_psi():
    reference = pd.Series(np.arange(100, dtype=float))
    current = pd.Series(np.arange(100, dtype=float) + 50)
    assert population_stability_index(reference, current) > 0


def test_identical_categorical_samples_have_zero_tv_distance():
    reference = pd.Series(["a", "b", "a", "c"] * 20)
    assert categorical_drift(reference, reference.copy()) == pytest.approx(0.0)


def test_monitor_features_flags_large_numeric_drift():
    reference = pd.DataFrame({"x": np.arange(100, dtype=float), "category": ["a"] * 50 + ["b"] * 50})
    current = pd.DataFrame({"x": np.arange(100, dtype=float) + 1000, "category": ["b"] * 100})
    result = monitor_features(reference, current, ["x"], ["category"], threshold=0.20)
    assert set(result.columns) >= {"feature", "drift_score", "drift_detected"}
    assert result["drift_detected"].any()


def test_prediction_monitoring_schema():
    reference = pd.Series(np.linspace(0, 10, 100))
    current = pd.Series(np.linspace(0, 10, 100))
    result = monitor_predictions(reference, current)
    assert not result["drift_detected"]
    assert result["psi"] == pytest.approx(0.0)


def test_invalid_threshold_rejected():
    with pytest.raises(ValueError):
        monitor_features(
            pd.DataFrame({"x": [1, 2]}),
            pd.DataFrame({"x": [1, 2]}),
            ["x"],
            [],
            threshold=0,
        )


def test_outputs_are_json_serializable(tmp_path, monkeypatch):
    monkeypatch.setattr("src.model_monitoring.OUTPUT_DIR", tmp_path)
    results = pd.DataFrame([
        {
            "feature": "x",
            "feature_type": "numeric",
            "drift_score": 0.0,
            "threshold": 0.2,
            "drift_detected": False,
        }
    ])
    prediction = {
        "psi": 0.0,
        "threshold": 0.2,
        "drift_detected": False,
        "reference_mean": 1.0,
        "current_mean": 1.0,
    }
    report = {
        "step": 21,
        "reference_rows": 2,
        "current_rows": 2,
        "features_monitored": 1,
        "features_with_drift": 0,
        "prediction_drift": prediction,
        "overall_drift_detected": False,
    }
    save_monitoring_outputs(results, prediction, report)
    assert (tmp_path / "drift_results.csv").exists()
    assert json.loads((tmp_path / "drift_report.json").read_text())['step'] == 21
