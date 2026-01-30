
import os, json, urllib.request
import subprocess
import tempfile

class BaseAdapter:
    """Base adapter class for AI-agnostic implementation"""
    def call(self, system, messages, tools):
        raise NotImplementedError("Subclasses must implement call()")

class LlamaCppAdapter(BaseAdapter):
    """
    Primary adapter using llama.cpp server.
    Simple, robust, and failproof implementation.
    
    Requirements:
    - llama.cpp server running locally or remotely
    - Compatible with OpenAI-style API endpoint
    
    Environment variables:
    - LLAMA_SERVER_URL: Server URL (default: http://localhost:8080)
    - LLAMA_MODEL: Model name/path (optional, server already has model loaded)
    - LLAMA_MAX_TOKENS: Maximum tokens to generate (default: 2048)
    - LLAMA_TEMPERATURE: Temperature for sampling (default: 0.7)
    - LLAMA_TIMEOUT: Request timeout in seconds (default: 120)
    """
    
    def __init__(self):
        self.server_url = os.environ.get("LLAMA_SERVER_URL", "http://localhost:8080")
        self.model = os.environ.get("LLAMA_MODEL", "local-model")
        self.max_tokens = int(os.environ.get("LLAMA_MAX_TOKENS", "2048"))
        self.temperature = float(os.environ.get("LLAMA_TEMPERATURE", "0.7"))
        self.timeout = int(os.environ.get("LLAMA_TIMEOUT", "120"))
        
        # Ensure server URL doesn't have trailing slash
        self.server_url = self.server_url.rstrip('/')
        
        # Check server availability at initialization
        try:
            self._check_server()
        except Exception as e:
            print(f"[WARNING] llama.cpp server not reachable at {self.server_url}: {e}")
            print("[WARNING] Make sure llama.cpp server is running")
    
    def _check_server(self):
        """Check if llama.cpp server is available"""
        try:
            req = urllib.request.Request(
                f"{self.server_url}/health",
                method="GET"
            )
            urllib.request.urlopen(req, timeout=5)
        except:
            # Try /v1/models endpoint as fallback
            req = urllib.request.Request(
                f"{self.server_url}/v1/models",
                method="GET"
            )
            urllib.request.urlopen(req, timeout=5)
    
    def call(self, system, messages, tools):
        """
        Call llama.cpp server with robust error handling.
        
        Args:
            system: System prompt string
            messages: List of message dicts with 'role' and 'content'
            tools: List of available tools (for tool-calling models)
        
        Returns:
            List of response content blocks
        """
        try:
            # Build the full message list with system prompt
            full_messages = []
            
            # Add system message if provided
            if system:
                full_messages.append({
                    "role": "system",
                    "content": system
                })
            
            # Add conversation messages
            full_messages.extend(messages)
            
            # Prepare payload for llama.cpp OpenAI-compatible endpoint
            payload = {
                "messages": full_messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "stream": False
            }
            
            # Add model if specified
            if self.model and self.model != "local-model":
                payload["model"] = self.model
            
            # Make request to llama.cpp server
            response = self._make_request("/v1/chat/completions", payload)
            
            # Parse response
            if "choices" in response and len(response["choices"]) > 0:
                message = response["choices"][0].get("message", {})
                content = message.get("content", "")
                
                # Check if this is a tool-calling response
                if tools and "tool_calls" in message:
                    # Return tool calls in Anthropic-style format
                    tool_blocks = []
                    for tool_call in message["tool_calls"]:
                        tool_blocks.append({
                            "type": "tool_use",
                            "name": tool_call["function"]["name"],
                            "input": json.loads(tool_call["function"]["arguments"])
                        })
                    return tool_blocks
                
                # Return text response
                return [{"type": "text", "text": content}]
            
            # Fallback if response format is unexpected
            return [{"type": "text", "text": str(response)}]
            
        except Exception as e:
            # Robust error handling
            error_msg = f"llama.cpp error: {str(e)}"
            print(f"[ERROR] {error_msg}")
            
            # Return error as text response to prevent complete failure
            return [{"type": "text", "text": f"Error: {error_msg}. Using fallback response."}]
    
    def _make_request(self, endpoint, payload):
        """
        Make HTTP request to llama.cpp server with retry logic.
        
        Args:
            endpoint: API endpoint path (e.g., "/v1/chat/completions")
            payload: Request payload dict
        
        Returns:
            Response dict
        """
        url = f"{self.server_url}{endpoint}"
        
        # Prepare request
        data = json.dumps(payload).encode('utf-8')
        headers = {
            "Content-Type": "application/json"
        }
        
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        
        # Execute request with timeout
        try:
            response = urllib.request.urlopen(req, timeout=self.timeout)
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else "No error details"
            raise Exception(f"HTTP {e.code}: {error_body}")
        except urllib.error.URLError as e:
            raise Exception(f"Connection error: {e.reason}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

class OllamaAdapter(BaseAdapter):
    """
    Ollama adapter - uses Ollama's native API.
    Works with locally running Ollama server.
    """
    
    def __init__(self):
        self.server_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        self.model = os.environ.get("LLAMA_MODEL", os.environ.get("OLLAMA_MODEL", "gladius:latest"))
        self.timeout = int(os.environ.get("LLAMA_TIMEOUT", "120"))
        
        # Check server availability
        try:
            req = urllib.request.Request(f"{self.server_url}/api/tags", method="GET")
            urllib.request.urlopen(req, timeout=5)
            print(f"[INFO] Ollama server available at {self.server_url}")
            print(f"[INFO] Using model: {self.model}")
        except Exception as e:
            print(f"[WARNING] Ollama server not reachable: {e}")
    
    def call(self, system, messages, tools):
        """Call Ollama API"""
        try:
            # Build prompt from system and messages
            prompt = ""
            if system:
                prompt = f"System: {system}\n\n"
            
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    prompt += f"User: {content}\n"
                elif role == "assistant":
                    prompt += f"Assistant: {content}\n"
            
            prompt += "Assistant:"
            
            # Add tool information if available
            if tools:
                tool_desc = "Available tools: " + ", ".join(tools)
                prompt = prompt.replace("System:", f"System: {tool_desc}\n")
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 2048
                }
            }
            
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                f"{self.server_url}/api/generate",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            response = urllib.request.urlopen(req, timeout=self.timeout)
            result = json.loads(response.read().decode('utf-8'))
            response_text = result.get("response", "")
            
            # Check if response contains tool calls (JSON format)
            if tools and "{" in response_text and "}" in response_text:
                try:
                    # Try to extract JSON tool call
                    start = response_text.find("{")
                    end = response_text.rfind("}") + 1
                    json_str = response_text[start:end]
                    tool_call = json.loads(json_str)
                    
                    if "name" in tool_call or "tool" in tool_call:
                        return [{
                            "type": "tool_use",
                            "name": tool_call.get("name", tool_call.get("tool")),
                            "input": tool_call.get("input", tool_call.get("args", {}))
                        }]
                except:
                    pass
            
            return [{"type": "text", "text": response_text}]
            
        except Exception as e:
            return [{"type": "text", "text": f"Error: {str(e)}"}]

class AnthropicAdapter(BaseAdapter):
    def __init__(self):
        self.key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.url = "https://api.anthropic.com/v1/messages"
        self.model = os.environ.get("MODEL","claude-3-opus-20240229")

    def call(self, system, messages, tools):
        if not self.key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "system": system,
            "messages": messages,
            "tools": tools
        }
        req = urllib.request.Request(
            self.url,
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type":"application/json",
                "anthropic-version":"2023-06-01",
                "x-api-key": self.key
            }
        )
        r = json.loads(urllib.request.urlopen(req).read())
        return r["content"]

class MockAdapter(BaseAdapter):
    """Mock adapter for testing without API keys"""
    def __init__(self):
        self.call_count = 0
        
    def call(self, system, messages, tools):
        self.call_count += 1
        user_msg = messages[-1]["content"] if messages else ""
        
        print(f"\n[MOCK LLM CALL #{self.call_count}]")
        print(f"System: {system}")
        print(f"User: {user_msg}")
        print(f"Available tools: {tools}")
        print()
        
        # Simulate different agent responses based on system prompt
        if "decompose tasks" in system.lower():
            # Planner agent
            response = input("Enter plan (or press Enter for default): ").strip()
            if not response:
                response = "1. List files\n2. Read important files\n3. Summarize findings"
            return [{"type": "text", "text": response}]
        
        elif "execute plans" in system.lower():
            # Executor agent - return tool use blocks
            print("Enter tool calls (format: tool_name arg1=val1 arg2=val2)")
            print("Example: bash cmd='ls -la'")
            print("Type 'done' when finished:")
            tool_blocks = []
            while True:
                line = input("Tool: ").strip()
                if line.lower() == 'done':
                    break
                if not line:
                    # Default action
                    tool_blocks.append({
                        "type": "tool_use",
                        "name": "bash",
                        "input": {"cmd": "pwd"}
                    })
                    break
                # Parse simple format: tool_name arg=val
                parts = line.split(None, 1)
                if len(parts) >= 1:
                    tool_name = parts[0]
                    args = {}
                    if len(parts) > 1:
                        # Simple key=value parser
                        for pair in parts[1].split():
                            if '=' in pair:
                                k, v = pair.split('=', 1)
                                # Remove quotes
                                v = v.strip("'\"")
                                args[k] = v
                    tool_blocks.append({
                        "type": "tool_use",
                        "name": tool_name,
                        "input": args
                    })
            return tool_blocks if tool_blocks else [{"type": "text", "text": "No tools to execute"}]
        
        elif "summarize" in system.lower():
            # Memory agent
            response = input("Enter summary (or press Enter for default): ").strip()
            if not response:
                response = "Completed task successfully"
            return [{"type": "text", "text": response}]
        
        else:
            # Generic response
            response = input("Enter response: ").strip()
            return [{"type": "text", "text": response or "OK"}]
