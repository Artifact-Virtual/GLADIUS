"""
Content Writing Agent - Enterprise Legion Framework
Create compelling internal and external communications
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
class ContentPiece:
    """Content piece data structure"""
    content_id: str
    title: str
    content_type: str
    target_audience: str
    content_body: str
    tone: str
    keywords: List[str]
    created_at: datetime
    status: str
    metadata: Dict[str, Any]


@dataclass
class ContentTemplate:
    """Content template data structure"""
    template_id: str
    template_name: str
    content_type: str
    structure: List[str]
    tone_guidelines: str
    target_length: int
    required_elements: List[str]


class ContentWritingAgent(BaseAgent):
    """
    Content Writing Agent for creating compelling internal and external
    communications, marketing copy, documentation, and reports.
    """
    
    def __init__(self, agent_id: str = "contentwritingagent"):
        capabilities = ["content_writing", "copywriting"]
        super().__init__(agent_id, "ContentWritingAgent", "communication", capabilities)
        self.content_templates = {}
        self.content_library = []
        self.brand_guidelines = {}
        self.tone_profiles = {}
        self.keyword_strategies = {}
        
    async def initialize(self):
        """Initialize the agent with content templates and brand guidelines"""
        await super().initialize()
        
        # Initialize content templates and brand guidelines
        self._setup_content_templates()
        self._setup_brand_guidelines()
        self._setup_tone_profiles()
        
        # Subscribe to relevant message types
        await self.subscribe_to_messages([
            "content_request",
            "research_update",
            "social_media_insights",
            "market_analysis_update",
            "brand_guidelines_update",
            "content_review_request",
            "template_creation_request"
        ])
        
        self.logger.info("Content Writing Agent initialized")
        
    def _setup_content_templates(self):
        """Setup content templates for different content types"""
        self.content_templates = {
            'blog_post': ContentTemplate(
                template_id="blog_post_template",
                template_name="Blog Post Template",
                content_type="blog_post",
                structure=[
                    "attention_grabbing_headline",
                    "engaging_introduction",
                    "main_content_sections",
                    "key_takeaways",
                    "call_to_action"
                ],
                tone_guidelines="Professional yet approachable, informative",
                target_length=800,
                required_elements=["headline", "introduction", "conclusion", "cta"]
            ),
            'email_newsletter': ContentTemplate(
                template_id="newsletter_template",
                template_name="Email Newsletter Template",
                content_type="email_newsletter",
                structure=[
                    "subject_line",
                    "personal_greeting",
                    "main_content",
                    "secondary_content",
                    "footer_cta"
                ],
                tone_guidelines="Friendly, personal, value-driven",
                target_length=400,
                required_elements=["subject", "greeting", "main_content", "cta"]
            ),
            'press_release': ContentTemplate(
                template_id="press_release_template",
                template_name="Press Release Template",
                content_type="press_release",
                structure=[
                    "headline",
                    "dateline",
                    "lead_paragraph",
                    "body_paragraphs",
                    "boilerplate",
                    "contact_information"
                ],
                tone_guidelines="Professional, factual, newsworthy",
                target_length=600,
                required_elements=["headline", "dateline", "lead", "contact"]
            ),
            'social_media_post': ContentTemplate(
                template_id="social_media_template",
                template_name="Social Media Post Template",
                content_type="social_media_post",
                structure=[
                    "hook",
                    "main_message",
                    "call_to_action",
                    "hashtags"
                ],
                tone_guidelines="Engaging, conversational, brand-aligned",
                target_length=280,
                required_elements=["hook", "message", "hashtags"]
            ),
            'internal_memo': ContentTemplate(
                template_id="memo_template",
                template_name="Internal Memo Template",
                content_type="internal_memo",
                structure=[
                    "header_info",
                    "purpose_statement",
                    "main_content",
                    "action_items",
                    "next_steps"
                ],
                tone_guidelines="Clear, direct, professional",
                target_length=300,
                required_elements=["purpose", "content", "action_items"]
            ),
            'product_description': ContentTemplate(
                template_id="product_desc_template",
                template_name="Product Description Template",
                content_type="product_description",
                structure=[
                    "product_headline",
                    "key_benefits",
                    "feature_details",
                    "use_cases",
                    "specifications"
                ],
                tone_guidelines="Persuasive, benefit-focused, clear",
                target_length=200,
                required_elements=["headline", "benefits", "features"]
            )
        }
        
    def _setup_brand_guidelines(self):
        """Setup brand guidelines and voice standards"""
        self.brand_guidelines = {
            'voice_characteristics': [
                "Professional yet approachable",
                "Knowledgeable and trustworthy",
                "Clear and concise",
                "Solution-oriented",
                "Innovation-focused"
            ],
            'tone_variations': {
                'formal': "Professional, authoritative, structured",
                'casual': "Friendly, conversational, relatable",
                'educational': "Informative, helpful, patient",
                'promotional': "Enthusiastic, benefit-focused, persuasive",
                'supportive': "Empathetic, helpful, reassuring"
            },
            'messaging_pillars': [
                "Innovation and technology leadership",
                "Customer success and satisfaction",
                "Quality and reliability",
                "Expertise and thought leadership",
                "Transparency and trust"
            ],
            'style_guidelines': {
                'sentence_length': 'Vary between short and medium sentences',
                'paragraph_length': 'Keep paragraphs to 3-4 sentences max',
                'language_level': 'Professional but accessible',
                'active_voice': 'Prefer active voice over passive',
                'technical_terms': 'Explain when necessary, avoid jargon'
            }
        }
        
    def _setup_tone_profiles(self):
        """Setup tone profiles for different content types and audiences"""
        self.tone_profiles = {
            'executive_communication': {
                'tone': 'formal',
                'characteristics': ['concise', 'strategic', 'data-driven'],
                'avoid': ['casual language', 'excessive detail', 'emotional appeals']
            },
            'customer_communication': {
                'tone': 'helpful',
                'characteristics': ['clear', 'solution-focused', 'empathetic'],
                'avoid': ['technical jargon', 'corporate speak', 'impersonal']
            },
            'marketing_content': {
                'tone': 'engaging',
                'characteristics': ['benefit-focused', 'persuasive', 'energetic'],
                'avoid': ['too salesy', 'feature-heavy', 'boring']
            },
            'internal_communication': {
                'tone': 'collaborative',
                'characteristics': ['clear', 'actionable', 'inclusive'],
                'avoid': ['ambiguity', 'blame language', 'exclusivity']
            }
        }

    async def process_message(self, message: AgentMessage):
        """Process incoming messages and handle content requests"""
        try:
            if message.message_type == "content_request":
                await self._handle_content_request(message)
            elif message.message_type == "research_update":
                await self._handle_research_update(message)
            elif message.message_type == "social_media_insights":
                await self._handle_social_insights(message)
            elif message.message_type == "market_analysis_update":
                await self._handle_market_analysis(message)
            elif message.message_type == "brand_guidelines_update":
                await self._handle_brand_update(message)
            elif message.message_type == "content_review_request":
                await self._handle_review_request(message)
            elif message.message_type == "template_creation_request":
                await self._handle_template_request(message)
                
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            
    async def _handle_content_request(self, message: AgentMessage):
        """Handle content creation requests"""
        request = message.content
        content_type = request.get('content_type', 'general')
        target_audience = request.get('target_audience', 'general')
        topic = request.get('topic', '')
        tone = request.get('tone', 'professional')
        length = request.get('length', 'medium')
        
        # Generate the requested content
        content = await self._generate_content(
            content_type=content_type,
            topic=topic,
            target_audience=target_audience,
            tone=tone,
            length=length,
            additional_params=request.get('additional_params', {})
        )
        
        # Store in content library
        self.content_library.append(content)
        
        # Send content back to requester
        response = AgentMessage(
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type="content_response",
            content={
                'content_piece': content.__dict__,
                'recommendations': await self._generate_content_recommendations(content),
                'optimization_suggestions': await self._suggest_optimizations(content)
            }
        )
        await self.send_message(response)
        
    async def _handle_research_update(self, message: AgentMessage):
        """Handle research updates for content creation"""
        research_data = message.content
        
        # Extract content opportunities from research
        opportunities = await self._identify_content_opportunities(research_data)
        
        if opportunities:
            # Send content suggestions to relevant agents
            for opportunity in opportunities:
                suggestion = AgentMessage(
                    sender_id=self.agent_id,
                    recipient_id="social_media_monitoring_agent",
                    message_type="content_opportunity",
                    content=opportunity
                )
                await self.send_message(suggestion)
                
    async def _handle_social_insights(self, message: AgentMessage):
        """Handle social media insights for content optimization"""
        insights = message.content
        
        # Update keyword strategies based on social trends
        trending_topics = insights.get('trending_topics', [])
        engagement_patterns = insights.get('engagement_patterns', {})
        
        await self._update_keyword_strategies(trending_topics, engagement_patterns)
        
        # Generate content recommendations based on insights
        recommendations = await self._generate_social_content_recommendations(insights)
        
        if recommendations:
            response = AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="content_recommendations",
                content=recommendations
            )
            await self.send_message(response)
            
    async def _generate_content(self, content_type: str, topic: str, 
                              target_audience: str, tone: str, length: str,
                              additional_params: Dict[str, Any]) -> ContentPiece:
        """Generate content based on parameters"""
        
        # Get appropriate template
        template = self.content_templates.get(content_type)
        if not template:
            template = self.content_templates['blog_post']  # Default template
            
        # Determine target length
        if length == 'short':
            target_length = int(template.target_length * 0.6)
        elif length == 'long':
            target_length = int(template.target_length * 1.5)
        else:
            target_length = template.target_length
            
        # Generate content based on template structure
        content_sections = {}
        for section in template.structure:
            content_sections[section] = await self._generate_section_content(
                section, topic, target_audience, tone, additional_params
            )
            
        # Combine sections into complete content
        content_body = await self._combine_content_sections(content_sections, template)
        
        # Generate appropriate keywords
        keywords = await self._generate_keywords(topic, content_type, target_audience)
        
        # Create content piece
        content_piece = ContentPiece(
            content_id=f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=content_sections.get('headline', 
                   content_sections.get('subject_line', f"Content about {topic}")),
            content_type=content_type,
            target_audience=target_audience,
            content_body=content_body,
            tone=tone,
            keywords=keywords,
            created_at=datetime.now(),
            status="draft",
            metadata={
                'template_used': template.template_id,
                'target_length': target_length,
                'actual_length': len(content_body),
                'sections': list(content_sections.keys())
            }
        )
        
        return content_piece
        
    async def _generate_section_content(self, section: str, topic: str, 
                                      audience: str, tone: str, 
                                      params: Dict[str, Any]) -> str:
        """Generate content for a specific section"""
        
        # Get tone profile
        tone_profile = self._get_tone_profile(audience, tone)
        
        if section == "headline" or section == "attention_grabbing_headline":
            return await self._generate_headline(topic, tone_profile, params)
        elif section == "subject_line":
            return await self._generate_subject_line(topic, tone_profile, params)
        elif section == "introduction" or section == "engaging_introduction":
            return await self._generate_introduction(topic, audience, tone_profile, params)
        elif section == "main_content" or section == "main_content_sections":
            return await self._generate_main_content(topic, audience, tone_profile, params)
        elif section == "conclusion" or section == "key_takeaways":
            return await self._generate_conclusion(topic, tone_profile, params)
        elif section == "call_to_action" or section == "cta":
            return await self._generate_cta(audience, tone_profile, params)
        elif section == "hook":
            return await self._generate_hook(topic, tone_profile, params)
        elif section == "hashtags":
            return await self._generate_hashtags(topic, params)
        else:
            return await self._generate_generic_section(section, topic, tone_profile, params)
            
    async def _generate_headline(self, topic: str, tone_profile: Dict[str, Any], 
                               params: Dict[str, Any]) -> str:
        """Generate compelling headlines"""
        headline_templates = [
            f"How to {topic}: A Complete Guide",
            f"The Ultimate Guide to {topic}",
            f"5 Key Strategies for {topic} Success",
            f"Transform Your {topic} with These Proven Methods",
            f"Why {topic} Matters More Than Ever",
            f"The Future of {topic}: What You Need to Know"
        ]
        
        # Select template based on tone and customize
        if tone_profile.get('tone') == 'formal':
            return f"Strategic Insights: {topic} Best Practices and Implementation"
        elif tone_profile.get('tone') == 'casual':
            return f"Everything You Need to Know About {topic}"
        else:
            return headline_templates[0]  # Default
            
    async def _generate_subject_line(self, topic: str, tone_profile: Dict[str, Any], 
                                   params: Dict[str, Any]) -> str:
        """Generate email subject lines"""
        if 'urgent' in params:
            return f"Action Required: {topic} Update"
        elif 'promotional' in params:
            return f"Exclusive: New {topic} Solutions Available"
        else:
            return f"Important Update on {topic}"
            
    async def _generate_introduction(self, topic: str, audience: str, 
                                   tone_profile: Dict[str, Any], 
                                   params: Dict[str, Any]) -> str:
        """Generate engaging introductions"""
        if audience == 'executive':
            return f"In today's competitive landscape, {topic} represents a critical factor in organizational success. This analysis provides key insights and strategic recommendations for implementation."
        elif audience == 'customer':
            return f"We understand that {topic} is important to you. That's why we've put together this comprehensive guide to help you achieve your goals."
        else:
            return f"Understanding {topic} is essential for success in today's market. Let's explore the key concepts and practical applications."
            
    async def _generate_main_content(self, topic: str, audience: str, 
                                   tone_profile: Dict[str, Any], 
                                   params: Dict[str, Any]) -> str:
        """Generate main content sections"""
        content_points = params.get('key_points', [
            f"Understanding the fundamentals of {topic}",
            f"Best practices for implementing {topic} strategies",
            f"Common challenges and how to overcome them",
            f"Measuring success and ROI"
        ])
        
        content = ""
        for i, point in enumerate(content_points, 1):
            content += f"\n\n{i}. {point}\n\n"
            content += await self._elaborate_on_point(point, audience, tone_profile)
            
        return content
        
    async def _elaborate_on_point(self, point: str, audience: str, 
                                tone_profile: Dict[str, Any]) -> str:
        """Elaborate on content points"""
        if audience == 'executive':
            return "This strategic initiative drives measurable business outcomes and competitive advantage through systematic implementation and performance monitoring."
        elif audience == 'technical':
            return "Implementation requires careful consideration of technical specifications, integration requirements, and performance optimization factors."
        else:
            return "This approach has proven effective across various scenarios and can be adapted to meet specific organizational needs."
            
    async def _generate_conclusion(self, topic: str, tone_profile: Dict[str, Any], 
                                 params: Dict[str, Any]) -> str:
        """Generate conclusions and key takeaways"""
        return f"In conclusion, {topic} presents significant opportunities for organizations that approach it strategically. The key to success lies in understanding the fundamentals, implementing best practices, and continuously measuring and optimizing performance."
        
    async def _generate_cta(self, audience: str, tone_profile: Dict[str, Any], 
                          params: Dict[str, Any]) -> str:
        """Generate call-to-action content"""
        cta_type = params.get('cta_type', 'general')
        
        if cta_type == 'consultation':
            return "Ready to get started? Contact our team for a personalized consultation."
        elif cta_type == 'download':
            return "Download our comprehensive guide to learn more."
        elif cta_type == 'subscription':
            return "Subscribe to our newsletter for the latest insights and updates."
        else:
            return "Take the next step toward achieving your goals."
            
    async def _generate_hook(self, topic: str, tone_profile: Dict[str, Any], 
                           params: Dict[str, Any]) -> str:
        """Generate social media hooks"""
        hooks = [
            f"Did you know that {topic} can transform your business?",
            f"Here's what most people get wrong about {topic}:",
            f"The secret to {topic} success? It's simpler than you think.",
            f"Why {topic} is the game-changer you've been looking for:"
        ]
        return hooks[0]  # Default selection
        
    async def _generate_hashtags(self, topic: str, params: Dict[str, Any]) -> str:
        """Generate relevant hashtags"""
        base_tags = [
            f"#{topic.replace(' ', '')}",
            "#business",
            "#success",
            "#strategy",
            "#innovation"
        ]
        
        industry_tags = params.get('industry_tags', [])
        base_tags.extend(industry_tags)
        
        return " ".join(base_tags[:10])  # Limit to 10 hashtags
        
    async def _generate_generic_section(self, section: str, topic: str, 
                                      tone_profile: Dict[str, Any], 
                                      params: Dict[str, Any]) -> str:
        """Generate content for generic sections"""
        return f"This section covers important aspects of {topic} that are relevant to your needs and objectives."
        
    async def _combine_content_sections(self, sections: Dict[str, str], 
                                      template: ContentTemplate) -> str:
        """Combine content sections into complete content"""
        content = ""
        
        for section_name in template.structure:
            if section_name in sections:
                content += sections[section_name] + "\n\n"
                
        return content.strip()
        
    async def _generate_keywords(self, topic: str, content_type: str, 
                               audience: str) -> List[str]:
        """Generate relevant keywords for content"""
        base_keywords = [topic]
        
        # Add content type specific keywords
        if content_type == 'blog_post':
            base_keywords.extend(['guide', 'tips', 'best practices'])
        elif content_type == 'product_description':
            base_keywords.extend(['features', 'benefits', 'solution'])
        elif content_type == 'social_media_post':
            base_keywords.extend(['trending', 'insights', 'update'])
            
        # Add audience specific keywords
        if audience == 'executive':
            base_keywords.extend(['strategy', 'ROI', 'business impact'])
        elif audience == 'technical':
            base_keywords.extend(['implementation', 'integration', 'specifications'])
            
        return base_keywords
        
    def _get_tone_profile(self, audience: str, tone: str) -> Dict[str, Any]:
        """Get appropriate tone profile"""
        if audience == 'executive':
            return self.tone_profiles['executive_communication']
        elif audience == 'customer':
            return self.tone_profiles['customer_communication']
        elif tone == 'marketing':
            return self.tone_profiles['marketing_content']
        else:
            return self.tone_profiles['internal_communication']

    async def get_status(self) -> Dict[str, Any]:
        """Get current status of the Content Writing Agent"""
        recent_content = [content for content in self.content_library 
                         if content.created_at > datetime.now() - timedelta(days=7)]
        
        return {
            'agent_id': self.agent_id,
            'status': 'active',
            'total_content_pieces': len(self.content_library),
            'recent_content_pieces': len(recent_content),
            'templates_available': len(self.content_templates),
            'tone_profiles': len(self.tone_profiles),
            'content_types_supported': list(self.content_templates.keys())
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
            elif task_type == 'generate_strategic_content':
                return await self._generate_strategic_content(parameters)
            else:
                return {"status": "failed", "error": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            self.logger.error(f"Error processing task: {str(e)}")
            return {"status": "failed", "error": str(e)}
            
    async def _generate_strategic_content(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strategic content based on parameters"""
        try:
            content_type = parameters.get('type', 'general')
            topic = parameters.get('topic', 'general_topic')
            target_audience = parameters.get('target_audience', 'general')
            
            # Generate content based on type
            if content_type == 'company_manifesto':
                content = await self._create_company_manifesto(topic, target_audience)
            elif content_type == 'service_portfolio':
                content = await self._create_service_portfolio(topic, target_audience)
            elif content_type == 'thought_leadership':
                content = await self._create_thought_leadership(topic, target_audience)
            else:
                content = await self._create_general_content(topic, target_audience)
                
            # Store content
            content_piece = ContentPiece(
                content_id=f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title=f"{content_type.title()}: {topic}",
                content_type=content_type,
                target_audience=target_audience,
                content_body=content,
                tone="professional",
                keywords=[],
                created_at=datetime.now(),
                status="completed",
                metadata=parameters
            )
            
            self.content_library.append(content_piece)
            
            return {
                "status": "completed",
                "content_id": content_piece.content_id,
                "content_type": content_type,
                "word_count": len(content.split()),
                "created_at": content_piece.created_at.isoformat()
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
            
    async def _create_company_manifesto(self, topic: str, audience: str) -> str:
        """Create company manifesto content"""
        return f"""
# Artifact Virtual: AI Consulting Manifesto

## Our Vision
Artifact Virtual represents the future of enterprise intelligence - where artificial intelligence seamlessly integrates with human expertise to create unprecedented business value.

## Our Mission
We empower organizations to harness the transformative power of AI through strategic consulting, innovative solutions, and pragmatic implementation approaches.

## Our Approach
- **Zero-Waste AI**: Every AI solution must deliver measurable ROI
- **Human-Centric Design**: AI amplifies human capability rather than replacing it
- **Ethical Implementation**: Responsible AI deployment with transparency and accountability
- **Continuous Evolution**: Adaptive strategies that grow with technological advancement

## Our Commitment
To democratize enterprise AI, making cutting-edge intelligence accessible to organizations of all sizes through innovative, cost-effective solutions.

Target Audience: {audience}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
    async def _create_service_portfolio(self, topic: str, audience: str) -> str:
        """Create service portfolio content"""
        return f"""
# Artifact Virtual AI Consulting Services

## Strategic AI Consulting
- AI Readiness Assessment
- Digital Transformation Strategy
- Technology Roadmap Development
- ROI Analysis and Business Case Development

## Implementation Services
- Custom AI Solution Development
- Process Automation Design
- Machine Learning Model Development
- Integration and Deployment

## Training and Enablement
- Executive AI Workshops
- Technical Team Training
- Change Management Support
- Ongoing Support and Optimization

## Specialized Solutions
- Document Processing Automation
- Predictive Analytics Implementation
- Customer Service AI Integration
- Supply Chain Optimization

Pricing starts at $150/hour for consulting, with project-based pricing available.

Target Audience: {audience}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
    async def _create_thought_leadership(self, topic: str, audience: str) -> str:
        """Create thought leadership content"""
        return f"""
# The Future of Enterprise AI: Building Digital Organizations

The enterprise landscape is undergoing a fundamental transformation. Organizations that successfully integrate AI into their core operations will not merely gain competitive advantages—they will redefine entire industries.

## The Digital Organization Paradigm
Traditional organizational structures are giving way to fluid, AI-enhanced ecosystems where:
- Decision-making is augmented by real-time intelligence
- Processes adapt dynamically to changing conditions
- Human creativity is amplified by machine precision

## Key Success Factors
1. **Strategic Vision**: AI implementation must align with business objectives
2. **Cultural Readiness**: Organizations must embrace data-driven decision making
3. **Incremental Deployment**: Start with high-impact, low-risk applications
4. **Continuous Learning**: Establish feedback loops for ongoing optimization

## The Path Forward
The future belongs to organizations that view AI not as a technology to be deployed, but as a capability to be cultivated. Success requires partnership between human insight and artificial intelligence.

Target Audience: {audience}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
    async def _create_general_content(self, topic: str, audience: str) -> str:
        """Create general content"""
        return f"""
# {topic.replace('_', ' ').title()}

Content generated for {audience} regarding {topic}.

This is a strategic content piece designed to provide value and establish thought leadership in the AI consulting space.

Key points:
- Relevant industry insights
- Practical implementation advice
- Strategic recommendations
- Future outlook and trends

Target Audience: {audience}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """

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

