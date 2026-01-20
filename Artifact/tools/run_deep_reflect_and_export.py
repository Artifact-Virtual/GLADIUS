#!/usr/bin/env python3
"""Run an optional ingest, feed ARTY store to context, run reflections (optionally parameter sweep), export reflections, and generate summary.md

Usage:
  python Artifact/tools/run_deep_reflect_and_export.py --server http://127.0.0.1:5000

"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
import requests

DEFAULT_SERVER = 'http://127.0.0.1:5000'
DEFAULT_OUT = Path('Artifact/research_outputs')


def login(server, username, password):
    r = requests.post(f"{server.rstrip('/')}/api/auth/login", json={'username': username, 'password': password})
    r.raise_for_status()
    j = r.json()
    if not j.get('success'):
        raise RuntimeError('Login failed')
    return j['access_token']


def run_ingest(script_dir, source='prices', adapter='yfinance_adapter', days=1):
    run = [str(script_dir / 'deploy' / 'run_ingest.sh'), source, adapter, None, str(days)]
    # Use shell invocation to let run_ingest resolve venv
    cmd = f"{str(script_dir / 'deploy' / 'run_ingest.sh')} {source} {adapter}"
    print('Running ingest:', cmd)
    subprocess.check_call(cmd, shell=True)


def feed_store(server, store_dir, username, password, batch_size=50):
    script = Path(__file__).parent / 'feed_arty_store_to_context.py'
    cmd = [sys.executable, str(script), '--store-dir', str(store_dir), '--server', server, '--username', username, '--password', password, '--batch-size', str(batch_size)]
    print('Feeding ARTY store to context...')
    subprocess.check_call(cmd)


def trigger_reflection(server, token, params):
    url = f"{server.rstrip('/')}/api/context/reflect"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    r = requests.post(url, json=params, headers=headers)
    r.raise_for_status()
    return r.json()


def export_reflections(out_dir):
    script = Path(__file__).parent / 'export_reflections.py'
    cmd = [sys.executable, str(script), '--out-dir', str(out_dir), '--keep-days', '90']
    subprocess.check_call(cmd)


def build_summary(out_dir: Path, added_ids: list):
    out = []
    for rid in added_ids:
        fname = out_dir / f"reflection_{rid}.json"
        if fname.exists():
            doc = json.loads(fname.read_text(encoding='utf-8'))
            out.append(doc)
    if not out:
        print('No new reflections to summarize')
        return
    # Create summary.md with key fields
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    summary_file = out_dir / f"summary_{ts}.md"

    lines = [f"# Deep Reflection Summary ({ts})\n"]
    for d in out:
        lines.append(f"## Reflection {d['id']} - {d['timestamp']}\n")
        excerpt = d['reflection'][:1000].replace('\n', '\n')
        lines.append(f"### Excerpt\n\n{excerpt}\n")
        if d.get('improvements'):
            lines.append('### Improvements\n')
            for imp in d['improvements']:
                lines.append(f"- {imp}\n")
        if d.get('action_items'):
            lines.append('### Action Items\n')
            for a in d['action_items']:
                lines.append(f"- {a}\n")
        lines.append('\n---\n')

    summary_file.write_text('\n'.join(lines), encoding='utf-8')
    print('Wrote summary:', summary_file)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--server', default=DEFAULT_SERVER)
    p.add_argument('--username', default='admin')
    p.add_argument('--password', required=True, help='Dashboard password (required for security - do not use defaults)')
    p.add_argument('--store-dir', default=str(Path(__file__).parent.parent / 'arty' / 'store'))
    p.add_argument('--out-dir', default=str(DEFAULT_OUT))
    p.add_argument('--run-ingest', action='store_true')
    p.add_argument('--prov-data', action='store_true', help='Run prov_data (may require pyarrow and keys)')
    p.add_argument('--sweep', action='store_true', help='Run parameter sweep for reflections')
    args = p.parse_args()

    server = args.server
    token = login(server, args.username, args.password)

    added = []

    script_dir = Path(__file__).parent.parent / 'arty' / 'ingest_bot'

    if args.run_ingest:
        try:
            run_ingest(script_dir, source='prices')
        except subprocess.CalledProcessError as e:
            print('Ingest failed:', e)

    # feed store
    feed_store(server, args.store_dir, args.username, args.password)

    # run reflection(s)
    params_list = []
    if args.sweep:
        # small sweep of params
        models = ['gemini-pro', 'gemini-1.5', None]
        temps = [0.2, 0.4, 0.7]
        max_tokens_opts = [4000, 8000]
        for m in models:
            for t in temps:
                for mt in max_tokens_opts:
                    params_list.append({'model': m, 'temperature': t, 'max_tokens': mt, 'context_max_tokens': 20000})
    else:
        params_list.append({'model': 'gemini-pro', 'temperature': 0.3, 'max_tokens': 8000, 'context_max_tokens': 20000})

    for params in params_list:
        print('Triggering reflection with params:', params)
        res = trigger_reflection(server, token, params)
        if res.get('success'):
            rid = res.get('reflection', {}).get('id')
            if rid:
                # reflection will be exported by next step, track ids
                added.append(rid)
        else:
            print('Reflection failed:', res)

    # export reflections
    out_dir = Path(args.out_dir)
    export_reflections(out_dir)

    # generate summary from added ids
    build_summary(out_dir, added)

    print('Deep reflect and export completed')


if __name__ == '__main__':
    main()
