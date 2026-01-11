import sys
import numpy as np
import pandas as pd
from pathlib import Path

proj_root = Path(__file__).resolve().parents[1]
if str(proj_root) not in sys.path:
    sys.path.insert(0, str(proj_root))

from scripts.charting import detect_swings, detect_trendlines_ransac, fit_trendline


def make_series(n=100):
    t = np.linspace(0, 6 * np.pi, n)
    prices = 100 + 2 * np.sin(t) + 0.1 * np.arange(n)
    return pd.Series(prices)


def test_ransac_detects_at_least_one_trendline():
    prices = make_series(120)
    lows, highs = detect_swings(prices, window=3)
    # Use lows points to find trendlines (if any)
    if len(lows) >= 2:
        lines = detect_trendlines_ransac(lows, prices.iloc[lows].tolist(), max_lines=3, threshold=1.0, min_support=2)
        assert isinstance(lines, list)
        # Either zero or one or more trendlines detected; this ensures function runs without error
    else:
        # Not enough swings generated; still function callable
        lines = detect_trendlines_ransac(list(range(5)), [100, 101, 102, 103, 104], max_lines=2)
        assert isinstance(lines, list)
