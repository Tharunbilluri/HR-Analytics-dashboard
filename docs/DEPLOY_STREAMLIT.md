# Deploy to Streamlit Community Cloud

## Prerequisites

- GitHub repo with this project (models + data committed)
- [Streamlit Community Cloud](https://share.streamlit.io/) account linked to GitHub

## Deploy steps

1. Push `hr_analytics_project` to GitHub (see root README).
2. Go to **share.streamlit.io** → **Create app**.
3. Select your repo and branch.
4. Set **Main file path:** `streamlit_app.py` (repo root).
5. **App URL** (example): `https://hr-analytics-dashboard-tharun.streamlit.app`
6. Click **Deploy** — first build installs `requirements.txt` (~2–5 min).

## After deploy

1. Copy the public URL into `README.md` (Live demo badge).
2. Record a 2-min Loom using [`LOOM_WALKTHROUGH.md`](LOOM_WALKTHROUGH.md).
3. Add the Loom link under **Demo video** in the README.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `FileNotFoundError` for model | Ensure `models/random_forest.joblib` is in the repo |
| Import errors | Main file must be root `streamlit_app.py`, not `app/streamlit_app.py` alone |
| App crashes on Predict | Run training locally and commit all `models/*.joblib` files |

## CLI (optional)

If logged in via Streamlit CLI:

```bash
cd hr_analytics_project
streamlit deploy
```

Follow prompts to link the GitHub repository.
