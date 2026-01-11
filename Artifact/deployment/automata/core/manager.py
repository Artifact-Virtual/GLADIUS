"""
Enterprise Manager - Central orchestration hub for all automation.

Coordinates ERP integrations, social media management, AI content generation,
and scheduling in a seamless, fully autonomous manner.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import asyncio

from .config import AutomationConfig
from ..erp_integrations.manager import ERPManager
from ..social_media.manager import SocialMediaManager
from ..ai_engine.generator import ContentGenerator
from ..scheduler.orchestrator import AutomationOrchestrator


class EnterpriseManager:
    """
    Central manager for the enterprise automation suite.
    
    Provides unified interface for:
    - ERP system integration and data synchronization
    - Social media content generation and posting
    - Autonomous scheduling and management
    - Analytics and reporting
    """
    
    def __init__(self, config: Optional[AutomationConfig] = None):
        """
        Initialize Enterprise Manager.
        
        Args:
            config: Automation configuration (creates new if not provided)
        """
        self.config = config or AutomationConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.erp_manager = ERPManager(self.config)
        self.social_manager = SocialMediaManager(self.config)
        self.content_generator = ContentGenerator(self.config)
        self.orchestrator = AutomationOrchestrator(
            self.config,
            self.social_manager,
            self.content_generator
        )
        
        # Initialize workers (not started until start())
        try:
            from ..ai_engine.editorial_worker import EditorialWorker
            from ..ai_engine.publish_worker import PublishWorker
            self.editorial_worker = EditorialWorker(self.content_generator.content_store, content_generator=self.content_generator)
            self.publish_worker = PublishWorker(self.content_generator.content_store, orchestrator=self.orchestrator)
        except Exception:
            self.editorial_worker = None
            self.publish_worker = None

        self.is_running = False
        self._tasks = []
    
    async def start(self) -> None:
        """Start the enterprise automation system."""
        self.logger.info("Starting Enterprise Automation Suite...")
        
        # Validate configuration
        errors = self.config.validate()
        if errors:
            self.logger.error(f"Configuration errors: {errors}")
            raise ValueError(f"Configuration validation failed: {errors}")
        
        self.is_running = True

        # Start content generator async subsystems (reflection, etc.)
        try:
            await self.content_generator.start()
        except Exception as e:
            self.logger.error(f"Failed to start content generator subsystems: {e}")

        # Start editorial & publish workers if available
        try:
            if getattr(self, 'editorial_worker', None):
                self.editorial_worker.start()
            if getattr(self, 'publish_worker', None):
                self.publish_worker.start()
        except Exception as e:
            self.logger.error(f"Failed to start workers: {e}")

        # Start ERP synchronization
        if self.config.get_enabled_erp_systems():
            self.logger.info("Starting ERP synchronization...")
            erp_task = asyncio.create_task(self.erp_manager.start_sync())
            self._tasks.append(erp_task)
        
        # Start social media orchestration
        if self.config.get_enabled_social_platforms():
            self.logger.info("Starting social media automation...")
            social_task = asyncio.create_task(self.orchestrator.start())
            self._tasks.append(social_task)
        
        self.logger.info("Enterprise Automation Suite started successfully!")
    
    async def stop(self) -> None:
        """Stop the enterprise automation system."""
        self.logger.info("Stopping Enterprise Automation Suite...")
        
        self.is_running = False
        
        # Stop workers
        try:
            if getattr(self, 'editorial_worker', None):
                self.editorial_worker.stop()
            if getattr(self, 'publish_worker', None):
                self.publish_worker.stop()
        except Exception as e:
            self.logger.error(f"Error stopping workers: {e}")

        # Stop all tasks
        for task in self._tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self._tasks, return_exceptions=True)
        
        self.logger.info("Enterprise Automation Suite stopped.")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the automation system.
        
        Returns:
            Status dictionary with component states
        """
        return {
            "running": self.is_running,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "erp_systems": {
                "enabled": self.config.get_enabled_erp_systems(),
                "sync_status": self.erp_manager.get_sync_status()
            },
            "social_media": {
                "enabled": self.config.get_enabled_social_platforms(),
                "queue_size": self.orchestrator.get_queue_size(),
                "posts_today": self.orchestrator.get_posts_count_today()
            },
            "ai_engine": {
                "provider": self.config.get("ai_engine.provider"),
                "model": self.config.get("ai_engine.model"),
                "generated_today": (self.content_generator.get_generated_count_today() if hasattr(self.content_generator, 'get_generated_count_today') else 0)
            }
        }
    
    def get_analytics(self) -> Dict[str, Any]:
        """
        Get analytics and performance metrics.
        
        Returns:
            Analytics dictionary
        """
        return {
            "erp": self.erp_manager.get_analytics(),
            "social_media": self.social_manager.get_analytics(),
            "content": self.content_generator.get_analytics()
        }
    
    async def generate_and_schedule_content(
        self,
        platform: str,
        topic: Optional[str] = None,
        schedule_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate content and schedule for posting.
        
        Args:
            platform: Social media platform
            topic: Content topic (auto-generated if not provided)
            schedule_time: When to post (immediately if not provided)
            
        Returns:
            Generated content and scheduling info
        """
        # Generate content
        content = await self.content_generator.generate(
            platform=platform,
            topic=topic
        )
        
        # Schedule post
        post_id = await self.orchestrator.schedule_post(
            platform=platform,
            content=content,
            schedule_time=schedule_time
        )
        
        return {
            "post_id": post_id,
            "platform": platform,
            "content": content,
            "scheduled_time": schedule_time.isoformat() if schedule_time else "immediate"
        }
    
    async def sync_erp_data(self, system: str, entity_type: str) -> Dict[str, Any]:
        """
        Manually trigger ERP data synchronization.
        
        Args:
            system: ERP system name
            entity_type: Type of entity to sync (customers, products, orders, etc.)
            
        Returns:
            Synchronization result
        """
        return await self.erp_manager.sync_entity(system, entity_type)
    
    def get_scheduled_posts(self, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get scheduled posts.
        
        Args:
            platform: Filter by platform (all if not provided)
            
        Returns:
            List of scheduled posts
        """
        return self.orchestrator.get_scheduled_posts(platform)
    
    def cancel_scheduled_post(self, post_id: str) -> bool:
        """
        Cancel a scheduled post.
        
        Args:
            post_id: ID of post to cancel
            
        Returns:
            True if cancelled, False if not found
        """
        return self.orchestrator.cancel_post(post_id)
