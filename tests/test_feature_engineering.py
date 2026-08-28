"""Tests for STEP 17 feature engineering and ablation study."""

import pandas as pd


def _frame(rows=32):
    return pd.DataFrame({
        "incident_id": range(rows),
        "incident_date": pd.date_range("2025-01-01", periods=rows, freq="D"),
        "sector": ["Finance", "Healthcare"] * (rows // 2),
        "region": ["North", "South"] * (rows // 2),
        "attack_type": ["Phishing", "Malware"] * (rows // 2),
        "threat_actor": ["A", "B"] * (rows // 2),
        "records_affected": range(10, 10 + rows),
        "downtime_hours": [1.0] * rows,
        "ransom_demand_usd": range(1000, 1000 + rows),
        "detection_time_hours": [float(i % 8 + 1) for i in range(rows)],
        "severity_score": [float(i % 10 + 1) for i in range(rows)],
        "response_team_size": [5] * rows,
        "regulatory_fine_usd": [0.0] * rows,
        "resolved_within_7_days": [1] * rows,
        "data_exfiltration": [i % 2 for i in range(rows)],
        "zero_day_used": [(i + 1) % 2 for i in range(rows)],
    })


def test_step17_engineers_expected_features():
    from src.feature_engineering import FeatureEngineeringAblationStudy
    engineered = FeatureEngineeringAblationStudy().engineer_features(_frame())
    assert "incident_id" not in engineered
    assert "incident_month" in engineered
    assert "log_records_affected" in engineered
    assert "advanced_attack_indicator" in engineered


def test_step17_generates_required_outputs(tmp_path):
    from src.feature_engineering import FeatureEngineeringAblationStudy
    results = FeatureEngineeringAblationStudy().run(_frame(), tmp_path)
    assert not results.empty
    assert set(results.columns) == {"scenario", "feature_count", "r2_score", "rmse", "mae"}
    for name in ("engineered_features.csv", "ablation_results.csv", "feature_engineering_report.json"):
        assert (tmp_path / name).is_file()
