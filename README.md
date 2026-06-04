# HR Analytics Dashboard

**End-to-end employee attrition analytics for HR leaders — from SQL insights to ML prediction.**

[![Author](https://img.shields.io/badge/Author-Tharun_Billuri-2C4368?style=flat)](https://github.com/Tharunbilluri)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E?style=flat)](https://scikit-learn.org/)
[![Live Demo](https://img.shields.io/badge/Live_Demo-Deploy_on_Streamlit_Cloud-FF4B4B?style=flat&logo=streamlit)](docs/DEPLOY_STREAMLIT.md)
[![Demo Video](https://img.shields.io/badge/Video-2_min_Loom_script-9146FF?style=flat)](docs/LOOM_WALKTHROUGH.md)

**Repository:** [github.com/Tharunbilluri/HR-Analytics-dashboard](https://github.com/Tharunbilluri/HR-Analytics-dashboard)  
**Dataset:** [IBM HR Employee Attrition](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset) · 1,470 employees · synthetic HR data

---

## Why this project exists

Companies lose money when employees leave unexpectedly. This dashboard turns HR data into **decisions**:

| Question | What you get |
|----------|----------------|
| **Where** is attrition highest? | Department, overtime, and satisfaction breakdowns + risk matrix |
| **Who** should HR call first? | Rule-based at-risk list with CSV export |
| **Will** someone leave? | Random Forest probability, risk tier, drivers, and HR recommendations |

Built as a **data analyst portfolio** project: business framing, SQL, Python pipeline, interactive Streamlit app, and downloadable executive reports.

---

## Results at a glance

| Metric | Value |
|--------|-------|
| Overall attrition | **16.1%** (237 exits) |
| Estimated exit cost | **~$1.70M** (1.5× monthly salary proxy) |
| Highest-risk department | **Sales — 20.6%** |
| Overtime impact | **+20.1 pp** (30.5% vs 10.4%) |
| Immediate intervention list | **39 at-risk employees** |

**Recommended actions:** reduce overtime exposure · Sales retention program · stay interviews for the at-risk cohort within 14 days.

→ Full narrative: [`docs/EXECUTIVE_SUMMARY.md`](docs/EXECUTIVE_SUMMARY.md)

---

## Dashboard preview

<p align="center">
  <img src="docs/images/overview.png" alt="Overview — executive summary, KPIs, and attrition risk matrix" width="100%" />
</p>

<p align="center">
  <img src="docs/images/insights.png" alt="Insights — demographics and drivers" width="49%" />
  <img src="docs/images/predict.png" alt="Predict — attrition probability and recommendations" width="49%" />
</p>

### Four pages

| Page | Highlights |
|------|------------|
| **Overview** | Filter-aware executive summary · KPI cards · attrition risk matrix · business impact · top priorities · **Download Executive Report** & **At-Risk CSV** |
| **Workforce** | Compensation, education, department risk ranking + export |
| **Insights** | Tabbed EDA: demographics, pay, engagement, ML feature importance |
| **Predict** | Live attrition score, gauge, key drivers, HR recommendations (RF vs LR explained) |

**Standout UX:** sidebar filters recalculate every metric, insight, and download — e.g. **Sales only → 446 employees, 20.6% attrition, 18 at-risk**.

---

## Tech stack

| Layer | Tools |
|-------|--------|
| Data & EDA | Python, Pandas, NumPy, Jupyter |
| ML | Scikit-learn (Logistic Regression + Random Forest) |
| Viz & app | Plotly, Streamlit |
| Database | SQL (MySQL / PostgreSQL scripts) |
| Pipeline | `main.py` CLI — preprocess → train → predict |

---

## Quick start

### 1. Clone & install

```bash
git clone https://github.com/Tharunbilluri/HR-Analytics-dashboard.git
cd HR-Analytics-dashboard
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run pipeline (first time)

```bash
python main.py --step preprocess
python main.py --step train
```

### 3. Launch dashboard

```bash
streamlit run streamlit_app.py
```

Open **http://localhost:8501**

### 4. Deploy live (optional)

Follow [`docs/DEPLOY_STREAMLIT.md`](docs/DEPLOY_STREAMLIT.md) — use root `streamlit_app.py` as the main file on [Streamlit Community Cloud](https://share.streamlit.io/).

---

## Machine learning

| Model | Accuracy | Recall (leavers) | Use case |
|-------|----------|------------------|----------|
| Logistic Regression | 75.2% | **76.6%** | Maximize catching leavers |
| **Random Forest** ✓ | **82.7%** | 25.5% | **Production default** — screening |

**Top drivers:** Monthly income · Age · Total working years · Overtime · Years at company  

Artifacts: `models/random_forest.joblib`, `models/model_metrics.json`, `models/feature_importance.csv`

Modeling choices: [`docs/DECISIONS.md`](docs/DECISIONS.md) · Interview talking points: [`docs/INTERVIEW_NOTES.md`](docs/INTERVIEW_NOTES.md)

---

## SQL analysis

| Department | Attrition % |
|------------|-------------|
| Sales | 20.6% |
| Human Resources | 19.0% |
| Research & Development | 13.8% |

| Overtime | Attrition % |
|----------|-------------|
| Yes | 30.5% |
| No | 10.4% |

Scripts: `sql/` · Results write-up: [`docs/SQL_RESULTS.md`](docs/SQL_RESULTS.md)

---

## Project structure

```
├── streamlit_app.py          # Streamlit Cloud entrypoint
├── app/
│   ├── streamlit_app.py      # 4-page dashboard UI
│   ├── analytics.py          # Insights, risk rules, executive logic
│   ├── utils.py              # Charts & KPIs
│   └── theme.py              # Design system
├── src/
│   ├── preprocessing.py
│   ├── train_model.py
│   └── predict.py
├── sql/                      # 6 analysis queries + schema
├── notebooks/eda_analysis.ipynb
├── models/                   # Trained models & metrics
├── data/                     # IBM HR CSV
├── docs/                     # Executive summary, deploy, Loom script
├── scripts/
│   ├── generate_docs.py
│   └── capture_screenshots.py
├── main.py
└── requirements.txt
```

---

## Documentation

| Doc | Purpose |
|-----|---------|
| [`docs/EXECUTIVE_SUMMARY.md`](docs/EXECUTIVE_SUMMARY.md) | Stakeholder-ready brief |
| [`docs/DEPLOY_STREAMLIT.md`](docs/DEPLOY_STREAMLIT.md) | Publish live demo |
| [`docs/LOOM_WALKTHROUGH.md`](docs/LOOM_WALKTHROUGH.md) | 2-minute video script |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | Modeling & product decisions |
| [`docs/INTERVIEW_NOTES.md`](docs/INTERVIEW_NOTES.md) | Portfolio interview prep |

---

## About the author

**Tharun Billuri** — Data Analyst  

This project demonstrates the full analyst workflow: **business question → SQL + Python analysis → ML → interactive dashboard → executive deliverables**.

- GitHub: [@Tharunbilluri](https://github.com/Tharunbilluri)
- Repo: [HR-Analytics-dashboard](https://github.com/Tharunbilluri/HR-Analytics-dashboard)

---

## License

IBM synthetic HR dataset per [Kaggle terms](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset). Project code for portfolio and learning use.
# HR-Analytics-dashboard
