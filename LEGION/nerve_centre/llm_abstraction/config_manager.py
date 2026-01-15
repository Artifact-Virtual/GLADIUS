"""
Configuration Management for LLM Abstraction Subsystem
"""
import os
import yaml
import json
import logging
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import jsonschema
from dataclasses import dataclass, asdict
from dotenv import load_dotenv


logger = logging.getLogger(__name__)

# Use relative paths that work from any environment
BASE_DIR = Path(__file__).parent.parent.parent  # enterprise root
CONFIG_DIR = BASE_DIR / 'config'
CONFIG_PATH = str(CONFIG_DIR / 'llm_config.json')
ENV_PATH = str(CONFIG_DIR / '.env')

# Create config directory if it doesn't exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Try to load .env file if it exists
if Path(ENV_PATH).exists():
    load_dotenv(ENV_PATH)
else:
    logger.warning(f"No .env file found at {ENV_PATH}, using environment variables only")


@dataclass
class ProviderConfig:
    """Configuration for LLM provider."""
    name: str
    type: str
    endpoint: str
    api_key: str
    model: str = "default"
    rate_limit: int = 60
    timeout: int = 30
    max_retries: int = 3
    enabled: bool = True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProviderConfig':
        """Create ProviderConfig from dictionary."""
        return cls(**data)


@dataclass
class SecurityConfig:
    """Security configuration."""
    enable_auth: bool = True
    enable_encryption: bool = True
    session_timeout: int = 3600
    max_requests_per_hour: int = 100
    max_prompt_length: int = 10000
    max_context_size: int = 50000
    required_permission: str = "llm_access"
    min_security_level: int = 1
    gdpr_enabled: bool = False
    hipaa_enabled: bool = False
    blocked_patterns: List[str] = None
    compliance_rules: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.blocked_patterns is None:
            self.blocked_patterns = []
        if self.compliance_rules is None:
            self.compliance_rules = []


@dataclass
class OrchestrationConfig:
    """Orchestration configuration."""
    max_context_tokens: int = 4000
    default_strategy: str = "clarity"
    enable_multiple_providers: bool = False
    enable_caching: bool = True
    cache_ttl: int = 3600
    quality_threshold: float = 0.3
    enable_metrics: bool = True


class ConfigManager:
    """Comprehensive configuration management."""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir or self._get_default_config_dir())
        self.config_schema = self._load_config_schema()
        self._config_cache = {}
        
    def load_config(
        self,
        config_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """Load and validate configuration."""
        if config_file is None:
            config_file = self.config_dir / "config.yaml"
        else:
            config_file = Path(config_file)
        
        # Check cache
        cache_key = str(config_file)
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        try:
            # Load configuration file
            config = self._load_config_file(config_file)
            
            # Merge with defaults
            config = self._merge_with_defaults(config)
            
            # Validate against schema
            self._validate_config(config)
            
            # Process environment variables
            config = self._process_env_vars(config)
            
            # Cache the result
            self._config_cache[cache_key] = config
            
            logger.info(f"Configuration loaded from {config_file}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def get_provider_configs(
        self,
        config: Dict[str, Any]
    ) -> List[ProviderConfig]:
        """Extract provider configurations."""
        providers = []
        
        for provider_data in config.get('llm_providers', []):
            try:
                provider_config = ProviderConfig.from_dict(provider_data)
                if provider_config.enabled:
                    providers.append(provider_config)
            except Exception as e:
                logger.error(f"Invalid provider config: {e}")
        
        return providers
    
    def get_security_config(
        self,
        config: Dict[str, Any]
    ) -> SecurityConfig:
        """Extract security configuration."""
        security_data = config.get('security', {})
        return SecurityConfig(**security_data)
    
    def get_orchestration_config(
        self,
        config: Dict[str, Any]
    ) -> OrchestrationConfig:
        """Extract orchestration configuration."""
        orchestration_data = config.get('orchestration', {})
        return OrchestrationConfig(**orchestration_data)
    
    def save_config(
        self,
        config: Dict[str, Any],
        config_file: Optional[str] = None
    ) -> None:
        """Save configuration to file."""
        if config_file is None:
            config_file = self.config_dir / "config.yaml"
        else:
            config_file = Path(config_file)
        
        try:
            # Validate before saving
            self._validate_config(config)
            
            # Ensure directory exists
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save configuration
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
            
            # Clear cache
            cache_key = str(config_file)
            if cache_key in self._config_cache:
                del self._config_cache[cache_key]
            
            logger.info(f"Configuration saved to {config_file}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise
    
    def _load_config_file(self, config_file: Path) -> Dict[str, Any]:
        """Load configuration from file."""
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            if config_file.suffix.lower() == '.json':
                return json.load(f)
            elif config_file.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(f) or {}
            else:
                raise ValueError(f"Unsupported config format: {config_file.suffix}")
    
    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge configuration with defaults."""
        defaults = self._get_default_config()
        
        def deep_merge(base: Dict, override: Dict) -> Dict:
            result = base.copy()
            for key, value in override.items():
                if (key in result and 
                    isinstance(result[key], dict) and 
                    isinstance(value, dict)):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        return deep_merge(defaults, config)
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration against schema."""
        try:
            jsonschema.validate(config, self.config_schema)
        except jsonschema.ValidationError as e:
            raise ValueError(f"Configuration validation failed: {e.message}")
    
    def _process_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process environment variable substitutions."""
        def substitute_env_vars(obj):
            if isinstance(obj, dict):
                return {k: substitute_env_vars(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [substitute_env_vars(item) for item in obj]
            elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
                env_var = obj[2:-1]
                default_value = None
                
                if ':' in env_var:
                    env_var, default_value = env_var.split(':', 1)
                
                return os.getenv(env_var, default_value)
            else:
                return obj
        
        return substitute_env_vars(config)
    
    def _get_default_config_dir(self) -> str:
        """Get default configuration directory."""
        return os.path.dirname(__file__) + "/config"
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            'llm_providers': [],
            'security': {
                'enable_auth': True,
                'enable_encryption': True,
                'session_timeout': 3600,
                'max_requests_per_hour': 100,
                'max_prompt_length': 10000,
                'max_context_size': 50000,
                'required_permission': 'llm_access',
                'min_security_level': 1,
                'gdpr_enabled': False,
                'hipaa_enabled': False,
                'blocked_patterns': [],
                'compliance_rules': []
            },
            'orchestration': {
                'max_context_tokens': 4000,
                'default_strategy': 'clarity',
                'enable_multiple_providers': False,
                'enable_caching': True,
                'cache_ttl': 3600,
                'quality_threshold': 0.3,
                'enable_metrics': True
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'llm_abstraction.log'
            }
        }
    
    def _load_config_schema(self) -> Dict[str, Any]:
        """Load configuration validation schema."""
        return {
            "type": "object",
            "properties": {
                "llm_providers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "endpoint": {"type": "string"},
                            "api_key": {"type": "string"},
                            "model": {"type": "string"},
                            "rate_limit": {"type": "integer", "minimum": 1},
                            "timeout": {"type": "integer", "minimum": 1},
                            "max_retries": {"type": "integer", "minimum": 0},
                            "enabled": {"type": "boolean"}
                        },
                        "required": ["name", "type", "endpoint", "api_key"]
                    }
                },
                "security": {
                    "type": "object",
                    "properties": {
                        "enable_auth": {"type": "boolean"},
                        "enable_encryption": {"type": "boolean"},
                        "session_timeout": {"type": "integer", "minimum": 60},
                        "max_requests_per_hour": {"type": "integer", "minimum": 1},
                        "max_prompt_length": {"type": "integer", "minimum": 1},
                        "max_context_size": {"type": "integer", "minimum": 1},
                        "required_permission": {"type": "string"},
                        "min_security_level": {"type": "integer", "minimum": 1},
                        "gdpr_enabled": {"type": "boolean"},
                        "hipaa_enabled": {"type": "boolean"},
                        "blocked_patterns": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "compliance_rules": {
                            "type": "array",
                            "items": {"type": "object"}
                        }
                    }
                },
                "orchestration": {
                    "type": "object",
                    "properties": {
                        "max_context_tokens": {"type": "integer", "minimum": 100},
                        "default_strategy": {"type": "string"},
                        "enable_multiple_providers": {"type": "boolean"},
                        "enable_caching": {"type": "boolean"},
                        "cache_ttl": {"type": "integer", "minimum": 0},
                        "quality_threshold": {"type": "number", "minimum": 0, "maximum": 1},
                        "enable_metrics": {"type": "boolean"}
                    }
                }
            }
        }


class EnvironmentManager:
    """Manage different deployment environments."""
    
    def __init__(self):
        self.environment = os.getenv('LLM_ENV', 'development')
        self.environments = {
            'development': self._get_dev_config,
            'staging': self._get_staging_config,
            'production': self._get_prod_config
        }
    
    def get_environment_config(self) -> Dict[str, Any]:
        """Get configuration for current environment."""
        if self.environment not in self.environments:
            raise ValueError(f"Unknown environment: {self.environment}")
        
        return self.environments[self.environment]()
    
    def _get_dev_config(self) -> Dict[str, Any]:
        """Development environment configuration."""
        return {
            'security': {
                'enable_auth': False,
                'enable_encryption': False,
                'max_requests_per_hour': 1000
            },
            'orchestration': {
                'enable_caching': False,
                'enable_metrics': True
            },
            'logging': {
                'level': 'DEBUG'
            }
        }
    
    def _get_staging_config(self) -> Dict[str, Any]:
        """Staging environment configuration."""
        return {
            'security': {
                'enable_auth': True,
                'enable_encryption': True,
                'max_requests_per_hour': 500
            },
            'orchestration': {
                'enable_caching': True,
                'enable_metrics': True
            },
            'logging': {
                'level': 'INFO'
            }
        }
    
    def _get_prod_config(self) -> Dict[str, Any]:
        """Production environment configuration."""
        return {
            'security': {
                'enable_auth': True,
                'enable_encryption': True,
                'max_requests_per_hour': 100,
                'gdpr_enabled': True,
                'hipaa_enabled': True
            },
            'orchestration': {
                'enable_caching': True,
                'enable_metrics': True,
                'quality_threshold': 0.5
            },
            'logging': {
                'level': 'WARNING'
            }
        }


def create_sample_config() -> Dict[str, Any]:
    """Create a sample configuration for testing."""
    return {
        'llm_providers': [
            {
                'name': 'openai',
                'type': 'openai',
                'endpoint': 'https://api.openai.com/v1',
                'api_key': '${OPENAI_API_KEY}',
                'model': 'gpt-3.5-turbo',
                'rate_limit': 60,
                'timeout': 30,
                'max_retries': 3,
                'enabled': True
            },
            {
                'name': 'anthropic',
                'type': 'anthropic',
                'endpoint': 'https://api.anthropic.com/v1',
                'api_key': '${ANTHROPIC_API_KEY}',
                'model': 'claude-3-sonnet-20240229',
                'rate_limit': 50,
                'timeout': 30,
                'max_retries': 3,
                'enabled': True
            }
        ],
        'security': {
            'enable_auth': True,
            'enable_encryption': True,
            'session_timeout': 3600,
            'max_requests_per_hour': 100,
            'max_prompt_length': 10000,
            'max_context_size': 50000,
            'required_permission': 'llm_access',
            'min_security_level': 2,
            'gdpr_enabled': True,
            'hipaa_enabled': False,
            'blocked_patterns': [
                'ignore previous instructions',
                'jailbreak',
                'prompt injection'
            ],
            'compliance_rules': [
                {
                    'name': 'no_personal_data',
                    'pattern': r'ssn|social security|credit card',
                    'description': 'Prevent personal data exposure'
                }
            ]
        },
        'orchestration': {
            'max_context_tokens': 4000,
            'default_strategy': 'clarity',
            'enable_multiple_providers': True,
            'enable_caching': True,
            'cache_ttl': 3600,
            'quality_threshold': 0.4,
            'enable_metrics': True
        },
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file': 'llm_abstraction.log'
        }
    }


class LLMConfigManager:
    """Centralized config manager for LLM abstraction."""
    def __init__(self, config_path: str = CONFIG_PATH):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def get_active_provider(self) -> str:
        return self.config.get('active_provider')

    def get_provider_config(self) -> Dict[str, Any]:
        provider = self.get_active_provider()
        providers = self.config.get('providers', {})
        if provider not in providers:
            raise ValueError(f"Provider '{provider}' not found in config.")
        return providers[provider]

    def get_vector_db_config(self) -> Dict[str, Any]:
        return self.config.get('vector_db', {})

    def get_rag_config(self) -> Dict[str, Any]:
        return self.config.get('rag', {})
