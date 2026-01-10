import json
import types
import pytest

from ingest_bot.adapters import load_adapter
from ingest_bot.orchestrator import main


def test_load_unknown_adapter_raises():
    with pytest.raises(ImportError):
        load_adapter("nonexistent_adapter_abc123")


def test_orchestrator_with_adapter(monkeypatch, tmp_path):
    # Create a fake adapter module
    fake = types.SimpleNamespace()

    def fake_fetch_since(since):
        return [{"timestamp": since, "value": 1}]

    fake.fetch_since = fake_fetch_since

    # Monkeypatch the import so load_adapter returns our fake module
    monkeypatch.setitem(__import__("sys").modules, "ingest_bot.adapters.fake", fake)

    rc = main(["--once", "--source", "f", "--adapter", "fake", "--since", "2020-01-01T00:00:00", "--dest-dir", str(tmp_path / "base")])
    assert rc == 0
    p = tmp_path / "base" / "f" / "manifest.json"
    assert p.exists()
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["last_ingest_timestamp"] == "2020-01-01T00:00:00"


def test_orchestrator_adapter_returns_nonlist(monkeypatch):
    fake = types.SimpleNamespace()

    def bad_fetch(since):
        return {"timestamp": since}

    fake.fetch_since = bad_fetch

    monkeypatch.setitem(__import__("sys").modules, "ingest_bot.adapters.bad", fake)

    rc = main(["--once", "--source", "b", "--adapter", "bad", "--since", "2020-01-01T00:00:00", "--dest-dir", ":memory:"])
    assert rc != 0
