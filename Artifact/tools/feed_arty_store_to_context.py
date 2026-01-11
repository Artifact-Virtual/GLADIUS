#!/usr/bin/env python3
"""Feed ARTY store records into Automata ContextEngine via dashboard API.

Usage:
    python feed_arty_store_to_context.py --store-dir /path/to/arty/store --server http://127.0.0.1:5000

The script will authenticate with the dashboard (default admin/admin123 unless overridden)
and POST context entries in batches to /api/context/entries. Each record is converted
into a compact content string and stored with metadata including source and timestamp.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import requests
import os
from typing import List

DEFAULT_USERNAME = os.getenv('DASHBOARD_ADMIN_USER', 'admin')
DEFAULT_PASSWORD = os.getenv('DASHBOARD_ADMIN_PASS', 'admin123')


def find_record_files(store_dir: Path) -> List[Path]:
    files = []
    for p in store_dir.iterdir():
        if p.is_dir():
            rec = p / 'records.json'
            if rec.exists():
                files.append(rec)
    return files


def record_to_entry(source: str, record: dict) -> dict:
    ts = record.get('timestamp') or record.get('date') or record.get('time')
    # Create a compact content string
    minimal = {k: record[k] for k in ('timestamp', 'date', 'close', 'open', 'high', 'low', 'volume') if k in record}
    content = f"Source: {source}\nTimestamp: {ts}\nData: {json.dumps(minimal)}"
    metadata = {
        'source': source,
        'original': {k: v for k, v in record.items() if k not in minimal}
    }
    return {'role': 'tool', 'content': content, 'metadata': metadata}


def login(server: str, username: str, password: str) -> str:
    url = server.rstrip('/') + '/api/auth/login'
    r = requests.post(url, json={'username': username, 'password': password})
    r.raise_for_status()
    j = r.json()
    if not j.get('success'):
        raise RuntimeError('Login failed')
    return j['access_token']


def post_entries(server: str, token: str, entries: List[dict]):
    url = server.rstrip('/') + '/api/context/entries'
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.post(url, json=entries, headers=headers)
    r.raise_for_status()
    return r.json()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--store-dir', default=os.environ.get('ARTY_STORE_DIR', str(Path(__file__).parent.parent / 'arty' / 'store')))
    p.add_argument('--server', default=os.environ.get('DASHBOARD_URL', 'http://127.0.0.1:5000'))
    p.add_argument('--username', default=DEFAULT_USERNAME)
    p.add_argument('--password', default=DEFAULT_PASSWORD)
    p.add_argument('--batch-size', type=int, default=20)
    args = p.parse_args()

    store = Path(args.store_dir)
    if not store.exists():
        raise SystemExit(f"Store dir not found: {store}")

    files = find_record_files(store)
    if not files:
        print("No record files found in store")
        return

    token = login(args.server, args.username, args.password)
    print(f"Logged in, obtained token (len={len(token)})")

    total = 0
    for rec_file in files:
        source = rec_file.parent.name
        print(f"Processing {source}: {rec_file}")
        data = json.loads(rec_file.read_text(encoding='utf-8'))
        # data may be a list of rows
        entries = [record_to_entry(source, row) for row in data]
        # post in batches
        for i in range(0, len(entries), args.batch_size):
            batch = entries[i:i+args.batch_size]
            resp = post_entries(args.server, token, batch)
            print(f"Posted batch: {len(batch)} -> {resp.get('ids')}")
            total += len(batch)

    print(f"Done. Posted {total} entries.")


if __name__ == '__main__':
    main()
