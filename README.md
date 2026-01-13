# GLADIUS

<p align="center">
  <img src="https://img.shields.io/badge/Language-C++-blue.svg" alt="C++">
  <img src="https://img.shields.io/badge/Python-3.10+-yellow.svg" alt="Python">
  <img src="https://img.shields.io/badge/AI-Native-brightgreen.svg" alt="Native AI">
  <img src="https://img.shields.io/badge/VectorDB-Hektor-informational.svg" alt="Hektor VDB">
  <img src="https://img.shields.io/badge/Status-65%25_Complete-orange.svg" alt="Progress">
</p>

> **Autonomous Enterprise Operating System** — Self-improving AI infrastructure with native cognition, multi-platform publishing, and market intelligence.

---

## What Gladius Actually Does

Gladius is an **autonomous enterprise system** that:

1. **Researches** — Continuously gathers and analyzes market data (gold, crypto, equities)
2. **Thinks** — Native AI cognition with vector memory, pattern learning, and self-improvement
3. **Acts** — Generates reports, publishes to social platforms, sends alerts
4. **Learns** — Tracks outcomes, adjusts strategies, proposes and implements improvements

### Core Workflow

```
Market Data → Syndicate Analysis → Cognition Processing → Publishing Pipeline → Social Channels
     ↓                                    ↓                        ↓
   Charts                         Self-Improvement            Engagement Tracking
   Reports                        Training Data                Optimal Timing
   Journals                       Proposals                    Multi-Platform
```

---

## System Schematic

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         GLADIUS ENTERPRISE OS                            │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   SYNDICATE  │  │   COGNITION  │  │   AUTOMATA   │  │     ARTY     │ │
│  │  (Research)  │  │   (Brain)    │  │  (Publish)   │  │  (Engage)    │ │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤  ├──────────────┤ │
│  │ • yfinance   │  │ • Hektor VDB │  │ • Twitter/X  │  │ • Discord    │ │
│  │ • FRED       │  │ • 16 Tools   │  │ • LinkedIn   │  │ • Consensus  │ │
│  │ • Charts     │  │ • Self-Imp.  │  │ • Facebook   │  │ • Community  │ │
│  │ • Journals   │  │ • Training   │  │ • Instagram  │  │              │ │
│  │ • Catalysts  │  │ • Memory     │  │ • YouTube    │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                        INFRASTRUCTURE                              │ │
│  │  FastAPI (7000) | Flask (5000) | Grafana (3001) | SQLite | Hektor  │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

```bash
# Start all services
./gladius.sh start

# Check system health
./gladius.sh health

# Run a complete cycle (research → publish)
./gladius.sh cycle

# Run self-improvement
./gladius.sh improve
```

### Configure Platforms (Optional)

Edit `.env` to add API credentials:
```bash
# Twitter/X
TWITTER_BEARER_TOKEN=your_token
TWITTER_ENABLED=true

# LinkedIn
LINKEDIN_ACCESS_TOKEN=your_token
LINKEDIN_ENABLED=true

# Discord (for consensus voting)
DISCORD_WEBHOOK_URL=your_webhook
DISCORD_ENABLED=true
```

---

## Architecture

### Components

| Component | Purpose | Progress |
|-----------|---------|----------|
| **Syndicate** | Market research, data ingestion, chart generation | 90% |
| **Cognition** | Hektor VDB, memory, tools, self-improvement | 85% |
| **Automata** | Social publishing, scheduling, engagement | 70% |
| **Arty** | Discord bot, consensus, community | 50% |
| **Infrastructure** | APIs, databases, monitoring | 60% |

### Data Flow

```
1. INGEST    → yfinance, FRED, news APIs → Raw Data
2. ANALYZE   → QuantEngine, Ollama → Reports, Charts
3. STORE     → SQLite, Hektor VDB → Memory
4. PUBLISH   → ContentAdapter → Twitter, LinkedIn, etc.
5. LEARN     → EngagementTracker → Optimize
```

---

## Cognition Engine

### Memory Tools (16)

| Tool | Description |
|------|-------------|
| `list_databases` | List connected databases |
| `read_db` | Query SQL databases |
| `write_db` | Write to databases |
| `search` | Vector similarity search |
| `hybrid_search` | Combined vector + keyword |
| `get_context` | Retrieve recent context |
| `remember` | Store in vector memory |
| `recall` | Retrieve from memory |
| `list_dir` | Browse workspace |
| `read_file` | Read file contents |
| `write_file` | Write files |
| `file_exists` | Check file existence |
| `get_tools` | List available tools |
| `get_history` | Get tool usage history |
| `call_tool` | Dynamic tool invocation |
| `execute_tool` | Execute with full context |

### Self-Improvement

```
Identify Issues → Create Proposal → Review/Approve → Implement → Learn
      ↓                                    ↓
  Low Risk: Auto-approve         Medium Risk: Discord vote
  High Risk: Email escalation
```

### Usage

```python
from cognition import MemoryModule, SelfImprovementEngine

# Memory operations
memory = MemoryModule()
result = memory.execute_tool("hybrid_search", {"query": "gold analysis", "k": 5})

# Self-improvement
engine = SelfImprovementEngine()
proposal = engine.create_proposal(
    title="Improve pattern accuracy",
    category="accuracy"
)
```

---

## Publishing Pipeline

### Supported Platforms

| Platform | Adapter | Features |
|----------|---------|----------|
| Twitter/X | ✅ | Threads, media, analytics |
| LinkedIn | ✅ | Articles, company pages |
| Facebook | ✅ | Posts, page management |
| Instagram | ✅ | Visual posts, stories |
| YouTube | ✅ | Video descriptions, SEO |

### Automatic Scheduling

- **Optimal posting times** per platform
- **Rate limiting** per platform
- **Priority queue** for urgent content
- **Auto-retry** on failures

### Usage

```python
from publishing import PublishingPipeline

pipeline = PublishingPipeline(
    syndicate_output_dir='./output',
    config=config
)

# Run a publishing cycle
results = await pipeline.run_publishing_cycle()
print(f"Published: {results['published']}")
```

---

## Documentation

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System diagrams and data flow |
| [CONTEXT.md](CONTEXT.md) | Operational context and history |
| [MANDATE.md](MANDATE.md) | Mission and responsibilities |
| [MODEL.md](MODEL.md) | Native AI model strategy |
| [COMMANDS.md](COMMANDS.md) | CLI commands reference |
| [SNAPSHOT.md](SNAPSHOT.md) | System benchmarks and status |
| [FLIGHT_CHECKLIST.md](FLIGHT_CHECKLIST.md) | Implementation progress |

---

## Directory Structure

```
gladius/
├── Artifact/
│   ├── syndicate/           # Research pipeline
│   │   └── src/cognition/   # Cognition engine
│   ├── hektor/              # Native vector database
│   ├── deployment/
│   │   └── automata/        # Publishing & automation
│   │       ├── social_media/
│   │       ├── publishing/
│   │       └── scheduler/
│   └── arty/                # Discord bot
├── gladius.sh               # Main control script
├── .env                     # API keys and config
└── *.md                     # Documentation
```

---

## Current Status

**Overall Progress: 65%**

| Component | Status |
|-----------|--------|
| Core Infrastructure | 83% |
| Cognition Engine | 85% |
| Syndicate (Research) | 90% |
| Automata (Publishing) | 70% |
| Arty (Engagement) | 50% |
| Digital Footprint | 0% |

See [FLIGHT_CHECKLIST.md](FLIGHT_CHECKLIST.md) for detailed breakdown.

---

## License

See [LICENSE.md](LICENSE.md)

---

*Last updated: 2026-01-13*

