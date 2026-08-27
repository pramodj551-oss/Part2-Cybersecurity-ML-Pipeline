"""
==========================================================
AI-Powered Cybersecurity ML Pipeline
Part 2 - Pipeline Runner

Author : Pramod Prakash Jadhav
Python : 3.11+
==========================================================
"""

from __future__ import annotations

import sys
import traceback
from datetime import datetime

from src.pipeline import MLPipeline
from src.logger import (
    logger,
    log_section,
    log_success,
)


def main() -> int:
    """
    Main entry point for the machine learning pipeline.

    Returns
    -------
    int
        Exit status code.
    """

    log_section(
        "AI-Powered Cybersecurity ML Pipeline"
    )

    logger.info(
        "Pipeline execution started at %s",
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    )

    try:

        pipeline = MLPipeline()

        summary = pipeline.run()

        log_success(
            "Pipeline executed successfully."
        )

        logger.info(
            "Execution Summary"
        )

        for key, value in summary.items():

            logger.info(
                "%s : %s",
                key,
                value,
            )

        logger.info(
            "Pipeline finished successfully."
        )

        return 0

    except KeyboardInterrupt:

        logger.warning(
            "Pipeline execution cancelled by user."
        )

        return 1

    except Exception as error:

        logger.exception(
            "Pipeline execution failed."
        )

        traceback.print_exc()

        print(
            "\nERROR:",
            error,
            file=sys.stderr,
        )

        return 1


if __name__ == "__main__":

    sys.exit(main())
