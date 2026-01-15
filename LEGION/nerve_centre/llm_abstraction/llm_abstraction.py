"""
LLM Abstraction Subsystem Core Module
"""
import json
import logging
import time
import hashlib
import re
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import requests
import yaml

from llm_abstraction.base import LLMProviderBase, ProviderType, SecurityLevel, LLMRequest, LLMResponse


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LLMRequest:
    """Structured LLM request with metadata."""
    prompt: str
    context: Optional[Dict[str, Any]] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    retry_count: int = 0
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class LLMResponse:
    """Structured LLM response with metrics."""
    content: str
    provider: str
    timestamp: float
    tokens_used: Optional[int] = None
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class OpenAIProvider(LLMProviderBase):
    """OpenAI LLM provider implementation."""
    
    def __init__(self, api_key, endpoint, config):
        self.api_key = api_key
        self.endpoint = endpoint
        self.config = config
        self.name = 'OpenAI'
        self.rate_limit = config.get('rate_limit', None)
    
    def query(self, request: LLMRequest) -> LLMResponse:
        """Execute OpenAI query."""
        self._rate_limit_check()
        start_time = time.time()
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.config.get('model', 'gpt-3.5-turbo'),
            'messages': [{'role': 'user', 'content': request.prompt}],
            'max_tokens': request.max_tokens or 1000,
            'temperature': request.temperature or 0.7
        }
        
        try:
            response = requests.post(
                f"{self.endpoint}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            tokens_used = data.get('usage', {}).get('total_tokens')
            
            return LLMResponse(
                content=content,
                provider=self.name,
                timestamp=time.time(),
                tokens_used=tokens_used,
                processing_time=time.time() - start_time,
                metadata={'model': payload['model']}
            )
            
        except Exception as e:
            logger.error(f"OpenAI query failed: {e}")
            raise
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get OpenAI provider metadata."""
        return {
            'name': self.name,
            'type': ProviderType.OPENAI.value,
            'models': ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo'],
            'capabilities': ['text-generation', 'conversation'],
            'rate_limit': self.rate_limit
        }


class AnthropicProvider(LLMProviderBase):
    """Anthropic LLM provider implementation."""
    
    def __init__(self, api_key, endpoint, config):
        self.api_key = api_key
        self.endpoint = endpoint
        self.config = config
        self.name = 'Anthropic'
        self.rate_limit = config.get('rate_limit', None)
    
    def query(self, request: LLMRequest) -> LLMResponse:
        """Execute Anthropic query."""
        self._rate_limit_check()
        start_time = time.time()
        
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        payload = {
            'model': self.config.get('model', 'claude-3-sonnet-20240229'),
            'max_tokens': request.max_tokens or 1000,
            'messages': [{'role': 'user', 'content': request.prompt}]
        }
        
        try:
            response = requests.post(
                f"{self.endpoint}/messages",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            content = data['content'][0]['text']
            tokens_used = data.get('usage', {}).get('output_tokens')
            
            return LLMResponse(
                content=content,
                provider=self.name,
                timestamp=time.time(),
                tokens_used=tokens_used,
                processing_time=time.time() - start_time,
                metadata={'model': payload['model']}
            )
            
        except Exception as e:
            logger.error(f"Anthropic query failed: {e}")
            raise
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get Anthropic provider metadata."""
        return {
            'name': self.name,
            'type': ProviderType.ANTHROPIC.value,
            'models': ['claude-3-sonnet-20240229', 'claude-3-opus-20240229'],
            'capabilities': ['text-generation', 'conversation', 'analysis'],
            'rate_limit': self.rate_limit
        }


class OllamaProvider(LLMProviderBase):
    """Ollama LLM provider implementation."""
    
    def __init__(self, base_url: str, model: str, timeout: int = 300):
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self.name = 'Ollama'
        
    def query(self, request: LLMRequest) -> LLMResponse:
        """Execute Ollama query."""
        start_time = time.time()
        
        payload = {
            'model': self.model,
            'prompt': request.prompt,
            'stream': False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            content = data.get('response', '')
            
            return LLMResponse(
                content=content,
                provider=self.name,
                timestamp=time.time(),
                processing_time=time.time() - start_time,
                metadata={'model': self.model}
            )
            
        except Exception as e:
            logger.error(f"Ollama query failed: {e}")
            raise
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get Ollama provider metadata."""
        return {
            'name': self.name,
            'type': 'local',
            'base_url': self.base_url,
            'model': self.model,
            'capabilities': ['text-generation', 'conversation']
        }

    def _rate_limit_check(self):
        """Ollama doesn't need rate limiting for local models."""
        pass


class PromptEngineer:
    """Advanced prompt engineering algorithms."""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.optimization_strategies = {
            'clarity': self._optimize_for_clarity,
            'context': self._optimize_for_context,
            'specificity': self._optimize_for_specificity,
            'creativity': self._optimize_for_creativity
        }
    
    def engineer(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        strategy: str = 'clarity'
    ) -> str:
        """Engineer optimized prompt using specified strategy."""
        if strategy not in self.optimization_strategies:
            logger.warning(f"Unknown strategy: {strategy}, using 'clarity'")
            strategy = 'clarity'
        
        # Apply base prompt engineering principles
        engineered_prompt = self._apply_base_principles(prompt)
        
        # Apply specific strategy
        engineered_prompt = self.optimization_strategies[strategy](
            engineered_prompt, context
        )
        
        # Add context if provided
        if context:
            engineered_prompt = self._inject_context(
                engineered_prompt, context
            )
        
        logger.info(f"Prompt engineered using {strategy} strategy")
        return engineered_prompt
    
    def _apply_base_principles(self, prompt: str) -> str:
        """Apply fundamental prompt engineering principles."""
        # Remove excessive whitespace
        prompt = re.sub(r'\s+', ' ', prompt.strip())
        
        # Ensure proper structure
        if not prompt.endswith(('?', '.', ':', '!')):
            prompt += '.'
        
        # Add instruction clarity
        if not any(word in prompt.lower() for word in [
            'please', 'analyze', 'explain', 'describe', 'generate'
        ]):
            prompt = f"Please {prompt.lower()}"
        
        return prompt
    
    def _optimize_for_clarity(
        self, prompt: str, context: Optional[Dict[str, Any]]
    ) -> str:
        """Optimize prompt for maximum clarity."""
        clarity_prefix = (
            "Please provide a clear and detailed response to the following: "
        )
        return f"{clarity_prefix}{prompt}"
    
    def _optimize_for_context(
        self, prompt: str, context: Optional[Dict[str, Any]]
    ) -> str:
        """Optimize prompt for context awareness."""
        context_prefix = (
            "Consider the following context and provide a relevant response: "
        )
        return f"{context_prefix}{prompt}"
    
    def _optimize_for_specificity(
        self, prompt: str, context: Optional[Dict[str, Any]]
    ) -> str:
        """Optimize prompt for specific, actionable responses."""
        specificity_prefix = (
            "Provide a specific, detailed, and actionable response to: "
        )
        return f"{specificity_prefix}{prompt}"
    
    def _optimize_for_creativity(
        self, prompt: str, context: Optional[Dict[str, Any]]
    ) -> str:
        """Optimize prompt for creative responses."""
        creativity_prefix = (
            "Think creatively and provide an innovative response to: "
        )
        return f"{creativity_prefix}{prompt}"
    
    def _inject_context(self, prompt: str, context: Dict[str, Any]) -> str:
        """Inject context information into prompt."""
        context_str = "\nContext:\n"
        for key, value in context.items():
            context_str += f"- {key}: {value}\n"
        
        return f"{context_str}\nQuery: {prompt}"
    
    def _load_templates(self) -> Dict[str, str]:
        """Load prompt templates for common use cases."""
        return {
            'analysis': "Analyze the following and provide insights: {content}",
            'summary': "Summarize the following content: {content}",
            'question': "Answer the following question: {content}",
            'creative': "Create something original based on: {content}"
        }


class ContextManager:
    """Advanced context management and optimization."""
    
    def __init__(self, max_context_tokens: int = 4000):
        self.max_context_tokens = max_context_tokens
        self.context_cache = {}
        
    def optimize(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize context for maximum relevance and efficiency."""
        # Calculate context hash for caching
        context_hash = self._hash_context(context)
        
        if context_hash in self.context_cache:
            logger.info("Using cached context optimization")
            return self.context_cache[context_hash]
        
        # Prioritize context elements
        prioritized_context = self._prioritize_context(context)
        
        # Trim context to fit token limits
        optimized_context = self._trim_context(prioritized_context)
        
        # Cache the result
        self.context_cache[context_hash] = optimized_context
        
        logger.info(f"Context optimized: {len(context)} -> {len(optimized_context)} elements")
        return optimized_context
    
    def _prioritize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prioritize context elements by relevance."""
        priority_keys = [
            'current_task', 'user_intent', 'primary_data',
            'recent_history', 'constraints', 'objectives'
        ]
        
        prioritized = {}
        
        # Add high-priority items first
        for key in priority_keys:
            if key in context:
                prioritized[key] = context[key]
        
        # Add remaining items
        for key, value in context.items():
            if key not in prioritized:
                prioritized[key] = value
        
        return prioritized
    
    def _trim_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Trim context to fit within token limits."""
        trimmed = {}
        estimated_tokens = 0
        
        for key, value in context.items():
            # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
            item_tokens = len(str(value)) // 4
            
            if estimated_tokens + item_tokens <= self.max_context_tokens:
                trimmed[key] = value
                estimated_tokens += item_tokens
            else:
                # Try to include partial content
                remaining_tokens = self.max_context_tokens - estimated_tokens
                if remaining_tokens > 10:  # Minimum useful size
                    partial_content = str(value)[:remaining_tokens * 4]
                    trimmed[f"{key}_partial"] = partial_content
                break
        
        return trimmed
    
    def _hash_context(self, context: Dict[str, Any]) -> str:
        """Generate hash for context caching."""
        context_str = json.dumps(context, sort_keys=True, default=str)
        return hashlib.md5(context_str.encode()).hexdigest()


class OutputProcessor:
    """Advanced output processing and ranking."""
    
    def __init__(self):
        self.quality_metrics = {
            'coherence': self._measure_coherence,
            'relevance': self._measure_relevance,
            'completeness': self._measure_completeness,
            'accuracy': self._measure_accuracy
        }
    
    def process(
        self,
        outputs: List[LLMResponse],
        request: LLMRequest
    ) -> List[LLMResponse]:
        """Process and rank multiple LLM outputs."""
        if not outputs:
            return outputs
        
        # Calculate quality scores for each output
        for output in outputs:
            output.confidence_score = self._calculate_quality_score(
                output, request
            )
        
        # Rank outputs by quality score
        ranked_outputs = sorted(
            outputs,
            key=lambda x: x.confidence_score or 0,
            reverse=True
        )
        
        # Apply post-processing filters
        filtered_outputs = self._apply_filters(ranked_outputs, request)
        
        logger.info(f"Processed {len(outputs)} outputs, returned {len(filtered_outputs)}")
        return filtered_outputs
    
    def _calculate_quality_score(
        self,
        output: LLMResponse,
        request: LLMRequest
    ) -> float:
        """Calculate comprehensive quality score for output."""
        scores = []
        
        for metric_name, metric_func in self.quality_metrics.items():
            try:
                score = metric_func(output, request)
                scores.append(score)
            except Exception as e:
                logger.warning(f"Failed to calculate {metric_name}: {e}")
                scores.append(0.5)  # Default neutral score
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _measure_coherence(
        self,
        output: LLMResponse,
        request: LLMRequest
    ) -> float:
        """Measure output coherence and structure."""
        content = output.content
        
        # Basic coherence indicators
        has_proper_structure = bool(re.search(r'[.!?]', content))
        has_logical_flow = len(content.split('.')) > 1
        appropriate_length = 10 <= len(content) <= 5000
        
        coherence_score = (
            (0.4 if has_proper_structure else 0) +
            (0.3 if has_logical_flow else 0) +
            (0.3 if appropriate_length else 0)
        )
        
        return coherence_score
    
    def _measure_relevance(
        self,
        output: LLMResponse,
        request: LLMRequest
    ) -> float:
        """Measure output relevance to request."""
        prompt_words = set(request.prompt.lower().split())
        output_words = set(output.content.lower().split())
        
        # Calculate word overlap
        overlap = len(prompt_words.intersection(output_words))
        relevance_score = min(overlap / max(len(prompt_words), 1), 1.0)
        
        return relevance_score
    
    def _measure_completeness(
        self,
        output: LLMResponse,
        request: LLMRequest
    ) -> float:
        """Measure output completeness."""
        content = output.content
        
        # Indicators of completeness
        has_conclusion = any(word in content.lower() for word in [
            'conclusion', 'summary', 'finally', 'in summary'
        ])
        sufficient_detail = len(content) > 50
        addresses_query = any(word in content.lower() for word in
                            request.prompt.lower().split()[:5])
        
        completeness_score = (
            (0.3 if has_conclusion else 0) +
            (0.4 if sufficient_detail else 0) +
            (0.3 if addresses_query else 0)
        )
        
        return completeness_score
    
    def _measure_accuracy(
        self,
        output: LLMResponse,
        request: LLMRequest
    ) -> float:
        """Measure output accuracy (basic heuristics)."""
        content = output.content
        
        # Basic accuracy indicators
        no_contradictions = not re.search(
            r'(not|never|no).*\b(is|are|was|were)\b.*\1', content.lower()
        )
        factual_language = any(word in content.lower() for word in [
            'according to', 'research shows', 'studies indicate', 'evidence'
        ])
        confident_tone = not any(phrase in content.lower() for phrase in [
            'i think', 'maybe', 'might be', 'possibly', 'i believe'
        ])
        
        accuracy_score = (
            (0.4 if no_contradictions else 0) +
            (0.3 if factual_language else 0) +
            (0.3 if confident_tone else 0)
        )
        
        return accuracy_score
    
    def _apply_filters(
        self,
        outputs: List[LLMResponse],
        request: LLMRequest
    ) -> List[LLMResponse]:
        """Apply security and quality filters."""
        filtered = []
        
        for output in outputs:
            # Security filter
            if self._passes_security_filter(output, request):
                # Quality threshold filter
                if (output.confidence_score or 0) >= 0.3:
                    filtered.append(output)
                else:
                    logger.debug(f"Output filtered due to low quality score: {output.confidence_score}")
            else:
                logger.warning("Output filtered due to security concerns")
        
        return filtered
    
    def _passes_security_filter(
        self,
        output: LLMResponse,
        request: LLMRequest
    ) -> bool:
        """Check if output passes security filters."""
        content = output.content.lower()
        
        # Basic security checks
        security_keywords = [
            'password', 'api_key', 'secret', 'token', 'private_key'
        ]
        
        for keyword in security_keywords:
            if keyword in content:
                return False
        
        return True


class LLMOrchestrator:
    """Advanced LLM orchestration with intelligent routing and workflow management."""
    
    def __init__(
        self,
        providers: List[LLMProviderBase],
        prompt_engineer: Optional[PromptEngineer] = None,
        context_manager: Optional[ContextManager] = None,
        output_processor: Optional[OutputProcessor] = None
    ):
        self.providers = providers
        self.prompt_engineer = prompt_engineer or PromptEngineer()
        self.context_manager = context_manager or ContextManager()
        self.output_processor = output_processor or OutputProcessor()
        self.provider_performance = {p.name: {'success': 0, 'failure': 0, 'avg_time': 0} for p in providers}
        
    def run(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        use_multiple_providers: bool = False
    ) -> Union[LLMResponse, List[LLMResponse]]:
        """Execute LLM query with advanced orchestration."""
        # Create structured request
        request = LLMRequest(
            prompt=prompt,
            context=context,
            security_level=SecurityLevel.MEDIUM
        )
        
        # Engineer the prompt
        engineered_prompt = self.prompt_engineer.engineer(
            request.prompt, request.context
        )
        request.prompt = engineered_prompt
        
        # Optimize context
        if request.context:
            request.context = self.context_manager.optimize(request.context)
        
        # Execute queries
        if use_multiple_providers:
            return self._run_multiple_providers(request, max_retries)
        else:
            return self._run_single_provider(request, max_retries)
    
    def _run_single_provider(
        self,
        request: LLMRequest,
        max_retries: int
    ) -> LLMResponse:
        """Run query on single best provider."""
        provider = self._select_best_provider(request)
        
        for attempt in range(max_retries + 1):
            try:
                request.retry_count = attempt
                response = provider.query(request)
                
                # Update performance metrics
                self._update_performance_metrics(
                    provider.name, True, response.processing_time
                )
                
                # Process output
                processed_outputs = self.output_processor.process(
                    [response], request
                )
                
                if processed_outputs:
                    return processed_outputs[0]
                else:
                    raise ValueError("Output failed processing filters")
                    
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed (attempt {attempt + 1}): {e}")
                self._update_performance_metrics(provider.name, False)
                
                if attempt == max_retries:
                    raise
                
                # Try next best provider for retry
                remaining_providers = [p for p in self.providers if p != provider]
                if remaining_providers:
                    provider = self._select_best_provider(
                        request, exclude=[provider]
                    )
        
        raise RuntimeError("All providers failed")
    
    def _run_multiple_providers(
        self,
        request: LLMRequest,
        max_retries: int
    ) -> List[LLMResponse]:
        """Run query on multiple providers and return ranked results."""
        responses = []
        
        for provider in self.providers:
            try:
                response = provider.query(request)
                responses.append(response)
                
                self._update_performance_metrics(
                    provider.name, True, response.processing_time
                )
                
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed: {e}")
                self._update_performance_metrics(provider.name, False)
        
        if not responses:
            raise RuntimeError("All providers failed")
        
        # Process and rank outputs
        return self.output_processor.process(responses, request)
    
    def _select_best_provider(
        self,
        request: LLMRequest,
        exclude: Optional[List[LLMProviderBase]] = None
    ) -> LLMProviderBase:
        """Select best provider based on performance metrics and request requirements."""
        exclude = exclude or []
        available_providers = [p for p in self.providers if p not in exclude]
        
        if not available_providers:
            raise ValueError("No available providers")
        
        # Calculate provider scores
        provider_scores = {}
        for provider in available_providers:
            metrics = self.provider_performance[provider.name]
            
            # Calculate success rate
            total_requests = metrics['success'] + metrics['failure']
            success_rate = metrics['success'] / max(total_requests, 1)
            
            # Calculate speed score (inverse of average time)
            speed_score = 1 / max(metrics['avg_time'], 0.1)
            
            # Combine scores
            provider_scores[provider] = (success_rate * 0.7) + (speed_score * 0.3)
        
        # Return provider with highest score
        return max(provider_scores.keys(), key=lambda p: provider_scores[p])
    
    def _update_performance_metrics(
        self,
        provider_name: str,
        success: bool,
        processing_time: Optional[float] = None
    ) -> None:
        """Update provider performance metrics."""
        metrics = self.provider_performance[provider_name]
        
        if success:
            metrics['success'] += 1
            if processing_time:
                # Update rolling average
                total_requests = metrics['success'] + metrics['failure']
                if total_requests == 1:
                    metrics['avg_time'] = processing_time
                else:
                    metrics['avg_time'] = (
                        (metrics['avg_time'] * (total_requests - 1) + processing_time) /
                        total_requests
                    )
        else:
            metrics['failure'] += 1
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get comprehensive provider status and metrics."""
        status = {}
        
        for provider in self.providers:
            metrics = self.provider_performance[provider.name]
            total_requests = metrics['success'] + metrics['failure']
            
            status[provider.name] = {
                'metadata': provider.get_metadata(),
                'success_rate': metrics['success'] / max(total_requests, 1),
                'average_response_time': metrics['avg_time'],
                'total_requests': total_requests,
                'status': 'active' if total_requests > 0 else 'ready'
            }
        
        return status


class LLMAbstraction:
    """Unified entry point for LLM queries using config-driven provider selection."""
    def __init__(self, enable_mcp: bool = True):
        import os
        # Load from llm_config.json instead of llm_factories.json
        config_path = os.path.join(os.path.dirname(__file__), '../../config/llm_config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        active_provider = config['active_provider']
        provider_config = config['providers'][active_provider]
        
        # Instantiate the correct provider based on active_provider
        if active_provider == 'ollama':
            self.provider = OllamaProvider(
                base_url=provider_config['base_url'],
                model=provider_config['model'],
                timeout=provider_config.get('timeout', 300)
            )
        elif active_provider == 'openai':
            self.provider = OpenAIProvider(
                api_key=os.environ.get('OPENAI_API_KEY', ''),
                endpoint=provider_config['base_url'],
                config=provider_config
            )
        elif active_provider == 'anthropic':
            self.provider = AnthropicProvider(
                api_key=os.environ.get('ANTHROPIC_API_KEY', ''),
                endpoint=provider_config['base_url'],
                config=provider_config
            )
        else:
            raise ValueError(f"Unsupported provider: {active_provider}")
            
        self.prompt_engineer = PromptEngineer()
        self.context_manager = ContextManager()
        self.output_processor = OutputProcessor()
        
        # MCP Integration
        self.mcp_enabled = enable_mcp
        self.mcp_integrator = None
        
        if self.mcp_enabled:
            try:
                from llm_abstraction.mcp.integration import MCPLLMIntegrator
                self.mcp_integrator = MCPLLMIntegrator()
                logger.info("MCP integration enabled")
            except ImportError:
                logger.warning("MCP integration not available")
                self.mcp_enabled = False

    async def initialize_mcp(self) -> bool:
        """Initialize MCP integration"""
        if not self.mcp_enabled or not self.mcp_integrator:
            return False
        
        try:
            return await self.mcp_integrator.initialize()
        except Exception as e:
            logger.error(f"Failed to initialize MCP: {e}")
            return False

    def query(self, prompt: str, context: Optional[Dict[str, Any]] = None, max_tokens: int = 1000, temperature: float = 0.7) -> LLMResponse:
        # Engineer prompt
        engineered_prompt = self.prompt_engineer.engineer(prompt, context)
        # Optimize context
        optimized_context = self.context_manager.optimize(context or {})
        # Build request
        request = LLMRequest(
            prompt=engineered_prompt,
            context=optimized_context,
            max_tokens=max_tokens,
            temperature=temperature
        )
        # Query provider
        response = self.provider.query(request)
        # Process output
        processed = self.output_processor.process([response], request)
        return processed[0] if processed else response

    async def query_with_mcp(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        auto_execute_mcp: bool = True
    ) -> Dict[str, Any]:
        """Query with MCP integration (async version)"""
        if not self.mcp_enabled or not self.mcp_integrator:
            # Fall back to regular query
            response = self.query(prompt, context, max_tokens, temperature)
            return {
                'llm_response': response,
                'mcp_results': {},
                'mcp_enabled': False
            }
        
        # Get MCP context
        mcp_context = await self.mcp_integrator.get_mcp_context_for_llm()
        mcp_context_str = self.mcp_integrator.format_mcp_context_for_prompt(mcp_context)
        
        # Enhance prompt with MCP context
        enhanced_prompt = f"{mcp_context_str}\n\nUser Query: {prompt}" if mcp_context_str else prompt
        
        # Execute regular query
        response = self.query(enhanced_prompt, context, max_tokens, temperature)
        
        # Process response for MCP calls
        mcp_results = await self.mcp_integrator.process_llm_response_for_mcp_calls(
            response.content, auto_execute_mcp
        )
        
        return {
            'llm_response': response,
            'mcp_results': mcp_results,
            'mcp_enabled': True,
            'mcp_context_included': bool(mcp_context_str)
        }

    def get_mcp_functions(self) -> List[Dict[str, Any]]:
        """Get list of available MCP functions"""
        if not self.mcp_enabled or not self.mcp_integrator or not self.mcp_integrator.mcp_client:
            return []
        
        return self.mcp_integrator.mcp_client.list_functions()

    async def execute_mcp_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP function directly"""
        if not self.mcp_enabled or not self.mcp_integrator:
            raise RuntimeError("MCP not enabled or not initialized")
        
        return await self.mcp_integrator.execute_mcp_function(function_name, arguments)

    def get_mcp_documentation(self) -> str:
        """Get MCP function documentation"""
        if not self.mcp_enabled or not self.mcp_integrator:
            return "MCP not available"
        
        return self.mcp_integrator.get_function_documentation()

    async def shutdown_mcp(self):
        """Shutdown MCP integration"""
        if self.mcp_integrator:
            await self.mcp_integrator.shutdown()
