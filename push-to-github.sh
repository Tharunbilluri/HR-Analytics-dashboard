#!/bin/bash
# Upload full project to https://github.com/Tharunbilluri/HR-Analytics-dashboard
set -e
cd "$(dirname "$0")"

echo "=== HR Analytics Dashboard → GitHub ==="
echo "Repo: https://github.com/Tharunbilluri/HR-Analytics-dashboard"
echo ""

if ! command -v gh &>/dev/null; then
  echo "Install GitHub CLI: brew install gh"
  exit 1
fi

echo "Step 1: Log in to GitHub as Tharunbilluri (browser will open)..."
gh auth login -h github.com -p https -w
gh auth setup-git

echo ""
echo "Step 2: Create repo on GitHub (if it does not exist)..."
if ! gh repo view Tharunbilluri/HR-Analytics-dashboard &>/dev/null; then
  gh repo create HR-Analytics-dashboard \
    --public \
    --description "HR Analytics dashboard — attrition, engagement, and workforce insights (Streamlit)" \
    --source=. \
    --remote=origin
else
  git remote set-url origin https://github.com/Tharunbilluri/HR-Analytics-dashboard.git
fi

echo ""
echo "Step 3: Pushing all files..."
git push -u origin main --force

echo ""
echo "Done! Open: https://github.com/Tharunbilluri/HR-Analytics-dashboard"
