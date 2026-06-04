"""Project paths and constants."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
SQL_DIR = PROJECT_ROOT / "sql"

RAW_DATA_FILE = DATA_DIR / "WA_Fn-UseC_-HR-Employee-Attrition.csv"
PROCESSED_DATA_FILE = DATA_DIR / "processed_employees.csv"
ENCODERS_FILE = MODELS_DIR / "label_encoders.joblib"
FEATURE_NAMES_FILE = MODELS_DIR / "feature_names.joblib"
LOGISTIC_MODEL_FILE = MODELS_DIR / "logistic_regression.joblib"
RANDOM_FOREST_MODEL_FILE = MODELS_DIR / "random_forest.joblib"
METRICS_FILE = MODELS_DIR / "model_metrics.json"
FEATURE_IMPORTANCE_FILE = MODELS_DIR / "feature_importance.csv"

TARGET_COLUMN = "Attrition"
CONSTANT_COLUMNS = ["EmployeeCount", "Over18", "StandardHours"]
DROP_COLUMNS = ["EmployeeNumber"] + CONSTANT_COLUMNS

CATEGORICAL_COLUMNS = [
    "Attrition",
    "BusinessTravel",
    "Department",
    "EducationField",
    "Gender",
    "JobRole",
    "MaritalStatus",
    "OverTime",
]

RANDOM_STATE = 42
TEST_SIZE = 0.2
