"""
SENTINEL Watchdog
=================

Monitors all SENTINEL processes and auto-restarts on failure.
Turing-safe: Only killed by power loss or password-protected command.

Features:
- Process monitoring with health checks
- Automatic restart on crash
- Password-protected kill command
- Heartbeat logging for audit
- Integration with systemd (optional)

Author: Artifact Virtual Systems
"""

import os
import sys
import json
import time
import signal
import hashlib
import logging
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SENTINEL.Watchdog")


class ProcessState(Enum):
    """State of a managed process"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    CRASHED = "crashed"
    RESTARTING = "restarting"


@dataclass
class ManagedProcess:
    """A process managed by the watchdog"""
    name: str
    command: List[str]
    working_dir: str
    state: ProcessState
    pid: Optional[int]
    restart_count: int
    last_start: Optional[datetime]
    last_crash: Optional[datetime]
    max_restarts: int
    restart_delay: int  # seconds


class Watchdog:
    """
    Monitors SENTINEL processes and ensures they stay running.
    
    Only killed by:
    1. Power loss
    2. Password-protected explicit command
    """
    
    KILL_PASSWORD_ENV = "SENTINEL_KILL_PASSWORD"
    HEARTBEAT_INTERVAL = 30  # seconds
    HEALTH_CHECK_INTERVAL = 10  # seconds
    
    def __init__(self, config_path: Optional[str] = None):
        self.base_path = Path(__file__).parent
        self.config_path = config_path or self.base_path / "config" / "watchdog_config.json"
        
        # Managed processes
        self.processes: Dict[str, ManagedProcess] = {}
        self.proc_handles: Dict[str, subprocess.Popen] = {}
        
        # State
        self.running = False
        self.shutdown_requested = False
        self.shutdown_password_verified = False
        
        # Load configuration
        self.config = self._load_config()
        self._init_processes()
        
        # Heartbeat log
        self.heartbeat_log = self.base_path / "watchdog_heartbeat.log"
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        logger.info("Watchdog initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load watchdog configuration"""
        default_config = {
            "processes": [
                {
                    "name": "learning_daemon",
                    "command": ["python", "services/learning_daemon.py", "start"],
                    "working_dir": str(self.base_path.parent),
                    "max_restarts": 10,
                    "restart_delay": 5
                }
            ],
            "heartbeat_interval": 30,
            "health_check_interval": 10,
            "max_total_restarts_per_hour": 30
        }
        
        try:
            if Path(self.config_path).exists():
                with open(self.config_path) as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
        except Exception as e:
            logger.warning(f"Could not load config: {e}")
        
        return default_config
    
    def _init_processes(self):
        """Initialize managed processes from config"""
        for proc_config in self.config.get("processes", []):
            name = proc_config.get("name")
            if not name:
                continue
            
            self.processes[name] = ManagedProcess(
                name=name,
                command=proc_config.get("command", []),
                working_dir=proc_config.get("working_dir", str(self.base_path.parent)),
                state=ProcessState.STOPPED,
                pid=None,
                restart_count=0,
                last_start=None,
                last_crash=None,
                max_restarts=proc_config.get("max_restarts", 10),
                restart_delay=proc_config.get("restart_delay", 5)
            )
    
    def _signal_handler(self, signum, frame):
        """
        Handle shutdown signals.
        Requires password verification for graceful shutdown.
        """
        logger.warning(f"Received signal {signum}")
        
        if not self.shutdown_password_verified:
            logger.warning("Shutdown signal ignored - password not verified")
            logger.info("Use watchdog.stop(password='...') to properly shutdown")
            return
        
        logger.info("Password verified - initiating shutdown")
        self.shutdown_requested = True
    
    def verify_kill_password(self, password: str) -> bool:
        """Verify the kill password"""
        stored_hash = os.getenv(self.KILL_PASSWORD_ENV)
        if not stored_hash:
            logger.warning("No kill password set in environment")
            # If no password is set, require explicit confirmation
            return False
        
        provided_hash = hashlib.sha256(password.encode()).hexdigest()
        return provided_hash == stored_hash
    
    def _log_heartbeat(self):
        """Log heartbeat for audit trail"""
        try:
            with open(self.heartbeat_log, "a") as f:
                status = {
                    "timestamp": datetime.now().isoformat(),
                    "processes": {
                        name: {
                            "state": proc.state.value,
                            "pid": proc.pid,
                            "restart_count": proc.restart_count
                        }
                        for name, proc in self.processes.items()
                    }
                }
                f.write(json.dumps(status) + "\n")
        except Exception as e:
            logger.error(f"Failed to log heartbeat: {e}")
    
    def start_process(self, name: str) -> bool:
        """Start a managed process"""
        if name not in self.processes:
            logger.error(f"Unknown process: {name}")
            return False
        
        proc = self.processes[name]
        
        if proc.state == ProcessState.RUNNING:
            logger.info(f"Process {name} already running")
            return True
        
        try:
            proc.state = ProcessState.STARTING
            
            # Start the process
            handle = subprocess.Popen(
                proc.command,
                cwd=proc.working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True  # Detach from parent
            )
            
            self.proc_handles[name] = handle
            proc.pid = handle.pid
            proc.state = ProcessState.RUNNING
            proc.last_start = datetime.now()
            
            logger.info(f"Started {name} with PID {proc.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start {name}: {e}")
            proc.state = ProcessState.CRASHED
            proc.last_crash = datetime.now()
            return False
    
    def stop_process(self, name: str, force: bool = False) -> bool:
        """Stop a managed process"""
        if name not in self.processes:
            logger.error(f"Unknown process: {name}")
            return False
        
        proc = self.processes[name]
        
        if proc.state == ProcessState.STOPPED:
            return True
        
        proc.state = ProcessState.STOPPING
        
        try:
            if name in self.proc_handles:
                handle = self.proc_handles[name]
                
                if force:
                    handle.kill()
                else:
                    handle.terminate()
                
                # Wait for process to end
                try:
                    handle.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    handle.kill()
                    handle.wait()
                
                del self.proc_handles[name]
            
            proc.state = ProcessState.STOPPED
            proc.pid = None
            logger.info(f"Stopped {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop {name}: {e}")
            return False
    
    def check_process_health(self, name: str) -> bool:
        """Check if a process is healthy"""
        if name not in self.processes:
            return False
        
        proc = self.processes[name]
        
        if proc.state != ProcessState.RUNNING:
            return False
        
        if name not in self.proc_handles:
            proc.state = ProcessState.CRASHED
            return False
        
        handle = self.proc_handles[name]
        
        # Check if process is still running
        poll_result = handle.poll()
        if poll_result is not None:
            # Process has exited
            exit_code = poll_result
            logger.warning(f"Process {name} exited with code {exit_code}")
            proc.state = ProcessState.CRASHED
            proc.last_crash = datetime.now()
            return False
        
        return True
    
    async def restart_process(self, name: str):
        """Restart a crashed process"""
        if name not in self.processes:
            return
        
        proc = self.processes[name]
        
        # Check restart limits
        if proc.restart_count >= proc.max_restarts:
            logger.error(f"Max restarts ({proc.max_restarts}) reached for {name}")
            proc.state = ProcessState.STOPPED
            return
        
        proc.state = ProcessState.RESTARTING
        proc.restart_count += 1
        
        # Wait before restart
        logger.info(f"Waiting {proc.restart_delay}s before restarting {name}...")
        await asyncio.sleep(proc.restart_delay)
        
        # Start the process
        if self.start_process(name):
            logger.info(f"Restarted {name} (attempt {proc.restart_count})")
        else:
            logger.error(f"Failed to restart {name}")
    
    async def health_check_loop(self):
        """Main health check loop"""
        while self.running and not self.shutdown_requested:
            for name, proc in self.processes.items():
                if proc.state == ProcessState.RUNNING:
                    if not self.check_process_health(name):
                        # Process crashed - schedule restart
                        asyncio.create_task(self.restart_process(name))
            
            await asyncio.sleep(self.config.get("health_check_interval", 10))
    
    async def heartbeat_loop(self):
        """Heartbeat logging loop"""
        while self.running and not self.shutdown_requested:
            self._log_heartbeat()
            await asyncio.sleep(self.config.get("heartbeat_interval", 30))
    
    async def run(self):
        """Main watchdog loop"""
        logger.info("Watchdog starting...")
        self.running = True
        
        # Start all managed processes
        for name in self.processes:
            self.start_process(name)
        
        try:
            # Run health check and heartbeat in parallel
            await asyncio.gather(
                self.health_check_loop(),
                self.heartbeat_loop()
            )
        except asyncio.CancelledError:
            logger.info("Watchdog cancelled")
        except Exception as e:
            logger.error(f"Watchdog error: {e}")
        finally:
            # Cleanup
            await self.cleanup()
    
    async def cleanup(self):
        """Clean shutdown of all processes"""
        logger.info("Cleaning up managed processes...")
        
        for name in list(self.processes.keys()):
            self.stop_process(name)
        
        self.running = False
        logger.info("Watchdog stopped")
    
    def stop(self, password: str) -> bool:
        """
        Stop the watchdog with password verification.
        """
        if not self.verify_kill_password(password):
            logger.warning("Invalid password for watchdog stop")
            return False
        
        self.shutdown_password_verified = True
        self.shutdown_requested = True
        logger.info("Watchdog stop authorized")
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current watchdog status"""
        return {
            "running": self.running,
            "shutdown_requested": self.shutdown_requested,
            "processes": {
                name: {
                    "state": proc.state.value,
                    "pid": proc.pid,
                    "restart_count": proc.restart_count,
                    "last_start": proc.last_start.isoformat() if proc.last_start else None,
                    "last_crash": proc.last_crash.isoformat() if proc.last_crash else None
                }
                for name, proc in self.processes.items()
            }
        }
    
    def add_process(self, name: str, command: List[str], 
                   working_dir: Optional[str] = None,
                   max_restarts: int = 10,
                   restart_delay: int = 5):
        """Dynamically add a process to watch"""
        if name in self.processes:
            logger.warning(f"Process {name} already exists")
            return
        
        self.processes[name] = ManagedProcess(
            name=name,
            command=command,
            working_dir=working_dir or str(self.base_path.parent),
            state=ProcessState.STOPPED,
            pid=None,
            restart_count=0,
            last_start=None,
            last_crash=None,
            max_restarts=max_restarts,
            restart_delay=restart_delay
        )
        
        # Auto-start if watchdog is running
        if self.running:
            self.start_process(name)


# CLI interface
async def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SENTINEL Watchdog")
    parser.add_argument("command", choices=["start", "stop", "status"],
                       help="Command to execute")
    parser.add_argument("--password", help="Kill password for stop command")
    
    args = parser.parse_args()
    
    watchdog = Watchdog()
    
    if args.command == "start":
        await watchdog.run()
    elif args.command == "stop":
        if not args.password:
            print("Error: --password required for stop command")
            sys.exit(1)
        success = watchdog.stop(args.password)
        print("Stop requested" if success else "Stop failed - invalid password")
    elif args.command == "status":
        status = watchdog.get_status()
        print(json.dumps(status, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
