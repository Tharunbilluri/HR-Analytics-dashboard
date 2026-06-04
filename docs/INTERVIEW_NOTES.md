# Interview Talking Points

## Elevator pitch (30 seconds)

"I built an end-to-end HR attrition platform: SQL workforce queries, cleaned data pipeline, EDA, two classification models, and a Streamlit dashboard with filter-aware insights, an at-risk worklist HR can export, and individual predictions with HR recommendations."

## Key numbers (full dataset)

- 1,470 employees · 16.1% attrition · 237 leavers  
- Overtime attrition 30.5% vs 10.4% without (+20 pp)  
- Sales 20.6% · HR 19.0% · R&D 13.8%  
- 39 employees in at-risk rule-based cohort  

## Expected questions

**Why Random Forest for production?**  
Higher accuracy for screening; LR when recall on leavers is the priority.

**Why rule-based at-risk if you have ML?**  
Executives need explainable cohorts for stay interviews; rules are auditable.

**How do filters change conclusions?**  
Insights and KPIs recompute on filtered data; banner shows filtered vs 16.1% baseline.

**How did you handle imbalance?**  
`class_weight='balanced'`; report precision/recall/F1, not accuracy alone.

**What would you do with real data?**  
Validate cost assumptions, A/B retention programs, monitor model drift, SHAP for drivers.

## Demo flow (5 minutes)

1. Overview — executive summary, top 3 actions, download at-risk CSV  
2. Insights — overtime + job role tabs  
3. Predict — high-risk preset → drivers + recommendations  
