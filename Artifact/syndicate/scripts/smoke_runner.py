#!/usr/bin/env python3
"""Smoke runner to exercise LLM task processing, organization, and basic checks.

Usage: python scripts/smoke_runner.py --iterations 3
"""
import argparse
import logging
import time
import sys
from pathlib import Path

# Ensure local modules are importable when running as script
proj_root = Path(__file__).resolve().parents[1]
if str(proj_root) not in sys.path:
    sys.path.insert(0, str(proj_root))

log = logging.getLogger("smoke")


def run_once():
    """Process all pending llm_tasks by calling process_task sequentially."""
    from db_manager import get_db
    from main import Config
    from scripts.llm_worker import process_task

    db = get_db()
    cfg = Config()
    processed = 0

    while True:
        tasks = db.claim_llm_tasks(limit=10)
        if not tasks:
            break
        for t in tasks:
            try:
                process_task(t, cfg)
            except Exception as e:
                log.exception("Task processing failed: %s", e)
            processed += 1
    return processed


def organize_output():
    from scripts.organizer import sync

    base = Path(__file__).resolve().parents[1]
    src = (base / "output").resolve()
    dest = (base.parent / "syndicate-legacy" / "output").resolve()
    copied = sync(src, dest, dry_run=False)
    return copied


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--iterations", type=int, default=1)
    args = p.parse_args()

    for i in range(args.iterations):
        log.info(f"Smoke run iteration {i+1}/{args.iterations}")
        proc = run_once()
        log.info(f"Processed {proc} tasks (LLM)")
        copied = organize_output()
        log.info(f"Organized output, copied {copied} files")
        # small pause between loops
        time.sleep(1)

    log.info("Smoke run completed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
