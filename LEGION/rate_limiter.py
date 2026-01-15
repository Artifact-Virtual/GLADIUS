import time
import asyncio
import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Callable
import threading
from enum import Enum
import json
import os

class RateLimitStrategy(Enum):
    """Rate limiting strategies"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    EXPONENTIAL_BACKOFF = "exponential_backoff"

class APICallPriority(Enum):
    """API call priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium" 
    LOW = "low"

class RateLimitConfig:
    """Configuration for rate limiting"""
    def __init__(self, 
                 requests_per_minute: int = 1,
                 burst_limit: int = 3,
                 strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW,
                 backoff_factor: float = 2.0,
                 max_backoff: int = 300,
                 retry_attempts: int = 3):
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.strategy = strategy
        self.backoff_factor = backoff_factor
        self.max_backoff = max_backoff
        self.retry_attempts = retry_attempts

class APIRequestQueue:
    """Queue for managing API requests with priority"""
    def __init__(self):
        self.queues = {
            APICallPriority.CRITICAL: deque(),
            APICallPriority.HIGH: deque(),
            APICallPriority.MEDIUM: deque(),
            APICallPriority.LOW: deque()
        }
        self.lock = threading.Lock()
    
    def enqueue(self, request: Dict[str, Any], priority: APICallPriority = APICallPriority.MEDIUM):
        """Add request to appropriate priority queue"""
        with self.lock:
            self.queues[priority].append({
                'request': request,
                'timestamp': datetime.now(),
                'priority': priority,
                'retry_count': 0
            })
    
    def dequeue(self) -> Optional[Dict[str, Any]]:
        """Get next request from highest priority queue"""
        with self.lock:
            for priority in APICallPriority:
                if self.queues[priority]:
                    return self.queues[priority].popleft()
            return None
    
    def size(self) -> Dict[APICallPriority, int]:
        """Get queue sizes by priority"""
        with self.lock:
            return {priority: len(queue) for priority, queue in self.queues.items()}

class IntelligentRateLimiter:
    """Intelligent rate limiting with multiple strategies and monitoring"""
    
    def __init__(self, config_file: str = "config/rate_limits.json"):
        self.config_file = config_file
        self.api_configs: Dict[str, RateLimitConfig] = {}
        self.request_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.token_buckets: Dict[str, Dict[str, Any]] = {}
        self.backoff_delays: Dict[str, float] = {}
        self.request_queue = APIRequestQueue()
        self.usage_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'rate_limited_requests': 0,
            'average_response_time': 0.0,
            'last_request_time': None,
            'quota_usage': 0.0
        })
        
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock()
        self._load_configs()
        self._start_background_processor()
    
    def _load_configs(self):
        """Load rate limiting configurations from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    configs = json.load(f)
                    for api_name, config_data in configs.items():
                        self.api_configs[api_name] = RateLimitConfig(**config_data)
            else:
                # Default configurations for common APIs
                self._create_default_configs()
        except Exception as e:
            self.logger.error(f"Failed to load rate limit configs: {e}")
            self._create_default_configs()
    
    def _create_default_configs(self):
        """Create default rate limiting configurations"""
        default_configs = {
            'coingecko': RateLimitConfig(
                requests_per_minute=10,
                burst_limit=3,
                strategy=RateLimitStrategy.SLIDING_WINDOW
            ),
            'newsapi': RateLimitConfig(
                requests_per_minute=1,
                burst_limit=2,
                strategy=RateLimitStrategy.TOKEN_BUCKET
            ),
            'openai': RateLimitConfig(
                requests_per_minute=3,
                burst_limit=1,
                strategy=RateLimitStrategy.EXPONENTIAL_BACKOFF,
                backoff_factor=2.0,
                max_backoff=300
            ),
            'default': RateLimitConfig(
                requests_per_minute=1,
                burst_limit=2,
                strategy=RateLimitStrategy.SLIDING_WINDOW
            )
        }
        
        self.api_configs.update(default_configs)
        self._save_configs()
    
    def _save_configs(self):
        """Save rate limiting configurations to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            configs_dict = {}
            for api_name, config in self.api_configs.items():
                # Handle strategy - convert enum to string value for JSON serialization
                if isinstance(config.strategy, RateLimitStrategy):
                    strategy_value = config.strategy.value
                elif isinstance(config.strategy, str):
                    strategy_value = config.strategy
                else:
                    strategy_value = str(config.strategy)
                
                configs_dict[api_name] = {
                    'requests_per_minute': config.requests_per_minute,
                    'burst_limit': config.burst_limit,
                    'strategy': strategy_value,
                    'backoff_factor': config.backoff_factor,
                    'max_backoff': config.max_backoff,
                    'retry_attempts': config.retry_attempts
                }
            
            with open(self.config_file, 'w') as f:
                json.dump(configs_dict, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save rate limit configs: {e}")
    
    def _start_background_processor(self):
        """Start background thread to process queued requests"""
        def processor():
            while True:
                try:
                    request_item = self.request_queue.dequeue()
                    if request_item:
                        self._process_queued_request(request_item)
                    else:
                        time.sleep(0.1)  # Short sleep when queue is empty
                except Exception as e:
                    self.logger.error(f"Error in background processor: {e}")
                    time.sleep(1)
        
        processor_thread = threading.Thread(target=processor, daemon=True)
        processor_thread.start()
    
    def _process_queued_request(self, request_item: Dict[str, Any]):
        """Process a queued request"""
        try:
            request_data = request_item['request']
            api_name = request_data.get('api_name', 'default')
            
            if self.can_make_request(api_name):
                # Execute the request
                callback = request_data.get('callback')
                if callback:
                    callback(request_data)
            else:
                # Re-queue with increased retry count
                request_item['retry_count'] += 1
                max_retries = self.api_configs.get(api_name, self.api_configs['default']).retry_attempts
                
                if request_item['retry_count'] < max_retries:
                    self.request_queue.enqueue(
                        request_data, 
                        request_item['priority']
                    )
                else:
                    self.logger.warning(f"Request for {api_name} exceeded max retries")
                    self.usage_stats[api_name]['failed_requests'] += 1
        except Exception as e:
            self.logger.error(f"Error processing queued request: {e}")
    
    def can_make_request(self, api_name: str) -> bool:
        """Check if a request can be made based on rate limiting rules"""
        config = self.api_configs.get(api_name, self.api_configs['default'])
        current_time = datetime.now()
        
        with self.lock:
            if config.strategy == RateLimitStrategy.SLIDING_WINDOW:
                return self._check_sliding_window(api_name, config, current_time)
            elif config.strategy == RateLimitStrategy.TOKEN_BUCKET:
                return self._check_token_bucket(api_name, config, current_time)
            elif config.strategy == RateLimitStrategy.EXPONENTIAL_BACKOFF:
                return self._check_exponential_backoff(api_name, config, current_time)
            else:
                return self._check_fixed_window(api_name, config, current_time)
    
    def _check_sliding_window(self, api_name: str, config: RateLimitConfig, current_time: datetime) -> bool:
        """Check sliding window rate limit"""
        history = self.request_history[api_name]
        window_start = current_time - timedelta(minutes=1)
        
        # Remove old requests outside the window
        while history and history[0] < window_start:
            history.popleft()
        
        return len(history) < config.requests_per_minute
    
    def _check_token_bucket(self, api_name: str, config: RateLimitConfig, current_time: datetime) -> bool:
        """Check token bucket rate limit"""
        if api_name not in self.token_buckets:
            self.token_buckets[api_name] = {
                'tokens': config.burst_limit,
                'last_refill': current_time
            }
        
        bucket = self.token_buckets[api_name]
        
        # Refill tokens based on time elapsed
        time_elapsed = (current_time - bucket['last_refill']).total_seconds()
        tokens_to_add = (time_elapsed / 60) * config.requests_per_minute
        bucket['tokens'] = min(config.burst_limit, bucket['tokens'] + tokens_to_add)
        bucket['last_refill'] = current_time
        
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            return True
        
        return False
    
    def _check_exponential_backoff(self, api_name: str, config: RateLimitConfig, current_time: datetime) -> bool:
        """Check exponential backoff rate limit"""
        if api_name in self.backoff_delays:
            last_request = self.usage_stats[api_name].get('last_request_time')
            if last_request:
                time_since_last = (current_time - last_request).total_seconds()
                if time_since_last < self.backoff_delays[api_name]:
                    return False
        
        return True
    
    def _check_fixed_window(self, api_name: str, config: RateLimitConfig, current_time: datetime) -> bool:
        """Check fixed window rate limit"""
        history = self.request_history[api_name]
        window_start = current_time.replace(second=0, microsecond=0)
        
        # Count requests in current minute
        requests_in_window = sum(1 for req_time in history if req_time >= window_start)
        
        return requests_in_window < config.requests_per_minute
    
    def record_request(self, api_name: str, success: bool = True, response_time: float = 0.0):
        """Record a completed request"""
        current_time = datetime.now()
        
        with self.lock:
            self.request_history[api_name].append(current_time)
            
            stats = self.usage_stats[api_name]
            stats['total_requests'] += 1
            stats['last_request_time'] = current_time
            
            if success:
                stats['successful_requests'] += 1
                # Update average response time
                total_successful = stats['successful_requests']
                current_avg = stats['average_response_time']
                stats['average_response_time'] = ((current_avg * (total_successful - 1)) + response_time) / total_successful
            else:
                stats['failed_requests'] += 1
                # Increase backoff delay for exponential backoff strategy
                config = self.api_configs.get(api_name, self.api_configs['default'])
                if config.strategy == RateLimitStrategy.EXPONENTIAL_BACKOFF:
                    current_delay = self.backoff_delays.get(api_name, 1.0)
                    self.backoff_delays[api_name] = min(
                        config.max_backoff,
                        current_delay * config.backoff_factor
                    )
    
    def record_rate_limit(self, api_name: str):
        """Record when a request was rate limited"""
        with self.lock:
            self.usage_stats[api_name]['rate_limited_requests'] += 1
    
    def queue_request(self, api_name: str, request_data: Dict[str, Any], 
                     priority: APICallPriority = APICallPriority.MEDIUM,
                     callback: Optional[Callable] = None):
        """Queue a request for later execution"""
        request_item = {
            'api_name': api_name,
            'data': request_data,
            'callback': callback
        }
        self.request_queue.enqueue(request_item, priority)
    
    def get_usage_stats(self, api_name: Optional[str] = None) -> Dict[str, Any]:
        """Get usage statistics for APIs"""
        if api_name:
            return self.usage_stats.get(api_name, {})
        return dict(self.usage_stats)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        queue_sizes = self.request_queue.size()
        return {
            'total_queued': sum(queue_sizes.values()),
            'by_priority': {priority.value: size for priority, size in queue_sizes.items()}
        }
    
    def predict_quota_usage(self, api_name: str, hours_ahead: int = 24) -> float:
        """Predict API quota usage for the next period"""
        stats = self.usage_stats.get(api_name, {})
        total_requests = stats.get('total_requests', 0)
        
        if not total_requests:
            return 0.0
        
        # Simple prediction based on current rate
        current_time = datetime.now()
        last_request = stats.get('last_request_time')
        
        if not last_request:
            return 0.0
        
        time_since_last = (current_time - last_request).total_seconds() / 3600  # hours
        if time_since_last > 0:
            requests_per_hour = total_requests / max(time_since_last, 1)
            predicted_requests = requests_per_hour * hours_ahead
            
            # Convert to percentage if we know the quota limit
            config = self.api_configs.get(api_name, self.api_configs['default'])
            hourly_limit = config.requests_per_minute * 60
            daily_limit = hourly_limit * 24
            
            return min(100.0, (predicted_requests / daily_limit) * 100)
        
        return 0.0
    
    def update_config(self, api_name: str, config: RateLimitConfig):
        """Update rate limiting configuration for an API"""
        self.api_configs[api_name] = config
        self._save_configs()
    
    def get_fallback_data(self, api_name: str, data_type: str) -> Optional[Dict[str, Any]]:
        """Get fallback data for when API is unavailable"""
        fallback_file = f"data/fallback_{api_name}_{data_type}.json"
        
        try:
            if os.path.exists(fallback_file):
                with open(fallback_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load fallback data: {e}")
        
        return None
    
    def save_fallback_data(self, api_name: str, data_type: str, data: Dict[str, Any]):
        """Save successful API response as fallback data"""
        try:
            os.makedirs("data", exist_ok=True)
            fallback_file = f"data/fallback_{api_name}_{data_type}.json"
            
            with open(fallback_file, 'w') as f:
                json.dump({
                    'data': data,
                    'timestamp': datetime.now().isoformat(),
                    'source': f'{api_name}_api'
                }, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save fallback data: {e}")

# Global rate limiter instance
rate_limiter = IntelligentRateLimiter()
