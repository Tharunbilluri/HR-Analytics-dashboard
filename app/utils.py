"""Shared helpers for the Streamlit dashboard."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.analytics import (
    COMPANY_ATTRITION_BASELINE,
    FEATURE_LABELS,
    at_risk_mask,
    attrition_rate,
    estimated_attrition_cost,
)
from app.theme import (
    ACCENT,
    ATTRITION_COLORS,
    ATTRITION_LABELS,
    BAR_SEQUENCE,
    DEPT_COLORS,
    DEPT_SHORT,
    LEAVE,
    OVERTIME_COLORS,
    OVERTIME_LABELS,
    PRIMARY,
    SCALE_ATTRITION,
    SCALE_IMPORTANCE,
    SECONDARY,
    STAY,
    apply_chart_style,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "WA_Fn-UseC_-HR-Employee-Attrition.csv"
METRICS_FILE = PROJECT_ROOT / "models" / "model_metrics.json"
IMPORTANCE_FILE = PROJECT_ROOT / "models" / "feature_importance.csv"


@st.cache_data
def load_employee_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    return df


def load_metrics() -> dict | None:
    if METRICS_FILE.exists():
        with open(METRICS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return None


def load_feature_importance() -> pd.DataFrame | None:
    if IMPORTANCE_FILE.exists():
        return pd.read_csv(IMPORTANCE_FILE)
    return None


def apply_filters(
    df: pd.DataFrame,
    departments: list[str] | None,
    genders: list[str] | None,
    job_roles: list[str] | None,
) -> pd.DataFrame:
    filtered = df.copy()
    if departments:
        filtered = filtered[filtered["Department"].isin(departments)]
    if genders:
        filtered = filtered[filtered["Gender"].isin(genders)]
    if job_roles:
        filtered = filtered[filtered["JobRole"].isin(job_roles)]
    return filtered


def _label_attrition(series: pd.Series) -> pd.Series:
    return series.map(ATTRITION_LABELS).fillna(series)


def _short_dept(name: str) -> str:
    return DEPT_SHORT.get(name, name)


def _metric(col, label: str, value: str, delta: str | None = None, inverse: bool = False):
    col.metric(label, value, delta=delta, delta_color="inverse" if inverse else "normal")


def kpi_overview(df: pd.DataFrame, cost_multiplier: float = 1.5) -> None:
    total = len(df)
    rate = attrition_rate(df)
    left = int((df["Attrition"] == "Yes").sum())
    risk = int(at_risk_mask(df).sum())
    cost = estimated_attrition_cost(df, cost_multiplier)
    delta = f"{rate - COMPANY_ATTRITION_BASELINE:+.1f}% vs co." if total else None

    c1, c2, c3, c4 = st.columns(4)
    _metric(c1, "Employees", f"{total:,}", None)
    _metric(c2, "Attrition rate", f"{rate:.1f}%", delta, inverse=True)
    _metric(
        c3,
        "Est. attrition cost",
        f"${cost / 1_000_000:.2f}M" if cost >= 1_000_000 else f"${cost:,.0f}",
        f"{left:,} exited",
    )
    _metric(c4, "At-risk employees", f"{risk:,}", f"{risk/total*100:.1f}%" if total else None)


def kpi_workforce(df: pd.DataFrame) -> None:
    c1, c2, c3, c4 = st.columns(4)
    _metric(c1, "Headcount", f"{len(df):,}", None)
    _metric(c2, "Avg. monthly salary", f"${df['MonthlyIncome'].mean():,.0f}", None)
    ot_pct = (df["OverTime"] == "Yes").mean() * 100
    _metric(c3, "Overtime rate", f"{ot_pct:.1f}%", None)
    _metric(c4, "Avg. tenure", f"{df['YearsAtCompany'].mean():.1f} yrs", None)


def kpi_insights(df: pd.DataFrame) -> None:
    ot_yes = df[df["OverTime"] == "Yes"]
    ot_no = df[df["OverTime"] == "No"]
    gap = attrition_rate(ot_yes) - attrition_rate(ot_no) if len(ot_yes) and len(ot_no) else 0
    low_sat = df[df["JobSatisfaction"] <= 2]
    low_sat_rate = attrition_rate(low_sat) if len(low_sat) else 0

    c1, c2, c3, c4 = st.columns(4)
    _metric(c1, "Attrition rate", f"{attrition_rate(df):.1f}%", None)
    _metric(c2, "Overtime attrition gap", f"{gap:+.1f} pp", None, inverse=gap > 0)
    _metric(c3, "Low satisfaction attrition", f"{low_sat_rate:.1f}%", f"n={len(low_sat)}")
    _metric(c4, "At-risk employees", f"{int(at_risk_mask(df).sum()):,}", None)


def plot_attrition_distribution(df: pd.DataFrame):
    counts = df["Attrition"].value_counts().reset_index()
    counts.columns = ["Status", "Count"]
    counts["Status"] = _label_attrition(counts["Status"])
    fig = px.pie(
        counts,
        values="Count",
        names="Status",
        title="Who Stayed vs Who Left",
        color="Status",
        color_discrete_map=ATTRITION_COLORS,
        hole=0.45,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        textfont=dict(size=13, color="white"),
        marker=dict(line=dict(color="white", width=2)),
    )
    fig.update_layout(legend=dict(title="Status"))
    return apply_chart_style(fig, height=380)


def plot_attrition_by_department(df: pd.DataFrame):
    dept = (
        df.groupby("Department")["Attrition"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .reset_index(name="Rate")
    )
    dept["Label"] = dept["Department"].map(_short_dept)
    dept["ColorKey"] = dept["Department"]

    fig = px.bar(
        dept,
        x="Label",
        y="Rate",
        title="Attrition Rate by Department",
        color="ColorKey",
        color_discrete_map=DEPT_COLORS,
        text="Rate",
        labels={"Label": "", "Rate": "Attrition %"},
    )
    fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
    fig.update_layout(
        showlegend=False,
        xaxis_title="",
        yaxis_title="Attrition %",
        xaxis_tickangle=0,
    )
    return apply_chart_style(fig, height=420, bottom_margin=48)


def plot_attrition_by_age(df: pd.DataFrame):
    df = df.copy()
    df["Age Group"] = pd.cut(
        df["Age"],
        bins=[17, 25, 35, 45, 55, 65],
        labels=["18-25", "26-35", "36-45", "46-55", "56+"],
    )
    age = (
        df.groupby("Age Group", observed=True)["Attrition"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .reset_index(name="Rate")
    )
    fig = px.bar(
        age,
        x="Age Group",
        y="Rate",
        title="Attrition Rate by Age Group",
        color="Age Group",
        color_discrete_sequence=BAR_SEQUENCE,
        labels={"Rate": "Attrition %"},
    )
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Attrition %")
    return apply_chart_style(fig, height=400)


def plot_attrition_by_salary(df: pd.DataFrame):
    df = df.copy()
    df["Salary Band"] = pd.qcut(
        df["MonthlyIncome"],
        q=4,
        labels=["Low", "Mid-Low", "Mid-High", "High"],
        duplicates="drop",
    )
    sal = (
        df.groupby("Salary Band", observed=True)["Attrition"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .reset_index(name="Rate")
    )
    fig = px.bar(
        sal,
        x="Salary Band",
        y="Rate",
        title="Attrition Rate by Salary Band",
        color="Salary Band",
        color_discrete_sequence=BAR_SEQUENCE,
        labels={"Rate": "Attrition %"},
    )
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Attrition %")
    return apply_chart_style(fig, height=400)


def plot_attrition_overtime(df: pd.DataFrame):
    ot = (
        df.groupby("OverTime")["Attrition"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .reset_index(name="Rate")
    )
    ot["Label"] = ot["OverTime"].map(OVERTIME_LABELS)
    fig = px.bar(
        ot,
        x="Label",
        y="Rate",
        title="Attrition Rate by Overtime",
        color="Label",
        color_discrete_map=OVERTIME_COLORS,
        text="Rate",
        labels={"Rate": "Attrition %"},
    )
    fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Attrition %")
    return apply_chart_style(fig, height=400)


def plot_attrition_job_satisfaction(df: pd.DataFrame):
    js = (
        df.groupby("JobSatisfaction")["Attrition"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .reset_index(name="Rate")
    )
    js["Satisfaction"] = js["JobSatisfaction"].map(
        {1: "Very Low", 2: "Low", 3: "High", 4: "Very High"}
    )
    fig = px.line(
        js,
        x="Satisfaction",
        y="Rate",
        markers=True,
        title="Attrition Rate by Job Satisfaction",
        labels={"Rate": "Attrition %"},
    )
    fig.update_traces(
        line=dict(width=3, color=SECONDARY),
        marker=dict(size=10, color=PRIMARY, line=dict(width=2, color="white")),
    )
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Attrition %")
    return apply_chart_style(fig, height=400, bottom_margin=64)


def plot_attrition_by_job_role(df: pd.DataFrame, min_count: int = 10):
    roles = (
        df.groupby("JobRole")["Attrition"]
        .agg(rate=lambda x: (x == "Yes").mean() * 100, count="count")
        .reset_index()
    )
    roles = roles[roles["count"] >= min_count].sort_values("rate", ascending=True).tail(10)
    roles["Label"] = roles["JobRole"].str.replace(" ", "<br>", regex=False)
    fig = px.bar(
        roles,
        x="rate",
        y="JobRole",
        orientation="h",
        title="Attrition Rate by Job Role (min 10 employees)",
        color="rate",
        color_continuous_scale=SCALE_ATTRITION,
        text="rate",
        labels={"rate": "Attrition %", "JobRole": ""},
    )
    fig.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
    fig.update_layout(coloraxis_showscale=False, showlegend=False)
    return apply_chart_style(fig, height=440)


def plot_risk_segments(df: pd.DataFrame):
    tmp = df.copy()
    tmp["Segment"] = at_risk_mask(tmp).map({True: "At-risk profile", False: "Other"})
    seg = (
        tmp.groupby(["Segment", "Attrition"])
        .size()
        .unstack(fill_value=0)
        .rename(columns={"No": "Stayed", "Yes": "Left"})
        .reset_index()
    )
    for col in ("Stayed", "Left"):
        if col not in seg.columns:
            seg[col] = 0
    fig = px.bar(
        seg,
        x="Segment",
        y=["Stayed", "Left"],
        title="Headcount: At-Risk Profile vs Others",
        color_discrete_map={"Stayed": STAY, "Left": LEAVE},
        labels={"value": "Employees", "variable": "Status"},
        barmode="stack",
    )
    fig.update_layout(legend_title_text="", xaxis_title="", yaxis_title="Employees")
    return apply_chart_style(fig, height=380)


def plot_education_attrition(df: pd.DataFrame):
    edu = (
        df.groupby("EducationField")["Attrition"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .reset_index(name="Rate")
        .sort_values("Rate", ascending=True)
        .tail(8)
    )
    fig = px.bar(
        edu,
        x="Rate",
        y="EducationField",
        orientation="h",
        title="Attrition Rate by Education Field",
        color="Rate",
        color_continuous_scale=SCALE_ATTRITION,
        text="Rate",
        labels={"Rate": "Attrition %", "EducationField": ""},
    )
    fig.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
    fig.update_layout(coloraxis_showscale=False, showlegend=False)
    return apply_chart_style(fig, height=420)


def plot_feature_importance(importance_df: pd.DataFrame, top_n: int = 10):
    top = importance_df.head(top_n).sort_values("importance").copy()
    top["label"] = top["feature"].map(lambda f: FEATURE_LABELS.get(f, f))
    fig = px.bar(
        top,
        x="importance",
        y="label",
        orientation="h",
        title=f"Top {top_n} Model Drivers (Random Forest)",
        color="importance",
        color_continuous_scale=SCALE_IMPORTANCE,
        labels={"importance": "Impact score", "label": ""},
    )
    fig.update_layout(coloraxis_showscale=False, showlegend=False)
    return apply_chart_style(fig, height=420)


def plot_income_by_department(df: pd.DataFrame):
    fig = go.Figure()
    for i, dept in enumerate(sorted(df["Department"].unique())):
        subset = df[df["Department"] == dept]
        color = DEPT_COLORS.get(dept, BAR_SEQUENCE[i % len(BAR_SEQUENCE)])
        fig.add_trace(
            go.Box(
                y=subset["MonthlyIncome"],
                name=_short_dept(dept),
                marker_color=color,
                line_color=PRIMARY,
                fillcolor=color,
                opacity=0.8,
            )
        )
    fig.update_layout(
        title="Monthly Salary by Department",
        yaxis_title="Monthly Income ($)",
        xaxis_title="",
        showlegend=False,
    )
    return apply_chart_style(fig, height=420)


def plot_attrition_risk_matrix(df: pd.DataFrame):
    """Executive bubble: attrition % vs department size."""
    g = (
        df.groupby("Department")
        .agg(
            headcount=("Attrition", "count"),
            attrition_pct=("Attrition", lambda x: (x == "Yes").mean() * 100),
        )
        .reset_index()
    )
    g["Label"] = g["Department"].map(_short_dept)
    fig = px.scatter(
        g,
        x="headcount",
        y="attrition_pct",
        size="headcount",
        color="attrition_pct",
        text="Label",
        title="Attrition Risk Matrix",
        color_continuous_scale=SCALE_ATTRITION,
        labels={
            "headcount": "Department Size (Employees)",
            "attrition_pct": "Attrition %",
        },
        size_max=60,
    )
    fig.update_traces(
        textposition="top center",
        marker=dict(line=dict(width=1, color="white")),
    )
    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_title="Department Size (Employees)",
        yaxis_title="Attrition %",
    )
    return apply_chart_style(fig, height=400)
