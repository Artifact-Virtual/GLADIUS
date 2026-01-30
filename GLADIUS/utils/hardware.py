#!/usr/bin/env python3
"""
GLADIUS Hardware Detection Utility
===================================

Centralized hardware detection for GPU/CPU fallback.
MUST check for GPU and downgrade to CPU if unavailable.

Usage:
    from GLADIUS.utils.hardware import get_device, get_hardware_info, configure_torch_for_device
    
    device = get_device()  # Returns 'cuda' or 'cpu'
    info = get_hardware_info()  # Detailed hardware info

Author: Artifact Virtual Systems
"""

import os
import sys
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class HardwareInfo:
    """Hardware configuration details"""
    device: str  # 'cuda' or 'cpu'
    gpu_available: bool
    gpu_name: Optional[str] = None
    gpu_memory_gb: Optional[float] = None
    cpu_cores: Optional[int] = None
    ram_gb: Optional[float] = None
    torch_version: Optional[str] = None
    cuda_version: Optional[str] = None
    
    def __str__(self):
        if self.gpu_available:
            return f"GPU: {self.gpu_name} ({self.gpu_memory_gb:.1f}GB)"
        return f"CPU ({self.cpu_cores} cores, {self.ram_gb:.1f}GB RAM)"


def get_device() -> str:
    """
    Detect available hardware device.
    MUST check for GPU and return 'cpu' if unavailable.
    
    Returns:
        'cuda' if GPU available, 'cpu' otherwise
    """
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
    except ImportError:
        pass
    return "cpu"


def get_hardware_info() -> HardwareInfo:
    """
    Get detailed hardware information.
    
    Returns:
        HardwareInfo dataclass with device details
    """
    device = "cpu"
    gpu_available = False
    gpu_name = None
    gpu_memory_gb = None
    torch_version = None
    cuda_version = None
    cpu_cores = None
    ram_gb = None
    
    # Get CPU info
    try:
        cpu_cores = os.cpu_count()
    except:
        pass
    
    # Get RAM info
    try:
        import psutil
        ram_gb = psutil.virtual_memory().total / (1024**3)
    except ImportError:
        pass
    
    # Check for GPU
    try:
        import torch
        torch_version = torch.__version__
        
        if torch.cuda.is_available():
            device = "cuda"
            gpu_available = True
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            cuda_version = torch.version.cuda
    except ImportError:
        pass
    except Exception:
        pass
    
    return HardwareInfo(
        device=device,
        gpu_available=gpu_available,
        gpu_name=gpu_name,
        gpu_memory_gb=gpu_memory_gb,
        cpu_cores=cpu_cores,
        ram_gb=ram_gb,
        torch_version=torch_version,
        cuda_version=cuda_version
    )


def configure_torch_for_device(device: str = None) -> Dict[str, Any]:
    """
    Configure PyTorch settings based on available hardware.
    MUST optimize for CPU if GPU not available.
    
    Args:
        device: Force specific device ('cuda' or 'cpu'), auto-detect if None
        
    Returns:
        Dict with recommended settings for model loading
    """
    if device is None:
        device = get_device()
    
    if device == "cuda":
        return {
            "device": "cuda",
            "device_map": "auto",
            "torch_dtype": "float16",
            "low_cpu_mem_usage": False,
            "max_tokens": 2048,
            "batch_size": 8,
        }
    else:
        # CPU mode - MUST optimize for memory and speed
        return {
            "device": "cpu",
            "device_map": None,  # No auto mapping for CPU
            "torch_dtype": "float32",
            "low_cpu_mem_usage": True,
            "max_tokens": 512,  # Reduced for CPU
            "batch_size": 1,  # Minimal batch for CPU
        }


def print_hardware_status():
    """Print hardware status to console"""
    info = get_hardware_info()
    
    print("\n" + "="*50)
    print("GLADIUS Hardware Detection")
    print("="*50)
    
    if info.gpu_available:
        print(f"  ✓ GPU Available: {info.gpu_name}")
        print(f"    Memory: {info.gpu_memory_gb:.1f} GB")
        print(f"    CUDA Version: {info.cuda_version}")
        print(f"    Mode: GPU (float16)")
    else:
        print(f"  ✗ GPU Not Available")
        print(f"    Mode: CPU (float32)")
        print(f"    CPU Cores: {info.cpu_cores}")
        if info.ram_gb:
            print(f"    RAM: {info.ram_gb:.1f} GB")
    
    if info.torch_version:
        print(f"    PyTorch: {info.torch_version}")
    
    print("="*50 + "\n")


if __name__ == "__main__":
    print_hardware_status()
    
    config = configure_torch_for_device()
    print("Recommended configuration:")
    for k, v in config.items():
        print(f"  {k}: {v}")
