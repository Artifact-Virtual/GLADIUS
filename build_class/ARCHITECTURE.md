# Nanocode v4 - Architecture Documentation

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Nanocode v4 Mesh                         │
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │   Planner    │      │   Executor   │      │    Memory    │ │
│  │    Agent     │──────│    Agent     │──────│    Agent     │ │
│  └──────────────┘      └──────────────┘      └──────────────┘ │
│         │                      │                      │        │
│         │                      │                      │        │
│         v                      v                      v        │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              Anthropic Claude API Adapter                │ │
│  └──────────────────────────────────────────────────────────┘ │
│                              │                                 │
└──────────────────────────────┼─────────────────────────────────┘
                               │
                               v
                    ┌──────────────────┐
                    │  Anthropic API   │
                    │ (Claude Models)  │
                    └──────────────────┘
```

## Data Flow

```
User Input
    │
    v
┌───────────────────┐
│ Planner Agent     │  "Decompose tasks into executable steps"
│ - Analyzes goal   │
│ - Creates plan    │
└───────┬───────────┘
        │
        │ Plan
        v
┌───────────────────┐
│ Executor Agent    │  "Execute plans strictly using tools"
│ - Receives plan   │
│ - Uses tools      │
│ - Collects logs   │
└───────┬───────────┘
        │
        │ Execution Log
        v
┌───────────────────┐
│ Memory Agent      │  "Summarize execution into durable memory"
│ - Summarizes      │
│ - Stores memory   │
└───────┬───────────┘
        │
        v
   .nanocode.memory.json
```

## Tool System Architecture

```
┌────────────────────────────────────────┐
│          Executor Agent                │
└────────────┬───────────────────────────┘
             │
             │ Tool Request
             v
┌────────────────────────────────────────┐
│       Policy Enforcement Layer         │
│  - Command whitelisting                │
│  - Write permission check              │
│  - File size validation                │
└────────────┬───────────────────────────┘
             │
             │ Validated Request
             v
┌────────────────────────────────────────┐
│          Tool Registry                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │  read   │ │  write  │ │  bash   │  │
│  └─────────┘ └─────────┘ └─────────┘  │
└────────────┬───────────────────────────┘
             │
             │ Execution
             v
┌────────────────────────────────────────┐
│        Sandboxed Execution             │
│  - Timeout protection (20s)            │
│  - Output truncation (4000 chars)      │
│  - Working directory constraint        │
└────────────┬───────────────────────────┘
             │
             │ Result
             v
        Executor Agent
```

## Component Details

### 1. Mesh (Orchestrator)

**Purpose**: Coordinates all agents and maintains system state

**Key Responsibilities**:
- Initialize agents with proper roles
- Load/save persistent memory
- Orchestrate the execution flow
- Manage context window (last 5 memories)

**State**:
```python
{
  "adapter": AnthropicAdapter,
  "planner": Planner,
  "executor": Executor, 
  "mem_agent": MemoryAgent,
  "memory": [
    {"id": "hash", "time": 123456, "goal": "...", "summary": "..."},
    ...
  ]
}
```

### 2. Planner Agent

**System Prompt**: "You decompose tasks into executable steps."

**Input**: User's natural language goal
**Output**: Step-by-step plan

**Example**:
- Input: "Find all Python files and count their lines"
- Output: 
  ```
  1. Use bash tool to list all .py files
  2. For each file, use bash to count lines
  3. Sum the total lines
  ```

### 3. Executor Agent

**System Prompt**: "You execute plans strictly using tools."

**Input**: 
- Plan from Planner
- Recent memory context (last 5 entries)

**Output**: Tool use blocks

**Example**:
```json
[
  {
    "type": "tool_use",
    "name": "bash",
    "input": {"cmd": "find . -name '*.py'"}
  },
  {
    "type": "tool_use", 
    "name": "bash",
    "input": {"cmd": "wc -l nanocode.py"}
  }
]
```

### 4. Memory Agent

**System Prompt**: "Summarize execution into durable memory."

**Input**: Execution log with goal, plan, and tool results
**Output**: Concise summary for future context

**Example**:
- Input: Goal + Plan + [tool outputs]
- Output: "Listed 3 Python files totaling 350 lines. Files: adapter_anthropic.py (29), nanocode.py (143), run.py (178)"

### 5. Policy Engine

**Configuration** (policy.json):
```json
{
  "allowed_commands": ["ls", "cat", "pwd", "echo", "grep"],
  "write_enabled": true,
  "max_file_size": 200000
}
```

**Enforcement Points**:
1. Before bash execution → check command whitelist
2. Before write → check write_enabled flag
3. Before read → check file size limit

### 6. Tools

#### Read Tool
```python
def tool_read(path: str) -> dict:
    """
    Read file with metadata and size limits
    
    Returns:
        {
            "meta": {"path": "...", "ext": "...", "size": N, "role": "..."},
            "content": "file contents (truncated to MAX_OUTPUT)"
        }
    """
```

#### Write Tool
```python
def tool_write(path: str, content: str) -> str:
    """
    Write content to file
    
    Requires: write_enabled = true in policy
    Returns: "wrote N bytes"
    """
```

#### Bash Tool
```python
def tool_bash(cmd: str) -> str:
    """
    Execute shell command
    
    Requires: first word in allowed_commands
    Timeout: 20 seconds
    Returns: stdout (truncated to MAX_OUTPUT)
    """
```

## Memory System

### Storage Format

```json
[
  {
    "id": "abc123def456",
    "time": 1705856400,
    "goal": "List all Python files",
    "summary": "Found 3 Python files: adapter_anthropic.py, nanocode.py, run.py"
  },
  ...
]
```

### Memory Lifecycle

```
1. Execution completes
         │
         v
2. Memory Agent summarizes
         │
         v
3. Generate hash ID (sha256 of goal + summary)
         │
         v
4. Add timestamp
         │
         v
5. Append to memory array
         │
         v
6. Save to .nanocode.memory.json
         │
         v
7. Load last 5 for next execution context
```

## Security Model

### Defense in Depth Layers

```
Layer 1: Policy Configuration
    ↓ (Define allowed operations)
    
Layer 2: Policy Enforcement
    ↓ (Validate before execution)
    
Layer 3: Tool Sandboxing
    ↓ (Execute with constraints)
    
Layer 4: Resource Limits
    ↓ (Timeout, output truncation)
    
Layer 5: Working Directory Isolation
    ↓ (CWD constraint)
    
Execution
```

### Current Limitations

⚠️ **Security Gaps**:
1. No path traversal protection
2. Command injection via shell operators
3. Environment variable exposure
4. No resource quotas (CPU, memory, disk)
5. No audit logging

## Extension Points

### Adding a New Tool

```python
# 1. Define the tool function
def tool_custom(arg1: str, arg2: int) -> str:
    """Your custom tool implementation"""
    # ... implementation ...
    return result

# 2. Register in TOOLS dictionary
TOOLS["custom"] = tool_custom

# 3. (Optional) Add policy enforcement
def enforce_policy(action, payload):
    # ...existing code...
    if action == "custom":
        # Your validation logic
        pass
```

### Adding a New Agent

```python
class CustomAgent(Agent):
    def custom_operation(self, input_data):
        messages = [{"role": "user", "content": input_data}]
        return self.call(messages)

# Add to Mesh
class Mesh:
    def __init__(self, adapter):
        # ...existing agents...
        self.custom = CustomAgent("custom", adapter, "Your role description")
```

### Adding a New LLM Adapter

```python
class OpenAIAdapter:
    def __init__(self):
        self.key = os.environ["OPENAI_API_KEY"]
        self.model = "gpt-4"
        
    def call(self, system, messages, tools):
        # Convert to OpenAI format
        # Make API call
        # Return in expected format: list of content blocks
        return response
```

## Performance Characteristics

### Time Complexity
- **Planning**: O(1) LLM call
- **Execution**: O(n) where n = number of tools in plan
- **Memory**: O(1) LLM call

### Space Complexity
- **Memory Storage**: O(m) where m = number of executions
- **Context Window**: O(1) - fixed at last 5 memories
- **Output**: O(1) - truncated at MAX_OUTPUT

### Typical Execution Flow Timing

```
User Input
    ↓ ~0s
Planner Agent
    ↓ ~2-5s (LLM latency)
Executor Agent
    ↓ ~3-10s (LLM + tool execution)
Tool Execution (each)
    ↓ ~0.1-20s (up to timeout)
Memory Agent
    ↓ ~2-5s (LLM latency)
Total: ~7-40 seconds per goal
```

## Configuration Options

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY="sk-ant-..."

# Optional
MODEL="claude-3-opus-20240229"    # Default model
WORKDIR="/custom/path"             # Custom working directory
```

### Policy Tuning

**Conservative** (read-only analysis):
```json
{
  "allowed_commands": ["ls", "cat", "grep", "find"],
  "write_enabled": false,
  "max_file_size": 100000
}
```

**Balanced** (default):
```json
{
  "allowed_commands": ["ls", "cat", "pwd", "echo", "grep"],
  "write_enabled": true,
  "max_file_size": 200000
}
```

**Permissive** (development):
```json
{
  "allowed_commands": ["ls", "cat", "pwd", "echo", "grep", "find", "head", "tail", "git"],
  "write_enabled": true,
  "max_file_size": 1000000
}
```

## Troubleshooting

### Common Issues

1. **"Command denied by policy"**
   - Solution: Add command to `allowed_commands` in policy.json

2. **"Write disabled by policy"**
   - Solution: Set `write_enabled: true` in policy.json

3. **"File too large"**
   - Solution: Increase `max_file_size` in policy.json

4. **API timeout**
   - Solution: Check network connection, verify API key

5. **Tool execution timeout**
   - Solution: Increase TIMEOUT constant or optimize command

### Debug Mode

Add this to enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Add to each tool
def tool_read(path):
    logging.debug(f"Reading {path}")
    # ...
```

---

**Last Updated**: 2026-01-21
**Version**: 4.0.0
