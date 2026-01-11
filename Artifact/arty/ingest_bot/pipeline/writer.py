from __future__ import annotations

from pathlib import Path
import json
import logging
import os
import tempfile
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


logger = logging.getLogger(__name__)


def _validate_timestamp(ts: Any) -> Optional[Union[int, float, str]]:
    """Validate timestamp value.

    Accept integer/float timestamps or ISO-8601 strings. Returns the original value
    if valid, otherwise raises ValueError.
    """
    if ts is None:
        return None

    if isinstance(ts, (int, float)):
        return ts

    if isinstance(ts, str):
        # Validate ISO-8601 parseability
        try:
            # datetime.fromisoformat accepts many ISO-like formats
            datetime.fromisoformat(ts)
            return ts
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError(f"timestamp string not ISO-8601: {ts!r}") from exc

    raise ValueError(f"unsupported timestamp type: {type(ts).__name__}")


def write_ingest_records(
    source: str, records: List[Dict], dest_dir: Union[str, Path] = Path("data/ingest")
) -> None:
    """Write a manifest for an ingest source.

    The manifest is written to ``<dest_dir>/<source>/manifest.json``. The write is
    performed atomically by writing to a temporary file in the same directory and
    renaming it over the final file.

    Parameters
    - source: name of the ingest source (used as a subdirectory)
    - records: list of records (the last record's ``timestamp`` will be used)
    - dest_dir: base directory under which to write ingest manifests

    Raises
    - TypeError if ``records`` is not a list
    - ValueError if the last record is missing or has an invalid ``timestamp`` value
    - OSError for filesystem errors
    """
    dest = Path(dest_dir) / source
    dest.mkdir(parents=True, exist_ok=True)

    if not isinstance(records, list):
        raise TypeError("records must be a list of mapping objects")

    if records:
        last = records[-1]
        if not isinstance(last, dict):
            raise ValueError("last record must be a mapping with a 'timestamp' key")
        ts = last.get("timestamp")
        try:
            last_ts = _validate_timestamp(ts)
        except ValueError as exc:
            logger.exception("Invalid timestamp in last record")
            raise
    else:
        last_ts = None

    manifest = {"last_ingest_timestamp": last_ts}

    # Write atomically: create a temp file in same directory then replace
    tmp_fd, tmp_path = tempfile.mkstemp(dir=str(dest), prefix="manifest_", suffix=".json.tmp")
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        final_path = dest / "manifest.json"
        os.replace(tmp_path, str(final_path))
        logger.info("Wrote manifest for source %s at %s", source, final_path)

        # If ARTY_STORE_DIR is set and exists, update ingest links manifest
        arty_store = os.environ.get("ARTY_STORE_DIR")
        if arty_store:
            try:
                from ingest_bot.pipeline.arty_integration import write_links_manifest

                write_links_manifest(Path(arty_store))
            except Exception:
                logger.exception("Failed to update ARTY ingest links")

        # If INFRA_API_URL is set, attempt to POST latest price to infra API
        infra_url = os.environ.get("INFRA_API_URL")
        if infra_url and records:
            # prefer price fields: 'close' or 'price'
            last = records[-1]
            symbol = last.get("ticker") or last.get("symbol")
            price = None
            if "close" in last:
                price = last.get("close")
            elif "price" in last:
                price = last.get("price")

            if symbol and price is not None:
                try:
                    import requests

                    payload = {"symbol": symbol, "price": float(price), "timestamp": last.get("timestamp")}
                    r = requests.post(f"{infra_url.rstrip('/')}/prices", json=payload, timeout=5)
                    if r.status_code >= 400:
                        logger.warning("Infra price ingest failed: %s %s", r.status_code, r.text)
                    else:
                        logger.info("Sent price to infra API for %s = %s", symbol, price)
                except Exception:
                    logger.exception("Failed to POST price to INFRA API")
    except Exception:
        # Clean up tmp file if something goes wrong
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:  # pragma: no cover - best-effort cleanup
            logger.exception("Failed to remove temporary manifest file %s", tmp_path)
        raise
