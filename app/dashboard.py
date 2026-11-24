from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
P2 = ROOT / "fixtures" / "credit_risk_engine"
sys.path.insert(0, str(ROOT))  # local shared/ for standalone + Streamlit Cloud
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(P2 / "src"))

from shared.plot_theme import COLORS, apply_plotly_theme  # noqa: E402
from challenge_tests import run_all_tests  # noqa: E402

st.set_page_config(page_title="Model Validation Pack", layout="wide")
st.markdown(
    f"<style>.stApp {{ background-color: {COLORS['bg']}; color: {COLORS['text']}; }}</style>",
    unsafe_allow_html=True,
)
st.title("Model Validation Pack")
st.caption("SR 11-7–aligned challenge tests on the Credit Risk Engine")

dd_path = P2 / "outputs" / "dd_panel.csv"
loss_path = P2 / "outputs" / "loss_sims.csv"
findings_path = ROOT / "outputs" / "findings.csv"
memo_path = ROOT / "outputs" / "VALIDATION_MEMO.md"

if st.button("Re-run challenge battery") or not findings_path.exists():
    if not dd_path.exists() or not loss_path.exists():
        st.warning("P2 outputs missing — run `python 02_credit_risk_engine/scripts/run_mvp.py` first.")
        st.stop()
    dd = pd.read_csv(dd_path, parse_dates=["date"])
    losses = pd.read_csv(loss_path)
    findings = run_all_tests(dd, losses)
    ROOT.joinpath("outputs").mkdir(exist_ok=True)
    findings.to_csv(findings_path, index=False)
else:
    findings = pd.read_csv(findings_path)

c1, c2, c3 = st.columns(3)
c1.metric("PASS", int((findings["status"] == "PASS").sum()))
c2.metric("WARN", int((findings["status"] == "WARN").sum()))
c3.metric("FAIL", int((findings["status"] == "FAIL").sum()))

color_map = {"PASS": COLORS["good"], "WARN": COLORS["warn"], "FAIL": COLORS["danger"]}
fig = px.bar(
    findings,
    x="test_id",
    y="name",
    color="status",
    color_discrete_map=color_map,
    title="Validation findings board",
    hover_data=["severity", "detail", "metric"],
    orientation="h",
)
apply_plotly_theme(fig)
st.plotly_chart(fig, use_container_width=True)
st.dataframe(findings, use_container_width=True)

if memo_path.exists():
    st.subheader("Validation memo")
    st.markdown(memo_path.read_text(encoding="utf-8"))
