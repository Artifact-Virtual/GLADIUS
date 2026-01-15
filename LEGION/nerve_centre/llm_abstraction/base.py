import time
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class ProviderType(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"

class SecurityLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class LLMRequest:
    prompt: str
    context: Optional[Dict[str, Any]] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    retry_count: int = 0
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class LLMResponse:
    content: str
    provider: str
    timestamp: float
    tokens_used: Optional[int] = None
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class LLMProviderBase(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('name', 'unknown')
        self.endpoint = config.get('endpoint', '')
        self.api_key = config.get('api_key', '')
        self.rate_limit = config.get('rate_limit', 60)
        self.last_request_time = 0
    @abstractmethod
    def query(self, request: LLMRequest) -> LLMResponse:
        pass
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        pass
    def _rate_limit_check(self) -> None:
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 60 / self.rate_limit
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            logging.info(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()
