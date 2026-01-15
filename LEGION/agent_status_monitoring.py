#!/usr/bin/env python3
"""
Agent Status Monitoring Utilities - Production Configuration
Real-time monitoring, health checking, and status tracking for Enterprise Legion agents
Enhanced with performance monitoring and alerting
"""

import asyncio
import json
import sqlite3
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging
import psutil

# Configure production logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agent_monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AgentStatusMonitor")

# Performance monitoring configuration
PERFORMANCE_MONITORING_ENABLED = (
    os.getenv('PERFORMANCE_MONITORING', 'true').lower() == 'true'
)
METRICS_COLLECTION_INTERVAL = int(
    os.getenv('METRICS_COLLECTION_INTERVAL', '30')
)  # seconds
ALERT_THRESHOLD_CPU = float(os.getenv('ALERT_THRESHOLD_CPU', '80.0'))
ALERT_THRESHOLD_MEMORY = float(os.getenv('ALERT_THRESHOLD_MEMORY', '85.0'))
ALERT_THRESHOLD_RESPONSE_TIME = float(
    os.getenv('ALERT_THRESHOLD_RESPONSE_TIME', '5000.0')
)  # ms


@dataclass
class SystemPerformanceMetrics:
    """System-wide performance metrics"""
    timestamp: datetime
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    network_io_bytes: Tuple[int, int]  # (bytes_sent, bytes_received)
    active_agents: int
    total_requests: int
    error_rate: float
    average_response_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "cpu_usage_percent": self.cpu_usage_percent,
            "memory_usage_percent": self.memory_usage_percent,
            "disk_usage_percent": self.disk_usage_percent,
            "network_bytes_sent": self.network_io_bytes[0],
            "network_bytes_received": self.network_io_bytes[1],
            "active_agents": self.active_agents,
            "total_requests": self.total_requests,
            "error_rate": self.error_rate,
            "average_response_time": self.average_response_time
        }


class PerformanceMonitor:
    """System performance monitoring and alerting"""
    
    def __init__(self):
        self.enabled = PERFORMANCE_MONITORING_ENABLED
        self.metrics_history = []
        self.alert_callbacks = []
        self.last_network_io = None
        
    def collect_system_metrics(self) -> SystemPerformanceMetrics:
        """Collect current system performance metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network I/O
        network_io = psutil.net_io_counters()
        network_bytes = (network_io.bytes_sent, network_io.bytes_recv)
        
        return SystemPerformanceMetrics(
            timestamp=datetime.now(),
            cpu_usage_percent=cpu_percent,
            memory_usage_percent=memory.percent,
            disk_usage_percent=disk.percent,
            network_io_bytes=network_bytes,
            active_agents=0,  # Will be updated by agent monitor
            total_requests=0,  # Will be updated by API monitor
            error_rate=0.0,  # Will be updated by error monitor
            average_response_time=0.0  # Will be updated by response monitor
        )
    
    def check_performance_alerts(self, metrics: SystemPerformanceMetrics):
        """Check for performance threshold violations and trigger alerts"""
        alerts = []
        
        if metrics.cpu_usage_percent > ALERT_THRESHOLD_CPU:
            alerts.append({
                'type': 'cpu_high',
                'severity': 'warning',
                'message': f'CPU usage high: {metrics.cpu_usage_percent:.1f}%',
                'threshold': ALERT_THRESHOLD_CPU,
                'current': metrics.cpu_usage_percent
            })
        
        if metrics.memory_usage_percent > ALERT_THRESHOLD_MEMORY:
            alerts.append({
                'type': 'memory_high',
                'severity': 'warning',
                'message': (f'Memory usage high: '
                           f'{metrics.memory_usage_percent:.1f}%'),
                'threshold': ALERT_THRESHOLD_MEMORY,
                'current': metrics.memory_usage_percent
            })
        
        if metrics.average_response_time > ALERT_THRESHOLD_RESPONSE_TIME:
            alerts.append({
                'type': 'response_time_high',
                'severity': 'warning',
                'message': (f'Response time high: '
                           f'{metrics.average_response_time:.1f}ms'),
                'threshold': ALERT_THRESHOLD_RESPONSE_TIME,
                'current': metrics.average_response_time
            })
        
        # Trigger alert callbacks
        for alert in alerts:
            self._trigger_alert(alert)
            
        return alerts
    
    def _trigger_alert(self, alert: Dict[str, Any]):
        """Trigger alert notifications"""
        logger.warning(f"PERFORMANCE ALERT: {alert['message']}")
        
        # Call registered alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
    
    def start_monitoring(self):
        """Start continuous performance monitoring"""
        if not self.enabled:
            logger.info("Performance monitoring disabled")
            return
        
        async def monitor_loop():
            while self.enabled:
                try:
                    metrics = self.collect_system_metrics()
                    self.metrics_history.append(metrics)
                    
                    # Keep only last 1000 metrics (for memory management)
                    if len(self.metrics_history) > 1000:
                        self.metrics_history.pop(0)
                    
                    # Check for alerts
                    self.check_performance_alerts(metrics)
                    
                    await asyncio.sleep(METRICS_COLLECTION_INTERVAL)
                    
                except Exception as e:
                    logger.error(f"Performance monitoring error: {e}")
                    await asyncio.sleep(60)  # Wait longer on error
        
        # Start monitoring in background
        asyncio.create_task(monitor_loop())
        interval_msg = f"Performance monitoring started (interval: {METRICS_COLLECTION_INTERVAL}s)"
        logger.info(interval_msg)


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


@dataclass
class AgentStatus:
    """Agent status data structure"""
    agent_id: str
    agent_type: str
    department: str
    status: str  # active, inactive, error, maintenance
    health_score: float  # 0.0 to 1.0
    last_heartbeat: datetime
    response_time_ms: float
    tasks_in_queue: int
    messages_processed: int
    memory_usage_mb: float
    cpu_usage_percent: float
    error_count: int
    uptime_seconds: int
    capabilities: List[str]
    current_task: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "department": self.department,
            "status": self.status,
            "health_score": self.health_score,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "response_time_ms": self.response_time_ms,
            "tasks_in_queue": self.tasks_in_queue,
            "messages_processed": self.messages_processed,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent,
            "error_count": self.error_count,
            "uptime_seconds": self.uptime_seconds,
            "capabilities": self.capabilities,
            "current_task": self.current_task
        }

@dataclass
class DepartmentStatus:
    """Department-level status aggregation"""
    department: str
    total_agents: int
    active_agents: int
    inactive_agents: int
    error_agents: int
    avg_health_score: float
    avg_response_time: float
    total_tasks_queued: int
    total_messages_processed: int
    avg_cpu_usage: float
    avg_memory_usage: float

class AgentStatusMonitor:
    """Real-time agent status monitoring system"""
    
    def __init__(self, db_path: str = "data/enterprise_operations.db"):
        self.db_path = db_path
        self.agent_statuses: Dict[str, AgentStatus] = {}
        self.monitoring_active = False
        self.heartbeat_interval = 30  # seconds
        self.health_check_interval = 60  # seconds
        self.websocket_clients = set()
        
        # Performance monitoring integration
        self.performance_monitor = performance_monitor
        self.total_requests = 0
        self.error_count = 0
        self.response_times = []
        
        # Initialize database tables
        self._init_monitoring_tables()
        
    def _init_monitoring_tables(self):
        """Initialize monitoring database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Agent status snapshots table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_status_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    agent_type TEXT,
                    department TEXT,
                    status TEXT,
                    health_score REAL,
                    response_time_ms REAL,
                    tasks_in_queue INTEGER,
                    messages_processed INTEGER,
                    memory_usage_mb REAL,
                    cpu_usage_percent REAL,
                    error_count INTEGER,
                    uptime_seconds INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Agent health alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_health_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    alert_type TEXT,
                    severity TEXT,
                    message TEXT,
                    resolved BOOLEAN DEFAULT FALSE,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # System performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpu_usage_percent REAL,
                    memory_usage_percent REAL,
                    disk_usage_percent REAL,
                    network_bytes_sent INTEGER,
                    network_bytes_received INTEGER,
                    active_agents INTEGER,
                    total_requests INTEGER,
                    error_rate REAL,
                    average_response_time REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Monitoring database tables initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize monitoring tables: {e}")
    
    def update_performance_metrics(self, request_time: float = None, 
                                 error_occurred: bool = False):
        """Update performance metrics from agent operations"""
        self.total_requests += 1
        
        if error_occurred:
            self.error_count += 1
            
        if request_time is not None:
            self.response_times.append(request_time)
            # Keep only last 1000 response times for memory management
            if len(self.response_times) > 1000:
                self.response_times.pop(0)
        
        # Update performance monitor with latest metrics
        if hasattr(self.performance_monitor, 'metrics_history') and \
           self.performance_monitor.metrics_history:
            latest_metrics = self.performance_monitor.metrics_history[-1]
            latest_metrics.active_agents = len([
                status for status in self.agent_statuses.values() 
                if status.status == 'active'
            ])
            latest_metrics.total_requests = self.total_requests
            latest_metrics.error_rate = (
                (self.error_count / self.total_requests * 100) 
                if self.total_requests > 0 else 0.0
            )
            latest_metrics.average_response_time = (
                sum(self.response_times) / len(self.response_times) 
                if self.response_times else 0.0
            )
    
    def save_performance_metrics(self, metrics: SystemPerformanceMetrics):
        """Save performance metrics to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_performance_metrics (
                    cpu_usage_percent, memory_usage_percent, disk_usage_percent,
                    network_bytes_sent, network_bytes_received, active_agents,
                    total_requests, error_rate, average_response_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.cpu_usage_percent,
                metrics.memory_usage_percent,
                metrics.disk_usage_percent,
                metrics.network_io_bytes[0],
                metrics.network_io_bytes[1],
                metrics.active_agents,
                metrics.total_requests,
                metrics.error_rate,
                metrics.average_response_time
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save performance metrics: {e}")
    
    def get_performance_history(self, hours: int = 24) -> List[Dict]:
        """Get performance metrics history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since_time = datetime.now() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT * FROM system_performance_metrics
                WHERE timestamp > ?
                ORDER BY timestamp DESC
            ''', (since_time.isoformat(),))
            
            metrics = []
            for row in cursor.fetchall():
                metrics.append({
                    "id": row[0],
                    "cpu_usage_percent": row[1],
                    "memory_usage_percent": row[2],
                    "disk_usage_percent": row[3],
                    "network_bytes_sent": row[4],
                    "network_bytes_received": row[5],
                    "active_agents": row[6],
                    "total_requests": row[7],
                    "error_rate": row[8],
                    "average_response_time": row[9],
                    "timestamp": row[10]
                })
            
            conn.close()
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get performance history: {e}")
            return []
    
    async def start_monitoring(self):
        """Start the agent monitoring system"""
        self.monitoring_active = True
        logger.info("Starting agent status monitoring system...")
        
        # Start performance monitoring
        if self.performance_monitor.enabled:
            self.performance_monitor.start_monitoring()
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._heartbeat_monitor()),
            asyncio.create_task(self._health_check_monitor()),
            asyncio.create_task(self._performance_collector()),
            asyncio.create_task(self._alert_processor()),
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop_monitoring(self):
        """Stop the monitoring system"""
        self.monitoring_active = False
        logger.info("Agent status monitoring system stopped")
    
    async def _heartbeat_monitor(self):
        """Monitor agent heartbeats"""
        while self.monitoring_active:
            try:
                await self._collect_heartbeats()
                await asyncio.sleep(self.heartbeat_interval)
            except Exception as e:
                logger.error(f"Heartbeat monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def _health_check_monitor(self):
        """Perform periodic health checks"""
        while self.monitoring_active:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(10)
    
    async def _performance_collector(self):
        """Collect performance metrics"""
        while self.monitoring_active:
            try:
                await self._collect_performance_metrics()
                await asyncio.sleep(30)  # Collect every 30 seconds
            except Exception as e:
                logger.error(f"Performance collection error: {e}")
                await asyncio.sleep(5)
    
    async def _alert_processor(self):
        """Process and generate alerts"""
        while self.monitoring_active:
            try:
                await self._process_alerts()
                await asyncio.sleep(15)  # Check for alerts every 15 seconds
            except Exception as e:
                logger.error(f"Alert processing error: {e}")
                await asyncio.sleep(5)
    
    async def _collect_heartbeats(self):
        """Collect heartbeats from all known agents"""
        # In a real implementation, this would ping each agent
        # For now, we'll simulate based on the agent catalog
        known_agents = await self._get_known_agents()
        
        for agent_info in known_agents:
            agent_id = agent_info['agent_id']
            try:
                # Simulate heartbeat response
                response_time = await self._ping_agent(agent_id)
                
                if response_time is not None:
                    # Agent responded - update status
                    await self._update_agent_heartbeat(agent_id, response_time)
                else:
                    # Agent didn't respond - mark as potentially inactive
                    await self._handle_missed_heartbeat(agent_id)
                    
            except Exception as e:
                logger.error(f"Failed to collect heartbeat for {agent_id}: {e}")
    
    async def _ping_agent(self, agent_id: str) -> Optional[float]:
        """Ping an agent and return response time in ms"""
        # This is a simulation - in reality would ping actual agent endpoints
        try:
            start_time = time.time()
            # Simulate agent response (replace with actual agent ping)
            await asyncio.sleep(0.01)  # Simulate 10ms response time
            end_time = time.time()
            return (end_time - start_time) * 1000
        except:
            return None
    
    async def _get_known_agents(self) -> List[Dict[str, Any]]:
        """Get list of known agents from agent catalog"""
        # This would typically query the agent registry
        # For now, return simulated data based on our agent catalog
        return [
            {"agent_id": "task_scheduler", "agent_type": "TaskSchedulingAgent", "department": "automation"},
            {"agent_id": "workflow_orchestrator", "agent_type": "WorkflowOrchestrationAgent", "department": "automation"},
            {"agent_id": "resource_optimizer", "agent_type": "ResourceOptimizationAgent", "department": "automation"},
            {"agent_id": "financial_analyst", "agent_type": "FinancialAnalysisAgent", "department": "finance"},
            {"agent_id": "financial_modeler", "agent_type": "FinancialModelingAgent", "department": "finance"},
            {"agent_id": "quality_assurance", "agent_type": "QualityAssuranceAgent", "department": "finance"},
            {"agent_id": "report_generator", "agent_type": "ReportGenerationAgent", "department": "finance"},
            {"agent_id": "content_writer", "agent_type": "ContentWritingAgent", "department": "communication"},
            {"agent_id": "social_media_monitor", "agent_type": "SocialMediaMonitoringAgent", "department": "communication"},
        ]
    
    async def _update_agent_heartbeat(self, agent_id: str, response_time: float):
        """Update agent heartbeat status"""
        now = datetime.now()
        
        if agent_id not in self.agent_statuses:
            # Initialize agent status
            agent_info = await self._get_agent_info(agent_id)
            self.agent_statuses[agent_id] = AgentStatus(
                agent_id=agent_id,
                agent_type=agent_info.get("agent_type", "Unknown"),
                department=agent_info.get("department", "unknown"),
                status="active",
                health_score=1.0,
                last_heartbeat=now,
                response_time_ms=response_time,
                tasks_in_queue=0,
                messages_processed=0,
                memory_usage_mb=0.0,
                cpu_usage_percent=0.0,
                error_count=0,
                uptime_seconds=0,
                capabilities=agent_info.get("capabilities", [])
            )
        else:
            # Update existing status
            status = self.agent_statuses[agent_id]
            status.last_heartbeat = now
            status.response_time_ms = response_time
            status.status = "active"
            status.health_score = min(1.0, status.health_score + 0.1)  # Improve health on successful heartbeat
        
        # Broadcast status update
        await self._broadcast_status_update(agent_id)
    
    async def _handle_missed_heartbeat(self, agent_id: str):
        """Handle missed heartbeat from agent"""
        if agent_id in self.agent_statuses:
            status = self.agent_statuses[agent_id]
            time_since_heartbeat = datetime.now() - status.last_heartbeat
            
            if time_since_heartbeat > timedelta(minutes=2):
                status.status = "inactive"
                status.health_score = max(0.0, status.health_score - 0.2)
                
                # Generate alert
                await self._generate_alert(
                    agent_id, 
                    "heartbeat_missed", 
                    "warning",
                    f"Agent {agent_id} missed heartbeat for {time_since_heartbeat}"
                )
    
    async def _perform_health_checks(self):
        """Perform comprehensive health checks on all agents"""
        for agent_id, status in self.agent_statuses.items():
            try:
                health_score = await self._calculate_health_score(agent_id, status)
                status.health_score = health_score
                
                # Update database snapshot
                await self._store_status_snapshot(status)
                
            except Exception as e:
                logger.error(f"Health check failed for {agent_id}: {e}")
    
    async def _calculate_health_score(self, agent_id: str, status: AgentStatus) -> float:
        """Calculate comprehensive health score for agent"""
        score = 1.0
        
        # Response time factor (lower is better)
        if status.response_time_ms > 1000:  # >1 second is concerning
            score -= 0.2
        elif status.response_time_ms > 500:  # >500ms is suboptimal
            score -= 0.1
        
        # Heartbeat freshness factor
        time_since_heartbeat = datetime.now() - status.last_heartbeat
        if time_since_heartbeat > timedelta(minutes=2):
            score -= 0.3
        elif time_since_heartbeat > timedelta(minutes=1):
            score -= 0.1
        
        # Error count factor
        if status.error_count > 10:
            score -= 0.2
        elif status.error_count > 5:
            score -= 0.1
        
        # Queue backup factor
        if status.tasks_in_queue > 100:
            score -= 0.2
        elif status.tasks_in_queue > 50:
            score -= 0.1
        
        # Resource usage factor
        if status.cpu_usage_percent > 90:
            score -= 0.2
        elif status.cpu_usage_percent > 70:
            score -= 0.1
        
        if status.memory_usage_mb > 1000:  # >1GB
            score -= 0.2
        elif status.memory_usage_mb > 500:  # >500MB
            score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    async def _collect_performance_metrics(self):
        """Collect performance metrics from agents"""
        # This would query actual agent performance APIs
        # For now, simulate realistic performance data
        import random
        
        for agent_id in self.agent_statuses:
            status = self.agent_statuses[agent_id]
            
            # Simulate realistic metrics
            status.tasks_in_queue = random.randint(0, 20)
            status.messages_processed += random.randint(0, 10)
            status.memory_usage_mb = random.uniform(50, 200)
            status.cpu_usage_percent = random.uniform(5, 30)
            status.uptime_seconds += 30  # Monitoring interval
    
    async def _process_alerts(self):
        """Process and generate system alerts"""
        critical_agents = []
        warning_agents = []
        
        for agent_id, status in self.agent_statuses.items():
            if status.health_score < 0.3:
                critical_agents.append(agent_id)
            elif status.health_score < 0.7:
                warning_agents.append(agent_id)
        
        # Generate alerts for critical agents
        for agent_id in critical_agents:
            await self._generate_alert(
                agent_id, 
                "health_critical", 
                "critical",
                f"Agent {agent_id} health score critically low: {self.agent_statuses[agent_id].health_score:.2f}"
            )
        
        # Generate alerts for warning agents
        for agent_id in warning_agents:
            await self._generate_alert(
                agent_id, 
                "health_warning", 
                "warning",
                f"Agent {agent_id} health score low: {self.agent_statuses[agent_id].health_score:.2f}"
            )
    
    async def _generate_alert(self, agent_id: str, alert_type: str, severity: str, message: str):
        """Generate and store system alert"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO agent_health_alerts (agent_id, alert_type, severity, message)
                VALUES (?, ?, ?, ?)
            ''', (agent_id, alert_type, severity, message))
            
            conn.commit()
            conn.close()
            
            logger.warning(f"Alert generated: {severity.upper()} - {agent_id}: {message}")
            
            # Broadcast alert
            await self._broadcast_alert({
                "agent_id": agent_id,
                "alert_type": alert_type,
                "severity": severity,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to generate alert: {e}")
    
    async def _store_status_snapshot(self, status: AgentStatus):
        """Store agent status snapshot in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO agent_status_snapshots (
                    agent_id, agent_type, department, status, health_score,
                    response_time_ms, tasks_in_queue, messages_processed,
                    memory_usage_mb, cpu_usage_percent, error_count, uptime_seconds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                status.agent_id, status.agent_type, status.department, status.status,
                status.health_score, status.response_time_ms, status.tasks_in_queue,
                status.messages_processed, status.memory_usage_mb, status.cpu_usage_percent,
                status.error_count, status.uptime_seconds
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store status snapshot: {e}")
    
    async def _get_agent_info(self, agent_id: str) -> Dict[str, Any]:
        """Get agent information"""
        # This would query the agent registry
        # For now, return simulated data
        agent_map = {
            "task_scheduler": {"agent_type": "TaskSchedulingAgent", "department": "automation", "capabilities": ["scheduling", "task_management"]},
            "workflow_orchestrator": {"agent_type": "WorkflowOrchestrationAgent", "department": "automation", "capabilities": ["orchestration", "coordination"]},
            "financial_analyst": {"agent_type": "FinancialAnalysisAgent", "department": "finance", "capabilities": ["financial_analysis", "reporting"]},
        }
        return agent_map.get(agent_id, {"agent_type": "Unknown", "department": "unknown", "capabilities": []})
    
    async def _broadcast_status_update(self, agent_id: str):
        """Broadcast status update to WebSocket clients"""
        if self.websocket_clients:
            status = self.agent_statuses[agent_id]
            message = json.dumps({
                "type": "agent_status_update",
                "data": status.to_dict()
            })
            
            # Send to all connected WebSocket clients
            for client in self.websocket_clients.copy():
                try:
                    await client.send(message)
                except:
                    self.websocket_clients.discard(client)
    
    async def _broadcast_alert(self, alert_data: Dict[str, Any]):
        """Broadcast alert to WebSocket clients"""
        if self.websocket_clients:
            message = json.dumps({
                "type": "agent_alert",
                "data": alert_data
            })
            
            for client in self.websocket_clients.copy():
                try:
                    await client.send(message)
                except:
                    self.websocket_clients.discard(client)
    
    # Public API methods
    
    def get_agent_status(self, agent_id: str) -> Optional[AgentStatus]:
        """Get current status of specific agent"""
        return self.agent_statuses.get(agent_id)
    
    def get_all_agent_statuses(self) -> Dict[str, AgentStatus]:
        """Get status of all monitored agents"""
        return self.agent_statuses.copy()
    
    def get_department_status(self, department: str) -> DepartmentStatus:
        """Get aggregated status for a department"""
        department_agents = [s for s in self.agent_statuses.values() if s.department == department]
        
        if not department_agents:
            return DepartmentStatus(
                department=department,
                total_agents=0,
                active_agents=0,
                inactive_agents=0,
                error_agents=0,
                avg_health_score=0.0,
                avg_response_time=0.0,
                total_tasks_queued=0,
                total_messages_processed=0,
                avg_cpu_usage=0.0,
                avg_memory_usage=0.0
            )
        
        active_count = sum(1 for s in department_agents if s.status == "active")
        inactive_count = sum(1 for s in department_agents if s.status == "inactive")
        error_count = sum(1 for s in department_agents if s.status == "error")
        
        return DepartmentStatus(
            department=department,
            total_agents=len(department_agents),
            active_agents=active_count,
            inactive_agents=inactive_count,
            error_agents=error_count,
            avg_health_score=sum(s.health_score for s in department_agents) / len(department_agents),
            avg_response_time=sum(s.response_time_ms for s in department_agents) / len(department_agents),
            total_tasks_queued=sum(s.tasks_in_queue for s in department_agents),
            total_messages_processed=sum(s.messages_processed for s in department_agents),
            avg_cpu_usage=sum(s.cpu_usage_percent for s in department_agents) / len(department_agents),
            avg_memory_usage=sum(s.memory_usage_mb for s in department_agents) / len(department_agents)
        )
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        if not self.agent_statuses:
            return {
                "total_agents": 0,
                "healthy_agents": 0,
                "unhealthy_agents": 0,
                "system_health_score": 0.0,
                "departments": {}
            }
        
        total_agents = len(self.agent_statuses)
        healthy_agents = sum(1 for s in self.agent_statuses.values() if s.health_score >= 0.7)
        unhealthy_agents = total_agents - healthy_agents
        system_health_score = sum(s.health_score for s in self.agent_statuses.values()) / total_agents
        
        # Department summaries
        departments = {}
        department_names = set(s.department for s in self.agent_statuses.values())
        for dept in department_names:
            departments[dept] = self.get_department_status(dept)
        
        return {
            "total_agents": total_agents,
            "healthy_agents": healthy_agents,
            "unhealthy_agents": unhealthy_agents,
            "system_health_score": system_health_score,
            "last_updated": datetime.now().isoformat(),
            "departments": {k: asdict(v) for k, v in departments.items()}
        }
    
    async def register_websocket_client(self, websocket):
        """Register WebSocket client for real-time updates"""
        self.websocket_clients.add(websocket)
        
        # Send current status to new client
        current_status = {
            "type": "initial_status",
            "data": {
                "agents": {k: v.to_dict() for k, v in self.agent_statuses.items()},
                "system_health": self.get_system_health_summary()
            }
        }
        await websocket.send(json.dumps(current_status))
    
    def unregister_websocket_client(self, websocket):
        """Unregister WebSocket client"""
        self.websocket_clients.discard(websocket)


class AgentStatusAPI:
    """REST API for agent status monitoring"""
    
    def __init__(self, monitor: AgentStatusMonitor):
        self.monitor = monitor
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get status of specific agent"""
        status = self.monitor.get_agent_status(agent_id)
        if status:
            return {"status": "success", "data": status.to_dict()}
        else:
            return {"status": "error", "message": f"Agent {agent_id} not found"}
    
    def get_all_agents_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        statuses = self.monitor.get_all_agent_statuses()
        return {
            "status": "success",
            "data": {agent_id: status.to_dict() for agent_id, status in statuses.items()}
        }
    
    def get_department_status(self, department: str) -> Dict[str, Any]:
        """Get department status summary"""
        dept_status = self.monitor.get_department_status(department)
        return {"status": "success", "data": asdict(dept_status)}
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        health_summary = self.monitor.get_system_health_summary()
        return {"status": "success", "data": health_summary}
    
    def get_recent_alerts(self, limit: int = 50) -> Dict[str, Any]:
        """Get recent system alerts"""
        try:
            conn = sqlite3.connect(self.monitor.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT agent_id, alert_type, severity, message, resolved, timestamp
                FROM agent_health_alerts
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            alerts = []
            for row in cursor.fetchall():
                alerts.append({
                    "agent_id": row[0],
                    "alert_type": row[1],
                    "severity": row[2],
                    "message": row[3],
                    "resolved": bool(row[4]),
                    "timestamp": row[5]
                })
            
            conn.close()
            return {"status": "success", "data": alerts}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Global monitor instance
agent_status_monitor = AgentStatusMonitor()
agent_status_api = AgentStatusAPI(agent_status_monitor)


async def main():
    """Test the agent status monitoring system"""
    print("🔍 Starting Agent Status Monitor Test...")
    
    monitor = AgentStatusMonitor()
    
    # Start monitoring in background
    monitoring_task = asyncio.create_task(monitor.start_monitoring())
    
    # Wait a bit for some data to be collected
    await asyncio.sleep(5)
    
    # Test API functionality
    api = AgentStatusAPI(monitor)
    
    print("📊 System Health Summary:")
    health = api.get_system_health()
    print(json.dumps(health, indent=2))
    
    print("\n🏢 Department Status (automation):")
    dept_status = api.get_department_status("automation")
    print(json.dumps(dept_status, indent=2))
    
    print("\n🚨 Recent Alerts:")
    alerts = api.get_recent_alerts(10)
    print(json.dumps(alerts, indent=2))
    
    # Stop monitoring
    await monitor.stop_monitoring()
    monitoring_task.cancel()
    
    print("\n✅ Agent Status Monitor test completed!")


if __name__ == "__main__":
    asyncio.run(main())
