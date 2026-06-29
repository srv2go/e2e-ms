# frontend/app.py
"""Paycon e2ePS — End-to-End Payment Simulator.

Multi-page Streamlit application shell.
The bulk of the UI lives in frontend/pages/ (01_home.py … 12_enrichment_trace.py).
This file sets global page config, injects the shared Paycon theme, and shows a
branded landing screen with a live health check.
"""
import sys
import os

# Make shared utilities importable from pages/ sub-modules.
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from utils.session_state import init_session_state
from utils.api_client import get_api_url
from utils.theme import inject_theme

init_session_state()

st.set_page_config(
    page_title="Paycon e2ePS — End-to-End Payment Simulator",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()

# ── Brand header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="pc-brand-bar">
  <span style="font-size:2em">🏦</span>
  <div>
    <div class="pc-brand-name">Pay<span>con</span> · e2ePS</div>
    <div style="font-size:0.76em;color:#7a9cc0">End-to-End Payment Simulator</div>
  </div>
  <span class="pc-brand-tag">pilot</span>
</div>
""", unsafe_allow_html=True)

st.markdown(
    "Use the **sidebar** to navigate. "
    "Start at **🏠 Home** for live health, a one-click demo run, and recent results."
)

st.markdown("---")

# ── Live backend status ────────────────────────────────────────────────────────
api_url = get_api_url()
st.caption(f"Backend: `{api_url}`")

try:
    import requests as _req
    r = _req.get(f"{api_url}/health", timeout=3)
    if r.status_code == 200:
        st.success("✅ Backend is reachable — navigate to **🏠 Home** to get started")
    else:
        st.warning(f"⚠️ Backend returned HTTP {r.status_code}")
except Exception as e:
    st.error(f"❌ Cannot reach backend at `{api_url}` — {e}")
    st.caption("Start the stack: `make demo-local` (no Docker) or `docker-compose up --build`")
