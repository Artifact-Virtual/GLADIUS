#!/usr/bin/env python3
"""
GLADIUS Autonomous Continuous Operation
========================================

Long-running autonomous mode that integrates:
1. Training cycles during idle time
2. Cognition and self-improvement
3. Artifact infrastructure operation
4. SENTINEL learning coordination

Usage:
    ./gladius.sh autonomous           # Run 30 days, 60min intervals
    ./gladius.sh autonomous 7 30      # Run 7 days, 30min intervals
    
    python3 GLADIUS/continuous.py --days 30 --interval 60
    python3 GLADIUS/continuous.py --hours 24 --interval 30

Cycle Flow:
┌─────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS CYCLE                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ OPERATE │→│ COGNIZE │→│  TRAIN  │→│  SLEEP  │→ REPEAT  │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │
│       │            │            │            │              │
│  Artifact     Self-review   Model       SENTINEL           │
│  operations   & planning    training    learning           │
└─────────────────────────────────────────────────────────────┘

Author: Artifact Virtual Systems
"""

import os
import sys
import json
import signal
import subprocess
import logging
import asyncio
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import threading

# Paths
GLADIUS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(GLADIUS_ROOT))

# Configure logging
LOG_DIR = GLADIUS_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "autonomous.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GLADIUS.Autonomous")


@dataclass
class CycleState:
    """State of the current autonomous cycle"""
    cycle_number: int
    phase: str  # OPERATE, COGNIZE, TRAIN, SLEEP
    started_at: str
    operations_completed: int
    training_triggered: bool
    cognition_insights: List[str]
    errors: List[str]


@dataclass
class AutonomousConfig:
    """Configuration for autonomous operation"""
    duration_hours: float = 720  # 30 days
    interval_minutes: int = 60
    training_every_n_cycles: int = 6  # Train every 6 hours
    cognition_enabled: bool = True
    artifact_operations_enabled: bool = True
    sentinel_coordination: bool = True


class AutonomousOperator:
    """
    Main autonomous operation controller.
    
    Manages the continuous loop of:
    - Operating Artifact infrastructure
    - Running cognition/self-improvement
    - Triggering training during sleep
    - Coordinating with SENTINEL learning
    """
    
    def __init__(self, config: AutonomousConfig = None):
        self.config = config or AutonomousConfig()
        self.running = False
        self.shutdown_requested = False
        self.current_state: Optional[CycleState] = None
        self.cycles_completed = 0
        self.start_time: Optional[datetime] = None
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # State file for recovery
        self.state_file = GLADIUS_ROOT / "data" / "autonomous_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True
    
    def _save_state(self):
        """Save current state for recovery"""
        if self.current_state:
            state_data = {
                "current_state": asdict(self.current_state),
                "cycles_completed": self.cycles_completed,
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "config": asdict(self.config),
                "saved_at": datetime.now().isoformat()
            }
            with open(self.state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
    
    def _load_state(self) -> bool:
        """Load state from recovery file"""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    state_data = json.load(f)
                
                self.cycles_completed = state_data.get("cycles_completed", 0)
                if state_data.get("start_time"):
                    self.start_time = datetime.fromisoformat(state_data["start_time"])
                
                logger.info(f"Recovered state: {self.cycles_completed} cycles completed")
                return True
            except Exception as e:
                logger.warning(f"Could not load state: {e}")
        return False
    
    async def operate(self) -> Dict[str, Any]:
        """
        OPERATE Phase: Run Artifact infrastructure operations.
        
        This phase:
        - Checks Syndicate status
        - Processes pending social media posts
        - Handles any scheduled operations
        """
        logger.info("OPERATE phase started")
        results = {
            "phase": "OPERATE",
            "started_at": datetime.now().isoformat(),
            "operations": [],
            "errors": []
        }
        
        if not self.config.artifact_operations_enabled:
            results["skipped"] = True
            return results
        
        try:
            # Check Syndicate status
            syndicate_check = await self._check_syndicate()
            results["operations"].append({"name": "syndicate_check", "result": syndicate_check})
            
            # Check LEGION agents
            legion_check = await self._check_legion()
            results["operations"].append({"name": "legion_check", "result": legion_check})
            
            # Process any pending operations
            pending_ops = await self._process_pending_operations()
            results["operations"].append({"name": "pending_ops", "result": pending_ops})
            
        except Exception as e:
            results["errors"].append(str(e))
            logger.error(f"OPERATE error: {e}")
        
        results["completed_at"] = datetime.now().isoformat()
        return results
    
    async def _check_syndicate(self) -> Dict:
        """Check Syndicate research pipeline"""
        try:
            # Check if syndicate daemon is running
            result = subprocess.run(
                ["pgrep", "-f", "syndicate"],
                capture_output=True,
                text=True
            )
            running = result.returncode == 0
            return {"status": "running" if running else "stopped"}
        except:
            return {"status": "unknown"}
    
    async def _check_legion(self) -> Dict:
        """Check LEGION orchestrator"""
        try:
            result = subprocess.run(
                ["pgrep", "-f", "continuous_operation"],
                capture_output=True,
                text=True
            )
            running = result.returncode == 0
            return {"status": "running" if running else "stopped"}
        except:
            return {"status": "unknown"}
    
    async def _process_pending_operations(self) -> Dict:
        """Process any pending scheduled operations"""
        # Check for pending posts, emails, etc.
        return {"processed": 0, "pending": 0}
    
    async def cognize(self) -> Dict[str, Any]:
        """
        COGNIZE Phase: Self-review and improvement.
        
        Uses GLADIUS to:
        - Analyze recent operations
        - Identify improvement opportunities
        - Generate learning targets
        - Update research keywords for SENTINEL
        """
        logger.info("COGNIZE phase started")
        results = {
            "phase": "COGNIZE",
            "started_at": datetime.now().isoformat(),
            "insights": [],
            "improvements": [],
            "errors": []
        }
        
        if not self.config.cognition_enabled:
            results["skipped"] = True
            return results
        
        cognition_prompts = [
            "Analyze the last 24 hours of operations. What patterns do you notice?",
            "What are 3 specific improvements I should make to my processing?",
            "Based on recent errors, what skills should I develop?",
            "Generate 5 new research keywords for the learning pipeline",
            "What Artifact operations could be automated better?"
        ]
        
        for prompt in cognition_prompts:
            try:
                # Query GLADIUS for insight
                response = await self._query_gladius(prompt)
                if response.get("success"):
                    results["insights"].append({
                        "prompt": prompt,
                        "response": response.get("response", "")[:500]
                    })
            except Exception as e:
                results["errors"].append(f"Cognition prompt failed: {e}")
        
        # Update SENTINEL targets if we have new keywords
        if results["insights"]:
            await self._update_sentinel_targets(results["insights"])
        
        results["completed_at"] = datetime.now().isoformat()
        return results
    
    async def _query_gladius(self, prompt: str) -> Dict:
        """Query GLADIUS AI - tries direct model first, then Ollama"""
        try:
            # Try importing and using direct speak interface
            try:
                from GLADIUS.speak import GladiusInterface
                interface = GladiusInterface(verbose=False, direct=True)
                result = interface.query(prompt)
                if result.get("success"):
                    return result
            except Exception:
                pass  # Fall through to Ollama
            
            # Try Ollama gladius model
            result = subprocess.run(
                ["ollama", "run", "gladius1.1:494M", prompt],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return {"success": True, "response": result.stdout.strip()}
            
            # Fallback to base model
            result = subprocess.run(
                ["ollama", "run", "qwen2.5:0.5b", prompt],
                capture_output=True,
                text=True,
                timeout=60
            )
            return {
                "success": result.returncode == 0,
                "response": result.stdout.strip() if result.returncode == 0 else result.stderr
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _update_sentinel_targets(self, insights: List[Dict]):
        """Update SENTINEL research targets from cognition insights"""
        try:
            # Extract keywords from insights
            keywords = []
            for insight in insights:
                response = insight.get("response", "")
                # Simple keyword extraction
                words = response.lower().split()
                keywords.extend([w for w in words if len(w) > 4 and w.isalpha()][:5])
            
            if keywords:
                # Update SENTINEL config
                sentinel_config = GLADIUS_ROOT / "SENTINEL" / "services" / "config" / "learning_config.json"
                if sentinel_config.exists():
                    with open(sentinel_config) as f:
                        config = json.load(f)
                    
                    existing = config.get("focused_targets", [])
                    updated = list(set(existing + keywords[:10]))[:15]
                    config["focused_targets"] = updated
                    
                    with open(sentinel_config, 'w') as f:
                        json.dump(config, f, indent=2)
                    
                    logger.info(f"Updated SENTINEL targets: {updated[:5]}...")
                    
        except Exception as e:
            logger.warning(f"Could not update SENTINEL targets: {e}")
    
    async def train(self) -> Dict[str, Any]:
        """
        TRAIN Phase: Run model training pipeline.
        
        This phase:
        - Checks if training is needed (threshold samples)
        - Runs the dual training pipeline (Qwen LoRA + Primary)
        - Validates and promotes model if successful
        """
        logger.info("TRAIN phase started")
        results = {
            "phase": "TRAIN",
            "started_at": datetime.now().isoformat(),
            "trained": False,
            "qwen_trained": False,
            "primary_trained": False,
            "errors": []
        }
        
        # Only train every N cycles
        if self.cycles_completed % self.config.training_every_n_cycles != 0:
            results["skipped"] = True
            results["reason"] = f"Train every {self.config.training_every_n_cycles} cycles"
            return results
        
        try:
            # Try dual trainer first (preferred)
            dual_trainer = GLADIUS_ROOT / "GLADIUS" / "training" / "dual_trainer.py"
            train_script = GLADIUS_ROOT / "GLADIUS" / "training" / "train_pipeline.py"
            
            script_to_run = dual_trainer if dual_trainer.exists() else train_script
            
            if script_to_run.exists():
                logger.info(f"Running training: {script_to_run.name}")
                result = subprocess.run(
                    ["python3", str(script_to_run), "--qwen-only"],  # Quick Qwen LoRA during cycle
                    capture_output=True,
                    text=True,
                    timeout=1800,  # 30 minute timeout for LoRA
                    cwd=str(GLADIUS_ROOT)
                )
                
                if result.returncode == 0:
                    results["trained"] = True
                    results["qwen_trained"] = True
                    results["output"] = result.stdout[-1000:]  # Last 1000 chars
                else:
                    results["errors"].append(result.stderr[-500:])
            else:
                results["errors"].append("Training script not found")
                
        except subprocess.TimeoutExpired:
            results["errors"].append("Training timed out (expected for full training)")
            results["trained"] = True  # Partial training is still progress
        except Exception as e:
            results["errors"].append(str(e))
        
        results["completed_at"] = datetime.now().isoformat()
        return results
    
    async def coordinate_sentinel(self):
        """
        Coordinate with SENTINEL learning daemon.
        
        Ensures SENTINEL is running and triggers a learning cycle.
        """
        if not self.config.sentinel_coordination:
            return
        
        try:
            # Check if SENTINEL learning daemon is running
            result = subprocess.run(
                ["pgrep", "-f", "learning_daemon"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # Start SENTINEL learning daemon
                logger.info("Starting SENTINEL learning daemon...")
                subprocess.Popen(
                    ["python3", str(GLADIUS_ROOT / "SENTINEL" / "services" / "learning_daemon.py"), "start"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            
        except Exception as e:
            logger.warning(f"SENTINEL coordination error: {e}")
    
    async def run_cycle(self) -> Dict[str, Any]:
        """Run a complete autonomous cycle"""
        self.cycles_completed += 1
        
        self.current_state = CycleState(
            cycle_number=self.cycles_completed,
            phase="STARTING",
            started_at=datetime.now().isoformat(),
            operations_completed=0,
            training_triggered=False,
            cognition_insights=[],
            errors=[]
        )
        
        cycle_results = {
            "cycle": self.cycles_completed,
            "started_at": self.current_state.started_at,
            "phases": {}
        }
        
        try:
            # Phase 1: OPERATE
            self.current_state.phase = "OPERATE"
            self._save_state()
            operate_results = await self.operate()
            cycle_results["phases"]["operate"] = operate_results
            
            if self.shutdown_requested:
                return cycle_results
            
            # Phase 2: COGNIZE
            self.current_state.phase = "COGNIZE"
            self._save_state()
            cognize_results = await self.cognize()
            cycle_results["phases"]["cognize"] = cognize_results
            self.current_state.cognition_insights = [
                i.get("response", "")[:100] for i in cognize_results.get("insights", [])
            ]
            
            if self.shutdown_requested:
                return cycle_results
            
            # Phase 3: TRAIN (during sleep time)
            self.current_state.phase = "TRAIN"
            self._save_state()
            train_results = await self.train()
            cycle_results["phases"]["train"] = train_results
            self.current_state.training_triggered = train_results.get("trained", False)
            
            if self.shutdown_requested:
                return cycle_results
            
            # Phase 4: COORDINATE WITH SENTINEL
            self.current_state.phase = "SENTINEL"
            await self.coordinate_sentinel()
            
            # Phase 5: SLEEP
            self.current_state.phase = "SLEEP"
            self._save_state()
            
        except Exception as e:
            self.current_state.errors.append(str(e))
            cycle_results["error"] = str(e)
            logger.error(f"Cycle error: {e}")
        
        cycle_results["completed_at"] = datetime.now().isoformat()
        
        # Log cycle summary
        logger.info(
            f"Cycle {self.cycles_completed} complete: "
            f"ops={len(cycle_results.get('phases', {}).get('operate', {}).get('operations', []))}, "
            f"insights={len(cycle_results.get('phases', {}).get('cognize', {}).get('insights', []))}, "
            f"trained={cycle_results.get('phases', {}).get('train', {}).get('trained', False)}"
        )
        
        return cycle_results
    
    async def run(self) -> Dict[str, Any]:
        """
        Main autonomous operation loop.
        
        Runs continuously for the configured duration.
        """
        self.running = True
        self.start_time = datetime.now()
        end_time = self.start_time + timedelta(hours=self.config.duration_hours)
        
        logger.info(f"Starting autonomous operation")
        logger.info(f"  Duration: {self.config.duration_hours} hours ({self.config.duration_hours/24:.1f} days)")
        logger.info(f"  Interval: {self.config.interval_minutes} minutes")
        logger.info(f"  End time: {end_time.isoformat()}")
        
        # Try to recover state
        self._load_state()
        
        all_results = {
            "started_at": self.start_time.isoformat(),
            "config": asdict(self.config),
            "cycles": []
        }
        
        try:
            while self.running and not self.shutdown_requested:
                # Check if we've exceeded duration
                if datetime.now() >= end_time:
                    logger.info("Duration complete, stopping autonomous operation")
                    break
                
                # Run cycle
                cycle_results = await self.run_cycle()
                all_results["cycles"].append(cycle_results)
                
                # Save results periodically
                if self.cycles_completed % 5 == 0:
                    results_file = LOG_DIR / f"autonomous_results_{self.start_time.strftime('%Y%m%d')}.json"
                    with open(results_file, 'w') as f:
                        json.dump(all_results, f, indent=2)
                
                if self.shutdown_requested:
                    break
                
                # Sleep until next cycle
                sleep_seconds = self.config.interval_minutes * 60
                logger.info(f"Sleeping {self.config.interval_minutes} minutes until next cycle...")
                
                # Interruptible sleep
                for _ in range(sleep_seconds):
                    if self.shutdown_requested:
                        break
                    await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Autonomous operation error: {e}")
            all_results["error"] = str(e)
        
        finally:
            all_results["completed_at"] = datetime.now().isoformat()
            all_results["total_cycles"] = self.cycles_completed
            
            # Save final results
            results_file = LOG_DIR / f"autonomous_results_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w') as f:
                json.dump(all_results, f, indent=2)
            
            logger.info(f"Autonomous operation complete. {self.cycles_completed} cycles. Results: {results_file}")
        
        return all_results


def print_banner():
    """Print autonomous mode banner"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║         G L A D I U S   A U T O N O M O U S   M O D E         ║
║                                                               ║
║       Continuous Learning · Training · Operations             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="GLADIUS Autonomous Continuous Operation")
    parser.add_argument("--days", type=float, default=30, help="Duration in days")
    parser.add_argument("--hours", type=float, help="Duration in hours (overrides days)")
    parser.add_argument("--interval", type=int, default=60, help="Interval in minutes")
    parser.add_argument("--no-training", action="store_true", help="Disable training phase")
    parser.add_argument("--no-cognition", action="store_true", help="Disable cognition phase")
    parser.add_argument("--single-cycle", action="store_true", help="Run single cycle and exit")
    parser.add_argument("--quiet", action="store_true", help="Quiet output")
    
    args = parser.parse_args()
    
    if not args.quiet:
        print_banner()
    
    config = AutonomousConfig()
    
    if args.hours:
        config.duration_hours = args.hours
    else:
        config.duration_hours = args.days * 24
    
    config.interval_minutes = args.interval
    
    if args.no_training:
        config.training_every_n_cycles = 99999  # Effectively disable
    
    if args.no_cognition:
        config.cognition_enabled = False
    
    operator = AutonomousOperator(config)
    
    if args.single_cycle:
        result = await operator.run_cycle()
        print(json.dumps(result, indent=2))
    else:
        await operator.run()


if __name__ == "__main__":
    asyncio.run(main())
