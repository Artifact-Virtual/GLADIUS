"""Vector store adapter layer.

Provides a Hektor (pyvdb) backed store, with an SQLite fallback for mapping
and minimal searches when pyvdb isn't available.
"""
from __future__ import annotations

import logging
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class BaseVectorStore:
    def add(self, entry_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[int]:
        raise NotImplementedError()

    def search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        raise NotImplementedError()


class SQLiteVectorFallback(BaseVectorStore):
    """Simple SQLite fallback: stores embeddings as JSON and performs brute-force cosine similarity.

    Only used when Hektor/pyvdb is not available or not initialized.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_tables()

    def _init_tables(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS vector_mappings (vec_id INTEGER PRIMARY KEY AUTOINCREMENT, entry_id TEXT UNIQUE, embedding TEXT)''')
        conn.commit()
        conn.close()

    def add(self, entry_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[int]:
        # No embeddings computed here; expect caller to pass embeddings into metadata['embedding'] if available
        emb = None
        if metadata:
            emb = metadata.get('embedding')
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute('REPLACE INTO vector_mappings (entry_id, embedding) VALUES (?, ?)', (entry_id, json.dumps(emb) if emb is not None else json.dumps([0.0])),)
            conn.commit()
            cur.execute('SELECT vec_id FROM vector_mappings WHERE entry_id = ?', (entry_id,))
            vid = cur.fetchone()[0]
            conn.close()
            return int(vid)
        except Exception as e:
            logger.warning('SQLiteVectorFallback add failed: %s', e)
            return None

    def _cosine(self, a: List[float], b: List[float]) -> float:
        import math
        da = sum(x * x for x in a)
        db = sum(x * x for x in b)
        if da == 0 or db == 0:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        return dot / (math.sqrt(da) * math.sqrt(db))

    def search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        # query is expected to be an embedding (list) or text; if text, nothing we can do here
        # This fallback expects caller to call embed() and then pass serialized embedding as query
        try:
            q_emb = None
            if isinstance(query, str):
                # caller gave raw text — can't embed here
                return []
            q_emb = query
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute('SELECT entry_id, embedding FROM vector_mappings')
            rows = cur.fetchall()
            conn.close()
            scores = []
            for entry_id, emb_json in rows:
                try:
                    emb = json.loads(emb_json)
                    s = self._cosine(q_emb, emb)
                    scores.append((s, entry_id))
                except Exception:
                    continue
            scores.sort(reverse=True)
            results = [{'entry_id': eid, 'score': float(s)} for s, eid in scores[:k]]
            return results
        except Exception as e:
            logger.warning('SQLiteVectorFallback search failed: %s', e)
            return []


class HektorVectorStore(BaseVectorStore):
    def __init__(self, context_db_path: str, path: str = None, dimension: int = 512):
        """Initialize Hektor-backed vector store.

        Args:
            context_db_path: path to the context sqlite DB (used for mapping table)
            path: path for the pyvdb database directory
            dimension: embedding dimensionality
        """
        self.context_db = context_db_path
        self.path = path or str(Path(context_db_path).with_suffix('.vdb'))
        self.dimension = dimension
        self.db = None
        try:
            import pyvdb
            self.pyvdb = pyvdb
        except Exception as e:
            logger.warning('pyvdb (Hektor) not available: %s', e)
            self.pyvdb = None
            return

        try:
            # create or open database
            self.db = self.pyvdb.create_database(self.path, dimension=self.dimension)
        except Exception as e:
            logger.warning('Failed to initialize Hektor DB: %s', e)
            self.db = None

        # ensure mapping table exists in context DB
        try:
            conn = sqlite3.connect(self.context_db)
            cur = conn.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS vector_mappings (vec_id INTEGER PRIMARY KEY, entry_id TEXT UNIQUE)''')
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning('Failed to create mapping table: %s', e)

    def available(self) -> bool:
        return self.db is not None

    def add(self, entry_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[int]:
        if not self.available():
            return None
        try:
            meta = metadata or {}
            # attach entry id so we can recover it from search results when possible
            meta['source_entry_id'] = entry_id
            vec_id = self.db.add_text(content, meta)
            # store mapping
            conn = sqlite3.connect(self.context_db)
            cur = conn.cursor()
            cur.execute('REPLACE INTO vector_mappings (vec_id, entry_id) VALUES (?, ?)', (int(vec_id), entry_id))
            conn.commit()
            conn.close()
            return int(vec_id)
        except Exception as e:
            logger.warning('Hektor add failed: %s', e)
            return None

    def search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        if not self.available():
            return []
        try:
            results = self.db.search(query, k=k)
            out = []
            for r in results:
                # Try to extract entry id: prefer metadata, fall back to mapping table
                entry_id = None
                try:
                    # some results may have .metadata or .meta dict
                    if hasattr(r, 'metadata') and r.metadata:
                        md = r.metadata
                        if isinstance(md, dict) and 'source_entry_id' in md:
                            entry_id = md['source_entry_id']
                    # try attribute
                    if entry_id is None and hasattr(r, 'meta') and r.meta:
                        md = r.meta
                        if isinstance(md, dict) and 'source_entry_id' in md:
                            entry_id = md['source_entry_id']
                except Exception:
                    pass

                if entry_id is None:
                    try:
                        vec_id = int(getattr(r, 'id', None) or getattr(r, 'vec_id', None) or getattr(r, 'vector_id', None))
                        # lookup mapping
                        conn = sqlite3.connect(self.context_db)
                        cur = conn.cursor()
                        cur.execute('SELECT entry_id FROM vector_mappings WHERE vec_id = ?', (vec_id,))
                        rr = cur.fetchone()
                        conn.close()
                        if rr:
                            entry_id = rr[0]
                    except Exception:
                        pass

                out.append({'entry_id': entry_id, 'score': float(getattr(r, 'score', 0.0))})
            return out
        except Exception as e:
            logger.warning('Hektor search failed: %s', e)
            return []


def get_vector_store(context_db_path: str, vdb_path: Optional[str] = None) -> BaseVectorStore:
    """Factory: prefer Hektor if available, otherwise SQLite fallback."""
    hektor = HektorVectorStore(context_db_path, path=vdb_path)
    if hektor.available():
        logger.info('Using Hektor vector store at %s', hektor.path)
        return hektor
    logger.info('Using SQLite vector fallback')
    return SQLiteVectorFallback(context_db_path)
