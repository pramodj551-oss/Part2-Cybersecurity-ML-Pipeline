"""
==========================================================
AI-Powered Cybersecurity ML Pipeline
Part 2 - Data Preprocessing

Author : Pramod Prakash Jadhav
Python : 3.11+
==========================================================
"""

from __future__ import annotations

import pandas as pd
import numpy as np

from sklearn.impute import SimpleImputer

from src.config import (
    TARGET_COLUMN,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
)

from src.logger import (
    logger,
    log_section,
    log_success,
)

from src.utils import (
    validate_dataframe,
)


class Preprocessor:
    """
    Performs data preprocessing before model training.

    Responsibilities
    ----------------
    - Dataset validation
    - Missing value handling
    - Duplicate removal
    - Date preprocessing
    - Feature encoding
    - Feature scaling
    - Train/Test split
    """

    def __init__(self) -> None:

        self.numeric_imputer = SimpleImputer(
            strategy="median"
        )

        self.categorical_imputer = SimpleImputer(
            strategy="most_frequent"
        )

    # ======================================================
    # DATASET VALIDATION
    # ======================================================

    def validate_dataset(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Validate input dataset before preprocessing.
        """

        log_section("Dataset Validation")

        validate_dataframe(df)

        if TARGET_COLUMN not in df.columns:
            raise ValueError(
                f"Target column '{TARGET_COLUMN}' not found."
            )

        logger.info(
            "Dataset Shape : %s",
            df.shape,
        )

        logger.info(
            "Target Column : %s",
            TARGET_COLUMN,
        )

        log_success(
            "Dataset validation completed."
        )

        return df

    # ======================================================
    # MISSING VALUE REPORT
    # ======================================================

    def get_missing_value_report(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Generate missing value statistics.
        """

        report = pd.DataFrame({

            "Missing Values": df.isnull().sum(),

            "Missing Percentage":
                (
                    df.isnull().mean() * 100
                ).round(2)

        })

        report = report[
            report["Missing Values"] > 0
        ]

        if report.empty:

            logger.info(
                "No missing values detected."
            )

        else:

            logger.info(
                "Missing value report generated."
            )

        return report.sort_values(
            by="Missing Values",
            ascending=False,
        )

    # ======================================================
    # HANDLE MISSING VALUES
    # ======================================================

    def handle_missing_values(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Fill missing values using
        Median (Numerical)
        Most Frequent (Categorical)
        """

        log_section(
            "Handling Missing Values"
        )

        numeric_columns = [

            col

            for col in NUMERICAL_FEATURES

            if col in df.columns

        ]

        categorical_columns = [

            col

            for col in CATEGORICAL_FEATURES

            if col in df.columns

        ]

        if numeric_columns:

            df[numeric_columns] = (
                self.numeric_imputer.fit_transform(
                    df[numeric_columns]
                )
            )

        if categorical_columns:

            df[categorical_columns] = (
                self.categorical_imputer.fit_transform(
                    df[categorical_columns]
                )
            )

        remaining = int(
            df.isnull().sum().sum()
        )

        logger.info(
            "Remaining Missing Values : %d",
            remaining,
        )

        log_success(
            "Missing value handling completed."
        )

        return df
      # ======================================================
    # REMOVE DUPLICATES
    # ======================================================

    def remove_duplicates(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Remove duplicate records from the dataset.
        """

        log_section("Removing Duplicate Records")

        before = len(df)

        df = df.drop_duplicates().reset_index(drop=True)

        removed = before - len(df)

        logger.info(
            "Duplicate rows removed : %d",
            removed,
        )

        log_success(
            "Duplicate removal completed."
        )

        return df

    # ======================================================
    # DATE PREPROCESSING
    # ======================================================

    def process_dates(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Convert incident_date to datetime format.
        """

        log_section("Processing Date Columns")

        if "incident_date" not in df.columns:

            logger.warning(
                "'incident_date' column not found."
            )

            return df

        df["incident_date"] = pd.to_datetime(
            df["incident_date"],
            errors="coerce",
        )

        invalid_dates = (
            df["incident_date"].isna().sum()
        )

        logger.info(
            "Invalid dates detected : %d",
            invalid_dates,
        )

        log_success(
            "Date preprocessing completed."
        )

        return df

    # ======================================================
    # BOOLEAN CONVERSION
    # ======================================================

    def convert_boolean_columns(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Convert Yes/No style columns into
        binary integer values.
        """

        log_section("Boolean Conversion")

        boolean_columns = [

            "resolved_within_7_days",

            "data_exfiltration",

            "zero_day_used",

        ]

        mapping = {

            "Yes": 1,
            "No": 0,
            "YES": 1,
            "NO": 0,
            "True": 1,
            "False": 0,
            True: 1,
            False: 0,
        }

        for column in boolean_columns:

            if column not in df.columns:
                continue

            df[column] = (
                df[column]
                .replace(mapping)
                .fillna(df[column])
                .astype("int64")
            )

            logger.info(
                "%s converted to binary.",
                column,
            )

        log_success(
            "Boolean conversion completed."
        )

        return df

    # ======================================================
    # DATA TYPE VALIDATION
    # ======================================================

    def validate_data_types(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Ensure numerical columns have numeric
        data types.
        """

        log_section("Validating Data Types")

        for column in NUMERICAL_FEATURES:

            if column not in df.columns:
                continue

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

        logger.info(
            "Numerical feature validation completed."
        )

        log_success(
            "Data type validation successful."
        )

        return df
      from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
)

    # ======================================================
    # BUILD PREPROCESSOR
    # ======================================================

    def build_preprocessor(self) -> ColumnTransformer:
        """
        Create a preprocessing pipeline for
        numerical and categorical features.
        """

        log_section("Building Preprocessing Pipeline")

        numeric_pipeline = Pipeline(
            steps=[
                ("scaler", StandardScaler())
            ]
        )

        categorical_pipeline = Pipeline(
            steps=[
                (
                    "encoder",
                    OneHotEncoder(
                        handle_unknown="ignore",
                        sparse_output=False,
                    ),
                )
            ]
        )

        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "numerical",
                    numeric_pipeline,
                    NUMERICAL_FEATURES,
                ),
                (
                    "categorical",
                    categorical_pipeline,
                    CATEGORICAL_FEATURES,
                ),
            ],
            remainder="drop",
        )

        log_success(
            "Preprocessing pipeline created."
        )

        return preprocessor

    # ======================================================
    # FIT & TRANSFORM
    # ======================================================

    def fit_transform(
        self,
        df: pd.DataFrame,
    ):
        """
        Fit preprocessing pipeline and
        transform training data.
        """

        log_section("Fitting Preprocessor")

        X = df.drop(columns=[TARGET_COLUMN])

        y = df[TARGET_COLUMN]

        preprocessor = self.build_preprocessor()

        X_processed = preprocessor.fit_transform(X)

        logger.info(
            "Processed feature matrix shape: %s",
            X_processed.shape,
        )

        log_success(
            "Training data transformed."
        )

        return (
            X_processed,
            y,
            preprocessor,
        )

    # ======================================================
    # TRANSFORM
    # ======================================================

    def transform(
        self,
        df: pd.DataFrame,
        preprocessor: ColumnTransformer,
    ):
        """
        Transform new data using an
        already-fitted preprocessor.
        """

        X = df.drop(columns=[TARGET_COLUMN])

        y = df[TARGET_COLUMN]

        X_processed = preprocessor.transform(X)

        logger.info(
            "Test dataset transformed."
        )

        return (
            X_processed,
            y,
      )
      from sklearn.model_selection import train_test_split

from src.config import (
    TEST_SIZE,
    RANDOM_STATE,
    TRAIN_DATA_FILE,
    TEST_DATA_FILE,
    FEATURE_COLUMNS_FILE,
)

from src.utils import (
    save_model,
)

    # ======================================================
    # TRAIN TEST SPLIT
    # ======================================================

    def split_data(
        self,
        df: pd.DataFrame,
    ):
        """
        Split dataset into train and test sets.
        """

        log_section("Train-Test Split")

        train_df, test_df = train_test_split(
            df,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
        )

        logger.info(
            "Training samples : %d",
            len(train_df),
        )

        logger.info(
            "Testing samples : %d",
            len(test_df),
        )

        log_success(
            "Train-Test split completed."
        )

        return train_df, test_df

    # ======================================================
    # SAVE DATASETS
    # ======================================================

    def save_processed_data(
        self,
        train_df: pd.DataFrame,
        test_df: pd.DataFrame,
    ) -> None:
        """
        Save processed datasets.
        """

        log_section("Saving Processed Datasets")

        train_df.to_csv(
            TRAIN_DATA_FILE,
            index=False,
        )

        test_df.to_csv(
            TEST_DATA_FILE,
            index=False,
        )

        logger.info(
            "Training dataset saved: %s",
            TRAIN_DATA_FILE,
        )

        logger.info(
            "Testing dataset saved: %s",
            TEST_DATA_FILE,
        )

        log_success(
            "Processed datasets saved."
        )

    # ======================================================
    # SAVE PREPROCESSOR
    # ======================================================

    def save_preprocessor(
        self,
        preprocessor,
    ) -> None:
        """
        Save fitted preprocessing pipeline.
        """

        from src.config import PREPROCESSOR_FILE

        save_model(
            preprocessor,
            PREPROCESSOR_FILE,
        )

        log_success(
            "Preprocessor saved successfully."
        )

    # ======================================================
    # SAVE FEATURE NAMES
    # ======================================================

    def save_feature_names(
        self,
        preprocessor,
    ) -> None:
        """
        Save transformed feature names.
        """

        feature_names = list(
            preprocessor.get_feature_names_out()
        )

        pd.DataFrame(
            {
                "feature_name": feature_names
            }
        ).to_csv(
            FEATURE_COLUMNS_FILE,
            index=False,
        )

        logger.info(
            "Feature names saved."
        )

    # ======================================================
    # PREPROCESSING SUMMARY
    # ======================================================

    def preprocessing_summary(
        self,
        train_df: pd.DataFrame,
        test_df: pd.DataFrame,
    ) -> None:
        """
        Display preprocessing summary.
        """

        log_section("Preprocessing Summary")

        logger.info(
            "Train Shape : %s",
            train_df.shape,
        )

        logger.info(
            "Test Shape : %s",
            test_df.shape,
        )

        logger.info(
            "Target Variable : %s",
            TARGET_COLUMN,
        )

        log_success(
            "Preprocessing completed successfully."
      )
      # ======================================================
    # COMPLETE PREPROCESSING PIPELINE
    # ======================================================

    def run(self, df: pd.DataFrame):
        """
        Execute the complete preprocessing pipeline.

        Returns
        -------
        tuple
            (
                X_train,
                X_test,
                y_train,
                y_test,
                fitted_preprocessor
            )
        """

        log_section("Starting Data Preprocessing Pipeline")

        try:

            # Step 1
            df = self.validate_dataset(df)

            # Step 2
            self.get_missing_value_report(df)

            # Step 3
            df = self.handle_missing_values(df)

            # Step 4
            df = self.remove_duplicates(df)

            # Step 5
            df = self.process_dates(df)

            # Step 6
            df = self.convert_boolean_columns(df)

            # Step 7
            df = self.validate_data_types(df)

            # Step 8
            train_df, test_df = self.split_data(df)

            # Step 9
            X_train, y_train, preprocessor = (
                self.fit_transform(train_df)
            )

            # Step 10
            X_test, y_test = (
                self.transform(
                    test_df,
                    preprocessor,
                )
            )

            # Step 11
            self.save_processed_data(
                train_df,
                test_df,
            )

            # Step 12
            self.save_preprocessor(
                preprocessor
            )

            # Step 13
            self.save_feature_names(
                preprocessor
            )

            # Step 14
            self.preprocessing_summary(
                train_df,
                test_df,
            )

            log_success(
                "Complete preprocessing pipeline executed successfully."
            )

            return (
                X_train,
                X_test,
                y_train,
                y_test,
                preprocessor,
            )

        except Exception as error:

            logger.exception(
                "Preprocessing pipeline failed."
            )

            raise error


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    from src.data_loader import DataLoader

    log_section(
        "Preprocessing Module Execution"
    )

    try:

        loader = DataLoader()

        df = loader.run()

        preprocessor = Preprocessor()

        (
            X_train,
            X_test,
            y_train,
            y_test,
            pipeline,
        ) = preprocessor.run(df)

        logger.info(
            "Training Features Shape : %s",
            X_train.shape,
        )

        logger.info(
            "Testing Features Shape : %s",
            X_test.shape,
        )

        logger.info(
            "Training Labels : %d",
            len(y_train),
        )

        logger.info(
            "Testing Labels : %d",
            len(y_test),
        )

        log_success(
            "Preprocessing completed successfully."
        )

    except Exception:

        logger.exception(
            "Preprocessing execution failed."
        )
        raise
      
