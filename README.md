<div align="center">

```
  ________.____       _____  ________  .___ ____ ___  _________
 ╱  _____╱│    │     ╱  _  ╲ ╲______ ╲ │   │    │   ╲╱   _____╱
╱   ╲  ___│    │    ╱  ╱_╲  ╲ │    │  ╲│   │    │   ╱╲_____  ╲ 
╲    ╲_╲  ╲    │___╱    │    ╲│    `   ╲   │    │  ╱ ╱        ╲
 ╲______  ╱_______ ╲____│__  ╱_______  ╱___│______╱ ╱_______  ╱
        ╲╱        ╲╱       ╲╱        ╲╱                     ╲╱ 
```

<p>
  <img src="https://img.shields.io/badge/Status-75%25-22C55E?style=for-the-badge" alt="Progress">
  <img src="https://img.shields.io/badge/AI-Native_GGUF-8B5CF6?style=for-the-badge" alt="Native AI">
  <img src="https://img.shields.io/badge/Tools-94_Commands-3776AB?style=for-the-badge" alt="Commands">
  <img src="https://img.shields.io/badge/Agents-26_Active-6366F1?style=for-the-badge" alt="Agents">
</p>

**Native AI-powered enterprise system with recursive self-improvement, autonomous research, and multi-platform publishing.**

> HuggingFace: https://huggingface.co/amuzetnoM/Gladius

[Architecture](docs/ARCHITECTURE_MASTER.md) · [Commands](docs/COMMAND_REFERENCE.md) · [Model](docs/MODEL.md) · [Checklist](docs/FLIGHT_CHECKLIST.md)

</div>

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ARTIFACT VIRTUAL                                 │
│                     (Enterprise Infrastructure)                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        GLADIUS                                   │   │
│  │                   (Native AI - The Brain)                        │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │   │
│  │  │ Cognition│ │  Memory  │ │  Router  │ │  Model   │           │   │
│  │  │  Engine  │ │  Module  │ │  (GGUF)  │ │ Trainer  │           │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐          │
│  │  SENTINEL  │ │   LEGION   │ │  SYNDICATE │ │  AUTOMATA  │          │
│  │ (Guardian) │ │  (Agents)  │ │ (Research) │ │ (Publish)  │          │
│  │ 24 cmds    │ │ 26 agents  │ │  Charts    │ │ 5 platforms│          │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Components

| Component | Purpose | Status |
|-----------|---------|--------|
| **GLADIUS** | Native AI model, cognition engine, tool router | 🧠 Brain |
| **SENTINEL** | Guardian process, security, background learning | 🛡️ Guardian |
| **LEGION** | 26 AI agents for enterprise operations | 🤖 Agents |
| **SYNDICATE** | Market research, charts, journals | 📊 Research |
| **AUTOMATA** | Social media publishing, ERP integrations | 📱 Automation |

---

## Quick Start

```bash
# Start everything
./gladius.sh start

# Check system health
./gladius.sh health

# Run a full cycle (research → analyze → publish)
./gladius.sh cycle

# Run autonomous mode (indefinite)
./gladius.sh autonomous
```

### Subsystem Commands

```bash
# GLADIUS (Native AI)
./gladius.sh gladius status
./gladius.sh gladius benchmark 10
./gladius.sh gladius train

# SENTINEL (Guardian)
./gladius.sh sentinel start
./gladius.sh sentinel scan
./gladius.sh sentinel learn status

# LEGION (Agents)
./gladius.sh legion system status
./gladius.sh legion agent list

# ARTIFACT (Enterprise)
./gladius.sh artifact syndicate run
./gladius.sh artifact publish test
./gladius.sh artifact erp status
```

---

## Current Status

**Overall Progress: 75%**

| Component | Progress | Details |
|-----------|----------|---------|
| Cognition Engine | 95% | 37+ tools, pattern router |
| Consensus System | ✅ 100% | Discord + Email working |
| SMTP Email | ✅ 100% | Hostinger SSL configured |
| SENTINEL | 90% | Cloned, needs daemons |
| LEGION | 90% | 26 agents, needs integration |
| Syndicate | 95% | Charts, journals working |
| Automata | 75% | 5 platforms configured |
| Research Pipeline | 20% | Needs arXiv/MIT crawler |
| Native Model | 50% | GGUF training in progress |

---

## Directory Structure

```
gladius/
├── gladius.sh                # Master control script
├── .env                      # Unified configuration
│
├── GLADIUS/                  # 🧠 NATIVE AI MODEL (isolated)
│   ├── models/               # GGUF model files
│   ├── training/             # Training data + harness
│   └── router/               # Tool routing
│
├── SENTINEL/                 # 🛡️ GUARDIAN PROCESS
│   ├── asas_cli.py          # 24 CLI commands
│   ├── services/            # Learning daemons
│   └── config/              # Constitutional rules
│
├── LEGION/                   # 🤖 AGENT ECOSYSTEM
│   ├── legion/              # 26 specialized agents
│   └── config/              # Agent configuration
│
├── Artifact/                 # 📦 ENTERPRISE OPS
│   ├── syndicate/           # Market research
│   ├── deployment/          # Automata + Infra
│   └── arty/                # Discord bot
│
├── docs/                     # Documentation
└── obsidian_sync/           # Operator notes
```

---

## Configuration

Edit `.env` for credentials:

```bash
# === GLADIUS ===
GLADIUS_ENABLED=true

# === SENTINEL ===
SENTINEL_ENABLED=true
SENTINEL_LEARNING_LOOP=true

# === LEGION ===
LEGION_ENABLED=true

# === SMTP (Email Escalation) ===
SMTP_HOST=smtp.hostinger.com
SMTP_PORT=465
SMTP_SSL=true
SMTP_USER=ali.shakil@artifactvirtual.com

# === Discord (Consensus) ===
DISCORD_WEBHOOK_URL=your_webhook
DISCORD_CONSENSUS_CHANNEL_ID=1327890703250096168

# === Social Media ===
TWITTER_ENABLED=true
LINKEDIN_ENABLED=true
```

---

## Documentation

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE_MASTER.md](docs/ARCHITECTURE_MASTER.md) | Complete system architecture |
| [COMMAND_REFERENCE.md](docs/COMMAND_REFERENCE.md) | All 94 commands |
| [FLIGHT_CHECKLIST.md](docs/FLIGHT_CHECKLIST.md) | Implementation progress |
| [MODEL.md](docs/MODEL.md) | Native AI model specification |
| [SENTINEL/SYSTEM_MAPPING.md](SENTINEL/SYSTEM_MAPPING.md) | Guardian commands |
| [LEGION/SYSTEM_MAPPING.md](LEGION/SYSTEM_MAPPING.md) | Agent ecosystem |

---

## 🔄 The Learning Loop

SENTINEL runs a continuous background process:

```
┌─────────────────────────────────────────────────────────────┐
│                 CONTINUOUS LEARNING LOOP                     │
│           (Turing-safe: password-protected kill)            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  DISCOVER → LEARN → TRAIN → UPGRADE → REVIEW → (repeat)    │
│                                                              │
│  • Web research: arXiv, MIT, GitHub, HuggingFace            │
│  • Keyword extraction for direction                         │
│  • Training data generation                                  │
│  • Model fine-tuning                                        │
│  • Self-review and target updates                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Tool Registry (37+ Tools)

| Category | Tools | Count |
|----------|-------|-------|
| Database | read_db, write_db, list_databases | 3 |
| Search | search, hybrid_search, get_context | 3 |
| Workspace | read_file, write_file, list_dir, file_exists | 4 |
| Memory | remember, recall, forget | 3 |
| Charting | generate_chart, detect_trendlines, calculate_indicators, etc. | 7 |
| Publishing | create_content, schedule_post, publish_content | 3 |
| ERP | erp_sync_customers, erp_sync_products, erp_sync_orders, etc. | 8 |
| Governance | create_proposal, route_proposal, get_voting_status | 3 |
| Reasoning | contextualize_content, reason_about_audience, think_about_timing | 3 |

---

## Security & Governance

### Consensus System
- **Low impact**: Auto-approved
- **Medium impact**: Discord vote
- **High impact**: Email escalation to dev team
- **Critical impact**: Executive approval required

### Constitutional AI
- Ethical decision framework in SENTINEL
- All automated actions logged and explainable
- Response proportional to threat severity

---

## Requirements

- Python 3.10+
- Node.js 18+ (for dashboards)
- SQLite3
- Ollama (optional, for LLM fallback)

---

## License

Proprietary - Artifact Virtual

---

<div align="center">

**[Artifact Virtual](https://artifactvirtual.com)** — Building Autonomous Enterprise Intelligence

*System at 75% completion | Last updated: 2026-01-14*

</div>
