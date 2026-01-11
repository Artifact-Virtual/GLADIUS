"""
Tool Registry - Function calling system for AI.

Allows AI to call tools and perform tasks autonomously.
"""

import logging
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
import inspect
import json
import asyncio


@dataclass
class Tool:
    """Tool definition."""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Callable
    is_async: bool


class ToolRegistry:
    """
    Registry for tools that AI can call.
    
    Features:
    - Register Python functions as tools
    - Automatic parameter schema generation
    - Safe execution with error handling
    - Async and sync function support
    """
    
    def __init__(self):
        """Initialize tool registry."""
        self.tools: Dict[str, Tool] = {}
        self.logger = logging.getLogger(__name__)
        
        # Register built-in tools
        self._register_builtin_tools()
    
    def register(
        self,
        name: str,
        function: Callable,
        description: str,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Register a tool.
        
        Args:
            name: Tool name
            function: Function to execute
            description: Tool description
            parameters: Parameter schema (auto-generated if not provided)
        """
        # Auto-generate parameter schema if not provided
        if parameters is None:
            parameters = self._generate_parameter_schema(function)
        
        # Check if function is async
        is_async = asyncio.iscoroutinefunction(function)
        
        tool = Tool(
            name=name,
            description=description,
            parameters=parameters,
            function=function,
            is_async=is_async
        )
        
        self.tools[name] = tool
        self.logger.info(f"Registered tool: {name}")
    
    def _generate_parameter_schema(self, function: Callable) -> Dict[str, Any]:
        """Generate JSON schema from function signature."""
        sig = inspect.signature(function)
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            # Determine type
            param_type = "string"  # default
            if param.annotation != inspect.Parameter.empty:
                type_name = param.annotation.__name__ if hasattr(param.annotation, '__name__') else str(param.annotation)
                
                type_mapping = {
                    'int': 'integer',
                    'float': 'number',
                    'bool': 'boolean',
                    'str': 'string',
                    'list': 'array',
                    'dict': 'object'
                }
                param_type = type_mapping.get(type_name, 'string')
            
            properties[param_name] = {
                'type': param_type,
                'description': f"Parameter {param_name}"
            }
            
            # Check if required
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        return {
            'type': 'object',
            'properties': properties,
            'required': required
        }
    
    async def execute(self, name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a tool.
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if name not in self.tools:
            raise ValueError(f"Tool not found: {name}")
        
        tool = self.tools[name]
        
        self.logger.info(f"Executing tool: {name} with args: {arguments}")
        
        try:
            if tool.is_async:
                result = await tool.function(**arguments)
            else:
                result = tool.function(**arguments)
            
            self.logger.info(f"Tool {name} executed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Tool {name} execution failed: {e}")
            raise
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Get OpenAI-compatible tool schemas.
        
        Returns:
            List of tool schemas for AI function calling
        """
        schemas = []
        
        for tool in self.tools.values():
            schemas.append({
                'type': 'function',
                'function': {
                    'name': tool.name,
                    'description': tool.description,
                    'parameters': tool.parameters
                }
            })
        
        return schemas
    
    def get_anthropic_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Get Anthropic-compatible tool schemas.
        
        Returns:
            List of tool schemas for Claude function calling
        """
        schemas = []
        
        for tool in self.tools.values():
            schemas.append({
                'name': tool.name,
                'description': tool.description,
                'input_schema': tool.parameters
            })
        
        return schemas
    
    def list_tools(self) -> List[str]:
        """Get list of registered tool names."""
        return list(self.tools.keys())
    
    def _register_builtin_tools(self):
        """Register built-in tools."""
        
        # Get current time
        def get_current_time() -> str:
            """Get current date and time."""
            from datetime import datetime, timezone
            return datetime.now(timezone.utc).isoformat()
        
        self.register(
            name="get_current_time",
            function=get_current_time,
            description="Get the current date and time in ISO format"
        )
        
        # Calculate
        def calculate(expression: str) -> float:
            """
            Safely evaluate a mathematical expression.
            
            Args:
                expression: Mathematical expression to evaluate
                
            Returns:
                Result of the calculation
            """
            import ast
            import operator
            
            # Safe operators
            ops = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.USub: operator.neg,
            }
            
            def eval_expr(node):
                if isinstance(node, ast.Num):
                    return node.n
                elif isinstance(node, ast.BinOp):
                    return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
                elif isinstance(node, ast.UnaryOp):
                    return ops[type(node.op)](eval_expr(node.operand))
                else:
                    raise ValueError(f"Unsupported expression: {ast.dump(node)}")
            
            return eval_expr(ast.parse(expression, mode='eval').body)
        
        self.register(
            name="calculate",
            function=calculate,
            description="Safely evaluate a mathematical expression",
            parameters={
                'type': 'object',
                'properties': {
                    'expression': {
                        'type': 'string',
                        'description': 'Mathematical expression to evaluate (e.g., "2 + 2", "10 * 5 + 3")'
                    }
                },
                'required': ['expression']
            }
        )
        
        # Search context
        def search_context(query: str) -> str:
            """
            Search for information in context memory.
            
            Args:
                query: Search query
                
            Returns:
                Search results
            """
            # This will be connected to context engine
            return f"Search results for: {query}\n(Context search not yet connected)"
        
        self.register(
            name="search_context",
            function=search_context,
            description="Search for information in the AI's context memory",
            parameters={
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'Search query to find relevant information'
                    }
                },
                'required': ['query']
            }
        )
        
        # Store note
        def store_note(title: str, content: str) -> str:
            """
            Store a note for future reference.
            
            Args:
                title: Note title
                content: Note content
                
            Returns:
                Confirmation message
            """
            # This will be connected to context engine
            return f"Note '{title}' stored successfully"
        
        self.register(
            name="store_note",
            function=store_note,
            description="Store a note or important information for future reference",
            parameters={
                'type': 'object',
                'properties': {
                    'title': {
                        'type': 'string',
                        'description': 'Title of the note'
                    },
                    'content': {
                        'type': 'string',
                        'description': 'Content of the note'
                    }
                },
                'required': ['title', 'content']
            }
        )


class ToolExecutor:
    """
    Executes tool calls from AI responses.
    
    Integrates with AI providers and tool registry to enable function calling.
    """
    
    def __init__(self, tool_registry: ToolRegistry, ai_provider):
        """
        Initialize tool executor.
        
        Args:
            tool_registry: Tool registry
            ai_provider: AI provider
        """
        self.registry = tool_registry
        self.ai_provider = ai_provider
        self.logger = logging.getLogger(__name__)
    
    async def execute_with_tools(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Execute AI request with tool calling support.
        
        Args:
            prompt: User prompt
            system_message: System message
            max_iterations: Maximum tool calling iterations
            
        Returns:
            Final AI response with tool results
        """
        messages = []
        
        if system_message:
            messages.append({'role': 'system', 'content': system_message})
        
        messages.append({'role': 'user', 'content': prompt})
        
        # Get tool schemas
        tools = self.registry.get_tool_schemas()
        
        for iteration in range(max_iterations):
            # Generate AI response
            response = await self.ai_provider.generate(
                prompt=messages[-1]['content'],
                system_message=system_message,
                tools=tools
            )
            
            # Check if AI wants to call tools
            if 'tool_calls' not in response:
                # No tool calls, return final response
                return {
                    'content': response['content'],
                    'tool_calls_made': iteration,
                    'success': True
                }
            
            # Execute tool calls
            tool_results = []
            
            for tool_call in response['tool_calls']:
                tool_name = tool_call['function']['name']
                tool_args = tool_call['function']['arguments']
                
                try:
                    result = await self.registry.execute(tool_name, tool_args)
                    tool_results.append({
                        'tool': tool_name,
                        'result': result,
                        'success': True
                    })
                except Exception as e:
                    tool_results.append({
                        'tool': tool_name,
                        'error': str(e),
                        'success': False
                    })
            
            # Add tool results to conversation
            tool_results_text = "\n\n".join([
                f"Tool: {tr['tool']}\nResult: {tr.get('result', tr.get('error'))}"
                for tr in tool_results
            ])
            
            messages.append({
                'role': 'assistant',
                'content': f"I used these tools:\n{tool_results_text}"
            })
            
            # Continue conversation with tool results
            messages.append({
                'role': 'user',
                'content': f"Here are the tool results. Please continue:\n{tool_results_text}"
            })
        
        # Max iterations reached
        return {
            'content': "Maximum tool calling iterations reached",
            'tool_calls_made': max_iterations,
            'success': False
        }
