import pandas as pd
import numpy as np
import pytest

# Skip entire module if sklearn not available in the environment
try:
    import sklearn  # type: ignore
except Exception:
    pytest.skip("sklearn not installed; skipping model tests", allow_module_level=True)

from ingest_bot.models import linear_regression_predict, arima_predict, random_forest_predict
from ingest_bot.backtest import evaluate_predictions


def make_series(n=20):
    # increasing series with noise
    idx = pd.date_range('2020-01-01', periods=n)
    s = pd.Series(np.cumsum(np.random.randn(n) + 0.5) + 100, index=idx)
    return s


def test_linear_and_rf_predict():
    s = make_series(10)
    r = linear_regression_predict(s, lags=3)
    assert 'predicted_close' in r
    r2 = random_forest_predict(s, lags=3)
    assert 'predicted_close' in r2


def test_arima_predict():
    s = make_series(30)
    r = arima_predict(s, order=(1,1,0))
    assert 'predicted_close' in r

def test_backtest_eval():
    s = make_series(10)
    # create a simple prediction series equal to last value (no movement) except shift
    preds = s.shift(1)
    res = evaluate_predictions(s, preds)
    assert 'mse' in res and 'directional_accuracy' in res
