#!/usr/bin/env python3
"""
GLADIUS Path Resolver
=====================

Central path configuration for the entire GLADIUS system.
All paths are resolved dynamically based on this script's location.

This module provides:
- Dynamic path resolution (no hardcoded paths)
- Cross-platform compatibility
- Environment variable support
- JSON config path variable resolution

Usage:
    from scripts.path_resolver import PATHS, resolve_path
    
    db_path = PATHS.gladius_root / "data" / "mydb.sqlite"
    resolved = resolve_path("${GLADIUS_ROOT}/LEGION/data")

Author: Artifact Virtual Systems
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional


class GladiusPaths:
    """Central path configuration for GLADIUS system"""
    
    def __init__(self):
        # Auto-detect root based on this file's location
        # scripts/path_resolver.py -> gladius root
        self._script_path = Path(__file__).resolve()
        self._gladius_root = self._script_path.parent.parent
        
        # Allow override via environment variable
        env_root = os.environ.get("GLADIUS_ROOT")
        if env_root:
            self._gladius_root = Path(env_root).resolve()
    
    @property
    def gladius_root(self) -> Path:
        """Root of GLADIUS installation"""
        return self._gladius_root
    
    @property
    def artifact(self) -> Path:
        """Artifact infrastructure root"""
        return self._gladius_root / "Artifact"
    
    @property
    def sentinel(self) -> Path:
        """SENTINEL guardian system root"""
        return self._gladius_root / "SENTINEL"
    
    @property
    def legion(self) -> Path:
        """LEGION enterprise orchestrator root"""
        return self._gladius_root / "LEGION"
    
    @property
    def gladius_model(self) -> Path:
        """GLADIUS AI model directory"""
        return self._gladius_root / "GLADIUS"
    
    @property
    def logs(self) -> Path:
        """Logs directory"""
        return self._gladius_root / "logs"
    
    @property
    def data(self) -> Path:
        """Data directory"""
        return self._gladius_root / "data"
    
    @property
    def config(self) -> Path:
        """Main config file"""
        return self._gladius_root / ".env"
    
    @property
    def docs(self) -> Path:
        """Documentation directory"""
        return self._gladius_root / "docs"
    
    @property
    def scripts(self) -> Path:
        """Scripts directory"""
        return self._gladius_root / "scripts"
    
    @property
    def pids(self) -> Path:
        """PID files directory"""
        return self._gladius_root / ".pids"
    
    @property
    def research_outputs(self) -> Path:
        """Research outputs directory"""
        return self.artifact / "research_outputs"
    
    @property
    def syndicate(self) -> Path:
        """Syndicate research pipeline"""
        return self.artifact / "syndicate"
    
    @property
    def training(self) -> Path:
        """Training directory for GLADIUS model"""
        return self.gladius_model / "training"
    
    @property
    def models(self) -> Path:
        """Trained models directory"""
        return self.gladius_model / "models"
    
    def to_dict(self) -> Dict[str, str]:
        """Export all paths as dictionary"""
        return {
            "GLADIUS_ROOT": str(self.gladius_root),
            "ARTIFACT": str(self.artifact),
            "SENTINEL": str(self.sentinel),
            "LEGION": str(self.legion),
            "GLADIUS_MODEL": str(self.gladius_model),
            "LOGS": str(self.logs),
            "DATA": str(self.data),
            "DOCS": str(self.docs),
            "SCRIPTS": str(self.scripts),
            "PIDS": str(self.pids),
            "RESEARCH_OUTPUTS": str(self.research_outputs),
            "SYNDICATE": str(self.syndicate),
            "TRAINING": str(self.training),
            "MODELS": str(self.models),
        }
    
    def ensure_directories(self):
        """Create all required directories if they don't exist"""
        for name, path in self.to_dict().items():
            p = Path(path)
            if not p.suffix:  # Only create if it's a directory (no file extension)
                p.mkdir(parents=True, exist_ok=True)


# Singleton instance
PATHS = GladiusPaths()


def resolve_path(path_string: str) -> Path:
    """
    Resolve a path string with ${GLADIUS_ROOT} style variables.
    
    Args:
        path_string: Path with variables like "${GLADIUS_ROOT}/LEGION"
        
    Returns:
        Resolved Path object
    """
    path_map = PATHS.to_dict()
    
    # Pattern to match ${VAR_NAME}
    pattern = re.compile(r'\$\{([A-Z_]+)\}')
    
    def replace_var(match):
        var_name = match.group(1)
        return path_map.get(var_name, match.group(0))
    
    resolved = pattern.sub(replace_var, path_string)
    return Path(resolved)


def resolve_config_paths(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively resolve all path variables in a configuration dictionary.
    
    Args:
        config: Configuration dictionary with ${VAR} style paths
        
    Returns:
        Config with all paths resolved
    """
    if isinstance(config, dict):
        return {k: resolve_config_paths(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [resolve_config_paths(item) for item in config]
    elif isinstance(config, str) and "${" in config:
        return str(resolve_path(config))
    return config


def load_config_with_paths(config_path: Path) -> Dict[str, Any]:
    """
    Load a JSON config file and resolve all path variables.
    
    Args:
        config_path: Path to JSON config file
        
    Returns:
        Configuration dictionary with resolved paths
    """
    with open(config_path) as f:
        config = json.load(f)
    return resolve_config_paths(config)


def export_paths_for_shell() -> str:
    """
    Export paths as shell environment variables.
    
    Returns:
        Shell export statements
    """
    lines = []
    for name, path in PATHS.to_dict().items():
        lines.append(f'export {name}="{path}"')
    return "\n".join(lines)


def print_paths():
    """Print all paths for debugging"""
    print("GLADIUS Path Configuration")
    print("=" * 60)
    for name, path in PATHS.to_dict().items():
        exists = "✓" if Path(path).exists() else "✗"
        print(f"  {exists} {name}: {path}")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "shell":
            print(export_paths_for_shell())
        elif cmd == "json":
            print(json.dumps(PATHS.to_dict(), indent=2))
        elif cmd == "resolve" and len(sys.argv) > 2:
            print(resolve_path(sys.argv[2]))
        elif cmd == "ensure":
            PATHS.ensure_directories()
            print("All directories created")
        else:
            print("Usage: path_resolver.py [shell|json|resolve <path>|ensure]")
    else:
        print_paths()
