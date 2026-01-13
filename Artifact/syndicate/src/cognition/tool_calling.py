"""
Native Tool Calling - Tool definitions for cognition self-learning.

This module defines the tool schema that the cognition engine learns to use.
Unlike third-party LLM tool calling, this is for native learning - the system
learns which tools to use through its own training, not external API calls.

The goal is for Gladius to eventually run its own GGUF/GGM models that have
been fine-tuned to use these tools natively.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
import json


@dataclass
class ToolParameter:
    """Describes a tool parameter."""
    name: str
    param_type: str  # 'string', 'integer', 'float', 'boolean', 'object', 'array'
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[str]] = None


@dataclass
class ToolDefinition:
    """
    Defines a tool that the cognition engine can learn to use.
    
    This schema is compatible with common tool-calling formats
    (OpenAI, Anthropic) for training data generation.
    """
    name: str
    description: str
    parameters: List[ToolParameter] = field(default_factory=list)
    category: str = "general"
    examples: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_openai_schema(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling schema."""
        properties = {}
        required = []
        
        for param in self.parameters:
            prop = {"type": param.param_type, "description": param.description}
            if param.enum:
                prop["enum"] = param.enum
            properties[param.name] = prop
            
            if param.required:
                required.append(param.name)
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
    
    def to_anthropic_schema(self) -> Dict[str, Any]:
        """Convert to Anthropic tool schema."""
        input_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param in self.parameters:
            input_schema["properties"][param.name] = {
                "type": param.param_type,
                "description": param.description
            }
            if param.required:
                input_schema["required"].append(param.name)
        
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": input_schema
        }
    
    def generate_training_example(self, args: Dict[str, Any], result: Any) -> Dict[str, Any]:
        """Generate a training example for fine-tuning."""
        return {
            "tool": self.name,
            "args": args,
            "result": result,
            "category": self.category
        }


# ============================================================
# Built-in Tool Definitions
# ============================================================

BUILTIN_TOOLS: List[ToolDefinition] = [
    # Database Tools
    ToolDefinition(
        name="read_db",
        description="Read data from a database. Supports SQLite (SQL queries), vector databases (semantic search), and JSON stores.",
        category="database",
        parameters=[
            ToolParameter("name", "string", "Name of the database to query"),
            ToolParameter("query", "string", "SQL query (for sqlite) or search query (for vector)"),
            ToolParameter("params", "array", "Query parameters for SQL", required=False),
        ],
        examples=[
            {"args": {"name": "syndicate", "query": "SELECT * FROM predictions ORDER BY date DESC LIMIT 5"}, "result": "[list of predictions]"},
            {"args": {"name": "hektor", "query": "gold bullish momentum"}, "result": "[semantic search results]"},
        ]
    ),
    
    ToolDefinition(
        name="write_db",
        description="Write data to a database. For SQLite: insert/update rows. For vector: add documents. For JSON: update keys.",
        category="database",
        parameters=[
            ToolParameter("name", "string", "Name of the database"),
            ToolParameter("data", "object", "Data to write"),
            ToolParameter("table", "string", "Table name (for SQLite)", required=False),
        ],
        examples=[
            {"args": {"name": "syndicate", "table": "predictions", "data": {"date": "2026-01-13", "bias": "BULLISH"}}, "result": {"written": True}},
        ]
    ),
    
    ToolDefinition(
        name="list_databases",
        description="List all connected databases with their types and paths.",
        category="database",
        parameters=[],
        examples=[
            {"args": {}, "result": [{"name": "hektor", "type": "vector"}, {"name": "syndicate", "type": "sqlite"}]},
        ]
    ),
    
    # Search Tools
    ToolDefinition(
        name="search",
        description="Semantic search across the vector database. Returns similar documents ranked by relevance.",
        category="search",
        parameters=[
            ToolParameter("query", "string", "Natural language search query"),
            ToolParameter("k", "integer", "Number of results to return", required=False, default=5),
            ToolParameter("db_name", "string", "Vector database name", required=False, default="hektor"),
        ],
        examples=[
            {"args": {"query": "gold resistance breakout", "k": 3}, "result": "[top 3 relevant documents]"},
        ]
    ),
    
    ToolDefinition(
        name="hybrid_search",
        description="Combined vector + BM25 lexical search. Better for queries mixing semantic meaning and keywords.",
        category="search",
        parameters=[
            ToolParameter("query", "string", "Search query"),
            ToolParameter("k", "integer", "Number of results", required=False, default=5),
            ToolParameter("vector_weight", "float", "Weight for vector similarity (0-1)", required=False, default=0.7),
            ToolParameter("bm25_weight", "float", "Weight for BM25 lexical match (0-1)", required=False, default=0.3),
        ],
        examples=[
            {"args": {"query": "XAUUSD support level 2680", "k": 5}, "result": "[hybrid ranked results]"},
        ]
    ),
    
    ToolDefinition(
        name="get_context",
        description="Retrieve relevant historical context for analysis. Returns formatted context string for prompts.",
        category="search",
        parameters=[
            ToolParameter("query", "string", "What context to retrieve"),
            ToolParameter("k", "integer", "Number of context items", required=False, default=3),
        ],
        examples=[
            {"args": {"query": "gold testing 2700 resistance"}, "result": "## Relevant Context\n..."},
        ]
    ),
    
    # Workspace Tools
    ToolDefinition(
        name="read_file",
        description="Read content from a file in the workspace.",
        category="workspace",
        parameters=[
            ToolParameter("path", "string", "File path (relative to workspace or absolute)"),
        ],
        examples=[
            {"args": {"path": "output/Journal_2026-01-13.md"}, "result": "# Market Journal..."},
        ]
    ),
    
    ToolDefinition(
        name="write_file",
        description="Write content to a file in the workspace. Creates parent directories if needed.",
        category="workspace",
        parameters=[
            ToolParameter("path", "string", "File path"),
            ToolParameter("content", "string", "Content to write"),
        ],
        examples=[
            {"args": {"path": "output/notes/analysis.md", "content": "# Analysis\n..."}, "result": {"path": "...", "bytes": 123}},
        ]
    ),
    
    ToolDefinition(
        name="list_dir",
        description="List files and directories in a path.",
        category="workspace",
        parameters=[
            ToolParameter("path", "string", "Directory path", required=False, default="."),
        ],
        examples=[
            {"args": {"path": "output"}, "result": [{"name": "journals", "type": "dir"}, {"name": "report.md", "type": "file"}]},
        ]
    ),
    
    ToolDefinition(
        name="file_exists",
        description="Check if a file exists.",
        category="workspace",
        parameters=[
            ToolParameter("path", "string", "File path to check"),
        ],
        examples=[
            {"args": {"path": "config.json"}, "result": True},
        ]
    ),
    
    # Memory Tools
    ToolDefinition(
        name="remember",
        description="Store a memory for later recall. Memories are vectorized for semantic retrieval.",
        category="memory",
        parameters=[
            ToolParameter("key", "string", "Memory key/identifier"),
            ToolParameter("value", "string", "Value to remember (will be stored as text)"),
            ToolParameter("metadata", "object", "Optional metadata", required=False),
        ],
        examples=[
            {"args": {"key": "gold_pattern_2026", "value": "Gold shows head-and-shoulders pattern..."}, "result": {"key": "gold_pattern_2026"}},
        ]
    ),
    
    ToolDefinition(
        name="recall",
        description="Recall memories related to a query using semantic search.",
        category="memory",
        parameters=[
            ToolParameter("query", "string", "What to recall"),
            ToolParameter("k", "integer", "Number of memories", required=False, default=3),
        ],
        examples=[
            {"args": {"query": "gold patterns"}, "result": [{"key": "gold_pattern_2026", "content": "..."}]},
        ]
    ),
    
    ToolDefinition(
        name="forget",
        description="Remove a specific memory.",
        category="memory",
        parameters=[
            ToolParameter("key", "string", "Memory key to forget"),
        ],
        examples=[
            {"args": {"key": "old_pattern"}, "result": {"forgotten": "old_pattern"}},
        ]
    ),
    
    # Introspection Tools
    ToolDefinition(
        name="get_tools",
        description="List all available tools with their descriptions.",
        category="introspection",
        parameters=[],
        examples=[
            {"args": {}, "result": {"search": "Semantic search...", "read_file": "Read content..."}},
        ]
    ),
    
    ToolDefinition(
        name="get_history",
        description="Get recent operation history for learning and debugging.",
        category="introspection",
        parameters=[
            ToolParameter("last_n", "integer", "Number of recent operations", required=False, default=20),
        ],
        examples=[
            {"args": {"last_n": 5}, "result": [{"tool": "search", "success": True, "timestamp": "..."}]},
        ]
    ),
]


class ToolRegistry:
    """
    Registry of tools available for cognition.
    
    Used for:
    - Generating training data for fine-tuning
    - Creating tool schemas for inference
    - Validating tool calls
    """
    
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        
        # Register built-in tools
        for tool in BUILTIN_TOOLS:
            self.register(tool)
    
    def register(self, tool: ToolDefinition):
        """Register a tool definition."""
        self.tools[tool.name] = tool
    
    def get(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self, category: Optional[str] = None) -> List[ToolDefinition]:
        """List all tools, optionally filtered by category."""
        if category:
            return [t for t in self.tools.values() if t.category == category]
        return list(self.tools.values())
    
    def to_openai_tools(self, category: Optional[str] = None) -> List[Dict]:
        """Export all tools in OpenAI format."""
        return [t.to_openai_schema() for t in self.list_tools(category)]
    
    def to_anthropic_tools(self, category: Optional[str] = None) -> List[Dict]:
        """Export all tools in Anthropic format."""
        return [t.to_anthropic_schema() for t in self.list_tools(category)]
    
    def generate_system_prompt(self) -> str:
        """Generate a system prompt describing available tools."""
        prompt_parts = ["You have access to the following tools:\n"]
        
        for category in sorted(set(t.category for t in self.tools.values())):
            prompt_parts.append(f"\n## {category.title()} Tools\n")
            
            for tool in self.list_tools(category):
                params_str = ", ".join(
                    f"{p.name}: {p.param_type}" + ("" if p.required else "?")
                    for p in tool.parameters
                )
                prompt_parts.append(f"- **{tool.name}**({params_str}): {tool.description}")
        
        prompt_parts.append("\n\nTo use a tool, respond with JSON: {\"tool\": \"name\", \"args\": {...}}")
        
        return "\n".join(prompt_parts)
    
    def validate_call(self, tool_name: str, args: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate a tool call.
        
        Returns:
            (is_valid, error_message)
        """
        if tool_name not in self.tools:
            return False, f"Unknown tool: {tool_name}"
        
        tool = self.tools[tool_name]
        
        # Check required parameters
        for param in tool.parameters:
            if param.required and param.name not in args:
                return False, f"Missing required parameter: {param.name}"
        
        return True, None
    
    def generate_training_data(self, calls: List[Dict]) -> List[Dict]:
        """
        Generate training data from tool call history.
        
        Args:
            calls: List of {"tool": name, "args": {...}, "result": ...}
        
        Returns:
            List of training examples
        """
        examples = []
        
        for call in calls:
            tool_name = call.get("tool")
            if tool_name in self.tools:
                tool = self.tools[tool_name]
                example = tool.generate_training_example(
                    call.get("args", {}),
                    call.get("result")
                )
                examples.append(example)
        
        return examples


# Global registry
TOOL_REGISTRY = ToolRegistry()


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry."""
    return TOOL_REGISTRY


def get_tools_schema(format: str = "openai", category: Optional[str] = None) -> List[Dict]:
    """
    Get tool schemas in specified format.
    
    Args:
        format: 'openai' or 'anthropic'
        category: Optional category filter
    
    Returns:
        List of tool schemas
    """
    if format == "openai":
        return TOOL_REGISTRY.to_openai_tools(category)
    elif format == "anthropic":
        return TOOL_REGISTRY.to_anthropic_tools(category)
    else:
        raise ValueError(f"Unknown format: {format}")
