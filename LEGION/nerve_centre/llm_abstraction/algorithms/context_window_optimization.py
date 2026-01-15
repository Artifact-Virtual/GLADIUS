"""
Advanced Context Window Optimization Algorithms
"""
import re
import math
import logging
from typing import Any, Dict, List, Tuple, Optional
from collections import defaultdict, Counter
import hashlib
import json


logger = logging.getLogger(__name__)


class ContextOptimizer:
    """Advanced context window optimization with multiple strategies."""
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self.token_weights = self._initialize_token_weights()
        self.context_cache = {}
        
    def optimize_context_window(
        self,
        context: Dict[str, Any],
        prompt: str,
        strategy: str = "relevance"
    ) -> Dict[str, Any]:
        """Optimize context window using specified strategy."""
        strategies = {
            "relevance": self._optimize_by_relevance,
            "recency": self._optimize_by_recency,
            "importance": self._optimize_by_importance,
            "compression": self._optimize_by_compression,
            "hybrid": self._optimize_hybrid
        }
        
        if strategy not in strategies:
            logger.warning(f"Unknown strategy: {strategy}, using 'relevance'")
            strategy = "relevance"
        
        # Check cache
        cache_key = self._get_cache_key(context, prompt, strategy)
        if cache_key in self.context_cache:
            return self.context_cache[cache_key]
        
        # Apply optimization strategy
        optimized_context = strategies[strategy](context, prompt)
        
        # Validate token count
        optimized_context = self._enforce_token_limit(optimized_context)
        
        # Cache result
        self.context_cache[cache_key] = optimized_context
        
        logger.info(f"Context optimized using {strategy} strategy: "
                   f"{self._estimate_tokens(context)} -> "
                   f"{self._estimate_tokens(optimized_context)} tokens")
        
        return optimized_context
    
    def _optimize_by_relevance(
        self,
        context: Dict[str, Any],
        prompt: str
    ) -> Dict[str, Any]:
        """Optimize context by relevance to prompt."""
        prompt_keywords = self._extract_keywords(prompt)
        
        # Score each context item by relevance
        scored_items = []
        for key, value in context.items():
            relevance_score = self._calculate_relevance_score(
                str(value), prompt_keywords
            )
            token_count = self._estimate_tokens({key: value})
            
            # Relevance per token ratio
            efficiency = relevance_score / max(token_count, 1)
            scored_items.append((key, value, efficiency, token_count))
        
        # Sort by efficiency (relevance per token)
        scored_items.sort(key=lambda x: x[2], reverse=True)
        
        # Build optimized context
        optimized = {}
        total_tokens = 0
        
        for key, value, efficiency, token_count in scored_items:
            if total_tokens + token_count <= self.max_tokens:
                optimized[key] = value
                total_tokens += token_count
            else:
                # Try to include partial content
                remaining_tokens = self.max_tokens - total_tokens
                if remaining_tokens > 50:  # Minimum useful size
                    partial_value = self._truncate_content(
                        str(value), remaining_tokens
                    )
                    optimized[f"{key}_partial"] = partial_value
                break
        
        return optimized
    
    def _optimize_by_recency(
        self,
        context: Dict[str, Any],
        prompt: str
    ) -> Dict[str, Any]:
        """Optimize context by recency/temporal relevance."""
        # Look for temporal indicators
        temporal_items = []
        non_temporal_items = []
        
        for key, value in context.items():
            timestamp = self._extract_timestamp(key, value)
            if timestamp:
                temporal_items.append((key, value, timestamp))
            else:
                non_temporal_items.append((key, value))
        
        # Sort temporal items by recency
        temporal_items.sort(key=lambda x: x[2], reverse=True)
        
        # Build optimized context prioritizing recent items
        optimized = {}
        total_tokens = 0
        
        # Add recent temporal items first
        for key, value, timestamp in temporal_items:
            token_count = self._estimate_tokens({key: value})
            if total_tokens + token_count <= self.max_tokens:
                optimized[key] = value
                total_tokens += token_count
        
        # Add non-temporal items
        for key, value in non_temporal_items:
            token_count = self._estimate_tokens({key: value})
            if total_tokens + token_count <= self.max_tokens:
                optimized[key] = value
                total_tokens += token_count
        
        return optimized
    
    def _optimize_by_importance(
        self,
        context: Dict[str, Any],
        prompt: str
    ) -> Dict[str, Any]:
        """Optimize context by importance indicators."""
        importance_keywords = [
            "critical", "important", "urgent", "priority", "key",
            "essential", "required", "mandatory", "core", "primary"
        ]
        
        scored_items = []
        for key, value in context.items():
            # Calculate importance score
            content = f"{key} {str(value)}".lower()
            importance_score = sum(
                content.count(keyword) for keyword in importance_keywords
            )
            
            # Boost score for certain key patterns
            if any(pattern in key.lower() for pattern in [
                "system", "config", "requirement", "constraint"
            ]):
                importance_score += 5
            
            token_count = self._estimate_tokens({key: value})
            scored_items.append((key, value, importance_score, token_count))
        
        # Sort by importance score
        scored_items.sort(key=lambda x: x[2], reverse=True)
        
        # Build optimized context
        optimized = {}
        total_tokens = 0
        
        for key, value, importance, token_count in scored_items:
            if total_tokens + token_count <= self.max_tokens:
                optimized[key] = value
                total_tokens += token_count
        
        return optimized
    
    def _optimize_by_compression(
        self,
        context: Dict[str, Any],
        prompt: str
    ) -> Dict[str, Any]:
        """Optimize context by compressing content."""
        optimized = {}
        
        for key, value in context.items():
            compressed_value = self._compress_content(str(value))
            
            # Only compress if it saves significant tokens
            original_tokens = self._estimate_tokens({key: value})
            compressed_tokens = self._estimate_tokens({key: compressed_value})
            
            if compressed_tokens < original_tokens * 0.8:  # 20% savings
                optimized[key] = compressed_value
            else:
                optimized[key] = value
        
        # Apply token limit after compression
        return self._enforce_token_limit(optimized)
    
    def _optimize_hybrid(
        self,
        context: Dict[str, Any],
        prompt: str
    ) -> Dict[str, Any]:
        """Hybrid optimization combining multiple strategies."""
        # First pass: relevance-based filtering
        relevance_optimized = self._optimize_by_relevance(context, prompt)
        
        # Second pass: compression on selected items
        compressed = {}
        for key, value in relevance_optimized.items():
            compressed[key] = self._compress_content(str(value))
        
        # Third pass: importance boosting
        return self._optimize_by_importance(compressed, prompt)
    
    def _calculate_relevance_score(
        self,
        content: str,
        keywords: List[str]
    ) -> float:
        """Calculate relevance score based on keyword overlap."""
        content_words = set(content.lower().split())
        keyword_set = set(kw.lower() for kw in keywords)
        
        # Direct keyword matches
        direct_matches = len(content_words.intersection(keyword_set))
        
        # Semantic similarity (simplified)
        semantic_score = self._calculate_semantic_similarity(content, keywords)
        
        return direct_matches * 2 + semantic_score
    
    def _calculate_semantic_similarity(
        self,
        content: str,
        keywords: List[str]
    ) -> float:
        """Calculate semantic similarity (simplified implementation)."""
        # This is a simplified version - in practice, you'd use embeddings
        related_terms = {
            "analyze": ["analysis", "examine", "study", "review"],
            "data": ["information", "dataset", "records", "facts"],
            "generate": ["create", "produce", "make", "build"],
            "process": ["handle", "manage", "execute", "run"]
        }
        
        content_lower = content.lower()
        similarity_score = 0
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in related_terms:
                for related in related_terms[keyword_lower]:
                    if related in content_lower:
                        similarity_score += 0.5
        
        return similarity_score
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Remove common stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at",
            "to", "for", "of", "with", "by", "is", "are", "was", "were"
        }
        
        # Extract words (alphanumeric only)
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Filter stop words and short words
        keywords = [w for w in words if len(w) > 2 and w not in stop_words]
        
        # Return most frequent keywords
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(10)]
    
    def _extract_timestamp(
        self,
        key: str,
        value: Any
    ) -> Optional[float]:
        """Extract timestamp from key or value."""
        import time
        from datetime import datetime
        
        # Look for timestamp patterns in key
        if any(pattern in key.lower() for pattern in [
            "time", "date", "created", "updated", "modified"
        ]):
            try:
                # Try to parse as timestamp
                if isinstance(value, (int, float)):
                    return float(value)
                elif isinstance(value, str):
                    # Try common date formats
                    for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
                        try:
                            dt = datetime.strptime(value, fmt)
                            return dt.timestamp()
                        except ValueError:
                            continue
            except (ValueError, TypeError):
                pass
        
        return None
    
    def _compress_content(self, content: str) -> str:
        """Compress content by removing redundancy."""
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Remove repeated sentences
        sentences = content.split('.')
        unique_sentences = []
        seen_sentences = set()
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sentence not in seen_sentences:
                unique_sentences.append(sentence)
                seen_sentences.add(sentence)
        
        # Remove filler words in non-critical content
        filler_words = [
            "actually", "basically", "literally", "obviously",
            "essentially", "fundamentally", "generally"
        ]
        
        compressed = '. '.join(unique_sentences)
        for filler in filler_words:
            compressed = re.sub(rf'\b{filler}\b\s*', '', compressed, flags=re.IGNORECASE)
        
        return compressed
    
    def _truncate_content(self, content: str, max_tokens: int) -> str:
        """Truncate content to fit within token limit."""
        # Rough approximation: 1 token ≈ 4 characters
        max_chars = max_tokens * 4
        
        if len(content) <= max_chars:
            return content
        
        # Try to truncate at sentence boundary
        truncated = content[:max_chars]
        last_period = truncated.rfind('.')
        
        if last_period > max_chars * 0.8:  # If we can save most content
            return truncated[:last_period + 1]
        else:
            return truncated + "..."
    
    def _estimate_tokens(self, data: Any) -> int:
        """Estimate token count for data."""
        if isinstance(data, dict):
            content = json.dumps(data, default=str)
        else:
            content = str(data)
        
        # Rough approximation: 1 token ≈ 4 characters
        return len(content) // 4
    
    def _enforce_token_limit(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce maximum token limit on context."""
        total_tokens = self._estimate_tokens(context)
        
        if total_tokens <= self.max_tokens:
            return context
        
        # Remove items until under limit
        items = list(context.items())
        optimized = {}
        current_tokens = 0
        
        for key, value in items:
            item_tokens = self._estimate_tokens({key: value})
            if current_tokens + item_tokens <= self.max_tokens:
                optimized[key] = value
                current_tokens += item_tokens
            else:
                break
        
        return optimized
    
    def _get_cache_key(
        self,
        context: Dict[str, Any],
        prompt: str,
        strategy: str
    ) -> str:
        """Generate cache key for context optimization."""
        content = json.dumps({
            "context": context,
            "prompt": prompt,
            "strategy": strategy,
            "max_tokens": self.max_tokens
        }, sort_keys=True, default=str)
        
        return hashlib.md5(content.encode()).hexdigest()
    
    def _initialize_token_weights(self) -> Dict[str, float]:
        """Initialize weights for different types of tokens."""
        return {
            "keyword": 2.0,
            "entity": 1.5,
            "number": 1.2,
            "stopword": 0.5,
            "punctuation": 0.1
        }
    
    def clear_cache(self) -> None:
        """Clear the optimization cache."""
        self.context_cache.clear()
        logger.info("Context optimization cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            "cache_size": len(self.context_cache),
            "max_tokens": self.max_tokens
        }


# Convenience function for backward compatibility
def optimize_context_window(context: dict) -> dict:
    """Simple context optimization function."""
    optimizer = ContextOptimizer()
    return optimizer.optimize_context_window(context, "", "relevance")
