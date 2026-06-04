"""Load, clean, and preprocess the IBM HR Employee Attrition dataset."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from src.config import (
    CATEGORICAL_COLUMNS,
    DATA_DIR,
    DROP_COLUMNS,
    ENCODERS_FILE,
    FEATURE_NAMES_FILE,
    MODELS_DIR,
    PROCESSED_DATA_FILE,
    RAW_DATA_FILE,
    TARGET_COLUMN,
)


def load_raw_data(filepath: Path | None = None) -> pd.DataFrame:
    """Load the raw CSV dataset."""
    path = filepath or RAW_DATA_FILE
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    return df


def check_data_quality(df: pd.DataFrame) -> dict:
    """Return missing values, duplicates, and shape summary."""
    return {
        "shape": list(df.shape),
        "missing_values": df.isnull().sum().to_dict(),
        "total_missing": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
    }


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates, constant columns, and ID fields."""
    cleaned = df.copy()
    cleaned = cleaned.drop_duplicates()
    cols_to_drop = [c for c in DROP_COLUMNS if c in cleaned.columns]
    cleaned = cleaned.drop(columns=cols_to_drop, errors="ignore")
    return cleaned


def get_descriptive_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Numeric describe plus categorical value counts summary."""
    numeric_stats = df.describe(include=[np.number]).T
    numeric_stats["dtype"] = "numeric"
    return numeric_stats


def encode_categoricals(
    df: pd.DataFrame,
    fit: bool = True,
    encoders: dict | None = None,
) -> tuple[pd.DataFrame, dict]:
    """Label-encode categorical columns; store encoders when fitting."""
    encoded_df = df.copy()
    encoder_map = encoders or {}

    for col in CATEGORICAL_COLUMNS:
        if col not in encoded_df.columns:
            continue
        if fit:
            le = LabelEncoder()
            encoded_df[col] = le.fit_transform(encoded_df[col].astype(str))
            encoder_map[col] = le
        else:
            le = encoder_map[col]
            values = encoded_df[col].astype(str)
            known = set(le.classes_)
            encoded_df[col] = values.apply(
                lambda x: le.transform([x])[0] if x in known else -1
            )

    return encoded_df, encoder_map


def prepare_features_target(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """Split encoded dataframe into X, y."""
    feature_cols = [c for c in df.columns if c != TARGET_COLUMN]
    X = df[feature_cols]
    y = df[TARGET_COLUMN]
    return X, y, feature_cols


def run_preprocessing(
    save: bool = True,
    verbose: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    Full preprocessing pipeline.

    Returns
    -------
    raw_cleaned : DataFrame after cleaning (human-readable labels)
    processed : DataFrame with encoded categoricals
    quality_report : dict with data quality metrics
    """
    raw = load_raw_data()
    quality = check_data_quality(raw)

    if verbose:
        print(f"Loaded {quality['shape'][0]} rows, {quality['shape'][1]} columns")
        print(f"Missing values: {quality['total_missing']}")
        print(f"Duplicate rows: {quality['duplicate_rows']}")

    cleaned = clean_data(raw)
    quality["shape_after_clean"] = list(cleaned.shape)
    stats = get_descriptive_statistics(cleaned)

    if verbose:
        print("\nDescriptive statistics (numeric):")
        print(stats.head(10).to_string())

    processed, encoders = encode_categoricals(cleaned, fit=True)

    if save:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        processed.to_csv(PROCESSED_DATA_FILE, index=False)
        joblib.dump(encoders, ENCODERS_FILE)
        X, _, feature_names = prepare_features_target(processed)
        joblib.dump(feature_names, FEATURE_NAMES_FILE)
        quality_path = MODELS_DIR / "data_quality_report.json"
        with open(quality_path, "w", encoding="utf-8") as f:
            json.dump(quality, f, indent=2)
        if verbose:
            print(f"\nSaved processed data to {PROCESSED_DATA_FILE}")
            print(f"Saved encoders to {ENCODERS_FILE}")

    return cleaned, processed, quality


if __name__ == "__main__":
    run_preprocessing()
