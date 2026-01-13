"""
Cognition Engine - Vector-based semantic memory for Gladius.

Supports two backends:
1. **Hektor VDB** (preferred): Native C++ SIMD-optimized vector database
2. **hnswlib + SQLite** (fallback): Python-based with SQLite persistence

Compatible with Hektor VDB API for future native integration.
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

__all__ = [
    'VectorStore', 
    'HektorVectorStore',
    'Document', 
    'SearchResult', 
    'Embedder', 
    'SyndicateCognition',
    'get_vector_store',
    'HEKTOR_AVAILABLE',
]
