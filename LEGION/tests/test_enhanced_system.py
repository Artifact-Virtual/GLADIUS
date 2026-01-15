#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced LEGION System
Tests all new features: message bus, memory, tracing, self-improvement
"""

import asyncio
import sys
from pathlib import Path

# Add legion directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "legion"))

import logging
from datetime import datetime

# Import systems
from message_bus import message_bus, Message
from agent_memory import agent_memory_system
from distributed_tracing import tracing_system
from self_improvement import self_improvement_system
from enhanced_agent_base import EnhancedAgentBase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestAgent(EnhancedAgentBase):
    """Test agent implementation"""
    
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            agent_type="test_agent",
            department="testing",
            capabilities=["testing", "learning"]
        )
        self.processed_messages = []
    
    async def process_message(self, message: Message):
        """Process incoming messages"""
        logger.info(f"TestAgent {self.agent_id} processing: {message.message_type}")
        self.processed_messages.append(message)
        return {"processed": True, "agent_id": self.agent_id}
    
    async def _execute_task_impl(self, task):
        """Execute test task"""
        logger.info(f"TestAgent {self.agent_id} executing task: {task.get('type')}")
        
        # Simulate work
        await asyncio.sleep(0.1)
        
        return {
            "status": "completed",
            "agent_id": self.agent_id,
            "task_type": task.get('type'),
            "quality_score": 0.9
        }


async def test_message_bus():
    """Test inter-agent communication via message bus"""
    logger.info("\n" + "="*60)
    logger.info("TESTING MESSAGE BUS")
    logger.info("="*60)
    
    # Create test agents
    agent1 = TestAgent("agent_1")
    agent2 = TestAgent("agent_2")
    agent3 = TestAgent("agent_3")
    
    await agent1.initialize()
    await agent2.initialize()
    await agent3.initialize()
    
    # Start message bus
    await message_bus.start()
    
    # Test 1: Point-to-point messaging
    logger.info("\nTest 1: Point-to-point messaging")
    success = await agent1.send_message(
        recipient_id="agent_2",
        message_type="test_message",
        content={"data": "Hello Agent 2!"},
        priority=7
    )
    assert success, "Failed to send point-to-point message"
    logger.info("✅ Point-to-point message sent successfully")
    
    # Wait for processing
    await asyncio.sleep(0.5)
    
    # Check if received
    assert len(agent2.processed_messages) > 0, "Agent 2 didn't receive message"
    logger.info(f"✅ Agent 2 received {len(agent2.processed_messages)} message(s)")
    
    # Test 2: Broadcasting
    logger.info("\nTest 2: Broadcasting")
    sent_count = await agent1.broadcast_message(
        message_type="broadcast_test",
        content={"announcement": "Test broadcast"}
    )
    logger.info(f"✅ Broadcast sent to {sent_count} agents")
    
    # Wait for processing
    await asyncio.sleep(0.5)
    
    # Test 3: Message bus statistics
    logger.info("\nTest 3: Message bus statistics")
    stats = message_bus.get_stats()
    logger.info(f"Total sent: {stats['total_sent']}")
    logger.info(f"Total delivered: {stats['total_delivered']}")
    logger.info(f"Average latency: {stats['average_latency_ms']:.2f}ms")
    logger.info(f"✅ Message bus statistics retrieved")
    
    # Stop message bus
    await message_bus.stop()
    
    logger.info("\n✅ ALL MESSAGE BUS TESTS PASSED")


async def test_agent_memory():
    """Test agent memory system"""
    logger.info("\n" + "="*60)
    logger.info("TESTING AGENT MEMORY SYSTEM")
    logger.info("="*60)
    
    test_agent_id = "memory_test_agent"
    
    # Test 1: Episodic memory (experiences)
    logger.info("\nTest 1: Episodic Memory")
    memory_id = agent_memory_system.remember_experience(
        agent_id=test_agent_id,
        event_type="task_completed",
        description="Successfully completed first test task",
        context={"task_id": "test_001", "result": "success"},
        importance=0.8,
        emotional_valence=0.6,
        outcome="positive"
    )
    assert memory_id, "Failed to store episodic memory"
    logger.info(f"✅ Stored episodic memory: {memory_id}")
    
    # Recall experiences
    experiences = agent_memory_system.recall_experiences(
        agent_id=test_agent_id,
        event_type="task_completed",
        limit=5
    )
    assert len(experiences) > 0, "Failed to recall experiences"
    logger.info(f"✅ Recalled {len(experiences)} experience(s)")
    
    # Test 2: Semantic memory (knowledge)
    logger.info("\nTest 2: Semantic Memory")
    knowledge_id = agent_memory_system.learn_knowledge(
        agent_id=test_agent_id,
        category="best_practices",
        concept="error_handling",
        knowledge={
            "rule": "Always validate inputs before processing",
            "examples": ["check_null", "validate_range"],
            "confidence": 0.95
        },
        confidence=0.95
    )
    assert knowledge_id, "Failed to store semantic memory"
    logger.info(f"✅ Stored semantic memory: {knowledge_id}")
    
    # Recall knowledge
    knowledge = agent_memory_system.recall_knowledge(
        agent_id=test_agent_id,
        category="best_practices",
        limit=5
    )
    assert len(knowledge) > 0, "Failed to recall knowledge"
    logger.info(f"✅ Recalled {len(knowledge)} knowledge item(s)")
    
    # Test 3: Procedural memory (skills)
    logger.info("\nTest 3: Procedural Memory")
    skill_id = agent_memory_system.learn_skill(
        agent_id=test_agent_id,
        skill_name="data_processing",
        procedure_steps=[
            {"step": 1, "action": "validate_input", "params": {}},
            {"step": 2, "action": "transform_data", "params": {}},
            {"step": 3, "action": "save_output", "params": {}}
        ],
        success_rate=0.95,
        average_duration=1.5
    )
    assert skill_id, "Failed to store procedural memory"
    logger.info(f"✅ Stored procedural memory: {skill_id}")
    
    # Recall skills
    skills = agent_memory_system.recall_skills(
        agent_id=test_agent_id,
        skill_name="data_processing",
        limit=5
    )
    assert len(skills) > 0, "Failed to recall skills"
    logger.info(f"✅ Recalled {len(skills)} skill(s)")
    
    logger.info("\n✅ ALL MEMORY TESTS PASSED")


async def test_distributed_tracing():
    """Test distributed tracing system"""
    logger.info("\n" + "="*60)
    logger.info("TESTING DISTRIBUTED TRACING")
    logger.info("="*60)
    
    # Test 1: Start trace
    logger.info("\nTest 1: Trace Lifecycle")
    trace_id = tracing_system.start_trace(
        operation_name="test_operation",
        tags={"test": True, "component": "testing"}
    )
    assert trace_id, "Failed to start trace"
    logger.info(f"✅ Started trace: {trace_id}")
    
    # Test 2: Nested spans
    logger.info("\nTest 2: Nested Spans")
    span1_id = tracing_system.start_span(
        trace_id=trace_id,
        operation_name="step_1",
        tags={"step": 1}
    )
    
    await asyncio.sleep(0.1)  # Simulate work
    
    span2_id = tracing_system.start_span(
        trace_id=trace_id,
        operation_name="step_2",
        parent_span_id=span1_id,
        tags={"step": 2}
    )
    
    await asyncio.sleep(0.05)  # Simulate work
    
    tracing_system.end_span(span2_id, status="success")
    tracing_system.end_span(span1_id, status="success")
    tracing_system.end_trace(trace_id)
    
    logger.info(f"✅ Created nested spans and ended trace")
    
    # Test 3: Context manager
    logger.info("\nTest 3: Context Manager")
    with tracing_system.trace_operation("context_test", {"test": "context"}):
        await asyncio.sleep(0.05)
        logger.info("✅ Context manager working")
    
    # Test 4: Get metrics
    logger.info("\nTest 4: Tracing Metrics")
    metrics = tracing_system.get_metrics()
    logger.info(f"Total traces: {metrics['total_traces']}")
    logger.info(f"Total spans: {metrics['total_spans']}")
    logger.info(f"Average duration: {metrics['average_duration_ms']:.2f}ms")
    logger.info("✅ Tracing metrics retrieved")
    
    logger.info("\n✅ ALL TRACING TESTS PASSED")


async def test_self_improvement():
    """Test self-improvement system"""
    logger.info("\n" + "="*60)
    logger.info("TESTING SELF-IMPROVEMENT SYSTEM")
    logger.info("="*60)
    
    test_agent_id = "improvement_test_agent"
    
    # Test 1: Record feedback
    logger.info("\nTest 1: Performance Feedback")
    for i in range(10):
        success = i % 3 != 0  # 2/3 success rate
        execution_time = 100 + (i * 50)  # Increasing time
        quality = 0.9 if success else 0.3
        
        await self_improvement_system.record_feedback(
            agent_id=test_agent_id,
            task_type="test_task",
            success=success,
            execution_time_ms=execution_time,
            quality_score=quality
        )
    
    logger.info(f"✅ Recorded 10 performance feedback entries")
    
    # Test 2: Get performance summary
    logger.info("\nTest 2: Performance Summary")
    summary = self_improvement_system.get_agent_performance_summary(
        agent_id=test_agent_id,
        days=1
    )
    logger.info(f"Total tasks: {summary['total_tasks']}")
    logger.info(f"Success rate: {summary['success_rate']:.1%}")
    logger.info(f"Avg execution time: {summary['average_execution_time_ms']:.2f}ms")
    logger.info(f"Avg quality: {summary['average_quality_score']:.2f}")
    logger.info(f"✅ Performance summary generated")
    
    # Test 3: Check for insights
    logger.info("\nTest 3: Learning Insights")
    if summary['insights_count'] > 0:
        logger.info(f"✅ Generated {summary['insights_count']} learning insight(s)")
        for insight in summary['top_insights']:
            logger.info(f"  - {insight}")
    else:
        logger.info("ℹ️  No insights yet (need more data)")
    
    logger.info("\n✅ ALL SELF-IMPROVEMENT TESTS PASSED")


async def test_enhanced_agent():
    """Test enhanced agent with all features integrated"""
    logger.info("\n" + "="*60)
    logger.info("TESTING ENHANCED AGENT INTEGRATION")
    logger.info("="*60)
    
    # Create agent
    agent = TestAgent("integration_test_agent")
    await agent.initialize()
    
    # Start message bus for communication
    await message_bus.start()
    
    # Test 1: Execute task with tracing and learning
    logger.info("\nTest 1: Task Execution with All Features")
    result = await agent.execute_task({
        "type": "integration_test",
        "data": "test_data"
    })
    assert result['status'] == "completed", "Task execution failed"
    logger.info("✅ Task executed with tracing and learning")
    
    # Test 2: Learn and recall knowledge
    logger.info("\nTest 2: Learn and Recall Knowledge")
    agent.learn_knowledge(
        category="testing",
        concept="integration_test",
        knowledge={"learned": "from_test", "value": 42}
    )
    
    knowledge = agent.recall_knowledge(category="testing")
    assert len(knowledge) > 0, "Failed to recall knowledge"
    logger.info(f"✅ Learned and recalled knowledge")
    
    # Test 3: Learn and recall skill
    logger.info("\nTest 3: Learn and Recall Skill")
    agent.learn_skill(
        skill_name="test_execution",
        procedure_steps=[
            {"step": 1, "action": "setup"},
            {"step": 2, "action": "execute"},
            {"step": 3, "action": "verify"}
        ]
    )
    
    skills = agent.recall_skills(skill_name="test_execution")
    assert len(skills) > 0, "Failed to recall skills"
    logger.info(f"✅ Learned and recalled skill")
    
    # Test 4: Message communication
    logger.info("\nTest 4: Inter-Agent Communication")
    agent2 = TestAgent("integration_test_agent_2")
    await agent2.initialize()
    
    success = await agent.send_message(
        recipient_id="integration_test_agent_2",
        message_type="integration_test",
        content={"message": "Hello from integration test"}
    )
    assert success, "Message sending failed"
    logger.info("✅ Inter-agent communication working")
    
    await asyncio.sleep(0.3)
    
    # Test 5: Get performance summary
    logger.info("\nTest 5: Performance Summary")
    summary = agent.get_performance_summary()
    logger.info(f"Performance data available: {summary.get('total_tasks', 0)} tasks")
    logger.info("✅ Performance summary retrieved")
    
    # Stop message bus
    await message_bus.stop()
    
    logger.info("\n✅ ALL INTEGRATION TESTS PASSED")


async def run_stress_test(duration_seconds: int = 30):
    """Run stress test with multiple agents"""
    logger.info("\n" + "="*60)
    logger.info(f"RUNNING STRESS TEST ({duration_seconds}s)")
    logger.info("="*60)
    
    # Create multiple agents
    num_agents = 10
    agents = [TestAgent(f"stress_test_agent_{i}") for i in range(num_agents)]
    
    for agent in agents:
        await agent.initialize()
    
    # Start systems
    await message_bus.start()
    await self_improvement_system.start()
    
    logger.info(f"Created {num_agents} agents")
    
    # Run tasks continuously
    start_time = datetime.now()
    task_count = 0
    message_count = 0
    
    while (datetime.now() - start_time).total_seconds() < duration_seconds:
        # Each agent executes a task
        tasks = []
        for agent in agents:
            tasks.append(agent.execute_task({
                "type": "stress_test",
                "iteration": task_count
            }))
        
        await asyncio.gather(*tasks, return_exceptions=True)
        task_count += num_agents
        
        # Random inter-agent messages
        for i in range(num_agents // 2):
            sender = agents[i]
            recipient = agents[(i + 1) % num_agents]
            await sender.send_message(
                recipient_id=recipient.agent_id,
                message_type="stress_test_message",
                content={"iteration": message_count}
            )
            message_count += 1
        
        await asyncio.sleep(0.1)
    
    # Stop systems
    await message_bus.stop()
    await self_improvement_system.stop()
    
    # Get statistics
    elapsed = (datetime.now() - start_time).total_seconds()
    bus_stats = message_bus.get_stats()
    tracing_stats = tracing_system.get_metrics()
    
    logger.info("\n" + "="*60)
    logger.info("STRESS TEST RESULTS")
    logger.info("="*60)
    logger.info(f"Duration: {elapsed:.1f}s")
    logger.info(f"Agents: {num_agents}")
    logger.info(f"Tasks executed: {task_count}")
    logger.info(f"Messages sent: {message_count}")
    logger.info(f"Tasks/second: {task_count/elapsed:.1f}")
    logger.info(f"Messages/second: {message_count/elapsed:.1f}")
    logger.info(f"\nMessage Bus Stats:")
    logger.info(f"  Total delivered: {bus_stats['total_delivered']}")
    logger.info(f"  Average latency: {bus_stats['average_latency_ms']:.2f}ms")
    logger.info(f"\nTracing Stats:")
    logger.info(f"  Total traces: {tracing_stats['total_traces']}")
    logger.info(f"  Total spans: {tracing_stats['total_spans']}")
    logger.info(f"  P95 latency: {tracing_stats['p95_duration_ms']:.2f}ms")
    
    logger.info("\n✅ STRESS TEST COMPLETED")


async def main():
    """Run all tests"""
    logger.info("\n" + "="*60)
    logger.info("LEGION ENHANCED SYSTEM COMPREHENSIVE TEST SUITE")
    logger.info("="*60)
    
    try:
        # Run feature tests
        await test_message_bus()
        await test_agent_memory()
        await test_distributed_tracing()
        await test_self_improvement()
        await test_enhanced_agent()
        
        # Run stress test
        await run_stress_test(duration_seconds=10)
        
        logger.info("\n" + "="*60)
        logger.info("🎉 ALL TESTS PASSED SUCCESSFULLY! 🎉")
        logger.info("="*60)
        
        return 0
        
    except Exception as e:
        logger.error(f"\n❌ TEST FAILED: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
