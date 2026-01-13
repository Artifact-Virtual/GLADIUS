"""
Publishing Pipeline - Connects Syndicate research → Automata social channels.

Flow:
1. Syndicate generates reports (journals, catalysts, analysis)
2. ContentAdapter formats for each platform
3. EngagementTracker optimizes timing/content
4. SocialMediaManager publishes to channels
"""

import os
import logging
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

try:
    from ..social_media.manager import SocialMediaManager
    from ..scheduler.orchestrator import AutomationOrchestrator, PostPriority
except ImportError:
    # Handle standalone imports
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from social_media.manager import SocialMediaManager
    from scheduler.orchestrator import AutomationOrchestrator, PostPriority


@dataclass
class PublishableContent:
    """Content ready for publishing."""
    id: str
    source: str  # journal, catalyst, analysis, etc.
    title: str
    body: str
    summary: str
    hashtags: List[str]
    media_paths: List[str]
    metadata: Dict[str, Any]
    priority: PostPriority = PostPriority.NORMAL


class PublishingPipeline:
    """
    Unified publishing pipeline connecting research → social channels.
    
    Features:
    - Auto-converts Syndicate reports to social content
    - Platform-specific formatting
    - Optimal timing scheduling
    - Engagement tracking feedback loop
    """
    
    def __init__(
        self,
        syndicate_output_dir: str,
        config: Dict[str, Any],
        social_manager: Optional[SocialMediaManager] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize publishing pipeline.
        
        Args:
            syndicate_output_dir: Path to Syndicate output directory
            config: Configuration dictionary
            social_manager: Optional existing social manager
            logger: Optional logger
        """
        self.syndicate_dir = Path(syndicate_output_dir)
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize components
        self.social_manager = social_manager or SocialMediaManager(config)
        self.content_adapter = ContentAdapter()
        self.engagement_tracker = EngagementTracker(config)
        
        # State
        self.published_ids: set = set()
        self.pending_queue: List[PublishableContent] = []
    
    async def scan_new_content(self) -> List[PublishableContent]:
        """
        Scan Syndicate output for new publishable content.
        
        Returns:
            List of new publishable content items
        """
        new_content = []
        
        # Scan journals
        journals_dir = self.syndicate_dir / "reports" / "journals"
        if journals_dir.exists():
            for journal_file in journals_dir.glob("*.md"):
                content_id = f"journal_{journal_file.stem}"
                if content_id not in self.published_ids:
                    content = self._parse_journal(journal_file)
                    if content:
                        new_content.append(content)
        
        # Scan catalysts
        catalysts_dir = self.syndicate_dir / "reports" / "catalysts"
        if catalysts_dir.exists():
            for catalyst_file in catalysts_dir.glob("*.md"):
                content_id = f"catalyst_{catalyst_file.stem}"
                if content_id not in self.published_ids:
                    content = self._parse_catalyst(catalyst_file)
                    if content:
                        new_content.append(content)
        
        # Scan charts (for visual content)
        charts_dir = self.syndicate_dir / "charts"
        if charts_dir.exists():
            for chart_file in charts_dir.glob("*.png"):
                content_id = f"chart_{chart_file.stem}_{datetime.now().strftime('%Y%m%d')}"
                if content_id not in self.published_ids:
                    content = self._parse_chart(chart_file)
                    if content:
                        new_content.append(content)
        
        self.logger.info(f"Found {len(new_content)} new content items")
        return new_content
    
    def _parse_journal(self, file_path: Path) -> Optional[PublishableContent]:
        """Parse a journal file into publishable content."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Extract title (first H1)
            lines = content.split('\n')
            title = "Daily Market Journal"
            for line in lines:
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
            
            # Extract bias
            bias = "NEUTRAL"
            if 'BULLISH' in content.upper():
                bias = "BULLISH"
            elif 'BEARISH' in content.upper():
                bias = "BEARISH"
            
            # Create summary for social
            summary = self._create_summary(content, max_length=250)
            
            return PublishableContent(
                id=f"journal_{file_path.stem}",
                source="journal",
                title=title,
                body=content,
                summary=summary,
                hashtags=["#Gold", "#XAUUSD", "#Trading", "#MarketAnalysis", f"#{bias}"],
                media_paths=[],
                metadata={"bias": bias, "date": file_path.stem.split('_')[-1]},
                priority=PostPriority.HIGH
            )
        except Exception as e:
            self.logger.error(f"Failed to parse journal {file_path}: {e}")
            return None
    
    def _parse_catalyst(self, file_path: Path) -> Optional[PublishableContent]:
        """Parse a catalyst file into publishable content."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            title = "Market Catalyst Alert"
            summary = self._create_summary(content, max_length=200)
            
            return PublishableContent(
                id=f"catalyst_{file_path.stem}",
                source="catalyst",
                title=title,
                body=content,
                summary=summary,
                hashtags=["#MarketNews", "#Trading", "#Catalysts", "#BreakingNews"],
                media_paths=[],
                metadata={"date": file_path.stem.split('_')[-1]},
                priority=PostPriority.URGENT  # Catalysts are time-sensitive
            )
        except Exception as e:
            self.logger.error(f"Failed to parse catalyst {file_path}: {e}")
            return None
    
    def _parse_chart(self, file_path: Path) -> Optional[PublishableContent]:
        """Parse a chart file into publishable content."""
        try:
            symbol = file_path.stem.upper()
            
            return PublishableContent(
                id=f"chart_{file_path.stem}_{datetime.now().strftime('%Y%m%d')}",
                source="chart",
                title=f"{symbol} Technical Analysis",
                body=f"Today's {symbol} chart with key levels and indicators.",
                summary=f"📊 {symbol} Technical Analysis - Key levels, support/resistance, and trend indicators.",
                hashtags=[f"#{symbol}", "#TechnicalAnalysis", "#Trading", "#Charts"],
                media_paths=[str(file_path)],
                metadata={"symbol": symbol},
                priority=PostPriority.NORMAL
            )
        except Exception as e:
            self.logger.error(f"Failed to parse chart {file_path}: {e}")
            return None
    
    def _create_summary(self, content: str, max_length: int = 250) -> str:
        """Create a social-friendly summary from content."""
        # Remove markdown
        import re
        text = re.sub(r'#+ ', '', content)
        text = re.sub(r'\*+', '', text)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        text = re.sub(r'\n+', ' ', text)
        text = text.strip()
        
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
        
        return text
    
    async def publish_to_platforms(
        self,
        content: PublishableContent,
        platforms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Publish content to specified platforms.
        
        Args:
            content: Publishable content
            platforms: List of platforms (all enabled if None)
            
        Returns:
            Publishing results per platform
        """
        if platforms is None:
            platforms = self.social_manager.get_enabled_platforms()
        
        results = {}
        
        for platform in platforms:
            try:
                # Adapt content for platform
                adapted = self.content_adapter.adapt(content, platform)
                
                # Post
                result = await self.social_manager.post_content(
                    platform=platform,
                    content={'text': adapted['text']},
                    media_urls=adapted.get('media_urls')
                )
                
                results[platform] = result
                
                if result.get('success'):
                    self.logger.info(f"Published to {platform}: {content.id}")
                    self.published_ids.add(content.id)
                    
                    # Track for engagement learning
                    self.engagement_tracker.track_post(
                        content_id=content.id,
                        platform=platform,
                        post_id=result.get('post_id'),
                        content_type=content.source,
                        posted_at=datetime.now(timezone.utc)
                    )
                else:
                    self.logger.warning(f"Failed to publish to {platform}: {result.get('error')}")
                    
            except Exception as e:
                self.logger.error(f"Error publishing to {platform}: {e}")
                results[platform] = {'success': False, 'error': str(e)}
        
        return results
    
    async def run_publishing_cycle(self) -> Dict[str, Any]:
        """
        Run a complete publishing cycle.
        
        Returns:
            Cycle results
        """
        results = {
            'scanned': 0,
            'published': 0,
            'failed': 0,
            'platforms': {}
        }
        
        # Scan for new content
        new_content = await self.scan_new_content()
        results['scanned'] = len(new_content)
        
        # Publish each item
        for content in new_content:
            publish_results = await self.publish_to_platforms(content)
            
            for platform, result in publish_results.items():
                if platform not in results['platforms']:
                    results['platforms'][platform] = {'success': 0, 'failed': 0}
                
                if result.get('success'):
                    results['platforms'][platform]['success'] += 1
                    results['published'] += 1
                else:
                    results['platforms'][platform]['failed'] += 1
                    results['failed'] += 1
        
        return results
    
    def get_publishing_stats(self) -> Dict[str, Any]:
        """Get publishing statistics."""
        return {
            'total_published': len(self.published_ids),
            'pending': len(self.pending_queue),
            'enabled_platforms': self.social_manager.get_enabled_platforms(),
            'engagement_stats': self.engagement_tracker.get_stats()
        }
