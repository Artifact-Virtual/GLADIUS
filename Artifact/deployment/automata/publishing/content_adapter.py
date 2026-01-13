"""
Content Adapter - Formats content for each social platform.

Each platform has unique requirements:
- Twitter/X: 280 chars, hashtags, threads
- LinkedIn: Professional tone, B2B focus
- Facebook: Casual, community focus
- Instagram: Visual-first, stories
- YouTube: Video descriptions, SEO
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class AdaptedContent:
    """Content adapted for a specific platform."""
    text: str
    media_urls: List[str]
    hashtags: List[str]
    metadata: Dict[str, Any]


class ContentAdapter:
    """
    Adapts content for each social media platform.
    
    Platform requirements:
    - Twitter/X: 280 char limit, 4 media max, hashtags
    - LinkedIn: 3000 char limit, professional tone
    - Facebook: 63,206 char limit, casual tone
    - Instagram: 2200 char limit, visual required
    - YouTube: SEO-optimized descriptions
    """
    
    PLATFORM_LIMITS = {
        'Twitter/X': {'text': 280, 'media': 4, 'hashtags': 5},
        'LinkedIn': {'text': 3000, 'media': 9, 'hashtags': 5},
        'Facebook': {'text': 63206, 'media': 10, 'hashtags': 10},
        'Instagram': {'text': 2200, 'media': 10, 'hashtags': 30},
        'YouTube': {'text': 5000, 'media': 1, 'hashtags': 15},
    }
    
    def adapt(self, content: Any, platform: str) -> Dict[str, Any]:
        """
        Adapt content for a specific platform.
        
        Args:
            content: PublishableContent object
            platform: Target platform name
            
        Returns:
            Adapted content dictionary
        """
        limits = self.PLATFORM_LIMITS.get(platform, {'text': 280, 'media': 4, 'hashtags': 5})
        
        # Get adaptation method
        adapter_method = getattr(self, f'_adapt_{platform.lower().replace("/", "_")}', self._adapt_generic)
        
        return adapter_method(content, limits)
    
    def _adapt_twitter_x(self, content: Any, limits: Dict) -> Dict[str, Any]:
        """Adapt content for Twitter/X."""
        # Build tweet text
        text = content.summary
        hashtags = content.hashtags[:limits['hashtags']]
        hashtag_text = ' '.join(hashtags)
        
        # Calculate available space
        max_text_length = limits['text'] - len(hashtag_text) - 2  # 2 for spacing
        
        if len(text) > max_text_length:
            text = text[:max_text_length-3] + "..."
        
        final_text = f"{text}\n\n{hashtag_text}"
        
        return {
            'text': final_text,
            'media_urls': content.media_paths[:limits['media']],
            'hashtags': hashtags,
            'metadata': {'platform': 'Twitter/X'}
        }
    
    def _adapt_linkedin(self, content: Any, limits: Dict) -> Dict[str, Any]:
        """Adapt content for LinkedIn (professional tone)."""
        # LinkedIn prefers more detailed, professional content
        title = content.title
        body = content.summary
        hashtags = content.hashtags[:limits['hashtags']]
        
        # Professional formatting
        text = f"📊 {title}\n\n{body}\n\n"
        
        # Add call to action
        text += "What are your thoughts on this analysis?\n\n"
        text += ' '.join(hashtags)
        
        if len(text) > limits['text']:
            text = text[:limits['text']-3] + "..."
        
        return {
            'text': text,
            'media_urls': content.media_paths[:limits['media']],
            'hashtags': hashtags,
            'metadata': {'platform': 'LinkedIn', 'post_type': 'article'}
        }
    
    def _adapt_facebook(self, content: Any, limits: Dict) -> Dict[str, Any]:
        """Adapt content for Facebook (community focus)."""
        text = f"{content.title}\n\n{content.summary}\n\n"
        text += "Share your thoughts in the comments! 👇\n\n"
        text += ' '.join(content.hashtags[:limits['hashtags']])
        
        return {
            'text': text,
            'media_urls': content.media_paths[:limits['media']],
            'hashtags': content.hashtags[:limits['hashtags']],
            'metadata': {'platform': 'Facebook'}
        }
    
    def _adapt_instagram(self, content: Any, limits: Dict) -> Dict[str, Any]:
        """Adapt content for Instagram (visual-first)."""
        # Instagram requires media
        if not content.media_paths:
            # Skip if no media
            return {
                'text': '',
                'media_urls': [],
                'hashtags': [],
                'metadata': {'skip': True, 'reason': 'No media for Instagram'}
            }
        
        text = f"{content.summary}\n\n"
        text += ".\n.\n.\n"  # Instagram engagement hack
        text += ' '.join(content.hashtags[:limits['hashtags']])
        
        if len(text) > limits['text']:
            text = text[:limits['text']-3] + "..."
        
        return {
            'text': text,
            'media_urls': content.media_paths[:limits['media']],
            'hashtags': content.hashtags[:limits['hashtags']],
            'metadata': {'platform': 'Instagram'}
        }
    
    def _adapt_youtube(self, content: Any, limits: Dict) -> Dict[str, Any]:
        """Adapt content for YouTube (SEO-optimized)."""
        # YouTube descriptions need SEO optimization
        text = f"{content.title}\n\n"
        text += f"{content.body}\n\n"
        text += "---\n"
        text += "TIMESTAMPS:\n00:00 Introduction\n\n"
        text += "TAGS:\n" + ', '.join(content.hashtags[:limits['hashtags']])
        
        if len(text) > limits['text']:
            text = text[:limits['text']-3] + "..."
        
        return {
            'text': text,
            'media_urls': content.media_paths[:1],  # YouTube is video-only
            'hashtags': content.hashtags[:limits['hashtags']],
            'metadata': {'platform': 'YouTube', 'content_type': 'description'}
        }
    
    def _adapt_generic(self, content: Any, limits: Dict) -> Dict[str, Any]:
        """Generic adaptation for unknown platforms."""
        text = f"{content.title}\n\n{content.summary}"
        
        if len(text) > limits['text']:
            text = text[:limits['text']-3] + "..."
        
        return {
            'text': text,
            'media_urls': content.media_paths[:limits.get('media', 4)],
            'hashtags': content.hashtags[:limits.get('hashtags', 5)],
            'metadata': {'platform': 'generic'}
        }
