# Gladius Architecture

> Autonomous Enterprise Operating System with Native AI

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              GLADIUS                                        │
│                    (Autonomous Enterprise Manager)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       COGNITION ENGINE                               │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │   │
│  │  │ Hektor VDB  │  │ Native Tool │  │   Memory    │  │  Learning  │  │   │
│  │  │ SIMD/HNSW   │  │   Router    │  │   Module    │  │    Loop    │  │   │
│  │  │ Vectors     │  │   (<10ms)   │  │  Multi-DB   │  │  Training  │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘  │   │
│  │                           │                                          │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │                    MODEL STACK                               │    │   │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │    │   │
│  │  │  │ Tool Router │  │ Ollama LLM  │  │  Gladius Native     │  │    │   │
│  │  │  │ (tiny GGUF) │  │ (fallback)  │  │  (future: full)     │  │    │   │
│  │  │  │   <10ms     │  │   ~100ms    │  │   <50ms all tasks   │  │    │   │
│  │  │  └─────────────┘  └─────────────┘  └─────────────────────┘  │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           │                        │                        │
           ▼                        ▼                        ▼
    ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
    │  ARTIFACT   │          │  ARTIFACT   │          │  ARTIFACT   │
    │   ALPHA     │          │    BETA     │          │   THETA     │
    │  Syndicate  │          │   Cthulu    │          │  (Future)   │
    │  Research   │          │   Trading   │          │ Publishing  │
    └─────────────┘          └─────────────┘          └─────────────┘
```

---

## Core Components

### 1. Cognition Engine

The brain of Gladius - provides semantic memory, native AI inference, and autonomous learning.

| Component | Purpose | Status |
|-----------|---------|--------|
| **Hektor VDB** | SIMD-optimized vectors, hybrid search | ✅ Production |
| **Native Tool Router** | Route queries to tools (<10ms) | ✅ Implemented |
| **Memory Module** | Multi-DB access, tool calling, history | ✅ Production |
| **Learning Loop** | Continuous training, self-improvement | ✅ Implemented |
| **Model Trainer** | Fine-tune GGUF models from history | ✅ Implemented |

### 2. Model Stack (see MODEL.md for details)

```
Layer 1: Native GGUF    ──► Tool routing (target: <10ms)
Layer 2: Ollama         ──► Complex reasoning (fallback: ~100ms)  
Layer 3: Gladius Native ──► Full autonomy (future: <50ms all tasks)
```

**Evolution Path:**
- Phase 1 (current): Ollama + pattern fallback
- Phase 2 (next): Fine-tuned tool router GGUF
- Phase 3 (target): Full native model, no external dependencies

### 3. Artifacts (Autonomous Business Units)

| Artifact | Codename | Purpose | Status | Domain |
|----------|----------|---------|--------|--------|
| Alpha | Syndicate | Market research & analysis | ✅ Production | /alpha |
| Beta | Cthulu | Trade execution (MQL5/MT5) | ✅ Staging | /beta |
| Theta | TBD | Social/Publishing | 🚧 Planned | /theta |

### 4. Infrastructure Layer

| Service | Port | Purpose |
|---------|------|---------|
| Infra API | 7000 | Market data, assets, portfolios |
| Dashboard Backend | 5000 | Automata control, content |
| Dashboard Frontend | 3000 | React operator interface |
| Grafana | 3001 | Metrics dashboards |

---

## Data Flow

```
Market Sources (yfinance, FRED)
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                    SYNDICATE PIPELINE                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Journals │  │ Premarket│  │ Catalysts│  │ Calendar │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       └─────────────┼───────────────┼───────────────┘       │
└─────────────────────┼───────────────┼───────────────────────┘
                      ▼               │
         ┌────────────────────────────┼──────────────────┐
         │       COGNITION ENGINE     │                  │
         │  ┌──────────────────────┐  │                  │
         │  │    NativeToolRouter  │◄─┘                  │
         │  │   (route → execute)  │                     │
         │  └──────────┬───────────┘                     │
         │             ▼                                 │
         │  ┌──────────────────────┐                     │
         │  │     Hektor VDB       │                     │
         │  │  (ingest → search)   │                     │
         │  └──────────┬───────────┘                     │
         │             ▼                                 │
         │  ┌──────────────────────┐                     │
         │  │   TrainingGenerator  │                     │
         │  │ (history → dataset)  │                     │
         │  └──────────┬───────────┘                     │
         │             ▼                                 │
         │  ┌──────────────────────┐                     │
         │  │    ModelTrainer      │                     │
         │  │  (train → deploy)    │                     │
         │  └──────────────────────┘                     │
         └───────────────────────────────────────────────┘
                      │
                      ▼
              Trade Signals → Cthulu → Execution
```

---

## Technology Stack

### Native AI (No External APIs)
- **llama.cpp**: GGUF model inference, fine-tuning
- **Hektor VDB**: SIMD vectors, hybrid search, ONNX encoders
- **pyvdb**: Python bindings for Hektor

### Python Backend
- **FastAPI**: REST APIs (Infra, Dashboard)
- **SQLite**: Lightweight persistence
- **hnswlib**: Fallback vector search
- **scikit-learn**: TF-IDF embeddings

### External (Being Replaced)
- **Ollama**: Local LLM inference (→ replaced by native GGUF)
- **Google Genai**: Cloud fallback (→ phased out)

---

## File Structure

```
gladius/
├── gladius.sh              # Unified control script
├── ARCHITECTURE.md         # This file
├── MODEL.md               # Native AI model strategy
├── COMMANDS.md            # Operator reference
├── CONTEXT.md             # Operational context
├── README.md              # Quick start
│
├── Artifact/
│   ├── syndicate/         # Alpha: Market research
│   │   ├── main.py        # Analysis pipeline
│   │   ├── run.py         # Daemon runner
│   │   ├── src/
│   │   │   └── cognition/ # Cognition engine
│   │   │       ├── native_model/  # Tool router + trainer
│   │   │       ├── hektor_store.py
│   │   │       ├── memory_module.py
│   │   │       ├── learning_loop.py
│   │   │       └── ...
│   │   ├── data/          # Databases, vectors, training
│   │   ├── output/        # Reports, charts, journals
│   │   └── models/        # GGUF models, LoRA adapters
│   │
│   ├── deployment/        # Infrastructure
│   │   ├── infra/         # FastAPI backend
│   │   └── automata/      # Dashboard
│   │
│   └── hektor/            # Native vector database
│       ├── src/           # C++ core
│       ├── bindings/      # Python (pyvdb)
│       └── build/         # Compiled artifacts
│
├── projects/              # External project links
│   ├── goldmax/           # Market memory
│   ├── herald/            # Execution agent
│   └── cthulu/            # MQL5 trading
│
└── obsidian_sync/         # Research knowledge base
```

---

*See MODEL.md for detailed native AI architecture and training pipeline.*
*See COMMANDS.md for operational commands.*
*See CONTEXT.md for current system state.*
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
│  │                   INFERENCE LAYER                        │    │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐            │    │
│  │  │ llama.cpp │  │   ONNX    │  │ Native    │            │    │
│  │  │ GGUF/GGM  │  │  Runtime  │  │ Embeddings│            │    │
│  │  └───────────┘  └───────────┘  └───────────┘            │    │
│  │  GPU: CUDA (if available), CPU: AVX2/AVX512             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   MEMORY MODULE                          │    │
│  │  ┌─────────────────────────────────────────────────┐    │    │
│  │  │  Multi-Database Access                           │    │    │
│  │  │  • Hektor VDB (vectors)  • SQLite (relational)   │    │    │
│  │  │  • JSON stores           • Prediction history    │    │    │
│  │  └─────────────────────────────────────────────────┘    │    │
│  │  ┌─────────────────────────────────────────────────┐    │    │
│  │  │  Native Tool Calling                             │    │    │
│  │  │  • DB read/write         • File operations       │    │    │
│  │  │  • Semantic search       • Context retrieval     │    │    │
│  │  │  • Workspace management  • Structure learning    │    │    │
│  │  └─────────────────────────────────────────────────┘    │    │
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
| **llama.cpp Integration** | ✅ | Local GGUF model inference (b7716) |
| **Python Bindings** | ✅ | pyvdb module for integration |
| **ONNX Runtime** | ✅ | Text/image encoders (libonnxruntime-dev) |
| **CUDA Acceleration** | 🔧 | Optional GPU support |

---

## Memory Module Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      MEMORY MODULE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐  ┌──────────────────────┐             │
│  │   UNIFIED MEMORY     │  │   DATABASE HOOKS     │             │
│  │   INTERFACE          │  │                      │             │
│  │                      │  │  ┌────────────────┐  │             │
│  │  • Query routing     │  │  │ Hektor VDB     │  │             │
│  │  • Context assembly  │  │  │ (vectors)      │  │             │
│  │  • Tool dispatch     │  │  └────────────────┘  │             │
│  │  • Response merge    │  │  ┌────────────────┐  │             │
│  │                      │  │  │ SQLite DBs     │  │             │
│  └──────────────────────┘  │  │ (relational)   │  │             │
│                            │  └────────────────┘  │             │
│  ┌──────────────────────┐  │  ┌────────────────┐  │             │
│  │   NATIVE TOOL        │  │  │ JSON stores    │  │             │
│  │   CALLING            │  │  │ (configs)      │  │             │
│  │                      │  │  └────────────────┘  │             │
│  │  • read_db(name, q)  │  └──────────────────────┘             │
│  │  • write_db(name, d) │                                       │
│  │  • search(query, k)  │  ┌──────────────────────┐             │
│  │  • read_file(path)   │  │   WORKSPACE ACCESS   │             │
│  │  • write_file(p, d)  │  │                      │             │
│  │  • list_dir(path)    │  │  • Sandboxed access  │             │
│  │  • get_context(q)    │  │  • File operations   │             │
│  │                      │  │  • Structure learn   │             │
│  └──────────────────────┘  └──────────────────────┘             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Primary | Fallback |
|-------|---------|----------|
| **Vectorization** | Hektor VDB (C++/SIMD) | hnswlib + TF-IDF |
| **Embeddings** | ONNX Runtime + llama.cpp | TF-IDF sklearn |
| **LLM Inference** | llama.cpp (GGUF) | Ollama → Gemini API |
| **Persistence** | Hektor native + SQLite | JSON export |
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
| `Outcome` | Outcome | Prediction outcomes for learning |

---

## Prediction Learning System

The cognition engine learns from predictions through a feedback loop:

```
┌─────────────────────────────────────────────────────────────────┐
│                   PREDICTION LEARNING LOOP                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│   │   Market     │────▶│   Predict    │────▶│   Record     │    │
│   │   Analysis   │     │   Bias       │     │   Outcome    │    │
│   └──────────────┘     └──────────────┘     └──────┬───────┘    │
│          ▲                                         │            │
│          │                                         ▼            │
│   ┌──────┴───────┐                        ┌──────────────┐      │
│   │   Pattern    │◀───────────────────────│   Grade      │      │
│   │   Feedback   │                        │   Performance│      │
│   └──────────────┘                        └──────────────┘      │
│                                                                  │
│   Features:                                                      │
│   • Pattern success rate analysis                                │
│   • Similar historical outcomes search                           │
│   • Adaptive recommendations                                     │
│   • Confidence scoring with streak tracking                      │
│   • Learning feedback generation for AI context                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Learning Methods

| Method | Purpose |
|--------|---------|
| `learn_from_prediction()` | Record prediction outcomes with context |
| `get_similar_historical_outcomes()` | Find similar market conditions |
| `get_pattern_success_rate()` | Calculate pattern reliability |
| `generate_learning_feedback()` | Generate AI context from history |
| `get_prediction_accuracy()` | Comprehensive accuracy statistics |

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
│   │   │       ├── memory_module.py   # Unified memory access
│   │   │       ├── tool_calling.py    # Native tool definitions
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

## Training & Self-Improvement System

The system now includes autonomous learning capabilities:

```
┌─────────────────────────────────────────────────────────────────┐
│                   LEARNING LOOP                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│   │   Ingest     │────▶│   Generate   │────▶│   Propose    │    │
│   │   Reports    │     │   Training   │     │   Improve    │    │
│   └──────────────┘     │   Data       │     └──────┬───────┘    │
│                        └──────────────┘            │            │
│                                                    ▼            │
│   ┌──────────────┐                        ┌──────────────┐      │
│   │   Snapshot   │◀───────────────────────│   Execute    │      │
│   │   Benchmark  │                        │   Changes    │      │
│   └──────────────┘                        └──────────────┘      │
│                                                                  │
│   Components:                                                    │
│   • TrainingDataGenerator - Generate fine-tuning data           │
│   • SelfImprovementEngine - Proposal lifecycle with audit       │
│   • CognitionLearningLoop - Autonomous learning cycles          │
│   • Snapshot management for rollback                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Training Data Generation

| Format | Description | Use Case |
|--------|-------------|----------|
| Chat | Conversational format | Instruction tuning |
| Completion | Prompt-completion pairs | Causal LM training |
| llama.cpp | llama.cpp specific JSON | GGUF fine-tuning |
| Tool | OpenAI tool-calling format | Function calling |

### Self-Improvement Workflow

1. **Proposal Creation** → Draft with items, rationale, risk
2. **Review Cycle** → Approve, request changes, or reject
3. **Implementation Plan** → Checklist, blueprint, execution plan
4. **Execution** → Pre/post snapshots, task tracking
5. **Completion** → Audit trail preserved

### Improvement Categories

| Category | Description |
|----------|-------------|
| COGNITION | Core reasoning and analysis |
| MEMORY | Database and storage |
| TOOLS | Tool calling capabilities |
| STRUCTURE | File and code organization |
| AUTOMATION | Workflow automation |
| PERFORMANCE | Speed and efficiency |
| ACCURACY | Prediction improvement |
| DOCUMENTATION | Docs and guides |

---

*Last updated: 2026-01-13*
