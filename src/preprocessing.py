"""AI-Powered Cybersecurity ML Pipeline - Data Preprocessing."""
from __future__ import annotations

import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import (
    TARGET_COLUMN,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    TEST_SIZE,
    RANDOM_STATE,
    TRAIN_DATA_FILE,
    TEST_DATA_FILE,
    FEATURE_COLUMNS_FILE,
    PREPROCESSOR_FILE,
)
from src.logger import logger, log_section, log_success
from src.utils import validate_dataframe, save_model


class Preprocessor:
    """Performs dataset validation and model-ready preprocessing."""

    def __init__(self) -> None:
        self.numeric_imputer = SimpleImputer(strategy="median")
        self.categorical_imputer = SimpleImputer(strategy="most_frequent")

    def validate_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        log_section("Dataset Validation")
        validate_dataframe(df)
        if TARGET_COLUMN not in df.columns:
            raise ValueError(f"Target column '{TARGET_COLUMN}' not found.")
        logger.info("Dataset Shape : %s", df.shape)
        logger.info("Target Column : %s", TARGET_COLUMN)
        log_success("Dataset validation completed.")
        return df

    def get_missing_value_report(self, df: pd.DataFrame) -> pd.DataFrame:
        report = pd.DataFrame({
            "Missing Values": df.isnull().sum(),
            "Missing Percentage": (df.isnull().mean() * 100).round(2),
        })
        report = report[report["Missing Values"] > 0]
        if report.empty:
            logger.info("No missing values detected.")
        else:
            logger.info("Missing value report generated.")
        return report.sort_values("Missing Values", ascending=False)

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        log_section("Handling Missing Values")
        numeric_columns = [c for c in NUMERICAL_FEATURES if c in df.columns]
        categorical_columns = [c for c in CATEGORICAL_FEATURES if c in df.columns]
        if numeric_columns:
            df[numeric_columns] = self.numeric_imputer.fit_transform(df[numeric_columns])
        if categorical_columns:
            df[categorical_columns] = self.categorical_imputer.fit_transform(df[categorical_columns])
        remaining = int(df.isnull().sum().sum())
        logger.info("Remaining Missing Values : %d", remaining)
        log_success("Missing value handling completed.")
        return df

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        log_section("Removing Duplicate Records")
        before = len(df)
        df = df.drop_duplicates().reset_index(drop=True)
        logger.info("Duplicate rows removed : %d", before - len(df))
        log_success("Duplicate removal completed.")
        return df

    def process_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        log_section("Processing Date Columns")
        if "incident_date" not in df.columns:
            logger.warning("'incident_date' column not found.")
            return df
        df["incident_date"] = pd.to_datetime(df["incident_date"], errors="coerce")
        logger.info("Invalid dates detected : %d", int(df["incident_date"].isna().sum()))
        log_success("Date preprocessing completed.")
        return df

    def convert_boolean_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        log_section("Boolean Conversion")
        boolean_columns = ["resolved_within_7_days", "data_exfiltration", "zero_day_used"]
        mapping = {"Yes": 1, "No": 0, "YES": 1, "NO": 0, "True": 1, "False": 0, True: 1, False: 0}
        for column in boolean_columns:
            if column not in df.columns:
                continue
            df[column] = pd.to_numeric(df[column].replace(mapping), errors="coerce").fillna(0).astype("int64")
            logger.info("%s converted to binary.", column)
        log_success("Boolean conversion completed.")
        return df

    def validate_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        log_section("Validating Data Types")
        for column in NUMERICAL_FEATURES:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")
        logger.info("Numerical feature validation completed.")
        log_success("Data type validation successful.")
        return df

    def build_preprocessor(self) -> ColumnTransformer:
        log_section("Building Preprocessing Pipeline")
        numeric_pipeline = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())])
        categorical_pipeline = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))])
        preprocessor = ColumnTransformer(
            transformers=[
                ("numerical", numeric_pipeline, [c for c in NUMERICAL_FEATURES if c != TARGET_COLUMN]),
                ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
            ],
            remainder="drop",
        )
        log_success("Preprocessing pipeline created.")
        return preprocessor

    def fit_transform(self, df: pd.DataFrame):
        log_section("Fitting Preprocessor")
        X = df.drop(columns=[TARGET_COLUMN])
        y = df[TARGET_COLUMN]
        preprocessor = self.build_preprocessor()
        X_processed = preprocessor.fit_transform(X)
        logger.info("Processed feature matrix shape: %s", X_processed.shape)
        log_success("Training data transformed.")
        return X_processed, y, preprocessor

    def transform(self, df: pd.DataFrame, preprocessor: ColumnTransformer):
        X = df.drop(columns=[TARGET_COLUMN])
        y = df[TARGET_COLUMN]
        X_processed = preprocessor.transform(X)
        logger.info("Test dataset transformed.")
        return X_processed, y

    def split_data(self, df: pd.DataFrame):
        log_section("Train-Test Split")
        train_df, test_df = train_test_split(df, test_size=TEST_SIZE, random_state=RANDOM_STATE)
        logger.info("Training samples : %d", len(train_df))
        logger.info("Testing samples : %d", len(test_df))
        log_success("Train-Test split completed.")
        return train_df, test_df

    def save_processed_data(self, train_df: pd.DataFrame, test_df: pd.DataFrame) -> None:
        log_section("Saving Processed Datasets")
        train_df.to_csv(TRAIN_DATA_FILE, index=False)
        test_df.to_csv(TEST_DATA_FILE, index=False)
        logger.info("Training dataset saved: %s", TRAIN_DATA_FILE)
        logger.info("Testing dataset saved: %s", TEST_DATA_FILE)
        log_success("Processed datasets saved.")

    def save_preprocessor(self, preprocessor) -> None:
        save_model(preprocessor, PREPROCESSOR_FILE)
        log_success("Preprocessor saved successfully.")

    def save_feature_names(self, preprocessor) -> None:
        feature_names = list(preprocessor.get_feature_names_out())
        pd.DataFrame({"feature_name": feature_names}).to_csv(FEATURE_COLUMNS_FILE, index=False)
        logger.info("Feature names saved.")

    def preprocessing_summary(self, train_df: pd.DataFrame, test_df: pd.DataFrame) -> None:
        log_section("Preprocessing Summary")
        logger.info("Train Shape : %s", train_df.shape)
        logger.info("Test Shape : %s", test_df.shape)
        logger.info("Target Variable : %s", TARGET_COLUMN)
        log_success("Preprocessing completed successfully.")

    def run(self, df: pd.DataFrame):
        log_section("Starting Data Preprocessing Pipeline")
        try:
            df = self.validate_dataset(df)
            self.get_missing_value_report(df)
            df = self.handle_missing_values(df)
            df = self.remove_duplicates(df)
            df = self.process_dates(df)
            df = self.convert_boolean_columns(df)
            df = self.validate_data_types(df)
            train_df, test_df = self.split_data(df)
            X_train, y_train, preprocessor = self.fit_transform(train_df)
            X_test, y_test = self.transform(test_df, preprocessor)
            self.save_processed_data(train_df, test_df)
            self.save_preprocessor(preprocessor)
            self.save_feature_names(preprocessor)
            self.preprocessing_summary(train_df, test_df)
            log_success("Complete preprocessing pipeline executed successfully.")
            return X_train, X_test, y_train, y_test, preprocessor
        except Exception as error:
            logger.exception("Preprocessing pipeline failed.")
            raise error


if __name__ == "__main__":
    from src.data_loader import DataLoader
    log_section("Preprocessing Module Execution")
    dataframe = DataLoader().run()
    Preprocessor().run(dataframe)
