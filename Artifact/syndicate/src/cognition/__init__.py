"""
Cognition Engine - Vector-based semantic memory for Gladius.

Uses HNSW index for fast similarity search with SQLite fallback for robustness.
Compatible with Hektor VDB API for future native integration.
"""

from .vector_store import VectorStore, Document, SearchResult
from .embedder import Embedder
from .syndicate_integration import SyndicateCognition

__all__ = ['VectorStore', 'Document', 'SearchResult', 'Embedder', 'SyndicateCognition']
