# GLADIUS

<p align="center">
  <img src="https://img.shields.io/badge/Language-C++-blue.svg" alt="C++">
  <img src="https://img.shields.io/badge/Python-3.10+-yellow.svg" alt="Python">
  <img src="https://img.shields.io/badge/AI-Native-brightgreen.svg" alt="Native AI">
  <img src="https://img.shields.io/badge/VectorDB-Hektor-informational.svg" alt="Hektor VDB">
</p>

> **Autonomous Enterprise Operating System** with fully native AI—no external API dependencies.

---

## Overview

Gladius manages multiple business artifacts through unified cognition, native vectorization, and semantic memory. Core features:

- **Hektor VDB**: Native C++ SIMD-optimized vector database
- **Native Tool Router**: Sub-10ms tool selection without external LLMs
- **Memory Module**: 16 tools for multi-database access
- **Consensus System**: Discord voting + email escalation for proposals
- **Context Manager**: Maintains coherent narrative across long sessions
- **Self-Improvement**: Autonomous proposal and implementation system

---

## Quick Start

```bash
# Start all services
./gladius.sh start

# Check status
./gladius.sh status

# Run a learning cycle
cd Artifact/syndicate && python -c "
from src.cognition import CognitionLearningLoop
with CognitionLearningLoop('.') as loop:
    result = loop.run_cycle()
    print(result)
"
```

---

## Architecture

```
GLADIUS
├── Cognition Engine
│   ├── Hektor VDB (SIMD vectors, hybrid search)
│   ├── Native Tool Router (<10ms routing)
│   ├── Memory Module (16 tools, multi-DB)
│   ├── Consensus System (Discord/Email)
│   └── Context Manager (Summarization)
├── Model Stack
│   ├── Native GGUF (<10ms) - Training
│   ├── Pattern Fallback (<1ms) - Active
│   └── Ollama (~100ms) - Fallback
└── Artifacts
    ├── Alpha (Syndicate) - Research
    ├── Beta (Cthulu) - Trading
    └── Theta (Future) - Publishing
```

---

## Cognition Engine

### Components

| Component | Purpose | Status |
|-----------|---------|--------|
| Hektor VDB | Native SIMD vector database | ✅ Production |
| Tool Router | Pattern-based tool selection | ✅ Production |
| Memory Module | Multi-DB access (16 tools) | ✅ Production |
| Training Generator | Fine-tuning data creation | ✅ Production |
| Self-Improvement | Autonomous proposals | ✅ Production |
| Learning Loop | Continuous improvement | ✅ Production |
| Consensus System | Discord/Email routing | ✅ Production |
| Context Manager | Narrative coherence | ✅ Production |

### Usage

```python
from cognition import (
    MemoryModule, 
    ConsensusSystem, 
    ContextManager,
    SelfImprovementEngine
)

# Memory with tool calling
memory = MemoryModule()
result = memory.execute_tool("hybrid_search", {"query": "gold analysis", "k": 5})

# Consensus for proposals
consensus = ConsensusSystem()
await consensus.route_proposal(
    proposal_id="prop_001",
    title="Improve accuracy",
    impact_level="medium"  # -> Discord vote
)

# Context management
context = ContextManager()
context.add_event("Market opened bullish")
context.add_decision("Hold positions")
window = context.get_context_window()

# Self-improvement
engine = SelfImprovementEngine()
proposal = engine.create_proposal(
    title="Add compound query patterns",
    category="accuracy"
)
```

---

## Model Evolution

| Phase | Model | Capability | Status |
|-------|-------|------------|--------|
| **1** | Ollama + Patterns | Tool routing | ✅ Production |
| **2** | Fine-tuned GGUF | Native routing <10ms | 🚧 Training |
| **3** | Gladius Native | Full autonomy | 📋 Planned |

See [MODEL.md](MODEL.md) for complete native AI strategy.

---

## Documentation

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System diagrams and flow |
| [CONTEXT.md](CONTEXT.md) | Operational context |
| [MANDATE.md](MANDATE.md) | Mission and responsibilities |
| [MODEL.md](MODEL.md) | Native AI model strategy |
| [COMMANDS.md](COMMANDS.md) | CLI commands reference |
| [SNAPSHOT.md](SNAPSHOT.md) | System benchmarks |

---

## Directory Structure

```
gladius/
├── Artifact/
│   ├── syndicate/       # Research pipeline
│   │   └── src/cognition/  # Cognition engine
│   ├── hektor/          # Native vector database
│   ├── deployment/      # Infrastructure
│   └── arty/            # Automation (Discord, etc)
├── gladius.sh           # Main control script
├── ARCHITECTURE.md      # System architecture
├── CONTEXT.md           # Operational context
├── MANDATE.md           # System mandate
└── MODEL.md             # AI model strategy
```

---

## License

See [LICENSE.md](LICENSE.md)

---

*Last updated: 2026-01-13*

