"""
==========================================================
AI-Powered Cybersecurity ML Pipeline
Part 2 - Utility Functions

Author : Pramod Prakash Jadhav
Python : 3.11+
==========================================================
"""

from __future__ import annotations

import json
import random
import time
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from src.logger import logger


# ==========================================================
# DIRECTORY UTILITIES
# ==========================================================

def ensure_directory(path: Path) -> None:
    """
    Create a directory if it does not already exist.
    """
    path.mkdir(parents=True, exist_ok=True)


# ==========================================================
# RANDOM SEED
# ==========================================================

def set_random_seed(seed: int = 42) -> None:
    """
    Set random seed for reproducibility.
    """
    random.seed(seed)
    np.random.seed(seed)

    logger.info("Random seed set to %d", seed)


# ==========================================================
# JSON UTILITIES
# ==========================================================

def save_json(data: dict, file_path: Path) -> None:
    """
    Save a dictionary as a JSON file.
    """
    ensure_directory(file_path.parent)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    logger.info("JSON saved: %s", file_path)


def load_json(file_path: Path) -> dict:
    """
    Load a JSON file.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


# ==========================================================
# MODEL UTILITIES
# ==========================================================

def save_model(model: Any, file_path: Path) -> None:
    """
    Save a trained model using Joblib.
    """
    ensure_directory(file_path.parent)

    joblib.dump(model, file_path)

    logger.info("Model saved: %s", file_path)


def load_model(file_path: Path) -> Any:
    """
    Load a trained model.
    """
    logger.info("Loading model: %s", file_path)

    return joblib.load(file_path)


# ==========================================================
# DATASET SUMMARY
# ==========================================================

def dataset_summary(df: pd.DataFrame) -> dict:
    """
    Generate a summary of the dataset.
    """
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_values": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "memory_usage_mb": round(
            df.memory_usage(deep=True).sum() / 1024**2,
            2,
        ),
    }


# ==========================================================
# EXECUTION TIMER
# ==========================================================

class Timer:
    """
    Simple execution timer.
    """

    def __init__(self) -> None:
        self.start_time = time.perf_counter()

    def stop(self) -> float:
        """
        Return elapsed execution time in seconds.
        """
        elapsed = time.perf_counter() - self.start_time

        logger.info(
            "Execution completed in %.2f seconds",
            elapsed,
        )

        return elapsed


# ==========================================================
# DATA VALIDATION
# ==========================================================

def validate_dataframe(df: pd.DataFrame) -> None:
    """
    Validate that the DataFrame is not empty.
    """
    if df.empty:
        raise ValueError("Input DataFrame is empty.")

    logger.info(
        "Dataset validation successful (%d rows).",
        len(df),
                 )
