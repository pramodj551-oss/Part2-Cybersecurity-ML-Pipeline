"""AI-Powered Cybersecurity ML Pipeline - Data Preprocessing."""
from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import (TARGET_COLUMN, NUMERICAL_FEATURES, CATEGORICAL_FEATURES,
                        TEST_SIZE, RANDOM_STATE, TRAIN_DATA_FILE, TEST_DATA_FILE,
                        FEATURE_COLUMNS_FILE, PREPROCESSOR_FILE)
from src.logger import logger, log_section, log_success
from src.utils import validate_dataframe, save_model


class Preprocessor:
    """Validate, split, and preprocess cybersecurity incident data."""

    def __init__(self) -> None:
        self.numeric_imputer = SimpleImputer(strategy="median")
        self.categorical_imputer = SimpleImputer(strategy="most_frequent")
        self._missing_value_imputers_fitted = False
        self.train_df_before_imputation_: pd.DataFrame | None = None
        self.test_df_before_imputation_: pd.DataFrame | None = None

    def validate_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        log_section("Dataset Validation")
        validate_dataframe(df)
        if TARGET_COLUMN not in df.columns:
            raise ValueError(f"Target column '{TARGET_COLUMN}' not found.")
        return df.copy()

    def get_missing_value_report(self, df: pd.DataFrame) -> pd.DataFrame:
        report = pd.DataFrame({"Missing Values": df.isnull().sum(),
                               "Missing Percentage": (df.isnull().mean() * 100).round(2)})
        return report[report["Missing Values"] > 0].sort_values("Missing Values", ascending=False)

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fit imputers on training data only."""
        result = df.copy()
        numeric = [c for c in NUMERICAL_FEATURES if c in result.columns]
        categorical = [c for c in CATEGORICAL_FEATURES if c in result.columns]
        if numeric:
            result[numeric] = self.numeric_imputer.fit_transform(result[numeric])
        if categorical:
            result[categorical] = self.categorical_imputer.fit_transform(result[categorical])
        self._missing_value_imputers_fitted = True
        return result

    def transform_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply training-fitted imputers to validation/test data."""
        if not self._missing_value_imputers_fitted:
            raise RuntimeError("Missing value imputers must be fitted on training data first.")
        result = df.copy()
        numeric = [c for c in NUMERICAL_FEATURES if c in result.columns]
        categorical = [c for c in CATEGORICAL_FEATURES if c in result.columns]
        if numeric:
            result[numeric] = self.numeric_imputer.transform(result[numeric])
        if categorical:
            result[categorical] = self.categorical_imputer.transform(result[categorical])
        return result

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.drop_duplicates().reset_index(drop=True)

    def process_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        if "incident_date" in result.columns:
            result["incident_date"] = pd.to_datetime(result["incident_date"], errors="coerce")
        return result

    def convert_boolean_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        mapping = {"Yes": 1, "No": 0, "YES": 1, "NO": 0, "True": 1, "False": 0, True: 1, False: 0}
        for column in ["resolved_within_7_days", "data_exfiltration", "zero_day_used"]:
            if column in result.columns:
                result[column] = pd.to_numeric(result[column].replace(mapping), errors="coerce").fillna(0).astype("int64")
        return result

    def validate_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        for column in NUMERICAL_FEATURES:
            if column in result.columns:
                result[column] = pd.to_numeric(result[column], errors="coerce")
        result[TARGET_COLUMN] = pd.to_numeric(result[TARGET_COLUMN], errors="coerce")
        if result[TARGET_COLUMN].isna().any():
            raise ValueError(f"Target column '{TARGET_COLUMN}' contains missing or non-numeric values.")
        return result

    def build_preprocessor(self) -> ColumnTransformer:
        numeric_pipeline = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())])
        categorical_pipeline = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))])
        return ColumnTransformer([
            ("numerical", numeric_pipeline, [c for c in NUMERICAL_FEATURES if c != TARGET_COLUMN]),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ], remainder="drop")

    def fit_transform(self, df: pd.DataFrame):
        X = df.drop(columns=[TARGET_COLUMN])
        y = df[TARGET_COLUMN]
        preprocessor = self.build_preprocessor()
        return preprocessor.fit_transform(X), y, preprocessor

    def transform(self, df: pd.DataFrame, preprocessor: ColumnTransformer):
        X = df.drop(columns=[TARGET_COLUMN], errors="ignore")
        y = df[TARGET_COLUMN] if TARGET_COLUMN in df.columns else None
        return preprocessor.transform(X), y

    def split_data(self, df: pd.DataFrame):
        return train_test_split(df, test_size=TEST_SIZE, random_state=RANDOM_STATE)

    def save_processed_data(self, train_df: pd.DataFrame, test_df: pd.DataFrame) -> None:
        train_df.to_csv(TRAIN_DATA_FILE, index=False)
        test_df.to_csv(TEST_DATA_FILE, index=False)

    def save_preprocessor(self, preprocessor) -> None:
        save_model(preprocessor, PREPROCESSOR_FILE)

    def save_feature_names(self, preprocessor) -> None:
        pd.DataFrame({"feature_name": list(preprocessor.get_feature_names_out())}).to_csv(FEATURE_COLUMNS_FILE, index=False)

    def preprocessing_summary(self, train_df: pd.DataFrame, test_df: pd.DataFrame) -> None:
        logger.info("Train Shape : %s | Test Shape : %s | Target : %s", train_df.shape, test_df.shape, TARGET_COLUMN)

    def run(self, df: pd.DataFrame):
        try:
            df = self.validate_dataset(df)
            self.get_missing_value_report(df)
            df = self.remove_duplicates(df)
            df = self.process_dates(df)
            df = self.convert_boolean_columns(df)
            df = self.validate_data_types(df)
            train_df, test_df = self.split_data(df)
            # Preserve the cleaned-but-unfitted split so CV can fit every
            # preprocessing step inside each fold without using other folds.
            self.train_df_before_imputation_ = train_df.copy()
            self.test_df_before_imputation_ = test_df.copy()
            train_df = self.handle_missing_values(train_df)
            test_df = self.transform_missing_values(test_df)
            X_train, y_train, preprocessor = self.fit_transform(train_df)
            X_test, y_test = self.transform(test_df, preprocessor)
            self.save_processed_data(train_df, test_df)
            self.save_preprocessor(preprocessor)
            self.save_feature_names(preprocessor)
            self.preprocessing_summary(train_df, test_df)
            log_success("Complete preprocessing pipeline executed successfully.")
            return X_train, X_test, y_train, y_test, preprocessor
        except Exception:
            logger.exception("Preprocessing pipeline failed.")
            raise
