# Analytics & Modeling Decisions

## Data processing

- **Dropped columns:** `EmployeeNumber`, `EmployeeCount`, `Over18`, `StandardHours` — ID or constant fields add no predictive value.
- **No imputation:** Dataset has zero missing values after load.
- **Label encoding:** Categorical features encoded for sklearn; encoders persisted for consistent inference.

## Train / test split

- **80/20 stratified split** on `Attrition` to preserve ~16% positive class in both sets.
- **Random state 42** for reproducibility.

## Class imbalance

- Both models use **`class_weight='balanced'`** so the minority "leave" class is not ignored.
- **No SMOTE** — kept pipeline simple; balanced weights sufficient for portfolio scope.

## Model selection

| Model | Strength | Weakness | When to use |
|-------|----------|----------|-------------|
| **Random Forest** | Accuracy 82.7% | Recall on leavers 25.5% | Default screening — fewer false alarms |
| **Logistic Regression** | Recall on leavers 76.6% | Lower accuracy 75.2% | When catching leavers matters most |

**Production default:** Random Forest (`models/random_forest.joblib`).

## At-risk segmentation (rule-based)

Separate from ML probability:

- Overtime = Yes  
- Job satisfaction ≤ 2  
- Tenure &lt; 3 years  

**Why:** Explainable to HR without model scores; produces a small actionable cohort (~39 employees).

## Attrition cost proxy

- **Formula:** Sum of leavers' monthly income × multiplier (default 1.5 months of salary).
- **Not a financial audit** — illustrative for executive storytelling; assumption shown in UI slider.

## Filters vs prediction

- Sidebar filters drive **analytics pages only**.
- **Predict** uses the full trained model on user input — avoids training-serving skew from partial filter subsets.
