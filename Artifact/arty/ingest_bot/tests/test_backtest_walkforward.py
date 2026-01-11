import pandas as pd
import numpy as np
from ingest_bot.backtest import walk_forward_backtest, compute_drawdown


def make_series(n=100):
    idx = pd.date_range('2020-01-01', periods=n)
    s = pd.Series(np.cumsum(np.random.randn(n) * 0.01) + 100, index=idx)
    return s


def test_walk_forward_basic():
    s = make_series(50)

    def model_fn(train):
        # predict next = last value (naive)
        return float(train.iloc[-1])

    res = walk_forward_backtest(s, model_fn, train_window=10)
    assert 'equity' in res and 'drawdown' in res and 'metrics' in res


def test_drawdown_calc():
    eq = pd.Series([1.0, 1.2, 1.1, 1.5, 1.0])
    dd = compute_drawdown(eq)
    assert dd.iloc[0] == 0.0
    assert dd.min() < 0
