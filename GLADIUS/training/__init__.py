"""
GLADIUS Training Module
=======================

Components:
- harness.py    Isolated training sandbox
- generator.py  Training data generation
- scripts/      Training scripts (trainer, progressive_trainer)
- data/         Training datasets

Usage:
    from GLADIUS.training.harness import CognitionSandbox
    from GLADIUS.training.generator import TrainingGenerator
"""

from pathlib import Path

# Module paths
TRAINING_DIR = Path(__file__).parent
DATA_DIR = TRAINING_DIR / "data"
SCRIPTS_DIR = TRAINING_DIR / "scripts"

def get_sandbox(base_path: str = None):
    """Create a training sandbox."""
    from .harness import CognitionSandbox
    return CognitionSandbox(base_path=base_path)

def get_generator():
    """Create a training data generator."""
    from .generator import TrainingGenerator
    return TrainingGenerator()
