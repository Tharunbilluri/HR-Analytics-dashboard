#!/usr/bin/env python3
"""Capture README screenshots from a running Streamlit app (localhost:8501)."""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "images"
BASE_URL = "http://localhost:8501"


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Install: pip install playwright && playwright install chromium")
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    shots = [
        ("overview.png", None, None),
        ("insights.png", "Insights", None),
        ("predict.png", "Predict", None),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(BASE_URL, wait_until="networkidle", timeout=60_000)
        page.wait_for_timeout(4000)

        for filename, nav_label, action in shots:
            if nav_label:
                page.locator(f'label:has-text("{nav_label}")').first.click()
                page.wait_for_timeout(3500)
            path = OUT / filename
            # Main content area (skip narrow sidebar for cleaner README)
            main = page.locator('[data-testid="stAppViewContainer"]').first
            main.screenshot(path=str(path))
            print(f"Wrote {path}")

        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
