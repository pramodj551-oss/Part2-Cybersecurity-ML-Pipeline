import json

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

import src.model_explainability as module
from src.model_explainability import ModelExplainability


def test_step20_generates_global_and_local_reports(tmp_path, monkeypatch):
    X = pd.DataFrame({"records_affected": [10, 20, 30, 40, 50, 60], "detection_time_hours": [1, 2, 3, 4, 5, 6]})
    y = pd.Series([2, 4, 6, 8, 10, 12], name="severity_score")
    preprocessor = ColumnTransformer([("num", StandardScaler(), ["records_affected", "detection_time_hours"])])
    Xt = preprocessor.fit_transform(X)
    model = RandomForestRegressor(n_estimators=20, random_state=42).fit(Xt, y)

    model_path = tmp_path / "best_model.pkl"
    preprocessor_path = tmp_path / "preprocessor.pkl"
    metadata_path = tmp_path / "model_metadata.json"
    test_path = tmp_path / "test_dataset.csv"
    joblib.dump(model, model_path)
    joblib.dump(preprocessor, preprocessor_path)
    metadata_path.write_text(json.dumps({"selected_feature_names": list(preprocessor.get_feature_names_out())}), encoding="utf-8")
    X.assign(severity_score=y).to_csv(test_path, index=False)

    monkeypatch.setattr(module, "BEST_MODEL_FILE", model_path)
    monkeypatch.setattr(module, "PREPROCESSOR_FILE", preprocessor_path)
    monkeypatch.setattr(module, "MODEL_METADATA_FILE", metadata_path)
    monkeypatch.setattr(module, "TEST_DATA_FILE", test_path)

    report = ModelExplainability(tmp_path / "outputs").run()

    assert report["step"] == 20
    assert report["model_explainability"]["feature_count"] == 2
    assert (tmp_path / "outputs" / "explainability_feature_importance.csv").exists()
    assert (tmp_path / "outputs" / "local_prediction_explanation.csv").exists()
    assert (tmp_path / "outputs" / "model_explainability_report.json").exists()


def test_select_columns_rejects_unknown_feature():
    matrix = np.zeros((2, 2))
    try:
        ModelExplainability._select_columns(matrix, ["a", "b"], ["missing"])
    except ValueError as exc:
        assert "missing" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unknown selected feature")
