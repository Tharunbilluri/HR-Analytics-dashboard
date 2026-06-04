"""
HR Analytics Dashboard — Employee Attrition Analysis & Prediction
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.analytics import (  # noqa: E402
    DEFAULT_COST_MULTIPLIER_MONTHS,
    FilterContext,
    at_risk_dataframe,
    attrition_rate,
    build_executive_report_markdown,
    department_risk_table,
    business_impact_section_html,
    executive_summary_section_html,
    hr_recommendations,
    top_priorities_section_html,
    insight_age,
    insight_at_risk,
    insight_department,
    insight_distribution,
    insight_job_roles,
    insight_overtime,
    insight_salary,
    insight_satisfaction,
    key_drivers_for_employee,
    model_selection_rationale,
    risk_tier,
)
from app.theme import (  # noqa: E402
    GAUGE_HIGH,
    GAUGE_LOW,
    GAUGE_MID,
    LEAVE,
    PAGES,
    SCALE_ATTRITION,
    STAY,
    apply_chart_style,
    render_app_footer,
    streamlit_custom_css,
)
from app.utils import (  # noqa: E402
    apply_filters,
    kpi_insights,
    kpi_overview,
    kpi_workforce,
    load_employee_data,
    load_feature_importance,
    load_metrics,
    plot_attrition_by_age,
    plot_attrition_by_department,
    plot_attrition_by_job_role,
    plot_attrition_by_salary,
    plot_attrition_distribution,
    plot_attrition_job_satisfaction,
    plot_attrition_overtime,
    plot_education_attrition,
    plot_feature_importance,
    plot_attrition_risk_matrix,
    plot_income_by_department,
    plot_risk_segments,
)
from src.predict import predict_attrition  # noqa: E402

st.set_page_config(
    page_title="HR Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(streamlit_custom_css(), unsafe_allow_html=True)

PREDICT_PRESETS = {
    "Custom (manual entry)": None,
    "High risk — Sales + overtime": {
        "Age": 28,
        "BusinessTravel": "Travel_Frequently",
        "Department": "Sales",
        "JobRole": "Sales Executive",
        "OverTime": "Yes",
        "JobSatisfaction": 1,
        "EnvironmentSatisfaction": 2,
        "WorkLifeBalance": 2,
        "YearsAtCompany": 2,
        "MonthlyIncome": 4500,
    },
    "Stable — R&D tenured": {
        "Age": 42,
        "BusinessTravel": "Travel_Rarely",
        "Department": "Research & Development",
        "JobRole": "Research Scientist",
        "OverTime": "No",
        "JobSatisfaction": 4,
        "EnvironmentSatisfaction": 3,
        "WorkLifeBalance": 3,
        "YearsAtCompany": 8,
        "MonthlyIncome": 7500,
    },
}


def render_insight(html: str) -> None:
    st.markdown(f'<div class="insight-box">{html}</div>', unsafe_allow_html=True)


def render_filter_banner(ctx: FilterContext, df_filtered: pd.DataFrame) -> None:
    rate = attrition_rate(df_filtered)
    st.markdown(
        f'<p class="filter-banner">{ctx.summary(rate)} · Filters apply to analytics pages</p>',
        unsafe_allow_html=True,
    )


def sidebar_filters(df: pd.DataFrame) -> tuple[pd.DataFrame, FilterContext]:
    st.sidebar.markdown("**Filters**")
    all_depts = sorted(df["Department"].unique())
    all_genders = sorted(df["Gender"].unique())

    if st.sidebar.button("Reset filters", use_container_width=True):
        for key in ("filter_dept", "filter_role", "filter_gender"):
            st.session_state.pop(key, None)
        st.rerun()

    departments = st.sidebar.multiselect(
        "Department",
        options=all_depts,
        default=all_depts,
        key="filter_dept",
    )
    role_pool = df[df["Department"].isin(departments)] if departments else df
    all_roles = sorted(role_pool["JobRole"].unique())
    job_roles = st.sidebar.multiselect(
        "Job role",
        options=all_roles,
        default=all_roles,
        key="filter_role",
    )
    genders = st.sidebar.multiselect(
        "Gender",
        options=all_genders,
        default=all_genders,
        key="filter_gender",
    )

    filtered = apply_filters(df, departments, genders, job_roles)
    ctx = FilterContext(
        total_raw=len(df),
        total_filtered=len(filtered),
        departments=departments or [],
        genders=genders or [],
        job_roles=job_roles or [],
        all_departments=all_depts,
        all_genders=all_genders,
        all_job_roles=all_roles,
    )
    return filtered, ctx


def render_executive_downloads(
    df: pd.DataFrame,
    ctx: FilterContext,
    df_company: pd.DataFrame,
    cost_multiplier: float,
) -> None:
    worklist = at_risk_dataframe(df)
    report = build_executive_report_markdown(df, ctx, df_company, cost_multiplier)
    slug = "filtered" if ctx.is_narrowed() else "company"
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "⬇ Download Executive Report",
            report.encode("utf-8"),
            file_name=f"executive_report_{slug}.md",
            mime="text/markdown",
            use_container_width=True,
            disabled=df.empty,
        )
    with c2:
        st.download_button(
            "⬇ Download At-Risk Employees",
            worklist.to_csv(index=False).encode("utf-8"),
            file_name=f"at_risk_employees_{slug}.csv",
            mime="text/csv",
            use_container_width=True,
            disabled=worklist.empty,
        )


def render_at_risk_section(df: pd.DataFrame) -> None:
    worklist = at_risk_dataframe(df)
    st.subheader("At-risk employee worklist")
    st.caption(
        "Profile: overtime + job satisfaction ≤ 2 + under 3 years tenure. "
        "Download and assign to HRBPs for stay interviews."
    )
    if worklist.empty:
        st.success("No employees match the at-risk profile in the current selection.")
        return
    st.dataframe(worklist, use_container_width=True, hide_index=True)


def render_model_expander() -> None:
    metrics = load_metrics()
    importance = load_feature_importance()
    if not metrics:
        return
    with st.expander("Model performance (Random Forest vs Logistic Regression)"):
        rows = [
            {
                "Model": name,
                "Accuracy": s["accuracy"],
                "Precision": s["precision"],
                "Recall": s["recall"],
                "F1": s["f1_score"],
            }
            for name, s in metrics.get("models", {}).items()
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        selected = st.selectbox("Confusion matrix", list(metrics["models"].keys()), key="cm_model")
        cm = metrics["models"][selected]["confusion_matrix"]
        fig_cm = go.Figure(
            data=go.Heatmap(
                z=cm,
                x=["Pred: Stay", "Pred: Leave"],
                y=["Actual: Stay", "Actual: Leave"],
                colorscale=SCALE_ATTRITION,
                text=cm,
                texttemplate="%{text}",
                textfont={"size": 14, "color": "white"},
            )
        )
        apply_chart_style(fig_cm, height=320)
        st.plotly_chart(fig_cm, use_container_width=True)
        if importance is not None:
            st.caption("Global feature importance from training set (not filter-specific).")


def page_overview(
    df: pd.DataFrame,
    ctx: FilterContext,
    df_company: pd.DataFrame,
    cost_multiplier: float,
) -> None:
    st.markdown('<p class="main-header">Overview</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Executive snapshot and attrition priorities</p>',
        unsafe_allow_html=True,
    )
    render_filter_banner(ctx, df)
    st.markdown(
        executive_summary_section_html(df, ctx, df_company, cost_multiplier),
        unsafe_allow_html=True,
    )
    render_executive_downloads(df, ctx, df_company, cost_multiplier)
    kpi_overview(df, cost_multiplier)
    st.plotly_chart(plot_attrition_risk_matrix(df), use_container_width=True)
    st.markdown(
        business_impact_section_html(df, cost_multiplier),
        unsafe_allow_html=True,
    )
    st.markdown(top_priorities_section_html(df), unsafe_allow_html=True)
    render_at_risk_section(df)

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(plot_attrition_distribution(df), use_container_width=True)
        render_insight(insight_distribution(df))
    with c2:
        st.plotly_chart(plot_attrition_by_department(df), use_container_width=True)
        render_insight(insight_department(df))

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(plot_attrition_overtime(df), use_container_width=True)
        render_insight(insight_overtime(df))
    with c4:
        st.plotly_chart(plot_risk_segments(df), use_container_width=True)
        render_insight(insight_at_risk(df))


def page_workforce(df: pd.DataFrame, ctx: FilterContext) -> None:
    st.markdown('<p class="main-header">Workforce</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Compensation, education, and department risk ranking</p>',
        unsafe_allow_html=True,
    )
    render_filter_banner(ctx, df)
    kpi_workforce(df)

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(plot_income_by_department(df), use_container_width=True)
    with c2:
        st.plotly_chart(plot_education_attrition(df), use_container_width=True)

    st.subheader("Department risk ranking")
    dept_tbl = department_risk_table(df)
    dept_tbl["avg_salary"] = dept_tbl["avg_salary"].round(0).astype(int)
    dept_tbl["attrition_pct"] = dept_tbl["attrition_pct"].round(1)
    dept_tbl["priority_score"] = dept_tbl["priority_score"].round(1)
    st.dataframe(
        dept_tbl.rename(
            columns={
                "Department": "Department",
                "headcount": "Headcount",
                "attrition_pct": "Attrition %",
                "avg_salary": "Avg salary",
                "priority_score": "Priority score",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "Download department summary (CSV)",
        dept_tbl.to_csv(index=False).encode("utf-8"),
        file_name="department_risk_summary.csv",
        mime="text/csv",
    )


def page_insights(df: pd.DataFrame, ctx: FilterContext) -> None:
    st.markdown('<p class="main-header">Insights</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Drivers of turnover in the current selection</p>',
        unsafe_allow_html=True,
    )
    render_filter_banner(ctx, df)
    kpi_insights(df)

    tab_demo, tab_comp, tab_eng, tab_drv = st.tabs(
        ["Demographics", "Compensation", "Engagement", "Drivers"]
    )

    with tab_demo:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(plot_attrition_by_age(df), use_container_width=True)
            render_insight(insight_age(df))
        with c2:
            st.plotly_chart(plot_attrition_by_salary(df), use_container_width=True)
            render_insight(insight_salary(df))

    with tab_comp:
        st.plotly_chart(plot_attrition_by_job_role(df), use_container_width=True)
        render_insight(insight_job_roles(df))

    with tab_eng:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(plot_attrition_overtime(df), use_container_width=True)
            render_insight(insight_overtime(df))
        with c2:
            st.plotly_chart(plot_attrition_job_satisfaction(df), use_container_width=True)
            render_insight(insight_satisfaction(df))

    with tab_drv:
        importance = load_feature_importance()
        if importance is not None:
            st.plotly_chart(plot_feature_importance(importance), use_container_width=True)
            render_insight(
                "<strong>Finding:</strong> Model ranks income, age, tenure, and overtime "
                "among the strongest predictors.<br>"
                "<strong>Action:</strong> Align retention budgets with the top 3 drivers above."
            )
        else:
            st.warning("Train the model first: `python main.py --step train`")


def _build_employee_from_form(
    df: pd.DataFrame,
    age,
    gender,
    marital,
    department,
    job_role,
    education,
    education_field,
    business_travel,
    monthly_income,
    job_level,
    job_involvement,
    job_satisfaction,
    env_satisfaction,
    rel_satisfaction,
    work_life,
    over_time,
    stock_options,
    percent_hike,
    performance,
    total_years,
    years_company,
    years_role,
    years_promo,
    years_manager,
    num_companies,
    training,
    distance,
) -> dict:
    return {
        "Age": age,
        "Attrition": "No",
        "BusinessTravel": business_travel,
        "DailyRate": int(df["DailyRate"].median()),
        "Department": department,
        "DistanceFromHome": distance,
        "Education": education,
        "EducationField": education_field,
        "EnvironmentSatisfaction": env_satisfaction,
        "Gender": gender,
        "HourlyRate": int(df["HourlyRate"].median()),
        "JobInvolvement": job_involvement,
        "JobLevel": job_level,
        "JobRole": job_role,
        "JobSatisfaction": job_satisfaction,
        "MaritalStatus": marital,
        "MonthlyIncome": monthly_income,
        "MonthlyRate": int(df["MonthlyRate"].median()),
        "NumCompaniesWorked": num_companies,
        "OverTime": over_time,
        "PercentSalaryHike": percent_hike,
        "PerformanceRating": performance,
        "RelationshipSatisfaction": rel_satisfaction,
        "StockOptionLevel": stock_options,
        "TotalWorkingYears": total_years,
        "TrainingTimesLastYear": training,
        "WorkLifeBalance": work_life,
        "YearsAtCompany": years_company,
        "YearsInCurrentRole": years_role,
        "YearsSinceLastPromotion": years_promo,
        "YearsWithCurrManager": years_manager,
    }


def page_prediction(df_ref: pd.DataFrame) -> None:
    st.markdown('<p class="main-header">Predict</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Individual attrition risk, drivers, and HR actions</p>',
        unsafe_allow_html=True,
    )
    st.caption("Predictions use the full trained model (not sidebar filters).")
    st.markdown(
        f'<div class="model-rationale">{model_selection_rationale()}</div>',
        unsafe_allow_html=True,
    )

    preset = st.selectbox("Load example profile", list(PREDICT_PRESETS.keys()))
    preset_vals = PREDICT_PRESETS[preset] or {}

    with st.form("predict_form"):
        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("Employee profile")
            age = st.slider("Age", 18, 60, preset_vals.get("Age", 35))
            gender = st.selectbox("Gender", sorted(df_ref["Gender"].unique()))
            marital = st.selectbox("Marital Status", sorted(df_ref["MaritalStatus"].unique()))
            dept_options = sorted(df_ref["Department"].unique())
            dept_default = preset_vals.get("Department", dept_options[0])
            dept_index = (
                dept_options.index(dept_default)
                if dept_default in dept_options
                else 0
            )
            department = st.selectbox("Department", dept_options, index=dept_index)
            roles = sorted(
                df_ref.loc[df_ref["Department"] == department, "JobRole"].unique().tolist()
            )
            if not roles:
                roles = sorted(df_ref["JobRole"].unique())
            role_index = (
                roles.index(preset_vals["JobRole"])
                if preset_vals.get("JobRole") in roles
                else 0
            )
            job_role = st.selectbox("Job Role", roles, index=role_index)
            education = st.selectbox("Education Level", [1, 2, 3, 4, 5])
            education_field = st.selectbox(
                "Education Field", sorted(df_ref["EducationField"].unique())
            )
            business_travel = st.selectbox(
                "Business Travel", sorted(df_ref["BusinessTravel"].unique())
            )

        with col_right:
            st.subheader("Job & compensation")
            monthly_income = st.number_input(
                "Monthly Income ($)",
                1000,
                20000,
                preset_vals.get("MonthlyIncome", 5000),
            )
            job_level = st.selectbox("Job Level", [1, 2, 3, 4, 5])
            job_involvement = st.selectbox("Job Involvement (1-4)", [1, 2, 3, 4])
            job_satisfaction = st.selectbox(
                "Job Satisfaction (1-4)",
                [1, 2, 3, 4],
                index=preset_vals.get("JobSatisfaction", 2) - 1,
            )
            env_satisfaction = st.selectbox(
                "Environment Satisfaction (1-4)",
                [1, 2, 3, 4],
                index=preset_vals.get("EnvironmentSatisfaction", 2) - 1,
            )
            rel_satisfaction = st.selectbox("Relationship Satisfaction (1-4)", [1, 2, 3, 4])
            work_life = st.selectbox(
                "Work Life Balance (1-4)",
                [1, 2, 3, 4],
                index=preset_vals.get("WorkLifeBalance", 2) - 1,
            )
            over_time = st.selectbox(
                "Overtime",
                ["Yes", "No"],
                index=0 if preset_vals.get("OverTime") == "Yes" else 1,
            )
            stock_options = st.selectbox("Stock Option Level", [0, 1, 2, 3])
            percent_hike = st.slider("Percent Salary Hike", 0, 25, 12)
            performance = st.selectbox("Performance Rating", [3, 4])

        st.subheader("Tenure & experience")
        t1, t2, t3, t4 = st.columns(4)
        with t1:
            total_years = st.slider("Total Working Years", 0, 40, 10)
        with t2:
            years_company = st.slider(
                "Years at Company", 0, 40, preset_vals.get("YearsAtCompany", 5)
            )
        with t3:
            years_role = st.slider("Years in Current Role", 0, 20, 3)
        with t4:
            years_promo = st.slider("Years Since Last Promotion", 0, 15, 1)
        t5, t6, t7 = st.columns(3)
        with t5:
            years_manager = st.slider("Years With Current Manager", 0, 15, 2)
        with t6:
            num_companies = st.slider("Number of Companies Worked", 0, 10, 2)
        with t7:
            training = st.slider("Training Times Last Year", 0, 6, 2)
        distance = st.slider("Distance From Home", 1, 30, 5)

        submitted = st.form_submit_button("Run prediction", type="primary", use_container_width=True)

    if submitted:
        employee = _build_employee_from_form(
            df_ref,
            age,
            gender,
            marital,
            department,
            job_role,
            education,
            education_field,
            business_travel,
            monthly_income,
            job_level,
            job_involvement,
            job_satisfaction,
            env_satisfaction,
            rel_satisfaction,
            work_life,
            over_time,
            stock_options,
            percent_hike,
            performance,
            total_years,
            years_company,
            years_role,
            years_promo,
            years_manager,
            num_companies,
            training,
            distance,
        )
        try:
            result = predict_attrition(employee)
            prob_leave = result["probability_leave"]
            label = result["prediction_label"]
            tier, tier_note = risk_tier(prob_leave)
            importance = load_feature_importance()
            drivers = key_drivers_for_employee(employee, importance, df_ref)
            recs = hr_recommendations(employee, prob_leave)

            st.markdown("### Results")
            r1, r2, r3 = st.columns(3)
            r1.metric("Prediction", label)
            r2.metric("Leave probability", f"{prob_leave:.1%}")
            r3.metric("Risk tier", tier)

            st.info(tier_note)

            res_col1, res_col2 = st.columns([1, 1])
            with res_col1:
                css_class = "prediction-leave" if "Leave" in label else "prediction-stay"
                st.markdown(
                    f'<div class="{css_class}"><h2>{label}</h2>'
                    f"<p>Risk tier: <strong>{tier}</strong></p></div>",
                    unsafe_allow_html=True,
                )
                st.markdown("**Key drivers**")
                for name, detail in drivers:
                    st.markdown(f"- **{name}** — {detail}")
            with res_col2:
                fig = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=prob_leave * 100,
                        title={"text": "Leave probability (%)"},
                        gauge={
                            "axis": {"range": [0, 100]},
                            "bar": {"color": LEAVE if prob_leave > 0.5 else STAY},
                            "steps": [
                                {"range": [0, 35], "color": GAUGE_LOW},
                                {"range": [35, 65], "color": GAUGE_MID},
                                {"range": [65, 100], "color": GAUGE_HIGH},
                            ],
                        },
                    )
                )
                fig.update_layout(height=280, margin=dict(t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("**HR recommendations**")
            for rec in recs:
                st.markdown(f"- {rec}")

        except FileNotFoundError:
            st.error("Train the model first: `python main.py --step train`")
        except Exception as exc:
            st.error(f"Prediction failed: {exc}")

    render_model_expander()


def main() -> None:
    st.sidebar.markdown(
        '<p class="sidebar-brand-title">HR Analytics</p>'
        '<p class="sidebar-brand-sub">Employee attrition dashboard</p>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("**Menu**")
    page = st.sidebar.radio(
        "Menu",
        list(PAGES.values()),
        label_visibility="collapsed",
    )
    st.sidebar.markdown("---")

    df_raw = load_employee_data()
    df, ctx = sidebar_filters(df_raw)

    if len(df) == 0 and page != PAGES["predict"]:
        st.warning(
            "No employees match the current filters. Click **Reset filters** in the sidebar "
            "or broaden your selection."
        )
        return

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Cost assumption**")
    cost_mult = st.sidebar.slider(
        "Exit cost multiplier (× monthly salary)",
        1.0,
        3.0,
        DEFAULT_COST_MULTIPLIER_MONTHS,
        0.1,
        help="Used for estimated attrition cost on Overview.",
    )

    page_key = {v: k for k, v in PAGES.items()}[page]
    if page_key == "overview":
        page_overview(df, ctx, df_raw, cost_mult)
    elif page_key == "workforce":
        page_workforce(df, ctx)
    elif page_key == "insights":
        page_insights(df, ctx)
    elif page_key == "predict":
        page_prediction(df_raw)

    st.sidebar.markdown("---")
    with st.sidebar.expander("SQL reference"):
        st.code(
            "sql/03_department_attrition.sql\nsql/05_overtime_analysis.sql",
            language="text",
        )
    st.sidebar.caption("Tharun Billuri")
    render_app_footer()


if __name__ == "__main__":
    main()
