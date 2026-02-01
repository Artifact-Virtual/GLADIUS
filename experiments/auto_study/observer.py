#!/usr/bin/env python3
"""
GLADIUS Auto-Study Observer
===========================

Watches experiment containers and logs observations WITHOUT interfering.
Runs parallel to system, reads container outputs, generates structured observations.

This module does NOT use AI - it uses rule-based observation to avoid circular dependencies.
GLADIUS will eventually control this module once mature.
"""

import os
import json
import time
import hashlib
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from collections import deque
import subprocess

# Paths
EXPERIMENTS_DIR = Path(__file__).parent.parent
CONTAINERS_DIR = EXPERIMENTS_DIR / "containers"
REPORTS_DIR = EXPERIMENTS_DIR / "auto_study" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class Observation:
    """Single observation from container"""
    timestamp: str
    container_id: str
    event_type: str  # log, metric, state_change, error, milestone
    source: str      # where the observation came from
    content: str     # raw content
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5  # 0-1 scale
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @property
    def hash(self) -> str:
        return hashlib.sha256(f"{self.timestamp}{self.content}".encode()).hexdigest()[:12]


@dataclass 
class ContainerMetrics:
    """Container resource metrics"""
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    memory_percent: float = 0.0
    disk_read_mb: float = 0.0
    disk_write_mb: float = 0.0
    network_rx_mb: float = 0.0
    network_tx_mb: float = 0.0
    uptime_seconds: float = 0.0


class ContainerWatcher:
    """Watches a single container"""
    
    def __init__(self, container_id: str, container_dir: Path):
        self.container_id = container_id
        self.container_dir = container_dir
        self.observations: deque = deque(maxlen=10000)
        self.metrics_history: deque = deque(maxlen=1000)
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self.log_positions: Dict[str, int] = {}  # Track log file positions
        
    def start(self):
        """Start watching container"""
        self.running = True
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()
        
    def stop(self):
        """Stop watching"""
        self.running = False
        if self._thread:
            self._thread.join(timeout=5)
    
    def _watch_loop(self):
        """Main watch loop"""
        while self.running:
            try:
                # Watch logs
                self._scan_logs()
                
                # Watch metrics (if container is docker)
                self._collect_metrics()
                
                # Watch state files
                self._scan_state_files()
                
                time.sleep(1)
            except Exception as e:
                self._add_observation("error", "watcher", f"Watch error: {e}", importance=0.8)
    
    def _scan_logs(self):
        """Scan log files for new content"""
        log_patterns = ["*.log", "logs/*.log", "output/*.log", "stdout.txt", "stderr.txt"]
        
        for pattern in log_patterns:
            for log_file in self.container_dir.glob(pattern):
                if not log_file.is_file():
                    continue
                    
                # Get last position
                last_pos = self.log_positions.get(str(log_file), 0)
                
                try:
                    with open(log_file, 'r') as f:
                        f.seek(last_pos)
                        new_content = f.read()
                        self.log_positions[str(log_file)] = f.tell()
                        
                        if new_content.strip():
                            self._parse_log_content(log_file.name, new_content)
                except Exception:
                    pass
    
    def _parse_log_content(self, source: str, content: str):
        """Parse log content and create observations"""
        for line in content.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Determine importance based on content
            importance = 0.3
            event_type = "log"
            
            # Error detection
            if any(kw in line.lower() for kw in ['error', 'exception', 'failed', 'crash']):
                importance = 0.9
                event_type = "error"
            # Warning detection
            elif any(kw in line.lower() for kw in ['warning', 'warn', 'deprecated']):
                importance = 0.6
                event_type = "log"
            # Milestone detection
            elif any(kw in line.lower() for kw in ['complete', 'success', 'finished', 'started', 'epoch', 'step']):
                importance = 0.7
                event_type = "milestone"
            # Metric detection
            elif any(kw in line.lower() for kw in ['loss:', 'accuracy:', 'score:', 'metric']):
                importance = 0.5
                event_type = "metric"
            
            self._add_observation(event_type, source, line, importance=importance)
    
    def _collect_metrics(self):
        """Collect container metrics via docker stats"""
        try:
            # Check if this is a docker container
            result = subprocess.run(
                ['docker', 'stats', '--no-stream', '--format', 
                 '{{.CPUPerc}},{{.MemUsage}},{{.NetIO}},{{.BlockIO}}',
                 self.container_id],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split(',')
                if len(parts) >= 4:
                    cpu = float(parts[0].replace('%', ''))
                    mem_parts = parts[1].split('/')
                    mem_used = self._parse_size(mem_parts[0].strip())
                    
                    metrics = ContainerMetrics(
                        cpu_percent=cpu,
                        memory_mb=mem_used
                    )
                    self.metrics_history.append(metrics)
                    
                    # High resource usage observation
                    if cpu > 90 or mem_used > 8000:
                        self._add_observation(
                            "metric", "docker_stats",
                            f"High resource usage: CPU={cpu}%, MEM={mem_used}MB",
                            importance=0.7
                        )
        except Exception:
            pass  # Container might not be docker
    
    def _scan_state_files(self):
        """Scan for state change files"""
        state_files = ["state.json", "status.json", "checkpoint.json"]
        
        for state_file in state_files:
            state_path = self.container_dir / state_file
            if state_path.exists():
                try:
                    with open(state_path) as f:
                        state = json.load(f)
                    
                    # Check for state changes
                    state_hash = hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()[:8]
                    cache_key = f"state_{state_file}"
                    
                    if hasattr(self, '_state_cache') and self._state_cache.get(cache_key) != state_hash:
                        self._add_observation(
                            "state_change", state_file,
                            f"State changed: {json.dumps(state)[:200]}",
                            importance=0.6,
                            metadata={"state": state}
                        )
                    
                    if not hasattr(self, '_state_cache'):
                        self._state_cache = {}
                    self._state_cache[cache_key] = state_hash
                except Exception:
                    pass
    
    def _parse_size(self, size_str: str) -> float:
        """Parse size string like '1.5GiB' to MB"""
        size_str = size_str.strip().upper()
        multipliers = {'B': 1/1024/1024, 'KB': 1/1024, 'KIB': 1/1024, 
                      'MB': 1, 'MIB': 1, 'GB': 1024, 'GIB': 1024}
        
        for suffix, mult in multipliers.items():
            if size_str.endswith(suffix):
                try:
                    return float(size_str[:-len(suffix)]) * mult
                except:
                    pass
        return 0.0
    
    def _add_observation(self, event_type: str, source: str, content: str, 
                        importance: float = 0.5, metadata: Dict = None):
        """Add observation to queue"""
        obs = Observation(
            timestamp=datetime.now().isoformat(),
            container_id=self.container_id,
            event_type=event_type,
            source=source,
            content=content,
            metadata=metadata or {},
            importance=importance
        )
        self.observations.append(obs)
    
    def get_observations(self, since: str = None, min_importance: float = 0.0) -> List[Observation]:
        """Get observations, optionally filtered"""
        obs_list = list(self.observations)
        
        if since:
            obs_list = [o for o in obs_list if o.timestamp > since]
        
        if min_importance > 0:
            obs_list = [o for o in obs_list if o.importance >= min_importance]
        
        return obs_list


class AutoStudyObserver:
    """Main observer managing all container watchers"""
    
    def __init__(self):
        self.watchers: Dict[str, ContainerWatcher] = {}
        self.global_observations: deque = deque(maxlen=50000)
        self.running = False
        
    def add_container(self, container_id: str, container_dir: Path):
        """Add container to watch"""
        if container_id not in self.watchers:
            watcher = ContainerWatcher(container_id, container_dir)
            self.watchers[container_id] = watcher
            if self.running:
                watcher.start()
    
    def remove_container(self, container_id: str):
        """Stop watching container"""
        if container_id in self.watchers:
            self.watchers[container_id].stop()
            del self.watchers[container_id]
    
    def start(self):
        """Start all watchers"""
        self.running = True
        for watcher in self.watchers.values():
            watcher.start()
        
        # Start aggregation thread
        self._agg_thread = threading.Thread(target=self._aggregate_loop, daemon=True)
        self._agg_thread.start()
    
    def stop(self):
        """Stop all watchers"""
        self.running = False
        for watcher in self.watchers.values():
            watcher.stop()
    
    def _aggregate_loop(self):
        """Aggregate observations from all watchers"""
        while self.running:
            for container_id, watcher in self.watchers.items():
                new_obs = watcher.get_observations()
                for obs in new_obs:
                    if obs not in self.global_observations:
                        self.global_observations.append(obs)
            time.sleep(5)
    
    def get_all_observations(self, min_importance: float = 0.0) -> List[Observation]:
        """Get all observations across all containers"""
        all_obs = []
        for watcher in self.watchers.values():
            all_obs.extend(watcher.get_observations(min_importance=min_importance))
        return sorted(all_obs, key=lambda x: x.timestamp)
    
    def save_observations(self, output_path: Path = None):
        """Save all observations to file"""
        if output_path is None:
            output_path = REPORTS_DIR / f"observations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        observations = self.get_all_observations()
        with open(output_path, 'w') as f:
            json.dump([o.to_dict() for o in observations], f, indent=2)
        
        return output_path
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary of all observations"""
        all_obs = self.get_all_observations()
        
        summary = {
            "generated_at": datetime.now().isoformat(),
            "total_observations": len(all_obs),
            "containers_watched": list(self.watchers.keys()),
            "by_type": {},
            "by_importance": {"high": 0, "medium": 0, "low": 0},
            "errors": [],
            "milestones": [],
            "recent_activity": []
        }
        
        for obs in all_obs:
            # Count by type
            summary["by_type"][obs.event_type] = summary["by_type"].get(obs.event_type, 0) + 1
            
            # Count by importance
            if obs.importance >= 0.8:
                summary["by_importance"]["high"] += 1
            elif obs.importance >= 0.5:
                summary["by_importance"]["medium"] += 1
            else:
                summary["by_importance"]["low"] += 1
            
            # Collect errors
            if obs.event_type == "error":
                summary["errors"].append({
                    "time": obs.timestamp,
                    "container": obs.container_id,
                    "content": obs.content[:200]
                })
            
            # Collect milestones
            if obs.event_type == "milestone":
                summary["milestones"].append({
                    "time": obs.timestamp,
                    "container": obs.container_id,
                    "content": obs.content[:200]
                })
        
        # Recent activity (last 20)
        summary["recent_activity"] = [
            {"time": o.timestamp, "type": o.event_type, "content": o.content[:100]}
            for o in all_obs[-20:]
        ]
        
        return summary


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="GLADIUS Auto-Study Observer")
    parser.add_argument("--watch", type=str, help="Container directory to watch")
    parser.add_argument("--id", type=str, default="default", help="Container ID")
    parser.add_argument("--summary", action="store_true", help="Generate summary")
    
    args = parser.parse_args()
    
    observer = AutoStudyObserver()
    
    if args.watch:
        container_dir = Path(args.watch)
        if container_dir.exists():
            observer.add_container(args.id, container_dir)
            observer.start()
            
            print(f"Watching container: {args.id} at {container_dir}")
            print("Press Ctrl+C to stop and save observations...")
            
            try:
                while True:
                    time.sleep(10)
                    summary = observer.generate_summary()
                    print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                          f"Observations: {summary['total_observations']} | "
                          f"Errors: {len(summary['errors'])} | "
                          f"Milestones: {len(summary['milestones'])}", end="")
            except KeyboardInterrupt:
                print("\nStopping observer...")
                observer.stop()
                output = observer.save_observations()
                print(f"Observations saved to: {output}")
        else:
            print(f"Container directory not found: {container_dir}")
    
    elif args.summary:
        # Load existing observations
        obs_files = list(REPORTS_DIR.glob("observations_*.json"))
        if obs_files:
            latest = max(obs_files, key=lambda p: p.stat().st_mtime)
            with open(latest) as f:
                data = json.load(f)
            print(f"Loaded {len(data)} observations from {latest}")
            print(json.dumps(data[:5], indent=2))
        else:
            print("No observation files found")
