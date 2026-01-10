import os
import types
import pytest

# Skip these unit tests if the real yfinance library is not installed; we require
# the real client libraries for production runs.
pytest.importorskip("yfinance")

import ingest_bot.adapters.yfinance_adapter as yfa


def test_yfinance_using_env_tickers(monkeypatch):
    fake_mod = types.SimpleNamespace()

    def fake_download(tk, start=None, progress=None):
        # Return dict-like mapping timestamps to row dicts
        return {"2020-01-01T00:00:00": {"Open": 1.0, "Close": 2.0}}

    fake_mod.download = fake_download

    monkeypatch.setenv("YFINANCE_TICKERS", "FOO,BAR")
    monkeypatch.setattr(yfa, "yf", fake_mod)

    out = yfa.fetch_since("2020-01-01T00:00:00")
    assert out
    assert out[0]["ticker"] in {"FOO", "BAR"}
    assert out[0]["open"] == 1.0
    assert out[0]["close"] == 2.0
