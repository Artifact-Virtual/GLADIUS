#!/usr/bin/env python3
"""
GLADIUS Status API - Real-time system state for WebUI integration
Provides /api/status endpoint that the webapp expects
"""

import os
import sys
import json
import psutil
import subprocess
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

app = FastAPI(title="GLADIUS Status API", version="1.1.0")

# Enable CORS for webapp
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load config
CONFIG_FILE = PROJECT_ROOT / "config.json"

def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}

def check_process_running(name: str) -> tuple[bool, Optional[int]]:
    """Check if a process with given name is running"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info.get('cmdline') or [])
            if name.lower() in cmdline.lower():
                return True, proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False, None

def check_gpu_available() -> bool:
    """Check if CUDA GPU is available"""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
            capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0 and len(result.stdout.strip()) > 0
    except:
        return False

def get_training_status() -> dict:
    """Get current training status from logs and checkpoint files"""
    import re
    checkpoint_dir = PROJECT_ROOT / "GLADIUS" / "models" / "checkpoints"
    training_active = False
    epochs = 0
    loss = 0.0
    progress = 0.0
    tokens = 0
    
    # Check if training process is running
    training_active, _ = check_process_running("train_cpu.py")
    if not training_active:
        training_active, _ = check_process_running("train_gpu.py")
    if not training_active:
        training_active, _ = check_process_running("gladius_trainer")
    
    # Try to read latest checkpoint info
    try:
        checkpoint_files = list(checkpoint_dir.glob("checkpoint_epoch_*.pt")) if checkpoint_dir.exists() else []
        if checkpoint_files:
            latest = max(checkpoint_files, key=lambda p: p.stat().st_mtime)
            epoch_str = latest.stem.split('_')[-1]
            epochs = int(epoch_str)
    except:
        pass
    
    # Try to read training log for loss and tokens
    # Log format example:
    # │  Epoch: 1/3   Step: 105/660   Progress: 15.9%
    # │  Current:  1.828325  ↓    Avg: 4.727455
    # │  Tokens Processed: 107,520
    log_file = PROJECT_ROOT / "logs" / "training.log"
    trainer_log = PROJECT_ROOT / "logs" / "trainer.log"
    
    log_to_read = log_file if log_file.exists() else (trainer_log if trainer_log.exists() else None)
    
    # ANSI escape code stripper
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    if log_to_read:
        try:
            with open(log_to_read, encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Strip ANSI escape codes
                content = ansi_escape.sub('', content)
                lines = content.split('\n')[-200:]  # Last 200 lines
                full_text = '\n'.join(lines)
                
                # Extract Tokens Processed: 107,520
                token_match = re.search(r'Tokens Processed:\s*([\d,]+)', full_text)
                if token_match:
                    tokens = int(token_match.group(1).replace(',', ''))
                
                # Extract Progress: 15.9%
                progress_match = re.search(r'Progress:\s*([\d.]+)%', full_text)
                if progress_match:
                    progress = float(progress_match.group(1))
                
                # Extract Epoch: 1/3
                epoch_match = re.search(r'Epoch:\s*(\d+)/\d+', full_text)
                if epoch_match:
                    epochs = int(epoch_match.group(1))
                
                # Extract Current loss: 1.828325
                loss_match = re.search(r'Current:\s*([\d.]+)', full_text)
                if loss_match:
                    loss = float(loss_match.group(1))
        except Exception as e:
            print(f"Error reading training log: {e}")
    
    return {
        "active": training_active,
        "progress": progress,
        "epochs": epochs,
        "loss": loss,
        "tokens": tokens
    }

def get_hektor_stats() -> dict:
    """Get Hektor VDB statistics"""
    vector_count = 0
    stores_stats = {}
    
    # Try to import and use actual Hektor memory
    try:
        from GLADIUS.utils.hektor_memory import get_memory_manager, HEKTOR_AVAILABLE
        if HEKTOR_AVAILABLE:
            manager = get_memory_manager()
            all_stats = manager.stats_all()
            for store_name, stats in all_stats.items():
                count = stats.get("total_vectors", 0)
                vector_count += count
                stores_stats[store_name] = count
    except ImportError:
        pass
    except Exception as e:
        print(f"Hektor stats error: {e}")
    
    # Fallback: read from vectorizer state file
    if vector_count == 0:
        vectorizer_state = PROJECT_ROOT / ".vectorizer_state.json"
        if vectorizer_state.exists():
            try:
                with open(vectorizer_state) as f:
                    data = json.load(f)
                    stats = data.get("stats", {})
                    vector_count = stats.get("total_processed", 0)
            except:
                pass
    
    # Fallback: read from hektor_texts.json files
    if vector_count == 0:
        memory_dir = PROJECT_ROOT / "GLADIUS" / "memory"
        if memory_dir.exists():
            for f in memory_dir.glob("*_texts.json"):
                try:
                    with open(f) as file:
                        data = json.load(file)
                        if isinstance(data, dict):
                            vector_count += len(data)
                except:
                    pass
    
    return {
        "active": vector_count > 0,
        "vector_count": vector_count,
        "stores": stores_stats
    }

def get_system_metrics() -> dict:
    """Get system resource metrics"""
    return {
        "memory_mb": psutil.virtual_memory().used // (1024 * 1024),
        "memory_percent": psutil.virtual_memory().percent,
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "gpu_available": check_gpu_available()
    }

def get_module_status(config: dict) -> dict:
    """Get status of all modules"""
    modules = config.get("modules", {})
    
    sentinel_running, _ = check_process_running("watchdog.py")
    legion_running, _ = check_process_running("legion") 
    syndicate_running, _ = check_process_running("syndicate")
    automata_running, _ = check_process_running("automata")
    hektor_active = get_hektor_stats()["active"]
    training_active = get_training_status()["active"]
    
    return {
        "sentinel": sentinel_running,
        "legion": legion_running and modules.get("legion", {}).get("enabled", False),
        "syndicate": syndicate_running and modules.get("syndicate", {}).get("enabled", True),
        "automata": automata_running and modules.get("automata", {}).get("enabled", True),
        "hektor": hektor_active,
        "training": training_active
    }

@app.get("/")
def root():
    return {"status": "ok", "service": "GLADIUS Status API", "version": "1.1.0"}

@app.get("/api/status")
def get_status():
    """Main status endpoint - returns full system state"""
    config = load_config()
    training = get_training_status()
    hektor = get_hektor_stats()
    system = get_system_metrics()
    modules = get_module_status(config)
    
    # Determine overall state
    if training["active"]:
        state = "LEARNING"
    elif modules["sentinel"] or modules["syndicate"]:
        state = "INTERACTING"
    else:
        state = "SLEEPING"
    
    return {
        "state": state,
        "model": {
            "name": "gladius1.1:71M-native",
            "version": "1.1.0",
            "params": 71000000,
            "architecture": "transformer"
        },
        "training": training,
        "hektor": hektor,
        "system": system,
        "modules": modules,
        "inference": {
            "active": False,  # Set when chat is active
            "latency_ms": 0,
            "tokens_per_second": 0,
            "context_length": 2048,
            "temperature": 0.7
        },
        "chat": {
            "active": False
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/state")
def set_state(payload: dict):
    """Update system state"""
    target = payload.get("state", "SLEEPING")
    # This would trigger actual state changes in a full implementation
    return {"success": True, "state": target}

@app.post("/api/training/start")
def start_training():
    """Start training process"""
    try:
        # Launch training in background
        training_script = PROJECT_ROOT / "GLADIUS" / "training" / "train_cpu.py"
        if check_gpu_available():
            training_script = PROJECT_ROOT / "GLADIUS" / "training" / "train_gpu.py"
        
        subprocess.Popen(
            [sys.executable, str(training_script)],
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return {"success": True, "message": "Training started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/training/stop")
def stop_training():
    """Stop training process"""
    # Find and terminate training processes
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info.get('cmdline') or [])
            if 'train_cpu.py' in cmdline or 'train_gpu.py' in cmdline:
                proc.terminate()
        except:
            pass
    return {"success": True, "message": "Training stopped"}

@app.get("/api/metrics")
def get_metrics():
    """Get detailed metrics for monitoring"""
    system = get_system_metrics()
    training = get_training_status()
    
    return {
        "system": system,
        "training": training,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    port = int(os.getenv("GLADIUS_API_PORT", "7000"))
    print(f"Starting GLADIUS Status API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
