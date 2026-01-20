#!/usr/bin/env python3
"""Generate article drafts via Automata Dashboard API and save them locally.

Usage:
  python Artifact/tools/generate_articles.py --server http://127.0.0.1:5000 --username admin --password devpass --count 3
"""
from __future__ import annotations

import argparse
import requests
from pathlib import Path
import json
from datetime import datetime, timezone

DEFAULT_SERVER = 'http://127.0.0.1:5000'
OUT_DIR = Path('Artifact/research_outputs/articles')


def login(server, username, password):
    r = requests.post(f"{server.rstrip('/')}/api/auth/login", json={'username': username, 'password': password})
    r.raise_for_status()
    j = r.json()
    if not j.get('success'):
        raise RuntimeError('Login failed')
    return j['access_token']


def generate(server, token, payload):
    url = f"{server.rstrip('/')}/api/content/generate"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    r = requests.post(url, json=payload, headers=headers, timeout=120)
    r.raise_for_status()
    return r.json()


def save_results(out_dir: Path, results: list):
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    for i, r in enumerate(results):
        fname = out_dir / f'draft_{ts}_{i}.json'
        fname.write_text(json.dumps(r, indent=2), encoding='utf-8')
        saved.append(str(fname))
    return saved


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--server', default=DEFAULT_SERVER)
    p.add_argument('--username', default='admin')
    p.add_argument('--password', required=True, help='Dashboard password (required for security - do not use defaults)')
    p.add_argument('--platform', default='LinkedIn')
    p.add_argument('--topic', default='Recent market insights')
    p.add_argument('--content-type', default='article')
    p.add_argument('--style', default='thought leadership')
    p.add_argument('--count', type=int, default=3)
    p.add_argument('--format', choices=['json', 'markdown'], default='json')
    p.add_argument('--finalize', action='store_true', help='Run editorial pipeline to finalise drafts')
    args = p.parse_args()

    token = login(args.server, args.username, args.password)
    print('Logged in.')

    payload = {
        'platform': args.platform,
        'topic': args.topic,
        'content_type': args.content_type,
        'style': args.style,
        'use_tools': False,
        'count': args.count
    }

    if args.finalize:
        # Call editorial pipeline which generates, improves, and saves final markdown files
        url = f"{args.server.rstrip('/')}/api/content/editorial"
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        r = requests.post(url, json=payload, headers=headers, timeout=180)
        r.raise_for_status()
        out = r.json()
        if not out.get('success'):
            raise RuntimeError('Editorial pipeline failed: ' + str(out))
        print('Final files:', out.get('files'))
        print('Batch summary:', out.get('summary'))
    else:
        resp = generate(args.server, token, payload)
        if not resp.get('success'):
            raise RuntimeError('Generation failed: ' + str(resp))

        generated = resp.get('generated', [])

        # Save drafts as JSON and optional markdown formatting
        saved = []
        for i, g in enumerate(generated):
            if args.format == 'json':
                saved.extend(save_results(OUT_DIR, [g]))
            else:
                # markdown: extract text
                text = g.get('content', {})
                if isinstance(text, dict):
                    text = text.get('text', '')
                md = f"# Draft {i+1}: {args.topic}\n\n{text}\n"
                fname = OUT_DIR / f'draft_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{i}.md'
                OUT_DIR.mkdir(parents=True, exist_ok=True)
                fname.write_text(md, encoding='utf-8')
                saved.append(str(fname))
        print('Saved drafts:', saved)


if __name__ == '__main__':
    main()
