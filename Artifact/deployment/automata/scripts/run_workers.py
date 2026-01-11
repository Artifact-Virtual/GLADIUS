#!/usr/bin/env python3
"""Run editorial and/or publish workers as a standalone process.

Usage examples:
  ./run_workers.py --editorial --interval 60
  ./run_workers.py --publish --interval 30 --oneshot
"""
import argparse
import time
from pathlib import Path
from automata.core.manager import EnterpriseManager


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--editorial', action='store_true')
    p.add_argument('--publish', action='store_true')
    p.add_argument('--interval', type=int, default=30)
    p.add_argument('--oneshot', action='store_true')
    args = p.parse_args()

    manager = EnterpriseManager()

    # Ensure manager is initialized (but do not start full async loops)
    # We'll use the pre-created workers
    try:
        if args.editorial and manager.editorial_worker:
            if args.oneshot:
                manager.editorial_worker.run_once()
            else:
                manager.editorial_worker.interval = args.interval
                manager.editorial_worker.start()
        if args.publish and manager.publish_worker:
            if args.oneshot:
                print(manager.publish_worker.run_once())
            else:
                manager.publish_worker.interval = args.interval
                manager.publish_worker.start()

        if not args.oneshot:
            print('Workers running. Press Ctrl-C to stop.')
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print('Shutting down workers...')
        if manager.editorial_worker:
            manager.editorial_worker.stop()
        if manager.publish_worker:
            manager.publish_worker.stop()


if __name__ == '__main__':
    main()
