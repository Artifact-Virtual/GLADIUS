"""
Base Social Media Platform Connector.

Provides common interface for all social media platforms.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import logging


class ContentType(Enum):
    """Types of social media content."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"
    THREAD = "thread"


class PostStatus(Enum):
    """Status of a post."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"


class SocialPlatform(ABC):
    """
    Abstract base class for social media platform connectors.
    
    Provides common interface for:
    - Authentication
    - Content posting
    - Analytics retrieval
    - Account management
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize platform connector.
        
        Args:
            config: Platform-specific configuration
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.authenticated = False
        self.platform_name = self.__class__.__name__.replace("Connector", "")
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Authenticate with the platform.
        
        Returns:
            True if authenticated successfully
        """
        pass
    
    @abstractmethod
    async def post_content(
        self,
        content: str,
        media_urls: Optional[List[str]] = None,
        content_type: ContentType = ContentType.TEXT,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Post content to the platform.
        
        Args:
            content: Text content
            media_urls: URLs of media files
            content_type: Type of content
            metadata: Additional platform-specific metadata
            
        Returns:
            Post result with ID and status
        """
        pass
    
    @abstractmethod
    async def schedule_post(
        self,
        content: str,
        schedule_time: datetime,
        media_urls: Optional[List[str]] = None,
        content_type: ContentType = ContentType.TEXT,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Schedule content for future posting.
        
        Args:
            content: Text content
            schedule_time: When to post
            media_urls: URLs of media files
            content_type: Type of content
            metadata: Additional metadata
            
        Returns:
            Scheduled post info
        """
        pass
    
    @abstractmethod
    async def delete_post(self, post_id: str) -> bool:
        """
        Delete a post.
        
        Args:
            post_id: Platform-specific post ID
            
        Returns:
            True if deleted successfully
        """
        pass
    
    @abstractmethod
    async def get_analytics(
        self,
        post_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get analytics/insights.
        
        Args:
            post_id: Specific post ID (None for account-level)
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            Analytics data
        """
        pass
    
    @abstractmethod
    async def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information.
        
        Returns:
            Account details
        """
        pass
    
    def is_authenticated(self) -> bool:
        """Check if authenticated."""
        return self.authenticated
    
    def get_platform_name(self) -> str:
        """Get platform name."""
        return self.platform_name
    
    def get_rate_limits(self) -> Dict[str, int]:
        """
        Get platform rate limits.
        
        Returns:
            Rate limit information
        """
        return {
            "posts_per_hour": self.config.get("rate_limit_hour", 10),
            "posts_per_day": self.config.get("max_posts_per_day", 50)
        }
    
    def format_content(
        self,
        content: str,
        max_length: Optional[int] = None,
        hashtags: Optional[List[str]] = None
    ) -> str:
        """
        Format content for platform constraints.
        
        Args:
            content: Original content
            max_length: Maximum character limit
            hashtags: List of hashtags to append
            
        Returns:
            Formatted content
        """
        formatted = content
        
        # Add hashtags if provided
        if hashtags:
            hashtag_str = " " + " ".join(f"#{tag}" for tag in hashtags)
            formatted += hashtag_str
        
        # Truncate if necessary
        if max_length and len(formatted) > max_length:
            formatted = formatted[:max_length-3] + "..."
        
        return formatted
