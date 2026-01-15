"""
Enterprise Legion Core Framework
Advanced AI Agent Framework with sophisticated orchestration
"""

import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
import uuid
import sqlite3
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AgentMessage:
    """Message structure for inter-agent communication"""
    message_id: str
    sender_id: str
    recipient_id: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime
    priority: int = 5
    response_required: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'message_id': self.message_id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'message_type': self.message_type,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority,
            'response_required': self.response_required
        }

@dataclass
class AgentTask:
    """Task structure for agent workflows"""
    task_id: str
    agent_id: str
    task_type: str
    description: str
    parameters: Dict[str, Any]
    status: str = "pending"
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class BaseAgent:
    """Base class for all Enterprise Legion agents"""
    
    def __init__(self, agent_id: str, agent_type: str, department: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.department = department
        self.capabilities = capabilities
        self.status = "initializing"
        self.message_queue = []
        self.task_queue = []
        self.last_heartbeat = datetime.now()
        self.performance_metrics = {}
        self.logger = logging.getLogger(f"{self.agent_type}.{self.agent_id}")
        
    async def initialize(self):
        """Initialize the agent"""
        self.logger.info(f"Initializing agent {self.agent_id}")
        self.status = "active"
        return True
        
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming message"""
        self.logger.info(f"Agent {self.agent_id} processing message from {message.sender_id}")
        # Override in subclasses
        return None
        
    async def process_task(self, task) -> Dict[str, Any]:
        """Process a task - default implementation"""
        self.logger.info(f"Agent {self.agent_id} processing task")
        return {"status": "success", "message": "Task processed"}
        
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a task"""
        self.logger.info(f"Agent {self.agent_id} executing task {task.task_id}")
        task.started_at = datetime.now()
        task.status = "running"
        
        # Override in subclasses
        result = {"status": "completed", "data": {}}
        
        task.completed_at = datetime.now()
        task.status = "completed"
        task.result = result
        
        return result
        
    def send_heartbeat(self):
        """Send heartbeat signal"""
        self.last_heartbeat = datetime.now()
        
    def is_healthy(self) -> bool:
        """Check if agent is healthy"""
        time_since_heartbeat = datetime.now() - self.last_heartbeat
        return time_since_heartbeat.total_seconds() < 60  # 60 seconds timeout

class EnterpriseAgent(BaseAgent):
    """Specialized enterprise agent with advanced features"""
    
    def __init__(self, agent_id: str, agent_type: str, department: str, capabilities: List[str], 
                 config: Dict[str, Any] = None):
        super().__init__(agent_id, agent_type, department, capabilities)
        self.config = config or {}
        self.knowledge_base = {}
        self.collaboration_history = []
        
    async def collaborate_with(self, other_agent_id: str, task_description: str) -> Dict[str, Any]:
        """Collaborate with another agent"""
        logger.info(f"Agent {self.agent_id} collaborating with {other_agent_id} on: {task_description}")
        
        collaboration_record = {
            "timestamp": datetime.now().isoformat(),
            "partner_agent": other_agent_id,
            "task": task_description,
            "status": "initiated"
        }
        
        self.collaboration_history.append(collaboration_record)
        return collaboration_record
        
    def update_knowledge(self, key: str, value: Any):
        """Update agent's knowledge base"""
        self.knowledge_base[key] = {
            "value": value,
            "updated_at": datetime.now().isoformat()
        }
        
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get agent performance summary"""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "tasks_completed": len([t for t in self.task_queue if t.status == "completed"]),
            "messages_processed": len(self.message_queue),
            "collaborations": len(self.collaboration_history),
            "knowledge_items": len(self.knowledge_base)
        }

class AgentRegistry:
    """Registry for managing all enterprise agents"""
    
    def __init__(self):
        self.agents: Dict[str, EnterpriseAgent] = {}
        self.agent_types: Dict[str, List[str]] = {}
        self.departments: Dict[str, List[str]] = {}
        
    def register_agent(self, agent: EnterpriseAgent):
        """Register a new agent"""
        self.agents[agent.agent_id] = agent
        
        # Update type registry
        if agent.agent_type not in self.agent_types:
            self.agent_types[agent.agent_type] = []
        self.agent_types[agent.agent_type].append(agent.agent_id)
        
        # Update department registry
        if agent.department not in self.departments:
            self.departments[agent.department] = []
        self.departments[agent.department].append(agent.agent_id)
        
        logger.info(f"Registered agent {agent.agent_id} in department {agent.department}")
        
    def get_agent(self, agent_id: str) -> Optional[EnterpriseAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
        
    def get_agents_by_department(self, department: str) -> List[EnterpriseAgent]:
        """Get all agents in a department"""
        agent_ids = self.departments.get(department, [])
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]
        
    def get_agents_by_type(self, agent_type: str) -> List[EnterpriseAgent]:
        """Get all agents of a specific type"""
        agent_ids = self.agent_types.get(agent_type, [])
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]
        
    def get_all_agents(self) -> List[EnterpriseAgent]:
        """Get all registered agents"""
        return list(self.agents.values())
        
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all agents"""
        healthy_agents = []
        unhealthy_agents = []
        
        for agent in self.agents.values():
            if agent.is_healthy():
                healthy_agents.append(agent.agent_id)
            else:
                unhealthy_agents.append(agent.agent_id)
                
        return {
            "total_agents": len(self.agents),
            "healthy_agents": healthy_agents,
            "unhealthy_agents": unhealthy_agents,
            "health_ratio": len(healthy_agents) / len(self.agents) if self.agents else 0
        }

# Global registry instance
enterprise_registry = AgentRegistry()
