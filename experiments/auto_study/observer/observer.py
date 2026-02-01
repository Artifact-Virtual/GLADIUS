#!/usr/bin/env python3
"""
Auto-Study Observer Team

Watches experiments in real-time, captures all metrics and events.
Runs parallel to experiments without interference.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | OBSERVER | %(message)s'
)
logger = logging.getLogger(__name__)


class ExperimentObserver(FileSystemEventHandler):
    """Watches experiment directories for changes."""
    
    def __init__(self, experiment_dir: Path, output_dir: Path):
        self.experiment_dir = experiment_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.observations = []
        self.metrics_buffer = []
        self.lock = threading.Lock()
        
        # Observation log
        self.log_file = self.output_dir / f"observations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    
    def on_created(self, event):
        """Log file creation events."""
        if not event.is_directory:
            self._log_event('created', event.src_path)
    
    def on_modified(self, event):
        """Log file modification events."""
        if not event.is_directory:
            self._log_event('modified', event.src_path)
            
            # Special handling for stats files
            if 'stats.json' in event.src_path or 'summary.json' in event.src_path:
                self._capture_metrics(event.src_path)
    
    def _log_event(self, event_type: str, path: str) -> None:
        """Log an observation event."""
        observation = {
            'timestamp': datetime.now().isoformat(),
            'event': event_type,
            'path': path,
            'relative_path': str(Path(path).relative_to(self.experiment_dir))
        }
        
        with self.lock:
            self.observations.append(observation)
            
            # Write to log file
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(observation) + '\n')
        
        logger.debug(f"{event_type}: {path}")
    
    def _capture_metrics(self, path: str) -> None:
        """Capture metrics from stats files."""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'source': path,
                'data': data
            }
            
            with self.lock:
                self.metrics_buffer.append(metrics)
            
            logger.info(f"Captured metrics from {Path(path).name}")
            
        except Exception as e:
            logger.error(f"Failed to capture metrics: {e}")
    
    def get_observations(self) -> List[Dict[str, Any]]:
        """Get all observations."""
        with self.lock:
            return list(self.observations)
    
    def get_metrics(self) -> List[Dict[str, Any]]:
        """Get buffered metrics."""
        with self.lock:
            return list(self.metrics_buffer)
    
    def save_snapshot(self) -> None:
        """Save current observation state."""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'total_observations': len(self.observations),
            'total_metrics': len(self.metrics_buffer),
            'observations': self.observations[-100:],  # Last 100
            'metrics': self.metrics_buffer[-50:]  # Last 50
        }
        
        snapshot_file = self.output_dir / f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(snapshot_file, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        logger.info(f"Snapshot saved: {snapshot_file}")


class ObserverTeam:
    """
    Observer Team - Watches experiments without interference.
    """
    
    def __init__(self, experiments_dir: str = None):
        self.experiments_dir = Path(experiments_dir or '/home/adam/worxpace/gladius/experiments')
        self.output_dir = self.experiments_dir / 'auto_study' / 'observer' / 'logs'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.watchers = {}
        self.observer = Observer()
        self.running = False
    
    def watch_experiment(self, experiment_name: str) -> None:
        """Start watching an experiment."""
        experiment_dir = self.experiments_dir / experiment_name
        
        if not experiment_dir.exists():
            logger.error(f"Experiment not found: {experiment_name}")
            return
        
        handler = ExperimentObserver(
            experiment_dir,
            self.output_dir / experiment_name
        )
        
        self.observer.schedule(handler, str(experiment_dir), recursive=True)
        self.watchers[experiment_name] = handler
        
        logger.info(f"Now watching: {experiment_name}")
    
    def watch_all(self) -> None:
        """Watch all experiments."""
        for item in self.experiments_dir.iterdir():
            if item.is_dir() and item.name not in ['auto_study', 'templates', '__pycache__']:
                self.watch_experiment(item.name)
    
    def start(self) -> None:
        """Start the observer."""
        self.observer.start()
        self.running = True
        logger.info("Observer team started")
    
    def stop(self) -> None:
        """Stop the observer."""
        self.observer.stop()
        self.observer.join()
        self.running = False
        
        # Save final snapshots
        for name, handler in self.watchers.items():
            handler.save_snapshot()
        
        logger.info("Observer team stopped")
    
    def run_loop(self, snapshot_interval: int = 300) -> None:
        """Run observation loop."""
        self.start()
        last_snapshot = time.time()
        
        try:
            while self.running:
                time.sleep(1)
                
                # Periodic snapshots
                if time.time() - last_snapshot > snapshot_interval:
                    for handler in self.watchers.values():
                        handler.save_snapshot()
                    last_snapshot = time.time()
        
        except KeyboardInterrupt:
            logger.info("Observer interrupted")
        
        finally:
            self.stop()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-Study Observer Team')
    parser.add_argument('--experiment', type=str, help='Specific experiment to watch')
    parser.add_argument('--all', action='store_true', help='Watch all experiments')
    parser.add_argument('--snapshot-interval', type=int, default=300, help='Snapshot interval in seconds')
    
    args = parser.parse_args()
    
    team = ObserverTeam()
    
    if args.experiment:
        team.watch_experiment(args.experiment)
    elif args.all:
        team.watch_all()
    else:
        team.watch_all()
    
    team.run_loop(args.snapshot_interval)


if __name__ == '__main__':
    main()
