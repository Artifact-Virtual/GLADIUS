"""
Gladius Native Tool Router Model

A lightweight, fast neural network for tool routing that achieves
near-perfect accuracy through progressive training on pattern data.

This model learns:
1. Tool selection from natural language queries
2. Parameter extraction patterns
3. Context-aware routing decisions

Architecture:
- TF-IDF vectorization (vocabulary from all tool patterns)
- MLP Classifier with dropout regularization
- Confidence-based routing with fallback to pattern matching
"""

import json
import pickle
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    """Represents a tool call prediction."""
    tool: str
    args: Dict[str, Any]
    confidence: float
    method: str  # 'neural', 'pattern', 'fallback'


@dataclass
class TrainingMetrics:
    """Training metrics for a model version."""
    version: int
    accuracy: float
    examples: int
    tools: int
    train_time_s: float
    timestamp: str


class GladiusToolRouter:
    """
    Native Gladius tool routing model.
    
    Uses TF-IDF + MLP for fast, accurate tool selection.
    Falls back to pattern matching when confidence is low.
    """
    
    def __init__(
        self,
        model_dir: str = "models",
        confidence_threshold: float = 0.7,
        max_features: int = 5000,
        hidden_layers: Tuple[int, ...] = (256, 128, 64),
    ):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.confidence_threshold = confidence_threshold
        self.max_features = max_features
        self.hidden_layers = hidden_layers
        
        # Model components
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.classifier: Optional[MLPClassifier] = None
        self.label_encoder: Optional[LabelEncoder] = None
        
        # Pattern fallback
        self.patterns: Dict[str, List[Dict]] = {}
        self.arg_extractors: Dict[str, Dict] = {}
        
        # Metrics
        self.version = 0
        self.metrics: List[TrainingMetrics] = []
        self.is_trained = False
        
        # Load existing model if available
        self._load_model()
    
    def _load_model(self) -> bool:
        """Load existing model from disk."""
        model_path = self.model_dir / "gladius-router.pkl"
        if model_path.exists():
            try:
                with open(model_path, 'rb') as f:
                    data = pickle.load(f)
                self.vectorizer = data.get('vectorizer')
                self.classifier = data.get('classifier')
                self.label_encoder = data.get('label_encoder')
                self.patterns = data.get('patterns', {})
                self.arg_extractors = data.get('arg_extractors', {})
                self.version = data.get('version', 0)
                self.metrics = data.get('metrics', [])
                self.is_trained = True
                logger.info(f"Loaded Gladius router v{self.version}")
                return True
            except Exception as e:
                logger.warning(f"Failed to load model: {e}")
        return False
    
    def _save_model(self):
        """Save model to disk."""
        model_path = self.model_dir / "gladius-router.pkl"
        data = {
            'vectorizer': self.vectorizer,
            'classifier': self.classifier,
            'label_encoder': self.label_encoder,
            'patterns': self.patterns,
            'arg_extractors': self.arg_extractors,
            'version': self.version,
            'metrics': self.metrics,
        }
        with open(model_path, 'wb') as f:
            pickle.dump(data, f)
        logger.info(f"Saved Gladius router v{self.version}")
    
    def load_patterns(self, pattern_files: List[str] = None) -> int:
        """Load training patterns from pattern JSON files."""
        if pattern_files is None:
            # Auto-discover pattern files
            pattern_files = list(self.model_dir.glob("*.patterns.json"))
        
        total_examples = 0
        for pf in pattern_files:
            try:
                with open(pf) as f:
                    data = json.load(f)
                patterns = data.get('patterns', {})
                for tool, examples in patterns.items():
                    if tool not in self.patterns:
                        self.patterns[tool] = []
                    for ex in examples:
                        # Avoid duplicates
                        if ex not in self.patterns[tool]:
                            self.patterns[tool].append(ex)
                            total_examples += 1
            except Exception as e:
                logger.warning(f"Failed to load {pf}: {e}")
        
        logger.info(f"Loaded {total_examples} examples for {len(self.patterns)} tools")
        return total_examples
    
    def _build_arg_extractors(self):
        """Build regex patterns for argument extraction."""
        # Common argument patterns
        self.arg_extractors = {
            'query': [
                r'(?:search|find|look for|get|retrieve)\s+(?:for\s+)?["\']?(.+?)["\']?$',
                r'(?:about|regarding|related to)\s+["\']?(.+?)["\']?$',
            ],
            'path': [
                r'(?:file|directory|folder|path)\s+["\']?([^\s"\']+)["\']?',
                r'in\s+["\']?([^\s"\']+)["\']?',
            ],
            'k': [
                r'(?:top|first|last)\s+(\d+)',
                r'(\d+)\s+(?:results|items|entries)',
            ],
            'key': [
                r'(?:remember|store|save)\s+(?:as\s+)?["\']?(\w+)["\']?',
                r'key\s*[=:]\s*["\']?(\w+)["\']?',
            ],
            'value': [
                r'(?:that|value)\s+["\']?(.+?)["\']?$',
            ],
            'content': [
                r'content\s*[=:]\s*["\']?(.+?)["\']?$',
            ],
            'last_n': [
                r'(?:last|recent)\s+(\d+)',
            ],
        }
    
    def train(
        self,
        pattern_files: List[str] = None,
        epochs: int = 100,
        early_stopping: bool = True,
    ) -> TrainingMetrics:
        """
        Train the neural network on pattern data.
        
        Uses progressive training with early stopping when accuracy plateaus.
        """
        import time
        start_time = time.time()
        
        # Load patterns
        if not self.patterns:
            self.load_patterns(pattern_files)
        
        if not self.patterns:
            raise ValueError("No patterns loaded for training")
        
        # Prepare training data
        X_texts = []
        y_labels = []
        
        for tool, examples in self.patterns.items():
            for ex in examples:
                query = ex.get('query', '')
                if query:
                    X_texts.append(query)
                    y_labels.append(tool)
        
        if len(X_texts) < 10:
            raise ValueError(f"Insufficient training data: {len(X_texts)} examples")
        
        # Encode labels
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y_labels)
        
        # Vectorize text
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=(1, 3),
            stop_words='english',
            sublinear_tf=True,
        )
        X_vectors = self.vectorizer.fit_transform(X_texts)
        
        # Split for validation
        X_train, X_val, y_train, y_val = train_test_split(
            X_vectors, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Train classifier
        self.classifier = MLPClassifier(
            hidden_layer_sizes=self.hidden_layers,
            activation='relu',
            solver='adam',
            alpha=0.0001,
            batch_size='auto',
            learning_rate='adaptive',
            learning_rate_init=0.001,
            max_iter=epochs,
            early_stopping=early_stopping,
            validation_fraction=0.1,
            n_iter_no_change=10,
            random_state=42,
        )
        
        self.classifier.fit(X_train, y_train)
        
        # Evaluate
        train_acc = self.classifier.score(X_train, y_train) * 100
        val_acc = self.classifier.score(X_val, y_val) * 100
        
        # Build arg extractors
        self._build_arg_extractors()
        
        # Update version
        self.version += 1
        self.is_trained = True
        
        elapsed = time.time() - start_time
        
        metrics = TrainingMetrics(
            version=self.version,
            accuracy=val_acc,
            examples=len(X_texts),
            tools=len(self.patterns),
            train_time_s=elapsed,
            timestamp=datetime.now().isoformat(),
        )
        self.metrics.append(metrics)
        
        # Save model
        self._save_model()
        
        logger.info(f"Training complete: v{self.version}, acc={val_acc:.1f}%, time={elapsed:.1f}s")
        return metrics
    
    def _extract_args(self, query: str, tool: str) -> Dict[str, Any]:
        """Extract arguments from query using regex patterns."""
        args = {}
        query_lower = query.lower()
        
        # Tool-specific default args
        tool_defaults = {
            'search': {'k': 5},
            'hybrid_search': {'k': 5},
            'recall': {'k': 3},
            'get_history': {'last_n': 10},
            'get_context': {'k': 3},
        }
        
        # Apply defaults
        if tool in tool_defaults:
            args.update(tool_defaults[tool])
        
        # Extract using patterns
        for arg_name, patterns in self.arg_extractors.items():
            for pattern in patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    # Convert numeric values
                    if arg_name in ('k', 'last_n'):
                        try:
                            value = int(value)
                        except ValueError:
                            continue
                    args[arg_name] = value
                    break
        
        # Fallback: use query as search query if no specific query extracted
        if 'query' not in args and tool in ('search', 'hybrid_search', 'recall', 'get_context'):
            # Extract the main query content
            args['query'] = query
        
        return args
    
    def _pattern_match(self, query: str) -> Optional[ToolCall]:
        """Fall back to pattern matching when neural confidence is low."""
        query_lower = query.lower()
        best_match = None
        best_score = 0
        
        for tool, examples in self.patterns.items():
            for ex in examples:
                pattern_query = ex.get('query', '').lower()
                if not pattern_query:
                    continue
                
                # Simple keyword overlap score
                query_words = set(query_lower.split())
                pattern_words = set(pattern_query.split())
                overlap = len(query_words & pattern_words)
                score = overlap / max(len(query_words), 1)
                
                if score > best_score:
                    best_score = score
                    best_match = (tool, ex.get('args', {}))
        
        if best_match and best_score > 0.3:
            tool, template_args = best_match
            # Merge template args with extracted args
            args = dict(template_args)
            args.update(self._extract_args(query, tool))
            return ToolCall(
                tool=tool,
                args=args,
                confidence=best_score,
                method='pattern'
            )
        
        return None
    
    def route(self, query: str) -> ToolCall:
        """
        Route a query to the appropriate tool.
        
        Uses neural network prediction with pattern fallback.
        """
        if not self.is_trained:
            # Fallback to pattern matching only
            result = self._pattern_match(query)
            if result:
                return result
            return ToolCall(
                tool='search',
                args={'query': query, 'k': 5},
                confidence=0.1,
                method='fallback'
            )
        
        # Neural prediction
        X = self.vectorizer.transform([query])
        proba = self.classifier.predict_proba(X)[0]
        pred_idx = np.argmax(proba)
        confidence = proba[pred_idx]
        tool = self.label_encoder.inverse_transform([pred_idx])[0]
        
        if confidence >= self.confidence_threshold:
            args = self._extract_args(query, tool)
            return ToolCall(
                tool=tool,
                args=args,
                confidence=float(confidence),
                method='neural'
            )
        
        # Low confidence - try pattern matching
        pattern_result = self._pattern_match(query)
        if pattern_result and pattern_result.confidence > confidence:
            return pattern_result
        
        # Return neural result even with low confidence
        args = self._extract_args(query, tool)
        return ToolCall(
            tool=tool,
            args=args,
            confidence=float(confidence),
            method='neural'
        )
    
    def benchmark(self, test_queries: List[Dict] = None) -> Dict[str, Any]:
        """
        Benchmark the model on test queries.
        
        Returns accuracy, latency, and per-tool metrics.
        """
        import time
        
        if test_queries is None:
            # Generate test queries from patterns
            test_queries = []
            for tool, examples in self.patterns.items():
                for ex in examples:
                    test_queries.append({
                        'query': ex.get('query', ''),
                        'expected_tool': tool,
                    })
        
        if not test_queries:
            return {'error': 'No test queries'}
        
        correct = 0
        total = 0
        latencies = []
        per_tool = {}
        
        for tq in test_queries:
            query = tq.get('query', '')
            expected = tq.get('expected_tool', '')
            if not query or not expected:
                continue
            
            start = time.perf_counter()
            result = self.route(query)
            elapsed = (time.perf_counter() - start) * 1000  # ms
            
            latencies.append(elapsed)
            total += 1
            
            is_correct = result.tool == expected
            if is_correct:
                correct += 1
            
            # Per-tool stats
            if expected not in per_tool:
                per_tool[expected] = {'correct': 0, 'total': 0}
            per_tool[expected]['total'] += 1
            if is_correct:
                per_tool[expected]['correct'] += 1
        
        return {
            'accuracy': (correct / total * 100) if total > 0 else 0,
            'total': total,
            'correct': correct,
            'avg_latency_ms': np.mean(latencies) if latencies else 0,
            'p99_latency_ms': np.percentile(latencies, 99) if latencies else 0,
            'per_tool': {
                k: {
                    'accuracy': (v['correct'] / v['total'] * 100) if v['total'] > 0 else 0,
                    **v
                }
                for k, v in per_tool.items()
            }
        }
    
    def export_onnx(self, output_path: str = None) -> str:
        """Export model to ONNX format for cross-platform deployment."""
        # Note: sklearn MLP doesn't directly support ONNX
        # This is a placeholder for future enhancement
        raise NotImplementedError("ONNX export requires skl2onnx")
    
    def stats(self) -> Dict[str, Any]:
        """Get model statistics."""
        return {
            'version': self.version,
            'is_trained': self.is_trained,
            'tools': len(self.patterns),
            'total_examples': sum(len(ex) for ex in self.patterns.values()),
            'confidence_threshold': self.confidence_threshold,
            'hidden_layers': self.hidden_layers,
            'latest_metrics': asdict(self.metrics[-1]) if self.metrics else None,
        }


# Singleton instance
_router_instance: Optional[GladiusToolRouter] = None


def get_gladius_router(model_dir: str = None) -> GladiusToolRouter:
    """Get or create the Gladius tool router."""
    global _router_instance
    if _router_instance is None:
        if model_dir is None:
            model_dir = str(Path(__file__).parent.parent.parent / "models")
        _router_instance = GladiusToolRouter(model_dir=model_dir)
    return _router_instance


def route_query(query: str, model_dir: str = None) -> ToolCall:
    """Route a query to a tool using the Gladius router."""
    router = get_gladius_router(model_dir)
    return router.route(query)
