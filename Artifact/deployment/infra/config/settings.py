"""
Configuration management system.

Provides centralized configuration for the business infrastructure.
"""

import os
import json
from typing import Any, Dict, Optional
from pathlib import Path

from ..core.exceptions import ConfigurationError


class Config:
    """
    Configuration manager for business infrastructure.
    
    Supports loading configuration from:
    - Environment variables
    - JSON configuration files
    - Default values
    """
    
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        """Singleton pattern to ensure single config instance."""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialize_defaults()
        return cls._instance
    
    def _initialize_defaults(self) -> None:
        """Initialize default configuration values."""
        self._config = {
            # System configuration
            "system": {
                "name": "Gold Standard Business Infrastructure",
                "version": "1.0.0",
                "environment": os.getenv("ENVIRONMENT", "development"),
            },
            
            # Database configuration
            "database": {
                "type": os.getenv("DB_TYPE", "in-memory"),
                "connection_string": os.getenv("DB_CONNECTION_STRING", ""),
                "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
            },
            
            # Market configuration
            "markets": {
                "default_timezone": os.getenv("DEFAULT_TIMEZONE", "America/New_York"),
                "default_currency": os.getenv("DEFAULT_CURRENCY", "USD"),
                "trading_days": [0, 1, 2, 3, 4],  # Monday-Friday
            },
            
            # Portfolio configuration
            "portfolio": {
                "default_base_currency": os.getenv("PORTFOLIO_CURRENCY", "USD"),
                "max_positions_per_portfolio": int(os.getenv("MAX_POSITIONS", "100")),
                "allow_short_positions": os.getenv("ALLOW_SHORT", "true").lower() == "true",
            },
            
            # Logging configuration
            "logging": {
                "level": os.getenv("LOG_LEVEL", "INFO"),
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "output": os.getenv("LOG_OUTPUT", "console"),
                "file_path": os.getenv("LOG_FILE", "logs/infra.log"),
            },
            
            # Validation configuration
            "validation": {
                "strict_mode": os.getenv("STRICT_VALIDATION", "true").lower() == "true",
                "max_symbol_length": int(os.getenv("MAX_SYMBOL_LENGTH", "20")),
                "max_name_length": int(os.getenv("MAX_NAME_LENGTH", "255")),
            },
        }
    
    def load_from_file(self, file_path: str) -> None:
        """
        Load configuration from JSON file.
        
        Args:
            file_path: Path to JSON configuration file
            
        Raises:
            ConfigurationError: If file cannot be loaded
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise ConfigurationError(
                    "config_file",
                    f"Configuration file not found: {file_path}"
                )
            
            with open(path, 'r') as f:
                file_config = json.load(f)
            
            # Merge with existing config
            self._deep_merge(self._config, file_config)
            
        except json.JSONDecodeError as e:
            raise ConfigurationError(
                "config_file",
                f"Invalid JSON in configuration file: {str(e)}"
            )
        except Exception as e:
            raise ConfigurationError(
                "config_file",
                f"Error loading configuration file: {str(e)}"
            )
    
    def _deep_merge(self, base: dict, updates: dict) -> None:
        """
        Deep merge updates into base dictionary.
        
        Args:
            base: Base dictionary to update
            updates: Dictionary with updates
        """
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.
        
        Args:
            key: Configuration key (e.g., "database.type")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by dot-notation key.
        
        Args:
            key: Configuration key (e.g., "database.type")
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section.
        
        Args:
            section: Section name (e.g., "database")
            
        Returns:
            Configuration section dictionary
            
        Raises:
            ConfigurationError: If section not found
        """
        value = self.get(section)
        if value is None:
            raise ConfigurationError(
                section,
                f"Configuration section '{section}' not found"
            )
        
        if not isinstance(value, dict):
            raise ConfigurationError(
                section,
                f"Configuration section '{section}' is not a dictionary"
            )
        
        return value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get full configuration as dictionary.
        
        Returns:
            Complete configuration dictionary
        """
        return self._config.copy()
    
    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._initialize_defaults()
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return f"Config(environment={self.get('system.environment')})"


# Global configuration instance
config = Config()
