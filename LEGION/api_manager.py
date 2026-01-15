import requests
import time
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import json
import os
from rate_limiter import rate_limiter, APICallPriority, RateLimitConfig

class EnterpriseAPIManager:
    """Enhanced API manager with intelligent rate limiting and fallback mechanisms"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Enterprise-System/1.0',
            'Accept': 'application/json'
        })
        
        # Load API keys and configurations
        self._load_api_credentials()
        
        # Initialize rate limiting configurations
        self._configure_rate_limits()
    
    def _load_api_credentials(self):
        """Load API credentials from environment and config files"""
        self.api_credentials = {
            'coingecko': {
                'base_url': 'https://api.coingecko.com/api/v3',
                'api_key': os.getenv('COINGECKO_API_KEY'),
                'headers': {}
            },
            'newsapi': {
                'base_url': 'https://newsapi.org/v2',
                'api_key': os.getenv('NEWSAPI_KEY'),
                'headers': {'X-API-Key': os.getenv('NEWSAPI_KEY')} if os.getenv('NEWSAPI_KEY') else {}
            },
            'openai': {
                'base_url': 'https://api.openai.com/v1',
                'api_key': os.getenv('OPENAI_API_KEY'),
                'headers': {'Authorization': f"Bearer {os.getenv('OPENAI_API_KEY')}"} if os.getenv('OPENAI_API_KEY') else {}
            }
        }
    
    def _configure_rate_limits(self):
        """Configure rate limits for different APIs"""
        # Configure CoinGecko - Conservative rate limiting
        rate_limiter.update_config('coingecko', RateLimitConfig(
            requests_per_minute=10,  # 10 requests per minute
            burst_limit=3,
            retry_attempts=3
        ))
        
        # Configure News API - Very conservative
        rate_limiter.update_config('newsapi', RateLimitConfig(
            requests_per_minute=1,   # 1 request per minute
            burst_limit=1,
            retry_attempts=2
        ))
        
        # Configure OpenAI - Ultra conservative
        rate_limiter.update_config('openai', RateLimitConfig(
            requests_per_minute=1,   # 1 request per minute
            burst_limit=1,
            retry_attempts=2
        ))
        
        # Default for any other APIs
        rate_limiter.update_config('default', RateLimitConfig(
            requests_per_minute=1,   # 1 request per minute default
            burst_limit=2,
            retry_attempts=3
        ))
    
    async def make_api_call(self, 
                           api_name: str, 
                           endpoint: str, 
                           method: str = 'GET',
                           params: Optional[Dict[str, Any]] = None,
                           data: Optional[Dict[str, Any]] = None,
                           priority: APICallPriority = APICallPriority.MEDIUM,
                           use_fallback: bool = True) -> Dict[str, Any]:
        """Make rate-limited API call with intelligent fallback"""
        
        # Check if we can make the request
        if not rate_limiter.can_make_request(api_name):
            self.logger.info(f"Rate limit hit for {api_name}, checking fallback options")
            rate_limiter.record_rate_limit(api_name)
            
            if use_fallback:
                fallback_data = rate_limiter.get_fallback_data(api_name, endpoint.split('/')[-1])
                if fallback_data:
                    self.logger.info(f"Using fallback data for {api_name}/{endpoint}")
                    return {
                        'success': True,
                        'data': fallback_data['data'],
                        'source': 'fallback',
                        'timestamp': fallback_data['timestamp']
                    }
            
            return {
                'success': False,
                'error': 'Rate limit exceeded and no fallback available',
                'retry_after': self._calculate_retry_delay(api_name)
            }
        
        # Make the actual API call
        try:
            start_time = time.time()
            
            # Get API configuration
            api_config = self.api_credentials.get(api_name)
            if not api_config:
                raise ValueError(f"Unknown API: {api_name}")
            
            # Construct URL
            url = f"{api_config['base_url']}/{endpoint.lstrip('/')}"
            
            # Prepare headers
            headers = api_config.get('headers', {}).copy()
            headers.update(self.session.headers)
            
            # Add API key to params if needed and not in headers
            if api_config.get('api_key') and 'Authorization' not in headers and 'X-API-Key' not in headers:
                if params is None:
                    params = {}
                params['api_key'] = api_config['api_key']
            
            # Make the request
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Record successful request
                rate_limiter.record_request(api_name, success=True, response_time=response_time)
                
                # Save as fallback data
                rate_limiter.save_fallback_data(api_name, endpoint.split('/')[-1], response_data)
                
                return {
                    'success': True,
                    'data': response_data,
                    'source': 'api',
                    'response_time': response_time,
                    'timestamp': datetime.now().isoformat()
                }
            
            elif response.status_code == 429:  # Rate limited by API
                self.logger.warning(f"API rate limit hit for {api_name}")
                rate_limiter.record_rate_limit(api_name)
                
                if use_fallback:
                    fallback_data = rate_limiter.get_fallback_data(api_name, endpoint.split('/')[-1])
                    if fallback_data:
                        return {
                            'success': True,
                            'data': fallback_data['data'],
                            'source': 'fallback_after_rate_limit',
                            'timestamp': fallback_data['timestamp']
                        }
                
                return {
                    'success': False,
                    'error': 'API rate limit exceeded',
                    'status_code': 429,
                    'retry_after': response.headers.get('Retry-After', 60)
                }
            
            else:
                rate_limiter.record_request(api_name, success=False, response_time=response_time)
                
                return {
                    'success': False,
                    'error': f"API error: {response.status_code}",
                    'status_code': response.status_code,
                    'response': response.text
                }
        
        except requests.exceptions.Timeout:
            rate_limiter.record_request(api_name, success=False)
            
            if use_fallback:
                fallback_data = rate_limiter.get_fallback_data(api_name, endpoint.split('/')[-1])
                if fallback_data:
                    return {
                        'success': True,
                        'data': fallback_data['data'],
                        'source': 'fallback_after_timeout',
                        'timestamp': fallback_data['timestamp']
                    }
            
            return {
                'success': False,
                'error': 'Request timeout',
                'retry_suggested': True
            }
        
        except Exception as e:
            self.logger.error(f"API call failed for {api_name}/{endpoint}: {e}")
            rate_limiter.record_request(api_name, success=False)
            
            if use_fallback:
                fallback_data = rate_limiter.get_fallback_data(api_name, endpoint.split('/')[-1])
                if fallback_data:
                    return {
                        'success': True,
                        'data': fallback_data['data'],
                        'source': 'fallback_after_error',
                        'timestamp': fallback_data['timestamp']
                    }
            
            return {
                'success': False,
                'error': str(e),
                'retry_suggested': True
            }
    
    def _calculate_retry_delay(self, api_name: str) -> int:
        """Calculate appropriate retry delay for rate-limited API"""
        config = rate_limiter.api_configs.get(api_name, rate_limiter.api_configs['default'])
        base_delay = 60 // config.requests_per_minute  # Seconds between requests
        return max(base_delay, 60)  # At least 1 minute
    
    def queue_api_call(self, 
                      api_name: str, 
                      endpoint: str, 
                      callback: Callable,
                      priority: APICallPriority = APICallPriority.MEDIUM,
                      **kwargs):
        """Queue an API call for later execution"""
        request_data = {
            'api_name': api_name,
            'endpoint': endpoint,
            'callback': callback,
            **kwargs
        }
        rate_limiter.queue_request(api_name, request_data, priority)
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get comprehensive API status and usage statistics"""
        stats = rate_limiter.get_usage_stats()
        queue_status = rate_limiter.get_queue_status()
        
        api_status = {}
        for api_name in self.api_credentials.keys():
            api_stats = stats.get(api_name, {})
            
            # Calculate health score
            total_requests = api_stats.get('total_requests', 0)
            successful_requests = api_stats.get('successful_requests', 0)
            
            if total_requests > 0:
                success_rate = (successful_requests / total_requests) * 100
                health_score = min(100, success_rate)
            else:
                health_score = 100  # No requests yet, assume healthy
            
            # Determine status
            if health_score >= 90:
                status = 'operational'
            elif health_score >= 70:
                status = 'degraded'
            else:
                status = 'critical'
            
            api_status[api_name] = {
                'status': status,
                'health_score': round(health_score, 1),
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'failed_requests': api_stats.get('failed_requests', 0),
                'rate_limited_requests': api_stats.get('rate_limited_requests', 0),
                'average_response_time': round(api_stats.get('average_response_time', 0), 2),
                'last_request': api_stats.get('last_request_time'),
                'can_make_request': rate_limiter.can_make_request(api_name),
                'predicted_quota_usage': round(rate_limiter.predict_quota_usage(api_name), 1)
            }
        
        return {
            'apis': api_status,
            'queue': queue_status,
            'overall_health': self._calculate_overall_health(api_status)
        }
    
    def _calculate_overall_health(self, api_status: Dict[str, Dict[str, Any]]) -> str:
        """Calculate overall API health status"""
        if not api_status:
            return 'unknown'
        
        operational_count = sum(1 for api in api_status.values() if api['status'] == 'operational')
        total_apis = len(api_status)
        
        operational_percentage = (operational_count / total_apis) * 100
        
        if operational_percentage >= 90:
            return 'operational'
        elif operational_percentage >= 70:
            return 'degraded'
        else:
            return 'critical'

# Convenience functions for common API calls
class CryptoAPI:
    """Cryptocurrency data API wrapper"""
    
    def __init__(self, api_manager: EnterpriseAPIManager):
        self.api_manager = api_manager
    
    async def get_price_data(self, symbols: str = 'bitcoin,ethereum') -> Dict[str, Any]:
        """Get cryptocurrency price data"""
        return await self.api_manager.make_api_call(
            api_name='coingecko',
            endpoint='simple/price',
            params={
                'ids': symbols,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true'
            },
            priority=APICallPriority.HIGH
        )
    
    async def get_market_data(self, limit: int = 10) -> Dict[str, Any]:
        """Get cryptocurrency market data"""
        return await self.api_manager.make_api_call(
            api_name='coingecko',
            endpoint='coins/markets',
            params={
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1
            },
            priority=APICallPriority.MEDIUM
        )

class NewsAPI:
    """News data API wrapper"""
    
    def __init__(self, api_manager: EnterpriseAPIManager):
        self.api_manager = api_manager
    
    async def get_headlines(self, category: str = 'business', country: str = 'us') -> Dict[str, Any]:
        """Get news headlines"""
        return await self.api_manager.make_api_call(
            api_name='newsapi',
            endpoint='top-headlines',
            params={
                'category': category,
                'country': country,
                'pageSize': 10
            },
            priority=APICallPriority.LOW
        )
    
    async def search_news(self, query: str, language: str = 'en') -> Dict[str, Any]:
        """Search for news articles"""
        return await self.api_manager.make_api_call(
            api_name='newsapi',
            endpoint='everything',
            params={
                'q': query,
                'language': language,
                'sortBy': 'publishedAt',
                'pageSize': 5
            },
            priority=APICallPriority.LOW
        )

# Global API manager instance
api_manager = EnterpriseAPIManager()
crypto_api = CryptoAPI(api_manager)
news_api = NewsAPI(api_manager)
