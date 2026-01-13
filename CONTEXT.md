# Gladius Context

> Operational context for the Gladius autonomous enterprise system

---

## System Overview

Gladius is an autonomous enterprise operating system that manages multiple artifacts (autonomous business units) through a unified cognition layer with native vectorization and AI capabilities.

- **Root**: `/home/adam/worxpace/gladius`
- **Primary Domain**: artifactvirtual.com (planned)
- **Cognition Backend**: Hektor VDB (native C++) + llama.cpp

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
└── syndicate_integration.py # Report ingestion & search
```

### Hektor VDB Features
- **SIMD Optimization**: AVX2/AVX512 vector operations
- **Hybrid Search**: Vector similarity + BM25 lexical fusion
- **Gold Standard Types**: Journal, Chart, Catalyst, Calendar, etc.
- **Native NLP**: WordPiece tokenizer, llama.cpp inference
- **Python Bindings**: pyvdb module for seamless integration

### Current State
| Metric | Value |
|--------|-------|
| Backend | Hektor VDB (native) |
| Fallback | hnswlib + TF-IDF |
| Vector Dimension | 384 |
| LLM Integration | llama.cpp (local GGUF) |
| Build Status | ✅ Complete |

---

## Memory Module

The memory module provides persistent learning and tool capabilities:

### Capabilities
- **Document Ingestion**: All Syndicate outputs vectorized
- **Semantic Search**: Natural language queries across history
- **Context Retrieval**: Historical context for AI analysis
- **Prediction Tracking**: Learning from outcomes
- **Tool Calling**: Native function invocation (in development)
- **Multi-DB Access**: Read/write across databases

### Data Flow
```
Syndicate Outputs → Cognition Engine → Hektor VDB
                                          │
                         ┌────────────────┼────────────────┐
                         │                │                │
                         ▼                ▼                ▼
                    Semantic         Learning         Context
                    Memory           History          Retrieval
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

# Build Hektor VDB
cd Artifact/hektor/build && cmake .. && make -j$(nproc)
```

---

## Current Capabilities

### ✅ Implemented
- Unified control script (`gladius.sh`)
- Hektor VDB native vector database
- llama.cpp local LLM inference
- Syndicate research pipeline
- Cognition engine with hybrid search
- Dashboard backend/frontend
- Infra API for market data

### 🚧 In Progress
- Native tool/function calling
- Multi-database memory hooks
- ONNX Runtime for Linux (currently MSVC only)

### 📋 Planned
- Artifact-specific GGUF/GGM models
- Web3 integration per artifact
- Social/publishing pipeline (Theta)
- Native embeddings without external APIs

---

## Integration Points

### Syndicate → Cognition
All Syndicate outputs are ingested:
- Journals → Vector memory
- Premarket reports → Semantic search
- Catalyst watchlists → Context retrieval
- Charts → Historical analysis

### Cognition → Cthulu
Trade signals flow through:
- Semantic context from history
- Prediction outcomes for learning
- Risk parameters from analysis

---

## Build Status

| Component | Status | Notes |
|-----------|--------|-------|
| libvdb_core.a | ✅ Built | Core C++ library |
| hektor CLI | ✅ Built | Command-line interface |
| pyvdb.so | ✅ Built | Python bindings |
| llama.cpp | ✅ Integrated | Tag b7716 |
| ONNX Runtime | ⚠️ Windows only | VDB_USE_ONNX_RUNTIME=OFF on Linux |

---

*Last updated: 2026-01-13*