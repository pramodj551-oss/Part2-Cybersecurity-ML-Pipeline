"""Minimal smoke tests for the Part 2 cybersecurity ML pipeline."""


def test_core_modules_import():
    from src.data_loader import DataLoader
    from src.feature_selection import FeatureSelector
    from src.model_evaluation import ModelEvaluator
    from src.model_training import ModelTrainer
    from src.predict import Predictor
    from src.preprocessing import Preprocessor

    assert DataLoader is not None
    assert FeatureSelector is not None
    assert ModelEvaluator is not None
    assert ModelTrainer is not None
    assert Predictor is not None
    assert Preprocessor is not None


def test_pipeline_config_imports():
    from src import config

    required = (
        "RANDOM_STATE",
        "FEATURE_IMPORTANCE_FILE",
        "BEST_MODEL_FILE",
        "PREPROCESSOR_FILE",
    )
    for name in required:
        assert hasattr(config, name), f"Missing config setting: {name}"


def test_logger_import():
    from src.logger import logger

    assert logger is not None
