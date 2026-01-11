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


class DummyProvider(AIProvider):
    """Minimal development provider that returns deterministic summaries and embeddings.

    Use for offline testing and local reflection when no external API is available.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = config.get('model', 'dummy')

    async def generate(self, prompt: str, system_message: Optional[str] = None, temperature: Optional[float] = None, max_tokens: Optional[int] = None, tools: Optional[List[Dict]] = None) -> Dict[str, Any]:
        content = f"DEV_SUMMARY: {prompt[:800]}"
        return {"content": content, "model": self.model, "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}, "finish_reason": "stop"}

    async def generate_streaming(self, prompt: str, system_message: Optional[str] = None, temperature: Optional[float] = None, max_tokens: Optional[int] = None):
        yield f"DEV_SUMMARY: {prompt[:800]}"

    async def embed(self, text: str) -> List[float]:
        # Return a small zero vector for testing
        return [0.0] * 16


class OllamaProvider(AIProvider):
    """Ollama local provider using the Ollama CLI for runs.

    Falls back to HTTP host if `OLLAMA_HOST` is set. Prefers CLI (fast and supports installed models).
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        import shutil
        self.model = config.get('model') or os.getenv('AI_MODEL') or os.getenv('OLLAMA_MODEL')
        self.ollama_cli = shutil.which('ollama')
        self.host = os.getenv('OLLAMA_HOST', 'http://127.0.0.1:11434')
        if not self.model:
            raise ValueError('OllamaProvider requires a model name via config or OLLAMA_MODEL env')

    async def generate(self, prompt: str, system_message: Optional[str] = None, temperature: Optional[float] = None, max_tokens: Optional[int] = None, tools: Optional[List[Dict]] = None) -> Dict[str, Any]:
        full_prompt = prompt
        if system_message:
            full_prompt = f"{system_message}\n\n{prompt}"

        # Prefer CLI if available
        if self.ollama_cli:
            import asyncio, shlex
            cmd = [self.ollama_cli, 'run', self.model, full_prompt]
            proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            out, err = await proc.communicate()
            if proc.returncode != 0:
                self.logger.error('Ollama CLI error: %s', err.decode('utf-8', errors='replace'))
                raise RuntimeError('Ollama CLI failed')
            content = out.decode('utf-8', errors='replace')
            return {"content": content.strip(), "model": self.model, "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}, "finish_reason": "stop"}

        # Otherwise, try HTTP endpoint (best-effort)
        try:
            import httpx
            url = f"{self.host}/api/generate"
            payload = {"model": self.model, "prompt": full_prompt}
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json=payload, timeout=30.0)
                r.raise_for_status()
                j = r.json()
                # Ollama HTTP might return plain text or JSON with 'output'
                if isinstance(j, dict) and 'output' in j:
                    content = j['output'][0] if isinstance(j['output'], list) else j['output']
                else:
                    content = str(j)
                return {"content": content, "model": self.model, "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}, "finish_reason": "stop"}
        except Exception as e:
            self.logger.error('Ollama HTTP generation failed: %s', e)
            raise

    async def generate_streaming(self, prompt: str, system_message: Optional[str] = None, temperature: Optional[float] = None, max_tokens: Optional[int] = None):
        # Use simple non-streaming wrapper for now
        result = await self.generate(prompt, system_message=system_message, temperature=temperature, max_tokens=max_tokens)
        yield result['content']

    async def embed(self, text: str) -> List[float]:
        # Ollama CLI/HTTP may not provide embeddings; return zero vector as fallback
        return [0.0] * 16


class GeminiProvider(AIProvider):
    """Google Gemini provider via the Google Generative AI Python SDK (google.generativeai).

    Use env var `GEMINI_API_KEY` or `GOOGLE_API_KEY` if not provided in config.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Try to import either the new `google.genai` package, the google.ai.generativelanguage client, or legacy `google.generativeai`.
        self._use_ga = False
        self._use_gal = False
        try:
            import google.genai as genai
            self.genai = genai
            self._use_ga = True
        except Exception:
            try:
                import google.ai.generativelanguage as gal
                self.genai = gal
                self._use_gal = True
            except Exception:
                try:
                    import google.generativeai as genai_legacy
                    self.genai = genai_legacy
                except Exception:
                    raise ImportError("Gemini provider requires google-genai (preferred) or google-ai-generativelanguage or google-generativeai. Install one of these packages.")

        key = config.get('api_key') or os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not key:
            raise ValueError('Gemini provider requires GEMINI_API_KEY or GOOGLE_API_KEY to be set')

        # Ensure environment key is available for Google clients that read env vars
        os.environ.setdefault('GOOGLE_API_KEY', key)

        # If the preferred genai package supports configure, try to use it
        try:
            if hasattr(self.genai, 'configure'):
                self.genai.configure(api_key=key)
        except Exception:
            pass

        self.client = self.genai
        self.model = config.get('model') or os.getenv('AI_MODEL', 'gemini-pro')

    async def generate(self, prompt: str, system_message: Optional[str] = None, temperature: Optional[float] = None, max_tokens: Optional[int] = None, tools: Optional[List[Dict]] = None) -> Dict[str, Any]:
        # Build content/messages depending on SDK expectations
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        import asyncio
        loop = asyncio.get_running_loop()

        def _call():
            # Try multiple SDK call patterns for compatibility across installed Google SDKs
            try:
                # 1) New google.genai (if present)
                if self._use_ga and hasattr(self.client, 'chat') and hasattr(self.client.chat, 'create'):
                    return self.client.chat.create(model=self.model, messages=messages, temperature=temperature if temperature is not None else self.config.get('temperature', 0.7), max_output_tokens=max_tokens if max_tokens is not None else self.config.get('max_tokens', 1024))
                if self._use_ga and hasattr(self.client, 'chat') and hasattr(self.client.chat, 'generate'):
                    return self.client.chat.generate(model=self.model, messages=messages, temperature=temperature if temperature is not None else self.config.get('temperature', 0.7), max_output_tokens=max_tokens if max_tokens is not None else self.config.get('max_tokens', 1024))

                # 2) google.ai.generativelanguage client
                if self._use_gal and hasattr(self.client, 'TextServiceClient'):
                    # Use a TextServiceClient to perform text generation
                    from google.ai.generativelanguage import TextServiceClient
                    client = TextServiceClient()
                    request = {"model": self.model, "prompt": {"text": '\n'.join([m.get('content','') for m in messages])}}
                    return client.generate_text(request=request)

                # 3) Legacy google.generativeai or other variants providing generate
                if hasattr(self.client, 'generate'):
                    flat = ('\n'.join([m.get('content','') for m in messages]))
                    return self.client.generate(model=self.model, prompt=flat, temperature=temperature if temperature is not None else self.config.get('temperature', 0.7), max_output_tokens=max_tokens if max_tokens is not None else self.config.get('max_tokens', 1024))

                # 4) Try text.generate if available
                if hasattr(self.client, 'text') and hasattr(self.client.text, 'generate'):
                    flat = ('\n'.join([m.get('content','') for m in messages]))
                    return self.client.text.generate(model=self.model, input=flat, temperature=temperature if temperature is not None else self.config.get('temperature', 0.7), max_output_tokens=max_tokens if max_tokens is not None else self.config.get('max_tokens', 1024))
            except Exception as e:
                return e

            raise RuntimeError('Unable to call Gemini API using installed SDK variant')

        resp = await loop.run_in_executor(None, _call)

        # Normalize response to extract text content
        content = ''
        try:
            # genai.chat.create -> resp.candidates[0].content
            if hasattr(resp, 'candidates') and resp.candidates:
                content = getattr(resp.candidates[0], 'content', str(resp.candidates[0]))
            # dict-like responses
            elif isinstance(resp, dict):
                if 'candidates' in resp and resp['candidates']:
                    c = resp['candidates'][0]
                    content = c.get('content') if isinstance(c, dict) else str(c)
                elif 'output' in resp:
                    out = resp['output']
                    if isinstance(out, list):
                        content = str(out[0])
                    else:
                        content = str(out)
                elif 'text' in resp:
                    content = resp['text']
                else:
                    content = str(resp)
            else:
                # Some SDKs return an object with .text or .content
                content = getattr(resp, 'text', getattr(resp, 'content', str(resp)))
        except Exception:
            content = str(resp)

        return {"content": content, "model": self.model, "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}, "finish_reason": "stop"}

    async def generate_streaming(self, prompt: str, system_message: Optional[str] = None, temperature: Optional[float] = None, max_tokens: Optional[int] = None):
        # Use non-streaming wrapper for now
        result = await self.generate(prompt, system_message=system_message, temperature=temperature, max_tokens=max_tokens)
        yield result['content']

    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using available Gemini SDKs or fall back to OpenAI.

        Tries multiple SDK patterns (genai.embeddings.create, gal EmbeddingsClient, legacy client
        or text.generate variants). If all fail and OpenAI is available, use OpenAI embeddings as fallback.
        """
        import asyncio
        loop = asyncio.get_running_loop()

        def _call_embed():
            # 1) Preferred google.genai with embeddings
            try:
                if self._use_ga:
                    if hasattr(self.client, 'embeddings') and hasattr(self.client.embeddings, 'create'):
                        r = self.client.embeddings.create(model='textembedding-gecko-001', input=text)
                        return r.data[0].embedding
                    if hasattr(self.client, 'embeddings') and hasattr(self.client.embeddings, 'generate'):
                        r = self.client.embeddings.generate(model='textembedding-gecko-001', input=text)
                        return r.data[0].embedding
            except Exception:
                pass

            # 2) google.ai.generativelanguage EmbeddingsClient pattern
            try:
                if self._use_gal:
                    from google.ai import generativelanguage as gal_mod
                    try:
                        client = gal_mod.EmbeddingsClient()
                        resp = client.create(model='textembedding-gecko-001', input=text)
                        # resp may have .data[0].embedding or .embeddings
                        if hasattr(resp, 'data') and resp.data:
                            return resp.data[0].embedding
                        if hasattr(resp, 'embeddings') and resp.embeddings:
                            return resp.embeddings[0].embedding
                    except Exception:
                        # Some versions may require request object
                        try:
                            resp = client.embed(request={'model':'textembedding-gecko-001','input':text})
                            return resp.data[0].embedding
                        except Exception:
                            pass
            except Exception:
                pass

            # 3) Legacy google.generativeai pattern
            try:
                if hasattr(self.client, 'embeddings') and callable(getattr(self.client, 'embeddings')):
                    r = self.client.embeddings(model='textembedding-gecko-001', input=text)
                    if isinstance(r, dict) and 'data' in r:
                        return r['data'][0]['embedding']
            except Exception:
                pass

            # 4) Try .text.generate style (some SDKs expose a text.generate that returns embeddings)
            try:
                if hasattr(self.client, 'text') and hasattr(self.client.text, 'embed'):
                    r = self.client.text.embed(model='textembedding-gecko-001', input=text)
                    return r.data[0].embedding
            except Exception:
                pass

            # 5) Fallback to OpenAI (synchronous call) if installed
            try:
                import openai
                r = openai.Embedding.create(model='text-embedding-3-small', input=text)
                return r['data'][0]['embedding']
            except Exception:
                pass

            # Final fallback: zero vector
            return [0.0] * 16

        return await loop.run_in_executor(None, _call_embed)

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
        'dummy': DummyProvider,
        'ollama': OllamaProvider,
        'gemini': GeminiProvider,
    }
    
    provider_class = providers.get(provider_name)
    if not provider_class:
        raise ValueError(f"Unknown AI provider: {provider_name}")
    
    return provider_class(config)
