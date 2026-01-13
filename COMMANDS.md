# Gladius Command Reference

> Complete operational command reference for developers and operators

---

## Quick Start

```bash
cd /home/adam/worxpace/gladius

# Start all services (with automatic health check)
./gladius.sh start

# Stop all services (with regression verification)
./gladius.sh stop

# Check status
./gladius.sh status

# Full health check
./gladius.sh health
```

---

## Gladius Control Script

The unified `gladius.sh` script manages all services:

| Command | Description |
|---------|-------------|
| `./gladius.sh start` | Start all services + health check |
| `./gladius.sh start --with-frontend` | Start all + React dev server |
| `./gladius.sh stop` | Stop all services + regression check |
| `./gladius.sh stop --force` | Force kill all services |
| `./gladius.sh restart` | Stop then start all |
| `./gladius.sh status` | Quick status check |
| `./gladius.sh health` | Full health check with API tests |
| `./gladius.sh infra` | Test Infra API specifically |
| `./gladius.sh logs` | Tail all log files |

---

## Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| Infra API | 7000 | Market data, assets, portfolios |
| Dashboard Backend | 5000 | Automata control, content management |
| Dashboard Frontend | 3000 | React UI (optional) |
| Grafana | 3000 | Metrics dashboards (via Docker) |

---

## Cognition Engine

**Location**: `Artifact/syndicate/src/cognition/`

### Python Usage

```python
from cognition import SyndicateCognition

# Initialize
cognition = SyndicateCognition(
    data_dir='./data',
    output_dir='./output'
)

# Ingest all reports into vectors
counts = cognition.ingest_all_reports()

# Semantic search
results = cognition.search("gold bullish momentum", k=5)

# Get context for AI analysis
context = cognition.get_context_for_analysis("Gold testing resistance")

# Get stats
stats = cognition.stats()

cognition.close()
```

### Hektor VDB Usage (Native)

```python
from cognition.hektor_store import HektorVectorStore, get_vector_store

# Get best available store (Hektor if available, hnswlib fallback)
store = get_vector_store("./vectors", dim=384, prefer_hektor=True)

# Add documents
store.add_text("doc1", "Gold broke above resistance", {"type": "journal"}, doc_type="journal")

# Vector search
results = store.search("gold breakout", k=5)

# Hybrid search (vector + BM25)
results = store.hybrid_search("gold breakout", k=5, vector_weight=0.7, lexical_weight=0.3)

# Stats
print(store.stats())
```

### CLI Testing

```bash
cd Artifact/syndicate

# Test cognition engine
python3 -c "
import sys; sys.path.insert(0, 'src')
from cognition import SyndicateCognition
cog = SyndicateCognition('./data', './output')
print(cog.stats())
cog.close()
"

# Test Hektor VDB
python3 -c "
import sys; sys.path.insert(0, 'src')
sys.path.insert(0, '../hektor/build')
from cognition.hektor_store import HektorVectorStore
print('Hektor VDB available')
"
```

---

## Hektor VDB (Native C++)

**Location**: `Artifact/hektor/`

### Build Commands

```bash
cd Artifact/hektor
mkdir -p build && cd build

# Standard build with Python bindings
cmake .. -DCMAKE_BUILD_TYPE=Release -DVDB_BUILD_PYTHON=ON
make -j$(nproc)

# Full build with all features
cmake .. -DCMAKE_BUILD_TYPE=Release \
  -DVDB_BUILD_PYTHON=ON \
  -DVDB_USE_LLAMA_CPP=ON \
  -DVDB_USE_ONNX_RUNTIME=ON
make -j$(nproc)

# Verify build
ls -la pyvdb*.so libvdb_core.a hektor
```

### CLI Usage

```bash
# Create database
./hektor create my_vectors --dimension 384

# Add vectors from file
./hektor add my_vectors --file vectors.json

# Search
./hektor search my_vectors --query "test query" --k 10

# Stats
./hektor stats my_vectors
```

### Build Options

| Option | Default | Description |
|--------|---------|-------------|
| `VDB_BUILD_PYTHON` | ON | Build Python bindings (pyvdb) |
| `VDB_USE_LLAMA_CPP` | ON | Enable llama.cpp for local inference (b7716) |
| `VDB_USE_AVX2` | ON | Enable AVX2 SIMD optimizations |
| `VDB_USE_AVX512` | OFF | Enable AVX-512 optimizations |
| `VDB_ENABLE_GPU` | OFF | Enable CUDA GPU acceleration |
| `VDB_USE_ONNX_RUNTIME` | ON | ONNX Runtime for text/image encoders |

### Dependencies

```bash
# For ONNX Runtime support
sudo apt install libonnxruntime-dev

# For llama.cpp (fetched automatically)
# Uses tag b7716 with updated API
```

---

## Infrastructure API (Port 7000)

**Location**: `Artifact/deployment/infra/`

### Start Server

```bash
cd Artifact/deployment
uvicorn infra.api.app:app --host 127.0.0.1 --port 7000

# Production
uvicorn infra.api.app:app --host 0.0.0.0 --port 7000 --workers 4
```

### Endpoints

```bash
# Markets
curl http://127.0.0.1:7000/markets
curl -X POST http://127.0.0.1:7000/markets \
  -H "Content-Type: application/json" \
  -d '{"symbol": "XAUUSD", "name": "Gold", "exchange": "COMEX"}'

# Assets
curl http://127.0.0.1:7000/assets

# Portfolios
curl http://127.0.0.1:7000/portfolios
curl http://127.0.0.1:7000/portfolios/{id}

# Price Ingestion
curl -X POST http://127.0.0.1:7000/prices \
  -H "Content-Type: application/json" \
  -d '{"ticker": "BTC-USD", "close": 42500, "timestamp": "2026-01-11T12:00:00Z"}'
```

### Seed Data

```bash
cd Artifact/deployment/infra
python scripts/seed_gold_bitcoin.py
```

---

## Automata Dashboard (Port 5000)

**Location**: `Artifact/deployment/automata/dashboard/`

### Start Backend

```bash
cd Artifact/deployment/automata/dashboard/backend
python app.py

# Production
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Start Frontend

```bash
cd Artifact/deployment/automata/dashboard/frontend
npm install
npm run dev      # Development (port 3000)
npm run build    # Production build
```

### Authentication

```bash
# Login
TOKEN=$(curl -s -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "gladius"}' | jq -r '.access_token')

# Use token
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/status
```

### Endpoints

```bash
# System
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/status
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/overview

# Context Engine
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/context/entries
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/context/stats
curl -X POST -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/context/reflect

# Content
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/content/drafts
```

---

## Syndicate Pipeline

**Location**: `Artifact/syndicate/`

### Daemon Mode

```bash
cd Artifact/syndicate

# Continuous operation
python run.py --daemon

# Single cycle
python run.py --once

# With Ollama preference
PREFER_OLLAMA=1 python run.py --daemon
```

### LLM Worker

```bash
cd Artifact/syndicate
python scripts/llm_worker.py
```

### Database Management

```bash
cd Artifact/syndicate
python db_manager.py       # Initialize
python check_db_vm.py      # Check on VM
python reset_db_vm.py      # Reset
```

---

## Memory Module (Native Tool Calling)

**Location**: `Artifact/syndicate/src/cognition/`

### Available Tools (In Development)

| Tool | Description |
|------|-------------|
| `read_db(name, query)` | Read from any connected database |
| `write_db(name, data)` | Write to any connected database |
| `search(query, k)` | Semantic search across all vectors |
| `get_context(query)` | Retrieve historical context |
| `read_file(path)` | Read file from workspace |
| `write_file(path, data)` | Write file to workspace |
| `list_dir(path)` | List directory contents |

### Database Connections

| Database | Type | Path |
|----------|------|------|
| Hektor VDB | Vector | `data/hektor.db` |
| Syndicate DB | SQLite | `data/syndicate.db` |
| Arty Store | SQLite | `Artifact/arty/store/arty.db` |
| Predictions | SQLite | `data/predictions.db` |
| Configs | JSON | `data/*.json` |

---

## Environment Variables

### Core

```bash
export INFRA_API_URL=http://127.0.0.1:7000
export PREFER_OLLAMA=1
```

### AI Providers

```bash
export GOOGLE_API_KEY=your-gemini-key
export NOTION_TOKEN=your-notion-token
export NOTION_DATABASE_ID=your-db-id
```

### Dashboard

```bash
export DASHBOARD_SECRET_KEY=your-secret
export JWT_SECRET_KEY=your-jwt-secret
export DASHBOARD_ALLOW_DEV_LOGIN=false
```

### Discord/LinkedIn

```bash
export DISCORD_TOKEN=your-bot-token
export DISCORD_CLIENT_ID=your-client-id
export LINKEDIN_ACCESS_TOKEN=your-token
```

---

## Emergency Operations

### Stop All

```bash
# By port
kill $(lsof -t -i:7000)   # Infra API
kill $(lsof -t -i:5000)   # Dashboard
kill $(lsof -t -i:3000)   # Frontend

# By process
pkill -f "uvicorn"
pkill -f "run.py"
```

### Check Services

```bash
# Ports in use
ss -tuln | grep -E '(7000|5000|3000)'

# Health checks
curl -s http://127.0.0.1:7000/docs > /dev/null && echo "Infra: OK" || echo "Infra: DOWN"
curl -s http://127.0.0.1:5000/health > /dev/null && echo "Dashboard: OK" || echo "Dashboard: DOWN"
```

---

## Log Locations

```bash
# Syndicate
tail -f Artifact/syndicate/run_once.log
tail -f Artifact/syndicate/output_log.txt

# Dashboard
tail -f Artifact/deployment/dashboard_backend.log
tail -f Artifact/deployment/infra_api.log
```

---

## Database Inspection

```bash
# Syndicate DB
sqlite3 Artifact/syndicate/data/syndicate.db ".tables"
sqlite3 Artifact/syndicate/data/syndicate.db "SELECT * FROM llm_tasks ORDER BY created_at DESC LIMIT 10;"

# Arty store
sqlite3 Artifact/arty/store/arty.db ".tables"

# Hektor VDB
./Artifact/hektor/build/hektor stats ./data/hektor.db
```

---

## Access URLs

| Service | URL |
|---------|-----|
| Infra API Docs | http://127.0.0.1:7000/docs |
| Dashboard | http://127.0.0.1:5000 |
| Dashboard Frontend | http://127.0.0.1:3000 |
| Grafana | http://127.0.0.1:3000 |

---

*Generated: 2026-01-13*
