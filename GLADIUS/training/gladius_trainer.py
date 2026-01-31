#!/usr/bin/env python3
"""
GLADIUS Unified Trainer
=======================

Single trainer that handles both CPU and GPU training with:
- Automatic hardware detection (CUDA/CPU)
- Shared checkpoint format (resumable on either device)
- Native GGUF export for llama.cpp

Architecture: Llama-compatible transformer
Output: Native GGUF file

Usage:
    python gladius_trainer.py --params 150 --epochs 10
    python gladius_trainer.py --resume --export-gguf
"""

import os
import sys
import json
import math
import time
import logging
import argparse
import threading
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import deque

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

# =============================================================================
# TERMINAL DISPLAY SYSTEM
# =============================================================================

class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    
    # Foreground
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright foreground
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'


class TrainingMetrics:
    """Track comprehensive training metrics"""
    def __init__(self, total_steps: int, total_epochs: int):
        self.total_steps = total_steps
        self.total_epochs = total_epochs
        self.start_time = time.time()
        self.epoch_start_time = time.time()
        
        # Loss tracking
        self.loss_history = deque(maxlen=1000)
        self.epoch_losses = []
        self.best_loss = float('inf')
        self.worst_loss = 0.0
        
        # Step tracking
        self.current_step = 0
        self.current_epoch = 0
        self.steps_in_epoch = 0
        self.tokens_processed = 0
        
        # Performance
        self.step_times = deque(maxlen=100)
        self.last_step_time = time.time()
        
        # Gradients
        self.grad_norm_history = deque(maxlen=100)
        self.learning_rates = []
        
        # Memory
        self.peak_memory_mb = 0
        self.current_memory_mb = 0
    
    def update(self, loss: float, grad_norm: float = 0.0, lr: float = 0.0, 
               batch_tokens: int = 0, memory_mb: float = 0.0):
        now = time.time()
        step_time = now - self.last_step_time
        self.last_step_time = now
        
        self.current_step += 1
        self.steps_in_epoch += 1
        self.tokens_processed += batch_tokens
        
        self.loss_history.append(loss)
        self.step_times.append(step_time)
        self.grad_norm_history.append(grad_norm)
        self.learning_rates.append(lr)
        
        if loss < self.best_loss:
            self.best_loss = loss
        if loss > self.worst_loss:
            self.worst_loss = loss
        
        self.current_memory_mb = memory_mb
        if memory_mb > self.peak_memory_mb:
            self.peak_memory_mb = memory_mb
    
    def start_epoch(self, epoch: int):
        self.current_epoch = epoch
        self.epoch_start_time = time.time()
        self.steps_in_epoch = 0
    
    def end_epoch(self):
        if self.loss_history:
            avg = sum(list(self.loss_history)[-self.steps_in_epoch:]) / max(self.steps_in_epoch, 1)
            self.epoch_losses.append(avg)
    
    @property
    def avg_loss(self) -> float:
        if not self.loss_history:
            return 0.0
        return sum(self.loss_history) / len(self.loss_history)
    
    @property
    def recent_loss(self) -> float:
        if not self.loss_history:
            return 0.0
        recent = list(self.loss_history)[-10:]
        return sum(recent) / len(recent)
    
    @property
    def loss_trend(self) -> str:
        if len(self.loss_history) < 20:
            return "━"
        old = sum(list(self.loss_history)[-20:-10]) / 10
        new = sum(list(self.loss_history)[-10:]) / 10
        diff = new - old
        if diff < -0.01:
            return "↓"
        elif diff > 0.01:
            return "↑"
        return "━"
    
    @property
    def steps_per_second(self) -> float:
        if not self.step_times:
            return 0.0
        return 1.0 / (sum(self.step_times) / len(self.step_times))
    
    @property
    def tokens_per_second(self) -> float:
        elapsed = time.time() - self.start_time
        if elapsed == 0:
            return 0.0
        return self.tokens_processed / elapsed
    
    @property
    def elapsed_time(self) -> str:
        return str(timedelta(seconds=int(time.time() - self.start_time)))
    
    @property
    def eta(self) -> str:
        if self.current_step == 0:
            return "calculating..."
        elapsed = time.time() - self.start_time
        rate = self.current_step / elapsed
        remaining_steps = self.total_steps - self.current_step
        if rate == 0:
            return "unknown"
        eta_seconds = remaining_steps / rate
        return str(timedelta(seconds=int(eta_seconds)))
    
    @property
    def progress_percent(self) -> float:
        if self.total_steps == 0:
            return 0.0
        return (self.current_step / self.total_steps) * 100


class AnimatedDisplay:
    """Animated terminal display for training progress"""
    
    LOGO = r"""
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║   ██████╗ ██╗      █████╗ ██████╗ ██╗██╗   ██╗███████╗               ║
    ║  ██╔════╝ ██║     ██╔══██╗██╔══██╗██║██║   ██║██╔════╝               ║
    ║  ██║  ███╗██║     ███████║██║  ██║██║██║   ██║███████╗               ║
    ║  ██║   ██║██║     ██╔══██║██║  ██║██║██║   ██║╚════██║               ║
    ║  ╚██████╔╝███████╗██║  ██║██████╔╝██║╚██████╔╝███████║               ║
    ║   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═════╝ ╚═╝ ╚═════╝ ╚══════╝               ║
    ║                    ◆ NEURAL TRAINING ENGINE ◆                        ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """
    
    SPINNER_FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    PULSE_FRAMES = ['◜', '◠', '◝', '◞', '◡', '◟']
    BRAIN_FRAMES = ['🧠', '💭', '⚡', '✨', '🔮', '💫']
    
    def __init__(self, device: str, config_info: dict):
        self.device = device
        self.config_info = config_info
        self.frame = 0
        self.running = True
        self._lock = threading.Lock()
        
    def clear_screen(self):
        print('\033[2J\033[H', end='')
    
    def move_cursor(self, row: int, col: int = 1):
        print(f'\033[{row};{col}H', end='')
    
    def hide_cursor(self):
        print('\033[?25l', end='')
    
    def show_cursor(self):
        print('\033[?25h', end='')
    
    def render_progress_bar(self, percent: float, width: int = 40, 
                           filled_char: str = '█', empty_char: str = '░') -> str:
        filled = int(width * percent / 100)
        empty = width - filled
        
        # Gradient effect
        bar = ''
        for i in range(filled):
            if i < width * 0.3:
                bar += f'{Colors.RED}{filled_char}'
            elif i < width * 0.6:
                bar += f'{Colors.YELLOW}{filled_char}'
            else:
                bar += f'{Colors.GREEN}{filled_char}'
        bar += f'{Colors.BRIGHT_BLACK}{empty_char * empty}{Colors.RESET}'
        
        return bar
    
    def render_mini_chart(self, values: list, width: int = 20, height: int = 5) -> List[str]:
        """Render a mini sparkline chart"""
        if not values:
            return ['─' * width] * height
        
        # Take last 'width' values
        vals = list(values)[-width:]
        if not vals:
            return ['─' * width] * height
        
        min_v, max_v = min(vals), max(vals)
        range_v = max_v - min_v if max_v != min_v else 1
        
        # Normalize to 0-height range
        normalized = [(v - min_v) / range_v * (height - 1) for v in vals]
        
        lines = []
        chars = '▁▂▃▄▅▆▇█'
        
        for row in range(height - 1, -1, -1):
            line = ''
            for val in normalized:
                if val >= row + 0.875:
                    line += f'{Colors.GREEN}█{Colors.RESET}'
                elif val >= row + 0.75:
                    line += f'{Colors.GREEN}▇{Colors.RESET}'
                elif val >= row + 0.625:
                    line += f'{Colors.BRIGHT_GREEN}▆{Colors.RESET}'
                elif val >= row + 0.5:
                    line += f'{Colors.YELLOW}▅{Colors.RESET}'
                elif val >= row + 0.375:
                    line += f'{Colors.YELLOW}▄{Colors.RESET}'
                elif val >= row + 0.25:
                    line += f'{Colors.BRIGHT_YELLOW}▃{Colors.RESET}'
                elif val >= row + 0.125:
                    line += f'{Colors.RED}▂{Colors.RESET}'
                elif val >= row:
                    line += f'{Colors.RED}▁{Colors.RESET}'
                else:
                    line += f'{Colors.BRIGHT_BLACK}·{Colors.RESET}'
            # Pad to width
            line += ' ' * (width - len(vals))
            lines.append(line)
        
        return lines
    
    def render_header(self, metrics: TrainingMetrics) -> str:
        self.frame += 1
        spinner = self.SPINNER_FRAMES[self.frame % len(self.SPINNER_FRAMES)]
        pulse = self.PULSE_FRAMES[self.frame % len(self.PULSE_FRAMES)]
        brain = self.BRAIN_FRAMES[self.frame % len(self.BRAIN_FRAMES)]
        
        return f"""
{Colors.CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  {brain} {Colors.BOLD}{Colors.BRIGHT_WHITE}GLADIUS NEURAL TRAINING ENGINE{Colors.RESET}  {Colors.BRIGHT_CYAN}{pulse}{Colors.RESET}  {Colors.DIM}v1.1{Colors.RESET}                              {Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  {Colors.BRIGHT_GREEN}{spinner}{Colors.RESET} {Colors.GREEN}Training Active{Colors.RESET}  │  {Colors.YELLOW}Device: {self.device.upper()}{Colors.RESET}  │  {Colors.MAGENTA}Params: {self.config_info.get('params', '?')}M{Colors.RESET}     {Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""

    def render_metrics(self, metrics: TrainingMetrics) -> str:
        trend_color = Colors.GREEN if metrics.loss_trend == "↓" else (Colors.RED if metrics.loss_trend == "↑" else Colors.YELLOW)
        
        # Memory info
        mem_str = f"{metrics.current_memory_mb:.0f}MB" if metrics.current_memory_mb > 0 else "N/A"
        peak_str = f"{metrics.peak_memory_mb:.0f}MB" if metrics.peak_memory_mb > 0 else "N/A"
        
        # Gradient norm
        grad_norm = list(metrics.grad_norm_history)[-1] if metrics.grad_norm_history else 0.0
        
        return f"""
{Colors.BRIGHT_BLACK}┌─────────────────────────────── PROGRESS ────────────────────────────────────┐{Colors.RESET}
{Colors.BRIGHT_BLACK}│{Colors.RESET}  {Colors.BOLD}Epoch:{Colors.RESET} {Colors.CYAN}{metrics.current_epoch}/{metrics.total_epochs}{Colors.RESET}   {Colors.BOLD}Step:{Colors.RESET} {Colors.CYAN}{metrics.current_step:,}/{metrics.total_steps:,}{Colors.RESET}   {Colors.BOLD}Progress:{Colors.RESET} {Colors.BRIGHT_WHITE}{metrics.progress_percent:.1f}%{Colors.RESET}
{Colors.BRIGHT_BLACK}│{Colors.RESET}  [{self.render_progress_bar(metrics.progress_percent, 60)}]
{Colors.BRIGHT_BLACK}└──────────────────────────────────────────────────────────────────────────────┘{Colors.RESET}

{Colors.BRIGHT_BLACK}┌──────────────────────────────── LOSS ───────────────────────────────────────┐{Colors.RESET}
{Colors.BRIGHT_BLACK}│{Colors.RESET}  {Colors.BOLD}Current:{Colors.RESET}  {Colors.BRIGHT_WHITE}{list(metrics.loss_history)[-1] if metrics.loss_history else 0:.6f}{Colors.RESET}  {trend_color}{metrics.loss_trend}{Colors.RESET}    {Colors.BOLD}Avg:{Colors.RESET} {Colors.YELLOW}{metrics.avg_loss:.6f}{Colors.RESET}
{Colors.BRIGHT_BLACK}│{Colors.RESET}  {Colors.BOLD}Best:{Colors.RESET}     {Colors.GREEN}{metrics.best_loss:.6f}{Colors.RESET}         {Colors.BOLD}Recent:{Colors.RESET} {Colors.CYAN}{metrics.recent_loss:.6f}{Colors.RESET}
{Colors.BRIGHT_BLACK}└──────────────────────────────────────────────────────────────────────────────┘{Colors.RESET}

{Colors.BRIGHT_BLACK}┌───────────────────────────── PERFORMANCE ───────────────────────────────────┐{Colors.RESET}
{Colors.BRIGHT_BLACK}│{Colors.RESET}  {Colors.BOLD}Speed:{Colors.RESET}      {Colors.CYAN}{metrics.steps_per_second:.2f}{Colors.RESET} steps/s   │  {Colors.BOLD}Tokens/s:{Colors.RESET}    {Colors.MAGENTA}{metrics.tokens_per_second:,.0f}{Colors.RESET}
{Colors.BRIGHT_BLACK}│{Colors.RESET}  {Colors.BOLD}Elapsed:{Colors.RESET}    {Colors.YELLOW}{metrics.elapsed_time}{Colors.RESET}       │  {Colors.BOLD}ETA:{Colors.RESET}         {Colors.GREEN}{metrics.eta}{Colors.RESET}
{Colors.BRIGHT_BLACK}│{Colors.RESET}  {Colors.BOLD}Grad Norm:{Colors.RESET}  {Colors.BRIGHT_WHITE}{grad_norm:.4f}{Colors.RESET}         │  {Colors.BOLD}LR:{Colors.RESET}          {Colors.BLUE}{metrics.learning_rates[-1] if metrics.learning_rates else 0:.2e}{Colors.RESET}
{Colors.BRIGHT_BLACK}└──────────────────────────────────────────────────────────────────────────────┘{Colors.RESET}

{Colors.BRIGHT_BLACK}┌─────────────────────────────── MEMORY ───────────────────────────────────────┐{Colors.RESET}
{Colors.BRIGHT_BLACK}│{Colors.RESET}  {Colors.BOLD}Current:{Colors.RESET} {Colors.CYAN}{mem_str}{Colors.RESET}   │   {Colors.BOLD}Peak:{Colors.RESET} {Colors.MAGENTA}{peak_str}{Colors.RESET}   │   {Colors.BOLD}Tokens Processed:{Colors.RESET} {Colors.GREEN}{metrics.tokens_processed:,}{Colors.RESET}
{Colors.BRIGHT_BLACK}└──────────────────────────────────────────────────────────────────────────────┘{Colors.RESET}
"""

    def render_loss_chart(self, metrics: TrainingMetrics) -> str:
        chart_lines = self.render_mini_chart(list(metrics.loss_history), width=60, height=6)
        chart = '\n'.join([f'{Colors.BRIGHT_BLACK}│{Colors.RESET}  {line}  {Colors.BRIGHT_BLACK}│{Colors.RESET}' for line in chart_lines])
        
        return f"""
{Colors.BRIGHT_BLACK}┌───────────────────────────── LOSS CHART ─────────────────────────────────────┐{Colors.RESET}
{chart}
{Colors.BRIGHT_BLACK}└──────────────────────────────────────────────────────────────────────────────┘{Colors.RESET}
"""

    def render_epoch_summary(self, metrics: TrainingMetrics) -> str:
        if not metrics.epoch_losses:
            return ""
        
        summaries = []
        for i, loss in enumerate(metrics.epoch_losses):
            status = "✓" if i < metrics.current_epoch else "◦"
            color = Colors.GREEN if i < metrics.current_epoch else Colors.YELLOW
            summaries.append(f"{color}{status} Epoch {i+1}: {loss:.6f}{Colors.RESET}")
        
        return f"""
{Colors.BRIGHT_BLACK}┌───────────────────────────── EPOCH HISTORY ──────────────────────────────────┐{Colors.RESET}
{Colors.BRIGHT_BLACK}│{Colors.RESET}  {' │ '.join(summaries[-5:])}
{Colors.BRIGHT_BLACK}└──────────────────────────────────────────────────────────────────────────────┘{Colors.RESET}
"""

    def render_full_display(self, metrics: TrainingMetrics) -> str:
        with self._lock:
            return (
                self.render_header(metrics) +
                self.render_metrics(metrics) +
                self.render_loss_chart(metrics) +
                self.render_epoch_summary(metrics)
            )
    
    def print_startup(self):
        """Print startup banner"""
        print(f"{Colors.CYAN}{self.LOGO}{Colors.RESET}")
        time.sleep(0.5)
    
    def print_completion(self, metrics: TrainingMetrics, gguf_path: str = None):
        """Print training completion summary"""
        print(f"""
{Colors.GREEN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════════════════╗
║                          ✓ TRAINING COMPLETE                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Total Steps:      {metrics.total_steps:>10,}                                          ║
║  Final Loss:       {metrics.recent_loss:>10.6f}                                          ║
║  Best Loss:        {metrics.best_loss:>10.6f}                                          ║
║  Total Time:       {metrics.elapsed_time:>10}                                          ║
║  Tokens Processed: {metrics.tokens_processed:>10,}                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.RESET}""")
        
        if gguf_path:
            print(f"{Colors.MAGENTA}  ◆ GGUF exported to: {gguf_path}{Colors.RESET}\n")

# =============================================================================
# PATH CONFIGURATION
# =============================================================================

SCRIPT_DIR = Path(__file__).parent.resolve()
GLADIUS_DIR = SCRIPT_DIR.parent.resolve()
PROJECT_ROOT = GLADIUS_DIR.parent.resolve()

# Shared directories for CPU and GPU
MODELS_DIR = GLADIUS_DIR / "models"
DATA_DIR = SCRIPT_DIR / "data"
OUTPUT_DIR = MODELS_DIR / "native"
CHECKPOINT_DIR = OUTPUT_DIR / "checkpoints"
TMP_DIR = GLADIUS_DIR / "tmp"

# Create directories
for d in [OUTPUT_DIR, CHECKPOINT_DIR, TMP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Add llama.cpp gguf-py to path
GGUF_PY_PATH = GLADIUS_DIR / "tools" / "llama.cpp" / "gguf-py"
if GGUF_PY_PATH.exists():
    sys.path.insert(0, str(GGUF_PY_PATH))

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(TMP_DIR / "gladius_training.log")
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# HARDWARE DETECTION
# =============================================================================

def detect_device() -> Tuple[torch.device, Dict[str, Any]]:
    """Detect best available device and return device info."""
    info = {
        "cuda_available": torch.cuda.is_available(),
        "cuda_devices": 0,
        "cuda_memory_gb": 0,
        "device_name": "cpu",
        "recommended_batch_size": 4,
        "recommended_params_m": 150,
    }
    
    if torch.cuda.is_available():
        info["cuda_devices"] = torch.cuda.device_count()
        info["cuda_memory_gb"] = torch.cuda.get_device_properties(0).total_memory / 1e9
        info["device_name"] = torch.cuda.get_device_name(0)
        
        # Scale recommendations based on VRAM
        vram = info["cuda_memory_gb"]
        if vram >= 24:
            info["recommended_batch_size"] = 32
            info["recommended_params_m"] = 1000
        elif vram >= 16:
            info["recommended_batch_size"] = 16
            info["recommended_params_m"] = 500
        elif vram >= 8:
            info["recommended_batch_size"] = 8
            info["recommended_params_m"] = 300
        else:
            info["recommended_batch_size"] = 4
            info["recommended_params_m"] = 150
        
        device = torch.device("cuda")
        logger.info(f"🚀 GPU detected: {info['device_name']} ({vram:.1f} GB VRAM)")
    else:
        # CPU mode
        import psutil
        ram_gb = psutil.virtual_memory().total / 1e9
        info["ram_gb"] = ram_gb
        
        if ram_gb >= 32:
            info["recommended_batch_size"] = 8
            info["recommended_params_m"] = 150
        elif ram_gb >= 16:
            info["recommended_batch_size"] = 4
            info["recommended_params_m"] = 100
        else:
            info["recommended_batch_size"] = 2
            info["recommended_params_m"] = 50
        
        device = torch.device("cpu")
        logger.info(f"💻 CPU mode: {ram_gb:.1f} GB RAM available")
    
    return device, info


# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

@dataclass
class GladiusConfig:
    """GLADIUS model configuration - scales for CPU or GPU"""
    vocab_size: int = 32000
    hidden_size: int = 512
    intermediate_size: int = 1408
    num_hidden_layers: int = 12
    num_attention_heads: int = 8
    num_key_value_heads: int = 4  # GQA
    max_position_embeddings: int = 2048
    rope_theta: float = 10000.0
    rms_norm_eps: float = 1e-6
    
    @property
    def head_dim(self) -> int:
        return self.hidden_size // self.num_attention_heads
    
    @property
    def total_params(self) -> int:
        embed = self.vocab_size * self.hidden_size * 2
        per_layer = (
            4 * self.hidden_size * self.hidden_size +
            3 * self.hidden_size * self.intermediate_size +
            2 * self.hidden_size
        )
        return embed + per_layer * self.num_hidden_layers
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def for_size(cls, target_params_m: int = 150):
        """Create config targeting specific parameter count in millions"""
        configs = {
            50:   dict(hidden_size=256, num_hidden_layers=6, num_attention_heads=4, num_key_value_heads=2, intermediate_size=704),
            100:  dict(hidden_size=384, num_hidden_layers=8, num_attention_heads=6, num_key_value_heads=2, intermediate_size=1056),
            150:  dict(hidden_size=512, num_hidden_layers=12, num_attention_heads=8, num_key_value_heads=4, intermediate_size=1408),
            300:  dict(hidden_size=768, num_hidden_layers=16, num_attention_heads=12, num_key_value_heads=4, intermediate_size=2048),
            500:  dict(hidden_size=1024, num_hidden_layers=20, num_attention_heads=16, num_key_value_heads=4, intermediate_size=2816),
            1000: dict(hidden_size=2048, num_hidden_layers=24, num_attention_heads=32, num_key_value_heads=8, intermediate_size=5632),
        }
        
        # Find closest config
        sizes = sorted(configs.keys())
        for size in sizes:
            if target_params_m <= size:
                return cls(**configs[size])
        return cls(**configs[sizes[-1]])


# =============================================================================
# MODEL ARCHITECTURE
# =============================================================================

class RMSNorm(nn.Module):
    """Root Mean Square Layer Normalization"""
    def __init__(self, hidden_size: int, eps: float = 1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(hidden_size))
        self.eps = eps
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        variance = x.pow(2).mean(-1, keepdim=True)
        x = x * torch.rsqrt(variance + self.eps)
        return self.weight * x


class RotaryEmbedding(nn.Module):
    """Rotary Position Embedding"""
    def __init__(self, dim: int, max_seq_len: int = 2048, theta: float = 10000.0):
        super().__init__()
        inv_freq = 1.0 / (theta ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq)
        self._set_cos_sin_cache(max_seq_len)
    
    def _set_cos_sin_cache(self, seq_len: int):
        t = torch.arange(seq_len, device=self.inv_freq.device)
        freqs = torch.outer(t, self.inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        self.register_buffer("cos_cached", emb.cos())
        self.register_buffer("sin_cached", emb.sin())
    
    def forward(self, x: torch.Tensor, seq_len: int):
        return (
            self.cos_cached[:seq_len].to(x.dtype),
            self.sin_cached[:seq_len].to(x.dtype)
        )


def rotate_half(x: torch.Tensor) -> torch.Tensor:
    x1, x2 = x[..., :x.shape[-1]//2], x[..., x.shape[-1]//2:]
    return torch.cat((-x2, x1), dim=-1)


def apply_rotary_pos_emb(q: torch.Tensor, k: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor):
    q_embed = (q * cos) + (rotate_half(q) * sin)
    k_embed = (k * cos) + (rotate_half(k) * sin)
    return q_embed, k_embed


class GladiusAttention(nn.Module):
    """Multi-head attention with GQA support"""
    def __init__(self, config: GladiusConfig):
        super().__init__()
        self.hidden_size = config.hidden_size
        self.num_heads = config.num_attention_heads
        self.num_kv_heads = config.num_key_value_heads
        self.head_dim = config.head_dim
        self.num_kv_groups = self.num_heads // self.num_kv_heads
        
        self.q_proj = nn.Linear(self.hidden_size, self.num_heads * self.head_dim, bias=False)
        self.k_proj = nn.Linear(self.hidden_size, self.num_kv_heads * self.head_dim, bias=False)
        self.v_proj = nn.Linear(self.hidden_size, self.num_kv_heads * self.head_dim, bias=False)
        self.o_proj = nn.Linear(self.num_heads * self.head_dim, self.hidden_size, bias=False)
        
        self.rotary_emb = RotaryEmbedding(self.head_dim, config.max_position_embeddings, config.rope_theta)
    
    def forward(self, x: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        batch, seq_len, _ = x.shape
        
        q = self.q_proj(x).view(batch, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(batch, seq_len, self.num_kv_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(batch, seq_len, self.num_kv_heads, self.head_dim).transpose(1, 2)
        
        cos, sin = self.rotary_emb(x, seq_len)
        q, k = apply_rotary_pos_emb(q, k, cos.unsqueeze(0).unsqueeze(0), sin.unsqueeze(0).unsqueeze(0))
        
        # GQA: expand k, v
        if self.num_kv_groups > 1:
            k = k.repeat_interleave(self.num_kv_groups, dim=1)
            v = v.repeat_interleave(self.num_kv_groups, dim=1)
        
        # Attention
        attn_weights = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        
        # Causal mask
        causal_mask = torch.triu(torch.ones(seq_len, seq_len, device=x.device), diagonal=1).bool()
        attn_weights = attn_weights.masked_fill(causal_mask, float('-inf'))
        
        attn_weights = F.softmax(attn_weights, dim=-1)
        out = torch.matmul(attn_weights, v)
        out = out.transpose(1, 2).contiguous().view(batch, seq_len, -1)
        
        return self.o_proj(out)


class GladiusMLP(nn.Module):
    """SwiGLU MLP"""
    def __init__(self, config: GladiusConfig):
        super().__init__()
        self.gate_proj = nn.Linear(config.hidden_size, config.intermediate_size, bias=False)
        self.up_proj = nn.Linear(config.hidden_size, config.intermediate_size, bias=False)
        self.down_proj = nn.Linear(config.intermediate_size, config.hidden_size, bias=False)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.down_proj(F.silu(self.gate_proj(x)) * self.up_proj(x))


class GladiusBlock(nn.Module):
    """Transformer block"""
    def __init__(self, config: GladiusConfig):
        super().__init__()
        self.input_layernorm = RMSNorm(config.hidden_size, config.rms_norm_eps)
        self.self_attn = GladiusAttention(config)
        self.post_attention_layernorm = RMSNorm(config.hidden_size, config.rms_norm_eps)
        self.mlp = GladiusMLP(config)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.self_attn(self.input_layernorm(x))
        x = x + self.mlp(self.post_attention_layernorm(x))
        return x


class GladiusModel(nn.Module):
    """Complete GLADIUS Model"""
    def __init__(self, config: GladiusConfig):
        super().__init__()
        self.config = config
        
        self.embed_tokens = nn.Embedding(config.vocab_size, config.hidden_size)
        self.layers = nn.ModuleList([GladiusBlock(config) for _ in range(config.num_hidden_layers)])
        self.norm = RMSNorm(config.hidden_size, config.rms_norm_eps)
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        
        # Tie weights
        self.lm_head.weight = self.embed_tokens.weight
        
        # Initialize
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
    
    def forward(self, input_ids: torch.Tensor, labels: Optional[torch.Tensor] = None):
        x = self.embed_tokens(input_ids)
        
        for layer in self.layers:
            x = layer(x)
        
        x = self.norm(x)
        logits = self.lm_head(x)
        
        loss = None
        if labels is not None:
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            loss = F.cross_entropy(
                shift_logits.view(-1, self.config.vocab_size),
                shift_labels.view(-1),
                ignore_index=0
            )
        
        return {"logits": logits, "loss": loss}


# =============================================================================
# TOKENIZER (Llama-compatible)
# =============================================================================

class LlamaTokenizer:
    """Byte-level tokenizer compatible with llama.cpp"""
    def __init__(self, vocab_size: int = 32000):
        self.vocab_size = vocab_size
        self.token_to_id = {}
        self.id_to_token = {}
        self._build_vocab()
    
    def _build_vocab(self):
        idx = 0
        
        # Special tokens
        for tok in ["<unk>", "<s>", "</s>"]:
            self.token_to_id[tok] = idx
            self.id_to_token[idx] = tok
            idx += 1
        
        # Byte tokens
        for i in range(256):
            tok = f"<0x{i:02X}>" if i < 32 or i >= 127 else chr(i)
            self.token_to_id[tok] = idx
            self.id_to_token[idx] = tok
            idx += 1
        
        # Common tokens
        for tok in ["tool", "function", "args", "query", "search", "read", "write",
                    "file", "database", "memory", "system", "user", "assistant",
                    "json", "response", "error", "success", "true", "false", "null",
                    "the", "is", "are", "was", "were", "have", "has", "been",
                    "GLADIUS", "Artifact", "Virtual", '{"', '"}', '":', '<|im_start|>', '<|im_end|>']:
            if tok not in self.token_to_id:
                self.token_to_id[tok] = idx
                self.id_to_token[idx] = tok
                idx += 1
        
        # Fill remaining
        while idx < self.vocab_size:
            self.token_to_id[f"<unused{idx}>"] = idx
            self.id_to_token[idx] = f"<unused{idx}>"
            idx += 1
        
        self.unk_id, self.bos_id, self.eos_id = 0, 1, 2
    
    def encode(self, text: str, add_bos: bool = True, add_eos: bool = True) -> List[int]:
        tokens = [self.bos_id] if add_bos else []
        for char in text:
            byte_val = ord(char)
            tok = f"<0x{byte_val:02X}>" if byte_val < 32 or byte_val >= 127 else char
            tokens.append(self.token_to_id.get(tok, self.unk_id))
        if add_eos:
            tokens.append(self.eos_id)
        return tokens
    
    def decode(self, ids: List[int], skip_special: bool = True) -> str:
        chars = []
        for token_id in ids:
            if skip_special and token_id in [self.unk_id, self.bos_id, self.eos_id]:
                continue
            tok = self.id_to_token.get(token_id, "")
            if tok.startswith("<0x") and tok.endswith(">"):
                try:
                    chars.append(chr(int(tok[3:5], 16)))
                except:
                    pass
            elif not tok.startswith("<unused"):
                chars.append(tok)
        return "".join(chars)
    
    def save(self, path: Path):
        with open(path, 'w') as f:
            json.dump({"vocab_size": self.vocab_size, "vocab": self.token_to_id,
                       "special_tokens": {"unk": self.unk_id, "bos": self.bos_id, "eos": self.eos_id}}, f, indent=2)
    
    @classmethod
    def load(cls, path: Path):
        with open(path) as f:
            data = json.load(f)
        tok = cls(data["vocab_size"])
        tok.token_to_id = data["vocab"]
        tok.id_to_token = {int(v): k for k, v in tok.token_to_id.items()}
        special = data.get("special_tokens", {})
        tok.unk_id, tok.bos_id, tok.eos_id = special.get("unk", 0), special.get("bos", 1), special.get("eos", 2)
        return tok


# =============================================================================
# DATASET
# =============================================================================

class GladiusDataset(Dataset):
    """Training dataset"""
    def __init__(self, data_path: Path, tokenizer: LlamaTokenizer, max_length: int = 512):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.samples = []
        
        logger.info(f"Loading data from {data_path}")
        with open(data_path) as f:
            for line in f:
                try:
                    data = json.loads(line)
                    text = data.get("text", "")
                    if text:
                        self.samples.append(text)
                except json.JSONDecodeError:
                    continue
        logger.info(f"Loaded {len(self.samples)} training samples")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        tokens = self.tokenizer.encode(self.samples[idx], add_bos=True, add_eos=True)
        if len(tokens) > self.max_length:
            tokens = tokens[:self.max_length]
        else:
            tokens = tokens + [self.tokenizer.unk_id] * (self.max_length - len(tokens))
        tokens = torch.tensor(tokens, dtype=torch.long)
        return {"input_ids": tokens, "labels": tokens.clone()}


# =============================================================================
# UNIFIED TRAINER
# =============================================================================

class GladiusTrainer:
    """Unified trainer for CPU and GPU with animated display"""
    
    def __init__(self, config: GladiusConfig = None, target_params_m: int = 150):
        self.device, self.device_info = detect_device()
        
        # Use recommended params if not specified
        if config is None:
            actual_params = target_params_m or self.device_info["recommended_params_m"]
            config = GladiusConfig.for_size(actual_params)
        
        self.config = config
        self.params_m = config.total_params / 1e6
        
        logger.info(f"Initializing GLADIUS Model")
        logger.info(f"  Device: {self.device}")
        logger.info(f"  Hidden size: {config.hidden_size}")
        logger.info(f"  Layers: {config.num_hidden_layers}")
        logger.info(f"  Heads: {config.num_attention_heads}")
        logger.info(f"  Parameters: ~{self.params_m:.1f}M")
        
        self.model = GladiusModel(config).to(self.device)
        self.tokenizer = LlamaTokenizer(config.vocab_size)
        
        # Learning rate
        self.base_lr = 1e-4 if self.device.type == "cpu" else 3e-4
        
        # Optimizer with GPU-specific settings
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.base_lr,
            weight_decay=0.01
        )
        
        # Mixed precision for GPU
        self.scaler = torch.cuda.amp.GradScaler() if self.device.type == "cuda" else None
        self.use_amp = self.device.type == "cuda"
        
        self.epoch = 0
        self.global_step = 0
        
        # Display system
        self.display = None
        self.metrics = None
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        if self.device.type == "cuda":
            return torch.cuda.memory_allocated() / 1024 / 1024
        else:
            try:
                import psutil
                process = psutil.Process()
                return process.memory_info().rss / 1024 / 1024
            except:
                return 0.0
    
    def _get_grad_norm(self) -> float:
        """Calculate gradient norm"""
        total_norm = 0.0
        for p in self.model.parameters():
            if p.grad is not None:
                param_norm = p.grad.data.norm(2)
                total_norm += param_norm.item() ** 2
        return total_norm ** 0.5
    
    def _get_lr(self) -> float:
        """Get current learning rate"""
        for param_group in self.optimizer.param_groups:
            return param_group['lr']
        return self.base_lr
    
    def train(self, data_path: Path, epochs: int = 3, batch_size: int = None, 
              max_length: int = 256, animated: bool = True):
        """Train the model with animated display"""
        if batch_size is None:
            batch_size = self.device_info["recommended_batch_size"]
        
        dataset = GladiusDataset(data_path, self.tokenizer, max_length)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, 
                               num_workers=2 if self.device.type == "cuda" else 0,
                               pin_memory=self.device.type == "cuda")
        
        self.model.train()
        total_steps = len(dataloader) * epochs
        
        # Initialize display and metrics
        config_info = {
            'params': f"{self.params_m:.0f}",
            'hidden': self.config.hidden_size,
            'layers': self.config.num_hidden_layers,
            'heads': self.config.num_attention_heads,
        }
        self.display = AnimatedDisplay(str(self.device), config_info)
        self.metrics = TrainingMetrics(total_steps, epochs)
        
        # Print startup banner
        if animated:
            self.display.print_startup()
            self.display.hide_cursor()
        
        logger.info(f"Starting training:")
        logger.info(f"  Epochs: {epochs}")
        logger.info(f"  Batch size: {batch_size}")
        logger.info(f"  Total steps: {total_steps}")
        logger.info(f"  Mixed precision: {self.use_amp}")
        
        try:
            for epoch in range(self.epoch, self.epoch + epochs):
                self.metrics.start_epoch(epoch + 1)
                epoch_loss = 0
                step_in_epoch = 0
                
                for batch in dataloader:
                    input_ids = batch["input_ids"].to(self.device)
                    labels = batch["labels"].to(self.device)
                    batch_tokens = input_ids.numel()
                    
                    self.optimizer.zero_grad()
                    
                    if self.use_amp:
                        with torch.cuda.amp.autocast():
                            outputs = self.model(input_ids, labels=labels)
                            loss = outputs["loss"]
                        self.scaler.scale(loss).backward()
                        self.scaler.unscale_(self.optimizer)
                        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                        self.scaler.step(self.optimizer)
                        self.scaler.update()
                    else:
                        outputs = self.model(input_ids, labels=labels)
                        loss = outputs["loss"]
                        loss.backward()
                        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                        self.optimizer.step()
                    
                    # Update metrics
                    grad_norm = self._get_grad_norm()
                    memory_mb = self._get_memory_usage()
                    lr = self._get_lr()
                    
                    self.metrics.update(
                        loss=loss.item(),
                        grad_norm=grad_norm,
                        lr=lr,
                        batch_tokens=batch_tokens,
                        memory_mb=memory_mb
                    )
                    
                    epoch_loss += loss.item()
                    self.global_step += 1
                    step_in_epoch += 1
                    
                    # Update display
                    if animated and self.global_step % 5 == 0:
                        self.display.clear_screen()
                        print(self.display.render_full_display(self.metrics))
                    elif not animated and self.global_step % 50 == 0:
                        logger.info(f"Step {self.global_step}/{total_steps} | Loss: {loss.item():.4f} | "
                                   f"Grad: {grad_norm:.4f} | Mem: {memory_mb:.0f}MB")
                
                self.metrics.end_epoch()
                avg_loss = epoch_loss / step_in_epoch
                
                if not animated:
                    logger.info(f"Epoch {epoch + 1}/{self.epoch + epochs} | Avg Loss: {avg_loss:.4f}")
                
                self.epoch = epoch + 1
                self.save_checkpoint()
            
            # Save final model
            self.save_model()
            
            # Print completion
            if animated:
                self.display.clear_screen()
                self.display.print_completion(self.metrics)
                self.display.show_cursor()
            
            return self.epoch
            
        except KeyboardInterrupt:
            if animated:
                self.display.show_cursor()
            logger.info("\n⚠ Training interrupted by user")
            self.save_checkpoint()
            raise
        except Exception as e:
            if animated:
                self.display.show_cursor()
            raise
    
    def save_checkpoint(self, path: Path = None):
        """Save checkpoint (device-agnostic)"""
        if path is None:
            path = CHECKPOINT_DIR / f"gladius_checkpoint_epoch{self.epoch}.pt"
        
        checkpoint = {
            "epoch": self.epoch,
            "global_step": self.global_step,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "config": self.config.to_dict(),
            "device_trained_on": str(self.device),
        }
        
        if self.scaler is not None:
            checkpoint["scaler_state_dict"] = self.scaler.state_dict()
        
        # Move to CPU for device-agnostic saving
        cpu_state = {k: v.cpu() if isinstance(v, torch.Tensor) else v 
                     for k, v in checkpoint["model_state_dict"].items()}
        checkpoint["model_state_dict"] = cpu_state
        
        torch.save(checkpoint, path)
        logger.info(f"Checkpoint saved: {path}")
        
        # Keep only last 3 checkpoints
        checkpoints = sorted(CHECKPOINT_DIR.glob("gladius_checkpoint_epoch*.pt"))
        for old_ckpt in checkpoints[:-3]:
            old_ckpt.unlink()
    
    def load_checkpoint(self, path: Path = None):
        """Load checkpoint (works on any device)"""
        if path is None:
            # Find latest checkpoint
            checkpoints = sorted(CHECKPOINT_DIR.glob("gladius_checkpoint_epoch*.pt"))
            if not checkpoints:
                logger.warning("No checkpoints found")
                return False
            path = checkpoints[-1]
        
        logger.info(f"Loading checkpoint: {path}")
        checkpoint = torch.load(path, map_location=self.device, weights_only=False)
        
        # Restore config if different
        saved_config = GladiusConfig(**checkpoint["config"])
        if saved_config.to_dict() != self.config.to_dict():
            logger.info("Reinitializing model with checkpoint config")
            self.config = saved_config
            self.model = GladiusModel(self.config).to(self.device)
            self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=1e-4, weight_decay=0.01)
        
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.epoch = checkpoint["epoch"]
        self.global_step = checkpoint["global_step"]
        
        if self.scaler is not None and "scaler_state_dict" in checkpoint:
            self.scaler.load_state_dict(checkpoint["scaler_state_dict"])
        
        logger.info(f"Resumed from epoch {self.epoch}, step {self.global_step}")
        logger.info(f"Originally trained on: {checkpoint.get('device_trained_on', 'unknown')}")
        return True
    
    def save_model(self, path: Path = None):
        """Save final model"""
        if path is None:
            path = OUTPUT_DIR / "gladius_final"
        path.mkdir(parents=True, exist_ok=True)
        
        torch.save(self.model.state_dict(), path / "model.pt")
        with open(path / "config.json", 'w') as f:
            json.dump(self.config.to_dict(), f, indent=2)
        self.tokenizer.save(path / "tokenizer.json")
        
        logger.info(f"Model saved: {path}")
    
    def export_gguf(self, output_path: Path = None) -> Path:
        """Export model to GGUF format"""
        try:
            from gguf import GGUFWriter, GGMLQuantizationType, TokenType
        except ImportError:
            logger.error("gguf package not found. Install from llama.cpp/gguf-py")
            return None
        
        if output_path is None:
            params_m = self.config.total_params / 1e6
            output_path = OUTPUT_DIR / f"gladius1.1-{int(params_m)}M.gguf"
        
        import numpy as np
        
        logger.info(f"Exporting to GGUF: {output_path}")
        
        writer = GGUFWriter(str(output_path), "llama")
        
        # Architecture metadata
        writer.add_context_length(self.config.max_position_embeddings)
        writer.add_embedding_length(self.config.hidden_size)
        writer.add_block_count(self.config.num_hidden_layers)
        writer.add_feed_forward_length(self.config.intermediate_size)
        writer.add_head_count(self.config.num_attention_heads)
        writer.add_head_count_kv(self.config.num_key_value_heads)
        writer.add_rope_dimension_count(self.config.head_dim)
        writer.add_layer_norm_rms_eps(self.config.rms_norm_eps)
        writer.add_rope_freq_base(self.config.rope_theta)
        writer.add_vocab_size(self.config.vocab_size)
        writer.add_name("GLADIUS")
        writer.add_author("Artifact Virtual")
        writer.add_description("GLADIUS native model - llama.cpp compatible")
        
        # Tokenizer
        self._add_tokenizer_to_gguf(writer, TokenType)
        
        # Tensor mappings
        tensor_map = {
            "embed_tokens.weight": "token_embd.weight",
            "norm.weight": "output_norm.weight",
            "lm_head.weight": "output.weight",
        }
        for n in range(self.config.num_hidden_layers):
            tensor_map.update({
                f"layers.{n}.input_layernorm.weight": f"blk.{n}.attn_norm.weight",
                f"layers.{n}.post_attention_layernorm.weight": f"blk.{n}.ffn_norm.weight",
                f"layers.{n}.self_attn.q_proj.weight": f"blk.{n}.attn_q.weight",
                f"layers.{n}.self_attn.k_proj.weight": f"blk.{n}.attn_k.weight",
                f"layers.{n}.self_attn.v_proj.weight": f"blk.{n}.attn_v.weight",
                f"layers.{n}.self_attn.o_proj.weight": f"blk.{n}.attn_output.weight",
                f"layers.{n}.mlp.gate_proj.weight": f"blk.{n}.ffn_gate.weight",
                f"layers.{n}.mlp.up_proj.weight": f"blk.{n}.ffn_up.weight",
                f"layers.{n}.mlp.down_proj.weight": f"blk.{n}.ffn_down.weight",
            })
        
        skip_patterns = ["rotary_emb"]
        
        logger.info("Adding tensors to GGUF...")
        state_dict = self.model.state_dict()
        tensor_count = 0
        
        for name, tensor in state_dict.items():
            if any(skip in name for skip in skip_patterns):
                continue
            
            gguf_name = tensor_map.get(name)
            if not gguf_name:
                continue
            
            tensor_cpu = tensor.cpu()
            if "norm" in gguf_name or tensor_cpu.dim() == 1:
                data = tensor_cpu.numpy().astype(np.float32)
                writer.add_tensor(gguf_name, data, raw_dtype=GGMLQuantizationType.F32)
            else:
                data = tensor_cpu.float().numpy().astype(np.float16)
                writer.add_tensor(gguf_name, data, raw_dtype=GGMLQuantizationType.F16)
            tensor_count += 1
        
        logger.info(f"Added {tensor_count} tensors")
        
        writer.write_header_to_file()
        writer.write_kv_data_to_file()
        writer.write_tensors_to_file()
        writer.close()
        
        size_mb = output_path.stat().st_size / 1024 / 1024
        logger.info(f"✓ GGUF exported: {output_path} ({size_mb:.1f} MB)")
        return output_path
    
    def _add_tokenizer_to_gguf(self, writer, TokenType):
        """Add tokenizer to GGUF"""
        tokens, scores, token_types = [], [], []
        
        for idx in range(self.config.vocab_size):
            tok = self.tokenizer.id_to_token.get(idx, f"<unused{idx}>")
            tokens.append(tok.encode('utf-8'))
            scores.append(-float(idx))
            
            if tok == "<unk>":
                token_types.append(int(TokenType.UNKNOWN))
            elif tok in ["<s>", "</s>"]:
                token_types.append(int(TokenType.CONTROL))
            elif tok.startswith("<0x"):
                token_types.append(int(TokenType.BYTE))
            elif tok.startswith("<unused"):
                token_types.append(int(TokenType.UNUSED))
            else:
                token_types.append(int(TokenType.NORMAL))
        
        writer.add_tokenizer_model("llama")
        writer.add_token_list(tokens)
        writer.add_token_scores([float(s) for s in scores])
        writer.add_token_types(token_types)
        writer.add_bos_token_id(self.tokenizer.bos_id)
        writer.add_eos_token_id(self.tokenizer.eos_id)
        writer.add_pad_token_id(self.tokenizer.unk_id)
        
        logger.info(f"Added tokenizer with {self.config.vocab_size} tokens")


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="GLADIUS Unified Trainer")
    parser.add_argument("--params", type=int, default=None, help="Target parameters in millions (auto-detected if not set)")
    parser.add_argument("--epochs", type=int, default=3, help="Training epochs")
    parser.add_argument("--batch-size", type=int, default=None, help="Batch size (auto-detected if not set)")
    parser.add_argument("--max-length", type=int, default=256, help="Max sequence length")
    parser.add_argument("--data", type=str, default=None, help="Training data path")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--export-gguf", action="store_true", help="Export to GGUF after training")
    parser.add_argument("--force-cpu", action="store_true", help="Force CPU training")
    parser.add_argument("--force-gpu", action="store_true", help="Force GPU training (fails if no GPU)")
    parser.add_argument("--no-animate", action="store_true", help="Disable animated display (use simple logging)")
    
    args = parser.parse_args()
    
    # Handle device forcing
    if args.force_cpu:
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
    elif args.force_gpu and not torch.cuda.is_available():
        logger.error("--force-gpu specified but no GPU available")
        sys.exit(1)
    
    # Print startup info if not animated
    if args.no_animate:
        logger.info("=" * 70)
        logger.info("GLADIUS UNIFIED TRAINER")
        logger.info("=" * 70)
    
    # Create trainer
    trainer = GladiusTrainer(target_params_m=args.params)
    
    # Resume if requested
    if args.resume:
        trainer.load_checkpoint()
    
    # Find data
    data_path = Path(args.data) if args.data else DATA_DIR / "gladius_1b_training.jsonl"
    if not data_path.exists():
        logger.error(f"Training data not found: {data_path}")
        sys.exit(1)
    
    # Train
    trainer.train(data_path, epochs=args.epochs, batch_size=args.batch_size, 
                  max_length=args.max_length, animated=not args.no_animate)
    
    # Export if requested
    if args.export_gguf:
        gguf_path = trainer.export_gguf()
        if trainer.display and not args.no_animate:
            trainer.display.print_completion(trainer.metrics, str(gguf_path) if gguf_path else None)
    
    if args.no_animate:
        logger.info("=" * 70)
        logger.info("Training complete!")
        logger.info("=" * 70)


if __name__ == "__main__":
    main()
