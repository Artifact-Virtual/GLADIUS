# Gladius Architecture

> Autonomous Enterprise Operating System with Native AI

---

## High-Level Architecture

```
                    ┌─────────────────────────────────────────┐
                    │              GLADIUS                     │
                    │    (Autonomous Enterprise Manager)       │
                    │                                          │
                    │   ┌─────────────────────────────────┐   │
                    │   │      COGNITION ENGINE           │   │
                    │   │   Hektor VDB + llama.cpp        │   │
                    │   │   Native SIMD • NLP • Embeddings│   │
                    │   └─────────────────────────────────┘   │
                    │                                          │
                    │   ┌─────────────────────────────────┐   │
                    │   │         MEMORY MODULE           │   │
                    │   │   Context • Learning • History   │   │
                    │   │   Tool Calling • DB Access       │   │
                    │   └─────────────────────────────────┘   │
                    └───────────────┬─────────────────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           │                        │                        │
           ▼                        ▼                        ▼
    ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
    │  ARTIFACT   │          │  ARTIFACT   │          │  ARTIFACT   │
    │   ALPHA     │          │    BETA     │          │   THETA     │
    │  Syndicate  │          │   Cthulu    │          │  (Future)   │
    │  Research   │          │   Trading   │          │  Publishing │
    └──────┬──────┘          └──────┬──────┘          └─────────────┘
           │                        │
           ▼                        ▼
    ┌─────────────┐          ┌─────────────┐
    │  Journals   │          │   Execute   │
    │  Premarket  │   ───►   │   Trades    │
    │  Catalysts  │          │   Manage    │
    │  Signals    │          │   Positions │
    └─────────────┘          └─────────────┘
```

---

## Core Components

### 1. Gladius (Enterprise Brain)
- **Context Management**: Unified context across all artifacts via native vectorization
- **Hektor VDB**: SIMD-optimized vector database with hybrid search (BM25 + semantic)
- **Native AI**: llama.cpp integration for local GGUF model inference
- **Memory Module**: Historical learning, prediction tracking, tool/function calling
- **Cognition Engine**: Autonomous learning loop with self-improvement capabilities

### 2. Artifacts (Autonomous Units)
Each artifact is a self-contained operational unit with its own identity:

| Artifact | Codename | Purpose | Status | Domain |
|----------|----------|---------|--------|--------|
| Alpha | Syndicate | Market research & analysis | ✅ Production | /alpha |
| Beta | Cthulu | Trade execution (MQL5/MT5) | ✅ Staging | /beta |
| Theta | TBD | Social/Publishing | 🚧 Planned | /theta |

### 3. Infrastructure Layer
- **Infra API** (7000): Market data, assets, portfolios
- **Automata Dashboard** (5000): Control panel, orchestration
- **Frontend UI** (3000): React-based operator interface
- **Grafana** (3000 via Docker): Metrics and monitoring dashboards

---

## Data Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                      SYNDICATE PIPELINE                          │
└──────────────────────────────────────────────────────────────────┘
                              │
    ┌─────────────────────────┼─────────────────────────┐
    │                         │                         │
    ▼                         ▼                         ▼
┌──────────┐           ┌──────────┐            ┌──────────┐
│ Journals │           │ Premarket│            │Catalysts │
│ Analysis │           │ Reports  │            │ Calendar │
└────┬─────┘           └────┬─────┘            └────┬─────┘
     │                      │                       │
     └──────────────────────┼───────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │    COGNITION ENGINE     │
              │   ┌─────────────────┐   │
              │   │  Hektor VDB     │   │
              │   │  SIMD Vectors   │   │
              │   │  BM25 Hybrid    │   │
              │   └─────────────────┘   │
              │   ┌─────────────────┐   │
              │   │  llama.cpp      │   │
              │   │  GGUF Models    │   │
              │   │  Local Inference│   │
              │   └─────────────────┘   │
              └───────────┬─────────────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
    ┌─────────┐     ┌──────────┐    ┌──────────┐
    │ Context │     │ Learning │    │ Signals  │
    │ Memory  │     │ History  │    │ to Trade │
    └─────────┘     └──────────┘    └────┬─────┘
                                         │
                                         ▼
                                  ┌──────────┐
                                  │  Cthulu  │
                                  │ (Execute)│
                                  └──────────┘
```

---

## Cognition Engine Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     COGNITION ENGINE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    HEKTOR VDB                            │    │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐            │    │
│  │  │  HNSW     │  │   BM25    │  │ Hybrid    │            │    │
│  │  │  Vectors  │  │  Lexical  │  │  Search   │            │    │
│  │  └───────────┘  └───────────┘  └───────────┘            │    │
│  │  Features: SIMD, Native NLP, Gold Standard Doc Types    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   llama.cpp                              │    │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐            │    │
│  │  │ GGUF Load │  │ Inference │  │ Embeddings│            │    │
│  │  │  Models   │  │   Engine  │  │  (Local)  │            │    │
│  │  └───────────┘  └───────────┘  └───────────┘            │    │
│  │  GPU: CUDA (if available), CPU: AVX2/AVX512             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   MEMORY MODULE                          │    │
│  │  - Document ingestion (all Syndicate outputs)            │    │
│  │  - Semantic search across history                        │    │
│  │  - Context retrieval for AI analysis                     │    │
│  │  - Prediction outcome learning                           │    │
│  │  - Native tool/function calling                          │    │
│  │  - Multi-database access (read/write)                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   FALLBACK LAYER                         │    │
│  │  SQLite persistence • TF-IDF embeddings • JSON export    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Hektor VDB Capabilities

| Feature | Status | Description |
|---------|--------|-------------|
| **SIMD Optimization** | ✅ | AVX2/AVX512 vector operations |
| **HNSW Index** | ✅ | Approximate nearest neighbor search |
| **BM25 Engine** | ✅ | Lexical/keyword search |
| **Hybrid Search** | ✅ | Vector + BM25 fusion (RRF) |
| **Gold Standard Types** | ✅ | Journal, Chart, Catalyst, Calendar, etc. |
| **Native Tokenizer** | ✅ | WordPiece (BERT-compatible) |
| **llama.cpp Integration** | ✅ | Local GGUF model inference |
| **Python Bindings** | ✅ | pyvdb module for integration |
| **ONNX Runtime** | ⚠️ | Windows/MSVC only (text/image encoders) |
| **CUDA Acceleration** | 🔧 | Optional GPU support |

---

## Technology Stack

| Layer | Primary | Fallback |
|-------|---------|----------|
| **Vectorization** | Hektor VDB (C++/SIMD) | hnswlib + TF-IDF |
| **Embeddings** | llama.cpp (native) | TF-IDF sklearn |
| **LLM Inference** | llama.cpp (GGUF) | Ollama → Gemini API |
| **Persistence** | Hektor native storage | SQLite + JSON |
| **API Framework** | FastAPI | Flask |
| **Frontend** | React + Vite | Grafana |
| **Trading** | MQL5/MetaTrader 5 | - |
| **Infrastructure** | GCP + Docker | systemd |

---

## Document Types (Gold Standard)

Hektor VDB supports typed document storage for Syndicate outputs:

| Type | Enum | Description |
|------|------|-------------|
| `Journal` | Journal | Daily/weekly market journals |
| `Chart` | Chart | Annotated chart analysis |
| `CatalystWatchlist` | CatalystWatchlist | Upcoming market catalysts |
| `EconomicCalendar` | EconomicCalendar | Economic event schedules |
| `PreMarket` | PreMarket | Pre-market analysis reports |
| `WeeklyRundown` | WeeklyRundown | Weekly market summaries |
| `MonthlyReport` | MonthlyReport | Monthly analysis |
| `ThreeMonthReport` | ThreeMonthReport | Quarterly outlook |
| `OneYearReport` | OneYearReport | Annual predictions |
| `InstitutionalMatrix` | InstitutionalMatrix | Institutional flow analysis |

---

## Future: Web3 Integration

| Component | Domain | Purpose |
|-----------|--------|---------|
| Gladius Core | artifactvirtual.com | Enterprise governance |
| Alpha (Syndicate) | /alpha | Research signal access |
| Beta (Cthulu) | /beta | Trading profit sharing |
| Theta | /theta | Content monetization |

Each artifact will have:
- **Blockchain integration** for transparency
- **Utility tokens** for access/governance
- **Soulbound tokens (SBT)** for reputation
- **Native GGUF/GGM models** for artifact-specific AI

---

## File Structure

```
gladius/
├── Artifact/
│   ├── syndicate/             # Alpha: Research engine
│   │   ├── src/
│   │   │   └── cognition/     # Vector memory system
│   │   │       ├── embedder.py
│   │   │       ├── vector_store.py    # hnswlib fallback
│   │   │       ├── hektor_store.py    # Native Hektor VDB
│   │   │       └── syndicate_integration.py
│   │   ├── main.py            # Core daemon
│   │   └── output/            # Generated reports
│   ├── hektor/                # Native VDB (C++)
│   │   ├── src/               # Core implementation
│   │   ├── include/vdb/       # Headers
│   │   ├── bindings/python/   # pyvdb module
│   │   └── build/             # Compiled artifacts
│   ├── deployment/
│   │   ├── infra/             # Market/Portfolio API
│   │   └── automata/          # Dashboard & orchestration
│   └── arty/                  # Automation framework
├── RESEARCH/                  # Articles & papers
├── docs/                      # Documentation
├── gladius.sh                 # Unified control script
├── ARCHITECTURE.md            # This file
├── COMMANDS.md                # Command reference
└── CONTEXT.md                 # Operational context
```

---

*Last updated: 2026-01-13*
