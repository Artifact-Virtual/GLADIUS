"""
Enterprise Automation Suite - Complete Business Automation Platform

A comprehensive, fully autonomous system with:
- AI-powered content generation with persistent memory
- Multi-platform social media management (Twitter, LinkedIn, Facebook, Instagram, YouTube)
- ERP system integration (SAP, Odoo, NetSuite, Dynamics, Salesforce)
- Autonomous scheduling with smart timing
- Self-reflection and continuous improvement
- Tool calling capabilities for AI
- Discord notifications and alerts

This suite seamlessly integrates with the business infrastructure for
complete end-to-end business operations management.

Version: 1.0.0 - Production Ready
"""

__version__ = "1.0.0"
__author__ = "Gold Standard Enterprise Automation"

# Core components
from .core.manager import EnterpriseManager
from .core.config import AutomationConfig

# AI Engine (NEW!)
from .ai_engine.generator import ContentGenerator
from .ai_engine.context_engine import ContextEngine
from .ai_engine.reflection_engine import ReflectionEngine
from .ai_engine.tool_registry import ToolRegistry
from .ai_engine.providers import (
    OpenAIProvider,
    AnthropicProvider,
    CohereProvider,
    LocalModelProvider,
    get_provider
)

# Social Media
from .social_media.manager import SocialMediaManager

# ERP Integrations  
from .erp_integrations.manager import ERPManager

# Scheduler (NEW!)
from .scheduler.orchestrator import AutomationOrchestrator

# Integrations (NEW!)
from .integrations.discord import DiscordIntegration

__all__ = [
    # Core
    "EnterpriseManager",
    "AutomationConfig",
    "__version__",
    
    # AI Engine
    "ContentGenerator",
    "ContextEngine",
    "ReflectionEngine",
    "ToolRegistry",
    "OpenAIProvider",
    "AnthropicProvider",
    "CohereProvider",
    "LocalModelProvider",
    "get_provider",
    
    # Managers
    "SocialMediaManager",
    "ERPManager",
    "AutomationOrchestrator",
    
    # Integrations
    "DiscordIntegration",
]

