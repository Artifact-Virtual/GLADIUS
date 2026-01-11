from __future__ import annotations

import argparse
import json
import logging
import sys
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .pipeline.writer import write_ingest_records

logger = logging.getLogger(__name__)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Minimal ingest_bot orchestrator")
    p.add_argument("--once", action="store_true", help="Run once and exit")
    p.add_argument("--source", required=True, help="Source name for the ingest")
    p.add_argument("--adapter", help="Name of adapter to use (e.g., 'fred' or 'yfinance')")
    p.add_argument(
        "--since",
        help="Fetch records since this ISO-8601 timestamp (required when using --adapter)",
    )
    p.add_argument(
        "--records-file",
        type=Path,
        help="Optional JSON file containing a list of records to ingest",
    )
    p.add_argument(
        "--dest-dir",
        type=Path,
        default=Path(os.environ.get("ARTY_STORE_DIR", "data/ingest")),
        help="Base directory where manifests are written (can be overridden by ARTY_STORE_DIR env)",
    )
    p.add_argument(
        "--save-records",
        action="store_true",
        dest="save_records",
        help="Save fetched records to <dest_dir>/<source>/records.json",
    )
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    logging.basicConfig(level=logging.INFO)
    args = parse_args(argv)

    if not args.once:
        logger.error("This minimal orchestrator supports only --once runs")
        return 2

    try:
        if args.records_file:
            with args.records_file.open("r", encoding="utf-8") as fh:
                records = json.load(fh)
                if not isinstance(records, list):
                    logger.error("records file must contain a JSON list")
                    return 3
        else:
            # Use an adapter if provided
            if not args.adapter:
                logger.error("--adapter is required for live adapter runs")
                return 4
            if not args.since:
                logger.error("--since is required when using --adapter")
                return 4
            from .adapters import load_adapter

            adapter = load_adapter(args.adapter)
            # adapter.fetch_since(timestamp, **kwargs) - adapters may require extra params
            # For live runs we expect the adapter to return live data using the real client libs
            records = adapter.fetch_since(args.since)
            if not isinstance(records, list):
                logger.error("adapter.fetch_since must return a list of records")
                return 5
            if not records:
                logger.error("adapter returned no records (no live data)")
                return 7

        # Optionally save raw records for inspection
        if args.save_records:
            records_dest = args.dest_dir / args.source
            records_dest.mkdir(parents=True, exist_ok=True)
            tmp_fd, tmp_path = tempfile.mkstemp(dir=str(records_dest), prefix="records_", suffix=".json.tmp")
            try:
                with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                    json.dump(records, f, ensure_ascii=False)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp_path, str(records_dest / "records.json"))
                logger.info("Saved records for source %s at %s", args.source, records_dest / "records.json")
            except Exception:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                raise

        write_ingest_records(args.source, records, dest_dir=args.dest_dir)
        logger.info("Ingest run completed for source %s", args.source)
        return 0
    except ImportError as exc:  # pragma: no cover - adapter import error
        logger.exception("Adapter load failed: %s", exc)
        return 6
    except Exception as exc:  # pragma: no cover - we test success paths
        logger.exception("Ingest run failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
