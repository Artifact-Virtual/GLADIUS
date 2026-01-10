"""Adapters package for ingest_bot.

Expose `load_adapter(name)` which imports adapters by module name from
`ingest_bot.adapters.<name>` and returns the module.
"""
from importlib import import_module
from types import ModuleType
from typing import Any


def load_adapter(name: str) -> ModuleType:
    """Load an adapter module by name.

    Example: `load_adapter('fred')` will import `ingest_bot.adapters.fred`.
    Raises ImportError if the adapter cannot be imported.
    """
    try:
        return import_module(f"ingest_bot.adapters.{name}")
    except Exception as exc:  # pragma: no cover - simple wrapper
        raise ImportError(f"could not load adapter {name!r}: {exc}") from exc


__all__ = ["load_adapter"]
