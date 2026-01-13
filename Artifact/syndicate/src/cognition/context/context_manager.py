"""
Context Management - Maintains coherent narrative through summarization and cleanup.

Provides:
- Context summarization for long-running sessions
- Memory consolidation to reduce token usage
- Narrative coherence across multiple cycles
- Context versioning and rollback
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
import hashlib


@dataclass
class ContextEntry:
    """A single context entry."""
    id: str
    timestamp: str
    entry_type: str  # event, learning, decision, observation, summary
    content: str
    importance: float = 0.5  # 0-1, used for pruning
    tokens_estimate: int = 0
    source: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.tokens_estimate == 0:
            # Rough estimate: 4 chars per token
            self.tokens_estimate = len(self.content) // 4


@dataclass
class ContextSummary:
    """A summary of context entries."""
    id: str
    created_at: str
    period_start: str
    period_end: str
    entries_summarized: int
    original_tokens: int
    summary_tokens: int
    compression_ratio: float
    summary: str
    key_learnings: List[str] = field(default_factory=list)
    key_decisions: List[str] = field(default_factory=list)
    key_events: List[str] = field(default_factory=list)


class ContextManager:
    """
    Manages context for long-running cognitive sessions.
    
    Features:
    - Rolling context window with automatic summarization
    - Importance-based pruning
    - Version history for rollback
    - Export for training data
    """
    
    def __init__(
        self,
        context_dir: str = "./data/context",
        max_tokens: int = 8000,  # Target context window
        summarize_threshold: int = 6000,  # Summarize when exceeding this
        min_importance: float = 0.3,  # Prune below this importance
        logger: Optional[logging.Logger] = None
    ):
        self.context_dir = Path(context_dir)
        self.context_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_tokens = max_tokens
        self.summarize_threshold = summarize_threshold
        self.min_importance = min_importance
        self.logger = logger or logging.getLogger(__name__)
        
        # Current context state
        self.entries: List[ContextEntry] = []
        self.summaries: List[ContextSummary] = []
        self.version = 0
        
        # Load existing context
        self._load_context()
    
    def _load_context(self):
        """Load context from disk."""
        context_file = self.context_dir / "current_context.json"
        if context_file.exists():
            with open(context_file) as f:
                data = json.load(f)
                self.version = data.get("version", 0)
                
                # Load entries
                for e in data.get("entries", []):
                    self.entries.append(ContextEntry(**e))
                
                # Load summaries
                for s in data.get("summaries", []):
                    self.summaries.append(ContextSummary(**s))
    
    def _save_context(self):
        """Save context to disk."""
        context_file = self.context_dir / "current_context.json"
        
        # Create version backup
        self.version += 1
        backup_file = self.context_dir / f"context_v{self.version:04d}.json"
        
        data = {
            "version": self.version,
            "updated_at": datetime.now().isoformat(),
            "entries": [asdict(e) for e in self.entries],
            "summaries": [asdict(s) for s in self.summaries],
            "stats": self.stats()
        }
        
        with open(context_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        with open(backup_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_entry(
        self,
        content: str,
        entry_type: str = "observation",
        importance: float = 0.5,
        source: str = "system",
        metadata: Dict[str, Any] = None
    ) -> ContextEntry:
        """Add a new context entry."""
        entry = ContextEntry(
            id=f"ctx_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.entries):04d}",
            timestamp=datetime.now().isoformat(),
            entry_type=entry_type,
            content=content,
            importance=importance,
            source=source,
            metadata=metadata or {}
        )
        self.entries.append(entry)
        
        # Check if we need to summarize
        total_tokens = self.total_tokens()
        if total_tokens > self.summarize_threshold:
            self._auto_summarize()
        
        self._save_context()
        return entry
    
    def add_event(self, content: str, importance: float = 0.7, **kwargs) -> ContextEntry:
        """Add an event entry."""
        return self.add_entry(content, entry_type="event", importance=importance, **kwargs)
    
    def add_learning(self, content: str, importance: float = 0.8, **kwargs) -> ContextEntry:
        """Add a learning entry (high importance by default)."""
        return self.add_entry(content, entry_type="learning", importance=importance, **kwargs)
    
    def add_decision(self, content: str, importance: float = 0.9, **kwargs) -> ContextEntry:
        """Add a decision entry (very high importance)."""
        return self.add_entry(content, entry_type="decision", importance=importance, **kwargs)
    
    def add_observation(self, content: str, importance: float = 0.4, **kwargs) -> ContextEntry:
        """Add an observation entry (lower importance)."""
        return self.add_entry(content, entry_type="observation", importance=importance, **kwargs)
    
    def total_tokens(self) -> int:
        """Get total token estimate for current context."""
        entry_tokens = sum(e.tokens_estimate for e in self.entries)
        summary_tokens = sum(s.summary_tokens for s in self.summaries)
        return entry_tokens + summary_tokens
    
    def _auto_summarize(self):
        """Automatically summarize old entries to reduce context size."""
        # Get entries older than 1 hour
        cutoff = datetime.now() - timedelta(hours=1)
        old_entries = [e for e in self.entries if datetime.fromisoformat(e.timestamp) < cutoff]
        
        if len(old_entries) < 5:
            # Not enough to summarize, just prune low-importance
            self._prune_low_importance()
            return
        
        # Create summary
        summary = self._create_summary(old_entries)
        if summary:
            self.summaries.append(summary)
            # Remove summarized entries
            self.entries = [e for e in self.entries if e not in old_entries]
            self.logger.info(f"Summarized {len(old_entries)} entries, saved {summary.original_tokens - summary.summary_tokens} tokens")
    
    def _prune_low_importance(self):
        """Remove low-importance entries."""
        original_count = len(self.entries)
        self.entries = [e for e in self.entries if e.importance >= self.min_importance]
        pruned = original_count - len(self.entries)
        if pruned > 0:
            self.logger.info(f"Pruned {pruned} low-importance entries")
    
    def _create_summary(self, entries: List[ContextEntry]) -> Optional[ContextSummary]:
        """Create a summary from a list of entries."""
        if not entries:
            return None
        
        # Group by type
        by_type = {
            "event": [],
            "learning": [],
            "decision": [],
            "observation": []
        }
        for e in entries:
            if e.entry_type in by_type:
                by_type[e.entry_type].append(e)
        
        # Build summary text
        summary_parts = []
        
        # Decisions (most important)
        if by_type["decision"]:
            summary_parts.append("**Key Decisions:**")
            for e in by_type["decision"][:5]:
                summary_parts.append(f"- {e.content[:200]}")
        
        # Learnings
        if by_type["learning"]:
            summary_parts.append("\n**Key Learnings:**")
            for e in by_type["learning"][:5]:
                summary_parts.append(f"- {e.content[:200]}")
        
        # Events
        if by_type["event"]:
            summary_parts.append("\n**Notable Events:**")
            for e in sorted(by_type["event"], key=lambda x: x.importance, reverse=True)[:5]:
                summary_parts.append(f"- {e.content[:150]}")
        
        # Observations (condensed)
        if by_type["observation"]:
            obs_count = len(by_type["observation"])
            summary_parts.append(f"\n*({obs_count} observations recorded)*")
        
        summary_text = "\n".join(summary_parts)
        
        original_tokens = sum(e.tokens_estimate for e in entries)
        summary_tokens = len(summary_text) // 4
        
        return ContextSummary(
            id=f"summary_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            created_at=datetime.now().isoformat(),
            period_start=entries[0].timestamp,
            period_end=entries[-1].timestamp,
            entries_summarized=len(entries),
            original_tokens=original_tokens,
            summary_tokens=summary_tokens,
            compression_ratio=summary_tokens / original_tokens if original_tokens > 0 else 0,
            summary=summary_text,
            key_learnings=[e.content[:100] for e in by_type["learning"][:3]],
            key_decisions=[e.content[:100] for e in by_type["decision"][:3]],
            key_events=[e.content[:100] for e in sorted(by_type["event"], key=lambda x: x.importance, reverse=True)[:3]]
        )
    
    def get_context_window(self, max_tokens: Optional[int] = None) -> str:
        """Get the current context as a formatted string."""
        max_tokens = max_tokens or self.max_tokens
        
        parts = []
        token_count = 0
        
        # Add recent summaries first
        for summary in reversed(self.summaries[-3:]):
            if token_count + summary.summary_tokens < max_tokens:
                parts.append(f"## Context Summary ({summary.period_start[:10]} to {summary.period_end[:10]})")
                parts.append(summary.summary)
                parts.append("")
                token_count += summary.summary_tokens
        
        # Add recent entries (newest first, then reverse for chronological)
        recent_entries = []
        for entry in reversed(self.entries):
            if token_count + entry.tokens_estimate < max_tokens:
                recent_entries.append(entry)
                token_count += entry.tokens_estimate
            else:
                break
        
        if recent_entries:
            parts.append("## Recent Activity")
            for entry in reversed(recent_entries):
                type_emoji = {
                    "event": "📌",
                    "learning": "💡",
                    "decision": "⚖️",
                    "observation": "👁️",
                    "summary": "📋"
                }.get(entry.entry_type, "•")
                parts.append(f"{type_emoji} [{entry.timestamp[:16]}] {entry.content}")
        
        return "\n".join(parts)
    
    def get_key_context(self) -> Dict[str, List[str]]:
        """Get key context items organized by type."""
        result = {
            "recent_decisions": [],
            "active_learnings": [],
            "recent_events": [],
            "from_summaries": []
        }
        
        # From entries
        for e in sorted(self.entries, key=lambda x: x.timestamp, reverse=True):
            if e.entry_type == "decision" and len(result["recent_decisions"]) < 5:
                result["recent_decisions"].append(e.content)
            elif e.entry_type == "learning" and len(result["active_learnings"]) < 5:
                result["active_learnings"].append(e.content)
            elif e.entry_type == "event" and len(result["recent_events"]) < 5:
                result["recent_events"].append(e.content)
        
        # From summaries
        for s in self.summaries[-3:]:
            result["from_summaries"].extend(s.key_learnings)
            result["from_summaries"].extend(s.key_decisions)
        
        return result
    
    def force_summarize(self, entries_to_keep: int = 10) -> ContextSummary:
        """Force summarization of all but the most recent entries."""
        if len(self.entries) <= entries_to_keep:
            return None
        
        to_summarize = self.entries[:-entries_to_keep]
        summary = self._create_summary(to_summarize)
        
        if summary:
            self.summaries.append(summary)
            self.entries = self.entries[-entries_to_keep:]
            self._save_context()
            self.logger.info(f"Force summarized {len(to_summarize)} entries")
        
        return summary
    
    def rollback(self, version: int) -> bool:
        """Rollback to a previous context version."""
        backup_file = self.context_dir / f"context_v{version:04d}.json"
        if not backup_file.exists():
            self.logger.error(f"Version {version} not found")
            return False
        
        with open(backup_file) as f:
            data = json.load(f)
        
        self.entries = [ContextEntry(**e) for e in data.get("entries", [])]
        self.summaries = [ContextSummary(**s) for s in data.get("summaries", [])]
        self.version = version
        
        self._save_context()
        self.logger.info(f"Rolled back to version {version}")
        return True
    
    def export_for_training(self) -> List[Dict[str, Any]]:
        """Export context history for training data generation."""
        examples = []
        
        # Export decision-making pairs
        for i, entry in enumerate(self.entries):
            if entry.entry_type == "decision":
                # Find preceding observations/events as context
                context_entries = [e for e in self.entries[:i] if e.timestamp < entry.timestamp][-5:]
                
                examples.append({
                    "type": "decision_making",
                    "context": [{"type": e.entry_type, "content": e.content} for e in context_entries],
                    "decision": entry.content,
                    "importance": entry.importance,
                    "metadata": entry.metadata
                })
        
        return examples
    
    def stats(self) -> Dict[str, Any]:
        """Get context manager statistics."""
        return {
            "version": self.version,
            "total_entries": len(self.entries),
            "total_summaries": len(self.summaries),
            "total_tokens": self.total_tokens(),
            "entries_by_type": {
                "event": sum(1 for e in self.entries if e.entry_type == "event"),
                "learning": sum(1 for e in self.entries if e.entry_type == "learning"),
                "decision": sum(1 for e in self.entries if e.entry_type == "decision"),
                "observation": sum(1 for e in self.entries if e.entry_type == "observation"),
            },
            "avg_importance": sum(e.importance for e in self.entries) / len(self.entries) if self.entries else 0,
            "compression_savings": sum(s.original_tokens - s.summary_tokens for s in self.summaries),
            "context_window_usage": f"{self.total_tokens()}/{self.max_tokens} tokens"
        }
    
    def clear(self, keep_summaries: bool = True):
        """Clear current context."""
        self.entries = []
        if not keep_summaries:
            self.summaries = []
        self._save_context()
        self.logger.info("Context cleared")
