"""GLADIUS Utilities"""

from .hardware import get_device, get_hardware_info, configure_torch_for_device, HardwareInfo, print_hardware_status

# Hektor memory (optional - requires hektor-vdb)
try:
    from .hektor_memory import (
        HektorMemory,
        GladiusMemoryManager,
        get_memory_manager,
        remember,
        recall,
        HEKTOR_AVAILABLE
    )
except ImportError:
    HEKTOR_AVAILABLE = False

__all__ = [
    "get_device",
    "get_hardware_info",
    "configure_torch_for_device",
    "print_hardware_status",
    "HardwareInfo",
    "HektorMemory",
    "GladiusMemoryManager", 
    "get_memory_manager",
    "remember",
    "recall",
    "HEKTOR_AVAILABLE"
]
