#!/usr/bin/env python3
"""
Comprehensive MCP Server Implementation
Enterprise-grade Model Context Protocol server with exhaustive tooling capabilities
"""

import asyncio
import json
import os
import sys
import subprocess
import logging
import sqlite3
import psutil
import hashlib
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
import tempfile
import shutil
import requests
from datetime import datetime, timedelta

# MCP Protocol imports
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Resource, Tool, TextContent, ImageContent, EmbeddedResource,
        CallToolRequest, CallToolResult, ListResourcesRequest, ListResourcesResult,
        ListToolsRequest, ListToolsResult, ReadResourceRequest, ReadResourceResult
    )
except ImportError:
    print("MCP library not found. Install with: pip install model-context-protocol")
    sys.exit(1)

# Additional imports for comprehensive functionality
try:
    import pyautogui
    import cv2
    import numpy as np
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from bs4 import BeautifulSoup
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email import encoders
except ImportError as e:
    print(f"Some optional dependencies not available: {e}")
    print("Install with: pip install pyautogui opencv-python selenium beautifulsoup4 pandas scikit-learn")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPFunction:
    """MCP Function definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    returns: Dict[str, Any]
    category: str
    implementation: callable

class ComprehensiveMCPServer:
    """Enterprise MCP Server with exhaustive tooling capabilities"""
    
    def __init__(self):
        self.server = Server("comprehensive-mcp-server")
        # Use relative path from script location to enterprise root
        # Path structure: mcp/server/mcp_server.py -> nerve_centre/llm_abstraction/mcp/server/
        # Need to go up 4 levels: server -> mcp -> llm_abstraction -> nerve_centre
        base_dir = Path(__file__).resolve().parents[4]  # Go up 4 levels to enterprise root
        self.config_path = base_dir / "config" / "mcp_functions.json"
        self.memory_db = sqlite3.connect(":memory:", check_same_thread=False)
        self.temp_dir = Path(tempfile.mkdtemp(prefix="mcp_workspace_"))
        self.web_driver = None
        self.setup_memory_db()
        self.load_configuration()
        self.register_all_functions()
        
    def setup_memory_db(self):
        """Initialize in-memory database for context management"""
        cursor = self.memory_db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_store (
                key TEXT PRIMARY KEY,
                value TEXT,
                category TEXT DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                metadata TEXT
            )
        """)
        self.memory_db.commit()
        
    def load_configuration(self):
        """Load MCP configuration from JSON"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
                logger.info(f"Loaded MCP configuration from {self.config_path}")
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {self.config_path}")
            self.config = {"function_categories": {}}
    
    def register_all_functions(self):
        """Register all MCP functions with the server"""
        
        # File Management Functions
        self.register_file_functions()
        
        # Code Execution Functions
        self.register_code_functions()
        
        # Web Operations Functions
        self.register_web_functions()
        
        # System Control Functions
        self.register_system_functions()
        
        # Database Functions
        self.register_database_functions()
        
        # Memory Management Functions
        self.register_memory_functions()
        
        # AI Operations Functions
        self.register_ai_functions()
        
        # Communication Functions
        self.register_communication_functions()
        
        # Auto-discovery and integration
        self.discover_external_mcp_servers()
        
    def register_file_functions(self):
        """Register file management functions"""
        
        @self.server.call_tool()
        async def create_file(file_path: str, content: str, encoding: str = "utf-8") -> Dict[str, Any]:
            """Create a new file with content"""
            try:
                path = Path(file_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, 'w', encoding=encoding) as f:
                    f.write(content)
                return {"success": True, "message": f"File created: {file_path}"}
            except Exception as e:
                return {"success": False, "message": f"Error creating file: {str(e)}"}
        
        @self.server.call_tool()
        async def read_file(file_path: str, encoding: str = "utf-8") -> str:
            """Read file content"""
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except Exception as e:
                return f"Error reading file: {str(e)}"
        
        @self.server.call_tool()
        async def write_file(file_path: str, content: str, mode: str = "w") -> bool:
            """Write content to file"""
            try:
                with open(file_path, mode) as f:
                    f.write(content)
                return True
            except Exception as e:
                logger.error(f"Error writing file: {e}")
                return False
        
        @self.server.call_tool()
        async def delete_file(file_path: str) -> bool:
            """Delete a file"""
            try:
                Path(file_path).unlink()
                return True
            except Exception as e:
                logger.error(f"Error deleting file: {e}")
                return False
        
        @self.server.call_tool()
        async def move_file(source_path: str, destination_path: str) -> bool:
            """Move or rename a file"""
            try:
                shutil.move(source_path, destination_path)
                return True
            except Exception as e:
                logger.error(f"Error moving file: {e}")
                return False
        
        @self.server.call_tool()
        async def copy_file(source_path: str, destination_path: str) -> bool:
            """Copy a file"""
            try:
                shutil.copy2(source_path, destination_path)
                return True
            except Exception as e:
                logger.error(f"Error copying file: {e}")
                return False
        
        @self.server.call_tool()
        async def list_directory(directory_path: str, recursive: bool = False) -> List[str]:
            """List directory contents"""
            try:
                path = Path(directory_path)
                if recursive:
                    return [str(p) for p in path.rglob("*")]
                else:
                    return [str(p) for p in path.iterdir()]
            except Exception as e:
                logger.error(f"Error listing directory: {e}")
                return []
        
        @self.server.call_tool()
        async def create_directory(directory_path: str, parents: bool = True) -> bool:
            """Create a directory"""
            try:
                Path(directory_path).mkdir(parents=parents, exist_ok=True)
                return True
            except Exception as e:
                logger.error(f"Error creating directory: {e}")
                return False
        
        @self.server.call_tool()
        async def get_file_info(file_path: str) -> Dict[str, Any]:
            """Get file metadata"""
            try:
                path = Path(file_path)
                stat = path.stat()
                return {
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "permissions": oct(stat.st_mode)[-3:],
                    "is_file": path.is_file(),
                    "is_directory": path.is_dir()
                }
            except Exception as e:
                return {"error": str(e)}
    
    def register_code_functions(self):
        """Register code execution functions"""
        
        @self.server.call_tool()
        async def execute_python(code: str, timeout: int = 30, capture_output: bool = True) -> Dict[str, Any]:
            """Execute Python code"""
            try:
                # Create temporary Python file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(code)
                    temp_file = f.name
                
                # Execute with timeout
                result = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=capture_output,
                    text=True,
                    timeout=timeout
                )
                
                # Cleanup
                os.unlink(temp_file)
                
                return {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.returncode
                }
            except subprocess.TimeoutExpired:
                return {"error": "Execution timed out", "exit_code": -1}
            except Exception as e:
                return {"error": str(e), "exit_code": -1}
        
        @self.server.call_tool()
        async def execute_shell(command: str, working_directory: str = "/", timeout: int = 30) -> Dict[str, Any]:
            """Execute shell commands"""
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=working_directory,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                return {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.returncode
                }
            except subprocess.TimeoutExpired:
                return {"error": "Command timed out", "exit_code": -1}
            except Exception as e:
                return {"error": str(e), "exit_code": -1}
        
        @self.server.call_tool()
        async def execute_javascript(code: str, timeout: int = 30) -> Dict[str, Any]:
            """Execute JavaScript code using Node.js"""
            try:
                result = subprocess.run(
                    ["node", "-e", code],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                return {
                    "result": result.stdout,
                    "error": result.stderr if result.stderr else None
                }
            except Exception as e:
                return {"error": str(e)}
    
    def register_web_functions(self):
        """Register web operations functions"""
        
        @self.server.call_tool()
        async def web_search(query: str, search_engine: str = "duckduckgo", num_results: int = 10) -> List[Dict[str, str]]:
            """Search the web"""
            try:
                # Simple implementation using requests
                if search_engine == "duckduckgo":
                    url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
                    response = requests.get(url)
                    data = response.json()
                    
                    results = []
                    for item in data.get("RelatedTopics", [])[:num_results]:
                        if "Text" in item and "FirstURL" in item:
                            results.append({
                                "title": item.get("Text", "")[:100],
                                "url": item.get("FirstURL", ""),
                                "snippet": item.get("Text", "")
                            })
                    
                    return results
                
                return [{"error": "Search engine not supported"}]
            except Exception as e:
                return [{"error": str(e)}]
        
        @self.server.call_tool()
        async def fetch_webpage(url: str, parse_html: bool = True, extract_text: bool = True) -> Dict[str, Any]:
            """Fetch and parse webpage content"""
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                result = {"content": response.text}
                
                if parse_html:
                    try:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        result["title"] = soup.title.string if soup.title else ""
                        result["links"] = [a.get('href') for a in soup.find_all('a', href=True)]
                        
                        if extract_text:
                            result["text_content"] = soup.get_text()
                    except Exception as e:
                        result["parse_error"] = str(e)
                
                return result
            except Exception as e:
                return {"error": str(e)}
        
        @self.server.call_tool()
        async def download_file(url: str, destination: str, chunk_size: int = 8192) -> Dict[str, Any]:
            """Download file from URL"""
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                file_size = 0
                with open(destination, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            file_size += len(chunk)
                
                return {"success": True, "file_size": file_size}
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    def register_system_functions(self):
        """Register system control functions"""
        
        @self.server.call_tool()
        async def run_application(application: str, arguments: List[str] = None, wait_for_exit: bool = False) -> Dict[str, Any]:
            """Launch an application"""
            try:
                args = [application] + (arguments or [])
                if wait_for_exit:
                    result = subprocess.run(args, capture_output=True, text=True)
                    return {"pid": 0, "success": True, "output": result.stdout}
                else:
                    process = subprocess.Popen(args)
                    return {"pid": process.pid, "success": True}
            except Exception as e:
                return {"pid": 0, "success": False, "error": str(e)}
        
        @self.server.call_tool()
        async def list_processes(filter_name: str = None) -> List[Dict[str, Any]]:
            """List running processes"""
            try:
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        pinfo = proc.info
                        if filter_name is None or filter_name.lower() in pinfo['name'].lower():
                            processes.append({
                                "pid": pinfo['pid'],
                                "name": pinfo['name'],
                                "cpu": pinfo['cpu_percent'],
                                "memory": pinfo['memory_percent']
                            })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                return processes
            except Exception as e:
                return [{"error": str(e)}]
        
        @self.server.call_tool()
        async def take_screenshot(region: Dict[str, int] = None, save_path: str = None) -> str:
            """Capture screen screenshot"""
            try:
                if save_path is None:
                    save_path = str(self.temp_dir / f"screenshot_{int(time.time())}.png")
                
                if region:
                    screenshot = pyautogui.screenshot(
                        region=(region['x'], region['y'], region['width'], region['height'])
                    )
                else:
                    screenshot = pyautogui.screenshot()
                
                screenshot.save(save_path)
                return save_path
            except Exception as e:
                return f"Error taking screenshot: {str(e)}"
        
        @self.server.call_tool()
        async def click_at(x: int, y: int, button: str = "left") -> bool:
            """Click at screen coordinates"""
            try:
                pyautogui.click(x, y, button=button)
                return True
            except Exception as e:
                logger.error(f"Error clicking: {e}")
                return False
        
        @self.server.call_tool()
        async def type_text(text: str, delay: float = 0.05) -> bool:
            """Type text at current cursor position"""
            try:
                pyautogui.typewrite(text, interval=delay)
                return True
            except Exception as e:
                logger.error(f"Error typing text: {e}")
                return False
    
    def register_memory_functions(self):
        """Register memory management functions"""
        
        @self.server.call_tool()
        async def store_memory(key: str, value: Any, category: str = "general", ttl: int = None) -> bool:
            """Store information in memory"""
            try:
                cursor = self.memory_db.cursor()
                expires_at = None
                if ttl:
                    expires_at = datetime.now() + timedelta(seconds=ttl)
                
                cursor.execute(
                    "INSERT OR REPLACE INTO memory_store (key, value, category, expires_at) VALUES (?, ?, ?, ?)",
                    (key, json.dumps(value), category, expires_at)
                )
                self.memory_db.commit()
                return True
            except Exception as e:
                logger.error(f"Error storing memory: {e}")
                return False
        
        @self.server.call_tool()
        async def retrieve_memory(key: str, category: str = "general") -> Any:
            """Retrieve information from memory"""
            try:
                cursor = self.memory_db.cursor()
                cursor.execute(
                    "SELECT value FROM memory_store WHERE key = ? AND category = ? AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)",
                    (key, category)
                )
                result = cursor.fetchone()
                if result:
                    return json.loads(result[0])
                return None
            except Exception as e:
                logger.error(f"Error retrieving memory: {e}")
                return None
        
        @self.server.call_tool()
        async def search_memory(query: str, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
            """Search memory by content"""
            try:
                cursor = self.memory_db.cursor()
                if category:
                    cursor.execute(
                        "SELECT key, value, category FROM memory_store WHERE value LIKE ? AND category = ? LIMIT ?",
                        (f"%{query}%", category, limit)
                    )
                else:
                    cursor.execute(
                        "SELECT key, value, category FROM memory_store WHERE value LIKE ? LIMIT ?",
                        (f"%{query}%", limit)
                    )
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        "key": row[0],
                        "value": json.loads(row[1]),
                        "category": row[2]
                    })
                return results
            except Exception as e:
                logger.error(f"Error searching memory: {e}")
                return []
    
    def register_database_functions(self):
        """Register database operation functions"""
        
        @self.server.call_tool()
        async def execute_sql(query: str, database_url: str, parameters: List[Any] = None) -> Dict[str, Any]:
            """Execute SQL query"""
            try:
                if database_url.startswith("sqlite://"):
                    db_path = database_url.replace("sqlite://", "")
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    if parameters:
                        cursor.execute(query, parameters)
                    else:
                        cursor.execute(query)
                    
                    if query.strip().upper().startswith("SELECT"):
                        rows = cursor.fetchall()
                        columns = [description[0] for description in cursor.description]
                        result = {
                            "rows": [dict(zip(columns, row)) for row in rows],
                            "affected_rows": len(rows)
                        }
                    else:
                        conn.commit()
                        result = {"affected_rows": cursor.rowcount}
                    
                    conn.close()
                    return result
                else:
                    return {"error": "Database type not supported"}
            except Exception as e:
                return {"error": str(e)}
    
    def register_ai_functions(self):
        """Register AI/ML operation functions"""
        
        @self.server.call_tool()
        async def semantic_search(query: str, documents: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
            """Perform semantic search using TF-IDF"""
            try:
                if not documents:
                    return []
                
                # Simple TF-IDF based semantic search
                vectorizer = TfidfVectorizer()
                doc_vectors = vectorizer.fit_transform(documents)
                query_vector = vectorizer.transform([query])
                
                similarities = cosine_similarity(query_vector, doc_vectors).flatten()
                top_indices = similarities.argsort()[-top_k:][::-1]
                
                results = []
                for idx in top_indices:
                    if similarities[idx] > 0:
                        results.append({
                            "document": documents[idx],
                            "similarity": float(similarities[idx]),
                            "index": int(idx)
                        })
                
                return results
            except Exception as e:
                return [{"error": str(e)}]
    
    def register_communication_functions(self):
        """Register communication functions"""
        
        @self.server.call_tool()
        async def make_http_request(url: str, method: str = "GET", headers: Dict[str, str] = None, 
                                 data: Any = None, timeout: int = 30) -> Dict[str, Any]:
            """Make HTTP request"""
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data if isinstance(data, dict) else None,
                    data=data if not isinstance(data, dict) else None,
                    timeout=timeout
                )
                
                return {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.text
                }
            except Exception as e:
                return {"error": str(e)}
    
    def discover_external_mcp_servers(self):
        """Auto-discover and integrate external MCP servers"""
        try:
            known_servers = self.config.get("mcp_servers", {}).get("known_servers", [])
            
            for server_config in known_servers:
                try:
                    # Test if server is available
                    test_cmd = server_config.get("command")
                    if test_cmd and shutil.which(test_cmd):
                        logger.info(f"Found MCP server: {server_config['name']}")
                        # Here you would integrate with the external server
                        # This is a simplified example
                        self.register_external_server(server_config)
                except Exception as e:
                    logger.debug(f"Could not connect to {server_config['name']}: {e}")
        except Exception as e:
            logger.error(f"Error during auto-discovery: {e}")
    
    def register_external_server(self, server_config: Dict[str, Any]):
        """Register functions from external MCP server"""
        # This would implement the actual integration with external MCP servers
        # For now, we log the availability
        logger.info(f"External MCP server available: {server_config['name']} - {server_config['description']}")
    
    async def run(self):
        """Run the MCP server"""
        try:
            logger.info("Starting Comprehensive MCP Server...")
            await stdio_server(self.server)
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.web_driver:
                self.web_driver.quit()
            
            if self.memory_db:
                self.memory_db.close()
            
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

async def main():
    """Main entry point"""
    server = ComprehensiveMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
