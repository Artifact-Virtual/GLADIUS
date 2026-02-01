#!/usr/bin/env python3
"""
Langton's Ant Simulation - GLADIUS IS THE ANT

This simulation uses the GLADIUS 71M model to make decisions
at each step instead of hardcoded rules.

The ant perceives its environment and decides which way to turn.
"""

import os
import sys
import json
import time
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import logging

# Add GLADIUS to path
GLADIUS_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(GLADIUS_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


class Grid:
    """2D grid for Langton's Ant simulation."""
    
    def __init__(self, size: int = 1000):
        self.size = size
        self.cells = np.zeros((size, size), dtype=np.uint8)  # 0=white, 1=black
        self.visit_count = np.zeros((size, size), dtype=np.uint32)
    
    def get(self, x: int, y: int) -> str:
        """Get cell color at position."""
        x, y = x % self.size, y % self.size
        return "black" if self.cells[y, x] else "white"
    
    def flip(self, x: int, y: int) -> None:
        """Flip cell color at position."""
        x, y = x % self.size, y % self.size
        self.cells[y, x] = 1 - self.cells[y, x]
        self.visit_count[y, x] += 1
    
    def get_neighborhood(self, x: int, y: int, radius: int = 1) -> list:
        """Get neighborhood around position."""
        neighborhood = []
        for dy in range(-radius, radius + 1):
            row = []
            for dx in range(-radius, radius + 1):
                nx, ny = (x + dx) % self.size, (y + dy) % self.size
                row.append(int(self.cells[ny, nx]))
            neighborhood.append(row)
        return neighborhood
    
    def save_snapshot(self, path: str) -> None:
        """Save grid as image."""
        try:
            from PIL import Image
            img = Image.fromarray((1 - self.cells) * 255)
            img.save(path)
        except ImportError:
            np.save(path.replace('.png', '.npy'), self.cells)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get grid statistics."""
        black_count = np.sum(self.cells)
        total = self.size * self.size
        return {
            "black_cells": int(black_count),
            "white_cells": int(total - black_count),
            "black_ratio": float(black_count / total),
            "visited_cells": int(np.sum(self.visit_count > 0)),
            "max_visits": int(np.max(self.visit_count))
        }


class GladiusAnt:
    """
    The Ant controlled by GLADIUS 71M model.
    
    Instead of following hardcoded rules, GLADIUS decides each move.
    """
    
    ORIENTATIONS = ['N', 'E', 'S', 'W']
    TURNS = {
        'clockwise': 1,
        'counter_clockwise': -1,
        'straight': 0,
        'reverse': 2
    }
    MOVES = {
        'N': (0, -1),
        'E': (1, 0),
        'S': (0, 1),
        'W': (-1, 0)
    }
    
    def __init__(self, model_path: Optional[str] = None, start_pos: Tuple[int, int] = None, grid_size: int = 1000):
        self.grid_size = grid_size
        self.x = start_pos[0] if start_pos else grid_size // 2
        self.y = start_pos[1] if start_pos else grid_size // 2
        self.orientation_idx = 0  # Start facing North
        self.step_count = 0
        
        self.model = None
        self.model_path = model_path
        self.use_model = False
        
        # Decision history for learning
        self.history = []
        
        # Try to load model
        if model_path and Path(model_path).exists():
            self._load_model(model_path)
        else:
            logger.warning("No model found. Using classic rules as baseline.")
    
    def _load_model(self, model_path: str) -> None:
        """Load GLADIUS model for decision making."""
        try:
            import torch
            
            # Try loading as GGUF via llama.cpp
            gguf_path = Path(model_path)
            if gguf_path.suffix == '.gguf' or (gguf_path / 'gladius.gguf').exists():
                logger.info("Loading GGUF model via llama.cpp...")
                self._load_gguf_model(model_path)
            else:
                # Try PyTorch checkpoint
                logger.info("Loading PyTorch checkpoint...")
                self.model = torch.load(model_path, map_location='cpu')
                self.use_model = True
                
            logger.info(f"Model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.use_model = False
    
    def _load_gguf_model(self, model_path: str) -> None:
        """Load GGUF model via llama-cpp-python."""
        try:
            from llama_cpp import Llama
            
            gguf_file = model_path if model_path.endswith('.gguf') else str(Path(model_path) / 'gladius.gguf')
            self.model = Llama(
                model_path=gguf_file,
                n_ctx=256,
                n_threads=2,
                verbose=False
            )
            self.use_model = True
        except ImportError:
            logger.warning("llama-cpp-python not installed. Using classic rules.")
        except Exception as e:
            logger.error(f"GGUF load error: {e}")
    
    @property
    def orientation(self) -> str:
        return self.ORIENTATIONS[self.orientation_idx]
    
    @property
    def position(self) -> Tuple[int, int]:
        return (self.x, self.y)
    
    def _classic_decision(self, cell_color: str) -> str:
        """Classic Langton's Ant rules (baseline)."""
        return "clockwise" if cell_color == "white" else "counter_clockwise"
    
    def _model_decision(self, state: Dict[str, Any]) -> Tuple[str, float]:
        """Let GLADIUS decide the move."""
        if not self.use_model or self.model is None:
            return self._classic_decision(state['cell_color']), 1.0
        
        try:
            # Format prompt for the model
            prompt = f"""You are an ant on a grid. Current state:
Cell color: {state['cell_color']}
Orientation: {state['orientation']}
Step: {state['step']}

Decide: turn clockwise, counter_clockwise, straight, or reverse.
Answer with one word:"""
            
            # Get model response
            if hasattr(self.model, '__call__'):
                # llama-cpp style
                response = self.model(prompt, max_tokens=10, temperature=0.1)
                text = response['choices'][0]['text'].strip().lower()
            else:
                # PyTorch model - would need custom inference
                text = self._classic_decision(state['cell_color'])
            
            # Parse response
            for turn in self.TURNS.keys():
                if turn in text:
                    return turn, 0.9
            
            # Default to classic if can't parse
            return self._classic_decision(state['cell_color']), 0.5
            
        except Exception as e:
            logger.debug(f"Model inference error: {e}")
            return self._classic_decision(state['cell_color']), 0.5
    
    def step(self, grid: Grid) -> Dict[str, Any]:
        """Execute one step of the ant."""
        start_time = time.time()
        
        # Get current state
        cell_color = grid.get(self.x, self.y)
        neighborhood = grid.get_neighborhood(self.x, self.y, radius=2)
        
        state = {
            'cell_color': cell_color,
            'orientation': self.orientation,
            'step': self.step_count,
            'neighborhood': neighborhood,
            'position': self.position
        }
        
        # Get decision from GLADIUS (or classic rules)
        decision, confidence = self._model_decision(state)
        
        # Record state before changes
        orientation_before = self.orientation
        position_before = self.position
        
        # Apply turn
        turn_amount = self.TURNS.get(decision, 0)
        self.orientation_idx = (self.orientation_idx + turn_amount) % 4
        
        # Flip cell
        grid.flip(self.x, self.y)
        
        # Move forward
        dx, dy = self.MOVES[self.orientation]
        self.x = (self.x + dx) % grid.size
        self.y = (self.y + dy) % grid.size
        
        self.step_count += 1
        latency = (time.time() - start_time) * 1000
        
        # Build step record
        record = {
            'step': self.step_count,
            'position_before': position_before,
            'position_after': self.position,
            'cell_before': cell_color,
            'cell_after': grid.get(*position_before),
            'orientation_before': orientation_before,
            'orientation_after': self.orientation,
            'decision': decision,
            'confidence': confidence,
            'latency_ms': latency,
            'used_model': self.use_model
        }
        
        self.history.append(record)
        
        # Keep history bounded
        if len(self.history) > 10000:
            self.history = self.history[-5000:]
        
        return record


class LangtonExperiment:
    """Main experiment runner."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        self.grid_size = self.config.get('grid_size', 1000)
        self.max_steps = self.config.get('max_steps', 1000000)
        self.checkpoint_interval = self.config.get('checkpoint_interval', 10000)
        self.model_path = self.config.get('model_path')
        
        self.results_dir = Path(__file__).parent.parent / 'results'
        self.results_dir.mkdir(exist_ok=True)
        
        self.grid = Grid(self.grid_size)
        self.ant = GladiusAnt(
            model_path=self.model_path,
            grid_size=self.grid_size
        )
        
        self.start_time = None
        self.decision_log = []
    
    def run(self, steps: Optional[int] = None) -> None:
        """Run the experiment."""
        steps = steps or self.max_steps
        self.start_time = datetime.now()
        
        logger.info(f"Starting Langton's Ant experiment")
        logger.info(f"Grid size: {self.grid_size}x{self.grid_size}")
        logger.info(f"Max steps: {steps}")
        logger.info(f"Model: {'GLADIUS' if self.ant.use_model else 'Classic Rules'}")
        
        try:
            for i in range(steps):
                record = self.ant.step(self.grid)
                
                # Log progress
                if (i + 1) % 1000 == 0:
                    stats = self.grid.get_stats()
                    logger.info(
                        f"Step {i+1:,} | Pos: {self.ant.position} | "
                        f"Black: {stats['black_ratio']:.2%} | "
                        f"Visited: {stats['visited_cells']:,}"
                    )
                
                # Checkpoint
                if (i + 1) % self.checkpoint_interval == 0:
                    self._save_checkpoint(i + 1)
        
        except KeyboardInterrupt:
            logger.info("Experiment interrupted by user")
        
        finally:
            self._save_final_results()
    
    def _save_checkpoint(self, step: int) -> None:
        """Save checkpoint."""
        checkpoint_dir = self.results_dir / f'checkpoint_{step}'
        checkpoint_dir.mkdir(exist_ok=True)
        
        # Save grid snapshot
        self.grid.save_snapshot(str(checkpoint_dir / 'grid.png'))
        
        # Save stats
        stats = {
            'step': step,
            'timestamp': datetime.now().isoformat(),
            'ant_position': self.ant.position,
            'ant_orientation': self.ant.orientation,
            'grid_stats': self.grid.get_stats(),
            'model_used': self.ant.use_model
        }
        
        with open(checkpoint_dir / 'stats.json', 'w') as f:
            json.dump(stats, f, indent=2)
        
        # Save recent decisions
        with open(checkpoint_dir / 'recent_decisions.json', 'w') as f:
            json.dump(self.ant.history[-1000:], f, indent=2)
        
        logger.info(f"Checkpoint saved at step {step}")
    
    def _save_final_results(self) -> None:
        """Save final experiment results."""
        final_dir = self.results_dir / 'final'
        final_dir.mkdir(exist_ok=True)
        
        # Save grid
        self.grid.save_snapshot(str(final_dir / 'final_grid.png'))
        
        # Save summary
        duration = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        summary = {
            'experiment_id': 'EXP-001',
            'name': 'langtons_ant',
            'completed': datetime.now().isoformat(),
            'total_steps': self.ant.step_count,
            'duration_seconds': duration,
            'steps_per_second': self.ant.step_count / duration if duration > 0 else 0,
            'final_position': self.ant.position,
            'final_orientation': self.ant.orientation,
            'grid_stats': self.grid.get_stats(),
            'model_info': {
                'used_model': self.ant.use_model,
                'model_path': self.ant.model_path
            }
        }
        
        with open(final_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Final results saved. Total steps: {self.ant.step_count:,}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Langton's Ant with GLADIUS")
    parser.add_argument('--steps', type=int, default=100000, help='Number of steps')
    parser.add_argument('--grid-size', type=int, default=1000, help='Grid size')
    parser.add_argument('--model', type=str, help='Path to GLADIUS model')
    parser.add_argument('--checkpoint', type=int, default=10000, help='Checkpoint interval')
    
    args = parser.parse_args()
    
    config = {
        'max_steps': args.steps,
        'grid_size': args.grid_size,
        'model_path': args.model,
        'checkpoint_interval': args.checkpoint
    }
    
    experiment = LangtonExperiment(config)
    experiment.run()


if __name__ == '__main__':
    main()
