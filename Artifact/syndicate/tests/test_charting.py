import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Ensure project root is importable
proj_root = Path(__file__).resolve().parents[1]
if str(proj_root) not in sys.path:
    sys.path.insert(0, str(proj_root))

from scripts.charting import detect_swings, generate_annotated_chart


def make_synthetic_series(n=200):
    dates = pd.date_range(end=pd.Timestamp("2026-01-11"), periods=n)
    t = np.linspace(0, 6 * np.pi, n)
    prices = 100 + 2 * np.sin(t) + 0.2 * np.arange(n)  # uptrending with oscillation
    return dates, pd.Series(prices)


def test_detect_swings_returns_points():
    dates, prices = make_synthetic_series(100)
    lows, highs = detect_swings(prices, window=3)
    assert isinstance(lows, list)
    assert isinstance(highs, list)
    # should find some swings
    assert len(lows) > 0
    assert len(highs) > 0


def test_generate_annotated_chart_creates_file(tmp_path):
    dates, prices = make_synthetic_series(150)
    out = tmp_path / "chart.png"
    meta = generate_annotated_chart(dates, prices, out_path=out, window=4)
    assert out.exists()
    assert out.stat().st_size > 1000
    # metadata keys
    assert "swings" in meta and "trendlines" in meta
    assert isinstance(meta["swings"]["lows"], list)
    assert isinstance(meta["swings"]["highs"], list)
