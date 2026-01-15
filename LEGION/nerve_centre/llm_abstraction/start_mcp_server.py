#!/usr/bin/env python3
"""
MCP Server Startup Script
Starts the comprehensive MCP server with all enterprise functions
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPServerManager:
    """Manager for MCP server lifecycle"""
    
    def __init__(self):
        self.server = None
        self.running = False
        self.config_path = None
        
    async def start_server(self, config_path: str = None, port: int = 9000):
        """Start the MCP server"""
        try:
            from llm_abstraction.mcp.server.comprehensive_server import ComprehensiveMCPServer
            
            self.config_path = config_path or self._get_default_config_path()
            
            logger.info(f"Starting MCP Server on port {port}...")
            logger.info(f"Using configuration: {self.config_path}")
            
            # Create and configure server
            self.server = ComprehensiveMCPServer(self.config_path)
            
            # Initialize server
            await self.server.initialize()
            
            # Start server
            await self.server.start(port=port)
            
            self.running = True
            logger.info(f"MCP Server started successfully on port {port}")
            
            return True
            
        except ImportError as e:
            logger.error(f"MCP server components not available: {e}")
            logger.error("Install required dependencies: pip install model-context-protocol")
            return False
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            return False
    
    async def stop_server(self):
        """Stop the MCP server"""
        if self.server and self.running:
            logger.info("Stopping MCP Server...")
            try:
                await self.server.stop()
                self.running = False
                logger.info("MCP Server stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping MCP server: {e}")
    
    def _get_default_config_path(self) -> str:
        """Get default configuration path"""
        config_path = Path(__file__).parent.parent.parent / 'config' / 'mcp_functions.json'
        return str(config_path)
    
    async def health_check(self):
        """Perform server health check"""
        if not self.server or not self.running:
            return False
        
        try:
            # Perform basic health check
            return await self.server.health_check()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# Global server manager
server_manager = MCPServerManager()


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    asyncio.create_task(server_manager.stop_server())


async def run_server_daemon(config_path: str = None, port: int = 9000):
    """Run the MCP server as a daemon"""
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start server
    success = await server_manager.start_server(config_path, port)
    
    if not success:
        logger.error("Failed to start MCP server")
        return False
    
    # Keep server running
    try:
        while server_manager.running:
            # Perform periodic health checks
            healthy = await server_manager.health_check()
            if not healthy:
                logger.warning("Server health check failed")
            
            await asyncio.sleep(30)  # Health check every 30 seconds
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        await server_manager.stop_server()
    
    return True


async def test_server_functionality():
    """Test server functionality before starting daemon"""
    
    logger.info("Testing MCP Server functionality...")
    
    try:
        # Start server in test mode
        success = await server_manager.start_server(port=9999)  # Use different port for testing
        
        if not success:
            return False
        
        # Test basic functionality
        health = await server_manager.health_check()
        logger.info(f"Health check: {'✓ PASSED' if health else '✗ FAILED'}")
        
        # Stop test server
        await server_manager.stop_server()
        
        logger.info("Server functionality test completed")
        return health
        
    except Exception as e:
        logger.error(f"Server test failed: {e}")
        return False


def create_mcp_server_config():
    """Create MCP server configuration if it doesn't exist"""
    
    config_dir = Path(__file__).parent.parent.parent / 'config'
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / 'mcp_server_config.json'
    
    if config_file.exists():
        logger.info(f"Using existing server config: {config_file}")
        return str(config_file)
    
    # Create default server configuration
    server_config = {
        "server": {
            "name": "comprehensive_mcp_server",
            "version": "1.0.0",
            "description": "Comprehensive Enterprise MCP Server",
            "host": "localhost",
            "port": 9000,
            "protocol": "sse",
            "cors_enabled": True,
            "debug": False
        },
        "functions": {
            "auto_register": True,
            "categories_enabled": [
                "file_management",
                "code_execution",
                "web_operations", 
                "system_control",
                "database_operations",
                "memory_management",
                "ai_operations",
                "communication"
            ]
        },
        "security": {
            "authentication_required": False,
            "rate_limiting": {
                "enabled": True,
                "requests_per_minute": 100
            },
            "allowed_origins": ["*"],
            "ssl_enabled": False
        },
        "logging": {
            "level": "INFO",
            "file": "mcp_server.log",
            "max_size": "10MB",
            "backup_count": 5
        },
        "monitoring": {
            "health_checks": True,
            "metrics_collection": True,
            "performance_monitoring": True
        }
    }
    
    with open(config_file, 'w') as f:
        import json
        json.dump(server_config, f, indent=2)
    
    logger.info(f"Created MCP server config: {config_file}")
    return str(config_file)


async def main():
    """Main startup function"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='MCP Server Startup')
    parser.add_argument('--config', type=str, help='Configuration file path')
    parser.add_argument('--port', type=int, default=9000, help='Server port')
    parser.add_argument('--test', action='store_true', help='Test functionality only')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("MCP (Model Context Protocol) Server")
    print("Enterprise-Grade Function Server")
    print("=" * 60)
    
    # Create config if needed
    config_path = args.config or create_mcp_server_config()
    
    if args.test:
        # Test mode
        logger.info("Running in test mode...")
        success = await test_server_functionality()
        
        if success:
            print("\n✓ Server test passed! Ready for production.")
            return 0
        else:
            print("\n✗ Server test failed! Check logs for details.")
            return 1
    
    elif args.daemon:
        # Daemon mode
        logger.info("Starting MCP Server daemon...")
        success = await run_server_daemon(config_path, args.port)
        
        return 0 if success else 1
    
    else:
        # Interactive mode
        print(f"\nStarting MCP Server on port {args.port}...")
        print(f"Configuration: {config_path}")
        print("\nPress Ctrl+C to stop the server")
        
        success = await run_server_daemon(config_path, args.port)
        return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Server startup interrupted")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        sys.exit(1)
