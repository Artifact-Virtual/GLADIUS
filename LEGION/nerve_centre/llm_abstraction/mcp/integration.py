#!/usr/bin/env python3
"""
MCP Integration Layer for LLM Abstraction
Provides seamless integration between MCP functions and LLM queries
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

from .client.mcp_client import ComprehensiveMCPClient
from .executors.code_executor_bridge import (
    CodeExecutorBridge, 
    MCPCodeExecutorFunctions,
    create_code_executor_bridge
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MCPToolCall:
    """Represents an MCP tool call within LLM context"""
    function_name: str
    arguments: Dict[str, Any]
    call_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


@dataclass
class MCPContext:
    """MCP context for LLM queries"""
    available_functions: List[Dict[str, Any]]
    server_status: Dict[str, Any]
    recent_calls: List[MCPToolCall]
    capabilities: List[str]


class MCPLLMIntegrator:
    """Integrates MCP functionality with LLM queries"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.mcp_client: Optional[ComprehensiveMCPClient] = None
        self.call_history: List[MCPToolCall] = []
        self.function_cache: Dict[str, Dict[str, Any]] = {}
        self.auto_execution_enabled = True
        self.safe_functions: set[str] = set()  # Functions that can be auto-executed
        self._load_safe_functions()
        
        # Code executor integration
        self.code_executor: Optional[CodeExecutorBridge] = None
        self.executor_functions: Optional[MCPCodeExecutorFunctions] = None
        
    def _load_safe_functions(self):
        """Load list of functions that are safe for auto-execution"""
        safe_function_patterns = [
            'read_*', 'list_*', 'get_*', 'search_*', 'find_*',
            'analyze_*', 'calculate_*', 'convert_*', 'format_*',
            'validate_*', 'check_*', 'ping_*', 'status_*'
        ]
        
        # These will be populated when MCP client initializes
        # For now, we'll use pattern matching
        self.safe_function_patterns = safe_function_patterns
    
    async def initialize(self) -> bool:
        """Initialize the MCP integration"""
        try:
            self.mcp_client = ComprehensiveMCPClient(self.config_path)
            success = await self.mcp_client.initialize()
            
            if success:
                # Cache function information
                await self._cache_function_info()
                # Identify safe functions
                await self._identify_safe_functions()
                
                # Initialize code executor
                await self._initialize_code_executor()
                
                logger.info("MCP LLM Integration initialized successfully")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP LLM Integration: {e}")
            return False
    
    async def _cache_function_info(self):
        """Cache function information for quick access"""
        if not self.mcp_client:
            return
        
        functions = self.mcp_client.list_functions()
        for func in functions:
            self.function_cache[func['name']] = func
    
    async def _identify_safe_functions(self):
        """Identify functions that are safe for auto-execution"""
        if not self.mcp_client:
            return
        
        functions = self.mcp_client.list_functions()
        
        for func in functions:
            func_name = func['name']
            
            # Check if function matches safe patterns
            is_safe = any(
                self._matches_pattern(func_name, pattern)
                for pattern in self.safe_function_patterns
            )
            
            # Additional safety checks
            if is_safe:
                # Check if function has destructive parameters
                params = func.get('parameters', {}).get('properties', {})
                destructive_params = ['delete', 'remove', 'destroy', 'truncate', 'drop']
                
                if any(param in str(params).lower() for param in destructive_params):
                    is_safe = False
            
            if is_safe:
                self.safe_functions.add(func_name)
        
        logger.info(f"Identified {len(self.safe_functions)} safe functions for auto-execution")
    
    def _matches_pattern(self, function_name: str, pattern: str) -> bool:
        """Check if function name matches a pattern"""
        if '*' in pattern:
            prefix = pattern.replace('*', '')
            return function_name.startswith(prefix)
        return function_name == pattern
    
    async def get_mcp_context_for_llm(self) -> MCPContext:
        """Get MCP context to include in LLM queries"""
        if not self.mcp_client:
            return MCPContext([], {}, [], [])
        
        # Get available functions from MCP client
        functions = self.mcp_client.list_functions()
        
        # Add code executor functions if available
        if self.executor_functions:
            executor_funcs = self.executor_functions.get_function_definitions()
            functions.extend(executor_funcs)
        
        # Get server status
        server_status = self.mcp_client.get_server_status()
        
        # Get recent calls (last 10)
        recent_calls = self.call_history[-10:] if self.call_history else []
        
        # Get capabilities
        capabilities = self._extract_capabilities(functions)
        
        return MCPContext(
            available_functions=functions,
            server_status=server_status,
            recent_calls=recent_calls,
            capabilities=capabilities
        )
    
    def _extract_capabilities(self, functions: List[Dict[str, Any]]) -> List[str]:
        """Extract high-level capabilities from available functions"""
        capabilities = set()
        
        capability_mapping = {
            'file_management': ['file', 'directory', 'path', 'folder'],
            'code_execution': ['execute', 'run', 'compile', 'script'],
            'web_operations': ['web', 'http', 'url', 'browser', 'scrape'],
            'system_control': ['system', 'process', 'service', 'monitor'],
            'database': ['database', 'sql', 'query', 'table'],
            'memory_management': ['memory', 'cache', 'store', 'retrieve'],
            'ai_operations': ['ai', 'ml', 'model', 'predict', 'analyze'],
            'communication': ['email', 'message', 'notification', 'send']
        }
        
        for func in functions:
            func_name = func['name'].lower()
            func_desc = func.get('description', '').lower()
            
            for capability, keywords in capability_mapping.items():
                if any(keyword in func_name or keyword in func_desc for keyword in keywords):
                    capabilities.add(capability)
        
        return list(capabilities)
    
    async def process_llm_response_for_mcp_calls(
        self,
        llm_response: str,
        auto_execute: bool = True
    ) -> Dict[str, Any]:
        """Process LLM response to identify and execute MCP function calls"""
        
        tool_calls = self._extract_tool_calls_from_response(llm_response)
        
        results = {
            'tool_calls_found': len(tool_calls),
            'tool_calls': [],
            'execution_results': [],
            'errors': []
        }
        
        for tool_call in tool_calls:
            call_record = MCPToolCall(
                function_name=tool_call['function_name'],
                arguments=tool_call['arguments'],
                call_id=tool_call.get('call_id')
            )
            
            results['tool_calls'].append(asdict(call_record))
            
            # Execute if auto_execute is enabled and function is safe
            if auto_execute and self._is_safe_for_auto_execution(tool_call['function_name']):
                try:
                    start_time = time.time()
                    result = await self.execute_mcp_function(
                        tool_call['function_name'],
                        tool_call['arguments']
                    )
                    
                    call_record.result = result
                    call_record.execution_time = time.time() - start_time
                    
                    results['execution_results'].append({
                        'function_name': tool_call['function_name'],
                        'success': True,
                        'result': result,
                        'execution_time': call_record.execution_time
                    })
                    
                except Exception as e:
                    call_record.error = str(e)
                    results['errors'].append({
                        'function_name': tool_call['function_name'],
                        'error': str(e)
                    })
            
            # Add to call history
            self.call_history.append(call_record)
        
        # Keep call history manageable
        if len(self.call_history) > 100:
            self.call_history = self.call_history[-100:]
        
        return results
    
    def _extract_tool_calls_from_response(self, response: str) -> List[Dict[str, Any]]:
        """Extract tool calls from LLM response"""
        tool_calls = []
        
        # Look for function call patterns in the response
        # This is a simplified implementation - in practice, you'd want more sophisticated parsing
        
        # Pattern 1: JSON-like function calls
        import re
        
        # Look for patterns like: call_function("function_name", {"arg1": "value1"})
        pattern1 = r'call_function\s*\(\s*["\']([^"\']+)["\']\s*,\s*(\{[^}]+\})\s*\)'
        matches1 = re.findall(pattern1, response)
        
        for match in matches1:
            try:
                function_name = match[0]
                arguments = json.loads(match[1])
                tool_calls.append({
                    'function_name': function_name,
                    'arguments': arguments
                })
            except json.JSONDecodeError:
                continue
        
        # Pattern 2: More natural language patterns
        # "I'll use the read_file function with path '/tmp/test.txt'"
        pattern2 = r'(?:use|call|execute)\s+(?:the\s+)?(\w+)\s+(?:function\s+)?with\s+([^.]+)'
        matches2 = re.findall(pattern2, response, re.IGNORECASE)
        
        for match in matches2:
            function_name = match[0]
            if function_name in self.function_cache:
                # Try to extract arguments from the text
                args_text = match[1].strip()
                arguments = self._parse_arguments_from_text(args_text, function_name)
                
                if arguments:
                    tool_calls.append({
                        'function_name': function_name,
                        'arguments': arguments
                    })
        
        return tool_calls
    
    def _parse_arguments_from_text(self, args_text: str, function_name: str) -> Dict[str, Any]:
        """Parse arguments from natural language text"""
        arguments = {}
        
        # Get function parameter info
        func_info = self.function_cache.get(function_name, {})
        params = func_info.get('parameters', {}).get('properties', {})
        
        # Simple parsing for common patterns
        # This is a basic implementation - could be much more sophisticated
        
        for param_name, param_info in params.items():
            param_type = param_info.get('type', 'string')
            
            # Look for parameter values in the text
            patterns = [
                rf'{param_name}[:\s=]+["\']([^"\']+)["\']',  # param: "value"
                rf'{param_name}[:\s=]+([^\s,]+)',  # param: value
                rf'["\']([^"\']+)["\']',  # Just quoted values
            ]
            
            for pattern in patterns:
                import re
                match = re.search(pattern, args_text, re.IGNORECASE)
                if match:
                    value = match.group(1)
                    
                    # Type conversion
                    if param_type == 'integer':
                        try:
                            value = int(value)
                        except ValueError:
                            continue
                    elif param_type == 'number':
                        try:
                            value = float(value)
                        except ValueError:
                            continue
                    elif param_type == 'boolean':
                        value = value.lower() in ['true', 'yes', '1', 'on']
                    
                    arguments[param_name] = value
                    break
        
        return arguments
    
    def _is_safe_for_auto_execution(self, function_name: str) -> bool:
        """Check if a function is safe for automatic execution"""
        return function_name in self.safe_functions
    
    async def execute_mcp_function(
        self,
        function_name: str,
        arguments: Dict[str, Any],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Execute an MCP function"""
        # Check if it's a code executor function first
        if self.executor_functions and hasattr(self.executor_functions, function_name):
            method = getattr(self.executor_functions, function_name)
            return await method(**arguments)
        
        # Otherwise use regular MCP client
        if not self.mcp_client:
            raise RuntimeError("MCP client not initialized")
        
        return await self.mcp_client.call_function(function_name, arguments, **kwargs)
    
    def get_function_documentation(self, include_examples: bool = True) -> str:
        """Get formatted documentation for all available functions"""
        if not self.mcp_client:
            return "MCP client not initialized"
        
        functions = self.mcp_client.list_functions()
        
        doc_parts = ["# Available MCP Functions\n"]
        
        # Group by category
        categories = {}
        for func in functions:
            category = func.get('category', 'other')
            if category not in categories:
                categories[category] = []
            categories[category].append(func)
        
        for category, category_functions in categories.items():
            doc_parts.append(f"\n## {category.replace('_', ' ').title()}\n")
            
            for func in category_functions:
                doc_parts.append(f"### {func['name']}\n")
                doc_parts.append(f"{func['description']}\n")
                
                # Parameters
                params = func.get('parameters', {}).get('properties', {})
                if params:
                    doc_parts.append("**Parameters:**\n")
                    for param_name, param_info in params.items():
                        param_type = param_info.get('type', 'unknown')
                        param_desc = param_info.get('description', 'No description')
                        required = param_info.get('required', False)
                        req_str = " (required)" if required else ""
                        doc_parts.append(f"- `{param_name}` ({param_type}){req_str}: {param_desc}\n")
                
                # Return type
                returns = func.get('returns', {})
                if returns:
                    return_type = returns.get('type', 'unknown')
                    return_desc = returns.get('description', 'No description')
                    doc_parts.append(f"**Returns:** {return_type} - {return_desc}\n")
                
                # Examples
                if include_examples and func.get('examples'):
                    doc_parts.append("**Examples:**\n")
                    for example in func['examples']:
                        doc_parts.append(f"```\n{json.dumps(example, indent=2)}\n```\n")
                
                doc_parts.append("\n")
        
        return "".join(doc_parts)
    
    def format_mcp_context_for_prompt(self, context: MCPContext) -> str:
        """Format MCP context for inclusion in LLM prompts"""
        context_parts = []
        
        # Capabilities summary
        if context.capabilities:
            context_parts.append("Available MCP Capabilities:")
            for capability in context.capabilities:
                context_parts.append(f"- {capability.replace('_', ' ').title()}")
            context_parts.append("")
        
        # Function count by category
        categories = {}
        for func in context.available_functions:
            category = func.get('category', 'other')
            categories[category] = categories.get(category, 0) + 1
        
        if categories:
            context_parts.append("Available Functions by Category:")
            for category, count in categories.items():
                context_parts.append(f"- {category.replace('_', ' ').title()}: {count} functions")
            context_parts.append("")
        
        # Recent function calls
        if context.recent_calls:
            context_parts.append("Recent MCP Function Calls:")
            for call in context.recent_calls[-5:]:  # Last 5 calls
                status = "✓" if call.result else "✗" if call.error else "⏳"
                context_parts.append(f"- {status} {call.function_name}")
            context_parts.append("")
        
        # Server status
        server_stats = context.server_status.get('execution_stats', {})
        if server_stats:
            total_calls = server_stats.get('total_executions', 0)
            success_rate = server_stats.get('success_rate', 0)
            context_parts.append(f"MCP System Status: {total_calls} total calls, {success_rate:.1%} success rate")
            context_parts.append("")
        
        # Usage instructions
        context_parts.extend([
            "To use MCP functions, mention them in your response like:",
            '- "I\'ll use the read_file function with path \'/tmp/example.txt\'"',
            '- call_function("create_file", {"file_path": "/tmp/new.txt", "content": "Hello"})',
            ""
        ])
        
        return "\n".join(context_parts)
    
    async def shutdown(self):
        """Shutdown the MCP integration"""
        if self.code_executor:
            await self.code_executor.shutdown()
            self.code_executor = None
            self.executor_functions = None
            
        if self.mcp_client:
            await self.mcp_client.shutdown()
            self.mcp_client = None
        logger.info("MCP LLM Integration shutdown completed")
    
    async def _initialize_code_executor(self):
        """Initialize the code executor bridge"""
        try:
            self.code_executor = await create_code_executor_bridge()
            self.executor_functions = MCPCodeExecutorFunctions(self.code_executor)
            
            # Add code execution functions to safe functions
            executor_func_names = [
                'execute_python', 'execute_javascript',
                'get_executor_info', 'list_supported_languages'
            ]
            for func_name in executor_func_names:
                self.safe_functions.add(func_name)
            
            logger.info("Code executor bridge initialized successfully")
            
        except Exception as e:
            logger.warning(f"Could not initialize code executor: {e}")
            # Continue without code executor
            self.code_executor = None
            self.executor_functions = None


class MCPEnhancedLLMAbstraction:
    """Enhanced LLM Abstraction with integrated MCP support"""
    
    def __init__(self, llm_abstraction, mcp_config_path: Optional[str] = None):
        self.llm_abstraction = llm_abstraction
        self.mcp_integrator = MCPLLMIntegrator(mcp_config_path)
        self.mcp_enabled = True
        
    async def initialize(self) -> bool:
        """Initialize the enhanced LLM abstraction"""
        if self.mcp_enabled:
            return await self.mcp_integrator.initialize()
        return True
    
    async def query(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        include_mcp_context: bool = True,
        auto_execute_mcp: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Enhanced query method with MCP integration"""
        
        # Get MCP context if enabled
        mcp_context_str = ""
        if self.mcp_enabled and include_mcp_context:
            mcp_context = await self.mcp_integrator.get_mcp_context_for_llm()
            mcp_context_str = self.mcp_integrator.format_mcp_context_for_prompt(mcp_context)
        
        # Enhance prompt with MCP context
        enhanced_prompt = prompt
        if mcp_context_str:
            enhanced_prompt = f"{mcp_context_str}\n\nUser Query: {prompt}"
        
        # Execute LLM query
        llm_response = self.llm_abstraction.query(
            enhanced_prompt,
            context,
            **kwargs
        )
        
        # Process response for MCP calls
        mcp_results = {}
        if self.mcp_enabled:
            mcp_results = await self.mcp_integrator.process_llm_response_for_mcp_calls(
                llm_response.content,
                auto_execute_mcp
            )
        
        # Return enhanced response
        return {
            'llm_response': llm_response,
            'mcp_results': mcp_results,
            'mcp_context_included': include_mcp_context and bool(mcp_context_str),
            'auto_execution_performed': auto_execute_mcp and mcp_results.get('execution_results', [])
        }
    
    async def get_mcp_documentation(self) -> str:
        """Get comprehensive MCP documentation"""
        if not self.mcp_enabled:
            return "MCP is not enabled"
        
        return self.mcp_integrator.get_function_documentation()
    
    async def execute_mcp_function(
        self,
        function_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute an MCP function directly"""
        if not self.mcp_enabled:
            raise RuntimeError("MCP is not enabled")
        
        return await self.mcp_integrator.execute_mcp_function(function_name, arguments)
    
    def list_mcp_functions(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available MCP functions"""
        if not self.mcp_enabled or not self.mcp_integrator.mcp_client:
            return []
        
        return self.mcp_integrator.mcp_client.list_functions(category=category)
    
    async def shutdown(self):
        """Shutdown the enhanced LLM abstraction"""
        if self.mcp_enabled:
            await self.mcp_integrator.shutdown()


# Example usage
async def main():
    """Example usage of MCP Enhanced LLM Abstraction"""
    from llm_abstraction.llm_abstraction import LLMAbstraction
    
    # Create base LLM abstraction
    llm_abstraction = LLMAbstraction()
    
    # Create enhanced version with MCP
    enhanced_llm = MCPEnhancedLLMAbstraction(llm_abstraction)
    await enhanced_llm.initialize()
    
    try:
        # Example query that might trigger MCP function calls
        result = await enhanced_llm.query(
            "Please read the contents of the file '/tmp/example.txt' and analyze it",
            include_mcp_context=True,
            auto_execute_mcp=True
        )
        
        print("LLM Response:", result['llm_response'].content)
        print("MCP Results:", result['mcp_results'])
        
        # Get MCP documentation
        docs = await enhanced_llm.get_mcp_documentation()
        print("MCP Functions Documentation:", docs[:500] + "...")
        
    finally:
        await enhanced_llm.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
