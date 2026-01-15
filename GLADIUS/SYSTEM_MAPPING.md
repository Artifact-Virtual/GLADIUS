# GLADIUS System Mapping

> **Module**: `/GLADIUS/`  
> **Last Updated**: 2026-01-14T23:55:00Z  
> **Purpose**: Native AI Model - The Brain of Artifact Virtual

---

## ⚠️ IMPORTANT: GLADIUS vs Qwen Operational

| System | Purpose | Location |
|--------|---------|----------|
| **GLADIUS** | Native AI model (custom weights) | `/GLADIUS/` |
| **Qwen Operational** | Artifact infrastructure AI | `/Artifact/qwen_operational.py` |

**GLADIUS** is the native model we are building from scratch with custom weights.
**Qwen Operational** is the operational AI that runs Artifact infrastructure NOW.

They are **completely separate**:
- Train GLADIUS: `./train_gladius_1b.ps1`
- Train Qwen: `./Artifact/train_qwen.ps1`

When GLADIUS reaches maturity, it will replace Qwen Operational.

---

## Overview

GLADIUS is the **native AI model** that powers all intelligent operations within Artifact Virtual. It provides:

1. **Native Model** - Custom architecture with own weights (target: 1B params)
2. **Tool Routing** - Pattern-based routing with 100% accuracy
3. **Training Pipeline** - Automated model training and validation
4. **Continuous Mode** - Autonomous operation with learning cycles
5. **Direct Interface** - Speak directly to GLADIUS

---

## Components

| File | Purpose | Status |
|------|---------|--------|
| `speak.py` | Direct GLADIUS conversation interface | ✅ Production |
| `interactive.py` | Tool routing interface | ✅ Production |
| `continuous.py` | Autonomous operation mode | ✅ Production |
| `training/train_pipeline.py` | Model training pipeline | ✅ Production |
| `training/harness.py` | Isolated training sandbox | ✅ Production |
| `training/generator.py` | Training data generation | ✅ Production |
| `router/pattern_router.py` | TF-IDF tool routing | ✅ Production |
| `models/production/` | Production model storage | ✅ gladius:latest |
| `models/staging/` | Staging model storage | ✅ Available |

---

## Model Information

### Current Production Model
| Property | Value |
|----------|-------|
| **Model Name** | gladius:latest |
| **Base Model** | Qwen2.5-0.5B |
| **Size** | 397 MB |
| **Accuracy** | 80% (tool-calling) |
| **Latency** | ~12s average (CPU) |
| **Version** | 0.1.0 |

### 1B Training Target
| Property | Value |
|----------|-------|
| **Target Model** | gladius:1b |
| **Base Model** | Qwen2.5-1.5B |
| **Target Params** | 1,000,000,000 |
| **Method** | LoRA + Progressive Training |
| **Trainer** | `./train_gladius_1b.ps1` or `.sh` |

---

## CLI Commands

### Direct AI Interaction
```bash
# Speak directly to GLADIUS (conversational)
./gladius.sh speak

# Single query
./gladius.sh speak "What can you do?"

# Interactive tool routing
./gladius.sh interact

# Check GLADIUS status
./gladius.sh speak --status
```

### Model Training
```bash
# Run full training pipeline
./gladius.sh train

# Train with specific base model
./gladius.sh train --base-model qwen2.5:0.5b

# Train specific version
./gladius.sh train --version 0.2.0

# Skip validation
./gladius.sh train --no-validate
```

### 1B Parameter Training (NEW)
```bash
# PowerShell (Windows/Cross-platform)
cd GLADIUS/training
./train_gladius_1b.ps1 start              # Start continuous training
./train_gladius_1b.ps1 status             # Check training progress
./train_gladius_1b.ps1 stop               # Stop with checkpoint
./train_gladius_1b.ps1 resume             # Resume from checkpoint
./train_gladius_1b.ps1 export             # Export to GGUF
./train_gladius_1b.ps1 -Hours 48 start    # Train for 48 hours

# Bash (Linux/Mac)
./train_gladius_1b.sh start               # Start training
./train_gladius_1b.sh --hours 72 start    # Train for 72 hours
./train_gladius_1b.sh status              # Check progress

# Python Direct
python3 gladius_1b_trainer.py --hours 168 --batch-size 4
python3 gladius_1b_trainer.py --status
python3 gladius_1b_trainer.py --export-only
```

### Continuous Autonomous Mode
```bash
# Run continuous mode (default: 30 days, 60min intervals)
./gladius.sh continuous

# Custom duration and interval
./gladius.sh continuous --days 7 --interval 30

# Run single cycle
./gladius.sh continuous --single-cycle

# Disable training during sleep
./gladius.sh continuous --no-training
```

### Legacy Commands
```bash
# Pattern-based routing test
python3 GLADIUS/interactive.py --query "search for gold"

# Full benchmark
./gladius.sh benchmark

# Cognition cycle
./gladius.sh cognition
```

---

## API Reference

### Direct Interface (speak.py)

```python
from GLADIUS.speak import GladiusInterface

interface = GladiusInterface()

# Get status
status = interface.get_status()
# {
#     "model": "gladius:latest",
#     "is_native": True,
#     "available": True,
#     "messages_exchanged": 0
# }

# Query GLADIUS
response = interface.query("What tools can you use?")
# {
#     "success": True,
#     "response": "{"tool": "get_tools", "args": {}}",
#     "model": "gladius:latest",
#     "latency_ms": 12000
# }
```

### Training Pipeline (train_pipeline.py)

```python
from GLADIUS.training.train_pipeline import TrainingPipeline

pipeline = TrainingPipeline()

# Run complete training
results = pipeline.run(validate=True, promote=True)
# {
#     "success": True,
#     "steps": {
#         "ollama_check": "passed",
#         "build": "success",
#         "validation": {"accuracy": 80.0},
#         "promotion": "success"
#     }
# }
```

### Continuous Mode (continuous.py)

```python
from GLADIUS.continuous import AutonomousOperator, AutonomousConfig
import asyncio

config = AutonomousConfig(
    duration_hours=168,  # 7 days
    interval_minutes=30,
    training_every_n_cycles=6
)

operator = AutonomousOperator(config)
results = asyncio.run(operator.run())
```

### Pattern Router

```python
from GLADIUS.router.pattern_router import NativeToolRouter

router = NativeToolRouter()

# Route a query
result = router.route("Search for gold analysis")
# RouteResult(
#     tool_name="search",
#     arguments={"query": "gold analysis", "k": 5},
#     confidence=0.98,
#     latency_ms=0.87,
#     source="pattern"
# )

# Get statistics
stats = router.stats()
# {
#     "pattern_calls": 145,
#     "ollama_calls": 12,
#     "total_calls": 157,
#     "avg_latency_ms": 1.2
# }
```

---

## Autonomous Cycle Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS CYCLE                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ OPERATE │→│ COGNIZE │→│  TRAIN  │→│  SLEEP  │→ REPEAT  │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │
│       │            │            │            │              │
│  Artifact     Self-review   Model       SENTINEL           │
│  operations   & planning    training    learning           │
└─────────────────────────────────────────────────────────────┘
```

---

## Tool Registry (37+ Tools)

### Database (3)
| Tool | Description |
|------|-------------|
| `read_db` | Query SQL databases |
| `write_db` | Write to databases |
| `list_databases` | List connected databases |

### Search (3)
| Tool | Description |
|------|-------------|
| `search` | Vector similarity search |
| `hybrid_search` | Combined vector + keyword |
| `get_context` | Retrieve recent context |

### Workspace (4)
| Tool | Description |
|------|-------------|
| `read_file` | Read file contents |
| `write_file` | Write files |
| `list_dir` | Browse workspace |
| `file_exists` | Check file existence |

### Memory (3)
| Tool | Description |
|------|-------------|
| `remember` | Store in vector memory |
| `recall` | Retrieve from memory |
| `forget` | Remove from memory |

### Communication (3)
| Tool | Description |
|------|-------------|
| `send_discord` | Send Discord message |
| `send_email` | Send email via SMTP |
| `post_social` | Post to social media |

### Syndicate (2)
| Tool | Description |
|------|-------------|
| `run_syndicate` | Run market analysis |
| `get_syndicate_status` | Check Syndicate status |

### Charting (7)
| Tool | Description |
|------|-------------|
| `generate_chart` | Create price charts |
| `detect_support_resistance` | Find S/R levels |
| `detect_trendlines` | Identify trends |
| `calculate_indicators` | RSI, MACD, etc. |
| `determine_regime` | Market regime |
| `annotate_chart` | Add annotations |
| `create_trade_setup` | Trade visualization |

### ERP (8)
| Tool | Description |
|------|-------------|
| `erp_sync_customers` | Sync customers |
| `erp_sync_products` | Sync products |
| `erp_sync_orders` | Sync orders |
| `erp_sync_inventory` | Sync inventory |
| `erp_get_status` | ERP status |
| `erp_create_customer` | Create customer |
| `erp_create_order` | Create order |
| `erp_update_inventory` | Update inventory |

### System (2)
| Tool | Description |
|------|-------------|
| `get_tools` | List available tools |
| `get_history` | Get operation history |

---

## Performance Benchmarks

| Metric | Value |
|--------|-------|
| Model Accuracy | 80% |
| Pattern Routing | 100% |
| Pattern Latency | <3ms |
| Model Latency | ~12s (CPU) |
| Training Samples | 75+ |
| Total Tools | 37+ |

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AI_PROVIDER` | AI provider (ollama) | `ollama` |
| `OLLAMA_HOST` | Ollama server | `http://localhost:11434` |
| `OLLAMA_MODEL` | Default model | `llama3.2` |
| `GLADIUS_ENABLED` | Enable GLADIUS | `true` |

---

## Quick Reference

```bash
# Speak to GLADIUS
./gladius.sh speak

# Train model
./gladius.sh train

# 1B Training (PowerShell)
cd GLADIUS/training && ./train_gladius_1b.ps1 start

# 1B Training (Bash)
cd GLADIUS/training && ./train_gladius_1b.sh start

# Continuous mode
./gladius.sh continuous

# Interactive routing
./gladius.sh interact

# Status
./gladius.sh speak --status
```

---

## Training Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 GLADIUS 1B TRAINING PIPELINE                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Phase 1    │ → │   Phase 2    │ → │   Phase 3    │  │
│  │ Base Fine-   │    │ Extended     │    │ LoRA Stack   │  │
│  │ tuning       │    │ Training     │    │ Expansion    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         ↓                                       ↓           │
│  ┌──────────────┐                       ┌──────────────┐   │
│  │ Checkpoints  │                       │   Phase 4    │   │
│  │ (Recovery)   │                       │ GGUF Export  │   │
│  └──────────────┘                       └──────────────┘   │
│                                                ↓            │
│                                         ┌──────────────┐   │
│                                         │ gladius:1b   │   │
│                                         │ (Ollama)     │   │
│                                         └──────────────┘   │
│                                                             │
│  Features:                                                  │
│  • LoRA-based parameter efficient training                  │
│  • 4-bit quantization for memory efficiency                 │
│  • Automatic checkpoint recovery                            │
│  • GGUF export for Ollama deployment                        │
│  • Target: 1 billion parameters                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

*Generated by Gladius System Mapper*
