"""
Context Engine - Persistent memory system with truncation and summarization.

Implements exponential context management:
1. Store full context until max tokens reached
2. First truncation: Summarize entire context into short summary
3. Store summary as single string
4. Also store on spreadsheet in DB for graphing
5. When DB full: Summarize DB into another string
6. Cycle repeats for exponential memory capacity
"""

import os
import json
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
import asyncio


@dataclass
class ContextEntry:
    """Single context entry."""
    id: str
    timestamp: datetime
    role: str  # user, assistant, system, tool
    content: str
    token_count: int
    metadata: Dict[str, Any]


@dataclass
class ContextSummary:
    """Summarized context block."""
    id: str
    timestamp: datetime
    original_token_count: int
    summary_token_count: int
    summary: str
    entry_count: int
    time_range: Dict[str, str]


class ContextEngine:
    """
    Persistent context memory with intelligent truncation and summarization.
    
    Features:
    - Persistent storage across restarts
    - Automatic truncation when limits reached
    - Two-level summarization (context -> summary -> meta-summary)
    - Spreadsheet storage in DB for analytics
    - Reflection and improvement tracking
    """
    
    def __init__(self, config: Dict[str, Any], ai_provider):
        """
        Initialize context engine.
        
        Args:
            config: Configuration dictionary
            ai_provider: AI provider for summarization
        """
        self.config = config
        self.ai_provider = ai_provider
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.db_path = os.path.expanduser(
            config.get('context_db_path') or 
            os.getenv('CONTEXT_DB_PATH', '~/.automata/context.db')
        )
        self.max_tokens = int(config.get('max_tokens', 100000))
        self.summary_tokens = int(config.get('summary_tokens', 10000))
        
        # Initialize database
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # In-memory cache
        self.current_context: List[ContextEntry] = []
        self.current_token_count = 0

        # Vector store (Hektor preferred, SQLite fallback)
        try:
            from .vector_store import get_vector_store
            vdb_path = config.get('vector_db_path')
            self.vector_store = get_vector_store(self.db_path, vdb_path)
            self._hektor_available = getattr(self.vector_store, 'available', lambda: False)()
        except Exception:
            self.vector_store = None
            self._hektor_available = False

        # Load existing context
        self._load_context()
    
    def _init_database(self):
        """Initialize SQLite database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Context entries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS context_entries (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                token_count INTEGER NOT NULL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Summaries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS context_summaries (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                original_token_count INTEGER NOT NULL,
                summary_token_count INTEGER NOT NULL,
                summary TEXT NOT NULL,
                entry_count INTEGER NOT NULL,
                time_range_start TEXT,
                time_range_end TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Meta-summaries table (summaries of summaries)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meta_summaries (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                summary_count INTEGER NOT NULL,
                total_original_tokens INTEGER NOT NULL,
                meta_summary TEXT NOT NULL,
                time_range_start TEXT,
                time_range_end TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Analytics spreadsheet table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS context_analytics (
                timestamp TEXT NOT NULL,
                entry_count INTEGER NOT NULL,
                token_count INTEGER NOT NULL,
                role_distribution TEXT,
                topic_tags TEXT,
                performance_metrics TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Reflection table (AI self-reflection)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reflections (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                context_snapshot TEXT NOT NULL,
                reflection TEXT NOT NULL,
                improvements TEXT,
                action_items TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Embeddings table: store embedding vector as JSON string for each entry
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS context_embeddings (
                entry_id TEXT PRIMARY KEY,
                embedding TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_context(self):
        """Load recent context from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load recent entries (up to max_tokens)
        cursor.execute('''
            SELECT id, timestamp, role, content, token_count, metadata
            FROM context_entries
            ORDER BY timestamp DESC
            LIMIT 1000
        ''')
        
        entries = []
        total_tokens = 0
        
        for row in cursor.fetchall():
            entry = ContextEntry(
                id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                role=row[2],
                content=row[3],
                token_count=row[4],
                metadata=json.loads(row[5]) if row[5] else {}
            )
            
            if total_tokens + entry.token_count <= self.max_tokens:
                entries.append(entry)
                total_tokens += entry.token_count
            else:
                break
        
        # Reverse to chronological order
        self.current_context = list(reversed(entries))
        self.current_token_count = total_tokens
        
        conn.close()
        
        self.logger.info(f"Loaded {len(self.current_context)} context entries ({total_tokens} tokens)")
    
    async def add_entry(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add entry to context.
        
        Args:
            role: Role (user, assistant, system, tool)
            content: Entry content
            metadata: Additional metadata
            
        Returns:
            Entry ID
        """
        # Estimate token count (rough approximation: 1 token ≈ 4 characters)
        token_count = len(content) // 4
        
        entry = ContextEntry(
            id=f"entry_{datetime.now(timezone.utc).timestamp()}",
            timestamp=datetime.now(timezone.utc),
            role=role,
            content=content,
            token_count=token_count,
            metadata=metadata or {}
        )
        
        # Add to current context
        self.current_context.append(entry)
        self.current_token_count += token_count
        
        # Save to database
        self._save_entry(entry)
        
        # Use vector store when available, otherwise compute and store embedding asynchronously (best-effort)
        try:
            if self._hektor_available and self.vector_store is not None:
                # Let Hektor index the text directly (it will encode internally). Store mapping inside vector_store.
                self.vector_store.add(entry.id, entry.content, metadata=entry.metadata)
            else:
                emb = await self.ai_provider.embed(entry.content)
                # persist embedding as JSON string
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cur.execute('REPLACE INTO context_embeddings (entry_id, embedding) VALUES (?, ?)', (entry.id, json.dumps(emb)))
                conn.commit()
                conn.close()
        except Exception as e:
            self.logger.warning(f"Failed to compute/store embedding for entry {entry.id}: {e}")

        return entry.id
    
    def _save_entry(self, entry: ContextEntry):
        """Save entry to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO context_entries (id, timestamp, role, content, token_count, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            entry.id,
            entry.timestamp.isoformat(),
            entry.role,
            entry.content,
            entry.token_count,
            json.dumps(entry.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    async def _truncate_context(self):
        """
        Truncate context by summarizing older entries.
        
        Implements exponential memory:
        1. Summarize old entries into compact summary
        2. Keep recent entries in full
        3. Store summary as single entry
        """
        self.logger.info("Context limit reached. Truncating...")
        
        # Calculate how many tokens to summarize
        tokens_to_remove = self.current_token_count - (self.max_tokens // 2)
        
        # Find entries to summarize
        entries_to_summarize = []
        tokens_counted = 0
        
        for entry in self.current_context:
            if tokens_counted < tokens_to_remove:
                entries_to_summarize.append(entry)
                tokens_counted += entry.token_count
            else:
                break
        
        if not entries_to_summarize:
            return
        
        # Generate summary
        summary_content = "\n\n".join([
            f"[{e.timestamp.isoformat()}] {e.role}: {e.content}"
            for e in entries_to_summarize
        ])
        
        summary_prompt = f"""Summarize the following context entries into a concise summary that preserves key information, decisions, and insights. Target length: {self.summary_tokens} tokens.

{summary_content}

Provide a detailed but concise summary:"""
        
        try:
            result = await self.ai_provider.generate(
                prompt=summary_prompt,
                system_message="You are a context summarization expert. Create concise, information-dense summaries.",
                temperature=0.3,
                max_tokens=self.summary_tokens
            )
            
            summary_text = result['content']
            
            # Create summary entry
            summary = ContextSummary(
                id=f"summary_{datetime.now(timezone.utc).timestamp()}",
                timestamp=datetime.now(timezone.utc),
                original_token_count=tokens_counted,
                summary_token_count=len(summary_text) // 4,
                summary=summary_text,
                entry_count=len(entries_to_summarize),
                time_range={
                    'start': entries_to_summarize[0].timestamp.isoformat(),
                    'end': entries_to_summarize[-1].timestamp.isoformat()
                }
            )
            
            # Save summary to database
            self._save_summary(summary)
            
            # Remove summarized entries from current context
            self.current_context = self.current_context[len(entries_to_summarize):]
            
            # Add summary as new entry
            await self.add_entry(
                role="system",
                content=f"[CONTEXT SUMMARY] {summary_text}",
                metadata={
                    'type': 'summary',
                    'original_entries': len(entries_to_summarize),
                    'original_tokens': tokens_counted
                }
            )
            
            self.logger.info(f"Truncated {len(entries_to_summarize)} entries into summary")
            
        except Exception as e:
            self.logger.error(f"Failed to truncate context: {e}")
    
    def _save_summary(self, summary: ContextSummary):
        """Save summary to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO context_summaries 
            (id, timestamp, original_token_count, summary_token_count, 
             summary, entry_count, time_range_start, time_range_end)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            summary.id,
            summary.timestamp.isoformat(),
            summary.original_token_count,
            summary.summary_token_count,
            summary.summary,
            summary.entry_count,
            summary.time_range['start'],
            summary.time_range['end']
        ))
        
        conn.commit()
        conn.close()
    
    async def _update_analytics(self):
        """Update analytics spreadsheet."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate role distribution
        role_dist = {}
        for entry in self.current_context:
            role_dist[entry.role] = role_dist.get(entry.role, 0) + 1
        
        cursor.execute('''
            INSERT INTO context_analytics 
            (timestamp, entry_count, token_count, role_distribution)
            VALUES (?, ?, ?, ?)
        ''', (
            datetime.now(timezone.utc).isoformat(),
            len(self.current_context),
            self.current_token_count,
            json.dumps(role_dist)
        ))
        
        conn.commit()
        conn.close()
    
    def get_context_for_prompt(self, max_tokens: Optional[int] = None, use_similarity: bool = True, similarity_k: int = 20, similarity_query: Optional[str] = None) -> str:
        """
        Get context formatted for AI prompt.

        Args:
            max_tokens: Maximum tokens to include
            use_similarity: Whether to include similar entries based on embeddings
            similarity_k: Number of similar entries to include
            similarity_query: Optional query string to compute similarity embeddings from (if not provided, use a short recent context)

        Returns:
            Formatted context string
        """
        token_limit = max_tokens or self.max_tokens

        # Start with recent entries (most recent first)
        context_parts = []
        tokens_used = 0

        # Optionally add top-K similar entries first to bias context
        if use_similarity:
            try:
                # Build a query for similarity embedding
                if similarity_query:
                    q = similarity_query
                else:
                    # Compose a short recent summary to use as query
                    q = " ".join(e.content for e in self.current_context[-5:]) if len(self.current_context) > 0 else ''

                if q:
                    # If Hektor is available, pass raw query text to its search (it will encode)
                    if self._hektor_available and self.vector_store is not None:
                        srows = self.vector_store.search(q, k=similarity_k)
                        for r in srows:
                            eid = r.get('entry_id')
                            if not eid:
                                continue
                            # fetch entry
                            conn = sqlite3.connect(self.db_path)
                            cur = conn.cursor()
                            cur.execute('SELECT id,timestamp,role,content,token_count,metadata FROM context_entries WHERE id = ?', (eid,))
                            rrow = cur.fetchone()
                            conn.close()
                            if not rrow:
                                continue
                            entry_obj = ContextEntry(id=rrow[0], timestamp=datetime.fromisoformat(rrow[1]), role=rrow[2], content=rrow[3], token_count=rrow[4], metadata=json.loads(rrow[5]) if rrow[5] else {})
                            if tokens_used + entry_obj.token_count <= token_limit:
                                context_parts.append(f"[{entry_obj.role}] {entry_obj.content}")
                                tokens_used += entry_obj.token_count
                            else:
                                break
                    else:
                        # Fall back to previous method: compute embedding and lookup similar entries via cosine
                        similar = self.get_similar_entries(q, top_k=similarity_k)
                        for e in similar:
                            if tokens_used + e.token_count <= token_limit:
                                context_parts.append(f"[{e.role}] {e.content}")
                                tokens_used += e.token_count
                            else:
                                break
            except Exception as ex:
                self.logger.warning(f"Similarity lookup failed: {ex}")

        # Fill the remaining budget with most recent entries
        for entry in reversed(self.current_context):
            if tokens_used + entry.token_count <= token_limit:
                context_parts.append(f"[{entry.role}] {entry.content}")
                tokens_used += entry.token_count
            else:
                break

        # Deduplicate while preserving order
        seen = set()
        ordered = []
        for p in context_parts:
            if p in seen:
                continue
            seen.add(p)
            ordered.append(p)

        return "\n\n".join(reversed(ordered))

    def get_similar_entries(self, query: str, top_k: int = 10) -> List[ContextEntry]:
        """Return top-k similar ContextEntry objects to the query string using cosine similarity."""
        try:
            import math
            q_emb = None
            # Run embedding in a separate thread to avoid event-loop conflicts
            try:
                import concurrent.futures
                def _sync_embed(q):
                    import asyncio
                    return asyncio.run(self.ai_provider.embed(q))
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                    fut = ex.submit(_sync_embed, query)
                    q_emb = fut.result(timeout=30)
            except Exception:
                q_emb = None

            if not q_emb:
                return []

            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute('SELECT entry_id, embedding FROM context_embeddings')
            rows = cur.fetchall()
            conn.close()

            def cos(a, b):
                import math
                da = sum(x*x for x in a)
                db = sum(x*x for x in b)
                if da == 0 or db == 0:
                    return 0.0
                dot = sum(x*y for x, y in zip(a, b))
                return dot / (math.sqrt(da) * math.sqrt(db))

            scores = []
            for entry_id, emb_json in rows:
                try:
                    emb = json.loads(emb_json)
                    if not isinstance(emb, list):
                        continue
                    s = cos(q_emb, emb)
                    scores.append((s, entry_id))
                except Exception:
                    continue

            # pick top_k
            scores.sort(reverse=True)
            top = scores[:top_k]

            # Fetch entries for top ids
            entries = []
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            for s, eid in top:
                cur.execute('SELECT id, timestamp, role, content, token_count, metadata FROM context_entries WHERE id = ?', (eid,))
                r = cur.fetchone()
                if r:
                    entries.append(ContextEntry(id=r[0], timestamp=datetime.fromisoformat(r[1]), role=r[2], content=r[3], token_count=r[4], metadata=json.loads(r[5]) if r[5] else {}))
            conn.close()

            return entries

        except Exception as e:
            self.logger.warning(f"Failed to compute similar entries: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get context statistics."""
        return {
            "current_entries": len(self.current_context),
            "current_tokens": self.current_token_count,
            "max_tokens": self.max_tokens,
            "utilization": (self.current_token_count / self.max_tokens) * 100,
            "role_distribution": self._get_role_distribution(),
        }
    
    def _get_role_distribution(self) -> Dict[str, int]:
        """Get distribution of roles in current context."""
        dist = {}
        for entry in self.current_context:
            dist[entry.role] = dist.get(entry.role, 0) + 1
        return dist
    
    async def create_meta_summary(self):
        """
        Create meta-summary by summarizing all summaries.
        This is the second level of truncation.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all summaries
        cursor.execute('''
            SELECT id, timestamp, summary, original_token_count, time_range_start, time_range_end
            FROM context_summaries
            ORDER BY timestamp ASC
        ''')
        
        summaries = cursor.fetchall()
        
        if len(summaries) < 10:  # Only create meta-summary if we have enough summaries
            conn.close()
            return
        
        # Combine summaries
        combined_summaries = "\n\n".join([
            f"[{row[1]}] {row[2]}"
            for row in summaries
        ])
        
        # Generate meta-summary
        meta_prompt = f"""Create a high-level meta-summary of these context summaries. Preserve the most critical information and patterns.

{combined_summaries}

Meta-summary:"""
        
        try:
            result = await self.ai_provider.generate(
                prompt=meta_prompt,
                system_message="You are creating a meta-summary of summaries. Focus on patterns, key decisions, and critical insights.",
                temperature=0.3,
                max_tokens=self.summary_tokens
            )
            
            meta_summary_text = result['content']
            
            # Save meta-summary
            cursor.execute('''
                INSERT INTO meta_summaries 
                (id, timestamp, summary_count, total_original_tokens, meta_summary, 
                 time_range_start, time_range_end)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                f"meta_{datetime.now(timezone.utc).timestamp()}",
                datetime.now(timezone.utc).isoformat(),
                len(summaries),
                sum(row[3] for row in summaries),
                meta_summary_text,
                summaries[0][4],  # first time_range_start
                summaries[-1][5]  # last time_range_end
            ))
            
            # Archive old summaries
            cursor.execute('DELETE FROM context_summaries WHERE timestamp < ?', (summaries[-1][1],))
            
            conn.commit()
            self.logger.info(f"Created meta-summary from {len(summaries)} summaries")
            
        except Exception as e:
            self.logger.error(f"Failed to create meta-summary: {e}")
        finally:
            conn.close()
