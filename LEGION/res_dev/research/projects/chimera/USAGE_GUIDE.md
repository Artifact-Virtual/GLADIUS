# Chimera Program 

## Enterprise Legion

### Introduction
The Chimera program is a sophisticated AI agent orchestration system designed to automate and optimize enterprise operations. It leverages a modular framework called **Enterprise Legion**, which consists of specialized agents across various departments, each designed to perform specific tasks and collaborate seamlessly.

# Chimera Usage Guide

This guide explains how to run the Chimera program and interact with its agents, including the new Enterprise Legion framework - the world's most advanced modular enterprise AI agent system.

## Table of Contents

1. [Enterprise Legion Agent Framework](#enterprise-legion-agent-framework)
2. [Quick Start - Enterprise Legion](#quick-start---enterprise-legion)
3. [Department Overview](#department-overview)
4. [Agent Interactions](#agent-interactions)
5. [API Reference](#api-reference)
6. [Legacy Chimera Usage](#legacy-chimera-usage)

## Enterprise Legion Agent Framework

The Enterprise Legion framework represents a revolutionary approach to enterprise AI automation. It consists of mathematically co-integrated agents across six core departments:

### Core Departments:
- **Accounts, Finance & Reporting** - Financial analysis, modeling, reporting, and quality assurance
- **Automation & Operations** - Workflow orchestration, resource optimization, and task scheduling
- **Business Intelligence & Strategy** - Market analysis, competitive intelligence, and strategic planning
- **Communication & Marketing** - Content creation, social media monitoring, and customer engagement
- **Legal & Compliance** - Compliance checking, legal document processing, and security auditing
- **Organizational Structure** - Calendar management, meeting coordination, and organizational optimization

## Quick Start - Enterprise Legion

### 1. Initialize the Enterprise Legion System

```python
from modules.llm_abstraction.agents.legion.enterprise.enterprise_registry import (
    initialize_enterprise_legion, 
    get_system_status,
    send_system_message
)

# Initialize the complete Enterprise Legion system
registry = await initialize_enterprise_legion()

# Check system status
status = await get_system_status()
print(f"System Status: {status['system_status']}")
print(f"Operational Agents: {status['operational_agents']}/{status['total_agents']}")
```

### 2. Basic Agent Interaction

```python
# Send a financial analysis request
await send_system_message(
    message_type="financial_analysis_request",
    content={
        "data": {
            "revenue": 1000000,
            "expenses": 750000,
            "period": "Q1_2024"
        }
    },
    target_agents=["financial_analysis_agent"]
)

# Request a market analysis report
await send_system_message(
    message_type="market_analysis_request", 
    content={
        "market_segment": "enterprise_software",
        "time_period": "last_quarter",
        "include_competitors": True
    },
    target_agents=["market_analysis_agent"]
)
```

### 3. Generate Comprehensive Reports

```python
# Request executive summary report
await send_system_message(
    message_type="report_request",
    content={
        "report_type": "executive_summary",
        "recipients": ["ceo", "board_members"],
        "time_period": "monthly"
    },
    target_agents=["report_generation_agent"]
)
```

## Department Overview

### Accounts, Finance & Reporting Department

#### Financial Analysis Agent
- **Purpose**: Analyze financial statements, transactions, and performance metrics
- **Key Functions**: 
  - Real-time financial data processing
  - Ratio analysis and trend identification
  - Budget variance analysis
  - Financial health scoring

```python
# Example: Request financial analysis
financial_data = {
    "transactions": [...],
    "budget_data": {...},
    "time_period": "current_month"
}

await send_system_message(
    message_type="financial_data_update",
    content=financial_data,
    target_agents=["financial_analysis_agent"]
)
```

#### Financial Modeling Agent
- **Purpose**: Build predictive financial models and scenario planning
- **Key Functions**:
  - DCF modeling and valuation
  - Monte Carlo simulations
  - Scenario analysis
  - Cash flow projections

```python
# Example: Request financial projections
await send_system_message(
    message_type="projection_request",
    content={
        "type": "cash_flow",
        "time_horizon": 12,
        "scenarios": ["optimistic", "base_case", "pessimistic"]
    },
    target_agents=["financial_modeling_agent"]
)
```

#### Report Generation Agent
- **Purpose**: Create comprehensive reports across all departments
- **Key Functions**:
  - Automated report generation
  - Cross-departmental data aggregation
  - Executive dashboards
  - Scheduled reporting

```python
# Example: Generate custom report
await send_system_message(
    message_type="report_request",
    content={
        "report_type": "financial_summary",
        "sections": ["revenue_analysis", "cost_analysis", "projections"],
        "format": "executive_summary"
    },
    target_agents=["report_generation_agent"]
)
```

### Automation & Operations Department

#### Workflow Orchestration Agent
- **Purpose**: Coordinate complex multi-agent workflows
- **Key Functions**:
  - Process automation
  - Task dependency management
  - Workflow optimization
  - Performance monitoring

```python
# Example: Execute complex workflow
workflow_config = {
    "workflow_name": "monthly_financial_close",
    "steps": [
        {"agent": "financial_analysis_agent", "task": "process_transactions"},
        {"agent": "quality_assurance_agent", "task": "validate_data"},
        {"agent": "report_generation_agent", "task": "generate_monthly_report"}
    ]
}

await send_system_message(
    message_type="workflow_execution_request",
    content=workflow_config,
    target_agents=["workflow_orchestration_agent"]
)
```

### Communication & Marketing Department

#### Content Writing Agent
- **Purpose**: Create compelling internal and external communications
- **Key Functions**:
  - Marketing copy generation
  - Internal documentation
  - Email templates
  - Blog content creation

```python
# Example: Request content creation
await send_system_message(
    message_type="content_request",
    content={
        "content_type": "blog_post",
        "topic": "AI in Enterprise Automation",
        "target_audience": "executive",
        "tone": "professional",
        "length": "long"
    },
    target_agents=["content_writing_agent"]
)
```

#### Social Media Monitoring Agent
- **Purpose**: Track brand presence and market sentiment
- **Key Functions**:
  - Brand mention tracking
  - Sentiment analysis
  - Competitor monitoring
  - Trend identification

```python
# Example: Get social media insights
await send_system_message(
    message_type="sentiment_analysis_request",
    content={
        "brands": ["your_company"],
        "time_period": "last_week",
        "platforms": ["twitter", "linkedin"]
    },
    target_agents=["social_media_monitoring_agent"]
)
```

## Agent Interactions

### Cross-Department Communication

The Enterprise Legion framework enables seamless communication between departments:

```python
# Example: Integrated financial and marketing analysis
await send_system_message(
    message_type="integrated_analysis_request",
    content={
        "financial_metrics": True,
        "market_sentiment": True,
        "content_recommendations": True
    },
    target_agents=[
        "financial_analysis_agent",
        "market_analysis_agent", 
        "content_writing_agent"
    ]
)
```

### Real-time Monitoring

```python
# Monitor system performance
status = await get_system_status()

for agent_id, agent_status in status['agent_details'].items():
    print(f"{agent_id}: {agent_status['status']}")
    if 'recent_tasks' in agent_status:
        print(f"  Recent tasks: {agent_status['recent_tasks']}")
```

## API Reference

### Core Functions

#### `initialize_enterprise_legion()`
Initializes the complete Enterprise Legion system with all agents.

**Returns**: `EnterpriseAgentRegistry` instance

#### `get_system_status()`
Returns comprehensive system status including all agent statuses.

**Returns**: Dictionary with system status, agent details, and metrics

#### `send_system_message(message_type, content, target_agents=None)`
Sends messages to specific agents or broadcasts system-wide.

**Parameters**:
- `message_type`: String identifier for message type
- `content`: Dictionary containing message payload
- `target_agents`: Optional list of agent IDs to target

### Message Types

#### Financial Messages
- `financial_data_update`: Update financial data
- `projection_request`: Request financial projections
- `budget_analysis_request`: Request budget analysis

#### Operational Messages
- `workflow_execution_request`: Execute workflow
- `resource_optimization_request`: Optimize resources
- `task_scheduling_request`: Schedule tasks

#### Communication Messages
- `content_request`: Request content creation
- `social_media_insights`: Social media data update
- `brand_monitoring_request`: Monitor brand mentions

#### Compliance Messages
- `compliance_check_request`: Request compliance check
- `audit_preparation_request`: Prepare for audit
- `policy_update`: Update policies

### Agent Status Fields

Each agent returns status information including:
- `agent_id`: Unique identifier
- `status`: Current operational status
- `tasks_completed`: Number of completed tasks
- `messages_processed`: Number of processed messages
- `last_activity`: Timestamp of last activity
- `department`: Department assignment
- `integration_points`: Connected agents

## Best Practices

### 1. System Initialization
Always initialize the system before sending messages:

```python
# Correct approach
registry = await initialize_enterprise_legion()
status = await get_system_status()

if status['system_status'] == 'operational':
    # System ready for use
    await send_system_message(...)
```

### 2. Error Handling
Implement proper error handling for agent interactions:

```python
try:
    await send_system_message(
        message_type="financial_analysis_request",
        content=data,
        target_agents=["financial_analysis_agent"]
    )
except Exception as e:
    logger.error(f"Failed to send message: {e}")
    # Implement fallback logic
```

### 3. Performance Monitoring
Regularly monitor system performance:

```python
# Monitor agent health
status = await get_system_status()
operational_agents = status['operational_agents']
total_agents = status['total_agents']

if operational_agents < total_agents:
    logger.warning(f"Some agents offline: {operational_agents}/{total_agents}")
```

### 4. Graceful Shutdown
Always shutdown the system gracefully:

```python
from modules.llm_abstraction.agents.legion.enterprise.enterprise_registry import shutdown_enterprise_legion

# At application shutdown
await shutdown_enterprise_legion()
```

## Advanced Usage

### Custom Workflows
Create complex multi-agent workflows:

```python
workflow = {
    "name": "quarterly_business_review",
    "steps": [
        {
            "agent": "financial_analysis_agent",
            "task": "analyze_quarterly_performance",
            "dependencies": []
        },
        {
            "agent": "market_analysis_agent", 
            "task": "analyze_market_conditions",
            "dependencies": []
        },
        {
            "agent": "report_generation_agent",
            "task": "generate_executive_summary",
            "dependencies": ["financial_analysis_agent", "market_analysis_agent"]
        }
    ]
}

await send_system_message(
    message_type="workflow_execution_request",
    content=workflow,
    target_agents=["workflow_orchestration_agent"]
)
```

### Integration with External Systems
Connect Enterprise Legion with external business systems:

```python
# Example: ERP integration
erp_data = fetch_from_erp_system()

await send_system_message(
    message_type="external_data_update",
    content={
        "source": "erp_system",
        "data": erp_data,
        "timestamp": datetime.now().isoformat()
    },
    target_agents=["financial_analysis_agent", "resource_optimization_agent"]
)
```

---

## Legacy Chimera Usage

### 1. Running the Chimera Orchestrator

The `ChimeraOrchestrator` is the legacy central component that discovers and manages individual agents. You can run it directly from the command line.

To run the orchestrator, navigate to the root directory of the `artifactvirtual` project in your terminal and execute the following command:

```bash
python chimera/run.py
```

Upon execution, the orchestrator will list all discovered and loaded agents. For example:

```
Available and loaded agents:
- Code-Genius [Loaded]
```

### 2. Interacting with Legacy Chimera Agents

The `Code-Genius` agent is designed to generate code based on a given prompt. While the current `orchestrator.py` includes an example of how to call it programmatically within its `if __name__ == '__main__':` block, in a real application, you would typically interact with it via the FastAPI interface exposed by `chimera/api/main.py`.

#### Example of Direct Interaction (for development/testing):

As seen in the `orchestrator.py` file, you can directly call the `execute_task` method on an instantiated `ChimeraOrchestrator` object.

```python
from chimera.core.orchestrator import ChimeraOrchestrator

orchestrator = ChimeraOrchestrator()

# Example execution with Code-Genius
if "Code-Genius" in orchestrator.agents:
    print("Executing task with Code-Genius...")
    task_prompt = "Create a Python function to reverse a string."
    response = orchestrator.execute_task("Code-Genius", task_prompt)
    print("\n--- Code-Genius Response ---")
    print(response)
    print("--------------------------")
else:
    print("Code-Genius agent not found.")

# Example execution with Research_Agent
if "Research_Agent" in orchestrator.agents:
    print("\nExecuting task with Research_Agent...")
    task_prompt = "Find the latest research on quantum computing."
    response = orchestrator.execute_task("Research_Agent", task_prompt)
    print("\n--- Research_Agent Response ---")
    print(response)
    print("--------------------------")
else:
    print("Research_Agent agent not found.")

# Example execution with Analytics_Agent
if "Analytics_Agent" in orchestrator.agents:
    print("\nExecuting task with Analytics_Agent...")
    task_prompt = "Analyze sales data for Q1 2024."
    response = orchestrator.execute_task("Analytics_Agent", task_prompt)
    print("\n--- Analytics_Agent Response ---")
    print(response)
    print("--------------------------")
else:
    print("Analytics_Agent agent not found.")
```

### Agent Functionality:

All agents are expected to have an `execute(task)` method. This method takes a string `task` as input, which describes the task you want the agent to perform. The agent then returns a string containing the result of the execution.

**Example Task:**

`"Create a Python function to calculate the factorial of a number."`

**Example Output (from Code-Genius):**

```python
// Code generated by CodeGeniusAgent for prompt: Create a Python function to calculate the factorial of a number.
```

*(Note: The current implementation of agents provides placeholder responses. Further development would integrate robust models and logic.)*


## 3. Future Interaction via API (Recommended)

For a more robust and scalable interaction, the `chimera/api/main.py` file sets up a FastAPI application. Once this API is running, you can interact with the agents via HTTP requests. This is the intended way to integrate Chimera into larger applications.

To start the API server (requires `uvicorn`):

```bash
uvicorn chimera/api/main:app --reload
```

Then, you could send a POST request to `/execute` with the agent name and task.

```json
{
  "agent": "Code-Genius",
  "task": "Create a JavaScript function for a debounce utility."
}
```

This guide provides a basic overview. For more detailed development, refer to the individual agent `main.py` files and the `chimera/core/orchestrator.py` for agent discovery logic.

## 4. Interaction via gRPC

For high-performance, cross-language communication, Chimera agents can also be interacted with via gRPC. This requires generating Python stubs from the Protocol Buffer definition and running a gRPC server.

### Setup gRPC:

1.  **Install `grpcio` and `grpcio-tools`:**
    ```bash
    pip install grpcio grpcio-tools
    ```

2.  **Generate gRPC stubs:**
    From the `artifactvirtual` root directory, run:
    ```bash
    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. chimera/grpc/agent_service.proto
    ```
    This will generate `chimera/grpc/agent_service_pb2.py` and `chimera/grpc/agent_service_pb2_grpc.py`.

### Running the gRPC Server:

Open a new terminal and execute the following command from the `artifactvirtual` root directory:

```bash
python chimera/grpc/server.py
```

### Interacting with the gRPC Server (Client Example):

You can use the provided client example to interact with the gRPC server. Open another terminal and run:

```bash
python chimera/grpc/client.py
```

This client demonstrates how to list agents and execute tasks via gRPC.
