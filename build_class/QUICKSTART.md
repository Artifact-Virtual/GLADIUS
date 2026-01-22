# Quick Start Guide - Nanocode v4

## Primary Setup: llama.cpp (Recommended)

```bash
# 1. Start llama.cpp server (see LLAMACPP_SETUP.md for details)
./server -m /path/to/model.gguf --port 8080

# 2. Configure nanocode
export ADAPTER_TYPE=llamacpp
export LLAMA_SERVER_URL=http://localhost:8080

# 3. Run nanocode
python run.py
```

See [LLAMACPP_SETUP.md](LLAMACPP_SETUP.md) for complete llama.cpp installation guide.

## Alternative: Test Without LLM (Mock Adapter)

```bash
# Set environment to use mock adapter
export ADAPTER_TYPE=mock

# Run nanocode
python run.py
```

When prompted, you'll simulate the LLM by providing responses.

## Alternative: Use Anthropic Claude

```bash
export ADAPTER_TYPE=anthropic
export ANTHROPIC_API_KEY="your-key-here"
python run.py
```

## Configuration

Edit `.env` file or set environment variables:

```bash
# Adapter type
ADAPTER_TYPE=mock              # or 'anthropic'

# Policy selection
USE_TEST_POLICY=true           # Use policy.test.json
# or
USE_TEST_POLICY=false          # Use policy.json

# Workspace
WORKSPACE_DIR=./workspace

# Allowed commands
ALLOWED_COMMANDS=ls,cat,pwd,echo,grep,find

# Write operations
WRITE_ENABLED=true
```

## Files Created

- `adapter.py` - AI-agnostic adapter (replaces adapter_anthropic.py)
- `policy.test.json` - Test policy with more commands
- `workspace/` - Directory for agent operations
- `test_automated.py` - Automated tests
- `test_monitor.py` - Monitoring tests
- `TESTING.md` - Full testing documentation
- `MONITORING_REPORT.md` - Test results and findings

## Test Results

All tests passing:
- ✓ Basic Bash Command
- ✓ File Write Operation
- ✓ File Read Operation
- ✓ Combined Operations
- ✓ Error Handling

No blockages found in any loops or sections.

## Documentation

- **TESTING.md** - How to test without API keys
- **MONITORING_REPORT.md** - Complete monitoring findings
- **README.md** - General usage and architecture
- **ARCHITECTURE.md** - Technical details
- **ANALYSIS.md** - Security analysis

## Next Steps

After testing, review MONITORING_REPORT.md for detailed findings, then let me know how to proceed with production deployment or additional features.
