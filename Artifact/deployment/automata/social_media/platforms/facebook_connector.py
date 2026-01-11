"""
Facebook Connector - Social networking platform integration.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import aiohttp

from ..base_platform import SocialPlatform


class FacebookConnector(SocialPlatform):
    """Facebook integration connector."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.page_id = config.get('page_id') or os.getenv('FACEBOOK_PAGE_ID')
        self.access_token = config.get('access_token') or os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.app_id = config.get('app_id') or os.getenv('FACEBOOK_APP_ID')
        self.app_secret = config.get('app_secret') or os.getenv('FACEBOOK_APP_SECRET')
        
        self.api_base = "https://graph.facebook.com/v18.0"
        self.authenticated = False
        self.logger = logging.getLogger(__name__)
    
    async def authenticate(self) -> bool:
        if self.access_token:
            self.authenticated = True
            return True
        return False
    
    async def post_content(self, content: str, media_urls: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        if not self.authenticated:
            await self.authenticate()
        
        url = f"{self.api_base}/{self.page_id}/feed"
        params = {
            'message': content,
            'access_token': self.access_token
        }
        
        if media_urls:
            # For images, use photos endpoint
            url = f"{self.api_base}/{self.page_id}/photos"
            params['url'] = media_urls[0]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        post_id = result.get('id', '')
                        
                        return {
                            'id': post_id,
                            'url': f"https://facebook.com/{post_id}",
                            'platform': 'Facebook',
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        }
                    else:
                        raise Exception(f"Facebook API error: {response.status}")
        except Exception as e:
            self.logger.error(f"Failed to post to Facebook: {e}")
            raise
    
    async def delete_post(self, post_id: str) -> bool:
        url = f"{self.api_base}/{post_id}"
        params = {'access_token': self.access_token}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, params=params) as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        url = f"{self.api_base}/{post_id}/insights"
        params = {
            'access_token': self.access_token,
            'metric': 'post_impressions,post_engaged_users,post_reactions_by_type_total'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        return {
                            'post_id': post_id,
                            'platform': 'Facebook',
                            'impressions': 0,
                            'engagement': 0,
                            'reactions': {}
                        }
        except Exception:
            return {}
    
    async def get_account_analytics(self) -> Dict[str, Any]:
        return {
            'platform': 'Facebook',
            'follower_count': 0,
            'page_views': 0,
            'post_reach': 0
        }
    
    async def test_connection(self) -> bool:
        try:
            url = f"{self.api_base}/{self.page_id}"
            params = {'access_token': self.access_token}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    return response.status == 200
        except Exception:
            return False
