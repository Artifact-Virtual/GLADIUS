"""
LLM Abstraction Subsystem - Enterprise-Grade LLM Management

This subsystem provides a comprehensive, secure, and extensible interface
for integrating, orchestrating, and optimizing large language models within
enterprise workflows.

Key Components:
- Core LLM provider abstractions and orchestration
- Advanced prompt engineering and context optimization
- Probabilistic output ranking and quality assessment
- Comprehensive security validation and compliance
- Multi-threaded agent system with workflow management
- Flexible configuration management
"""

# Core abstractions and orchestration
from llm_abstraction.llm_abstraction import (
    LLMProviderBase,
    LLMOrchestrator,
    PromptEngineer,
    ContextManager,
    OutputProcessor,
    OpenAIProvider,
    AnthropicProvider,
    OllamaProvider,
    LLMRequest,
    LLMResponse,
    ProviderType,
    SecurityLevel
)

# Security and compliance
from llm_abstraction.security import (
    SecurityValidator,
    SecurityContext,
    SecurityEvent,
    EncryptionManager,
    ComplianceManager
)

# Configuration management
from llm_abstraction.config_manager import (
    ConfigManager,
    ProviderConfig,
    SecurityConfig,
    OrchestrationConfig,
    EnvironmentManager,
    create_sample_config
)

# Agent system and workflows
from llm_abstraction.agents.llm_agent import (
    LLMOrchestrationAgent,
    Task,
    Workflow,
    WorkflowBuilder,
    WorkflowTemplates,
    AgentStatus,
    WorkflowStatus,
    AgentCallback,
    DefaultAgentCallback,
    TaskScheduler,
    SecurityError
)

# Advanced algorithms
from llm_abstraction.algorithms.context_window_optimization import (
    ContextOptimizer,
    optimize_context_window
)

from llm_abstraction.algorithms.output_ranking import (
    ProbabilisticRanker,
    OutputMetrics,
    rank_outputs,
    rank_outputs_weighted
)

# MCP (Model Context Protocol) integration
try:
    from llm_abstraction.mcp import (
        ComprehensiveMCPClient,
        MCPLLMIntegrator,
        MCPEnhancedLLMAbstraction,
        MCPContext,
        MCPToolCall,
        create_mcp_client,
        is_server_available
    )
    mcp_available = True
except ImportError:
    mcp_available = False
    # Define placeholder classes
    ComprehensiveMCPClient = None
    MCPLLMIntegrator = None
    MCPEnhancedLLMAbstraction = None
    MCPContext = None
    MCPToolCall = None
    create_mcp_client = None
    
    def is_server_available():
        return False

__version__ = "1.0.0"
__author__ = "Enterprise Nerve Centre Team"
__description__ = "Enterprise-grade LLM abstraction and orchestration"

# Package metadata
__all__ = [
    # Core classes
    "LLMProviderBase",
    "LLMOrchestrator", 
    "PromptEngineer",
    "ContextManager",
    "OutputProcessor",
    "OpenAIProvider",
    "AnthropicProvider",
    "OllamaProvider",
    
    # Data structures
    "LLMRequest",
    "LLMResponse",
    "ProviderType",
    "SecurityLevel",
    
    # Security
    "SecurityValidator",
    "SecurityContext", 
    "SecurityEvent",
    "EncryptionManager",
    "ComplianceManager",
    
    # Configuration
    "ConfigManager",
    "ProviderConfig",
    "SecurityConfig", 
    "OrchestrationConfig",
    "EnvironmentManager",
    "create_sample_config",
    
    # Agents and workflows
    "LLMOrchestrationAgent",
    "Task",
    "Workflow",
    "WorkflowBuilder",
    "WorkflowTemplates",
    "AgentStatus",
    "WorkflowStatus",
    "AgentCallback",
    "DefaultAgentCallback",
    "TaskScheduler",
    "SecurityError",
    
    # Algorithms
    "ContextOptimizer",
    "optimize_context_window",
    "ProbabilisticRanker",
    "OutputMetrics",
    "rank_outputs",
    "rank_outputs_weighted",
    
    # MCP (Model Context Protocol)
    "ComprehensiveMCPClient",
    "MCPLLMIntegrator",
    "MCPEnhancedLLMAbstraction",
    "MCPContext",
    "MCPToolCall",
    "create_mcp_client",
    "is_server_available",
    "mcp_available"
]


def is_mcp_available() -> bool:
    """Check if MCP components are available"""
    return mcp_available
