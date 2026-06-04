# 2-Minute Loom Walkthrough Script

**Title:** HR Analytics Dashboard — Attrition Analysis & Prediction  
**Length:** ~2:00  
**Record:** Full browser at 1440px, start on Overview after `streamlit run streamlit_app.py`

---

## 0:00–0:15 — Hook

> "This is my HR attrition analytics dashboard. It answers three questions for leadership: where turnover is highest, who HR should contact first, and whether a specific employee is likely to leave."

*Show Overview — executive summary + KPI row.*

---

## 0:15–0:45 — Overview & filters

> "The executive summary updates with filters. Here’s the full company: sixteen percent attrition, about one point seven million in estimated exit cost, and thirty-nine at-risk employees."

*Sidebar: select **Sales** only.*

> "When I filter to Sales only, the view drops to four forty-six employees, attrition jumps to twenty point six percent, and downloads update for analysts."

*Point at Download Executive Report and At-Risk CSV.*

> "The risk matrix plots attrition percent against department size — Sales sits high on both axes."

---

## 0:45–1:15 — Insights

*Click **Insights** → open **Drivers** or **Engagement** tab.*

> "Insights break down demographics, compensation, and engagement. Overtime is a major driver — thirty percent attrition with overtime versus ten percent without."

*Briefly scroll one chart + Finding/Action box.*

---

## 1:15–1:45 — Predict

*Click **Predict** → preset **High risk — Sales + overtime** → **Run prediction**.*

> "The predict page uses a Random Forest model trained on the full dataset. This profile shows elevated leave probability, a risk tier, top drivers, and HR-style recommendations."

*Show gauge + recommendations.*

> "We compared Random Forest and Logistic Regression — RF for accuracy, LR when catching leavers matters more."

---

## 1:45–2:00 — Close

*Scroll to footer or back to Overview.*

> "Stack: Python, SQL, Scikit-learn, Plotly, Streamlit. Code and live demo are linked in the README. Thanks for watching."

---

## Checklist before recording

- [ ] App running locally or use live Streamlit URL  
- [ ] Models trained (`python main.py --step train`)  
- [ ] Mic clear, no notifications  
- [ ] Paste Loom link in README under **Demo video**
