from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


@dataclass
class Finding:
    test_id: str
    name: str
    severity: str  # Critical / High / Medium / Low / Info
    status: str  # PASS / FAIL / WARN
    detail: str
    metric: float | None = None


def _sev(status: str, default_fail: str = "High") -> str:
    return "Info" if status == "PASS" else default_fail


def test_pd_bounds(dd: pd.DataFrame) -> Finding:
    if dd.empty or "PD" not in dd.columns:
        return Finding("T01", "PD bounds", "Critical", "FAIL", "DD panel empty or missing PD")
    bad = ((dd["PD"] < 0) | (dd["PD"] > 1)).sum()
    status = "PASS" if bad == 0 else "FAIL"
    return Finding("T01", "PD bounds in [0,1]", _sev(status, "Critical"), status, f"out_of_bounds={int(bad)}", float(bad))


def test_dd_pd_monotonic(dd: pd.DataFrame) -> Finding:
    if dd.empty or not {"DD", "PD"}.issubset(dd.columns):
        return Finding("T02", "DD–PD monotonicity", "High", "FAIL", "Missing DD/PD")
    # Higher DD should mean lower PD
    corr, _ = spearmanr(dd["DD"].dropna(), dd["PD"].dropna())
    status = "PASS" if corr < -0.9 else ("WARN" if corr < 0 else "FAIL")
    sev = "Info" if status == "PASS" else ("Medium" if status == "WARN" else "High")
    return Finding("T02", "DD vs PD rank correlation negative", sev, status, f"spearman={corr:.3f}", float(corr))


def test_irb_monotonicity() -> Finding:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "fixtures" / "credit_risk_engine" / "src"))
    from irb import risk_weight

    r1 = risk_weight(0.001, 0.45)
    r2 = risk_weight(0.05, 0.45)
    status = "PASS" if r2 > r1 else "FAIL"
    return Finding("T03", "IRB RW increases in PD", _sev(status, "Critical"), status, f"rw(0.1%)={r1:.3f}, rw(5%)={r2:.3f}", r2 - r1)


def test_stability_rolling(dd: pd.DataFrame, max_jump: float = 0.2) -> Finding:
    if dd.empty or "PD" not in dd.columns:
        return Finding("T04", "PD stability", "High", "FAIL", "No PD series")
    jumps = []
    for t, g in dd.groupby("ticker"):
        s = g.sort_values("date")["PD"]
        if len(s) < 5:
            continue
        jumps.append(s.diff().abs().max())
    if not jumps:
        return Finding("T04", "PD stability", "Medium", "WARN", "Insufficient history per name")
    m = float(np.nanmax(jumps))
    status = "PASS" if m < max_jump else "WARN"
    return Finding("T04", "Max |ΔPD| below threshold", "Medium" if status == "WARN" else "Info", status, f"max_abs_dPD={m:.3f}", m)


def test_leakage_placeholder() -> Finding:
    """Conceptual soundness reminder: point-in-time debt must not use future filings."""
    return Finding(
        "T05",
        "Point-in-time debt (conceptual)",
        "High",
        "WARN",
        "Current MVP uses constant illustrative debt — flag as model limitation / incomplete PIT.",
        None,
    )


def test_loss_sim_sanity(losses: pd.DataFrame) -> Finding:
    if losses.empty:
        return Finding("T06", "Loss sim non-empty", "Critical", "FAIL", "No simulations")
    if (losses["loss"] < 0).any():
        return Finding("T06", "Loss non-negative", "Critical", "FAIL", "Negative losses found")
    p99 = float(losses["loss"].quantile(0.99))
    mean = float(losses["loss"].mean())
    status = "PASS" if p99 >= mean else "FAIL"
    return Finding("T06", "Loss tail above mean", _sev(status), status, f"mean={mean:.0f}, p99={p99:.0f}", p99)


def test_concentration(dd: pd.DataFrame) -> Finding:
    if dd.empty:
        return Finding("T07", "Universe coverage", "Medium", "FAIL", "Empty panel")
    n = dd["ticker"].nunique()
    status = "PASS" if n >= 5 else "WARN"
    return Finding("T07", "Minimum name coverage", "Low" if status == "WARN" else "Info", status, f"n_tickers={n}", float(n))


def run_all_tests(dd: pd.DataFrame, losses: pd.DataFrame) -> pd.DataFrame:
    findings = [
        test_pd_bounds(dd),
        test_dd_pd_monotonic(dd),
        test_irb_monotonicity(),
        test_stability_rolling(dd),
        test_leakage_placeholder(),
        test_loss_sim_sanity(losses),
        test_concentration(dd),
    ]
    return pd.DataFrame([asdict(f) for f in findings])
