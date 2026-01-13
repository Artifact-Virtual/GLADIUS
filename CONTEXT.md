# Gladius Context

> Working context and operational notes for the Gladius autonomous enterprise system.

---

## Overview

Gladius is an autonomous enterprise operating system that manages multiple artifacts (autonomous business units) through a unified context and cognition layer.

- **Root**: `/home/adam/worxpace/gladius`
- **Primary Domain**: artifactvirtual.com (planned)

---

## Active Artifacts

### Alpha: Syndicate (Research)
- **Path**: `Artifact/syndicate/`
- **Purpose**: Market research, analysis, journal generation
- **Status**: ✅ Production
- **Cognition**: Integrated (HNSW + SQLite)

### Beta: Cthulu (Trading)
- **Path**: External (`/_build/cthulu/`)
- **Purpose**: Trade execution via MQL5/MetaTrader 5
- **Status**: ✅ Staging (GCP deployed)

### Infrastructure
- **Infra API** (7000): Markets, assets, portfolios
- **Automata Dashboard** (5000): Control panel
- **Frontend UI** (3000): React operator interface

---

## Cognition Engine

The cognition engine provides semantic memory across all artifacts:

```
Location: Artifact/syndicate/src/cognition/
├── __init__.py
├── embedder.py          # TF-IDF / neural embeddings
├── vector_store.py      # HNSW index + SQLite persistence
└── syndicate_integration.py  # Report ingestion & search
```

**Current State**:
- Documents indexed: 12+
- Vector dimension: 384
- Embedder: TF-IDF (sklearn)
- Fallback: SQLite persistence

---

## Environment Variables

```bash
# Core
INFRA_API_URL=http://127.0.0.1:7000
PREFER_OLLAMA=1

# AI Providers
GOOGLE_API_KEY=your-gemini-key
NOTION_TOKEN=your-notion-token

# Dashboard
DASHBOARD_SECRET_KEY=your-secret
JWT_SECRET_KEY=your-jwt-secret
```

---

## Quick Operations

```bash
# Start all services
./gladius.sh start

# Check status
./gladius.sh status

# Stop all services
./gladius.sh stop

# Run single Syndicate cycle
cd Artifact/syndicate && python main.py --once
```

---

## Recent Changes (2026-01-13)

1. **Cognition Engine Integration**
   - Added HNSW-based vector store with SQLite fallback
   - Reports automatically ingested into semantic memory
   - AI analysis now receives historical context

2. **Unified Control Script**
   - `gladius.sh` manages all services
   - Automatic health checks on start
   - Regression verification on stop

3. **Dashboard Enhancement**
   - React frontend at port 3000
   - Backend API at port 5000
   - JWT authentication

---

## Current Limitations / TODOs

- [ ] Fix Hektor C++ VDB for native performance
- [ ] Persist portfolios & positions to SQLite
- [ ] Add API authentication to Infra API
- [ ] Deploy web presence (artifactvirtual.com)
- [ ] Implement blockchain/token architecture

---

## Next Steps

1. **Short-term**: Stabilize Syndicate cognition loop
2. **Medium-term**: Deploy Cthulu to production trading
3. **Long-term**: Web3 integration per artifact

---

*Last updated: 2026-01-13*