"""
Discord Integration - Push notifications and alerts.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import aiohttp
import asyncio


class DiscordIntegration:
    """
    Discord integration for notifications and alerts.
    
    Features:
    - Webhook notifications
    - Bot messaging
    - Error alerts
    - ERP sync notifications
    - Social media post notifications
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Discord integration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.enabled = config.get('enabled', False) or os.getenv('DISCORD_ENABLED', 'false').lower() == 'true'
        self.bot_token = config.get('bot_token') or os.getenv('DISCORD_BOT_TOKEN')
        self.webhook_url = config.get('webhook_url') or os.getenv('DISCORD_WEBHOOK_URL')
        self.channel_id = config.get('channel_id') or os.getenv('DISCORD_CHANNEL_ID')
        
        self.notify_posts = config.get('notify_posts', True) or os.getenv('DISCORD_NOTIFY_POSTS', 'true').lower() == 'true'
        self.notify_errors = config.get('notify_errors', True) or os.getenv('DISCORD_NOTIFY_ERRORS', 'true').lower() == 'true'
        self.notify_erp_sync = config.get('notify_erp_sync', True) or os.getenv('DISCORD_NOTIFY_ERP_SYNC', 'true').lower() == 'true'
    
    async def send_webhook(self, content: str, embed: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send message via webhook.
        
        Args:
            content: Message content
            embed: Optional embed object
            
        Returns:
            True if sent successfully
        """
        if not self.enabled or not self.webhook_url:
            return False
        
        payload = {
            'content': content,
            'username': 'Enterprise Automation Bot',
            'avatar_url': 'https://cdn.discordapp.com/embed/avatars/0.png'
        }
        
        if embed:
            payload['embeds'] = [embed]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 204:
                        self.logger.info("Discord notification sent")
                        return True
                    else:
                        self.logger.error(f"Discord webhook failed: {response.status}")
                        return False
        except Exception as e:
            self.logger.error(f"Failed to send Discord notification: {e}")
            return False
    
    async def notify_post(self, platform: str, content: str, post_url: str) -> bool:
        """
        Notify about a new social media post.
        
        Args:
            platform: Social media platform
            content: Post content
            post_url: URL to the post
            
        Returns:
            True if notified successfully
        """
        if not self.notify_posts:
            return False
        
        embed = {
            'title': f'New Post on {platform}',
            'description': content[:200] + ('...' if len(content) > 200 else ''),
            'color': 0x00ff00,  # Green
            'fields': [
                {
                    'name': 'Platform',
                    'value': platform,
                    'inline': True
                },
                {
                    'name': 'URL',
                    'value': post_url if post_url else 'N/A',
                    'inline': True
                }
            ],
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'footer': {
                'text': 'Enterprise Automation Suite'
            }
        }
        
        return await self.send_webhook('', embed=embed)
    
    async def notify_error(self, error_type: str, error_message: str, context: Optional[str] = None) -> bool:
        """
        Notify about an error.
        
        Args:
            error_type: Type of error
            error_message: Error message
            context: Additional context
            
        Returns:
            True if notified successfully
        """
        if not self.notify_errors:
            return False
        
        embed = {
            'title': f'⚠️ Error: {error_type}',
            'description': error_message,
            'color': 0xff0000,  # Red
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'footer': {
                'text': 'Enterprise Automation Suite'
            }
        }
        
        if context:
            embed['fields'] = [
                {
                    'name': 'Context',
                    'value': context,
                    'inline': False
                }
            ]
        
        return await self.send_webhook('', embed=embed)
    
    async def notify_erp_sync(self, system: str, entity_type: str, count: int, success: bool) -> bool:
        """
        Notify about ERP synchronization.
        
        Args:
            system: ERP system name
            entity_type: Type of entity synced
            count: Number of entities synced
            success: Whether sync was successful
            
        Returns:
            True if notified successfully
        """
        if not self.notify_erp_sync:
            return False
        
        color = 0x00ff00 if success else 0xff0000  # Green if success, red if failed
        status = '✅ Success' if success else '❌ Failed'
        
        embed = {
            'title': f'ERP Sync: {system}',
            'description': f'{status} - Synced {count} {entity_type}',
            'color': color,
            'fields': [
                {
                    'name': 'System',
                    'value': system,
                    'inline': True
                },
                {
                    'name': 'Entity Type',
                    'value': entity_type,
                    'inline': True
                },
                {
                    'name': 'Count',
                    'value': str(count),
                    'inline': True
                }
            ],
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'footer': {
                'text': 'Enterprise Automation Suite'
            }
        }
        
        return await self.send_webhook('', embed=embed)
    
    async def notify_system_status(self, status: str, message: str) -> bool:
        """
        Notify about system status changes.
        
        Args:
            status: Status (started, stopped, error)
            message: Status message
            
        Returns:
            True if notified successfully
        """
        color_map = {
            'started': 0x00ff00,  # Green
            'stopped': 0xffa500,  # Orange
            'error': 0xff0000,    # Red
        }
        
        embed = {
            'title': f'System Status: {status.title()}',
            'description': message,
            'color': color_map.get(status.lower(), 0x808080),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'footer': {
                'text': 'Enterprise Automation Suite'
            }
        }
        
        return await self.send_webhook('', embed=embed)
    
    async def notify_reflection(self, improvements: list, action_items: list) -> bool:
        """
        Notify about AI reflection and improvements.
        
        Args:
            improvements: List of improvements identified
            action_items: List of action items
            
        Returns:
            True if notified successfully
        """
        embed = {
            'title': '🧠 AI Reflection Complete',
            'description': f'Identified {len(improvements)} improvements',
            'color': 0x0099ff,  # Blue
            'fields': [
                {
                    'name': 'Improvements',
                    'value': '\n'.join(f'• {imp}' for imp in improvements[:5]) or 'None',
                    'inline': False
                },
                {
                    'name': 'Action Items',
                    'value': '\n'.join(f'• {action}' for action in action_items[:5]) or 'None',
                    'inline': False
                }
            ],
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'footer': {
                'text': 'Enterprise Automation Suite'
            }
        }
        
        return await self.send_webhook('', embed=embed)
