# Gladius Context

> Operational context for the Gladius autonomous enterprise system

---

## System Overview

Gladius is an autonomous enterprise operating system evolving toward **full native AI** - no external API dependencies. It manages multiple artifacts (autonomous business units) through a unified cognition layer.

- **Root**: `/home/adam/worxpace/gladius`
- **Primary Domain**: artifactvirtual.com (planned)
- **Cognition Backend**: Hektor VDB + Native Tool Router + Ollama (transitional)

---

## Current State

### Model Stack

| Layer | Component | Speed | Status |
|-------|-----------|-------|--------|
| Tool Routing | Native GGUF (target) | <10ms | 🚧 Training pipeline ready |
| Tool Routing | Pattern fallback | <1ms | ✅ Working |
| Reasoning | Ollama (llama3.2) | ~100ms | ✅ Production |
| Embeddings | TF-IDF + Hektor | <5ms | ✅ Production |
| Vectors | Hektor VDB (SIMD) | <1ms | ✅ Production |

### Active Artifacts

| Artifact | Purpose | Status | Cognition |
|----------|---------|--------|-----------|
| **Alpha (Syndicate)** | Market research | ✅ Production | Hektor + native tools |
| **Beta (Cthulu)** | Trade execution | ✅ Staging | Pending integration |
| **Infrastructure** | APIs, Dashboard | ✅ Production | N/A |

### Services

| Service | Port | Status |
|---------|------|--------|
| Infra API | 7000 | ✅ Running |
| Dashboard API | 5000 | ✅ Running |
| Dashboard UI | 3000 | ○ On-demand |
| Grafana | 3001 | ✅ Running |

---

## Cognition Engine Components

```
Location: Artifact/syndicate/src/cognition/
├── __init__.py              # Module exports
├── embedder.py              # TF-IDF embeddings
├── vector_store.py          # hnswlib fallback
├── hektor_store.py          # Native Hektor VDB
├── memory_module.py         # Multi-DB access, tool execution
├── tool_calling.py          # Tool definitions & registry
├── syndicate_integration.py # Report ingestion, prediction learning
├── training_generator.py    # Fine-tuning data generation
├── self_improvement.py      # Autonomous improvement proposals
├── learning_loop.py         # Continuous learning cycle
└── native_model/            # Native AI models
    ├── __init__.py
    ├── router.py            # NativeToolRouter
    └── trainer.py           # ModelTrainer for GGUF
```

### Features Status

| Feature | Status | Notes |
|---------|--------|-------|
| Hektor VDB | ✅ Working | SIMD vectors, hybrid search |
| Memory Module | ✅ Working | 11/11 tools passing |
| Tool Calling | ✅ Working | 16 tools registered |
| Native Router | ✅ Implemented | Pattern fallback active |
| Model Trainer | ✅ Implemented | Ready for fine-tuning |
| Training Data | ✅ Generating | 155+ examples collected |
| Learning Loop | ✅ Working | 5 cycle benchmark complete |
| Self-Improvement | ✅ Working | Proposal pipeline ready |

---

## Training & Learning

### Data Generation

```python
from cognition import TrainingDataGenerator

gen = TrainingDataGenerator('./data/training')
dataset = gen.generate_from_history(memory.history)
dataset += gen.generate_synthetic(n_per_category=100)
gen.export(dataset, format='llama')
```

### Model Training (Planned)

```bash
# Download base model
# Fine-tune with LoRA
# Quantize to Q4_K_M
# Deploy as tool-router.gguf
```

### Learning Loop

```python
from cognition import CognitionLearningLoop

with CognitionLearningLoop('.') as loop:
    result = loop.run_cycle(current_gold_price=2690.0)
    # Ingests reports → generates training data → proposes improvements
```

---

## Model Evolution

See `MODEL.md` for complete native AI strategy.

| Phase | Model | Capability | Target |
|-------|-------|------------|--------|
| **Phase 1** (current) | Ollama + patterns | Tool routing, analysis | ✅ Working |
| **Phase 2** (next) | SmolLM2-135M GGUF | Native tool routing (<10ms) | Q1 2026 |
| **Phase 3** (target) | Gladius Native 1-3B | Full autonomy | Q3-Q4 2026 |

---

## Key Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Tool routing latency | ~50ms (pattern) | <10ms (native) |
| Tool routing accuracy | ~60% (pattern) | >95% (trained) |
| Documents indexed | 18+ | Growing |
| Training examples | 155+ | 1000+ |
| Prediction win rate | 55% | >65% |
| Memory module tools | 11/11 passing | All |
| Self-improvement proposals | Pipeline ready | Autonomous |

---

## Immediate Next Steps

1. **Download SmolLM2-135M GGUF** - Base model for tool router
2. **Generate 1000+ training examples** - From history + synthetic
3. **Fine-tune with LoRA** - 8 rank, 3 epochs
4. **Integrate native router** - Replace pattern fallback
5. **Benchmark latency/accuracy** - vs Ollama

---

*Last updated: 2026-01-13*

engine = SelfImprovementEngine(base_dir='.')

# Create proposal
proposal = engine.create_proposal(
    title='Improve prediction accuracy',
    category=ImprovementCategory.ACCURACY,
    summary='Need to improve pattern recognition',
    items=[{'description': 'Analyze failures', 'impact': 'high'}]
)

# Review and approve
engine.submit_for_review(proposal.id)
engine.review_proposal(proposal.id, 'cognition', 'approve', 'Looks good')

# Create implementation plan
engine.create_implementation_plan(
    proposal.id,
    plan='Detailed plan...',
    checklist_items=['Task 1', 'Task 2', 'Verify']
)

# Execute with snapshots
engine.begin_implementation(proposal.id)
engine.complete_task(proposal.id, 'check_0', 'Done')
engine.complete_implementation(proposal.id)
```

### Learning Loop
Continuous autonomous learning:

```python
from cognition import CognitionLearningLoop

with CognitionLearningLoop(base_dir='.') as loop:
    # Single cycle
    result = loop.run_cycle(current_gold_price=2690.0)
    
    # Benchmark with 10 cycles
    benchmark = loop.run_benchmark(n_cycles=10)
    print(f"Win rate: {benchmark['initial_metrics']['win_rate']} -> {benchmark['final_metrics']['win_rate']}")
```

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

### Native Tool Calling
The cognition engine learns to use tools natively, not through third-party LLMs:

| Tool | Category | Description |
|------|----------|-------------|
| `read_db(name, query)` | database | Read from any connected database |
| `write_db(name, data)` | database | Write to any connected database |
| `query_db(name, query)` | database | Execute raw database query |
| `list_databases()` | database | List all connected databases |
| `search(query, k)` | search | Semantic search across vectors |
| `hybrid_search(query, k)` | search | Vector + BM25 fusion search |
| `get_context(query)` | search | Retrieve historical context |
| `read_file(path)` | workspace | Read file from workspace |
| `write_file(path, data)` | workspace | Write file to workspace |
| `list_dir(path)` | workspace | List directory contents |
| `file_exists(path)` | workspace | Check if file exists |
| `remember(key, value)` | memory | Store memory for recall |
| `recall(query, k)` | memory | Recall related memories |
| `forget(key)` | memory | Remove a memory |
| `get_tools()` | introspection | List available tools |
| `get_history(n)` | introspection | Get operation history |

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
- Memory Module with unified database access
- Native tool calling (16 tools implemented)
- Prediction learning with feedback loops
- Pattern success rate analysis
- Historical outcome similarity search
- Adaptive recommendations based on history

### 🚧 In Progress
- Workspace access for self-improvement
- Artifact-specific GGUF/GGM model training

### 📋 Planned
- Full autonomous learning loop
- Web3 integration per artifact
- Social/publishing pipeline (Theta)
- Blockchain and SBT integration

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