# Gladius Context

> Operational context for the Gladius autonomous enterprise system

---

## System Overview

Gladius is an autonomous enterprise operating system that manages multiple artifacts (autonomous business units) through a unified cognition layer with native vectorization, ONNX Runtime, and llama.cpp inference.

- **Root**: `/home/adam/worxpace/gladius`
- **Primary Domain**: artifactvirtual.com (planned)
- **Cognition Backend**: Hektor VDB (native C++) + llama.cpp + ONNX Runtime

---

## Active Artifacts

### Alpha: Syndicate (Research)
- **Path**: `Artifact/syndicate/`
- **Purpose**: Market research, analysis, journal generation
- **Status**: ✅ Production
- **Cognition**: Hektor VDB (SIMD + hybrid search)
- **Outputs**: Journals, Premarket, Catalysts, Calendar, Charts

### Beta: Cthulu (Trading)
- **Path**: External (`/_build/cthulu/`)
- **Purpose**: Trade execution via MQL5/MetaTrader 5
- **Status**: ✅ Staging (GCP deployed)

### Infrastructure
- **Infra API** (7000): Markets, assets, portfolios
- **Automata Dashboard** (5000): Control panel
- **Frontend UI** (3000): React operator interface

---

## Cognition Engine

The cognition engine provides semantic memory and native AI across all artifacts:

```
Location: Artifact/syndicate/src/cognition/
├── __init__.py
├── embedder.py              # TF-IDF / neural embeddings
├── vector_store.py          # hnswlib fallback
├── hektor_store.py          # Native Hektor VDB integration
├── memory_module.py         # Unified memory access (planned)
├── tool_calling.py          # Native tool definitions (planned)
└── syndicate_integration.py # Report ingestion & search
```

### Hektor VDB Features
- **SIMD Optimization**: AVX2/AVX512 vector operations
- **Hybrid Search**: Vector similarity + BM25 lexical fusion
- **Gold Standard Types**: Journal, Chart, Catalyst, Calendar, etc.
- **Native NLP**: WordPiece tokenizer, llama.cpp inference
- **ONNX Runtime**: Native text/image encoders on Linux
- **Python Bindings**: pyvdb module for seamless integration

### Current State
| Metric | Value |
|--------|-------|
| Backend | Hektor VDB (native) |
| Fallback | hnswlib + TF-IDF |
| Vector Dimension | 384 |
| LLM Integration | llama.cpp (b7716) |
| ONNX Runtime | ✅ Enabled |
| Build Status | ✅ Complete |

---

## Memory Module

The memory module provides persistent learning, multi-database access, and native tool capabilities:

### Unified Memory Access
All databases are accessible through a single interface:

| Database | Type | Purpose |
|----------|------|---------|
| Hektor VDB | Vector | Semantic search, embeddings |
| Syndicate DB | SQLite | Predictions, tasks, history |
| Arty Store | SQLite | Automation state |
| Configs | JSON | Runtime configuration |

### Native Tool Calling (In Development)
The cognition engine will learn to use tools natively, not through third-party LLMs:

| Tool | Description |
|------|-------------|
| `read_db(name, query)` | Read from any connected database |
| `write_db(name, data)` | Write to any connected database |
| `search(query, k)` | Semantic search across all vectors |
| `get_context(query)` | Retrieve historical context |
| `read_file(path)` | Read file from workspace |
| `write_file(path, data)` | Write file to workspace |
| `list_dir(path)` | List directory contents |

### Workspace Access
The system will have sandboxed access to its own workspace for:
- File and structure management training
- Business automation learning
- Automata self-improvement

---

## Data Flow

```
Syndicate Outputs → Cognition Engine → Hektor VDB
                                          │
                         ┌────────────────┼────────────────┐
                         │                │                │
                         ▼                ▼                ▼
                    Semantic         Learning         Context
                    Memory           History          Retrieval
                         │                │                │
                         └────────────────┼────────────────┘
                                          │
                                          ▼
                                   Memory Module
                                          │
                         ┌────────────────┼────────────────┐
                         ▼                ▼                ▼
                    Tool Calling    DB Access      Workspace Ops
```

---

## Document Types

Hektor VDB recognizes these Gold Standard document types:

| Type | Purpose | Source |
|------|---------|--------|
| Journal | Daily/weekly market journals | Syndicate |
| Chart | Annotated chart analysis | Syndicate |
| CatalystWatchlist | Upcoming market catalysts | Syndicate |
| EconomicCalendar | Economic event schedules | Syndicate |
| PreMarket | Pre-market analysis | Syndicate |
| WeeklyRundown | Weekly summaries | Syndicate |
| MonthlyReport | Monthly analysis | Syndicate |
| ThreeMonthReport | Quarterly outlook | Syndicate |
| OneYearReport | Annual predictions | Syndicate |
| InstitutionalMatrix | Institutional flows | Syndicate |

---

## Environment Configuration

```bash
# Core
INFRA_API_URL=http://127.0.0.1:7000
PREFER_OLLAMA=1

# AI Providers
GOOGLE_API_KEY=your-gemini-key
NOTION_TOKEN=your-notion-token

# Dashboard
DASHBOARD_SECRET_KEY=your-secret
JWT_SECRET_KEY=your-jwt-secret
```

---

## Quick Operations

```bash
# Start all services
./gladius.sh start

# Check status
./gladius.sh status

# Stop all services
./gladius.sh stop

# Run single Syndicate cycle
cd Artifact/syndicate && python main.py --once

# Build Hektor VDB with ONNX
cd Artifact/hektor/build
cmake .. -DVDB_BUILD_PYTHON=ON -DVDB_USE_ONNX_RUNTIME=ON && make -j$(nproc)
```

---

## Current Capabilities

### ✅ Implemented
- Unified control script (`gladius.sh`)
- Hektor VDB native vector database
- llama.cpp local LLM inference (b7716)
- ONNX Runtime for native embeddings
- Syndicate research pipeline
- Cognition engine with hybrid search
- Dashboard backend/frontend
- Infra API for market data

### 🚧 In Progress
- Native tool/function calling (cognition learns tools)
- Multi-database memory hooks
- Workspace access for self-improvement

### 📋 Planned
- Artifact-specific GGUF/GGM models
- Web3 integration per artifact
- Social/publishing pipeline (Theta)
- Full autonomous learning loop

---

## Integration Points

### Syndicate → Cognition
All Syndicate outputs are ingested:
- Journals → Vector memory
- Premarket reports → Semantic search
- Catalyst watchlists → Context retrieval
- Charts → Historical analysis

### Cognition → Memory Module
The memory module connects:
- All databases (vector + relational)
- Workspace operations
- Tool calling interface
- Learning history

### Memory Module → Artifacts
Training data flows to:
- Business automation learning
- File/structure management
- Self-improvement cycles

---

## Build Status

| Component | Status | Notes |
|-----------|--------|-------|
| libvdb_core.a | ✅ Built | Core C++ library |
| hektor CLI | ✅ Built | Command-line interface |
| pyvdb.so | ✅ Built | Python bindings |
| llama.cpp | ✅ Integrated | Tag b7716 |
| ONNX Runtime | ✅ Enabled | VDB_USE_ONNX_RUNTIME=ON |

---

*Last updated: 2026-01-13*