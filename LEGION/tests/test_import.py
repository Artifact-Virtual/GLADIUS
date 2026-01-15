#!/usr/bin/env python3
"""Simple import test"""

import sys
sys.path.append('.')

try:
    from automation.task_scheduling_agent import TaskSchedulingAgent
    agent = TaskSchedulingAgent()
    print("✅ TaskSchedulingAgent works!")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
