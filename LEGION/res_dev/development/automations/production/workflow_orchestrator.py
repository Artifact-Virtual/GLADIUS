#!/usr/bin/env python3
"""
Advanced Multi-Agent Workflow Orchestrator
Military-grade orchestration system based on MAOS patterns
"""

import asyncio
import json
import logging
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status"""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionStrategy(Enum):
    """Workflow execution strategies"""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"
    ADAPTIVE = "adaptive"


@dataclass
class WorkflowTask:
    """Individual task within a workflow"""

    task_id: str
    agent_role: str
    phase: str
    description: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    dependencies: List[str]
    priority: int
    estimated_duration: int  # minutes
    status: WorkflowStatus
    assigned_agent: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class WorkflowContext:
    """Context for workflow execution"""

    workflow_id: str
    project_id: str
    project_name: str
    project_description: str
    business_objectives: List[str]
    technical_constraints: Dict[str, Any]
    resources: Dict[str, Any]
    timeline: Dict[str, Any]
    stakeholders: List[Dict[str, Any]]
    success_criteria: List[str]
    metadata: Dict[str, Any]


class WorkflowEngine:
    """Advanced workflow execution engine"""

    def __init__(self, workspace_root: str = None):
        self.workspace_root = Path(workspace_root or ".")
        self.db_path = self.workspace_root / "data" / "workflow_engine.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.active_workflows: Dict[str, WorkflowContext] = {}
        self.task_queue: Dict[str, List[WorkflowTask]] = {}
        self.agent_pool: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[Dict[str, Any]] = []

        self._init_database()
        self._load_agent_pool()

        self.logger = logging.getLogger("workflow_engine")

    def _init_database(self):
        """Initialize workflow database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS workflows (
                    workflow_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    project_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    context_data TEXT,
                    results TEXT
                );

                CREATE TABLE IF NOT EXISTS workflow_tasks (
                    task_id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    agent_role TEXT NOT NULL,
                    phase TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority INTEGER DEFAULT 5,
                    dependencies TEXT,
                    inputs TEXT,
                    outputs TEXT,
                    assigned_agent TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    execution_time_seconds REAL,
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (workflow_id) REFERENCES workflows (workflow_id)
                );
                
                CREATE TABLE IF NOT EXISTS agent_assignments (
                    assignment_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    workflow_id TEXT NOT NULL,
                    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'assigned',
                    FOREIGN KEY (task_id) REFERENCES workflow_tasks (task_id),
                    FOREIGN KEY (workflow_id) REFERENCES workflows (workflow_id)
                );
                
                CREATE TABLE IF NOT EXISTS execution_metrics (
                    metric_id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    task_id TEXT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL,
                    metric_unit TEXT,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (workflow_id) REFERENCES workflows (workflow_id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);
                CREATE INDEX IF NOT EXISTS idx_tasks_workflow ON workflow_tasks(workflow_id);
                CREATE INDEX IF NOT EXISTS idx_tasks_status ON workflow_tasks(status);
                CREATE INDEX IF NOT EXISTS idx_assignments_agent ON agent_assignments(agent_id);
            """
            )

    def _load_agent_pool(self):
        """Load available agents into pool"""
        # Simulate agent pool - in production, this would be dynamic
        self.agent_pool = {
            "requirements_analyst_001": {
                "role": "requirements_analyst",
                "status": "idle",
                "capabilities": ["requirements_gathering", "stakeholder_analysis"],
                "load_factor": 0.0,
                "max_concurrent_tasks": 3,
            },
            "solution_architect_001": {
                "role": "solution_architect",
                "status": "idle",
                "capabilities": ["system_design", "technology_selection"],
                "load_factor": 0.0,
                "max_concurrent_tasks": 2,
            },
            "senior_developer_001": {
                "role": "senior_developer",
                "status": "idle",
                "capabilities": ["code_generation", "integration"],
                "load_factor": 0.0,
                "max_concurrent_tasks": 4,
            },
            "qa_engineer_001": {
                "role": "qa_engineer",
                "status": "idle",
                "capabilities": ["test_design", "quality_assurance"],
                "load_factor": 0.0,
                "max_concurrent_tasks": 3,
            },
            "devops_specialist_001": {
                "role": "devops_specialist",
                "status": "idle",
                "capabilities": ["deployment", "infrastructure"],
                "load_factor": 0.0,
                "max_concurrent_tasks": 2,
            },
        }

    async def create_workflow(
        self,
        context: WorkflowContext,
        strategy: ExecutionStrategy = ExecutionStrategy.HIERARCHICAL,
    ) -> str:
        """Create new workflow"""
        workflow_id = context.workflow_id

        # Store workflow in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO workflows 
                (workflow_id, project_id, project_name, status, strategy, context_data)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    workflow_id,
                    context.project_id,
                    context.project_name,
                    WorkflowStatus.PENDING.value,
                    strategy.value,
                    json.dumps(asdict(context)),
                ),
            )

        # Generate workflow tasks
        tasks = self._generate_workflow_tasks(context)
        self.task_queue[workflow_id] = tasks

        # Store tasks in database
        with sqlite3.connect(self.db_path) as conn:
            for task in tasks:
                conn.execute(
                    """
                    INSERT INTO workflow_tasks 
                    (task_id, workflow_id, agent_role, phase, description, status, 
                     priority, dependencies, inputs, outputs)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        task.task_id,
                        workflow_id,
                        task.agent_role,
                        task.phase,
                        task.description,
                        task.status.value,
                        task.priority,
                        json.dumps(task.dependencies),
                        json.dumps(task.inputs),
                        json.dumps(task.outputs),
                    ),
                )

        self.active_workflows[workflow_id] = context
        self.logger.info(f"Created workflow {workflow_id} with {len(tasks)} tasks")

        return workflow_id

    def _generate_workflow_tasks(self, context: WorkflowContext) -> List[WorkflowTask]:
        """Generate tasks for workflow based on context"""
        tasks = []

        # Phase 1: Requirements Analysis
        req_task = WorkflowTask(
            task_id=f"req_{uuid4().hex[:8]}",
            agent_role="requirements_analyst",
            phase="requirements",
            description="Analyze project requirements and stakeholder needs",
            inputs={
                "project_description": context.project_description,
                "business_objectives": context.business_objectives,
                "stakeholders": context.stakeholders,
            },
            outputs={},
            dependencies=[],
            priority=1,
            estimated_duration=120,  # 2 hours
            status=WorkflowStatus.PENDING,
        )
        tasks.append(req_task)

        # Phase 2: Solution Architecture
        arch_task = WorkflowTask(
            task_id=f"arch_{uuid4().hex[:8]}",
            agent_role="solution_architect",
            phase="architecture",
            description="Design system architecture and select technologies",
            inputs={
                "requirements": "dependency:requirements",
                "constraints": context.technical_constraints,
            },
            outputs={},
            dependencies=[req_task.task_id],
            priority=2,
            estimated_duration=180,  # 3 hours
            status=WorkflowStatus.PENDING,
        )
        tasks.append(arch_task)

        # Phase 3: Development Planning
        dev_plan_task = WorkflowTask(
            task_id=f"dev_plan_{uuid4().hex[:8]}",
            agent_role="senior_developer",
            phase="development_planning",
            description="Create development plan and estimate effort",
            inputs={
                "architecture": "dependency:architecture",
                "requirements": "dependency:requirements",
            },
            outputs={},
            dependencies=[arch_task.task_id],
            priority=3,
            estimated_duration=90,  # 1.5 hours
            status=WorkflowStatus.PENDING,
        )
        tasks.append(dev_plan_task)

        # Phase 4: Core Development
        core_dev_task = WorkflowTask(
            task_id=f"dev_core_{uuid4().hex[:8]}",
            agent_role="senior_developer",
            phase="core_development",
            description="Implement core system components",
            inputs={
                "development_plan": "dependency:development_planning",
                "architecture": "dependency:architecture",
            },
            outputs={},
            dependencies=[dev_plan_task.task_id],
            priority=4,
            estimated_duration=480,  # 8 hours
            status=WorkflowStatus.PENDING,
        )
        tasks.append(core_dev_task)

        # Phase 5: Quality Assurance
        qa_task = WorkflowTask(
            task_id=f"qa_{uuid4().hex[:8]}",
            agent_role="qa_engineer",
            phase="quality_assurance",
            description="Design and execute test plans",
            inputs={
                "code_artifacts": "dependency:core_development",
                "requirements": "dependency:requirements",
            },
            outputs={},
            dependencies=[core_dev_task.task_id],
            priority=5,
            estimated_duration=240,  # 4 hours
            status=WorkflowStatus.PENDING,
        )
        tasks.append(qa_task)

        # Phase 6: Deployment Preparation
        deploy_task = WorkflowTask(
            task_id=f"deploy_{uuid4().hex[:8]}",
            agent_role="devops_specialist",
            phase="deployment",
            description="Prepare deployment pipeline and infrastructure",
            inputs={
                "architecture": "dependency:architecture",
                "code_artifacts": "dependency:core_development",
                "test_results": "dependency:quality_assurance",
            },
            outputs={},
            dependencies=[qa_task.task_id],
            priority=6,
            estimated_duration=180,  # 3 hours
            status=WorkflowStatus.PENDING,
        )
        tasks.append(deploy_task)

        return tasks

    async def execute_workflow(
        self,
        workflow_id: str,
        strategy: ExecutionStrategy = ExecutionStrategy.HIERARCHICAL,
    ) -> Dict[str, Any]:
        """Execute workflow with specified strategy"""
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        self.logger.info(
            f"Starting workflow execution: {workflow_id} with strategy: {strategy.value}"
        )

        # Update workflow status
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE workflows 
                SET status = ?, started_at = CURRENT_TIMESTAMP 
                WHERE workflow_id = ?
            """,
                (WorkflowStatus.RUNNING.value, workflow_id),
            )

        start_time = datetime.now()

        try:
            if strategy == ExecutionStrategy.SEQUENTIAL:
                result = await self._execute_sequential(workflow_id)
            elif strategy == ExecutionStrategy.PARALLEL:
                result = await self._execute_parallel(workflow_id)
            elif strategy == ExecutionStrategy.HIERARCHICAL:
                result = await self._execute_hierarchical(workflow_id)
            else:
                result = await self._execute_adaptive(workflow_id)

            execution_time = (datetime.now() - start_time).total_seconds()

            # Update workflow completion
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE workflows 
                    SET status = ?, completed_at = CURRENT_TIMESTAMP, results = ?
                    WHERE workflow_id = ?
                """,
                    (WorkflowStatus.COMPLETED.value, json.dumps(result), workflow_id),
                )

            self.logger.info(
                f"Workflow {workflow_id} completed in {execution_time:.2f}s"
            )
            return result

        except Exception as e:
            self.logger.error(f"Workflow {workflow_id} failed: {str(e)}")

            # Update workflow failure
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE workflows 
                    SET status = ? 
                    WHERE workflow_id = ?
                """,
                    (WorkflowStatus.FAILED.value, workflow_id),
                )

            raise

    async def _execute_hierarchical(self, workflow_id: str) -> Dict[str, Any]:
        """Execute workflow in hierarchical phases"""
        tasks = self.task_queue[workflow_id]
        completed_tasks = {}
        phase_results = {}

        # Group tasks by phase and priority
        phases = {}
        for task in tasks:
            if task.phase not in phases:
                phases[task.phase] = []
            phases[task.phase].append(task)

        # Sort phases by priority
        sorted_phases = sorted(
            phases.items(), key=lambda x: min(t.priority for t in x[1])
        )

        for phase_name, phase_tasks in sorted_phases:
            self.logger.info(
                f"Executing phase: {phase_name} with {len(phase_tasks)} tasks"
            )

            # Execute tasks in phase
            phase_task_results = []
            for task in sorted(phase_tasks, key=lambda t: t.priority):
                # Check dependencies
                if not self._check_dependencies(task, completed_tasks):
                    self.logger.warning(
                        f"Task {task.task_id} dependencies not met, skipping"
                    )
                    continue

                # Assign agent
                agent_id = await self._assign_agent(task)
                if not agent_id:
                    self.logger.error(f"No available agent for task {task.task_id}")
                    continue

                # Execute task
                result = await self._execute_task(task, agent_id, completed_tasks)
                completed_tasks[task.task_id] = result
                phase_task_results.append(result)

            phase_results[phase_name] = phase_task_results

        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "phases": phase_results,
            "total_tasks": len(tasks),
            "completed_tasks": len(completed_tasks),
            "execution_summary": self._generate_execution_summary(completed_tasks),
        }

    async def _execute_sequential(self, workflow_id: str) -> Dict[str, Any]:
        """Execute workflow tasks sequentially"""
        tasks = self.task_queue[workflow_id]
        completed_tasks = {}

        # Sort tasks by priority and dependencies
        sorted_tasks = self._topological_sort(tasks)

        for task in sorted_tasks:
            # Assign agent
            agent_id = await self._assign_agent(task)
            if not agent_id:
                continue

            # Execute task
            result = await self._execute_task(task, agent_id, completed_tasks)
            completed_tasks[task.task_id] = result

        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "tasks": list(completed_tasks.values()),
            "execution_summary": self._generate_execution_summary(completed_tasks),
        }

    async def _execute_parallel(self, workflow_id: str) -> Dict[str, Any]:
        """Execute workflow tasks in parallel where possible"""
        tasks = self.task_queue[workflow_id]
        completed_tasks = {}
        running_tasks = set()

        while len(completed_tasks) < len(tasks):
            # Find tasks ready to execute
            ready_tasks = [
                task
                for task in tasks
                if (
                    task.task_id not in completed_tasks
                    and task.task_id not in running_tasks
                    and self._check_dependencies(task, completed_tasks)
                )
            ]

            # Start ready tasks
            for task in ready_tasks:
                agent_id = await self._assign_agent(task)
                if agent_id:
                    running_tasks.add(task.task_id)
                    asyncio.create_task(
                        self._execute_task_parallel(
                            task, agent_id, completed_tasks, running_tasks
                        )
                    )

            # Wait a bit before checking again
            await asyncio.sleep(0.1)

        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "tasks": list(completed_tasks.values()),
            "execution_summary": self._generate_execution_summary(completed_tasks),
        }

    async def _execute_adaptive(self, workflow_id: str) -> Dict[str, Any]:
        """Execute workflow with adaptive strategy based on load and dependencies"""
        # Start with hierarchical, adapt based on conditions
        return await self._execute_hierarchical(workflow_id)

    def _check_dependencies(
        self, task: WorkflowTask, completed_tasks: Dict[str, Any]
    ) -> bool:
        """Check if task dependencies are satisfied"""
        return all(dep_id in completed_tasks for dep_id in task.dependencies)

    async def _assign_agent(self, task: WorkflowTask) -> Optional[str]:
        """Assign available agent to task"""
        available_agents = [
            agent_id
            for agent_id, agent_info in self.agent_pool.items()
            if (
                agent_info["role"] == task.agent_role
                and agent_info["status"] == "idle"
                and agent_info["load_factor"] < 0.8
            )
        ]

        if not available_agents:
            return None

        # Select agent with lowest load factor
        selected_agent = min(
            available_agents, key=lambda a: self.agent_pool[a]["load_factor"]
        )

        # Update agent status
        self.agent_pool[selected_agent]["status"] = "busy"
        self.agent_pool[selected_agent]["load_factor"] += 0.25

        # Record assignment
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO agent_assignments 
                (assignment_id, agent_id, task_id, workflow_id)
                VALUES (?, ?, ?, ?)
            """,
                (str(uuid4()), selected_agent, task.task_id, task.workflow_id),
            )

        return selected_agent

    async def _execute_task(
        self, task: WorkflowTask, agent_id: str, completed_tasks: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute individual task"""
        start_time = datetime.now()

        # Update task status
        task.status = WorkflowStatus.RUNNING
        task.assigned_agent = agent_id
        task.start_time = start_time

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE workflow_tasks 
                SET status = ?, assigned_agent = ?, start_time = ?
                WHERE task_id = ?
            """,
                (
                    WorkflowStatus.RUNNING.value,
                    agent_id,
                    start_time.isoformat(),
                    task.task_id,
                ),
            )

        try:
            # Simulate task execution
            self.logger.info(f"Executing task {task.task_id} with agent {agent_id}")

            # Resolve input dependencies
            resolved_inputs = self._resolve_task_inputs(task, completed_tasks)

            # Simulate work based on estimated duration
            work_duration = (
                task.estimated_duration / 60
            )  # Convert to seconds for simulation
            await asyncio.sleep(min(work_duration, 2.0))  # Cap at 2 seconds for demo

            # Generate mock results
            task_result = {
                "task_id": task.task_id,
                "agent_id": agent_id,
                "phase": task.phase,
                "status": "completed",
                "inputs": resolved_inputs,
                "outputs": self._generate_mock_outputs(task),
                "execution_time": (datetime.now() - start_time).total_seconds(),
                "timestamp": start_time.isoformat(),
            }

            # Update task completion
            task.status = WorkflowStatus.COMPLETED
            task.end_time = datetime.now()
            task.outputs = task_result["outputs"]

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE workflow_tasks 
                    SET status = ?, end_time = ?, outputs = ?, execution_time_seconds = ?
                    WHERE task_id = ?
                """,
                    (
                        WorkflowStatus.COMPLETED.value,
                        task.end_time.isoformat(),
                        json.dumps(task.outputs),
                        task_result["execution_time"],
                        task.task_id,
                    ),
                )

            self.logger.info(f"Task {task.task_id} completed successfully")
            return task_result

        except Exception as e:
            # Handle task failure
            task.status = WorkflowStatus.FAILED
            task.error_message = str(e)
            task.end_time = datetime.now()

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE workflow_tasks 
                    SET status = ?, error_message = ?, end_time = ?
                    WHERE task_id = ?
                """,
                    (
                        WorkflowStatus.FAILED.value,
                        str(e),
                        task.end_time.isoformat(),
                        task.task_id,
                    ),
                )

            self.logger.error(f"Task {task.task_id} failed: {str(e)}")
            raise

        finally:
            # Release agent
            self.agent_pool[agent_id]["status"] = "idle"
            self.agent_pool[agent_id]["load_factor"] = max(
                0.0, self.agent_pool[agent_id]["load_factor"] - 0.25
            )

    async def _execute_task_parallel(
        self,
        task: WorkflowTask,
        agent_id: str,
        completed_tasks: Dict[str, Any],
        running_tasks: Set[str],
    ):
        """Execute task in parallel mode"""
        try:
            result = await self._execute_task(task, agent_id, completed_tasks)
            completed_tasks[task.task_id] = result
        finally:
            running_tasks.discard(task.task_id)

    def _resolve_task_inputs(
        self, task: WorkflowTask, completed_tasks: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve task inputs from dependencies"""
        resolved_inputs = task.inputs.copy()

        for key, value in task.inputs.items():
            if isinstance(value, str) and value.startswith("dependency:"):
                dependency_phase = value.split(":", 1)[1]
                # Find completed task from that phase
                for dep_task_id, dep_result in completed_tasks.items():
                    if dep_result.get("phase") == dependency_phase:
                        resolved_inputs[key] = dep_result.get("outputs", {})
                        break

        return resolved_inputs

    def _generate_mock_outputs(self, task: WorkflowTask) -> Dict[str, Any]:
        """Generate mock outputs for task simulation"""
        if task.phase == "requirements":
            return {
                "requirements_specification": {
                    "functional": [
                        "User authentication",
                        "Data processing",
                        "Reporting",
                    ],
                    "non_functional": ["Performance", "Security", "Scalability"],
                },
                "stakeholder_analysis": ["Product Owner", "End Users", "Operations"],
                "acceptance_criteria": [
                    "Login system",
                    "Data validation",
                    "Report generation",
                ],
            }
        elif task.phase == "architecture":
            return {
                "system_architecture": {
                    "components": ["API Gateway", "Service Layer", "Database"],
                    "patterns": ["Microservices", "Event-driven"],
                },
                "technology_stack": {
                    "backend": "FastAPI",
                    "database": "PostgreSQL",
                    "cache": "Redis",
                },
            }
        elif task.phase in ["development_planning", "core_development"]:
            return {
                "code_artifacts": ["main.py", "models.py", "api.py"],
                "test_suite": ["test_main.py", "test_models.py"],
                "documentation": ["README.md", "API_DOCS.md"],
            }
        elif task.phase == "quality_assurance":
            return {
                "test_results": {
                    "unit_tests": {"passed": 45, "failed": 0, "coverage": 95.2},
                    "integration_tests": {"passed": 12, "failed": 0},
                    "performance_tests": {
                        "response_time": "150ms",
                        "throughput": "1000 req/s",
                    },
                }
            }
        elif task.phase == "deployment":
            return {
                "deployment_artifacts": [
                    "Dockerfile",
                    "docker-compose.yml",
                    "k8s-manifests",
                ],
                "infrastructure": {
                    "cloud": "AWS",
                    "services": ["EKS", "RDS", "ElastiCache"],
                },
                "deployment_url": "https://api.example.com",
            }
        else:
            return {"generic_output": f"Results from {task.phase} phase"}

    def _topological_sort(self, tasks: List[WorkflowTask]) -> List[WorkflowTask]:
        """Sort tasks topologically based on dependencies"""
        # Simple topological sort
        task_map = {task.task_id: task for task in tasks}
        visited = set()
        result = []

        def visit(task_id: str):
            if task_id in visited:
                return

            task = task_map.get(task_id)
            if not task:
                return

            for dep_id in task.dependencies:
                visit(dep_id)

            visited.add(task_id)
            result.append(task)

        for task in tasks:
            visit(task.task_id)

        return result

    def _generate_execution_summary(
        self, completed_tasks: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate execution summary"""
        total_time = sum(
            task.get("execution_time", 0) for task in completed_tasks.values()
        )

        return {
            "total_tasks": len(completed_tasks),
            "total_execution_time": total_time,
            "average_task_time": (
                total_time / len(completed_tasks) if completed_tasks else 0
            ),
            "success_rate": 100.0,  # Simplified for demo
            "phases_completed": len(
                set(task.get("phase") for task in completed_tasks.values())
            ),
        }

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current workflow status"""
        with sqlite3.connect(self.db_path) as conn:
            workflow_row = conn.execute(
                """
                SELECT * FROM workflows WHERE workflow_id = ?
            """,
                (workflow_id,),
            ).fetchone()

            if not workflow_row:
                return {"error": "Workflow not found"}

            task_rows = conn.execute(
                """
                SELECT * FROM workflow_tasks WHERE workflow_id = ?
            """,
                (workflow_id,),
            ).fetchall()

        # Convert to dictionaries
        workflow_keys = [desc[0] for desc in conn.description]
        workflow_data = dict(zip(workflow_keys, workflow_row))

        task_keys = [
            "task_id",
            "workflow_id",
            "agent_role",
            "phase",
            "description",
            "status",
            "priority",
            "dependencies",
            "inputs",
            "outputs",
            "assigned_agent",
            "start_time",
            "end_time",
            "execution_time_seconds",
            "error_message",
            "retry_count",
            "created_at",
        ]
        tasks_data = [dict(zip(task_keys, row)) for row in task_rows]

        return {
            "workflow": workflow_data,
            "tasks": tasks_data,
            "agent_pool_status": self.agent_pool,
        }


# CLI interface for testing
async def main():
    """Test workflow orchestrator"""
    print("🔄 Testing Advanced Workflow Orchestrator...")

    # Initialize engine
    engine = WorkflowEngine(".")

    # Create workflow context
    context = WorkflowContext(
        workflow_id=str(uuid4()),
        project_id="test_project_001",
        project_name="Advanced Task Management System",
        project_description="Build a comprehensive task management system with real-time collaboration",
        business_objectives=[
            "Increase team productivity by 30%",
            "Reduce project delivery time",
            "Improve task visibility and tracking",
        ],
        technical_constraints={
            "budget": 100000,
            "timeline_months": 4,
            "team_size": 8,
            "technology_preferences": ["Python", "React", "PostgreSQL"],
        },
        resources={
            "development_environments": 3,
            "testing_environments": 2,
            "production_environment": 1,
        },
        timeline={
            "start_date": "2024-01-15",
            "end_date": "2024-05-15",
            "milestones": ["Alpha", "Beta", "Release"],
        },
        stakeholders=[
            {"role": "Product Owner", "name": "John Smith", "influence": "high"},
            {"role": "Engineering Lead", "name": "Jane Doe", "influence": "high"},
            {"role": "QA Lead", "name": "Bob Johnson", "influence": "medium"},
        ],
        success_criteria=[
            "All functional requirements implemented",
            "Performance targets met",
            "Security requirements satisfied",
            "User acceptance > 4.0/5.0",
        ],
        metadata={
            "created_by": "system",
            "priority": "high",
            "classification": "internal",
        },
    )

    # Create workflow
    workflow_id = await engine.create_workflow(context, ExecutionStrategy.HIERARCHICAL)
    print(f"✅ Created workflow: {workflow_id}")

    # Execute workflow
    print("🚀 Executing workflow...")
    result = await engine.execute_workflow(workflow_id, ExecutionStrategy.HIERARCHICAL)

    print(f"✅ Workflow completed!")
    print(f"   Total tasks: {result['total_tasks']}")
    print(f"   Completed tasks: {result['completed_tasks']}")
    print(f"   Phases: {len(result['phases'])}")

    # Show phase results
    for phase_name, phase_tasks in result["phases"].items():
        print(f"   📋 {phase_name}: {len(phase_tasks)} tasks completed")

    # Get final status
    status = engine.get_workflow_status(workflow_id)
    print(f"📊 Final Status: {status['workflow']['status']}")

    print("\n🎯 Advanced Workflow Orchestrator Ready!")


if __name__ == "__main__":
    asyncio.run(main())
