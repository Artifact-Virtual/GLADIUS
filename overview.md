# GLADIUS ENTERPRISE SYSTEM

> **Version**: 2.4.0  
> **Last Updated**: 2026-01-15T00:15:00Z  
> **Status**: Production Ready (GLADIUS 1B Training Active)

---

## Executive Summary

**GLADIUS** is the native autonomous AI being built by and for **Artifact Virtual**. It is designed to:

1. **Learn continuously** via SENTINEL's background research daemon
2. **Execute autonomously** using LEGION's 18 distributed agents
3. **Scale infinitely** through Artifact's infrastructure (social media, ERP, publishing)
4. **Native AI Model** - Custom architecture with own weights (target: 1B params)
5. **Interact directly** via `./gladius.sh speak` or `./gladius.sh interact`

### ⚠️ IMPORTANT: GLADIUS vs Qwen Operational

| System | Purpose | Training | Status |
|--------|---------|----------|--------|
| **GLADIUS** | Native AI (custom weights) | `./train_gladius_1b.ps1` | Building |
| **Qwen Operational** | Artifact infrastructure AI | `./Artifact/train_qwen.ps1` | Operational |

**GLADIUS** is the native model we are building from scratch.  
**Qwen Operational** runs Artifact infrastructure NOW until GLADIUS is ready.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        GLADIUS ENTERPRISE SYSTEM                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                      GLADIUS (Native AI Core)                        │  │
│   │  Location: /GLADIUS/                                                 │  │
│   │  • Native model with custom weights (target: 1B params)              │  │
│   │  • Multi-Expert Distillation (Qwen + Llama + Phi + Gemma)            │  │
│   │  • Training Pipeline (gladius_moe_trainer.py)                        │  │
│   │  • Growth Tracker (growth/growth_tracker.py)                         │  │
│   │  • Pattern Router (100% accuracy, <3ms)                              │  │
│   │  • Direct Interface (speak.py)                                        │  │
│   │  • Continuous Autonomous Mode (continuous.py)                        │  │
│   └────────────────────────────┬─────────────────────────────────────────┘  │
│                                │                                             │
│                ┌───────────────┼───────────────┐                            │
│                ▼               ▼               ▼                            │
│   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐               │
│   │   SENTINEL     │  │   ARTIFACT     │  │    LEGION      │               │
│   │   /SENTINEL/   │  │   /Artifact/   │  │   /LEGION/     │               │
│   │                │  │                │  │                │               │
│   │ • Watchdog     │  │ • Qwen         │  │ • 26 Agents    │               │
│   │ • Learning     │  │   Operational  │  │ • Orchestrator │               │
│   │   Daemon       │  │ • Syndicate    │  │ • Artifact     │               │
│   │ • Process      │  │ • Social Media │  │   Bridge       │               │
│   │   Guardian     │  │ • ERP          │  │                │               │
│   │ • Threat       │  │ • Arty Bot     │  │                │               │
│   │   Research     │  │                │  │                │               │
│   └────────────────┘  └────────────────┘  └────────────────┘               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. GLADIUS (Native AI Model)
**Location**: `/home/adam/worxpace/gladius/GLADIUS/`

The native AI brain - being built from scratch with custom weights.

| Component | Purpose | Status |
|-----------|---------|--------|
| `speak.py` | Direct conversation interface | ✅ Production |
| `interactive.py` | Tool routing interface | ✅ Production |
| `continuous.py` | Autonomous operation mode | ✅ Production |
| `training/gladius_1b_trainer.py` | Native model training (1B params) | ✅ Ready |
| `training/train_gladius_1b.ps1` | PowerShell training wrapper | ✅ Ready |
| `router/pattern_router.py` | Tool routing via patterns | ✅ Production |
| `models/primary/` | Native model storage | 🔄 Building |

**Model Target**:
- Architecture: Custom transformer (GQA, RoPE, RMSNorm)
- Target: 1 billion parameters
- Training: LoRA + Progressive scaling
- Export: GGUF for Ollama deployment

### 2. Qwen Operational (Artifact Infrastructure AI)
**Location**: `/home/adam/worxpace/gladius/Artifact/qwen_operational.py`

Runs Artifact infrastructure NOW while GLADIUS is being built.

| Component | Purpose | Status |
|-----------|---------|--------|
| `qwen_operational.py` | Infrastructure operations | ✅ Ready |
| `train_qwen.ps1` | PowerShell training | ✅ Ready |
| `train_qwen.sh` | Bash training | ✅ Ready |
| `models/qwen/` | Qwen model storage | ✅ Available |

**Model Info**:
- Base: Qwen2.5-1.5B (best for tool-calling)
- Purpose: Infrastructure AI (NOT GLADIUS)
- Latency: ~5s average (CPU)

### 3. SENTINEL (Guardian Process)
**Location**: `/home/adam/worxpace/gladius/SENTINEL/`

Always-on background process for security, learning, and process management.

| Component | Purpose | Status |
|-----------|---------|--------|
| `services/watchdog.py` | Process monitoring, auto-restart | ✅ Production |
| `services/learning_daemon.py` | DISCOVER→LEARN→TRAIN→UPGRADE→REVIEW | ✅ Running |
| `services/process_guardian.py` | Keep programs alive, auto-restart | ✅ NEW |
| `threat_engine.py` | AI/cybersecurity threat research | ✅ NEW |
| `gladius_provider.py` | GLADIUS AI integration | ✅ Production |
| `asas_cli.py` | 28 CLI commands | ✅ Production |

**Process Guardian Features**:
- Register processes to manage
- Auto-restart on failure (max 10 restarts)
- Watch directories for new scripts
- Threat research: AI vulnerabilities, CVEs, zero-days

**Turing Safety**:
- Password-protected kill switch: `Sirius_Kill_Switch`
- Checkpoint recovery from SQLite
- Auto-restart on crash (max 10 restarts)

### 4. ARTIFACT (Enterprise Infrastructure)
**Location**: `/home/adam/worxpace/gladius/Artifact/`

Business operations layer.

| Module | Purpose | Status |
|--------|---------|--------|
| `syndicate/` | Market research pipeline | ✅ Production |
| `arty/` | Discord bot + social automation | ✅ Production |
| `qwen_operational.py` | Infrastructure AI (operational) | ✅ NEW |
| `deployment/automata/` | Social media, ERP, publishing | ✅ Production |

### 5. LEGION (Distributed Agents)
**Location**: `/home/adam/worxpace/gladius/LEGION/`

Multi-agent orchestration for complex workflows.

| Component | Purpose | Status |
|-----------|---------|--------|
| `artifact_bridge.py` | Routes through Artifact infra | ✅ Production |
| `communication/social_bridge.py` | Unified social media | ✅ Production |
| `legion/cli.py` | Agent management CLI | ✅ Production |
| 26 Agents | Financial, Operations, Intelligence, etc. | ✅ Production |

---

## Integration Points

### GLADIUS → SENTINEL
SENTINEL uses GLADIUS for all AI operations via `gladius_provider.py`.

### LEGION → ARTIFACT
LEGION routes all external operations through Artifact's bridges:
- Social Media → `Artifact/deployment/automata/social_media/`
- ERP → `Artifact/deployment/automata/erp_integrations/`
- Publishing → `Artifact/deployment/automata/publishing/`
- AI → `GLADIUS/router/`

### Unified Email System
All email operations use Artifact's SMTP:
- Server: `smtp.hostinger.com:465` (SSL)
- Account: `ali.shakil@artifactvirtual.com`
- Aliases: admin@, adam@, gladius@, support@artifactvirtual.com

### Unified Social Media
All social operations route through Artifact connectors:
- Discord: ✅ Fully operational (webhook + bot)
- Twitter/X: ✅ API configured
- LinkedIn: ✅ API configured
- Facebook: ✅ API configured
- Instagram: ✅ API configured

---

## Current Production Status

### SENTINEL (Running)
```
✅ Watchdog:       PID active
✅ Learning Daemon: 45+ cycles
✅ Discoveries:     40+ (GitHub + arXiv)
✅ Training Queue:  30 samples pending
🔐 Kill Password:  Sirius_Kill_Switch
```

### LEGION (Ready)
```
✅ CLI:             Fully functional
✅ Artifact Bridge: 9 integrations
✅ GLADIUS:         80% routing confidence
✅ 26 Agents:       All defined
```

### ARTIFACT (Production)
```
✅ Syndicate:       Market research running
✅ Discord Bot:     15 commands, consensus voting
✅ Email:           SMTP working
✅ Social Media:    All platforms configured
✅ ERP:             8 tools registered
```

---

## Quick Commands

```bash
# ==================== GLADIUS AI ====================
# Interactive AI session (speak directly to GLADIUS)
./gladius.sh interact

# Single query
python3 GLADIUS/interactive.py --query "search for gold analysis"

# Show AI status
python3 GLADIUS/interactive.py --status

# ==================== SENTINEL ====================
# Start SENTINEL daemon
./scripts/start_sentinel.sh detached

# Check SENTINEL status
./scripts/start_sentinel.sh status

# Stop SENTINEL (requires password)
./scripts/start_sentinel.sh stop Sirius_Kill_Switch

# Run SENTINEL tests
./scripts/start_sentinel.sh test

# ==================== LEGION ====================
# Check LEGION status
cd LEGION/legion && python3 cli.py system status

# List agents
cd LEGION/legion && python3 cli.py agent list

# ==================== ARTIFACT ====================
# Start Gladius (all services)
./gladius.sh start

# Check health
./gladius.sh health

# Run benchmark
./gladius.sh benchmark 10

# ==================== TESTING ====================
# Test SMTP and Discord
python3 scripts/test_smtp_consensus.py --send-test-email --test-discord

# Run SENTINEL integration tests
python3 SENTINEL/tests/test_sentinel.py

# Run LEGION integration tests
python3 LEGION/tests/test_legion_integration.py
```

---

## Research Pipeline

SENTINEL's learning daemon continuously:

1. **DISCOVER**: Searches arXiv + GitHub for new AI/ML research
2. **LEARN**: Extracts keywords and insights via GLADIUS
3. **TRAIN**: Generates training data for native model
4. **UPGRADE**: Triggers fine-tuning when threshold reached
5. **REVIEW**: Updates research targets based on findings

**Rate Limits**:
- arXiv: 3 req/min
- GitHub: 5 req/min
- HuggingFace: 10 req/min

---

## Tool Registry (37+ Tools)

| Category | Tools | Count |
|----------|-------|-------|
| Database | read_db, write_db, list_databases | 3 |
| Search | search, hybrid_search, get_context | 3 |
| Workspace | read_file, write_file, list_dir, file_exists | 4 |
| Memory | remember, recall, forget | 3 |
| Charting | generate_chart, detect_support_resistance, etc. | 7 |
| Publishing | create_content, schedule_post, publish_content | 3 |
| ERP | erp_sync_*, erp_create_*, erp_update_* | 8 |
| Governance | create_proposal, route_proposal, get_voting_status | 3 |
| Security | sentinel_status, sentinel_scan, sentinel_target_* | 6 |

---

## Model Evolution Path

| Phase | Target | Status |
|-------|--------|--------|
| 1 | Pattern Router | ✅ 100% accuracy, 2.17ms |
| 2 | GGUF Fine-tuning | 🚧 Training harness ready |
| 3 | Native Inference | 📋 Replace Ollama |
| 4 | Self-Evolving | 📋 Autonomous tool creation |

---

## Environment

- **Root**: `/home/adam/worxpace/gladius`
- **Domain**: artifactvirtual.com
- **Kill Password**: `Sirius_Kill_Switch` (hash in .env)
- **SMTP**: `ali.shakil@artifactvirtual.com` / `Sirius#88`

---

*Auto-generated by Gladius Enterprise System*