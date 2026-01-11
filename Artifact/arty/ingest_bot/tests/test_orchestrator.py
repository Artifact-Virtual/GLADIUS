import json
from ingest_bot.orchestrator import main


def test_orchestrator_generates_manifest(tmp_path):
    # use an explicit records file to avoid requiring a live adapter in unit tests
    rf = tmp_path / "records.json"
    rf.write_text(json.dumps([{"timestamp": "2020-01-01T00:00:00"}]), encoding="utf-8")
    rc = main(["--once", "--source", "fred", "--records-file", str(rf), "--dest-dir", str(tmp_path / "base")])
    assert rc == 0
    p = tmp_path / "base" / "fred" / "manifest.json"
    assert p.exists()
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["last_ingest_timestamp"] is not None


def test_orchestrator_with_records_file(tmp_path):
    rf = tmp_path / "records.json"
    rf.write_text(json.dumps([{"timestamp": "2021-01-02T03:04:05"}]), encoding="utf-8")
    rc = main(["--once", "--source", "s", "--records-file", str(rf), "--dest-dir", str(tmp_path / "base")])
    assert rc == 0
    data = json.loads((tmp_path / "base" / "s" / "manifest.json").read_text(encoding="utf-8"))
    assert data["last_ingest_timestamp"] == "2021-01-02T03:04:05"
