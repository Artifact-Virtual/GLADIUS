"""
Memory Module - Unified memory access with native tool calling.

Provides:
- Multi-database access (Hektor VDB, SQLite, JSON)
- Native tool calling for cognition self-learning
- Workspace operations (sandboxed file access)
- Unified interface across all data stores
"""

import os
import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field

# Try Hektor first
try:
    from .hektor_store import HektorVectorStore, HEKTOR_AVAILABLE, get_vector_store
except ImportError:
    HEKTOR_AVAILABLE = False
    HektorVectorStore = None
    get_vector_store = None

from .vector_store import VectorStore, SearchResult


@dataclass
class ToolResult:
    """Result from a tool call."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    tool_name: str = ""
    execution_time_ms: float = 0.0


@dataclass
class DatabaseConnection:
    """Represents a connected database."""
    name: str
    db_type: str  # 'vector', 'sqlite', 'json'
    path: Path
    connection: Any = None
    read_only: bool = False


class MemoryModule:
    """
    Unified memory interface with native tool calling.
    
    Connects all databases and provides tools that the cognition engine
    can learn to use natively (not through third-party LLMs).
    """
    
    def __init__(
        self,
        base_dir: str = ".",
        workspace_dir: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        sandbox_enabled: bool = True,
        vector_store: Any = None,
        skip_vector_discovery: bool = False
    ):
        self.base_dir = Path(base_dir).resolve()
        self.workspace_dir = Path(workspace_dir or base_dir).resolve()
        self.logger = logger or logging.getLogger(__name__)
        self.sandbox_enabled = sandbox_enabled
        self.skip_vector_discovery = skip_vector_discovery
        
        # Database connections
        self.databases: Dict[str, DatabaseConnection] = {}
        
        # Tool registry
        self.tools: Dict[str, Callable] = {}
        
        # Operation history for learning
        self.history: List[Dict[str, Any]] = []
        
        # Initialize
        self._register_default_tools()
        self._auto_discover_databases()
        
        # Use provided vector store if available
        if vector_store is not None:
            self.databases["hektor"] = DatabaseConnection(
                name="hektor",
                db_type="vector",
                path=self.base_dir / "data" / "vectors",
                connection=vector_store,
                read_only=False
            )
        
        self.logger.info(f"[MEMORY] Initialized with {len(self.databases)} databases, {len(self.tools)} tools")
    
    def _register_default_tools(self):
        """Register built-in tools."""
        self.tools = {
            # Database tools
            "read_db": self.read_db,
            "write_db": self.write_db,
            "query_db": self.query_db,
            "list_databases": self.list_databases,
            
            # Search tools
            "search": self.search,
            "hybrid_search": self.hybrid_search,
            "get_context": self.get_context,
            
            # Workspace tools
            "read_file": self.read_file,
            "write_file": self.write_file,
            "list_dir": self.list_dir,
            "file_exists": self.file_exists,
            
            # Memory tools
            "remember": self.remember,
            "recall": self.recall,
            "forget": self.forget,
            
            # Introspection
            "get_tools": self.get_tools,
            "get_history": self.get_history,
        }
    
    def _auto_discover_databases(self):
        """Auto-discover databases in the base directory."""
        # Look for SQLite databases
        for db_path in self.base_dir.rglob("*.db"):
            if db_path.name.startswith('.'):
                continue
            # Skip hektor databases - they're not SQLite
            if 'hektor' in db_path.name.lower() or 'vectors' in str(db_path):
                continue
            name = db_path.stem
            if name not in self.databases:
                self.connect_database(name, "sqlite", db_path)
        
        # Look for JSON stores
        data_dir = self.base_dir / "data"
        if data_dir.exists():
            for json_path in data_dir.glob("*.json"):
                name = f"json_{json_path.stem}"
                if name not in self.databases:
                    self.connect_database(name, "json", json_path)
        
        # Skip vector discovery if requested or if we have an external store
        if self.skip_vector_discovery:
            return
            
        # Try to connect Hektor VDB only if not already connected
        if "hektor" not in self.databases:
            vectors_dir = self.base_dir / "data" / "vectors"
            if vectors_dir.exists() and HEKTOR_AVAILABLE:
                try:
                    self.connect_database("hektor", "vector", vectors_dir)
                except Exception as e:
                    self.logger.warning(f"[MEMORY] Could not connect Hektor VDB: {e}")
    
    def connect_database(
        self,
        name: str,
        db_type: str,
        path: Union[str, Path],
        read_only: bool = False
    ) -> bool:
        """
        Connect a database.
        
        Args:
            name: Name for the database connection
            db_type: Type ('vector', 'sqlite', 'json')
            path: Path to database
            read_only: If True, only allow reads
        
        Returns:
            True if connected successfully
        """
        path = Path(path)
        
        try:
            connection = None
            
            if db_type == "sqlite":
                mode = "ro" if read_only else "rw"
                uri = f"file:{path}?mode={mode}"
                connection = sqlite3.connect(uri, uri=True)
                connection.row_factory = sqlite3.Row
                
            elif db_type == "vector":
                if HEKTOR_AVAILABLE:
                    connection = HektorVectorStore(path)
                else:
                    connection = VectorStore(path)
                    
            elif db_type == "json":
                # JSON is loaded on-demand, just verify it exists
                if path.exists():
                    connection = {"path": path}
            
            self.databases[name] = DatabaseConnection(
                name=name,
                db_type=db_type,
                path=path,
                connection=connection,
                read_only=read_only
            )
            
            self.logger.info(f"[MEMORY] Connected database: {name} ({db_type})")
            return True
            
        except Exception as e:
            self.logger.error(f"[MEMORY] Failed to connect {name}: {e}")
            return False
    
    # ========== Database Tools ==========
    
    def read_db(self, name: str, query: str, params: Optional[tuple] = None) -> ToolResult:
        """
        Read from a database.
        
        Args:
            name: Database name
            query: SQL query (for sqlite) or search query (for vector)
            params: Query parameters (for sqlite)
        """
        start = datetime.now()
        
        if name not in self.databases:
            return ToolResult(
                success=False,
                error=f"Database '{name}' not found",
                tool_name="read_db"
            )
        
        db = self.databases[name]
        
        try:
            if db.db_type == "sqlite":
                cursor = db.connection.cursor()
                cursor.execute(query, params or ())
                rows = cursor.fetchall()
                data = [dict(row) for row in rows]
                
            elif db.db_type == "vector":
                results = db.connection.search(query, k=10)
                data = [{"id": r.document.id, "score": r.score, "content": r.document.content[:200]} for r in results]
                
            elif db.db_type == "json":
                with open(db.path, 'r') as f:
                    full_data = json.load(f)
                # Simple key-based query
                if query in full_data:
                    data = full_data[query]
                else:
                    data = full_data
            else:
                return ToolResult(success=False, error=f"Unknown db type: {db.db_type}", tool_name="read_db")
            
            elapsed = (datetime.now() - start).total_seconds() * 1000
            self._record_operation("read_db", name, query, True)
            
            return ToolResult(success=True, data=data, tool_name="read_db", execution_time_ms=elapsed)
            
        except Exception as e:
            self._record_operation("read_db", name, query, False, str(e))
            return ToolResult(success=False, error=str(e), tool_name="read_db")
    
    def write_db(self, name: str, data: Any, table: Optional[str] = None) -> ToolResult:
        """
        Write to a database.
        
        Args:
            name: Database name
            data: Data to write
            table: Table name (for sqlite)
        """
        start = datetime.now()
        
        if name not in self.databases:
            return ToolResult(success=False, error=f"Database '{name}' not found", tool_name="write_db")
        
        db = self.databases[name]
        
        if db.read_only:
            return ToolResult(success=False, error=f"Database '{name}' is read-only", tool_name="write_db")
        
        try:
            if db.db_type == "sqlite":
                if not table or not isinstance(data, dict):
                    return ToolResult(success=False, error="Need table name and dict data for sqlite", tool_name="write_db")
                
                columns = ", ".join(data.keys())
                placeholders = ", ".join("?" * len(data))
                sql = f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})"
                
                cursor = db.connection.cursor()
                cursor.execute(sql, tuple(data.values()))
                db.connection.commit()
                
            elif db.db_type == "vector":
                if isinstance(data, dict) and "id" in data and "content" in data:
                    db.connection.add_text(
                        data["id"],
                        data["content"],
                        data.get("metadata", {}),
                        doc_type=data.get("doc_type", "memory")
                    )
                else:
                    return ToolResult(success=False, error="Vector data needs 'id' and 'content'", tool_name="write_db")
                    
            elif db.db_type == "json":
                with open(db.path, 'r') as f:
                    full_data = json.load(f)
                
                if isinstance(data, dict):
                    full_data.update(data)
                else:
                    return ToolResult(success=False, error="JSON data must be a dict", tool_name="write_db")
                
                with open(db.path, 'w') as f:
                    json.dump(full_data, f, indent=2)
            
            elapsed = (datetime.now() - start).total_seconds() * 1000
            self._record_operation("write_db", name, str(data)[:100], True)
            
            return ToolResult(success=True, data={"written": True}, tool_name="write_db", execution_time_ms=elapsed)
            
        except Exception as e:
            self._record_operation("write_db", name, str(data)[:100], False, str(e))
            return ToolResult(success=False, error=str(e), tool_name="write_db")
    
    def query_db(self, name: str, query: str) -> ToolResult:
        """Execute a raw query on a database."""
        return self.read_db(name, query)
    
    def list_databases(self) -> ToolResult:
        """List all connected databases."""
        data = [
            {
                "name": db.name,
                "type": db.db_type,
                "path": str(db.path),
                "read_only": db.read_only
            }
            for db in self.databases.values()
        ]
        return ToolResult(success=True, data=data, tool_name="list_databases")
    
    # ========== Search Tools ==========
    
    def search(self, query: str, k: int = 5, db_name: str = "hektor") -> ToolResult:
        """
        Semantic search across vector database.
        
        Args:
            query: Search query
            k: Number of results
            db_name: Vector database to search
        """
        if db_name not in self.databases:
            # Try to find any vector database
            for name, db in self.databases.items():
                if db.db_type == "vector":
                    db_name = name
                    break
        
        if db_name not in self.databases or self.databases[db_name].db_type != "vector":
            return ToolResult(success=False, error="No vector database available", tool_name="search")
        
        try:
            db = self.databases[db_name]
            results = db.connection.search(query, k=k)
            
            data = [
                {
                    "id": r.document.id,
                    "score": r.score,
                    "content": r.document.content[:500],
                    "metadata": r.document.metadata
                }
                for r in results
            ]
            
            self._record_operation("search", query, f"k={k}", True)
            return ToolResult(success=True, data=data, tool_name="search")
            
        except Exception as e:
            return ToolResult(success=False, error=str(e), tool_name="search")
    
    def hybrid_search(
        self,
        query: str,
        k: int = 5,
        vector_weight: float = 0.7,
        bm25_weight: float = 0.3
    ) -> ToolResult:
        """Hybrid search with vector + BM25."""
        for name, db in self.databases.items():
            if db.db_type == "vector":
                try:
                    if hasattr(db.connection, 'hybrid_search'):
                        results = db.connection.hybrid_search(
                            query, k=k,
                            vector_weight=vector_weight,
                            bm25_weight=bm25_weight
                        )
                    else:
                        results = db.connection.search(query, k=k)
                    
                    data = [
                        {
                            "id": r.document.id,
                            "score": r.score,
                            "content": r.document.content[:500]
                        }
                        for r in results
                    ]
                    
                    return ToolResult(success=True, data=data, tool_name="hybrid_search")
                    
                except Exception as e:
                    return ToolResult(success=False, error=str(e), tool_name="hybrid_search")
        
        return ToolResult(success=False, error="No vector database available", tool_name="hybrid_search")
    
    def get_context(self, query: str, k: int = 3) -> ToolResult:
        """Get relevant context for a query."""
        result = self.search(query, k=k)
        
        if not result.success:
            return result
        
        context_parts = ["## Relevant Context\n"]
        for i, item in enumerate(result.data, 1):
            context_parts.append(f"### [{i}] (Score: {item['score']:.2f})\n{item['content']}\n")
        
        return ToolResult(
            success=True,
            data="\n".join(context_parts),
            tool_name="get_context"
        )
    
    # ========== Workspace Tools ==========
    
    def _check_sandbox(self, path: Path) -> bool:
        """Check if path is within sandbox."""
        if not self.sandbox_enabled:
            return True
        
        try:
            resolved = path.resolve()
            return str(resolved).startswith(str(self.workspace_dir))
        except:
            return False
    
    def read_file(self, path: str) -> ToolResult:
        """
        Read a file from the workspace.
        
        Args:
            path: Relative or absolute path to file
        """
        filepath = Path(path)
        if not filepath.is_absolute():
            filepath = self.workspace_dir / filepath
        
        if not self._check_sandbox(filepath):
            return ToolResult(success=False, error="Path outside sandbox", tool_name="read_file")
        
        if not filepath.exists():
            return ToolResult(success=False, error=f"File not found: {path}", tool_name="read_file")
        
        try:
            content = filepath.read_text(encoding='utf-8')
            self._record_operation("read_file", str(path), f"{len(content)} bytes", True)
            return ToolResult(success=True, data=content, tool_name="read_file")
        except Exception as e:
            return ToolResult(success=False, error=str(e), tool_name="read_file")
    
    def write_file(self, path: str, content: str) -> ToolResult:
        """
        Write a file to the workspace.
        
        Args:
            path: Relative or absolute path
            content: Content to write
        """
        filepath = Path(path)
        if not filepath.is_absolute():
            filepath = self.workspace_dir / filepath
        
        if not self._check_sandbox(filepath):
            return ToolResult(success=False, error="Path outside sandbox", tool_name="write_file")
        
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(content, encoding='utf-8')
            self._record_operation("write_file", str(path), f"{len(content)} bytes", True)
            return ToolResult(success=True, data={"path": str(filepath), "bytes": len(content)}, tool_name="write_file")
        except Exception as e:
            return ToolResult(success=False, error=str(e), tool_name="write_file")
    
    def list_dir(self, path: str = ".") -> ToolResult:
        """
        List directory contents.
        
        Args:
            path: Directory path (relative to workspace)
        """
        dirpath = Path(path)
        if not dirpath.is_absolute():
            dirpath = self.workspace_dir / dirpath
        
        if not self._check_sandbox(dirpath):
            return ToolResult(success=False, error="Path outside sandbox", tool_name="list_dir")
        
        if not dirpath.exists():
            return ToolResult(success=False, error=f"Directory not found: {path}", tool_name="list_dir")
        
        try:
            items = []
            for item in dirpath.iterdir():
                if item.name.startswith('.'):
                    continue
                items.append({
                    "name": item.name,
                    "type": "dir" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })
            
            return ToolResult(success=True, data=sorted(items, key=lambda x: (x["type"], x["name"])), tool_name="list_dir")
        except Exception as e:
            return ToolResult(success=False, error=str(e), tool_name="list_dir")
    
    def file_exists(self, path: str) -> ToolResult:
        """Check if a file exists."""
        filepath = Path(path)
        if not filepath.is_absolute():
            filepath = self.workspace_dir / filepath
        
        return ToolResult(success=True, data=filepath.exists(), tool_name="file_exists")
    
    # ========== Memory Tools ==========
    
    def remember(self, key: str, value: Any, metadata: Optional[Dict] = None) -> ToolResult:
        """
        Store a memory for later recall.
        
        Args:
            key: Memory key/identifier
            value: Value to remember
            metadata: Optional metadata
        """
        # Find a vector database to store in
        for name, db in self.databases.items():
            if db.db_type == "vector" and not db.read_only:
                try:
                    content = json.dumps(value) if not isinstance(value, str) else value
                    full_metadata = {
                        "key": key,
                        "remembered_at": datetime.now().isoformat(),
                        **(metadata or {})
                    }
                    
                    db.connection.add_text(f"memory_{key}", content, full_metadata, doc_type="memory")
                    
                    self._record_operation("remember", key, str(value)[:50], True)
                    return ToolResult(success=True, data={"key": key}, tool_name="remember")
                    
                except Exception as e:
                    return ToolResult(success=False, error=str(e), tool_name="remember")
        
        return ToolResult(success=False, error="No writable vector database", tool_name="remember")
    
    def recall(self, query: str, k: int = 3) -> ToolResult:
        """
        Recall memories related to a query.
        
        Args:
            query: What to recall
            k: Number of memories to retrieve
        """
        # Search memories specifically
        for name, db in self.databases.items():
            if db.db_type == "vector":
                try:
                    results = db.connection.search(query, k=k, doc_type="memory")
                    
                    data = [
                        {
                            "key": r.document.metadata.get("key", r.document.id),
                            "content": r.document.content,
                            "score": r.score,
                            "remembered_at": r.document.metadata.get("remembered_at")
                        }
                        for r in results
                    ]
                    
                    return ToolResult(success=True, data=data, tool_name="recall")
                    
                except Exception as e:
                    return ToolResult(success=False, error=str(e), tool_name="recall")
        
        return ToolResult(success=False, error="No vector database", tool_name="recall")
    
    def forget(self, key: str) -> ToolResult:
        """
        Remove a memory.
        
        Args:
            key: Memory key to forget
        """
        for name, db in self.databases.items():
            if db.db_type == "vector" and not db.read_only:
                try:
                    if hasattr(db.connection, 'delete'):
                        db.connection.delete(f"memory_{key}")
                        return ToolResult(success=True, data={"forgotten": key}, tool_name="forget")
                except:
                    pass
        
        return ToolResult(success=False, error="Could not forget memory", tool_name="forget")
    
    # ========== Introspection ==========
    
    def get_tools(self) -> ToolResult:
        """Get list of available tools."""
        tool_docs = {}
        for name, func in self.tools.items():
            doc = func.__doc__ or "No documentation"
            tool_docs[name] = doc.strip().split('\n')[0]  # First line only
        
        return ToolResult(success=True, data=tool_docs, tool_name="get_tools")
    
    def get_history(self, last_n: int = 20) -> ToolResult:
        """Get recent operation history."""
        return ToolResult(success=True, data=self.history[-last_n:], tool_name="get_history")
    
    def _record_operation(
        self,
        tool: str,
        arg1: str,
        arg2: str,
        success: bool,
        error: Optional[str] = None
    ):
        """Record an operation for learning."""
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "tool": tool,
            "args": [arg1, arg2],
            "success": success,
            "error": error
        })
        
        # Keep history bounded
        if len(self.history) > 1000:
            self.history = self.history[-500:]
    
    # ========== Tool Execution ==========
    
    def call_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """
        Execute a tool by name.
        
        This is the interface the cognition engine uses to call tools.
        
        Args:
            tool_name: Name of the tool
            **kwargs: Tool arguments
        
        Returns:
            ToolResult with success status and data
        """
        if tool_name not in self.tools:
            return ToolResult(
                success=False,
                error=f"Unknown tool: {tool_name}. Available: {list(self.tools.keys())}",
                tool_name=tool_name
            )
        
        try:
            return self.tools[tool_name](**kwargs)
        except Exception as e:
            return ToolResult(success=False, error=str(e), tool_name=tool_name)
    
    def close(self):
        """Close all database connections."""
        for db in self.databases.values():
            if db.db_type == "sqlite" and db.connection:
                try:
                    db.connection.close()
                except:
                    pass
            elif db.db_type == "vector" and db.connection:
                try:
                    db.connection.close()
                except:
                    pass
        
        self.logger.info("[MEMORY] Closed all connections")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
