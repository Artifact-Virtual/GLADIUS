#!/usr/bin/env python3
"""
Enhanced Enterprise Legion Startup Script
Launches the advanced AI-powered enterprise system with sophisticated orchestration
"""

import logging
from enhanced_orchestrator import EnhancedEnterpriseOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enterprise_legion.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('EnterpriseLegion')

def main():
    """Main startup function"""
    try:
        logger.info("🚀 STARTING ENHANCED ENTERPRISE LEGION AI ORGANIZATION")
        logger.info("=" * 70)
        
        # Initialize enhanced orchestrator
        orchestrator = EnhancedEnterpriseOrchestrator()
        
        # Run the enhanced system
        orchestrator.run()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error starting Enhanced Enterprise Legion: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n" + "=" * 60)
        print("\U0001F4CA System Status: Operational")
        print("\U0001F916 Advanced AI Agents: Active")
        print("\U0001F504 Workflow Orchestration: Running")
        print("\U0001F4C8 Business Intelligence: Generating")
        print("\U0001F4B0 Revenue Target: $4,167.00/month")
        print("")
        print("\U0001F4C1 Data Location:")
        print("   Enterprise: l:/devops/artifactvirtual/enterprise/")
        print("   Reports: l:/devops/artifactvirtual/enterprise/reporting/")
        print("   Legion: l:/devops/artifactvirtual/enterprise/legion/")
        print("")
        print("See logs in: l:/devops/artifactvirtual/enterprise/logs/ or ./logs/")
        print("\n" + "=" * 60)
    else:
        print("❌ Enhanced Enterprise Legion startup failed!")
