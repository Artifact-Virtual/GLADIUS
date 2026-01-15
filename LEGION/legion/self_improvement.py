"""
Self-Improvement and Learning System for LEGION Agents
Integrates with intelligent iteration engine for continuous evolution
"""

import asyncio
import logging
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import uuid
from collections import defaultdict
from enum import Enum

# Define enums locally if iteration engine not available
try:
    import sys
    iterate_path = Path(__file__).parent.parent.parent / "res_dev" / "development" / ".iterate"
    sys.path.insert(0, str(iterate_path))
    from intelligent_iteration_engine import ImprovementOpportunity, IterationType, ImprovementStatus
except (ImportError, ModuleNotFoundError):
    # Fallback: define locally
    class IterationType(Enum):
        PERFORMANCE_OPTIMIZATION = "performance_optimization"
        QUALITY_IMPROVEMENT = "quality_improvement"
        FEATURE_ENHANCEMENT = "feature_enhancement"
    
    class ImprovementStatus(Enum):
        IDENTIFIED = "identified"
        PLANNED = "planned"
    
    @dataclass
    class ImprovementOpportunity:
        opportunity_id: str
        type: IterationType
        title: str
        description: str
        impact_score: float
        effort_score: float
        priority_score: float
        identified_by: str
        identified_at: datetime
        evidence: Dict[str, Any]
        affected_components: List[str]
        success_criteria: List[str]
        risk_assessment: Dict[str, Any]
        status: ImprovementStatus

logger = logging.getLogger(__name__)


@dataclass
class PerformanceFeedback:
    """Feedback on agent performance"""
    feedback_id: str
    agent_id: str
    task_type: str
    success: bool
    execution_time_ms: float
    quality_score: float  # 0.0 to 1.0
    user_satisfaction: Optional[float]  # 0.0 to 1.0
    error_details: Optional[str]
    context: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'feedback_id': self.feedback_id,
            'agent_id': self.agent_id,
            'task_type': self.task_type,
            'success': self.success,
            'execution_time_ms': self.execution_time_ms,
            'quality_score': self.quality_score,
            'user_satisfaction': self.user_satisfaction,
            'error_details': self.error_details,
            'context': self.context,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class LearningInsight:
    """Insight learned from experience"""
    insight_id: str
    agent_id: str
    category: str
    pattern: str
    confidence: float
    evidence_count: int
    learned_from: List[str]  # List of feedback/memory IDs
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'insight_id': self.insight_id,
            'agent_id': self.agent_id,
            'category': self.category,
            'pattern': self.pattern,
            'confidence': self.confidence,
            'evidence_count': self.evidence_count,
            'learned_from': self.learned_from,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class ImprovementAction:
    """Action to improve agent performance"""
    action_id: str
    agent_id: str
    improvement_type: str
    description: str
    expected_impact: float
    implemented: bool
    validation_results: Optional[Dict[str, Any]]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'action_id': self.action_id,
            'agent_id': self.agent_id,
            'improvement_type': self.improvement_type,
            'description': self.description,
            'expected_impact': self.expected_impact,
            'implemented': self.implemented,
            'validation_results': self.validation_results,
            'timestamp': self.timestamp.isoformat()
        }


class SelfImprovementSystem:
    """
    Self-improvement and learning system for agents
    Features:
    - Continuous performance monitoring
    - Pattern recognition from experiences
    - Automated improvement suggestions
    - A/B testing of strategies
    - Integration with iteration engine
    """
    
    def __init__(self, db_path: str = "data/self_improvement.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Performance tracking
        self.performance_history: Dict[str, List[PerformanceFeedback]] = defaultdict(list)
        
        # Learning insights
        self.insights: Dict[str, List[LearningInsight]] = defaultdict(list)
        
        # Improvement actions
        self.actions: Dict[str, List[ImprovementAction]] = defaultdict(list)
        
        # Performance baselines
        self.baselines: Dict[str, Dict[str, float]] = {}
        
        # Running flag
        self.running = False
        
        self._initialize_db()
        logger.info("Self-improvement system initialized")
    
    def _initialize_db(self):
        """Initialize SQLite database for self-improvement tracking"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Performance feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_feedback (
                feedback_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                task_type TEXT NOT NULL,
                success INTEGER NOT NULL,
                execution_time_ms REAL NOT NULL,
                quality_score REAL NOT NULL,
                user_satisfaction REAL,
                error_details TEXT,
                context TEXT,
                timestamp TEXT NOT NULL
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_feedback ON performance_feedback(agent_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_type ON performance_feedback(task_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp_pf ON performance_feedback(timestamp)')
        
        # Learning insights table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_insights (
                insight_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                category TEXT NOT NULL,
                pattern TEXT NOT NULL,
                confidence REAL NOT NULL,
                evidence_count INTEGER NOT NULL,
                learned_from TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_insights ON learning_insights(agent_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category_li ON learning_insights(category)')
        
        # Improvement actions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS improvement_actions (
                action_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                improvement_type TEXT NOT NULL,
                description TEXT NOT NULL,
                expected_impact REAL NOT NULL,
                implemented INTEGER DEFAULT 0,
                validation_results TEXT,
                timestamp TEXT NOT NULL
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_actions ON improvement_actions(agent_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_implemented ON improvement_actions(implemented)')
        
        # Performance baselines table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_baselines (
                agent_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                baseline_value REAL NOT NULL,
                last_updated TEXT NOT NULL,
                PRIMARY KEY (agent_id, metric_name)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Self-improvement database initialized")
    
    async def record_feedback(self, agent_id: str, task_type: str, success: bool,
                              execution_time_ms: float, quality_score: float = 1.0,
                              user_satisfaction: float = None, error_details: str = None,
                              context: Dict[str, Any] = None) -> str:
        """
        Record performance feedback for an agent task
        Returns feedback_id
        """
        # Validate agent_id parameter
        if not agent_id or not isinstance(agent_id, str):
            raise ValueError("agent_id must be a non-empty string")
        
        feedback_id = str(uuid.uuid4())
        
        feedback = PerformanceFeedback(
            feedback_id=feedback_id,
            agent_id=agent_id,
            task_type=task_type,
            success=success,
            execution_time_ms=execution_time_ms,
            quality_score=quality_score,
            user_satisfaction=user_satisfaction,
            error_details=error_details,
            context=context or {},
            timestamp=datetime.now()
        )
        
        # Store in memory
        self.performance_history[agent_id].append(feedback)
        
        # Persist to database
        self._persist_feedback(feedback)
        
        # Trigger learning analysis
        await self._analyze_performance(agent_id, feedback)
        
        logger.debug(f"Recorded feedback {feedback_id} for agent {agent_id}")
        return feedback_id
    
    async def _analyze_performance(self, agent_id: str, feedback: PerformanceFeedback):
        """Analyze performance and identify learning opportunities"""
        # Get recent performance history
        recent_feedback = self._get_recent_feedback(agent_id, days=7)
        
        if len(recent_feedback) < 10:
            # Need more data
            return
        
        # Analyze patterns
        await self._identify_patterns(agent_id, recent_feedback)
        
        # Check for performance degradation
        await self._check_degradation(agent_id, recent_feedback)
        
        # Suggest improvements
        await self._suggest_improvements(agent_id, recent_feedback)
    
    async def _identify_patterns(self, agent_id: str, feedback_list: List[PerformanceFeedback]):
        """Identify patterns in performance data"""
        # Group by task type
        by_task_type = defaultdict(list)
        for fb in feedback_list:
            by_task_type[fb.task_type].append(fb)
        
        # Analyze each task type
        for task_type, feedbacks in by_task_type.items():
            success_rate = sum(1 for f in feedbacks if f.success) / len(feedbacks)
            avg_execution_time = sum(f.execution_time_ms for f in feedbacks) / len(feedbacks)
            avg_quality = sum(f.quality_score for f in feedbacks) / len(feedbacks)
            
            # Pattern: Low success rate
            if success_rate < 0.7:
                insight = LearningInsight(
                    insight_id=str(uuid.uuid4()),
                    agent_id=agent_id,
                    category="low_success_rate",
                    pattern=f"Task type '{task_type}' has {success_rate:.1%} success rate",
                    confidence=0.9,
                    evidence_count=len(feedbacks),
                    learned_from=[f.feedback_id for f in feedbacks],
                    timestamp=datetime.now()
                )
                self._store_insight(insight)
            
            # Pattern: Slow execution
            if avg_execution_time > 5000:  # > 5 seconds
                insight = LearningInsight(
                    insight_id=str(uuid.uuid4()),
                    agent_id=agent_id,
                    category="slow_execution",
                    pattern=f"Task type '{task_type}' averages {avg_execution_time:.0f}ms",
                    confidence=0.85,
                    evidence_count=len(feedbacks),
                    learned_from=[f.feedback_id for f in feedbacks],
                    timestamp=datetime.now()
                )
                self._store_insight(insight)
            
            # Pattern: Low quality
            if avg_quality < 0.7:
                insight = LearningInsight(
                    insight_id=str(uuid.uuid4()),
                    agent_id=agent_id,
                    category="low_quality",
                    pattern=f"Task type '{task_type}' has {avg_quality:.1%} quality score",
                    confidence=0.8,
                    evidence_count=len(feedbacks),
                    learned_from=[f.feedback_id for f in feedbacks],
                    timestamp=datetime.now()
                )
                self._store_insight(insight)
    
    async def _check_degradation(self, agent_id: str, recent_feedback: List[PerformanceFeedback]):
        """Check for performance degradation over time"""
        if len(recent_feedback) < 20:
            return
        
        # Split into two halves (older vs newer)
        mid_point = len(recent_feedback) // 2
        older = recent_feedback[:mid_point]
        newer = recent_feedback[mid_point:]
        
        # Compare metrics
        older_success_rate = sum(1 for f in older if f.success) / len(older)
        newer_success_rate = sum(1 for f in newer if f.success) / len(newer)
        
        older_avg_time = sum(f.execution_time_ms for f in older) / len(older)
        newer_avg_time = sum(f.execution_time_ms for f in newer) / len(newer)
        
        # Detect degradation
        if newer_success_rate < older_success_rate * 0.8:  # 20% drop
            logger.warning(f"Agent {agent_id} success rate degraded: {older_success_rate:.1%} -> {newer_success_rate:.1%}")
            
            # Create improvement opportunity
            await self._create_improvement_opportunity(
                agent_id=agent_id,
                type=IterationType.QUALITY_IMPROVEMENT,
                title="Success rate degradation detected",
                description=f"Success rate dropped from {older_success_rate:.1%} to {newer_success_rate:.1%}",
                impact_score=8.0
            )
        
        if newer_avg_time > older_avg_time * 1.5:  # 50% slower
            logger.warning(f"Agent {agent_id} execution time degraded: {older_avg_time:.0f}ms -> {newer_avg_time:.0f}ms")
            
            await self._create_improvement_opportunity(
                agent_id=agent_id,
                type=IterationType.PERFORMANCE_OPTIMIZATION,
                title="Execution time degradation detected",
                description=f"Execution time increased from {older_avg_time:.0f}ms to {newer_avg_time:.0f}ms",
                impact_score=7.0
            )
    
    async def _suggest_improvements(self, agent_id: str, recent_feedback: List[PerformanceFeedback]):
        """Suggest specific improvements based on patterns"""
        # Get insights for this agent
        insights = self._get_insights(agent_id)
        
        for insight in insights:
            if insight.category == "slow_execution":
                action = ImprovementAction(
                    action_id=str(uuid.uuid4()),
                    agent_id=agent_id,
                    improvement_type="optimization",
                    description="Optimize execution path for frequently used operations",
                    expected_impact=0.3,  # 30% improvement
                    implemented=False,
                    validation_results=None,
                    timestamp=datetime.now()
                )
                self._store_action(action)
            
            elif insight.category == "low_success_rate":
                action = ImprovementAction(
                    action_id=str(uuid.uuid4()),
                    agent_id=agent_id,
                    improvement_type="reliability",
                    description="Add error handling and retry logic for failing operations",
                    expected_impact=0.25,  # 25% improvement
                    implemented=False,
                    validation_results=None,
                    timestamp=datetime.now()
                )
                self._store_action(action)
            
            elif insight.category == "low_quality":
                action = ImprovementAction(
                    action_id=str(uuid.uuid4()),
                    agent_id=agent_id,
                    improvement_type="quality",
                    description="Enhance output quality with additional validation steps",
                    expected_impact=0.2,  # 20% improvement
                    implemented=False,
                    validation_results=None,
                    timestamp=datetime.now()
                )
                self._store_action(action)
    
    async def _create_improvement_opportunity(self, agent_id: str, type: IterationType,
                                             title: str, description: str, impact_score: float):
        """Create an improvement opportunity in the iteration engine"""
        opportunity = ImprovementOpportunity(
            opportunity_id=str(uuid.uuid4()),
            type=type,
            title=title,
            description=description,
            impact_score=impact_score,
            effort_score=5.0,  # Medium effort
            priority_score=impact_score / 5.0,  # Simple priority calculation
            identified_by=f"agent_{agent_id}",
            identified_at=datetime.now(),
            evidence={
                "agent_id": agent_id,
                "analysis_source": "self_improvement_system"
            },
            affected_components=[agent_id],
            success_criteria=["Performance metrics improved"],
            risk_assessment={"risk_level": "low"},
            status=ImprovementStatus.IDENTIFIED
        )
        
        logger.info(f"Created improvement opportunity: {title}")
        # This would integrate with the iteration engine
        return opportunity
    
    def _get_recent_feedback(self, agent_id: str, days: int = 7) -> List[PerformanceFeedback]:
        """Get recent performance feedback for an agent"""
        cutoff = datetime.now() - timedelta(days=days)
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM performance_feedback
                WHERE agent_id = ? AND timestamp > ?
                ORDER BY timestamp DESC
            ''', (agent_id, cutoff.isoformat()))
            
            feedbacks = []
            for row in cursor.fetchall():
                feedback = PerformanceFeedback(
                    feedback_id=row[0],
                    agent_id=row[1],
                    task_type=row[2],
                    success=bool(row[3]),
                    execution_time_ms=row[4],
                    quality_score=row[5],
                    user_satisfaction=row[6],
                    error_details=row[7],
                    context=json.loads(row[8]) if row[8] else {},
                    timestamp=datetime.fromisoformat(row[9])
                )
                feedbacks.append(feedback)
            
            conn.close()
            return feedbacks
            
        except Exception as e:
            logger.error(f"Failed to get recent feedback: {e}")
            return []
    
    def _get_insights(self, agent_id: str, limit: int = 10) -> List[LearningInsight]:
        """Get learning insights for an agent"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM learning_insights
                WHERE agent_id = ?
                ORDER BY confidence DESC, timestamp DESC
                LIMIT ?
            ''', (agent_id, limit))
            
            insights = []
            for row in cursor.fetchall():
                insight = LearningInsight(
                    insight_id=row[0],
                    agent_id=row[1],
                    category=row[2],
                    pattern=row[3],
                    confidence=row[4],
                    evidence_count=row[5],
                    learned_from=json.loads(row[6]),
                    timestamp=datetime.fromisoformat(row[7])
                )
                insights.append(insight)
            
            conn.close()
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get insights: {e}")
            return []
    
    def _persist_feedback(self, feedback: PerformanceFeedback):
        """Persist feedback to database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_feedback
                (feedback_id, agent_id, task_type, success, execution_time_ms,
                 quality_score, user_satisfaction, error_details, context, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                feedback.feedback_id,
                feedback.agent_id,
                feedback.task_type,
                int(feedback.success),
                feedback.execution_time_ms,
                feedback.quality_score,
                feedback.user_satisfaction,
                feedback.error_details,
                json.dumps(feedback.context),
                feedback.timestamp.isoformat()
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to persist feedback: {e}")
    
    def _store_insight(self, insight: LearningInsight):
        """Store learning insight"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO learning_insights
                (insight_id, agent_id, category, pattern, confidence,
                 evidence_count, learned_from, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                insight.insight_id,
                insight.agent_id,
                insight.category,
                insight.pattern,
                insight.confidence,
                insight.evidence_count,
                json.dumps(insight.learned_from),
                insight.timestamp.isoformat()
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Stored insight: {insight.pattern}")
        except Exception as e:
            logger.error(f"Failed to store insight: {e}")
    
    def _store_action(self, action: ImprovementAction):
        """Store improvement action"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO improvement_actions
                (action_id, agent_id, improvement_type, description,
                 expected_impact, implemented, validation_results, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                action.action_id,
                action.agent_id,
                action.improvement_type,
                action.description,
                action.expected_impact,
                int(action.implemented),
                json.dumps(action.validation_results) if action.validation_results else None,
                action.timestamp.isoformat()
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Stored improvement action: {action.description}")
        except Exception as e:
            logger.error(f"Failed to store action: {e}")
    
    def get_agent_performance_summary(self, agent_id: str, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive performance summary for an agent"""
        feedback_list = self._get_recent_feedback(agent_id, days)
        
        if not feedback_list:
            return {"agent_id": agent_id, "message": "No performance data available"}
        
        # Calculate metrics
        total_tasks = len(feedback_list)
        successful_tasks = sum(1 for f in feedback_list if f.success)
        success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0
        
        avg_execution_time = sum(f.execution_time_ms for f in feedback_list) / total_tasks
        avg_quality = sum(f.quality_score for f in feedback_list) / total_tasks
        
        # Get insights and actions
        insights = self._get_insights(agent_id)
        
        return {
            "agent_id": agent_id,
            "time_period_days": days,
            "total_tasks": total_tasks,
            "success_rate": success_rate,
            "average_execution_time_ms": avg_execution_time,
            "average_quality_score": avg_quality,
            "insights_count": len(insights),
            "top_insights": [i.pattern for i in insights[:3]],
            "improvement_opportunities": len([i for i in insights if i.confidence > 0.7])
        }
    
    async def start(self):
        """Start the self-improvement system"""
        self.running = True
        logger.info("Self-improvement system started")
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self._periodic_analysis()),
            asyncio.create_task(self._cleanup_old_data())
        ]
        
        return tasks
    
    async def stop(self):
        """Stop the self-improvement system"""
        self.running = False
        logger.info("Self-improvement system stopped")
    
    async def _periodic_analysis(self):
        """Periodically analyze agent performance"""
        while self.running:
            await asyncio.sleep(3600)  # Every hour
            
            try:
                # Get all agents with recent feedback
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT DISTINCT agent_id FROM performance_feedback
                    WHERE timestamp > ?
                ''', ((datetime.now() - timedelta(hours=1)).isoformat(),))
                
                agent_ids = [row[0] for row in cursor.fetchall()]
                conn.close()
                
                # Analyze each agent
                for agent_id in agent_ids:
                    recent_feedback = self._get_recent_feedback(agent_id, days=1)
                    if recent_feedback:
                        await self._analyze_performance(agent_id, recent_feedback[-1])
                
                logger.info(f"Periodic analysis completed for {len(agent_ids)} agents")
                
            except Exception as e:
                logger.error(f"Periodic analysis failed: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old performance data"""
        while self.running:
            await asyncio.sleep(86400)  # Daily
            
            try:
                cutoff = datetime.now() - timedelta(days=90)
                
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM performance_feedback WHERE timestamp < ?', 
                             (cutoff.isoformat(),))
                
                deleted = cursor.rowcount
                conn.commit()
                conn.close()
                
                logger.info(f"Cleaned up {deleted} old performance records")
                
            except Exception as e:
                logger.error(f"Cleanup failed: {e}")


# Global self-improvement system instance
self_improvement_system = SelfImprovementSystem()
