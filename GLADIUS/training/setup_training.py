#!/usr/bin/env python3
"""
GLADIUS Pre-Training Setup
==========================
Downloads all required models and verifies environment before training.
Run this to ensure seamless training execution.
"""

import os
import sys
from pathlib import Path

# Setup paths
SCRIPT_DIR = Path(__file__).parent.resolve()
GLADIUS_DIR = SCRIPT_DIR.parent.resolve()
TMP_BASE = GLADIUS_DIR / "tmp"
CACHE_DIR = TMP_BASE / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

os.environ['HF_HOME'] = str(CACHE_DIR)
os.environ['TRANSFORMERS_CACHE'] = str(CACHE_DIR)

# Expert models to download
EXPERTS = [
    ("Qwen/Qwen2.5-1.5B-Instruct", "qwen", "Primary: Tool-calling, structured output"),
    ("meta-llama/Llama-3.2-1B-Instruct", "llama", "Reasoning backbone"),
    ("microsoft/phi-2", "phi", "Math and code"),
    ("google/gemma-2-2b-it", "gemma", "Safety and web knowledge"),
    ("TinyLlama/TinyLlama-1.1B-Chat-v1.0", "tiny", "Speed patterns"),
]

def check_packages():
    """Ensure required packages are installed"""
    print("\n" + "="*60)
    print("CHECKING DEPENDENCIES")
    print("="*60)
    
    required = ["torch", "transformers", "datasets", "accelerate", "sentencepiece"]
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
            print(f"  ✓ {pkg}")
        except ImportError:
            missing.append(pkg)
            print(f"  ✗ {pkg} (MISSING)")
    
    if missing:
        print(f"\nInstalling: {', '.join(missing)}")
        import subprocess
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-q",
            "torch", "transformers>=4.40.0", "datasets>=2.18.0",
            "accelerate>=0.28.0", "sentencepiece", "protobuf"
        ])
        print("  ✓ Packages installed")
    
    return True

def check_hardware():
    """Detect and report hardware"""
    print("\n" + "="*60)
    print("HARDWARE DETECTION")
    print("="*60)
    
    import torch
    
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"  ✓ GPU: {gpu_name}")
        print(f"  ✓ VRAM: {gpu_mem:.1f}GB")
        return "cuda"
    else:
        import psutil
        ram = psutil.virtual_memory().total / 1e9
        print(f"  ⚠ GPU: Not available")
        print(f"  ✓ RAM: {ram:.1f}GB")
        print(f"  → Will use CPU (slower but functional)")
        return "cpu"

def download_experts(device: str):
    """Download all expert models"""
    print("\n" + "="*60)
    print("DOWNLOADING EXPERT MODELS")
    print("="*60)
    print(f"Cache location: {CACHE_DIR}")
    print()
    
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    
    total_size = 0
    
    for hf_id, name, description in EXPERTS:
        print(f"\n[{name.upper()}] {hf_id}")
        print(f"  Purpose: {description}")
        
        try:
            # Download tokenizer
            print(f"  → Downloading tokenizer...", end=" ", flush=True)
            tokenizer = AutoTokenizer.from_pretrained(
                hf_id,
                trust_remote_code=True,
                cache_dir=CACHE_DIR
            )
            print("✓")
            
            # Download model
            print(f"  → Downloading model...", end=" ", flush=True)
            if device == "cuda":
                model = AutoModelForCausalLM.from_pretrained(
                    hf_id,
                    torch_dtype=torch.float16,
                    trust_remote_code=True,
                    cache_dir=CACHE_DIR
                )
            else:
                model = AutoModelForCausalLM.from_pretrained(
                    hf_id,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True,
                    trust_remote_code=True,
                    cache_dir=CACHE_DIR
                )
            print("✓")
            
            params = sum(p.numel() for p in model.parameters())
            print(f"  ✓ Parameters: {params:,}")
            
            # Free memory
            del model
            del tokenizer
            if device == "cuda":
                torch.cuda.empty_cache()
            
        except Exception as e:
            print(f"✗")
            print(f"  ERROR: {e}")
            print(f"  → This expert may require special access or credentials")
    
    # Report cache size
    import subprocess
    result = subprocess.run(["du", "-sh", str(CACHE_DIR)], capture_output=True, text=True)
    cache_size = result.stdout.split()[0] if result.returncode == 0 else "unknown"
    print(f"\nTotal cache size: {cache_size}")

def verify_training_data():
    """Check training data exists"""
    print("\n" + "="*60)
    print("VERIFYING TRAINING DATA")
    print("="*60)
    
    data_dir = SCRIPT_DIR / "data"
    
    if not data_dir.exists():
        data_dir.mkdir(parents=True)
        print(f"  ⚠ Created empty data directory: {data_dir}")
        return False
    
    files = list(data_dir.glob("*.json*"))
    
    if not files:
        print(f"  ⚠ No training data found")
        print(f"  → Will generate synthetic data during training")
        return False
    
    total_samples = 0
    for f in files:
        try:
            import json
            if f.suffix == ".jsonl":
                with open(f) as fp:
                    count = sum(1 for _ in fp)
            else:
                with open(f) as fp:
                    data = json.load(fp)
                    count = len(data) if isinstance(data, list) else 1
            print(f"  ✓ {f.name}: {count} samples")
            total_samples += count
        except Exception as e:
            print(f"  ✗ {f.name}: Error - {e}")
    
    print(f"\nTotal training samples: {total_samples}")
    return total_samples > 0

def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              GLADIUS PRE-TRAINING SETUP                       ║
║                                                               ║
║      Preparing environment for 1B parameter training          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Check packages
    check_packages()
    
    # Step 2: Detect hardware
    device = check_hardware()
    
    # Step 3: Download experts
    download_experts(device)
    
    # Step 4: Verify training data
    verify_training_data()
    
    print("\n" + "="*60)
    print("SETUP COMPLETE")
    print("="*60)
    print("""
Ready to train GLADIUS! Run:

  ./train_gladius_moe.sh     (Linux/Mac)
  ./train_gladius_moe.ps1    (PowerShell)

Or directly:
  python gladius_moe_trainer.py
    """)

if __name__ == "__main__":
    main()
