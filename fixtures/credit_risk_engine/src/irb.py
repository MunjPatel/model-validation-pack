from __future__ import annotations

import numpy as np
from scipy.stats import norm


def corporate_r(pd: float) -> float:
    """Basel IRB asset correlation for corporate exposures (simplified public formula)."""
    pd = float(np.clip(pd, 1e-6, 0.999999))
    return 0.12 * (1 - np.exp(-50 * pd)) / (1 - np.exp(-50)) + 0.24 * (
        1 - (1 - np.exp(-50 * pd)) / (1 - np.exp(-50))
    )


def maturity_adjustment(pd: float, m: float) -> float:
    pd = float(np.clip(pd, 1e-6, 0.999999))
    b = (0.11852 - 0.05478 * np.log(pd)) ** 2
    return (1 + (m - 2.5) * b) / (1 - 1.5 * b)


def capital_requirement(pd: float, lgd: float, m: float = 2.5) -> float:
    """
    Basel II/III corporate IRB capital requirement K (simplified).
    K = LGD * [N((G(PD)-sqrt(R)*G(0.999))/sqrt(1-R)) - PD] * maturity_adj
    """
    pd = float(np.clip(pd, 0.0003, 0.999999))  # illustrative floor
    lgd = float(np.clip(lgd, 0.0, 1.0))
    r = corporate_r(pd)
    g_pd = norm.ppf(pd)
    g_999 = norm.ppf(0.999)
    # Basel corporate IRB: N( (G(PD) + sqrt(R)*G(0.999)) / sqrt(1-R) )
    conditional = norm.cdf((g_pd + np.sqrt(r) * g_999) / np.sqrt(1 - r))
    k = lgd * (conditional - pd) * maturity_adjustment(pd, m)
    return float(max(k, 0.0))


def risk_weight(pd: float, lgd: float, m: float = 2.5) -> float:
    """RW = 12.5 * K."""
    return 12.5 * capital_requirement(pd, lgd, m)


def rw_grid(pds=None, lgds=None, m: float = 2.5) -> dict:
    pds = pds or [0.001, 0.005, 0.01, 0.02, 0.05, 0.1]
    lgds = lgds or [0.25, 0.45, 0.65]
    grid = {}
    for lgd in lgds:
        grid[lgd] = {pd: risk_weight(pd, lgd, m) for pd in pds}
    return grid
