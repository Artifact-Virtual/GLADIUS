"""
Syndicate Cognition Integration - Ingest reports into vector memory.

This module connects Syndicate's output (journals, catalysts, analysis)
to the cognition engine for semantic retrieval and learning.

Supports:
- Hektor VDB (native C++ SIMD-optimized) - preferred
- hnswlib + SQLite (Python fallback) - always available
"""

import os
import re
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Try Hektor first, fallback to hnswlib
try:
    from .hektor_store import HektorVectorStore, HEKTOR_AVAILABLE, get_vector_store
except ImportError:
    HEKTOR_AVAILABLE = False
    get_vector_store = None

from .vector_store import VectorStore, Document, SearchResult


class SyndicateCognition:
    """
    Integrates Syndicate reports with the cognition engine.
    
    Provides:
    - Automatic ingestion of reports into vector store
    - Semantic search across all historical data
    - Hybrid search (vector + BM25) when using Hektor
    - Context retrieval for AI analysis
    - Learning from past predictions
    """
    
    # Document type mappings
    DOC_TYPES = {
        'journal': 'journal',
        'catalyst': 'catalyst',
        'premarket': 'premarket',
        'weekly': 'weekly',
        'monthly': 'monthly',
        'yearly': 'yearly',
        'institutional': 'institutional',
        'economic': 'economic',
        'analysis': 'analysis'
    }
    
    def __init__(
        self,
        data_dir: str = "./data",
        output_dir: str = "./output",
        prefer_hektor: bool = True,
        logger: Optional[logging.Logger] = None
    ):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.logger = logger or logging.getLogger(__name__)
        self.using_hektor = False
        
        # Initialize vector store - try Hektor first
        vectors_path = self.data_dir / "vectors"
        
        if prefer_hektor and HEKTOR_AVAILABLE:
            try:
                from .hektor_store import HektorVectorStore
                self.store = HektorVectorStore(vectors_path)
                self.using_hektor = True
                self.logger.info(f"[COGNITION] Using Hektor VDB (native C++ backend)")
            except Exception as e:
                self.logger.warning(f"[COGNITION] Hektor init failed: {e}, using hnswlib")
                self.store = VectorStore(vectors_path)
        else:
            self.store = VectorStore(vectors_path)
        
        self.logger.info(f"[COGNITION] Initialized with {self.store.count()} documents")
    
    def ingest_report(
        self,
        filepath: str,
        doc_type: str = "journal",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Ingest a single report into the vector store.
        
        Args:
            filepath: Path to the report file
            doc_type: Type of document (journal, catalyst, etc.)
            metadata: Additional metadata to store
        
        Returns:
            Document ID if successful, None otherwise
        """
        filepath = Path(filepath)
        if not filepath.exists():
            self.logger.warning(f"[COGNITION] File not found: {filepath}")
            return None
        
        try:
            content = filepath.read_text(encoding='utf-8')
            
            # Extract frontmatter if present
            fm_metadata = self._extract_frontmatter(content)
            
            # Remove frontmatter from content
            content = self._strip_frontmatter(content)
            
            # Generate document ID from filename
            doc_id = f"{doc_type}_{filepath.stem}"
            
            # Merge metadata
            full_metadata = {
                "filepath": str(filepath),
                "filename": filepath.name,
                "doc_type": doc_type,
                "ingested_at": datetime.now().isoformat(),
                **(fm_metadata or {}),
                **(metadata or {})
            }
            
            # Add to store
            self.store.add_text(doc_id, content, full_metadata, doc_type=doc_type)
            
            self.logger.info(f"[COGNITION] Ingested: {doc_id} ({len(content)} chars)")
            return doc_id
            
        except Exception as e:
            self.logger.error(f"[COGNITION] Failed to ingest {filepath}: {e}")
            return None
    
    def ingest_all_reports(self) -> Dict[str, int]:
        """
        Ingest all reports from the output directory.
        
        Returns:
            Dict with counts by document type
        """
        counts = {}
        
        # Define report directories and their types
        report_dirs = {
            "reports/journals": "journal",
            "reports/catalysts": "catalyst",
            "reports/premarket": "premarket",
            "reports/weekly": "weekly",
            "reports/monthly": "monthly",
            "reports/yearly": "yearly",
            "reports/institutional": "institutional",
            "reports/economic": "economic",
            "reports/analysis": "analysis"
        }
        
        for subdir, doc_type in report_dirs.items():
            dir_path = self.output_dir / subdir
            if not dir_path.exists():
                continue
            
            count = 0
            for filepath in dir_path.glob("*.md"):
                doc_id = self.ingest_report(filepath, doc_type)
                if doc_id:
                    count += 1
            
            if count > 0:
                counts[doc_type] = count
        
        # Also ingest root-level journals
        for filepath in self.output_dir.glob("Journal_*.md"):
            doc_id = self.ingest_report(filepath, "journal")
            if doc_id:
                counts["journal"] = counts.get("journal", 0) + 1
        
        self.logger.info(f"[COGNITION] Ingested {sum(counts.values())} reports: {counts}")
        return counts
    
    def search(
        self,
        query: str,
        k: int = 5,
        doc_type: Optional[str] = None,
        min_score: float = 0.1
    ) -> List[SearchResult]:
        """
        Search for similar content across all ingested reports.
        
        Args:
            query: Search query
            k: Number of results
            doc_type: Filter by document type
            min_score: Minimum similarity threshold
        
        Returns:
            List of SearchResult objects
        """
        return self.store.search(query, k=k, doc_type=doc_type, min_score=min_score)
    
    def hybrid_search(
        self,
        query: str,
        k: int = 5,
        doc_type: Optional[str] = None,
        vector_weight: float = 0.7,
        bm25_weight: float = 0.3,
        lexical_weight: Optional[float] = None
    ) -> List[SearchResult]:
        """
        Hybrid search combining vector similarity and BM25 lexical matching.
        
        Only available when using Hektor backend. Falls back to regular search otherwise.
        
        Args:
            query: Search query
            k: Number of results
            doc_type: Filter by document type
            vector_weight: Weight for vector similarity (0-1)
            bm25_weight: Weight for BM25 lexical match (0-1) - alias for lexical_weight
            lexical_weight: Weight for BM25 lexical match (0-1)
        
        Returns:
            List of SearchResult objects
        """
        # Use lexical_weight if provided, otherwise use bm25_weight
        lex_weight = lexical_weight if lexical_weight is not None else bm25_weight
        
        if self.using_hektor and hasattr(self.store, 'hybrid_search'):
            return self.store.hybrid_search(
                query, k=k, doc_type=doc_type,
                vector_weight=vector_weight, lexical_weight=lex_weight
            )
        else:
            return self.search(query, k=k, doc_type=doc_type)
    
    def get_context_for_analysis(
        self,
        current_conditions: str,
        k: int = 3
    ) -> str:
        """
        Get relevant historical context for AI analysis.
        
        Args:
            current_conditions: Description of current market conditions
            k: Number of historical examples to retrieve
        
        Returns:
            Formatted context string for LLM prompt
        """
        results = self.search(current_conditions, k=k, min_score=0.1)
        
        if not results:
            return "No relevant historical data found."
        
        context_parts = ["## Relevant Historical Context\n"]
        
        for i, r in enumerate(results, 1):
            doc = r.document
            if doc:
                date = doc.metadata.get('date', 'Unknown date')
                bias = doc.metadata.get('bias', 'N/A')
                
                # Truncate content
                content = doc.content[:500] + "..." if len(doc.content) > 500 else doc.content
                
                context_parts.append(f"""
### Historical Example {i} (Similarity: {r.score:.2f})
**Date**: {date} | **Type**: {doc.doc_type} | **Bias**: {bias}

{content}
""")
        
        return "\n".join(context_parts)
    
    def learn_from_prediction(
        self,
        prediction_date: str,
        predicted_bias: str,
        actual_outcome: str,
        gold_price_then: float,
        gold_price_now: float,
        market_context: Optional[str] = None,
        catalysts: Optional[List[str]] = None
    ) -> bool:
        """
        Record a prediction outcome for learning.
        
        Args:
            prediction_date: Date of the prediction
            predicted_bias: What was predicted (BULLISH, BEARISH, NEUTRAL)
            actual_outcome: What actually happened (WIN, LOSS, NEUTRAL, PENDING)
            gold_price_then: Gold price at prediction time
            gold_price_now: Current gold price
            market_context: Optional market conditions at time of prediction
            catalysts: Optional list of catalysts that influenced the outcome
        
        Returns:
            True if recorded successfully
        """
        try:
            doc_id = f"outcome_{prediction_date}"
            
            pct_change = ((gold_price_now - gold_price_then) / gold_price_then * 100) if gold_price_then else 0
            
            # Determine outcome if it was PENDING
            if actual_outcome == "PENDING":
                # Auto-evaluate: if price moved >0.5% in predicted direction = WIN
                if predicted_bias == "BULLISH" and pct_change > 0.5:
                    actual_outcome = "WIN"
                elif predicted_bias == "BEARISH" and pct_change < -0.5:
                    actual_outcome = "WIN"
                elif abs(pct_change) <= 0.5:
                    actual_outcome = "NEUTRAL"
                else:
                    actual_outcome = "LOSS"
            
            # Build rich content for semantic learning
            catalyst_str = ", ".join(catalysts) if catalysts else "None specified"
            context_str = market_context or "No context recorded"
            
            # Determine what patterns led to this outcome
            outcome_analysis = self._analyze_prediction_outcome(
                predicted_bias, actual_outcome, pct_change, catalysts
            )
            
            content = f"""
Prediction Outcome Record
========================
Date: {prediction_date}
Predicted Bias: {predicted_bias}
Actual Outcome: {actual_outcome}
Gold Price Then: ${gold_price_then:.2f}
Gold Price Now: ${gold_price_now:.2f}
Change: {pct_change:+.2f}%

Market Context:
{context_str}

Active Catalysts:
{catalyst_str}

Learning Analysis:
{outcome_analysis}

Key Insight: {self._extract_key_insight(predicted_bias, actual_outcome, pct_change)}
"""
            
            metadata = {
                "prediction_date": prediction_date,
                "predicted_bias": predicted_bias,
                "actual_outcome": actual_outcome,
                "gold_price_then": gold_price_then,
                "gold_price_now": gold_price_now,
                "pct_change": pct_change,
                "catalysts": catalysts or [],
                "has_context": market_context is not None,
                "recorded_at": datetime.now().isoformat()
            }
            
            self.store.add_text(doc_id, content, metadata, doc_type="outcome")
            self.logger.info(f"[COGNITION] Recorded prediction outcome: {prediction_date} -> {actual_outcome} ({pct_change:+.2f}%)")
            return True
            
        except Exception as e:
            self.logger.error(f"[COGNITION] Failed to record outcome: {e}")
            return False
    
    def _analyze_prediction_outcome(
        self,
        predicted_bias: str,
        actual_outcome: str,
        pct_change: float,
        catalysts: Optional[List[str]]
    ) -> str:
        """Generate learning analysis from prediction outcome."""
        if actual_outcome == "WIN":
            if abs(pct_change) > 1.0:
                return f"Strong {predicted_bias} prediction confirmed with {abs(pct_change):.2f}% move. Pattern recognition was accurate."
            else:
                return f"Correct {predicted_bias} bias but moderate movement. Consider position sizing for similar setups."
        elif actual_outcome == "LOSS":
            if abs(pct_change) > 1.0:
                return f"Strong reversal against {predicted_bias} bias ({pct_change:+.2f}%). Review: Was there a missed catalyst or technical signal?"
            else:
                return f"Moderate loss on {predicted_bias} prediction. The setup may have been valid but timing was off."
        else:  # NEUTRAL
            return f"Consolidation phase. {predicted_bias} bias neither confirmed nor denied. Market awaiting catalyst."
    
    def _extract_key_insight(self, predicted_bias: str, actual_outcome: str, pct_change: float) -> str:
        """Extract a single key insight for quick reference."""
        if actual_outcome == "WIN" and abs(pct_change) > 1.5:
            return f"High-conviction {predicted_bias} patterns remain reliable"
        elif actual_outcome == "LOSS" and abs(pct_change) > 1.5:
            return "Strong reversal - need to weight contrary signals more"
        elif actual_outcome == "NEUTRAL":
            return "Consolidation periods require patience before directional bets"
        elif actual_outcome == "WIN":
            return f"{predicted_bias} setups are working - maintain strategy"
        else:
            return "Minor loss - within acceptable variance"
    
    def get_similar_historical_outcomes(
        self,
        market_conditions: str,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find historically similar market conditions and their outcomes.
        Used for pattern-based decision making.
        
        Args:
            market_conditions: Current market condition description
            k: Number of similar outcomes to retrieve
        
        Returns:
            List of similar historical outcomes with their results
        """
        results = self.search(market_conditions, k=k, doc_type="outcome")
        
        similar_outcomes = []
        for r in results:
            doc = r.document
            similar_outcomes.append({
                "date": doc.metadata.get("prediction_date"),
                "bias": doc.metadata.get("predicted_bias"),
                "outcome": doc.metadata.get("actual_outcome"),
                "pct_change": doc.metadata.get("pct_change", 0),
                "similarity": r.score,
                "catalysts": doc.metadata.get("catalysts", [])
            })
        
        return similar_outcomes
    
    def get_pattern_success_rate(
        self,
        pattern_description: str,
        min_similarity: float = 0.3
    ) -> Dict[str, Any]:
        """
        Calculate success rate for similar patterns.
        
        Args:
            pattern_description: Description of the pattern to analyze
            min_similarity: Minimum similarity threshold
        
        Returns:
            Dict with success metrics for similar patterns
        """
        similar = self.get_similar_historical_outcomes(pattern_description, k=20)
        
        # Filter by minimum similarity
        relevant = [s for s in similar if s["similarity"] >= min_similarity]
        
        if not relevant:
            return {
                "pattern": pattern_description,
                "sample_size": 0,
                "success_rate": None,
                "recommendation": "Insufficient data for this pattern"
            }
        
        wins = sum(1 for s in relevant if s["outcome"] == "WIN")
        losses = sum(1 for s in relevant if s["outcome"] == "LOSS")
        total = wins + losses
        
        success_rate = (wins / total * 100) if total > 0 else 0
        
        # Determine recommendation based on historical performance
        if total < 3:
            recommendation = "Insufficient data - proceed with caution"
        elif success_rate >= 70:
            recommendation = "Strong pattern - consider higher conviction"
        elif success_rate >= 50:
            recommendation = "Moderate pattern - standard position sizing"
        else:
            recommendation = "Weak pattern - reduce exposure or skip"
        
        return {
            "pattern": pattern_description,
            "sample_size": len(relevant),
            "wins": wins,
            "losses": losses,
            "success_rate": round(success_rate, 1) if total > 0 else None,
            "avg_similarity": round(sum(s["similarity"] for s in relevant) / len(relevant), 2),
            "recommendation": recommendation
        }
    
    def generate_learning_feedback(self) -> str:
        """
        Generate a learning feedback summary for the AI.
        
        This is used to improve future predictions by providing
        a summary of what's working and what's not.
        """
        accuracy = self.get_prediction_accuracy(last_n=30)
        
        if accuracy["total"] == 0:
            return "No prediction history available for learning feedback."
        
        feedback_parts = ["## Learning Feedback Summary\n"]
        
        # Overall performance
        feedback_parts.append(f"**Overall Win Rate**: {accuracy['win_rate']}%")
        feedback_parts.append(f"**Total Predictions**: {accuracy['total']}")
        feedback_parts.append(f"**Confidence Score**: {accuracy['confidence_score']}/100\n")
        
        # Bias-specific performance
        bullish = accuracy["by_bias"]["bullish"]
        bearish = accuracy["by_bias"]["bearish"]
        
        feedback_parts.append("### Performance by Bias")
        if bullish["total"] > 0:
            feedback_parts.append(f"- BULLISH: {bullish['win_rate']}% ({bullish['wins']}/{bullish['total']})")
        if bearish["total"] > 0:
            feedback_parts.append(f"- BEARISH: {bearish['win_rate']}% ({bearish['wins']}/{bearish['total']})")
        
        # Streak analysis
        streak = accuracy["current_streak"]
        if streak["type"] == "WIN" and streak["length"] >= 3:
            feedback_parts.append(f"\n**Current State**: On a {streak['length']}-prediction win streak!")
        elif streak["type"] == "LOSS" and streak["length"] >= 2:
            feedback_parts.append(f"\n**Warning**: On a {streak['length']}-prediction losing streak. Consider increased caution.")
        
        # Adaptive recommendations
        feedback_parts.append("\n### Adaptive Recommendations")
        
        if bullish["total"] >= 3 and bearish["total"] >= 3:
            if bullish["win_rate"] > bearish["win_rate"] + 15:
                feedback_parts.append("- Historical data suggests bullish setups are more reliable")
            elif bearish["win_rate"] > bullish["win_rate"] + 15:
                feedback_parts.append("- Historical data suggests bearish setups are more reliable")
        
        if accuracy["avg_pct_change"] > 0.5:
            feedback_parts.append("- Average move is positive - bullish bias may be appropriate")
        elif accuracy["avg_pct_change"] < -0.5:
            feedback_parts.append("- Average move is negative - bearish bias may be appropriate")
        else:
            feedback_parts.append("- Market showing consolidation - consider neutral stance")
        
        return "\n".join(feedback_parts)
    
    def update_pending_predictions(self, current_gold_price: float) -> Dict[str, str]:
        """
        Update all PENDING predictions with actual outcomes.
        
        Args:
            current_gold_price: Current gold price for comparison
        
        Returns:
            Dict of {prediction_date: new_outcome}
        """
        updates = {}
        pending = self.store.list_documents(doc_type="outcome", limit=100)
        
        for doc in pending:
            if doc.metadata.get("actual_outcome") == "PENDING":
                prediction_date = doc.metadata.get("prediction_date")
                predicted_bias = doc.metadata.get("predicted_bias", "NEUTRAL")
                gold_price_then = doc.metadata.get("gold_price_then", current_gold_price)
                
                # Re-record with current price to trigger auto-evaluation
                self.learn_from_prediction(
                    prediction_date=prediction_date,
                    predicted_bias=predicted_bias,
                    actual_outcome="PENDING",  # Will be auto-evaluated
                    gold_price_then=gold_price_then,
                    gold_price_now=current_gold_price,
                    catalysts=doc.metadata.get("catalysts")
                )
                
                # Get the new outcome
                updated_doc = self.store.get_document(f"outcome_{prediction_date}")
                if updated_doc:
                    new_outcome = updated_doc.metadata.get("actual_outcome", "UNKNOWN")
                    updates[prediction_date] = new_outcome
        
        if updates:
            self.logger.info(f"[COGNITION] Updated {len(updates)} pending predictions")
        
        return updates
    
    def get_prediction_accuracy(self, last_n: int = 20) -> Dict[str, Any]:
        """
        Analyze prediction accuracy from stored outcomes.
        
        Args:
            last_n: Number of recent predictions to analyze
        
        Returns:
            Dict with comprehensive accuracy statistics
        """
        outcomes = self.store.list_documents(doc_type="outcome", limit=last_n)
        
        if not outcomes:
            return {"total": 0, "win_rate": 0.0, "message": "No predictions recorded yet"}
        
        # Basic counts
        wins = sum(1 for o in outcomes if o.metadata.get("actual_outcome") == "WIN")
        losses = sum(1 for o in outcomes if o.metadata.get("actual_outcome") == "LOSS")
        neutrals = sum(1 for o in outcomes if o.metadata.get("actual_outcome") == "NEUTRAL")
        pending = sum(1 for o in outcomes if o.metadata.get("actual_outcome") == "PENDING")
        
        total = wins + losses + neutrals
        win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0.0
        
        # Breakdown by bias type
        bullish_outcomes = [o for o in outcomes if o.metadata.get("predicted_bias") == "BULLISH"]
        bearish_outcomes = [o for o in outcomes if o.metadata.get("predicted_bias") == "BEARISH"]
        
        bullish_wins = sum(1 for o in bullish_outcomes if o.metadata.get("actual_outcome") == "WIN")
        bearish_wins = sum(1 for o in bearish_outcomes if o.metadata.get("actual_outcome") == "WIN")
        
        bullish_wr = (bullish_wins / len(bullish_outcomes) * 100) if bullish_outcomes else 0.0
        bearish_wr = (bearish_wins / len(bearish_outcomes) * 100) if bearish_outcomes else 0.0
        
        # Price movement analysis
        pct_changes = [o.metadata.get("pct_change", 0) for o in outcomes if o.metadata.get("pct_change") is not None]
        avg_pct_change = sum(pct_changes) / len(pct_changes) if pct_changes else 0
        max_win = max([p for p in pct_changes if p > 0], default=0)
        max_loss = min([p for p in pct_changes if p < 0], default=0)
        
        # Streak analysis
        recent_streak = self._calculate_streak(outcomes[:10])
        
        return {
            "total": total,
            "wins": wins,
            "losses": losses,
            "neutrals": neutrals,
            "pending": pending,
            "win_rate": round(win_rate, 1),
            "avg_pct_change": round(avg_pct_change, 2),
            "max_win_pct": round(max_win, 2),
            "max_loss_pct": round(max_loss, 2),
            "by_bias": {
                "bullish": {"total": len(bullish_outcomes), "wins": bullish_wins, "win_rate": round(bullish_wr, 1)},
                "bearish": {"total": len(bearish_outcomes), "wins": bearish_wins, "win_rate": round(bearish_wr, 1)}
            },
            "current_streak": recent_streak,
            "confidence_score": self._calculate_confidence_score(win_rate, total, recent_streak)
        }
    
    def _calculate_streak(self, outcomes: List) -> Dict[str, Any]:
        """Calculate current win/loss streak."""
        if not outcomes:
            return {"type": "none", "length": 0}
        
        streak_type = None
        streak_length = 0
        
        for o in outcomes:
            outcome = o.metadata.get("actual_outcome")
            if outcome in ("WIN", "LOSS"):
                if streak_type is None:
                    streak_type = outcome
                    streak_length = 1
                elif outcome == streak_type:
                    streak_length += 1
                else:
                    break
        
        return {"type": streak_type or "none", "length": streak_length}
    
    def _calculate_confidence_score(self, win_rate: float, total: int, streak: Dict) -> float:
        """Calculate overall confidence score (0-100)."""
        # Base score from win rate (40% weight)
        base = win_rate * 0.4
        
        # Sample size bonus (30% weight) - more predictions = more confidence
        sample_bonus = min(total / 50, 1.0) * 30
        
        # Streak bonus/penalty (30% weight)
        streak_factor = 0
        if streak["type"] == "WIN":
            streak_factor = min(streak["length"] * 5, 30)
        elif streak["type"] == "LOSS":
            streak_factor = -min(streak["length"] * 5, 20)
        
        return round(max(0, min(100, base + sample_bonus + streak_factor)), 1)
    
    def stats(self) -> Dict[str, Any]:
        """Get cognition statistics."""
        store_stats = self.store.stats()
        accuracy = self.get_prediction_accuracy()
        
        return {
            **store_stats,
            "prediction_accuracy": accuracy
        }
    
    def _extract_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract YAML frontmatter from markdown content."""
        if not content.startswith('---'):
            return None
        
        try:
            end = content.find('---', 3)
            if end == -1:
                return None
            
            fm_text = content[3:end].strip()
            
            # Simple YAML parsing
            metadata = {}
            for line in fm_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    
                    # Try to parse as JSON for lists
                    if value.startswith('['):
                        try:
                            value = json.loads(value)
                        except:
                            pass
                    
                    metadata[key] = value
            
            return metadata
            
        except Exception:
            return None
    
    def _strip_frontmatter(self, content: str) -> str:
        """Remove YAML frontmatter from content."""
        if not content.startswith('---'):
            return content
        
        end = content.find('---', 3)
        if end == -1:
            return content
        
        return content[end + 3:].strip()
    
    def close(self):
        """Close the cognition engine."""
        self.store.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
