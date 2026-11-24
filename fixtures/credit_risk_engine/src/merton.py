from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import root_scalar
from scipy.stats import norm


def merton_equity_value(V: float, D: float, T: float, r: float, sigma_v: float) -> float:
    """Black–Scholes–Merton equity as call on assets."""
    if V <= 0 or sigma_v <= 0 or T <= 0:
        return np.nan
    d1 = (np.log(V / D) + (r + 0.5 * sigma_v**2) * T) / (sigma_v * np.sqrt(T))
    d2 = d1 - sigma_v * np.sqrt(T)
    return V * norm.cdf(d1) - D * np.exp(-r * T) * norm.cdf(d2)


def implied_asset_value(
    E: float, D: float, T: float, r: float, sigma_e: float, sigma_v_guess: float | None = None
) -> tuple[float, float]:
    """
    Solve for asset value V and asset vol sigma_v given equity value/vol (KMV-style iteration lite).
    Uses the relationship sigma_e * E = N(d1) * sigma_v * V.
    """
    if E <= 0 or D <= 0:
        return np.nan, np.nan
    sigma_v = sigma_v_guess or max(sigma_e * E / (E + D), 0.05)

    for _ in range(50):
        def f(V):
            return merton_equity_value(V, D, T, r, sigma_v) - E

        try:
            sol = root_scalar(f, bracket=[E * 0.5, E + D * 3])
            V = sol.root
        except Exception:
            V = E + D
        d1 = (np.log(V / D) + (r + 0.5 * sigma_v**2) * T) / (sigma_v * np.sqrt(T))
        delta = norm.cdf(d1)
        if delta <= 1e-8 or V <= 0:
            break
        sigma_v_new = sigma_e * E / (delta * V)
        if abs(sigma_v_new - sigma_v) < 1e-6:
            sigma_v = sigma_v_new
            break
        sigma_v = 0.5 * sigma_v + 0.5 * sigma_v_new
    return float(V), float(sigma_v)


def distance_to_default(V: float, D: float, T: float, r: float, sigma_v: float) -> float:
    if V <= 0 or sigma_v <= 0 or T <= 0:
        return np.nan
    return (np.log(V / D) + (r - 0.5 * sigma_v**2) * T) / (sigma_v * np.sqrt(T))


def dd_to_pd(dd: float) -> float:
    """Risk-neutral / normal mapping (simplified — not Moody's EDF empirical mapping)."""
    if np.isnan(dd):
        return np.nan
    return float(norm.cdf(-dd))


def panel_dd_from_equity(
    prices: pd.DataFrame,
    debt: pd.Series,
    r: float = 0.03,
    T: float = 1.0,
    vol_window: int = 252,
) -> pd.DataFrame:
    """
    prices: wide daily equity prices
    debt: face debt by ticker (constant)
    """
    rets = prices.pct_change()
    rows = []
    for ticker in prices.columns:
        D = float(debt.get(ticker, np.nan))
        if not np.isfinite(D) or D <= 0:
            continue
        px = prices[ticker].dropna()
        if len(px) < vol_window + 5:
            continue
        for i in range(vol_window, len(px)):
            window = px.iloc[i - vol_window : i]
            E = float(window.iloc[-1])
            sigma_e = float(window.pct_change().std() * np.sqrt(252))
            if not np.isfinite(sigma_e) or sigma_e <= 0:
                continue
            # Scale: treat price as index; use market-cap proxy = price (relative DD still informative)
            # For demo: assume shares=1e6 so E_market = price * 1e6; debt already in same units.
            E_mkt = E * 1_000_000
            V, sig_v = implied_asset_value(E_mkt, D, T, r, sigma_e)
            dd = distance_to_default(V, D, T, r, sig_v)
            rows.append(
                {
                    "date": px.index[i],
                    "ticker": ticker,
                    "equity_px": E,
                    "sigma_e": sigma_e,
                    "V": V,
                    "sigma_v": sig_v,
                    "DD": dd,
                    "PD": dd_to_pd(dd),
                }
            )
    return pd.DataFrame(rows)
