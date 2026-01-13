"""
Engagement Tracker - Tracks and learns from social media engagement.

Features:
- Track post performance
- Learn optimal posting times
- Identify high-performing content types
- Feedback loop for content optimization
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
from dataclasses import dataclass, asdict


@dataclass
class EngagementRecord:
    """Record of a post's engagement metrics."""
    content_id: str
    platform: str
    post_id: str
    content_type: str
    posted_at: datetime
    likes: int = 0
    comments: int = 0
    shares: int = 0
    impressions: int = 0
    clicks: int = 0
    engagement_rate: float = 0.0
    last_updated: Optional[datetime] = None


class EngagementTracker:
    """
    Tracks engagement metrics and learns from performance.
    
    Uses historical data to:
    - Optimize posting times
    - Identify best content types
    - Improve hashtag selection
    - Learn audience preferences
    """
    
    def __init__(self, config: Dict[str, Any], data_dir: Optional[str] = None):
        """
        Initialize engagement tracker.
        
        Args:
            config: Configuration dictionary
            data_dir: Directory for persistence
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Data directory
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = Path.home() / ".gladius" / "engagement"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Storage
        self.records: Dict[str, EngagementRecord] = {}
        self.platform_stats: Dict[str, Dict] = defaultdict(lambda: {
            'total_posts': 0,
            'total_engagement': 0,
            'avg_engagement_rate': 0.0,
            'best_posting_hours': [],
            'best_content_types': []
        })
        
        # Load existing data
        self._load_data()
    
    def track_post(
        self,
        content_id: str,
        platform: str,
        post_id: str,
        content_type: str,
        posted_at: datetime
    ) -> str:
        """
        Start tracking a new post.
        
        Args:
            content_id: Internal content ID
            platform: Social platform
            post_id: Platform's post ID
            content_type: Type of content (journal, catalyst, chart)
            posted_at: When it was posted
            
        Returns:
            Tracking record ID
        """
        record_id = f"{platform}_{post_id}"
        
        record = EngagementRecord(
            content_id=content_id,
            platform=platform,
            post_id=post_id,
            content_type=content_type,
            posted_at=posted_at
        )
        
        self.records[record_id] = record
        self.platform_stats[platform]['total_posts'] += 1
        
        self._save_data()
        
        self.logger.info(f"Tracking post: {record_id}")
        return record_id
    
    def update_metrics(
        self,
        record_id: str,
        likes: int = 0,
        comments: int = 0,
        shares: int = 0,
        impressions: int = 0,
        clicks: int = 0
    ):
        """
        Update engagement metrics for a tracked post.
        
        Args:
            record_id: Tracking record ID
            likes, comments, shares, impressions, clicks: Metrics
        """
        if record_id not in self.records:
            self.logger.warning(f"Record not found: {record_id}")
            return
        
        record = self.records[record_id]
        record.likes = likes
        record.comments = comments
        record.shares = shares
        record.impressions = impressions
        record.clicks = clicks
        record.last_updated = datetime.now(timezone.utc)
        
        # Calculate engagement rate
        if impressions > 0:
            record.engagement_rate = ((likes + comments + shares + clicks) / impressions) * 100
        
        # Update platform stats
        self._update_platform_stats(record)
        
        self._save_data()
    
    def _update_platform_stats(self, record: EngagementRecord):
        """Update aggregate platform statistics."""
        stats = self.platform_stats[record.platform]
        
        # Update totals
        stats['total_engagement'] += record.likes + record.comments + record.shares
        
        # Recalculate average engagement rate
        platform_records = [r for r in self.records.values() if r.platform == record.platform]
        if platform_records:
            stats['avg_engagement_rate'] = sum(r.engagement_rate for r in platform_records) / len(platform_records)
        
        # Track best posting hours
        posting_hour = record.posted_at.hour
        if record.engagement_rate > stats['avg_engagement_rate']:
            if posting_hour not in stats['best_posting_hours']:
                stats['best_posting_hours'].append(posting_hour)
                stats['best_posting_hours'] = sorted(stats['best_posting_hours'])[:5]
        
        # Track best content types
        if record.engagement_rate > stats['avg_engagement_rate']:
            if record.content_type not in stats['best_content_types']:
                stats['best_content_types'].append(record.content_type)
    
    def get_optimal_posting_time(self, platform: str) -> int:
        """
        Get the optimal posting hour for a platform.
        
        Args:
            platform: Social platform
            
        Returns:
            Best hour (0-23) to post
        """
        stats = self.platform_stats.get(platform, {})
        best_hours = stats.get('best_posting_hours', [])
        
        if best_hours:
            return best_hours[0]  # Return the best hour
        
        # Default optimal times if no data
        defaults = {
            'Twitter/X': 9,
            'LinkedIn': 8,
            'Facebook': 13,
            'Instagram': 11,
            'YouTube': 14
        }
        
        return defaults.get(platform, 12)
    
    def get_best_content_types(self, platform: str) -> List[str]:
        """Get the best performing content types for a platform."""
        stats = self.platform_stats.get(platform, {})
        return stats.get('best_content_types', ['journal', 'chart'])
    
    def get_stats(self) -> Dict[str, Any]:
        """Get overall engagement statistics."""
        total_posts = sum(s['total_posts'] for s in self.platform_stats.values())
        total_engagement = sum(s['total_engagement'] for s in self.platform_stats.values())
        
        return {
            'total_posts_tracked': total_posts,
            'total_engagement': total_engagement,
            'platforms': dict(self.platform_stats),
            'records_count': len(self.records)
        }
    
    def get_top_performing_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing posts by engagement rate."""
        sorted_records = sorted(
            self.records.values(),
            key=lambda r: r.engagement_rate,
            reverse=True
        )
        
        return [
            {
                'content_id': r.content_id,
                'platform': r.platform,
                'content_type': r.content_type,
                'engagement_rate': r.engagement_rate,
                'posted_at': r.posted_at.isoformat() if r.posted_at else None
            }
            for r in sorted_records[:limit]
        ]
    
    def _load_data(self):
        """Load persisted data."""
        records_file = self.data_dir / "engagement_records.json"
        stats_file = self.data_dir / "platform_stats.json"
        
        if records_file.exists():
            try:
                with open(records_file) as f:
                    data = json.load(f)
                    for record_id, record_data in data.items():
                        record_data['posted_at'] = datetime.fromisoformat(record_data['posted_at'])
                        if record_data.get('last_updated'):
                            record_data['last_updated'] = datetime.fromisoformat(record_data['last_updated'])
                        self.records[record_id] = EngagementRecord(**record_data)
            except Exception as e:
                self.logger.error(f"Failed to load records: {e}")
        
        if stats_file.exists():
            try:
                with open(stats_file) as f:
                    self.platform_stats.update(json.load(f))
            except Exception as e:
                self.logger.error(f"Failed to load stats: {e}")
    
    def _save_data(self):
        """Persist data to disk."""
        records_file = self.data_dir / "engagement_records.json"
        stats_file = self.data_dir / "platform_stats.json"
        
        try:
            records_data = {}
            for record_id, record in self.records.items():
                data = asdict(record)
                data['posted_at'] = record.posted_at.isoformat() if record.posted_at else None
                data['last_updated'] = record.last_updated.isoformat() if record.last_updated else None
                records_data[record_id] = data
            
            with open(records_file, 'w') as f:
                json.dump(records_data, f, indent=2)
            
            with open(stats_file, 'w') as f:
                json.dump(dict(self.platform_stats), f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save data: {e}")
