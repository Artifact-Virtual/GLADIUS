"""
Simple text embedder using sentence piece or TF-IDF fallback.
"""

import hashlib
import numpy as np
from typing import List, Optional
from pathlib import Path


class Embedder:
    """
    Text embedder with multiple backend options.
    
    Priority:
    1. sentence-transformers (if available)
    2. TF-IDF vectorizer (always available)
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", dim: int = 384):
        self.model_name = model_name
        self.dim = dim
        self._model = None
        self._tfidf = None
        self._use_tfidf = False
        
        # Try sentence-transformers first
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(model_name)
            self.dim = self._model.get_sentence_embedding_dimension()
        except ImportError:
            # Fallback to TF-IDF
            self._use_tfidf = True
            self._init_tfidf()
    
    def _init_tfidf(self):
        """Initialize TF-IDF vectorizer."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.decomposition import TruncatedSVD
            self._tfidf = TfidfVectorizer(max_features=1000)
            self._svd = TruncatedSVD(n_components=self.dim)
            self._fitted = False
        except ImportError:
            # Ultimate fallback: hash-based embeddings
            self._tfidf = None
    
    def embed(self, text: str) -> np.ndarray:
        """Embed a single text."""
        return self.embed_batch([text])[0]
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Embed multiple texts."""
        if self._model is not None:
            return self._model.encode(texts, convert_to_numpy=True)
        elif self._tfidf is not None:
            return self._embed_tfidf(texts)
        else:
            return self._embed_hash(texts)
    
    def _embed_tfidf(self, texts: List[str]) -> np.ndarray:
        """TF-IDF + SVD embedding."""
        if not self._fitted:
            tfidf_matrix = self._tfidf.fit_transform(texts)
            if tfidf_matrix.shape[0] >= self.dim:
                self._svd.fit(tfidf_matrix)
            self._fitted = True
        
        tfidf_matrix = self._tfidf.transform(texts)
        if hasattr(self, '_svd') and tfidf_matrix.shape[0] >= self.dim:
            return self._svd.transform(tfidf_matrix).astype(np.float32)
        else:
            # Pad or truncate to dim
            result = np.zeros((len(texts), self.dim), dtype=np.float32)
            for i, row in enumerate(tfidf_matrix.toarray()):
                result[i, :min(len(row), self.dim)] = row[:self.dim]
            return result
    
    def _embed_hash(self, texts: List[str]) -> np.ndarray:
        """Hash-based embedding fallback."""
        embeddings = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, text in enumerate(texts):
            # Create deterministic hash-based embedding
            h = hashlib.sha256(text.encode()).digest()
            # Use hash bytes to seed random generator
            rng = np.random.default_rng(int.from_bytes(h[:8], 'big'))
            embeddings[i] = rng.standard_normal(self.dim).astype(np.float32)
            # Normalize
            norm = np.linalg.norm(embeddings[i])
            if norm > 0:
                embeddings[i] /= norm
        return embeddings
    
    @property
    def is_neural(self) -> bool:
        """Check if using neural embeddings."""
        return self._model is not None
