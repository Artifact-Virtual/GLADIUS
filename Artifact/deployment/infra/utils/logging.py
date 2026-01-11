"""
Logging utilities for business infrastructure.

Provides consistent logging across the system.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from ..config.settings import config


class Logger:
    """
    Logging wrapper providing consistent logging interface.
    """
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get or create a logger.
        
        Args:
            name: Logger name (usually module name)
            
        Returns:
            Configured logger
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        
        # Get configuration
        level = config.get("logging.level", "INFO")
        format_str = config.get("logging.format") or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        output = config.get("logging.output", "console")
        
        # Set level
        logger.setLevel(getattr(logging, level.upper()))
        
        # Remove existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(format_str)
        
        # Add console handler
        if output in ["console", "both"]:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # Add file handler
        if output in ["file", "both"]:
            file_path = config.get("logging.file_path")
            if file_path:
                # Ensure directory exists
                Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                
                file_handler = logging.FileHandler(file_path)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
        
        cls._loggers[name] = logger
        return logger
    
    @classmethod
    def set_level(cls, level: str) -> None:
        """
        Set logging level for all loggers.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        level_obj = getattr(logging, level.upper())
        
        for logger in cls._loggers.values():
            logger.setLevel(level_obj)
        
        config.set("logging.level", level.upper())


def get_logger(name: str) -> logging.Logger:
    """
    Convenience function to get a logger.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger
    """
    return Logger.get_logger(name)
