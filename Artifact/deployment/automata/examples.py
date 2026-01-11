"""
Enterprise Automation Suite - Example Usage

This script demonstrates the full capabilities of the system.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
import os
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def example_full_automation():
    """Example: Full autonomous operation."""
    logger.info("=" * 60)
    logger.info("EXAMPLE 1: Full Autonomous Automation")
    logger.info("=" * 60)
    
    from core.manager import EnterpriseManager
    
    # Create manager
    manager = EnterpriseManager()
    
    # Start autonomous operation
    logger.info("Starting autonomous automation...")
    await manager.start()
    
    # Let it run for a bit
    logger.info("System is now running autonomously!")
    logger.info("- AI generating content")
    logger.info("- Scheduler posting automatically")
    logger.info("- ERP syncing in background")
    logger.info("- Reflection running periodically")
    
    # Wait and show status
    await asyncio.sleep(5)
    
    status = manager.get_status()
    logger.info(f"\nSystem Status:\n{status}\n")
    
    await manager.stop()
    logger.info("Stopped autonomous automation\n")


async def example_manual_content_generation():
    """Example: Manual content generation with AI."""
    logger.info("=" * 60)
    logger.info("EXAMPLE 2: Manual AI Content Generation")
    logger.info("=" * 60)
    
    from ai_engine.generator import ContentGenerator
    from core.config import AutomationConfig
    
    # Create config
    config = AutomationConfig()
    
    # Set demo values (normally from .env)
    config.set('ai_engine.provider', 'openai')
    config.set('ai_engine.model', 'gpt-4')
    config.set('ai_engine.api_key', os.getenv('AI_API_KEY', 'demo-key'))
    
    config.set('business.name', 'TechCorp')
    config.set('business.industry', 'Technology')
    config.set('business.brand_voice', 'professional')
    
    # Create generator
    generator = ContentGenerator(config.config)
    
    # Generate content
    logger.info("Generating content for Twitter/X...")
    
    try:
        result = await generator.generate(
            platform="Twitter/X",
            topic="Latest trends in AI and automation",
            use_tools=False  # Set to True if you have API key
        )
        
        logger.info(f"\nGenerated Content:")
        logger.info(f"Platform: {result['platform']}")
        logger.info(f"Content: {result['content']['text']}")
        logger.info(f"Hashtags: {result['content']['hashtags']}")
        logger.info(f"Length: {result['content']['length']} chars")
        logger.info(f"Tokens Used: {result['metadata']['tokens_used']}\n")
        
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        logger.info("(This is expected if no API key is configured)\n")


async def example_context_and_reflection():
    """Example: Context memory and reflection."""
    logger.info("=" * 60)
    logger.info("EXAMPLE 3: Context Memory and Reflection")
    logger.info("=" * 60)
    
    from ai_engine.providers import OpenAIProvider
    from ai_engine.context_engine import ContextEngine
    from ai_engine.reflection_engine import ReflectionEngine
    
    # Setup mock provider
    provider_config = {
        'provider': 'openai',
        'api_key': 'demo',
        'model': 'gpt-4'
    }
    
    try:
        provider = OpenAIProvider(provider_config)
    except:
        logger.info("OpenAI provider requires API key. Using mock mode.\n")
        return
    
    # Create context engine
    context_config = {
        'context_db_path': '/tmp/demo_context.db',
        'max_tokens': 10000,
        'summary_tokens': 1000
    }
    
    context_engine = ContextEngine(context_config, provider)
    
    # Add entries
    logger.info("Adding entries to context memory...")
    
    await context_engine.add_entry(
        role="user",
        content="Our company focuses on AI-powered automation for enterprises."
    )
    
    await context_engine.add_entry(
        role="assistant",
        content="I understand. I'll tailor content to enterprise AI automation."
    )
    
    await context_engine.add_entry(
        role="user",
        content="Remember: our target audience is CTOs and IT directors."
    )
    
    # Get statistics
    stats = context_engine.get_statistics()
    logger.info(f"\nContext Statistics:")
    logger.info(f"Entries: {stats['current_entries']}")
    logger.info(f"Tokens: {stats['current_tokens']}")
    logger.info(f"Utilization: {stats['utilization']:.1f}%")
    logger.info(f"Role Distribution: {stats['role_distribution']}\n")
    
    # Get context for prompt
    context = context_engine.get_context_for_prompt(max_tokens=500)
    logger.info(f"Context for AI:\n{context}\n")
    
    logger.info("Context persists across system restarts!\n")


async def example_tool_calling():
    """Example: AI tool calling."""
    logger.info("=" * 60)
    logger.info("EXAMPLE 4: AI Tool Calling")
    logger.info("=" * 60)
    
    from ai_engine.tool_registry import ToolRegistry
    
    # Create tool registry
    registry = ToolRegistry()
    
    # Register custom tool
    def get_customer_count() -> int:
        """Get total number of customers."""
        return 1523  # Mock data
    
    registry.register(
        name="get_customer_count",
        function=get_customer_count,
        description="Get the total number of customers in the database"
    )
    
    # Show available tools
    logger.info("Available Tools:")
    for tool_name in registry.list_tools():
        logger.info(f"  - {tool_name}")
    
    # Get tool schemas (for AI)
    schemas = registry.get_tool_schemas()
    logger.info(f"\nTool schemas ready for AI function calling")
    logger.info(f"Total tools: {len(schemas)}\n")
    
    # Execute a tool
    logger.info("Executing tool: get_customer_count")
    result = await registry.execute("get_customer_count", {})
    logger.info(f"Result: {result} customers\n")


async def example_scheduler():
    """Example: Autonomous scheduler."""
    logger.info("=" * 60)
    logger.info("EXAMPLE 5: Autonomous Scheduler")
    logger.info("=" * 60)
    
    from scheduler.orchestrator import AutomationOrchestrator, PostPriority
    from core.config import AutomationConfig
    
    config = AutomationConfig()
    
    # Mock social manager and content generator
    class MockSocialManager:
        async def post_content(self, platform, content):
            logger.info(f"[MOCK] Posted to {platform}: {content['text'][:50]}...")
            return {'success': True}
    
    class MockContentGenerator:
        async def generate(self, platform, **kwargs):
            return {
                'content': {
                    'text': f'Sample content for {platform}',
                    'hashtags': ['#automation', '#AI']
                }
            }
    
    # Create orchestrator
    orchestrator = AutomationOrchestrator(
        config.config,
        MockSocialManager(),
        MockContentGenerator()
    )
    
    # Schedule posts
    logger.info("Scheduling posts...")
    
    post1_id = await orchestrator.schedule_post(
        platform="Twitter/X",
        content={'text': 'First post about AI automation'},
        schedule_time=datetime.now(timezone.utc) + timedelta(seconds=5),
        priority=PostPriority.HIGH
    )
    
    post2_id = await orchestrator.schedule_post(
        platform="LinkedIn",
        content={'text': 'Professional post for B2B audience'},
        schedule_time=datetime.now(timezone.utc) + timedelta(seconds=10),
        priority=PostPriority.NORMAL
    )
    
    logger.info(f"Scheduled: {post1_id}")
    logger.info(f"Scheduled: {post2_id}")
    
    # Get scheduled posts
    scheduled = orchestrator.get_scheduled_posts()
    logger.info(f"\nScheduled posts: {len(scheduled)}")
    for post in scheduled:
        logger.info(f"  - {post['platform']} at {post['scheduled_time']}")
    
    # Get statistics
    stats = orchestrator.get_statistics()
    logger.info(f"\nScheduler Statistics:")
    logger.info(f"Queue Size: {stats['queue_size']}")
    logger.info(f"Posts Today: {stats['posts_today']}")
    logger.info(f"Posts Total: {stats['posts_total']}\n")


async def example_discord_notifications():
    """Example: Discord notifications."""
    logger.info("=" * 60)
    logger.info("EXAMPLE 6: Discord Notifications")
    logger.info("=" * 60)
    
    from integrations.discord import DiscordIntegration
    
    config = {
        'enabled': False,  # Set to True if you have webhook
        'webhook_url': os.getenv('DISCORD_WEBHOOK_URL'),
        'notify_posts': True,
        'notify_errors': True,
        'notify_erp_sync': True
    }
    
    discord = DiscordIntegration(config)
    
    logger.info("Discord Integration configured")
    logger.info(f"Enabled: {discord.enabled}")
    logger.info(f"Notify Posts: {discord.notify_posts}")
    logger.info(f"Notify Errors: {discord.notify_errors}")
    logger.info(f"Notify ERP Sync: {discord.notify_erp_sync}")
    
    if discord.enabled and discord.webhook_url:
        logger.info("\nSending test notification...")
        await discord.notify_system_status(
            status="started",
            message="Enterprise Automation Suite is running"
        )
        logger.info("Notification sent!\n")
    else:
        logger.info("\n(Configure DISCORD_WEBHOOK_URL to enable notifications)\n")


async def main():
    """Run all examples."""
    logger.info("\n" + "=" * 60)
    logger.info("ENTERPRISE AUTOMATION SUITE - EXAMPLES")
    logger.info("=" * 60 + "\n")
    
    examples = [
        ("Full Automation", example_full_automation),
        ("Manual Content Generation", example_manual_content_generation),
        ("Context & Reflection", example_context_and_reflection),
        ("Tool Calling", example_tool_calling),
        ("Scheduler", example_scheduler),
        ("Discord Notifications", example_discord_notifications),
    ]
    
    for name, example_func in examples:
        try:
            await example_func()
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Example '{name}' failed: {e}\n")
    
    logger.info("=" * 60)
    logger.info("ALL EXAMPLES COMPLETE")
    logger.info("=" * 60)
    logger.info("\nNext steps:")
    logger.info("1. Copy .env.template to .env")
    logger.info("2. Add your API keys")
    logger.info("3. Enable platforms you want to use")
    logger.info("4. Run: python -m automata.core.manager")
    logger.info("\nEnjoy your autonomous business automation! 🚀\n")


if __name__ == "__main__":
    asyncio.run(main())
