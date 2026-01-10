"""Prediction models: linear regression, ARIMA, and RandomForest (optional).

Each function accepts a pandas Series of prices indexed by timestamp and returns a
prediction (next close) and diagnostic info (like expected pct change).
"""
from __future__ import annotations

from typing import Dict, Any
import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from statsmodels.tsa.arima.model import ARIMA


def _make_lag_features(series: pd.Series, lags: int = 3) -> (np.ndarray, np.ndarray):
    x = []
    y = []
    vals = series.values
    for i in range(lags, len(vals)):
        x.append(vals[i - lags : i])
        y.append(vals[i])
    return np.array(x), np.array(y)


def linear_regression_predict(series: pd.Series, lags: int = 3) -> Dict[str, Any]:
    x, y = _make_lag_features(series, lags=lags)
    if len(y) == 0:
        return {"predicted_close": None, "expected_pct_change": None}
    model = LinearRegression()
    model.fit(x, y)
    last = series.values[-lags:]
    pred = float(model.predict(last.reshape(1, -1))[0])
    last_close = float(series.values[-1])
    return {"predicted_close": pred, "expected_pct_change": (pred - last_close) / last_close}


def random_forest_predict(series: pd.Series, lags: int = 3) -> Dict[str, Any]:
    x, y = _make_lag_features(series, lags=lags)
    if len(y) == 0:
        return {"predicted_close": None, "expected_pct_change": None}
    model = RandomForestRegressor(n_estimators=100, random_state=0)
    model.fit(x, y)
    last = series.values[-lags:]
    pred = float(model.predict(last.reshape(1, -1))[0])
    last_close = float(series.values[-1])
    return {"predicted_close": pred, "expected_pct_change": (pred - last_close) / last_close}


def arima_predict(series: pd.Series, order=(1, 1, 0)) -> Dict[str, Any]:
    if len(series) < max(order) + 2:
        return {"predicted_close": None, "expected_pct_change": None}
    model = ARIMA(series, order=order)
    fit = model.fit()
    pred = fit.forecast(steps=1)
    pred_val = float(pred.iloc[0]) if hasattr(pred, 'iloc') else float(pred[0])
    last_close = float(series.iloc[-1])
    return {"predicted_close": pred_val, "expected_pct_change": (pred_val - last_close) / last_close}
