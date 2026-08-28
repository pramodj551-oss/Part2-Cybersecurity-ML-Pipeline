"""Tests for STEP 18 automated hyperparameter optimization."""

import pandas as pd


def _frame(rows=30):
    return pd.DataFrame({
        "records_affected": range(10, 10 + rows),
        "detection_time_hours": [float(i % 8 + 1) for i in range(rows)],
        "ransom_demand_usd": range(1000, 1000 + rows),
        "sector": ["Finance", "Healthcare"] * (rows // 2),
        "region": ["North", "South"] * (rows // 2),
        "attack_type": ["Phishing", "Malware"] * (rows // 2),
        "threat_actor": ["A", "B"] * (rows // 2),
        "data_exfiltration": [i % 2 for i in range(rows)],
        "zero_day_used": [(i + 1) % 2 for i in range(rows)],
        "severity_score": [float(i % 10 + 1) for i in range(rows)],
    })


def test_step18_search_space_contains_configured_models():
    from src.hyperparameter_optimization import HyperparameterOptimization
    spaces = HyperparameterOptimization()._search_spaces()
    assert set(spaces) == {"Random Forest", "Gradient Boosting"}
    assert spaces["Random Forest"][1]
    assert spaces["Gradient Boosting"][1]


def test_step18_generates_required_outputs(tmp_path):
    from src.hyperparameter_optimization import HyperparameterOptimization
    results = HyperparameterOptimization(cv_folds=3).run(_frame(), tmp_path)
    assert len(results) == 2
    assert list(results.columns) == ["model", "best_cv_r2", "best_params", "cv_folds", "n_iter"]
    assert (tmp_path / "hyperparameter_optimization.csv").is_file()
    assert (tmp_path / "hyperparameter_optimization_report.json").is_file()
    assert results["best_cv_r2"].notna().all()
