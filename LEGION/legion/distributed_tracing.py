"""
Distributed Tracing and Observability System
Implements OpenTelemetry-compatible tracing for agent operations
Follows IBM and QCOMP standards for enterprise observability
"""

import logging
import time
import json
import sqlite3
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from contextlib import contextmanager
import uuid
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class Span:
    """Represents a single unit of work in a trace"""
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: float
    end_time: Optional[float]
    duration_ms: Optional[float]
    status: str  # "success", "error", "running"
    tags: Dict[str, Any]
    logs: List[Dict[str, Any]]
    agent_id: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'span_id': self.span_id,
            'trace_id': self.trace_id,
            'parent_span_id': self.parent_span_id,
            'operation_name': self.operation_name,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration_ms': self.duration_ms,
            'status': self.status,
            'tags': self.tags,
            'logs': self.logs,
            'agent_id': self.agent_id
        }


@dataclass
class Trace:
    """Represents a complete distributed trace across agents"""
    trace_id: str
    root_span_id: str
    start_time: float
    end_time: Optional[float]
    total_duration_ms: Optional[float]
    spans: List[Span]
    tags: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'trace_id': self.trace_id,
            'root_span_id': self.root_span_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'total_duration_ms': self.total_duration_ms,
            'spans': [s.to_dict() for s in self.spans],
            'tags': self.tags
        }


class TracingSystem:
    """
    Enterprise-grade distributed tracing system
    Features:
    - Trace context propagation across agents
    - Span lifecycle management
    - Performance metrics collection
    - Error tracking and root cause analysis
    - Real-time monitoring dashboards
    """
    
    def __init__(self, db_path: str = "data/tracing.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Active spans (in-memory for fast access)
        self.active_spans: Dict[str, Span] = {}
        self.active_traces: Dict[str, Trace] = {}
        
        # Thread-local storage for current span context
        self.thread_local = threading.local()
        
        # Metrics
        self.metrics = {
            "total_traces": 0,
            "total_spans": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "average_duration_ms": 0.0,
            "p95_duration_ms": 0.0,
            "p99_duration_ms": 0.0
        }
        
        # Performance buckets
        self.duration_buckets = defaultdict(int)
        
        self._initialize_db()
        logger.info("Tracing system initialized")
    
    def _initialize_db(self):
        """Initialize SQLite database for trace persistence"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Traces table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS traces (
                trace_id TEXT PRIMARY KEY,
                root_span_id TEXT NOT NULL,
                start_time REAL NOT NULL,
                end_time REAL,
                total_duration_ms REAL,
                tags TEXT,
                status TEXT
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_start_time ON traces(start_time)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_duration_tr ON traces(total_duration_ms)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status_tr ON traces(status)')
        
        # Spans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS spans (
                span_id TEXT PRIMARY KEY,
                trace_id TEXT NOT NULL,
                parent_span_id TEXT,
                operation_name TEXT NOT NULL,
                start_time REAL NOT NULL,
                end_time REAL,
                duration_ms REAL,
                status TEXT NOT NULL,
                tags TEXT,
                logs TEXT,
                agent_id TEXT
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace ON spans(trace_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_operation ON spans(operation_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_tr ON spans(agent_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_duration_sp ON spans(duration_ms)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status_sp ON spans(status)')
        
        # Metrics snapshots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                total_traces INTEGER,
                total_spans INTEGER,
                successful_operations INTEGER,
                failed_operations INTEGER,
                average_duration_ms REAL,
                p95_duration_ms REAL,
                p99_duration_ms REAL
            )
        ''')
        
        # Performance alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                operation_name TEXT,
                agent_id TEXT,
                details TEXT,
                resolved INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Tracing database initialized")
    
    def start_trace(self, operation_name: str, tags: Dict[str, Any] = None) -> str:
        """
        Start a new distributed trace
        Returns trace_id
        """
        trace_id = str(uuid.uuid4())
        root_span_id = self.start_span(
            trace_id=trace_id,
            operation_name=operation_name,
            tags=tags
        )
        
        trace = Trace(
            trace_id=trace_id,
            root_span_id=root_span_id,
            start_time=time.time(),
            end_time=None,
            total_duration_ms=None,
            spans=[],
            tags=tags or {}
        )
        
        self.active_traces[trace_id] = trace
        self.metrics["total_traces"] += 1
        
        logger.debug(f"Started trace {trace_id} for operation {operation_name}")
        return trace_id
    
    def start_span(self, trace_id: str, operation_name: str, 
                   parent_span_id: str = None, tags: Dict[str, Any] = None,
                   agent_id: str = None) -> str:
        """
        Start a new span within a trace
        Returns span_id
        """
        span_id = str(uuid.uuid4())
        
        span = Span(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            start_time=time.time(),
            end_time=None,
            duration_ms=None,
            status="running",
            tags=tags or {},
            logs=[],
            agent_id=agent_id
        )
        
        self.active_spans[span_id] = span
        self.metrics["total_spans"] += 1
        
        # Set as current span in thread-local storage
        self.thread_local.current_span_id = span_id
        self.thread_local.current_trace_id = trace_id
        
        logger.debug(f"Started span {span_id} for operation {operation_name}")
        return span_id
    
    def end_span(self, span_id: str, status: str = "success", error: str = None):
        """End a span and calculate duration"""
        if span_id not in self.active_spans:
            logger.warning(f"Span {span_id} not found in active spans")
            return
        
        span = self.active_spans[span_id]
        span.end_time = time.time()
        span.duration_ms = (span.end_time - span.start_time) * 1000
        span.status = status
        
        if error:
            span.tags['error'] = error
            self.metrics["failed_operations"] += 1
        else:
            self.metrics["successful_operations"] += 1
        
        # Update duration metrics
        self._update_duration_metrics(span.duration_ms)
        
        # Check for performance issues
        self._check_performance_alerts(span)
        
        # Persist span
        self._persist_span(span)
        
        # Add to trace
        if span.trace_id in self.active_traces:
            self.active_traces[span.trace_id].spans.append(span)
        
        # Remove from active spans
        del self.active_spans[span_id]
        
        logger.debug(f"Ended span {span_id} with status {status} (duration: {span.duration_ms:.2f}ms)")
    
    def end_trace(self, trace_id: str):
        """End a trace and calculate total duration"""
        if trace_id not in self.active_traces:
            logger.warning(f"Trace {trace_id} not found in active traces")
            return
        
        trace = self.active_traces[trace_id]
        trace.end_time = time.time()
        trace.total_duration_ms = (trace.end_time - trace.start_time) * 1000
        
        # Persist trace
        self._persist_trace(trace)
        
        # Remove from active traces
        del self.active_traces[trace_id]
        
        logger.debug(f"Ended trace {trace_id} (duration: {trace.total_duration_ms:.2f}ms)")
    
    @contextmanager
    def trace_operation(self, operation_name: str, tags: Dict[str, Any] = None,
                       agent_id: str = None):
        """
        Context manager for tracing an operation
        Usage:
            with tracing.trace_operation("process_task", {"task_id": "123"}):
                # Your code here
        """
        # Get current trace context or start new trace
        if hasattr(self.thread_local, 'current_trace_id'):
            trace_id = self.thread_local.current_trace_id
            parent_span_id = getattr(self.thread_local, 'current_span_id', None)
            span_id = self.start_span(trace_id, operation_name, parent_span_id, tags, agent_id)
        else:
            trace_id = self.start_trace(operation_name, tags)
            span_id = self.thread_local.current_span_id
        
        try:
            yield span_id
            self.end_span(span_id, status="success")
        except Exception as e:
            self.end_span(span_id, status="error", error=str(e))
            raise
    
    def add_span_log(self, span_id: str, level: str, message: str, data: Dict[str, Any] = None):
        """Add a log entry to a span"""
        if span_id not in self.active_spans:
            return
        
        log_entry = {
            "timestamp": time.time(),
            "level": level,
            "message": message,
            "data": data or {}
        }
        
        self.active_spans[span_id].logs.append(log_entry)
    
    def add_span_tag(self, span_id: str, key: str, value: Any):
        """Add a tag to a span"""
        if span_id not in self.active_spans:
            return
        
        self.active_spans[span_id].tags[key] = value
    
    def get_current_trace_id(self) -> Optional[str]:
        """Get current trace ID from thread-local storage"""
        return getattr(self.thread_local, 'current_trace_id', None)
    
    def get_current_span_id(self) -> Optional[str]:
        """Get current span ID from thread-local storage"""
        return getattr(self.thread_local, 'current_span_id', None)
    
    def _persist_span(self, span: Span):
        """Persist span to database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO spans 
                (span_id, trace_id, parent_span_id, operation_name, start_time, end_time,
                 duration_ms, status, tags, logs, agent_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                span.span_id,
                span.trace_id,
                span.parent_span_id,
                span.operation_name,
                span.start_time,
                span.end_time,
                span.duration_ms,
                span.status,
                json.dumps(span.tags),
                json.dumps(span.logs),
                span.agent_id
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to persist span {span.span_id}: {e}")
    
    def _persist_trace(self, trace: Trace):
        """Persist trace to database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Determine overall trace status
            status = "success"
            for span in trace.spans:
                if span.status == "error":
                    status = "error"
                    break
            
            cursor.execute('''
                INSERT INTO traces 
                (trace_id, root_span_id, start_time, end_time, total_duration_ms, tags, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                trace.trace_id,
                trace.root_span_id,
                trace.start_time,
                trace.end_time,
                trace.total_duration_ms,
                json.dumps(trace.tags),
                status
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to persist trace {trace.trace_id}: {e}")
    
    def _update_duration_metrics(self, duration_ms: float):
        """Update duration metrics with new measurement"""
        # Update average
        total_ops = self.metrics["successful_operations"] + self.metrics["failed_operations"]
        current_avg = self.metrics["average_duration_ms"]
        self.metrics["average_duration_ms"] = (current_avg * (total_ops - 1) + duration_ms) / total_ops
        
        # Update duration buckets for percentile calculations
        bucket = int(duration_ms // 100) * 100  # Round to nearest 100ms
        self.duration_buckets[bucket] += 1
        
        # Calculate percentiles
        self._calculate_percentiles()
    
    def _calculate_percentiles(self):
        """Calculate P95 and P99 latencies"""
        if not self.duration_buckets:
            return
        
        total_count = sum(self.duration_buckets.values())
        p95_count = total_count * 0.95
        p99_count = total_count * 0.99
        
        cumulative = 0
        p95_found = False
        p99_found = False
        
        for bucket in sorted(self.duration_buckets.keys()):
            cumulative += self.duration_buckets[bucket]
            
            if not p95_found and cumulative >= p95_count:
                self.metrics["p95_duration_ms"] = bucket
                p95_found = True
            
            if cumulative >= p99_count:
                self.metrics["p99_duration_ms"] = bucket
                break
    
    def _check_performance_alerts(self, span: Span):
        """Check for performance issues and create alerts"""
        alerts = []
        
        # Check for slow operations (> 5 seconds)
        if span.duration_ms > 5000:
            alerts.append({
                "alert_type": "slow_operation",
                "severity": "warning",
                "operation_name": span.operation_name,
                "agent_id": span.agent_id,
                "details": f"Operation took {span.duration_ms:.2f}ms"
            })
        
        # Check for very slow operations (> 30 seconds)
        if span.duration_ms > 30000:
            alerts.append({
                "alert_type": "very_slow_operation",
                "severity": "critical",
                "operation_name": span.operation_name,
                "agent_id": span.agent_id,
                "details": f"Operation took {span.duration_ms:.2f}ms"
            })
        
        # Check for errors
        if span.status == "error":
            alerts.append({
                "alert_type": "operation_error",
                "severity": "error",
                "operation_name": span.operation_name,
                "agent_id": span.agent_id,
                "details": span.tags.get('error', 'Unknown error')
            })
        
        # Persist alerts
        if alerts:
            self._persist_alerts(alerts)
    
    def _persist_alerts(self, alerts: List[Dict[str, Any]]):
        """Persist performance alerts to database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            for alert in alerts:
                cursor.execute('''
                    INSERT INTO performance_alerts 
                    (timestamp, alert_type, severity, operation_name, agent_id, details)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    time.time(),
                    alert['alert_type'],
                    alert['severity'],
                    alert['operation_name'],
                    alert['agent_id'],
                    alert['details']
                ))
                
                logger.warning(f"Performance alert: {alert['alert_type']} - {alert['details']}")
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to persist alerts: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current tracing metrics"""
        return {
            **self.metrics,
            "active_traces": len(self.active_traces),
            "active_spans": len(self.active_spans)
        }
    
    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get a complete trace with all spans"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get trace
            cursor.execute('SELECT * FROM traces WHERE trace_id = ?', (trace_id,))
            trace_row = cursor.fetchone()
            
            if not trace_row:
                conn.close()
                return None
            
            # Get all spans for trace
            cursor.execute('SELECT * FROM spans WHERE trace_id = ? ORDER BY start_time', (trace_id,))
            span_rows = cursor.fetchall()
            
            conn.close()
            
            spans = []
            for row in span_rows:
                spans.append({
                    'span_id': row[0],
                    'trace_id': row[1],
                    'parent_span_id': row[2],
                    'operation_name': row[3],
                    'start_time': row[4],
                    'end_time': row[5],
                    'duration_ms': row[6],
                    'status': row[7],
                    'tags': json.loads(row[8]) if row[8] else {},
                    'logs': json.loads(row[9]) if row[9] else [],
                    'agent_id': row[10]
                })
            
            return {
                'trace_id': trace_row[0],
                'root_span_id': trace_row[1],
                'start_time': trace_row[2],
                'end_time': trace_row[3],
                'total_duration_ms': trace_row[4],
                'tags': json.loads(trace_row[5]) if trace_row[5] else {},
                'status': trace_row[6],
                'spans': spans
            }
            
        except Exception as e:
            logger.error(f"Failed to get trace {trace_id}: {e}")
            return None
    
    def get_slow_operations(self, threshold_ms: float = 1000, limit: int = 100) -> List[Dict[str, Any]]:
        """Get operations slower than threshold"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT operation_name, agent_id, AVG(duration_ms) as avg_duration, 
                       COUNT(*) as count, MIN(duration_ms) as min_duration, 
                       MAX(duration_ms) as max_duration
                FROM spans
                WHERE duration_ms > ?
                GROUP BY operation_name, agent_id
                ORDER BY avg_duration DESC
                LIMIT ?
            ''', (threshold_ms, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'operation_name': row[0],
                    'agent_id': row[1],
                    'avg_duration_ms': row[2],
                    'count': row[3],
                    'min_duration_ms': row[4],
                    'max_duration_ms': row[5]
                })
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Failed to get slow operations: {e}")
            return []
    
    def get_error_rate(self, operation_name: str = None, hours: int = 24) -> Dict[str, Any]:
        """Get error rate for operations"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cutoff_time = time.time() - (hours * 3600)
            
            if operation_name:
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as errors
                    FROM spans
                    WHERE operation_name = ? AND start_time > ?
                ''', (operation_name, cutoff_time))
            else:
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as errors
                    FROM spans
                    WHERE start_time > ?
                ''', (cutoff_time,))
            
            row = cursor.fetchone()
            conn.close()
            
            total = row[0] if row else 0
            errors = row[1] if row else 0
            error_rate = (errors / total * 100) if total > 0 else 0
            
            return {
                'operation_name': operation_name or 'all',
                'total_operations': total,
                'errors': errors,
                'error_rate_percent': error_rate,
                'time_window_hours': hours
            }
            
        except Exception as e:
            logger.error(f"Failed to get error rate: {e}")
            return {}


# Global tracing system instance
tracing_system = TracingSystem()
