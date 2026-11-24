from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P2 = ROOT / "fixtures" / "credit_risk_engine"
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(P2 / "src"))

from challenge_tests import run_all_tests  # noqa: E402
from memo import render_memo  # noqa: E402


def main():
    out = ROOT / "outputs"
    out.mkdir(parents=True, exist_ok=True)

    dd_path = P2 / "outputs" / "dd_panel.csv"
    loss_path = P2 / "outputs" / "loss_sims.csv"

    if not dd_path.exists() or not loss_path.exists():
        # Ensure P2 artifacts exist
        import runpy

        runpy.run_path(str(P2 / "scripts" / "run_mvp.py"), run_name="__main__")

    dd = pd.read_csv(dd_path, parse_dates=["date"]) if dd_path.exists() else pd.DataFrame()
    losses = pd.read_csv(loss_path) if loss_path.exists() else pd.DataFrame()

    findings = run_all_tests(dd, losses)
    findings.to_csv(out / "findings.csv", index=False)
    render_memo(findings, out / "VALIDATION_MEMO.md")

    summary = {
        "n_tests": int(len(findings)),
        "pass": int((findings["status"] == "PASS").sum()),
        "warn": int((findings["status"] == "WARN").sum()),
        "fail": int((findings["status"] == "FAIL").sum()),
    }
    (out / "meta.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("P3 MVP complete ->", out)
    print(findings[["test_id", "name", "status", "severity"]].to_string(index=False))


if __name__ == "__main__":
    main()
