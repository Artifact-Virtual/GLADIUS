#!/usr/bin/env python3
"""
Code Executor Bridge for MCP Integration
Bridges the matrix executor_manager with MCP protocol
"""

import asyncio
import logging
import time
import tempfile
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ExecutionRequest:
    """Code execution request"""
    language: str
    code: str
    timeout: int = 30
    memory_limit: str = "512mb"
    environment: Optional[Dict[str, str]] = None
    files: Optional[Dict[str, str]] = None  # filename -> content


@dataclass
class ExecutionResult:
    """Code execution result"""
    success: bool
    output: str
    error: Optional[str] = None
    execution_time: Optional[float] = None
    memory_used: Optional[str] = None
    exit_code: Optional[int] = None


class CodeExecutorBridge:
    """Bridge between MCP and matrix executor_manager"""
    
    def __init__(self, executor_manager_url: str = "http://localhost:8000"):
        self.executor_url = executor_manager_url
        self.session = None
        self.supported_languages = ["python", "javascript", "nodejs"]
        
    async def initialize(self):
        """Initialize the executor bridge"""
        try:
            import aiohttp
            self.session = aiohttp.ClientSession()
            
            # Test connection to executor manager
            await self._test_connection()
            logger.info("Code Executor Bridge initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Code Executor Bridge: {e}")
            return False
    
    async def _test_connection(self):
        """Test connection to executor manager"""
        try:
            health_url = f"{self.executor_url}/health"
            async with self.session.get(health_url) as response:
                if response.status == 200:
                    logger.info("Connection to executor manager verified")
                else:
                    msg = f"Executor manager returned status {response.status}"
                    raise ConnectionError(msg)
        except Exception as e:
            logger.warning(f"Could not connect to executor manager: {e}")
            # Don't fail initialization - we'll fall back to local execution
    
    async def execute_code(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute code using the matrix executor manager"""
        start_time = time.time()
        
        try:
            # Try executor manager first
            if self.session:
                result = await self._execute_via_manager(request)
                if result:
                    result.execution_time = time.time() - start_time
                    return result
            
            # Fallback to local execution
            logger.info("Falling back to local code execution")
            result = await self._execute_locally(request)
            result.execution_time = time.time() - start_time
            return result
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Execution failed: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    async def _execute_via_manager(
        self, request: ExecutionRequest
    ) -> Optional[ExecutionResult]:
        """Execute code via the matrix executor manager"""
        try:
            payload = {
                "language": request.language,
                "code": request.code,
                "timeout": request.timeout,
                "memory_limit": request.memory_limit
            }
            
            if request.environment:
                payload["environment"] = request.environment
            
            if request.files:
                payload["files"] = request.files
            
            async with self.session.post(
                f"{self.executor_url}/execute",
                json=payload,
                timeout=request.timeout + 10
            ) as response:
                
                if response.status == 200:
                    result_data = await response.json()
                    return ExecutionResult(
                        success=result_data.get("success", False),
                        output=result_data.get("output", ""),
                        error=result_data.get("error"),
                        memory_used=result_data.get("memory_used"),
                        exit_code=result_data.get("exit_code")
                    )
                else:
                    error_text = await response.text()
                    error_msg = (
                        f"Executor manager error: "
                        f"{response.status} - {error_text}"
                    )
                    logger.error(error_msg)
                    return None
                    
        except asyncio.TimeoutError:
            logger.error("Execution timeout via manager")
            return None
        except Exception as e:
            logger.error(f"Error executing via manager: {e}")
            return None
    
    async def _execute_locally(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute code locally as fallback"""
        if request.language.lower() in ["python", "python3"]:
            return await self._execute_python_locally(request)
        elif request.language.lower() in ["javascript", "nodejs", "node"]:
            return await self._execute_nodejs_locally(request)
        else:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Language {request.language} not supported for local execution"
            )
    
    async def _execute_python_locally(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute Python code locally"""
        try:
            import tempfile
            import subprocess
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(request.code)
                temp_file = f.name
            
            try:
                # Execute with timeout
                process = await asyncio.create_subprocess_exec(
                    'python3', temp_file,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=request.environment
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=request.timeout
                )
                
                return ExecutionResult(
                    success=process.returncode == 0,
                    output=stdout.decode('utf-8'),
                    error=stderr.decode('utf-8') if stderr else None,
                    exit_code=process.returncode
                )
                
            finally:
                # Clean up temp file
                Path(temp_file).unlink(missing_ok=True)
                
        except asyncio.TimeoutError:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Execution timed out after {request.timeout} seconds"
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Local Python execution failed: {str(e)}"
            )
    
    async def _execute_nodejs_locally(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute Node.js code locally"""
        try:
            import tempfile
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(request.code)
                temp_file = f.name
            
            try:
                # Execute with timeout
                process = await asyncio.create_subprocess_exec(
                    'node', temp_file,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=request.environment
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=request.timeout
                )
                
                return ExecutionResult(
                    success=process.returncode == 0,
                    output=stdout.decode('utf-8'),
                    error=stderr.decode('utf-8') if stderr else None,
                    exit_code=process.returncode
                )
                
            finally:
                # Clean up temp file
                Path(temp_file).unlink(missing_ok=True)
                
        except asyncio.TimeoutError:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Execution timed out after {request.timeout} seconds"
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Local Node.js execution failed: {str(e)}"
            )
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported programming languages"""
        return self.supported_languages.copy()
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            if self.session:
                async with self.session.get(f"{self.executor_url}/system-info") as response:
                    if response.status == 200:
                        return await response.json()
            
            # Fallback to local system info
            import platform
            import psutil
            
            return {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "executor_type": "local_fallback"
            }
            
        except Exception as e:
            return {
                "error": f"Could not get system info: {str(e)}",
                "executor_type": "error"
            }
    
    async def shutdown(self):
        """Shutdown the executor bridge"""
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("Code Executor Bridge shutdown completed")


class MCPCodeExecutorFunctions:
    """MCP functions for code execution"""
    
    def __init__(self, executor_bridge: CodeExecutorBridge):
        self.executor = executor_bridge
    
    def get_function_definitions(self) -> List[Dict[str, Any]]:
        """Get MCP function definitions for code execution"""
        return [
            {
                "name": "execute_python",
                "description": "Execute Python code safely in a containerized environment",
                "category": "code_execution",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Python code to execute"
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Execution timeout in seconds",
                            "default": 30
                        },
                        "files": {
                            "type": "object",
                            "description": "Optional files to create before execution (filename -> content)",
                            "additionalProperties": {"type": "string"}
                        }
                    },
                    "required": ["code"]
                },
                "returns": {
                    "type": "object",
                    "description": "Execution result with output, errors, and metadata"
                },
                "examples": [
                    {
                        "code": "print('Hello, World!')\nprint(2 + 2)"
                    },
                    {
                        "code": "import numpy as np\nprint(np.array([1, 2, 3]).mean())",
                        "timeout": 60
                    }
                ]
            },
            {
                "name": "execute_javascript",
                "description": "Execute JavaScript/Node.js code safely in a containerized environment",
                "category": "code_execution",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "JavaScript/Node.js code to execute"
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Execution timeout in seconds",
                            "default": 30
                        },
                        "files": {
                            "type": "object",
                            "description": "Optional files to create before execution (filename -> content)",
                            "additionalProperties": {"type": "string"}
                        }
                    },
                    "required": ["code"]
                },
                "returns": {
                    "type": "object",
                    "description": "Execution result with output, errors, and metadata"
                },
                "examples": [
                    {
                        "code": "console.log('Hello, World!');\nconsole.log(2 + 2);"
                    },
                    {
                        "code": "const fs = require('fs');\nconsole.log(process.version);",
                        "timeout": 60
                    }
                ]
            },
            {
                "name": "get_executor_info",
                "description": "Get information about the code execution environment",
                "category": "system_info",
                "parameters": {
                    "type": "object",
                    "properties": {}
                },
                "returns": {
                    "type": "object",
                    "description": "System information and capabilities"
                },
                "examples": [{}]
            },
            {
                "name": "list_supported_languages",
                "description": "List all supported programming languages for execution",
                "category": "system_info",
                "parameters": {
                    "type": "object",
                    "properties": {}
                },
                "returns": {
                    "type": "array",
                    "description": "List of supported language names"
                },
                "examples": [{}]
            }
        ]
    
    async def execute_python(self, code: str, timeout: int = 30, files: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Execute Python code"""
        request = ExecutionRequest(
            language="python",
            code=code,
            timeout=timeout,
            files=files
        )
        
        result = await self.executor.execute_code(request)
        
        return {
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "execution_time": result.execution_time,
            "memory_used": result.memory_used,
            "exit_code": result.exit_code
        }
    
    async def execute_javascript(self, code: str, timeout: int = 30, files: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Execute JavaScript/Node.js code"""
        request = ExecutionRequest(
            language="javascript",
            code=code,
            timeout=timeout,
            files=files
        )
        
        result = await self.executor.execute_code(request)
        
        return {
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "execution_time": result.execution_time,
            "memory_used": result.memory_used,
            "exit_code": result.exit_code
        }
    
    async def get_executor_info(self) -> Dict[str, Any]:
        """Get executor system information"""
        return await self.executor.get_system_info()
    
    async def list_supported_languages(self) -> List[str]:
        """List supported programming languages"""
        return self.executor.get_supported_languages()


# Integration helper
async def create_code_executor_bridge(executor_url: str = "http://localhost:8000") -> CodeExecutorBridge:
    """Create and initialize a code executor bridge"""
    bridge = CodeExecutorBridge(executor_url)
    await bridge.initialize()
    return bridge
