# Gladius Architecture

> Autonomous Enterprise Operating System

---

## High-Level Architecture

```
                    ┌─────────────────────────────────────┐
                    │           GLADIUS                   │
                    │   (Autonomous Enterprise Manager)   │
                    │   Context • Vectorization • Memory  │
                    │   ┌─────────────────────────────┐   │
                    │   │     COGNITION ENGINE        │   │
                    │   │   HNSW + SQLite + Hektor    │   │
                    │   └─────────────────────────────┘   │
                    └───────────────┬─────────────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           │                        │                        │
           ▼                        ▼                        ▼
    ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
    │  ARTIFACT   │          │  ARTIFACT   │          │  ARTIFACT   │
    │   ALPHA     │          │    BETA     │          │   THETA     │
    │  Syndicate  │          │   Cthulu    │          │  (Future)   │
    │  Research   │          │   Trading   │          │  Publishing │
    └──────┬──────┘          └──────┬──────┘          └─────────────┘
           │                        │
           ▼                        ▼
    ┌─────────────┐          ┌─────────────┐
    │  Journals   │          │   Execute   │
    │  Analysis   │   ───►   │   Trades    │
    │  Signals    │          │   Manage    │
    └─────────────┘          └─────────────┘
```

---

## Core Components

### 1. Gladius (Enterprise Brain)
- **Context Management**: Unified context across all artifacts
- **Vectorization**: Semantic memory via HNSW index
- **Cognition Engine**: TF-IDF/Neural embeddings with SQLite fallback
- **Memory Persistence**: Historical learning and prediction tracking

### 2. Artifacts (Autonomous Units)
Each artifact is a self-contained operational unit:

| Artifact | Codename | Purpose | Status |
|----------|----------|---------|--------|
| Alpha | Syndicate | Market research & analysis | ✅ Production |
| Beta | Cthulu | Trade execution (MQL5/MT5) | ✅ Staging |
| Theta | TBD | Social/Publishing | 🚧 Planned |

### 3. Infrastructure Layer
- **Infra API** (7000): Market data, assets, portfolios
- **Automata Dashboard** (5000): Control panel, orchestration
- **Frontend UI** (3000): React-based operator interface

---

## Data Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Market Data │────►│   Syndicate  │────►│   Cognition  │
│  (yfinance)  │     │  (Analysis)  │     │   (Vectors)  │
└──────────────┘     └──────┬───────┘     └──────┬───────┘
                            │                     │
                            ▼                     ▼
                     ┌──────────────┐     ┌──────────────┐
                     │   Journals   │     │  Historical  │
                     │   Reports    │     │   Context    │
                     └──────┬───────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   Cthulu     │
                     │  (Execute)   │
                     └──────────────┘
```

---

## Cognition Engine Architecture

```
┌─────────────────────────────────────────────────────┐
│                 COGNITION ENGINE                     │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  Embedder   │  │ VectorStore │  │   SQLite    │ │
│  │  (TF-IDF)   │  │   (HNSW)    │  │  (Fallback) │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘ │
│         │                │                │        │
│         ▼                ▼                ▼        │
│  ┌─────────────────────────────────────────────┐  │
│  │          SyndicateCognition                  │  │
│  │  - Ingest reports into vectors               │  │
│  │  - Semantic search across history            │  │
│  │  - Context retrieval for AI analysis         │  │
│  │  - Learning from predictions                 │  │
│  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Vectorization** | hnswlib, scikit-learn TF-IDF |
| **Persistence** | SQLite, JSON |
| **API Framework** | FastAPI, Flask |
| **Frontend** | React, Vite |
| **Trading** | MQL5, MetaTrader 5 |
| **LLM** | Ollama (primary), Gemini (fallback) |
| **Infrastructure** | GCP, Docker, systemd |

---

## Future: Web3 Integration

| Component | Domain | Purpose |
|-----------|--------|---------|
| Gladius Core | artifactvirtual.com | Enterprise governance |
| Alpha (Syndicate) | /alpha | Research signal access |
| Beta (Cthulu) | /beta | Trading profit sharing |
| Theta | /theta | Content monetization |

Each artifact will have:
- **Blockchain integration** for transparency
- **Utility tokens** for access/governance
- **Soulbound tokens (SBT)** for reputation

---

## File Structure

```
gladius/
├── Artifact/
│   ├── syndicate/         # Alpha: Research engine
│   │   ├── src/
│   │   │   └── cognition/ # Vector memory system
│   │   ├── main.py        # Core daemon
│   │   └── output/        # Generated reports
│   ├── deployment/
│   │   ├── infra/         # Market/Portfolio API
│   │   └── automata/      # Dashboard & orchestration
│   ├── arty/              # Automation framework
│   └── hektor/            # Native VDB (pending fixes)
├── RESEARCH/              # Articles & papers
├── docs/                  # Documentation
├── gladius.sh             # Unified control script
└── ARCHITECTURE.md        # This file
```

---

*Last updated: 2026-01-13*
