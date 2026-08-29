import json
from pathlib import Path
import pandas as pd
import pytest
from src.model_lifecycle import compare_models, retraining_required

def test_retraining_required_on_feature_drift():
    required, reasons = retraining_required({'features_with_drift': 2, 'prediction_drift': {'drift_detected': False}})
    assert required is True and len(reasons) == 1

def test_retraining_not_required_without_drift():
    assert retraining_required({'features_with_drift': 0, 'prediction_drift': {'drift_detected': False}}) == (False, [])

def test_retraining_threshold_validation():
    with pytest.raises(ValueError): retraining_required({}, threshold=0)

def test_model_comparison_requires_cv_improvement():
    current={'model_name':'current','cv_mean':0.70}
    report=pd.DataFrame([{'Model':'candidate','CV Mean':0.75,'R2 Score':0.76,'RMSE':1.2,'MAE':0.9}])
    result=compare_models(current,'candidate',report)
    assert result['promotion_eligible'] is True
    assert result['cv_improvement'] == pytest.approx(0.05)
