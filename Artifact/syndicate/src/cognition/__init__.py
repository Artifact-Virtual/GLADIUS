"""
Cognition Engine - Vector-based semantic memory for Gladius.

Supports two backends:
1. **Hektor VDB** (preferred): Native C++ SIMD-optimized vector database
2. **hnswlib + SQLite** (fallback): Python-based with SQLite persistence

Features:
- Semantic search across all historical data
- Hybrid search (vector + BM25) with Hektor backend
- Memory Module: Multi-database access with native tool calling
- Tool Calling: Native function definitions for cognition learning
- Training Generator: Generate fine-tuning data from tool usage
- Self-Improvement: Autonomous improvement proposals with audit trail
- Learning Loop: Continuous learning cycle with benchmarking
"""

from .vector_store import VectorStore, Document, SearchResult
from .embedder import Embedder
from .syndicate_integration import SyndicateCognition

# Try to import Hektor backend
HEKTOR_AVAILABLE = False
HektorVectorStore = None
try:
    from .hektor_store import HektorVectorStore, HEKTOR_AVAILABLE, get_vector_store
except ImportError:
    def get_vector_store(path, dim=384, prefer_hektor=True, **kwargs):
        """Fallback when hektor_store can't be imported."""
        return VectorStore(path, dim=dim, **kwargs)

# Memory Module and Tool Calling
try:
    from .memory_module import MemoryModule, ToolResult, DatabaseConnection
    from .tool_calling import (
        ToolDefinition, 
        ToolParameter, 
        ToolRegistry, 
        TOOL_REGISTRY,
        get_tool_registry,
        get_tools_schema,
        BUILTIN_TOOLS
    )
    MEMORY_MODULE_AVAILABLE = True
except ImportError as e:
    MEMORY_MODULE_AVAILABLE = False
    MemoryModule = None
    ToolResult = None
    ToolRegistry = None

# Training and Self-Improvement
try:
    from .training_generator import (
        TrainingDataGenerator,
        TrainingDataset,
        TrainingExample,
        FineTuningPipeline
    )
    from .self_improvement import (
        SelfImprovementEngine,
        ImprovementProposal,
        ImprovementCategory,
        ProposalStatus,
        Snapshot
    )
    from .learning_loop import (
        CognitionLearningLoop,
        LearningCycleResult,
        run_learning_cycle,
        run_benchmark
    )
    LEARNING_AVAILABLE = True
except ImportError as e:
    LEARNING_AVAILABLE = False
    TrainingDataGenerator = None
    SelfImprovementEngine = None
    CognitionLearningLoop = None

# Native Model (for tool routing)
try:
    from .native_model import (
        NativeToolRouter,
        ToolRoutingResult,
        NATIVE_MODEL_AVAILABLE,
        ModelTrainer,
        TrainingConfig,
        TrainingMetrics
    )
except ImportError:
    NATIVE_MODEL_AVAILABLE = False
    NativeToolRouter = None
    ModelTrainer = None

__all__ = [
    # Core
    'VectorStore', 
    'HektorVectorStore',
    'Document', 
    'SearchResult', 
    'Embedder', 
    'SyndicateCognition',
    'get_vector_store',
    'HEKTOR_AVAILABLE',
    
    # Memory Module
    'MemoryModule',
    'ToolResult',
    'DatabaseConnection',
    'MEMORY_MODULE_AVAILABLE',
    
    # Tool Calling
    'ToolDefinition',
    'ToolParameter',
    'ToolRegistry',
    'TOOL_REGISTRY',
    'get_tool_registry',
    'get_tools_schema',
    'BUILTIN_TOOLS',
    
    # Training & Learning
    'TrainingDataGenerator',
    'TrainingDataset',
    'TrainingExample',
    'FineTuningPipeline',
    'SelfImprovementEngine',
    'ImprovementProposal',
    'ImprovementCategory',
    'ProposalStatus',
    'Snapshot',
    'CognitionLearningLoop',
    'LearningCycleResult',
    'run_learning_cycle',
    'run_benchmark',
    'LEARNING_AVAILABLE',
    
    # Native Model
    'NativeToolRouter',
    'ToolRoutingResult',
    'NATIVE_MODEL_AVAILABLE',
    'ModelTrainer',
    'TrainingConfig',
    'TrainingMetrics',
]
