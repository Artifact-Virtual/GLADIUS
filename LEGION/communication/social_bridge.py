"""
Social Media Bridge for LEGION
==============================

This module provides an abstraction layer for LEGION's social media operations.
It uses Artifact's API-based connectors when available, falling back to 
LEGION's Selenium-based automation when necessary.

Priority Order:
1. Artifact API Connectors (preferred - faster, more reliable)
2. LEGION Selenium Automation (fallback)

Author: Artifact Virtual Systems
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

# Setup paths
GLADIUS_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(GLADIUS_ROOT))

logger = logging.getLogger("LEGION.SocialBridge")


@dataclass
class PostResult:
    """Result from social media post operation"""
    success: bool
    platform: str
    post_id: Optional[str]
    url: Optional[str]
    error: Optional[str]
    method: str  # 'artifact_api' or 'selenium'
    timestamp: datetime


class SocialMediaBridge:
    """
    Unified social media interface for LEGION.
    
    Routes operations through Artifact connectors when available,
    falls back to Selenium automation otherwise.
    """
    
    def __init__(self):
        self._artifact_bridge = None
        self._legacy_service = None
        self._available_platforms = {}
        self._initialize()
    
    def _initialize(self):
        """Initialize available connectors"""
        # Try to load Artifact bridge
        try:
            from legion.artifact_bridge import get_bridge
            self._artifact_bridge = get_bridge()
            logger.info("Artifact bridge loaded for social media")
        except ImportError:
            logger.warning("Artifact bridge not available")
        
        # Check which platforms are available via API
        if self._artifact_bridge:
            for platform in ['discord', 'twitter', 'linkedin', 'facebook', 'instagram']:
                self._available_platforms[platform] = \
                    self._artifact_bridge.available_integrations.get(platform, False)
    
    @property
    def artifact_bridge(self):
        """Get Artifact bridge (lazy load if needed)"""
        if self._artifact_bridge is None:
            try:
                from legion.artifact_bridge import get_bridge
                self._artifact_bridge = get_bridge()
            except ImportError:
                pass
        return self._artifact_bridge
    
    @property
    def legacy_service(self):
        """Get legacy Selenium service (lazy load)"""
        if self._legacy_service is None:
            try:
                from communication.social_media_service import SocialMediaAgent
                self._legacy_service = SocialMediaAgent()
                logger.info("Legacy social media service loaded as fallback")
            except ImportError:
                logger.warning("Legacy social media service not available")
        return self._legacy_service
    
    async def post(
        self,
        platform: str,
        content: str,
        media_urls: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> PostResult:
        """
        Post content to a social media platform.
        
        Automatically routes to the best available method:
        1. Artifact API connector (if available)
        2. Legacy Selenium automation (fallback)
        
        Args:
            platform: Platform name (twitter, linkedin, discord, etc.)
            content: Text content to post
            media_urls: Optional list of media URLs
            metadata: Optional platform-specific metadata
            
        Returns:
            PostResult with success status and details
        """
        platform = platform.lower()
        
        # Try Artifact API connector first
        if self._available_platforms.get(platform) and self.artifact_bridge:
            logger.info(f"Posting to {platform} via Artifact API")
            result = await self.artifact_bridge.post_to_social(
                platform, content, media_urls, metadata
            )
            
            if result.success:
                return PostResult(
                    success=True,
                    platform=platform,
                    post_id=result.data.get('post_id') if result.data else None,
                    url=result.data.get('url') if result.data else None,
                    error=None,
                    method='artifact_api',
                    timestamp=datetime.now()
                )
            else:
                logger.warning(f"Artifact API failed for {platform}: {result.error}")
                # Fall through to legacy method
        
        # Fallback to legacy Selenium service
        if self.legacy_service:
            logger.info(f"Posting to {platform} via legacy Selenium service")
            try:
                result = await self._post_legacy(platform, content, media_urls, metadata)
                return result
            except Exception as e:
                return PostResult(
                    success=False,
                    platform=platform,
                    post_id=None,
                    url=None,
                    error=str(e),
                    method='selenium',
                    timestamp=datetime.now()
                )
        
        # Neither method available
        return PostResult(
            success=False,
            platform=platform,
            post_id=None,
            url=None,
            error=f"No connector available for {platform}",
            method='none',
            timestamp=datetime.now()
        )
    
    async def _post_legacy(
        self,
        platform: str,
        content: str,
        media_urls: Optional[List[str]],
        metadata: Optional[Dict]
    ) -> PostResult:
        """Post using legacy Selenium service"""
        if not self.legacy_service:
            raise RuntimeError("Legacy service not available")
        
        # Map to legacy service methods
        if platform == 'twitter':
            success = await self.legacy_service._post_to_twitter(content)
        elif platform == 'linkedin':
            success = await self.legacy_service._post_to_linkedin(content)
        elif platform == 'facebook':
            success = await self.legacy_service._post_to_facebook(content)
        elif platform == 'instagram':
            success = await self.legacy_service._post_to_instagram(content, media_urls)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
        
        return PostResult(
            success=success,
            platform=platform,
            post_id=None,
            url=None,
            error=None if success else "Post failed",
            method='selenium',
            timestamp=datetime.now()
        )
    
    async def get_engagement(
        self,
        platform: str,
        post_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get engagement metrics for a platform or post"""
        if self.artifact_bridge:
            try:
                # Try Artifact analytics
                from publishing.analytics import get_engagement
                return await get_engagement(platform, post_id)
            except ImportError:
                pass
        
        return {
            "platform": platform,
            "error": "Analytics not available",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_available_platforms(self) -> Dict[str, Dict[str, bool]]:
        """Get available platforms and their methods"""
        platforms = {}
        
        for platform in ['discord', 'twitter', 'linkedin', 'facebook', 'instagram', 'youtube']:
            platforms[platform] = {
                'artifact_api': self._available_platforms.get(platform, False),
                'selenium': self.legacy_service is not None
            }
        
        return platforms
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of social media bridge"""
        return {
            "artifact_bridge_available": self.artifact_bridge is not None,
            "legacy_service_available": self.legacy_service is not None,
            "platforms": self.get_available_platforms(),
            "preferred_method": "artifact_api" if self.artifact_bridge else "selenium",
            "timestamp": datetime.now().isoformat()
        }


# Singleton instance
_bridge_instance: Optional[SocialMediaBridge] = None


def get_social_bridge() -> SocialMediaBridge:
    """Get or create social media bridge instance"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = SocialMediaBridge()
    return _bridge_instance


# Convenience function for LEGION agents
async def post_to_social(
    platform: str,
    content: str,
    media_urls: Optional[List[str]] = None,
    metadata: Optional[Dict] = None
) -> PostResult:
    """
    Post to social media via the unified bridge.
    
    Example:
        result = await post_to_social("twitter", "Hello from LEGION!")
        if result.success:
            print(f"Posted: {result.url}")
    """
    bridge = get_social_bridge()
    return await bridge.post(platform, content, media_urls, metadata)
