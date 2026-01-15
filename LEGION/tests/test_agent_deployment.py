#!/usr/bin/env python3
"""
Test Agent Deployment - Enterprise Legion
Simple test to verify agent deployment and imports work correctly
"""

import sys
import asyncio
from pathlib import Path

# Add enterprise directory to path
enterprise_root = Path(__file__).parent
sys.path.insert(0, str(enterprise_root))
sys.path.insert(0, str(enterprise_root / "legion"))

async def test_agent_imports():
    """Test importing and initializing agents"""
    print("🧪 Testing Agent Imports and Initialization")
    print("=" * 50)
    
    successful_imports = []
    failed_imports = []
    
    # Test automation agents
    try:
        print("Testing automation agents...")
        from automation import TaskSchedulingAgent
        agent = TaskSchedulingAgent()
        successful_imports.append("TaskSchedulingAgent")
        print("✅ TaskSchedulingAgent imported successfully")
    except Exception as e:
        failed_imports.append(f"TaskSchedulingAgent: {e}")
        print(f"❌ TaskSchedulingAgent failed: {e}")
    
    # Test finance agents  
    try:
        print("Testing finance agents...")
        from finance import FinancialAnalysisAgent
        agent = FinancialAnalysisAgent()
        successful_imports.append("FinancialAnalysisAgent")
        print("✅ FinancialAnalysisAgent imported successfully")
    except Exception as e:
        failed_imports.append(f"FinancialAnalysisAgent: {e}")
        print(f"❌ FinancialAnalysisAgent failed: {e}")
    
    # Test business intelligence agents
    try:
        print("Testing business intelligence agents...")
        from business_intelligence import MarketAnalysisAgent
        agent = MarketAnalysisAgent()
        successful_imports.append("MarketAnalysisAgent")
        print("✅ MarketAnalysisAgent imported successfully")
    except Exception as e:
        failed_imports.append(f"MarketAnalysisAgent: {e}")
        print(f"❌ MarketAnalysisAgent failed: {e}")
    
    # Test communication agents
    try:
        print("Testing communication agents...")
        from communication import ContentWritingAgent
        agent = ContentWritingAgent()
        successful_imports.append("ContentWritingAgent")
        print("✅ ContentWritingAgent imported successfully")
    except Exception as e:
        failed_imports.append(f"ContentWritingAgent: {e}")
        print(f"❌ ContentWritingAgent failed: {e}")
    
    # Test legal agents
    try:
        print("Testing legal agents...")
        from legal import ComplianceCheckerAgent
        agent = ComplianceCheckerAgent()
        successful_imports.append("ComplianceCheckerAgent")
        print("✅ ComplianceCheckerAgent imported successfully")
    except Exception as e:
        failed_imports.append(f"ComplianceCheckerAgent: {e}")
        print(f"❌ ComplianceCheckerAgent failed: {e}")
    
    # Test org structure agents
    try:
        print("Testing org structure agents...")
        from org_structure import CalendarManagementAgent
        agent = CalendarManagementAgent()
        successful_imports.append("CalendarManagementAgent")
        print("✅ CalendarManagementAgent imported successfully")
    except Exception as e:
        failed_imports.append(f"CalendarManagementAgent: {e}")
        print(f"❌ CalendarManagementAgent failed: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 IMPORT TEST RESULTS")
    print(f"✅ Successful: {len(successful_imports)}")
    print(f"❌ Failed: {len(failed_imports)}")
    
    if successful_imports:
        print(f"\n✅ Working agents: {', '.join(successful_imports)}")
    
    if failed_imports:
        print(f"\n❌ Failed agents:")
        for failure in failed_imports:
            print(f"   • {failure}")
    
    return len(successful_imports), len(failed_imports)

async def main():
    """Main test function"""
    successful, failed = await test_agent_imports()
    
    if failed == 0:
        print(f"\n🎉 ALL TESTS PASSED! {successful} agents ready for deployment.")
        return 0
    else:
        print(f"\n⚠️ {failed} agents need fixes before deployment.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
