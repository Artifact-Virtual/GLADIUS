"""
Agent Memory System - Episodic and Semantic Memory
Implements multi-tier memory storage with SQLite backend (swappable with vector DB)
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import hashlib
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@dataclass
class EpisodicMemory:
    """
    Episodic memory - stores experiences and events
    What happened, when, and in what context
    """
    memory_id: str
    agent_id: str
    event_type: str
    description: str
    context: Dict[str, Any]
    timestamp: datetime
    importance: float  # 0.0 to 1.0
    emotional_valence: float  # -1.0 to 1.0
    outcome: Optional[str] = None
    learned_from: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'memory_id': self.memory_id,
            'agent_id': self.agent_id,
            'event_type': self.event_type,
            'description': self.description,
            'context': self.context,
            'timestamp': self.timestamp.isoformat(),
            'importance': self.importance,
            'emotional_valence': self.emotional_valence,
            'outcome': self.outcome,
            'learned_from': self.learned_from
        }


@dataclass
class SemanticMemory:
    """
    Semantic memory - stores knowledge and facts
    What the agent knows about the world
    """
    memory_id: str
    agent_id: str
    category: str
    concept: str
    knowledge: Dict[str, Any]
    confidence: float  # 0.0 to 1.0
    source: str
    timestamp: datetime
    last_accessed: datetime
    access_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'memory_id': self.memory_id,
            'agent_id': self.agent_id,
            'category': self.category,
            'concept': self.concept,
            'knowledge': self.knowledge,
            'confidence': self.confidence,
            'source': self.source,
            'timestamp': self.timestamp.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            'access_count': self.access_count
        }


@dataclass
class ProceduralMemory:
    """
    Procedural memory - stores skills and how-to knowledge
    How to do things
    """
    memory_id: str
    agent_id: str
    skill_name: str
    procedure_steps: List[Dict[str, Any]]
    success_rate: float  # 0.0 to 1.0
    average_duration: float  # seconds
    last_used: datetime
    use_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'memory_id': self.memory_id,
            'agent_id': self.agent_id,
            'skill_name': self.skill_name,
            'procedure_steps': self.procedure_steps,
            'success_rate': self.success_rate,
            'average_duration': self.average_duration,
            'last_used': self.last_used.isoformat(),
            'use_count': self.use_count
        }


class MemoryBackend(ABC):
    """Abstract base class for memory storage backends"""
    
    @abstractmethod
    def store_episodic(self, memory: EpisodicMemory):
        pass
    
    @abstractmethod
    def store_semantic(self, memory: SemanticMemory):
        pass
    
    @abstractmethod
    def store_procedural(self, memory: ProceduralMemory):
        pass
    
    @abstractmethod
    def retrieve_episodic(self, agent_id: str, filters: Dict[str, Any]) -> List[EpisodicMemory]:
        pass
    
    @abstractmethod
    def retrieve_semantic(self, agent_id: str, filters: Dict[str, Any]) -> List[SemanticMemory]:
        pass
    
    @abstractmethod
    def retrieve_procedural(self, agent_id: str, filters: Dict[str, Any]) -> List[ProceduralMemory]:
        pass


class SQLiteMemoryBackend(MemoryBackend):
    """SQLite implementation of memory storage (easily swappable)"""
    
    def __init__(self, db_path: str = "data/agent_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_db()
        logger.info(f"SQLite memory backend initialized at {db_path}")
    
    def _initialize_db(self):
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Episodic memory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS episodic_memory (
                memory_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                context TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                importance REAL NOT NULL,
                emotional_valence REAL NOT NULL,
                outcome TEXT,
                learned_from INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_episodic ON episodic_memory(agent_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON episodic_memory(event_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp_ep ON episodic_memory(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_importance ON episodic_memory(importance)')
        
        # Semantic memory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS semantic_memory (
                memory_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                category TEXT NOT NULL,
                concept TEXT NOT NULL,
                knowledge TEXT NOT NULL,
                confidence REAL NOT NULL,
                source TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                last_accessed TEXT NOT NULL,
                access_count INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_semantic ON semantic_memory(agent_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON semantic_memory(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_concept ON semantic_memory(concept)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_confidence ON semantic_memory(confidence)')
        
        # Procedural memory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS procedural_memory (
                memory_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                skill_name TEXT NOT NULL,
                procedure_steps TEXT NOT NULL,
                success_rate REAL NOT NULL,
                average_duration REAL NOT NULL,
                last_used TEXT NOT NULL,
                use_count INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_procedural ON procedural_memory(agent_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_skill ON procedural_memory(skill_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_success_rate ON procedural_memory(success_rate)')
        
        # Memory consolidation table (for long-term storage)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_consolidation (
                consolidation_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                consolidated_at TEXT NOT NULL,
                memory_ids TEXT NOT NULL,
                summary TEXT NOT NULL,
                importance REAL NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Memory database schema initialized")
    
    def store_episodic(self, memory: EpisodicMemory):
        """Store episodic memory"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO episodic_memory
                (memory_id, agent_id, event_type, description, context, timestamp,
                 importance, emotional_valence, outcome, learned_from)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                memory.memory_id,
                memory.agent_id,
                memory.event_type,
                memory.description,
                json.dumps(memory.context),
                memory.timestamp.isoformat(),
                memory.importance,
                memory.emotional_valence,
                memory.outcome,
                int(memory.learned_from)
            ))
            
            conn.commit()
            conn.close()
            logger.debug(f"Stored episodic memory {memory.memory_id} for agent {memory.agent_id}")
        except Exception as e:
            logger.error(f"Failed to store episodic memory: {e}")
    
    def store_semantic(self, memory: SemanticMemory):
        """Store semantic memory"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO semantic_memory
                (memory_id, agent_id, category, concept, knowledge, confidence,
                 source, timestamp, last_accessed, access_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                memory.memory_id,
                memory.agent_id,
                memory.category,
                memory.concept,
                json.dumps(memory.knowledge),
                memory.confidence,
                memory.source,
                memory.timestamp.isoformat(),
                memory.last_accessed.isoformat(),
                memory.access_count
            ))
            
            conn.commit()
            conn.close()
            logger.debug(f"Stored semantic memory {memory.memory_id} for agent {memory.agent_id}")
        except Exception as e:
            logger.error(f"Failed to store semantic memory: {e}")
    
    def store_procedural(self, memory: ProceduralMemory):
        """Store procedural memory"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO procedural_memory
                (memory_id, agent_id, skill_name, procedure_steps, success_rate,
                 average_duration, last_used, use_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                memory.memory_id,
                memory.agent_id,
                memory.skill_name,
                json.dumps(memory.procedure_steps),
                memory.success_rate,
                memory.average_duration,
                memory.last_used.isoformat(),
                memory.use_count
            ))
            
            conn.commit()
            conn.close()
            logger.debug(f"Stored procedural memory {memory.memory_id} for agent {memory.agent_id}")
        except Exception as e:
            logger.error(f"Failed to store procedural memory: {e}")
    
    def retrieve_episodic(self, agent_id: str, filters: Dict[str, Any] = None) -> List[EpisodicMemory]:
        """Retrieve episodic memories with optional filters"""
        filters = filters or {}
        memories = []
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            query = "SELECT * FROM episodic_memory WHERE agent_id = ?"
            params = [agent_id]
            
            if 'event_type' in filters:
                query += " AND event_type = ?"
                params.append(filters['event_type'])
            
            if 'min_importance' in filters:
                query += " AND importance >= ?"
                params.append(filters['min_importance'])
            
            if 'since' in filters:
                query += " AND timestamp >= ?"
                params.append(filters['since'])
            
            query += " ORDER BY timestamp DESC"
            
            if 'limit' in filters:
                query += " LIMIT ?"
                params.append(filters['limit'])
            
            cursor.execute(query, params)
            
            for row in cursor.fetchall():
                memory = EpisodicMemory(
                    memory_id=row[0],
                    agent_id=row[1],
                    event_type=row[2],
                    description=row[3],
                    context=json.loads(row[4]),
                    timestamp=datetime.fromisoformat(row[5]),
                    importance=row[6],
                    emotional_valence=row[7],
                    outcome=row[8],
                    learned_from=bool(row[9])
                )
                memories.append(memory)
            
            conn.close()
        except Exception as e:
            logger.error(f"Failed to retrieve episodic memories: {e}")
        
        return memories
    
    def retrieve_semantic(self, agent_id: str, filters: Dict[str, Any] = None) -> List[SemanticMemory]:
        """Retrieve semantic memories with optional filters"""
        filters = filters or {}
        memories = []
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            query = "SELECT * FROM semantic_memory WHERE agent_id = ?"
            params = [agent_id]
            
            if 'category' in filters:
                query += " AND category = ?"
                params.append(filters['category'])
            
            if 'concept' in filters:
                query += " AND concept LIKE ?"
                params.append(f"%{filters['concept']}%")
            
            if 'min_confidence' in filters:
                query += " AND confidence >= ?"
                params.append(filters['min_confidence'])
            
            query += " ORDER BY confidence DESC, access_count DESC"
            
            if 'limit' in filters:
                query += " LIMIT ?"
                params.append(filters['limit'])
            
            cursor.execute(query, params)
            
            for row in cursor.fetchall():
                memory = SemanticMemory(
                    memory_id=row[0],
                    agent_id=row[1],
                    category=row[2],
                    concept=row[3],
                    knowledge=json.loads(row[4]),
                    confidence=row[5],
                    source=row[6],
                    timestamp=datetime.fromisoformat(row[7]),
                    last_accessed=datetime.fromisoformat(row[8]),
                    access_count=row[9]
                )
                memories.append(memory)
                
                # Update access count
                cursor.execute('''
                    UPDATE semantic_memory 
                    SET access_count = access_count + 1, last_accessed = ?
                    WHERE memory_id = ?
                ''', (datetime.now().isoformat(), memory.memory_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to retrieve semantic memories: {e}")
        
        return memories
    
    def retrieve_procedural(self, agent_id: str, filters: Dict[str, Any] = None) -> List[ProceduralMemory]:
        """Retrieve procedural memories with optional filters"""
        filters = filters or {}
        memories = []
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            query = "SELECT * FROM procedural_memory WHERE agent_id = ?"
            params = [agent_id]
            
            if 'skill_name' in filters:
                query += " AND skill_name LIKE ?"
                params.append(f"%{filters['skill_name']}%")
            
            if 'min_success_rate' in filters:
                query += " AND success_rate >= ?"
                params.append(filters['min_success_rate'])
            
            query += " ORDER BY success_rate DESC, use_count DESC"
            
            if 'limit' in filters:
                query += " LIMIT ?"
                params.append(filters['limit'])
            
            cursor.execute(query, params)
            
            for row in cursor.fetchall():
                memory = ProceduralMemory(
                    memory_id=row[0],
                    agent_id=row[1],
                    skill_name=row[2],
                    procedure_steps=json.loads(row[3]),
                    success_rate=row[4],
                    average_duration=row[5],
                    last_used=datetime.fromisoformat(row[6]),
                    use_count=row[7]
                )
                memories.append(memory)
            
            conn.close()
        except Exception as e:
            logger.error(f"Failed to retrieve procedural memories: {e}")
        
        return memories


class AgentMemorySystem:
    """
    Main memory system interface for agents
    Supports episodic, semantic, and procedural memory
    Backend is swappable (SQLite, Vector DB, etc.)
    """
    
    def __init__(self, backend: MemoryBackend = None):
        self.backend = backend or SQLiteMemoryBackend()
        logger.info("Agent Memory System initialized")
    
    def remember_experience(self, agent_id: str, event_type: str, description: str,
                           context: Dict[str, Any], importance: float = 0.5,
                           emotional_valence: float = 0.0, outcome: str = None) -> str:
        """
        Store an episodic memory (experience/event)
        Returns memory_id
        """
        memory_id = self._generate_memory_id(agent_id, event_type, description)
        
        memory = EpisodicMemory(
            memory_id=memory_id,
            agent_id=agent_id,
            event_type=event_type,
            description=description,
            context=context,
            timestamp=datetime.now(),
            importance=importance,
            emotional_valence=emotional_valence,
            outcome=outcome
        )
        
        self.backend.store_episodic(memory)
        logger.info(f"Agent {agent_id} remembered experience: {event_type}")
        return memory_id
    
    def learn_knowledge(self, agent_id: str, category: str, concept: str,
                       knowledge: Dict[str, Any], confidence: float = 0.8,
                       source: str = "experience") -> str:
        """
        Store semantic memory (knowledge/fact)
        Returns memory_id
        """
        memory_id = self._generate_memory_id(agent_id, category, concept)
        
        memory = SemanticMemory(
            memory_id=memory_id,
            agent_id=agent_id,
            category=category,
            concept=concept,
            knowledge=knowledge,
            confidence=confidence,
            source=source,
            timestamp=datetime.now(),
            last_accessed=datetime.now()
        )
        
        self.backend.store_semantic(memory)
        logger.info(f"Agent {agent_id} learned knowledge: {concept}")
        return memory_id
    
    def learn_skill(self, agent_id: str, skill_name: str, procedure_steps: List[Dict[str, Any]],
                   success_rate: float = 1.0, average_duration: float = 0.0) -> str:
        """
        Store procedural memory (skill/how-to)
        Returns memory_id
        """
        memory_id = self._generate_memory_id(agent_id, "skill", skill_name)
        
        memory = ProceduralMemory(
            memory_id=memory_id,
            agent_id=agent_id,
            skill_name=skill_name,
            procedure_steps=procedure_steps,
            success_rate=success_rate,
            average_duration=average_duration,
            last_used=datetime.now()
        )
        
        self.backend.store_procedural(memory)
        logger.info(f"Agent {agent_id} learned skill: {skill_name}")
        return memory_id
    
    def recall_experiences(self, agent_id: str, event_type: str = None,
                          min_importance: float = None, limit: int = 10) -> List[EpisodicMemory]:
        """Recall episodic memories (experiences)"""
        filters = {'limit': limit}
        if event_type:
            filters['event_type'] = event_type
        if min_importance:
            filters['min_importance'] = min_importance
        
        return self.backend.retrieve_episodic(agent_id, filters)
    
    def recall_knowledge(self, agent_id: str, category: str = None,
                        concept: str = None, limit: int = 10) -> List[SemanticMemory]:
        """Recall semantic memories (knowledge)"""
        filters = {'limit': limit}
        if category:
            filters['category'] = category
        if concept:
            filters['concept'] = concept
        
        return self.backend.retrieve_semantic(agent_id, filters)
    
    def recall_skills(self, agent_id: str, skill_name: str = None,
                     min_success_rate: float = None, limit: int = 10) -> List[ProceduralMemory]:
        """Recall procedural memories (skills)"""
        filters = {'limit': limit}
        if skill_name:
            filters['skill_name'] = skill_name
        if min_success_rate:
            filters['min_success_rate'] = min_success_rate
        
        return self.backend.retrieve_procedural(agent_id, filters)
    
    def _generate_memory_id(self, agent_id: str, *components) -> str:
        """Generate unique memory ID"""
        content = f"{agent_id}_{datetime.now().isoformat()}_{'_'.join(map(str, components))}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def consolidate_memories(self, agent_id: str, days_old: int = 7):
        """
        Consolidate old memories to save space
        Combines similar memories into summaries
        """
        # This would be implemented based on specific consolidation strategy
        logger.info(f"Memory consolidation triggered for agent {agent_id}")


# Global memory system instance
agent_memory_system = AgentMemorySystem()
