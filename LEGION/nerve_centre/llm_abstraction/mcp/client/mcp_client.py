#!/usr/bin/env python3
"""
Comprehensive MCP Client Implementation
Enterprise-grade Model Context Protocol client with auto-discovery and intelligent integration
"""

import asyncio
import json
import logging
import time
import inspect
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
import aiohttp
import websockets

# MCP Protocol imports
try:
    from mcp.client.session import ClientSession
    from mcp.client.stdio import stdio_client
    from mcp.client.sse import sse_client
    from mcp.types import (
        Tool, Resource, CallToolRequest, CallToolResult,
        ListToolsRequest, ListToolsResult, ListResourcesRequest, ListResourcesResult
    )
except ImportError:
    print("MCP library not found. Install with: pip install model-context-protocol")


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MCPServerInfo:
    """Information about an MCP server"""
    name: str
    url: str
    protocol: str  # 'stdio', 'sse', 'websocket'
    capabilities: List[str]
    tools: List[str]
    resources: List[str]
    status: str = "discovered"
    last_ping: Optional[float] = None
    error_count: int = 0


@dataclass
class MCPFunction:
    """Standardized MCP function representation"""
    name: str
    description: str
    parameters: Dict[str, Any]
    returns: Dict[str, Any]
    server: str
    category: str
    examples: Optional[List[Dict[str, Any]]] = None


class MCPServerRegistry:
    """Registry for managing MCP servers and their capabilities"""
    
    def __init__(self):
        self.servers: Dict[str, MCPServerInfo] = {}
        self.functions: Dict[str, MCPFunction] = {}
        self.auto_discovery_active = False
        self.health_check_interval = 30  # seconds
        
    def register_server(self, server_info: MCPServerInfo) -> bool:
        """Register a new MCP server"""
        try:
            self.servers[server_info.name] = server_info
            logger.info(f"Registered MCP server: {server_info.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register server {server_info.name}: {e}")
            return False
    
    def unregister_server(self, server_name: str) -> bool:
        """Unregister an MCP server"""
        if server_name in self.servers:
            # Remove all functions from this server
            functions_to_remove = [
                func_name for func_name, func in self.functions.items()
                if func.server == server_name
            ]
            for func_name in functions_to_remove:
                del self.functions[func_name]
            
            del self.servers[server_name]
            logger.info(f"Unregistered MCP server: {server_name}")
            return True
        return False
    
    def register_function(self, function: MCPFunction) -> bool:
        """Register a function from an MCP server"""
        try:
            self.functions[function.name] = function
            logger.debug(f"Registered function: {function.name} from {function.server}")
            return True
        except Exception as e:
            logger.error(f"Failed to register function {function.name}: {e}")
            return False
    
    def get_server_info(self, server_name: str) -> Optional[MCPServerInfo]:
        """Get information about a specific server"""
        return self.servers.get(server_name)
    
    def get_function_info(self, function_name: str) -> Optional[MCPFunction]:
        """Get information about a specific function"""
        return self.functions.get(function_name)
    
    def list_servers(self) -> List[MCPServerInfo]:
        """List all registered servers"""
        return list(self.servers.values())
    
    def list_functions(self, category: Optional[str] = None, server: Optional[str] = None) -> List[MCPFunction]:
        """List functions with optional filtering"""
        functions = list(self.functions.values())
        
        if category:
            functions = [f for f in functions if f.category == category]
        
        if server:
            functions = [f for f in functions if f.server == server]
        
        return functions
    
    def search_functions(self, query: str) -> List[MCPFunction]:
        """Search functions by name or description"""
        query_lower = query.lower()
        return [
            func for func in self.functions.values()
            if query_lower in func.name.lower() or query_lower in func.description.lower()
        ]


class MCPAutoDiscovery:
    """Auto-discovery system for MCP servers"""
    
    def __init__(self, registry: MCPServerRegistry):
        self.registry = registry
        self.discovery_methods = [
            self._discover_local_servers,
            self._discover_network_servers,
            self._discover_config_servers
        ]
        
    async def discover_servers(self) -> List[MCPServerInfo]:
        """Discover MCP servers using all available methods"""
        discovered_servers = []
        
        for method in self.discovery_methods:
            try:
                servers = await method()
                discovered_servers.extend(servers)
                logger.info(f"Discovered {len(servers)} servers using {method.__name__}")
            except Exception as e:
                logger.warning(f"Discovery method {method.__name__} failed: {e}")
        
        # Remove duplicates
        unique_servers = {}
        for server in discovered_servers:
            if server.name not in unique_servers:
                unique_servers[server.name] = server
        
        return list(unique_servers.values())
    
    async def _discover_local_servers(self) -> List[MCPServerInfo]:
        """Discover locally running MCP servers"""
        servers = []
        
        # Common local MCP server ports
        common_ports = [9000, 9001, 9002, 8080, 8081, 3000, 4000, 5000]
        
        for port in common_ports:
            try:
                async with aiohttp.ClientSession() as session:
                    url = f"http://localhost:{port}/mcp"
                    async with session.get(url, timeout=2) as response:
                        if response.status == 200:
                            data = await response.json()
                            server_info = MCPServerInfo(
                                name=data.get('name', f'local-{port}'),
                                url=url,
                                protocol='sse',
                                capabilities=data.get('capabilities', []),
                                tools=data.get('tools', []),
                                resources=data.get('resources', [])
                            )
                            servers.append(server_info)
            except:
                continue  # Port not responsive
        
        return servers
    
    async def _discover_network_servers(self) -> List[MCPServerInfo]:
        """Discover MCP servers on the network"""
        servers = []
        
        # Network discovery would go here
        # This could include mDNS, service discovery, etc.
        
        return servers
    
    async def _discover_config_servers(self) -> List[MCPServerInfo]:
        """Discover MCP servers from configuration files"""
        servers = []
        
        # Look for MCP server configurations
        config_paths = [
            Path.home() / '.mcp' / 'servers.json',
            Path('/etc/mcp/servers.json'),
            Path(__file__).parent.parent.parent.parent / 'config' / 'mcp_servers.json'
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        
                    for server_config in config.get('servers', []):
                        server_info = MCPServerInfo(
                            name=server_config['name'],
                            url=server_config['url'],
                            protocol=server_config.get('protocol', 'sse'),
                            capabilities=server_config.get('capabilities', []),
                            tools=server_config.get('tools', []),
                            resources=server_config.get('resources', [])
                        )
                        servers.append(server_info)
                        
                except Exception as e:
                    logger.warning(f"Failed to load MCP config from {config_path}: {e}")
        
        return servers


class MCPSessionManager:
    """Manager for MCP client sessions"""
    
    def __init__(self, registry: MCPServerRegistry):
        self.registry = registry
        self.sessions: Dict[str, ClientSession] = {}
        self.connection_pools: Dict[str, Any] = {}
        
    async def get_session(self, server_name: str) -> Optional[ClientSession]:
        """Get or create a session for a server"""
        if server_name in self.sessions:
            return self.sessions[server_name]
        
        server_info = self.registry.get_server_info(server_name)
        if not server_info:
            logger.error(f"Server not found: {server_name}")
            return None
        
        try:
            session = await self._create_session(server_info)
            if session:
                self.sessions[server_name] = session
                return session
        except Exception as e:
            logger.error(f"Failed to create session for {server_name}: {e}")
            
        return None
    
    async def _create_session(self, server_info: MCPServerInfo) -> Optional[ClientSession]:
        """Create a new MCP session based on protocol"""
        try:
            if server_info.protocol == 'sse':
                streams = await sse_client(server_info.url)
                session = ClientSession(streams[0], streams[1])
                await session.initialize()
                return session
                
            elif server_info.protocol == 'stdio':
                # For stdio connections, we'd need to start the process
                # This is more complex and depends on the server implementation
                pass
                
            elif server_info.protocol == 'websocket':
                # WebSocket implementation would go here
                pass
                
        except Exception as e:
            logger.error(f"Failed to create {server_info.protocol} session: {e}")
            
        return None
    
    async def close_session(self, server_name: str) -> bool:
        """Close a session"""
        if server_name in self.sessions:
            try:
                session = self.sessions[server_name]
                await session.close()
                del self.sessions[server_name]
                return True
            except Exception as e:
                logger.error(f"Failed to close session for {server_name}: {e}")
        
        return False
    
    async def close_all_sessions(self):
        """Close all active sessions"""
        for server_name in list(self.sessions.keys()):
            await self.close_session(server_name)


class MCPFunctionExecutor:
    """Executor for MCP functions with intelligent routing and error handling"""
    
    def __init__(self, registry: MCPServerRegistry, session_manager: MCPSessionManager):
        self.registry = registry
        self.session_manager = session_manager
        self.execution_history: List[Dict[str, Any]] = []
        self.retry_strategies = {
            'immediate': self._immediate_retry,
            'exponential_backoff': self._exponential_backoff_retry,
            'circuit_breaker': self._circuit_breaker_retry
        }
        
    async def execute_function(
        self,
        function_name: str,
        arguments: Dict[str, Any],
        retry_strategy: str = 'exponential_backoff',
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Execute an MCP function with intelligent error handling"""
        
        function_info = self.registry.get_function_info(function_name)
        if not function_info:
            raise ValueError(f"Function not found: {function_name}")
        
        start_time = time.time()
        execution_record = {
            'function_name': function_name,
            'server': function_info.server,
            'start_time': start_time,
            'arguments': arguments,
            'attempts': 0,
            'success': False,
            'result': None,
            'error': None
        }
        
        try:
            # Validate arguments
            self._validate_arguments(function_info, arguments)
            
            # Execute with retry strategy
            result = await self.retry_strategies[retry_strategy](
                function_info, arguments, max_retries, execution_record
            )
            
            execution_record['success'] = True
            execution_record['result'] = result
            execution_record['execution_time'] = time.time() - start_time
            
            return result
            
        except Exception as e:
            execution_record['error'] = str(e)
            execution_record['execution_time'] = time.time() - start_time
            logger.error(f"Function execution failed: {function_name} - {e}")
            raise
            
        finally:
            self.execution_history.append(execution_record)
            # Keep only last 1000 executions
            if len(self.execution_history) > 1000:
                self.execution_history = self.execution_history[-1000:]
    
    async def _immediate_retry(
        self,
        function_info: MCPFunction,
        arguments: Dict[str, Any],
        max_retries: int,
        execution_record: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Immediate retry strategy"""
        for attempt in range(max_retries + 1):
            execution_record['attempts'] = attempt + 1
            try:
                return await self._execute_single_attempt(function_info, arguments)
            except Exception as e:
                if attempt == max_retries:
                    raise
                logger.warning(f"Attempt {attempt + 1} failed, retrying immediately: {e}")
    
    async def _exponential_backoff_retry(
        self,
        function_info: MCPFunction,
        arguments: Dict[str, Any],
        max_retries: int,
        execution_record: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Exponential backoff retry strategy"""
        for attempt in range(max_retries + 1):
            execution_record['attempts'] = attempt + 1
            try:
                return await self._execute_single_attempt(function_info, arguments)
            except Exception as e:
                if attempt == max_retries:
                    raise
                    
                wait_time = (2 ** attempt) * 0.5  # 0.5, 1, 2, 4 seconds
                logger.warning(f"Attempt {attempt + 1} failed, waiting {wait_time}s before retry: {e}")
                await asyncio.sleep(wait_time)
    
    async def _circuit_breaker_retry(
        self,
        function_info: MCPFunction,
        arguments: Dict[str, Any],
        max_retries: int,
        execution_record: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Circuit breaker retry strategy"""
        # Check if server is in circuit breaker state
        server_info = self.registry.get_server_info(function_info.server)
        if server_info and server_info.error_count > 10:
            raise Exception(f"Server {function_info.server} is in circuit breaker state")
        
        return await self._exponential_backoff_retry(
            function_info, arguments, max_retries, execution_record
        )
    
    async def _execute_single_attempt(
        self,
        function_info: MCPFunction,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single function call attempt"""
        session = await self.session_manager.get_session(function_info.server)
        if not session:
            raise Exception(f"Failed to get session for server: {function_info.server}")
        
        try:
            result = await session.call_tool(
                name=function_info.name,
                arguments=arguments
            )
            
            # Update server health
            server_info = self.registry.get_server_info(function_info.server)
            if server_info:
                server_info.error_count = max(0, server_info.error_count - 1)
                server_info.last_ping = time.time()
            
            return result.model_dump() if hasattr(result, 'model_dump') else result
            
        except Exception as e:
            # Update server error count
            server_info = self.registry.get_server_info(function_info.server)
            if server_info:
                server_info.error_count += 1
            raise
    
    def _validate_arguments(self, function_info: MCPFunction, arguments: Dict[str, Any]):
        """Validate function arguments against schema"""
        required_params = []
        param_schema = function_info.parameters
        
        # Extract required parameters
        if 'properties' in param_schema:
            for param_name, param_def in param_schema['properties'].items():
                if param_def.get('required', False) or param_name in param_schema.get('required', []):
                    required_params.append(param_name)
        
        # Check required parameters
        for param in required_params:
            if param not in arguments:
                raise ValueError(f"Missing required parameter: {param}")
        
        # Type validation could be added here
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        if not self.execution_history:
            return {"total_executions": 0}
        
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for ex in self.execution_history if ex['success'])
        
        function_stats = {}
        server_stats = {}
        
        for execution in self.execution_history:
            func_name = execution['function_name']
            server_name = execution['server']
            
            # Function stats
            if func_name not in function_stats:
                function_stats[func_name] = {'calls': 0, 'successes': 0, 'avg_time': 0}
            
            function_stats[func_name]['calls'] += 1
            if execution['success']:
                function_stats[func_name]['successes'] += 1
            
            if 'execution_time' in execution:
                current_avg = function_stats[func_name]['avg_time']
                new_time = execution['execution_time']
                calls = function_stats[func_name]['calls']
                function_stats[func_name]['avg_time'] = (current_avg * (calls - 1) + new_time) / calls
            
            # Server stats
            if server_name not in server_stats:
                server_stats[server_name] = {'calls': 0, 'successes': 0, 'avg_time': 0}
            
            server_stats[server_name]['calls'] += 1
            if execution['success']:
                server_stats[server_name]['successes'] += 1
            
            if 'execution_time' in execution:
                current_avg = server_stats[server_name]['avg_time']
                new_time = execution['execution_time']
                calls = server_stats[server_name]['calls']
                server_stats[server_name]['avg_time'] = (current_avg * (calls - 1) + new_time) / calls
        
        return {
            'total_executions': total_executions,
            'success_rate': successful_executions / total_executions,
            'function_stats': function_stats,
            'server_stats': server_stats
        }


class ComprehensiveMCPClient:
    """Comprehensive MCP client with auto-discovery, intelligent routing, and robust error handling"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
        
        # Core components
        self.registry = MCPServerRegistry()
        self.auto_discovery = MCPAutoDiscovery(self.registry)
        self.session_manager = MCPSessionManager(self.registry)
        self.function_executor = MCPFunctionExecutor(self.registry, self.session_manager)
        
        # State
        self.initialized = False
        self.background_tasks: List[asyncio.Task] = []
        
    def _get_default_config_path(self) -> str:
        """Get default configuration path"""
        return str(Path(__file__).parent.parent.parent.parent / 'config' / 'mcp_functions.json')
    
    def _load_config(self) -> Dict[str, Any]:
        """Load MCP configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {self.config_path}")
            return {}
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    async def initialize(self) -> bool:
        """Initialize the MCP client system"""
        try:
            logger.info("Initializing Comprehensive MCP Client...")
            
            # Auto-discover MCP servers
            if self.config.get('mcp_configuration', {}).get('auto_discovery', True):
                discovered_servers = await self.auto_discovery.discover_servers()
                for server in discovered_servers:
                    self.registry.register_server(server)
                logger.info(f"Auto-discovered {len(discovered_servers)} MCP servers")
            
            # Load functions from configuration
            await self._load_functions_from_config()
            
            # Start background tasks
            if self.config.get('mcp_configuration', {}).get('auto_integration', True):
                task = asyncio.create_task(self._background_server_integration())
                self.background_tasks.append(task)
            
            # Health monitoring
            task = asyncio.create_task(self._background_health_monitoring())
            self.background_tasks.append(task)
            
            self.initialized = True
            logger.info("MCP Client initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"MCP Client initialization failed: {e}")
            return False
    
    async def _load_functions_from_config(self):
        """Load function definitions from configuration"""
        function_categories = self.config.get('function_categories', {})
        
        for category_name, category_data in function_categories.items():
            functions = category_data.get('functions', [])
            
            for func_data in functions:
                function = MCPFunction(
                    name=func_data['name'],
                    description=func_data['description'],
                    parameters=func_data['parameters'],
                    returns=func_data['returns'],
                    server='local',  # Default to local server
                    category=category_name,
                    examples=func_data.get('examples', [])
                )
                self.registry.register_function(function)
        
        logger.info(f"Loaded {len(self.registry.functions)} functions from configuration")
    
    async def _background_server_integration(self):
        """Background task for continuous server integration"""
        while True:
            try:
                # Re-discover servers periodically
                new_servers = await self.auto_discovery.discover_servers()
                
                for server in new_servers:
                    if server.name not in self.registry.servers:
                        self.registry.register_server(server)
                        await self._integrate_server_functions(server)
                        logger.info(f"Integrated new server: {server.name}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Background server integration error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _integrate_server_functions(self, server_info: MCPServerInfo):
        """Integrate functions from a newly discovered server"""
        try:
            session = await self.session_manager.get_session(server_info.name)
            if session:
                # List available tools
                tools_result = await session.list_tools()
                
                for tool in tools_result.tools:
                    function = MCPFunction(
                        name=tool.name,
                        description=tool.description or "No description available",
                        parameters=tool.inputSchema.model_dump() if tool.inputSchema else {},
                        returns={'type': 'object'},  # Default return type
                        server=server_info.name,
                        category='auto_discovered'
                    )
                    self.registry.register_function(function)
                
                logger.info(f"Integrated {len(tools_result.tools)} functions from {server_info.name}")
                
        except Exception as e:
            logger.error(f"Failed to integrate functions from {server_info.name}: {e}")
    
    async def _background_health_monitoring(self):
        """Background task for server health monitoring"""
        while True:
            try:
                for server_info in self.registry.list_servers():
                    # Simple ping to check server health
                    try:
                        session = await self.session_manager.get_session(server_info.name)
                        if session:
                            # Try to list tools as a health check
                            await session.list_tools()
                            server_info.last_ping = time.time()
                            server_info.status = "healthy"
                        else:
                            server_info.status = "unreachable"
                    except Exception:
                        server_info.status = "error"
                        server_info.error_count += 1
                
                await asyncio.sleep(30)  # Health check every 30 seconds
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(60)
    
    # Public API methods
    
    async def call_function(
        self,
        function_name: str,
        arguments: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Call an MCP function"""
        if not self.initialized:
            raise RuntimeError("MCP Client not initialized")
        
        return await self.function_executor.execute_function(
            function_name, arguments, **kwargs
        )
    
    def list_functions(
        self,
        category: Optional[str] = None,
        server: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List available functions"""
        functions = self.registry.list_functions(category, server)
        return [asdict(func) for func in functions]
    
    def search_functions(self, query: str) -> List[Dict[str, Any]]:
        """Search functions by name or description"""
        functions = self.registry.search_functions(query)
        return [asdict(func) for func in functions]
    
    def get_function_info(self, function_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a function"""
        function = self.registry.get_function_info(function_name)
        return asdict(function) if function else None
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get status of all registered servers"""
        servers = self.registry.list_servers()
        return {
            'total_servers': len(servers),
            'servers': [asdict(server) for server in servers],
            'execution_stats': self.function_executor.get_execution_stats()
        }
    
    async def shutdown(self):
        """Shutdown the MCP client"""
        logger.info("Shutting down MCP Client...")
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Close all sessions
        await self.session_manager.close_all_sessions()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        self.initialized = False
        logger.info("MCP Client shutdown completed")


# Async context manager support
class MCPClientContext:
    """Async context manager for MCP client"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.client = ComprehensiveMCPClient(config_path)
    
    async def __aenter__(self):
        await self.client.initialize()
        return self.client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.shutdown()


# Convenience function
async def create_mcp_client(config_path: Optional[str] = None) -> ComprehensiveMCPClient:
    """Create and initialize an MCP client"""
    client = ComprehensiveMCPClient(config_path)
    await client.initialize()
    return client


# Example usage
async def main():
    """Example usage of the Comprehensive MCP Client"""
    async with MCPClientContext() as mcp_client:
        # List all available functions
        functions = mcp_client.list_functions()
        print(f"Available functions: {len(functions)}")
        
        # Search for file-related functions
        file_functions = mcp_client.search_functions("file")
        print(f"File functions: {len(file_functions)}")
        
        # Execute a function
        try:
            result = await mcp_client.call_function(
                "create_file",
                {
                    "file_path": "/tmp/test.txt",
                    "content": "Hello from MCP!"
                }
            )
            print(f"Function result: {result}")
        except Exception as e:
            print(f"Function execution failed: {e}")
        
        # Get server status
        status = mcp_client.get_server_status()
        print(f"Server status: {status}")


if __name__ == "__main__":
    asyncio.run(main())
