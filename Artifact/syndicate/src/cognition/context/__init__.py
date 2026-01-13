"""
Context Management Module.

Provides context summarization, consolidation, and narrative management
for long-running cognitive sessions.
"""

from .context_manager import ContextManager, ContextEntry, ContextSummary

__all__ = [
    "ContextManager",
    "ContextEntry", 
    "ContextSummary"
]
