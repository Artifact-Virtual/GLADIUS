# Testing Nanocode v4

This document describes how to test nanocode v4 without API keys using the mock adapter.

## Quick Start - Testing Without API Keys

1. **Set up environment:**
```bash
# Copy the example env file
cp .env.example .env

# Or set environment variables directly
export ADAPTER_TYPE=mock
export USE_TEST_POLICY=true
```

2. **Run interactive test mode:**
```bash
python run.py
```

This will start nanocode in interactive mock mode where you'll be prompted to provide responses for:
- **Planner agent**: Enter the plan (or press Enter for default)
- **Executor agent**: Enter tool calls (or 'done' to finish)
- **Memory agent**: Enter summary (or press Enter for default)

## Automated Testing

### Basic Automated Test

Run the basic automated test:
```bash
python test_automated.py
```

This executes 3 test cases with pre-defined responses.

### Comprehensive Monitoring Test

Run the comprehensive monitoring test:
```bash
python test_monitor.py
```

This test:
- Executes 5 different test scenarios
- Monitors all LLM calls and tool executions
- Generates a detailed report
- Checks workspace file creation

## Test Scenarios Covered

### 1. Basic Bash Command
Tests execution of simple bash commands (pwd, ls, etc.)

### 2. File Write Operation
Tests creating files in the workspace

### 3. File Read Operation
Tests reading files from the workspace

### 4. Combined Operations
Tests multiple sequential operations

### 5. Error Handling
Tests graceful handling of errors

## Configuration Options

### Environment Variables

Set these in `.env` or as environment variables:

- `ADAPTER_TYPE`: `mock` for testing, `anthropic` for production
- `USE_TEST_POLICY`: `true` to use test policy with more commands
- `WORKSPACE_DIR`: Directory for agent operations (default: `./workspace`)
- `WRITE_ENABLED`: Enable/disable file writing
- `ALLOWED_COMMANDS`: Comma-separated list of allowed bash commands

### Policy Files

- `policy.json` - Default production policy
- `policy.test.json` - Test policy with expanded permissions
- `policy.safe.json` - Conservative read-only policy

Toggle between policies using `USE_TEST_POLICY` environment variable.

## Test Output

### Workspace Directories

Tests create separate workspace directories:
- `workspace/` - Main workspace for normal operation
- `workspace_monitor/` - Used by monitoring tests

These directories are excluded from git (see `.gitignore`).

### Memory Files

- `.nanocode.memory.json` - Persistent memory across sessions
- Excluded from git for privacy

## Interactive Mock Mode

When running with `ADAPTER_TYPE=mock`, you can provide custom responses:

### Planner Agent
Prompted with: "Enter plan (or press Enter for default):"
- Provide a multi-line plan
- Or press Enter for a generic plan

### Executor Agent
Prompted with: "Enter tool calls"
- Format: `tool_name arg=value`
- Example: `bash cmd='ls -la'`
- Type `done` when finished
- Or press Enter for default action

### Memory Agent
Prompted with: "Enter summary (or press Enter for default):"
- Provide a summary of what was accomplished
- Or press Enter for a generic summary

## Example Interactive Session

```
$ python run.py
[INFO] Adapter type: mock
[INFO] Using mock adapter (interactive testing mode)
[CONFIG] Using policy: policy.test.json
[CONFIG] Workspace: /path/to/workspace
nanocode v4 ready
❯ List all files

[MOCK LLM CALL #1]
System: You decompose tasks into executable steps.
User: List all files
Available tools: []

Enter plan (or press Enter for default):
1. Use ls command to list files
2. Format the output

[MOCK LLM CALL #2]
...
```

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
Set `ADAPTER_TYPE=mock` to test without API keys.

### "Command denied by policy"
Add the command to `ALLOWED_COMMANDS` in `.env` or use `USE_TEST_POLICY=true`.

### "Path outside workspace"
All file operations must be within the workspace directory for security.

### Workspace not created
Check that `WORKSPACE_DIR` is writable and the path is valid.

## Switching to Production

To use with real LLM:

1. Set environment:
```bash
export ADAPTER_TYPE=anthropic
export ANTHROPIC_API_KEY="your-key-here"
export USE_TEST_POLICY=false  # Use production policy
```

2. Run:
```bash
python run.py
```

## Test Results

All tests pass successfully:
- ✓ Basic Bash Command
- ✓ File Write Operation
- ✓ File Read Operation
- ✓ Combined Operations
- ✓ Error Handling

The system correctly:
- Creates workspace directories
- Enforces policy restrictions
- Executes tools safely
- Maintains memory across sessions
- Handles errors gracefully
