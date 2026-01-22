#!/usr/bin/env python3
"""
Comprehensive monitoring and testing script for build_class
Tests all loops, sections, and identifies blockages
"""

import os
import sys
import json

# Set test environment
os.environ["ADAPTER_TYPE"] = "mock"
os.environ["USE_TEST_POLICY"] = "true"
os.environ["WORKSPACE_DIR"] = "./workspace_monitor"

class MonitoringAdapter:
    """Adapter with detailed monitoring"""
    def __init__(self):
        self.calls = []
        
    def call(self, system, messages, tools):
        call_info = {
            "call_num": len(self.calls) + 1,
            "system": system,
            "messages": messages,
            "tools": tools,
            "agent_type": self._identify_agent(system)
        }
        self.calls.append(call_info)
        
        print(f"\n{'='*60}")
        print(f"LLM CALL #{call_info['call_num']} - {call_info['agent_type']}")
        print(f"{'='*60}")
        print(f"System Prompt: {system[:80]}...")
        print(f"User Message: {messages[-1]['content'][:80] if messages else 'None'}...")
        print(f"Tools Available: {len(tools)} tools" if tools else "No tools")
        
        # Return appropriate response based on agent type
        if call_info['agent_type'] == 'PLANNER':
            return self._planner_response(messages)
        elif call_info['agent_type'] == 'EXECUTOR':
            return self._executor_response(messages, tools)
        elif call_info['agent_type'] == 'MEMORY':
            return self._memory_response(messages)
        else:
            return [{"type": "text", "text": "Unknown agent"}]
    
    def _identify_agent(self, system):
        if "decompose" in system.lower():
            return "PLANNER"
        elif "execute" in system.lower():
            return "EXECUTOR"
        elif "summarize" in system.lower():
            return "MEMORY"
        return "UNKNOWN"
    
    def _planner_response(self, messages):
        user_msg = messages[-1]['content'] if messages else ""
        
        # Generate different plans based on the goal
        if "error" in user_msg.lower():
            plan = "1. Trigger an error condition\n2. Handle the error"
        elif "file" in user_msg.lower():
            plan = "1. List current files\n2. Create or modify the file\n3. Verify the operation"
        elif "bash" in user_msg.lower() or "command" in user_msg.lower():
            plan = "1. Execute the bash command\n2. Capture the output\n3. Process results"
        else:
            plan = "1. Analyze the request\n2. Execute appropriate tools\n3. Report results"
        
        print(f"[PLANNER OUTPUT] Generated plan with {len(plan.split(chr(10)))} steps")
        return [{"type": "text", "text": plan}]
    
    def _executor_response(self, messages, tools):
        user_msg = messages[-1]['content'] if messages else ""
        
        # Parse the plan from the message
        tool_calls = []
        
        if "list" in user_msg.lower() or "ls" in user_msg.lower():
            tool_calls.append({
                "type": "tool_use",
                "name": "bash",
                "input": {"cmd": "ls -la"}
            })
        
        if "create" in user_msg.lower() or "write" in user_msg.lower():
            tool_calls.append({
                "type": "tool_use",
                "name": "write",
                "input": {"path": "monitor_test.txt", "content": "Monitoring test content"}
            })
        
        if "read" in user_msg.lower():
            tool_calls.append({
                "type": "tool_use",
                "name": "read",
                "input": {"path": "monitor_test.txt"}
            })
        
        if "pwd" in user_msg.lower():
            tool_calls.append({
                "type": "tool_use",
                "name": "bash",
                "input": {"cmd": "pwd"}
            })
        
        # If no specific tools matched, do a default action
        if not tool_calls:
            tool_calls.append({
                "type": "tool_use",
                "name": "bash",
                "input": {"cmd": "echo 'Default monitoring action'"}
            })
        
        print(f"[EXECUTOR OUTPUT] Returning {len(tool_calls)} tool calls")
        for i, tc in enumerate(tool_calls, 1):
            print(f"  Tool {i}: {tc['name']}({tc['input']})")
        
        return tool_calls
    
    def _memory_response(self, messages):
        user_msg = messages[-1]['content'] if messages else ""
        
        # Parse log to create meaningful summary
        try:
            data = json.loads(user_msg)
            goal = data.get('goal', 'Unknown goal')
            log = data.get('log', [])
            
            summary = f"Completed '{goal}': executed {len(log)} tools successfully"
            
        except:
            summary = "Execution completed"
        
        print(f"[MEMORY OUTPUT] {summary}")
        return [{"type": "text", "text": summary}]
    
    def report(self):
        """Generate monitoring report"""
        print(f"\n{'='*60}")
        print("MONITORING REPORT")
        print(f"{'='*60}")
        print(f"Total LLM calls: {len(self.calls)}")
        
        by_type = {}
        for call in self.calls:
            agent_type = call['agent_type']
            by_type[agent_type] = by_type.get(agent_type, 0) + 1
        
        print("\nCalls by agent type:")
        for agent_type, count in by_type.items():
            print(f"  {agent_type}: {count}")
        
        print(f"\nCall sequence:")
        for call in self.calls:
            print(f"  #{call['call_num']}: {call['agent_type']}")

def test_section(name, goal, adapter, mesh):
    """Test a specific section"""
    print(f"\n\n{'#'*60}")
    print(f"# SECTION: {name}")
    print(f"{'#'*60}")
    
    try:
        plan, summary, log = mesh.run(goal)
        print(f"\n[SECTION RESULT] SUCCESS")
        print(f"  Plan steps: {len(plan.split(chr(10)))}")
        print(f"  Tools executed: {len(log)}")
        print(f"  Summary: {summary[:60]}...")
        return True
    except Exception as e:
        print(f"\n[SECTION RESULT] FAILED")
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("BUILD_CLASS COMPREHENSIVE MONITORING TEST")
    print("="*60)
    
    # Import build_class
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from build_class import Mesh
    
    # Create monitoring adapter
    adapter = MonitoringAdapter()
    
    # Create mesh
    print("\n[INIT] Creating mesh with monitoring...")
    mesh = Mesh(adapter)
    
    # Test sections
    sections = [
        ("Basic Bash Command", "Execute pwd command to show current directory"),
        ("File Write Operation", "Create a file called output.txt with test content"),
        ("File Read Operation", "Read the contents of output.txt"),
        ("Combined Operations", "List all files, then create status.log"),
        ("Error Handling", "Try to read a non-existent file gracefully"),
    ]
    
    results = []
    for name, goal in sections:
        success = test_section(name, goal, adapter, mesh)
        results.append((name, success))
    
    # Generate report
    adapter.report()
    
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} - {name}")
    
    passed = sum(1 for _, s in results if s)
    print(f"\nPassed: {passed}/{len(results)}")
    
    # Check workspace
    print(f"\n{'='*60}")
    print("WORKSPACE CHECK")
    print(f"{'='*60}")
    workspace = os.environ.get("WORKSPACE_DIR", "./workspace_monitor")
    if os.path.exists(workspace):
        files = os.listdir(workspace)
        print(f"Files created: {len(files)}")
        for f in files:
            path = os.path.join(workspace, f)
            size = os.path.getsize(path)
            print(f"  - {f} ({size} bytes)")
    else:
        print("Workspace not created!")
    
    print(f"\n{'='*60}")
    print("MONITORING COMPLETE")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
