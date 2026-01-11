#!/usr/bin/env python3
"""Organizer: mirror syndicate output into legacy layout (idempotent)

Default: copy from ./output to ../syndicate-legacy/output preserving subtree.
Generates a 'file_index.json' manifest at destination root.
"""
import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path
from datetime import datetime


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def build_manifest(dest_root: Path) -> dict:
    entries = []
    for p in sorted(dest_root.rglob("*")):
        if p.is_file():
            stat = p.stat()
            entries.append(
                {
                    "path": str(p.relative_to(dest_root)),
                    "size": stat.st_size,
                    "mtime": stat.st_mtime,
                }
            )
    manifest = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "files": entries,
    }
    return manifest


def sync(src: Path, dest: Path, dry_run: bool = False) -> int:
    if not src.exists():
        raise FileNotFoundError(f"Source not found: {src}")
    dest.mkdir(parents=True, exist_ok=True)

    copied = 0
    for p in src.rglob("*"):
        if p.is_dir():
            continue
        rel = p.relative_to(src)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        # copy only if missing or older
        if not target.exists() or p.stat().st_mtime > target.stat().st_mtime:
            if dry_run:
                print(f"[DRY] Copy {p} -> {target}")
            else:
                shutil.copy2(p, target)
            copied += 1
    # write manifest
    manifest = build_manifest(dest)
    manifest_path = dest / "file_index.json"
    if not dry_run:
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
    return copied


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", default="./output", help="Source output dir")
    p.add_argument("--dest", default="../syndicate-legacy/output", help="Destination directory")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    src = Path(args.src).resolve()
    dest = Path(args.dest).resolve()

    copied = sync(src, dest, dry_run=args.dry_run)
    print(f"Copied {copied} files")


if __name__ == "__main__":
    main()
