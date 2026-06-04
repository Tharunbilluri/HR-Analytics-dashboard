#!/usr/bin/env python3
"""Regenerate executive summary and SQL snapshot for README."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd  # noqa: E402

from app.analytics import build_executive_summary_markdown  # noqa: E402
from app.utils import load_employee_data  # noqa: E402


def sql_snapshot(df: pd.DataFrame) -> str:
    lines = ["## SQL analysis results (computed in Python, mirrors `sql/` scripts)", ""]
    rate = (df["Attrition"] == "Yes").mean() * 100
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Overall attrition rate | {rate:.2f}% |")
    lines.append(f"| Total employees | {len(df):,} |")
    lines.append("")
    lines.append("| Department | Attrition % |")
    lines.append("|------------|-------------|")
    for dept, grp in df.groupby("Department"):
        r = (grp["Attrition"] == "Yes").mean() * 100
        lines.append(f"| {dept} | {r:.1f}% |")
    lines.append("")
    lines.append("| Overtime | Attrition % |")
    lines.append("|----------|-------------|")
    for ot, grp in df.groupby("OverTime"):
        r = (grp["Attrition"] == "Yes").mean() * 100
        lines.append(f"| {ot} | {r:.1f}% |")
    return "\n".join(lines)


def main():
    df = load_employee_data()
    docs = PROJECT_ROOT / "docs"
    docs.mkdir(exist_ok=True)
    (docs / "EXECUTIVE_SUMMARY.md").write_text(
        build_executive_summary_markdown(df), encoding="utf-8"
    )
    (docs / "SQL_RESULTS.md").write_text(sql_snapshot(df), encoding="utf-8")
    print(f"Wrote {docs / 'EXECUTIVE_SUMMARY.md'}")
    print(f"Wrote {docs / 'SQL_RESULTS.md'}")


if __name__ == "__main__":
    main()
