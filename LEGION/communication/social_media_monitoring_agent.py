"""
Social Media Monitoring Agent - Enterprise Legion Framework
Track brand presence and market sentiment across social platforms
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try:
    from legion.core_framework import BaseAgent, AgentMessage
except ImportError:
    # Fallback for standalone operation
    class BaseAgent:
        def __init__(self, name):
            self.name = name
        def log(self, message):
            print(f"[{self.name}] {message}")
    
    class AgentMessage:
        def __init__(self, content, sender=None):
            self.content = content
            self.sender = sender
import uuid


@dataclass
class SocialMention:
    """Social media mention data structure"""
    mention_id: str
    platform: str
    author: str
    content: str
    timestamp: datetime
    sentiment: str
    engagement_metrics: Dict[str, int]
    reach: int
    influence_score: float


@dataclass
class TrendAnalysis:
    """Trend analysis data structure"""
    trend_id: str
    topic: str
    platforms: List[str]
    trend_score: float
    growth_rate: float
    related_keywords: List[str]
    sentiment_distribution: Dict[str, float]
    peak_activity_time: datetime


class SocialMediaMonitoringAgent(BaseAgent):
    """
    Social Media Monitoring Agent for tracking brand presence,
    sentiment, and engagement across social platforms.
    """
    
    def __init__(self, agent_id: str = "socialmediamonitoringagent"):
        capabilities = ["social_media_monitoring", "sentiment_analysis"]
        super().__init__(agent_id, "SocialMediaMonitoringAgent", "communication", capabilities)
        self.mentions = []
        self.trending_topics = []
        self.sentiment_history = {}
        self.competitor_mentions = {}
        self.engagement_metrics = {}
        self.brand_keywords = []
        self.monitored_platforms = []
        
    async def initialize(self):
        """Initialize the agent with monitoring parameters"""
        await super().initialize()
        
        # Setup monitoring parameters
        self._setup_brand_keywords()
        self._setup_monitored_platforms()
        self._setup_sentiment_analysis()
        
        # Subscribe to relevant message types
        await self.subscribe_to_messages([
            "social_data_update",
            "brand_mention_alert",
            "competitor_analysis_request",
            "sentiment_analysis_request",
            "trend_analysis_request",
            "engagement_report_request"
        ])
        
        self.logger.info("Social Media Monitoring Agent initialized")
        
    def _setup_brand_keywords(self):
        """Setup brand keywords to monitor"""
        self.brand_keywords = [
            "company_name",
            "brand_name",
            "product_names",
            "ceo_name",
            "key_executives",
            "hashtag_campaigns",
            "branded_terms"
        ]
        
    def _setup_monitored_platforms(self):
        """Setup social media platforms to monitor"""
        self.monitored_platforms = [
            {
                'name': 'linkedin',
                'priority': 'high',
                'update_frequency': 'hourly',
                'metrics': ['likes', 'comments', 'shares', 'views']
            },
            {
                'name': 'facebook',
                'priority': 'medium',
                'update_frequency': 'hourly',
                'metrics': ['likes', 'comments', 'shares', 'reach']
            },
            {
                'name': 'instagram',
                'priority': 'medium',
                'update_frequency': 'daily',
                'metrics': ['likes', 'comments', 'saves', 'reach']
            },
            {
                'name': 'youtube',
                'priority': 'low',
                'update_frequency': 'daily',
                'metrics': ['views', 'likes', 'comments', 'subscribers']
            }
        ]
        
    def _setup_sentiment_analysis(self):
        """Setup sentiment analysis parameters"""
        self.sentiment_categories = {
            'positive': {'score_range': (0.6, 1.0), 'keywords': ['great', 'excellent', 'love', 'amazing']},
            'neutral': {'score_range': (0.4, 0.6), 'keywords': ['okay', 'fine', 'average']},
            'negative': {'score_range': (0.0, 0.4), 'keywords': ['bad', 'terrible', 'hate', 'awful']}
        }

    async def process_message(self, message: AgentMessage):
        """Process incoming messages and handle monitoring requests"""
        try:
            if message.message_type == "social_data_update":
                await self._handle_social_data_update(message)
            elif message.message_type == "brand_mention_alert":
                await self._handle_brand_mention_alert(message)
            elif message.message_type == "competitor_analysis_request":
                await self._handle_competitor_analysis_request(message)
            elif message.message_type == "sentiment_analysis_request":
                await self._handle_sentiment_analysis_request(message)
            elif message.message_type == "trend_analysis_request":
                await self._handle_trend_analysis_request(message)
            elif message.message_type == "engagement_report_request":
                await self._handle_engagement_report_request(message)
                
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            
    async def _handle_social_data_update(self, message: AgentMessage):
        """Handle incoming social media data updates"""
        social_data = message.content
        
        # Process mentions
        mentions = social_data.get('mentions', [])
        for mention_data in mentions:
            mention = await self._process_mention(mention_data)
            self.mentions.append(mention)
            
            # Check for urgent mentions requiring immediate attention
            if await self._is_urgent_mention(mention):
                await self._send_urgent_mention_alert(mention)
                
        # Update trending topics
        await self._update_trending_topics(social_data.get('trending', []))
        
        # Update engagement metrics
        await self._update_engagement_metrics(social_data.get('engagement', {}))
        
        # Analyze sentiment trends
        sentiment_analysis = await self._analyze_sentiment_trends()
        
        # Send insights to content writing agent
        insights = {
            'trending_topics': self.trending_topics[-10:],  # Last 10 trends
            'sentiment_summary': sentiment_analysis,
            'engagement_patterns': self.engagement_metrics,
            'mention_volume': len([m for m in self.mentions 
                                 if m.timestamp > datetime.now() - timedelta(hours=24)])
        }
        
        insights_message = AgentMessage(
            sender_id=self.agent_id,
            recipient_id="content_writing_agent",
            message_type="social_media_insights",
            content=insights
        )
        await self.send_message(insights_message)
        
    async def _process_mention(self, mention_data: Dict[str, Any]) -> SocialMention:
        """Process a social media mention"""
        # Analyze sentiment
        sentiment = await self._analyze_mention_sentiment(mention_data.get('content', ''))
        
        # Calculate influence score
        influence_score = await self._calculate_influence_score(mention_data)
        
        mention = SocialMention(
            mention_id=mention_data.get('id', f"mention_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            platform=mention_data.get('platform', 'unknown'),
            author=mention_data.get('author', 'anonymous'),
            content=mention_data.get('content', ''),
            timestamp=datetime.fromisoformat(mention_data.get('timestamp', datetime.now().isoformat())),
            sentiment=sentiment,
            engagement_metrics=mention_data.get('engagement', {}),
            reach=mention_data.get('reach', 0),
            influence_score=influence_score
        )
        
        return mention
        
    async def _analyze_mention_sentiment(self, content: str) -> str:
        """Analyze sentiment of a mention"""
        content_lower = content.lower()
        
        positive_score = 0
        negative_score = 0
        
        # Simple keyword-based sentiment analysis
        for sentiment, config in self.sentiment_categories.items():
            for keyword in config['keywords']:
                if keyword in content_lower:
                    if sentiment == 'positive':
                        positive_score += 1
                    elif sentiment == 'negative':
                        negative_score += 1
                        
        if positive_score > negative_score:
            return 'positive'
        elif negative_score > positive_score:
            return 'negative'
        else:
            return 'neutral'
            
    async def _calculate_influence_score(self, mention_data: Dict[str, Any]) -> float:
        """Calculate influence score for a mention"""
        engagement = mention_data.get('engagement', {})
        follower_count = mention_data.get('author_followers', 0)
        reach = mention_data.get('reach', 0)
        
        # Simple influence calculation
        engagement_score = sum(engagement.values()) if engagement else 0
        follower_score = min(follower_count / 1000, 100)  # Cap at 100
        reach_score = min(reach / 1000, 100)  # Cap at 100
        
        return (engagement_score + follower_score + reach_score) / 3
        
    async def _is_urgent_mention(self, mention: SocialMention) -> bool:
        """Determine if a mention requires urgent attention"""
        urgent_keywords = ['crisis', 'problem', 'issue', 'complaint', 'lawsuit']
        content_lower = mention.content.lower()
        
        # Check for urgent keywords
        if any(keyword in content_lower for keyword in urgent_keywords):
            return True
            
        # Check for high influence negative mentions
        if mention.sentiment == 'negative' and mention.influence_score > 50:
            return True
            
        # Check for viral mentions
        if mention.reach > 10000:
            return True
            
        return False
        
    async def _send_urgent_mention_alert(self, mention: SocialMention):
        """Send urgent mention alert"""
        alert = AgentMessage(
            sender_id=self.agent_id,
            recipient_id="customer_service_agent",
            message_type="urgent_mention_alert",
            content={
                'mention': mention.__dict__,
                'urgency_level': 'high',
                'recommended_action': 'immediate_response',
                'escalation_needed': mention.influence_score > 75
            }
        )
        await self.send_message(alert)
        
    async def _update_trending_topics(self, trending_data: List[Dict[str, Any]]):
        """Update trending topics analysis"""
        for trend_data in trending_data:
            trend = TrendAnalysis(
                trend_id=trend_data.get('id', f"trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                topic=trend_data.get('topic', ''),
                platforms=trend_data.get('platforms', []),
                trend_score=trend_data.get('score', 0.0),
                growth_rate=trend_data.get('growth_rate', 0.0),
                related_keywords=trend_data.get('keywords', []),
                sentiment_distribution=trend_data.get('sentiment', {}),
                peak_activity_time=datetime.fromisoformat(
                    trend_data.get('peak_time', datetime.now().isoformat())
                )
            )
            self.trending_topics.append(trend)
            
        # Keep only recent trends (last 7 days)
        cutoff_date = datetime.now() - timedelta(days=7)
        self.trending_topics = [t for t in self.trending_topics 
                               if t.peak_activity_time > cutoff_date]
        
    async def _update_engagement_metrics(self, engagement_data: Dict[str, Any]):
        """Update engagement metrics"""
        for platform, metrics in engagement_data.items():
            if platform not in self.engagement_metrics:
                self.engagement_metrics[platform] = []
                
            metric_entry = {
                'timestamp': datetime.now(),
                'metrics': metrics,
                'growth_rate': await self._calculate_engagement_growth(platform, metrics)
            }
            
            self.engagement_metrics[platform].append(metric_entry)
            
            # Keep only last 30 days of metrics
            cutoff_date = datetime.now() - timedelta(days=30)
            self.engagement_metrics[platform] = [
                entry for entry in self.engagement_metrics[platform]
                if entry['timestamp'] > cutoff_date
            ]
            
    async def _calculate_engagement_growth(self, platform: str, current_metrics: Dict[str, int]) -> float:
        """Calculate engagement growth rate"""
        historical_metrics = self.engagement_metrics.get(platform, [])
        
        if not historical_metrics:
            return 0.0
            
        # Compare with metrics from 24 hours ago
        yesterday = datetime.now() - timedelta(days=1)
        historical_entry = None
        
        for entry in reversed(historical_metrics):
            if entry['timestamp'] <= yesterday:
                historical_entry = entry
                break
                
        if not historical_entry:
            return 0.0
            
        # Calculate growth rate
        current_total = sum(current_metrics.values())
        historical_total = sum(historical_entry['metrics'].values())
        
        if historical_total == 0:
            return 0.0
            
        growth_rate = ((current_total - historical_total) / historical_total) * 100
        return growth_rate
        
    async def _analyze_sentiment_trends(self) -> Dict[str, Any]:
        """Analyze sentiment trends over time"""
        recent_mentions = [m for m in self.mentions 
                          if m.timestamp > datetime.now() - timedelta(days=7)]
        
        if not recent_mentions:
            return {'overall_sentiment': 'neutral', 'sentiment_distribution': {}, 'trend': 'stable'}
            
        # Calculate sentiment distribution
        sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        for mention in recent_mentions:
            sentiment_counts[mention.sentiment] += 1
            
        total_mentions = len(recent_mentions)
        sentiment_distribution = {
            sentiment: (count / total_mentions) * 100
            for sentiment, count in sentiment_counts.items()
        }
        
        # Determine overall sentiment
        if sentiment_distribution['positive'] > 50:
            overall_sentiment = 'positive'
        elif sentiment_distribution['negative'] > 30:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
            
        # Analyze trend (compare with previous week)
        prev_week_mentions = [m for m in self.mentions 
                             if datetime.now() - timedelta(days=14) <= m.timestamp <= datetime.now() - timedelta(days=7)]
        
        trend = 'stable'
        if prev_week_mentions:
            prev_positive_rate = len([m for m in prev_week_mentions if m.sentiment == 'positive']) / len(prev_week_mentions)
            current_positive_rate = sentiment_distribution['positive'] / 100
            
            if current_positive_rate > prev_positive_rate + 0.1:
                trend = 'improving'
            elif current_positive_rate < prev_positive_rate - 0.1:
                trend = 'declining'
                
        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_distribution': sentiment_distribution,
            'trend': trend,
            'total_mentions': total_mentions,
            'average_influence_score': sum(m.influence_score for m in recent_mentions) / total_mentions
        }
        
    async def _handle_competitor_analysis_request(self, message: AgentMessage):
        """Handle competitor analysis requests"""
        request = message.content
        competitors = request.get('competitors', [])
        
        competitor_analysis = {}
        
        for competitor in competitors:
            competitor_mentions = [m for m in self.mentions if competitor.lower() in m.content.lower()]
            
            if competitor_mentions:
                analysis = {
                    'mention_count': len(competitor_mentions),
                    'sentiment_distribution': await self._calculate_competitor_sentiment(competitor_mentions),
                    'average_engagement': sum(sum(m.engagement_metrics.values()) for m in competitor_mentions) / len(competitor_mentions),
                    'trending_topics': await self._extract_competitor_topics(competitor_mentions)
                }
                competitor_analysis[competitor] = analysis
                
        response = AgentMessage(
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type="competitor_analysis_response",
            content=competitor_analysis
        )
        await self.send_message(response)
        
    async def _calculate_competitor_sentiment(self, mentions: List[SocialMention]) -> Dict[str, float]:
        """Calculate sentiment distribution for competitor mentions"""
        sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        
        for mention in mentions:
            sentiment_counts[mention.sentiment] += 1
            
        total = len(mentions)
        return {sentiment: (count / total) * 100 for sentiment, count in sentiment_counts.items()}
        
    async def _extract_competitor_topics(self, mentions: List[SocialMention]) -> List[str]:
        """Extract trending topics for competitor mentions"""
        # Simple keyword extraction
        all_content = ' '.join(m.content for m in mentions).lower()
        common_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        
        words = all_content.split()
        word_counts = {}
        
        for word in words:
            if word not in common_words and len(word) > 3:
                word_counts[word] = word_counts.get(word, 0) + 1
                
        # Return top 10 most frequent words
        return sorted(word_counts.keys(), key=lambda x: word_counts[x], reverse=True)[:10]

    async def get_status(self) -> Dict[str, Any]:
        """Get current status of the Social Media Monitoring Agent"""
        recent_mentions = [m for m in self.mentions 
                          if m.timestamp > datetime.now() - timedelta(hours=24)]
        
        sentiment_summary = await self._analyze_sentiment_trends()
        
        return {
            'agent_id': self.agent_id,
            'status': 'active',
            'total_mentions': len(self.mentions),
            'recent_mentions_24h': len(recent_mentions),
            'monitored_platforms': len(self.monitored_platforms),
            'trending_topics_count': len(self.trending_topics),
            'overall_sentiment': sentiment_summary.get('overall_sentiment', 'neutral'),
            'sentiment_trend': sentiment_summary.get('trend', 'stable'),
            'brand_keywords': len(self.brand_keywords)
        }
    async def process_task(self, task) -> Dict[str, Any]:
        """Process assigned tasks - accepts both AgentTask objects and dicts"""
        try:
            # Handle both AgentTask objects and plain dictionaries
            if hasattr(task, 'task_type'):
                task_type = task.task_type
                parameters = task.parameters
            else:
                task_type = task.get('type', 'unknown')
                parameters = task
            
            if task_type == 'status_check':
                return {"status": "completed", "agent_status": "active"}
            elif task_type == 'ping':
                return {"status": "completed", "response": "pong"}
            elif task_type == 'build_brand_presence':
                return await self._build_brand_presence(parameters)
            else:
                return {"status": "failed", "error": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            self.logger.error(f"Error processing task: {str(e)}")
            return {"status": "failed", "error": str(e)}
            
    async def _build_brand_presence(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Build brand presence strategy"""
        try:
            brand_voice = parameters.get('brand_voice', 'professional')
            platforms = parameters.get('target_platforms', ['linkedin'])
            themes = parameters.get('content_themes', ['general'])
            
            # Create brand presence plan
            presence_plan = {
                "strategy_id": f"brand_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "brand_voice": brand_voice,
                "target_platforms": platforms,
                "content_themes": themes,
                "posting_schedule": {
                    "linkedin": "daily",
                    "twitter": "3x_daily",
                    "medium": "weekly"
                },
                "engagement_targets": {
                    "month_1": {"followers": 100, "engagement_rate": 2.0},
                    "month_3": {"followers": 500, "engagement_rate": 3.5},
                    "month_6": {"followers": 1500, "engagement_rate": 5.0}
                }
            }
            
            return {
                "status": "completed",
                "strategy_id": presence_plan["strategy_id"],
                "platforms_configured": len(platforms),
                "content_themes": len(themes),
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle incoming messages from other agents"""
        try:
            # Default handling - can be overridden by specific agents
            self.logger.info(f"Received message of type: {message.message_type}")
            
            if message.message_type == "ping":
                response = AgentMessage(
                    id=str(uuid.uuid4()),
                    source_agent=self.agent_id,
                    target_agent=message.source_agent,
                    message_type="pong",
                    payload={"response": "pong"},
                    timestamp=datetime.now()
                )
                return response
            
            self.performance_metrics["messages_processed"] += 1
            return None
            
        except Exception as e:
            self.logger.error(f"Error handling message: {str(e)}")
            self.performance_metrics["errors"] += 1
            return None

