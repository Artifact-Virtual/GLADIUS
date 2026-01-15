#!/usr/bin/env python3
"""
Intelligent Iteration and Continuous Improvement System
Military-grade system for automated optimization and enhancement cycles
"""

import asyncio
import hashlib
import json
import logging
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IterationType(Enum):
    """Types of iteration cycles"""

    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    QUALITY_IMPROVEMENT = "quality_improvement"
    FEATURE_ENHANCEMENT = "feature_enhancement"
    BUG_FIX = "bug_fix"
    REFACTORING = "refactoring"
    SECURITY_HARDENING = "security_hardening"
    SCALABILITY_ENHANCEMENT = "scalability_enhancement"
    USER_EXPERIENCE = "user_experience"


class ImprovementStatus(Enum):
    """Status of improvement iterations"""

    IDENTIFIED = "identified"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    VALIDATED = "validated"
    DEPLOYED = "deployed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MetricType(Enum):
    """Types of metrics to track"""

    PERFORMANCE = "performance"
    QUALITY = "quality"
    RELIABILITY = "reliability"
    SECURITY = "security"
    USABILITY = "usability"
    MAINTAINABILITY = "maintainability"


@dataclass
class ImprovementOpportunity:
    """Identified improvement opportunity"""

    opportunity_id: str
    type: IterationType
    title: str
    description: str
    impact_score: float  # 0.0 to 10.0
    effort_score: float  # 0.0 to 10.0
    priority_score: float
    identified_by: str
    identified_at: datetime
    evidence: Dict[str, Any]
    affected_components: List[str]
    success_criteria: List[str]
    risk_assessment: Dict[str, Any]
    status: ImprovementStatus


@dataclass
class IterationCycle:
    """Complete iteration cycle"""

    cycle_id: str
    project_id: str
    cycle_number: int
    start_date: datetime
    target_end_date: datetime
    actual_end_date: Optional[datetime]
    objectives: List[str]
    selected_opportunities: List[str]
    baseline_metrics: Dict[str, float]
    target_metrics: Dict[str, float]
    actual_metrics: Dict[str, float]
    status: ImprovementStatus
    results: Dict[str, Any]
    lessons_learned: List[str]


class IntelligentIterationEngine:
    """Engine for continuous improvement and optimization"""

    def __init__(self, workspace_root: str = None):
        self.workspace_root = Path(workspace_root or ".")
        self.db_path = self.workspace_root / "data" / "iteration_engine.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.active_cycles: Dict[str, IterationCycle] = {}
        self.opportunity_queue: List[ImprovementOpportunity] = []
        self.metric_history: Dict[str, List[Dict[str, Any]]] = {}
        self.improvement_patterns: Dict[str, Dict[str, Any]] = {}

        self._init_database()
        self._load_improvement_patterns()

        self.logger = logging.getLogger("iteration_engine")

    def _init_database(self):
        """Initialize iteration tracking database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS improvement_opportunities (
                    opportunity_id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    impact_score REAL NOT NULL,
                    effort_score REAL NOT NULL,
                    priority_score REAL NOT NULL,
                    identified_by TEXT NOT NULL,
                    identified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    evidence TEXT,
                    affected_components TEXT,
                    success_criteria TEXT,
                    risk_assessment TEXT,
                    status TEXT DEFAULT 'identified'
                );
                
                CREATE TABLE IF NOT EXISTS iteration_cycles (
                    cycle_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    cycle_number INTEGER NOT NULL,
                    start_date TIMESTAMP NOT NULL,
                    target_end_date TIMESTAMP NOT NULL,
                    actual_end_date TIMESTAMP,
                    objectives TEXT,
                    selected_opportunities TEXT,
                    baseline_metrics TEXT,
                    target_metrics TEXT,
                    actual_metrics TEXT,
                    status TEXT DEFAULT 'planned',
                    results TEXT,
                    lessons_learned TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS metric_snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    cycle_id TEXT,
                    metric_type TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metric_unit TEXT,
                    measurement_method TEXT,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    context_data TEXT
                );
                
                CREATE TABLE IF NOT EXISTS improvement_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_name TEXT NOT NULL,
                    improvement_type TEXT NOT NULL,
                    success_rate REAL DEFAULT 0.0,
                    average_impact REAL DEFAULT 0.0,
                    typical_effort REAL DEFAULT 0.0,
                    prerequisites TEXT,
                    implementation_steps TEXT,
                    risk_factors TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS cycle_experiments (
                    experiment_id TEXT PRIMARY KEY,
                    cycle_id TEXT NOT NULL,
                    experiment_name TEXT NOT NULL,
                    hypothesis TEXT NOT NULL,
                    methodology TEXT,
                    results TEXT,
                    conclusion TEXT,
                    confidence_level REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cycle_id) REFERENCES iteration_cycles (cycle_id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_opportunities_priority 
                ON improvement_opportunities(priority_score DESC);
                CREATE INDEX IF NOT EXISTS idx_opportunities_status 
                ON improvement_opportunities(status);
                CREATE INDEX IF NOT EXISTS idx_cycles_project 
                ON iteration_cycles(project_id);
                CREATE INDEX IF NOT EXISTS idx_metrics_project 
                ON metric_snapshots(project_id, recorded_at);
            """
            )

    def _load_improvement_patterns(self):
        """Load proven improvement patterns"""
        patterns = {
            "database_optimization": {
                "name": "Database Query Optimization",
                "type": IterationType.PERFORMANCE_OPTIMIZATION,
                "success_rate": 0.85,
                "average_impact": 7.2,
                "typical_effort": 4.0,
                "prerequisites": ["Database access", "Query analysis tools"],
                "steps": [
                    "Analyze slow queries",
                    "Add appropriate indexes",
                    "Optimize query structure",
                    "Test performance improvements",
                ],
                "risk_factors": ["Potential downtime", "Index maintenance overhead"],
            },
            "code_refactoring": {
                "name": "Code Structure Refactoring",
                "type": IterationType.REFACTORING,
                "success_rate": 0.78,
                "average_impact": 5.8,
                "typical_effort": 6.5,
                "prerequisites": ["Comprehensive test suite", "Version control"],
                "steps": [
                    "Identify code smells",
                    "Design improved structure",
                    "Refactor incrementally",
                    "Validate functionality",
                ],
                "risk_factors": ["Regression risks", "Team coordination needed"],
            },
            "caching_implementation": {
                "name": "Strategic Caching Implementation",
                "type": IterationType.PERFORMANCE_OPTIMIZATION,
                "success_rate": 0.92,
                "average_impact": 8.1,
                "typical_effort": 3.5,
                "prerequisites": ["Cache infrastructure", "Performance metrics"],
                "steps": [
                    "Identify cacheable data",
                    "Design cache strategy",
                    "Implement caching layer",
                    "Monitor cache effectiveness",
                ],
                "risk_factors": ["Cache invalidation complexity", "Memory usage"],
            },
        }

        self.improvement_patterns = patterns

        # Store patterns in database
        with sqlite3.connect(self.db_path) as conn:
            for pattern_id, pattern in patterns.items():
                conn.execute(
                    """
                    INSERT OR REPLACE INTO improvement_patterns
                    (pattern_id, pattern_name, improvement_type, success_rate,
                     average_impact, typical_effort, prerequisites, 
                     implementation_steps, risk_factors)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        pattern_id,
                        pattern["name"],
                        pattern["type"].value,
                        pattern["success_rate"],
                        pattern["average_impact"],
                        pattern["typical_effort"],
                        json.dumps(pattern["prerequisites"]),
                        json.dumps(pattern["steps"]),
                        json.dumps(pattern["risk_factors"]),
                    ),
                )

    async def analyze_project_for_improvements(
        self, project_id: str, context: Dict[str, Any]
    ) -> List[ImprovementOpportunity]:
        """Analyze project and identify improvement opportunities"""
        self.logger.info(f"Analyzing project {project_id} for improvements...")

        opportunities = []

        # Analyze performance metrics
        perf_opportunities = await self._analyze_performance_metrics(
            project_id, context
        )
        opportunities.extend(perf_opportunities)

        # Analyze code quality
        quality_opportunities = await self._analyze_code_quality(project_id, context)
        opportunities.extend(quality_opportunities)

        # Analyze security posture
        security_opportunities = await self._analyze_security(project_id, context)
        opportunities.extend(security_opportunities)

        # Analyze user feedback
        ux_opportunities = await self._analyze_user_experience(project_id, context)
        opportunities.extend(ux_opportunities)

        # Store opportunities in database
        with sqlite3.connect(self.db_path) as conn:
            for opp in opportunities:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO improvement_opportunities
                    (opportunity_id, type, title, description, impact_score,
                     effort_score, priority_score, identified_by, evidence,
                     affected_components, success_criteria, risk_assessment, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        opp.opportunity_id,
                        opp.type.value,
                        opp.title,
                        opp.description,
                        opp.impact_score,
                        opp.effort_score,
                        opp.priority_score,
                        opp.identified_by,
                        json.dumps(opp.evidence),
                        json.dumps(opp.affected_components),
                        json.dumps(opp.success_criteria),
                        json.dumps(opp.risk_assessment),
                        opp.status.value,
                    ),
                )

        self.opportunity_queue.extend(opportunities)
        self.logger.info(f"Identified {len(opportunities)} improvement opportunities")

        return opportunities

    async def _analyze_performance_metrics(
        self, project_id: str, context: Dict[str, Any]
    ) -> List[ImprovementOpportunity]:
        """Analyze performance metrics for improvement opportunities"""
        opportunities = []

        # Simulate performance analysis
        metrics = context.get("performance_metrics", {})

        # Check response time
        response_time = metrics.get("avg_response_time_ms", 200)
        if response_time > 150:
            opportunity = ImprovementOpportunity(
                opportunity_id=f"perf_response_{uuid4().hex[:8]}",
                type=IterationType.PERFORMANCE_OPTIMIZATION,
                title="Optimize API Response Time",
                description=f"Current average response time is {response_time}ms, target is <150ms",
                impact_score=8.0,
                effort_score=5.0,
                priority_score=8.5,
                identified_by="performance_analyzer",
                identified_at=datetime.now(),
                evidence={
                    "current_response_time": response_time,
                    "target_response_time": 150,
                    "bottlenecks": ["database_queries", "external_api_calls"],
                },
                affected_components=["api_layer", "database_layer"],
                success_criteria=[
                    "Average response time < 150ms",
                    "95th percentile < 300ms",
                    "No regression in functionality",
                ],
                risk_assessment={
                    "probability": "low",
                    "impact": "medium",
                    "mitigation": "Staged rollout with monitoring",
                },
                status=ImprovementStatus.IDENTIFIED,
            )
            opportunities.append(opportunity)

        # Check throughput
        throughput = metrics.get("requests_per_second", 100)
        if throughput < 200:
            opportunity = ImprovementOpportunity(
                opportunity_id=f"perf_throughput_{uuid4().hex[:8]}",
                type=IterationType.SCALABILITY_ENHANCEMENT,
                title="Increase System Throughput",
                description=f"Current throughput is {throughput} req/s, target is >200 req/s",
                impact_score=7.5,
                effort_score=6.0,
                priority_score=7.0,
                identified_by="performance_analyzer",
                identified_at=datetime.now(),
                evidence={
                    "current_throughput": throughput,
                    "target_throughput": 200,
                    "scaling_options": [
                        "horizontal_scaling",
                        "caching",
                        "optimization",
                    ],
                },
                affected_components=[
                    "load_balancer",
                    "application_servers",
                    "database",
                ],
                success_criteria=[
                    "Sustained throughput > 200 req/s",
                    "Linear scaling with resources",
                    "Stable performance under load",
                ],
                risk_assessment={
                    "probability": "medium",
                    "impact": "low",
                    "mitigation": "Load testing and gradual rollout",
                },
                status=ImprovementStatus.IDENTIFIED,
            )
            opportunities.append(opportunity)

        return opportunities

    async def _analyze_code_quality(
        self, project_id: str, context: Dict[str, Any]
    ) -> List[ImprovementOpportunity]:
        """Analyze code quality metrics"""
        opportunities = []

        quality_metrics = context.get("code_quality", {})

        # Check test coverage
        coverage = quality_metrics.get("test_coverage_percent", 85)
        if coverage < 90:
            opportunity = ImprovementOpportunity(
                opportunity_id=f"quality_coverage_{uuid4().hex[:8]}",
                type=IterationType.QUALITY_IMPROVEMENT,
                title="Improve Test Coverage",
                description=f"Current test coverage is {coverage}%, target is >90%",
                impact_score=6.5,
                effort_score=4.0,
                priority_score=6.8,
                identified_by="quality_analyzer",
                identified_at=datetime.now(),
                evidence={
                    "current_coverage": coverage,
                    "target_coverage": 90,
                    "uncovered_areas": ["error_handling", "edge_cases"],
                },
                affected_components=["test_suite", "all_modules"],
                success_criteria=[
                    "Test coverage > 90%",
                    "Critical paths 100% covered",
                    "Regression test suite complete",
                ],
                risk_assessment={
                    "probability": "low",
                    "impact": "low",
                    "mitigation": "Incremental test addition",
                },
                status=ImprovementStatus.IDENTIFIED,
            )
            opportunities.append(opportunity)

        # Check code complexity
        complexity = quality_metrics.get("cyclomatic_complexity", 5.0)
        if complexity > 7.0:
            opportunity = ImprovementOpportunity(
                opportunity_id=f"quality_complexity_{uuid4().hex[:8]}",
                type=IterationType.REFACTORING,
                title="Reduce Code Complexity",
                description=f"Average complexity is {complexity}, target is <7.0",
                impact_score=5.5,
                effort_score=7.0,
                priority_score=5.8,
                identified_by="quality_analyzer",
                identified_at=datetime.now(),
                evidence={
                    "current_complexity": complexity,
                    "target_complexity": 7.0,
                    "complex_functions": ["data_processor", "validation_logic"],
                },
                affected_components=["core_logic", "validation_modules"],
                success_criteria=[
                    "Average complexity < 7.0",
                    "No functions with complexity > 15",
                    "Improved maintainability score",
                ],
                risk_assessment={
                    "probability": "medium",
                    "impact": "medium",
                    "mitigation": "Incremental refactoring with tests",
                },
                status=ImprovementStatus.IDENTIFIED,
            )
            opportunities.append(opportunity)

        return opportunities

    async def _analyze_security(
        self, project_id: str, context: Dict[str, Any]
    ) -> List[ImprovementOpportunity]:
        """Analyze security posture"""
        opportunities = []

        security_metrics = context.get("security", {})

        # Check for security vulnerabilities
        vuln_count = security_metrics.get("known_vulnerabilities", 2)
        if vuln_count > 0:
            opportunity = ImprovementOpportunity(
                opportunity_id=f"security_vulns_{uuid4().hex[:8]}",
                type=IterationType.SECURITY_HARDENING,
                title="Address Security Vulnerabilities",
                description=f"Found {vuln_count} known vulnerabilities requiring attention",
                impact_score=9.0,
                effort_score=3.0,
                priority_score=9.5,
                identified_by="security_analyzer",
                identified_at=datetime.now(),
                evidence={
                    "vulnerability_count": vuln_count,
                    "severity_breakdown": {"high": 0, "medium": 1, "low": 1},
                    "affected_dependencies": ["requests", "cryptography"],
                },
                affected_components=["dependencies", "authentication"],
                success_criteria=[
                    "Zero known vulnerabilities",
                    "All dependencies up to date",
                    "Security scan passes",
                ],
                risk_assessment={
                    "probability": "high",
                    "impact": "high",
                    "mitigation": "Immediate patching with testing",
                },
                status=ImprovementStatus.IDENTIFIED,
            )
            opportunities.append(opportunity)

        return opportunities

    async def _analyze_user_experience(
        self, project_id: str, context: Dict[str, Any]
    ) -> List[ImprovementOpportunity]:
        """Analyze user experience metrics"""
        opportunities = []

        ux_metrics = context.get("user_experience", {})

        # Check user satisfaction
        satisfaction = ux_metrics.get("satisfaction_score", 3.8)
        if satisfaction < 4.0:
            opportunity = ImprovementOpportunity(
                opportunity_id=f"ux_satisfaction_{uuid4().hex[:8]}",
                type=IterationType.USER_EXPERIENCE,
                title="Improve User Satisfaction",
                description=f"User satisfaction score is {satisfaction}/5.0, target is >4.0",
                impact_score=7.0,
                effort_score=5.5,
                priority_score=7.2,
                identified_by="ux_analyzer",
                identified_at=datetime.now(),
                evidence={
                    "current_score": satisfaction,
                    "target_score": 4.0,
                    "feedback_themes": ["slow_loading", "confusing_navigation"],
                },
                affected_components=["ui_components", "navigation", "performance"],
                success_criteria=[
                    "User satisfaction > 4.0/5.0",
                    "Reduced support tickets",
                    "Improved task completion rates",
                ],
                risk_assessment={
                    "probability": "low",
                    "impact": "low",
                    "mitigation": "A/B testing and user feedback",
                },
                status=ImprovementStatus.IDENTIFIED,
            )
            opportunities.append(opportunity)

        return opportunities

    def prioritize_opportunities(
        self,
        opportunities: List[ImprovementOpportunity],
        constraints: Dict[str, Any] = None,
    ) -> List[ImprovementOpportunity]:
        """Prioritize opportunities based on impact, effort, and constraints"""
        constraints = constraints or {}

        # Calculate priority scores
        for opp in opportunities:
            # Base priority from impact/effort ratio
            base_score = opp.impact_score / max(opp.effort_score, 1.0)

            # Apply constraints
            if constraints.get("max_effort", float("inf")) < opp.effort_score:
                base_score *= 0.5  # Penalize high-effort items

            if opp.type in constraints.get("priority_types", []):
                base_score *= 1.5  # Boost priority types

            if opp.type == IterationType.SECURITY_HARDENING:
                base_score *= 2.0  # Security is always high priority

            opp.priority_score = base_score

        # Sort by priority score (descending)
        return sorted(opportunities, key=lambda x: x.priority_score, reverse=True)

    async def create_iteration_cycle(
        self,
        project_id: str,
        opportunities: List[ImprovementOpportunity],
        cycle_duration_days: int = 14,
    ) -> IterationCycle:
        """Create new iteration cycle"""
        cycle_id = str(uuid4())
        cycle_number = (
            len([c for c in self.active_cycles.values() if c.project_id == project_id])
            + 1
        )

        start_date = datetime.now()
        target_end_date = start_date + timedelta(days=cycle_duration_days)

        # Select opportunities for this cycle
        selected_opps = opportunities[:3]  # Limit to top 3 for focus

        # Define objectives
        objectives = [
            "Improve system performance and reliability",
            "Enhance code quality and maintainability",
            "Address critical security and user experience issues",
        ]

        # Set baseline and target metrics
        baseline_metrics = await self._capture_baseline_metrics(project_id)
        target_metrics = self._define_target_metrics(selected_opps, baseline_metrics)

        cycle = IterationCycle(
            cycle_id=cycle_id,
            project_id=project_id,
            cycle_number=cycle_number,
            start_date=start_date,
            target_end_date=target_end_date,
            actual_end_date=None,
            objectives=objectives,
            selected_opportunities=[opp.opportunity_id for opp in selected_opps],
            baseline_metrics=baseline_metrics,
            target_metrics=target_metrics,
            actual_metrics={},
            status=ImprovementStatus.PLANNED,
            results={},
            lessons_learned=[],
        )

        # Store cycle in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO iteration_cycles
                (cycle_id, project_id, cycle_number, start_date, target_end_date,
                 objectives, selected_opportunities, baseline_metrics, 
                 target_metrics, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    cycle_id,
                    project_id,
                    cycle_number,
                    start_date.isoformat(),
                    target_end_date.isoformat(),
                    json.dumps(objectives),
                    json.dumps([opp.opportunity_id for opp in selected_opps]),
                    json.dumps(baseline_metrics),
                    json.dumps(target_metrics),
                    ImprovementStatus.PLANNED.value,
                ),
            )

        self.active_cycles[cycle_id] = cycle
        self.logger.info(f"Created iteration cycle {cycle_id} for project {project_id}")

        return cycle

    async def _capture_baseline_metrics(self, project_id: str) -> Dict[str, float]:
        """Capture baseline metrics for comparison"""
        # Simulate metric capture
        baseline = {
            "response_time_ms": 180.0,
            "throughput_rps": 120.0,
            "error_rate_percent": 0.5,
            "test_coverage_percent": 85.0,
            "code_complexity": 6.2,
            "security_score": 7.5,
            "user_satisfaction": 3.8,
        }

        # Store metrics snapshot
        with sqlite3.connect(self.db_path) as conn:
            for metric_name, value in baseline.items():
                conn.execute(
                    """
                    INSERT INTO metric_snapshots
                    (snapshot_id, project_id, metric_type, metric_name, 
                     metric_value, measurement_method)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        str(uuid4()),
                        project_id,
                        "baseline",
                        metric_name,
                        value,
                        "automated_capture",
                    ),
                )

        return baseline

    def _define_target_metrics(
        self, opportunities: List[ImprovementOpportunity], baseline: Dict[str, float]
    ) -> Dict[str, float]:
        """Define target metrics based on opportunities"""
        targets = baseline.copy()

        for opp in opportunities:
            if opp.type == IterationType.PERFORMANCE_OPTIMIZATION:
                targets["response_time_ms"] = min(
                    targets.get("response_time_ms", 200), 150
                )
                targets["throughput_rps"] = max(targets.get("throughput_rps", 100), 200)
            elif opp.type == IterationType.QUALITY_IMPROVEMENT:
                targets["test_coverage_percent"] = max(
                    targets.get("test_coverage_percent", 80), 90
                )
                targets["code_complexity"] = min(
                    targets.get("code_complexity", 10), 7.0
                )
            elif opp.type == IterationType.SECURITY_HARDENING:
                targets["security_score"] = max(targets.get("security_score", 5), 9.0)
            elif opp.type == IterationType.USER_EXPERIENCE:
                targets["user_satisfaction"] = max(
                    targets.get("user_satisfaction", 3), 4.0
                )

        return targets

    async def execute_iteration_cycle(self, cycle_id: str) -> Dict[str, Any]:
        """Execute iteration cycle"""
        if cycle_id not in self.active_cycles:
            raise ValueError(f"Cycle {cycle_id} not found")

        cycle = self.active_cycles[cycle_id]
        self.logger.info(f"Executing iteration cycle {cycle_id}")

        # Update status
        cycle.status = ImprovementStatus.IN_PROGRESS

        try:
            # Execute improvements for each selected opportunity
            results = {}
            for opp_id in cycle.selected_opportunities:
                opp_result = await self._execute_improvement(opp_id, cycle)
                results[opp_id] = opp_result

            # Capture final metrics
            final_metrics = await self._capture_final_metrics(
                cycle.project_id, cycle_id
            )
            cycle.actual_metrics = final_metrics

            # Analyze results
            analysis = self._analyze_cycle_results(cycle)
            cycle.results = analysis

            # Generate lessons learned
            lessons = self._extract_lessons_learned(cycle, results)
            cycle.lessons_learned = lessons

            # Update status
            cycle.status = ImprovementStatus.VALIDATED
            cycle.actual_end_date = datetime.now()

            # Update database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE iteration_cycles
                    SET status = ?, actual_end_date = ?, actual_metrics = ?,
                        results = ?, lessons_learned = ?
                    WHERE cycle_id = ?
                """,
                    (
                        cycle.status.value,
                        cycle.actual_end_date.isoformat(),
                        json.dumps(cycle.actual_metrics),
                        json.dumps(cycle.results),
                        json.dumps(cycle.lessons_learned),
                        cycle_id,
                    ),
                )

            self.logger.info(f"Iteration cycle {cycle_id} completed successfully")
            return {
                "cycle_id": cycle_id,
                "status": "completed",
                "results": cycle.results,
                "metrics_improvement": self._calculate_improvement_percentages(
                    cycle.baseline_metrics, cycle.actual_metrics
                ),
            }

        except Exception as e:
            cycle.status = ImprovementStatus.FAILED
            self.logger.error(f"Iteration cycle {cycle_id} failed: {str(e)}")
            raise

    async def _execute_improvement(
        self, opportunity_id: str, cycle: IterationCycle
    ) -> Dict[str, Any]:
        """Execute specific improvement"""
        # Simulate improvement execution
        await asyncio.sleep(0.1)

        return {
            "opportunity_id": opportunity_id,
            "status": "completed",
            "execution_time": 45.0,  # minutes
            "success_metrics": {"objectives_met": 3, "total_objectives": 3},
        }

    async def _capture_final_metrics(
        self, project_id: str, cycle_id: str
    ) -> Dict[str, float]:
        """Capture final metrics after improvements"""
        # Simulate improved metrics
        final = {
            "response_time_ms": 145.0,  # Improved
            "throughput_rps": 185.0,  # Improved
            "error_rate_percent": 0.3,  # Improved
            "test_coverage_percent": 92.0,  # Improved
            "code_complexity": 5.8,  # Improved
            "security_score": 8.5,  # Improved
            "user_satisfaction": 4.1,  # Improved
        }

        # Store final metrics
        with sqlite3.connect(self.db_path) as conn:
            for metric_name, value in final.items():
                conn.execute(
                    """
                    INSERT INTO metric_snapshots
                    (snapshot_id, project_id, cycle_id, metric_type, 
                     metric_name, metric_value, measurement_method)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        str(uuid4()),
                        project_id,
                        cycle_id,
                        "final",
                        metric_name,
                        value,
                        "automated_capture",
                    ),
                )

        return final

    def _analyze_cycle_results(self, cycle: IterationCycle) -> Dict[str, Any]:
        """Analyze iteration cycle results"""
        improvements = {}
        targets_met = 0
        total_targets = len(cycle.target_metrics)

        for metric, target in cycle.target_metrics.items():
            actual = cycle.actual_metrics.get(metric, 0)
            baseline = cycle.baseline_metrics.get(metric, 0)

            # Calculate improvement
            if baseline != 0:
                improvement_pct = ((actual - baseline) / baseline) * 100
            else:
                improvement_pct = 0

            improvements[metric] = {
                "baseline": baseline,
                "target": target,
                "actual": actual,
                "improvement_percent": improvement_pct,
                "target_met": self._is_target_met(metric, target, actual),
            }

            if improvements[metric]["target_met"]:
                targets_met += 1

        return {
            "targets_met": targets_met,
            "total_targets": total_targets,
            "success_rate": (targets_met / total_targets) * 100,
            "metric_improvements": improvements,
            "overall_grade": self._calculate_overall_grade(improvements),
        }

    def _is_target_met(self, metric_name: str, target: float, actual: float) -> bool:
        """Check if target was met for specific metric"""
        # Different metrics have different improvement directions
        if metric_name in ["response_time_ms", "error_rate_percent", "code_complexity"]:
            return actual <= target  # Lower is better
        else:
            return actual >= target  # Higher is better

    def _calculate_overall_grade(self, improvements: Dict[str, Any]) -> str:
        """Calculate overall grade for the cycle"""
        met_count = sum(1 for imp in improvements.values() if imp["target_met"])
        total_count = len(improvements)

        if total_count == 0:
            return "N/A"

        success_rate = (met_count / total_count) * 100

        if success_rate >= 90:
            return "A"
        elif success_rate >= 80:
            return "B"
        elif success_rate >= 70:
            return "C"
        elif success_rate >= 60:
            return "D"
        else:
            return "F"

    def _extract_lessons_learned(
        self, cycle: IterationCycle, results: Dict[str, Any]
    ) -> List[str]:
        """Extract lessons learned from cycle execution"""
        lessons = []

        # Analyze success patterns
        if cycle.results.get("success_rate", 0) >= 80:
            lessons.append(
                "High success rate achieved through focused improvement selection"
            )
            lessons.append(
                "Performance optimizations showed immediate measurable impact"
            )

        # Analyze failure patterns
        if cycle.results.get("success_rate", 0) < 60:
            lessons.append(
                "Consider reducing scope or extending timeline for complex improvements"
            )
            lessons.append("Better estimation needed for effort assessment")

        # Generic lessons
        lessons.extend(
            [
                "Continuous measurement is critical for tracking progress",
                "Small, focused improvements are more manageable than large changes",
                "Security improvements should always be prioritized",
            ]
        )

        return lessons

    def _calculate_improvement_percentages(
        self, baseline: Dict[str, float], actual: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate improvement percentages"""
        improvements = {}

        for metric, base_value in baseline.items():
            actual_value = actual.get(metric, base_value)

            if base_value != 0:
                improvement = ((actual_value - base_value) / base_value) * 100
            else:
                improvement = 0

            improvements[metric] = improvement

        return improvements

    def get_cycle_status(self, cycle_id: str) -> Dict[str, Any]:
        """Get current status of iteration cycle"""
        if cycle_id not in self.active_cycles:
            return {"error": "Cycle not found"}

        cycle = self.active_cycles[cycle_id]

        return {
            "cycle_id": cycle_id,
            "project_id": cycle.project_id,
            "cycle_number": cycle.cycle_number,
            "status": cycle.status.value,
            "progress": self._calculate_cycle_progress(cycle),
            "objectives": cycle.objectives,
            "selected_opportunities": len(cycle.selected_opportunities),
            "start_date": cycle.start_date.isoformat(),
            "target_end_date": cycle.target_end_date.isoformat(),
            "days_remaining": (cycle.target_end_date - datetime.now()).days,
        }

    def _calculate_cycle_progress(self, cycle: IterationCycle) -> float:
        """Calculate cycle progress percentage"""
        if cycle.status == ImprovementStatus.PLANNED:
            return 0.0
        elif cycle.status == ImprovementStatus.IN_PROGRESS:
            # Estimate based on time elapsed
            total_duration = (cycle.target_end_date - cycle.start_date).total_seconds()
            elapsed = (datetime.now() - cycle.start_date).total_seconds()
            return min(90.0, (elapsed / total_duration) * 100)
        elif cycle.status in [ImprovementStatus.VALIDATED, ImprovementStatus.DEPLOYED]:
            return 100.0
        else:
            return 0.0


# CLI interface for testing
async def main():
    """Test iteration engine"""
    print("🔄 Testing Intelligent Iteration Engine...")

    # Initialize engine
    engine = IntelligentIterationEngine(".")

    # Create test project context
    project_id = "test_project_001"
    context = {
        "performance_metrics": {
            "avg_response_time_ms": 180,
            "requests_per_second": 120,
            "error_rate_percent": 0.5,
        },
        "code_quality": {
            "test_coverage_percent": 85,
            "cyclomatic_complexity": 6.2,
            "maintainability_index": 75,
        },
        "security": {"known_vulnerabilities": 2, "security_score": 7.5},
        "user_experience": {"satisfaction_score": 3.8, "task_completion_rate": 82},
    }

    # Analyze for improvements
    print("🔍 Analyzing project for improvement opportunities...")
    opportunities = await engine.analyze_project_for_improvements(project_id, context)
    print(f"   Found {len(opportunities)} opportunities")

    # Prioritize opportunities
    prioritized = engine.prioritize_opportunities(opportunities, {"max_effort": 7.0})
    print(f"   Top 3 priorities:")
    for i, opp in enumerate(prioritized[:3], 1):
        print(
            f"   {i}. {opp.title} (Impact: {opp.impact_score:.1f}, Priority: {opp.priority_score:.1f})"
        )

    # Create iteration cycle
    print("\n📋 Creating iteration cycle...")
    cycle = await engine.create_iteration_cycle(project_id, prioritized, 14)
    print(f"   Cycle ID: {cycle.cycle_id}")
    print(
        f"   Duration: {cycle.start_date.strftime('%Y-%m-%d')} to {cycle.target_end_date.strftime('%Y-%m-%d')}"
    )
    print(f"   Selected {len(cycle.selected_opportunities)} improvements")

    # Execute cycle
    print("\n🚀 Executing iteration cycle...")
    result = await engine.execute_iteration_cycle(cycle.cycle_id)
    print(f"   Status: {result['status']}")
    print(f"   Success Rate: {result['results']['success_rate']:.1f}%")
    print(f"   Grade: {result['results']['overall_grade']}")

    # Show improvements
    print("\n📊 Metric Improvements:")
    for metric, improvement in result["metrics_improvement"].items():
        print(f"   {metric}: {improvement:+.1f}%")

    print("\n🎯 Intelligent Iteration Engine Ready!")


if __name__ == "__main__":
    asyncio.run(main())
