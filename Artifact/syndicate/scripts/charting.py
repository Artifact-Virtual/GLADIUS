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


def _point_line_distance(x0: float, y0: float, a: float, b: float) -> float:
    """Distance from point (x0,y0) to line y = a*x + b"""
    # For line ax - y + b = 0, distance = |a*x0 - 1*y0 + b| / sqrt(a^2 + 1)
    return abs(a * x0 - y0 + b) / np.sqrt(a * a + 1)


def detect_trendlines_ransac(x: List[int], y: List[float], max_lines: int = 2, threshold: float = 0.5, min_support: int = 3, iterations: int = 200) -> List[Tuple[Line, List[int]]]:
    """Detect multiple trendlines using a simple RANSAC-like approach.

    Args:
        x, y: lists of point coordinates (x indices and y values)
        max_lines: maximum number of lines to return
        threshold: distance threshold (in price units) to consider an inlier
        min_support: minimal number of inliers to accept a line
        iterations: number of random samples per line

    Returns:
        List of tuples: (Line, inlier_indices)
    """
    pts = list(zip(list(x), list(y)))
    remaining = pts.copy()
    results: List[Tuple[Line, List[int]]] = []

    # Work on index-space remapped to original indices
    original_indices = list(x)

    while remaining and len(results) < max_lines and len(remaining) >= min_support:
        best_inliers: List[int] = []
        best_line: Line = None

        for _ in range(iterations):
            # pick two distinct points
            if len(remaining) < 2:
                break
            i1, i2 = np.random.choice(len(remaining), size=2, replace=False)
            (x1, y1), (x2, y2) = remaining[i1], remaining[i2]
            if x2 == x1:
                continue
            # slope and intercept
            a = (y2 - y1) / (x2 - x1)
            b = y1 - a * x1
            # find inliers
            inliers = []
            for idx, (xx, yy) in enumerate(remaining):
                d = _point_line_distance(xx, yy, a, b)
                if d <= threshold:
                    inliers.append(idx)
            if len(inliers) > len(best_inliers):
                best_inliers = inliers
                best_line = Line(x=(min([remaining[i][0] for i in inliers]), max([remaining[i][0] for i in inliers])), y=(a * min([remaining[i][0] for i in inliers]) + b, a * max([remaining[i][0] for i in inliers]) + b))

        if best_line is None or len(best_inliers) < min_support:
            break

        # Map inliers back to original indices
        inlier_points = [remaining[i] for i in best_inliers]
        inlier_idxs = [original_indices.index(p[0]) for p in inlier_points]
        results.append((best_line, inlier_idxs))

        # Remove inliers from remaining
        new_remaining = [p for i, p in enumerate(remaining) if i not in best_inliers]
        remaining = new_remaining

    return results


def angle_degrees(line: Line) -> float:
    """Return angle in degrees of the trendline (positive = upward)"""
    dx = line.x[1] - line.x[0]
    dy = line.y[1] - line.y[0]
    if dx == 0:
        return 90.0
    return float(np.degrees(np.arctan2(dy, dx)))


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
        # Use RANSAC to detect multiple trendlines for highs and lows
        try:
            low_trendlines = detect_trendlines_ransac(lows_idx, prices.iloc[lows_idx].tolist(), max_lines=2, threshold=0.5, min_support=2)
        except Exception:
            low_trendlines = []
        try:
            high_trendlines = detect_trendlines_ransac(highs_idx, prices.iloc[highs_idx].tolist(), max_lines=2, threshold=0.5, min_support=2)
        except Exception:
            high_trendlines = []

        # Plot RANSAC trendlines and annotate with angle and price
        for idx, (ln, inliers) in enumerate(low_trendlines):
            x_pts = [dates.iloc[int(ln.x[0])], dates.iloc[int(ln.x[1])]]
            y_pts = [ln.y[0], ln.y[1]]
            ax.plot(x_pts, y_pts, color="green", linestyle="--", linewidth=1.0, label=f"support_{idx+1}")
            ang = angle_degrees(ln)
            ax.text(x_pts[-1], y_pts[-1], f"S{idx+1}: {y_pts[-1]:.2f} ({ang:.1f}°)", color="green", fontsize=8, ha="right", va="bottom")

        for idx, (ln, inliers) in enumerate(high_trendlines):
            x_pts = [dates.iloc[int(ln.x[0])], dates.iloc[int(ln.x[1])]]
            y_pts = [ln.y[0], ln.y[1]]
            ax.plot(x_pts, y_pts, color="red", linestyle="--", linewidth=1.0, label=f"resistance_{idx+1}")
            ang = angle_degrees(ln)
            ax.text(x_pts[-1], y_pts[-1], f"R{idx+1}: {y_pts[-1]:.2f} ({ang:.1f}°)", color="red", fontsize=8, ha="right", va="top")

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
