# SYSTEM ARCHITECTURE

> **Generated**: 2026-01-31T14:45:00Z  
> **Version**: gladius1.1:71M-native  
> **Purpose**: Complete system architecture for Artifact Virtual Enterprise

---

## 🎯 CORE PHILOSOPHY

**GLADIUS** = The Native AI (the brain) - 71M parameter GGUF model  
**HEKTOR VDB** = Vector Memory (contextual recall)  
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
│  │                    GLADIUS 1.1:71M-native                        │   │
│  │                   (Native AI - The Brain)                        │   │
│  │                                                                   │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │   │
│  │  │ Cognition│ │ Hektor   │ │  Router  │ │ Trainer  │           │   │
│  │  │  Engine  │ │   VDB    │ │llama.cpp │ │ CPU/GPU  │           │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                        │   │
│  │  │  Chat    │ │ Twitter  │ │  Build   │                        │   │
│  │  │ Interface│ │  Agent   │ │  Class   │                        │   │
│  │  └──────────┘ └──────────┘ └──────────┘                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│         ┌────────────────────┼────────────────────┐                    │
│         ▼                    ▼                    ▼                    │
│  ┌────────────┐       ┌────────────┐       ┌────────────┐              │
│  │  SENTINEL  │       │   LEGION   │       │  SYNDICATE │              │
│  │ (Guardian) │       │  (Agents)  │       │  (Data)    │              │
│  │            │       │            │       │            │              │
│  │ • AI/AGI   │       │ • 26 agents│       │ • Markets  │              │
│  │   Research │       │ • Workflow │       │ • News     │              │
│  │ • Threats  │       │ • Messaging│       │ • Context  │              │
│  └────────────┘       └────────────┘       └────────────┘              │
│         │                    │                    │                    │
│         └────────────────────┼────────────────────┘                    │
│                              ▼                                          │
│                       ┌────────────┐                                   │
│                       │ HEKTOR VDB │                                   │
│                       │            │                                   │
│                       │ • Vectorize│                                   │
│                       │ • Context  │                                   │
│                       │ • Memory   │                                   │
│                       └────────────┘                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 DIRECTORY STRUCTURE

```
/home/adam/worxpace/gladius/
├── gladius.sh                    # Master control script
├── config.json                   # Module toggles
├── .env                          # Environment & secrets
│
├── GLADIUS/                      # 🧠 NATIVE AI MODEL
│   ├── models/
│   │   └── native/              # gladius1.1-71M.gguf
│   ├── training/
│   │   └── gladius_trainer.py   # Unified CPU/GPU trainer
│   ├── router/                  # Tool routing (llama.cpp)
│   ├── utils/
│   │   ├── hardware.py          # GPU/CPU auto-detection
│   │   └── hektor_memory.py     # Vector DB integration
│   ├── chat_server.py           # Chat CLI + HTTP API
│   ├── twitter_agent.py         # Autonomous Twitter
│   ├── speak.py                 # Direct conversation
│   └── docs/                    # Model documentation
│       ├── ARCHITECTURE.md      # Blueprint
│       └── MODEL_CARD.md        # HuggingFace card
│
├── SENTINEL/                     # 🛡️ GUARDIAN PROCESS
│   ├── asas_cli.py              # CLI interface
│   ├── services/
│   │   ├── learning_daemon.py   # Continuous learning
│   │   └── watchdog.py          # Process recovery
│   └── config/
│       └── research_targets.json # AI/AGI/xAI research
│
├── LEGION/                       # 🤖 AGENT ECOSYSTEM
│   └── legion/
│       ├── cli.py               # CLI interface
│       ├── core_framework.py    # Agent framework
│       └── agents/              # 26 specialized agents
│
├── Artifact/                     # 📦 ENTERPRISE OPS
│   ├── syndicate/               # Market + News Data
│   │   └── src/cognition/       # Cognition engine
│   └── deployment/
│       └── automata/            # Social media + ERP
│
├── build_class/                  # 🔧 CODE BUILDER
│   ├── adapter.py               # llama.cpp adapter
│   └── builder.py               # Code generation
│
├── ui/                           # 🖥️ ELECTRON UI
│   └── src/                     # React + Electron
│
└── docs/                         # 📚 DOCUMENTATION
    ├── ARCHITECTURE.md          # This file
    ├── COMMAND_REFERENCE.md     # 94 commands
    └── MODEL.md                 # Model specification
```

---

## 🔄 THE DATA FLOW

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐                              ┌──────────────┐         │
│  │   SENTINEL   │                              │  SYNDICATE   │         │
│  │  (R&D Data)  │                              │(Market Data) │         │
│  │              │                              │              │         │
│  │ • AI/AGI    │                              │ • yfinance   │         │
│  │   research   │                              │ • FRED       │         │
│  │ • xAI news   │                              │ • News       │         │
│  │ • Threats    │                              │ • Trends     │         │
│  └──────┬───────┘                              └──────┬───────┘         │
│         │                                             │                  │
│         └─────────────────┬───────────────────────────┘                  │
│                           │                                              │
│                           ▼                                              │
│                  ┌─────────────────┐                                    │
│                  │   HEKTOR VDB    │                                    │
│                  │                 │                                    │
│                  │ • Vectorize     │                                    │
│                  │ • Contextualize │                                    │
│                  │ • Store/Recall  │                                    │
│                  │ • SIMD Accel    │                                    │
│                  └────────┬────────┘                                    │
│                           │                                              │
│                           ▼                                              │
│                  ┌─────────────────┐                                    │
│                  │     GLADIUS     │                                    │
│                  │   (71M GGUF)    │                                    │
│                  │                 │                                    │
│                  │ • Learn tools   │                                    │
│                  │ • Recall context│                                    │
│                  │ • Self-improve  │                                    │
│                  └────────┬────────┘                                    │
│                           │                                              │
│              ┌────────────┼────────────┐                                │
│              ▼            ▼            ▼                                │
│      ┌───────────┐ ┌───────────┐ ┌───────────┐                         │
│      │   CHAT    │ │  TWITTER  │ │  BUILD    │                         │
│      │ Interface │ │   Agent   │ │   CLASS   │                         │
│      └───────────┘ └───────────┘ └───────────┘                         │
│                                                                          │
│    (Feedback from all interactions feeds back into Hektor)              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Hektor VDB Integration

```python
from hektor_vdb import HektorDB

# Initialize vector database
db = HektorDB(path="./data/hektor")

# Store context from SENTINEL/SYNDICATE
db.add(
    texts=["AI research paper on AGI safety..."],
    metadata=[{"source": "sentinel", "type": "research"}]
)

# Recall relevant context for GLADIUS
results = db.search("What are the latest AGI threats?", k=5)
```

---

## 📊 DATA PIPELINES

### SENTINEL (R&D Pipeline)
**Focus**: AI, AGI, xAI threats and research

```
Research Targets → Web Crawl → Analysis → Vectorize → Hektor
    │
    ├── arXiv (AI papers)
    ├── GitHub (trending AI repos)
    ├── HuggingFace (model releases)
    └── Security advisories
```

### SYNDICATE (Market Pipeline)
**Focus**: Market data and current affairs

```
Data Sources → Fetch → Analyze → Vectorize → Hektor
    │
    ├── yfinance (market data)
    ├── FRED (economic indicators)
    ├── News APIs (current affairs)
    └── Social sentiment
```

---

## 🔧 UNIFIED CLI

All commands use namespace prefixes to avoid conflicts:

```bash
# Master control
./gladius.sh <command> [args]

# Core commands
./gladius.sh run                  # Lightweight startup (recommended)
./gladius.sh start                # Full system startup
./gladius.sh stop                 # Stop all services
./gladius.sh status               # Quick status check

# GLADIUS AI
./gladius.sh chat                 # Chat interface
./gladius.sh speak                # Direct conversation
./gladius.sh train                # Run training

# Social
./gladius.sh twitter test         # Test Twitter connection
./gladius.sh twitter-run          # Start Twitter agent
```

---

## 📊 SYSTEM STATUS

| Component | Status | Notes |
|-----------|--------|-------|
| Native GGUF Model | ✅ | gladius1.1:71M trained |
| llama.cpp Integration | ✅ | Full native inference |
| Hektor VDB | ✅ | Vector memory active |
| Chat Interface | ✅ | CLI + HTTP API |
| Twitter Agent | ✅ | Autonomous engagement |
| CPU/GPU Auto-detect | ✅ | Automatic fallback |
| SENTINEL | ✅ | R&D on AI/AGI/xAI |
| SYNDICATE | ✅ | Market + news data |
| Training Pipeline | ✅ | Dual CPU/GPU |
| LEGION | 🚧 | Agents pending integration |
| Electron UI | 🚧 | Dashboard in progress |

---

## 🔐 ENVIRONMENT VARIABLES

```bash
# === GLADIUS MODEL ===
GLADIUS_ENABLED=true
ADAPTER_TYPE=llamacpp
LLAMA_SERVER_URL=http://localhost:8080
LLAMA_MODEL=gladius1.1:71M-native

# === HEKTOR VDB ===
HEKTOR_PATH=./data/hektor
HEKTOR_EMBEDDING_MODEL=all-MiniLM-L6-v2

# === SENTINEL ===
SENTINEL_ENABLED=true
SENTINEL_RESEARCH_TARGETS=AI,AGI,xAI,threats

# === HARDWARE ===
PREFER_GPU=true
FALLBACK_TO_CPU=true
MAX_MEMORY_MB=4096
```

---

*Document Version*: 2.0.0  
*Last Updated*: 2026-01-31  
*Model Version*: gladius1.1:71M-native
