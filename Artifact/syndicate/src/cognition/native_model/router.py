"""
Native Tool Router - Routes queries to tools using embedded GGUF model.

Architecture:
1. Tiny GGUF model (~100MB) fine-tuned on tool schemas
2. Ultra-fast routing (<10ms latency)
3. Fallback to Ollama for complex reasoning
4. Zero external API calls for basic tool selection
"""

import os
import json
import logging
import subprocess
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

# Check for llama.cpp availability
NATIVE_MODEL_AVAILABLE = False
LLAMA_CPP_PATH = None

# Try common llama.cpp locations
for llama_path in [
    Path("/usr/local/bin/llama-cli"),
    Path.home() / ".local" / "bin" / "llama-cli",
    Path("/opt/llama.cpp/llama-cli"),
    Path(__file__).parent.parent.parent.parent.parent / "hektor" / "build" / "llama-cli",
]:
    if llama_path.exists():
        LLAMA_CPP_PATH = llama_path
        NATIVE_MODEL_AVAILABLE = True
        break


@dataclass
class ToolRoutingResult:
    """Result of tool routing decision."""
    tool_name: str
    arguments: Dict[str, Any]
    confidence: float
    latency_ms: float
    source: str  # "native", "ollama", "fallback"
    raw_response: Optional[str] = None
    error: Optional[str] = None
    
    @property
    def success(self) -> bool:
        return self.error is None and self.tool_name is not None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "confidence": self.confidence,
            "latency_ms": self.latency_ms,
            "source": self.source,
            "success": self.success,
            "error": self.error
        }


class NativeToolRouter:
    """
    Routes queries to appropriate tools using native GGUF model.
    
    Layered approach:
    1. Native GGUF model (tiny, fast) - for simple tool routing
    2. Ollama (local LLM) - for complex reasoning
    3. Pattern matching fallback - when models unavailable
    
    Usage:
        router = NativeToolRouter(model_path="./models/tool-router.gguf")
        result = router.route("Search for gold price analysis")
        # result.tool_name = "search"
        # result.arguments = {"query": "gold price analysis", "k": 5}
    """
    
    # Common tool patterns for fallback routing
    TOOL_PATTERNS = {
        "search": [
            r"search\s+(?:for\s+)?(.+)",
            r"find\s+(?:me\s+)?(.+)",
            r"look\s+(?:up|for)\s+(.+)",
            r"query\s+(.+)",
        ],
        "read_file": [
            r"read\s+(?:file\s+)?(.+\.\w+)",
            r"show\s+(?:me\s+)?(?:the\s+)?(?:contents?\s+of\s+)?(.+\.\w+)",
            r"open\s+(.+\.\w+)",
            r"cat\s+(.+\.\w+)",
        ],
        "list_dir": [
            r"list\s+(?:files?\s+in\s+)?(.+)",
            r"ls\s+(.+)",
            r"show\s+(?:files?\s+in\s+)?(.+)",
            r"what's\s+in\s+(.+)",
        ],
        "remember": [
            r"remember\s+(?:that\s+)?(.+)",
            r"save\s+(?:the\s+)?(?:note|memory)\s+(.+)",
            r"store\s+(.+)",
        ],
        "recall": [
            r"recall\s+(.+)",
            r"what\s+do\s+(?:i|you)\s+know\s+about\s+(.+)",
            r"remind\s+me\s+about\s+(.+)",
        ],
        "get_context": [
            r"get\s+context\s+(?:for\s+)?(.+)",
            r"context\s+(?:for|about)\s+(.+)",
            r"what's\s+the\s+context\s+(?:for|of)\s+(.+)",
        ],
        "read_db": [
            r"query\s+(?:the\s+)?(\w+)\s+database",
            r"select\s+.+\s+from\s+(\w+)",
            r"read\s+from\s+(\w+)",
        ],
    }
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        ollama_model: str = "qwen2.5:0.5b",
        ollama_host: str = "http://localhost:11434",
        use_native: bool = True,
        use_ollama: bool = True,
        logger: Optional[logging.Logger] = None
    ):
        self.model_path = Path(model_path) if model_path else None
        self.ollama_model = ollama_model
        self.ollama_host = ollama_host
        self.use_native = use_native and NATIVE_MODEL_AVAILABLE
        self.use_ollama = use_ollama
        self.logger = logger or logging.getLogger(__name__)
        
        # Validate model path if provided
        if self.use_native and self.model_path:
            if not self.model_path.exists():
                self.logger.warning(f"Model not found: {self.model_path}, disabling native routing")
                self.use_native = False
        
        # Load tool definitions for prompt building
        try:
            from ..tool_calling import TOOL_REGISTRY
            self.tool_registry = TOOL_REGISTRY
        except ImportError:
            self.tool_registry = None
        
        self._init_system_prompt()
        
        # Routing statistics
        self._stats = {
            "native_calls": 0,
            "ollama_calls": 0,
            "fallback_calls": 0,
            "total_latency_ms": 0.0,
            "errors": 0
        }
        
        self.logger.info(f"NativeToolRouter initialized (native={self.use_native}, ollama={self.use_ollama})")
    
    def _init_system_prompt(self):
        """Initialize the system prompt for tool routing."""
        tool_list = ""
        if self.tool_registry:
            for name, tool in self.tool_registry.tools.items():
                params = ", ".join(f"{p.name}: {p.param_type}" for p in tool.parameters)
                tool_list += f"- {name}({params}): {tool.description}\n"
        else:
            tool_list = """- search(query: str, k: int): Semantic search
- hybrid_search(query: str, k: int): Vector + BM25 search
- read_file(path: str): Read file contents
- write_file(path: str, content: str): Write to file
- list_dir(path: str): List directory
- remember(key: str, value: str): Store memory
- recall(query: str, k: int): Recall memories
- get_context(query: str, k: int): Get context
- read_db(name: str, query: str): Read from database
- list_databases(): List databases
- get_tools(): List available tools"""
        
        self.system_prompt = f"""You are a tool router. Given a user query, output a JSON object with the tool to call.

Available tools:
{tool_list}

Output format:
{{"tool": "<tool_name>", "args": {{...}}}}

IMPORTANT: Only output the JSON, no explanation."""
    
    def route(
        self,
        query: str,
        context: Optional[str] = None,
        prefer_source: Optional[str] = None
    ) -> ToolRoutingResult:
        """
        Route a query to the appropriate tool.
        
        Args:
            query: User query
            context: Optional context
            prefer_source: Force specific source ("native", "ollama", "fallback")
        
        Returns:
            ToolRoutingResult with tool selection
        """
        start_time = datetime.now()
        
        # Try in order: native -> ollama -> fallback
        result = None
        
        if prefer_source == "native" or (self.use_native and prefer_source is None):
            result = self._route_native(query, context)
            if result.success:
                self._stats["native_calls"] += 1
                self._record_latency(start_time)
                return result
        
        if prefer_source == "ollama" or (self.use_ollama and prefer_source is None):
            result = self._route_ollama(query, context)
            if result.success:
                self._stats["ollama_calls"] += 1
                self._record_latency(start_time)
                return result
        
        # Fallback to pattern matching
        result = self._route_fallback(query)
        self._stats["fallback_calls"] += 1
        
        if not result.success:
            self._stats["errors"] += 1
        
        self._record_latency(start_time)
        return result
    
    def _record_latency(self, start_time: datetime):
        """Record latency statistics."""
        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        self._stats["total_latency_ms"] += elapsed
    
    def _route_native(self, query: str, context: Optional[str] = None) -> ToolRoutingResult:
        """Route using native GGUF model via llama.cpp."""
        start = datetime.now()
        
        if not self.model_path or not self.model_path.exists():
            return ToolRoutingResult(
                tool_name=None,
                arguments={},
                confidence=0.0,
                latency_ms=0.0,
                source="native",
                error="Model not available"
            )
        
        try:
            prompt = f"{self.system_prompt}\n\nUser: {query}\nAssistant:"
            
            # Call llama-cli
            result = subprocess.run(
                [
                    str(LLAMA_CPP_PATH),
                    "-m", str(self.model_path),
                    "-p", prompt,
                    "-n", "100",  # Max tokens
                    "--temp", "0.1",  # Low temperature for deterministic output
                    "-ngl", "0",  # CPU only for speed
                ],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            latency = (datetime.now() - start).total_seconds() * 1000
            
            if result.returncode != 0:
                return ToolRoutingResult(
                    tool_name=None,
                    arguments={},
                    confidence=0.0,
                    latency_ms=latency,
                    source="native",
                    error=f"llama-cli failed: {result.stderr}"
                )
            
            # Parse JSON from output
            output = result.stdout.strip()
            tool_call = self._parse_tool_json(output)
            
            if tool_call:
                return ToolRoutingResult(
                    tool_name=tool_call.get("tool"),
                    arguments=tool_call.get("args", {}),
                    confidence=0.9,
                    latency_ms=latency,
                    source="native",
                    raw_response=output
                )
            
            return ToolRoutingResult(
                tool_name=None,
                arguments={},
                confidence=0.0,
                latency_ms=latency,
                source="native",
                error="Failed to parse tool call",
                raw_response=output
            )
            
        except subprocess.TimeoutExpired:
            return ToolRoutingResult(
                tool_name=None,
                arguments={},
                confidence=0.0,
                latency_ms=10000,
                source="native",
                error="Timeout"
            )
        except Exception as e:
            return ToolRoutingResult(
                tool_name=None,
                arguments={},
                confidence=0.0,
                latency_ms=0.0,
                source="native",
                error=str(e)
            )
    
    def _route_ollama(self, query: str, context: Optional[str] = None) -> ToolRoutingResult:
        """Route using Ollama API."""
        start = datetime.now()
        
        try:
            import httpx
            
            prompt = f"{self.system_prompt}\n\nUser: {query}\nAssistant:"
            
            response = httpx.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 100,
                    }
                },
                timeout=30.0
            )
            
            latency = (datetime.now() - start).total_seconds() * 1000
            
            if response.status_code != 200:
                return ToolRoutingResult(
                    tool_name=None,
                    arguments={},
                    confidence=0.0,
                    latency_ms=latency,
                    source="ollama",
                    error=f"HTTP {response.status_code}"
                )
            
            data = response.json()
            output = data.get("response", "").strip()
            
            tool_call = self._parse_tool_json(output)
            
            if tool_call:
                return ToolRoutingResult(
                    tool_name=tool_call.get("tool"),
                    arguments=tool_call.get("args", {}),
                    confidence=0.8,
                    latency_ms=latency,
                    source="ollama",
                    raw_response=output
                )
            
            return ToolRoutingResult(
                tool_name=None,
                arguments={},
                confidence=0.0,
                latency_ms=latency,
                source="ollama",
                error="Failed to parse tool call",
                raw_response=output
            )
            
        except Exception as e:
            latency = (datetime.now() - start).total_seconds() * 1000
            return ToolRoutingResult(
                tool_name=None,
                arguments={},
                confidence=0.0,
                latency_ms=latency,
                source="ollama",
                error=str(e)
            )
    
    def _route_fallback(self, query: str) -> ToolRoutingResult:
        """Route using pattern matching fallback."""
        start = datetime.now()
        query_lower = query.lower()
        
        for tool_name, patterns in self.TOOL_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, query_lower, re.IGNORECASE)
                if match:
                    # Extract the matched group as the main argument
                    arg_value = match.group(1) if match.groups() else query
                    
                    # Build arguments based on tool
                    if tool_name == "search":
                        args = {"query": arg_value, "k": 5}
                    elif tool_name == "read_file":
                        args = {"path": arg_value}
                    elif tool_name == "list_dir":
                        args = {"path": arg_value if arg_value != query_lower else "."}
                    elif tool_name == "remember":
                        # Split into key and value
                        parts = arg_value.split(":", 1)
                        args = {"key": parts[0].strip(), "value": parts[1].strip() if len(parts) > 1 else arg_value}
                    elif tool_name == "recall":
                        args = {"query": arg_value, "k": 5}
                    elif tool_name == "get_context":
                        args = {"query": arg_value, "k": 3}
                    elif tool_name == "read_db":
                        args = {"name": match.group(1), "query": "SELECT * FROM sqlite_master LIMIT 5"}
                    else:
                        args = {"query": arg_value}
                    
                    latency = (datetime.now() - start).total_seconds() * 1000
                    return ToolRoutingResult(
                        tool_name=tool_name,
                        arguments=args,
                        confidence=0.5,  # Lower confidence for pattern matching
                        latency_ms=latency,
                        source="fallback"
                    )
        
        # Default to search if no pattern matched
        latency = (datetime.now() - start).total_seconds() * 1000
        return ToolRoutingResult(
            tool_name="search",
            arguments={"query": query, "k": 5},
            confidence=0.3,
            latency_ms=latency,
            source="fallback",
            error="No pattern matched, defaulting to search"
        )
    
    def _parse_tool_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse tool call JSON from model output."""
        # Try to find JSON in the text
        try:
            # Look for JSON object
            match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except json.JSONDecodeError:
            pass
        
        # Try parsing the entire text
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        return None
    
    def stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        total_calls = (
            self._stats["native_calls"] +
            self._stats["ollama_calls"] +
            self._stats["fallback_calls"]
        )
        
        return {
            "native_calls": self._stats["native_calls"],
            "ollama_calls": self._stats["ollama_calls"],
            "fallback_calls": self._stats["fallback_calls"],
            "total_calls": total_calls,
            "errors": self._stats["errors"],
            "avg_latency_ms": (
                self._stats["total_latency_ms"] / total_calls
                if total_calls > 0 else 0.0
            ),
            "native_available": self.use_native,
            "ollama_available": self.use_ollama,
            "model_path": str(self.model_path) if self.model_path else None
        }
    
    def reset_stats(self):
        """Reset routing statistics."""
        self._stats = {
            "native_calls": 0,
            "ollama_calls": 0,
            "fallback_calls": 0,
            "total_latency_ms": 0.0,
            "errors": 0
        }
