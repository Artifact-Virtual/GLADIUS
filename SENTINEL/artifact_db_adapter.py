"""
SENTINEL Artifact Database Adapter
===================================

Integrates SENTINEL with Artifact Virtual's unified database infrastructure.

Uses:
- Syndicate's db_manager for transactional data (SQLite WAL)
- Hektor/HNSW vector store for semantic memory with SIMD optimization
- Unified research_outputs for cross-system access

This replaces standalone SQLite databases with Artifact's native infrastructure.

Author: Artifact Virtual Systems
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add paths for Artifact imports
ARTIFACT_ROOT = Path(__file__).parent.parent / "Artifact"
sys.path.insert(0, str(ARTIFACT_ROOT / "syndicate"))
sys.path.insert(0, str(ARTIFACT_ROOT / "syndicate" / "src"))
sys.path.insert(0, str(ARTIFACT_ROOT / "deployment" / "automata"))

logger = logging.getLogger("SENTINEL.ArtifactDB")


class ArtifactDatabaseAdapter:
    """
    Unified adapter for SENTINEL to use Artifact's database infrastructure.
    
    Features:
    - Uses Syndicate's SQLite (WAL mode) for state/discoveries/insights
    - Uses Hektor vector store for semantic search and memory
    - Exports to unified research_outputs for cross-system access
    """
    
    def __init__(self):
        self._db_manager = None
        self._vector_store = None
        self._initialized = False
        
    def _ensure_initialized(self):
        """Lazy initialization to avoid import errors"""
        if self._initialized:
            return
            
        try:
            # Try to import Syndicate's database manager
            from db_manager import get_db
            self._db_manager = get_db()
            logger.info("Connected to Syndicate database manager")
        except ImportError as e:
            logger.warning(f"Syndicate db_manager not available: {e}")
            self._db_manager = None
            
        try:
            # Try to import Hektor vector store
            from cognition.hektor_store import get_vector_store, HEKTOR_AVAILABLE
            if HEKTOR_AVAILABLE:
                vector_path = ARTIFACT_ROOT / "syndicate" / "data" / "sentinel_vectors"
                self._vector_store = get_vector_store(str(vector_path), dim=384)
                logger.info(f"Hektor vector store initialized at {vector_path}")
            else:
                # Fall back to HNSW-based store
                from cognition.vector_store import VectorStore
                vector_path = ARTIFACT_ROOT / "syndicate" / "data" / "sentinel_vectors"
                self._vector_store = VectorStore(str(vector_path), dim=384)
                logger.info(f"HNSW vector store initialized at {vector_path}")
        except ImportError as e:
            logger.warning(f"Vector store not available: {e}")
            self._vector_store = None
            
        self._initialized = True
        
        # Initialize SENTINEL-specific tables
        self._init_sentinel_tables()
    
    def _init_sentinel_tables(self):
        """Initialize SENTINEL-specific tables in Syndicate database"""
        if not self._db_manager:
            return
            
        try:
            with self._db_manager._get_connection() as conn:
                cursor = conn.cursor()
                
                # SENTINEL state table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sentinel_state (
                        id INTEGER PRIMARY KEY,
                        current_phase TEXT,
                        last_cycle_start TEXT,
                        last_cycle_end TEXT,
                        cycles_completed INTEGER DEFAULT 0,
                        training_pending INTEGER DEFAULT 0,
                        last_checkpoint TEXT,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # SENTINEL discoveries
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sentinel_discoveries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cycle_id INTEGER,
                        source TEXT NOT NULL,
                        title TEXT,
                        url TEXT UNIQUE,
                        keywords TEXT,
                        relevance_score REAL DEFAULT 0.5,
                        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                        content_summary TEXT,
                        processed INTEGER DEFAULT 0,
                        vector_id INTEGER
                    )
                ''')
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_sentinel_disc_cycle ON sentinel_discoveries(cycle_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_sentinel_disc_source ON sentinel_discoveries(source)")
                
                # SENTINEL insights
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sentinel_insights (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cycle_id INTEGER,
                        discovery_id INTEGER,
                        topic TEXT,
                        keywords TEXT,
                        relevance REAL DEFAULT 0.5,
                        recommended_action TEXT,
                        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (discovery_id) REFERENCES sentinel_discoveries(id)
                    )
                ''')
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_sentinel_insights_cycle ON sentinel_insights(cycle_id)")
                
                # SENTINEL training queue
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sentinel_training_queue (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        insight_id INTEGER,
                        instruction TEXT NOT NULL,
                        input_text TEXT,
                        output_text TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        trained INTEGER DEFAULT 0,
                        model_version TEXT,
                        FOREIGN KEY (insight_id) REFERENCES sentinel_insights(id)
                    )
                ''')
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_sentinel_train_status ON sentinel_training_queue(trained)")
                
                # SENTINEL metrics
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sentinel_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_type TEXT NOT NULL,
                        metric_name TEXT NOT NULL,
                        metric_value REAL,
                        metadata TEXT,
                        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_sentinel_metrics_type ON sentinel_metrics(metric_type)")
                
                conn.commit()
                logger.info("SENTINEL tables initialized in Syndicate database")
                
        except Exception as e:
            logger.error(f"Failed to initialize SENTINEL tables: {e}")
    
    @property
    def db(self):
        """Get Syndicate database manager"""
        self._ensure_initialized()
        return self._db_manager
    
    @property
    def vectors(self):
        """Get vector store"""
        self._ensure_initialized()
        return self._vector_store
    
    # ==========================================
    # STATE MANAGEMENT
    # ==========================================
    
    def load_state(self) -> Optional[Dict[str, Any]]:
        """Load SENTINEL state from Syndicate database"""
        self._ensure_initialized()
        if not self._db_manager:
            return None
            
        try:
            with self._db_manager._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sentinel_state ORDER BY id DESC LIMIT 1")
                row = cursor.fetchone()
                if row:
                    return {
                        "current_phase": row["current_phase"],
                        "last_cycle_start": row["last_cycle_start"],
                        "last_cycle_end": row["last_cycle_end"],
                        "cycles_completed": row["cycles_completed"],
                        "training_pending": bool(row["training_pending"]),
                        "last_checkpoint": row["last_checkpoint"]
                    }
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
        return None
    
    def save_state(self, state: Dict[str, Any]) -> bool:
        """Save SENTINEL state to Syndicate database"""
        self._ensure_initialized()
        if not self._db_manager:
            return False
            
        try:
            with self._db_manager._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO sentinel_state 
                    (id, current_phase, last_cycle_start, last_cycle_end, 
                     cycles_completed, training_pending, last_checkpoint, updated_at)
                    VALUES (1, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    state.get("current_phase", "idle"),
                    state.get("last_cycle_start"),
                    state.get("last_cycle_end"),
                    state.get("cycles_completed", 0),
                    int(state.get("training_pending", False)),
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            return False
    
    # ==========================================
    # DISCOVERY STORAGE
    # ==========================================
    
    def store_discovery(self, discovery: Dict[str, Any], cycle_id: int) -> Optional[int]:
        """Store a discovery in Syndicate database and vector store"""
        self._ensure_initialized()
        if not self._db_manager:
            return None
            
        try:
            # Store in SQLite
            with self._db_manager._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO sentinel_discoveries 
                    (cycle_id, source, title, url, keywords, relevance_score, 
                     timestamp, content_summary)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    cycle_id,
                    discovery.get("source", "unknown"),
                    discovery.get("title", ""),
                    discovery.get("url", ""),
                    json.dumps(discovery.get("keywords", [])),
                    discovery.get("relevance_score", 0.5),
                    discovery.get("timestamp", datetime.now().isoformat()),
                    discovery.get("content_summary", "")
                ))
                discovery_id = cursor.lastrowid
                
                # Store in vector store for semantic search
                if self._vector_store:
                    text = f"{discovery.get('title', '')} {discovery.get('content_summary', '')}"
                    doc_id = f"sentinel_discovery_{discovery_id}"
                    self._vector_store.add_text(
                        doc_id,
                        text,
                        metadata={
                            "source": discovery.get("source"),
                            "url": discovery.get("url"),
                            "cycle_id": cycle_id
                        },
                        doc_type="sentinel_discovery"
                    )
                    
                    # Update with vector ID
                    cursor.execute(
                        "UPDATE sentinel_discoveries SET vector_id = ? WHERE id = ?",
                        (discovery_id, discovery_id)
                    )
                
                conn.commit()
                return discovery_id
                
        except Exception as e:
            logger.error(f"Failed to store discovery: {e}")
            return None
    
    def store_discoveries(self, discoveries: List[Dict[str, Any]], cycle_id: int) -> int:
        """Store multiple discoveries"""
        stored = 0
        for disc in discoveries:
            if self.store_discovery(disc, cycle_id):
                stored += 1
        return stored
    
    def get_discoveries(self, cycle_id: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get discoveries from database"""
        self._ensure_initialized()
        if not self._db_manager:
            return []
            
        try:
            with self._db_manager._get_connection() as conn:
                cursor = conn.cursor()
                if cycle_id:
                    cursor.execute('''
                        SELECT * FROM sentinel_discoveries 
                        WHERE cycle_id = ? 
                        ORDER BY timestamp DESC LIMIT ?
                    ''', (cycle_id, limit))
                else:
                    cursor.execute('''
                        SELECT * FROM sentinel_discoveries 
                        ORDER BY timestamp DESC LIMIT ?
                    ''', (limit,))
                    
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get discoveries: {e}")
            return []
    
    def search_discoveries(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Search discoveries using semantic similarity"""
        self._ensure_initialized()
        if not self._vector_store:
            return []
            
        try:
            results = self._vector_store.search(query, k=k, doc_type="sentinel_discovery")
            return [
                {
                    "id": r.id,
                    "score": r.score,
                    "document": r.document.to_dict() if r.document else None
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Failed to search discoveries: {e}")
            return []
    
    # ==========================================
    # INSIGHT STORAGE
    # ==========================================
    
    def store_insight(self, insight: Dict[str, Any], cycle_id: int) -> Optional[int]:
        """Store an insight"""
        self._ensure_initialized()
        if not self._db_manager:
            return None
            
        try:
            with self._db_manager._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO sentinel_insights 
                    (cycle_id, discovery_id, topic, keywords, relevance, 
                     recommended_action, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    cycle_id,
                    insight.get("discovery_id"),
                    insight.get("topic", ""),
                    json.dumps(insight.get("keywords", [])),
                    insight.get("relevance", 0.5),
                    insight.get("recommended_action", "review"),
                    insight.get("timestamp", datetime.now().isoformat())
                ))
                insight_id = cursor.lastrowid
                
                # Also store in Syndicate's entity_insights for cross-system access
                if hasattr(self._db_manager, 'save_entity_insight'):
                    self._db_manager.save_entity_insight(
                        entity_name=insight.get("topic", ""),
                        entity_type="sentinel_insight",
                        context=json.dumps(insight.get("keywords", [])),
                        relevance_score=insight.get("relevance", 0.5),
                        source_report=f"sentinel_cycle_{cycle_id}",
                        metadata=json.dumps({"source": "sentinel", "action": insight.get("recommended_action")})
                    )
                
                conn.commit()
                return insight_id
                
        except Exception as e:
            logger.error(f"Failed to store insight: {e}")
            return None
    
    def store_insights(self, insights: List[Dict[str, Any]], cycle_id: int) -> int:
        """Store multiple insights"""
        stored = 0
        for insight in insights:
            if self.store_insight(insight, cycle_id):
                stored += 1
        return stored
    
    def get_insights(self, cycle_id: Optional[int] = None, min_relevance: float = 0.0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get insights from database"""
        self._ensure_initialized()
        if not self._db_manager:
            return []
            
        try:
            with self._db_manager._get_connection() as conn:
                cursor = conn.cursor()
                if cycle_id:
                    cursor.execute('''
                        SELECT * FROM sentinel_insights 
                        WHERE cycle_id = ? AND relevance >= ?
                        ORDER BY relevance DESC, timestamp DESC LIMIT ?
                    ''', (cycle_id, min_relevance, limit))
                else:
                    cursor.execute('''
                        SELECT * FROM sentinel_insights 
                        WHERE relevance >= ?
                        ORDER BY relevance DESC, timestamp DESC LIMIT ?
                    ''', (min_relevance, limit))
                    
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get insights: {e}")
            return []
    
    # ==========================================
    # TRAINING QUEUE
    # ==========================================
    
    def add_training_sample(self, sample: Dict[str, Any], insight_id: Optional[int] = None) -> Optional[int]:
        """Add a training sample to the queue"""
        self._ensure_initialized()
        if not self._db_manager:
            return None
            
        try:
            with self._db_manager._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO sentinel_training_queue 
                    (insight_id, instruction, input_text, output_text, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    insight_id,
                    sample.get("instruction", ""),
                    sample.get("input", ""),
                    sample.get("output", ""),
                    datetime.now().isoformat()
                ))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to add training sample: {e}")
            return None
    
    def add_training_samples(self, samples: List[Dict[str, Any]]) -> int:
        """Add multiple training samples"""
        added = 0
        for sample in samples:
            if self.add_training_sample(sample):
                added += 1
        return added
    
    def get_pending_training_samples(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get pending training samples"""
        self._ensure_initialized()
        if not self._db_manager:
            return []
            
        try:
            with self._db_manager._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM sentinel_training_queue 
                    WHERE trained = 0 
                    ORDER BY created_at ASC LIMIT ?
                ''', (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get training samples: {e}")
            return []
    
    def get_pending_training_count(self) -> int:
        """Get count of pending training samples"""
        self._ensure_initialized()
        if not self._db_manager:
            return 0
            
        try:
            with self._db_manager._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sentinel_training_queue WHERE trained = 0")
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Failed to count training samples: {e}")
            return 0
    
    def mark_samples_trained(self, sample_ids: Optional[List[int]] = None, model_version: str = None) -> int:
        """Mark training samples as trained"""
        self._ensure_initialized()
        if not self._db_manager:
            return 0
            
        try:
            with self._db_manager._get_connection() as conn:
                cursor = conn.cursor()
                if sample_ids:
                    placeholders = ",".join("?" for _ in sample_ids)
                    cursor.execute(f'''
                        UPDATE sentinel_training_queue 
                        SET trained = 1, model_version = ?
                        WHERE id IN ({placeholders})
                    ''', [model_version] + sample_ids)
                else:
                    cursor.execute('''
                        UPDATE sentinel_training_queue 
                        SET trained = 1, model_version = ?
                        WHERE trained = 0
                    ''', (model_version,))
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Failed to mark samples trained: {e}")
            return 0
    
    # ==========================================
    # METRICS
    # ==========================================
    
    def record_metric(self, metric_type: str, metric_name: str, value: float, metadata: Optional[Dict] = None) -> bool:
        """Record a metric"""
        self._ensure_initialized()
        if not self._db_manager:
            return False
            
        try:
            with self._db_manager._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO sentinel_metrics 
                    (metric_type, metric_name, metric_value, metadata, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    metric_type,
                    metric_name,
                    value,
                    json.dumps(metadata) if metadata else None,
                    datetime.now().isoformat()
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
            return False
    
    def get_metrics(self, metric_type: Optional[str] = None, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent metrics"""
        self._ensure_initialized()
        if not self._db_manager:
            return []
            
        try:
            with self._db_manager._get_connection() as conn:
                cursor = conn.cursor()
                if metric_type:
                    cursor.execute('''
                        SELECT * FROM sentinel_metrics 
                        WHERE metric_type = ? 
                        AND timestamp >= datetime('now', ?)
                        ORDER BY timestamp DESC
                    ''', (metric_type, f'-{hours} hours'))
                else:
                    cursor.execute('''
                        SELECT * FROM sentinel_metrics 
                        WHERE timestamp >= datetime('now', ?)
                        ORDER BY timestamp DESC
                    ''', (f'-{hours} hours',))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return []
    
    # ==========================================
    # EXPORT TO ARTIFACT
    # ==========================================
    
    def export_to_research_outputs(self, cycle_id: int) -> Optional[Path]:
        """Export cycle data to Artifact/research_outputs for cross-system access"""
        self._ensure_initialized()
        
        try:
            research_outputs = ARTIFACT_ROOT / "research_outputs"
            research_outputs.mkdir(parents=True, exist_ok=True)
            
            # Get discoveries and insights for this cycle
            discoveries = self.get_discoveries(cycle_id)
            insights = self.get_insights(cycle_id)
            
            export_data = {
                "id": f"sentinel_cycle_{cycle_id}",
                "source": "SENTINEL",
                "timestamp": datetime.now().isoformat(),
                "cycle_id": cycle_id,
                "summary": {
                    "discoveries_count": len(discoveries),
                    "insights_count": len(insights),
                    "high_relevance_count": len([i for i in insights if i.get("relevance", 0) >= 0.7])
                },
                "discoveries": discoveries,
                "insights": insights
            }
            
            # Save export file
            filename = f"sentinel_cycle_{cycle_id}_{int(datetime.now().timestamp())}.json"
            filepath = research_outputs / filename
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            # Update index
            index_path = research_outputs / "index.json"
            if index_path.exists():
                with open(index_path) as f:
                    index = json.load(f)
            else:
                index = {"exports": []}
            
            index["exports"].insert(0, {
                "id": export_data["id"],
                "timestamp": export_data["timestamp"],
                "file": str(filepath.name),
                "type": "sentinel_cycle",
                "discoveries": len(discoveries),
                "insights": len(insights)
            })
            
            # Keep last 100 entries
            index["exports"] = index["exports"][:100]
            
            with open(index_path, 'w') as f:
                json.dump(index, f, indent=2)
            
            logger.info(f"Exported cycle {cycle_id} to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export to research_outputs: {e}")
            return None
    
    # ==========================================
    # STATS
    # ==========================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get SENTINEL database statistics"""
        self._ensure_initialized()
        
        stats = {
            "database_connected": self._db_manager is not None,
            "vector_store_connected": self._vector_store is not None,
            "backend": "syndicate" if self._db_manager else "none"
        }
        
        if self._db_manager:
            try:
                with self._db_manager._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT COUNT(*) FROM sentinel_discoveries")
                    stats["total_discoveries"] = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM sentinel_insights")
                    stats["total_insights"] = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM sentinel_training_queue")
                    stats["total_training_samples"] = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM sentinel_training_queue WHERE trained = 0")
                    stats["pending_training"] = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT cycles_completed FROM sentinel_state WHERE id = 1")
                    row = cursor.fetchone()
                    stats["cycles_completed"] = row[0] if row else 0
                    
            except Exception as e:
                logger.error(f"Failed to get stats: {e}")
        
        if self._vector_store:
            try:
                stats["vector_stats"] = self._vector_store.stats()
            except Exception as e:
                logger.error(f"Failed to get vector stats: {e}")
        
        return stats


# Singleton instance
_adapter: Optional[ArtifactDatabaseAdapter] = None


def get_artifact_db() -> ArtifactDatabaseAdapter:
    """Get singleton database adapter instance"""
    global _adapter
    if _adapter is None:
        _adapter = ArtifactDatabaseAdapter()
    return _adapter


if __name__ == "__main__":
    # Test the adapter
    adapter = get_artifact_db()
    print("Adapter stats:")
    import json
    print(json.dumps(adapter.get_stats(), indent=2))
