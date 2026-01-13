"""
Syndicate Cognition Integration - Ingest reports into vector memory.

This module connects Syndicate's output (journals, catalysts, analysis)
to the cognition engine for semantic retrieval and learning.
"""

import os
import re
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

from .vector_store import VectorStore, Document, SearchResult


class SyndicateCognition:
    """
    Integrates Syndicate reports with the cognition engine.
    
    Provides:
    - Automatic ingestion of reports into vector store
    - Semantic search across all historical data
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
        logger: Optional[logging.Logger] = None
    ):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize vector store
        vectors_path = self.data_dir / "vectors"
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
        gold_price_now: float
    ) -> bool:
        """
        Record a prediction outcome for learning.
        
        Args:
            prediction_date: Date of the prediction
            predicted_bias: What was predicted (BULLISH, BEARISH, NEUTRAL)
            actual_outcome: What actually happened (WIN, LOSS, NEUTRAL)
            gold_price_then: Gold price at prediction time
            gold_price_now: Current gold price
        
        Returns:
            True if recorded successfully
        """
        try:
            doc_id = f"outcome_{prediction_date}"
            
            pct_change = ((gold_price_now - gold_price_then) / gold_price_then * 100) if gold_price_then else 0
            
            content = f"""
Prediction Outcome Record
Date: {prediction_date}
Predicted Bias: {predicted_bias}
Actual Outcome: {actual_outcome}
Gold Price Then: ${gold_price_then:.2f}
Gold Price Now: ${gold_price_now:.2f}
Change: {pct_change:+.2f}%

Analysis: The {predicted_bias} prediction resulted in a {actual_outcome}.
"""
            
            metadata = {
                "prediction_date": prediction_date,
                "predicted_bias": predicted_bias,
                "actual_outcome": actual_outcome,
                "gold_price_then": gold_price_then,
                "gold_price_now": gold_price_now,
                "pct_change": pct_change
            }
            
            self.store.add_text(doc_id, content, metadata, doc_type="outcome")
            return True
            
        except Exception as e:
            self.logger.error(f"[COGNITION] Failed to record outcome: {e}")
            return False
    
    def get_prediction_accuracy(self, last_n: int = 20) -> Dict[str, Any]:
        """
        Analyze prediction accuracy from stored outcomes.
        
        Args:
            last_n: Number of recent predictions to analyze
        
        Returns:
            Dict with accuracy statistics
        """
        outcomes = self.store.list_documents(doc_type="outcome", limit=last_n)
        
        if not outcomes:
            return {"total": 0, "win_rate": 0.0}
        
        wins = sum(1 for o in outcomes if o.metadata.get("actual_outcome") == "WIN")
        losses = sum(1 for o in outcomes if o.metadata.get("actual_outcome") == "LOSS")
        neutrals = sum(1 for o in outcomes if o.metadata.get("actual_outcome") == "NEUTRAL")
        
        total = wins + losses + neutrals
        win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0.0
        
        return {
            "total": total,
            "wins": wins,
            "losses": losses,
            "neutrals": neutrals,
            "win_rate": win_rate,
            "avg_pct_change": sum(o.metadata.get("pct_change", 0) for o in outcomes) / total if total else 0
        }
    
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
