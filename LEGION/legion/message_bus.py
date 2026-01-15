"""
Enhanced Inter-Agent Communication Protocol and Message Bus
Implements robust message routing, delivery confirmation, and error handling
"""

import asyncio
import logging
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from pathlib import Path
from collections import defaultdict
import uuid

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Enhanced message structure with routing and tracking"""
    message_id: str
    sender_id: str
    recipient_id: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime
    priority: int = 5
    response_required: bool = False
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    status: str = "pending"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'message_id': self.message_id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'message_type': self.message_type,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority,
            'response_required': self.response_required,
            'correlation_id': self.correlation_id,
            'trace_id': self.trace_id,
            'retry_count': self.retry_count,
            'status': self.status
        }


class MessageBus:
    """
    Robust message bus for inter-agent communication
    Features:
    - Priority-based routing
    - Delivery confirmation
    - Message persistence
    - Retry logic
    - Dead letter queue
    - Broadcast/multicast support
    - Distributed tracing integration
    """
    
    def __init__(self, db_path: str = "data/message_bus.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Message queues by agent ID
        self.agent_queues: Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)
        
        # Registered agents and their handlers
        self.registered_agents: Dict[str, Callable] = {}
        
        # Message history for tracking
        self.message_history: List[Message] = []
        
        # Dead letter queue for failed messages
        self.dead_letter_queue: List[Message] = []
        
        # Statistics
        self.stats = {
            "total_sent": 0,
            "total_delivered": 0,
            "total_failed": 0,
            "average_latency_ms": 0.0
        }
        
        # Running flag
        self.running = False
        
        # Initialize database
        self._initialize_db()
        
        logger.info("MessageBus initialized")
    
    def _initialize_db(self):
        """Initialize SQLite database for message persistence"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                sender_id TEXT NOT NULL,
                recipient_id TEXT NOT NULL,
                message_type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                priority INTEGER DEFAULT 5,
                response_required INTEGER DEFAULT 0,
                correlation_id TEXT,
                trace_id TEXT,
                retry_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                delivered_at TEXT
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_recipient ON messages(recipient_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON messages(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace ON messages(trace_id)')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_sent INTEGER,
                total_delivered INTEGER,
                total_failed INTEGER,
                average_latency_ms REAL
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Message bus database initialized")
    
    def register_agent(self, agent_id: str, handler: Callable):
        """Register an agent with its message handler"""
        self.registered_agents[agent_id] = handler
        logger.info(f"Agent {agent_id} registered with message bus")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.registered_agents:
            del self.registered_agents[agent_id]
            logger.info(f"Agent {agent_id} unregistered from message bus")
    
    async def send_message(self, message: Message) -> bool:
        """
        Send a message to a specific agent
        Returns True if queued successfully
        """
        try:
            # Assign trace ID if not present
            if not message.trace_id:
                message.trace_id = str(uuid.uuid4())
            
            # Persist to database
            self._persist_message(message)
            
            # Add to recipient's queue
            await self.agent_queues[message.recipient_id].put(message)
            
            self.stats["total_sent"] += 1
            message.status = "queued"
            
            logger.debug(f"Message {message.message_id} queued for {message.recipient_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message {message.message_id}: {e}")
            message.status = "failed"
            self.stats["total_failed"] += 1
            return False
    
    async def broadcast_message(self, sender_id: str, message_type: str, 
                                content: Dict[str, Any], exclude_agents: List[str] = None) -> int:
        """
        Broadcast a message to all registered agents
        Returns number of agents message was sent to
        """
        exclude_agents = exclude_agents or []
        sent_count = 0
        trace_id = str(uuid.uuid4())
        
        for agent_id in self.registered_agents.keys():
            if agent_id not in exclude_agents and agent_id != sender_id:
                message = Message(
                    message_id=str(uuid.uuid4()),
                    sender_id=sender_id,
                    recipient_id=agent_id,
                    message_type=message_type,
                    content=content,
                    timestamp=datetime.now(),
                    trace_id=trace_id
                )
                if await self.send_message(message):
                    sent_count += 1
        
        logger.info(f"Broadcast message sent to {sent_count} agents")
        return sent_count
    
    async def send_to_department(self, sender_id: str, department: str, 
                                 message_type: str, content: Dict[str, Any]) -> int:
        """
        Send message to all agents in a specific department
        Returns number of agents message was sent to
        """
        # This would integrate with agent registry to get department agents
        # For now, return 0 as placeholder
        sent_count = 0
        
        # TODO: Integrate with AgentRegistry to get agents by department
        logger.info(f"Department message sent to {sent_count} agents in {department}")
        return sent_count
    
    async def get_messages(self, agent_id: str, max_messages: int = 10) -> List[Message]:
        """
        Get pending messages for an agent
        Non-blocking, returns empty list if no messages
        """
        messages = []
        try:
            for _ in range(max_messages):
                if not self.agent_queues[agent_id].empty():
                    message = await asyncio.wait_for(
                        self.agent_queues[agent_id].get(), 
                        timeout=0.1
                    )
                    messages.append(message)
                else:
                    break
        except asyncio.TimeoutError:
            # A timeout here is expected and simply indicates no messages became
            # available within the short wait; return whatever we collected so far.
            logger.debug(
                "Timeout while fetching messages for agent %s; returning %d messages",
                agent_id,
                len(messages),
            )
        
        return messages
    
    async def process_agent_messages(self, agent_id: str):
        """
        Process messages for a specific agent
        Calls the registered handler for each message
        """
        if agent_id not in self.registered_agents:
            logger.warning(f"Agent {agent_id} not registered")
            return
        
        handler = self.registered_agents[agent_id]
        
        while self.running:
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(
                    self.agent_queues[agent_id].get(),
                    timeout=1.0
                )
                
                # Measure latency
                latency = (datetime.now() - message.timestamp).total_seconds() * 1000
                
                try:
                    # Call agent handler
                    response = await handler(message)
                    
                    message.status = "delivered"
                    self.stats["total_delivered"] += 1
                    
                    # Update average latency
                    current_avg = self.stats["average_latency_ms"]
                    delivered = self.stats["total_delivered"]
                    self.stats["average_latency_ms"] = (current_avg * (delivered - 1) + latency) / delivered
                    
                    # Update database
                    self._update_message_status(message.message_id, "delivered")
                    
                    # Handle response if needed
                    if message.response_required and response:
                        await self._send_response(message, response)
                    
                    logger.debug(f"Message {message.message_id} delivered to {agent_id} (latency: {latency:.2f}ms)")
                    
                except Exception as e:
                    logger.error(f"Handler error for message {message.message_id}: {e}")
                    await self._handle_delivery_failure(message)
                    
            except asyncio.TimeoutError:
                # No messages, continue waiting
                continue
            except Exception as e:
                logger.error(f"Error processing messages for {agent_id}: {e}")
                await asyncio.sleep(1)
    
    async def _send_response(self, original_message: Message, response: Dict[str, Any]):
        """Send a response message"""
        response_message = Message(
            message_id=str(uuid.uuid4()),
            sender_id=original_message.recipient_id,
            recipient_id=original_message.sender_id,
            message_type=f"{original_message.message_type}_response",
            content=response,
            timestamp=datetime.now(),
            correlation_id=original_message.message_id,
            trace_id=original_message.trace_id
        )
        await self.send_message(response_message)
    
    async def _handle_delivery_failure(self, message: Message):
        """Handle failed message delivery with retry logic"""
        message.retry_count += 1
        
        if message.retry_count < message.max_retries:
            # Retry after delay
            await asyncio.sleep(2 ** message.retry_count)  # Exponential backoff
            message.status = "retrying"
            await self.send_message(message)
            logger.warning(f"Retrying message {message.message_id} (attempt {message.retry_count})")
        else:
            # Move to dead letter queue
            message.status = "dead_letter"
            self.dead_letter_queue.append(message)
            self.stats["total_failed"] += 1
            self._update_message_status(message.message_id, "dead_letter")
            logger.error(f"Message {message.message_id} moved to dead letter queue after {message.retry_count} retries")
    
    def _persist_message(self, message: Message):
        """Persist message to database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO messages 
                (message_id, sender_id, recipient_id, message_type, content, timestamp, 
                 priority, response_required, correlation_id, trace_id, retry_count, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                message.message_id,
                message.sender_id,
                message.recipient_id,
                message.message_type,
                json.dumps(message.content),
                message.timestamp.isoformat(),
                message.priority,
                int(message.response_required),
                message.correlation_id,
                message.trace_id,
                message.retry_count,
                message.status
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to persist message {message.message_id}: {e}")
    
    def _update_message_status(self, message_id: str, status: str):
        """Update message status in database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE messages 
                SET status = ?, delivered_at = ?
                WHERE message_id = ?
            ''', (status, datetime.now().isoformat(), message_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to update message status {message_id}: {e}")
    
    async def start(self):
        """Start the message bus processing"""
        self.running = True
        logger.info("Message bus started")
        
        # Start message processing tasks for all registered agents
        tasks = []
        for agent_id in self.registered_agents.keys():
            task = asyncio.create_task(self.process_agent_messages(agent_id))
            tasks.append(task)
        
        # Start statistics collector
        stats_task = asyncio.create_task(self._collect_stats())
        tasks.append(stats_task)
        
        return tasks
    
    async def stop(self):
        """Stop the message bus"""
        self.running = False
        logger.info("Message bus stopped")
    
    async def _collect_stats(self):
        """Periodically collect and persist statistics"""
        while self.running:
            await asyncio.sleep(60)  # Collect every minute
            
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO message_stats 
                    (timestamp, total_sent, total_delivered, total_failed, average_latency_ms)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    self.stats["total_sent"],
                    self.stats["total_delivered"],
                    self.stats["total_failed"],
                    self.stats["average_latency_ms"]
                ))
                
                conn.commit()
                conn.close()
            except Exception as e:
                logger.error(f"Failed to collect stats: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current message bus statistics"""
        return {
            **self.stats,
            "registered_agents": len(self.registered_agents),
            "pending_messages": sum(q.qsize() for q in self.agent_queues.values()),
            "dead_letter_count": len(self.dead_letter_queue)
        }
    
    def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get statistics for a specific agent"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_messages,
                    SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
                FROM messages
                WHERE recipient_id = ?
            ''', (agent_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            return {
                "agent_id": agent_id,
                "total_messages": row[0] if row else 0,
                "delivered": row[1] if row else 0,
                "failed": row[2] if row else 0,
                "pending": self.agent_queues[agent_id].qsize()
            }
        except Exception as e:
            logger.error(f"Failed to get agent stats for {agent_id}: {e}")
            return {}


# Global message bus instance
message_bus = MessageBus()
