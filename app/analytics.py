"""Business analytics: dynamic insights, risk segmentation, and HR guidance."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

COMPANY_ATTRITION_BASELINE = 16.1
DEFAULT_COST_MULTIPLIER_MONTHS = 1.5  # industry proxy: 1.5× monthly salary per exit

FEATURE_LABELS = {
    "MonthlyIncome": "Monthly income",
    "Age": "Age",
    "TotalWorkingYears": "Total working years",
    "DailyRate": "Daily rate",
    "OverTime": "Overtime",
    "YearsAtCompany": "Years at company",
    "HourlyRate": "Hourly rate",
    "DistanceFromHome": "Distance from home",
    "MonthlyRate": "Monthly rate",
    "YearsWithCurrManager": "Years with current manager",
    "JobSatisfaction": "Job satisfaction",
    "EnvironmentSatisfaction": "Environment satisfaction",
    "WorkLifeBalance": "Work-life balance",
    "StockOptionLevel": "Stock option level",
    "JobInvolvement": "Job involvement",
    "YearsSinceLastPromotion": "Years since last promotion",
    "NumCompaniesWorked": "Companies worked",
    "JobLevel": "Job level",
    "PercentSalaryHike": "Salary hike %",
}

RISK_RULES = {
    "overtime": ("OverTime", "Yes"),
    "low_satisfaction": ("JobSatisfaction", lambda v: v <= 2),
    "short_tenure": ("YearsAtCompany", lambda v: v < 3),
    "no_promotion": ("YearsSinceLastPromotion", lambda v: v >= 4),
    "low_work_life": ("WorkLifeBalance", lambda v: v <= 2),
}


DEPT_DISPLAY = {
    "Human Resources": "HR",
    "Research & Development": "R&D",
    "Sales": "Sales",
}


@dataclass
class FilterContext:
    total_raw: int
    total_filtered: int
    departments: list[str]
    genders: list[str]
    job_roles: list[str]
    all_departments: list[str]
    all_genders: list[str]
    all_job_roles: list[str]

    def _dept_label(self, name: str) -> str:
        return DEPT_DISPLAY.get(name, name)

    def departments_display(self) -> str:
        order = {d: i for i, d in enumerate(self.all_departments)}
        labels = [self._dept_label(d) for d in sorted(self.departments, key=lambda x: order.get(x, 99))]
        return ", ".join(labels)

    def departments_all_selected(self) -> bool:
        return set(self.departments) >= set(self.all_departments)

    def genders_all_selected(self) -> bool:
        return set(self.genders) >= set(self.all_genders)

    def job_roles_all_selected(self) -> bool:
        return set(self.job_roles) >= set(self.all_job_roles)

    def is_narrowed(self) -> bool:
        return (
            not self.departments_all_selected()
            or not self.genders_all_selected()
            or not self.job_roles_all_selected()
            or self.total_filtered < self.total_raw
        )

    def filter_reason_suffix(self) -> str:
        """Human-readable filter label, e.g. 'Sales only' or 'HR, R&D · Female'."""
        parts: list[str] = []
        if not self.departments_all_selected():
            if len(self.departments) == 1:
                parts.append(f"{self._dept_label(self.departments[0])} only")
            else:
                parts.append(self.departments_display())
        if not self.genders_all_selected():
            if len(self.genders) == 1:
                parts.append(f"{self.genders[0]} only")
            else:
                parts.append(f"{len(self.genders)} genders")
        if not self.job_roles_all_selected():
            n = len(self.job_roles)
            parts.append(f"{n} job role{'s' if n != 1 else ''}")
        return " · ".join(parts)

    def summary(self, filtered_rate: float, company_rate: float = COMPANY_ATTRITION_BASELINE) -> str:
        parts = [f"**{self.total_filtered:,}** employees"]
        if self.total_filtered != self.total_raw:
            parts.append(f"(of {self.total_raw:,} total)")
        parts.append(
            f"Attrition **{filtered_rate:.1f}%** (company baseline **{company_rate:.1f}%**)"
        )
        return " · ".join(parts)


def attrition_rate(df: pd.DataFrame) -> float:
    if len(df) == 0:
        return 0.0
    return (df["Attrition"] == "Yes").mean() * 100


def at_risk_mask(df: pd.DataFrame) -> pd.Series:
    """HR rule-based risk: overtime + low satisfaction + short tenure."""
    return (
        (df["OverTime"] == "Yes")
        & (df["JobSatisfaction"] <= 2)
        & (df["YearsAtCompany"] < 3)
    )


def at_risk_stats(df: pd.DataFrame) -> dict:
    mask = at_risk_mask(df)
    n = int(mask.sum())
    total = len(df)
    return {
        "count": n,
        "pct": (n / total * 100) if total else 0.0,
        "mask": mask,
    }


def risk_tier(probability_leave: float) -> tuple[str, str]:
    pct = probability_leave * 100
    if pct >= 55:
        return "High", "Immediate retention review recommended."
    if pct >= 30:
        return "Medium", "Monitor closely and address drivers within 30 days."
    return "Low", "Standard engagement practices are sufficient."


def format_insight(finding: str, action: str) -> str:
    return (
        f"<strong>Finding:</strong> {finding}<br>"
        f"<strong>Action:</strong> {action}"
    )


def insight_distribution(df: pd.DataFrame) -> str:
    rate = attrition_rate(df)
    left = int((df["Attrition"] == "Yes").sum())
    stayed = len(df) - left
    delta = rate - COMPANY_ATTRITION_BASELINE
    trend = "above" if delta > 0.5 else "below" if delta < -0.5 else "near"
    return format_insight(
        f"{rate:.1f}% attrition ({left} left, {stayed} stayed) — {trend} the "
        f"{COMPANY_ATTRITION_BASELINE:.1f}% company baseline.",
        "Prioritize stay interviews for employees in high-risk segments shown below.",
    )


def insight_department(df: pd.DataFrame) -> str:
    dept = (
        df.groupby("Department")["Attrition"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .sort_values(ascending=False)
    )
    if dept.empty:
        return format_insight("No data for selected filters.", "Adjust filters to continue.")
    top = dept.index[0]
    low = dept.index[-1]
    return format_insight(
        f"{top} has the highest attrition at {dept.iloc[0]:.1f}% vs "
        f"{low} at {dept.iloc[-1]:.1f}%.",
        f"Run a targeted retention plan in {top} (compensation, career path, manager support).",
    )


def insight_overtime(df: pd.DataFrame) -> str:
    ot = df.groupby("OverTime")["Attrition"].apply(lambda x: (x == "Yes").mean() * 100)
    if "Yes" not in ot.index or "No" not in ot.index:
        return format_insight("Insufficient overtime groups in selection.", "Broaden filters.")
    gap = ot["Yes"] - ot["No"]
    return format_insight(
        f"Overtime attrition is {ot['Yes']:.1f}% vs {ot['No']:.1f}% without overtime "
        f"({gap:+.1f} pp gap).",
        "Cap overtime hours and rebalance workload in teams with sustained overtime.",
    )


def insight_age(df: pd.DataFrame) -> str:
    tmp = df.copy()
    tmp["Age Group"] = pd.cut(
        tmp["Age"],
        bins=[17, 25, 35, 45, 55, 65],
        labels=["18-25", "26-35", "36-45", "46-55", "56+"],
    )
    rates = (
        tmp.groupby("Age Group", observed=True)["Attrition"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .sort_values(ascending=False)
    )
    if rates.empty:
        return format_insight("No age data available.", "Adjust filters.")
    top = rates.index[0]
    return format_insight(
        f"Highest attrition is in the {top} band at {rates.iloc[0]:.1f}%.",
        "Offer mentorship and career clarity for early-career employees in that band.",
    )


def insight_salary(df: pd.DataFrame) -> str:
    tmp = df.copy()
    tmp["Band"] = pd.qcut(
        tmp["MonthlyIncome"], q=4, labels=["Low", "Mid-Low", "Mid-High", "High"], duplicates="drop"
    )
    rates = (
        tmp.groupby("Band", observed=True)["Attrition"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .sort_values(ascending=False)
    )
    if rates.empty:
        return format_insight("Not enough salary variation in selection.", "Adjust filters.")
    return format_insight(
        f"{rates.index[0]} salary band shows {rates.iloc[0]:.1f}% attrition — "
        f"highest among bands.",
        "Benchmark pay for the low and mid bands against market rates in the same role.",
    )


def insight_satisfaction(df: pd.DataFrame) -> str:
    rates = (
        df.groupby("JobSatisfaction")["Attrition"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .sort_index()
    )
    if len(rates) < 2:
        return format_insight("Limited satisfaction data.", "Expand filter selection.")
    low = rates.index.min()
    high = rates.index.max()
    return format_insight(
        f"Attrition at satisfaction {low}/4 is {rates.loc[low]:.1f}% vs "
        f"{rates.loc[high]:.1f}% at {high}/4.",
        "Managers should run monthly 1:1s for employees with satisfaction ≤ 2.",
    )


def insight_job_roles(df: pd.DataFrame, min_count: int = 10) -> str:
    roles = (
        df.groupby("JobRole")["Attrition"]
        .agg(["mean", "count"])
        .rename(columns={"mean": "rate"})
    )
    roles = roles[roles["count"] >= min_count].sort_values("rate", ascending=False)
    if roles.empty:
        return format_insight(
            "No roles meet minimum headcount for comparison.",
            "Lower the filter scope or review department-level attrition instead.",
        )
    top = roles.index[0]
    return format_insight(
        f"{top} has the highest attrition at {roles.iloc[0]['rate']*100:.1f}% "
        f"(n={int(roles.iloc[0]['count'])}).",
        f"Review compensation and progression paths for {top} within 60 days.",
    )


def insight_at_risk(df: pd.DataFrame) -> str:
    stats = at_risk_stats(df)
    return format_insight(
        f"{stats['count']} employees ({stats['pct']:.1f}%) match the at-risk profile: "
        "overtime + low job satisfaction + under 3 years tenure.",
        "Assign HR business partners to this cohort for stay interviews this quarter.",
    )


def detect_risk_flags(employee: dict) -> list[str]:
    flags = []
    if employee.get("OverTime") == "Yes":
        flags.append("overtime")
    if employee.get("JobSatisfaction", 3) <= 2:
        flags.append("low_satisfaction")
    if employee.get("YearsAtCompany", 5) < 3:
        flags.append("short_tenure")
    if employee.get("YearsSinceLastPromotion", 0) >= 4:
        flags.append("no_promotion")
    if employee.get("WorkLifeBalance", 3) <= 2:
        flags.append("low_work_life")
    if employee.get("EnvironmentSatisfaction", 3) <= 2:
        flags.append("low_environment")
    return flags


RECOMMENDATIONS = {
    "overtime": "Reduce overtime load or add headcount; review burnout risk within 2 weeks.",
    "low_satisfaction": "Conduct a stay interview and identify blockers with the direct manager.",
    "short_tenure": "Assign a mentor and clarify 12-month career path milestones.",
    "no_promotion": "Discuss promotion timeline and development plan at next review cycle.",
    "low_work_life": "Evaluate flexible scheduling or workload redistribution.",
    "low_environment": "Assess workspace, tools, and team dynamics with HR partner.",
    "high_probability": "Escalate to retention program: compensation review + succession backup plan.",
    "medium_probability": "Add to quarterly flight-risk watchlist with manager follow-up.",
}


def hr_recommendations(employee: dict, probability_leave: float) -> list[str]:
    recs = []
    flags = detect_risk_flags(employee)
    for flag in flags:
        if flag in RECOMMENDATIONS:
            recs.append(RECOMMENDATIONS[flag])

    tier, _ = risk_tier(probability_leave)
    if tier == "High" and RECOMMENDATIONS["high_probability"] not in recs:
        recs.append(RECOMMENDATIONS["high_probability"])
    elif tier == "Medium":
        recs.append(RECOMMENDATIONS["medium_probability"])

    if not recs:
        recs.append("Maintain regular check-ins; no immediate escalation required.")
    return recs[:5]


def key_drivers_for_employee(
    employee: dict,
    importance_df: pd.DataFrame | None,
    reference_df: pd.DataFrame,
) -> list[tuple[str, str]]:
    """Top drivers as human-readable factors with context."""
    drivers: list[tuple[str, str]] = []

    if employee.get("OverTime") == "Yes":
        ot_rate = attrition_rate(reference_df[reference_df["OverTime"] == "Yes"])
        drivers.append(("Overtime", f"Overtime group attrition is {ot_rate:.1f}% in dataset"))

    if employee.get("JobSatisfaction", 3) <= 2:
        drivers.append(("Low job satisfaction", "Score ≤ 2 is linked to higher turnover"))

    med_income = reference_df["MonthlyIncome"].median()
    if employee.get("MonthlyIncome", med_income) < med_income:
        drivers.append(
            (
                "Below-median pay",
                f"Income ${employee['MonthlyIncome']:,} vs median ${med_income:,.0f}",
            )
        )

    if employee.get("YearsAtCompany", 5) < 3:
        drivers.append(("Short tenure", "Under 3 years at company"))

    if importance_df is not None:
        for _, row in importance_df.head(5).iterrows():
            feat = row["feature"]
            if feat in employee and len(drivers) < 5:
                label = FEATURE_LABELS.get(feat, feat)
                val = employee[feat]
                if label not in [d[0] for d in drivers]:
                    drivers.append((label, f"Model weight: {row['importance']:.3f} · value: {val}"))

    return drivers[:5]


def estimated_attrition_cost(
    df: pd.DataFrame,
    multiplier_months: float = DEFAULT_COST_MULTIPLIER_MONTHS,
) -> float:
    """Proxy cost = sum(monthly income of leavers) × multiplier (months of pay)."""
    leavers = df[df["Attrition"] == "Yes"]
    if leavers.empty:
        return 0.0
    return float(leavers["MonthlyIncome"].sum() * multiplier_months)


def at_risk_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Actionable worklist for HR."""
    mask = at_risk_mask(df)
    cols = [
        "Department",
        "JobRole",
        "Age",
        "Gender",
        "MonthlyIncome",
        "YearsAtCompany",
        "OverTime",
        "JobSatisfaction",
        "Attrition",
    ]
    out = df.loc[mask, cols].copy()
    out = out.rename(
        columns={
            "JobRole": "Job Role",
            "MonthlyIncome": "Monthly Income",
            "YearsAtCompany": "Years at Company",
            "OverTime": "Overtime",
            "JobSatisfaction": "Job Satisfaction",
            "Attrition": "Historical Outcome",
        }
    )
    out["Historical Outcome"] = out["Historical Outcome"].map({"Yes": "Left", "No": "Stayed"})
    return out.sort_values(["Department", "Job Role"])


def department_risk_table(df: pd.DataFrame) -> pd.DataFrame:
    """Department attrition with headcount for workforce page."""
    g = (
        df.groupby("Department")
        .agg(
            headcount=("Attrition", "count"),
            attrition_pct=("Attrition", lambda x: (x == "Yes").mean() * 100),
            avg_salary=("MonthlyIncome", "mean"),
        )
        .reset_index()
    )
    g["priority_score"] = g["attrition_pct"] * g["headcount"] / 100
    return g.sort_values("priority_score", ascending=False)


def format_cost_display(amount: float) -> str:
    if amount >= 1_000_000:
        return f"${amount / 1_000_000:.2f}M"
    return f"${amount:,.0f}"


def _overtime_gap(df: pd.DataFrame) -> float:
    ot = df.groupby("OverTime")["Attrition"].apply(lambda x: (x == "Yes").mean() * 100)
    if "Yes" in ot.index and "No" in ot.index:
        return float(ot["Yes"] - ot["No"])
    return 0.0


def prioritized_actions(df: pd.DataFrame) -> list[str]:
    """Top 3 executive priorities (plain language)."""
    if df.empty:
        return []

    priorities: list[str] = []
    ot_gap = _overtime_gap(df)
    if ot_gap > 3:
        priorities.append("Reduce overtime exposure in high-risk teams")

    dept = (
        df.groupby("Department")["Attrition"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .sort_values(ascending=False)
    )
    if not dept.empty:
        top = dept.index[0]
        if top == "Sales":
            priorities.append("Execute Sales retention initiative")
        else:
            priorities.append(f"Execute {top} retention initiative")

    risk_n = int(at_risk_mask(df).sum())
    if risk_n > 0:
        priorities.append(
            f"Complete stay interviews for all {risk_n} at-risk employees within 14 days"
        )

    return priorities[:3]


def _business_impact_metrics(
    df: pd.DataFrame,
    cost_multiplier: float = DEFAULT_COST_MULTIPLIER_MONTHS,
) -> tuple[int, str, float]:
    ot_n = int((df["OverTime"] == "Yes").sum())
    risk_n = int(at_risk_mask(df).sum())
    cost = estimated_attrition_cost(df, cost_multiplier)
    left = max(int((df["Attrition"] == "Yes").sum()), 1)
    avg_exit_cost = cost / left
    ot_preventable = max(0, round(ot_n * 0.05))
    preventable_exits = ot_preventable + risk_n
    savings = preventable_exits * avg_exit_cost
    return preventable_exits, format_cost_display(savings), cost_multiplier


def expected_business_impact_text(
    df: pd.DataFrame,
    cost_multiplier: float = DEFAULT_COST_MULTIPLIER_MONTHS,
    html: bool = True,
) -> str:
    """Scenario narrative for leadership."""
    preventable, savings_fmt, mult = _business_impact_metrics(df, cost_multiplier)
    if html:
        return (
            f"If overtime-related attrition is reduced by <strong>5 percentage points</strong> and the "
            f"at-risk cohort is retained, the organization could prevent approximately "
            f"<strong>{preventable:,}</strong> avoidable exits annually and reduce replacement "
            f"costs by an estimated <strong>{savings_fmt}</strong> "
            f"(proxy based on {mult:.1f}× monthly salary per exit)."
        )
    return (
        f"If overtime-related attrition is reduced by 5 percentage points and the "
        f"at-risk cohort is retained, the organization could prevent approximately "
        f"{preventable:,} avoidable exits annually and reduce replacement "
        f"costs by an estimated {savings_fmt} "
        f"(proxy based on {mult:.1f}× monthly salary per exit)."
    )


def filter_scope_header_html(ctx: FilterContext | None, employee_count: int) -> str:
    """Scope block above executive bullets — reflects sidebar filters."""
    if ctx is None:
        return (
            f'<p class="filter-scope"><strong>Employees in View:</strong> {employee_count:,}</p>'
        )

    if not ctx.is_narrowed():
        return f"""
        <p class="filter-scope" style="margin:0.35rem 0 0.75rem 0;line-height:1.65;">
        <strong>Selected Departments:</strong><br>
        <span style="color:#4A5D73;">{ctx.departments_display()}</span><br>
        <strong>Employees in View:</strong> {employee_count:,}
        </p>
        """

    reason = ctx.filter_reason_suffix()
    suffix = f" ({reason})" if reason else ""
    return f"""
    <p class="filter-scope" style="margin:0.35rem 0 0.75rem 0;line-height:1.65;">
    <strong>Filtered View:</strong> {employee_count:,} employees{suffix}
    </p>
    """


def executive_summary_section_html(
    df: pd.DataFrame,
    ctx: FilterContext | None = None,
    df_company: pd.DataFrame | None = None,
    cost_multiplier: float = DEFAULT_COST_MULTIPLIER_MONTHS,
) -> str:
    """Filter-aware executive bullets (numbers from current selection only)."""
    if df.empty:
        return (
            '<div class="executive-summary"><strong>Executive Summary</strong>'
            "<p>No employees match the current filters.</p></div>"
        )

    rate = attrition_rate(df)
    total = len(df)
    left = int((df["Attrition"] == "Yes").sum())
    risk = at_risk_stats(df)
    cost = estimated_attrition_cost(df, cost_multiplier)
    ot_gap = _overtime_gap(df)

    dept = (
        df.groupby("Department")["Attrition"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .sort_values(ascending=False)
    )
    top_dept = dept.index[0] if len(dept) else "N/A"
    top_dept_rate = dept.iloc[0] if len(dept) else 0.0

    scope_header = filter_scope_header_html(ctx, total)
    baseline_line = ""
    if df_company is not None and total != len(df_company):
        baseline_line = (
            f"<li><strong>Company baseline:</strong> {attrition_rate(df_company):.1f}% attrition "
            f"across {len(df_company):,} employees "
            f"(Δ <strong>{rate - attrition_rate(df_company):+.1f} pp</strong> in this view)</li>"
        )

    ot_line = (
        f"<li><strong>Overtime</strong> increases attrition by <strong>{ot_gap:.1f} percentage points</strong> "
        f"within this selection</li>"
        if ot_gap > 0
        else ""
    )

    return f"""
    <div class="executive-summary">
    <strong>Executive Summary</strong>
    {scope_header}
    <ul style="margin:0.5rem 0 0 0;padding-left:1.2rem;line-height:1.75;">
    <li><strong>Attrition Rate:</strong> {rate:.1f}% ({left:,} employees exited)</li>
    <li><strong>Employees:</strong> {total:,}</li>
    <li><strong>Estimated Attrition Cost:</strong> {format_cost_display(cost)}</li>
    <li><strong>Highest Risk Department:</strong> {top_dept} ({top_dept_rate:.1f}% attrition)</li>
    {ot_line}
    <li><strong>At-Risk Employees:</strong> {risk['count']:,} for immediate retention intervention</li>
    {baseline_line}
    </ul>
    </div>
    """


def business_impact_section_html(
    df: pd.DataFrame,
    cost_multiplier: float = DEFAULT_COST_MULTIPLIER_MONTHS,
) -> str:
    if df.empty:
        return ""
    return f"""
    <div class="executive-summary" style="margin-top:0.75rem;">
    <strong>Expected Business Impact</strong>
    <p style="margin:0.5rem 0 0 0;line-height:1.6;">{expected_business_impact_text(df, cost_multiplier)}</p>
    </div>
    """


def top_priorities_section_html(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    priorities = prioritized_actions(df)
    priority_html = "".join(f"<li>{p}</li>" for p in priorities)
    return f"""
    <div class="actions-panel" style="margin-top:0.75rem;">
    <strong>Top Priorities</strong>
    <ol style="margin:0.5rem 0 0 0;padding-left:1.2rem;line-height:1.75;">{priority_html}</ol>
    </div>
    """


def executive_brief_html(
    df: pd.DataFrame,
    df_company: pd.DataFrame | None = None,
    cost_multiplier: float = DEFAULT_COST_MULTIPLIER_MONTHS,
    ctx: FilterContext | None = None,
) -> str:
    """Full brief (legacy combined block)."""
    return (
        executive_summary_section_html(df, ctx, df_company, cost_multiplier)
        + business_impact_section_html(df, cost_multiplier)
        + top_priorities_section_html(df)
    )


def executive_summary_html(
    df: pd.DataFrame,
    df_company: pd.DataFrame,
    cost_multiplier: float = DEFAULT_COST_MULTIPLIER_MONTHS,
) -> str:
    """Alias for executive brief (backward compatible)."""
    return executive_brief_html(df, df_company, cost_multiplier)


def model_selection_rationale() -> str:
    return (
        "**Production model: Random Forest** — best accuracy (82.7%) for workforce screening. "
        "**Logistic Regression** — higher recall on leavers (76.6%) when catching flight risk matters more "
        "than avoiding false alarms. Use RF for prioritization lists; consider LR when missing leavers is costly."
    )


def build_executive_report_markdown(
    df: pd.DataFrame,
    ctx: FilterContext | None = None,
    df_company: pd.DataFrame | None = None,
    cost_multiplier: float = DEFAULT_COST_MULTIPLIER_MONTHS,
) -> str:
    """Downloadable executive report for the current filter selection."""
    rate = attrition_rate(df)
    total = len(df)
    left = int((df["Attrition"] == "Yes").sum())
    cost = estimated_attrition_cost(df, cost_multiplier)
    risk = at_risk_stats(df)
    ot_gap = _overtime_gap(df)
    dept = (
        df.groupby("Department")["Attrition"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .sort_values(ascending=False)
    )
    top_dept = dept.index[0] if len(dept) else "N/A"
    top_rate = dept.iloc[0] if len(dept) else 0.0

    scope_lines: list[str] = []
    if ctx is not None:
        if not ctx.is_narrowed():
            scope_lines = [
                f"- **Selected departments:** {ctx.departments_display()}",
                f"- **Employees in view:** {total:,}",
            ]
        else:
            reason = ctx.filter_reason_suffix()
            scope_lines = [
                f"- **Filtered view:** {total:,} employees"
                + (f" ({reason})" if reason else ""),
            ]
        if ctx.total_filtered != ctx.total_raw:
            scope_lines.append(f"- **Company total:** {ctx.total_raw:,} employees")

    lines = [
        "# HR Attrition — Executive Report",
        "",
        "## Scope",
        *scope_lines,
        "",
        "## Executive Summary",
        f"- **Attrition rate:** {rate:.1f}% ({left:,} employees exited)",
        f"- **Employees:** {total:,}",
        f"- **Estimated attrition cost:** {format_cost_display(cost)} "
        f"(multiplier {cost_multiplier:.1f}× monthly salary)",
        f"- **Highest risk department:** {top_dept} ({top_rate:.1f}% attrition)",
        f"- **Overtime** increases attrition by {ot_gap:.1f} percentage points in this selection",
        f"- **At-risk employees:** {risk['count']:,} for immediate retention intervention",
    ]
    if df_company is not None and total != len(df_company):
        lines.append(
            f"- **Company baseline:** {attrition_rate(df_company):.1f}% attrition "
            f"(Δ {rate - attrition_rate(df_company):+.1f} pp vs this view)"
        )
    lines.extend(
        [
            "",
            "## Expected Business Impact",
            expected_business_impact_text(df, html=False),
            "",
            "## Top Priorities",
        ]
    )
    for i, p in enumerate(prioritized_actions(df), 1):
        lines.append(f"{i}. {p}")

    lines.extend(
        [
            "",
            "## Department attrition",
        ]
    )
    for dept, r in dept.items():
        lines.append(f"- {dept}: {r:.1f}%")

    lines.extend(
        [
            "",
            "## Model note",
            model_selection_rationale().replace("**", ""),
            "",
            "*IBM HR Attrition dataset — synthetic data for portfolio demonstration.*",
            "",
            "Built with Python, SQL, Scikit-Learn, Plotly, and Streamlit",
            "Author: Tharun Billuri",
        ]
    )
    return "\n".join(lines)


def build_executive_summary_markdown(df: pd.DataFrame) -> str:
    """Alias for full-company report export."""
    return build_executive_report_markdown(df)
