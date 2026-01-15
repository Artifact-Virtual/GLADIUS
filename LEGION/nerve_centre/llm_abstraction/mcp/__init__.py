#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Module
Comprehensive MCP implementation for the LLM Abstraction subsystem
"""

from .client.mcp_client import (
    ComprehensiveMCPClient,
    MCPClientContext,
    MCPServerRegistry,
    MCPAutoDiscovery,
    MCPSessionManager,
    MCPFunctionExecutor,
    create_mcp_client
)

from .integration import (
    MCPLLMIntegrator,
    MCPEnhancedLLMAbstraction,
    MCPToolCall,
    MCPContext
)

from .executors.code_executor_bridge import (
    CodeExecutorBridge,
    MCPCodeExecutorFunctions,
    ExecutionRequest,
    ExecutionResult,
    create_code_executor_bridge
)

# Try to import server components (may not be available if deps missing)
try:
    from .server.mcp_server import ComprehensiveMCPServer
    server_available = True
except ImportError:
    server_available = False
    ComprehensiveMCPServer = None

__all__ = [
    # Client components
    'ComprehensiveMCPClient',
    'MCPClientContext',
    'MCPServerRegistry',
    'MCPAutoDiscovery',
    'MCPSessionManager',
    'MCPFunctionExecutor',
    'create_mcp_client',
    
    # Integration components
    'MCPLLMIntegrator',
    'MCPEnhancedLLMAbstraction',
    'MCPToolCall',
    'MCPContext',
    
    # Code executor components
    'CodeExecutorBridge',
    'MCPCodeExecutorFunctions',
    'ExecutionRequest',
    'ExecutionResult',
    'create_code_executor_bridge',
    
    # Server components (if available)
    'ComprehensiveMCPServer',
    
    # Utility
    'is_server_available'
]


def is_server_available() -> bool:
    """Check if MCP server components are available"""
    return server_available


# Version info
__version__ = "1.0.0"
__author__ = "Enterprise LLM Abstraction Team"
__description__ = "Comprehensive Model Context Protocol implementation"
