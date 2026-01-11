"""Charting utilities for Syndicate

Provides functions to detect support/resistance (swing lows/highs),
trendlines, and render annotated charts with matplotlib.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


@dataclass
class Line:
    x: Tuple[float, float]
    y: Tuple[float, float]


def detect_swings(prices: pd.Series, window: int = 5) -> Tuple[List[int], List[int]]:
    """Detect swing highs and lows indices in a price series.

    A swing high is a point higher than the `window` points on each side.
    A swing low is a point lower than the `window` points on each side.

    Returns (lows_idx, highs_idx) as sorted lists of integer positions (0-based).
    """
    highs = []
    lows = []
    n = len(prices)
    for i in range(window, n - window):
        window_slice = prices.iloc[i - window : i + window + 1]
        val = prices.iloc[i]
        if val == window_slice.max() and (window_slice == val).sum() == 1:
            highs.append(int(i))
        if val == window_slice.min() and (window_slice == val).sum() == 1:
            lows.append(int(i))
    return lows, highs


def fit_trendline(x: List[int], y: List[float]) -> Line:
    """Fit a simple linear trendline through provided points and return endpoints across the full x range."""
    if len(x) < 2:
        # degenerate: return a flat line at the mean
        mean_y = float(np.mean(y)) if len(y) > 0 else 0.0
        return Line(x=(min(x) if x else 0, max(x) if x else 0), y=(mean_y, mean_y))

    # linear fit
    coeffs = np.polyfit(x, y, 1)
    a, b = coeffs
    x0, x1 = min(x), max(x)
    return Line(x=(x0, x1), y=(a * x0 + b, a * x1 + b))


def generate_annotated_chart(
    dates: pd.Series,
    prices: pd.Series,
    out_path: Path,
    window: int = 5,
    annotate_swings: bool = True,
    show_trendlines: bool = True,
    figsize: Tuple[int, int] = (10, 6),
    dpi: int = 150,
) -> dict:
    """Generate a PNG chart with support/resistance and trendlines.

    Returns metadata dict with swing indices and trendline endpoints.
    """
    # Normalize inputs to Series for robust indexing
    dates = pd.Series(dates).reset_index(drop=True)
    prices = pd.Series(prices).reset_index(drop=True)

    if len(dates) != len(prices):
        raise ValueError("dates and prices length mismatch")

    lows_idx, highs_idx = detect_swings(prices, window=window)

    # Fit trendlines on swing highs and lows
    low_line = fit_trendline(lows_idx, prices.iloc[lows_idx].tolist()) if lows_idx else None
    high_line = fit_trendline(highs_idx, prices.iloc[highs_idx].tolist()) if highs_idx else None

    # Plot
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.plot(dates, prices, color="black", linewidth=1.0)

    if annotate_swings:
        if lows_idx:
            ax.scatter(dates.iloc[lows_idx], prices.iloc[lows_idx], color="green", marker="o", label="swing low")
        if highs_idx:
            ax.scatter(dates.iloc[highs_idx], prices.iloc[highs_idx], color="red", marker="^", label="swing high")

    if show_trendlines:
        if low_line is not None and len(lows_idx) >= 2:
            ax.plot([dates.iloc[int(low_line.x[0])], dates.iloc[int(low_line.x[1])]], [low_line.y[0], low_line.y[1]], color="green", linestyle="--", linewidth=1.0, label="support")
        if high_line is not None and len(highs_idx) >= 2:
            ax.plot([dates.iloc[int(high_line.x[0])], dates.iloc[int(high_line.x[1])]], [high_line.y[0], high_line.y[1]], color="red", linestyle="--", linewidth=1.0, label="resistance")

    ax.set_title("Price with annotations")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    fig.autofmt_xdate()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out_path), bbox_inches="tight")
    plt.close(fig)

    meta = {
        "swings": {"lows": lows_idx, "highs": highs_idx},
        "trendlines": {
            "support": (list(low_line.x), list(low_line.y)) if low_line else None,
            "resistance": (list(high_line.x), list(high_line.y)) if high_line else None,
        },
    }
    return meta
