"""Runtime entry point for STEP 20 model explainability.

Works when invoked directly from the repository root or by GitHub Actions.
"""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.model_explainability import ModelExplainability


if __name__ == "__main__":
    ModelExplainability().run()
    print("STEP 20 model explainability completed successfully.")
