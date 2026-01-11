import os
import json
import pytest
from datetime import datetime, timedelta

from ingest_bot.orchestrator import main


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_FRED_INTEGRATION") != "1",
    reason="FRED integration tests require RUN_FRED_INTEGRATION=1 and FRED_API_KEY"
)


def test_fred_orchestrator_live(tmp_path):
    # requires FRED_API_KEY and FRED_SERIES set in environment
    since = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S")
    rc = main(["--once", "--source", "f", "--adapter", "fred", "--since", since, "--dest-dir", str(tmp_path / "base")])
    assert rc == 0
    p = tmp_path / "base" / "f" / "manifest.json"
    assert p.exists()
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["last_ingest_timestamp"] is not None
