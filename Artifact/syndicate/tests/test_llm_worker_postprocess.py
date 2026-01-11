import sys
from pathlib import Path
import pytest
import pandas as pd

proj_root = Path(__file__).resolve().parents[1]
if str(proj_root) not in sys.path:
    sys.path.insert(0, str(proj_root))

from scripts.llm_worker import process_task
from db_manager import DatabaseManager
from main import Config

class DummyProvider:
    def generate_content(self, prompt):
        class R:
            text = "Generated content including SPY ticker."
        return R()


def test_llm_worker_calls_postprocessor(tmp_path, monkeypatch):
    # Setup DB
    db_path = tmp_path / "syndicate.db"
    import os
    os.environ["GOLD_STANDARD_TEST_DB"] = str(db_path)

    db = DatabaseManager(db_path)

    # Insert a task
    out_dir = tmp_path / "output" / "reports"
    out_file = out_dir / "premarket_wp.md"  # ensure filename detected as Pre-Market type
    with db._get_connection() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO llm_tasks (document_path, prompt, status, task_type) VALUES (?, ?, 'pending', 'generate')", (str(out_file), "Prompt with SPY"))
        task_id = cur.lastrowid

    # Monkeypatch provider
    import main as synd_main
    monkeypatch.setattr(synd_main, "create_llm_provider", lambda cfg, log: DummyProvider())

    # Monkeypatch fetch_price_series to synthetic series
    import numpy as np
    def fake_fetch(ticker, period_days=120):
        idx = pd.date_range(end=pd.Timestamp("2026-01-11"), periods=50)
        vals = pd.Series(100 + 0.5 * np.arange(50), index=idx)
        return vals

    monkeypatch.setattr("scripts.postprocessor.fetch_price_series", lambda *a, **k: fake_fetch(*a, **k))

    # Prevent external network calls during worker run
    # Provide a dummy NotionPublisher with sync_file method
    class DummyPub:
        def sync_file(self, path):
            return True

    monkeypatch.setattr("scripts.llm_worker.NotionPublisher", DummyPub)
    monkeypatch.setattr("integrations.automata_client.push_context_entry", lambda *a, **k: None)
    monkeypatch.setattr("integrations.automata_client.push_task_metadata", lambda *a, **k: None)

    # Run task processing
    tasks = db.claim_llm_tasks(limit=1)
    cfg = Config()
    process_task(tasks[0], cfg)

    # Expect charts metadata file exists
    meta_path = out_file.with_suffix(out_file.suffix + ".charts.json")
    assert meta_path.exists()
