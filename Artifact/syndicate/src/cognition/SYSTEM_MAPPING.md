# Cognition Engine System Mapping

> Module: `Artifact/syndicate/src/cognition/`
> Last Updated: 2026-01-14

---

## Overview

The Cognition Engine is Gladius's brain - handling vector search, memory, tool routing, training, and self-improvement.

---

## Components

| File | Class/Function | Purpose | Status |
|------|----------------|---------|--------|
| `__init__.py` | Module exports | Feature flags and component loading | ✅ Active |
| `gladius_model.py` | `GladiusToolRouter` | Primary TF-IDF + MLP tool router (100% accuracy) | ✅ Production |
| `memory_module.py` | `MemoryModule` | Unified memory interface with 16+ tools | ✅ Production |
| `tool_calling.py` | `ToolRegistry`, `BUILTIN_TOOLS` | Tool definitions for native learning | ✅ Production |
| `training_harness.py` | `TrainingHarness` | Isolated training environment | ✅ Ready |
| `training_generator.py` | `TrainingDataGenerator` | Synthetic + historical training data | ✅ Production |
| `self_improvement.py` | `SelfImprovementEngine` | Proposal lifecycle with snapshots | ✅ Production |
| `learning_loop.py` | `CognitionLearningLoop` | Continuous learning cycle | ✅ Production |
| `consensus.py` | `ConsensusSystem` | Discord voting + email escalation | ✅ Configured |
| `hektor_store.py` | `HektorVectorStore` | Native C++ vector database | ✅ Production |
| `vector_store.py` | `VectorStore` | hnswlib fallback | ✅ Fallback |
| `embedder.py` | `Embedder` | TF-IDF embeddings | ✅ Production |
| `syndicate_integration.py` | `SyndicateCognition` | Report ingestion, prediction learning | ✅ Production |
| `context/context_manager.py` | `ContextManager` | Token-aware summarization | ✅ Production |
| `native_model/router.py` | `NativeToolRouter` | Pattern/Ollama/fallback routing | ✅ Production |
| `native_model/trainer.py` | `ModelTrainer` | GGUF fine-tuning pipeline | 🚧 Ready |
| `native_model/progressive_trainer.py` | `ProgressiveTrainer` | Tier-based training | ✅ Production |

---

## Tool Registry (22 Tools)

### Database Tools
| Tool | Function | Parameters |
|------|----------|------------|
| `read_db` | Query any connected database | `name`, `query`, `params?` |
| `write_db` | Write data to database | `name`, `data`, `table?` |
| `list_databases` | List all connected databases | - |

### Search Tools
| Tool | Function | Parameters |
|------|----------|------------|
| `search` | Semantic vector search | `query`, `k?`, `db_name?` |
| `hybrid_search` | Vector + BM25 fusion | `query`, `k?`, `vector_weight?`, `bm25_weight?` |
| `get_context` | Retrieve historical context | `query`, `k?` |

### Workspace Tools
| Tool | Function | Parameters |
|------|----------|------------|
| `read_file` | Read file from workspace | `path` |
| `write_file` | Write file to workspace | `path`, `content` |
| `list_dir` | List directory contents | `path?` |
| `file_exists` | Check if file exists | `path` |

### Memory Tools
| Tool | Function | Parameters |
|------|----------|------------|
| `remember` | Store memory for recall | `key`, `value`, `metadata?` |
| `recall` | Recall related memories | `query`, `k?` |
| `forget` | Remove a memory | `key` |

### Introspection Tools
| Tool | Function | Parameters |
|------|----------|------------|
| `get_tools` | List available tools | - |
| `get_history` | Get operation history | `last_n?` |

### Charting Tools
| Tool | Function | Parameters |
|------|----------|------------|
| `generate_chart` | Generate enhanced chart | `symbol`, `timeframe?`, `show_indicators?`, `show_levels?`, `show_trade_setup?` |
| `detect_support_resistance` | Detect S/R levels | `symbol`, `window?`, `num_levels?` |
| `detect_trendlines` | RANSAC trendline detection | `symbol`, `max_lines?` |
| `calculate_indicators` | Calculate RSI/ADX/ATR/SMA | `symbol` |
| `determine_regime` | Determine market regime | `symbol` |
| `annotate_chart` | Add annotations to chart | `symbol`, `annotations` |
| `create_trade_setup` | Create trade setup visualization | `symbol`, `entry`, `stop`, `targets` |

---

## Consensus System Commands

### Discord Voting
```python
from cognition import ConsensusSystem
cs = ConsensusSystem()

# Create voting session
await cs.route_proposal(
    proposal_id="prop_001",
    title="Improve accuracy",
    summary="Need to enhance pattern recognition",
    impact_level="medium"  # -> Discord vote
)
```

### Email Escalation
```python
# High-impact proposals automatically escalate to email
await cs.route_proposal(
    proposal_id="prop_002",
    title="Architecture change",
    summary="Major refactoring needed",
    impact_level="high"  # -> Email to dev_team_emails
)
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_WEBHOOK_URL` | Discord webhook for notifications | Required |
| `DISCORD_CONSENSUS_CHANNEL_ID` | Channel for voting sessions | `1327890703250096168` |
| `SMTP_HOST` | SMTP server hostname | `smtp.hostinger.com` |
| `SMTP_PORT` | SMTP server port | `465` |
| `SMTP_SSL` | Use SSL (true for port 465) | `true` |
| `SMTP_USER` | SMTP username | `ali.shakil@artifactvirtual.com` |
| `SMTP_PASSWORD` | SMTP password | Required |
| `EMAIL_FROM` | From address for emails | `support@artifactvirtual.com` |
| `DEV_TEAM_EMAILS` | Dev team email list (comma-sep) | Required |
| `EXECUTIVE_EMAILS` | Executive email list (comma-sep) | Required |
| `ESCALATION_EMAIL` | Fallback escalation email | `ali.shakil@artifactvirtual.com` |

---

## Benchmarks

| Metric | Value |
|--------|-------|
| Tool Routing Accuracy | 100% |
| Average Latency | 0.93ms |
| P99 Latency | 2.28ms |
| Training Examples | 914+ |
| Model Size | 5.4MB |
| Total Tools | 37+ |

---

## CLI Commands

```bash
# Run cognition cycle
./gladius.sh cognition

# Run benchmark
./gladius.sh benchmark 10

# Full autonomous mode
./gladius.sh autonomous
```

---

*Generated by Gladius System Mapper*
