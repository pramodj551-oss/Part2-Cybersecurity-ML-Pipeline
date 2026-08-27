"""Smoke and regression-pipeline hardening tests."""


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
    for name in ("RANDOM_STATE", "FEATURE_IMPORTANCE_FILE", "BEST_MODEL_FILE", "PREPROCESSOR_FILE"):
        assert hasattr(config, name)


def test_feature_selection_preserves_original_indices():
    import numpy as np
    from src.feature_selection import FeatureSelector
    X = np.array([[1, 10, 5], [1, 20, 6], [1, 30, 7], [1, 40, 8]], dtype=float)
    selector = FeatureSelector(variance_threshold=0.1)
    selector.run(X=X, y=np.array([1., 2., 3., 4.]), feature_names=["constant", "a", "b"], top_n=1)
    assert selector.selected_feature_indices_[0] in (1, 2)


def test_model_training_cross_validation_uses_train_data(monkeypatch):
    import numpy as np
    import src.model_training as mt
    seen = {}
    def fake_cv(model, X, y, **kwargs):
        seen["X"] = X; seen["y"] = y
        return np.array([0.5, 0.6, 0.7, 0.6, 0.5])
    monkeypatch.setattr(mt, "cross_val_score", fake_cv)
    trainer = mt.ModelTrainer()
    X_train = np.arange(20, dtype=float).reshape(10, 2); y_train = np.arange(10, dtype=float)
    X_test = np.arange(8, dtype=float).reshape(4, 2); y_test = np.arange(4, dtype=float)
    trainer.evaluate_model("Linear Regression", trainer.get_model("Linear Regression"), X_train, y_train, X_test, y_test)
    assert seen["X"] is X_train and seen["y"] is y_train
