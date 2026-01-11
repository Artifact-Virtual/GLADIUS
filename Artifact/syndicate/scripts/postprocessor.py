#!/usr/bin/env python3
"""Post-processing for generated reports.

- Extract tickers from content using frontmatter utilities
- Fetch price series via yfinance
- Generate annotated charts and write metadata files
- Increment Prometheus counters for charts/reports
"""
from pathlib import Path
import json
import logging
from datetime import timedelta, datetime

import yfinance as yf
import pandas as pd

from scripts.frontmatter import extract_tags_from_content, detect_type
from scripts.charting import generate_annotated_chart

log = logging.getLogger("postprocessor")

# Lazy import metrics counters to avoid hard dependency in tests
try:
    from scripts.metrics import charts_generated_total, reports_generated_total
except Exception:
    charts_generated_total = None
    reports_generated_total = None


def _choose_tickers(content: str):
    tags = extract_tags_from_content(content)
    # Prefer SPY if no explicit tickers found
    tickers = [t for t in tags if len(t) <= 6]
    if not tickers:
        return ["^GSPC"]
    return tickers[:2]


def fetch_price_series(ticker: str, period_days: int = 90) -> pd.Series:
    # Use yfinance to get close prices
    try:
        df = yf.download(ticker, period=f"{period_days}d", progress=False)
        if df is None or df.empty:
            raise RuntimeError("No data")
        return df["Close"].dropna()
    except Exception as e:
        log.exception("Failed to fetch data for %s: %s", ticker, e)
        return pd.Series([], dtype=float)


def process_document(doc_path: str) -> dict:
    """Process a generated document and produce charts/metadata.

    Returns metadata dict with created chart paths.
    """
    p = Path(doc_path)
    if not p.exists():
        raise FileNotFoundError(doc_path)

    content = p.read_text(encoding="utf-8")
    doc_type = detect_type(p.name)

    # Only generate charts for report-like files
    if doc_type not in ("Pre-Market", "reports", "analysis", "analysis"):
        log.debug("Skipping chart generation for type: %s", doc_type)
        return {}

    tickers = _choose_tickers(content)
    charts = []
    for tkr in tickers:
        series = fetch_price_series(tkr, period_days=120)
        if series.empty:
            continue
        dates = series.index
        prices = series
        out_dir = p.parent / "charts"
        out_dir.mkdir(parents=True, exist_ok=True)
        safe_tkr = tkr.replace("^", "caret_").replace("=", "_")
        out_path = out_dir / f"{p.stem}_{safe_tkr}.png"
        meta = generate_annotated_chart(dates, prices, out_path)
        charts.append({"ticker": tkr, "path": str(out_path), "meta": meta})

        # Increment metric
        try:
            if charts_generated_total is not None:
                charts_generated_total.inc()
        except Exception:
            pass

    # increment reports metric
    try:
        if reports_generated_total is not None:
            reports_generated_total.inc()
    except Exception:
        pass

    # write metadata file
    if charts:
        meta_path = p.with_suffix(p.suffix + ".charts.json")
        meta_obj = {"generated_at": datetime.utcnow().isoformat() + "Z", "charts": charts}
        meta_path.write_text(json.dumps(meta_obj, indent=2), encoding="utf-8")

    return {"charts": charts}
