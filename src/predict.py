"""Predict employee attrition from input features."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.config import (
    CATEGORICAL_COLUMNS,
    FEATURE_NAMES_FILE,
    RANDOM_FOREST_MODEL_FILE,
    TARGET_COLUMN,
)
from src.preprocessing import encode_categoricals


def load_model(model_path: Path | None = None):
    """Load the production Random Forest model."""
    path = model_path or RANDOM_FOREST_MODEL_FILE
    return joblib.load(path)


def load_artifacts() -> tuple:
    """Load model, encoders, and feature column order."""
    from src.config import ENCODERS_FILE

    model = load_model()
    encoders = joblib.load(ENCODERS_FILE)
    feature_names = joblib.load(FEATURE_NAMES_FILE)
    return model, encoders, feature_names


def build_input_dataframe(employee_data: dict) -> pd.DataFrame:
    """Single-row DataFrame from user-provided employee details."""
    return pd.DataFrame([employee_data])


def predict_attrition(
    employee_data: dict,
    model=None,
    encoders=None,
    feature_names=None,
) -> dict:
    """
    Predict whether an employee will leave.

    Parameters
    ----------
    employee_data : dict
        Raw feature values (same keys as dataset, excluding dropped columns).

    Returns
    -------
    dict with keys: prediction_label, prediction_code, probability_leave
    """
    if model is None or encoders is None or feature_names is None:
        model, encoders, feature_names = load_artifacts()

    df = build_input_dataframe(employee_data)
    encoded, _ = encode_categoricals(df, fit=False, encoders=encoders)

    if TARGET_COLUMN in encoded.columns:
        encoded = encoded.drop(columns=[TARGET_COLUMN])

    X = encoded.reindex(columns=feature_names, fill_value=0)

    proba = model.predict_proba(X)[0]
    pred_code = int(model.predict(X)[0])

    # Attrition encoder: 0 = No (Stay), 1 = Yes (Leave) — verify from encoders
    attrition_encoder = encoders.get(TARGET_COLUMN)
    if attrition_encoder is not None:
        classes = list(attrition_encoder.classes_)
        leave_idx = classes.index("Yes") if "Yes" in classes else 1
        stay_idx = classes.index("No") if "No" in classes else 0
        label = "Will Leave" if pred_code == leave_idx else "Will Stay"
        prob_leave = float(proba[leave_idx])
    else:
        label = "Will Leave" if pred_code == 1 else "Will Stay"
        prob_leave = float(proba[1]) if len(proba) > 1 else float(proba[0])

    return {
        "prediction_label": label,
        "prediction_code": pred_code,
        "probability_leave": round(prob_leave, 4),
        "probability_stay": round(1 - prob_leave, 4),
    }


if __name__ == "__main__":
    sample = {
        "Age": 35,
        "Attrition": "No",
        "BusinessTravel": "Travel_Rarely",
        "DailyRate": 1000,
        "Department": "Sales",
        "DistanceFromHome": 5,
        "Education": 3,
        "EducationField": "Life Sciences",
        "EnvironmentSatisfaction": 3,
        "Gender": "Male",
        "HourlyRate": 80,
        "JobInvolvement": 3,
        "JobLevel": 2,
        "JobRole": "Sales Executive",
        "JobSatisfaction": 2,
        "MaritalStatus": "Married",
        "MonthlyIncome": 5000,
        "MonthlyRate": 15000,
        "NumCompaniesWorked": 2,
        "OverTime": "Yes",
        "PercentSalaryHike": 15,
        "PerformanceRating": 3,
        "RelationshipSatisfaction": 3,
        "StockOptionLevel": 1,
        "TotalWorkingYears": 10,
        "TrainingTimesLastYear": 2,
        "WorkLifeBalance": 2,
        "YearsAtCompany": 5,
        "YearsInCurrentRole": 3,
        "YearsSinceLastPromotion": 1,
        "YearsWithCurrManager": 2,
    }
    result = predict_attrition(sample)
    print(result)
