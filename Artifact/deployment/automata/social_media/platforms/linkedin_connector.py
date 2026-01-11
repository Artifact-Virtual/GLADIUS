"""
LinkedIn Connector - Professional networking platform integration.

Features:
- OAuth 2.0 authentication
- Post to personal profile and company pages
- Article publishing
- Analytics API
- B2B optimization
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import aiohttp

from ..base_platform import SocialPlatform, ContentType, PostStatus


class LinkedInConnector(SocialPlatform):
    """
    LinkedIn integration connector.
    
    Supports:
    - Text posts
    - Image posts
    - Article publishing
    - Company page posting
    - Analytics
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize LinkedIn connector.
        
        Args:
            config: LinkedIn configuration
        """
        super().__init__(config)
        
        self.client_id = config.get('client_id') or os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = config.get('client_secret') or os.getenv('LINKEDIN_CLIENT_SECRET')
        self.access_token = config.get('access_token') or os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.organization_id = config.get('organization_id') or os.getenv('LINKEDIN_ORGANIZATION_ID')
        
        self.api_base = "https://api.linkedin.com/v2"
        self.authenticated = False
        
        self.logger = logging.getLogger(__name__)
    
    async def authenticate(self) -> bool:
        """Authenticate with LinkedIn OAuth 2.0."""
        if self.access_token:
            self.authenticated = True
            self.logger.info("LinkedIn authenticated with access token")
            return True
        
        # OAuth 2.0 flow would go here
        # For now, assume token is provided in config
        self.logger.warning("No access token provided for LinkedIn")
        return False
    
    async def post_content(
        self,
        content: str,
        media_urls: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post content to LinkedIn.
        
        Args:
            content: Post text
            media_urls: Optional image URLs
            **kwargs: Additional parameters
                - post_to_company: Post to company page instead of personal
                - article_title: If publishing as article
                
        Returns:
            Post result with ID and URL
        """
        if not self.authenticated:
            await self.authenticate()
        
        post_to_company = kwargs.get('post_to_company', False)
        article_title = kwargs.get('article_title')
        
        # Determine author (person or organization)
        if post_to_company and self.organization_id:
            author = f"urn:li:organization:{self.organization_id}"
        else:
            # Get person URN (would need to fetch from profile API)
            author = "urn:li:person:PERSON_ID"  # Placeholder
        
        # Build post payload
        if article_title:
            # Article post
            payload = {
                "author": author,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "ARTICLE",
                        "media": [{
                            "status": "READY",
                            "description": {
                                "text": content
                            },
                            "originalUrl": media_urls[0] if media_urls else "",
                            "title": {
                                "text": article_title
                            }
                        }]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
        elif media_urls:
            # Image post
            payload = {
                "author": author,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "IMAGE",
                        "media": [
                            {
                                "status": "READY",
                                "description": {
                                    "text": content
                                },
                                "media": url,
                                "title": {
                                    "text": "Image"
                                }
                            }
                            for url in media_urls[:9]  # LinkedIn supports up to 9 images
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
        else:
            # Text-only post
            payload = {
                "author": author,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/ugcPosts",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        post_id = result.get('id', '')
                        
                        self.logger.info(f"Posted to LinkedIn: {post_id}")
                        
                        return {
                            'id': post_id,
                            'url': f"https://www.linkedin.com/feed/update/{post_id}",
                            'platform': 'LinkedIn',
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        }
                    else:
                        error_text = await response.text()
                        self.logger.error(f"LinkedIn post failed: {response.status} - {error_text}")
                        raise Exception(f"LinkedIn API error: {response.status}")
        
        except Exception as e:
            self.logger.error(f"Failed to post to LinkedIn: {e}")
            raise
    
    async def delete_post(self, post_id: str) -> bool:
        """Delete a LinkedIn post."""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.api_base}/ugcPosts/{post_id}",
                    headers=headers
                ) as response:
                    return response.status == 204
        except Exception as e:
            self.logger.error(f"Failed to delete LinkedIn post: {e}")
            return False
    
    async def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get analytics for a specific post."""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Get share statistics
                async with session.get(
                    f"{self.api_base}/socialActions/{post_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        return {
                            'post_id': post_id,
                            'likes': data.get('likeCount', 0),
                            'comments': data.get('commentCount', 0),
                            'shares': data.get('shareCount', 0),
                            'clicks': data.get('clickCount', 0),
                            'impressions': data.get('impressionCount', 0),
                            'engagement': data.get('engagementCount', 0),
                            'platform': 'LinkedIn'
                        }
        except Exception as e:
            self.logger.error(f"Failed to get LinkedIn analytics: {e}")
            return {}
    
    async def get_account_analytics(self) -> Dict[str, Any]:
        """Get overall account analytics."""
        # LinkedIn analytics require organization analytics API
        # This is a simplified version
        
        return {
            'platform': 'LinkedIn',
            'follower_count': 0,  # Would fetch from profile API
            'connection_count': 0,
            'profile_views': 0,
            'post_impressions': 0,
            'engagement_rate': 0.0
        }
    
    async def test_connection(self) -> bool:
        """Test LinkedIn API connection."""
        if not self.access_token:
            return False
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/me",
                    headers=headers
                ) as response:
                    return response.status == 200
        except Exception:
            return False
