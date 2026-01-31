#!/usr/bin/env python3
"""
Simple Vector Memory for GLADIUS
================================

A lightweight, pure-Python vector store using numpy and faiss (if available).
Falls back to brute-force cosine similarity if faiss not available.

This is a fallback when hektor-vdb has issues.

Author: ARTIFACT VIRTUAL
"""

import os
import json
import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)

# Try to use faiss for fast similarity search
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.info("FAISS not available, using numpy brute-force search")

# Try sentence transformers for embeddings
_embedder = None

def get_embedder():
    """Get or create sentence transformer for embeddings."""
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedder = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Loaded sentence-transformers: all-MiniLM-L6-v2")
        except ImportError:
            logger.warning("sentence-transformers not available, using hash embeddings")
            _embedder = "hash"
    return _embedder


def embed_text(text: str, dimension: int = 384) -> np.ndarray:
    """Generate embedding for text."""
    embedder = get_embedder()
    
    if embedder == "hash":
        # Hash-based fallback embedding
        import hashlib
        hash_bytes = hashlib.sha512(text.encode()).digest()
        full_bytes = hash_bytes
        while len(full_bytes) < dimension * 4:
            hash_bytes = hashlib.sha512(hash_bytes).digest()
            full_bytes += hash_bytes
        vec = np.frombuffer(full_bytes[:dimension * 4], dtype=np.float32).copy()
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec
    else:
        vec = embedder.encode(text, convert_to_numpy=True)
        return vec.astype(np.float32)


class SimpleVectorStore:
    """
    Simple vector store with persistence.
    Uses numpy arrays and optionally FAISS for fast search.
    """
    
    def __init__(
        self,
        db_path: str,
        dimension: int = 384,
        use_faiss: bool = True
    ):
        self.db_path = Path(db_path)
        self.dimension = dimension
        self.use_faiss = use_faiss and FAISS_AVAILABLE
        
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Storage
        self.vectors: List[np.ndarray] = []
        self.metadata: List[Dict[str, Any]] = []
        self.texts: List[str] = []
        
        # FAISS index
        self.index = None
        
        # Load existing data
        self._load()
        
        logger.info(f"SimpleVectorStore initialized at {db_path} with {len(self.vectors)} vectors")
    
    def _load(self):
        """Load data from disk."""
        data_file = self.db_path.with_suffix('.json')
        vectors_file = self.db_path.with_suffix('.npy')
        
        if data_file.exists():
            try:
                with open(data_file) as f:
                    data = json.load(f)
                    self.metadata = data.get('metadata', [])
                    self.texts = data.get('texts', [])
            except Exception as e:
                logger.warning(f"Could not load metadata: {e}")
        
        if vectors_file.exists():
            try:
                self.vectors = list(np.load(vectors_file, allow_pickle=True))
            except Exception as e:
                logger.warning(f"Could not load vectors: {e}")
        
        # Rebuild FAISS index
        if self.vectors and self.use_faiss:
            self._rebuild_index()
    
    def _save(self):
        """Save data to disk."""
        data_file = self.db_path.with_suffix('.json')
        vectors_file = self.db_path.with_suffix('.npy')
        
        try:
            with open(data_file, 'w') as f:
                json.dump({
                    'metadata': self.metadata,
                    'texts': self.texts,
                    'count': len(self.vectors),
                    'dimension': self.dimension,
                    'updated': datetime.now().isoformat()
                }, f, indent=2)
            
            if self.vectors:
                np.save(vectors_file, np.array(self.vectors))
        except Exception as e:
            logger.error(f"Could not save data: {e}")
    
    def _rebuild_index(self):
        """Rebuild FAISS index."""
        if not self.use_faiss or not self.vectors:
            return
        
        try:
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product (cosine with normalized)
            vectors_array = np.array(self.vectors).astype('float32')
            # Normalize for cosine similarity
            faiss.normalize_L2(vectors_array)
            self.index.add(vectors_array)
        except Exception as e:
            logger.warning(f"FAISS index build failed: {e}")
            self.index = None
    
    def add_text(
        self,
        text: str,
        doc_type: str = "unknown",
        source: str = "",
        extra: Dict[str, Any] = None
    ) -> int:
        """Add text with automatic embedding."""
        vector = embed_text(text, self.dimension)
        return self.add_vector(vector, text, doc_type, source, extra)
    
    def add_vector(
        self,
        vector: np.ndarray,
        text: str = "",
        doc_type: str = "unknown",
        source: str = "",
        extra: Dict[str, Any] = None
    ) -> int:
        """Add a vector with metadata."""
        vector = np.asarray(vector, dtype=np.float32)
        
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        vec_id = len(self.vectors)
        self.vectors.append(vector)
        self.texts.append(text)
        self.metadata.append({
            'id': vec_id,
            'doc_type': doc_type,
            'source': source,
            'date': datetime.now().isoformat(),
            'extra': extra or {}
        })
        
        # Update FAISS index
        if self.use_faiss and self.index is not None:
            vec_normalized = vector.reshape(1, -1).astype('float32')
            self.index.add(vec_normalized)
        elif self.use_faiss and len(self.vectors) == 1:
            self._rebuild_index()
        
        # Auto-save periodically
        if len(self.vectors) % 100 == 0:
            self._save()
        
        return vec_id
    
    def query_text(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Query by text."""
        query_vec = embed_text(query, self.dimension)
        return self.query_vector(query_vec, top_k)
    
    def query_vector(
        self,
        vector: np.ndarray,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Query by vector."""
        if not self.vectors:
            return []
        
        vector = np.asarray(vector, dtype=np.float32)
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        k = min(top_k, len(self.vectors))
        
        if self.use_faiss and self.index is not None:
            # FAISS search
            query_vec = vector.reshape(1, -1).astype('float32')
            scores, indices = self.index.search(query_vec, k)
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx >= 0 and idx < len(self.vectors):
                    results.append({
                        'id': int(idx),
                        'score': float(score),
                        'text': self.texts[idx],
                        **self.metadata[idx]
                    })
            return results
        else:
            # Brute force cosine similarity
            vectors_array = np.array(self.vectors)
            similarities = np.dot(vectors_array, vector)
            top_indices = np.argsort(similarities)[-k:][::-1]
            
            results = []
            for idx in top_indices:
                results.append({
                    'id': int(idx),
                    'score': float(similarities[idx]),
                    'text': self.texts[idx],
                    **self.metadata[idx]
                })
            return results
    
    def count(self) -> int:
        """Get total vector count."""
        return len(self.vectors)
    
    def save(self):
        """Force save to disk."""
        self._save()
    
    def stats(self) -> Dict[str, Any]:
        """Get statistics."""
        return {
            'path': str(self.db_path),
            'dimension': self.dimension,
            'total_vectors': len(self.vectors),
            'using_faiss': self.use_faiss and self.index is not None,
            'faiss_available': FAISS_AVAILABLE
        }


class GladiusVectorMemory:
    """
    High-level memory manager for GLADIUS.
    Manages multiple vector stores for different purposes.
    """
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = str(Path(__file__).parent.parent / "memory")
        
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self._stores: Dict[str, SimpleVectorStore] = {}
        self._init_default_stores()
    
    def _init_default_stores(self):
        """Initialize default memory stores."""
        self._stores["conversations"] = SimpleVectorStore(
            db_path=str(self.base_path / "conversations"),
            dimension=384
        )
        self._stores["training"] = SimpleVectorStore(
            db_path=str(self.base_path / "training"),
            dimension=384
        )
        self._stores["knowledge"] = SimpleVectorStore(
            db_path=str(self.base_path / "knowledge"),
            dimension=384
        )
    
    def get_store(self, name: str) -> SimpleVectorStore:
        """Get a store by name, creating if needed."""
        if name not in self._stores:
            self._stores[name] = SimpleVectorStore(
                db_path=str(self.base_path / name)
            )
        return self._stores[name]
    
    def remember(self, text: str, store: str = "conversations", **kwargs) -> int:
        """Store a memory."""
        return self.get_store(store).add_text(text, **kwargs)
    
    def recall(self, query: str, store: str = "conversations", top_k: int = 5) -> List[Dict]:
        """Recall similar memories."""
        return self.get_store(store).query_text(query, top_k)
    
    def recall_all(self, query: str, top_k: int = 3) -> Dict[str, List[Dict]]:
        """Recall from all stores."""
        return {name: store.query_text(query, top_k) for name, store in self._stores.items()}
    
    def stats_all(self) -> Dict[str, Dict]:
        """Get stats for all stores."""
        return {name: store.stats() for name, store in self._stores.items()}
    
    def save_all(self):
        """Save all stores."""
        for store in self._stores.values():
            store.save()
    
    def total_vectors(self) -> int:
        """Get total vectors across all stores."""
        return sum(store.count() for store in self._stores.values())


# Global instance
_memory_manager: Optional[GladiusVectorMemory] = None


def get_vector_memory() -> GladiusVectorMemory:
    """Get or create the global memory manager."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = GladiusVectorMemory()
    return _memory_manager


def remember(text: str, store: str = "conversations", **kwargs) -> int:
    """Quick function to store a memory."""
    return get_vector_memory().remember(text, store, **kwargs)


def recall(query: str, store: str = "conversations", top_k: int = 5) -> List[Dict]:
    """Quick function to recall memories."""
    return get_vector_memory().recall(query, store, top_k)


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Simple Vector Memory...")
    
    mem = get_vector_memory()
    
    # Add test data
    samples = [
        ("GLADIUS is an AI system for AGI research", "knowledge"),
        ("SENTINEL monitors research and development", "knowledge"),
        ("Market data from SYNDICATE feeds", "knowledge"),
        ("User asked about vector databases", "conversations"),
        ("Training sample: How to use llama.cpp", "training"),
    ]
    
    for text, store in samples:
        vid = mem.remember(text, store=store, doc_type="test")
        print(f"Added to {store}: ID {vid}")
    
    print(f"\nTotal vectors: {mem.total_vectors()}")
    print(f"\nStats: {json.dumps(mem.stats_all(), indent=2)}")
    
    # Query
    results = mem.recall("What is GLADIUS?", store="knowledge", top_k=3)
    print(f"\nQuery 'What is GLADIUS?':")
    for r in results:
        print(f"  Score {r['score']:.4f}: {r['text'][:50]}...")
    
    # Save
    mem.save_all()
    print("\nMemory saved successfully!")
