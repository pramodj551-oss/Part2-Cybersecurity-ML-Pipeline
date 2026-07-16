"""
==========================================================
AI-Powered Cybersecurity ML Pipeline
Part 2 - Centralized Logging Module

Author : Pramod Prakash Jadhav
Python : 3.11+
==========================================================
"""

import logging
from pathlib import Path

from src.config import OUTPUT_DIR, TRAINING_LOG_FILE


def setup_logger(
    logger_name: str = "CybersecurityMLPipeline",
    log_level: int = logging.INFO,
) -> logging.Logger:
    """
    Configure and return a reusable logger.

    Parameters
    ----------
    logger_name : str
        Name of the logger.
    log_level : int
        Logging level.

    Returns
    -------
    logging.Logger
        Configured logger instance.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(logger_name)

    if logger.handlers:
        return logger

    logger.setLevel(log_level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # File Handler
    file_handler = logging.FileHandler(
        TRAINING_LOG_FILE,
        mode="a",
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.propagate = False

    return logger


logger = setup_logger()


def log_section(title: str) -> None:
    """
    Log a formatted section heading.
    """

    logger.info("=" * 70)
    logger.info(title)
    logger.info("=" * 70)


def log_success(message: str) -> None:
    """
    Log a success message.
    """

    logger.info(f"SUCCESS: {message}")


def log_warning(message: str) -> None:
    """
    Log a warning message.
    """

    logger.warning(message)


def log_error(message: str) -> None:
    """
    Log an error message.
    """

    logger.error(message)


def log_exception(message: str) -> None:
    """
    Log an exception with traceback.
    """

    logger.exception(message)
