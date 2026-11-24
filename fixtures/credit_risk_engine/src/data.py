from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache"


def load_equity_panel(tickers: list[str] | None = None, start: str = "2018-01-01") -> pd.DataFrame:
    CACHE.mkdir(parents=True, exist_ok=True)
    out = CACHE / "equity_panel.csv"
    tickers = tickers or ["AAPL", "MSFT", "JPM", "XOM", "WMT", "BA", "GE", "F", "T", "INTC"]
    try:
        import yfinance as yf

        data = yf.download(tickers, start=start, auto_adjust=True, progress=False, threads=True)
        px = data["Close"] if isinstance(data.columns, pd.MultiIndex) else data
        px = px.dropna(how="all").ffill().dropna()
        px.to_csv(out)
        return px
    except Exception:
        if out.exists():
            return pd.read_csv(out, index_col=0, parse_dates=True)
        rng = np.random.default_rng(0)
        dates = pd.date_range(start, periods=1500, freq="B")
        px = pd.DataFrame(
            {t: 100 * np.exp(np.cumsum(rng.normal(0.0003, 0.02, len(dates)))) for t in tickers},
            index=dates,
        )
        px.to_csv(out)
        return px


def illustrative_debt_face(tickers: list[str]) -> pd.Series:
    """
    Illustrative debt face values in USD (not live EDGAR pulls).
    Documented as demo inputs so DD is computable without WRDS.
    """
    # Rough ballpark faces so DD is in a sensible range vs price*1e6 equity proxy
    base = {
        "AAPL": 1.0e11,
        "MSFT": 8.0e10,
        "JPM": 3.0e11,
        "XOM": 5.0e10,
        "WMT": 6.0e10,
        "BA": 5.5e10,
        "GE": 7.0e10,
        "F": 1.4e11,
        "T": 1.3e11,
        "INTC": 5.0e10,
    }
    return pd.Series({t: base.get(t, 5.0e10) for t in tickers})
