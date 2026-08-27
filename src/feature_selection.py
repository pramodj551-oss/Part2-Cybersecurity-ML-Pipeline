"""Feature selection for the cybersecurity regression pipeline."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import VarianceThreshold

from src.config import FEATURE_IMPORTANCE_FILE, RANDOM_STATE
from src.logger import logger, log_section, log_success


class FeatureSelector:
    def __init__(self, variance_threshold: float = 0.01) -> None:
        self.variance_selector = VarianceThreshold(threshold=variance_threshold)
        self.random_forest = RandomForestRegressor(n_estimators=200, random_state=RANDOM_STATE, n_jobs=-1)
        self.selected_features_: list[str] = []
        self.selected_feature_indices_: list[int] = []
        self.feature_importance_: pd.DataFrame | None = None
        self._variance_selected_indices: list[int] = []

    @staticmethod
    def validate_feature_names(feature_names: list[str], X: np.ndarray) -> None:
        if len(feature_names) != X.shape[1]:
            raise ValueError("Feature name count does not match transformed feature matrix.")

    def remove_low_variance_features(self, X: np.ndarray, feature_names: list[str]):
        X_selected = self.variance_selector.fit_transform(X)
        mask = self.variance_selector.get_support()
        self._variance_selected_indices = np.flatnonzero(mask).tolist()
        names = [n for n, keep in zip(feature_names, mask) if keep]
        return X_selected, names

    def calculate_feature_importance(self, X, y, feature_names):
        self.validate_feature_names(feature_names, X)
        self.random_forest.fit(X, y)
        self.feature_importance_ = pd.DataFrame({"feature": feature_names, "importance": self.random_forest.feature_importances_}).sort_values("importance", ascending=False).reset_index(drop=True)
        return self.feature_importance_

    def rank_features(self):
        if self.feature_importance_ is None:
            raise ValueError("Feature importance has not been calculated.")
        ranked = self.feature_importance_.copy()
        ranked["rank"] = ranked["importance"].rank(method="dense", ascending=False).astype(int)
        return ranked[["rank", "feature", "importance"]]

    def select_top_features(self, top_n: int = 20):
        if top_n < 1:
            raise ValueError("top_n must be at least 1.")
        if self.feature_importance_ is None:
            raise ValueError("Feature importance has not been calculated.")
        self.selected_features_ = self.feature_importance_.head(top_n)["feature"].tolist()
        return self.selected_features_

    def export_feature_importance(self):
        if self.feature_importance_ is None:
            raise ValueError("Feature importance has not been calculated.")
        self.feature_importance_.to_csv(FEATURE_IMPORTANCE_FILE, index=False)

    def feature_summary(self):
        if self.feature_importance_ is not None:
            logger.info("Total Features : %d | Selected Features : %d", len(self.feature_importance_), len(self.selected_features_))

    def run(self, X=None, y=None, feature_names=None, top_n: int = 20, *, X_train=None, y_train=None):
        X = X if X is not None else X_train
        y = y if y is not None else y_train
        if X is None or y is None or feature_names is None:
            raise ValueError("X/X_train, y/y_train and feature_names are required.")
        self.validate_feature_names(feature_names, X)
        X_filtered, filtered_names = self.remove_low_variance_features(X, feature_names)
        importance = self.calculate_feature_importance(X_filtered, y, filtered_names)
        self.rank_features()
        selected_features = self.select_top_features(top_n)
        self.export_feature_importance()
        self.feature_summary()
        filtered_indices = [filtered_names.index(name) for name in selected_features]
        self.selected_feature_indices_ = [self._variance_selected_indices[i] for i in filtered_indices]
        X_selected = X[:, self.selected_feature_indices_]
        return X_selected, selected_features, importance
