#!/usr/bin/env python3
"""HR Analytics pipeline: preprocess data, train models, launch dashboard."""

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def run_preprocess():
    from src.preprocessing import run_preprocessing

    print("=" * 60)
    print("STEP 1: Data Processing")
    print("=" * 60)
    run_preprocessing()


def run_train():
    from src.train_model import run_training

    print("\n" + "=" * 60)
    print("STEP 2: Model Training")
    print("=" * 60)
    run_training()


def run_dashboard():
    app_path = PROJECT_ROOT / "app" / "streamlit_app.py"
    print("\n" + "=" * 60)
    print("STEP 3: Launching Streamlit Dashboard")
    print("=" * 60)
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(app_path)],
        check=True,
    )


def main():
    parser = argparse.ArgumentParser(
        description="HR Analytics — attrition analysis and prediction"
    )
    parser.add_argument(
        "--step",
        choices=["all", "preprocess", "train", "dashboard"],
        default="all",
        help="Pipeline step to run (default: all)",
    )
    args = parser.parse_args()

    if args.step in ("all", "preprocess"):
        run_preprocess()
    if args.step in ("all", "train"):
        run_train()
    if args.step in ("all", "dashboard"):
        run_dashboard()


if __name__ == "__main__":
    main()
