"""
Configuration management for Enterprise Automation Suite.

Manages all configuration for ERP integrations, social media platforms,
AI settings, and automation preferences.
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from enum import Enum


class ERPSystem(Enum):
    """Supported ERP systems."""
    SAP = "SAP"
    NETSUITE = "NetSuite"
    ODOO = "Odoo"
    MICROSOFT_DYNAMICS = "Microsoft Dynamics"
    ORACLE_ERP = "Oracle ERP Cloud"
    WORKDAY = "Workday"
    INFOR = "Infor"
    SAGE = "Sage"
    EPICOR = "Epicor"
    ACUMATICA = "Acumatica"


class SocialPlatform(Enum):
    """Supported social media platforms."""
    TWITTER = "Twitter/X"
    LINKEDIN = "LinkedIn"
    FACEBOOK = "Facebook"
    INSTAGRAM = "Instagram"
    REDDIT = "Reddit"
    YOUTUBE = "YouTube"
    TIKTOK = "TikTok"
    PINTEREST = "Pinterest"
    MEDIUM = "Medium"
    SUBSTACK = "Substack"


class AutomationConfig:
    """
    Central configuration manager for the enterprise automation suite.
    
    Handles configuration for:
    - ERP system connections
    - Social media platform credentials
    - AI content generation settings
    - Scheduling preferences
    - Dashboard access
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to configuration file (JSON)
        """
        self.config_file = config_file or os.getenv(
            "ENTERPRISE_CONFIG",
            str(Path.home() / ".automata" / "config.json")
        )
        self.config = self._load_default_config()
        
        if Path(self.config_file).exists():
            self.load_from_file(self.config_file)
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        return {
            "version": "1.0.0",
            "business": {
                "name": "",
                "industry": "",
                "target_audience": "",
                "brand_voice": "professional",
                "timezone": "UTC"
            },
            "erp_systems": {
                system.value: {
                    "enabled": False,
                    "api_url": "",
                    "api_key": "",
                    "api_secret": "",
                    "username": "",
                    "password": "",
                    "sync_interval": 3600,  # seconds
                    "sync_entities": []  # customers, products, orders, etc.
                }
                for system in ERPSystem
            },
            "social_media": {
                platform.value: {
                    "enabled": False,
                    "api_key": "",
                    "api_secret": "",
                    "access_token": "",
                    "access_token_secret": "",
                    "client_id": "",
                    "client_secret": "",
                    "refresh_token": "",
                    "account_id": "",
                    "post_frequency": "daily",  # hourly, daily, weekly
                    "optimal_times": [],  # best times to post
                    "content_types": [],  # text, image, video, carousel
                    "hashtags": [],
                    "max_posts_per_day": 5
                }
                for platform in SocialPlatform
            },
            "ai_engine": {
                "provider": "openai",  # openai, anthropic, cohere, local
                "model": "gpt-4",
                "api_key": "",
                "temperature": 0.7,
                "max_tokens": 500,
                "content_style": "engaging",
                "include_emojis": True,
                "include_hashtags": True,
                "include_call_to_action": True,
                "content_themes": [],
                "avoid_topics": [],
                "brand_guidelines": ""
            },
            "scheduler": {
                "enabled": True,
                "check_interval": 60,  # seconds
                "max_concurrent_posts": 10,
                "retry_failed": True,
                "retry_attempts": 3,
                "queue_size": 100
            },
            "dashboard": {
                "host": "0.0.0.0",
                "port": 5000,
                "secret_key": "",
                "enable_auth": True,
                "admin_username": "admin",
                "admin_password": "",
                "session_timeout": 3600
            },
            "analytics": {
                "track_engagement": True,
                "track_conversions": True,
                "report_frequency": "weekly",
                "metrics": [
                    "likes", "shares", "comments", "clicks",
                    "impressions", "reach", "engagement_rate"
                ]
            },
            "integrations": {
                "infra": True,
                "gold_standard_pipeline": True,
                "herald_agent": True
            }
        }
    
    def load_from_file(self, file_path: str) -> None:
        """
        Load configuration from JSON file.
        
        Args:
            file_path: Path to configuration file
        """
        try:
            with open(file_path, 'r') as f:
                loaded_config = json.load(f)
            
            # Deep merge with defaults
            self._deep_merge(self.config, loaded_config)
        except Exception as e:
            print(f"Warning: Could not load config from {file_path}: {e}")
    
    def save_to_file(self, file_path: Optional[str] = None) -> None:
        """
        Save configuration to JSON file.
        
        Args:
            file_path: Path to save configuration (uses default if not provided)
        """
        path = file_path or self.config_file
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _deep_merge(self, base: dict, updates: dict) -> None:
        """Deep merge updates into base dictionary."""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.
        
        Args:
            key: Configuration key (e.g., "ai_engine.model")
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
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
            key: Configuration key
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_enabled_erp_systems(self) -> List[str]:
        """Get list of enabled ERP systems."""
        return [
            system for system, conf in self.config["erp_systems"].items()
            if conf.get("enabled", False)
        ]
    
    def get_enabled_social_platforms(self) -> List[str]:
        """Get list of enabled social media platforms."""
        return [
            platform for platform, conf in self.config["social_media"].items()
            if conf.get("enabled", False)
        ]
    
    def is_erp_enabled(self, system: str) -> bool:
        """Check if ERP system is enabled."""
        return self.config["erp_systems"].get(system, {}).get("enabled", False)
    
    def is_social_platform_enabled(self, platform: str) -> bool:
        """Check if social platform is enabled."""
        return self.config["social_media"].get(platform, {}).get("enabled", False)
    
    def validate(self) -> List[str]:
        """
        Validate configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check business info
        if not self.config["business"]["name"]:
            errors.append("Business name is required")
        
        # Check enabled ERPs have credentials
        for system in self.get_enabled_erp_systems():
            conf = self.config["erp_systems"][system]
            if not conf.get("api_url") and not conf.get("username"):
                errors.append(f"{system}: Missing credentials")
        
        # Check enabled social platforms have credentials
        for platform in self.get_enabled_social_platforms():
            conf = self.config["social_media"][platform]
            if not conf.get("api_key") and not conf.get("access_token"):
                errors.append(f"{platform}: Missing credentials")
        
        # Check AI configuration if social media is enabled
        if self.get_enabled_social_platforms():
            if not self.config["ai_engine"].get("api_key") and \
               self.config["ai_engine"]["provider"] != "local":
                errors.append("AI Engine: API key required for content generation")
        
        # Check dashboard password
        if self.config["dashboard"]["enable_auth"]:
            if not self.config["dashboard"]["admin_password"]:
                errors.append("Dashboard: Admin password required when auth is enabled")
        
        return errors
