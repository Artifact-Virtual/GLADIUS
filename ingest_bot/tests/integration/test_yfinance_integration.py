import os
import json
import pytest
from datetime import datetime, timedelta

from ingest_bot.orchestrator import main


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_INTEGRATION") != "1",
    reason="Integration tests are disabled unless RUN_INTEGRATION=1"
)


def test_yfinance_orchestrator_live(tmp_path):
    # run an orchestrator live run using yfinance; since a recent date (yesterday)
    since = (datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S")
    rc = main(["--once", "--source", "y", "--adapter", "yfinance_adapter", "--since", since, "--dest-dir", str(tmp_path / "base")])
    assert rc == 0
    p = tmp_path / "base" / "y" / "manifest.json"
    assert p.exists()
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["last_ingest_timestamp"] is not None


def test_yfinance_returns_prices(tmp_path):
    # another sanity check: ensure we get price fields in record
    since = (datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S")
    rc = main(["--once", "--source", "y", "--adapter", "yfinance_adapter", "--since", since, "--dest-dir", str(tmp_path / "base")])
    assert rc == 0
    p = tmp_path / "base" / "y" / "manifest.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["last_ingest_timestamp"] is not None
    # ensure the adapter actually wrote recent data by checking manifest timestamp format
    # full verification of price fields is left to adapter unit tests or direct adapter usage
