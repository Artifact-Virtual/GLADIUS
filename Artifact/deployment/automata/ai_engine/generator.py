"""
AI Content Generator with context, reflection, and tool calling.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import asyncio
import os

from .providers import get_provider
from .context_engine import ContextEngine
from .reflection_engine import ReflectionEngine
from .tool_registry import ToolRegistry, ToolExecutor


class ContentGenerator:
    """
    AI-powered content generator with full intelligence capabilities.
    
    Features:
    - Multi-provider AI support (OpenAI, Anthropic, Cohere, Local)
    - Persistent context memory
    - Self-reflection and improvement
    - Tool calling capabilities
    - Platform-specific optimization
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize content generator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize AI provider
        ai_config = config.get('ai_engine', {})
        
        # Override with environment variables
        ai_config['provider'] = os.getenv('AI_PROVIDER', ai_config.get('provider', 'openai'))
        ai_config['model'] = os.getenv('AI_MODEL', ai_config.get('model', 'gpt-4'))
        ai_config['api_key'] = os.getenv('AI_API_KEY', ai_config.get('api_key'))
        ai_config['temperature'] = float(os.getenv('AI_TEMPERATURE', ai_config.get('temperature', 0.7)))
        ai_config['max_tokens'] = int(os.getenv('AI_MAX_TOKENS', ai_config.get('max_tokens', 2000)))
        
        self.ai_provider = get_provider(ai_config)
        
        # Initialize context engine
        context_config = {
            'context_db_path': os.getenv('CONTEXT_DB_PATH', '~/.automata/context.db'),
            'max_tokens': int(os.getenv('CONTEXT_MAX_TOKENS', 100000)),
            'summary_tokens': int(os.getenv('CONTEXT_SUMMARY_TOKENS', 10000)),
        }
        self.context_engine = ContextEngine(context_config, self.ai_provider)
        
        # Initialize reflection engine
        reflection_config = {
            'enable_reflection': os.getenv('ENABLE_REFLECTION', 'true').lower() == 'true',
            'reflection_interval': int(os.getenv('CONTEXT_REFLECTION_INTERVAL', 3600)),
        }
        self.reflection_engine = ReflectionEngine(
            reflection_config,
            self.ai_provider,
            self.context_engine
        )
        
        # Initialize tool registry
        self.tool_registry = ToolRegistry()
        self.tool_executor = ToolExecutor(self.tool_registry, self.ai_provider)
        
        # Start reflection engine
        if reflection_config['enable_reflection']:
            asyncio.create_task(self.reflection_engine.start())
        
        # Statistics
        self.generation_count = 0
        self.generation_count_today = 0
        self.last_reset = datetime.now(timezone.utc).date()
        
        self.logger.info(f"Content generator initialized with {ai_config['provider']} ({ai_config['model']})")
    
    async def generate(
        self,
        platform: str,
        topic: Optional[str] = None,
        content_type: str = "text",
        style: Optional[str] = None,
        use_tools: bool = False
    ) -> Dict[str, Any]:
        """
        Generate content for social media platform.
        
        Args:
            platform: Social media platform
            topic: Content topic (auto-generated if not provided)
            content_type: Type of content (text, image_caption, video_script, etc.)
            style: Content style override
            use_tools: Enable tool calling
            
        Returns:
            Generated content dictionary
        """
        self.logger.info(f"Generating {content_type} for {platform}" + 
                        (f" on topic: {topic}" if topic else ""))
        
        # Update daily counter
        self._update_counters()
        
        # Get business context
        business_info = self.config.get('business', {})
        brand_voice = style or business_info.get('brand_voice', 'professional')
        
        # Get platform config
        platform_config = self.config.get('social_media', {}).get(platform, {})
        
        # Get relevant context
        context = self.context_engine.get_context_for_prompt(max_tokens=3000)
        
        # Get recent improvements from reflections
        improvements = self.reflection_engine.get_recent_improvements(limit=5)
        improvements_text = ""
        if improvements:
            improvements_text = "\n\nRecent learnings and improvements:\n" + "\n".join(f"- {imp}" for imp in improvements)
        
        # Build prompt
        prompt = self._build_content_prompt(
            platform=platform,
            topic=topic,
            content_type=content_type,
            brand_voice=brand_voice,
            platform_config=platform_config,
            business_info=business_info,
            improvements_text=improvements_text
        )
        
        system_message = f"""You are an expert social media content creator for {business_info.get('name', 'the company')}.

Industry: {business_info.get('industry', 'General')}
Target Audience: {business_info.get('target_audience', 'General audience')}
Brand Voice: {brand_voice}

Create engaging, on-brand content optimized for {platform}.
{improvements_text}"""
        
        try:
            # Generate content (with or without tools)
            if use_tools and os.getenv('ENABLE_TOOL_CALLING', 'true').lower() == 'true':
                result = await self.tool_executor.execute_with_tools(
                    prompt=prompt,
                    system_message=system_message
                )
                content_text = result['content']
                tool_calls_made = result.get('tool_calls_made', 0)
            else:
                result = await self.ai_provider.generate(
                    prompt=prompt,
                    system_message=system_message
                )
                content_text = result['content']
                tool_calls_made = 0
            
            # Parse content
            parsed_content = self._parse_content(content_text, platform)
            
            # Store in context
            await self.context_engine.add_entry(
                role="assistant",
                content=f"Generated {platform} content: {parsed_content.get('text', '')[:200]}...",
                metadata={
                    'type': 'content_generation',
                    'platform': platform,
                    'topic': topic,
                    'tool_calls': tool_calls_made
                }
            )
            
            self.generation_count += 1
            self.generation_count_today += 1
            
            return {
                'platform': platform,
                'content': parsed_content,
                'topic': topic,
                'metadata': {
                    'model': result.get('model'),
                    'tokens_used': result.get('usage', {}).get('total_tokens', 0),
                    'tool_calls_made': tool_calls_made,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}")
            
            # Store error in context
            await self.context_engine.add_entry(
                role="system",
                content=f"Content generation failed for {platform}: {str(e)}",
                metadata={'type': 'error', 'platform': platform}
            )
            
            raise
    
    def _build_content_prompt(
        self,
        platform: str,
        topic: Optional[str],
        content_type: str,
        brand_voice: str,
        platform_config: Dict,
        business_info: Dict,
        improvements_text: str
    ) -> str:
        """Build content generation prompt."""
        
        # Platform-specific guidelines
        platform_guidelines = {
            'Twitter/X': {
                'max_length': 280,
                'style': 'concise and engaging',
                'features': 'Use 2-3 relevant hashtags, emojis welcome'
            },
            'LinkedIn': {
                'max_length': 3000,
                'style': 'professional and insightful',
                'features': 'Start with a hook, use line breaks for readability, 3-5 hashtags'
            },
            'Facebook': {
                'max_length': 63206,
                'style': 'conversational and engaging',
                'features': 'Ask questions, encourage engagement, use emojis'
            },
            'Instagram': {
                'max_length': 2200,
                'style': 'visual-focused, inspirational',
                'features': 'First line is crucial (appears in feed), 10-15 hashtags, call-to-action'
            },
            'YouTube': {
                'max_length': 5000,
                'style': 'descriptive and keyword-rich',
                'features': 'Video description, include timestamps, relevant tags'
            }
        }
        
        guidelines = platform_guidelines.get(platform, {
            'max_length': 1000,
            'style': 'engaging',
            'features': 'Use appropriate hashtags'
        })
        
        topic_instruction = f"Topic: {topic}\n\n" if topic else "Choose a relevant, timely topic that would interest our audience.\n\n"
        
        prompt = f"""Create {content_type} for {platform}.

{topic_instruction}Brand Voice: {brand_voice}
Style: {guidelines['style']}
Max Length: {guidelines['max_length']} characters

Platform Features:
{guidelines['features']}

Requirements:
- On-brand and aligned with our voice
- Engaging and likely to drive interaction
- Optimized for {platform}'s algorithm and audience
- Include appropriate hashtags and emojis (if applicable)
- Call-to-action when appropriate

Generate the content:"""
        
        return prompt
    
    def _parse_content(self, content_text: str, platform: str) -> Dict[str, Any]:
        """Parse generated content into structured format."""
        
        # Extract hashtags
        import re
        hashtags = re.findall(r'#\w+', content_text)
        
        # Extract URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content_text)
        
        # Extract mentions
        mentions = re.findall(r'@\w+', content_text)
        
        return {
            'text': content_text,
            'hashtags': hashtags,
            'urls': urls,
            'mentions': mentions,
            'length': len(content_text)
        }
    
    def _update_counters(self):
        """Update generation counters."""
        today = datetime.now(timezone.utc).date()
        
        if today != self.last_reset:
            self.generation_count_today = 0
            self.last_reset = today
    
    def get_generated_count_today(self) -> int:
        """Get number of content pieces generated today."""
        self._update_counters()
        return self.generation_count_today
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get content generation analytics."""
        return {
            'total_generated': self.generation_count,
            'generated_today': self.get_generated_count_today(),
            'context_stats': self.context_engine.get_statistics(),
            'recent_improvements': self.reflection_engine.get_recent_improvements(limit=5),
            'reflection_history': self.reflection_engine.get_reflection_history(days=7)
        }
    
    async def trigger_reflection(self) -> Dict[str, Any]:
        """Manually trigger a reflection session."""
        reflection = await self.reflection_engine.reflect()
        return {
            'id': reflection.id,
            'timestamp': reflection.timestamp.isoformat(),
            'improvements': reflection.improvements,
            'action_items': reflection.action_items
        }
    
    def register_tool(self, name: str, function, description: str):
        """
        Register a custom tool for AI to use.
        
        Args:
            name: Tool name
            function: Tool function
            description: Tool description
        """
        self.tool_registry.register(name, function, description)
    
    def get_context_stats(self) -> Dict[str, Any]:
        """Get context engine statistics."""
        return self.context_engine.get_statistics()
