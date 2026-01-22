#!/usr/bin/env python3
"""Tests for vector database."""

import numpy as np
import os
from vector_db import VectorDatabase

def test_create():
    """Test database creation."""
    db = VectorDatabase(dimension=10, metric='cosine')
    assert db.dimension == 10
    assert len(db) == 0
    print("✓ Creation test passed")

def test_add():
    """Test adding vectors."""
    db = VectorDatabase(dimension=5)
    vec = np.array([1, 2, 3, 4, 5])
    id = db.add(vec, metadata={'label': 'test'})
    assert len(db) == 1
    print("✓ Add test passed")

def test_search():
    """Test similarity search."""
    db = VectorDatabase(dimension=3, metric='cosine')
    
    # Add test vectors
    db.add(np.array([1, 0, 0]), metadata={'name': 'x'})
    db.add(np.array([0, 1, 0]), metadata={'name': 'y'})
    db.add(np.array([0, 0, 1]), metadata={'name': 'z'})
    
    # Search for x-like vector
    results = db.search(np.array([0.9, 0.1, 0.0]), k=1)
    assert results[0][2]['name'] == 'x'
    print("✓ Search test passed")

def test_persistence():
    """Test save/load."""
    db = VectorDatabase(dimension=4)
    db.add(np.array([1, 2, 3, 4]))
    db.save('test_save.json')
    
    loaded = VectorDatabase.load('test_save.json')
    assert len(loaded) == 1
    assert loaded.dimension == 4
    
    os.remove('test_save.json')
    print("✓ Persistence test passed")

def test_batch():
    """Test batch operations."""
    db = VectorDatabase(dimension=2)
    vectors = np.array([[1, 2], [3, 4], [5, 6]])
    ids = db.add_batch(vectors)
    assert len(db) == 3
    assert len(ids) == 3
    print("✓ Batch test passed")

if __name__ == "__main__":
    test_create()
    test_add()
    test_search()
    test_persistence()
    test_batch()
    print("\nAll vector database tests passed!")
