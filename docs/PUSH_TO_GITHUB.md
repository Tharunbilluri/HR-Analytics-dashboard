# Push this project to GitHub

Repo: **https://github.com/Tharunbilluri/HR-Analytics-dashboard**

The full project is committed locally on branch `main`. GitHub currently has only a placeholder README — you will replace it with this repo.

## Option A — GitHub CLI (recommended)

```bash
cd "/Users/varunbilluri/HR Analytics dashboard/hr_analytics_project"
./push-to-github.sh
```

Or manually:

```bash
gh auth login -h github.com -p https -w   # sign in as Tharunbilluri
gh auth setup-git
git remote set-url origin https://github.com/Tharunbilluri/HR-Analytics-dashboard.git
git push -u origin main --force
```

Sign in as **Tharunbilluri** when prompted. Do not use SSH unless that key is added to the Tharunbilluri account (this machine’s SSH key is linked to another user).

## Option B — HTTPS + personal access token

1. Create a token: GitHub → Settings → Developer settings → Personal access tokens  
2. Run:

```bash
cd "/Users/varunbilluri/HR Analytics dashboard/hr_analytics_project"
git remote set-url origin https://github.com/Tharunbilluri/HR-Analytics-dashboard.git
git push -u origin main --force
```

Use username `Tharunbilluri` and the token as the password.

## Option C — SSH (Tharunbilluri account key)

Add your **Tharunbilluri** SSH key to GitHub, then:

```bash
git remote set-url origin git@github.com:Tharunbilluri/HR-Analytics-dashboard.git
git push -u origin main --force
```

> `--force` is safe here: the remote only has the initial README; your local repo has the complete dashboard.

## Verify

Open https://github.com/Tharunbilluri/HR-Analytics-dashboard — you should see `app/`, `models/`, `docs/images/`, and the new README with screenshots.
