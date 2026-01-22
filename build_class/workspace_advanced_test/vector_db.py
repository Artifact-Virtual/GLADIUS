#!/usr/bin/env python3
"""
Scalable Robust Vector Database
Supports vector storage, similarity search, and persistence.
"""

import numpy as np
import json
import os
from typing import List, Tuple, Optional, Dict, Any

class VectorDatabase:
    """
    A simple but robust vector database implementation.
    Supports adding vectors, similarity search, and persistence.
    """
    
    def __init__(self, dimension: int, metric: str = 'cosine'):
        """
        Initialize vector database.
        
        Args:
            dimension: Vector dimension
            metric: Distance metric ('cosine', 'euclidean', 'dot')
        """
        self.dimension = dimension
        self.metric = metric
        self.vectors = np.array([]).reshape(0, dimension)
        self.metadata = []
        self.index = {}
        
    def add(self, vector: np.ndarray, metadata: Optional[Dict[str, Any]] = None, id: Optional[str] = None):
        """Add a vector to the database."""
        if vector.shape[0] != self.dimension:
            raise ValueError(f"Vector dimension must be {self.dimension}")
        
        # Add vector
        self.vectors = np.vstack([self.vectors, vector.reshape(1, -1)])
        
        # Add metadata
        meta = metadata or {}
        if id:
            meta['id'] = id
        else:
            meta['id'] = str(len(self.metadata))
        self.metadata.append(meta)
        
        # Update index
        self.index[meta['id']] = len(self.metadata) - 1
        
        return meta['id']
    
    def add_batch(self, vectors: np.ndarray, metadata: Optional[List[Dict]] = None):
        """Add multiple vectors at once."""
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"Vector dimension must be {self.dimension}")
        
        ids = []
        for i, vec in enumerate(vectors):
            meta = metadata[i] if metadata and i < len(metadata) else {}
            vid = self.add(vec, meta)
            ids.append(vid)
        return ids
    
    def search(self, query: np.ndarray, k: int = 5) -> List[Tuple[str, float, Dict]]:
        """
        Search for k nearest vectors.
        
        Args:
            query: Query vector
            k: Number of results
            
        Returns:
            List of (id, score, metadata) tuples
        """
        if len(self.vectors) == 0:
            return []
        
        if query.shape[0] != self.dimension:
            raise ValueError(f"Query dimension must be {self.dimension}")
        
        # Compute similarities
        if self.metric == 'cosine':
            # Cosine similarity
            query_norm = query / (np.linalg.norm(query) + 1e-8)
            vectors_norm = self.vectors / (np.linalg.norm(self.vectors, axis=1, keepdims=True) + 1e-8)
            scores = np.dot(vectors_norm, query_norm)
        elif self.metric == 'euclidean':
            # Negative euclidean distance (higher is better)
            scores = -np.linalg.norm(self.vectors - query, axis=1)
        elif self.metric == 'dot':
            # Dot product
            scores = np.dot(self.vectors, query)
        else:
            raise ValueError(f"Unknown metric: {self.metric}")
        
        # Get top k
        k = min(k, len(scores))
        top_indices = np.argsort(scores)[-k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append((
                self.metadata[idx]['id'],
                float(scores[idx]),
                self.metadata[idx]
            ))
        
        return results
    
    def get(self, id: str) -> Optional[Tuple[np.ndarray, Dict]]:
        """Get vector by id."""
        if id not in self.index:
            return None
        idx = self.index[id]
        return self.vectors[idx], self.metadata[idx]
    
    def delete(self, id: str) -> bool:
        """Delete vector by id."""
        if id not in self.index:
            return False
        
        idx = self.index[id]
        
        # Remove from vectors
        self.vectors = np.delete(self.vectors, idx, axis=0)
        
        # Remove metadata
        del self.metadata[idx]
        
        # Rebuild index
        self.index = {meta['id']: i for i, meta in enumerate(self.metadata)}
        
        return True
    
    def save(self, filepath: str):
        """Save database to disk."""
        data = {
            'dimension': self.dimension,
            'metric': self.metric,
            'vectors': self.vectors.tolist(),
            'metadata': self.metadata
        }
        with open(filepath, 'w') as f:
            json.dump(data, f)
    
    @classmethod
    def load(cls, filepath: str) -> 'VectorDatabase':
        """Load database from disk."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        db = cls(data['dimension'], data['metric'])
        db.vectors = np.array(data['vectors'])
        db.metadata = data['metadata']
        db.index = {meta['id']: i for i, meta in enumerate(db.metadata)}
        
        return db
    
    def __len__(self):
        """Return number of vectors."""
        return len(self.vectors)
    
    def __repr__(self):
        return f"VectorDatabase(dimension={self.dimension}, size={len(self)}, metric={self.metric})"


if __name__ == "__main__":
    # Example usage
    print("Vector Database Example")
    
    # Create database
    db = VectorDatabase(dimension=128, metric='cosine')
    
    # Add vectors
    for i in range(10):
        vec = np.random.randn(128)
        db.add(vec, metadata={'label': f'vector_{i}'})
    
    print(f"Created database: {db}")
    
    # Search
    query = np.random.randn(128)
    results = db.search(query, k=3)
    
    print(f"\nTop 3 similar vectors:")
    for id, score, meta in results:
        print(f"  {id}: score={score:.4f}, {meta}")
    
    # Save and load
    db.save('test_db.json')
    print(f"\nSaved to test_db.json")
    
    loaded_db = VectorDatabase.load('test_db.json')
    print(f"Loaded: {loaded_db}")
