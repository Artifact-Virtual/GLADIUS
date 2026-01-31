#!/usr/bin/env python3
"""
GLADIUS API Server - Real-time system state endpoint
Provides /api/status for WebUI visualization
"""

import os
import sys
import json
import time
import psutil
import subprocess
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS

# Add paths
GLADIUS_ROOT = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(GLADIUS_ROOT))

app = Flask(__name__)
CORS(app)

# Config
CONFIG_PATH = GLADIUS_ROOT / "config.json"
HEKTOR_DB_PATH = GLADIUS_ROOT / "GLADIUS" / "hektor_data"

def load_config():
    """Load config.json"""
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except:
        return {}

def check_process_running(pattern: str) -> bool:
    """Check if a process matching pattern is running"""
    try:
        result = subprocess.run(
            ['pgrep', '-f', pattern],
            capture_output=True, text=True
        )
        return result.returncode == 0
    except:
        return False

def get_gpu_available() -> bool:
    """Check if GPU is available"""
    try:
        import torch
        return torch.cuda.is_available()
    except:
        pass
    # Fallback: check nvidia-smi
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True)
        return result.returncode == 0
    except:
        return False

def get_hektor_vector_count() -> int:
    """Get vector count from Hektor VDB"""
    try:
        # Check if hektor data exists
        if HEKTOR_DB_PATH.exists():
            # Count vectors from stored data
            total = 0
            for db_file in HEKTOR_DB_PATH.glob("*.json"):
                try:
                    with open(db_file) as f:
                        data = json.load(f)
                        if 'vectors' in data:
                            total += len(data['vectors'])
                except:
                    pass
            return total
    except:
        pass
    return 0

def get_training_status() -> dict:
    """Get training status from checkpoint/state files"""
    checkpoint_dir = GLADIUS_ROOT / "GLADIUS" / "tmp" / "checkpoints"
    state_file = checkpoint_dir / "training_state.json"
    
    result = {
        "active": check_process_running("gladius_trainer"),
        "progress": 0,
        "epochs": 0,
        "loss": 0.0,
        "tokens": 0
    }
    
    try:
        if state_file.exists():
            with open(state_file) as f:
                state = json.load(f)
                result["epochs"] = state.get("epoch", 0)
                result["progress"] = state.get("progress", 0)
                result["loss"] = state.get("loss", 0.0)
                result["tokens"] = state.get("tokens_processed", 0)
    except:
        pass
    
    return result

def determine_system_state() -> str:
    """Determine overall system state"""
    # Check if training
    if check_process_running("gladius_trainer"):
        return "LEARNING"
    
    # Check if interacting (chat, inference, etc)
    if check_process_running("chat_interface") or check_process_running("speak.py"):
        return "INTERACTING"
    
    # Check if any modules are actively processing
    if check_process_running("sentinel") or check_process_running("syndicate"):
        return "INTERACTING"
    
    return "SLEEPING"

@app.route('/api/status', methods=['GET'])
def get_status():
    """Main status endpoint for WebUI"""
    config = load_config()
    training = get_training_status()
    
    # System metrics
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=0.1)
    
    response = {
        "state": determine_system_state(),
        "model": {
            "name": config.get("model", {}).get("name", "gladius1.1:71M-native"),
            "params": config.get("model", {}).get("parameters", 71000000),
            "version": config.get("version", "1.1.0"),
            "type": "native"
        },
        "hektor": {
            "vector_count": get_hektor_vector_count()
        },
        "training": training,
        "system": {
            "memory_mb": int(memory.used / 1024 / 1024),
            "memory_total_mb": int(memory.total / 1024 / 1024),
            "cpu_percent": cpu_percent,
            "gpu_available": get_gpu_available()
        },
        "modules": {
            "sentinel": check_process_running("sentinel"),
            "legion": check_process_running("continuous_operation"),
            "syndicate": check_process_running("syndicate"),
            "automata": check_process_running("automata"),
            "hektor": HEKTOR_DB_PATH.exists(),
            "training": training["active"]
        },
        "inference": {
            "active": check_process_running("llama"),
            "latency_ms": 0,
            "tokens_per_second": 0,
            "context_length": 2048,
            "temperature": 0.7
        },
        "timestamp": int(time.time() * 1000)
    }
    
    return jsonify(response)

@app.route('/api/state', methods=['POST'])
def set_state():
    """Trigger state change (start/stop training, etc)"""
    data = request.json or {}
    target_state = data.get('state', '').upper()
    
    if target_state == 'LEARNING':
        # Start training if not running
        if not check_process_running("gladius_trainer"):
            # Launch training in background
            trainer_path = GLADIUS_ROOT / "GLADIUS" / "training" / "gladius_trainer.py"
            if trainer_path.exists():
                subprocess.Popen(
                    [sys.executable, str(trainer_path), '--epochs', '10'],
                    cwd=str(GLADIUS_ROOT),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return jsonify({"success": True, "message": "Training started"})
        return jsonify({"success": False, "message": "Training already running"})
    
    elif target_state == 'SLEEPING':
        # Stop training if running (would need proper implementation)
        return jsonify({"success": True, "message": "State set to sleeping"})
    
    return jsonify({"success": True, "state": target_state})

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "gladius-api"})

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Detailed metrics endpoint"""
    memory = psutil.virtual_memory()
    cpu_times = psutil.cpu_times_percent(interval=0.1)
    
    return jsonify({
        "memory": {
            "total_mb": int(memory.total / 1024 / 1024),
            "used_mb": int(memory.used / 1024 / 1024),
            "available_mb": int(memory.available / 1024 / 1024),
            "percent": memory.percent
        },
        "cpu": {
            "percent": psutil.cpu_percent(),
            "user": cpu_times.user,
            "system": cpu_times.system,
            "idle": cpu_times.idle
        },
        "gpu_available": get_gpu_available(),
        "uptime_seconds": time.time() - psutil.boot_time()
    })

if __name__ == '__main__':
    port = int(os.environ.get('GLADIUS_API_PORT', 7001))
    print(f"🚀 GLADIUS API Server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
