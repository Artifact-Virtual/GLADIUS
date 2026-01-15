"""
Enhanced Agent Base Class with All New Features Integrated
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

# Import new systems
from message_bus import message_bus, Message
from agent_memory import agent_memory_system
from distributed_tracing import tracing_system
from self_improvement import self_improvement_system

logger = logging.getLogger(__name__)


class EnhancedAgentBase:
    """
    Enhanced agent base class with all new capabilities:
    - Inter-agent communication via message bus
    - Episodic, semantic, and procedural memory
    - Distributed tracing
    - Self-improvement and learning
    """
    
    def __init__(self, agent_id: str, agent_type: str, department: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.department = department
        self.capabilities = capabilities
        self.status = "initializing"
        
        # Register with message bus
        message_bus.register_agent(self.agent_id, self._handle_message)
        
        logger.info(f"Enhanced agent {self.agent_id} initialized with new capabilities")
    
    async def initialize(self):
        """Initialize the enhanced agent"""
        self.status = "active"
        logger.info(f"Agent {self.agent_id} initialized and ready")
    
    async def _handle_message(self, message: Message) -> Optional[Dict[str, Any]]:
        """
        Handle incoming messages from message bus
        Override in subclasses for custom behavior
        """
        logger.info(f"Agent {self.agent_id} received message: {message.message_type}")
        
        # Record message in episodic memory
        agent_memory_system.remember_experience(
            agent_id=self.agent_id,
            event_type="message_received",
            description=f"Received {message.message_type} from {message.sender_id}",
            context={
                "message_id": message.message_id,
                "sender": message.sender_id,
                "content": message.content
            },
            importance=0.7 if message.priority > 5 else 0.5
        )
        
        # Process message
        response = await self.process_message(message)
        
        return response
    
    async def process_message(self, message: Message) -> Optional[Dict[str, Any]]:
        """
        Process message - override in subclasses
        """
        return {"status": "processed", "agent_id": self.agent_id}
    
    async def send_message(self, recipient_id: str, message_type: str, 
                          content: Dict[str, Any], priority: int = 5,
                          response_required: bool = False) -> bool:
        """Send a message to another agent"""
        message = Message(
            message_id=str(uuid.uuid4()),
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            message_type=message_type,
            content=content,
            timestamp=datetime.now(),
            priority=priority,
            response_required=response_required,
            trace_id=tracing_system.get_current_trace_id()
        )
        
        success = await message_bus.send_message(message)
        
        if success:
            # Remember sending message
            agent_memory_system.remember_experience(
                agent_id=self.agent_id,
                event_type="message_sent",
                description=f"Sent {message_type} to {recipient_id}",
                context={
                    "message_id": message.message_id,
                    "recipient": recipient_id,
                    "content": content
                },
                importance=0.6
            )
        
        return success
    
    async def broadcast_message(self, message_type: str, content: Dict[str, Any]) -> int:
        """Broadcast message to all agents"""
        return await message_bus.broadcast_message(
            sender_id=self.agent_id,
            message_type=message_type,
            content=content
        )
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task with tracing and learning
        """
        task_type = task.get('type', 'unknown')
        
        # Start tracing
        with tracing_system.trace_operation(
            operation_name=f"execute_{task_type}",
            tags={"agent_id": self.agent_id, "task_type": task_type},
            agent_id=self.agent_id
        ) as span_id:
            
            start_time = datetime.now()
            
            try:
                # Execute task (override in subclass)
                result = await self._execute_task_impl(task)
                
                execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
                
                # Record successful execution
                await self._record_task_feedback(
                    task_type=task_type,
                    success=True,
                    execution_time_ms=execution_time_ms,
                    quality_score=result.get('quality_score', 1.0)
                )
                
                # Remember successful task
                agent_memory_system.remember_experience(
                    agent_id=self.agent_id,
                    event_type="task_completed",
                    description=f"Completed {task_type} successfully",
                    context={"task": task, "result": result},
                    importance=0.8,
                    emotional_valence=0.5,
                    outcome="success"
                )
                
                return result
                
            except Exception as e:
                execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
                
                # Record failed execution
                await self._record_task_feedback(
                    task_type=task_type,
                    success=False,
                    execution_time_ms=execution_time_ms,
                    quality_score=0.0,
                    error_details=str(e)
                )
                
                # Remember failure for learning
                agent_memory_system.remember_experience(
                    agent_id=self.agent_id,
                    event_type="task_failed",
                    description=f"Failed {task_type}: {str(e)}",
                    context={"task": task, "error": str(e)},
                    importance=0.9,
                    emotional_valence=-0.5,
                    outcome="failure"
                )
                
                raise
    
    async def _execute_task_impl(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actual task execution - override in subclass
        """
        return {"status": "completed", "agent_id": self.agent_id}
    
    async def _record_task_feedback(self, task_type: str, success: bool,
                                   execution_time_ms: float, quality_score: float = 1.0,
                                   error_details: str = None):
        """Record feedback for self-improvement"""
        await self_improvement_system.record_feedback(
            agent_id=self.agent_id,
            task_type=task_type,
            success=success,
            execution_time_ms=execution_time_ms,
            quality_score=quality_score,
            error_details=error_details
        )
    
    def learn_knowledge(self, category: str, concept: str, knowledge: Dict[str, Any]):
        """Learn new knowledge (semantic memory)"""
        return agent_memory_system.learn_knowledge(
            agent_id=self.agent_id,
            category=category,
            concept=concept,
            knowledge=knowledge
        )
    
    def learn_skill(self, skill_name: str, procedure_steps: List[Dict[str, Any]]):
        """Learn new skill (procedural memory)"""
        return agent_memory_system.learn_skill(
            agent_id=self.agent_id,
            skill_name=skill_name,
            procedure_steps=procedure_steps
        )
    
    def recall_experiences(self, event_type: str = None, limit: int = 10):
        """Recall past experiences (episodic memory)"""
        return agent_memory_system.recall_experiences(
            agent_id=self.agent_id,
            event_type=event_type,
            limit=limit
        )
    
    def recall_knowledge(self, category: str = None, concept: str = None, limit: int = 10):
        """Recall knowledge (semantic memory)"""
        return agent_memory_system.recall_knowledge(
            agent_id=self.agent_id,
            category=category,
            concept=concept,
            limit=limit
        )
    
    def recall_skills(self, skill_name: str = None, limit: int = 10):
        """Recall skills (procedural memory)"""
        return agent_memory_system.recall_skills(
            agent_id=self.agent_id,
            skill_name=skill_name,
            limit=limit
        )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary with self-improvement insights"""
        return self_improvement_system.get_agent_performance_summary(
            agent_id=self.agent_id
        )
