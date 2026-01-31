#!/usr/bin/env python3
"""
GLADIUS Twitter Autonomous Agent
================================

Fully autonomous Twitter management powered by GLADIUS AI.
Monitors mentions, replies contextually, posts intelligently.

Features:
- Real-time mention monitoring
- Contextual reply generation using GLADIUS
- Sentiment-aware engagement
- Learning from interactions (stored in Hektor)
- Rate-limited, policy-compliant automation

Author: Artifact Virtual Systems
"""

import os
import sys
import json
import asyncio
import logging
import aiohttp
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import hashlib

# Add paths
GLADIUS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(GLADIUS_ROOT))

# Import GLADIUS components
try:
    from GLADIUS.speak import GladiusInterface
    GLADIUS_AVAILABLE = True
except ImportError:
    GLADIUS_AVAILABLE = False

try:
    from GLADIUS.utils.hektor_memory import get_memory_manager
    HEKTOR_AVAILABLE = True
except ImportError:
    HEKTOR_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GLADIUS.TwitterAgent")


class TweetType(Enum):
    MENTION = "mention"
    REPLY = "reply"
    QUOTE = "quote"
    DIRECT_MESSAGE = "dm"
    TIMELINE = "timeline"


@dataclass
class Tweet:
    """Represents a tweet for processing."""
    id: str
    text: str
    author_id: str
    author_username: str
    created_at: str
    tweet_type: TweetType
    conversation_id: Optional[str] = None
    in_reply_to: Optional[str] = None
    referenced_tweets: Optional[List[Dict]] = None
    metrics: Optional[Dict] = None


class GladiusTwitterAgent:
    """
    Autonomous Twitter agent powered by GLADIUS.
    
    Handles:
    - Mention monitoring and contextual replies
    - Intelligent engagement with followers
    - Content generation and posting
    - Learning from interactions
    """
    
    API_BASE = "https://api.twitter.com/2"
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Twitter agent.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or str(
            GLADIUS_ROOT.parent / "config" / "twitter_agent.json"
        )
        self.config = self._load_config()
        
        # Twitter API credentials
        self.bearer_token = self.config.get("bearer_token") or os.getenv("TWITTER_BEARER_TOKEN")
        self.api_key = self.config.get("api_key") or os.getenv("TWITTER_API_KEY")
        self.api_secret = self.config.get("api_secret") or os.getenv("TWITTER_API_SECRET")
        self.access_token = self.config.get("access_token") or os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_secret = self.config.get("access_token_secret") or os.getenv("TWITTER_ACCESS_SECRET")
        
        # Agent state
        self.user_id: Optional[str] = None
        self.username: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = False
        self.last_mention_id: Optional[str] = None
        
        # GLADIUS interface
        self.gladius: Optional[GladiusInterface] = None
        if GLADIUS_AVAILABLE:
            try:
                self.gladius = GladiusInterface(verbose=False, direct=True)
                logger.info(f"GLADIUS connected: {self.gladius.model}")
            except Exception as e:
                logger.warning(f"GLADIUS initialization failed: {e}")
        
        # Memory for learning
        self.memory = get_memory_manager() if HEKTOR_AVAILABLE else None
        
        # Processing queue
        self.tweet_queue: asyncio.Queue = asyncio.Queue()
        
        # Rate limiting
        self.rate_limits = {
            "mentions_check": 60,      # Seconds between checks
            "reply_cooldown": 30,      # Min seconds between replies
            "posts_per_hour": 10,      # Max posts per hour
            "replies_per_hour": 30     # Max replies per hour
        }
        self.post_count = 0
        self.reply_count = 0
        self.last_hour_reset = datetime.now()
        
        logger.info("GLADIUS Twitter Agent initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        default_config = {
            "enabled": True,
            "auto_reply": True,
            "auto_like": True,
            "reply_to_mentions": True,
            "reply_to_replies": True,
            "personality": "professional_friendly",
            "topics": ["AI", "technology", "innovation", "automation"],
            "response_style": {
                "max_length": 280,
                "include_hashtags": True,
                "mention_author": True
            },
            "posting_schedule": {
                "enabled": True,
                "posts_per_day": 3,
                "best_times": ["09:00", "12:00", "18:00"]
            },
            "filters": {
                "min_follower_count": 0,
                "block_keywords": ["spam", "giveaway", "free followers"],
                "priority_keywords": ["AI", "AGI", "machine learning", "Artifact"]
            }
        }
        
        try:
            if Path(self.config_path).exists():
                with open(self.config_path) as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
        except Exception as e:
            logger.warning(f"Could not load config: {e}")
        
        return default_config
    
    async def authenticate(self) -> bool:
        """Authenticate with Twitter API."""
        if not self.bearer_token:
            logger.error("No Twitter bearer token configured")
            return False
        
        try:
            self.session = aiohttp.ClientSession()
            
            headers = {
                "Authorization": f"Bearer {self.bearer_token}"
            }
            
            async with self.session.get(
                f"{self.API_BASE}/users/me",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.user_id = data["data"]["id"]
                    self.username = data["data"]["username"]
                    logger.info(f"Authenticated as @{self.username}")
                    return True
                else:
                    error = await response.text()
                    logger.error(f"Authentication failed: {error}")
                    return False
                    
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    async def fetch_mentions(self) -> List[Tweet]:
        """Fetch recent mentions."""
        if not self.user_id:
            return []
        
        try:
            headers = {
                "Authorization": f"Bearer {self.bearer_token}"
            }
            
            params = {
                "tweet.fields": "created_at,conversation_id,in_reply_to_user_id,referenced_tweets,public_metrics",
                "expansions": "author_id,referenced_tweets.id",
                "user.fields": "username,public_metrics"
            }
            
            if self.last_mention_id:
                params["since_id"] = self.last_mention_id
            
            url = f"{self.API_BASE}/users/{self.user_id}/mentions"
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "data" not in data:
                        return []
                    
                    # Parse users for username lookup
                    users = {}
                    if "includes" in data and "users" in data["includes"]:
                        for user in data["includes"]["users"]:
                            users[user["id"]] = user["username"]
                    
                    tweets = []
                    for tweet_data in data["data"]:
                        tweet = Tweet(
                            id=tweet_data["id"],
                            text=tweet_data["text"],
                            author_id=tweet_data["author_id"],
                            author_username=users.get(tweet_data["author_id"], "unknown"),
                            created_at=tweet_data["created_at"],
                            tweet_type=TweetType.MENTION,
                            conversation_id=tweet_data.get("conversation_id"),
                            in_reply_to=tweet_data.get("in_reply_to_user_id"),
                            referenced_tweets=tweet_data.get("referenced_tweets"),
                            metrics=tweet_data.get("public_metrics")
                        )
                        tweets.append(tweet)
                        
                        # Update last seen ID
                        if not self.last_mention_id or tweet.id > self.last_mention_id:
                            self.last_mention_id = tweet.id
                    
                    logger.info(f"Fetched {len(tweets)} new mentions")
                    return tweets
                else:
                    logger.warning(f"Failed to fetch mentions: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching mentions: {e}")
            return []
    
    async def generate_reply(self, tweet: Tweet) -> Optional[str]:
        """
        Generate a contextual reply using GLADIUS.
        
        Args:
            tweet: The tweet to reply to
            
        Returns:
            Generated reply text or None
        """
        if not self.gladius:
            logger.warning("GLADIUS not available for reply generation")
            return None
        
        try:
            # Build context for GLADIUS
            context_parts = [
                f"You are the AI for Artifact Virtual (@{self.username} on Twitter).",
                f"Generate a reply to this tweet from @{tweet.author_username}:",
                f'"{tweet.text}"',
                "",
                "Guidelines:",
                "- Be helpful, intelligent, and engaging",
                "- Keep response under 280 characters",
                "- Be conversational but professional",
                "- If asked a technical question, provide accurate info",
                "- Include relevant hashtags if appropriate",
                f"- Address @{tweet.author_username} naturally"
            ]
            
            # Add memory context if available
            if self.memory:
                try:
                    # Search for relevant past interactions
                    memories = self.memory.recall(
                        tweet.text,
                        store="conversations",
                        top_k=3
                    )
                    if memories:
                        context_parts.append("\nRelevant past context:")
                        for m in memories[:2]:
                            if m.get('score', 0) > 0.3:
                                context_parts.append(f"- {m.get('text', '')[:100]}")
                except Exception as e:
                    logger.debug(f"Memory recall failed: {e}")
            
            prompt = "\n".join(context_parts)
            
            # Query GLADIUS
            result = self.gladius.query(prompt, include_system=True)
            
            if result.get("success"):
                reply = result.get("response", "").strip()
                
                # Ensure reply fits Twitter limit
                if len(reply) > 280:
                    reply = reply[:277] + "..."
                
                # Store interaction for learning
                if self.memory:
                    try:
                        self.memory.remember(
                            f"Tweet from @{tweet.author_username}: {tweet.text}\nReply: {reply}",
                            store="conversations",
                            doc_type="twitter_interaction",
                            source=f"tweet_{tweet.id}"
                        )
                    except Exception as e:
                        logger.debug(f"Failed to store interaction: {e}")
                
                return reply
            else:
                logger.warning(f"GLADIUS reply generation failed: {result.get('error')}")
                return None
                
        except Exception as e:
            logger.error(f"Reply generation error: {e}")
            return None
    
    async def post_reply(self, tweet: Tweet, reply_text: str) -> bool:
        """
        Post a reply to a tweet.
        
        Args:
            tweet: Original tweet
            reply_text: Reply text
            
        Returns:
            True if posted successfully
        """
        # Check rate limits
        await self._check_rate_limits()
        
        if self.reply_count >= self.rate_limits["replies_per_hour"]:
            logger.warning("Reply rate limit reached")
            return False
        
        try:
            # OAuth 1.0a required for posting
            # This would need proper OAuth implementation
            # For now, log what would be posted
            
            logger.info(f"Would reply to @{tweet.author_username}: {reply_text[:50]}...")
            
            # In production, implement actual posting:
            # headers = self._get_oauth_headers("POST", f"{self.API_BASE}/tweets")
            # async with self.session.post(
            #     f"{self.API_BASE}/tweets",
            #     headers=headers,
            #     json={
            #         "text": reply_text,
            #         "reply": {"in_reply_to_tweet_id": tweet.id}
            #     }
            # ) as response:
            #     ...
            
            self.reply_count += 1
            return True
            
        except Exception as e:
            logger.error(f"Error posting reply: {e}")
            return False
    
    async def process_tweet(self, tweet: Tweet):
        """Process a single tweet (generate and post reply if appropriate)."""
        # Check filters
        if not self._should_engage(tweet):
            logger.debug(f"Skipping tweet {tweet.id} (filtered)")
            return
        
        # Generate reply
        reply = await self.generate_reply(tweet)
        
        if reply:
            # Post reply
            success = await self.post_reply(tweet, reply)
            if success:
                logger.info(f"Replied to @{tweet.author_username}")
            else:
                logger.warning(f"Failed to reply to @{tweet.author_username}")
    
    def _should_engage(self, tweet: Tweet) -> bool:
        """Determine if we should engage with this tweet."""
        filters = self.config.get("filters", {})
        
        # Check blocked keywords
        block_keywords = filters.get("block_keywords", [])
        for keyword in block_keywords:
            if keyword.lower() in tweet.text.lower():
                return False
        
        # Don't reply to ourselves
        if tweet.author_id == self.user_id:
            return False
        
        return True
    
    async def _check_rate_limits(self):
        """Reset rate limits if hour has passed."""
        now = datetime.now()
        if (now - self.last_hour_reset).total_seconds() >= 3600:
            self.post_count = 0
            self.reply_count = 0
            self.last_hour_reset = now
    
    async def monitor_loop(self):
        """Main monitoring loop - runs continuously."""
        logger.info("Starting Twitter monitoring loop...")
        
        while self.running:
            try:
                # Fetch new mentions
                mentions = await self.fetch_mentions()
                
                # Queue for processing
                for tweet in mentions:
                    await self.tweet_queue.put(tweet)
                
                # Wait before next check
                await asyncio.sleep(self.rate_limits["mentions_check"])
                
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                await asyncio.sleep(60)
    
    async def processing_loop(self):
        """Process queued tweets."""
        logger.info("Starting tweet processing loop...")
        
        while self.running:
            try:
                # Get tweet from queue with timeout
                try:
                    tweet = await asyncio.wait_for(
                        self.tweet_queue.get(),
                        timeout=10
                    )
                    
                    # Process tweet
                    await self.process_tweet(tweet)
                    
                    # Cooldown between replies
                    await asyncio.sleep(self.rate_limits["reply_cooldown"])
                    
                except asyncio.TimeoutError:
                    continue
                    
            except Exception as e:
                logger.error(f"Processing loop error: {e}")
                await asyncio.sleep(10)
    
    async def run(self):
        """Run the Twitter agent."""
        logger.info("Starting GLADIUS Twitter Agent...")
        
        # Authenticate
        if not await self.authenticate():
            logger.error("Failed to authenticate")
            return
        
        self.running = True
        
        # Run monitoring and processing loops
        try:
            await asyncio.gather(
                self.monitor_loop(),
                self.processing_loop()
            )
        except asyncio.CancelledError:
            logger.info("Agent cancelled")
        finally:
            self.running = False
            if self.session:
                await self.session.close()
    
    def stop(self):
        """Stop the agent."""
        logger.info("Stopping Twitter Agent...")
        self.running = False
    
    async def post_tweet(self, content: str, media_ids: List[str] = None) -> Optional[str]:
        """
        Post a new tweet.
        
        Args:
            content: Tweet text
            media_ids: Optional media IDs to attach
            
        Returns:
            Tweet ID if successful
        """
        await self._check_rate_limits()
        
        if self.post_count >= self.rate_limits["posts_per_hour"]:
            logger.warning("Post rate limit reached")
            return None
        
        logger.info(f"Would post tweet: {content[:50]}...")
        self.post_count += 1
        
        # Return mock ID for now
        return hashlib.md5(content.encode()).hexdigest()[:19]
    
    async def generate_post(self, topic: str = None) -> Optional[str]:
        """
        Generate an original post using GLADIUS.
        
        Args:
            topic: Optional topic for the post
            
        Returns:
            Generated tweet text
        """
        if not self.gladius:
            return None
        
        topics = self.config.get("topics", ["AI", "technology"])
        if not topic:
            import random
            topic = random.choice(topics)
        
        prompt = f"""Generate a thoughtful, engaging tweet about {topic} for the Artifact Virtual AI account.

Guidelines:
- Be insightful and intelligent
- Keep it under 280 characters
- Use 1-2 relevant hashtags
- Be authentic, not promotional
- Share a unique perspective or interesting observation

Generate only the tweet text, nothing else."""

        result = self.gladius.query(prompt, include_system=True)
        
        if result.get("success"):
            tweet = result.get("response", "").strip()
            if len(tweet) > 280:
                tweet = tweet[:277] + "..."
            return tweet
        
        return None


async def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GLADIUS Twitter Agent")
    parser.add_argument(
        "command",
        choices=["run", "test", "generate"],
        help="Command to execute"
    )
    parser.add_argument(
        "--topic",
        help="Topic for generate command"
    )
    
    args = parser.parse_args()
    
    agent = GladiusTwitterAgent()
    
    if args.command == "run":
        try:
            await agent.run()
        except KeyboardInterrupt:
            agent.stop()
            
    elif args.command == "test":
        if await agent.authenticate():
            print(f"✅ Authenticated as @{agent.username}")
            
            # Test mention fetch
            mentions = await agent.fetch_mentions()
            print(f"📬 Found {len(mentions)} recent mentions")
            
            for tweet in mentions[:3]:
                print(f"  - @{tweet.author_username}: {tweet.text[:50]}...")
        else:
            print("❌ Authentication failed")
            
    elif args.command == "generate":
        topic = args.topic or "artificial intelligence"
        tweet = await agent.generate_post(topic)
        if tweet:
            print(f"Generated tweet about '{topic}':")
            print(f"\n{tweet}\n")
            print(f"[{len(tweet)} characters]")
        else:
            print("Failed to generate tweet")
    
    if agent.session:
        await agent.session.close()


if __name__ == "__main__":
    asyncio.run(main())
