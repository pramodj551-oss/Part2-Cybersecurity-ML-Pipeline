import numpy as np
import pytest
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from src.model_calibration import calibrate_classifier, optimize_threshold, evaluate_probabilities


def test_optimize_threshold_returns_valid_result():
    y = np.array([0, 0, 1, 1, 1, 0])
    p = np.array([.1, .2, .55, .7, .9, .4])
    result = optimize_threshold(y, p)
    assert 0 < result.threshold <= 1
    assert 0 <= result.precision <= 1
    assert 0 <= result.recall <= 1


def test_invalid_inputs_are_rejected():
    with pytest.raises(ValueError):
        optimize_threshold([0, 1], [0.2], step=.1)
    with pytest.raises(ValueError):
        optimize_threshold([0, 1], [0.2, 1.2])


def test_calibration_produces_probabilities():
    X, y = make_classification(n_samples=80, n_features=5, random_state=42)
    model = calibrate_classifier(LogisticRegression(max_iter=500), X, y, cv=3)
    probabilities = model.predict_proba(X)[:, 1]
    assert probabilities.shape == (80,)
    assert np.all((probabilities >= 0) & (probabilities <= 1))


def test_evaluation_contains_security_metrics():
    metrics = evaluate_probabilities([0, 1, 1, 0], [.1, .8, .7, .2], .5)
    assert metrics["false_positives"] == 0
    assert metrics["false_negatives"] == 0
    assert metrics["pr_auc"] >= 0
