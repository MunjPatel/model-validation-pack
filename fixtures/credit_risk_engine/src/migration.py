from __future__ import annotations

import numpy as np
import pandas as pd

# Illustrative one-year letter-rating migration matrix (rows=from, cols=to), including default.
# Numbers are rounded educational approximations — not an agency proprietary matrix.
RATINGS = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "D"]

MIGRATION = np.array(
    [
        [0.9081, 0.0833, 0.0068, 0.0006, 0.0002, 0.0000, 0.0000, 0.0010],
        [0.0070, 0.9065, 0.0779, 0.0064, 0.0006, 0.0004, 0.0002, 0.0010],
        [0.0009, 0.0227, 0.9105, 0.0552, 0.0074, 0.0026, 0.0001, 0.0006],
        [0.0002, 0.0033, 0.0595, 0.8697, 0.0530, 0.0117, 0.0012, 0.0014],
        [0.0003, 0.0014, 0.0067, 0.0773, 0.8053, 0.0884, 0.0100, 0.0106],
        [0.0000, 0.0011, 0.0024, 0.0043, 0.0648, 0.8346, 0.0407, 0.0521],
        [0.0022, 0.0000, 0.0022, 0.0130, 0.0238, 0.1124, 0.6486, 0.1978],
        [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 1.0000],
    ]
)


def normalize_rows(m: np.ndarray) -> np.ndarray:
    m = m.astype(float).copy()
    m = m / m.sum(axis=1, keepdims=True)
    return m


def simulate_losses(
    n_obligors: int = 500,
    horizon_years: int = 1,
    lgd_mean: float = 0.45,
    lgd_std: float = 0.15,
    rating_weights: dict | None = None,
    seed: int = 42,
    n_sims: int = 2000,
) -> pd.DataFrame:
    """
    Incidence × severity (SOA-style framing): default incidence from migrations × LGD severity.
    """
    rng = np.random.default_rng(seed)
    m = normalize_rows(MIGRATION)
    weights = rating_weights or {
        "AAA": 0.05,
        "AA": 0.10,
        "A": 0.20,
        "BBB": 0.30,
        "BB": 0.20,
        "B": 0.10,
        "CCC": 0.05,
    }
    start_ratings = list(weights.keys())
    p = np.array([weights[r] for r in start_ratings])
    p = p / p.sum()
    start_idx = [RATINGS.index(r) for r in start_ratings]

    portfolio = rng.choice(start_idx, size=n_obligors, p=p)
    ead = rng.lognormal(mean=np.log(1_000_000), sigma=0.5, size=n_obligors)

    losses = []
    for _ in range(n_sims):
        state = portfolio.copy()
        for _y in range(horizon_years):
            new_state = np.empty_like(state)
            for i, s in enumerate(state):
                new_state[i] = rng.choice(len(RATINGS), p=m[s])
            state = new_state
        defaulted = state == RATINGS.index("D")
        lgds = np.clip(rng.normal(lgd_mean, lgd_std, n_obligors), 0.05, 0.95)
        loss = float((defaulted * lgds * ead).sum())
        n_def = int(defaulted.sum())
        losses.append({"loss": loss, "defaults": n_def, "default_rate": n_def / n_obligors})
    return pd.DataFrame(losses)
