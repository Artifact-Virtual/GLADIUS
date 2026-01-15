# LEGION System Mapping

> Module: `/LEGION/`
> Last Updated: 2026-01-14
> Purpose: Distributed Multi-Agent Enterprise Ecosystem

---

## Overview

LEGION is a **distributed multi-agent ecosystem** that orchestrates complex business workflows through intelligent automation. It features:
- **26 specialized AI agents** across 7 business domains
- Real-time data processing and WebSocket connections
- Self-healing architecture with 99.9% uptime
- **Full integration with Artifact Virtual infrastructure via ArtifactBridge**

---

## Integration with Artifact

LEGION uses the **ArtifactBridge** to route all external operations through Artifact's native infrastructure:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        LEGION AGENTS                                     │
├─────────────────────────────────────────────────────────────────────────┤
│  CRM Agent │ Marketing Agent │ ERP Agent │ Social Media Agent │ ...    │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │    ARTIFACT BRIDGE     │
              │  (legion/artifact_     │
              │    bridge.py)          │
              └────────────┬───────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   GLADIUS    │  │   SOCIAL     │  │     ERP      │
│   (Native    │  │   MEDIA      │  │ INTEGRATIONS │
│    AI)       │  │  CONNECTORS  │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Using the Bridge

```python
from legion.artifact_bridge import get_bridge, post_social, sync_erp, query_ai

# Query GLADIUS for AI operations
result = await query_ai("Analyze this market data")

# Post to social media via Artifact connectors
result = await post_social("twitter", "New market analysis available!")

# Sync with ERP
result = await sync_erp("customers", {"name": "Acme Corp", "status": "active"})
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        LEGION ENTERPRISE                                 │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  Financial  │  │  Operations │  │Intelligence │  │Communication│   │
│  │   Domain    │  │   Domain    │  │   Domain    │  │   Domain    │   │
│  │  3 agents   │  │  4 agents   │  │  6 agents   │  │  3 agents   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                     │
│  │ Integration │  │ Compliance  │  │  Customer   │                     │
│  │   Domain    │  │   Domain    │  │   Domain    │                     │
│  │  5 agents   │  │  2 agents   │  │  2 agents   │                     │
│  └─────────────┘  └─────────────┘  └─────────────┘                     │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    CORE ORCHESTRATION LAYER                      │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │   Master     │  │   Agent      │  │   Message    │          │   │
│  │  │ Orchestrator │  │  Registry    │  │     Bus      │          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Integration Test Results (2026-01-14)

```
1️⃣  LEGION CLI Commands       ✅ system status, agent list
2️⃣  Artifact Bridge           ✅ 9 integrations available
3️⃣  GLADIUS Routing           ✅ 80% confidence, search tool
4️⃣  Social Media Bridge       ✅ 5 API platforms available
5️⃣  Agent Registry            ✅ 26 agents defined
6️⃣  Message Bus               ✅ Messaging functional
```

### Running Tests

```bash
cd /home/adam/worxpace/gladius
python3 LEGION/tests/test_legion_integration.py
```

---

## Components

| File | Class | Purpose | Status |
|------|-------|---------|--------|
| `legion/cli.py` | CLI | Command-line interface | ✅ Production |
| `legion/artifact_bridge.py` | `ArtifactBridge` | **Artifact integration** | ✅ NEW |
| `communication/social_bridge.py` | `SocialMediaBridge` | **Unified social media** | ✅ NEW |
| `legion/core_framework.py` | `AgentFramework` | Base agent architecture | ✅ Production |
| `legion/enhanced_orchestrator.py` | `EnhancedOrchestrator` | Agent coordination | ✅ Production |
| `legion/enterprise_registry.py` | `EnterpriseRegistry` | Agent registration | ✅ Production |
| `legion/message_bus.py` | `MessageBus` | Inter-agent messaging | ✅ Production |
| `legion/agent_memory.py` | `AgentMemory` | Memory persistence | ✅ Production |
| `legion/distributed_tracing.py` | `DistributedTracing` | Performance tracking | ✅ Production |
| `legion/self_improvement.py` | `SelfImprovement` | Auto-optimization | ✅ Production |
| `legion/continuous_operation.py` | `ContinuousOperation` | 24/7 operation mode | ✅ Production |

---

## Agent Ecosystem (26 Agents)

### Financial Intelligence Domain (3 agents)
| Agent | Function | Status |
|-------|----------|--------|
| `FinancialAnalysisAgent` | Financial data processing and analysis | ✅ |
| `FinancialModelingAgent` | Financial forecasting and modeling | ✅ |
| `ForecastingAgent` | Predictive analytics and forecasting | ✅ |

### Operations Domain (4 agents)
| Agent | Function | Status |
|-------|----------|--------|
| `TaskSchedulingAgent` | Task automation and scheduling | ✅ |
| `WorkflowOrchestrationAgent` | Cross-department workflow coordination | ✅ |
| `ResourceOptimizationAgent` | System resource allocation optimization | ✅ |
| `QualityAssuranceAgent` | Quality control and compliance monitoring | ✅ |

### Business Intelligence Domain (6 agents)
| Agent | Function | Status |
|-------|----------|--------|
| `ComprehensiveAnalyticsAgent` | Business intelligence and reporting | ✅ |
| `AnalyticsAgent` | Core analytics processing | ✅ |
| `MarketAnalysisAgent` | Market research and competitive analysis | ✅ |
| `ResearchAgent` | Research coordination and data gathering | ✅ |
| `StrategicPlanningAgent` | Strategic planning and decision support | ✅ |
| `AnomalyDetectionAgent` | System anomaly detection and alerting | ✅ |

### Communication Domain (3 agents)
| Agent | Function | Status |
|-------|----------|--------|
| `ContentWritingAgent` | AI-powered content generation | ✅ |
| `SocialMediaMonitoringAgent` | Social media automation and monitoring | ✅ |
| `CalendarManagementAgent` | Calendar and meeting management | ✅ |

### Integration Domain (5 agents)
| Agent | Function | Status |
|-------|----------|--------|
| `ExternalSystemsIntegrationAgent` | API integration and data sync | ✅ |
| `EnhancedExternalSystemsAgent` | Advanced integration capabilities | ✅ |
| `CloudIntegrationAgent` | Cloud services integration | ✅ |
| `CrmIntegrationAgent` | CRM system integration | ✅ |
| `ErpIntegrationAgent` | ERP system integration | ✅ |

### Legal & Compliance Domain (2 agents)
| Agent | Function | Status |
|-------|----------|--------|
| `ComplianceCheckerAgent` | Regulatory compliance and audit | ✅ |
| `ReportGenerationAgent` | Automated report generation | ✅ |

### Customer Intelligence Domain (2 agents)
| Agent | Function | Status |
|-------|----------|--------|
| `CustomerInsightsAgent` | Customer behavior analysis | ✅ |
| `SupplyChainAgent` | Supply chain optimization | ✅ |

---

## CLI Commands (8 categories)

### System Commands
```bash
# Display system status
python cli.py system status

# Check component health
python cli.py system health
```

### Agent Commands
```bash
# List all agents
python cli.py agent list

# Get agent status
python cli.py agent status <agent_id>
```

### Message Commands
```bash
# Send message to agent
python cli.py message send --to <agent_id> --content "<message>" [--priority <1-10>]

# View message bus statistics
python cli.py message stats
```

### Memory Commands
```bash
# Query agent memory
python cli.py memory query <agent_id> <type> [--limit N]

# Search memories
python cli.py memory search <agent_id> "<query>" [--limit N]
```

### Trace Commands
```bash
# List traces
python cli.py trace list [--limit N]

# Get trace details
python cli.py trace get <trace_id>

# View trace statistics
python cli.py trace stats
```

### Improvement Commands
```bash
# View improvement insights
python cli.py improvement insights [--limit N]

# Get improvement suggestions
python cli.py improvement suggest [--agent <agent_id>]

# Execute improvement action
python cli.py improvement apply <suggestion_id>
```

### Operation Commands
```bash
# Start continuous operation mode
python cli.py operation start

# Stop continuous operation
python cli.py operation stop

# View operation status
python cli.py operation status
```

### Config Commands
```bash
# View configuration
python cli.py config show [--section <section>]

# Update configuration
python cli.py config set <key> <value>
```

---

## Integration with Gladius

### Mapping LEGION Agents to Gladius Tools

| Gladius Tool | LEGION Agent | Usage |
|--------------|--------------|-------|
| `financial_analysis` | `FinancialAnalysisAgent` | Analyze financial data |
| `market_research` | `MarketAnalysisAgent` | Market intelligence |
| `content_create` | `ContentWritingAgent` | Generate content |
| `social_post` | `SocialMediaMonitoringAgent` | Social media automation |
| `compliance_check` | `ComplianceCheckerAgent` | Regulatory compliance |
| `erp_sync` | `ErpIntegrationAgent` | ERP synchronization |
| `crm_sync` | `CrmIntegrationAgent` | CRM synchronization |
| `anomaly_detect` | `AnomalyDetectionAgent` | System anomalies |

### Tool Registry Integration

```python
# In cognition/tool_calling.py

ToolDefinition(
    name="legion_agent_query",
    description="Query a LEGION agent for specific task execution",
    category="agents",
    parameters=[
        ToolParameter("agent_id", "string", "Agent to query"),
        ToolParameter("task", "string", "Task description"),
        ToolParameter("priority", "integer", "Priority 1-10", required=False, default=5),
    ],
    examples=[
        {"args": {"agent_id": "financial_agent", "task": "Analyze Q4 revenue"}, 
         "result": {"status": "completed", "analysis": "..."}},
    ]
),
```

---

## Databases

| Database | Location | Purpose |
|----------|----------|---------|
| CRM | `data/crm.db` | Customer relationship management |
| Projects | `data/projects.db` | Project and task tracking |
| Enterprise Operations | `enterprise_operations.db` | Business metrics |
| Agent Communications | `logs/agent_communications.db` | Inter-agent messages |

---

## Dashboard Components

LEGION provides 7 React dashboard views:

1. **Command Dashboard** - System command center
2. **Operations Dashboard** - Business operations
3. **Intelligence Dashboard** - Business analytics
4. **Coordination Dashboard** - Cross-department integration
5. **Management Dashboard** - Executive overview
6. **Optimization Dashboard** - Performance enhancement
7. **API Monitoring Dashboard** - Integration health

---

## Overlap Resolution with Artifact

### Potential Conflicts

| Feature | LEGION | Artifact Current | Resolution |
|---------|--------|------------------|------------|
| ERP Integration | `ErpIntegrationAgent` | `erp_integrations/` | Use LEGION agent, Artifact connectors |
| Social Media | `SocialMediaMonitoringAgent` | `social_media/` | Merge capabilities |
| Scheduling | `TaskSchedulingAgent` | `scheduler/` | LEGION orchestrates, Artifact executes |
| Analytics | `ComprehensiveAnalyticsAgent` | Syndicate reports | Feed into LEGION |

### Integration Strategy

1. **LEGION as Orchestrator**: LEGION agents coordinate high-level tasks
2. **Artifact as Executor**: Artifact modules execute specific operations
3. **Gladius as Brain**: Native model makes decisions via tool calls
4. **SENTINEL as Guardian**: Monitors security and process health

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LEGION_ENABLED` | Enable LEGION system | `true` |
| `LEGION_AGENTS_ACTIVE` | Number of active agents | `26` |
| `LEGION_DB_PATH` | Database directory | `./data` |
| `LEGION_LOG_LEVEL` | Logging level | `INFO` |
| `LEGION_WEBSOCKET_PORT` | WebSocket server port | `8765` |
| `LEGION_API_PORT` | REST API port | `8000` |

---

## Quick Start

```bash
cd /home/adam/worxpace/gladius/LEGION

# Install dependencies
pip install -r requirements.txt

# Start LEGION
python start_enterprise.py

# Or use the CLI
python legion/cli.py system status
```

---

## CLI Quick Reference

```bash
# System
legion system status|health

# Agents
legion agent list|status

# Messages
legion message send|stats

# Memory
legion memory query|search

# Traces
legion trace list|get|stats

# Improvement
legion improvement insights|suggest|apply

# Operation
legion operation start|stop|status

# Config
legion config show|set
```

---

*Generated by Gladius System Mapper*
