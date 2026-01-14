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
    
    # Charting Tools
    ToolDefinition(
        name="generate_chart",
        description="Generate an enhanced technical chart with indicators (RSI, ADX, ATR), support/resistance levels, trendlines, and trade setups.",
        category="charting",
        parameters=[
            ToolParameter("symbol", "string", "Asset symbol (e.g., XAUUSD, SPY)"),
            ToolParameter("timeframe", "string", "Chart timeframe", required=False, default="1D"),
            ToolParameter("show_indicators", "boolean", "Show RSI/ADX subplots", required=False, default=True),
            ToolParameter("show_levels", "boolean", "Show S/R levels", required=False, default=True),
            ToolParameter("show_trade_setup", "boolean", "Show trade setup zones", required=False, default=True),
        ],
        examples=[
            {"args": {"symbol": "XAUUSD", "timeframe": "1D"}, "result": {"chart_path": "output/charts/XAUUSD_1D.png", "rsi": 58.2, "adx": 32.1}},
            {"args": {"symbol": "SPY", "show_trade_setup": True}, "result": {"chart_path": "output/charts/SPY_1D.png", "regime": "TRENDING"}},
        ]
    ),
    
    ToolDefinition(
        name="detect_support_resistance",
        description="Detect horizontal support and resistance levels from price data using swing point analysis.",
        category="charting",
        parameters=[
            ToolParameter("symbol", "string", "Asset symbol"),
            ToolParameter("window", "integer", "Swing detection window size", required=False, default=10),
            ToolParameter("num_levels", "integer", "Number of levels to return", required=False, default=3),
        ],
        examples=[
            {"args": {"symbol": "XAUUSD"}, "result": {"support": [2650.0, 2680.5], "resistance": [2710.0, 2745.0]}},
        ]
    ),
    
    ToolDefinition(
        name="detect_trendlines",
        description="Detect trendlines using RANSAC algorithm on swing highs and lows.",
        category="charting",
        parameters=[
            ToolParameter("symbol", "string", "Asset symbol"),
            ToolParameter("max_lines", "integer", "Maximum trendlines to detect", required=False, default=2),
        ],
        examples=[
            {"args": {"symbol": "XAUUSD"}, "result": {"support_lines": [{"angle": 12.5, "price": 2680}], "resistance_lines": [{"angle": -5.2, "price": 2720}]}},
        ]
    ),
    
    ToolDefinition(
        name="calculate_indicators",
        description="Calculate technical indicators (RSI, ADX, ATR, SMAs) for a symbol.",
        category="charting",
        parameters=[
            ToolParameter("symbol", "string", "Asset symbol"),
            ToolParameter("indicators", "array", "List of indicators to calculate", required=False, default=["RSI", "ADX_14", "ATR", "SMA_50", "SMA_200"]),
        ],
        examples=[
            {"args": {"symbol": "XAUUSD"}, "result": {"RSI": 58.2, "ADX_14": 32.1, "ATR": 28.5, "regime": "TRENDING"}},
        ]
    ),
    
    ToolDefinition(
        name="determine_regime",
        description="Determine market regime (TRENDING, RANGING, VOLATILE) based on ADX and ATR values.",
        category="charting",
        parameters=[
            ToolParameter("symbol", "string", "Asset symbol"),
        ],
        examples=[
            {"args": {"symbol": "XAUUSD"}, "result": {"regime": "TRENDING", "adx": 32.1, "atr_pct": 1.2}},
        ]
    ),
    
    ToolDefinition(
        name="annotate_chart",
        description="Add custom annotations to a chart: levels, trendlines, zones, labels.",
        category="charting",
        parameters=[
            ToolParameter("chart_path", "string", "Path to existing chart"),
            ToolParameter("annotations", "object", "Annotations to add (support_levels, resistance_levels, labels)"),
        ],
        examples=[
            {"args": {"chart_path": "output/charts/XAUUSD.png", "annotations": {"support_levels": [2680], "labels": [{"x": 10, "y": 2700, "text": "Key resistance"}]}}, "result": {"updated_path": "output/charts/XAUUSD_annotated.png"}},
        ]
    ),
    
    ToolDefinition(
        name="create_trade_setup",
        description="Create a trade setup with entry, stop loss, and take profit levels.",
        category="charting",
        parameters=[
            ToolParameter("symbol", "string", "Asset symbol"),
            ToolParameter("bias", "string", "Trade direction: LONG or SHORT", enum=["LONG", "SHORT"]),
            ToolParameter("entry", "float", "Entry price"),
            ToolParameter("stop_loss", "float", "Stop loss price"),
            ToolParameter("target_1", "float", "First take profit target"),
            ToolParameter("target_2", "float", "Second take profit target", required=False),
        ],
        examples=[
            {"args": {"symbol": "XAUUSD", "bias": "LONG", "entry": 2685, "stop_loss": 2670, "target_1": 2710}, "result": {"setup_id": "ts_001", "risk_reward": 1.67}},
        ]
    ),
    
    # Publishing/Social Media Tools
    ToolDefinition(
        name="create_content",
        description="Generate content from analysis, journals, or raw data. Formats for social media or website publication.",
        category="publishing",
        parameters=[
            ToolParameter("source_type", "string", "Type of source: journal, analysis, catalyst, raw", enum=["journal", "analysis", "catalyst", "raw"]),
            ToolParameter("source_path", "string", "Path to source file or data", required=False),
            ToolParameter("content_type", "string", "Output format: post, thread, article, summary", enum=["post", "thread", "article", "summary"], required=False, default="post"),
            ToolParameter("tone", "string", "Content tone: professional, casual, educational", required=False, default="professional"),
        ],
        examples=[
            {"args": {"source_type": "journal", "source_path": "output/Journal_2026-01-13.md", "content_type": "post"}, "result": {"content_id": "cnt_001", "text": "Gold approaching key resistance...", "char_count": 280}},
        ]
    ),
    
    ToolDefinition(
        name="schedule_post",
        description="Schedule content for publishing at optimal time. Uses engagement analytics to determine best posting windows.",
        category="publishing",
        parameters=[
            ToolParameter("content_id", "string", "ID of content to schedule"),
            ToolParameter("platforms", "array", "Target platforms: discord, twitter, linkedin, notion"),
            ToolParameter("schedule_time", "string", "ISO datetime or 'optimal' for auto-scheduling", required=False, default="optimal"),
        ],
        examples=[
            {"args": {"content_id": "cnt_001", "platforms": ["discord", "twitter"], "schedule_time": "optimal"}, "result": {"scheduled_at": "2026-01-14T14:00:00Z", "platforms": ["discord", "twitter"]}},
        ]
    ),
    
    ToolDefinition(
        name="publish_content",
        description="Immediately publish content to specified platforms. Handles formatting per platform.",
        category="publishing",
        parameters=[
            ToolParameter("content", "string", "Raw content to publish"),
            ToolParameter("title", "string", "Content title", required=False),
            ToolParameter("platforms", "array", "Target platforms", required=False, default=["discord"]),
        ],
        examples=[
            {"args": {"content": "# Gold Update\n\nBullish momentum confirmed...", "title": "Gold Update", "platforms": ["discord"]}, "result": {"published": True, "urls": {"discord": "..."}}},
        ]
    ),
    
    ToolDefinition(
        name="get_engagement",
        description="Fetch engagement metrics from social platforms. Track likes, shares, comments, views.",
        category="analytics",
        parameters=[
            ToolParameter("platform", "string", "Platform to check: discord, twitter, linkedin"),
            ToolParameter("post_id", "string", "Specific post ID to check", required=False),
            ToolParameter("time_range", "string", "Time range: 24h, 7d, 30d", required=False, default="7d"),
        ],
        examples=[
            {"args": {"platform": "twitter", "time_range": "7d"}, "result": {"impressions": 1250, "engagements": 87, "engagement_rate": 6.9}},
        ]
    ),
    
    ToolDefinition(
        name="contextualize_content",
        description="Add market context to content. Enriches with current prices, trends, and relevant data.",
        category="reasoning",
        parameters=[
            ToolParameter("content", "string", "Raw content to contextualize"),
            ToolParameter("context_type", "string", "Type of context: market, technical, sentiment", enum=["market", "technical", "sentiment", "full"]),
            ToolParameter("symbols", "array", "Symbols to include context for", required=False, default=["XAUUSD"]),
        ],
        examples=[
            {"args": {"content": "Gold showing strength", "context_type": "market", "symbols": ["XAUUSD"]}, "result": {"contextualized": "Gold ($2,695) showing strength with RSI at 58.2 and ADX confirming trend..."}},
        ]
    ),
    
    ToolDefinition(
        name="reason_about_audience",
        description="Determine target audience and appropriate tone for content. Uses platform analytics and content type.",
        category="reasoning",
        parameters=[
            ToolParameter("content", "string", "Content to analyze"),
            ToolParameter("platform", "string", "Target platform"),
        ],
        examples=[
            {"args": {"content": "Technical analysis of gold...", "platform": "linkedin"}, "result": {"audience": "professional traders", "tone": "educational", "hashtags": ["#gold", "#trading", "#markets"]}},
        ]
    ),
    
    ToolDefinition(
        name="think_about_timing",
        description="Determine optimal posting time based on audience activity, market hours, and historical engagement.",
        category="reasoning",
        parameters=[
            ToolParameter("content_type", "string", "Type of content: alert, analysis, journal"),
            ToolParameter("platforms", "array", "Target platforms"),
            ToolParameter("timezone", "string", "User timezone", required=False, default="UTC"),
        ],
        examples=[
            {"args": {"content_type": "analysis", "platforms": ["twitter", "linkedin"]}, "result": {"optimal_time": "2026-01-14T14:00:00Z", "reasoning": "Peak engagement for trading content during US market hours"}},
        ]
    ),
    
    ToolDefinition(
        name="engage_with_reply",
        description="Generate contextual reply for engagement. Maintains brand voice while being helpful.",
        category="engagement",
        parameters=[
            ToolParameter("platform", "string", "Platform: discord, twitter, linkedin"),
            ToolParameter("original_message", "string", "Message to reply to"),
            ToolParameter("context", "string", "Additional context for reply", required=False),
            ToolParameter("tone", "string", "Reply tone: helpful, professional, casual", required=False, default="helpful"),
        ],
        examples=[
            {"args": {"platform": "discord", "original_message": "What's your view on gold?", "tone": "helpful"}, "result": {"reply": "Gold is showing bullish momentum above 2680 support. Key resistance at 2710. See today's journal for full analysis."}},
        ]
    ),
    
    # ERP Integration Tools
    ToolDefinition(
        name="erp_sync_customers",
        description="Sync customer data from connected ERP system (SAP, Odoo, NetSuite, Dynamics, Salesforce).",
        category="erp",
        parameters=[
            ToolParameter("system", "string", "ERP system: SAP, Odoo, NetSuite, Dynamics, Salesforce"),
            ToolParameter("limit", "integer", "Maximum records to sync", required=False, default=1000),
        ],
        examples=[
            {"args": {"system": "SAP"}, "result": {"success": True, "count": 150, "customers": "[...]"}},
            {"args": {"system": "Odoo", "limit": 500}, "result": {"success": True, "count": 312}},
        ]
    ),
    
    ToolDefinition(
        name="erp_sync_products",
        description="Sync product/service catalog from connected ERP system.",
        category="erp",
        parameters=[
            ToolParameter("system", "string", "ERP system: SAP, Odoo, NetSuite, Dynamics, Salesforce"),
            ToolParameter("limit", "integer", "Maximum records to sync", required=False, default=1000),
        ],
        examples=[
            {"args": {"system": "NetSuite"}, "result": {"success": True, "count": 450, "products": "[...]"}},
        ]
    ),
    
    ToolDefinition(
        name="erp_sync_orders",
        description="Sync sales orders/transactions from connected ERP system.",
        category="erp",
        parameters=[
            ToolParameter("system", "string", "ERP system: SAP, Odoo, NetSuite, Dynamics, Salesforce"),
            ToolParameter("date_from", "string", "Start date for order sync (ISO format)", required=False),
            ToolParameter("limit", "integer", "Maximum records to sync", required=False, default=1000),
        ],
        examples=[
            {"args": {"system": "Salesforce", "date_from": "2026-01-01"}, "result": {"success": True, "count": 85, "orders": "[...]"}},
        ]
    ),
    
    ToolDefinition(
        name="erp_sync_inventory",
        description="Sync inventory/stock levels from connected ERP system.",
        category="erp",
        parameters=[
            ToolParameter("system", "string", "ERP system: SAP, Odoo, NetSuite, Dynamics, Salesforce"),
            ToolParameter("warehouse", "string", "Specific warehouse to sync", required=False),
        ],
        examples=[
            {"args": {"system": "SAP", "warehouse": "WH001"}, "result": {"success": True, "count": 1200, "inventory": "[...]"}},
        ]
    ),
    
    ToolDefinition(
        name="erp_get_status",
        description="Get connection status and sync statistics for all connected ERP systems.",
        category="erp",
        parameters=[],
        examples=[
            {"args": {}, "result": {"SAP": {"connected": True, "last_sync": "2026-01-14T10:00:00Z"}, "Odoo": {"connected": False}}},
        ]
    ),
    
    ToolDefinition(
        name="erp_create_customer",
        description="Create a new customer record in the connected ERP system.",
        category="erp",
        parameters=[
            ToolParameter("system", "string", "ERP system: SAP, Odoo, NetSuite, Dynamics, Salesforce"),
            ToolParameter("name", "string", "Customer name"),
            ToolParameter("email", "string", "Customer email", required=False),
            ToolParameter("phone", "string", "Customer phone", required=False),
            ToolParameter("address", "object", "Customer address object", required=False),
        ],
        examples=[
            {"args": {"system": "Salesforce", "name": "Acme Corp", "email": "contact@acme.com"}, "result": {"success": True, "customer_id": "CUST-001234"}},
        ]
    ),
    
    ToolDefinition(
        name="erp_create_order",
        description="Create a new sales order in the connected ERP system.",
        category="erp",
        parameters=[
            ToolParameter("system", "string", "ERP system: SAP, Odoo, NetSuite, Dynamics, Salesforce"),
            ToolParameter("customer_id", "string", "Customer identifier"),
            ToolParameter("items", "array", "Order line items [{product_id, quantity, price}]"),
            ToolParameter("notes", "string", "Order notes", required=False),
        ],
        examples=[
            {"args": {"system": "NetSuite", "customer_id": "CUST-001", "items": [{"product_id": "PROD-001", "quantity": 5, "price": 100}]}, "result": {"success": True, "order_id": "SO-2026-0001"}},
        ]
    ),
    
    ToolDefinition(
        name="erp_update_inventory",
        description="Update inventory levels for a product in the connected ERP system.",
        category="erp",
        parameters=[
            ToolParameter("system", "string", "ERP system: SAP, Odoo, NetSuite, Dynamics, Salesforce"),
            ToolParameter("product_id", "string", "Product identifier"),
            ToolParameter("quantity", "integer", "New quantity"),
            ToolParameter("warehouse", "string", "Warehouse location", required=False),
        ],
        examples=[
            {"args": {"system": "Odoo", "product_id": "PROD-001", "quantity": 500}, "result": {"success": True, "updated": True, "previous_qty": 450}},
        ]
    ),
    
    # Consensus/Governance Tools
    ToolDefinition(
        name="create_proposal",
        description="Create a new improvement proposal for consensus voting.",
        category="governance",
        parameters=[
            ToolParameter("title", "string", "Proposal title"),
            ToolParameter("summary", "string", "Proposal summary"),
            ToolParameter("impact_level", "string", "Impact level: low, medium, high, critical", enum=["low", "medium", "high", "critical"]),
            ToolParameter("category", "string", "Proposal category: accuracy, performance, architecture, documentation", required=False),
        ],
        examples=[
            {"args": {"title": "Improve prediction accuracy", "summary": "Enhance pattern recognition", "impact_level": "medium"}, "result": {"proposal_id": "prop_001", "status": "pending_review"}},
        ]
    ),
    
    ToolDefinition(
        name="route_proposal",
        description="Route a proposal through the consensus system based on impact level.",
        category="governance",
        parameters=[
            ToolParameter("proposal_id", "string", "Proposal ID to route"),
        ],
        examples=[
            {"args": {"proposal_id": "prop_001"}, "result": {"action": "community_vote", "discord_sent": True, "session_id": "session_001"}},
        ]
    ),
    
    ToolDefinition(
        name="get_voting_status",
        description="Get current voting status for open proposals.",
        category="governance",
        parameters=[
            ToolParameter("session_id", "string", "Voting session ID", required=False),
        ],
        examples=[
            {"args": {}, "result": {"open_sessions": 2, "sessions": [{"id": "session_001", "title": "...", "votes": {"approve": 3, "reject": 1}}]}},
        ]
    ),
    
    # Email Tools
    ToolDefinition(
        name="send_escalation_email",
        description="Send an escalation email to dev team or executives for high-impact proposals.",
        category="communication",
        parameters=[
            ToolParameter("subject", "string", "Email subject"),
            ToolParameter("body", "string", "Email body (HTML supported)"),
            ToolParameter("escalation_level", "string", "Level: senior_review, executive", enum=["senior_review", "executive"]),
        ],
        examples=[
            {"args": {"subject": "URGENT: Architecture Change Proposal", "body": "...", "escalation_level": "senior_review"}, "result": {"sent": True, "recipients": 2}},
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
