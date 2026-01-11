"""Lightweight background job manager for long-running computations.

This uses a ThreadPoolExecutor and an in-memory job registry. Jobs are persisted
by writing results to the report directory when complete so the dashboard can
retrieve them later.
"""
from __future__ import annotations

import concurrent.futures
import uuid
import threading
from typing import Callable, Dict, Any
import os
import json
from pathlib import Path

_registry_lock = threading.Lock()
_jobs: Dict[str, Dict[str, Any]] = {}
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

# File-backed persistence for job registry. Location can be overridden via ENV var
# INGEST_JOB_FILE, otherwise defaults to <repo-root>/data/jobs.json
try:
    JOBS_FILE = Path(os.environ.get("INGEST_JOB_FILE")) if os.environ.get("INGEST_JOB_FILE") else (Path(__file__).resolve().parents[1] / "data" / "jobs.json")
except Exception:
    JOBS_FILE = Path("./data/jobs.json")


def _load_jobs_from_disk() -> None:
    if JOBS_FILE.exists():
        try:
            raw = json.loads(JOBS_FILE.read_text(encoding="utf-8"))
            with _registry_lock:
                _jobs.clear()
                for k, v in raw.items():
                    _jobs[k] = v
        except Exception:
            # best-effort: ignore corrupt files
            pass


def _persist_jobs_to_disk() -> None:
    try:
        JOBS_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = JOBS_FILE.with_suffix('.json.tmp')
        with tmp.open('w', encoding='utf-8') as fh:
            json.dump(_jobs, fh)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, JOBS_FILE)
    except Exception:
        # don't blow up the app for persistence errors
        pass

# load existing jobs on import
_load_jobs_from_disk()


def submit_job(func: Callable[[], Any], job_meta: Dict[str, Any] = None) -> str:
    job_id = str(uuid.uuid4())
    meta = {"status": "queued", "result": None, "error": None, "meta": job_meta or {}}
    with _registry_lock:
        _jobs[job_id] = meta
        _persist_jobs_to_disk()

    def _run():
        with _registry_lock:
            _jobs[job_id]["status"] = "running"
            _persist_jobs_to_disk()
        try:
            res = func()
            # ensure result is serializable; convert to str if needed
            try:
                json.dumps(res)
                serial = res
            except Exception:
                serial = str(res)
            with _registry_lock:
                _jobs[job_id]["status"] = "finished"
                _jobs[job_id]["result"] = serial
                _persist_jobs_to_disk()
        except Exception as exc:  # pragma: no cover - runtime errors
            with _registry_lock:
                _jobs[job_id]["status"] = "error"
                _jobs[job_id]["error"] = str(exc)
                _persist_jobs_to_disk()

    _executor.submit(_run)
    return job_id


def get_job(job_id: str) -> Dict[str, Any]:
    with _registry_lock:
        return _jobs.get(job_id, {"status": "not_found"})


def list_jobs() -> Dict[str, Dict[str, Any]]:
    with _registry_lock:
        return dict(_jobs)
