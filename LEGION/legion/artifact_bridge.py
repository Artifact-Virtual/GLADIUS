"""
LEGION-ARTIFACT Integration Bridge
==================================

This module provides integration between LEGION agents and Artifact's native
infrastructure. It routes LEGION's operations through Artifact's connectors.

Key Integrations:
- Social Media: Route through Artifact/deployment/automata/social_media
- ERP: Route through Artifact/deployment/automata/erp_integrations
- Publishing: Route through Artifact/deployment/automata/publishing
- AI: Route through GLADIUS native model

Author: Artifact Virtual Systems
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

# Setup paths
GLADIUS_ROOT = Path(__file__).parent.parent.parent
ARTIFACT_ROOT = GLADIUS_ROOT / "Artifact"
AUTOMATA_ROOT = ARTIFACT_ROOT / "deployment" / "automata"

sys.path.insert(0, str(GLADIUS_ROOT))
sys.path.insert(0, str(ARTIFACT_ROOT))
sys.path.insert(0, str(AUTOMATA_ROOT))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LEGION.ArtifactBridge")


@dataclass
class BridgeResult:
    """Result from bridge operation"""
    success: bool
    data: Any
    error: Optional[str]
    source: str  # Which connector was used


class ArtifactBridge:
    """
    Bridge between LEGION agents and Artifact infrastructure.
    
    Routes all LEGION operations through Artifact's native connectors,
    ensuring unified integrations and avoiding duplicate implementations.
    """
    
    def __init__(self):
        self.gladius_root = GLADIUS_ROOT
        self.artifact_root = ARTIFACT_ROOT
        self.automata_root = AUTOMATA_ROOT
        
        # Lazy-loaded connectors
        self._social_manager = None
        self._erp_manager = None
        self._gladius_router = None
        
        # Track available integrations
        self.available_integrations = self._discover_integrations()
        
        logger.info(f"ArtifactBridge initialized with {len(self.available_integrations)} integrations")
    
    def _discover_integrations(self) -> Dict[str, bool]:
        """Discover available Artifact integrations"""
        integrations = {}
        
        # Social Media
        social_path = self.automata_root / "social_media" / "platforms"
        integrations["discord"] = (social_path / "discord_connector.py").exists() or \
                                  (self.artifact_root / "arty" / "discord").exists()
        integrations["twitter"] = (social_path / "twitter_connector.py").exists()
        integrations["linkedin"] = (social_path / "linkedin_connector.py").exists()
        integrations["facebook"] = (social_path / "facebook_connector.py").exists()
        integrations["instagram"] = (social_path / "instagram_connector.py").exists()
        integrations["youtube"] = (social_path / "youtube_connector.py").exists()
        
        # ERP
        erp_path = self.automata_root / "erp_integrations"
        integrations["erp"] = erp_path.exists()
        
        # Publishing
        publishing_path = self.automata_root / "publishing"
        integrations["publishing"] = publishing_path.exists()
        
        # GLADIUS
        gladius_path = GLADIUS_ROOT / "GLADIUS"
        integrations["gladius"] = gladius_path.exists()
        
        return integrations
    
    # ==================== GLADIUS AI ====================
    
    @property
    def gladius_router(self):
        """Lazy load GLADIUS router"""
        if self._gladius_router is None:
            try:
                from GLADIUS.router.pattern_router import NativeToolRouter
                self._gladius_router = NativeToolRouter()
                logger.info("GLADIUS router loaded")
            except ImportError as e:
                logger.warning(f"GLADIUS router not available: {e}")
                self._gladius_router = None
        return self._gladius_router
    
    async def query_gladius(self, query: str, context: Optional[Dict] = None) -> BridgeResult:
        """Query GLADIUS for AI operations"""
        if not self.gladius_router:
            return BridgeResult(
                success=False,
                data=None,
                error="GLADIUS router not available",
                source="gladius"
            )
        
        try:
            result = self.gladius_router.route(query)
            # Handle ToolRoutingResult dataclass
            data = {
                "tool": result.tool_name,
                "confidence": result.confidence,
                "latency_ms": result.latency_ms,
                "source": result.source,
                "success": result.success
            }
            return BridgeResult(
                success=result.success,
                data=data,
                error=result.error,
                source="gladius"
            )
        except Exception as e:
            return BridgeResult(
                success=False,
                data=None,
                error=str(e),
                source="gladius"
            )
    
    # ==================== SOCIAL MEDIA ====================
    
    @property
    def social_manager(self):
        """Lazy load social media manager"""
        if self._social_manager is None:
            try:
                from social_media.manager import SocialMediaManager
                self._social_manager = SocialMediaManager()
                logger.info("Social media manager loaded")
            except ImportError as e:
                logger.warning(f"Social media manager not available: {e}")
                self._social_manager = None
        return self._social_manager
    
    async def post_to_social(
        self,
        platform: str,
        content: str,
        media_urls: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> BridgeResult:
        """
        Post content to a social media platform using Artifact connectors.
        
        This replaces LEGION's Selenium-based approach with API-based connectors.
        """
        platform = platform.lower()
        
        if not self.available_integrations.get(platform):
            return BridgeResult(
                success=False,
                data=None,
                error=f"Platform {platform} not available in Artifact",
                source=f"artifact.social.{platform}"
            )
        
        try:
            # Route to appropriate Artifact connector
            if platform == "discord":
                result = await self._post_discord(content, media_urls, metadata)
            elif platform == "twitter":
                result = await self._post_twitter(content, media_urls, metadata)
            elif platform == "linkedin":
                result = await self._post_linkedin(content, media_urls, metadata)
            elif platform == "facebook":
                result = await self._post_facebook(content, media_urls, metadata)
            else:
                return BridgeResult(
                    success=False,
                    data=None,
                    error=f"Unsupported platform: {platform}",
                    source=f"artifact.social.{platform}"
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Social post error ({platform}): {e}")
            return BridgeResult(
                success=False,
                data=None,
                error=str(e),
                source=f"artifact.social.{platform}"
            )
    
    async def _post_discord(
        self,
        content: str,
        media_urls: Optional[List[str]],
        metadata: Optional[Dict]
    ) -> BridgeResult:
        """Post to Discord using Artifact's arty bot"""
        try:
            # Use arty's discord module
            from Artifact.arty.discord import discord_bot
            
            channel_id = metadata.get("channel_id") if metadata else None
            result = await discord_bot.send_message(channel_id, content)
            
            return BridgeResult(
                success=True,
                data={"message_id": result},
                error=None,
                source="artifact.arty.discord"
            )
        except ImportError:
            # Fallback: Try direct connector
            try:
                from social_media.platforms.discord_connector import DiscordConnector
                connector = DiscordConnector()
                result = await connector.post(content)
                return BridgeResult(
                    success=True,
                    data=result,
                    error=None,
                    source="artifact.social.discord"
                )
            except Exception as e:
                return BridgeResult(
                    success=False,
                    data=None,
                    error=str(e),
                    source="artifact.social.discord"
                )
    
    async def _post_twitter(
        self,
        content: str,
        media_urls: Optional[List[str]],
        metadata: Optional[Dict]
    ) -> BridgeResult:
        """Post to Twitter using Artifact connector"""
        try:
            from social_media.platforms.twitter_connector import TwitterConnector
            connector = TwitterConnector()
            result = await connector.post_tweet(content, media_urls)
            return BridgeResult(
                success=True,
                data=result,
                error=None,
                source="artifact.social.twitter"
            )
        except Exception as e:
            return BridgeResult(
                success=False,
                data=None,
                error=str(e),
                source="artifact.social.twitter"
            )
    
    async def _post_linkedin(
        self,
        content: str,
        media_urls: Optional[List[str]],
        metadata: Optional[Dict]
    ) -> BridgeResult:
        """Post to LinkedIn using Artifact connector"""
        try:
            from social_media.platforms.linkedin_connector import LinkedInConnector
            connector = LinkedInConnector()
            result = await connector.post_update(content, media_urls)
            return BridgeResult(
                success=True,
                data=result,
                error=None,
                source="artifact.social.linkedin"
            )
        except Exception as e:
            return BridgeResult(
                success=False,
                data=None,
                error=str(e),
                source="artifact.social.linkedin"
            )
    
    async def _post_facebook(
        self,
        content: str,
        media_urls: Optional[List[str]],
        metadata: Optional[Dict]
    ) -> BridgeResult:
        """Post to Facebook using Artifact connector"""
        try:
            from social_media.platforms.facebook_connector import FacebookConnector
            connector = FacebookConnector()
            result = await connector.post(content, media_urls)
            return BridgeResult(
                success=True,
                data=result,
                error=None,
                source="artifact.social.facebook"
            )
        except Exception as e:
            return BridgeResult(
                success=False,
                data=None,
                error=str(e),
                source="artifact.social.facebook"
            )
    
    # ==================== ERP OPERATIONS ====================
    
    @property
    def erp_manager(self):
        """Lazy load ERP manager"""
        if self._erp_manager is None:
            try:
                from erp_integrations import ERPManager
                self._erp_manager = ERPManager()
                logger.info("ERP manager loaded")
            except ImportError as e:
                logger.warning(f"ERP manager not available: {e}")
                self._erp_manager = None
        return self._erp_manager
    
    async def erp_sync(self, entity_type: str, data: Dict) -> BridgeResult:
        """
        Sync data with ERP system using Artifact connectors.
        
        Entity types: customers, products, orders, inventory
        """
        if not self.available_integrations.get("erp"):
            return BridgeResult(
                success=False,
                data=None,
                error="ERP integration not available",
                source="artifact.erp"
            )
        
        try:
            from erp_integrations.sync_manager import ERPSyncManager
            manager = ERPSyncManager()
            
            if entity_type == "customers":
                result = await manager.sync_customers(data)
            elif entity_type == "products":
                result = await manager.sync_products(data)
            elif entity_type == "orders":
                result = await manager.sync_orders(data)
            elif entity_type == "inventory":
                result = await manager.sync_inventory(data)
            else:
                return BridgeResult(
                    success=False,
                    data=None,
                    error=f"Unknown entity type: {entity_type}",
                    source="artifact.erp"
                )
            
            return BridgeResult(
                success=True,
                data=result,
                error=None,
                source="artifact.erp"
            )
            
        except Exception as e:
            return BridgeResult(
                success=False,
                data=None,
                error=str(e),
                source="artifact.erp"
            )
    
    # ==================== PUBLISHING ====================
    
    async def publish_content(
        self,
        content_type: str,
        content: str,
        platforms: List[str],
        metadata: Optional[Dict] = None
    ) -> BridgeResult:
        """
        Publish content using Artifact publishing pipeline.
        """
        try:
            from publishing.content_publisher import ContentPublisher
            publisher = ContentPublisher()
            
            result = await publisher.publish(
                content_type=content_type,
                content=content,
                platforms=platforms,
                metadata=metadata
            )
            
            return BridgeResult(
                success=True,
                data=result,
                error=None,
                source="artifact.publishing"
            )
            
        except Exception as e:
            return BridgeResult(
                success=False,
                data=None,
                error=str(e),
                source="artifact.publishing"
            )
    
    # ==================== STATUS ====================
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all integrations"""
        return {
            "bridge": "active",
            "gladius_available": self.gladius_router is not None,
            "social_manager_available": self.social_manager is not None,
            "erp_available": self.erp_manager is not None,
            "integrations": self.available_integrations,
            "timestamp": datetime.now().isoformat()
        }


# Singleton instance
_bridge_instance: Optional[ArtifactBridge] = None


def get_bridge() -> ArtifactBridge:
    """Get or create ArtifactBridge instance"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = ArtifactBridge()
    return _bridge_instance


# Convenience functions for LEGION agents
async def post_social(platform: str, content: str, **kwargs) -> BridgeResult:
    """Post to social media via Artifact bridge"""
    bridge = get_bridge()
    return await bridge.post_to_social(platform, content, **kwargs)


async def sync_erp(entity_type: str, data: Dict) -> BridgeResult:
    """Sync with ERP via Artifact bridge"""
    bridge = get_bridge()
    return await bridge.erp_sync(entity_type, data)


async def query_ai(query: str, context: Optional[Dict] = None) -> BridgeResult:
    """Query GLADIUS via Artifact bridge"""
    bridge = get_bridge()
    return await bridge.query_gladius(query, context)
