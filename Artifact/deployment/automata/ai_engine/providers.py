"""
AI Provider abstraction layer for seamless provider swapping.
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging
import json


class AIProvider(ABC):
    """
    Abstract base class for AI providers.
    
    Enables easy swapping between OpenAI, Anthropic, Cohere, and local models.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize AI provider.
        
        Args:
            config: Provider configuration
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Generate text completion.
        
        Args:
            prompt: User prompt
            system_message: System instruction
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            tools: Available tools for function calling
            
        Returns:
            Response dictionary with content and metadata
        """
        pass
    
    @abstractmethod
    async def generate_streaming(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """
        Generate text completion with streaming.
        
        Args:
            prompt: User prompt
            system_message: System instruction
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Yields:
            Chunks of generated text
        """
        pass
    
    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """
        Generate embeddings for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        pass


class OpenAIProvider(AIProvider):
    """OpenAI provider (GPT-4, GPT-3.5, etc.)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            import openai
            self.client = openai.AsyncOpenAI(
                api_key=config.get('api_key') or os.getenv('AI_API_KEY') or os.getenv('OPENAI_API_KEY')
            )
            self.model = config.get('model', 'gpt-4')
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    async def generate(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Generate completion using OpenAI."""
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.config.get('temperature', 0.7),
            "max_tokens": max_tokens or self.config.get('max_tokens', 2000),
        }
        
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        
        try:
            response = await self.client.chat.completions.create(**kwargs)
            
            result = {
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "finish_reason": response.choices[0].finish_reason,
            }
            
            # Handle tool calls if present
            if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": tc.id,
                        "function": {
                            "name": tc.function.name,
                            "arguments": json.loads(tc.function.arguments)
                        }
                    }
                    for tc in response.choices[0].message.tool_calls
                ]
            
            return result
            
        except Exception as e:
            self.logger.error(f"OpenAI generation failed: {e}")
            raise
    
    async def generate_streaming(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """Generate streaming completion using OpenAI."""
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.config.get('temperature', 0.7),
            max_tokens=max_tokens or self.config.get('max_tokens', 2000),
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using OpenAI."""
        response = await self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding


class AnthropicProvider(AIProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(
                api_key=config.get('api_key') or os.getenv('ANTHROPIC_API_KEY')
            )
            self.model = config.get('model', 'claude-3-opus-20240229')
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
    
    async def generate(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Generate completion using Anthropic Claude."""
        kwargs = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens or self.config.get('max_tokens', 2000),
            "temperature": temperature or self.config.get('temperature', 0.7),
        }
        
        if system_message:
            kwargs["system"] = system_message
        
        if tools:
            kwargs["tools"] = tools
        
        try:
            response = await self.client.messages.create(**kwargs)
            
            result = {
                "content": response.content[0].text if response.content else "",
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
                "finish_reason": response.stop_reason,
            }
            
            # Handle tool use if present
            tool_uses = [block for block in response.content if block.type == "tool_use"]
            if tool_uses:
                result["tool_calls"] = [
                    {
                        "id": tu.id,
                        "function": {
                            "name": tu.name,
                            "arguments": tu.input
                        }
                    }
                    for tu in tool_uses
                ]
            
            return result
            
        except Exception as e:
            self.logger.error(f"Anthropic generation failed: {e}")
            raise
    
    async def generate_streaming(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """Generate streaming completion using Anthropic."""
        kwargs = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens or self.config.get('max_tokens', 2000),
            "temperature": temperature or self.config.get('temperature', 0.7),
            "stream": True
        }
        
        if system_message:
            kwargs["system"] = system_message
        
        async with self.client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text
    
    async def embed(self, text: str) -> List[float]:
        """Anthropic doesn't provide embeddings - fallback to OpenAI."""
        self.logger.warning("Anthropic doesn't provide embeddings, using OpenAI fallback")
        fallback = OpenAIProvider({"api_key": os.getenv('OPENAI_API_KEY')})
        return await fallback.embed(text)


class CohereProvider(AIProvider):
    """Cohere provider."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key') or os.getenv('COHERE_API_KEY')
        self.model = config.get('model', 'command')
        
        try:
            import cohere
            self.client = cohere.AsyncClient(api_key=self.api_key)
        except ImportError:
            raise ImportError("cohere package not installed. Run: pip install cohere")
    
    async def generate(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Generate completion using Cohere."""
        full_prompt = prompt
        if system_message:
            full_prompt = f"{system_message}\n\n{prompt}"
        
        try:
            response = await self.client.generate(
                model=self.model,
                prompt=full_prompt,
                max_tokens=max_tokens or self.config.get('max_tokens', 2000),
                temperature=temperature or self.config.get('temperature', 0.7),
            )
            
            return {
                "content": response.generations[0].text,
                "model": self.model,
                "usage": {
                    "prompt_tokens": 0,  # Cohere doesn't provide this
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
                "finish_reason": "stop",
            }
            
        except Exception as e:
            self.logger.error(f"Cohere generation failed: {e}")
            raise
    
    async def generate_streaming(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """Generate streaming completion using Cohere."""
        full_prompt = prompt
        if system_message:
            full_prompt = f"{system_message}\n\n{prompt}"
        
        async for chunk in self.client.generate_stream(
            model=self.model,
            prompt=full_prompt,
            max_tokens=max_tokens or self.config.get('max_tokens', 2000),
            temperature=temperature or self.config.get('temperature', 0.7),
        ):
            if chunk.text:
                yield chunk.text
    
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using Cohere."""
        response = await self.client.embed(
            texts=[text],
            model="embed-english-v3.0"
        )
        return response.embeddings[0]


class LocalModelProvider(AIProvider):
    """Local model provider (Llama, Mistral, etc.) using llama-cpp-python."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_path = config.get('model_path') or os.getenv('LOCAL_MODEL_PATH')
        self.model_type = config.get('model_type', 'llama')
        
        try:
            from llama_cpp import Llama
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=config.get('context_length', 4096),
                n_threads=config.get('threads', 4),
                n_gpu_layers=config.get('gpu_layers', 0),
            )
        except ImportError:
            raise ImportError("llama-cpp-python not installed. Run: pip install llama-cpp-python")
    
    async def generate(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Generate completion using local model."""
        full_prompt = prompt
        if system_message:
            full_prompt = f"<|system|>\n{system_message}\n<|user|>\n{prompt}\n<|assistant|>\n"
        
        response = self.model(
            full_prompt,
            max_tokens=max_tokens or self.config.get('max_tokens', 2000),
            temperature=temperature or self.config.get('temperature', 0.7),
            stop=["<|user|>", "<|system|>"],
        )
        
        return {
            "content": response['choices'][0]['text'],
            "model": self.model_type,
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            "finish_reason": response['choices'][0]['finish_reason'],
        }
    
    async def generate_streaming(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """Generate streaming completion using local model."""
        full_prompt = prompt
        if system_message:
            full_prompt = f"<|system|>\n{system_message}\n<|user|>\n{prompt}\n<|assistant|>\n"
        
        for chunk in self.model(
            full_prompt,
            max_tokens=max_tokens or self.config.get('max_tokens', 2000),
            temperature=temperature or self.config.get('temperature', 0.7),
            stream=True,
        ):
            yield chunk['choices'][0]['text']
    
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using local model."""
        embedding = self.model.embed(text)
        return embedding


def get_provider(config: Dict[str, Any]) -> AIProvider:
    """
    Factory function to get appropriate AI provider.
    
    Args:
        config: Provider configuration
        
    Returns:
        AI provider instance
    """
    provider_name = config.get('provider', 'openai').lower()
    
    providers = {
        'openai': OpenAIProvider,
        'anthropic': AnthropicProvider,
        'claude': AnthropicProvider,
        'cohere': CohereProvider,
        'local': LocalModelProvider,
    }
    
    provider_class = providers.get(provider_name)
    if not provider_class:
        raise ValueError(f"Unknown AI provider: {provider_name}")
    
    return provider_class(config)
