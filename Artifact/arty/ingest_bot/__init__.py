"""Minimal ingest_bot package (self-contained).

Exports:
- pipeline.write_ingest_records
- orchestrator.main (CLI entry point)
"""

from .pipeline import write_ingest_records
from . import orchestrator

__all__ = ["pipeline", "write_ingest_records", "orchestrator"]
