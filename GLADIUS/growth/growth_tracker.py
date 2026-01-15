#!/usr/bin/env python3
"""
GLADIUS Growth Tracker
======================

Visual dashboard for monitoring GLADIUS model growth, training progress,
and capability development over time.

Features:
- Parameter count progression
- Training phase visualization
- Capability scores by expert
- Loss curve plotting
- Session history

Author: Artifact Virtual Systems
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Path configuration (universal)
SCRIPT_DIR = Path(__file__).parent.resolve()
GLADIUS_DIR = SCRIPT_DIR.parent.resolve()
PROJECT_ROOT = GLADIUS_DIR.parent.resolve()

# Use local tmp directory for all training files
TMP_BASE = GLADIUS_DIR / "tmp"
CHECKPOINTS_DIR = TMP_BASE / "checkpoints"
LOGS_DIR = TMP_BASE / "logs"
GROWTH_DATA_FILE = SCRIPT_DIR / "growth_history.json"


class GrowthHistory:
    """Tracks GLADIUS growth over time"""
    
    def __init__(self):
        self.data = self.load()
    
    def load(self) -> Dict[str, Any]:
        """Load growth history"""
        if GROWTH_DATA_FILE.exists():
            with open(GROWTH_DATA_FILE) as f:
                return json.load(f)
        return {
            "sessions": [],
            "milestones": [],
            "capability_progress": {},
            "parameter_history": [],
            "total_training_hours": 0.0
        }
    
    def save(self):
        """Save growth history"""
        with open(GROWTH_DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_session(self, session_data: Dict):
        """Record a training session"""
        session_data["recorded_at"] = datetime.now().isoformat()
        self.data["sessions"].append(session_data)
        self.data["total_training_hours"] += session_data.get("hours", 0)
        self.save()
    
    def record_milestone(self, milestone: str, params: int):
        """Record a milestone"""
        self.data["milestones"].append({
            "milestone": milestone,
            "params": params,
            "timestamp": datetime.now().isoformat()
        })
        self.save()
    
    def update_capability(self, name: str, score: float):
        """Update capability score"""
        if name not in self.data["capability_progress"]:
            self.data["capability_progress"][name] = []
        self.data["capability_progress"][name].append({
            "score": score,
            "timestamp": datetime.now().isoformat()
        })
        self.save()
    
    def record_params(self, count: int):
        """Record parameter count"""
        self.data["parameter_history"].append({
            "count": count,
            "timestamp": datetime.now().isoformat()
        })
        self.save()


def get_training_state() -> Dict[str, Any]:
    """Get current training state"""
    # Try lightweight trainer state first
    state_file = CHECKPOINTS_DIR / "lightweight_state.json"
    if state_file.exists():
        with open(state_file) as f:
            return json.load(f)
    
    # Try MoE trainer state
    state_file = CHECKPOINTS_DIR / "moe_training_state.json"
    if state_file.exists():
        with open(state_file) as f:
            return json.load(f)
    
    # Try single expert state
    state_file = CHECKPOINTS_DIR / "training_state.json"
    if state_file.exists():
        with open(state_file) as f:
            return json.load(f)
    
    return {}


def create_progress_bar(current: float, total: float, width: int = 40, 
                        fill_char: str = "█", empty_char: str = "░") -> str:
    """Create ASCII progress bar"""
    if total == 0:
        return empty_char * width
    
    progress = min(current / total, 1.0)
    filled = int(width * progress)
    empty = width - filled
    
    return f"{fill_char * filled}{empty_char * empty}"


def format_number(n: int) -> str:
    """Format large numbers with suffixes"""
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.2f}B"
    elif n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.2f}K"
    return str(n)


def render_dashboard():
    """Render the growth dashboard"""
    state = get_training_state()
    history = GrowthHistory()
    
    # Colors (ANSI)
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"
    
    # Clear screen
    print("\033[2J\033[H", end="")
    
    # Header
    print(f"{CYAN}╔══════════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{CYAN}║{RESET}{BOLD}                     G L A D I U S   G R O W T H   T R A C K E R            {RESET}{CYAN}║{RESET}")
    print(f"{CYAN}╚══════════════════════════════════════════════════════════════════════════╝{RESET}")
    print()
    
    # Current Status
    current_params = state.get("current_params", 0)
    target_params = state.get("target_params", 1_000_000_000)
    status = state.get("status", "unknown")
    phase = state.get("phase", 0)
    
    status_color = GREEN if status == "completed" else YELLOW if status == "training" else RED
    
    print(f"{BOLD}▌ Model Status{RESET}")
    print(f"  ├─ Status:     {status_color}{status.upper()}{RESET}")
    print(f"  ├─ Phase:      {phase}/6")
    print(f"  ├─ Step:       {state.get('step', 0)}")
    print(f"  ├─ Expert:     {state.get('current_expert', 'N/A')}")
    print(f"  └─ Target:     {format_number(target_params)}")
    print()
    
    # Parameter Progress Bar
    print(f"{BOLD}▌ Parameter Growth{RESET}")
    progress_pct = (current_params / target_params * 100) if target_params > 0 else 0
    bar = create_progress_bar(current_params, target_params, 50)
    print(f"  {bar} {progress_pct:.1f}%")
    print(f"  {DIM}{format_number(current_params)} / {format_number(target_params)}{RESET}")
    print()
    
    # Expert Distillation Progress
    experts_completed = state.get("experts_completed", state.get("experts_distilled", []))
    
    # All experts from main trainer
    all_experts = ["qwen", "llama", "phi", "tinyllama"]
    
    print(f"{BOLD}▌ Expert Distillation{RESET}")
    for expert in all_experts:
        done = expert in experts_completed
        current = state.get("current_expert", "") == expert
        if done:
            status_icon = f"{GREEN}✓{RESET}"
            bar = f"{GREEN}{'█' * 20}{RESET}"
            pct = "100%"
        elif current:
            step = state.get("step", 0)
            pct_val = min(step / 500 * 100, 100)  # ~500 steps per expert
            filled = int(pct_val / 5)
            bar = f"{YELLOW}{'█' * filled}{'░' * (20-filled)}{RESET}"
            status_icon = f"{YELLOW}◆{RESET}"
            pct = f"{pct_val:.0f}%"
        else:
            status_icon = f"{DIM}○{RESET}"
            bar = f"{DIM}{'░' * 20}{RESET}"
            pct = "0%"
        
        expert_name = expert.upper().ljust(10)
        print(f"  {status_icon} {expert_name} {bar} {pct}")
    print()
    
    # Training Time
    total_hours = state.get("total_training_hours", 0) or state.get("training_hours", 0)
    
    print(f"{BOLD}▌ Training Time{RESET}")
    print(f"  ├─ This session: {total_hours:.2f} hours")
    print(f"  └─ Total:        {history.data.get('total_training_hours', 0) + total_hours:.2f} hours")
    print()
    
    # Loss History
    loss_history = state.get("loss_history", [])
    if loss_history:
        print(f"{BOLD}▌ Loss Curve (last 10){RESET}")
        recent_loss = loss_history[-10:]
        max_loss = max(recent_loss) if recent_loss else 1
        min_loss = min(recent_loss) if recent_loss else 0
        
        # Simple ASCII chart
        chart_height = 5
        for row in range(chart_height):
            threshold = max_loss - (row * (max_loss - min_loss) / chart_height)
            line = "  │"
            for loss in recent_loss:
                if loss >= threshold:
                    line += "█"
                else:
                    line += " "
            line = line.ljust(15)
            if row == 0:
                line += f" {max_loss:.3f}"
            elif row == chart_height - 1:
                line += f" {min_loss:.3f}"
            print(line)
        print(f"  └{'─' * len(recent_loss)}")
    print()
    
    # Milestones
    print(f"{BOLD}▌ Milestones{RESET}")
    milestones = history.data.get("milestones", [])
    if milestones:
        for m in milestones[-5:]:
            print(f"  • {m['milestone']} ({format_number(m['params'])})")
    else:
        print(f"  {DIM}No milestones yet{RESET}")
    print()
    
    # Quick Commands
    print(f"{BOLD}▌ Commands{RESET}")
    print(f"  {DIM}Train:{RESET}    ./train_gladius_moe.ps1")
    print(f"  {DIM}Status:{RESET}   ./train_gladius_moe.ps1 -Status")
    print(f"  {DIM}Refresh:{RESET}  python3 growth_tracker.py --live")
    print()
    
    # Footer
    print(f"{DIM}Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print()


def sync_from_training_state():
    """Sync growth history from training state"""
    state = get_training_state()
    history = GrowthHistory()
    
    if not state:
        print("No training state found")
        return
    
    # Record current params
    current_params = state.get("current_params", 0)
    if current_params > 0:
        history.record_params(current_params)
    
    # Record capability scores
    for name, score in state.get("capability_scores", {}).items():
        history.update_capability(name, score)
    
    # Check for milestones
    milestones = [
        (100_000_000, "100M Parameters"),
        (250_000_000, "250M Parameters"),
        (500_000_000, "500M Parameters"),
        (750_000_000, "750M Parameters"),
        (1_000_000_000, "1B Parameters - TARGET REACHED!"),
    ]
    
    recorded_milestones = {m["milestone"] for m in history.data.get("milestones", [])}
    
    for threshold, milestone in milestones:
        if current_params >= threshold and milestone not in recorded_milestones:
            history.record_milestone(milestone, current_params)
            print(f"🎉 MILESTONE: {milestone}")
    
    print(f"Synced growth data. Current: {format_number(current_params)}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="GLADIUS Growth Tracker")
    parser.add_argument("--live", action="store_true", help="Live dashboard mode (updates every 5s)")
    parser.add_argument("--sync", action="store_true", help="Sync from training state")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if args.sync:
        sync_from_training_state()
        return
    
    if args.json:
        state = get_training_state()
        history = GrowthHistory()
        output = {
            "current_state": state,
            "history": history.data
        }
        print(json.dumps(output, indent=2))
        return
    
    if args.live:
        import time
        try:
            while True:
                render_dashboard()
                time.sleep(5)
        except KeyboardInterrupt:
            print("\nExiting...")
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
