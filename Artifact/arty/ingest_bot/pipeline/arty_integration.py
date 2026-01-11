from __future__ import annotations

from pathlib import Path
import json
import logging
import fnmatch

logger = logging.getLogger(__name__)

DB_GLOBS = ["*.db", "*.sqlite", "*.sqlite3"]


def scan_arty_store(store_dir: Path) -> dict:
    """Scan `store_dir` for database files and return a small manifest.

    The manifest includes absolute paths and file sizes. This is intentionally
    read-only and does not modify databases. The caller may use this to decide
    how to link or import data.
    """
    store_dir = Path(store_dir)
    if not store_dir.exists():
        logger.debug("Arty store dir does not exist: %s", store_dir)
        return {"store": str(store_dir), "dbs": []}

    dbs = []
    for root, _, files in __import__("os").walk(store_dir):
        for pattern in DB_GLOBS:
            for fname in fnmatch.filter(files, pattern):
                p = Path(root) / fname
                try:
                    size = p.stat().st_size
                except Exception:
                    size = None
                dbs.append({"path": str(p.resolve()), "size": size})

    manifest = {"store": str(store_dir.resolve()), "dbs": dbs}
    return manifest


def write_links_manifest(store_dir: Path):
    """Write `ingest_links.json` into `store_dir` describing discovered DBs."""
    manifest = scan_arty_store(store_dir)
    out = Path(store_dir) / "ingest_links.json"
    try:
        out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        logger.info("Wrote ingest_links manifest to %s", out)
    except Exception:
        logger.exception("Failed to write ingest_links manifest to %s", out)
        raise


# For convenience, provide a small CLI-like helper
if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("store_dir")
    args = p.parse_args()
    write_links_manifest(Path(args.store_dir))
