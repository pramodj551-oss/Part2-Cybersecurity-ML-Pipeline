"""
==========================================================
AI-Powered Cybersecurity ML Pipeline
Part 2 - Root Pipeline Executor

This is the entry point for running the complete ML pipeline.
It imports and executes the main pipeline from src.run_pipeline.

Author : Pramod Prakash Jadhav
Python : 3.11+
==========================================================
"""

from __future__ import annotations

import sys

# Import main entry point from src
from src.run_pipeline import main

if __name__ == "__main__":
    sys.exit(main())
