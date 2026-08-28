"""Smoke and regression-pipeline hardening tests."""

import numpy as np
import pandas as pd


def test_core_modules_import():
    from src.data_loader import DataLoader
    from src.feature_selection import FeatureSelector
    from src.model_evaluation import ModelEvaluator
    from src.model_training import ModelTrainer
    from src.predict import Predictor
    from src.preprocessing import Preprocessor
    assert all([DataLoader, FeatureSelector, ModelEvaluator, ModelTrainer, Predictor, Preprocessor])


def test_pipeline_config_imports():
    from src import config
    for name in (
        "RANDOM_STATE",
        "CV_FOLDS",
        "CV_SCORING",
        "FEATURE_SELECTION_TOP_N",
        "FEATURE_IMPORTANCE_FILE",
        "BEST_MODEL_FILE",
        "PREPROCESSOR_FILE",
    ):
        assert hasattr(config, name)


def test_feature_selection_preserves_original_indices():
    from src.feature_selection import FeatureSelector

    X = np.array([[1, 10, 5], [1, 20, 6], [1, 30, 7], [1, 40, 8]], dtype=float)
    selector = FeatureSelector(variance_threshold=0.1)
    selector.run(
        X=X,
        y=np.array([1.0, 2.0, 3.0, 4.0]),
        feature_names=["constant", "a", "b"],
        top_n=1,
    )
    assert selector.selected_feature_indices_[0] in (1, 2)


def _make_raw_training_frame(rows=25):
    rng = np.random.RandomState(7)
    frame = pd.DataFrame(
        {
            "records_affected": rng.randint(10, 1000, rows).astype(float),
            "detection_time_hours": rng.uniform(1, 48, rows),
            "ransom_demand_usd": rng.uniform(0, 100000, rows),
            "sector": rng.choice(["Finance", "Healthcare", "Technology"], rows),
            "region": rng.choice(["North", "South", "West"], rows),
            "attack_type": rng.choice(["Phishing", "Malware", "Ransomware"], rows),
            "threat_actor": rng.choice(["Actor A", "Actor B", "Actor C"], rows),
            "data_exfiltration": rng.choice([0, 1], rows),
            "zero_day_used": rng.choice([0, 1], rows),
        }
    )
    frame["severity_score"] = (
        0.02 * frame["records_affected"]
        + 0.4 * frame["detection_time_hours"]
        + 0.00002 * frame["ransom_demand_usd"]
        + frame["zero_day_used"] * 2
        + rng.normal(0, 0.2, rows)
    )
    return frame


def test_fold_safe_cv_fits_each_fold_independently():
    from src.model_training import ModelTrainer

    trainer = ModelTrainer()
    scores = trainer.fold_safe_cv_scores(_make_raw_training_frame(), top_n=3)

    assert trainer.cv_is_fold_safe is True
    assert set(scores) == set(trainer.list_models())
    assert all(len(model_scores) == 5 for model_scores in scores.values())
    assert all(np.isfinite(model_scores).all() for model_scores in scores.values())


def test_model_training_rejects_cv_without_raw_training_data():
    from src.model_training import ModelTrainer

    trainer = ModelTrainer()
    X_train = np.arange(40, dtype=float).reshape(20, 2)
    y_train = np.arange(20, dtype=float)
    X_test = np.arange(10, dtype=float).reshape(5, 2)
    y_test = np.arange(5, dtype=float)

    try:
        trainer.train_all_models(X_train, y_train, X_test, y_test)
    except ValueError as exc:
        assert "raw_train_df" in str(exc)
    else:
        raise AssertionError("Training must require raw_train_df for fold-safe CV.")


def test_feature_contract_excludes_post_incident_columns():
    from src.config import CATEGORICAL_FEATURES, NUMERICAL_FEATURES

    prediction_features = set(NUMERICAL_FEATURES + CATEGORICAL_FEATURES)
    forbidden = {
        "downtime_hours",
        "response_team_size",
        "regulatory_fine_usd",
        "resolved_within_7_days",
    }
    assert prediction_features.isdisjoint(forbidden)
