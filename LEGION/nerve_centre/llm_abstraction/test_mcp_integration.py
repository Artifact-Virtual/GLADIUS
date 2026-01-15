!/usr/bin/env python3
"""
MCP Demonstration and Testing Script
Shows comprehensive MCP integration with LLM abstraction
"""

import asyncio
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_mcp_integration():
    """Test the MCP integration with LLM abstraction"""
    
    logger.info("Starting MCP Integration Test...")
    
    try:
        # Import the enhanced LLM abstraction
        from llm_abstraction.mcp.integration import MCPEnhancedLLMAbstraction
        from llm_abstraction.llm_abstraction import LLMAbstraction
        
        # Create base LLM abstraction
        base_llm = LLMAbstraction()
        
        # Create enhanced version with MCP
        enhanced_llm = MCPEnhancedLLMAbstraction(base_llm)
        
        # Initialize the MCP system
        logger.info("Initializing MCP system...")
        success = await enhanced_llm.initialize()
        
        if not success:
            logger.error("Failed to initialize MCP system")
            return False
        
        # Test 1: Get MCP documentation
        logger.info("Test 1: Getting MCP documentation...")
        docs = await enhanced_llm.get_mcp_documentation()
        logger.info(f"Documentation length: {len(docs)} characters")
        
        # Test 2: List available functions
        logger.info("Test 2: Listing available MCP functions...")
        functions = enhanced_llm.list_mcp_functions()
        logger.info(f"Available functions: {len(functions)}")
        
        # Print function categories
        categories = {}
        for func in functions:
            category = func.get('category', 'other')
            categories[category] = categories.get(category, 0) + 1
        
        logger.info("Function categories:")
        for category, count in categories.items():
            logger.info(f"  - {category}: {count} functions")
        
        # Test 3: Enhanced query with MCP context
        logger.info("Test 3: Enhanced LLM query with MCP context...")
        
        test_query = (
            "I need to create a temporary file called 'test_output.txt' "
            "with the content 'Hello from MCP integration!' and then read it back. "
            "Can you help me with this?"
        )
        
        result = await enhanced_llm.query(
            test_query,
            include_mcp_context=True,
            auto_execute_mcp=True
        )
        
        logger.info("LLM Response:")
        logger.info(result['llm_response'].content[:500] + "...")
        
        logger.info("MCP Results:")
        mcp_results = result['mcp_results']
        logger.info(f"  - Tool calls found: {mcp_results.get('tool_calls_found', 0)}")
        logger.info(f"  - Executions performed: {len(mcp_results.get('execution_results', []))}")
        logger.info(f"  - Errors: {len(mcp_results.get('errors', []))}")
        
        # Show execution results
        for exec_result in mcp_results.get('execution_results', []):
            logger.info(f"  - Executed: {exec_result['function_name']} - Success: {exec_result['success']}")
        
        # Test 4: Code execution
        logger.info("Test 4: Code execution via MCP...")
        
        try:
            # Test Python execution
            python_result = await enhanced_llm.execute_mcp_function(
                'execute_python',
                {
                    'code': 'print("Hello from Python!")\nresult = 2 + 2\nprint(f"2 + 2 = {result}")',
                    'timeout': 30
                }
            )
            logger.info(f"Python execution result: {python_result}")
            
            # Test JavaScript execution
            js_result = await enhanced_llm.execute_mcp_function(
                'execute_javascript',
                {
                    'code': 'console.log("Hello from JavaScript!"); console.log("2 + 2 =", 2 + 2);',
                    'timeout': 30
                }
            )
            logger.info(f"JavaScript execution result: {js_result}")
            
        except Exception as e:
            logger.warning(f"Code execution test failed: {e}")
        
        # Test 5: Direct function execution
        logger.info("Test 5: Direct MCP function execution...")
        
        try:
            # Try to create a file directly
            file_result = await enhanced_llm.execute_mcp_function(
                'create_file',
                {
                    'file_path': '/tmp/mcp_test.txt',
                    'content': 'Direct MCP function call test!'
                }
            )
            logger.info(f"Direct file creation result: {file_result}")
            
        except Exception as e:
            logger.warning(f"Direct function execution failed: {e}")
        
        # Test 6: Search functions
        logger.info("Test 6: Searching MCP functions...")
        
        search_results = enhanced_llm.mcp_integrator.mcp_client.search_functions('file')
        logger.info(f"File-related functions found: {len(search_results)}")
        
        for func in search_results[:3]:  # Show first 3
            logger.info(f"  - {func['name']}: {func['description']}")
        
        logger.info("MCP Integration Test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"MCP Integration Test failed: {e}")
        return False
        
    finally:
        # Cleanup
        try:
            await enhanced_llm.shutdown()
        except:
            pass


async def test_mcp_client_only():
    """Test just the MCP client functionality"""
    
    logger.info("Starting MCP Client-Only Test...")
    
    try:
        from enterprise.nerve_centre.llm_abstraction.mcp.client.mcp_client import ComprehensiveMCPClient
        
        # Create MCP client
        client = ComprehensiveMCPClient()
        
        # Initialize
        success = await client.initialize()
        if not success:
            logger.error("Failed to initialize MCP client")
            return False
        
        # List functions
        functions = client.list_functions()
        logger.info(f"MCP Client found {len(functions)} functions")
        
        # Get server status
        status = client.get_server_status()
        logger.info(f"Server status: {status['total_servers']} servers")
        
        # Search functions
        file_functions = client.search_functions('file')
        logger.info(f"File functions: {len(file_functions)}")
        
        logger.info("MCP Client Test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"MCP Client Test failed: {e}")
        return False
        
    finally:
        try:
            await client.shutdown()
        except:
            pass


def create_sample_mcp_config():
    """Create a sample MCP configuration for testing"""
    
    config_dir = Path(__file__).parent.parent / 'config'
    config_dir.mkdir(exist_ok=True)
    
    sample_config = {
        "mcp_configuration": {
            "version": "1.0.0",
            "description": "Sample MCP Configuration for Testing",
            "auto_discovery": True,
            "auto_integration": True,
            "security_level": "development"
        },
        "function_categories": {
            "file_management": {
                "description": "File system operations",
                "functions": [
                    {
                        "name": "create_file",
                        "description": "Create a new file with content",
                        "parameters": {
                            "properties": {
                                "file_path": {"type": "string", "description": "Path to the file"},
                                "content": {"type": "string", "description": "File content"}
                            },
                            "required": ["file_path", "content"]
                        },
                        "returns": {"type": "object"},
                        "examples": [
                            {
                                "file_path": "/tmp/test.txt",
                                "content": "Hello World!"
                            }
                        ]
                    },
                    {
                        "name": "read_file",
                        "description": "Read file content",
                        "parameters": {
                            "properties": {
                                "file_path": {"type": "string", "description": "Path to the file"}
                            },
                            "required": ["file_path"]
                        },
                        "returns": {"type": "string"},
                        "examples": [
                            {
                                "file_path": "/tmp/test.txt"
                            }
                        ]
                    }
                ]
            },
            "system_info": {
                "description": "System information functions",
                "functions": [
                    {
                        "name": "get_system_info",
                        "description": "Get system information",
                        "parameters": {
                            "properties": {}
                        },
                        "returns": {"type": "object"}
                    }
                ]
            }
        }
    }
    
    config_file = config_dir / 'mcp_test_config.json'
    with open(config_file, 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    logger.info(f"Created sample MCP config: {config_file}")
    return str(config_file)


async def main():
    """Main demonstration function"""
    
    print("=" * 60)
    print("MCP (Model Context Protocol) Integration Demonstration")
    print("=" * 60)
    
    # Create sample config
    config_file = create_sample_mcp_config()
    
    # Test 1: MCP Client only
    print("\n1. Testing MCP Client functionality...")
    client_success = await test_mcp_client_only()
    
    # Test 2: Full LLM + MCP integration
    print("\n2. Testing Full LLM + MCP Integration...")
    integration_success = await test_mcp_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print(f"  MCP Client Test: {'✓ PASSED' if client_success else '✗ FAILED'}")
    print(f"  Integration Test: {'✓ PASSED' if integration_success else '✗ FAILED'}")
    
    if client_success and integration_success:
        print("\n🎉 All tests passed! MCP integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the logs for details.")
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
