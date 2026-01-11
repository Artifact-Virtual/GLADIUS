"""Backtesting utilities for simple prediction-based strategies.

Provides functions to compute MSE, directional accuracy, and cumulative returns
if entering a position on predicted direction (long for positive predicted return).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict


def evaluate_predictions(series: pd.Series, predictions: pd.Series) -> Dict[str, float]:
    # predictions indexed same as series (one-step-ahead predictions aligned with actuals)
    df = pd.DataFrame({"actual": series, "pred": predictions}).dropna()
    if df.empty:
        return {"mse": float('nan'), "directional_accuracy": float('nan'), "strategy_return": float('nan')}

    mse = float(((df['actual'] - df['pred']) ** 2).mean())
    # directional accuracy
    dir_acc = float((np.sign(df['actual'].diff()) == np.sign(df['pred'].diff())).mean())
    # simple strategy: go long when predicted next > current, else hold cash
    returns = df['actual'].pct_change().shift(-1)  # return following day
    signals = (df['pred'] > df['actual']).astype(int)
    strat_ret = (signals * returns).dropna()
    cum = float((1 + strat_ret).prod() - 1) if not strat_ret.empty else 0.0
    return {"mse": mse, "directional_accuracy": dir_acc, "strategy_return": cum}


def compute_equity(returns: pd.Series, initial_capital: float = 1.0) -> pd.Series:
    """Compute equity curve from a returns series (percent returns, e.g., 0.01 = 1%)."""
    eq = (1 + returns.fillna(0)).cumprod() * initial_capital
    return eq


def compute_drawdown(equity: pd.Series) -> pd.Series:
    """Compute drawdown series from an equity curve."""
    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    return drawdown


def walk_forward_backtest(series: pd.Series, model_fn_callable, train_window: int = 100, test_window: int = 1, min_train: int = 20, transaction_cost: float = 0.0, position_size: float = 1.0) -> Dict:
    """Walk-forward backtest using a prediction function.

    model_fn_callable: function(series_train: pd.Series) -> predicted_next_value (float)
    transaction_cost: proportional cost applied on trade (e.g., 0.0005 = 0.05%)
    position_size: fraction of capital to allocate to the trade (0..1)

    Returns dict with predictions series, strategy returns, equity curve, drawdown series and metrics.
    """
    preds = pd.Series(index=series.index, dtype=float)
    n = len(series)
    for start in range(train_window, n):
        train_start = max(0, start - train_window)
        train_series = series.iloc[train_start:start]
        if len(train_series) < min_train:
            continue
        try:
            pred = model_fn_callable(train_series)
        except Exception:
            pred = None
        if pred is not None:
            preds.iloc[start] = pred

    # Signals: 1 if predicted > current price, else 0
    signals = (preds > series).astype(int)

    # next-day returns
    returns = series.pct_change().shift(-1)  # aligned: index i predicts return from i to i+1

    # compute trade costs: when entering a position (signal changes 0->1) or exiting (1->0)
    trades = signals.diff().abs().fillna(0)

    # apply position sizing and transaction costs
    # strategy return for each day = signal_prev * returns - trade_costs
    signal_prev = signals.shift(1).fillna(0)
    gross_returns = signal_prev * returns

    trade_costs = trades * transaction_cost * position_size

    strat_returns = (gross_returns * position_size - trade_costs).fillna(0)

    equity = compute_equity(strat_returns)
    dd = compute_drawdown(equity)
    metrics = {
        'total_return': float(equity.iloc[-1] - 1.0) if not equity.empty else 0.0,
        'max_drawdown': float(dd.min()) if not dd.empty else 0.0,
        'sharpe': float(strat_returns.mean() / strat_returns.std() * (252 ** 0.5)) if strat_returns.std() not in (0, None) else float('nan'),
        'transaction_cost': transaction_cost,
        'position_size': position_size,
    }
    return {'predictions': preds, 'returns': strat_returns, 'equity': equity, 'drawdown': dd, 'metrics': metrics}


def cross_validated_walk_forward(series: pd.Series, model_factory, param_grid: Dict[str, list], train_windows: list, min_train: int = 20, transaction_cost: float = 0.0, position_size: float = 1.0) -> Dict:
    """Perform walk-forward cross-validation over parameter grid.

    model_factory: callable(params) -> function(series_train) -> predicted next value
    param_grid: dict of parameter name -> list of values (supports multiple keys)
    train_windows: list of train_window values to test (outer hyperparam)

    Returns a dict of results keyed by parameter combinations with aggregated metrics.
    """
    import itertools
    results = {}

    keys = list(param_grid.keys())
    for combo in itertools.product(*[param_grid[k] for k in keys]):
        params = dict(zip(keys, combo))
        combo_key = ",".join(f"{k}={v}" for k, v in params.items())
        metrics_list = []
        for tw in train_windows:
            model_fn = model_factory(params)
            res = walk_forward_backtest(series, model_fn, train_window=tw, min_train=min_train, transaction_cost=transaction_cost, position_size=position_size)
            metrics_list.append(res['metrics'])
        # aggregate metrics
        agg = {}
        for m in metrics_list[0].keys():
            vals = [x[m] for x in metrics_list]
            agg[f"{m}_mean"] = float(pd.Series(vals).mean())
            agg[f"{m}_std"] = float(pd.Series(vals).std())
        results[combo_key] = agg
    return results


def parameter_surface(series: pd.Series, model_factory, param_grid: Dict[str, list], train_window: int = 100) -> Dict:
    """Evaluate performance over a grid of parameters.

    model_factory: callable(params) -> function(series_train) -> predicted value
    param_grid: dict of param_name -> list of values
    Returns dict with meshgrid (X,Y) and Z performance metric (e.g., total_return)
    """
    # simple 2D grid assumed (use first two keys)
    keys = list(param_grid.keys())
    if len(keys) < 2:
        raise ValueError('param_grid must contain at least two parameters for surface')
    xkey, ykey = keys[0], keys[1]
    xs = param_grid[xkey]
    ys = param_grid[ykey]
    import numpy as np
    Z = np.zeros((len(xs), len(ys)))

    for i, xv in enumerate(xs):
        for j, yv in enumerate(ys):
            params = {xkey: xv, ykey: yv}
            model_fn = model_factory(params)
            res = walk_forward_backtest(series, model_fn, train_window=train_window)
            Z[i, j] = res['metrics']['total_return']
    return {'x': xs, 'y': ys, 'z': Z}
