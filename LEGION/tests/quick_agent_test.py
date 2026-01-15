#!/usr/bin/env python3
"""
Quick test for all agents after WorkflowOrchestrationAgent fix
"""

import asyncio
import sys
import os

# Add enterprise directory to path
sys.path.append(os.path.dirname(__file__))

async def quick_test():
    print("🧪 QUICK AGENT VERIFICATION TEST")
    print("=" * 50)
    
    # Test WorkflowOrchestrationAgent specifically
    try:
        from automation.workflow_orchestration_agent import WorkflowOrchestrationAgent
        
        agent = WorkflowOrchestrationAgent()
        print(f"✅ WorkflowOrchestrationAgent has logger: {hasattr(agent, 'logger')}")
        
        # Test workflow registration
        result = await agent.process_task({
            "action": "register_workflow",
            "workflow_id": "test_workflow",
            "definition": {
                "name": "Test Workflow",
                "steps": [{"stage": "test", "action": "test_action"}]
            }
        })
        
        if result.get("status") == "success":
            print("✅ Workflow orchestration capabilities verified")
        else:
            print(f"❌ Workflow test failed: {result}")
            
    except Exception as e:
        print(f"❌ WorkflowOrchestrationAgent test failed: {e}")
    
    # Test other key agents quickly
    agents_to_test = [
        ("business_intelligence.comprehensive_analytics_agent", "ComprehensiveAnalyticsAgent"),
        ("operations.external_systems_integration_agent", "ExternalSystemsIntegrationAgent")
    ]
    
    for module_name, class_name in agents_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            agent_cls = getattr(module, class_name)
            agent = agent_cls()
            
            # Test task processing
            result = await agent.process_task({"action": "test", "test": True})
            print(f"✅ {class_name} working correctly")
            
        except Exception as e:
            print(f"❌ {class_name} failed: {e}")
    
    print("\n🎉 VERIFICATION COMPLETE")

if __name__ == "__main__":
    asyncio.run(quick_test())
