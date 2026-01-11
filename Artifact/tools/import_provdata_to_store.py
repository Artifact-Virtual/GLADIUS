#!/usr/bin/env python3
"""Import prov_data parquet outputs into ARTY store as per-symbol records.json files.

Usage:
  python Artifact/tools/import_provdata_to_store.py --prov-dir ohlcv_data --store-dir Artifact/arty/store

This reads STOCK_PARQUET and CRYPTO_API_PARQUET produced by prov_data.py and writes
per-symbol folders under the store with `records.json` and `manifest.json`.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import json
import pandas as pd


def df_to_records(df: pd.DataFrame):
    out = []
    for _, r in df.iterrows():
        out.append({
            'timestamp': r['timestamp'].isoformat() if hasattr(r['timestamp'], 'isoformat') else str(r['timestamp']),
            'open': float(r['open']),
            'high': float(r['high']),
            'low': float(r['low']),
            'close': float(r['close']),
            'volume': float(r.get('volume', 0)),
        })
    return out


def import_parquet(p: Path, store_dir: Path):
    if not p.exists():
        print('No parquet:', p)
        return
    df = pd.read_parquet(p)
    # expect 'symbol' and 'timestamp'
    for sym, group in df.groupby('symbol'):
        name = str(sym).lower().replace('/', '_').replace(' ', '_')
        dest = store_dir / name
        dest.mkdir(parents=True, exist_ok=True)
        recs = df_to_records(group.sort_values('timestamp'))
        (dest / 'records.json').write_text(json.dumps(recs, indent=2), encoding='utf-8')
        manifest = {'symbol': sym, 'rows': len(recs)}
        (dest / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        print('Wrote', dest / 'records.json')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--prov-dir', default='ohlcv_data')
    p.add_argument('--store-dir', default='Artifact/arty/store')
    args = p.parse_args()

    import_parquet(Path(args.prov_dir) / 'stock_ohlcv.parquet', Path(args.store_dir))
    import_parquet(Path(args.prov_dir) / 'crypto_api.parquet', Path(args.store_dir))
    print('Import complete')
