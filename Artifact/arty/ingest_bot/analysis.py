"""Lightweight analysis utilities for ingest_bot records.

Provides functions to compute daily pct change, simple moving averages, bias,
volatility, and a naive next-step prediction.

CLI: python -m ingest_bot.analysis --records-file path/to/records.json [--sma 3 --sma 7] [--predict-window 3] [--save-report path]
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd


def load_records(path: Path) -> List[dict]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data


def records_to_df(records: List[dict]) -> pd.DataFrame:
    df = pd.DataFrame(records)
    if "timestamp" not in df.columns:
        raise ValueError("records must contain 'timestamp' field")
    # ensure timestamp is parsed and set as index
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp").sort_index()

    # ensure close price exists
    if "close" not in df.columns:
        raise ValueError("records must contain 'close' field for price analysis")

    # coerce close to float
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    return df


def add_indicators(df: pd.DataFrame, sma_windows: List[int]) -> pd.DataFrame:
    df = df.copy()
    df["pct_change"] = df["close"].pct_change()
    df["log_return"] = np.log(df["close"]/df["close"].shift(1))

    for w in sma_windows:
        col = f"sma_{w}"
        df[col] = df["close"].rolling(window=w, min_periods=1).mean()
        df[f"bias_{w}"] = (df["close"] - df[col]) / df[col]
    return df


def summarize(df: pd.DataFrame, lookback: int = 7) -> dict:
    last = df.iloc[-1]
    recent = df.tail(lookback)
    mean_pct = recent["pct_change"].mean()
    vol = recent["pct_change"].std()
    return {
        "last_close": float(last["close"]),
        "last_timestamp": str(last.name),
        "mean_pct_change": float(mean_pct) if not pd.isna(mean_pct) else None,
        "volatility": float(vol) if not pd.isna(vol) else None,
        "count": int(len(df)),
    }


def predict_next(df: pd.DataFrame, window: int = 3) -> dict:
    # Simple prediction: use mean pct change over window to forecast next close
    recent = df["pct_change"].dropna().tail(window)
    if recent.empty:
        return {"predicted_close": None, "expected_pct_change": None}
    mean_pct = float(recent.mean())
    last_close = float(df["close"].iloc[-1])
    predicted = last_close * (1 + mean_pct)
    return {"predicted_close": predicted, "expected_pct_change": mean_pct}


# Import heavy ML models lazily inside functions to avoid importing sklearn at module import time
from .backtest import evaluate_predictions
import matplotlib.pyplot as plt


def _save_plot(df, dest: Path, name: str):
    dest.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df.index, df['close'], label='close')
    if 'sma_3' in df.columns:
        ax.plot(df.index, df['sma_3'], label='sma_3')
    if 'sma_7' in df.columns:
        ax.plot(df.index, df['sma_7'], label='sma_7')
    ax.legend()
    fig.autofmt_xdate()
    out = dest / f"{name}.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def analyze_records(
    path: Path,
    sma_windows: Optional[List[int]] = None,
    lookback: int = 7,
    predict_window: int = 3,
    run_models: Optional[list] = None,
    save_plots_to: Optional[Path] = None,
) -> dict:
    if sma_windows is None:
        sma_windows = [3, 7]
    if run_models is None:
        run_models = ['linear', 'arima']

    records = load_records(path)
    df = records_to_df(records)
    df = add_indicators(df, sma_windows)
    summary = summarize(df, lookback=lookback)

    # Run prediction models
    series = df['close']
    preds = {}
    evals = {}
    for m in run_models:
        if m == 'linear':
            from .models import linear_regression_predict
            p = linear_regression_predict(series)
        elif m == 'arima':
            from .models import arima_predict
            p = arima_predict(series)
        elif m == 'rf':
            from .models import random_forest_predict
            p = random_forest_predict(series)
        else:
            continue
        preds[m] = p

    # produce in-sample one-step predictions for backtest evaluation (naive approach)
    # build a predictions series by rolling-fit simple models (for speed use last-window linear)
    pred_series = pd.Series(index=series.index, dtype=float)
    # simple: use linear regression with lag=3 to predict each point after warmup
    lags = 3
    x, y = None, None
    for i in range(lags, len(series)):
        window = series.iloc[:i]
        res = linear_regression_predict(window, lags=3)
        pred_series.iloc[i] = res['predicted_close']

    evals['in_sample_linear'] = evaluate_predictions(series, pred_series)

    # Save plot if requested
    plot_path = None
    equity_plot = None
    drawdown_plot = None
    surface_plot = None
    if save_plots_to is not None:
        plot_path = _save_plot(df, save_plots_to, path.stem)

        # compute parameter surface and save as part of report
        try:
            grid = parameter_surface(df['close'], lambda p: linear_factory(p), {'lags': list(range(1,8)), 'train': [10,20,30]}, train_window=30)
            # serialize numeric grid
            import numpy as _np
            grid_serializable = {'x': grid['x'], 'y': grid['y'], 'z': _np.nan_to_num(grid['z']).tolist()}
        except Exception:
            grid_serializable = None
    else:
        grid_serializable = None

    # Walk-forward backtest using a simple linear model factory
    def linear_factory(params):
        def _model_fn(train_series):
            from .models import linear_regression_predict
            out = linear_regression_predict(train_series, lags=params.get('lags', 3))
            return out['predicted_close']
        return _model_fn

    from .backtest import walk_forward_backtest, parameter_surface
    wfb = walk_forward_backtest(df['close'], model_fn_callable=linear_factory({'lags':3}), train_window=10)

    # generate equity and drawdown plots
    if save_plots_to is not None:
        save_plots_to.mkdir(parents=True, exist_ok=True)
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10,4))
        wfb['equity'].plot(ax=ax, title='Equity Curve')
        fig.autofmt_xdate()
        equity_plot = save_plots_to / f"{path.stem}_equity.png"
        fig.savefig(equity_plot)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(10,4))
        wfb['drawdown'].plot(ax=ax, title='Drawdown', color='red')
        fig.autofmt_xdate()
        drawdown_plot = save_plots_to / f"{path.stem}_drawdown.png"
        fig.savefig(drawdown_plot)
        plt.close(fig)

        # parameter surface example: lags x train_window
        grid = parameter_surface(df['close'], lambda p: linear_factory({'lags': p['lags']}), {'lags': list(range(1,6)), 'train': [10]}, train_window=30)
        try:
            from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
            import numpy as np
            X, Y = np.meshgrid(grid['x'], grid['y'])
            Z = grid['z'].T
            fig = plt.figure(figsize=(8,6))
            ax = fig.add_subplot(111, projection='3d')
            ax.plot_surface(X, Y, Z, cmap='viridis')
            ax.set_xlabel('lags')
            ax.set_ylabel('train')
            ax.set_zlabel('total_return')
            surface_plot = save_plots_to / f"{path.stem}_surface.png"
            fig.savefig(surface_plot)
            plt.close(fig)
        except Exception:
            surface_plot = None

    # bias summary
    bias = {}
    for w in sma_windows:
        bcol = f"bias_{w}"
        bias[f"bias_{w}"] = float(df[bcol].iloc[-1]) if bcol in df.columns else None

    out = {
        "summary": summary,
        "predictions": preds,
        "evals": evals,
        "bias": bias,
        "last_rows": df.tail(10).reset_index().to_dict(orient="records"),
        "plot": str(plot_path) if plot_path is not None else None,
    }
    return out


def _format_report(report: dict) -> str:
    s = report["summary"]
    p = report["prediction"]
    b = report["bias"]

    lines = [
        f"Last timestamp: {s['last_timestamp']}",
        f"Last close: {s['last_close']:.6f}",
        f"Mean pct change ({s['count']} points): {s['mean_pct_change']:.6%}" if s["mean_pct_change"] is not None else "Mean pct change: N/A",
        f"Volatility (std pct change): {s['volatility']:.6%}" if s["volatility"] is not None else "Volatility: N/A",
        f"Prediction (next close): {p['predicted_close']:.6f} (expected pct {p['expected_pct_change']:.6%})" if p["predicted_close"] is not None else "Prediction: N/A",
    ]
    for k, v in b.items():
        lines.append(f"{k}: {v:.6%}" if v is not None else f"{k}: N/A")
    lines.append("\nLast rows:")
    for r in report["last_rows"]:
        lines.append(f"{r['timestamp']}: close={r['close']}, pct_change={r.get('pct_change')}")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:  # pragma: no cover - simple CLI
    import argparse

    p = argparse.ArgumentParser(description="Analyze ingest_bot records")
    p.add_argument("--records-file", type=Path, required=True)
    p.add_argument("--sma", type=int, action="append", help="SMA window (can specify multiple)")
    p.add_argument("--lookback", type=int, default=7)
    p.add_argument("--predict-window", type=int, default=3)
    p.add_argument("--save-report", type=Path, help="Optional path to save JSON report")
    p.add_argument("--save-plots-dir", type=Path, help="Directory to save generated plots")

    args = p.parse_args(argv)

    report = analyze_records(
        args.records_file,
        sma_windows=args.sma or [3, 7],
        lookback=args.lookback,
        predict_window=args.predict_window,
        run_models=['linear','arima','rf'],
        save_plots_to=args.save_plots_dir,
    )
    print(_format_report(report))
    if args.save_report:
        with args.save_report.open("w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
