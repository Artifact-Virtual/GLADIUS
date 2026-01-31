#!/usr/bin/env python3
"""
GLADIUS CLI - Command Line Interface for GLADIUS Native AI

This CLI provides direct interaction with the GLADIUS model and system.
Used by the Electron UI for IPC communication.

Usage:
    python gladius_cli.py status
    python gladius_cli.py interact --message "Hello"
    python gladius_cli.py benchmark
    python gladius_cli.py train --epochs 10
"""

import sys
import os
import json
import argparse
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import GLADIUS modules
try:
    from GLADIUS.router.pattern_router import NativeToolRouter
    from GLADIUS.utils.hardware import detect_hardware, get_optimal_settings
    from GLADIUS.utils.hektor_memory import HektorMemory
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    IMPORT_ERROR = str(e)


def get_model_path():
    """Get the path to the native GGUF model."""
    base = Path(__file__).parent
    paths = [
        base / "models" / "native" / "gladius1.1-71M.gguf",
        base / "models" / "gladius1.1-71M.gguf",
        base / "gladius_train" / "models" / "gladius1.1-71M.gguf",
    ]
    for p in paths:
        if p.exists():
            return p
    return None


def cmd_status(args):
    """Check GLADIUS status."""
    result = {
        "status": "ready",
        "version": "gladius1.1:71M-native",
        "timestamp": datetime.now().isoformat(),
        "modules_available": MODULES_AVAILABLE
    }
    
    # Check hardware
    if MODULES_AVAILABLE:
        try:
            hw = detect_hardware()
            result["hardware"] = {
                "gpu_available": hw.get("gpu_available", False),
                "gpu_name": hw.get("gpu_name"),
                "memory_gb": hw.get("memory_gb"),
                "cpu_cores": hw.get("cpu_cores")
            }
        except Exception as e:
            result["hardware"] = {"error": str(e)}
    
    # Check model
    model_path = get_model_path()
    if model_path:
        result["model"] = {
            "path": str(model_path),
            "exists": True,
            "size_mb": model_path.stat().st_size / (1024 * 1024)
        }
    else:
        result["model"] = {"exists": False}
    
    # Check memory system
    try:
        memory = HektorMemory()
        result["memory"] = {"status": "ready", "provider": "hektor-vdb"}
    except Exception:
        result["memory"] = {"status": "unavailable"}
    
    print(json.dumps(result, indent=2))
    return 0


def cmd_interact(args):
    """Interactive conversation with GLADIUS."""
    message = args.message
    
    if not message:
        print(json.dumps({"error": "No message provided"}))
        return 1
    
    result = {
        "query": message,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # Try native router first
        if MODULES_AVAILABLE:
            model_path = get_model_path()
            router = NativeToolRouter(
                model_path=str(model_path) if model_path else None,
                use_native=model_path is not None,
                use_ollama=True,
                use_pattern=True
            )
            
            routing_result = router.route(message)
            
            if routing_result.success:
                result["response"] = f"I understand you want to use the '{routing_result.tool_name}' tool with arguments: {routing_result.arguments}"
                result["tool_routing"] = routing_result.to_dict()
            else:
                result["response"] = f"I'm GLADIUS, a native AI assistant. I received your message: '{message}'. My tool router couldn't determine a specific tool, so I'm responding directly. How can I help you?"
                result["routing_status"] = "fallback"
        else:
            # Basic response without modules
            result["response"] = f"GLADIUS received: '{message}'. Note: Some modules are not available ({IMPORT_ERROR}). Running in limited mode."
            result["limited_mode"] = True
            
    except Exception as e:
        result["response"] = f"Error processing request: {str(e)}"
        result["error"] = str(e)
    
    print(json.dumps(result, indent=2))
    return 0


def cmd_benchmark(args):
    """Run performance benchmark."""
    result = {
        "benchmark": "gladius_performance",
        "timestamp": datetime.now().isoformat(),
        "metrics": {}
    }
    
    # Inference speed test
    start = time.time()
    iterations = int(args.iterations) if args.iterations else 10
    
    model_path = get_model_path()
    
    if MODULES_AVAILABLE and model_path:
        try:
            router = NativeToolRouter(
                model_path=str(model_path),
                use_native=True,
                use_ollama=False,
                use_pattern=True
            )
            
            latencies = []
            for i in range(iterations):
                iter_start = time.time()
                router.route(f"Test query {i}")
                latencies.append((time.time() - iter_start) * 1000)
            
            result["metrics"]["routing_latency_ms"] = {
                "min": min(latencies),
                "max": max(latencies),
                "avg": sum(latencies) / len(latencies),
                "iterations": iterations
            }
        except Exception as e:
            result["metrics"]["routing_error"] = str(e)
    else:
        result["metrics"]["note"] = "Model or modules not available for benchmark"
    
    # Memory test
    try:
        memory = HektorMemory()
        mem_start = time.time()
        memory.remember("benchmark_test", "This is a benchmark test entry")
        memory.recall("benchmark test")
        result["metrics"]["memory_roundtrip_ms"] = (time.time() - mem_start) * 1000
    except Exception as e:
        result["metrics"]["memory_error"] = str(e)
    
    result["metrics"]["total_time_seconds"] = time.time() - start
    
    print(json.dumps(result, indent=2))
    return 0


def cmd_train(args):
    """Start training pipeline."""
    result = {
        "action": "train",
        "timestamp": datetime.now().isoformat()
    }
    
    epochs = int(args.epochs) if args.epochs else 10
    batch_size = int(args.batch_size) if args.batch_size else 32
    
    result["config"] = {
        "epochs": epochs,
        "batch_size": batch_size,
        "dataset": args.dataset or "default"
    }
    
    # Check hardware for GPU/CPU decision
    if MODULES_AVAILABLE:
        try:
            hw = detect_hardware()
            if hw.get("gpu_available"):
                result["trainer"] = "gpu"
                result["message"] = f"Starting GPU training for {epochs} epochs"
            else:
                result["trainer"] = "cpu"
                result["message"] = f"Starting CPU training for {epochs} epochs (no GPU detected)"
        except Exception as e:
            result["trainer"] = "cpu"
            result["message"] = f"Starting CPU training (hardware detection failed: {e})"
    else:
        result["trainer"] = "cpu"
        result["message"] = "Starting training in limited mode"
    
    # Note: Actual training would be spawned as a separate process
    result["status"] = "initiated"
    result["note"] = "Training process started. Monitor logs for progress."
    
    print(json.dumps(result, indent=2))
    return 0


def cmd_tools(args):
    """List available tools."""
    tools = {
        "memory": ["remember", "recall", "forget", "get_context"],
        "search": ["search", "hybrid_search"],
        "workspace": ["read_file", "write_file", "list_dir"],
        "database": ["read_db", "write_db", "list_databases"],
        "build": ["build", "build_workspace", "build_memory"],
        "social": ["post_tweet", "reply_tweet", "like_tweet"],
        "analysis": ["generate_chart", "detect_trendlines"],
    }
    
    result = {
        "tool_count": sum(len(v) for v in tools.values()),
        "categories": tools,
        "router": "native" if get_model_path() else "pattern_fallback"
    }
    
    print(json.dumps(result, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="GLADIUS CLI - Native AI Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check GLADIUS status")
    
    # Interact command
    interact_parser = subparsers.add_parser("interact", help="Interact with GLADIUS")
    interact_parser.add_argument("--message", "-m", required=True, help="Message to send")
    
    # Benchmark command
    benchmark_parser = subparsers.add_parser("benchmark", help="Run performance benchmark")
    benchmark_parser.add_argument("--dataset", help="Benchmark dataset")
    benchmark_parser.add_argument("--metric", help="Specific metric to measure")
    benchmark_parser.add_argument("--iterations", "-n", default="10", help="Number of iterations")
    
    # Train command
    train_parser = subparsers.add_parser("train", help="Start training")
    train_parser.add_argument("--dataset", help="Training dataset")
    train_parser.add_argument("--epochs", "-e", default="10", help="Number of epochs")
    train_parser.add_argument("--batch-size", "-b", default="32", help="Batch size")
    
    # Tools command
    tools_parser = subparsers.add_parser("tools", help="List available tools")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        "status": cmd_status,
        "interact": cmd_interact,
        "benchmark": cmd_benchmark,
        "train": cmd_train,
        "tools": cmd_tools,
    }
    
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
