"""
Vector Store - HNSW-based semantic memory with SQLite fallback.

Provides:
- Fast similarity search via HNSW index
- Persistent storage via SQLite
- Document lifecycle management
- Hektor VDB compatible API
"""

import json
import sqlite3
import hnswlib
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging

from .embedder import Embedder


@dataclass
class Document:
    """A document stored in the vector database."""
    id: str
    content: str
    embedding: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    doc_type: str = "text"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "doc_type": self.doc_type,
            "created_at": self.created_at
        }


@dataclass
class SearchResult:
    """A search result from the vector store."""
    id: str
    score: float
    document: Optional[Document] = None
    
    def __repr__(self):
        return f"SearchResult(id={self.id}, score={self.score:.4f})"


class VectorStore:
    """
    HNSW-based vector store with SQLite persistence.
    
    Usage:
        store = VectorStore("./vectors")
        store.add_text("doc1", "Gold broke above resistance", {"type": "journal"})
        results = store.search("gold breakout", k=5)
    """
    
    def __init__(
        self,
        path: Union[str, Path],
        dim: int = 384,
        max_elements: int = 100000,
        ef_construction: int = 200,
        M: int = 16,
        embedder: Optional[Embedder] = None
    ):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        
        self.dim = dim
        self.max_elements = max_elements
        self.ef_construction = ef_construction
        self.M = M
        
        self.embedder = embedder or Embedder(dim=dim)
        self.dim = self.embedder.dim  # Use embedder's dimension
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize HNSW index
        self._init_hnsw()
        
        # Initialize SQLite for persistence
        self._init_sqlite()
        
        # Load existing data
        self._load()
    
    def _init_hnsw(self):
        """Initialize HNSW index."""
        self.index = hnswlib.Index(space='cosine', dim=self.dim)
        self.index.init_index(
            max_elements=self.max_elements,
            ef_construction=self.ef_construction,
            M=self.M
        )
        self.index.set_ef(50)  # Query time accuracy
        
        # ID mapping
        self._id_to_idx: Dict[str, int] = {}
        self._idx_to_id: Dict[int, str] = {}
        self._next_idx = 0
    
    def _init_sqlite(self):
        """Initialize SQLite database."""
        db_path = self.path / "cognition.db"
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                metadata TEXT,
                doc_type TEXT DEFAULT 'text',
                created_at TEXT,
                embedding BLOB
            )
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_doc_type ON documents(doc_type)
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON documents(created_at)
        """)
        
        self.conn.commit()
    
    def _load(self):
        """Load existing documents from SQLite into HNSW."""
        cursor = self.conn.execute(
            "SELECT id, embedding FROM documents WHERE embedding IS NOT NULL"
        )
        
        embeddings = []
        ids = []
        
        for row in cursor:
            embedding = np.frombuffer(row['embedding'], dtype=np.float32)
            if len(embedding) == self.dim:
                embeddings.append(embedding)
                ids.append(row['id'])
        
        if embeddings:
            # Resize index if needed
            if len(embeddings) > self.max_elements:
                self.index.resize_index(len(embeddings) + 10000)
            
            embeddings_array = np.vstack(embeddings)
            for i, (doc_id, emb) in enumerate(zip(ids, embeddings_array)):
                idx = self._next_idx
                self.index.add_items(emb.reshape(1, -1), np.array([idx]))
                self._id_to_idx[doc_id] = idx
                self._idx_to_id[idx] = doc_id
                self._next_idx += 1
            
            self.logger.info(f"Loaded {len(embeddings)} documents into HNSW index")
    
    def add_text(
        self,
        doc_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_type: str = "text"
    ) -> str:
        """Add a text document to the store."""
        metadata = metadata or {}
        
        # Generate embedding
        embedding = self.embedder.embed(content)
        
        # Create document
        doc = Document(
            id=doc_id,
            content=content,
            embedding=embedding,
            metadata=metadata,
            doc_type=doc_type
        )
        
        # Add to HNSW
        if doc_id in self._id_to_idx:
            # Update existing
            idx = self._id_to_idx[doc_id]
        else:
            # New document
            idx = self._next_idx
            self._next_idx += 1
            self._id_to_idx[doc_id] = idx
            self._idx_to_id[idx] = doc_id
        
        # Resize if needed
        if idx >= self.index.get_max_elements():
            self.index.resize_index(idx + 10000)
        
        self.index.add_items(embedding.reshape(1, -1), np.array([idx]))
        
        # Persist to SQLite
        self.conn.execute("""
            INSERT OR REPLACE INTO documents (id, content, metadata, doc_type, created_at, embedding)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            doc_id,
            content,
            json.dumps(metadata),
            doc_type,
            doc.created_at,
            embedding.tobytes()
        ))
        self.conn.commit()
        
        return doc_id
    
    def search(
        self,
        query: str,
        k: int = 10,
        doc_type: Optional[str] = None,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """
        Search for similar documents.
        
        Args:
            query: Search query text
            k: Number of results to return
            doc_type: Filter by document type
            min_score: Minimum similarity score (0-1)
        
        Returns:
            List of SearchResult objects
        """
        if self._next_idx == 0:
            return []
        
        # Embed query
        query_embedding = self.embedder.embed(query)
        
        # Search HNSW
        k_search = min(k * 2, self._next_idx)  # Over-fetch for filtering
        labels, distances = self.index.knn_query(
            query_embedding.reshape(1, -1),
            k=k_search
        )
        
        results = []
        for idx, dist in zip(labels[0], distances[0]):
            if idx not in self._idx_to_id:
                continue
            
            doc_id = self._idx_to_id[idx]
            
            # Convert distance to similarity score (cosine distance -> similarity)
            score = 1.0 - dist
            
            if score < min_score:
                continue
            
            # Load document from SQLite
            doc = self.get_document(doc_id)
            
            if doc_type and doc and doc.doc_type != doc_type:
                continue
            
            results.append(SearchResult(
                id=doc_id,
                score=score,
                document=doc
            ))
            
            if len(results) >= k:
                break
        
        return results
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID."""
        cursor = self.conn.execute(
            "SELECT * FROM documents WHERE id = ?",
            (doc_id,)
        )
        row = cursor.fetchone()
        
        if row:
            return Document(
                id=row['id'],
                content=row['content'],
                metadata=json.loads(row['metadata']) if row['metadata'] else {},
                doc_type=row['doc_type'],
                created_at=row['created_at']
            )
        return None
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document."""
        if doc_id not in self._id_to_idx:
            return False
        
        # Note: HNSW doesn't support deletion, but we can mark as deleted
        # For now, just remove from SQLite
        self.conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        self.conn.commit()
        
        # Remove from mapping (index entry remains but is orphaned)
        idx = self._id_to_idx.pop(doc_id, None)
        if idx is not None:
            self._idx_to_id.pop(idx, None)
        
        return True
    
    def count(self, doc_type: Optional[str] = None) -> int:
        """Count documents."""
        if doc_type:
            cursor = self.conn.execute(
                "SELECT COUNT(*) FROM documents WHERE doc_type = ?",
                (doc_type,)
            )
        else:
            cursor = self.conn.execute("SELECT COUNT(*) FROM documents")
        return cursor.fetchone()[0]
    
    def list_documents(
        self,
        doc_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Document]:
        """List documents with optional filtering."""
        if doc_type:
            cursor = self.conn.execute(
                "SELECT * FROM documents WHERE doc_type = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (doc_type, limit, offset)
            )
        else:
            cursor = self.conn.execute(
                "SELECT * FROM documents ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset)
            )
        
        return [
            Document(
                id=row['id'],
                content=row['content'],
                metadata=json.loads(row['metadata']) if row['metadata'] else {},
                doc_type=row['doc_type'],
                created_at=row['created_at']
            )
            for row in cursor
        ]
    
    def stats(self) -> Dict[str, Any]:
        """Get store statistics."""
        cursor = self.conn.execute(
            "SELECT doc_type, COUNT(*) as count FROM documents GROUP BY doc_type"
        )
        type_counts = {row['doc_type']: row['count'] for row in cursor}
        
        return {
            "total_documents": self.count(),
            "indexed_documents": self._next_idx,
            "dimension": self.dim,
            "max_elements": self.max_elements,
            "by_type": type_counts,
            "embedder_neural": self.embedder.is_neural
        }
    
    def close(self):
        """Close the store."""
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
