"""
Instagram Connector - Visual content platform integration.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import aiohttp

from ..base_platform import SocialPlatform


class InstagramConnector(SocialPlatform):
    """Instagram integration connector (Graph API)."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.account_id = config.get('account_id') or os.getenv('INSTAGRAM_ACCOUNT_ID')
        self.access_token = config.get('access_token') or os.getenv('INSTAGRAM_ACCESS_TOKEN')
        
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
        
        if not media_urls:
            raise ValueError("Instagram requires at least one media URL")
        
        is_reel = kwargs.get('is_reel', False)
        
        # Step 1: Create media container
        container_url = f"{self.api_base}/{self.account_id}/media"
        container_params = {
            'access_token': self.access_token,
            'caption': content
        }
        
        if is_reel:
            container_params['media_type'] = 'REELS'
            container_params['video_url'] = media_urls[0]
        else:
            container_params['image_url'] = media_urls[0]
        
        try:
            async with aiohttp.ClientSession() as session:
                # Create container
                async with session.post(container_url, params=container_params) as response:
                    if response.status == 200:
                        container_data = await response.json()
                        container_id = container_data.get('id')
                        
                        # Step 2: Publish media
                        publish_url = f"{self.api_base}/{self.account_id}/media_publish"
                        publish_params = {
                            'access_token': self.access_token,
                            'creation_id': container_id
                        }
                        
                        async with session.post(publish_url, params=publish_params) as pub_response:
                            if pub_response.status == 200:
                                result = await pub_response.json()
                                media_id = result.get('id')
                                
                                return {
                                    'id': media_id,
                                    'url': f"https://instagram.com/p/{media_id}",
                                    'platform': 'Instagram',
                                    'timestamp': datetime.now(timezone.utc).isoformat()
                                }
                    
                    raise Exception(f"Instagram API error: {response.status}")
        except Exception as e:
            self.logger.error(f"Failed to post to Instagram: {e}")
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
            'metric': 'impressions,reach,engagement,saved,video_views'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        return {
                            'post_id': post_id,
                            'platform': 'Instagram',
                            'impressions': 0,
                            'reach': 0,
                            'engagement': 0
                        }
        except Exception:
            return {}
    
    async def get_account_analytics(self) -> Dict[str, Any]:
        return {
            'platform': 'Instagram',
            'follower_count': 0,
            'profile_views': 0,
            'post_impressions': 0
        }
    
    async def test_connection(self) -> bool:
        try:
            url = f"{self.api_base}/{self.account_id}"
            params = {'access_token': self.access_token}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    return response.status == 200
        except Exception:
            return False
