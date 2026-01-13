# Gladius

> Autonomous Enterprise Operating System with Native AI

An autonomous enterprise system evolving toward **fully native AI** - no external API dependencies. Manages multiple artifacts (business units) through unified cognition, native vectorization, and semantic memory. Features native C++ vector database (Hektor), native tool routing, and autonomous learning.

---

## 🚀 Quick Start

```bash
cd /home/adam/worxpace/gladius

# Start all services
./gladius.sh start

# Check status
./gladius.sh status

# Stop services
./gladius.sh stop
```

**Access Points**:
| Service | URL | Credentials |
|---------|-----|-------------|
| Dashboard | http://localhost:3000 | admin / gladius |
| API Docs | http://localhost:7000/docs | - |
| Grafana | http://localhost:3001 | admin / admin |

---

## 📋 Documentation

| Document | Purpose |
|----------|---------|
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System architecture & component design |
| **[MODEL.md](MODEL.md)** | Native AI model strategy & training pipeline |
| **[COMMANDS.md](COMMANDS.md)** | Complete command reference |
| **[CONTEXT.md](CONTEXT.md)** | Current operational context |
| **[MANDATE.md](MANDATE.md)** | Operational mandate |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         GLADIUS                                  │
│              (Autonomous Enterprise Manager)                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │  Hektor VDB   │  │ Native Router │  │ Memory Module │       │
│  │  SIMD/HNSW    │  │  (tool <10ms) │  │  (16 tools)   │       │
│  └───────────────┘  └───────────────┘  └───────────────┘       │
│  ┌───────────────────────────────────────────────────────┐     │
│  │                    MODEL STACK                         │     │
│  │  Native GGUF (<10ms) → Ollama (~100ms) → Fallback     │     │
│  └───────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
  │   ALPHA     │      │    BETA     │      │   THETA     │
  │  Syndicate  │      │   Cthulu    │      │  (Future)   │
  │  Research   │      │   Trading   │      │  Publishing │
  └─────────────┘      └─────────────┘      └─────────────┘
```

---

## 🧠 Native AI Model Stack

The system is evolving toward fully native AI (see [MODEL.md](MODEL.md)):

| Layer | Component | Latency | Status |
|-------|-----------|---------|--------|
| **Tool Routing** | Native GGUF | <10ms | 🚧 Training ready |
| **Fallback** | Pattern Match | <1ms | ✅ Working |
| **Reasoning** | Ollama | ~100ms | ✅ Production |
| **Embeddings** | TF-IDF + Hektor | <5ms | ✅ Production |

**Evolution Path:**
```
Phase 1 (current) → Phase 2 (next) → Phase 3 (target)
Ollama + patterns → Fine-tuned GGUF → Gladius Native (full autonomy)
```

---

## ⚙️ Core Systems

| System | Port | Status | Description |
|--------|------|--------|-------------|
| **Hektor VDB** | - | ✅ Production | Native C++ vectors (SIMD, HNSW, BM25) |
| **Native Router** | - | ✅ Implemented | Tool routing (<10ms target) |
| **Memory Module** | - | ✅ Production | 16 tools, multi-DB access |
| **Infra API** | 7000 | ✅ Production | Market data, portfolios |
| **Dashboard** | 5000 | ✅ Production | Control panel |
| **Syndicate** | - | ✅ Production | Market intelligence |
| **Cthulu** | - | ✅ Staging | MQL5/MT5 trading |

---

## 🔧 Quick Examples

### Hektor VDB (Native Vectors)

```bash
cd Artifact/hektor && mkdir build && cd build
cmake .. -DVDB_BUILD_PYTHON=ON && make -j$(nproc)
```

```python
from cognition.hektor_store import get_vector_store
store = get_vector_store("./vectors", dim=384)
store.add_text("doc1", "Gold broke above resistance")
results = store.hybrid_search("gold breakout", k=5)
```

### Native Tool Router

```python
from cognition import NativeToolRouter

router = NativeToolRouter()
result = router.route("Search for gold analysis")
print(f"Tool: {result.tool_name}, Confidence: {result.confidence}")
```

### Memory Module

```python
from cognition import MemoryModule

mm = MemoryModule(base_dir='.')
mm.call_tool('search', query='gold bullish', k=5)
mm.remember('pattern', 'Head and shoulders at 2700')
mm.recall('gold patterns', k=3)
```

### Learning Loop

```python
from cognition import CognitionLearningLoop

with CognitionLearningLoop('.') as loop:
    result = loop.run_cycle(current_gold_price=2690.0)
    print(f"Training examples: {result.training_examples_generated}")
```

---

## 📊 Training Pipeline

Generate training data for native models:

```python
from cognition import TrainingDataGenerator

gen = TrainingDataGenerator('./data/training')
dataset = gen.generate_synthetic(n_per_category=100)
gen.export_all([dataset], formats=['llama'])
```

Fine-tune with LoRA (see [MODEL.md](MODEL.md) for details):
```bash
llama-finetune --model-base smollm2-135m.gguf \
    --train-data combined.jsonl --lora-r 8 --epochs 3
```

---

## 🎯 Roadmap

| Phase | Target | Status |
|-------|--------|--------|
| **Phase 2.1** | Native tool router GGUF | Q1 2026 |
| **Phase 2.2** | Domain specialist (gold/trading) | Q2 2026 |
| **Phase 3** | Gladius Native (full autonomy) | Q3-Q4 2026 |

---

*See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design.*
*See [MODEL.md](MODEL.md) for native AI strategy.*
*See [COMMANDS.md](COMMANDS.md) for complete reference.*

---

*Last updated: 2026-01-13*
