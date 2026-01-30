#!/usr/bin/env python3
"""
GLADIUS Interactive Mode
========================

Direct interface to interact with GLADIUS AI.

Usage:
    python3 GLADIUS/interactive.py           # Start interactive session
    python3 GLADIUS/interactive.py --query "What tools do you have?"
    python3 GLADIUS/interactive.py --status  # Show system status
    python3 GLADIUS/interactive.py --execute # Execute tool calls (not just route)

Author: Artifact Virtual Systems
"""

import sys
import os
import json
import argparse
import readline  # For command history
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add paths
GLADIUS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(GLADIUS_ROOT))
sys.path.insert(0, str(GLADIUS_ROOT / "GLADIUS"))

# Terminal colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    NC = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Print GLADIUS header."""
    print(f"""
{Colors.BLUE}╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║            G L A D I U S   I N T E R A C T I V E              ║
║                                                               ║
║         Native AI  ·  Artifact Virtual  ·  Enterprise         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝{Colors.NC}
""")

def get_system_status() -> Dict[str, Any]:
    """Get GLADIUS system status."""
    status = {
        "timestamp": datetime.now().isoformat(),
        "gladius": {
            "router": "unknown",
            "model": "unknown",
            "training": "unknown"
        },
        "sentinel": {
            "watchdog": "unknown",
            "learning": "unknown"
        },
        "legion": {
            "orchestrator": "unknown",
            "agents": 0
        }
    }
    
    # Check router
    try:
        from GLADIUS.router.pattern_router import NativeToolRouter
        router = NativeToolRouter()
        stats = router.stats()
        status["gladius"]["router"] = "operational"
        status["gladius"]["model"] = "pattern" if router.use_pattern else "ollama"
        status["gladius"]["total_calls"] = stats.get("total_calls", 0)
    except Exception as e:
        status["gladius"]["router"] = f"error: {e}"
    
    # Check training
    training_harness = GLADIUS_ROOT / "GLADIUS" / "training" / "harness.py"
    status["gladius"]["training"] = "available" if training_harness.exists() else "not found"
    
    # Check SENTINEL
    sentinel_pid = GLADIUS_ROOT / "SENTINEL" / "sentinel.pid"
    if sentinel_pid.exists():
        try:
            pid = int(sentinel_pid.read_text().strip())
            os.kill(pid, 0)  # Check if process exists
            status["sentinel"]["watchdog"] = f"running (PID: {pid})"
        except:
            status["sentinel"]["watchdog"] = "stale PID"
    else:
        status["sentinel"]["watchdog"] = "not running"
    
    # Check learning daemon
    import subprocess
    result = subprocess.run(["pgrep", "-f", "learning_daemon.py"], capture_output=True)
    status["sentinel"]["learning"] = "running" if result.returncode == 0 else "not running"
    
    # Check LEGION
    result = subprocess.run(["pgrep", "-f", "continuous_operation.py"], capture_output=True)
    status["legion"]["orchestrator"] = "running" if result.returncode == 0 else "not running"
    
    # Count LEGION agents
    legion_config = GLADIUS_ROOT / "LEGION" / "legion" / "legion_config.json"
    if legion_config.exists():
        try:
            config = json.loads(legion_config.read_text())
            departments = config.get("departments", {})
            status["legion"]["agents"] = sum(3 for d in departments.values() if d.get("active", False))
        except:
            pass
    
    return status

def print_status():
    """Print formatted system status."""
    status = get_system_status()
    
    print(f"\n{Colors.CYAN}System Status{Colors.NC}")
    print("─" * 60)
    print(f"  {Colors.BOLD}Timestamp:{Colors.NC} {status['timestamp']}")
    
    print(f"\n{Colors.BLUE}GLADIUS (Native AI){Colors.NC}")
    print("─" * 60)
    router_status = status["gladius"]["router"]
    router_color = Colors.GREEN if "operational" in router_status else Colors.RED
    print(f"  {router_color}●{Colors.NC} Router:    {router_status}")
    print(f"  {Colors.GREEN}●{Colors.NC} Model:     {status['gladius']['model']}")
    print(f"  {Colors.GREEN}●{Colors.NC} Training:  {status['gladius']['training']}")
    
    print(f"\n{Colors.BLUE}SENTINEL (Guardian){Colors.NC}")
    print("─" * 60)
    wd_status = status["sentinel"]["watchdog"]
    wd_color = Colors.GREEN if "running" in wd_status else Colors.YELLOW
    print(f"  {wd_color}●{Colors.NC} Watchdog:  {wd_status}")
    ld_status = status["sentinel"]["learning"]
    ld_color = Colors.GREEN if "running" in ld_status else Colors.YELLOW
    print(f"  {ld_color}●{Colors.NC} Learning:  {ld_status}")
    
    print(f"\n{Colors.BLUE}LEGION (Enterprise){Colors.NC}")
    print("─" * 60)
    orch_status = status["legion"]["orchestrator"]
    orch_color = Colors.GREEN if "running" in orch_status else Colors.YELLOW
    print(f"  {orch_color}●{Colors.NC} Orchestrator: {orch_status}")
    print(f"  {Colors.GREEN}●{Colors.NC} Agents:       {status['legion']['agents']} active")
    
    print("")

def query_gladius(query: str, verbose: bool = False) -> Dict[str, Any]:
    """
    Query GLADIUS and get a response.
    
    Currently routes to tools via pattern router.
    Future: Full conversational AI with native GGUF model.
    """
    try:
        from GLADIUS.router.pattern_router import NativeToolRouter
        router = NativeToolRouter()
        result = router.route(query)
        
        response = {
            "query": query,
            "tool": result.tool_name,
            "arguments": result.arguments,
            "confidence": result.confidence,
            "latency_ms": result.latency_ms,
            "source": result.source,
            "success": result.success,
            "error": result.error
        }
        
        if verbose:
            response["raw_response"] = result.raw_response
        
        return response
        
    except Exception as e:
        return {
            "query": query,
            "error": str(e),
            "success": False
        }


def execute_tool(tool_name: str, arguments: Dict[str, Any], original_query: str = "") -> Dict[str, Any]:
    """
    Execute a routed tool and return results.
    
    Supports:
    - build: BUILD_CLASS autonomous coding kernel
    - build_workspace: List build workspace files
    - build_memory: Get build history
    """
    try:
        if tool_name == "build":
            from GLADIUS.tools.build_class_tool import tool_build
            goal = arguments.get("goal", "")
            # If goal looks like just a filename, use the original query instead
            if goal and (goal.endswith('.py') or goal.endswith('.js') or len(goal.split()) < 3):
                goal = original_query if original_query else goal
            return tool_build(goal)
        
        elif tool_name == "build_workspace":
            from GLADIUS.tools.build_class_tool import tool_build_workspace
            return tool_build_workspace()
        
        elif tool_name == "build_memory":
            from GLADIUS.tools.build_class_tool import tool_build_memory
            limit = arguments.get("limit", 5)
            return tool_build_memory(limit)
        
        elif tool_name == "build_read":
            from GLADIUS.tools.build_class_tool import tool_build_read
            path = arguments.get("path", "")
            return tool_build_read(path)
        
        else:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' execution not implemented yet",
                "tool": tool_name,
                "arguments": arguments
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "tool": tool_name
        }


def interactive_loop(execute_mode: bool = False):
    """Run interactive GLADIUS session."""
    print_header()
    
    print(f"{Colors.CYAN}Commands:{Colors.NC}")
    print("  /status    - Show system status")
    print("  /stats     - Show routing statistics")
    print("  /help      - Show help")
    print("  /quit      - Exit")
    print("")
    print(f"{Colors.YELLOW}Type your query to interact with GLADIUS...{Colors.NC}")
    print("")
    
    # Initialize router
    try:
        from GLADIUS.router.pattern_router import NativeToolRouter
        router = NativeToolRouter()
        print(f"{Colors.GREEN}● Router initialized{Colors.NC}")
        stats = router.stats()
        print(f"  Mode: {stats.get('model_path', 'pattern/ollama')}")
        print("")
    except Exception as e:
        print(f"{Colors.RED}● Router error: {e}{Colors.NC}")
        router = None
    
    while True:
        try:
            # Prompt
            user_input = input(f"{Colors.BLUE}GLADIUS>{Colors.NC} ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith("/"):
                cmd = user_input.lower()
                
                if cmd == "/quit" or cmd == "/exit" or cmd == "/q":
                    print(f"\n{Colors.CYAN}Exiting GLADIUS interactive mode.{Colors.NC}")
                    break
                
                elif cmd == "/status":
                    print_status()
                
                elif cmd == "/stats":
                    if router:
                        stats = router.stats()
                        print(f"\n{Colors.CYAN}Routing Statistics{Colors.NC}")
                        print("─" * 40)
                        print(f"  Pattern calls:  {stats['pattern_calls']}")
                        print(f"  Ollama calls:   {stats['ollama_calls']}")
                        print(f"  Fallback calls: {stats['fallback_calls']}")
                        print(f"  Total calls:    {stats['total_calls']}")
                        print(f"  Errors:         {stats['errors']}")
                        print(f"  Avg latency:    {stats['avg_latency_ms']:.2f}ms")
                        print("")
                    else:
                        print(f"{Colors.RED}Router not available{Colors.NC}")
                
                elif cmd == "/help":
                    print(f"""
{Colors.CYAN}GLADIUS Interactive Help{Colors.NC}
─────────────────────────────────────────

{Colors.BOLD}Commands:{Colors.NC}
  /status    - Show system status
  /stats     - Show routing statistics
  /help      - Show this help
  /quit      - Exit interactive mode

{Colors.BOLD}Query Examples:{Colors.NC}
  search for gold price analysis
  read file config.json
  list directory ./docs
  remember key: value
  recall my notes about trading
  get context for market analysis

{Colors.BOLD}The system will:{Colors.NC}
  1. Parse your query
  2. Route to the appropriate tool
  3. Show the routing decision

{Colors.BOLD}Future Features:{Colors.NC}
  - Full conversational AI (native GGUF model)
  - Direct tool execution
  - Memory persistence
  - Context awareness
""")
                
                else:
                    print(f"{Colors.YELLOW}Unknown command: {cmd}{Colors.NC}")
                    print("Type /help for available commands")
                
                continue
            
            # Route query
            if router:
                result = router.route(user_input)
                
                # Format response
                if result.success:
                    print(f"\n{Colors.GREEN}● Tool:{Colors.NC} {result.tool_name}")
                    print(f"  {Colors.CYAN}Args:{Colors.NC} {json.dumps(result.arguments, indent=2)}")
                    print(f"  {Colors.CYAN}Confidence:{Colors.NC} {result.confidence:.0%}")
                    print(f"  {Colors.CYAN}Latency:{Colors.NC} {result.latency_ms:.2f}ms")
                    print(f"  {Colors.CYAN}Source:{Colors.NC} {result.source}")
                    
                    # Execute tool if in execute mode
                    if execute_mode and result.tool_name:
                        print(f"\n{Colors.YELLOW}Executing tool...{Colors.NC}")
                        exec_result = execute_tool(result.tool_name, result.arguments, user_input)
                        
                        if exec_result.get("success"):
                            print(f"{Colors.GREEN}● Execution successful{Colors.NC}")
                            # Print relevant results
                            if "plan" in exec_result:
                                print(f"\n{Colors.CYAN}Plan:{Colors.NC}")
                                print(exec_result["plan"][:500])
                            if "summary" in exec_result:
                                print(f"\n{Colors.CYAN}Summary:{Colors.NC}")
                                print(exec_result["summary"])
                            if "log" in exec_result:
                                print(f"\n{Colors.CYAN}Execution Log:{Colors.NC}")
                                for entry in exec_result["log"][:5]:
                                    print(f"  - {entry}")
                            if "files" in exec_result:
                                print(f"\n{Colors.CYAN}Workspace Files:{Colors.NC}")
                                for f in exec_result["files"][:10]:
                                    print(f"  - {f.get('path', f)}")
                            if "memory" in exec_result:
                                print(f"\n{Colors.CYAN}Build Memory ({exec_result.get('count', 0)} entries):{Colors.NC}")
                                for m in exec_result["memory"][:5]:
                                    print(f"  - {m.get('goal', m)[:60]}...")
                        else:
                            print(f"{Colors.RED}● Execution failed:{Colors.NC} {exec_result.get('error', 'Unknown error')}")
                else:
                    print(f"\n{Colors.RED}● Error:{Colors.NC} {result.error}")
                
                print("")
            else:
                print(f"{Colors.RED}Router not available{Colors.NC}")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.CYAN}Interrupted. Type /quit to exit.{Colors.NC}")
        except EOFError:
            print(f"\n{Colors.CYAN}Exiting GLADIUS interactive mode.{Colors.NC}")
            break

def main():
    parser = argparse.ArgumentParser(
        description="GLADIUS Interactive Mode - Direct AI interaction"
    )
    parser.add_argument(
        "--query", "-q",
        help="Single query mode (non-interactive)"
    )
    parser.add_argument(
        "--status", "-s",
        action="store_true",
        help="Show system status and exit"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output in JSON format"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--execute", "-x",
        action="store_true",
        help="Execute tool calls (not just route)"
    )
    
    args = parser.parse_args()
    
    if args.status:
        if args.json:
            status = get_system_status()
            print(json.dumps(status, indent=2))
        else:
            print_header()
            print_status()
        return
    
    if args.query:
        result = query_gladius(args.query, verbose=args.verbose)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_header()
            if result.get("success"):
                print(f"{Colors.GREEN}● Tool:{Colors.NC} {result['tool']}")
                print(f"  {Colors.CYAN}Args:{Colors.NC} {json.dumps(result['arguments'], indent=2)}")
                print(f"  {Colors.CYAN}Confidence:{Colors.NC} {result['confidence']:.0%}")
                print(f"  {Colors.CYAN}Latency:{Colors.NC} {result['latency_ms']:.2f}ms")
                
                # Execute if requested
                if args.execute and result.get('tool'):
                    print(f"\n{Colors.YELLOW}Executing tool...{Colors.NC}")
                    exec_result = execute_tool(result['tool'], result['arguments'], args.query)
                    
                    if args.json:
                        print(json.dumps(exec_result, indent=2))
                    else:
                        if exec_result.get("success"):
                            print(f"{Colors.GREEN}● Execution successful{Colors.NC}")
                            if "plan" in exec_result:
                                print(f"\n{Colors.CYAN}Plan:{Colors.NC}\n{exec_result['plan'][:1000]}")
                            if "summary" in exec_result:
                                print(f"\n{Colors.CYAN}Summary:{Colors.NC}\n{exec_result['summary']}")
                            if "workspace" in exec_result:
                                print(f"\n{Colors.CYAN}Workspace:{Colors.NC} {exec_result['workspace']}")
                        else:
                            print(f"{Colors.RED}● Execution failed:{Colors.NC} {exec_result.get('error')}")
            else:
                print(f"{Colors.RED}● Error:{Colors.NC} {result.get('error')}")
        return
    
    # Interactive mode
    interactive_loop(execute_mode=args.execute)

if __name__ == "__main__":
    main()
