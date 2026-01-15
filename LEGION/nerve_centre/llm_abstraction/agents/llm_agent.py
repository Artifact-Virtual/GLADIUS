"""
Advanced Agent System for LLM Orchestration
"""
import asyncio
import logging
import time
import uuid
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import threading
import queue
import json

from ..llm_abstraction import (
    LLMOrchestrator, LLMRequest, LLMResponse, SecurityLevel
)
from ..security import SecurityContext, SecurityValidator
from ..config_manager import ConfigManager


logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Individual task within a workflow."""
    id: str
    name: str
    prompt: str
    context: Optional[Dict[str, Any]] = None
    dependencies: List[str] = field(default_factory=list)
    max_retries: int = 3
    timeout: int = 30
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    status: AgentStatus = AgentStatus.IDLE
    result: Optional[LLMResponse] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None


@dataclass
class Workflow:
    """Collection of related tasks."""
    id: str
    name: str
    description: str
    tasks: List[Task]
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_by: str = "system"
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentCallback(ABC):
    """Abstract base for agent callbacks."""
    
    @abstractmethod
    def on_task_started(self, task: Task) -> None:
        """Called when a task starts."""
        pass
    
    @abstractmethod
    def on_task_completed(self, task: Task) -> None:
        """Called when a task completes successfully."""
        pass
    
    @abstractmethod
    def on_task_failed(self, task: Task, error: str) -> None:
        """Called when a task fails."""
        pass
    
    @abstractmethod
    def on_workflow_completed(self, workflow: Workflow) -> None:
        """Called when a workflow completes."""
        pass


class DefaultAgentCallback(AgentCallback):
    """Default implementation of agent callbacks."""
    
    def on_task_started(self, task: Task) -> None:
        logger.info(f"Task started: {task.name} ({task.id})")
    
    def on_task_completed(self, task: Task) -> None:
        logger.info(f"Task completed: {task.name} ({task.id})")
    
    def on_task_failed(self, task: Task, error: str) -> None:
        logger.error(f"Task failed: {task.name} ({task.id}) - {error}")
    
    def on_workflow_completed(self, workflow: Workflow) -> None:
        logger.info(f"Workflow completed: {workflow.name} ({workflow.id})")


class TaskScheduler:
    """Schedules and manages task execution order."""
    
    def __init__(self):
        self.task_graph = {}
        self.completed_tasks = set()
    
    def build_execution_graph(self, tasks: List[Task]) -> Dict[str, List[str]]:
        """Build task dependency graph."""
        graph = {task.id: task.dependencies for task in tasks}
        
        # Validate dependencies
        all_task_ids = {task.id for task in tasks}
        for task in tasks:
            for dep in task.dependencies:
                if dep not in all_task_ids:
                    raise ValueError(f"Task {task.id} depends on unknown task {dep}")
        
        return graph
    
    def get_ready_tasks(self, tasks: List[Task]) -> List[Task]:
        """Get tasks that are ready to execute."""
        ready_tasks = []
        
        for task in tasks:
            if (task.status == AgentStatus.IDLE and
                all(dep in self.completed_tasks for dep in task.dependencies)):
                ready_tasks.append(task)
        
        return ready_tasks
    
    def mark_task_completed(self, task_id: str) -> None:
        """Mark a task as completed."""
        self.completed_tasks.add(task_id)
    
    def has_circular_dependencies(self, tasks: List[Task]) -> bool:
        """Check for circular dependencies in task graph."""
        graph = self.build_execution_graph(tasks)
        
        def has_cycle(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        for task_id in graph:
            if task_id not in visited:
                if has_cycle(task_id, visited, set()):
                    return True
        
        return False


class LLMOrchestrationAgent:
    """Advanced LLM orchestration agent with workflow management."""
    
    def __init__(
        self,
        orchestrator: LLMOrchestrator,
        security_validator: Optional[SecurityValidator] = None,
        config_manager: Optional[ConfigManager] = None,
        max_concurrent_tasks: int = 5,
        callback: Optional[AgentCallback] = None
    ):
        self.orchestrator = orchestrator
        self.security_validator = security_validator
        self.config_manager = config_manager
        self.max_concurrent_tasks = max_concurrent_tasks
        self.callback = callback or DefaultAgentCallback()
        
        self.task_scheduler = TaskScheduler()
        self.active_workflows = {}
        self.task_queue = queue.Queue()
        self.result_cache = {}
        
        self.executor_threads = []
        self.shutdown_event = threading.Event()
        
        # Start task executor threads
        for i in range(max_concurrent_tasks):
            thread = threading.Thread(
                target=self._task_executor_loop,
                name=f"TaskExecutor-{i}",
                daemon=True
            )
            thread.start()
            self.executor_threads.append(thread)
        
        logger.info(f"LLM Orchestration Agent initialized with {max_concurrent_tasks} executors")
    
    def execute_task(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        security_context: Optional[SecurityContext] = None,
        timeout: int = 30
    ) -> LLMResponse:
        """Execute a single LLM task."""
        task = Task(
            id=str(uuid.uuid4()),
            name="single_task",
            prompt=prompt,
            context=context,
            timeout=timeout
        )
        
        return self._execute_single_task(task, security_context)
    
    def execute_workflow(
        self,
        workflow: Workflow,
        security_context: Optional[SecurityContext] = None
    ) -> Workflow:
        """Execute a complete workflow."""
        logger.info(f"Starting workflow execution: {workflow.name}")
        
        # Validate workflow
        self._validate_workflow(workflow)
        
        # Store workflow
        self.active_workflows[workflow.id] = workflow
        workflow.status = WorkflowStatus.IN_PROGRESS
        workflow.started_at = time.time()
        
        try:
            # Execute tasks
            self._execute_workflow_tasks(workflow, security_context)
            
            # Update workflow status
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = time.time()
            
            self.callback.on_workflow_completed(workflow)
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            logger.error(f"Workflow execution failed: {e}")
            raise
        
        finally:
            # Cleanup
            if workflow.id in self.active_workflows:
                del self.active_workflows[workflow.id]
        
        return workflow
    
    def create_task(
        self,
        name: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None,
        **kwargs
    ) -> Task:
        """Create a new task."""
        return Task(
            id=str(uuid.uuid4()),
            name=name,
            prompt=prompt,
            context=context or {},
            dependencies=dependencies or [],
            **kwargs
        )
    
    def create_workflow(
        self,
        name: str,
        description: str,
        tasks: List[Task],
        created_by: str = "system",
        **kwargs
    ) -> Workflow:
        """Create a new workflow."""
        return Workflow(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            tasks=tasks,
            created_by=created_by,
            **kwargs
        )
    
    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowStatus]:
        """Get current workflow status."""
        workflow = self.active_workflows.get(workflow_id)
        return workflow.status if workflow else None
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow."""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow.status = WorkflowStatus.CANCELLED
            
            # Cancel pending tasks
            for task in workflow.tasks:
                if task.status == AgentStatus.IDLE:
                    task.status = AgentStatus.CANCELLED
            
            logger.info(f"Workflow cancelled: {workflow.name}")
            return True
        
        return False
    
    def shutdown(self, timeout: int = 30) -> None:
        """Shutdown the agent gracefully."""
        logger.info("Shutting down LLM Orchestration Agent")
        
        # Signal shutdown
        self.shutdown_event.set()
        
        # Wait for threads to finish
        for thread in self.executor_threads:
            thread.join(timeout=timeout)
        
        logger.info("LLM Orchestration Agent shutdown complete")
    
    def _validate_workflow(self, workflow: Workflow) -> None:
        """Validate workflow before execution."""
        if not workflow.tasks:
            raise ValueError("Workflow must contain at least one task")
        
        # Check for circular dependencies
        if self.task_scheduler.has_circular_dependencies(workflow.tasks):
            raise ValueError("Workflow contains circular dependencies")
        
        # Validate task IDs are unique
        task_ids = [task.id for task in workflow.tasks]
        if len(task_ids) != len(set(task_ids)):
            raise ValueError("Workflow contains duplicate task IDs")
    
    def _execute_workflow_tasks(
        self,
        workflow: Workflow,
        security_context: Optional[SecurityContext]
    ) -> None:
        """Execute all tasks in a workflow."""
        pending_tasks = workflow.tasks.copy()
        
        while pending_tasks:
            # Get ready tasks
            ready_tasks = self.task_scheduler.get_ready_tasks(pending_tasks)
            
            if not ready_tasks:
                # Check if we're deadlocked
                if all(task.status == AgentStatus.IDLE for task in pending_tasks):
                    raise RuntimeError("Workflow deadlock detected")
                
                # Wait a bit for running tasks to complete
                time.sleep(0.1)
                continue
            
            # Execute ready tasks
            for task in ready_tasks:
                self._queue_task_execution(task, security_context)
                pending_tasks.remove(task)
            
            # Wait for some tasks to complete
            self._wait_for_task_completion(workflow)
    
    def _queue_task_execution(
        self,
        task: Task,
        security_context: Optional[SecurityContext]
    ) -> None:
        """Queue a task for execution."""
        self.task_queue.put((task, security_context))
    
    def _wait_for_task_completion(self, workflow: Workflow) -> None:
        """Wait for at least one task to complete."""
        while True:
            running_tasks = [
                task for task in workflow.tasks
                if task.status == AgentStatus.RUNNING
            ]
            
            if not running_tasks:
                break
            
            time.sleep(0.1)
    
    def _task_executor_loop(self) -> None:
        """Main loop for task executor threads."""
        while not self.shutdown_event.is_set():
            try:
                # Get task from queue with timeout
                task, security_context = self.task_queue.get(timeout=1.0)
                
                # Execute task
                self._execute_single_task(task, security_context)
                
                # Mark task as completed in scheduler
                if task.status == AgentStatus.COMPLETED:
                    self.task_scheduler.mark_task_completed(task.id)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Task executor error: {e}")
    
    def _execute_single_task(
        self,
        task: Task,
        security_context: Optional[SecurityContext]
    ) -> LLMResponse:
        """Execute a single task."""
        task.status = AgentStatus.RUNNING
        task.started_at = time.time()
        
        self.callback.on_task_started(task)
        
        try:
            # Security validation
            if self.security_validator and security_context:
                if not self.security_validator.validate_request(
                    task.prompt, task.context, security_context
                ):
                    raise SecurityError("Task failed security validation")
            
            # Create LLM request
            request = LLMRequest(
                prompt=task.prompt,
                context=task.context,
                security_level=task.security_level
            )
            
            # Execute with retry logic
            response = self._execute_with_retries(request, task.max_retries)
            
            # Security validation for response
            if self.security_validator and security_context:
                if not self.security_validator.validate_response(
                    response.content, security_context
                ):
                    raise SecurityError("Response failed security validation")
            
            # Update task
            task.result = response
            task.status = AgentStatus.COMPLETED
            task.completed_at = time.time()
            
            self.callback.on_task_completed(task)
            
            return response
            
        except Exception as e:
            error_msg = str(e)
            task.error = error_msg
            task.status = AgentStatus.FAILED
            task.completed_at = time.time()
            
            self.callback.on_task_failed(task, error_msg)
            
            raise
    
    def _execute_with_retries(
        self,
        request: LLMRequest,
        max_retries: int
    ) -> LLMResponse:
        """Execute LLM request with retry logic."""
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                request.retry_count = attempt
                return self.orchestrator.run(
                    request.prompt,
                    request.context
                )
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.warning(f"Task attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Task failed after {max_retries + 1} attempts: {e}")
        
        raise last_error


class WorkflowBuilder:
    """Builder for creating complex workflows."""
    
    def __init__(self):
        self.tasks = []
        self.task_lookup = {}
    
    def add_task(
        self,
        name: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        depends_on: Optional[List[str]] = None,
        **kwargs
    ) -> 'WorkflowBuilder':
        """Add a task to the workflow."""
        # Resolve dependencies
        dependencies = []
        if depends_on:
            for dep_name in depends_on:
                if dep_name not in self.task_lookup:
                    raise ValueError(f"Unknown dependency: {dep_name}")
                dependencies.append(self.task_lookup[dep_name])
        
        # Create task
        task = Task(
            id=str(uuid.uuid4()),
            name=name,
            prompt=prompt,
            context=context or {},
            dependencies=dependencies,
            **kwargs
        )
        
        self.tasks.append(task)
        self.task_lookup[name] = task.id
        
        return self
    
    def add_parallel_tasks(
        self,
        task_configs: List[Dict[str, Any]]
    ) -> 'WorkflowBuilder':
        """Add multiple tasks that can run in parallel."""
        for config in task_configs:
            self.add_task(**config)
        
        return self
    
    def add_sequential_tasks(
        self,
        task_configs: List[Dict[str, Any]]
    ) -> 'WorkflowBuilder':
        """Add tasks that must run sequentially."""
        previous_task = None
        
        for config in task_configs:
            if previous_task:
                config['depends_on'] = [previous_task]
            
            self.add_task(**config)
            previous_task = config['name']
        
        return self
    
    def build(
        self,
        name: str,
        description: str,
        created_by: str = "system"
    ) -> Workflow:
        """Build the workflow."""
        return Workflow(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            tasks=self.tasks,
            created_by=created_by
        )


class SecurityError(Exception):
    """Security-related error."""
    pass


# Workflow templates for common use cases
class WorkflowTemplates:
    """Pre-built workflow templates."""
    
    @staticmethod
    def create_analysis_workflow(
        data: str,
        analysis_types: List[str]
    ) -> Workflow:
        """Create a data analysis workflow."""
        builder = WorkflowBuilder()
        
        # Initial data processing
        builder.add_task(
            name="data_preprocessing",
            prompt=f"Preprocess and clean the following data for analysis: {data}",
            context={"data": data}
        )
        
        # Parallel analysis tasks
        analysis_tasks = []
        for analysis_type in analysis_types:
            task_config = {
                "name": f"{analysis_type}_analysis",
                "prompt": f"Perform {analysis_type} analysis on the preprocessed data",
                "depends_on": ["data_preprocessing"],
                "context": {"analysis_type": analysis_type}
            }
            analysis_tasks.append(task_config)
        
        builder.add_parallel_tasks(analysis_tasks)
        
        # Final synthesis
        builder.add_task(
            name="synthesis",
            prompt="Synthesize all analysis results into a comprehensive report",
            depends_on=[f"{at}_analysis" for at in analysis_types]
        )
        
        return builder.build(
            name="Data Analysis Workflow",
            description="Comprehensive data analysis with multiple analysis types"
        )
    
    @staticmethod
    def create_content_generation_workflow(
        topic: str,
        content_types: List[str]
    ) -> Workflow:
        """Create a content generation workflow."""
        builder = WorkflowBuilder()
        
        # Research phase
        builder.add_task(
            name="research",
            prompt=f"Research comprehensive information about: {topic}",
            context={"topic": topic}
        )
        
        # Content generation tasks
        for content_type in content_types:
            builder.add_task(
                name=f"generate_{content_type}",
                prompt=f"Generate {content_type} content based on the research",
                depends_on=["research"],
                context={"content_type": content_type, "topic": topic}
            )
        
        # Quality review
        builder.add_task(
            name="quality_review",
            prompt="Review all generated content for quality and consistency",
            depends_on=[f"generate_{ct}" for ct in content_types]
        )
        
        return builder.build(
            name="Content Generation Workflow",
            description=f"Multi-format content generation for {topic}"
        )
