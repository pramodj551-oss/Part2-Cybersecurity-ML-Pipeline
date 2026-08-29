"""Regression tests for STEP 22 model lifecycle decisions."""
import pandas as pd
import pytest

from src.model_lifecycle import compare_models, retraining_required


def test_retraining_required_when_feature_drift_detected():
    report = {
        "features_with_drift": 2,
        "prediction_drift": {"drift_detected": False},
    }
    required, reasons = retraining_required(report)
    assert required is True
    assert len(reasons) == 1


def test_retraining_required_when_prediction_drift_detected():
    report = {
        "features_with_drift": 0,
        "prediction_drift": {"drift_detected": True},
    }
    required, reasons = retraining_required(report)
    assert required is True
    assert "prediction drift" in reasons[0]


def test_no_retraining_when_no_drift():
    required, reasons = retraining_required(
        {"features_with_drift": 0, "prediction_drift": {"drift_detected": False}}
    )
    assert required is False
    assert reasons == []


def test_promotion_requires_strict_cv_improvement():
    current = {"model_name": "Linear Regression", "cv_mean": 0.40}
    candidate_report = pd.DataFrame(
        [
            {
                "Model": "Gradient Boosting",
                "CV Mean": 0.42,
                "CV Std": 0.03,
                "R2 Score": 0.43,
                "RMSE": 1.20,
                "MAE": 0.95,
            }
        ]
    )
    result = compare_models(current, "Gradient Boosting", candidate_report)
    assert result["promotion_eligible"] is True
    assert result["cv_improvement"] == pytest.approx(0.02)


def test_equal_cv_score_does_not_promote():
    current = {"model_name": "Linear Regression", "cv_mean": 0.40}
    candidate_report = pd.DataFrame(
        [
            {
                "Model": "Random Forest",
                "CV Mean": 0.40,
                "CV Std": 0.02,
                "R2 Score": 0.45,
                "RMSE": 1.18,
                "MAE": 0.94,
            }
        ]
    )
    result = compare_models(current, "Random Forest", candidate_report)
    assert result["promotion_eligible"] is False


def test_invalid_drift_threshold_rejected():
    with pytest.raises(ValueError):
        retraining_required(
            {"features_with_drift": 1, "prediction_drift": {"drift_detected": False}},
            threshold=0,
        )
