"""
Automation Orchestrator - Smart scheduling and queue management.

Features:
- Intelligent posting time optimization
- Priority-based queue management
- Automatic retry logic
- Rate limit compliance
- Multi-platform coordination
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import heapq
from collections import defaultdict
import pytz


class PostPriority(Enum):
    """Post priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class PostStatus(Enum):
    """Post status."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    POSTING = "posting"
    POSTED = "posted"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(order=True)
class ScheduledPost:
    """Scheduled social media post."""
    priority: int = field(compare=True)
    scheduled_time: datetime = field(compare=True)
    id: str = field(compare=False)
    platform: str = field(compare=False, default="")
    content: Dict[str, Any] = field(compare=False, default_factory=dict)
    status: PostStatus = field(compare=False, default=PostStatus.PENDING)
    retry_count: int = field(compare=False, default=0)
    metadata: Dict[str, Any] = field(compare=False, default_factory=dict)


class AutomationOrchestrator:
    """
    Central orchestration for autonomous social media management.
    
    Features:
    - Smart scheduling based on audience engagement patterns
    - Priority queue for post management
    - Automatic retry on failures
    - Rate limiting per platform
    - Conflict resolution
    """
    
    def __init__(self, config: Dict[str, Any], social_manager, content_generator):
        """
        Initialize orchestrator.
        
        Args:
            config: Configuration dictionary
            social_manager: Social media manager instance
            content_generator: Content generator instance
        """
        self.config = config
        self.social_manager = social_manager
        self.content_generator = content_generator
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        scheduler_config = config.get('scheduler', {})
        self.enabled = scheduler_config.get('enabled', True)
        self.check_interval = scheduler_config.get('check_interval', 60)
        self.max_concurrent = scheduler_config.get('max_concurrent_posts', 10)
        self.retry_enabled = scheduler_config.get('retry_failed', True)
        self.max_retries = scheduler_config.get('retry_attempts', 3)
        self.queue_size = scheduler_config.get('queue_size', 100)
        
        # Priority queue (min heap)
        self.post_queue: List[ScheduledPost] = []
        self.post_history: List[ScheduledPost] = []
        
        # Rate limiting
        self.post_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # State
        self.is_running = False
        self.scheduler_task = None
        
        # Statistics
        self.posts_today = 0
        self.posts_total = 0
        self.failed_posts = 0
        self.last_reset = datetime.now(timezone.utc).date()
    
    async def start(self):
        """Start the orchestrator."""
        if not self.enabled:
            self.logger.info("Scheduler disabled")
            return
        
        self.logger.info("Starting automation orchestrator...")
        self.is_running = True
        
        # Start scheduler loop
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        # Start automatic content generation loop
        asyncio.create_task(self._auto_content_loop())
    
    async def stop(self):
        """Stop the orchestrator."""
        self.logger.info("Stopping automation orchestrator...")
        self.is_running = False
        
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
    
    async def _scheduler_loop(self):
        """Main scheduler loop."""
        while self.is_running:
            try:
                await asyncio.sleep(self.check_interval)
                await self._process_queue()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Scheduler loop error: {e}")
    
    async def _auto_content_loop(self):
        """Automatic content generation and scheduling loop."""
        while self.is_running:
            try:
                # Wait between auto-generations
                await asyncio.sleep(3600)  # 1 hour
                
                # Generate and schedule content for enabled platforms
                enabled_platforms = self.config.get_enabled_social_platforms()
                
                for platform in enabled_platforms:
                    # Check if we should post to this platform today
                    if self._should_generate_for_platform(platform):
                        await self._generate_and_schedule_for_platform(platform)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Auto content loop error: {e}")
    
    def _should_generate_for_platform(self, platform: str) -> bool:
        """Check if we should generate content for platform today."""
        platform_config = self.config.get('social_media', {}).get(platform, {})
        max_posts_today = platform_config.get('max_posts_per_day', 5)
        
        # Count posts today for this platform
        today = datetime.now(timezone.utc).date()
        posts_today = sum(
            1 for post in self.post_history
            if post.platform == platform and 
            post.scheduled_time.date() == today and
            post.status == PostStatus.POSTED
        )
        
        return posts_today < max_posts_today
    
    async def _generate_and_schedule_for_platform(self, platform: str):
        """Generate and schedule content for platform."""
        try:
            self.logger.info(f"Auto-generating content for {platform}")
            
            # Generate content
            content = await self.content_generator.generate(
                platform=platform,
                use_tools=True
            )
            
            # Calculate optimal posting time
            optimal_time = self._calculate_optimal_time(platform)
            
            # Schedule post
            await self.schedule_post(
                platform=platform,
                content=content['content'],
                schedule_time=optimal_time,
                priority=PostPriority.NORMAL
            )
            
        except Exception as e:
            self.logger.error(f"Auto-generation failed for {platform}: {e}")
    
    def _calculate_optimal_time(self, platform: str) -> datetime:
        """
        Calculate optimal posting time based on platform and audience.
        
        Args:
            platform: Social media platform
            
        Returns:
            Optimal posting datetime
        """
        # Get platform config
        platform_config = self.config.get('social_media', {}).get(platform, {})
        optimal_times = platform_config.get('optimal_times', [])
        
        # Get timezone
        business_timezone = self.config.get('business', {}).get('timezone', 'UTC')
        tz = pytz.timezone(business_timezone)
        
        # Default optimal times by platform (based on industry research)
        default_optimal_times = {
            'Twitter/X': ['09:00', '12:00', '17:00'],
            'LinkedIn': ['08:00', '12:00', '17:00'],
            'Facebook': ['13:00', '15:00', '19:00'],
            'Instagram': ['11:00', '13:00', '19:00'],
            'YouTube': ['14:00', '18:00', '20:00'],
        }
        
        times_to_try = optimal_times or default_optimal_times.get(platform, ['12:00'])
        
        # Find next available optimal time
        now = datetime.now(tz)
        
        for time_str in times_to_try:
            hour, minute = map(int, time_str.split(':'))
            
            # Try today first
            target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            if target > now:
                # Check if slot is available
                if not self._is_time_slot_taken(platform, target):
                    return target.astimezone(timezone.utc)
            
            # Try tomorrow
            target = target + timedelta(days=1)
            if not self._is_time_slot_taken(platform, target):
                return target.astimezone(timezone.utc)
        
        # Fallback: schedule for tomorrow at first optimal time
        hour, minute = map(int, times_to_try[0].split(':'))
        target = (now + timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        return target.astimezone(timezone.utc)
    
    def _is_time_slot_taken(self, platform: str, time: datetime) -> bool:
        """Check if time slot is already taken."""
        time_window = timedelta(minutes=15)
        
        for post in self.post_queue:
            if post.platform == platform and post.status == PostStatus.SCHEDULED:
                if abs((post.scheduled_time - time).total_seconds()) < time_window.total_seconds():
                    return True
        
        return False
    
    async def schedule_post(
        self,
        platform: str,
        content: Dict[str, Any],
        schedule_time: Optional[datetime] = None,
        priority: PostPriority = PostPriority.NORMAL
    ) -> str:
        """
        Schedule a post.
        
        Args:
            platform: Social media platform
            content: Post content
            schedule_time: When to post (now if not specified)
            priority: Post priority
            
        Returns:
            Post ID
        """
        post_id = f"{platform}_{datetime.now(timezone.utc).timestamp()}"
        
        if schedule_time is None:
            schedule_time = datetime.now(timezone.utc)
        
        post = ScheduledPost(
            priority=-priority.value,  # Negative for min heap to act as max heap
            scheduled_time=schedule_time,
            id=post_id,
            platform=platform,
            content=content,
            status=PostStatus.SCHEDULED,
            metadata={
                'created_at': datetime.now(timezone.utc).isoformat()
            }
        )
        
        heapq.heappush(self.post_queue, post)
        
        self.logger.info(f"Scheduled post {post_id} for {platform} at {schedule_time}")
        
        return post_id
    
    async def _process_queue(self):
        """Process scheduled posts."""
        self._update_daily_counters()
        
        now = datetime.now(timezone.utc)
        posts_to_process = []
        
        # Find posts ready to be posted
        while self.post_queue and len(posts_to_process) < self.max_concurrent:
            if self.post_queue[0].scheduled_time <= now:
                post = heapq.heappop(self.post_queue)
                
                if post.status == PostStatus.SCHEDULED:
                    posts_to_process.append(post)
                elif post.status == PostStatus.CANCELLED:
                    continue
            else:
                break
        
        # Process posts concurrently
        if posts_to_process:
            tasks = [self._post_content(post) for post in posts_to_process]
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _post_content(self, post: ScheduledPost):
        """Post content to platform."""
        try:
            self.logger.info(f"Posting to {post.platform}: {post.id}")
            
            # Check rate limits
            if not self._check_rate_limit(post.platform):
                self.logger.warning(f"Rate limit reached for {post.platform}, rescheduling")
                post.scheduled_time = datetime.now(timezone.utc) + timedelta(hours=1)
                heapq.heappush(self.post_queue, post)
                return
            
            post.status = PostStatus.POSTING
            
            # Post through social manager
            result = await self.social_manager.post_content(
                platform=post.platform,
                content=post.content
            )
            
            if result.get('success'):
                post.status = PostStatus.POSTED
                self.posts_today += 1
                self.posts_total += 1
                
                # Record rate limit
                self._record_post(post.platform)
                
                self.logger.info(f"Successfully posted {post.id}")
            else:
                raise Exception(result.get('error', 'Unknown error'))
            
        except Exception as e:
            self.logger.error(f"Failed to post {post.id}: {e}")
            post.status = PostStatus.FAILED
            self.failed_posts += 1
            
            # Retry logic
            if self.retry_enabled and post.retry_count < self.max_retries:
                post.retry_count += 1
                post.status = PostStatus.SCHEDULED
                post.scheduled_time = datetime.now(timezone.utc) + timedelta(minutes=15 * post.retry_count)
                heapq.heappush(self.post_queue, post)
                self.logger.info(f"Rescheduled {post.id} for retry {post.retry_count}/{self.max_retries}")
        
        finally:
            self.post_history.append(post)
    
    def _check_rate_limit(self, platform: str) -> bool:
        """Check if platform rate limit allows posting."""
        platform_config = self.config.get('social_media', {}).get(platform, {})
        max_per_day = platform_config.get('max_posts_per_day', 10)
        
        today = datetime.now(timezone.utc).date().isoformat()
        current_count = self.post_counts[platform][today]
        
        return current_count < max_per_day
    
    def _record_post(self, platform: str):
        """Record a post for rate limiting."""
        today = datetime.now(timezone.utc).date().isoformat()
        self.post_counts[platform][today] += 1
    
    def _update_daily_counters(self):
        """Update daily counters."""
        today = datetime.now(timezone.utc).date()
        
        if today != self.last_reset:
            self.posts_today = 0
            self.last_reset = today
    
    def get_queue_size(self) -> int:
        """Get current queue size."""
        return len(self.post_queue)
    
    def get_posts_count_today(self) -> int:
        """Get posts published today."""
        self._update_daily_counters()
        return self.posts_today
    
    def get_scheduled_posts(self, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get scheduled posts.
        
        Args:
            platform: Filter by platform (all if None)
            
        Returns:
            List of scheduled posts
        """
        posts = []
        
        for post in self.post_queue:
            if post.status == PostStatus.SCHEDULED:
                if platform is None or post.platform == platform:
                    posts.append({
                        'id': post.id,
                        'platform': post.platform,
                        'scheduled_time': post.scheduled_time.isoformat(),
                        'priority': PostPriority(-post.priority).name,
                        'content': post.content
                    })
        
        return sorted(posts, key=lambda x: x['scheduled_time'])
    
    def cancel_post(self, post_id: str) -> bool:
        """
        Cancel a scheduled post.
        
        Args:
            post_id: Post ID
            
        Returns:
            True if cancelled, False if not found
        """
        for post in self.post_queue:
            if post.id == post_id:
                post.status = PostStatus.CANCELLED
                self.logger.info(f"Cancelled post {post_id}")
                return True
        
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        return {
            'queue_size': self.get_queue_size(),
            'posts_today': self.posts_today,
            'posts_total': self.posts_total,
            'failed_posts': self.failed_posts,
            'success_rate': (self.posts_total / (self.posts_total + self.failed_posts) * 100) 
                          if (self.posts_total + self.failed_posts) > 0 else 0,
            'platform_stats': dict(self.post_counts)
        }
