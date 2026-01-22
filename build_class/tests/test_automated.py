#!/usr/bin/env python3
"""
Automated test script for build_class
Tests the system by simulating LLM responses to find all blockages and issues
"""

import os
import sys

# Set test environment
os.environ["ADAPTER_TYPE"] = "mock"
os.environ["USE_TEST_POLICY"] = "true"
os.environ["WORKSPACE_DIR"] = "./workspace"

# Mock the MockAdapter to return automated responses
class AutomatedMockAdapter:
    """Fully automated mock adapter for testing"""
    def __init__(self):
        self.call_count = 0
        
    def call(self, system, messages, tools):
        self.call_count += 1
        user_msg = messages[-1]["content"] if messages else ""
        
        print(f"\n[AUTO-MOCK #{self.call_count}]")
        print(f"System: {system[:50]}...")
        print(f"User: {user_msg[:80]}...")
        print(f"Tools: {tools}")
        
        # Simulate different agent responses based on system prompt
        if "decompose tasks" in system.lower():
            # Planner agent - return a simple plan
            plan = f"Step 1: List files in workspace\nStep 2: Create a test file\nStep 3: Read the test file"
            print(f"[AUTO-PLAN] {plan}")
            return [{"type": "text", "text": plan}]
        
        elif "execute plans" in system.lower():
            # Executor agent - return tool use blocks
            tools_to_use = [
                {
                    "type": "tool_use",
                    "name": "bash",
                    "input": {"cmd": "ls -la"}
                },
                {
                    "type": "tool_use",
                    "name": "write",
                    "input": {"path": "test.txt", "content": "Hello from nanocode test!"}
                },
                {
                    "type": "tool_use",
                    "name": "read",
                    "input": {"path": "test.txt"}
                }
            ]
            print(f"[AUTO-EXEC] Returning {len(tools_to_use)} tool calls")
            return tools_to_use
        
        elif "summarize" in system.lower():
            # Memory agent - return summary
            summary = "Successfully tested workspace operations: listed files, created test file, and read it back"
            print(f"[AUTO-SUMMARY] {summary}")
            return [{"type": "text", "text": summary}]
        
        else:
            # Generic response
            return [{"type": "text", "text": "Automated response"}]

def run_test():
    """Run automated test"""
    print("="*60)
    print("BUILD_CLASS AUTOMATED TEST")
    print("="*60)
    
    # Import build_class
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from build_class import Mesh
    
    # Create automated adapter
    adapter = AutomatedMockAdapter()
    
    # Create mesh
    print("\n[TEST] Creating mesh...")
    mesh = Mesh(adapter)
    
    # Test cases
    test_cases = [
        "List all files in the workspace",
        "Create a file called hello.txt with content 'Hello World'",
        "Read the content of hello.txt",
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST CASE {i}: {test_case}")
        print(f"{'='*60}")
        
        try:
            plan, summary, log = mesh.run(test_case)
            
            print(f"\n[RESULT {i}] SUCCESS")
            print(f"Plan: {plan[:100]}...")
            print(f"Summary: {summary[:100]}...")
            print(f"Executed {len(log)} tools")
            
        except Exception as e:
            print(f"\n[RESULT {i}] FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print(f"Total LLM calls: {adapter.call_count}")
    print("="*60)

if __name__ == "__main__":
    run_test()
