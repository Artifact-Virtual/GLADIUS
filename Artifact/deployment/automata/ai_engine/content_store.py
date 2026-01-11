"""Content storage DAO for tracking drafts and final articles.

Stores content items in the same context DB used by ContextEngine so we keep
content lifecycle and memory in a single place (simple SQLite schema/migration).
"""
from typing import Optional, List, Dict, Any
import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path


class ContentStore:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path).expanduser()
        self._init_table()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        return conn

    def _init_table(self):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS content_items (
                id TEXT PRIMARY KEY,
                platform TEXT,
                topic TEXT,
                status TEXT,
                content_json TEXT,
                text TEXT,
                title TEXT,
                author TEXT,
                tags TEXT,
                model TEXT,
                tokens INTEGER,
                export_path TEXT,
                batch_id TEXT,
                published_url TEXT,
                published_at TEXT,
                publish_metrics TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT
            )
        ''')
        # Backwards compatible: try to add published columns if they are missing (no-op on newer DBs)
        try:
            cur.execute('ALTER TABLE content_items ADD COLUMN published_url TEXT')
        except Exception:
            pass
        try:
            cur.execute('ALTER TABLE content_items ADD COLUMN published_at TEXT')
        except Exception:
            pass
        try:
            cur.execute('ALTER TABLE content_items ADD COLUMN publish_metrics TEXT')
        except Exception:
            pass
        # Backwards compatible: error column for publish results
        try:
            cur.execute('ALTER TABLE content_items ADD COLUMN publish_error TEXT')
        except Exception:
            pass
        conn.commit()
        conn.close()

    def create(self, item_id: str, platform: str, topic: str, content: Dict[str, Any], status: str = 'draft') -> None:
        conn = self._get_conn()
        cur = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        text = ''
        title = None
        if isinstance(content, dict):
            text = content.get('text') or content.get('article') or ''
            title = content.get('title')
        cur.execute('''
            INSERT OR REPLACE INTO content_items (id, platform, topic, status, content_json, text, title, model, tokens, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item_id,
            platform,
            topic,
            status,
            json.dumps(content),
            text,
            title,
            content.get('model') if isinstance(content, dict) else None,
            content.get('tokens') if isinstance(content, dict) else None,
            now,
            now,
        ))
        conn.commit()
        conn.close()

    def list(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        cur = conn.cursor()
        if status:
            cur.execute('SELECT * FROM content_items WHERE status = ? ORDER BY created_at DESC', (status,))
        else:
            cur.execute('SELECT * FROM content_items ORDER BY created_at DESC')
        rows = cur.fetchall()
        cols = [c[0] for c in cur.description]
        conn.close()
        result = []
        for r in rows:
            d = dict(zip(cols, r))
            if d.get('content_json'):
                try:
                    d['content'] = json.loads(d['content_json'])
                except Exception:
                    d['content'] = d['content_json']
            result.append(d)
        return result

    def get(self, item_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute('SELECT * FROM content_items WHERE id = ?', (item_id,))
        r = cur.fetchone()
        conn.close()
        if not r:
            return None
        cols = [c[0] for c in cur.description]
        d = dict(zip(cols, r))
        if d.get('content_json'):
            try:
                d['content'] = json.loads(d['content_json'])
            except Exception:
                d['content'] = d['content_json']
        return d

    def update_status(self, item_id: str, status: str, **kwargs) -> None:
        conn = self._get_conn()
        cur = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        fields = ['status = ?', 'updated_at = ?']
        values = [status, now]
        for k, v in kwargs.items():
            fields.append(f"{k} = ?")
            values.append(v)
        values.append(item_id)
        sql = f"UPDATE content_items SET {', '.join(fields)} WHERE id = ?"
        cur.execute(sql, tuple(values))
        conn.commit()
        conn.close()
