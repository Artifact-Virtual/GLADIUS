# BUILD_CLASS KERNEL
> Codename: Buck

A minimal autonomous coding agent system with multi-agent mesh architecture.

## Overview

 This is a lightweight autonomous execution kernel that uses a planner/executor pattern with persistent semantic memory. It features:

- **Multi-Agent Architecture**: Separate Planner, Executor, and Memory agents for specialized tasks
- **Policy-Based Security**: Configurable policy engine for sandboxed execution
- **Persistent Memory**: Semantic memory system for learning across sessions
- **Tool System**: Safe, sandboxed tools for file operations and bash commands
- **Mesh Coordination**: Agent mesh for coordinated autonomous operation

## Architecture

### Components

1. **Planner Agent**: Decomposes high-level goals into executable steps
2. **Executor Agent**: Executes plans using available tools
3. **Memory Agent**: Summarizes execution history into durable memory
4. **Policy Engine**: Enforces security constraints on operations
5. **Tool System**: Provides sandboxed read, write, and bash capabilities

### Design Patterns

- **Planner/Executor Split**: Separates planning from execution for better control
- **Policy Enforcement**: All operations pass through policy validation
- **Semantic Memory**: Context preserved across multiple executions
- **Mesh Architecture**: Coordinated multi-agent system

## Installation

### Prerequisites

- Python 3.7+
- **Primary**: llama.cpp server (recommended - local & free)
- **Alternative**: Anthropic API key (cloud-based)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/amuzetnom02/test_recursion.git
cd test_recursion
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. **Option A: Set up llama.cpp (Recommended)**
```bash
# See LLAMACPP_SETUP.md for complete guide
# Quick start:
export ADAPTER_TYPE=llamacpp
export LLAMA_SERVER_URL=http://localhost:8080
```

4. **Option B: Set up Anthropic (Alternative)**
```bash
export ADAPTER_TYPE=anthropic
export ANTHROPIC_API_KEY="your-api-key-here"
```

5. **Option C: Use mock adapter for testing**
```bash
export ADAPTER_TYPE=mock
```

## Usage

### Primary: Using llama.cpp (Local & Free)

```bash
# Start llama.cpp server first (see LLAMACPP_SETUP.md)
./server -m /path/to/model.gguf --port 8080

# Run nanocode
python run.py
```

### Alternative: Using Anthropic Claude

```bash
export ADAPTER_TYPE=anthropic
export ANTHROPIC_API_KEY="your-key-here"
python run.py
```

### Testing: Using Mock Adapter

```bash
export ADAPTER_TYPE=mock
python run.py
```

### Interactive Mode

Once running, you can issue natural language commands:

```
nanocode v4 ready
❯ list all python files in the current directory
❯ read the contents of nanocode.py
❯ create a new file called test.txt with hello world
❯ exit
```

## Configuration

### Policy Configuration (`policy.json`)

Control security and operational constraints:

```json
{
  "allowed_commands": ["ls", "cat", "pwd", "echo", "grep"],
  "write_enabled": true,
  "max_file_size": 200000
}
```

**Parameters:**
- `allowed_commands`: Whitelist of bash commands
- `write_enabled`: Enable/disable file write operations
- `max_file_size`: Maximum file size to read (bytes)

### Memory System

Nanocode maintains persistent memory in `.nanocode.memory.json`:
- Automatically summarizes each execution
- Keeps historical context for future operations
- Limited to last 5 entries for context window management

## Tools

### Available Tools

1. **read**: Read file contents with metadata
   - Respects `max_file_size` policy
   - Returns file classification (code/config/data)
   - Truncates output to prevent overflow

2. **write**: Write content to files
   - Requires `write_enabled` in policy
   - Creates/overwrites files

3. **bash**: Execute shell commands
   - Restricted to `allowed_commands` whitelist
   - Timeout protection (20 seconds)
   - Output truncation

## Security

### Policy Enforcement

All operations are validated against the policy before execution:
- Bash commands must be in the allowed list
- Write operations can be globally disabled
- File size limits prevent memory issues
- Command timeouts prevent infinite loops

### Sandboxing

- Commands execute in the configured working directory
- Output is truncated to prevent overflow
- Timeouts prevent runaway processes
- No network access by default (except API calls)

## Development

### File Structure

```
.
├── adapter_anthropic.py    # Anthropic API adapter
├── nanocode.py             # Main execution kernel
├── policy.json             # Security policy
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

### Extending Nanocode

#### Adding New Tools

```python
def tool_custom(arg1, arg2):
    # Your implementation
    return result

TOOLS["custom"] = tool_custom
```

#### Adding New Agents

```python
class CustomAgent(Agent):
    def custom_method(self, input):
        return self.call([{"role":"user","content":input}])
```

## Limitations

- Depends on external LLM (Anthropic Claude)
- Policy restrictions limit bash capabilities
- Memory context limited to recent history
- No built-in version control for changes
- Single-threaded execution

## Future Enhancements

- [ ] Additional LLM adapters (OpenAI, local models)
- [ ] Enhanced tool library
- [ ] Better error handling and recovery
- [ ] Parallel execution support
- [ ] Web interface
- [ ] Plugin system for extensibility

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## Acknowledgments

Built with Claude by Anthropic.
