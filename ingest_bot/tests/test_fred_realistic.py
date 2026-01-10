import os
from datetime import datetime
import types
import pytest

# Skip these unit tests if the real client library is not installed; the user wants
# production runs to always use the real clients.
pytest.importorskip("fredapi")

import ingest_bot.adapters.fred as fred_adapter


def test_fred_using_env_series(monkeypatch):
    class FakeFred:
        def __init__(self, api_key=None):
            self.api_key = api_key

        def get_series(self, sid, observation_start=None):
            # return a dict of datetimes to values
            return {datetime(2020, 1, 1, 0, 0): 12.34}

    monkeypatch.setenv("FRED_SERIES", "SER1,SER2")
    monkeypatch.setenv("FRED_API_KEY", "abc")
    monkeypatch.setattr(fred_adapter, "Fred", FakeFred)

    out = fred_adapter.fetch_since("2020-01-01T00:00:00")
    assert isinstance(out, list)
    assert out and out[0]["series_id"] in {"SER1", "SER2"}
    assert out[0]["timestamp"] == "2020-01-01T00:00:00"
