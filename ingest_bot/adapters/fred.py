"""FRED adapter.

Real implementation that uses `fredapi.Fred` if available and reads basic
configuration from the environment:

- FRED_API_KEY: optional API key for fredapi (if the client requires it)
- FRED_SERIES: comma-separated list of default series ids when none are provided

If the `fredapi` package is not installed, importing this module will succeed but
calling `fetch_since` will raise ImportError to make errors visible to users.
"""
from __future__ import annotations

import os
from datetime import datetime
from typing import Iterable, List, Optional

from fredapi import Fred  # import must succeed; ImportError will propagate if not installed


def _iter_series_items(series) -> Iterable:
    """Normalize returned series to an iterable of (timestamp, value)."""
    # pandas.Series: has items() that yields (ts, value)
    if hasattr(series, "items"):
        return list(series.items())
    # dict-like
    if isinstance(series, dict):
        return list(series.items())
    # fallback: attempt to iterate
    return list(series)


def fetch_since(timestamp: str, series_ids: Optional[Iterable[str]] = None) -> List[dict]:
    """Fetch new FRED observations since `timestamp`.

    If `series_ids` is None, this function will look at the `FRED_SERIES`
    environment variable (comma-separated) for defaults and raise ``ValueError``
    if none are configured.

    Raises:
      ImportError: if fredapi is not installed
      ValueError: if no series ids are supplied
    """
    if Fred is None:
        raise ImportError("fredapi is not installed; install fredapi to use the FRED adapter")

    if not series_ids:
        env = os.environ.get("FRED_SERIES")
        if not env:
            raise ValueError("series_ids must be provided or FRED_SERIES environment variable set")
        series_ids = [s.strip() for s in env.split(",") if s.strip()]

    api_key = os.environ.get("FRED_API_KEY")
    client = Fred(api_key) if api_key else Fred()

    out: List[dict] = []
    for sid in series_ids:
        series = client.get_series(sid, observation_start=timestamp)
        for t, v in _iter_series_items(series):
            if hasattr(t, "isoformat"):
                iso = t.isoformat()
            else:
                iso = str(t)
            out.append({"timestamp": iso, "series_id": sid, "value": float(v)})
    return out
