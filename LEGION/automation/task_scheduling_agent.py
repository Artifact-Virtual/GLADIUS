"""
Task Scheduling Agent - Enterprise Legion Fixed
Manages task scheduling, prioritization, and deadline coordination
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import uuid
import heapq
import sys
import os

# Add enterprise directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core_framework import BaseAgent, AgentTask, AgentMessage

logger = logging.getLogger(__name__)


class Priority(Enum):
    """Task priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class TaskStatus(Enum):
    """Task status types"""
    PENDING = "pending"
    SCHEDULED = "scheduled" 
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledTask:
    """Scheduled task definition"""
    task_id: str
    agent_id: str
    task_type: str
    description: str
    priority: Priority
    scheduled_time: datetime
    deadline: Optional[datetime] = None
    dependencies: List[str] = None
    recurring: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class TaskSchedulingAgent(BaseAgent):
    """Advanced task scheduling and coordination agent"""
    
    def __init__(self, agent_id: str = "task_scheduling_agent"):
        capabilities = [
            "task_scheduling",
            "priority_management", 
            "deadline_tracking",
            "resource_coordination",
            "workflow_integration"
        ]
        super().__init__(agent_id, "TaskSchedulingAgent", "automation", capabilities)
        
        self.scheduled_tasks = {}
        self.task_queue = []  # Priority queue
        self.running_tasks = {}
        self.completed_tasks = []
        self.recurring_patterns = {}
        self.scheduling_algorithms = {
            "priority_first": self._priority_first_scheduling,
            "earliest_deadline": self._earliest_deadline_first,
            "round_robin": self._round_robin_scheduling
        }
        self.integration_points = [
            "workflow_orchestrator",
            "resource_optimizer", 
            "performance_monitor",
            "all_department_agents"
        ]
        self._initialize_recurring_patterns()
    
    async def initialize(self) -> bool:
        """Initialize the agent"""
        try:
            logger.info(f"Initializing {self.agent_id}...")
            await super().initialize()
            logger.info(f"{self.agent_id} initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize {self.agent_id}: {e}")
            return False
    
    def _initialize_recurring_patterns(self):
        """Initialize predefined recurring patterns"""
        self.recurring_patterns = {
            "daily": {"interval": 1, "unit": "days"},
            "weekly": {"interval": 1, "unit": "weeks"}, 
            "monthly": {"interval": 1, "unit": "months"},
            "hourly": {"interval": 1, "unit": "hours"}
        }
    
    async def process_task(self, task) -> Dict[str, Any]:
        """Process task scheduling operations"""
        try:
            # Handle both AgentTask objects and dicts
            if hasattr(task, 'parameters'):
                task_data = task.parameters
                task_type = getattr(task, 'task_type', 'task_management')
            else:
                task_data = task
                task_type = task_data.get('type', 'task_management')
            
            action = task_data.get('action', 'schedule')
            
            if action == "schedule":
                return await self._schedule_task(task_data)
            elif action == "cancel":
                return await self._cancel_task(task_data)
            elif action == "get_schedule":
                return await self._get_schedule(task_data)
            else:
                return {"status": "error", "message": "Unknown action"}
                
        except Exception as e:
            logger.error(f"Error in task scheduling: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _schedule_task(self, params: Dict) -> Dict[str, Any]:
        """Schedule a new task"""
        try:
            task_id = params.get('task_id', str(uuid.uuid4()))
            agent_id = params.get('agent_id', 'unknown')
            task_type = params.get('task_type', 'general')
            description = params.get('description', 'No description')
            priority = Priority(params.get('priority', 3))
            scheduled_time = params.get('scheduled_time', datetime.now())
            deadline = params.get('deadline')
            dependencies = params.get('dependencies', [])
            recurring = params.get('recurring')
            
            # Convert string datetime if needed
            if isinstance(scheduled_time, str):
                scheduled_time = datetime.fromisoformat(scheduled_time)
            if isinstance(deadline, str) and deadline:
                deadline = datetime.fromisoformat(deadline)
            
            scheduled_task = ScheduledTask(
                task_id=task_id,
                agent_id=agent_id,
                task_type=task_type,
                description=description,
                priority=priority,
                scheduled_time=scheduled_time,
                deadline=deadline,
                dependencies=dependencies,
                recurring=recurring
            )
            
            self.scheduled_tasks[task_id] = scheduled_task
            await self._add_to_queue(scheduled_task)
            
            logger.info(f"Scheduled task {task_id} for agent {agent_id}")
            
            return {
                "status": "success",
                "task_id": task_id,
                "scheduled_time": scheduled_time.isoformat(),
                "agent_id": agent_id
            }
            
        except Exception as e:
            logger.error(f"Error scheduling task: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _add_to_queue(self, scheduled_task: ScheduledTask):
        """Add task to priority queue"""
        priority_score = self._calculate_priority_score(scheduled_task)
        heapq.heappush(self.task_queue, (-priority_score, scheduled_task.task_id))
        scheduled_task.status = TaskStatus.SCHEDULED
    
    def _calculate_priority_score(self, task: ScheduledTask) -> float:
        """Calculate priority score for task ordering"""
        base_priority = task.priority.value
        
        # Time urgency factor
        time_until_deadline = 1.0
        if task.deadline:
            hours_until_deadline = (task.deadline - datetime.now()).total_seconds() / 3600
            time_until_deadline = max(0.1, min(1.0, hours_until_deadline / 24))
        
        # Dependency factor
        dependency_factor = 1.0 + (len(task.dependencies) * 0.1)
        
        return (10 - base_priority) * time_until_deadline * dependency_factor
    
    async def _cancel_task(self, params: Dict) -> Dict[str, Any]:
        """Cancel a scheduled task"""
        task_id = params.get('task_id')
        
        if task_id in self.scheduled_tasks:
            task = self.scheduled_tasks[task_id]
            task.status = TaskStatus.CANCELLED
            
            # Remove from queue if present
            self.task_queue = [(p, tid) for p, tid in self.task_queue if tid != task_id]
            heapq.heapify(self.task_queue)
            
            logger.info(f"Cancelled task {task_id}")
            return {"status": "success", "cancelled_task": task_id}
        else:
            return {"status": "error", "message": "Task not found"}
    
    async def _get_schedule(self, params: Dict) -> Dict[str, Any]:
        """Get current schedule information"""
        agent_id = params.get('agent_id')
        
        if agent_id:
            filtered_tasks = [
                {
                    "task_id": task.task_id,
                    "description": task.description,
                    "status": task.status.value,
                    "scheduled_time": task.scheduled_time.isoformat(),
                    "priority": task.priority.name
                }
                for task in self.scheduled_tasks.values()
                if task.agent_id == agent_id
            ]
        else:
            filtered_tasks = [
                {
                    "task_id": task.task_id,
                    "agent_id": task.agent_id,
                    "description": task.description,
                    "status": task.status.value,
                    "scheduled_time": task.scheduled_time.isoformat(),
                    "priority": task.priority.name
                }
                for task in self.scheduled_tasks.values()
            ]
        
        return {
            "status": "success",
            "total_tasks": len(filtered_tasks),
            "tasks": filtered_tasks,
            "queue_length": len(self.task_queue)
        }
    
    async def _priority_first_scheduling(self) -> Dict[str, Any]:
        """Priority-first scheduling algorithm"""
        # Sort by priority
        sorted_tasks = sorted(
            [task for task in self.scheduled_tasks.values() if task.status == TaskStatus.SCHEDULED],
            key=lambda t: t.priority.value
        )
        
        # Rebuild queue
        self.task_queue.clear()
        for task in sorted_tasks:
            priority_score = self._calculate_priority_score(task)
            heapq.heappush(self.task_queue, (-priority_score, task.task_id))
        
        return {"reordered_tasks": len(sorted_tasks), "optimization_type": "priority_first"}
    
    async def _earliest_deadline_first(self) -> Dict[str, Any]:
        """Earliest deadline first scheduling"""
        tasks_with_deadlines = [
            task for task in self.scheduled_tasks.values() 
            if task.status == TaskStatus.SCHEDULED and task.deadline
        ]
        
        sorted_tasks = sorted(tasks_with_deadlines, key=lambda t: t.deadline)
        
        # Rebuild queue
        self.task_queue.clear()
        for task in sorted_tasks:
            priority_score = self._calculate_priority_score(task)
            heapq.heappush(self.task_queue, (-priority_score, task.task_id))
        
        return {"reordered_tasks": len(sorted_tasks), "optimization_type": "earliest_deadline_first"}
    
    async def _round_robin_scheduling(self) -> Dict[str, Any]:
        """Round-robin scheduling by agent"""
        # Group tasks by agent
        agent_tasks = {}
        
        for task in self.scheduled_tasks.values():
            if task.status == TaskStatus.SCHEDULED:
                if task.agent_id not in agent_tasks:
                    agent_tasks[task.agent_id] = []
                agent_tasks[task.agent_id].append(task)
        
        # Clear queue and rebuild in round-robin order
        self.task_queue.clear()
        
        max_tasks = max(len(tasks) for tasks in agent_tasks.values()) if agent_tasks else 0
        
        for i in range(max_tasks):
            for agent_id, tasks in agent_tasks.items():
                if i < len(tasks):
                    task = tasks[i]
                    priority_score = self._calculate_priority_score(task)
                    heapq.heappush(self.task_queue, (-priority_score, task.task_id))
        
        return {
            "reordered_tasks": sum(len(tasks) for tasks in agent_tasks.values()),
            "optimization_type": "round_robin_by_agent"
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "total_scheduled_tasks": len(self.scheduled_tasks),
            "queue_length": len(self.task_queue),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "capabilities": self.capabilities,
            "last_heartbeat": self.last_heartbeat.isoformat()
        }
