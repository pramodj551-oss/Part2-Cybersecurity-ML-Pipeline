"""
AI-Powered Cybersecurity ML Pipeline - Feature Selection
"""
from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import VarianceThreshold

from src.config import FEATURE_IMPORTANCE_FILE, RANDOM_STATE
from src.logger import logger, log_section, log_success


class FeatureSelector:
    """Feature selection pipeline."""

    def __init__(self, variance_threshold: float = 0.01) -> None:
        self.variance_selector = VarianceThreshold(threshold=variance_threshold)
        self.random_forest = RandomForestRegressor(
            n_estimators=200,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )
        self.selected_features_: List[str] = []
        self.selected_feature_indices_: List[int] = []
        self.feature_importance_: pd.DataFrame | None = None

    def remove_low_variance_features(
        self,
        X: np.ndarray,
        feature_names: List[str],
    ) -> tuple[np.ndarray, List[str]]:
        log_section("Variance Threshold Feature Selection")
        X_selected = self.variance_selector.fit_transform(X)
        mask = self.variance_selector.get_support()
        selected_names = [name for name, keep in zip(feature_names, mask) if keep]
        self.selected_features_ = selected_names
        logger.info("Original Features : %d", len(feature_names))
        logger.info("Selected Features : %d", len(selected_names))
        logger.info("Removed Features : %d", len(feature_names) - len(selected_names))
        log_success("Low variance feature removal completed.")
        return X_selected, selected_names

    @staticmethod
    def validate_feature_names(feature_names: List[str], X: np.ndarray) -> None:
        if len(feature_names) != X.shape[1]:
            raise ValueError("Feature name count does not match transformed feature matrix.")
        logger.info("Feature names validated successfully.")

    def calculate_feature_importance(
        self,
        X: np.ndarray,
        y: pd.Series,
        feature_names: List[str],
    ) -> pd.DataFrame:
        log_section("Calculating Feature Importance")
        self.validate_feature_names(feature_names, X)
        self.random_forest.fit(X, y)
        importance_df = pd.DataFrame({
            "feature": feature_names,
            "importance": self.random_forest.feature_importances_,
        }).sort_values("importance", ascending=False).reset_index(drop=True)
        self.feature_importance_ = importance_df
        logger.info("Feature importance calculated for %d features.", len(importance_df))
        log_success("Feature importance calculation completed.")
        return importance_df

    def rank_features(self) -> pd.DataFrame:
        log_section("Ranking Features")
        if self.feature_importance_ is None:
            raise ValueError("Feature importance has not been calculated.")
        ranked = self.feature_importance_.copy()
        ranked["rank"] = ranked["importance"].rank(method="dense", ascending=False).astype(int)
        return ranked[["rank", "feature", "importance"]]

    def select_top_features(self, top_n: int = 20) -> list[str]:
        log_section("Selecting Top Features")
        if self.feature_importance_ is None:
            raise ValueError("Feature importance has not been calculated.")
        self.selected_features_ = self.feature_importance_.head(top_n)["feature"].tolist()
        return self.selected_features_

    def export_feature_importance(self) -> None:
        log_section("Exporting Feature Importance")
        if self.feature_importance_ is None:
            raise ValueError("Feature importance has not been calculated.")
        self.feature_importance_.to_csv(FEATURE_IMPORTANCE_FILE, index=False)
        log_success("Feature importance report exported.")

    def feature_summary(self) -> None:
        log_section("Feature Selection Summary")
        if self.feature_importance_ is None:
            logger.warning("Feature importance is unavailable.")
            return
        logger.info("Total Features : %d", len(self.feature_importance_))
        logger.info("Selected Features : %d", len(self.selected_features_))

    def run(
        self,
        X=None,
        y=None,
        feature_names: list[str] | None = None,
        top_n: int = 20,
        *,
        X_train=None,
        y_train=None,
    ):
        """Run feature selection with backward-compatible train aliases."""
        if X is None:
            X = X_train
        if y is None:
            y = y_train
        if X is None or y is None or feature_names is None:
            raise ValueError("X/X_train, y/y_train and feature_names are required.")

        log_section("Starting Feature Selection Pipeline")
        self.validate_feature_names(feature_names, X)
        X_filtered, filtered_names = self.remove_low_variance_features(X, feature_names)
        importance_df = self.calculate_feature_importance(X_filtered, y, filtered_names)
        self.rank_features()
        selected_features = self.select_top_features(top_n)
        self.export_feature_importance()
        self.feature_summary()
        selected_indices = [filtered_names.index(name) for name in selected_features]
        self.selected_feature_indices_ = selected_indices
        X_selected = X_filtered[:, selected_indices]
        log_success("Feature selection pipeline completed successfully.")
        return X_selected, selected_features, importance_df


if __name__ == "__main__":
    from src.data_loader import DataLoader
    from src.preprocessing import Preprocessor

    dataframe = DataLoader().run()
    X_train, X_test, y_train, y_test, fitted_preprocessor = Preprocessor().run(dataframe)
    feature_names = list(fitted_preprocessor.get_feature_names_out())
    X_selected, selected_features, importance_report = FeatureSelector().run(
        X_train, y_train, feature_names, top_n=20
    )
    logger.info("Selected Feature Matrix Shape : %s", X_selected.shape)
    logger.info("Selected Feature Count : %d", len(selected_features))
    log_success("Feature selection completed successfully.")
