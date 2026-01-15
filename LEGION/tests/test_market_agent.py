#!/usr/bin/env python3
"""Test MarketAnalysisAgent in isolation"""

import sys
sys.path.append('.')

try:
    print("Testing direct import...")
    from business_intelligence.market_analysis_agent import MarketAnalysisAgent
    print("✅ Direct import successful")
    
    print("Testing instantiation...")
    agent = MarketAnalysisAgent()
    print("✅ MarketAnalysisAgent instantiated successfully")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
