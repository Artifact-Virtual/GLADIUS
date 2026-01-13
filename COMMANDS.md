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

### Python Usage

```python
from cognition.memory_module import MemoryModule

# Initialize
mm = MemoryModule(
    base_dir='.',
    workspace_dir='./output',
    sandbox_enabled=True
)

# List databases
result = mm.list_databases()
print(result.data)

# Call any tool
result = mm.call_tool('search', query='gold breakout', k=5)
if result.success:
    print(result.data)

# Workspace operations
result = mm.read_file('output/Journal_2026-01-13.md')
result = mm.list_dir('output')
result = mm.file_exists('config.json')

# Memory operations
mm.remember('gold_pattern', 'Head and shoulders at 2700')
result = mm.recall('gold patterns', k=3)

# Get operation history
result = mm.get_history(last_n=20)

mm.close()
```

### Available Tools

| Tool | Category | Description |
|------|----------|-------------|
| `read_db(name, query)` | database | Read from any connected database |
| `write_db(name, data, table)` | database | Write to any connected database |
| `query_db(name, query)` | database | Execute raw database query |
| `list_databases()` | database | List all connected databases |
| `search(query, k, db_name)` | search | Semantic search across vectors |
| `hybrid_search(query, k)` | search | Vector + BM25 fusion search |
| `get_context(query, k)` | search | Retrieve historical context |
| `read_file(path)` | workspace | Read file from workspace |
| `write_file(path, content)` | workspace | Write file to workspace |
| `list_dir(path)` | workspace | List directory contents |
| `file_exists(path)` | workspace | Check if file exists |
| `remember(key, value, metadata)` | memory | Store memory for recall |
| `recall(query, k)` | memory | Recall related memories |
| `forget(key)` | memory | Remove a memory |
| `get_tools()` | introspection | List available tools |
| `get_history(last_n)` | introspection | Get operation history |

### Database Connections (Auto-Discovered)

| Database | Type | Path |
|----------|------|------|
| Hektor VDB | Vector | `data/vectors/` |
| Syndicate DB | SQLite | `data/syndicate.db` |
| Gold Standard | SQLite | `data/gold_standard.db` |
| Cortex Memory | JSON | `data/cortex_memory.json` |

---

## Prediction Learning System

### Python Usage

```python
from cognition.syndicate_integration import SyndicateCognition

cognition = SyndicateCognition(data_dir='./data', output_dir='./output')

# Record a prediction
cognition.learn_from_prediction(
    prediction_date='2026-01-13',
    predicted_bias='BULLISH',
    actual_outcome='PENDING',
    gold_price_then=2680.0,
    gold_price_now=2695.0,
    market_context='Gold testing 2700 resistance',
    catalysts=['Fed decision', 'CPI data']
)

# Get accuracy stats
accuracy = cognition.get_prediction_accuracy(last_n=30)
print(f"Win rate: {accuracy['win_rate']}%")

# Find similar historical conditions
similar = cognition.get_similar_historical_outcomes(
    'gold testing resistance level', k=5
)

# Get pattern success rate
pattern = cognition.get_pattern_success_rate(
    'gold bullish breakout',
    min_similarity=0.3
)
print(f"Success rate: {pattern['success_rate']}%")

# Generate learning feedback for AI
feedback = cognition.generate_learning_feedback()
print(feedback)

cognition.close()
```

### Learning Methods

| Method | Description |
|--------|-------------|
| `learn_from_prediction()` | Record prediction with context and catalysts |
| `get_similar_historical_outcomes()` | Find similar market conditions |
| `get_pattern_success_rate()` | Calculate pattern reliability |
| `generate_learning_feedback()` | Generate AI context from history |
| `get_prediction_accuracy()` | Comprehensive accuracy statistics |
| `update_pending_predictions()` | Auto-evaluate pending predictions |

---

## Training Data Generation

**Location**: `Artifact/syndicate/src/cognition/training_generator.py`

### Python Usage

```python
from cognition import TrainingDataGenerator, TrainingDataset

# Initialize generator
gen = TrainingDataGenerator(output_dir='./data/training')

# Generate from tool history
from cognition import MemoryModule
mm = MemoryModule(base_dir='.')
history_result = mm.get_history(last_n=100)
dataset = gen.generate_from_history(history_result.data, 'history')

# Generate synthetic examples
synthetic = gen.generate_synthetic(n_per_category=20, dataset_name='synthetic')

# Generate from tool schemas
schemas = gen.generate_from_tool_schemas('schemas')

# Combine datasets
combined = gen.combine_datasets([dataset, synthetic, schemas], 'combined')

# Export in multiple formats
paths = gen.export_all([combined], formats=['chat', 'completion', 'llama'])
print(paths)

mm.close()
```

### Export Formats

| Format | File | Description |
|--------|------|-------------|
| `chat` | `.jsonl` | Conversational instruction format |
| `completion` | `.jsonl` | Prompt-completion pairs |
| `llama` | `.json` | llama.cpp fine-tuning format |
| `tool` | `.jsonl` | OpenAI tool-calling format |

### CLI Usage

```bash
cd Artifact/syndicate

# Test training data generation
python3 -c "
import sys; sys.path.insert(0, 'src')
from cognition import TrainingDataGenerator
gen = TrainingDataGenerator('./data/training')
ds = gen.generate_synthetic(n_per_category=5)
gen.export_all([ds], formats=['llama'])
print(ds.stats())
"
```

---

## Self-Improvement Engine

**Location**: `Artifact/syndicate/src/cognition/self_improvement.py`

### Python Usage

```python
from cognition import SelfImprovementEngine, ImprovementCategory, ProposalStatus

# Initialize
engine = SelfImprovementEngine(
    base_dir='.',
    proposals_dir='./data/improvements/proposals',
    snapshots_dir='./data/improvements/snapshots'
)

# Create a proposal
proposal = engine.create_proposal(
    title='Improve prediction accuracy',
    category=ImprovementCategory.ACCURACY,
    summary='Win rate below 50%, need improvement',
    items=[
        {'description': 'Analyze losing predictions', 'impact': 'high', 'risk': 'low'},
        {'description': 'Add more context', 'impact': 'medium', 'risk': 'low'}
    ]
)

# Submit for review
engine.submit_for_review(proposal.id)

# Review and approve
engine.review_proposal(proposal.id, 'cognition', 'approve', 'Good plan')

# Create implementation plan
engine.create_implementation_plan(
    proposal.id,
    plan='Detailed implementation steps...',
    checklist_items=['Analyze failures', 'Add context', 'Verify improvements']
)

# Begin implementation (creates pre-snapshot)
engine.begin_implementation(proposal.id)

# Complete tasks
engine.complete_task(proposal.id, 'check_0', 'Analysis complete')
engine.complete_task(proposal.id, 'check_1', 'Context added')
engine.complete_task(proposal.id, 'check_2', 'Verified')

# Complete implementation (creates post-snapshot)
engine.complete_implementation(proposal.id)

# Generate report
print(engine.generate_report())

# Get audit trail
trail = engine.get_audit_trail(proposal.id)
for entry in trail:
    print(f"{entry['timestamp']}: {entry['action']}")
```

### Proposal Lifecycle

| Status | Description |
|--------|-------------|
| `DRAFT` | Initial creation |
| `PENDING_REVIEW` | Submitted for review |
| `REVISION_REQUESTED` | Changes requested |
| `APPROVED` | Ready for implementation |
| `REJECTED` | Declined |
| `IMPLEMENTING` | Work in progress |
| `COMPLETED` | Successfully implemented |
| `ROLLED_BACK` | Reverted to previous state |

### Snapshot Management

```python
# Create manual snapshot
snapshot = engine.create_snapshot(
    name='pre_major_change',
    description='Before significant update',
    files_to_backup=['file1.py', 'file2.py'],
    database_paths=['data/syndicate.db']
)

# Restore from snapshot
engine.restore_snapshot(snapshot.id)
```

---

## Cognition Learning Loop

**Location**: `Artifact/syndicate/src/cognition/learning_loop.py`

### Python Usage

```python
from cognition import CognitionLearningLoop, run_learning_cycle, run_benchmark

# Full loop initialization
with CognitionLearningLoop(
    base_dir='.',
    data_dir='./data',
    output_dir='./output'
) as loop:
    # Run single cycle
    result = loop.run_cycle(current_gold_price=2690.0)
    print(f"Ingested: {result.reports_ingested} reports")
    print(f"Training examples: {result.training_examples_generated}")
    print(f"Success rate: {result.pattern_success_rate}%")
    
    # Get learning feedback for AI context
    feedback = loop.get_learning_feedback()
    print(feedback)
    
    # Get stats
    print(loop.stats())

# Quick convenience functions
result = run_learning_cycle('.', current_gold_price=2690.0)
benchmark = run_benchmark('.', n_cycles=10)
```

### Benchmark Mode

```python
# Run 10 cycles with before/after comparison
benchmark = loop.run_benchmark(n_cycles=10)

print(f"Initial win rate: {benchmark['initial_metrics']['win_rate']}%")
print(f"Final win rate: {benchmark['final_metrics']['win_rate']}%")
print(f"Improvement: {benchmark['improvements']['win_rate_delta']}%")
print(f"Documents added: {benchmark['improvements']['documents_added']}")
```

### Learning Cycle Steps

| Step | Description |
|------|-------------|
| 1. Ingest | Ingest new reports into vector memory |
| 2. Process | Evaluate pending predictions |
| 3. Generate | Create training data from tool usage |
| 4. Analyze | Create improvement proposals |
| 5. Execute | Implement approved improvements |
| 6. Benchmark | Track metrics and create snapshots |

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
