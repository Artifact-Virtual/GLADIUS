#!/usr/bin/env python3
"""
SENTINEL Process Guardian
=========================

Manages persistent processes and ensures they stay alive.
Monitors a target directory and auto-restarts any processes that die.

Features:
- Process lifecycle management
- Auto-restart on failure
- Health monitoring
- Threat research (AI/cybersecurity threats)
- Fail-safe recovery

Author: Artifact Virtual Systems
"""

import os
import sys
import json
import time
import signal
import hashlib
import logging
import subprocess
import threading
import psutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | SENTINEL-GUARDIAN | %(levelname)s | %(message)s'
)
logger = logging.getLogger("SENTINEL.ProcessGuardian")


class ProcessState(Enum):
    """Process states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    FAILED = "failed"
    RESTARTING = "restarting"


@dataclass
class ManagedProcess:
    """A process managed by SENTINEL"""
    name: str
    command: str
    working_dir: str
    pid: Optional[int] = None
    state: str = "stopped"
    restart_count: int = 0
    max_restarts: int = 10
    last_start: str = ""
    last_crash: str = ""
    uptime_seconds: float = 0.0
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ProcessGuardian:
    """
    SENTINEL Process Guardian
    
    Monitors and manages persistent processes, ensuring they stay alive.
    """
    
    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path(__file__).parent / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.processes_file = self.config_dir / "managed_processes.json"
        self.processes: Dict[str, ManagedProcess] = {}
        self.running = True
        self.monitor_interval = 5  # seconds
        
        # Load existing processes
        self._load_processes()
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)
        
        logger.info("ProcessGuardian initialized")
    
    def _shutdown(self, signum, frame):
        """Graceful shutdown"""
        logger.info("Shutdown signal received")
        self.running = False
        self._save_processes()
    
    def _load_processes(self):
        """Load managed processes from config"""
        if self.processes_file.exists():
            try:
                with open(self.processes_file) as f:
                    data = json.load(f)
                    for name, proc_data in data.items():
                        self.processes[name] = ManagedProcess(**proc_data)
                logger.info(f"Loaded {len(self.processes)} managed processes")
            except Exception as e:
                logger.error(f"Failed to load processes: {e}")
    
    def _save_processes(self):
        """Save managed processes to config"""
        try:
            with open(self.processes_file, 'w') as f:
                json.dump({k: v.to_dict() for k, v in self.processes.items()}, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save processes: {e}")
    
    def register(self, name: str, command: str, working_dir: str = ".", max_restarts: int = 10) -> bool:
        """Register a process to be managed"""
        if name in self.processes:
            logger.warning(f"Process {name} already registered")
            return False
        
        self.processes[name] = ManagedProcess(
            name=name,
            command=command,
            working_dir=str(Path(working_dir).absolute()),
            max_restarts=max_restarts
        )
        self._save_processes()
        logger.info(f"Registered process: {name}")
        return True
    
    def unregister(self, name: str) -> bool:
        """Unregister a managed process"""
        if name not in self.processes:
            logger.warning(f"Process {name} not found")
            return False
        
        # Stop if running
        self.stop(name)
        
        del self.processes[name]
        self._save_processes()
        logger.info(f"Unregistered process: {name}")
        return True
    
    def start(self, name: str) -> bool:
        """Start a managed process"""
        if name not in self.processes:
            logger.error(f"Process {name} not registered")
            return False
        
        proc = self.processes[name]
        
        if proc.pid and self._is_running(proc.pid):
            logger.warning(f"Process {name} already running (PID: {proc.pid})")
            return True
        
        try:
            proc.state = ProcessState.STARTING.value
            
            # Start the process
            p = subprocess.Popen(
                proc.command,
                shell=True,
                cwd=proc.working_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            proc.pid = p.pid
            proc.state = ProcessState.RUNNING.value
            proc.last_start = datetime.now().isoformat()
            
            self._save_processes()
            logger.info(f"Started {name} (PID: {proc.pid})")
            return True
            
        except Exception as e:
            proc.state = ProcessState.FAILED.value
            logger.error(f"Failed to start {name}: {e}")
            return False
    
    def stop(self, name: str) -> bool:
        """Stop a managed process"""
        if name not in self.processes:
            logger.error(f"Process {name} not registered")
            return False
        
        proc = self.processes[name]
        
        if not proc.pid:
            logger.warning(f"Process {name} has no PID")
            return True
        
        try:
            if self._is_running(proc.pid):
                os.kill(proc.pid, signal.SIGTERM)
                time.sleep(1)
                
                # Force kill if still running
                if self._is_running(proc.pid):
                    os.kill(proc.pid, signal.SIGKILL)
            
            proc.pid = None
            proc.state = ProcessState.STOPPED.value
            self._save_processes()
            
            logger.info(f"Stopped {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop {name}: {e}")
            return False
    
    def restart(self, name: str) -> bool:
        """Restart a managed process"""
        self.stop(name)
        time.sleep(1)
        return self.start(name)
    
    def _is_running(self, pid: int) -> bool:
        """Check if a process is running"""
        try:
            return psutil.pid_exists(pid) and psutil.Process(pid).status() != psutil.STATUS_ZOMBIE
        except:
            return False
    
    def status(self, name: str = None) -> Dict:
        """Get status of processes"""
        if name:
            if name not in self.processes:
                return {"error": f"Process {name} not found"}
            
            proc = self.processes[name]
            running = proc.pid and self._is_running(proc.pid)
            
            return {
                "name": proc.name,
                "pid": proc.pid,
                "state": "running" if running else "stopped",
                "restart_count": proc.restart_count,
                "last_start": proc.last_start,
                "command": proc.command
            }
        
        # All processes
        result = {}
        for name, proc in self.processes.items():
            running = proc.pid and self._is_running(proc.pid)
            result[name] = {
                "pid": proc.pid,
                "state": "running" if running else "stopped",
                "restart_count": proc.restart_count
            }
        
        return result
    
    def monitor_loop(self):
        """Main monitoring loop - auto-restart failed processes"""
        logger.info("Starting process monitor loop")
        
        while self.running:
            for name, proc in self.processes.items():
                if proc.state == ProcessState.RUNNING.value:
                    if not proc.pid or not self._is_running(proc.pid):
                        # Process died, restart it
                        proc.last_crash = datetime.now().isoformat()
                        proc.restart_count += 1
                        
                        if proc.restart_count <= proc.max_restarts:
                            logger.warning(f"Process {name} died, restarting ({proc.restart_count}/{proc.max_restarts})")
                            proc.state = ProcessState.RESTARTING.value
                            self._save_processes()
                            
                            time.sleep(2)  # Brief delay before restart
                            self.start(name)
                        else:
                            logger.error(f"Process {name} exceeded max restarts, giving up")
                            proc.state = ProcessState.FAILED.value
                            self._save_processes()
            
            time.sleep(self.monitor_interval)
        
        logger.info("Monitor loop stopped")
    
    def start_all(self):
        """Start all registered processes"""
        for name in self.processes:
            self.start(name)
    
    def stop_all(self):
        """Stop all managed processes"""
        for name in self.processes:
            self.stop(name)
    
    def watch_directory(self, directory: Path, pattern: str = "*.py"):
        """Watch a directory and manage all matching processes"""
        directory = Path(directory)
        if not directory.exists():
            logger.error(f"Directory {directory} does not exist")
            return
        
        # Find all matching files
        for file_path in directory.glob(pattern):
            name = file_path.stem
            command = f"python3 {file_path}"
            
            if name not in self.processes:
                self.register(name, command, str(directory))
        
        logger.info(f"Watching {directory} for {pattern}")


class ThreatResearcher:
    """
    SENTINEL Threat Researcher
    
    Researches AI and cybersecurity threats to keep the system protected.
    """
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path(__file__).parent.parent.parent / "Artifact" / "research_outputs" / "threats"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.sources = {
            "arxiv_security": "https://arxiv.org/list/cs.CR/recent",
            "arxiv_ai": "https://arxiv.org/list/cs.AI/recent",
            "cve": "https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=",
            "github_advisories": "https://github.com/advisories",
            "nist_nvd": "https://nvd.nist.gov/vuln/search/results",
        }
        
        self.keywords = [
            "llm vulnerability",
            "ai injection attack",
            "prompt injection",
            "model extraction",
            "adversarial attack",
            "neural network security",
            "data poisoning",
            "model backdoor",
            "ransomware",
            "zero day",
            "critical vulnerability",
            "remote code execution"
        ]
        
        logger.info("ThreatResearcher initialized")
    
    def research_cycle(self) -> Dict[str, Any]:
        """Run a threat research cycle"""
        import aiohttp
        import asyncio
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "threats_found": [],
            "advisories": [],
            "research_papers": []
        }
        
        # For now, just log what we would do
        # Full implementation would scrape/API the sources
        logger.info("Running threat research cycle...")
        logger.info(f"Sources: {list(self.sources.keys())}")
        logger.info(f"Keywords: {self.keywords[:5]}...")
        
        # Save results
        output_file = self.output_dir / f"threat_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Research results saved to {output_file}")
        return results


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="SENTINEL Process Guardian")
    parser.add_argument("command", choices=["monitor", "register", "unregister", "start", "stop", "restart", "status", "research"],
                       help="Command to execute")
    parser.add_argument("--name", help="Process name")
    parser.add_argument("--cmd", help="Command to run")
    parser.add_argument("--dir", default=".", help="Working directory")
    parser.add_argument("--watch", help="Directory to watch")
    
    args = parser.parse_args()
    
    guardian = ProcessGuardian()
    
    if args.command == "monitor":
        if args.watch:
            guardian.watch_directory(Path(args.watch))
        guardian.start_all()
        guardian.monitor_loop()
        
    elif args.command == "register":
        if not args.name or not args.cmd:
            print("--name and --cmd required")
            return
        guardian.register(args.name, args.cmd, args.dir)
        
    elif args.command == "unregister":
        if not args.name:
            print("--name required")
            return
        guardian.unregister(args.name)
        
    elif args.command == "start":
        if args.name:
            guardian.start(args.name)
        else:
            guardian.start_all()
            
    elif args.command == "stop":
        if args.name:
            guardian.stop(args.name)
        else:
            guardian.stop_all()
            
    elif args.command == "restart":
        if not args.name:
            print("--name required")
            return
        guardian.restart(args.name)
        
    elif args.command == "status":
        status = guardian.status(args.name)
        print(json.dumps(status, indent=2))
        
    elif args.command == "research":
        researcher = ThreatResearcher()
        researcher.research_cycle()


if __name__ == "__main__":
    main()
