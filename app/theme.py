"""
User-friendly color theme for the HR Analytics dashboard.

Design system: light main canvas, white sidebar, dark readable text,
blue brand accents, coral/sage only for attrition semantics.
"""

from __future__ import annotations

# Brand
PRIMARY = "#2C4368"
SECONDARY = "#4A6FA5"
ACCENT = "#6B8FC4"
MUTED = "#7A8FA6"

# Semantic (attrition only — do not use red for UI chrome)
STAY = "#3D8B7A"
LEAVE = "#C66B5C"

# Surfaces
BG_MAIN = "#F8FAFC"
BG_CARD = "#FFFFFF"
BG_SIDEBAR = "#FFFFFF"
BG_INSIGHT = "#F0F5FB"
BORDER = "#D0DAE6"
BORDER_LIGHT = "#E8EDF3"

# Text (WCAG-friendly on white / light gray)
TEXT_PRIMARY = "#1E2A3A"
TEXT_SECONDARY = "#4A5D73"
TEXT_ON_ACCENT = "#FFFFFF"

# Charts — each department gets a distinct, visible bar color
DEPT_COLORS = {
    "Sales": "#C66B5C",
    "Human Resources": "#4A6FA5",
    "Research & Development": "#2C4368",
}
DEPT_SHORT = {
    "Sales": "Sales",
    "Human Resources": "HR",
    "Research & Development": "R&D",
}

ATTRITION_LABELS = {"Yes": "Left", "No": "Stayed"}
ATTRITION_COLORS = {"Left": LEAVE, "Stayed": STAY, "Yes": LEAVE, "No": STAY}
OVERTIME_LABELS = {"Yes": "Overtime", "No": "No Overtime"}
OVERTIME_COLORS = {"Overtime": LEAVE, "No Overtime": SECONDARY, "Yes": LEAVE, "No": SECONDARY}

GENDER_COLORS = {"Female": "#7B6BA8", "Male": "#4A6FA5"}

BAR_SEQUENCE = [SECONDARY, PRIMARY, ACCENT, "#7B6BA8", STAY, LEAVE]

SCALE_ATTRITION = [[0.0, ACCENT], [0.5, SECONDARY], [1.0, PRIMARY]]
SCALE_IMPORTANCE = [[0.0, "#D6E4F4"], [0.5, ACCENT], [1.0, PRIMARY]]
SCALE_CORRELATION = [[0.0, "#3D6E8F"], [0.5, "#F8FAFC"], [1.0, "#C66B5C"]]
SCALE_SUNBURST = [[0.0, "#D6E4F4"], [0.5, ACCENT], [1.0, PRIMARY]]

GAUGE_LOW = "#D4EDE8"
GAUGE_MID = "#F0E6CE"
GAUGE_HIGH = "#F5DDD8"

# Navigation (short, scannable labels)
PAGES = {
    "overview": "Overview",
    "workforce": "Workforce",
    "insights": "Insights",
    "predict": "Predict",
}


def apply_chart_style(fig, height: int | None = None, bottom_margin: int = 56):
    """White chart card on light gray page — readable bars and labels."""
    fig.update_layout(
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_CARD,
        font=dict(family="Inter, system-ui, sans-serif", color=TEXT_PRIMARY, size=13),
        title_font=dict(size=15, color=PRIMARY),
        margin=dict(t=48, b=bottom_margin, l=12, r=12),
    )
    if height:
        fig.update_layout(height=height)
    fig.update_xaxes(
        gridcolor=BORDER_LIGHT,
        linecolor=BORDER,
        tickfont=dict(color=TEXT_SECONDARY, size=12),
        title_font=dict(color=TEXT_SECONDARY, size=12),
        zeroline=False,
    )
    fig.update_yaxes(
        gridcolor=BORDER_LIGHT,
        linecolor=BORDER,
        tickfont=dict(color=TEXT_SECONDARY, size=12),
        title_font=dict(color=TEXT_SECONDARY, size=12),
        zeroline=False,
    )
    return fig


def streamlit_custom_css() -> str:
    """Override Streamlit defaults that cause white-on-light sidebar text."""
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp {{
        background-color: {BG_MAIN} !important;
    }}

    [data-testid="stAppViewContainer"] > section.main {{
        background-color: {BG_MAIN} !important;
    }}

    [data-testid="stMainBlockContainer"] {{
        background-color: {BG_MAIN} !important;
        padding-top: 1rem;
    }}

    /* ── Sidebar: white bg, dark text everywhere ── */
    section[data-testid="stSidebar"] {{
        background-color: {BG_SIDEBAR} !important;
        border-right: 1px solid {BORDER} !important;
    }}

    section[data-testid="stSidebar"] * {{
        color: {TEXT_PRIMARY} !important;
    }}

    section[data-testid="stSidebar"] .sidebar-brand-title {{
        color: {PRIMARY} !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        margin: 0 0 0.15rem 0 !important;
    }}

    section[data-testid="stSidebar"] .sidebar-brand-sub {{
        color: {TEXT_SECONDARY} !important;
        font-size: 0.85rem !important;
        margin: 0 0 1rem 0 !important;
    }}

    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {{
        color: {PRIMARY} !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        margin-top: 0.5rem !important;
    }}

    /* Navigation radio */
    section[data-testid="stSidebar"] div[role="radiogroup"] {{
        gap: 0.25rem !important;
    }}

    section[data-testid="stSidebar"] div[role="radiogroup"] label {{
        background-color: transparent !important;
        color: {TEXT_PRIMARY} !important;
        font-weight: 500 !important;
        padding: 0.55rem 0.75rem !important;
        border-radius: 8px !important;
        border: 1px solid transparent !important;
    }}

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
        background-color: {BG_INSIGHT} !important;
    }}

    section[data-testid="stSidebar"] div[role="radiogroup"] label span,
    section[data-testid="stSidebar"] div[role="radiogroup"] label p,
    section[data-testid="stSidebar"] div[role="radiogroup"] label div {{
        color: {TEXT_PRIMARY} !important;
    }}

    /* Multiselect: white box, blue tags (not red) */
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
        background-color: {BG_CARD} !important;
        border: 1px solid {BORDER} !important;
        color: {TEXT_PRIMARY} !important;
    }}

    section[data-testid="stSidebar"] span[data-baseweb="tag"] {{
        background-color: {SECONDARY} !important;
        color: {TEXT_ON_ACCENT} !important;
        border: none !important;
    }}

    section[data-testid="stSidebar"] span[data-baseweb="tag"] span {{
        color: {TEXT_ON_ACCENT} !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
        color: {TEXT_SECONDARY} !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
    }}

    section[data-testid="stSidebar"] hr {{
        border-color: {BORDER} !important;
        margin: 0.75rem 0 !important;
    }}

    section[data-testid="stSidebar"] .stCaption {{
        color: {MUTED} !important;
        font-size: 0.75rem !important;
    }}

    /* ── Main content ── */
    .main-header {{
        font-size: 1.75rem;
        font-weight: 700;
        color: {PRIMARY};
        margin-bottom: 0.15rem;
    }}

    .sub-header {{
        font-size: 0.95rem;
        color: {TEXT_SECONDARY};
        margin-bottom: 1.25rem;
    }}

    .filter-banner {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-size: 0.88rem;
        color: {TEXT_SECONDARY};
        margin-bottom: 1rem;
    }}

    .executive-summary {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-left: 4px solid {PRIMARY};
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
        color: {TEXT_PRIMARY};
        font-size: 0.92rem;
    }}

    .filter-scope {{
        color: {TEXT_SECONDARY};
        font-size: 0.88rem;
    }}

    .app-footer {{
        margin-top: 2.5rem;
        padding: 1.25rem 0 2rem 0;
        border-top: 1px solid {BORDER};
        text-align: center;
        color: {TEXT_SECONDARY};
        font-size: 0.82rem;
        line-height: 1.6;
    }}

    .app-footer .footer-author {{
        color: {TEXT_PRIMARY};
        font-weight: 600;
        margin-top: 0.35rem;
    }}

    .actions-panel {{
        background: {BG_INSIGHT};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 1rem;
    }}

    .actions-panel strong {{
        color: {PRIMARY};
    }}

    .model-rationale {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 0.9rem;
        color: {TEXT_PRIMARY};
        margin-bottom: 1rem;
    }}

    .insight-box {{
        background: {BG_INSIGHT};
        border-left: 4px solid {SECONDARY};
        padding: 0.85rem 1.1rem;
        border-radius: 0 10px 10px 0;
        margin: 0.5rem 0 1rem 0;
        font-size: 0.9rem;
        line-height: 1.55;
        color: {TEXT_PRIMARY};
    }}

    .insight-box strong {{
        color: {PRIMARY};
    }}

    div[data-testid="stMetric"] {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 0.85rem 1rem;
        box-shadow: 0 1px 4px rgba(44, 67, 104, 0.06);
    }}

    div[data-testid="stMetric"] label {{
        color: {TEXT_SECONDARY} !important;
    }}

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: {PRIMARY} !important;
        font-weight: 700 !important;
    }}

    [data-testid="stPlotlyChart"] {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 0.35rem;
    }}

    h1, h2, h3 {{
        color: {PRIMARY} !important;
    }}

    .stButton > button[kind="primary"] {{
        background: {PRIMARY} !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
    }}

    .stButton > button[kind="primary"]:hover {{
        background: {SECONDARY} !important;
    }}
    </style>
    """


def render_app_footer() -> None:
    """Portfolio footer for screenshots and sharing."""
    import streamlit as st

    st.markdown(
        f"""
        <div class="app-footer">
            Built with Python, SQL, Scikit-Learn, Plotly, and Streamlit<br>
            <span class="footer-author">Author: Tharun Billuri</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
