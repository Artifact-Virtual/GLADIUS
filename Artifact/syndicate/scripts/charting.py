"""Charting utilities for Syndicate

Provides functions to detect support/resistance (swing lows/highs),
trendlines, and render annotated charts with matplotlib.

Enhanced with:
- RSI, ADX, ATR subplots
- Support/Resistance level annotations
- Trade setup zones
- Trend direction indicators
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from pathlib import Path
import os


@dataclass
class Line:
    x: Tuple[float, float]
    y: Tuple[float, float]


@dataclass
class TradeSetup:
    """Trade setup zone for chart annotation"""
    entry_price: float
    stop_loss: float
    target_1: float
    target_2: Optional[float] = None
    bias: str = "LONG"  # LONG or SHORT
    label: str = ""


@dataclass
class ChartAnnotations:
    """Collection of all chart annotations"""
    support_levels: List[float] = field(default_factory=list)
    resistance_levels: List[float] = field(default_factory=list)
    trendlines: List[Line] = field(default_factory=list)
    trade_setups: List[TradeSetup] = field(default_factory=list)
    key_levels: Dict[str, float] = field(default_factory=dict)  # e.g., {"20 DMA": 2650.0}
    regime: str = ""  # TRENDING, RANGING, VOLATILE
    adx_value: float = 0.0
    rsi_value: float = 0.0
    atr_value: float = 0.0


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


def detect_support_resistance(prices: pd.Series, window: int = 10, num_levels: int = 3) -> Tuple[List[float], List[float]]:
    """Detect horizontal support and resistance levels from price data.
    
    Uses swing highs/lows and clusters them to find key price levels.
    
    Returns (support_levels, resistance_levels) as sorted lists of price values.
    """
    lows_idx, highs_idx = detect_swings(prices, window=window)
    
    # Extract price values at swing points
    support_prices = [prices.iloc[i] for i in lows_idx] if lows_idx else []
    resistance_prices = [prices.iloc[i] for i in highs_idx] if highs_idx else []
    
    # Cluster similar price levels (within 0.5% of each other)
    def cluster_levels(levels: List[float], tolerance: float = 0.005) -> List[float]:
        if not levels:
            return []
        sorted_levels = sorted(levels)
        clusters = []
        current_cluster = [sorted_levels[0]]
        
        for level in sorted_levels[1:]:
            if abs(level - current_cluster[-1]) / current_cluster[-1] < tolerance:
                current_cluster.append(level)
            else:
                clusters.append(np.mean(current_cluster))
                current_cluster = [level]
        clusters.append(np.mean(current_cluster))
        
        # Return the most significant levels (touched most often)
        # For simplicity, return the levels closest to current price
        return sorted(clusters)[-num_levels:] if len(clusters) > num_levels else clusters
    
    support = cluster_levels(support_prices)
    resistance = cluster_levels(resistance_prices)
    
    return support, resistance


def determine_regime(adx: float, atr_pct: float) -> str:
    """Determine market regime based on ADX and ATR.
    
    Args:
        adx: ADX value (0-100)
        atr_pct: ATR as percentage of price
        
    Returns:
        "TRENDING", "RANGING", or "VOLATILE"
    """
    if adx > 25:
        return "TRENDING"
    elif atr_pct > 2.0:  # >2% daily range = volatile
        return "VOLATILE"
    else:
        return "RANGING"


def generate_enhanced_chart(
    df: pd.DataFrame,
    name: str,
    out_path: Path,
    annotations: Optional[ChartAnnotations] = None,
    show_indicators: bool = True,
    show_levels: bool = True,
    show_trade_setup: bool = True,
    figsize: Tuple[int, int] = (14, 10),
    dpi: int = 150,
    style: str = "nightclouds",
) -> Dict[str, Any]:
    """Generate an enhanced candlestick chart with technical indicators and annotations.
    
    Features:
    - Main price chart with candlesticks
    - SMA 50/200 overlays
    - Support/Resistance horizontal lines
    - RSI subplot (if available)
    - ADX subplot (if available)
    - Volume subplot
    - Trade setup zones (entry/SL/TP)
    - Trend direction indicators
    - Key price level annotations
    
    Args:
        df: DataFrame with OHLCV + indicators (RSI, ADX_14, ATR, SMA_50, SMA_200)
        name: Asset name for title
        out_path: Path to save the chart
        annotations: Optional ChartAnnotations with levels and setups
        show_indicators: Whether to show RSI/ADX subplots
        show_levels: Whether to show S/R levels
        show_trade_setup: Whether to show trade setup zones
        figsize: Figure size
        dpi: DPI for output
        style: mplfinance style name
        
    Returns:
        Metadata dict with detected levels and annotations
    """
    import matplotlib
    matplotlib.use(os.environ.get("MPLBACKEND", "Agg"))
    
    try:
        import mplfinance as mpf
    except ImportError:
        # Fallback to basic matplotlib chart
        return _generate_basic_chart(df, name, out_path, annotations, figsize, dpi)
    
    # Ensure required columns exist
    required = ["Open", "High", "Low", "Close"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    # Work with a copy to avoid modifying original
    plot_df = df.copy()
    
    # Prepare addplots list
    addplots = []
    
    # Check if volume is available first - this affects panel numbering
    has_volume = "Volume" in plot_df.columns and not plot_df["Volume"].isna().all()
    
    # Panel ratios: [main, volume (if present), RSI (if present), ADX (if present)]
    # When volume=True, mplfinance creates panels 0=main, 1=volume
    # Our addplots should use panel numbers starting after volume
    panel_ratios = [4]  # Main panel ratio
    if has_volume:
        panel_ratios.append(1)  # Volume panel ratio
    
    # Track which panel number to use for addplots
    next_panel = 1 if not has_volume else 2
    
    # --- Moving Averages (on main panel 0) ---
    if "SMA_50" in plot_df.columns and not plot_df["SMA_50"].isna().all():
        addplots.append(mpf.make_addplot(plot_df["SMA_50"], color="orange", width=1.0, panel=0))
    if "SMA_200" in plot_df.columns and not plot_df["SMA_200"].isna().all():
        addplots.append(mpf.make_addplot(plot_df["SMA_200"], color="blue", width=1.5, panel=0))
    
    # --- RSI Subplot ---
    if show_indicators and "RSI" in plot_df.columns and not plot_df["RSI"].isna().all():
        rsi_panel = next_panel
        next_panel += 1
        panel_ratios.append(1)
        rsi = plot_df["RSI"].fillna(50)  # Fill NaN with neutral
        addplots.append(mpf.make_addplot(rsi, panel=rsi_panel, color="purple", width=0.8, ylabel="RSI"))
        # Add overbought/oversold lines
        addplots.append(mpf.make_addplot([70] * len(plot_df), panel=rsi_panel, color="red", linestyle="--", width=0.5, secondary_y=False))
        addplots.append(mpf.make_addplot([30] * len(plot_df), panel=rsi_panel, color="green", linestyle="--", width=0.5, secondary_y=False))
    
    # --- ADX Subplot ---
    if show_indicators and "ADX_14" in plot_df.columns and not plot_df["ADX_14"].isna().all():
        adx_panel = next_panel
        next_panel += 1
        panel_ratios.append(1)
        adx = plot_df["ADX_14"].fillna(0)
        addplots.append(mpf.make_addplot(adx, panel=adx_panel, color="cyan", width=0.8, ylabel="ADX"))
        # Trend threshold line at 25
        addplots.append(mpf.make_addplot([25] * len(plot_df), panel=adx_panel, color="gray", linestyle="--", width=0.5))
        
        # DI+ and DI- if available
        if "DMP_14" in plot_df.columns:
            addplots.append(mpf.make_addplot(plot_df["DMP_14"].fillna(0), panel=adx_panel, color="green", width=0.5))
        if "DMN_14" in plot_df.columns:
            addplots.append(mpf.make_addplot(plot_df["DMN_14"].fillna(0), panel=adx_panel, color="red", width=0.5))
    
    # --- Detect Support/Resistance if not provided ---
    meta = {"name": name, "generated": True}
    support_levels = []
    resistance_levels = []
    
    if annotations:
        support_levels = annotations.support_levels
        resistance_levels = annotations.resistance_levels
    else:
        # Auto-detect from price data
        try:
            support_levels, resistance_levels = detect_support_resistance(plot_df["Close"], window=5, num_levels=3)
        except Exception:
            pass
    
    meta["support_levels"] = support_levels
    meta["resistance_levels"] = resistance_levels
    
    # --- Create horizontal lines for S/R levels ---
    hlines = {}
    if show_levels:
        all_levels = []
        colors = []
        linestyles = []
        linewidths = []
        
        for level in support_levels:
            all_levels.append(level)
            colors.append("green")
            linestyles.append("--")
            linewidths.append(1.0)
        
        for level in resistance_levels:
            all_levels.append(level)
            colors.append("red")
            linestyles.append("--")
            linewidths.append(1.0)
        
        if all_levels:
            hlines = dict(hlines=all_levels, colors=colors, linestyle=linestyles, linewidths=linewidths)
    
    # --- Generate the chart ---
    try:
        mpf_style = mpf.make_mpf_style(
            base_mpf_style=style,
            rc={"font.size": 8},
            gridcolor="gray",
            gridstyle=":",
            y_on_right=False
        )
        
        # Current price and indicator values for title
        current_price = float(plot_df["Close"].iloc[-1])
        
        # Safely extract indicator values
        def safe_float(series_or_val):
            try:
                if series_or_val is None:
                    return None
                val = float(series_or_val)
                if np.isnan(val) or np.isinf(val):
                    return None
                return val
            except (TypeError, ValueError):
                return None
        
        rsi_val = safe_float(plot_df["RSI"].iloc[-1]) if "RSI" in plot_df.columns else None
        adx_val = safe_float(plot_df["ADX_14"].iloc[-1]) if "ADX_14" in plot_df.columns else None
        atr_val = safe_float(plot_df["ATR"].iloc[-1]) if "ATR" in plot_df.columns else None
        
        # Build title with current values
        title_parts = [f"{name} | ${current_price:.2f}"]
        if rsi_val is not None:
            title_parts.append(f"RSI: {rsi_val:.1f}")
        if adx_val is not None:
            title_parts.append(f"ADX: {adx_val:.1f}")
        if atr_val is not None:
            atr_pct = (atr_val / current_price) * 100
            title_parts.append(f"ATR: {atr_val:.2f} ({atr_pct:.1f}%)")
        
        title = " | ".join(title_parts)
        
        # Determine regime
        if adx_val is not None and atr_val is not None:
            atr_pct = (atr_val / current_price) * 100
            regime = determine_regime(adx_val, atr_pct)
            title += f" | {regime}"
            meta["regime"] = regime
        
        meta["rsi"] = rsi_val
        meta["adx"] = adx_val
        meta["atr"] = atr_val
        meta["current_price"] = current_price
        
        # Plot kwargs
        plot_kwargs = {
            "type": "candle",
            "style": mpf_style,
            "title": title,
            "ylabel": "Price",
            "volume": has_volume,
            "figsize": figsize,
            "savefig": dict(fname=str(out_path), dpi=dpi, bbox_inches="tight"),
            "warn_too_much_data": 500,
        }
        
        # Set panel_ratios if we have multiple panels (volume and/or indicators)
        if len(panel_ratios) > 1:
            plot_kwargs["panel_ratios"] = tuple(panel_ratios)
        
        if addplots:
            plot_kwargs["addplot"] = addplots
        
        if hlines:
            plot_kwargs["hlines"] = hlines
        
        # Create the chart
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        mpf.plot(plot_df, **plot_kwargs)
        
        meta["chart_path"] = str(out_path)
        meta["success"] = True
        
    except Exception as e:
        meta["error"] = str(e)
        meta["success"] = False
        # Try fallback
        try:
            return _generate_basic_chart(df, name, out_path, annotations, figsize, dpi)
        except Exception:
            pass
    
    return meta


def _generate_basic_chart(
    df: pd.DataFrame,
    name: str,
    out_path: Path,
    annotations: Optional[ChartAnnotations] = None,
    figsize: Tuple[int, int] = (14, 10),
    dpi: int = 150,
) -> Dict[str, Any]:
    """Fallback basic chart using matplotlib only."""
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(3, 1, figsize=figsize, dpi=dpi, gridspec_kw={"height_ratios": [3, 1, 1]})
    ax_price, ax_rsi, ax_adx = axes
    
    # Price line
    ax_price.plot(df.index, df["Close"], color="white", linewidth=1.0, label="Close")
    
    # SMAs
    if "SMA_50" in df.columns:
        ax_price.plot(df.index, df["SMA_50"], color="orange", linewidth=0.8, label="SMA 50")
    if "SMA_200" in df.columns:
        ax_price.plot(df.index, df["SMA_200"], color="blue", linewidth=1.0, label="SMA 200")
    
    # Support/Resistance
    if annotations:
        for level in annotations.support_levels:
            ax_price.axhline(y=level, color="green", linestyle="--", alpha=0.7, label=f"S: {level:.2f}")
        for level in annotations.resistance_levels:
            ax_price.axhline(y=level, color="red", linestyle="--", alpha=0.7, label=f"R: {level:.2f}")
    
    ax_price.set_title(f"{name} | ${df['Close'].iloc[-1]:.2f}")
    ax_price.set_ylabel("Price")
    ax_price.legend(loc="upper left", fontsize=8)
    ax_price.set_facecolor("#1a1a2e")
    ax_price.grid(True, alpha=0.3)
    
    # RSI
    if "RSI" in df.columns:
        ax_rsi.plot(df.index, df["RSI"], color="purple", linewidth=0.8)
        ax_rsi.axhline(70, color="red", linestyle="--", alpha=0.5)
        ax_rsi.axhline(30, color="green", linestyle="--", alpha=0.5)
        ax_rsi.fill_between(df.index, 30, 70, alpha=0.1, color="gray")
        ax_rsi.set_ylabel("RSI")
        ax_rsi.set_ylim(0, 100)
    ax_rsi.set_facecolor("#1a1a2e")
    ax_rsi.grid(True, alpha=0.3)
    
    # ADX
    if "ADX_14" in df.columns:
        ax_adx.plot(df.index, df["ADX_14"], color="cyan", linewidth=0.8, label="ADX")
        ax_adx.axhline(25, color="gray", linestyle="--", alpha=0.5)
        if "DMP_14" in df.columns:
            ax_adx.plot(df.index, df["DMP_14"], color="green", linewidth=0.5, alpha=0.7, label="+DI")
        if "DMN_14" in df.columns:
            ax_adx.plot(df.index, df["DMN_14"], color="red", linewidth=0.5, alpha=0.7, label="-DI")
        ax_adx.set_ylabel("ADX")
        ax_adx.legend(loc="upper left", fontsize=7)
    ax_adx.set_facecolor("#1a1a2e")
    ax_adx.grid(True, alpha=0.3)
    
    fig.tight_layout()
    fig.patch.set_facecolor("#0d0d12")
    
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out_path), bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    
    return {
        "name": name,
        "chart_path": str(out_path),
        "success": True,
        "fallback": True,
    }


def add_trade_setup_to_chart(
    ax: plt.Axes,
    setup: TradeSetup,
    x_start: int,
    x_end: int,
    alpha: float = 0.2,
) -> None:
    """Add trade setup visualization to an existing axes.
    
    Draws entry zone, stop loss, and take profit levels.
    """
    if setup.bias == "LONG":
        # Entry to TP1 zone (green)
        height = setup.target_1 - setup.entry_price
        rect_tp = Rectangle((x_start, setup.entry_price), x_end - x_start, height,
                            facecolor="green", alpha=alpha, edgecolor="green", linewidth=0.5)
        ax.add_patch(rect_tp)
        
        # Entry to SL zone (red)
        height_sl = setup.entry_price - setup.stop_loss
        rect_sl = Rectangle((x_start, setup.stop_loss), x_end - x_start, height_sl,
                            facecolor="red", alpha=alpha, edgecolor="red", linewidth=0.5)
        ax.add_patch(rect_sl)
        
    else:  # SHORT
        # Entry to TP1 zone (green)
        height = setup.entry_price - setup.target_1
        rect_tp = Rectangle((x_start, setup.target_1), x_end - x_start, height,
                            facecolor="green", alpha=alpha, edgecolor="green", linewidth=0.5)
        ax.add_patch(rect_tp)
        
        # Entry to SL zone (red)
        height_sl = setup.stop_loss - setup.entry_price
        rect_sl = Rectangle((x_start, setup.entry_price), x_end - x_start, height_sl,
                            facecolor="red", alpha=alpha, edgecolor="red", linewidth=0.5)
        ax.add_patch(rect_sl)
    
    # Labels
    ax.axhline(setup.entry_price, color="white", linestyle="-", linewidth=0.8, alpha=0.8)
    ax.axhline(setup.stop_loss, color="red", linestyle=":", linewidth=0.8, alpha=0.8)
    ax.axhline(setup.target_1, color="green", linestyle=":", linewidth=0.8, alpha=0.8)
    
    if setup.target_2:
        ax.axhline(setup.target_2, color="lime", linestyle=":", linewidth=0.5, alpha=0.6)
    
    # Text annotations
    ax.text(x_end, setup.entry_price, f" Entry: {setup.entry_price:.2f}", fontsize=7, color="white", va="center")
    ax.text(x_end, setup.stop_loss, f" SL: {setup.stop_loss:.2f}", fontsize=7, color="red", va="center")
    ax.text(x_end, setup.target_1, f" TP1: {setup.target_1:.2f}", fontsize=7, color="green", va="center")
