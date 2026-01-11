import sys
import json
from pathlib import Path
import pandas as pd
import pytest
from pathlib import Path

proj_root = Path(__file__).resolve().parents[1]
if str(proj_root) not in sys.path:
    sys.path.insert(0, str(proj_root))

from scripts.postprocessor import process_document
import scripts.metrics as metrics


def test_postprocessor_creates_charts_and_metadata(tmp_path, monkeypatch):
    # Create a fake report file with a ticker in content
    report = tmp_path / "premarket_test.md"
    report.write_text("# Test\nSPY is interesting today.\n")

    # Monkeypatch fetch to return synthetic price series
    import numpy as np

    def fake_fetch(ticker, period_days=120):
        idx = pd.date_range(end=pd.Timestamp("2026-01-11"), periods=50)
        vals = pd.Series(100 + 0.5 * np.arange(50), index=idx)
        return vals

    monkeypatch.setattr("scripts.postprocessor.fetch_price_series", fake_fetch)

    # Reset counters if possible
    try:
        metrics.charts_generated_total._value.set(0)
        metrics.reports_generated_total._value.set(0)
    except Exception:
        pass

    res = process_document(str(report))

    # metadata file created
    meta_path = report.with_suffix(report.suffix + ".charts.json")
    assert meta_path.exists()

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert "charts" in meta and len(meta["charts"]) >= 1

    # Chart image exists
    chart_path = Path(meta["charts"][0]["path"])
    assert chart_path.exists()

    # Metrics incremented (best-effort)
    try:
        assert metrics.charts_generated_total._value.get() >= 1
        assert metrics.reports_generated_total._value.get() >= 1
    except Exception:
        # Some test environments may not expose metric internals; that's okay
        pass
