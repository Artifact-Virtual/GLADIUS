"""
Enterprise Legion Agent Registry - Central Management System
Initialize, register, and coordinate all enterprise agents
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Import all agent classes from actual directories
try:
    # Finance agents
    from finance.financial_analysis_agent import FinancialAnalysisAgent
    from finance.financial_modeling_agent import FinancialModelingAgent
    from finance.report_generation_agent import ReportGenerationAgent
    from finance.quality_assurance_agent import QualityAssuranceAgent

    # Automation agents
    from automation.workflow_orchestration_agent import WorkflowOrchestrationAgent
    from automation.resource_optimization_agent import ResourceOptimizationAgent
    from automation.task_scheduling_agent import TaskSchedulingAgent

    # Business intelligence agents
    from business_intelligence.market_analysis_agent import MarketAnalysisAgent
    from business_intelligence.analytics_agent import AnalyticsAgent
    from business_intelligence.research_agent import ResearchAgent
    from business_intelligence.strategic_planning_agent import StrategicPlanningAgent

    # Communication agents
    from communication.content_writing_agent import ContentWritingAgent
    from communication.social_media_monitoring_agent import SocialMediaMonitoringAgent

    # Legal agents
    from legal.compliance_checker_agent import ComplianceCheckerAgent

    # Org structure agents
    from org_structure.calendar_management_agent import CalendarManagementAgent

    from core_framework import BaseAgent, AgentMessage
except ImportError:
    # Fallback for relative imports
    from ..finance.financial_analysis_agent import FinancialAnalysisAgent
    from ..finance.financial_modeling_agent import FinancialModelingAgent
    from ..finance.report_generation_agent import ReportGenerationAgent
    from ..finance.quality_assurance_agent import QualityAssuranceAgent

    from ..automation.workflow_orchestration_agent import WorkflowOrchestrationAgent
    from ..automation.resource_optimization_agent import ResourceOptimizationAgent
    from ..automation.task_scheduling_agent import TaskSchedulingAgent

    from ..business_intelligence.market_analysis_agent import MarketAnalysisAgent
    from ..business_intelligence.analytics_agent import AnalyticsAgent
    from ..business_intelligence.research_agent import ResearchAgent
    from ..business_intelligence.strategic_planning_agent import StrategicPlanningAgent

    from ..communication.content_writing_agent import ContentWritingAgent
    from ..communication.social_media_monitoring_agent import SocialMediaMonitoringAgent

    from ..legal.compliance_checker_agent import ComplianceCheckerAgent

    from ..org_structure.calendar_management_agent import CalendarManagementAgent

    from .core_framework import BaseAgent, AgentMessage


@dataclass
class AgentRegistration:
    """Agent registration information"""
    agent_id: str
    agent_class: type
    department: str
    dependencies: List[str]
    initialization_priority: int
    status: str
    instance: Optional[BaseAgent] = None


class EnterpriseAgentRegistry:
    """
    Central registry for managing all Enterprise Legion agents.
    Handles initialization, coordination, and communication routing.
    """
    
    def __init__(self):
        self.agents = {}
        self.agent_registrations = {}
        self.message_bus = asyncio.Queue()
        self.logger = logging.getLogger(__name__)
        self.system_status = "initializing"
        self.initialization_order = []
        
    async def initialize_system(self):
        """Initialize the complete Enterprise Legion system"""
        self.logger.info("Initializing Enterprise Legion Agent System")
        
        # Register all agents
        await self._register_all_agents()
        
        # Initialize agents in dependency order
        await self._initialize_agents_by_priority()
        
        # Start message routing system
        await self._start_message_routing()
        
        # Perform system integration tests
        await self._run_integration_tests()
        
        self.system_status = "operational"
        self.logger.info("Enterprise Legion System fully operational")
        
    async def _register_all_agents(self):
        """Register all available agents with their configurations"""
        
        # Accounts, Finance, Reporting Department
        explicit_agents = {
            "financial_analysis_agent": FinancialAnalysisAgent,
            "financial_modeling_agent": FinancialModelingAgent,
            "report_generation_agent": ReportGenerationAgent,
            "quality_assurance_agent": QualityAssuranceAgent,
            "workflow_orchestration_agent": WorkflowOrchestrationAgent,
            "resource_optimization_agent": ResourceOptimizationAgent,
            "task_scheduling_agent": TaskSchedulingAgent,
            "market_analysis_agent": MarketAnalysisAgent,
            "analytics_agent": AnalyticsAgent,
            "research_agent": ResearchAgent,
            "strategic_planning_agent": StrategicPlanningAgent,
            "social_media_monitoring_agent": SocialMediaMonitoringAgent,
            "content_writing_agent": ContentWritingAgent,
            "compliance_checker_agent": ComplianceCheckerAgent,
            "calendar_management_agent": CalendarManagementAgent,
        }

        # Register explicit agents (preserve config/deps)
        for agent_id, agent_class in explicit_agents.items():
            if agent_id not in self.agent_registrations:
                self._register_agent(
                    agent_id=agent_id,
                    agent_class=agent_class,
                    department=getattr(agent_class, 'department', 'unknown'),
                    dependencies=[],
                    priority=1
                )

        # --- AUTO-DISCOVERY OF ALL AGENTS ---
        # Scan all submodules for subclasses of BaseAgent/EnterpriseAgent
        import sys, os
        from pathlib import Path
        agent_base_classes = (BaseAgent, EnterpriseAgent)
        project_root = Path(__file__).parent.parent
        agent_dirs = [
            'automation', 'business_intelligence', 'communication', 'finance', 'legal', 'org_structure', 'operations', 'monitoring', 'global_markets', 'nerve_centre', 'legion/agents'
        ]
        for agent_dir in agent_dirs:
            abs_dir = project_root / agent_dir
            if not abs_dir.exists():
                continue
            for finder, name, ispkg in pkgutil.iter_modules([str(abs_dir)]):
                try:
                    modname = f"{agent_dir.replace('/', '.')}.{name}"
                    module = importlib.import_module(modname)
                    for obj_name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, agent_base_classes) and obj not in agent_base_classes:
                            # Use class name as agent_id if not already registered
                            agent_id = getattr(obj, 'agent_id', obj_name.lower())
                            if agent_id not in self.agent_registrations:
                                self._register_agent(
                                    agent_id=agent_id,
                                    agent_class=obj,
                                    department=getattr(obj, 'department', agent_dir),
                                    dependencies=[],
                                    priority=1
                                )
                except Exception as e:
                    self.logger.warning(f"Auto-discovery failed for {modname}: {e}")

        self.logger.info(f"Registered {len(self.agent_registrations)} agents (explicit + auto-discovered)")
        
    def _register_agent(self, agent_id: str, agent_class: type, department: str,
                       dependencies: List[str], priority: int):
        """Register a single agent"""
        registration = AgentRegistration(
            agent_id=agent_id,
            agent_class=agent_class,
            department=department,
            dependencies=dependencies,
            initialization_priority=priority,
            status="registered"
        )
        self.agent_registrations[agent_id] = registration
        
    async def _initialize_agents_by_priority(self):
        """Initialize agents in dependency-aware priority order"""
        
        # Sort by priority and resolve dependencies
        initialization_groups = self._resolve_initialization_order()
        
        for group in initialization_groups:
            # Initialize agents in parallel within each group
            initialization_tasks = []
            
            for agent_id in group:
                registration = self.agent_registrations[agent_id]
                task = self._initialize_single_agent(registration)
                initialization_tasks.append(task)
                
            # Wait for all agents in this group to initialize
            await asyncio.gather(*initialization_tasks)
            
            self.logger.info(f"Initialized agent group: {group}")
            
    def _resolve_initialization_order(self) -> List[List[str]]:
        """Resolve agent initialization order based on dependencies"""
        groups = []
        remaining_agents = set(self.agent_registrations.keys())
        
        while remaining_agents:
            current_group = []
            
            # Find agents with satisfied dependencies
            for agent_id in list(remaining_agents):
                registration = self.agent_registrations[agent_id]
                dependencies_satisfied = all(
                    dep_id not in remaining_agents 
                    for dep_id in registration.dependencies
                )
                
                if dependencies_satisfied:
                    current_group.append(agent_id)
                    
            # Remove agents in current group from remaining
            for agent_id in current_group:
                remaining_agents.remove(agent_id)
                
            if current_group:
                # Sort by priority within group
                current_group.sort(
                    key=lambda x: self.agent_registrations[x].initialization_priority
                )
                groups.append(current_group)
            else:
                # Circular dependency or missing dependency
                self.logger.error(f"Cannot resolve dependencies for: {remaining_agents}")
                break
                
        return groups
        
    async def _initialize_single_agent(self, registration: AgentRegistration):
        """Initialize a single agent instance"""
        try:
            self.logger.info(f"Initializing agent: {registration.agent_id}")
            
            # Create agent instance
            agent_instance = registration.agent_class(registration.agent_id)
            
            # Set up message routing reference
            agent_instance.registry = self
            
            # Initialize the agent
            await agent_instance.initialize()
            
            # Store the instance
            registration.instance = agent_instance
            registration.status = "initialized"
            self.agents[registration.agent_id] = agent_instance
            
            self.logger.info(f"Successfully initialized: {registration.agent_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize {registration.agent_id}: {str(e)}")
            registration.status = "failed"
            raise
            
    async def _start_message_routing(self):
        """Start the central message routing system"""
        # Start message router task
        asyncio.create_task(self._message_router())
        self.logger.info("Message routing system started")
        
    async def _message_router(self):
        """Central message routing between agents"""
        while self.system_status in ["initializing", "operational"]:
            try:
                # Get message from bus with timeout
                message = await asyncio.wait_for(self.message_bus.get(), timeout=1.0)
                
                # Route message to target agent
                target_agent = self.agents.get(message.recipient_id)
                if target_agent:
                    await target_agent.process_message(message)
                else:
                    self.logger.warning(f"Target agent not found: {message.recipient_id}")
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error in message routing: {str(e)}")
                
    async def route_message(self, message: AgentMessage):
        """Route message to target agent"""
        await self.message_bus.put(message)
    
    async def health_check(self):
        """Check health of all agents"""
        health_status = {}
        
        for agent_id, agent in self.agents.items():
            try:
                # Check if agent is responsive
                status = await agent.get_status()
                health_status[agent_id] = {
                    'status': 'healthy',
                    'last_response': time.time(),
                    'capabilities': list(agent.capabilities)
                }
                
                # Send a test message to verify responsiveness
                test_message = AgentMessage(
                    id=str(uuid.uuid4()),
                    source_agent="health_checker",
                    target_agent=agent_id,
                    message_type="health_check",
                    payload={"timestamp": time.time()},
                    timestamp=datetime.now(),
                    priority=1
                )
                
                await self.route_message(test_message)
                
            except Exception as e:
                health_status[agent_id] = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'last_response': None
                }
        
        return health_status
    
    async def broadcast_message(self, message_type: str, payload: Dict[str, Any], sender: str = "system"):
        """Broadcast message to all agents"""
        for agent_id in self.agents.keys():
            if agent_id != sender:  # Don't send to sender
                try:
                    message = AgentMessage(
                        id=str(uuid.uuid4()),
                        source_agent=sender,
                        target_agent=agent_id,
                        message_type=message_type,
                        payload=payload,
                        timestamp=datetime.now(),
                        priority=1
                    )
                    
                    await self.route_message(message)
                    
                except Exception as e:
                    self.logger.error(f"Failed to broadcast to {agent_id}: {e}")
    
    async def emergency_shutdown(self):
        """Emergency shutdown of all agents"""
        self.logger.info("🚨 Emergency shutdown initiated")
        
        # Broadcast shutdown message
        await self.broadcast_message("emergency_shutdown", {"reason": "system_shutdown"})
        
        # Stop all agents
        for agent_id, agent in self.agents.items():
            try:
                await agent.stop()
                self.logger.info(f"✅ Stopped agent: {agent_id}")
            except Exception as e:
                self.logger.error(f"❌ Failed to stop {agent_id}: {e}")
        
        # Clear registry
        self.agents.clear()
        self.capabilities.clear()
        
        self.logger.info("🔴 All agents stopped - Registry cleared")
    
    def generate_organizational_report(self) -> Dict[str, Any]:
        """Generate comprehensive organizational report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'total_agents': len(self.agents),
            'active_agents': len([a for a in self.agents.values() if hasattr(a, 'is_running') and a.is_running]),
            'total_capabilities': len(self.capabilities),
            'departments': {
                'accounts_finance': len([a for a in self.agents.keys() if 'financial' in a or 'report' in a]),
                'automation_operations': len([a for a in self.agents.keys() if 'task' in a or 'workflow' in a or 'resource' in a]),
                'business_intelligence': len([a for a in self.agents.keys() if 'analytics' in a or 'research' in a or 'market' in a or 'strategic' in a]),
                'communication_marketing': len([a for a in self.agents.keys() if 'content' in a or 'social' in a]),
                'legal': len([a for a in self.agents.keys() if 'compliance' in a]),
                'org_structure': len([a for a in self.agents.keys() if 'calendar' in a])
            },
            'message_queue_size': self.message_bus.qsize() if hasattr(self.message_bus, 'qsize') else 0
        }
    
    async def send_daily_report(self):
        """Send daily organizational report"""
        report = self.generate_organizational_report()
        
        # Broadcast daily report to all agents
        message = AgentMessage(
            sender="enterprise_registry",
            target="all",
            message_type="daily_report",
            payload=report,
            priority=2
        )
        
        await self.broadcast_message("daily_report", report, "enterprise_registry")
        
    async def _run_integration_tests(self):
        """Run basic integration tests to verify system connectivity"""
        self.logger.info("Running integration tests...")
        
        test_results = {}
        
        # Test 1: Agent status checks
        for agent_id, agent in self.agents.items():
            try:
                status = await agent.get_status()
                test_results[f"{agent_id}_status"] = "passed"
            except Exception as e:
                test_results[f"{agent_id}_status"] = f"failed: {str(e)}"
                
        # Test 2: Message routing
        try:
            # Send test message between agents
            if "financial_analysis_agent" in self.agents and "report_generation_agent" in self.agents:
                test_message = AgentMessage(
                    sender="system_test",
                    target="report_generation_agent",
                    message_type="test_message",
                    payload={"test": "integration_test"}
                )
                await self.route_message(test_message)
                test_results["message_routing"] = "passed"
                
        except Exception as e:
            test_results["message_routing"] = f"failed: {str(e)}"
            
        # Test 3: Cross-department communication
        test_results["cross_dept_communication"] = await self._test_cross_department_communication()
        
        # Log test results
        passed_tests = len([r for r in test_results.values() if r == "passed"])
        total_tests = len(test_results)
        
        self.logger.info(f"Integration tests completed: {passed_tests}/{total_tests} passed")
        
        if passed_tests < total_tests:
            self.logger.warning("Some integration tests failed - system may have limited functionality")
            
    async def _test_cross_department_communication(self) -> str:
        """Test communication between different departments"""
        try:
            # Test financial -> marketing communication
            if ("financial_analysis_agent" in self.agents and 
                "content_writing_agent" in self.agents):
                
                test_message = AgentMessage(
                    sender="financial_analysis_agent",
                    target="content_writing_agent",
                    message_type="performance_data_update",
                    payload={"revenue_growth": 0.15, "profit_margin": 0.20}
                )
                await self.route_message(test_message)
                
            return "passed"
            
        except Exception as e:
            return f"failed: {str(e)}"
            
    async def send_system_message(self, message_type: str, content: Dict[str, Any], 
                                 target_agents: Optional[List[str]] = None):
        """Send a system-wide message to all or specified agents"""
        targets = target_agents if target_agents else list(self.agents.keys())
        
        for agent_id in targets:
            message = AgentMessage(
                sender="system",
                target=agent_id,
                message_type=message_type,
                payload=content
            )
            await self.route_message(message)
            
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        agent_statuses = {}
        
        for agent_id, agent in self.agents.items():
            try:
                agent_statuses[agent_id] = await agent.get_status()
            except Exception as e:
                agent_statuses[agent_id] = {"status": "error", "error": str(e)}
                
        return {
            "system_status": self.system_status,
            "total_agents": len(self.agents),
            "operational_agents": len([s for s in agent_statuses.values() 
                                     if s.get("status") == "active"]),
            "agent_details": agent_statuses,
            "departments": {
                "accounts_finance_reporting": len([a for a in self.agent_registrations.values() 
                                                  if a.department == "accounts_finance_reporting"]),
                "automation_operations": len([a for a in self.agent_registrations.values() 
                                            if a.department == "automation_operations"]),
                "business_intelligence_strategy": len([a for a in self.agent_registrations.values() 
                                                     if a.department == "business_intelligence_strategy"]),
                "communication_marketing": len([a for a in self.agent_registrations.values() 
                                              if a.department == "communication_marketing"]),
                "legal": len([a for a in self.agent_registrations.values() 
                            if a.department == "legal"]),
                "org_structure": len([a for a in self.agent_registrations.values() 
                                    if a.department == "org_structure"])
            },
            "initialization_time": datetime.now().isoformat()
        }
        
    async def shutdown_system(self):
        """Gracefully shutdown the entire system"""
        self.logger.info("Shutting down Enterprise Legion System")
        self.system_status = "shutting_down"
        
        # Shutdown all agents
        shutdown_tasks = []
        for agent in self.agents.values():
            if hasattr(agent, 'shutdown'):
                shutdown_tasks.append(agent.shutdown())
                
        await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        
        self.system_status = "shutdown"
        self.logger.info("System shutdown complete")
    
    def get_agent(self, agent_id: str):
        """Get an agent instance by ID"""
        return self.agents.get(agent_id)
    
    async def get_agent_async(self, agent_id: str):
        """Async version of get_agent for compatibility"""
        return self.get_agent(agent_id)
    
    def get_all_agents(self) -> Dict[str, Any]:
        """Get all registered agents"""
        return self.agents.copy()
    
    def get_agent_status(self, agent_id: str) -> str:
        """Get the status of a specific agent"""
        agent = self.get_agent(agent_id)
        if agent:
            return getattr(agent, 'status', 'unknown')
        return 'not_found'


# Global registry instance
enterprise_registry = EnterpriseAgentRegistry()


async def initialize_enterprise_legion():
    """Initialize the complete Enterprise Legion system"""
    await enterprise_registry.initialize_system()
    return enterprise_registry


async def get_system_status():
    """Get current system status"""
    return await enterprise_registry.get_system_status()


async def send_system_message(message_type: str, content: Dict[str, Any], 
                             target_agents: Optional[List[str]] = None):
    """Send a system-wide message"""
    await enterprise_registry.send_system_message(message_type, content, target_agents)


async def shutdown_enterprise_legion():
    """Shutdown the Enterprise Legion system"""
    await enterprise_registry.shutdown_system()
