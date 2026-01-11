import pandas as pd
import numpy as np
from ingest_bot.backtest import walk_forward_backtest


def make_series(n=50):
    idx = pd.date_range('2020-01-01', periods=n)
    s = pd.Series(np.cumsum(np.random.randn(n) * 0.01) + 100, index=idx)
    return s


def test_transaction_cost_and_position():
    s = make_series(30)

    def model_fn(train):
        return float(train.iloc[-1]) * 1.001  # small positive bias

    res_no_cost = walk_forward_backtest(s, model_fn, train_window=10, transaction_cost=0.0, position_size=1.0)
    res_with_cost = walk_forward_backtest(s, model_fn, train_window=10, transaction_cost=0.001, position_size=1.0)

    assert 'metrics' in res_no_cost and 'metrics' in res_with_cost
    # with cost, total_return should be <= without cost
    assert res_with_cost['metrics']['total_return'] <= res_no_cost['metrics']['total_return'] + 1e-8


def test_position_sizing_effect():
    s = make_series(30)

    def model_fn(train):
        return float(train.iloc[-1]) * 1.002

    res_full = walk_forward_backtest(s, model_fn, train_window=10, position_size=1.0)
    res_half = walk_forward_backtest(s, model_fn, train_window=10, position_size=0.5)

    assert res_half['metrics']['total_return'] <= res_full['metrics']['total_return'] + 1e-8
