import os
import sys
import tempfile
import sqlite3
import json
import time

import pytest

# Ensure test DB is isolated
from pathlib import Path

# Ensure package modules are importable when pytest runs from workspace root
proj_root = Path(__file__).resolve().parents[1]
if str(proj_root) not in sys.path:
    sys.path.insert(0, str(proj_root))


def make_tmp_db(tmp_path):
    db_path = tmp_path / "syndicate_test.db"
    os.environ["GOLD_STANDARD_TEST_DB"] = str(db_path)
    # Import DB manager after env set
    from db_manager import DatabaseManager

    db = DatabaseManager(db_path)
    return db


class DummyProvider:
    def __init__(self):
        self.name = "Dummy"

    def generate_content(self, prompt):
        class R:
            text = "Generated content for prompt: " + prompt

        return R()


def test_directory_creation_and_automata_failure_is_handled(tmp_path, monkeypatch, caplog):
    """
    Verify that process_task creates parent directories, writes the file,
    and that Automata client failures don't crash the task processing.
    """
    # Setup DB
    db = make_tmp_db(tmp_path)

    # Create a target path in a nested (non-existent) folder
    out_dir = tmp_path / "output" / "reports"
    out_file = out_dir / "test_task.md"

    # Insert llm_task
    with db._get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO llm_tasks (document_path, prompt, status, task_type) VALUES (?, ?, 'pending', 'generate')",
            (str(out_file), "Test prompt: 123",),
        )
        task_id = cur.lastrowid

    # Monkeypatch provider creation to return DummyProvider
    import main as synd_main

    monkeypatch.setattr(synd_main, "create_llm_provider", lambda cfg, log: DummyProvider())

    # Monkeypatch Automata client to raise connection error
    def fake_push_context_entry(*args, **kwargs):
        raise ConnectionError("Automata down")

    def fake_push_task_metadata(*args, **kwargs):
        raise ConnectionError("Automata down")

    monkeypatch.setenv("PREFER_OLLAMA", "1")
    monkeypatch.setenv("LLM_WORKER_LOG_LEVEL", "DEBUG")

    monkeypatch.setattr("integrations.automata_client.push_context_entry", fake_push_context_entry)
    monkeypatch.setattr("integrations.automata_client.push_task_metadata", fake_push_task_metadata)

    # Import the worker function and run processing
    from scripts.llm_worker import process_task
    from main import Config

    cfg = Config()

    # Claim tasks like the worker would
    tasks = db.claim_llm_tasks(limit=1)
    assert tasks, "Task was not inserted"

    # Run processing (should not raise)
    process_task(tasks[0], cfg)

    # Assert file exists and contains generated content
    assert out_file.exists(), "Output file was not written"
    content = out_file.read_text(encoding="utf-8")
    assert "Generated content" in content

    # Task should be marked completed in DB
    with db._get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT status FROM llm_tasks WHERE id = ?", (task_id,))
        row = cur.fetchone()
        assert row[0] == "completed"


def test_multiple_runs_process_tasks_without_stuck_state(tmp_path, monkeypatch):
    """
    Enqueue multiple tasks and process them sequentially to ensure
    repeated runs don't leave tasks stuck.
    """
    db = make_tmp_db(tmp_path)
    from main import Config

    # Create multiple tasks
    out_dir = tmp_path / "output" / "reports"
    for i in range(5):
        p = out_dir / f"task_{i}.md"
        with db._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO llm_tasks (document_path, prompt, status, task_type) VALUES (?, ?, 'pending', 'generate')",
                (str(p), f"Prompt {i}")
            )

    # Monkeypatch provider
    import main as synd_main

    monkeypatch.setattr(synd_main, "create_llm_provider", lambda cfg, log: DummyProvider())
    from scripts.llm_worker import process_task

    cfg = Config()

    # Process tasks repeatedly, simulating multiple worker loops
    for _ in range(3):
        tasks = db.claim_llm_tasks(limit=10)
        for t in tasks:
            process_task(t, cfg)
        time.sleep(0.1)

    # Verify all tasks completed
    with db._get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(1) FROM llm_tasks WHERE status != 'completed'")
        row = cur.fetchone()
        assert row[0] == 0
