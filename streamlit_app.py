"""
Streamlit Community Cloud entrypoint (repo root).

Deploy settings:
  Main file path: streamlit_app.py
  Working directory: repository root
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

runpy.run_path(str(ROOT / "app" / "streamlit_app.py"), run_name="__main__")
