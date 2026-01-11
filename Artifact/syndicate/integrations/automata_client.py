"""Simple Automata API client for pushing context entries and task metadata.

This keeps Syndicate's cognition in sync with the Artifact/Automata context engine.
"""
import os
import requests
import logging
from typing import Optional, Dict, Any

LOG = logging.getLogger(__name__)

AUTOMATA_API_URL = os.environ.get("AUTOMATA_API_URL", "http://127.0.0.1:5000/api")
AUTOMATA_API_TOKEN = os.environ.get("AUTOMATA_API_TOKEN")


def _build_headers():
    headers = {"Content-Type": "application/json"}
    if AUTOMATA_API_TOKEN:
        headers["Authorization"] = f"Bearer {AUTOMATA_API_TOKEN}"
    return headers


def push_context_entry(title: str, body: str, meta: Optional[Dict[str, Any]] = None) -> bool:
    """Push a context entry to Automata's context API.

    Returns True on success, False otherwise.
    """
    url = f"{AUTOMATA_API_URL}/context/entries"
    payload = {
        "title": title,
        "body": body,
        "meta": meta or {},
    }
    try:
        resp = requests.post(url, json=payload, headers=_build_headers(), timeout=5)
        resp.raise_for_status()
        return True
    except Exception as e:
        LOG.warning("Automata client: failed to push context entry: %s", e)
        return False


def push_task_metadata(task_id: int, status: str, doc_path: Optional[str] = None, extra: Optional[Dict[str, Any]] = None) -> bool:
    """Push LLM task metadata for observability into Automata.

    This helps the cognition engine remain aware of the research pipeline status.
    """
    url = f"{AUTOMATA_API_URL}/context/llm_task"
    payload = {
        "task_id": task_id,
        "status": status,
        "doc_path": doc_path,
        "extra": extra or {},
    }
    try:
        resp = requests.post(url, json=payload, headers=_build_headers(), timeout=5)
        resp.raise_for_status()
        return True
    except Exception as e:
        LOG.warning("Automata client: failed to push task metadata: %s", e)
        return False
