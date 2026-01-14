# SYSTEM ARCHITECTURE

> **Generated**: 2026-01-14T17:30:00Z
> **Purpose**: Complete system architecture for Artifact Virtual Enterprise

---

## 🎯 CORE PHILOSOPHY

**GLADIUS** = The Native AI (the brain)  
**ARTIFACT VIRTUAL** = The Enterprise Infrastructure (the body)

GLADIUS uses Artifact's infrastructure to learn, grow, and evolve recursively and autonomously.
GLADIUS is both a **product** of Artifact and the **driver** of Artifact's operations.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ARTIFACT VIRTUAL                                 │
│                     (Enterprise Infrastructure)                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        GLADIUS                                   │   │
│  │                   (Native AI - The Brain)                        │   │
│  │                                                                   │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │   │
│  │  │ Cognition│ │  Memory  │ │  Router  │ │  Model   │           │   │
│  │  │  Engine  │ │  Module  │ │  (GGUF)  │ │ Trainer  │           │   │
│  │  │  37+ tools│ │  VDB     │ │  <2ms   │ │  LoRA    │           │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│         ┌────────────────────┼────────────────────┐                    │
│         ▼                    ▼                    ▼                    │
│  ┌────────────┐       ┌────────────┐       ┌────────────┐              │
│  │  SENTINEL  │       │   LEGION   │       │  SYNDICATE │              │
│  │ (Guardian) │       │  (Agents)  │       │ (Research) │              │
│  │            │       │            │       │            │              │
│  │ • Security │       │ • 26 agents│       │ • Charts   │              │
│  │ • Learning │       │ • Workflow │       │ • Journals │              │
│  │ • Watchdog │       │ • Messaging│       │ • Analysis │              │
│  └────────────┘       └────────────┘       └────────────┘              │
│         │                    │                    │                    │
│         └────────────────────┼────────────────────┘                    │
│                              ▼                                          │
│                       ┌────────────┐                                   │
│                       │  AUTOMATA  │                                   │
│                       │ (Publish)  │                                   │
│                       │            │                                   │
│                       │ • Social   │                                   │
│                       │ • ERP      │                                   │
│                       │ • Scheduler│                                   │
│                       └────────────┘                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 DIRECTORY STRUCTURE (CURRENT & TARGET)

```
/home/adam/worxpace/gladius/
├── gladius.sh                    # Master control script
├── README.md                     # This documentation
├── LICENSE.md
├── .env                          # Unified configuration
│
├── GLADIUS/                      # 🧠 NATIVE AI MODEL (TO CREATE)
│   ├── models/                   # GGUF/GGM model files
│   │   ├── production/          # Live model
│   │   ├── staging/             # Testing model
│   │   └── base/                # Base models for fine-tuning
│   ├── training/                # Training data and scripts
│   │   ├── data/                # Training datasets (JSONL)
│   │   ├── harness.py           # Training harness
│   │   └── generator.py         # Data generator
│   ├── router/                  # Native tool router
│   │   ├── pattern_router.py    # Pattern-based routing
│   │   └── gguf_router.py       # GGUF inference router
│   ├── docs/                    # Model documentation
│   │   ├── MODEL.md             # Model card
│   │   ├── TRAINING.md          # Training methodology
│   │   └── API.md               # Inference API
│   └── SYSTEM_MAPPING.md        # Command reference
│
├── SENTINEL/                     # 🛡️ GUARDIAN PROCESS (CLONED)
│   ├── asas_cli.py              # CLI interface (24 commands)
│   ├── system_controller.py     # Central controller
│   ├── security_monitor.py      # Security monitoring
│   ├── threat_engine.py         # Threat detection
│   ├── auto_response.py         # Automated response
│   ├── basenet_connector.py     # AI provider abstraction
│   ├── platform_interface.py    # Cross-platform ops
│   ├── config/
│   │   └── constitutional_rules.json
│   ├── services/                # 🆕 TO IMPLEMENT
│   │   ├── learning_daemon.py   # Continuous learning loop
│   │   ├── research_daemon.py   # Web research crawler
│   │   ├── upgrade_daemon.py    # Self-upgrade manager
│   │   └── watchdog.py          # Process recovery
│   └── SYSTEM_MAPPING.md
│
├── LEGION/                       # 🤖 AGENT ECOSYSTEM (CLONED)
│   ├── legion/
│   │   ├── cli.py               # CLI interface
│   │   ├── core_framework.py    # Agent framework
│   │   ├── enhanced_orchestrator.py
│   │   ├── enterprise_registry.py
│   │   ├── message_bus.py       # Inter-agent messaging
│   │   ├── agent_memory.py      # Agent memory
│   │   ├── self_improvement.py  # Auto-optimization
│   │   └── agents/              # 26 specialized agents
│   ├── config/
│   │   ├── integrations.json
│   │   └── llm_config.json
│   └── SYSTEM_MAPPING.md
│
├── Artifact/                     # 📦 ENTERPRISE INFRASTRUCTURE
│   ├── syndicate/               # Market Research Pipeline
│   │   ├── src/
│   │   │   ├── cognition/       # Cognition engine (CURRENT HOME)
│   │   │   │   ├── memory.py
│   │   │   │   ├── tool_calling.py
│   │   │   │   ├── training_harness.py
│   │   │   │   ├── consensus.py
│   │   │   │   └── SYSTEM_MAPPING.md
│   │   │   ├── publishing/      # Content pipeline
│   │   │   └── gost/            # Gold analysis
│   │   ├── models/              # Model files (TO MOVE)
│   │   └── output/              # Generated content
│   │
│   ├── deployment/
│   │   ├── infra/               # FastAPI server (port 7000)
│   │   └── automata/
│   │       ├── social_media/    # Platform connectors
│   │       │   └── SYSTEM_MAPPING.md
│   │       ├── erp_integrations/# ERP connectors
│   │       │   └── SYSTEM_MAPPING.md
│   │       ├── publishing/      # Content adapters
│   │       └── scheduler/       # Smart scheduling
│   │
│   ├── arty/                    # Discord bot & engagement
│   │
│   └── research/                # 🆕 Business Development (TO CREATE)
│       ├── arxiv_crawler.py
│       ├── mit_scraper.py
│       ├── keyword_extractor.py
│       └── direction_engine.py
│
├── docs/                         # Documentation
│   ├── ARCHITECTURE_MASTER.md   # This file
│   ├── COMMAND_REFERENCE.md     # Unified 94 commands
│   ├── FLIGHT_CHECKLIST.md      # Progress tracking
│   ├── MODEL.md                 # Model specification
│   ├── CONTEXT.md               # Operational context
│   ├── MANDATE.md               # Mission statement
│   └── changelog/
│       └── CHANGELOG.md
│
├── scripts/                      # Utility scripts
│   └── test_smtp_consensus.py
│
├── logs/                         # System logs
├── data/                         # Persistent data
└── obsidian_sync/               # Operator notes
    └── gladius/.dev/todo.md
```

---

## 🔄 THE SILENT LEARNING LOOP

SENTINEL manages a **detached background process** that runs continuously:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SENTINEL LEARNING DAEMON                              │
│                  (Always Running - Turing Safe)                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │   DISCOVER   │───▶│    LEARN     │───▶│   TRAIN      │              │
│  │              │    │              │    │              │              │
│  │ • Web search │    │ • Parse new  │    │ • Generate   │              │
│  │ • arXiv      │    │   theories   │    │   training   │              │
│  │ • MIT        │    │ • Extract    │    │   data       │              │
│  │ • GitHub     │    │   patterns   │    │ • Fine-tune  │              │
│  │ • Keywords   │    │ • Correlate  │    │   model      │              │
│  └──────────────┘    └──────────────┘    └──────────────┘              │
│         │                   │                   │                       │
│         └───────────────────┼───────────────────┘                       │
│                             ▼                                            │
│                    ┌──────────────┐                                     │
│                    │   UPGRADE    │                                     │
│                    │              │                                     │
│                    │ • Benchmark  │                                     │
│                    │ • Compare    │                                     │
│                    │ • Promote    │                                     │
│                    │ • Rollback   │                                     │
│                    └──────────────┘                                     │
│                             │                                            │
│                             ▼                                            │
│                    ┌──────────────┐                                     │
│                    │   REVIEW     │                                     │
│                    │              │                                     │
│                    │ • Self-eval  │                                     │
│                    │ • Update     │                                     │
│                    │   targets    │                                     │
│                    │ • Log cycle  │                                     │
│                    └──────────────┘                                     │
│                             │                                            │
│                             └──────────────▶ (Loop back to DISCOVER)    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Turing Safety Features:
1. **Watchdog Process**: Monitors daemon and auto-restarts on crash
2. **State Persistence**: SQLite saves loop state for recovery
3. **Checkpoint System**: Saves progress at each phase
4. **Password-Protected Kill**: Only explicit command can terminate
5. **Graceful Degradation**: Falls back to previous known-good state

---

## 📊 RESEARCH PIPELINES

### Pipeline 1: SYNDICATE (Market Intelligence)
**Status**: ✅ OPERATIONAL

```
SYNDICATE Pipeline:
  yfinance → FRED → Analysis → Charts → Journals → Publishing
  
Multiple Syndicate instances can run in parallel:
  - syndicate_gold (XAUUSD) ✅
  - syndicate_btc (BTCUSD) 🚧
  - syndicate_equities (SPY, QQQ) 📋
  - syndicate_crypto (Top 10) 📋
```

### Pipeline 2: Business Development Research
**Status**: 📋 TO IMPLEMENT

```
Research Pipeline:
  Vision Config → Direction Engine → arXiv/MIT → Keyword Extraction
       ↓
  Trend Analysis → Opportunity Scoring → Action Items → Proposals
       ↓
  Consensus (Discord/Email) → Implementation → Self-Improvement
```

**Sources**:
- arXiv (AI/ML papers)
- MIT News (technology research)
- GitHub Trending (code/tools)
- HuggingFace Papers (model releases)
- Google Scholar (academic)

---

## 🔧 COMMAND OVERLAP ANALYSIS

### POTENTIAL CONFLICTS:

| Command | GLADIUS | SENTINEL | LEGION | Resolution |
|---------|---------|----------|--------|------------|
| `start` | cognition | asas | enterprise | Namespace prefix |
| `stop` | cognition | asas | enterprise | Namespace prefix |
| `status` | model | security | agents | Namespace prefix |
| `monitor` | training | threats | dashboard | Namespace prefix |
| `scan` | - | security | - | No conflict |
| `agents` | - | - | list/info | No conflict |

### RESOLUTION: Unified CLI with Namespaces

```bash
# Master control
./gladius.sh <system> <command> [args]

# Examples:
./gladius.sh gladius train          # Train the native model
./gladius.sh gladius benchmark      # Benchmark the model
./gladius.sh gladius status         # Model status

./gladius.sh sentinel start         # Start security daemon
./gladius.sh sentinel status        # Security status
./gladius.sh sentinel scan          # Run security scan

./gladius.sh legion start           # Start agent ecosystem
./gladius.sh legion agents list     # List agents
./gladius.sh legion status          # Enterprise status

./gladius.sh artifact syndicate     # Run syndicate analysis
./gladius.sh artifact publish       # Publish content
./gladius.sh artifact research      # Run research pipeline
```

---

## 📋 IMPLEMENTATION PLAN

### Phase 1: Isolate GLADIUS Model (Current Session)
1. Create `GLADIUS/` directory structure
2. Move model files from `Artifact/syndicate/models/`
3. Move training harness from cognition
4. Create isolated model documentation
5. Update imports and paths

### Phase 2: Integrate SENTINEL
1. Install SENTINEL dependencies
2. Create `services/` directory for daemons
3. Implement `learning_daemon.py`
4. Implement `research_daemon.py`
5. Implement `watchdog.py` for Turing safety
6. Create unified configuration

### Phase 3: Confine LEGION
1. Move LEGION into `Artifact/`
2. Resolve command overlaps
3. Integrate with existing automata
4. Map all 26 agents to Gladius tools
5. Update orchestrator to use native AI

### Phase 4: Research Pipeline
1. Create `Artifact/research/` structure
2. Implement arXiv crawler
3. Implement keyword extractor
4. Connect to direction engine
5. Feed into self-improvement loop

### Phase 5: Unified Documentation
1. System mapping for each component
2. CLI documentation with all commands
3. Integration guide
4. Deployment documentation
5. Model card for publishing

---

## 🔐 ENVIRONMENT VARIABLES (UNIFIED)

```bash
# === GLADIUS MODEL ===
GLADIUS_MODEL_PATH=/home/adam/worxpace/gladius/GLADIUS/models/production
GLADIUS_TRAINING_DATA=/home/adam/worxpace/gladius/GLADIUS/training/data
GLADIUS_ENABLED=true

# === SENTINEL ===
SENTINEL_ENABLED=true
SENTINEL_WATCHDOG=true
SENTINEL_LEARNING_LOOP=true
SENTINEL_KILL_PASSWORD=<secure_hash>

# === LEGION ===
LEGION_ENABLED=true
LEGION_AGENTS_ACTIVE=26

# === RESEARCH ===
RESEARCH_ARXIV_ENABLED=true
RESEARCH_KEYWORDS=["AI", "LLM", "GGUF", "fine-tuning", "trading"]
RESEARCH_INTERVAL_HOURS=6

# === EXISTING (from .env) ===
# ... all current variables ...
```

---

## 📊 SYSTEM STATUS SUMMARY

| Component | Status | Location | Dependencies |
|-----------|--------|----------|--------------|
| GLADIUS Model | 🚧 Needs Isolation | `Artifact/syndicate/src/cognition/` | - |
| SENTINEL | ✅ Cloned | `/SENTINEL/` | psutil, aiohttp |
| LEGION | ✅ Cloned | `/LEGION/` | asyncio, sqlite3 |
| Syndicate | ✅ Operational | `Artifact/syndicate/` | yfinance, ollama |
| Automata | ✅ Operational | `Artifact/deployment/automata/` | social media APIs |
| Research Pipeline | 📋 Not Started | `Artifact/research/` | arxiv, beautifulsoup |

---

*This document will be updated as components are integrated.*
