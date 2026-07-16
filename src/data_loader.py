"""
==========================================================
AI-Powered Cybersecurity ML Pipeline
Part 2 - Data Loader

Author : Pramod Prakash Jadhav
Python : 3.11+
==========================================================
"""

from pathlib import Path

import pandas as pd

from src.config import RAW_DATA_FILE
from src.logger import (
    logger,
    log_section,
    log_success,
)
from src.utils import (
    dataset_summary,
    validate_dataframe,
)

# ==========================================================
# REQUIRED DATASET SCHEMA
# ==========================================================

REQUIRED_COLUMNS = [

    "incident_id",
    "incident_date",
    "sector",
    "region",
    "attack_type",
    "threat_actor",
    "records_affected",
    "downtime_hours",
    "ransom_demand_usd",
    "detection_time_hours",
    "severity_score",
    "response_team_size",
    "regulatory_fine_usd",
    "resolved_within_7_days",
    "data_exfiltration",
    "zero_day_used",

]


class DataLoader:
    """
    Loads and validates the cybersecurity dataset.
    """

    def __init__(self, file_path: Path = RAW_DATA_FILE):

        self.file_path = file_path

    # ======================================================

    def load_data(self) -> pd.DataFrame:
        """
        Load CSV dataset.
        """

        log_section("Loading Cybersecurity Dataset")

        if not self.file_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {self.file_path}"
            )

        df = pd.read_csv(self.file_path)

        validate_dataframe(df)

        log_success(
            f"Dataset loaded successfully "
            f"({len(df)} rows)"
        )

        return df

    # ======================================================

    def validate_schema(
        self,
        df: pd.DataFrame,
    ) -> None:
        """
        Validate required columns.
        """

        missing_columns = [

            col

            for col in REQUIRED_COLUMNS

            if col not in df.columns

        ]

        if missing_columns:

            raise ValueError(
                f"Missing columns: {missing_columns}"
            )

        logger.info(
            "Schema validation successful."
        )

    # ======================================================

    def print_summary(
        self,
        df: pd.DataFrame,
    ) -> None:
        """
        Print dataset summary.
        """

        summary = dataset_summary(df)

        logger.info("=" * 60)

        logger.info("DATASET SUMMARY")

        logger.info("=" * 60)

        for key, value in summary.items():

            logger.info("%s : %s", key, value)

    # ======================================================

    def run(self) -> pd.DataFrame:
        """
        Execute complete loading pipeline.
        """

        df = self.load_data()

        self.validate_schema(df)

        self.print_summary(df)

        return df


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    loader = DataLoader()

    dataframe = loader.run()

    print(dataframe.head())
