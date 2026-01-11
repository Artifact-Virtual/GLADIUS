"""
Social Media Manager - Coordinates all social media platform connectors.
"""

import logging
from typing import Dict, List, Any, Optional
import asyncio

from .base_platform import SocialPlatform
from .platforms import *


class SocialMediaManager:
    """
    Manager for all social media platform integrations.
    
    Coordinates posting, analytics, and management across multiple platforms.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize social media manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize platform connectors
        self.platforms: Dict[str, SocialPlatform] = {}
        self._init_platforms()
    
    def _init_platforms(self):
        """Initialize enabled platform connectors."""
        social_config = self.config.get('social_media', {})
        
        # Available platform connectors
        from .platforms import (
            TwitterConnector, 
            LinkedInConnector,
            FacebookConnector,
            InstagramConnector,
            YouTubeConnector
        )
        
        platform_classes = {
            'Twitter/X': TwitterConnector,
            'LinkedIn': LinkedInConnector,
            'Facebook': FacebookConnector,
            'Instagram': InstagramConnector,
            'YouTube': YouTubeConnector,
        }
        
        for platform_name, platform_class in platform_classes.items():
            platform_config = social_config.get(platform_name, {})
            
            if platform_config.get('enabled', False):
                try:
                    connector = platform_class(platform_config)
                    self.platforms[platform_name] = connector
                    self.logger.info(f"Initialized {platform_name} connector")
                except Exception as e:
                    self.logger.error(f"Failed to initialize {platform_name}: {e}")
    
    async def post_content(
        self,
        platform: str,
        content: Dict[str, Any],
        media_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Post content to platform.
        
        Args:
            platform: Platform name
            content: Content dictionary
            media_urls: Optional media URLs
            
        Returns:
            Post result
        """
        if platform not in self.platforms:
            return {
                'success': False,
                'error': f'Platform {platform} not enabled or not found'
            }
        
        connector = self.platforms[platform]
        
        try:
            # Authenticate if needed
            if not connector.authenticated:
                await connector.authenticate()
            
            # Post content
            result = await connector.post_content(
                content=content.get('text', ''),
                media_urls=media_urls
            )
            
            return {
                'success': True,
                'platform': platform,
                'post_id': result.get('id'),
                'url': result.get('url'),
                'data': result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to post to {platform}: {e}")
            return {
                'success': False,
                'platform': platform,
                'error': str(e)
            }
    
    async def get_analytics(
        self,
        platform: Optional[str] = None,
        post_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get analytics.
        
        Args:
            platform: Specific platform (all if None)
            post_id: Specific post (all if None)
            
        Returns:
            Analytics data
        """
        if platform:
            if platform not in self.platforms:
                return {'error': f'Platform {platform} not found'}
            
            connector = self.platforms[platform]
            
            if post_id:
                return await connector.get_post_analytics(post_id)
            else:
                return await connector.get_account_analytics()
        else:
            # Get analytics from all platforms
            all_analytics = {}
            
            for platform_name, connector in self.platforms.items():
                try:
                    analytics = await connector.get_account_analytics()
                    all_analytics[platform_name] = analytics
                except Exception as e:
                    self.logger.error(f"Failed to get analytics for {platform_name}: {e}")
                    all_analytics[platform_name] = {'error': str(e)}
            
            return all_analytics
    
    def get_enabled_platforms(self) -> List[str]:
        """Get list of enabled platforms."""
        return list(self.platforms.keys())
    
    async def test_connection(self, platform: str) -> bool:
        """
        Test platform connection.
        
        Args:
            platform: Platform name
            
        Returns:
            True if connection successful
        """
        if platform not in self.platforms:
            return False
        
        try:
            connector = self.platforms[platform]
            return await connector.test_connection()
        except Exception as e:
            self.logger.error(f"Connection test failed for {platform}: {e}")
            return False
