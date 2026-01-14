# GLADIUS System Mapping

> **Module**: `/GLADIUS/`  
> **Last Updated**: 2026-01-14  
> **Purpose**: Native AI Model - The Brain of Artifact Virtual

---

## Overview

GLADIUS is the **native AI model** that powers all intelligent operations within Artifact Virtual. It provides:

1. **Tool Routing** - Pattern-based routing with 100% accuracy
2. **Inference** - GGUF model for task execution
3. **Training** - Continuous learning from operations
4. **Self-Improvement** - Autonomous model upgrades

---

## Components

| File | Class/Function | Purpose | Status |
|------|----------------|---------|--------|
| `router/pattern_router.py` | `PatternRouter` | TF-IDF tool routing | ✅ Production |
| `router/gguf_router.py` | `GGUFRouter` | GGUF inference | 📋 To Implement |
| `training/harness.py` | `CognitionSandbox` | Isolated training | ✅ Production |
| `training/generator.py` | `TrainingGenerator` | Data generation | ✅ Production |
| `training/scripts/trainer.py` | `ModelTrainer` | LoRA fine-tuning | ✅ Production |
| `training/scripts/progressive_trainer.py` | `ProgressiveTrainer` | Multi-stage training | ✅ Production |

---

## CLI Commands

Namespace: `./gladius.sh gladius <command>`

### Model Operations
```bash
# Check model status
./gladius.sh gladius status

# Show model info
./gladius.sh gladius info

# Run benchmark
./gladius.sh gladius benchmark [--cycles N]
```

### Training Operations
```bash
# Start training
./gladius.sh gladius train [--data PATH] [--epochs N]

# Generate training data
./gladius.sh gladius generate-training [--categories LIST]

# Validate staged model
./gladius.sh gladius validate
```

### Deployment Operations
```bash
# Deploy staging to production
./gladius.sh gladius deploy [--version VERSION]

# Rollback to previous version
./gladius.sh gladius rollback [--to VERSION]

# List model versions
./gladius.sh gladius versions
```

### Routing Operations
```bash
# Test tool routing
./gladius.sh gladius route "<query>"

# List available tools
./gladius.sh gladius tools [--category CAT]

# Export tool schemas
./gladius.sh gladius export-tools [--format json|openai]
```

### Cognition Operations
```bash
# Run single cognition cycle
./gladius.sh gladius cognition

# Run autonomous mode
./gladius.sh gladius autonomous [--hours N]

# Check cognition health
./gladius.sh gladius health
```

---

## API Reference

### Pattern Router

```python
from GLADIUS.router.pattern_router import PatternRouter

router = PatternRouter()

# Route a query
result = router.route("Search for gold analysis")
print(result)
# {
#     "tool": "search",
#     "confidence": 0.98,
#     "latency_ms": 0.87,
#     "alternatives": [
#         {"tool": "hybrid_search", "confidence": 0.72}
#     ]
# }

# Get all tools
tools = router.get_tools()

# Export OpenAI schema
schema = router.export_openai_schema()
```

### Training Harness

```python
from GLADIUS.training.harness import CognitionSandbox

# Create sandbox
sandbox = CognitionSandbox(base_path="./run_001")

# Run training
result = await sandbox.run_training_cycle(
    data_path="./training/data/combined.json",
    epochs=3
)

# Promote if successful
if result.accuracy >= 0.99:
    sandbox.promote_to_staging()
```

### Data Generator

```python
from GLADIUS.training.generator import TrainingGenerator

gen = TrainingGenerator()

# Generate from tool history
data = gen.generate_from_history(memory_module)

# Generate synthetic
data = gen.generate_synthetic(
    categories=["charting", "erp"],
    count=1000
)

# Export
gen.export_llama_format("./output.jsonl")
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

### Publishing (3)
| Tool | Description |
|------|-------------|
| `create_content` | Generate content |
| `schedule_post` | Schedule publishing |
| `publish_content` | Publish to platforms |

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

### Governance (3)
| Tool | Description |
|------|-------------|
| `create_proposal` | Create proposal |
| `route_proposal` | Route for approval |
| `get_voting_status` | Check vote status |

### Reasoning (3)
| Tool | Description |
|------|-------------|
| `contextualize_content` | Add context |
| `reason_about_audience` | Audience analysis |
| `think_about_timing` | Optimal timing |

### Engagement (1)
| Tool | Description |
|------|-------------|
| `engage_with_reply` | Generate replies |

### Analytics (1)
| Tool | Description |
|------|-------------|
| `get_engagement` | Engagement metrics |

### Communication (1)
| Tool | Description |
|------|-------------|
| `send_escalation_email` | Send escalation |

---

## Performance Benchmarks

| Metric | Value |
|--------|-------|
| Routing Accuracy | 100% |
| Avg Latency | 0.93ms |
| P99 Latency | 2.28ms |
| Training Samples | 914+ |
| Categories | 13 |
| Total Tools | 37+ |

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GLADIUS_ENABLED` | Enable GLADIUS | `true` |
| `GLADIUS_MODEL_PATH` | Production model path | `./models/production` |
| `GLADIUS_STAGING_PATH` | Staging model path | `./models/staging` |
| `GLADIUS_TRAINING_DATA` | Training data path | `./training/data` |
| `GLADIUS_FALLBACK` | Enable Ollama fallback | `true` |

---

## CLI Quick Reference

```bash
# Model
gladius status|info|benchmark|versions

# Training
gladius train|generate-training|validate

# Deployment
gladius deploy|rollback

# Routing
gladius route|tools|export-tools

# Cognition
gladius cognition|autonomous|health
```

---

*Generated by Gladius System Mapper*
