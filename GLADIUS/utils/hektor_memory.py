#!/usr/bin/env python3
"""
Hektor Vector Database Integration for GLADIUS
High-performance vector memory using pyvdb (hektor-vdb)

Author: ARTIFACT VIRTUAL
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Callable
from datetime import datetime

try:
    import pyvdb
    from pyvdb import (
        VectorDatabase,
        DatabaseConfig,
        Metadata,
        QueryOptions,
        DistanceMetric,
        DocumentType
    )
    HEKTOR_AVAILABLE = True
except ImportError:
    HEKTOR_AVAILABLE = False

import numpy as np

logger = logging.getLogger(__name__)


# Simple embedding function using sentence transformers (if available)
_sentence_transformer = None

def get_embedder():
    """Get or create sentence transformer for embeddings."""
    global _sentence_transformer
    if _sentence_transformer is None:
        try:
            from sentence_transformers import SentenceTransformer
            _sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Loaded sentence-transformers model: all-MiniLM-L6-v2")
        except ImportError:
            logger.warning("sentence-transformers not available, using hash embeddings")
            _sentence_transformer = "hash"
    return _sentence_transformer


def embed_text(text: str, dimension: int = 384) -> np.ndarray:
    """
    Generate embedding for text.
    Uses sentence-transformers if available, otherwise hash-based fallback.
    """
    embedder = get_embedder()
    
    if embedder == "hash":
        # Hash-based fallback embedding (deterministic but less semantic)
        import hashlib
        hash_bytes = hashlib.sha512(text.encode()).digest()
        # Expand to dimension using multiple hashes
        full_bytes = hash_bytes
        while len(full_bytes) < dimension * 4:
            hash_bytes = hashlib.sha512(hash_bytes).digest()
            full_bytes += hash_bytes
        # Convert to float32 array
        vec = np.frombuffer(full_bytes[:dimension * 4], dtype=np.float32)
        # Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec
    else:
        # Use sentence transformers
        vec = embedder.encode(text, convert_to_numpy=True)
        return vec.astype(np.float32)


class HektorMemory:
    """
    GLADIUS long-term memory powered by Hektor vector database.
    Stores embeddings, conversations, training data, and knowledge.
    """
    
    def __init__(
        self,
        db_path: str = None,
        dimension: int = 384,  # Default embedding dimension
        max_elements: int = 1000000,
        metric: str = "cosine",
        num_threads: int = 4,
        auto_sync: bool = True,
        embedder: Callable[[str], np.ndarray] = None
    ):
        """
        Initialize Hektor memory.
        
        Args:
            db_path: Path to database file (default: GLADIUS/memory/hektor.db)
            dimension: Embedding dimension
            max_elements: Maximum number of vectors to store
            metric: Distance metric (cosine, l2, dot)
            num_threads: Number of threads for search
            auto_sync: Auto-sync to disk
            embedder: Custom embedding function (text -> numpy array)
        """
        if not HEKTOR_AVAILABLE:
            raise ImportError(
                "hektor-vdb not installed. Install with: pip install hektor-vdb"
            )
        
        # Default path
        if db_path is None:
            base_dir = Path(__file__).parent.parent
            db_path = str(base_dir / "memory" / "hektor.db")
        
        self.db_path = db_path
        self.dimension = dimension
        self._embedder = embedder or (lambda t: embed_text(t, dimension))
        
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Configure database
        config = DatabaseConfig()
        config.path = db_path
        config.dimension = dimension
        config.max_elements = max_elements
        config.num_threads = num_threads
        config.auto_sync = auto_sync
        config.memory_only = False
        
        # Set distance metric
        if metric.lower() == "cosine":
            config.metric = DistanceMetric.Cosine
        elif metric.lower() == "l2":
            config.metric = DistanceMetric.L2
        elif metric.lower() == "dot":
            config.metric = DistanceMetric.DotProduct
        else:
            config.metric = DistanceMetric.Cosine
        
        # HNSW parameters for quality/speed tradeoff
        config.hnsw_m = 16  # Connections per node
        config.hnsw_ef_construction = 200  # Construction quality
        config.hnsw_ef_search = 100  # Search quality
        
        self.config = config
        self.db = VectorDatabase(config)
        self.db.init()
        
        logger.info(f"Hektor memory initialized at {db_path}")
        logger.info(f"  Dimension: {dimension}, Metric: {metric}")
        logger.info(f"  Existing vectors: {len(self.db)}")
    
    def add_text(
        self,
        text: str,
        doc_type: str = "unknown",
        date: str = None,
        source: str = "",
        extra: Dict[str, Any] = None
    ) -> int:
        """
        Add text to the database with automatic embedding.
        
        Args:
            text: Text content to store
            doc_type: Document type (conversation, training, knowledge, etc.)
            date: Date string (defaults to now)
            source: Source identifier
            extra: Additional metadata
            
        Returns:
            Vector ID
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Generate embedding using our embedder
        vector = self._embedder(text)
        
        # Create metadata - using available fields
        meta = Metadata()
        meta.date = date
        meta.source_file = source or doc_type
        meta.asset = text[:100] if text else ""  # Store truncated text in asset field
        meta.bias = doc_type  # Store doc type in bias field
        
        # Store full text and extra as JSON in a file (since Metadata is limited)
        text_store = self._get_text_store()
        text_id = len(text_store)
        text_store[str(text_id)] = {
            "text": text,
            "doc_type": doc_type,
            "date": date,
            "source": source,
            "extra": extra or {}
        }
        self._save_text_store(text_store)
        
        try:
            vec_id = self.db.add_vector(vector, meta)
            logger.debug(f"Added text vector {vec_id}: {text[:50]}...")
            return vec_id
        except Exception as e:
            logger.error(f"Failed to add text: {e}")
            raise
    
    def _get_text_store_path(self) -> Path:
        """Get path to text store JSON file."""
        return Path(self.db_path).parent / f"{Path(self.db_path).stem}_texts.json"
    
    def _get_text_store(self) -> Dict:
        """Load text store from disk."""
        path = self._get_text_store_path()
        if path.exists():
            try:
                return json.loads(path.read_text())
            except:
                return {}
        return {}
    
    def _save_text_store(self, store: Dict):
        """Save text store to disk."""
        path = self._get_text_store_path()
        path.write_text(json.dumps(store, indent=2))
    
    def get_full_text(self, vec_id: int) -> Optional[str]:
        """Get full text for a vector ID."""
        store = self._get_text_store()
        data = store.get(str(vec_id))
        return data.get("text") if data else None
    
    def add_vector(
        self,
        vector: np.ndarray,
        text: str = "",
        source: str = "",
        doc_type: str = "unknown",
        extra: Dict[str, Any] = None
    ) -> int:
        """
        Add a pre-computed vector with metadata.
        
        Args:
            vector: Embedding vector (numpy array)
            text: Original text content
            source: Source identifier
            doc_type: Document type
            extra: Additional metadata
            
        Returns:
            Vector ID
        """
        # Ensure vector is float32
        vector = np.asarray(vector, dtype=np.float32)
        
        if vector.shape[0] != self.dimension:
            raise ValueError(
                f"Vector dimension {vector.shape[0]} doesn't match "
                f"database dimension {self.dimension}"
            )
        
        # Create metadata
        meta = Metadata()
        meta.text = text[:1000] if text else ""  # Truncate long text
        meta.source = source
        meta.date = datetime.now().strftime("%Y-%m-%d")
        
        # Store extra metadata as JSON in notes field if available
        if extra:
            meta.notes = json.dumps(extra)
        
        vec_id = self.db.add_vector(vector, meta)
        logger.debug(f"Added vector {vec_id}")
        return vec_id
    
    def query_text(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Query similar texts using semantic search.
        
        Args:
            query: Query text
            top_k: Number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of results with text, score, and metadata
        """
        # Generate query embedding
        query_vec = self._embedder(query)
        
        # Use vector query
        return self.query_vector(query_vec, top_k=top_k, threshold=threshold)
    
    def query_vector(
        self,
        vector: np.ndarray,
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Query similar vectors directly.
        
        Args:
            vector: Query vector
            top_k: Number of results
            threshold: Minimum similarity
            
        Returns:
            List of results
        """
        vector = np.asarray(vector, dtype=np.float32)
        
        options = QueryOptions()
        options.k = top_k
        options.include_metadata = True
        
        try:
            results = self.db.query_vector(vector, options)
            text_store = self._get_text_store()
            
            output = []
            for r in results:
                # Get full text from text store
                text_data = text_store.get(str(r.id), {})
                
                item = {
                    "id": r.id,
                    "score": r.score,
                    "distance": r.distance,
                    "text": text_data.get("text", r.metadata.asset if r.metadata else ""),
                    "doc_type": text_data.get("doc_type", r.metadata.bias if r.metadata else ""),
                    "date": text_data.get("date", r.metadata.date if r.metadata else ""),
                    "source": text_data.get("source", r.metadata.source_file if r.metadata else ""),
                }
                output.append(item)
            
            return output
        except Exception as e:
            logger.error(f"Vector query failed: {e}")
            return []
    
    def get_metadata(self, vec_id: int) -> Optional[Dict[str, Any]]:
        """Get metadata for a vector by ID."""
        meta = self.db.get_metadata(vec_id)
        if meta:
            return {
                "id": vec_id,
                "text": meta.text,
                "source": meta.source,
                "date": meta.date,
            }
        return None
    
    def get_vector(self, vec_id: int) -> Optional[np.ndarray]:
        """Get raw vector by ID."""
        return self.db.get_vector(vec_id)
    
    def count(self) -> int:
        """Get total number of vectors."""
        return len(self.db)
    
    def optimize(self):
        """Optimize the index for better search performance."""
        self.db.optimize()
        logger.info("Database optimized")
    
    def compact(self):
        """Compact the database to reduce disk usage."""
        self.db.compact()
        logger.info("Database compacted")
    
    def export_training_data(self, output_path: str):
        """Export vectors as training data."""
        self.db.export_training_data(output_path)
        logger.info(f"Exported training data to {output_path}")
    
    def stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        return {
            "path": self.db_path,
            "dimension": self.dimension,
            "total_vectors": len(self.db),
            "is_ready": self.db.is_ready(),
            "config": {
                "metric": str(self.config.metric),
                "max_elements": self.config.max_elements,
                "hnsw_m": self.config.hnsw_m,
                "hnsw_ef_search": self.config.hnsw_ef_search,
            }
        }


class GladiusMemoryManager:
    """
    High-level memory manager for GLADIUS.
    Manages multiple memory stores for different purposes.
    """
    
    def __init__(self, base_path: str = None):
        """
        Initialize memory manager.
        
        Args:
            base_path: Base path for memory stores
        """
        if base_path is None:
            base_path = str(Path(__file__).parent.parent / "memory")
        
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self._stores: Dict[str, HektorMemory] = {}
        
        # Initialize default stores
        self._init_default_stores()
    
    def _init_default_stores(self):
        """Initialize default memory stores."""
        # Conversation memory - recent interactions
        self._stores["conversations"] = HektorMemory(
            db_path=str(self.base_path / "conversations.db"),
            dimension=384,
            max_elements=100000
        )
        
        # Training memory - learned patterns
        self._stores["training"] = HektorMemory(
            db_path=str(self.base_path / "training.db"),
            dimension=384,
            max_elements=500000
        )
        
        # Knowledge base - long-term knowledge
        self._stores["knowledge"] = HektorMemory(
            db_path=str(self.base_path / "knowledge.db"),
            dimension=384,
            max_elements=1000000
        )
    
    def get_store(self, name: str) -> HektorMemory:
        """Get a memory store by name."""
        if name not in self._stores:
            # Create new store on demand
            self._stores[name] = HektorMemory(
                db_path=str(self.base_path / f"{name}.db")
            )
        return self._stores[name]
    
    def remember(
        self,
        text: str,
        store: str = "conversations",
        **kwargs
    ) -> int:
        """
        Store a memory.
        
        Args:
            text: Text to remember
            store: Which store to use
            **kwargs: Additional metadata
            
        Returns:
            Memory ID
        """
        return self.get_store(store).add_text(text, **kwargs)
    
    def recall(
        self,
        query: str,
        store: str = "conversations",
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Recall similar memories.
        
        Args:
            query: Query text
            store: Which store to search
            top_k: Number of results
            
        Returns:
            List of matching memories
        """
        return self.get_store(store).query_text(query, top_k=top_k)
    
    def recall_all(
        self,
        query: str,
        top_k: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Recall from all stores.
        
        Args:
            query: Query text
            top_k: Number of results per store
            
        Returns:
            Dict of store -> results
        """
        results = {}
        for name, store in self._stores.items():
            results[name] = store.query_text(query, top_k=top_k)
        return results
    
    def stats_all(self) -> Dict[str, Dict[str, Any]]:
        """Get stats for all stores."""
        return {name: store.stats() for name, store in self._stores.items()}
    
    def optimize_all(self):
        """Optimize all stores."""
        for name, store in self._stores.items():
            logger.info(f"Optimizing {name}...")
            store.optimize()


# Convenience function for quick access
_default_manager: Optional[GladiusMemoryManager] = None


def get_memory_manager() -> GladiusMemoryManager:
    """Get or create the default memory manager."""
    global _default_manager
    if _default_manager is None:
        _default_manager = GladiusMemoryManager()
    return _default_manager


def remember(text: str, store: str = "conversations", **kwargs) -> int:
    """Quick function to store a memory."""
    return get_memory_manager().remember(text, store, **kwargs)


def recall(query: str, store: str = "conversations", top_k: int = 5) -> List[Dict]:
    """Quick function to recall memories."""
    return get_memory_manager().recall(query, store, top_k)


# Test function
def _test():
    """Test Hektor integration."""
    print("Testing Hektor Memory Integration...")
    print(f"Hektor available: {HEKTOR_AVAILABLE}")
    
    if not HEKTOR_AVAILABLE:
        print("Install with: pip install hektor-vdb")
        return
    
    # Create test memory
    memory = HektorMemory(
        db_path="/tmp/gladius_hektor_test.db",
        dimension=384
    )
    
    print(f"Database initialized: {memory.stats()}")
    
    # Add some test data
    id1 = memory.add_text("GLADIUS is an AI system being developed", doc_type="knowledge")
    id2 = memory.add_text("Training uses PyTorch and exports to GGUF", doc_type="training")
    id3 = memory.add_text("The user asked about vector databases", doc_type="conversation")
    
    print(f"Added vectors: {id1}, {id2}, {id3}")
    print(f"Total vectors: {memory.count()}")
    
    # Query
    results = memory.query_text("What is GLADIUS?", top_k=3)
    print(f"\nQuery results for 'What is GLADIUS?':")
    for r in results:
        print(f"  Score: {r['score']:.4f} - {r['text'][:50]}...")
    
    print("\nHektor integration test complete!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _test()
