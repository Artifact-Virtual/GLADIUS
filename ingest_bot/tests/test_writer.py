import json
import pytest

from ingest_bot.pipeline.writer import write_ingest_records


def test_write_and_manifest(tmp_path):
    base = tmp_path / "base"
    write_ingest_records("fred", [{"timestamp": "2020-01-01T00:00:00"}], dest_dir=base)
    manifest = base / "fred" / "manifest.json"
    assert manifest.exists()
    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data["last_ingest_timestamp"] == "2020-01-01T00:00:00"


def test_write_empty_records(tmp_path):
    base = tmp_path / "base2"
    write_ingest_records("s", [], dest_dir=base)
    data = json.loads((base / "s" / "manifest.json").read_text(encoding="utf-8"))
    assert data["last_ingest_timestamp"] is None


def test_invalid_timestamp_raises(tmp_path):
    with pytest.raises(ValueError):
        write_ingest_records("bad", [{"timestamp": object()}], dest_dir=tmp_path / "d")
