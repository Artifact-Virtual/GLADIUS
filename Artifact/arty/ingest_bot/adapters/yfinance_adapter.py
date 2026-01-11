"""YFinance adapter.

This adapter uses `yfinance` when available and reads default tickers from
`YFINANCE_TICKERS` environment variable (comma-separated) if none are supplied.
It attempts to be tolerant to different return types from `yfinance.download`,
so unit tests can mock its behaviour without requiring pandas.
"""
from __future__ import annotations

import os
from typing import Iterable, List, Optional

import yfinance as yf  # import must succeed; ImportError will propagate if not installed


def _iter_downloaded(df):
    """Yield (timestamp, row) pairs from different df-like objects."""
    if df is None:
        return
    if hasattr(df, "iterrows"):
        for idx, row in df.iterrows():
            yield idx, row
        return
    # dict-like: mapping timestamp -> row-dict
    if isinstance(df, dict):
        for idx, row in df.items():
            yield idx, row
        return
    # try items()
    if hasattr(df, "items"):
        for idx, row in df.items():
            yield idx, row
        return
    # fallback: nothing
    return


def fetch_since(timestamp: str, tickers: Optional[Iterable[str]] = None) -> List[dict]:
    if yf is None:
        raise ImportError("yfinance is not installed; install yfinance to use this adapter")

    if not tickers:
        env = os.environ.get("YFINANCE_TICKERS")
        if not env:
            raise ValueError("tickers must be provided or YFINANCE_TICKERS environment variable set")
        tickers = [t.strip() for t in env.split(",") if t.strip()]

    out: List[dict] = []
    # yfinance prefers a 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' start value; normalize
    start = timestamp
    try:
        # prefer date-only string to avoid time parsing issues
        from datetime import datetime

        dt = datetime.fromisoformat(timestamp)
        start = dt.date().isoformat()
    except Exception:
        # fallback: replace 'T' with space
        start = timestamp.replace("T", " ")

    for tk in tickers:
        df = yf.download(tk, start=start, progress=False)
        for idx, row in _iter_downloaded(df):
            ts = idx.isoformat() if hasattr(idx, "isoformat") else str(idx)
            open_v = row.get("Open") if isinstance(row, dict) else getattr(row, "Open", None)
            close_v = row.get("Close") if isinstance(row, dict) else getattr(row, "Close", None)
            out.append({
                "timestamp": ts,
                "ticker": tk,
                "open": None if open_v is None else float(open_v),
                "close": None if close_v is None else float(close_v),
            })
    return out
