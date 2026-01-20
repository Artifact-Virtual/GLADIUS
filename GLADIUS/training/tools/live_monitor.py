#!/usr/bin/env python3
"""
GLADIUS Training Live Monitor
=============================

Rich-powered terminal dashboard that visualizes training progress in real time.
Reads the MoE trainer state file and renders:
  • Phase/step/epoch indicators
  • Loss sparkline
  • Expert coverage
  • Animated spinner + elapsed time

Usage:
    python -m GLADIUS.training.tools.live_monitor

Press Ctrl+C to exit.
"""

import json
import math
import time
from pathlib import Path
from typing import Dict, List

from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table
from rich.text import Text

SCRIPT_DIR = Path(__file__).resolve().parent
GLADIUS_DIR = SCRIPT_DIR.parent.parent
STATE_PATH = GLADIUS_DIR / "tmp" / "checkpoints" / "moe_training_state.json"
LOG_PATH = GLADIUS_DIR / "tmp" / "logs"

console = Console()


def load_state() -> Dict:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def render_loss_spark(loss_history: List[float]) -> Text:
    if not loss_history:
        return Text("No loss data yet", style="dim")
    # Keep last 30 points
    data = loss_history[-30:]
    min_loss = min(data)
    max_loss = max(data)
    span = max(max_loss - min_loss, 1e-6)
    chars = "▁▂▃▄▅▆▇█"
    spark = Text()
    for point in data:
        idx = int(((point - min_loss) / span) * (len(chars) - 1))
        spark.append(chars[idx], style="magenta")
    spark.append(f"  last={data[-1]:.4f}", style="bold")
    return spark


def build_layout(state: Dict, cycle_time: float) -> Panel:
    phase = state.get("phase", 0)
    step = state.get("step", 0)
    epoch = state.get("epoch", 0)
    status = state.get("status", "initializing")
    experts = state.get("experts_distilled", [])
    total_hours = state.get("total_training_hours", 0.0)
    target_params = state.get("target_params", 1_000_000_000)
    current_params = state.get("current_params", 0)
    loss_history = state.get("loss_history", [])

    phase_panel = Table.grid(padding=(0, 1))
    phase_panel.add_row("Phase", str(phase))
    phase_panel.add_row("Epoch", str(epoch))
    phase_panel.add_row("Step", str(step))
    phase_panel.add_row("Status", status.title())

    expert_table = Table(title="Experts Distilled", box=box.SIMPLE, expand=True)
    expert_table.add_column("Expert", style="cyan")
    expert_table.add_column("Status", justify="right")
    if experts:
        for exp in experts:
            expert_table.add_row(exp, "✅")
    else:
        expert_table.add_row("—", "pending")

    param_progress = Progress(
        SpinnerColumn(style="green"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed:,}/{task.total:,} params"),
        transient=True,
    )
    task = param_progress.add_task("Parameters", total=target_params, completed=current_params)

    loss_panel = Panel(
        render_loss_spark(loss_history),
        title="Loss Trend",
        border_style="magenta",
    )

    elapsed = Text(f"Training hours: {total_hours:.2f}\nMonitor uptime: {cycle_time:.1f}s", style="dim")

    grid = Table.grid(expand=True)
    grid.add_row(Panel(phase_panel, title="Phase Status", border_style="cyan"), Panel(param_progress, title="Capacity", border_style="green"))
    grid.add_row(loss_panel, expert_table)
    grid.add_row(Align.center(elapsed))

    return Panel(grid, title="[bold]GLADIUS 1B Live Monitor[/bold]", border_style="bright_blue", padding=(1, 1))


def main():
    console.print(f"Watching {STATE_PATH}", style="dim cyan")
    start_time = time.time()
    try:
        with Live(console=console, refresh_per_second=5) as live:
            while True:
                state = load_state()
                elapsed = time.time() - start_time
                live.update(build_layout(state, elapsed))
                time.sleep(1.0)
    except KeyboardInterrupt:
        console.print("\nExiting live monitor…", style="bold yellow")


if __name__ == "__main__":
    main()
