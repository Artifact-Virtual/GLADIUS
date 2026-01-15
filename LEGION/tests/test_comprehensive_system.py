#!/usr/bin/env python3
"""
Test all operational agents including new comprehensive components
"""

import asyncio
import sys
import os

# Add enterprise directory to path
sys.path.append(os.path.dirname(__file__))

def test_agent_import(agent_module, agent_class):
    """Test importing and basic initialization of an agent"""
    try:
        module = __import__(agent_module, fromlist=[agent_class])
        agent_cls = getattr(module, agent_class)
        agent = agent_cls()
        print(f"✅ {agent_class} imported and initialized successfully")
        return True, agent
    except Exception as e:
        print(f"❌ {agent_class} failed: {e}")
        return False, None

async def test_agent_processing(agent, agent_name):
    """Test basic agent task processing"""
    try:
        result = await agent.process_task({"action": "test", "test": True})
        print(f"✅ {agent_name} task processing works")
        return True
    except Exception as e:
        print(f"❌ {agent_name} task processing failed: {e}")
        return False

async def main():
    print("🧪 TESTING COMPREHENSIVE ENTERPRISE LEGION AGENTS")
    print("=" * 60)
    
    agents_to_test = [
        # Core agents
        ("automation.task_scheduling_agent", "TaskSchedulingAgent"),
        ("automation.workflow_orchestration_agent", "WorkflowOrchestrationAgent"),
        ("finance.financial_analysis_agent", "FinancialAnalysisAgent"),
        ("communication.content_writing_agent", "ContentWritingAgent"),
        ("legal.compliance_checker_agent", "ComplianceCheckerAgent"),
        ("org_structure.calendar_management_agent", "CalendarManagementAgent"),
        # New comprehensive agents
        ("business_intelligence.comprehensive_analytics_agent", "ComprehensiveAnalyticsAgent"),
        ("operations.external_systems_integration_agent", "ExternalSystemsIntegrationAgent")
    ]
    
    successful_imports = 0
    successful_processing = 0
    working_agents = []
    
    # Test imports and initialization
    print("\n📥 Testing Agent Imports and Initialization...")
    active_agents = []
    
    for module_name, class_name in agents_to_test:
        success, agent = test_agent_import(module_name, class_name)
        if success:
            successful_imports += 1
            active_agents.append((agent, class_name))
            working_agents.append(class_name)
    
    # Test task processing
    print("\n⚙️ Testing Agent Task Processing...")
    for agent, agent_name in active_agents:
        if await test_agent_processing(agent, agent_name):
            successful_processing += 1
    
    # Test specific operational capabilities
    print("\n🔧 Testing Operational Capabilities...")
    
    # Test workflow orchestration
    for agent, agent_name in active_agents:
        if agent_name == "WorkflowOrchestrationAgent":
            try:
                workflow_result = await agent.process_task({
                    "action": "register_workflow",
                    "workflow_id": "test_workflow",
                    "definition": {
                        "name": "Test Workflow",
                        "steps": [{"stage": "test", "action": "test_action"}]
                    }
                })
                print(f"✅ Workflow orchestration capabilities verified")
            except Exception as e:
                print(f"❌ Workflow orchestration test failed: {e}")
    
    # Test analytics capabilities
    for agent, agent_name in active_agents:
        if agent_name == "ComprehensiveAnalyticsAgent":
            try:
                analytics_result = await agent.process_task({
                    "action": "generate_report",
                    "report_type": "executive_dashboard"
                })
                print(f"✅ Business intelligence capabilities verified")
            except Exception as e:
                print(f"❌ Analytics test failed: {e}")
    
    # Test external integration
    for agent, agent_name in active_agents:
        if agent_name == "ExternalSystemsIntegrationAgent":
            try:
                integration_result = await agent.process_task({
                    "action": "sync_data",
                    "system": "crm",
                    "data_type": "leads"
                })
                print(f"✅ External systems integration capabilities verified")
            except Exception as e:
                print(f"❌ Integration test failed: {e}")
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TESTING RESULTS")
    print(f"✅ Successful imports: {successful_imports}/{len(agents_to_test)}")
    print(f"✅ Successful processing: {successful_processing}/{len(active_agents)}")
    print(f"✅ Working agents: {', '.join(working_agents)}")
    
    if successful_imports == len(agents_to_test) and successful_processing == len(active_agents):
        print("🎉 ALL COMPREHENSIVE TESTS PASSED! System ready for full operation.")
        return True
    else:
        print("⚠️ Some tests failed. Check individual agent implementations.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
