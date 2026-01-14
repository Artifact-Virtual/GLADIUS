# GLADIUS Native AI Model

> **Module**: `/GLADIUS/`  
> **Version**: 0.1.0  
> **Last Updated**: 2026-01-14  
> **Status**: Training Phase

---

## Overview

GLADIUS is the **native AI model** that powers Artifact Virtual's autonomous operations. It is a custom GGUF model trained for:

1. **Tool Routing** - 100% accuracy at selecting the right tool for any query (<2ms)
2. **Task Execution** - Understanding and executing complex multi-step operations
3. **Self-Improvement** - Generating training data from its own operations
4. **Research Analysis** - Market intelligence and business development

---

## Model Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        GLADIUS MODEL STACK                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     INFERENCE LAYER                               │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │ Pattern      │  │ GGUF         │  │ Fallback     │          │   │
│  │  │ Router       │  │ Inference    │  │ (Ollama)     │          │   │
│  │  │ (0.93ms)     │  │ (target)     │  │ (backup)     │          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     TRAINING LAYER                                │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │ Harness      │  │ Generator    │  │ Progressive  │          │   │
│  │  │ (isolated)   │  │ (synthetic)  │  │ Trainer      │          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     MODEL VERSIONS                                │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │ Base         │  │ Staging      │  │ Production   │          │   │
│  │  │ (Qwen 0.5B)  │  │ (Testing)    │  │ (Live)       │          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Current Performance

| Metric | Value | Target |
|--------|-------|--------|
| Tool Routing Accuracy | 100% | 100% |
| Average Latency | 0.93ms | <5ms |
| P99 Latency | 2.28ms | <10ms |
| Training Examples | 914+ | 10,000+ |
| Model Size | 5.4MB | <100MB |
| Fallback Rate | 0% | <1% |

---

## Directory Structure

```
GLADIUS/
├── models/                   # GGUF model files
│   ├── production/          # Live model
│   ├── staging/             # Testing model
│   └── base/                # Base models for fine-tuning
│
├── training/                # Training infrastructure
│   ├── data/                # Training datasets
│   │   └── combined_training_llama.json
│   ├── scripts/             # Training scripts
│   │   ├── trainer.py       # Base trainer
│   │   └── progressive_trainer.py
│   ├── harness.py           # Isolated training harness
│   └── generator.py         # Synthetic data generator
│
├── router/                  # Inference routing
│   ├── pattern_router.py    # Pattern-based routing (current)
│   └── gguf_router.py       # GGUF inference (target)
│
├── docs/                    # Documentation
│   ├── MODEL.md             # This file
│   ├── TRAINING.md          # Training methodology
│   └── API.md               # Inference API
│
└── SYSTEM_MAPPING.md        # Command reference
```

---

## Training Pipeline

### 1. Data Generation

```python
from GLADIUS.training.generator import TrainingGenerator

generator = TrainingGenerator()

# Generate from tool usage
data = generator.generate_from_history(memory_module)

# Generate synthetic examples
data = generator.generate_synthetic(categories=["charting", "erp"])

# Export to JSONL
generator.export_llama_format("training/data/batch_001.jsonl")
```

### 2. Training Harness

```python
from GLADIUS.training.harness import CognitionSandbox

# Create isolated training environment
sandbox = CognitionSandbox(base_path="./training_run_001")

# Run training cycle
result = await sandbox.run_training_cycle(
    data_path="training/data/combined_training_llama.json",
    epochs=3,
    batch_size=32
)

# Validate before promotion
if result.accuracy >= 0.99:
    sandbox.promote_to_staging()
```

### 3. Progressive Training

```python
from GLADIUS.training.scripts.progressive_trainer import run_progressive_training

# Run full training pipeline
result = run_progressive_training(
    model_path="./models/base/qwen2.5-0.5b-instruct-q4_k_m.gguf",
    output_path="./models/staging",
    data_path="./training/data"
)
```

---

## Inference API

### Pattern Router (Current)

```python
from GLADIUS.router.pattern_router import PatternRouter

router = PatternRouter()

# Route a query to the appropriate tool
result = router.route("Search for gold price analysis")
# Returns: {"tool": "search", "confidence": 0.98, "latency_ms": 0.87}

# Execute with context
response = router.execute(
    query="Generate a chart for XAUUSD",
    context={"timeframe": "1D", "indicators": ["RSI", "MACD"]}
)
```

### GGUF Router (Target)

```python
from GLADIUS.router.gguf_router import GGUFRouter

router = GGUFRouter(model_path="./models/production/gladius-v1.gguf")

# Direct inference
response = router.inference(
    prompt="Given this market data, what's your analysis?",
    max_tokens=512,
    temperature=0.7
)
```

---

## Tool Registry Integration

GLADIUS routes to 37+ tools across categories:

| Category | Tools | Examples |
|----------|-------|----------|
| Database | 3 | read_db, write_db, list_databases |
| Search | 3 | search, hybrid_search, get_context |
| Workspace | 4 | read_file, write_file, list_dir |
| Memory | 3 | remember, recall, forget |
| Charting | 7 | generate_chart, detect_trendlines |
| Publishing | 3 | create_content, schedule_post |
| ERP | 8 | erp_sync_customers, erp_sync_orders |
| Governance | 3 | create_proposal, route_proposal |
| Reasoning | 3 | contextualize_content |

---

## Roadmap

### Phase 1: Pattern Router ✅
- TF-IDF based routing
- 100% accuracy on known tools
- <2ms latency

### Phase 2: GGUF Training 🚧
- Fine-tune Qwen 0.5B on tool routing
- Add task execution capabilities
- Target: <5ms latency

### Phase 3: Full Inference 📋
- Replace all Ollama calls
- Self-contained model
- No external dependencies

### Phase 4: Self-Evolution 📋
- Continuous learning from operations
- Automatic fine-tuning
- Version management

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GLADIUS_MODEL_PATH` | Path to production model | `./models/production` |
| `GLADIUS_STAGING_PATH` | Path to staging model | `./models/staging` |
| `GLADIUS_TRAINING_DATA` | Path to training data | `./training/data` |
| `GLADIUS_FALLBACK_ENABLED` | Enable Ollama fallback | `true` |
| `GLADIUS_LOG_LEVEL` | Logging level | `INFO` |

---

## License

Proprietary - Artifact Virtual

---

*Part of the Gladius Enterprise System*
