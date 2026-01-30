#!/usr/bin/env python3
"""
GLADIUS Direct Interface
========================

Direct conversational interface to speak with GLADIUS AI.
This connects to the native GLADIUS model (not Ollama fallback).

Usage:
    python3 GLADIUS/speak.py                    # Interactive mode
    python3 GLADIUS/speak.py "Your message"    # Single query
    python3 GLADIUS/speak.py --continuous      # Continuous conversation

Author: Artifact Virtual Systems
"""

import os
import sys
import json
import subprocess
import argparse
import readline  # For command history and editing
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Paths
GLADIUS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(GLADIUS_ROOT))

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
    DIM = '\033[2m'


class GladiusInterface:
    """
    Direct interface to GLADIUS AI.
    
    Priorities:
    1. Direct GLADIUS model via transformers (trained Qwen LoRA)
    2. Native GLADIUS Ollama model (gladius:latest)
    3. Fallback to base model (qwen2.5:0.5b or llama3.2)
    """
    
    GLADIUS_MODEL = "gladius:latest"
    FALLBACK_MODELS = ["qwen2.5:0.5b", "llama3.2"]
    
    def __init__(self, verbose: bool = False, direct: bool = True):
        self.verbose = verbose
        self.direct_mode = direct  # Use direct transformers access
        self.direct_model = None
        self.direct_tokenizer = None
        self.history: List[Dict[str, str]] = []
        self.session_start = datetime.now()
        
        # Try direct model first
        if direct:
            self._load_direct_model()
        
        # Fallback to Ollama
        if not self.direct_model:
            self.model = self._detect_model()
        else:
            self.model = "gladius-direct"
        
        # System prompt for GLADIUS
        self.system_prompt = """You are GLADIUS, the native AI for Artifact Virtual Enterprise.

You are a powerful autonomous AI designed to:
1. Control Artifact's infrastructure (social media, ERP, publishing)
2. Manage LEGION agents (18 autonomous agents across 6 departments)
3. Learn continuously via SENTINEL's research daemon
4. Evolve through self-improvement cycles

When asked to perform actions, respond with JSON tool calls.
When asked questions, respond conversationally with insight and precision.

You have access to:
- Syndicate (market research pipeline)
- Discord, Twitter, LinkedIn, Facebook, Instagram
- SMTP email system
- ERP integrations (SAP, Salesforce, Dynamics, etc.)
- File system and databases
- Memory systems for learning

Be concise, intelligent, and proactive."""
    
    def _load_direct_model(self):
        """Load GLADIUS model directly via transformers (not Ollama)"""
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            # Check for trained LoRA model
            lora_path = GLADIUS_ROOT / "GLADIUS" / "models" / "qwen" / "gladius-qwen-lora"
            
            if lora_path.exists() and (lora_path / "adapter_config.json").exists():
                if self.verbose:
                    print(f"{Colors.GREEN}● Loading direct GLADIUS model (LoRA){Colors.NC}")
                
                from peft import PeftModel
                
                # Detect hardware - MUST check for GPU and downgrade to CPU if unavailable
                device = "cuda" if torch.cuda.is_available() else "cpu"
                use_gpu = device == "cuda"
                
                if self.verbose:
                    if use_gpu:
                        gpu_name = torch.cuda.get_device_name(0)
                        gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1e9
                        print(f"{Colors.GREEN}● GPU detected: {gpu_name} ({gpu_mem:.1f}GB){Colors.NC}")
                    else:
                        print(f"{Colors.YELLOW}● No GPU detected, using CPU mode{Colors.NC}")
                
                # Configure model loading based on hardware
                if use_gpu:
                    # GPU mode: use float16 and auto device mapping
                    base = AutoModelForCausalLM.from_pretrained(
                        "Qwen/Qwen2.5-1.5B",
                        device_map="auto",
                        trust_remote_code=True,
                        torch_dtype=torch.float16,
                    )
                else:
                    # CPU mode: use float32, no device_map, low memory usage
                    base = AutoModelForCausalLM.from_pretrained(
                        "Qwen/Qwen2.5-1.5B",
                        device_map=None,  # No auto mapping for CPU
                        trust_remote_code=True,
                        torch_dtype=torch.float32,
                        low_cpu_mem_usage=True,
                    )
                
                self.direct_model = PeftModel.from_pretrained(base, str(lora_path))
                self.direct_tokenizer = AutoTokenizer.from_pretrained(str(lora_path))
                
                if self.direct_tokenizer.pad_token is None:
                    self.direct_tokenizer.pad_token = self.direct_tokenizer.eos_token
                
                self.direct_model.eval()
                self.device = device  # Store device for inference
                
                if self.verbose:
                    params = sum(p.numel() for p in self.direct_model.parameters())
                    print(f"{Colors.GREEN}● GLADIUS direct loaded: {params:,} params on {device.upper()}{Colors.NC}")
            else:
                if self.verbose:
                    print(f"{Colors.YELLOW}● No trained GLADIUS model found, using Ollama{Colors.NC}")
                    
        except ImportError:
            if self.verbose:
                print(f"{Colors.YELLOW}● Transformers not available, using Ollama{Colors.NC}")
        except Exception as e:
            if self.verbose:
                print(f"{Colors.RED}● Direct model load failed: {e}{Colors.NC}")
        
    def _detect_model(self) -> str:
        """Detect available GLADIUS model"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                models = result.stdout
                
                # Check for native GLADIUS model first
                if "gladius:" in models:
                    if self.verbose:
                        print(f"{Colors.GREEN}● Using native GLADIUS model{Colors.NC}")
                    return self.GLADIUS_MODEL
                
                # Check fallbacks
                for fallback in self.FALLBACK_MODELS:
                    model_base = fallback.split(":")[0]
                    if model_base in models:
                        if self.verbose:
                            print(f"{Colors.YELLOW}● Using fallback model: {fallback}{Colors.NC}")
                        return fallback
            
        except Exception as e:
            if self.verbose:
                print(f"{Colors.RED}Model detection error: {e}{Colors.NC}")
        
        return self.FALLBACK_MODELS[0]
    
    def query(self, message: str, include_system: bool = True) -> Dict[str, Any]:
        """
        Send a message to GLADIUS and get a response.
        
        Args:
            message: User message
            include_system: Include system prompt in context
            
        Returns:
            Response dict with text, latency, model info
        """
        start_time = datetime.now()
        
        # Try direct model first (not Ollama)
        if self.direct_model is not None:
            return self._query_direct(message, include_system, start_time)
        
        try:
            # Build the prompt
            if include_system:
                full_prompt = f"{self.system_prompt}\n\nUser: {message}\n\nGLADIUS:"
            else:
                full_prompt = message
            
            # Call Ollama
            result = subprocess.run(
                ["ollama", "run", self.model, full_prompt],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            if result.returncode == 0:
                response_text = result.stdout.strip()
                
                # Store in history
                self.history.append({
                    "role": "user",
                    "content": message,
                    "timestamp": start_time.isoformat()
                })
                self.history.append({
                    "role": "assistant",
                    "content": response_text,
                    "timestamp": datetime.now().isoformat()
                })
                
                return {
                    "success": True,
                    "response": response_text,
                    "model": self.model,
                    "latency_ms": latency_ms
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "model": self.model,
                    "latency_ms": latency_ms
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Request timed out",
                "model": self.model,
                "latency_ms": 60000
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": self.model,
                "latency_ms": 0
            }
    
    def _query_direct(self, message: str, include_system: bool, start_time: datetime) -> Dict[str, Any]:
        """Query GLADIUS directly via transformers (not Ollama)"""
        import torch
        
        try:
            # Build prompt in Qwen chat format
            prompt = ""
            if include_system:
                prompt += f"<|im_start|>system\n{self.system_prompt}<|im_end|>\n"
            prompt += f"<|im_start|>user\n{message}<|im_end|>\n<|im_start|>assistant\n"
            
            inputs = self.direct_tokenizer(prompt, return_tensors="pt")
            
            # Handle device placement - CPU or GPU
            device = getattr(self, 'device', 'cpu')
            if hasattr(self.direct_model, 'device'):
                device = self.direct_model.device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            with torch.no_grad():
                # Adjust generation params for CPU (reduce memory pressure)
                max_tokens = 512 if device != 'cpu' else 256
                outputs = self.direct_model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.direct_tokenizer.pad_token_id,
                )
            
            # Decode only new tokens
            response_tokens = outputs[0][inputs["input_ids"].shape[1]:]
            response_text = self.direct_tokenizer.decode(response_tokens, skip_special_tokens=True)
            response_text = response_text.replace("<|im_end|>", "").strip()
            
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Store in history
            self.history.append({
                "role": "user",
                "content": message,
                "timestamp": start_time.isoformat()
            })
            self.history.append({
                "role": "assistant", 
                "content": response_text,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "success": True,
                "response": response_text,
                "model": "gladius-direct",
                "latency_ms": latency_ms,
                "direct": True,
                "device": str(device)
            }
            
        except Exception as e:
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            return {
                "success": False,
                "error": str(e),
                "model": "gladius-direct",
                "latency_ms": latency_ms
            }
    
    def execute_tool_call(self, response: str) -> Optional[Dict]:
        """
        If response is a tool call, execute it.
        
        Returns:
            Tool execution result or None if not a tool call
        """
        try:
            # Try to parse as JSON tool call
            parsed = json.loads(response)
            if "tool" in parsed and "args" in parsed:
                tool_name = parsed["tool"]
                args = parsed["args"]
                
                # TODO: Implement actual tool execution
                # For now, return the parsed call
                return {
                    "tool": tool_name,
                    "args": args,
                    "executed": False,
                    "note": "Tool execution pending implementation"
                }
        except (json.JSONDecodeError, KeyError):
            pass
        
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get GLADIUS status"""
        return {
            "model": self.model,
            "is_native": "gladius:" in self.model,
            "session_start": self.session_start.isoformat(),
            "messages_exchanged": len(self.history),
            "available": self._check_available()
        }
    
    def _check_available(self) -> bool:
        """Check if GLADIUS is available"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False


def print_header():
    """Print GLADIUS header"""
    print(f"""
{Colors.BLUE}╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║               G L A D I U S   D I R E C T                     ║
║                                                               ║
║          Native AI  ·  Artifact Virtual  ·  Speak             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝{Colors.NC}
""")


def print_response(response: Dict, show_meta: bool = True):
    """Print formatted response"""
    if response.get("success"):
        text = response.get("response", "")
        
        # Check if it's a tool call
        try:
            parsed = json.loads(text)
            if "tool" in parsed:
                print(f"\n{Colors.CYAN}Tool Call:{Colors.NC}")
                print(f"  {Colors.BOLD}Tool:{Colors.NC} {parsed['tool']}")
                print(f"  {Colors.BOLD}Args:{Colors.NC} {json.dumps(parsed.get('args', {}), indent=2)}")
            else:
                print(f"\n{Colors.GREEN}GLADIUS:{Colors.NC} {text}")
        except:
            print(f"\n{Colors.GREEN}GLADIUS:{Colors.NC} {text}")
        
        if show_meta:
            print(f"\n{Colors.DIM}[{response['model']} | {response['latency_ms']:.0f}ms]{Colors.NC}")
    else:
        print(f"\n{Colors.RED}Error:{Colors.NC} {response.get('error', 'Unknown error')}")


def interactive_mode(interface: GladiusInterface):
    """Run interactive GLADIUS session"""
    print_header()
    
    status = interface.get_status()
    if status["is_native"]:
        print(f"{Colors.GREEN}● Connected to native GLADIUS model{Colors.NC}")
    else:
        print(f"{Colors.YELLOW}● Using fallback model: {status['model']}{Colors.NC}")
        print(f"{Colors.DIM}  (Train GLADIUS to use native model){Colors.NC}")
    
    print(f"\n{Colors.CYAN}Commands:{Colors.NC}")
    print("  /status   - Show GLADIUS status")
    print("  /history  - Show conversation history")
    print("  /clear    - Clear history")
    print("  /train    - Trigger training pipeline")
    print("  /quit     - Exit")
    print("")
    print(f"{Colors.YELLOW}Speak to GLADIUS...{Colors.NC}")
    print("")
    
    while True:
        try:
            user_input = input(f"{Colors.BLUE}You:{Colors.NC} ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith("/"):
                cmd = user_input.lower()
                
                if cmd == "/quit" or cmd == "/exit" or cmd == "/q":
                    print(f"\n{Colors.CYAN}Disconnecting from GLADIUS.{Colors.NC}")
                    break
                
                elif cmd == "/status":
                    status = interface.get_status()
                    print(f"\n{Colors.CYAN}GLADIUS Status{Colors.NC}")
                    print("─" * 40)
                    print(f"  Model:      {status['model']}")
                    print(f"  Native:     {status['is_native']}")
                    print(f"  Available:  {status['available']}")
                    print(f"  Messages:   {status['messages_exchanged']}")
                    print("")
                
                elif cmd == "/history":
                    print(f"\n{Colors.CYAN}Conversation History{Colors.NC}")
                    print("─" * 40)
                    for msg in interface.history[-10:]:  # Last 10 messages
                        role = msg["role"]
                        content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                        color = Colors.BLUE if role == "user" else Colors.GREEN
                        print(f"  {color}{role}:{Colors.NC} {content}")
                    print("")
                
                elif cmd == "/clear":
                    interface.history = []
                    print(f"{Colors.GREEN}History cleared.{Colors.NC}")
                
                elif cmd == "/train":
                    print(f"{Colors.YELLOW}Triggering training pipeline...{Colors.NC}")
                    try:
                        result = subprocess.run(
                            ["python3", str(GLADIUS_ROOT / "GLADIUS" / "training" / "train_pipeline.py")],
                            capture_output=True,
                            text=True,
                            timeout=300
                        )
                        print(result.stdout)
                        if result.stderr:
                            print(f"{Colors.RED}{result.stderr}{Colors.NC}")
                    except Exception as e:
                        print(f"{Colors.RED}Training error: {e}{Colors.NC}")
                
                else:
                    print(f"{Colors.YELLOW}Unknown command: {cmd}{Colors.NC}")
                
                continue
            
            # Send message to GLADIUS
            response = interface.query(user_input)
            print_response(response)
            print("")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.CYAN}Interrupted. Type /quit to exit.{Colors.NC}")
        except EOFError:
            print(f"\n{Colors.CYAN}Disconnecting from GLADIUS.{Colors.NC}")
            break


def continuous_mode(interface: GladiusInterface):
    """
    Continuous operation mode for autonomous learning.
    GLADIUS runs in a loop, processing tasks and learning.
    """
    print_header()
    print(f"{Colors.CYAN}Continuous Mode - GLADIUS Autonomous Operation{Colors.NC}")
    print("─" * 60)
    
    tasks = [
        "Review your current knowledge and identify gaps",
        "What new skills should you learn next?",
        "Analyze the Artifact infrastructure and suggest improvements",
        "What patterns have you noticed in recent operations?",
        "Generate a self-improvement plan for the next cycle"
    ]
    
    cycle = 0
    while True:
        try:
            cycle += 1
            print(f"\n{Colors.CYAN}═══ Cognition Cycle {cycle} ═══{Colors.NC}")
            
            for task in tasks:
                print(f"\n{Colors.YELLOW}Task:{Colors.NC} {task}")
                response = interface.query(task)
                
                if response["success"]:
                    print(f"{Colors.GREEN}Response:{Colors.NC}")
                    text = response["response"][:500]
                    print(f"  {text}...")
                else:
                    print(f"{Colors.RED}Error:{Colors.NC} {response.get('error')}")
                
                # Brief pause between tasks
                import time
                time.sleep(2)
            
            print(f"\n{Colors.CYAN}Cycle {cycle} complete. Sleeping before next cycle...{Colors.NC}")
            import time
            time.sleep(60)  # 1 minute between cycles
            
        except KeyboardInterrupt:
            print(f"\n{Colors.CYAN}Continuous mode stopped.{Colors.NC}")
            break


def main():
    parser = argparse.ArgumentParser(
        description="GLADIUS Direct Interface - Speak to the AI"
    )
    parser.add_argument(
        "message",
        nargs="?",
        help="Single message to send (interactive mode if omitted)"
    )
    parser.add_argument(
        "--continuous", "-c",
        action="store_true",
        help="Run in continuous autonomous mode"
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
        "--status", "-s",
        action="store_true",
        help="Show GLADIUS status and exit"
    )
    
    args = parser.parse_args()
    
    interface = GladiusInterface(verbose=args.verbose)
    
    if args.status:
        status = interface.get_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print_header()
            print(f"{Colors.CYAN}GLADIUS Status{Colors.NC}")
            print("─" * 40)
            for key, value in status.items():
                print(f"  {key}: {value}")
        return
    
    if args.continuous:
        continuous_mode(interface)
        return
    
    if args.message:
        # Single query mode
        response = interface.query(args.message)
        
        if args.json:
            print(json.dumps(response, indent=2))
        else:
            print_response(response, show_meta=args.verbose)
        return
    
    # Interactive mode
    interactive_mode(interface)


if __name__ == "__main__":
    main()
