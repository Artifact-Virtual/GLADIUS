"""
Native Tool Calling Model - Embedded GGUF model for native tool execution.

This module provides:
1. NativeToolRouter - Route queries to appropriate tools using tiny GGUF model
2. ModelTrainer - Fine-tune models on tool schemas
3. Integration with llama.cpp for inference
4. Fallback to Ollama when native model unavailable
"""

from .router import (
    NativeToolRouter,
    ToolRoutingResult,
    NATIVE_MODEL_AVAILABLE,
)
from .trainer import (
    ModelTrainer,
    TrainingConfig,
    TrainingMetrics,
)

__all__ = [
    "NativeToolRouter",
    "ToolRoutingResult", 
    "NATIVE_MODEL_AVAILABLE",
    "ModelTrainer",
    "TrainingConfig",
    "TrainingMetrics",
]
