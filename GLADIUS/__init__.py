"""
GLADIUS - Native AI Model
=========================

The brain of Artifact Virtual Enterprise.

Components:
- router/          Pattern-based and GGUF inference routing
- training/        Training harness and data generation
- models/          GGUF model files (production, staging, base)

Usage:
    from GLADIUS.router.pattern_router import PatternRouter
    from GLADIUS.training.harness import CognitionSandbox
    from GLADIUS.training.generator import TrainingGenerator
"""

__version__ = "0.1.0"
__author__ = "Artifact Virtual"

# Lazy imports to avoid circular dependencies
def get_router():
    """Get the pattern router instance."""
    from GLADIUS.router.pattern_router import PatternRouter
    return PatternRouter()

def get_sandbox(base_path: str = None):
    """Get a training sandbox instance."""
    from GLADIUS.training.harness import CognitionSandbox
    return CognitionSandbox(base_path=base_path)

def get_generator():
    """Get the training data generator."""
    from GLADIUS.training.generator import TrainingGenerator
    return TrainingGenerator()
