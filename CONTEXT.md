# System Context

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
├── consensus.py             # Discord voting + email escalation
├── context/                 # Context management
│   ├── __init__.py
│   └── context_manager.py   # Summarization + coherence
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
| Consensus System | ✅ Working | Discord voting, email escalation |
| Context Manager | ✅ Working | Summarization, coherence |

---

## Consensus System

Routes proposals based on impact level:

| Impact | Routing | Approval |
|--------|---------|----------|
| Low | Auto-approve | Immediate |
| Medium | Discord community vote | 60% threshold |
| High | Email to dev team | Manual review |
| Critical | Email to executives | Escalated review |

```python
from cognition import ConsensusSystem

cs = ConsensusSystem()
await cs.route_proposal(
    proposal_id='prop_001',
    title='Improve prediction accuracy',
    summary='Need to enhance pattern recognition',
    impact_level='medium'
)
# -> Creates Discord voting session
```

---

## Context Management

Maintains coherent narrative through:
- **Auto-summarization** when context exceeds threshold
- **Importance-based pruning** for low-value entries
- **Version history** for rollback
- **Training export** from context decisions

```python
from cognition import ContextManager

cm = ContextManager(max_tokens=8000)
cm.add_event('Market opened bullish')
cm.add_learning('RSI divergence confirmed')
cm.add_decision('Hold current positions')

context = cm.get_context_window()
# Formatted context with summaries + recent entries
```

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
| Consensus sessions | 1 test | Production ready |

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

# Run learning cycle
cd Artifact/syndicate && python -c "
from src.cognition import CognitionLearningLoop
with CognitionLearningLoop('.') as loop:
    result = loop.run_cycle()
"
```

---

## Immediate Next Steps

1. ~~Implement Consensus System~~ ✅ Done
2. ~~Implement Context Manager~~ ✅ Done
3. **Configure Discord webhook** for community voting
4. **Configure SMTP** for email escalation
5. **Run autonomous improvement cycle** to verify self-improvement

---

*Last updated: 2026-01-13*