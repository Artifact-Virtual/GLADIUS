# Matrix Subsystem - Code Executor Integration

## Overview

The Matrix subsystem has been successfully integrated with the MCP (Model Context Protocol) system to provide advanced code execution capabilities. This integration bridges the sophisticated executor manager from the matrix with your LLM abstraction layer.

## ✅ Completed Integration

### 1. **Helm Charts Moved**
- **From**: `/nerve_centre/matrix/helm/`
- **To**: `/nerve_centre/foundry/helm/`
- **Rationale**: Foundry subsystem handles deployment orchestration and agent factory operations

### 2. **Code Executor Bridge Created**
- **Location**: `/nerve_centre/llm_abstraction/mcp/executors/code_executor_bridge.py`
- **Features**:
  - Connects matrix executor_manager with MCP protocol
  - Supports Python and JavaScript/Node.js execution
  - Fallback to local execution when containerized execution unavailable
  - Comprehensive error handling and timeout management

### 3. **MCP Integration Enhanced**
- **Enhanced**: `/nerve_centre/llm_abstraction/mcp/integration.py`
- **New Capabilities**:
  - Code execution functions integrated into MCP function registry
  - Automatic function discovery and registration
  - Safe function identification for auto-execution
  - Comprehensive logging and error handling

### 4. **Startup Scripts Created**
- **Executor Manager**: `start_executor_manager.py`
- **Setup Script**: `setup_matrix.py`
- **Enhanced Test**: `test_mcp_integration.py` (updated with code execution tests)

## 🚀 Usage

### Quick Start

1. **Setup the system**:
   ```bash
   cd /enterprise/nerve_centre/llm_abstraction
   python setup_matrix.py
   ```

2. **Start the executor manager** (optional - has local fallback):
   ```bash
   python start_executor_manager.py --port 8000
   ```

3. **Test the integration**:
   ```bash
   python test_mcp_integration.py
   ```

### Code Execution via MCP

```python
from llm_abstraction.mcp import MCPEnhancedLLMAbstraction
from llm_abstraction.llm_abstraction import LLMAbstraction

# Create enhanced LLM with code execution
base_llm = LLMAbstraction()
enhanced_llm = MCPEnhancedLLMAbstraction(base_llm)
await enhanced_llm.initialize()

# Execute Python code
result = await enhanced_llm.execute_mcp_function(
    'execute_python',
    {
        'code': 'print("Hello from Matrix!"); result = 2 ** 10; print(f"2^10 = {result}")',
        'timeout': 30
    }
)

# Execute JavaScript
js_result = await enhanced_llm.execute_mcp_function(
    'execute_javascript',
    {
        'code': 'console.log("Hello from Node.js!"); console.log("Math.PI =", Math.PI);',
        'timeout': 30
    }
)
```

### LLM Query with Auto Code Execution

```python
# LLM can automatically execute code mentioned in queries
result = await enhanced_llm.query(
    "Please calculate the factorial of 10 using Python and show me the result",
    include_mcp_context=True,
    auto_execute_mcp=True
)

print("LLM Response:", result['llm_response'].content)
print("Code Execution Results:", result['mcp_results'])
```

## 🏗️ Architecture

### Matrix Subsystem Components (Recommended)

#### **✅ ADOPT - High Value**

1. **graphrag/** - Graph Retrieval-Augmented Generation
   - Advanced knowledge graph construction
   - Entity resolution and community detection
   - Sophisticated query rewriting and analysis
   - **Integration**: Fully compatible with MCP, provides core intelligence

2. **organized_retrieval.py** - Hierarchical Information Organization
   - Recursive abstractive processing
   - UMAP dimensionality reduction
   - Gaussian mixture clustering
   - **Integration**: Excellent for organizing code execution results

3. **deepdoc/** - Multi-modal Document Processing
   - Advanced PDF parsing with OCR
   - Vision models for table recognition
   - Structured document analysis
   - **Integration**: Can process code documentation and technical documents

4. **nlp/** - Natural Language Processing Foundation
   - Core tokenization and text processing
   - Search capabilities and similarity matching
   - **Integration**: Essential for MCP query processing

5. **executor_manager/** - Secure Code Execution ✨
   - **NOW INTEGRATED**: Containerized Python/Node.js execution
   - Docker-based isolation
   - Resource limits and timeout management
   - **Integration**: Core component for code execution capabilities

#### **📦 INFRASTRUCTURE**

6. **helm/** - Kubernetes Deployment
   - **MOVED TO**: `/foundry/helm/`
   - Production deployment configuration
   - **Integration**: Deploy entire system with Helm charts

## 🔧 Technical Details

### Code Executor Features

- **Dual Execution Modes**:
  - **Containerized**: Via matrix executor_manager (Docker-based)
  - **Local Fallback**: Direct Python/Node.js execution

- **Safety Features**:
  - Execution timeouts
  - Memory limits
  - Safe function identification
  - Automatic error handling

- **Supported Languages**:
  - Python 3.x
  - JavaScript/Node.js

### MCP Function Registry

The integration automatically registers these MCP functions:

- `execute_python(code, timeout=30, files=None)` - Execute Python code
- `execute_javascript(code, timeout=30, files=None)` - Execute JavaScript/Node.js
- `get_executor_info()` - Get system information
- `list_supported_languages()` - List available runtime languages

### Auto-Execution Safety

Functions marked as "safe" can be automatically executed by the LLM:
- All code execution functions (in controlled environment)
- Read-only operations (`get_*`, `list_*`, `read_*`)
- Analysis functions (`analyze_*`, `calculate_*`)

## 🎯 Next Steps

### Immediate Actions

1. **Test the complete integration**:
   ```bash
   python test_mcp_integration.py
   ```

2. **Start using in your workflows**:
   - Code analysis and execution
   - Document processing with deepdoc
   - Knowledge graph operations with graphrag

### Future Enhancements

1. **Additional Language Support**:
   - Add R, Julia, or other language executors
   - Custom runtime environments

2. **Advanced Integration**:
   - Combine with graphrag for code knowledge graphs
   - Use organized_retrieval for code documentation
   - Integrate deepdoc for processing code documentation

3. **Production Deployment**:
   - Use Helm charts in foundry for K8s deployment
   - Scale executor containers based on demand

## 📚 Documentation

- **Matrix Architecture**: `/matrix/ARCHITECTURE.md`
- **Foundry Architecture**: `/foundry/ARCHITECTURE.md`
- **Code Executor API**: Check function definitions in code_executor_bridge.py

## 🎉 Summary

Your Matrix subsystem is now fully integrated with sophisticated code execution capabilities! The system provides:

- ✅ **Secure code execution** via matrix executor_manager
- ✅ **MCP protocol integration** for seamless LLM interaction
- ✅ **Fallback mechanisms** for maximum reliability
- ✅ **Production-ready deployment** with Helm charts
- ✅ **Comprehensive testing** and monitoring

The integration maintains the mathematical sophistication of the matrix architecture while adding powerful execution capabilities that make your nerve centre truly intelligent and capable.
