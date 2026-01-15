#!/usr/bin/env python3
"""
Enterprise Automation Orchestrator for Artifact Virtual
Unified automation coordination across all enterprise systems
"""
import asyncio
import importlib
import json
import logging
import os
import sqlite3
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AutomationPriority(Enum):
    """Automation execution priority"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class AutomationStatus(Enum):
    """Automation execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"


@dataclass
class AutomationTask:
    """Automation task definition"""

    id: str
    name: str
    description: str
    module_path: str
    function_name: str
    parameters: Dict[str, Any]
    priority: AutomationPriority
    schedule: Optional[str] = None  # Cron-like schedule
    dependencies: Optional[List[str]] = None
    timeout: Optional[int] = None
    retry_count: int = 3
    retry_delay: int = 60
    environment: str = "production"
    enabled: bool = True


@dataclass
class AutomationExecution:
    """Automation execution record"""

    id: str
    task_id: str
    status: AutomationStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_attempt: int = 0


class EnterpriseAutomationOrchestrator:
    """Main automation orchestration system"""

    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.db_path = self.workspace_path / "data" / "automation_orchestrator.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.running = False
        self.task_registry: Dict[str, AutomationTask] = {}
        self.active_executions: Dict[str, AutomationExecution] = {}
        self.execution_queue: List[AutomationTask] = []

        self.init_database()
        self.register_default_automations()

    def init_database(self):
        """Initialize orchestrator database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Automation tasks table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS automation_tasks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    module_path TEXT NOT NULL,
                    function_name TEXT NOT NULL,
                    parameters TEXT,
                    priority INTEGER NOT NULL,
                    schedule TEXT,
                    dependencies TEXT,
                    timeout INTEGER,
                    retry_count INTEGER DEFAULT 3,
                    retry_delay INTEGER DEFAULT 60,
                    environment TEXT DEFAULT 'production',
                    enabled BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Automation executions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS automation_executions (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at DATETIME NOT NULL,
                    completed_at DATETIME,
                    result TEXT,
                    error_message TEXT,
                    retry_attempt INTEGER DEFAULT 0,
                    FOREIGN KEY (task_id) REFERENCES automation_tasks (id)
                )
            """
            )

            # Automation schedules table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS automation_schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    next_run DATETIME NOT NULL,
                    last_run DATETIME,
                    schedule_pattern TEXT NOT NULL,
                    FOREIGN KEY (task_id) REFERENCES automation_tasks (id)
                )
            """
            )

            conn.commit()

    def register_default_automations(self):
        """Register default enterprise automations"""
        default_tasks = [
            # System monitoring and health checks
            AutomationTask(
                id="system_health_check",
                name="System Health Check",
                description="Comprehensive system health monitoring",
                module_path="workshop.production.devops_monitoring_dashboard",
                function_name="collect_system_metrics",
                parameters={},
                priority=AutomationPriority.HIGH,
                schedule="*/5 * * * *",  # Every 5 minutes
                timeout=120,
            ),
            # Backup operations
            AutomationTask(
                id="automated_backup",
                name="Automated System Backup",
                description="Create comprehensive system backups",
                module_path="tools.backup.backup_system",
                function_name="create_backup",
                parameters={"backup_type": "incremental"},
                priority=AutomationPriority.NORMAL,
                schedule="0 2 * * *",  # Daily at 2 AM
                timeout=3600,
            ),
            # Code analysis and quality checks
            AutomationTask(
                id="code_quality_analysis",
                name="Code Quality Analysis",
                description="Automated code quality and security analysis",
                module_path="tools.analysis.advanced_analysis",
                function_name="analyze_codebase",
                parameters={"include_security": True},
                priority=AutomationPriority.NORMAL,
                schedule="0 6 * * 1",  # Weekly on Monday at 6 AM
                timeout=1800,
            ),
            # Production deployment monitoring
            AutomationTask(
                id="deployment_validation",
                name="Deployment Validation",
                description="Validate production deployment status",
                module_path="workshop.production.intelligent_production_crew",
                function_name="validate_deployment",
                parameters={},
                priority=AutomationPriority.HIGH,
                schedule="*/15 * * * *",  # Every 15 minutes
                timeout=300,
            ),
            # Research lab maintenance
            AutomationTask(
                id="research_lab_maintenance",
                name="Research Lab Maintenance",
                description="Automated research lab system maintenance",
                module_path="research.labs.secure_research_lab",
                function_name="perform_maintenance",
                parameters={"maintenance_type": "routine"},
                priority=AutomationPriority.NORMAL,
                schedule="0 3 * * 0",  # Weekly on Sunday at 3 AM
                timeout=1800,
            ),
            # Agent coordination and optimization
            AutomationTask(
                id="agent_optimization",
                name="Agent Performance Optimization",
                description="Optimize agent performance and coordination",
                module_path="workshop.automations.production.workflow_orchestrator",
                function_name="optimize_agents",
                parameters={},
                priority=AutomationPriority.NORMAL,
                schedule="0 4 * * *",  # Daily at 4 AM
                timeout=1200,
            ),
            # Database maintenance and optimization
            AutomationTask(
                id="database_maintenance",
                name="Database Maintenance",
                description="Database optimization and cleanup",
                module_path="core.data.database_manager",
                function_name="perform_maintenance",
                parameters={"optimize": True, "vacuum": True},
                priority=AutomationPriority.NORMAL,
                schedule="0 1 * * 0",  # Weekly on Sunday at 1 AM
                timeout=2400,
            ),
            # Security audit and compliance
            AutomationTask(
                id="security_audit",
                name="Security Audit",
                description="Comprehensive security audit and compliance check",
                module_path="workshop.production.enterprise_cicd_pipeline",
                function_name="run_security_scan",
                parameters={"comprehensive": True},
                priority=AutomationPriority.HIGH,
                schedule="0 0 * * 1",  # Weekly on Monday at midnight
                timeout=3600,
            ),
            # Performance analytics and reporting
            AutomationTask(
                id="performance_analytics",
                name="Performance Analytics",
                description="Generate performance analytics and reports",
                module_path="reports.performance_analytics",
                function_name="generate_analytics_report",
                parameters={"period": "daily"},
                priority=AutomationPriority.NORMAL,
                schedule="0 8 * * *",  # Daily at 8 AM
                timeout=900,
            ),
            # Continuous improvement engine
            AutomationTask(
                id="continuous_improvement",
                name="Continuous Improvement Engine",
                description="Run continuous improvement analysis",
                module_path="workshop.iterate.intelligent_iteration_engine",
                function_name="analyze_and_improve",
                parameters={},
                priority=AutomationPriority.NORMAL,
                schedule="0 12 * * 1",  # Weekly on Monday at noon
                timeout=1800,
            ),
        ]

        for task in default_tasks:
            self.register_task(task)

    def register_task(self, task: AutomationTask):
        """Register automation task"""
        self.task_registry[task.id] = task

        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO automation_tasks (
                    id, name, description, module_path, function_name,
                    parameters, priority, schedule, dependencies, timeout,
                    retry_count, retry_delay, environment, enabled
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    task.id,
                    task.name,
                    task.description,
                    task.module_path,
                    task.function_name,
                    json.dumps(task.parameters),
                    task.priority.value,
                    task.schedule,
                    json.dumps(task.dependencies) if task.dependencies else None,
                    task.timeout,
                    task.retry_count,
                    task.retry_delay,
                    task.environment,
                    task.enabled,
                ),
            )
            conn.commit()

        logger.info(f"Registered automation task: {task.name}")

    async def start_orchestrator(self):
        """Start the automation orchestrator"""
        self.running = True
        logger.info("🚀 Starting Enterprise Automation Orchestrator...")

        # Load tasks from database
        await self._load_tasks_from_database()

        # Start scheduler
        scheduler_task = asyncio.create_task(self._scheduler_loop())

        # Start executor
        executor_task = asyncio.create_task(self._executor_loop())

        try:
            await asyncio.gather(scheduler_task, executor_task)
        except asyncio.CancelledError:
            logger.info("Orchestrator cancelled")
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
        finally:
            self.running = False

    def stop_orchestrator(self):
        """Stop the orchestrator"""
        self.running = False
        logger.info("⏹️ Stopping automation orchestrator...")

    async def _load_tasks_from_database(self):
        """Load automation tasks from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM automation_tasks WHERE enabled = TRUE
            """
            )

            for row in cursor.fetchall():
                task = AutomationTask(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    module_path=row[3],
                    function_name=row[4],
                    parameters=json.loads(row[5]) if row[5] else {},
                    priority=AutomationPriority(row[6]),
                    schedule=row[7],
                    dependencies=json.loads(row[8]) if row[8] else None,
                    timeout=row[9],
                    retry_count=row[10],
                    retry_delay=row[11],
                    environment=row[12],
                    enabled=bool(row[13]),
                )
                self.task_registry[task.id] = task

        logger.info(f"Loaded {len(self.task_registry)} automation tasks")

    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                # Check for scheduled tasks
                current_time = datetime.utcnow()

                for task in self.task_registry.values():
                    if task.enabled and task.schedule:
                        if await self._should_run_task(task, current_time):
                            await self._queue_task(task)

                # Wait before next check
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)

    async def _executor_loop(self):
        """Main executor loop"""
        while self.running:
            try:
                if self.execution_queue:
                    # Sort queue by priority
                    self.execution_queue.sort(
                        key=lambda t: t.priority.value, reverse=True
                    )

                    # Execute next task
                    task = self.execution_queue.pop(0)
                    await self._execute_task(task)

                # Wait before checking queue again
                await asyncio.sleep(10)

            except Exception as e:
                logger.error(f"Executor error: {e}")
                await asyncio.sleep(30)

    async def _should_run_task(
        self, task: AutomationTask, current_time: datetime
    ) -> bool:
        """Check if task should run based on schedule"""
        if not task.schedule:
            return False

        # Simple schedule check (in real implementation, use proper cron parser)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT last_run FROM automation_schedules 
                WHERE task_id = ?
            """,
                (task.id,),
            )

            result = cursor.fetchone()
            if result and result[0]:
                last_run = datetime.fromisoformat(result[0])
                # Simple check: run if more than 1 hour since last run
                # (This should be replaced with proper cron parsing)
                return (current_time - last_run).seconds > 3600
            else:
                # Never run before
                return True

    async def _queue_task(self, task: AutomationTask):
        """Queue task for execution"""
        if task.id not in [t.id for t in self.execution_queue]:
            # Check dependencies
            if task.dependencies:
                missing_deps = await self._check_dependencies(task.dependencies)
                if missing_deps:
                    logger.warning(
                        f"Task {task.name} has missing dependencies: {missing_deps}"
                    )
                    return

            self.execution_queue.append(task)
            logger.info(f"Queued task for execution: {task.name}")

    async def _check_dependencies(self, dependencies: List[str]) -> List[str]:
        """Check if task dependencies are satisfied"""
        missing = []

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            for dep_id in dependencies:
                cursor.execute(
                    """
                    SELECT status, completed_at FROM automation_executions 
                    WHERE task_id = ? AND completed_at > datetime('now', '-24 hours')
                    ORDER BY completed_at DESC LIMIT 1
                """,
                    (dep_id,),
                )

                result = cursor.fetchone()
                if not result or result[0] != AutomationStatus.COMPLETED.value:
                    missing.append(dep_id)

        return missing

    async def _execute_task(self, task: AutomationTask):
        """Execute automation task"""
        execution_id = f"exec-{task.id}-{int(time.time())}"

        execution = AutomationExecution(
            id=execution_id,
            task_id=task.id,
            status=AutomationStatus.RUNNING,
            started_at=datetime.utcnow(),
        )

        self.active_executions[execution_id] = execution

        logger.info(f"🔄 Executing task: {task.name}")

        try:
            # Import module and get function
            module = importlib.import_module(task.module_path)
            func = getattr(module, task.function_name)

            # Execute with timeout
            if asyncio.iscoroutinefunction(func):
                if task.timeout:
                    result = await asyncio.wait_for(
                        func(**task.parameters), timeout=task.timeout
                    )
                else:
                    result = await func(**task.parameters)
            else:
                # Run synchronous function in thread pool
                loop = asyncio.get_event_loop()
                if task.timeout:
                    result = await asyncio.wait_for(
                        loop.run_in_executor(None, lambda: func(**task.parameters)),
                        timeout=task.timeout,
                    )
                else:
                    result = await loop.run_in_executor(
                        None, lambda: func(**task.parameters)
                    )

            # Success
            execution.status = AutomationStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.result = (
                result if isinstance(result, dict) else {"result": str(result)}
            )

            logger.info(f"✅ Task completed successfully: {task.name}")

        except asyncio.TimeoutError:
            execution.status = AutomationStatus.FAILED
            execution.completed_at = datetime.utcnow()
            execution.error_message = f"Task timed out after {task.timeout} seconds"
            logger.error(f"❌ Task timed out: {task.name}")

        except Exception as e:
            execution.status = AutomationStatus.FAILED
            execution.completed_at = datetime.utcnow()
            execution.error_message = str(e)
            logger.error(f"❌ Task failed: {task.name} - {e}")

            # Retry if configured
            if execution.retry_attempt < task.retry_count:
                logger.info(
                    f"🔄 Retrying task {task.name} (attempt {execution.retry_attempt + 1}/{task.retry_count})"
                )
                execution.retry_attempt += 1
                await asyncio.sleep(task.retry_delay)
                # Re-queue for retry
                await self._queue_task(task)

        finally:
            # Store execution record
            await self._store_execution(execution)

            # Update schedule
            await self._update_schedule(task.id)

            # Remove from active executions
            del self.active_executions[execution_id]

    async def _store_execution(self, execution: AutomationExecution):
        """Store execution record in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO automation_executions (
                    id, task_id, status, started_at, completed_at,
                    result, error_message, retry_attempt
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    execution.id,
                    execution.task_id,
                    execution.status.value,
                    execution.started_at.isoformat(),
                    (
                        execution.completed_at.isoformat()
                        if execution.completed_at
                        else None
                    ),
                    json.dumps(execution.result) if execution.result else None,
                    execution.error_message,
                    execution.retry_attempt,
                ),
            )
            conn.commit()

    async def _update_schedule(self, task_id: str):
        """Update task schedule after execution"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO automation_schedules (task_id, last_run, next_run, schedule_pattern)
                VALUES (?, ?, ?, ?)
            """,
                (
                    task_id,
                    datetime.utcnow().isoformat(),
                    datetime.utcnow().isoformat(),  # Should calculate next run
                    self.task_registry[task_id].schedule or "",
                ),
            )
            conn.commit()

    async def execute_task_now(self, task_id: str) -> bool:
        """Execute specific task immediately"""
        if task_id not in self.task_registry:
            logger.error(f"Task not found: {task_id}")
            return False

        task = self.task_registry[task_id]
        if not task.enabled:
            logger.error(f"Task is disabled: {task_id}")
            return False

        await self._queue_task(task)
        return True

    async def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get task statistics
            cursor.execute(
                """
                SELECT COUNT(*) FROM automation_tasks WHERE enabled = TRUE
            """
            )
            total_tasks = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*) FROM automation_executions 
                WHERE started_at > datetime('now', '-24 hours')
            """
            )
            executions_24h = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*) FROM automation_executions 
                WHERE status = ? AND started_at > datetime('now', '-24 hours')
            """,
                (AutomationStatus.COMPLETED.value,),
            )
            successful_24h = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*) FROM automation_executions 
                WHERE status = ? AND started_at > datetime('now', '-24 hours')
            """,
                (AutomationStatus.FAILED.value,),
            )
            failed_24h = cursor.fetchone()[0]

        return {
            "running": self.running,
            "total_tasks": total_tasks,
            "queued_tasks": len(self.execution_queue),
            "active_executions": len(self.active_executions),
            "executions_24h": executions_24h,
            "successful_24h": successful_24h,
            "failed_24h": failed_24h,
            "success_rate": (
                (successful_24h / executions_24h * 100) if executions_24h > 0 else 0
            ),
            "timestamp": datetime.utcnow().isoformat(),
        }


async def main():
    """CLI interface for Enterprise Automation Orchestrator"""
    import argparse
    import signal

    parser = argparse.ArgumentParser(description="Enterprise Automation Orchestrator")
    parser.add_argument("--workspace", default=".", help="Workspace path")
    parser.add_argument("--start", action="store_true", help="Start orchestrator")
    parser.add_argument(
        "--status", action="store_true", help="Show orchestrator status"
    )
    parser.add_argument("--execute", help="Execute specific task by ID")
    parser.add_argument(
        "--list-tasks", action="store_true", help="List all registered tasks"
    )

    args = parser.parse_args()

    orchestrator = EnterpriseAutomationOrchestrator(args.workspace)

    if args.start:
        # Set up signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            orchestrator.stop_orchestrator()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            await orchestrator.start_orchestrator()
        except KeyboardInterrupt:
            logger.info("Orchestrator stopped by user")

    elif args.status:
        status = await orchestrator.get_orchestrator_status()
        print("\n🎯 AUTOMATION ORCHESTRATOR STATUS")
        print("=" * 50)
        print(f"Running: {'✅ Yes' if status['running'] else '❌ No'}")
        print(f"Total Tasks: {status['total_tasks']}")
        print(f"Queued Tasks: {status['queued_tasks']}")
        print(f"Active Executions: {status['active_executions']}")
        print(f"Executions (24h): {status['executions_24h']}")
        print(f"Successful (24h): {status['successful_24h']}")
        print(f"Failed (24h): {status['failed_24h']}")
        print(f"Success Rate: {status['success_rate']:.1f}%")
        print(f"Last Updated: {status['timestamp']}")

    elif args.execute:
        success = await orchestrator.execute_task_now(args.execute)
        if success:
            print(f"✅ Task queued for execution: {args.execute}")
        else:
            print(f"❌ Failed to queue task: {args.execute}")

    elif args.list_tasks:
        print("\n📋 REGISTERED AUTOMATION TASKS")
        print("=" * 50)
        for task_id, task in orchestrator.task_registry.items():
            status_icon = "✅" if task.enabled else "❌"
            priority_icon = (
                "🔥"
                if task.priority.value >= 4
                else "⚡" if task.priority.value >= 3 else "📄"
            )
            print(f"{status_icon} {priority_icon} {task.name}")
            print(f"   ID: {task_id}")
            print(f"   Description: {task.description}")
            print(f"   Schedule: {task.schedule or 'Manual'}")
            print(f"   Priority: {task.priority.name}")
            print()

    else:
        # Show quick status
        status = await orchestrator.get_orchestrator_status()
        print(f"🎯 Enterprise Automation Orchestrator")
        print(
            f"📊 Tasks: {status['total_tasks']} registered | {status['queued_tasks']} queued | {status['active_executions']} running"
        )
        print(
            f"📈 Success Rate (24h): {status['success_rate']:.1f}% ({status['successful_24h']}/{status['executions_24h']})"
        )
        print("\nUse --help for more options")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Orchestrator stopped")
