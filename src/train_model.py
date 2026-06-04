"""Train and evaluate attrition prediction models."""

from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

from src.config import (
    FEATURE_IMPORTANCE_FILE,
    FEATURE_NAMES_FILE,
    LOGISTIC_MODEL_FILE,
    METRICS_FILE,
    MODELS_DIR,
    PROCESSED_DATA_FILE,
    RANDOM_FOREST_MODEL_FILE,
    RANDOM_STATE,
    TARGET_COLUMN,
    TEST_SIZE,
)
from src.preprocessing import prepare_features_target, run_preprocessing


def evaluate_model(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Compute classification metrics and confusion matrix."""
    return {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 4),
        "f1_score": round(f1_score(y_true, y_pred, zero_division=0), 4),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }


def train_models(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
) -> dict:
    """Train Logistic Regression and Random Forest; return metrics."""
    models = {
        "Logistic Regression": Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "clf",
                    LogisticRegression(
                        max_iter=2000,
                        class_weight="balanced",
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }

    results: dict = {}
    trained: dict = {}

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        results[name] = evaluate_model(y_test.values, y_pred)
        trained[name] = model

    return results, trained


def extract_feature_importance(
    model: RandomForestClassifier,
    feature_names: list[str],
) -> pd.DataFrame:
    """Top factors from Random Forest feature importances."""
    importance = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": model.feature_importances_,
        }
    ).sort_values("importance", ascending=False)
    importance["rank"] = range(1, len(importance) + 1)
    return importance


def run_training(verbose: bool = True) -> dict:
    """End-to-end training pipeline."""
    if not PROCESSED_DATA_FILE.exists():
        if verbose:
            print("Processed data not found. Running preprocessing...")
        run_preprocessing(verbose=verbose)

    processed = pd.read_csv(PROCESSED_DATA_FILE)
    X, y, feature_names = prepare_features_target(processed)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    metrics, models = train_models(X_train, X_test, y_train, y_test)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(models["Logistic Regression"], LOGISTIC_MODEL_FILE)
    joblib.dump(models["Random Forest"], RANDOM_FOREST_MODEL_FILE)
    joblib.dump(feature_names, FEATURE_NAMES_FILE)

    rf_importance = extract_feature_importance(
        models["Random Forest"], feature_names
    )
    rf_importance.to_csv(FEATURE_IMPORTANCE_FILE, index=False)

    output = {
        "models": metrics,
        "best_model": "Random Forest",
        "train_size": len(X_train),
        "test_size": len(X_test),
        "top_features": rf_importance.head(10).to_dict(orient="records"),
    }

    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    if verbose:
        print("\nModel Performance Comparison")
        print("-" * 50)
        for name, scores in metrics.items():
            print(f"\n{name}:")
            for key in ("accuracy", "precision", "recall", "f1_score"):
                print(f"  {key}: {scores[key]}")
            print(f"  confusion_matrix: {scores['confusion_matrix']}")
        print(f"\nTop 5 attrition drivers:")
        print(rf_importance.head(5).to_string(index=False))

    return output


if __name__ == "__main__":
    run_training()
