# GLADIUS Test Suite

Comprehensive testing infrastructure for validating GLADIUS system capabilities.

## Test Files

### `test_comprehensive_system.py`
Complete system validation covering:
- **Tool Discovery & Execution**: Tests tool routing, pattern matching, and execution
- **Discovery Mechanisms**: Validates SENTINEL research and learning capabilities
- **Inference Capabilities**: Tests AI understanding, context awareness, and actionability
- **Workspace Control**: Validates file system, database, and memory operations
- **Integration Testing**: Tests subsystem connections and end-to-end workflows

## Running Tests

### Run All Tests
```bash
cd /home/runner/work/GLADIUS/GLADIUS
python3 tests/test_comprehensive_system.py
```

### Quick Test
```bash
# Make it executable
chmod +x tests/test_comprehensive_system.py

# Run directly
./tests/test_comprehensive_system.py
```

## Test Results

Results are automatically saved to `tests/test_results.json` after each run.

## Test Coverage

The comprehensive test validates:

### Phase 1: Tools
- ✓ Tool discovery and pattern matching
- ✓ Query routing to appropriate tools
- ✓ Tool execution with proper arguments
- ✓ Response validation

### Phase 2: Discovery
- ✓ SENTINEL research capabilities
- ✓ Learning loop functionality
- ✓ Knowledge storage and retrieval
- ✓ arXiv and GitHub integration readiness

### Phase 3: Inference
- ✓ Complex query understanding
- ✓ Confidence scoring
- ✓ Context awareness
- ✓ Response actionability
- ✓ Response speed

### Phase 4: Workspace
- ✓ File system operations (CRUD)
- ✓ Database operations (CRUD)
- ✓ Memory management
- ✓ State persistence

### Phase 5: Integration
- ✓ LEGION-GLADIUS bridge
- ✓ End-to-end workflows
- ✓ Error handling and recovery
- ✓ Continuous operation capability

## Exit Codes

- `0`: All tests passed
- `1`: Some tests failed

## Requirements

- Python 3.10+
- GLADIUS system installed
- SENTINEL services available
- LEGION framework present

## Test Environment

Tests run in isolated temporary workspaces and clean up after themselves. No production data is affected.
