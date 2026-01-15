"""
Advanced Probabilistic Output Ranking Algorithms
"""
import math
import logging
import re
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter
from dataclasses import dataclass
import statistics


logger = logging.getLogger(__name__)


@dataclass
class OutputMetrics:
    """Metrics for evaluating LLM output quality."""
    coherence_score: float
    relevance_score: float
    completeness_score: float
    accuracy_score: float
    fluency_score: float
    confidence_score: float
    combined_score: float


class ProbabilisticRanker:
    """Advanced probabilistic ranking system for LLM outputs."""
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or {
            'coherence': 0.20,
            'relevance': 0.25,
            'completeness': 0.20,
            'accuracy': 0.15,
            'fluency': 0.10,
            'confidence': 0.10
        }
        
        # Ensure weights sum to 1.0
        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > 0.01:
            for key in self.weights:
                self.weights[key] /= total_weight
    
    def rank_outputs(
        self,
        outputs: List[str],
        query: str = "",
        context: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, OutputMetrics]]:
        """Rank outputs using probabilistic scoring."""
        if not outputs:
            return []
        
        # Calculate metrics for each output
        scored_outputs = []
        for output in outputs:
            metrics = self._calculate_output_metrics(output, query, context)
            scored_outputs.append((output, metrics))
        
        # Sort by combined score (descending)
        scored_outputs.sort(key=lambda x: x[1].combined_score, reverse=True)
        
        logger.info(f"Ranked {len(outputs)} outputs")
        return scored_outputs
    
    def _calculate_output_metrics(
        self,
        output: str,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> OutputMetrics:
        """Calculate comprehensive metrics for output quality."""
        coherence = self._measure_coherence(output)
        relevance = self._measure_relevance(output, query)
        completeness = self._measure_completeness(output, query)
        accuracy = self._measure_accuracy(output, context)
        fluency = self._measure_fluency(output)
        confidence = self._measure_confidence(output)
        
        # Calculate weighted combined score
        combined = (
            coherence * self.weights['coherence'] +
            relevance * self.weights['relevance'] +
            completeness * self.weights['completeness'] +
            accuracy * self.weights['accuracy'] +
            fluency * self.weights['fluency'] +
            confidence * self.weights['confidence']
        )
        
        return OutputMetrics(
            coherence_score=coherence,
            relevance_score=relevance,
            completeness_score=completeness,
            accuracy_score=accuracy,
            fluency_score=fluency,
            confidence_score=confidence,
            combined_score=combined
        )
    
    def _measure_coherence(self, output: str) -> float:
        """Measure logical coherence and structure."""
        if not output.strip():
            return 0.0
        
        score = 0.0
        
        # Sentence structure
        sentences = self._split_sentences(output)
        if len(sentences) > 0:
            score += 0.2
        
        # Proper punctuation
        if re.search(r'[.!?]$', output.strip()):
            score += 0.15
        
        # Logical connectors
        connectors = [
            'therefore', 'however', 'moreover', 'furthermore',
            'consequently', 'additionally', 'similarly', 'in contrast'
        ]
        connector_count = sum(
            1 for connector in connectors
            if connector in output.lower()
        )
        score += min(connector_count * 0.1, 0.3)
        
        # Paragraph structure
        paragraphs = output.split('\n\n')
        if len(paragraphs) > 1:
            score += 0.1
        
        # Avoid repetition
        words = output.lower().split()
        unique_ratio = len(set(words)) / max(len(words), 1)
        score += unique_ratio * 0.25
        
        return min(score, 1.0)
    
    def _measure_relevance(self, output: str, query: str) -> float:
        """Measure relevance to the original query."""
        if not query.strip():
            return 0.5  # Neutral score when no query
        
        query_words = set(self._extract_keywords(query))
        output_words = set(self._extract_keywords(output))
        
        if not query_words:
            return 0.5
        
        # Keyword overlap
        overlap = len(query_words.intersection(output_words))
        keyword_score = overlap / len(query_words)
        
        # Topic coherence (simplified)
        topic_score = self._calculate_topic_coherence(output, query)
        
        # Query answering indicators
        answer_indicators = [
            'answer', 'solution', 'result', 'conclusion',
            'therefore', 'because', 'due to'
        ]
        answer_score = min(
            sum(1 for indicator in answer_indicators
                if indicator in output.lower()) * 0.1,
            0.3
        )
        
        return min(keyword_score * 0.5 + topic_score * 0.3 + answer_score, 1.0)
    
    def _measure_completeness(self, output: str, query: str) -> float:
        """Measure completeness of the response."""
        if not output.strip():
            return 0.0
        
        score = 0.0
        
        # Length appropriateness
        word_count = len(output.split())
        if 20 <= word_count <= 500:
            score += 0.3
        elif 10 <= word_count < 20 or 500 < word_count <= 1000:
            score += 0.2
        elif word_count > 10:
            score += 0.1
        
        # Structure completeness
        has_introduction = self._has_introduction(output)
        has_body = self._has_body(output)
        has_conclusion = self._has_conclusion(output)
        
        structure_score = (has_introduction + has_body + has_conclusion) / 3
        score += structure_score * 0.4
        
        # Addresses query aspects
        if query:
            query_aspects = self._extract_query_aspects(query)
            addressed_aspects = sum(
                1 for aspect in query_aspects
                if aspect.lower() in output.lower()
            )
            aspect_score = addressed_aspects / max(len(query_aspects), 1)
            score += aspect_score * 0.3
        
        return min(score, 1.0)
    
    def _measure_accuracy(
        self,
        output: str,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Measure factual accuracy (heuristic-based)."""
        score = 0.5  # Start with neutral score
        
        # Confidence indicators
        confident_phrases = [
            'according to', 'research shows', 'studies indicate',
            'data suggests', 'evidence points', 'established fact'
        ]
        confidence_boost = min(
            sum(1 for phrase in confident_phrases
                if phrase in output.lower()) * 0.1,
            0.2
        )
        score += confidence_boost
        
        # Uncertainty indicators (negative)
        uncertain_phrases = [
            'i think', 'maybe', 'possibly', 'might be',
            'not sure', 'unclear', 'uncertain'
        ]
        uncertainty_penalty = min(
            sum(1 for phrase in uncertain_phrases
                if phrase in output.lower()) * 0.1,
            0.3
        )
        score -= uncertainty_penalty
        
        # Contradiction detection
        if self._has_contradictions(output):
            score -= 0.2
        
        # Context consistency
        if context:
            consistency_score = self._check_context_consistency(output, context)
            score += consistency_score * 0.3
        
        return max(min(score, 1.0), 0.0)
    
    def _measure_fluency(self, output: str) -> float:
        """Measure language fluency and readability."""
        if not output.strip():
            return 0.0
        
        score = 0.0
        
        # Grammar indicators (simplified)
        sentences = self._split_sentences(output)
        
        # Sentence length variation
        if sentences:
            lengths = [len(sentence.split()) for sentence in sentences]
            if len(lengths) > 1:
                variation = statistics.stdev(lengths) / max(statistics.mean(lengths), 1)
                score += min(variation * 0.5, 0.2)
        
        # Proper capitalization
        if re.search(r'^[A-Z]', output.strip()):
            score += 0.1
        
        # Word variety
        words = output.lower().split()
        if words:
            unique_ratio = len(set(words)) / len(words)
            score += unique_ratio * 0.3
        
        # Readability (simplified Flesch score approximation)
        readability_score = self._calculate_readability(output)
        score += readability_score * 0.4
        
        return min(score, 1.0)
    
    def _measure_confidence(self, output: str) -> float:
        """Measure confidence level of the output."""
        confidence_indicators = {
            'high': ['definitely', 'certainly', 'clearly', 'obviously', 'undoubtedly'],
            'medium': ['likely', 'probably', 'generally', 'typically', 'usually'],
            'low': ['possibly', 'maybe', 'might', 'could be', 'perhaps'],
            'very_low': ['not sure', 'uncertain', 'unclear', 'hard to say']
        }
        
        scores = {'high': 1.0, 'medium': 0.7, 'low': 0.4, 'very_low': 0.1}
        
        output_lower = output.lower()
        confidence_score = 0.5  # Default neutral confidence
        
        for level, indicators in confidence_indicators.items():
            for indicator in indicators:
                if indicator in output_lower:
                    confidence_score = max(confidence_score, scores[level])
                    break
        
        # Adjust based on output characteristics
        if len(output.split()) < 10:
            confidence_score *= 0.8  # Short answers less confident
        
        if re.search(r'[.!]{2,}', output):
            confidence_score *= 1.1  # Emphatic punctuation
        
        return min(confidence_score, 1.0)
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
            'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'
        }
        
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return [w for w in words if len(w) > 2 and w not in stop_words]
    
    def _calculate_topic_coherence(self, output: str, query: str) -> float:
        """Calculate topic coherence between output and query."""
        # Simplified topic coherence using word co-occurrence
        output_words = Counter(self._extract_keywords(output))
        query_words = Counter(self._extract_keywords(query))
        
        if not query_words:
            return 0.5
        
        # Calculate overlap strength
        total_overlap = 0
        for word, query_count in query_words.items():
            output_count = output_words.get(word, 0)
            total_overlap += min(query_count, output_count)
        
        return min(total_overlap / sum(query_words.values()), 1.0)
    
    def _has_introduction(self, output: str) -> bool:
        """Check if output has an introduction."""
        first_sentence = self._split_sentences(output)[0] if self._split_sentences(output) else ""
        intro_indicators = [
            'introduction', 'overview', 'begin', 'start', 'first',
            'initially', 'to understand', 'let me explain'
        ]
        return any(indicator in first_sentence.lower() for indicator in intro_indicators)
    
    def _has_body(self, output: str) -> bool:
        """Check if output has substantial body content."""
        sentences = self._split_sentences(output)
        return len(sentences) > 2  # More than intro and conclusion
    
    def _has_conclusion(self, output: str) -> bool:
        """Check if output has a conclusion."""
        last_sentence = self._split_sentences(output)[-1] if self._split_sentences(output) else ""
        conclusion_indicators = [
            'conclusion', 'summary', 'finally', 'in summary',
            'to conclude', 'therefore', 'thus', 'overall'
        ]
        return any(indicator in last_sentence.lower() for indicator in conclusion_indicators)
    
    def _extract_query_aspects(self, query: str) -> List[str]:
        """Extract key aspects from the query."""
        # Look for question words and key topics
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which']
        aspects = []
        
        query_lower = query.lower()
        for qword in question_words:
            if qword in query_lower:
                aspects.append(qword)
        
        # Add key nouns/topics
        keywords = self._extract_keywords(query)
        aspects.extend(keywords[:5])  # Top 5 keywords
        
        return aspects
    
    def _has_contradictions(self, output: str) -> bool:
        """Detect potential contradictions in output."""
        # Simple contradiction detection
        contradiction_patterns = [
            (r'\bnot\b.*\bis\b', r'\bis\b'),
            (r'\bno\b.*\byes\b', r'\byes\b.*\bno\b'),
            (r'\btrue\b.*\bfalse\b', r'\bfalse\b.*\btrue\b'),
        ]
        
        output_lower = output.lower()
        for pattern1, pattern2 in contradiction_patterns:
            if re.search(pattern1, output_lower) and re.search(pattern2, output_lower):
                return True
        
        return False
    
    def _check_context_consistency(
        self,
        output: str,
        context: Dict[str, Any]
    ) -> float:
        """Check consistency with provided context."""
        context_text = " ".join(str(v) for v in context.values()).lower()
        output_lower = output.lower()
        
        # Simple consistency check based on common keywords
        context_keywords = set(self._extract_keywords(context_text))
        output_keywords = set(self._extract_keywords(output_lower))
        
        if not context_keywords:
            return 0.5
        
        overlap = len(context_keywords.intersection(output_keywords))
        return overlap / len(context_keywords)
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score (simplified Flesch approximation)."""
        sentences = self._split_sentences(text)
        words = text.split()
        
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables = self._estimate_syllables(text) / len(words)
        
        # Simplified Flesch-like score
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
        
        # Normalize to 0-1 range
        return max(min(score / 100, 1.0), 0.0)
    
    def _estimate_syllables(self, text: str) -> int:
        """Estimate syllable count (simplified)."""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        total_syllables = 0
        
        for word in words:
            syllables = len(re.findall(r'[aeiou]', word))
            if word.endswith('e'):
                syllables -= 1
            total_syllables += max(syllables, 1)  # At least 1 syllable per word
        
        return total_syllables


# Convenience function for backward compatibility
def rank_outputs(outputs: List[str]) -> List[str]:
    """Simple ranking function returning sorted outputs."""
    ranker = ProbabilisticRanker()
    ranked = ranker.rank_outputs(outputs)
    return [output for output, metrics in ranked]


# Advanced ranking with custom weights
def rank_outputs_weighted(
    outputs: List[str],
    weights: Dict[str, float],
    query: str = "",
    context: Optional[Dict[str, Any]] = None
) -> List[Tuple[str, OutputMetrics]]:
    """Rank outputs with custom weights."""
    ranker = ProbabilisticRanker(weights)
    return ranker.rank_outputs(outputs, query, context)
