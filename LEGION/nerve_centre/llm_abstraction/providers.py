"""
Real LLM Provider Implementations
"""
import requests
import logging
import os
import time
from typing import Any, Dict, Optional
from .base import LLMProviderBase, LLMRequest, LLMResponse


class OllamaProvider(LLMProviderBase):
    """Ollama local LLM provider implementation."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral:7b", timeout: int = 300, flash_attention: bool = True, num_threads: int = 8, quantization: str = "Q4_K_M"):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout
        self.flash_attention = flash_attention
        self.num_threads = num_threads
        self.quantization = quantization
    
    def query(self, request):
        try:
            payload = {
                "model": self.model,
                "prompt": request.prompt,
                "stream": False,
                "options": {
                    "temperature": request.temperature if request.temperature is not None else 0.7,
                    "top_p": request.context["top_p"] if request.context and "top_p" in request.context else 0.9,
                    "max_tokens": request.max_tokens if request.max_tokens is not None else 2048,
                    "flash_attention": self.flash_attention,
                    "num_threads": self.num_threads,
                    "quantization": self.quantization
                }
            }
            if request.context and "system" in request.context:
                payload["system"] = request.context["system"]
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            return LLMResponse(
                content=data["response"],
                provider="ollama",
                timestamp=time.time(),
                tokens_used=data.get("tokens", None),
                processing_time=data.get("duration", None),
                metadata={"model": self.model}
            )
        except requests.exceptions.ConnectionError:
            logging.error("Ollama server not available. Is Ollama running?")
            raise
        except Exception as e:
            logging.error(f"Ollama API error: {e}")
            raise
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Ollama",
            "model": self.model,
            "provider_type": "local",
            "capabilities": ["chat", "completion", "embedding"],
            "base_url": self.base_url
        }


class LlamaCppProvider(LLMProviderBase):
    """Llama.cpp server provider implementation."""
    
    def __init__(self, base_url: str = "http://localhost:8080", model_path: str = "./models/", timeout: int = 300, flash_attention: bool = True, num_threads: int = 8, quantization: str = "Q4_K_M"):
        self.base_url = base_url.rstrip('/')
        self.model_path = model_path
        self.timeout = timeout
        self.flash_attention = flash_attention
        self.num_threads = num_threads
        self.quantization = quantization
    
    def query(self, request):
        try:
            payload = {
                "prompt": request.prompt,
                "n_predict": request.max_tokens if request.max_tokens is not None else 2048,
                "temperature": request.temperature if request.temperature is not None else 0.7,
                "top_p": request.context["top_p"] if request.context and "top_p" in request.context else 0.9,
                "stop": request.context["stop"] if request.context and "stop" in request.context else [],
                "stream": False,
                "flash_attention": self.flash_attention,
                "num_threads": self.num_threads,
                "quantization": self.quantization
            }
            response = requests.post(
                f"{self.base_url}/completion",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            return LLMResponse(
                content=data["content"],
                provider="llamacpp",
                timestamp=time.time(),
                tokens_used=data.get("tokens", None),
                processing_time=data.get("duration", None),
                metadata={"model_path": self.model_path}
            )
        except requests.exceptions.ConnectionError:
            logging.error("Llama.cpp server not available. Is llama.cpp server running?")
            raise
        except Exception as e:
            logging.error(f"Llama.cpp API error: {e}")
            raise
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Llama.cpp",
            "model": "local-model",
            "provider_type": "local",
            "capabilities": ["completion", "chat"],
            "base_url": self.base_url
        }


class LocalAIProvider(LLMProviderBase):
    """LocalAI provider implementation."""
    
    def __init__(self, base_url: str = "http://localhost:8080", api_key: str = "", model: str = "gpt-3.5-turbo", timeout: int = 300):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    def query(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        try:
            messages = [{"role": "user", "content": prompt}]
            if context and "system" in context:
                messages.insert(0, {"role": "system", "content": context["system"]})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": context.get("max_tokens", 2048) if context else 2048,
                "temperature": context.get("temperature", 0.7) if context else 0.7
            }
            
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logging.error(f"LocalAI API error: {e}")
            raise
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "LocalAI",
            "model": self.model,
            "provider_type": "local",
            "capabilities": ["chat", "completion", "embedding"],
            "base_url": self.base_url
        }


class LLMStudioProvider(LLMProviderBase):
    """LM Studio provider implementation."""
    
    def __init__(self, base_url: str = "http://localhost:1234", api_key: str = "", model: str = "local-model", timeout: int = 300):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    def query(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        try:
            messages = [{"role": "user", "content": prompt}]
            if context and "system" in context:
                messages.insert(0, {"role": "system", "content": context["system"]})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": context.get("max_tokens", 2048) if context else 2048,
                "temperature": context.get("temperature", 0.7) if context else 0.7,
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logging.error(f"LM Studio API error: {e}")
            raise
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "LM Studio",
            "model": self.model,
            "provider_type": "local",
            "capabilities": ["chat", "completion"],
            "base_url": self.base_url
        }


class OpenAIProvider(LLMProviderBase):
    """OpenAI GPT provider implementation."""
    
    def __init__(self, api_key: str, model: str = "gpt-4", base_url: str = "https://api.openai.com/v1", timeout: int = 60):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def query(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        try:
            messages = [{"role": "user", "content": prompt}]
            if context and "system" in context:
                messages.insert(0, {"role": "system", "content": context["system"]})
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": context.get("max_tokens", 1000) if context else 1000,
                    "temperature": context.get("temperature", 0.7) if context else 0.7
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            raise
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "OpenAI",
            "model": self.model,
            "provider_type": "cloud",
            "capabilities": ["chat", "completion", "function_calling"],
            "base_url": self.base_url
        }


class GeminiProvider(LLMProviderBase):
    """Google Gemini provider implementation."""
    
    def __init__(self, api_key: str, model: str = "gemini-pro", base_url: str = "https://generativelanguage.googleapis.com/v1beta", timeout: int = 60):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
    
    def query(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        try:
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": context.get("temperature", 0.7) if context else 0.7,
                    "maxOutputTokens": context.get("max_tokens", 2048) if context else 2048,
                }
            }
            
            response = requests.post(
                f"{self.base_url}/models/{self.model}:generateContent",
                params={"key": self.api_key},
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            logging.error(f"Gemini API error: {e}")
            raise
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Gemini",
            "model": self.model,
            "provider_type": "cloud",
            "capabilities": ["chat", "completion", "multimodal"],
            "base_url": self.base_url
        }


class AnthropicProvider(LLMProviderBase):
    """Anthropic Claude provider implementation."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229", base_url: str = "https://api.anthropic.com/v1", timeout: int = 60):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
    
    def query(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        try:
            messages = [{"role": "user", "content": prompt}]
            
            payload = {
                "model": self.model,
                "max_tokens": context.get("max_tokens", 1000) if context else 1000,
                "messages": messages,
                "temperature": context.get("temperature", 0.7) if context else 0.7
            }
            
            if context and "system" in context:
                payload["system"] = context["system"]
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["content"][0]["text"]
        except Exception as e:
            logging.error(f"Anthropic API error: {e}")
            raise
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Anthropic",
            "model": self.model,
            "provider_type": "cloud",
            "capabilities": ["chat", "completion", "analysis"],
            "base_url": self.base_url
        }


class HuggingFaceProvider(LLMProviderBase):
    """Hugging Face Inference API provider implementation."""
    
    def __init__(self, api_key: str, model: str = "microsoft/DialoGPT-large", base_url: str = "https://api-inference.huggingface.co/models", timeout: int = 60):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def query(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": context.get("max_tokens", 512) if context else 512,
                    "temperature": context.get("temperature", 0.7) if context else 0.7,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                f"{self.base_url}/{self.model}",
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
            return str(result)
        except Exception as e:
            logging.error(f"Hugging Face API error: {e}")
            raise
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Hugging Face",
            "model": self.model,
            "provider_type": "cloud",
            "capabilities": ["completion", "generation"],
            "base_url": self.base_url
        }
