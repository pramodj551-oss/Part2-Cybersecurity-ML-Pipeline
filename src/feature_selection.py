"""
==========================================================
AI-Powered Cybersecurity ML Pipeline
Part 2 - Feature Selection

Author : Pramod Prakash Jadhav
Python : 3.11+
==========================================================
"""

from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd

from sklearn.feature_selection import VarianceThreshold
from sklearn.ensemble import RandomForestRegressor

from src.config import RANDOM_STATE
from src.logger import (
    logger,
    log_section,
    log_success,
)


class FeatureSelector:
    """
    Feature selection pipeline for the
    Cybersecurity ML project.

    Responsibilities
    ----------------
    - Low variance feature removal
    - Feature importance estimation
    - Feature ranking
    - Top feature selection
    - Export reports
    """

    def __init__(
        self,
        variance_threshold: float = 0.01,
    ) -> None:

        self.variance_selector = VarianceThreshold(
            threshold=variance_threshold
        )

        self.random_forest = RandomForestRegressor(
            n_estimators=200,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )

        self.selected_features_: List[str] = []

        self.feature_importance_: pd.DataFrame | None = None

    # ======================================================
    # VARIANCE THRESHOLD
    # ======================================================

    def remove_low_variance_features(
        self,
        X: np.ndarray,
        feature_names: List[str],
    ) -> tuple[np.ndarray, List[str]]:
        """
        Remove features with very low variance.

        Parameters
        ----------
        X : np.ndarray
            Input feature matrix.

        feature_names : List[str]
            Names of transformed features.

        Returns
        -------
        tuple
            Filtered feature matrix and feature names.
        """

        log_section(
            "Variance Threshold Feature Selection"
        )

        X_selected = (
            self.variance_selector.fit_transform(X)
        )

        mask = (
            self.variance_selector.get_support()
        )

        selected_names = [

            name

            for name, keep in zip(
                feature_names,
                mask,
            )

            if keep

        ]

        removed = (
            len(feature_names)
            - len(selected_names)
        )

        logger.info(
            "Original Features : %d",
            len(feature_names),
        )

        logger.info(
            "Selected Features : %d",
            len(selected_names),
        )

        logger.info(
            "Removed Features : %d",
            removed,
        )

        self.selected_features_ = selected_names

        log_success(
            "Low variance feature removal completed."
        )

        return (
            X_selected,
            selected_names,
        )

    # ======================================================
    # FEATURE NAME VALIDATION
    # ======================================================

    @staticmethod
    def validate_feature_names(
        feature_names: List[str],
        X: np.ndarray,
    ) -> None:
        """
        Validate feature name count.
        """

        if len(feature_names) != X.shape[1]:

            raise ValueError(

                "Feature name count does not "
                "match transformed feature matrix."

            )

        logger.info(
            "Feature names validated successfully."
    )
      # ======================================================
    # RANDOM FOREST FEATURE IMPORTANCE
    # ======================================================

    def calculate_feature_importance(
        self,
        X: np.ndarray,
        y: pd.Series,
        feature_names: List[str],
    ) -> pd.DataFrame:
        """
        Train a Random Forest model and compute
        feature importance scores.

        Parameters
        ----------
        X : np.ndarray
            Feature matrix.

        y : pd.Series
            Target variable.

        feature_names : List[str]
            Feature names.

        Returns
        -------
        pd.DataFrame
            Feature importance table.
        """

        log_section(
            "Calculating Feature Importance"
        )

        self.validate_feature_names(
            feature_names,
            X,
        )

        self.random_forest.fit(X, y)

        importance_df = pd.DataFrame(
            {
                "feature": feature_names,
                "importance": (
                    self.random_forest.feature_importances_
                ),
            }
        )

        importance_df = (
            importance_df
            .sort_values(
                by="importance",
                ascending=False,
            )
            .reset_index(drop=True)
        )

        self.feature_importance_ = importance_df

        logger.info(
            "Feature importance calculated for %d features.",
            len(importance_df),
        )

        log_success(
            "Feature importance calculation completed."
        )

        return importance_df

    # ======================================================
    # FEATURE RANKING
    # ======================================================

    def rank_features(
        self,
    ) -> pd.DataFrame:
        """
        Rank features based on importance score.
        """

        log_section(
            "Ranking Features"
        )

        if self.feature_importance_ is None:

            raise ValueError(
                "Feature importance has not been calculated."
            )

        ranked = (
            self.feature_importance_
            .copy()
        )

        ranked["rank"] = (
            ranked["importance"]
            .rank(
                method="dense",
                ascending=False,
            )
            .astype(int)
        )

        ranked = ranked[
            [
                "rank",
                "feature",
                "importance",
            ]
        ]

        logger.info(
            "Top Feature : %s",
            ranked.iloc[0]["feature"],
        )

        logger.info(
            "Top Importance Score : %.6f",
            ranked.iloc[0]["importance"],
        )

        log_success(
            "Feature ranking completed."
        )

        return ranked
      from src.config import (
    FEATURE_IMPORTANCE_FILE,
)

# ======================================================
# SELECT TOP FEATURES
# ======================================================

def select_top_features(
    self,
    top_n: int = 20,
) -> list[str]:
    """
    Select the top N most important features.

    Parameters
    ----------
    top_n : int
        Number of top features to select.

    Returns
    -------
    List[str]
        Selected feature names.
    """

    log_section("Selecting Top Features")

    if self.feature_importance_ is None:

        raise ValueError(
            "Feature importance has not been calculated."
        )

    selected = (
        self.feature_importance_
        .head(top_n)
        .copy()
    )

    self.selected_features_ = (
        selected["feature"].tolist()
    )

    logger.info(
        "Top %d features selected.",
        len(self.selected_features_),
    )

    log_success(
        "Top feature selection completed."
    )

    return self.selected_features_


# ======================================================
# EXPORT FEATURE IMPORTANCE
# ======================================================

def export_feature_importance(
    self,
) -> None:
    """
    Export feature importance report as CSV.
    """

    log_section(
        "Exporting Feature Importance"
    )

    if self.feature_importance_ is None:

        raise ValueError(
            "Feature importance has not been calculated."
        )

    self.feature_importance_.to_csv(
        FEATURE_IMPORTANCE_FILE,
        index=False,
    )

    logger.info(
        "Feature importance exported to %s",
        FEATURE_IMPORTANCE_FILE,
    )

    log_success(
        "Feature importance report exported."
    )


# ======================================================
# FEATURE SUMMARY
# ======================================================

def feature_summary(
    self,
) -> None:
    """
    Display feature selection summary.
    """

    log_section(
        "Feature Selection Summary"
    )

    if self.feature_importance_ is None:

        logger.warning(
            "Feature importance is unavailable."
        )

        return

    logger.info(
        "Total Features : %d",
        len(self.feature_importance_),
    )

    logger.info(
        "Selected Features : %d",
        len(self.selected_features_),
    )

    logger.info(
        "Top Five Features:"
    )

    for _, row in (
        self.feature_importance_
        .head(5)
        .iterrows()
    ):

        logger.info(
            "%s -> %.6f",
            row["feature"],
            row["importance"],
        )

    log_success(
        "Feature selection summary generated."
      )
# ======================================================
    # COMPLETE FEATURE SELECTION PIPELINE
    # ======================================================

    def run(
        self,
        X,
        y,
        feature_names: list[str],
        top_n: int = 20,
    ):
        """
        Execute the complete feature selection pipeline.

        Returns
        -------
        tuple
            (
                X_selected,
                selected_feature_names,
                feature_importance_dataframe
            )
        """

        log_section("Starting Feature Selection Pipeline")

        try:

            # Step 1
            self.validate_feature_names(
                feature_names,
                X,
            )

            # Step 2
            X_filtered, filtered_names = (
                self.remove_low_variance_features(
                    X,
                    feature_names,
                )
            )

            # Step 3
            importance_df = (
                self.calculate_feature_importance(
                    X_filtered,
                    y,
                    filtered_names,
                )
            )

            # Step 4
            self.rank_features()

            # Step 5
            selected_features = (
                self.select_top_features(
                    top_n=top_n
                )
            )

            # Step 6
            self.export_feature_importance()

            # Step 7
            self.feature_summary()

            selected_indices = [

                filtered_names.index(name)

                for name in selected_features

            ]

            X_selected = X_filtered[
                :,
                selected_indices
            ]

            log_success(
                "Feature selection pipeline completed successfully."
            )

            return (
                X_selected,
                selected_features,
                importance_df,
            )

        except Exception:

            logger.exception(
                "Feature selection pipeline failed."
            )

            raise


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    from src.data_loader import DataLoader
    from src.preprocessing import Preprocessor

    try:

        log_section(
            "Feature Selection Module"
        )

        loader = DataLoader()

        dataframe = loader.run()

        preprocessor = Preprocessor()

        (
            X_train,
            X_test,
            y_train,
            y_test,
            fitted_preprocessor,
        ) = preprocessor.run(dataframe)

        feature_names = list(
            fitted_preprocessor.get_feature_names_out()
        )

        selector = FeatureSelector()

        (
            X_selected,
            selected_features,
            importance_report,
        ) = selector.run(
            X_train,
            y_train,
            feature_names,
            top_n=20,
        )

        logger.info(
            "Selected Feature Matrix Shape : %s",
            X_selected.shape,
        )

        logger.info(
            "Selected Feature Count : %d",
            len(selected_features),
        )

        log_success(
            "Feature selection completed successfully."
        )

    except Exception:

        logger.exception(
            "Feature selection execution failed."
        )

        raise
      
