#!/usr/bin/env python3
"""Export reflections from ContextEngine DB to research_outputs and maintain index.

Usage:
  python Artifact/tools/export_reflections.py --out-dir Artifact/research_outputs --keep-days 30

Behavior:
- Scans ~/.automata/context.db reflections table for rows not yet exported (tracked in index.json)
- Writes each reflection to a file reflection_<id>.json
- Updates index.json with metadata (id, timestamp, filename)
- Removes older exports beyond --keep-days (rotates)
"""
from __future__ import annotations
import argparse
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DEFAULT_DB = Path.home() / '.automata' / 'context.db'


def load_index(out_dir: Path):
    idx_file = out_dir / 'index.json'
    if idx_file.exists():
        return json.loads(idx_file.read_text(encoding='utf-8'))
    return {'exports': []}


def save_index(out_dir: Path, idx: dict):
    idx_file = out_dir / 'index.json'
    out_dir.mkdir(parents=True, exist_ok=True)
    idx_file.write_text(json.dumps(idx, indent=2), encoding='utf-8')


def export_reflections(db_path: Path, out_dir: Path, keep_days: int = 30):
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute('SELECT id, timestamp, reflection, improvements, action_items FROM reflections ORDER BY timestamp ASC')
    rows = cursor.fetchall()
    conn.close()

    idx = load_index(out_dir)
    exported_ids = {e['id'] for e in idx['exports']}

    new_exports = []
    for row in rows:
        rid, ts, reflection_text, improvements, action_items = row
        if rid in exported_ids:
            continue
        # Compose JSON doc
        doc = {
            'id': rid,
            'timestamp': ts,
            'reflection': reflection_text,
            'improvements': json.loads(improvements) if improvements else [],
            'action_items': json.loads(action_items) if action_items else []
        }
        fname = out_dir / f"reflection_{rid}.json"
        out_dir.mkdir(parents=True, exist_ok=True)
        fname.write_text(json.dumps(doc, indent=2), encoding='utf-8')
        new_exports.append({'id': rid, 'timestamp': ts, 'file': str(fname)})
        print('Exported', rid)

    # update index
    idx['exports'].extend(new_exports)
    # keep sorted by timestamp desc
    idx['exports'] = sorted(idx['exports'], key=lambda e: e['timestamp'], reverse=True)

    # rotate old exports
    if keep_days is not None:
        # Use timezone-aware UTC cutoff to compare against ISO timestamps
        cutoff = datetime.now(tz=__import__('datetime').timezone.utc) - timedelta(days=keep_days)
        keep = []
        for e in idx['exports']:
            try:
                t = datetime.fromisoformat(e['timestamp'])
                # if timestamp is naive, assume UTC
                if t.tzinfo is None:
                    t = t.replace(tzinfo=__import__('datetime').timezone.utc)
            except Exception:
                keep.append(e)
                continue
            if t >= cutoff:
                keep.append(e)
            else:
                # remove file if exists
                try:
                    Path(e['file']).unlink()
                    print('Removed old export', e['file'])
                except Exception:
                    pass
        idx['exports'] = keep

    save_index(out_dir, idx)
    print('Index updated:', out_dir / 'index.json')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--db', type=Path, default=DEFAULT_DB)
    p.add_argument('--out-dir', type=Path, default=Path('Artifact/research_outputs'))
    p.add_argument('--keep-days', type=int, default=30)
    args = p.parse_args()

    export_reflections(args.db, args.out_dir, keep_days=args.keep_days)
