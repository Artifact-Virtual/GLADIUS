# Gladius Command Reference

> Complete operational command reference for developers and operators
> 
> **Last Updated**: 2026-01-11

---

## Quick Start (Single Command)

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

# Test Infra API specifically
./gladius.sh infra
```

---

## 📋 Gladius Control Script

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

## 📊 Service Ports

| System | Port | Purpose |
|--------|------|---------|
| Infra API | 7000 | Market data, assets, portfolios |
| Dashboard Backend | 5000 | Automata control, content management |
| Dashboard Frontend | 3000 | React UI (optional) |
| Grafana | 3000 | Metrics dashboards (via Docker) |

---

## 🏗️ Infrastructure API (Port 7000)

**Location**: `Artifact/deployment/infra/`

### Start Server

```bash
cd Artifact/deployment
uvicorn infra.api.app:app --host 127.0.0.1 --port 7000

# Production with reload disabled
uvicorn infra.api.app:app --host 0.0.0.0 --port 7000 --workers 4
```

### API Endpoints

```bash
# Markets
curl http://127.0.0.1:7000/markets                    # GET all markets
curl -X POST http://127.0.0.1:7000/markets \
  -H "Content-Type: application/json" \
  -d '{"symbol": "XAUUSD", "name": "Gold", "exchange": "COMEX"}'

# Assets
curl http://127.0.0.1:7000/assets                     # GET all assets
curl -X POST http://127.0.0.1:7000/assets \
  -H "Content-Type: application/json" \
  -d '{"ticker": "BTC-USD", "name": "Bitcoin", "asset_type": "crypto"}'

# Portfolios
curl http://127.0.0.1:7000/portfolios                 # GET all portfolios
curl http://127.0.0.1:7000/portfolios/{id}            # GET portfolio by ID

# Price Ingestion
curl -X POST http://127.0.0.1:7000/prices \
  -H "Content-Type: application/json" \
  -d '{"ticker": "BTC-USD", "close": 42500, "timestamp": "2026-01-11T12:00:00Z"}'
```

### Seed Sample Data

```bash
cd Artifact/deployment/infra
python scripts/seed_gold_bitcoin.py
```

---

## 🤖 Automata Dashboard (Port 5000)

**Location**: `Artifact/deployment/automata/dashboard/`

### Start Backend

```bash
cd Artifact/deployment/automata/dashboard/backend
python app.py

# Or with gunicorn (production)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Start Frontend (React)

```bash
cd Artifact/deployment/automata/dashboard/frontend
npm install
npm run dev      # Development (port 3000)
npm run build    # Production build
```

### API Authentication

```bash
# Login and get JWT token
TOKEN=$(curl -s -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "gladius"}' | jq -r '.access_token')

echo $TOKEN

# Use token in subsequent requests
curl http://127.0.0.1:5000/api/status \
  -H "Authorization: Bearer $TOKEN"
```

### Dashboard API Endpoints

```bash
# System Status
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/status
curl -X POST -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/status/start
curl -X POST -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/status/stop

# Overview (aggregated dashboard data)
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/overview

# Configuration
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/config
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/config/platforms

# Analytics
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/analytics

# Content Management
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/content/drafts
curl -X POST -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/content/generate \
  -H "Content-Type: application/json" \
  -d '{"platform": "LinkedIn", "topic": "AI Trading", "content_type": "article"}'

# Context Engine
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/context/entries
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/context/stats
curl -X POST -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/context/reflect

# Reflections
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/reflections/recent
```

---

## 📊 Syndicate Intelligence Pipeline

**Location**: `Artifact/syndicate/`

### Start Daemon (Continuous Operation)

```bash
cd Artifact/syndicate
python run.py --daemon

# With Ollama preference (local-first)
PREFER_OLLAMA=1 python run.py --daemon

# Single run (one analysis cycle)
python run.py --once
```

### LLM Worker (Separate Process)

```bash
cd Artifact/syndicate
python scripts/llm_worker.py
```

### Database Management

```bash
cd Artifact/syndicate

# Initialize/reset database
python db_manager.py

# Check database on VM
python check_db_vm.py

# Reset database
python reset_db_vm.py
```

### Chart Generation

```bash
cd Artifact/syndicate

# Test chart annotations
python -m pytest tests/test_chart_utils.py -v

# Generate sample charts
python scripts/generate_sample_charts.py
```

### Provider Configuration

```bash
# Ollama-first (recommended for cost)
export PREFER_OLLAMA=1

# Gemini API key (fallback)
export GOOGLE_API_KEY=your-key

# Force specific provider
export SYNDICATE_PROVIDER=ollama  # or gemini, local
```

---

## 🎭 Arty Automation Framework

**Location**: `Artifact/arty/`

### Install All Modules

```bash
cd Artifact/arty
npm install
```

### Initialize Storage

```bash
cd Artifact/arty/store
node init-databases.js
```

### Research Engine

```bash
cd Artifact/arty
npm run research:cycle    # Single research cycle
npm run research:start    # Continuous mode
```

### Discord Bot

```bash
cd Artifact/arty
npm run discord:install   # Install dependencies
npm run discord:deploy    # Deploy slash commands
npm run discord:start     # Start bot
npm run discord:dev       # Development mode
npm run discord:test      # Run tests
```

### LinkedIn Automation

```bash
cd Artifact/arty
npm run linkedin:install
npm run linkedin:start    # Start scheduler
npm run linkedin:post     # Post now
npm run linkedin:schedule # Schedule posts
npm run linkedin:test     # Run tests
```

### Ingest Bot

```bash
cd Artifact/arty/ingest_bot

# Activate venv
source .venv/bin/activate

# Run ingest with API integration
INFRA_API_URL=http://127.0.0.1:7000 python orchestrator.py

# Manual price ingest
python -c "from pipeline.writer import write_ingest_records; \
  write_ingest_records('prices', [{'timestamp':'2026-01-11T12:00:00Z','ticker':'BTC-USD','close':42500}])"

# Run backtest
python backtest.py

# Generate reports
python reports.py
```

### Run All Tests

```bash
cd Artifact/arty
npm test                  # Discord + LinkedIn tests
npm run test:summary      # View test results
```

---

## 📈 Grafana Dashboards

**Location**: `Artifact/syndicate/deploy/grafana/`

### Start Grafana (Docker)

```bash
cd Artifact/syndicate/docker
docker-compose up -d grafana prometheus

# Access at http://localhost:3000
# Default: admin/gladius
```

### Available Dashboards

- `syndicate_overview_dashboard.json` - System overview
- `syndicate_llm_dashboard.json` - LLM performance metrics

### Manual Import

```bash
# Copy dashboard to Grafana provisioning
cp Artifact/syndicate/deploy/grafana/*.json /etc/grafana/provisioning/dashboards/
```

---

## 🖥️ VM/Infrastructure Management

### Cthulu GCP VM

```bash
# SSH to VM
gcloud compute ssh cthulu-node --zone=us-central1-a

# Check Windows container status
docker ps

# Access Windows Desktop (via browser)
# http://34.171.231.16:8006

# VS Code Server
# https://34.171.231.16:8443
```

### PowerShell Scripts (Windows)

```powershell
# Configure Git/GH globally
.\dev_docs\scripts\configure_gh_global.ps1

# Launch Herald with MT5
.\dev_docs\scripts\desktop_launch_herald_and_mt5.ps1

# Run integration test (dry run)
.\dev_docs\scripts\integration_run_dry.ps1

# Start Herald wizard
.\dev_docs\scripts\run_herald_wizard_foreground.ps1
```

### Shell Scripts (Linux)

```bash
# GCP startup scripts
./dev_docs/scripts/gcp_startup_odyssey.sh
./dev_docs/scripts/gcp_startup_soundwave.sh

# MT5 automation
./dev_docs/scripts/mt5_automate.sh

# SSH key append
./dev_docs/scripts/append_key.sh
```

---

## 🔧 Development Commands

### Git Operations

```bash
cd /home/adam/worxpace/gladius

# Status and diff
git --no-pager status
git --no-pager diff

# Recent commits
git --no-pager log --oneline -20

# Branch management
git branch -a
git checkout main
git pull origin main
```

### Testing

```bash
# Syndicate tests
cd Artifact/syndicate
pytest tests/ -v

# Arty tests
cd Artifact/arty
npm test

# Infra tests
cd Artifact/deployment/infra
pytest tests/ -v

# Automata tests
cd Artifact/deployment/automata
pytest tests/ -v
```

### Linting

```bash
# Python (ruff)
cd Artifact/syndicate
ruff check .
ruff format .

# JavaScript (eslint)
cd Artifact/arty
npm run lint
```

---

## 🔐 Environment Variables

### Core Variables

```bash
# Infra API
export INFRA_API_URL=http://127.0.0.1:7000

# Syndicate
export PREFER_OLLAMA=1
export GOOGLE_API_KEY=your-gemini-key
export NOTION_TOKEN=your-notion-token
export NOTION_DATABASE_ID=your-db-id

# Automata Dashboard
export DASHBOARD_SECRET_KEY=your-secret
export JWT_SECRET_KEY=your-jwt-secret
export DASHBOARD_ALLOW_DEV_LOGIN=false

# Discord Bot
export DISCORD_TOKEN=your-bot-token
export DISCORD_CLIENT_ID=your-client-id
export DISCORD_GUILD_ID=your-guild-id

# LinkedIn
export LINKEDIN_ACCESS_TOKEN=your-token
```

### Load from .env

```bash
# Root .env file exists at /home/adam/worxpace/gladius/.env
source .env

# Or use python-dotenv (automatic in Python apps)
```

---

## 🛑 Emergency Operations

### Stop All Services

```bash
# Find and kill by port
kill $(lsof -t -i:7000)   # Infra API
kill $(lsof -t -i:5000)   # Dashboard
kill $(lsof -t -i:3000)   # Grafana/React

# Kill Python processes
pkill -f "uvicorn"
pkill -f "run.py"
pkill -f "app.py"
```

### Check Running Services

```bash
# List ports in use
ss -tuln | grep -E '(7000|5000|3000)'

# Check process status
ps aux | grep -E "(uvicorn|python|node)"

# Health checks
curl -s http://127.0.0.1:7000/docs > /dev/null && echo "Infra API: OK" || echo "Infra API: DOWN"
curl -s http://127.0.0.1:5000/health > /dev/null && echo "Dashboard: OK" || echo "Dashboard: DOWN"
```

### Restart Sequence

```bash
# Kill all
pkill -f "uvicorn" 2>/dev/null
pkill -f "run.py" 2>/dev/null
pkill -f "dashboard" 2>/dev/null
sleep 2

# Restart
cd /home/adam/worxpace/gladius/Artifact/deployment
uvicorn infra.api.app:app --host 127.0.0.1 --port 7000 &
cd automata/dashboard/backend && python app.py &
cd ../../Artifact/syndicate && python run.py --daemon &
```

---

## 📊 Monitoring & Logs

### Log Locations

```bash
# Syndicate logs
tail -f Artifact/syndicate/run_once.log
tail -f Artifact/syndicate/notion_publish.log
tail -f Artifact/syndicate/output_log.txt

# Dashboard logs
tail -f Artifact/deployment/dashboard_backend.log
tail -f Artifact/deployment/infra_api.log

# Arty logs
tail -f Artifact/arty/discord/logs/*.log
tail -f Artifact/arty/ingest_bot/dashboard.log
```

### Prometheus Metrics

```bash
# Syndicate exposes Prometheus metrics
curl http://127.0.0.1:8000/metrics
```

### Database Inspection

```bash
# SQLite databases
sqlite3 Artifact/syndicate/data/syndicate.db ".tables"
sqlite3 Artifact/syndicate/data/syndicate.db "SELECT * FROM llm_tasks ORDER BY created_at DESC LIMIT 10;"

# Arty store
sqlite3 Artifact/arty/store/arty.db ".tables"
```

---

## 📁 Key File Locations

| Purpose | Path |
|---------|------|
| Root Config | `/home/adam/worxpace/gladius/.env` |
| Infra API | `Artifact/deployment/infra/api/app.py` |
| Dashboard Backend | `Artifact/deployment/automata/dashboard/backend/app.py` |
| Syndicate Daemon | `Artifact/syndicate/run.py` |
| Arty Discord | `Artifact/arty/discord/` |
| Grafana Dashboards | `Artifact/syndicate/deploy/grafana/` |
| Research Articles | `obsidian_sync/dev_docs/articles/` |

---

## 🔗 Access URLs

| Service | URL |
|---------|-----|
| Infra API Docs | http://127.0.0.1:7000/docs |
| Dashboard | http://127.0.0.1:5000 |
| Dashboard Frontend | http://127.0.0.1:3000 |
| Grafana | http://127.0.0.1:3000 |
| Cthulu Windows | http://34.171.231.16:8006 |
| Cthulu VS Code | https://34.171.231.16:8443 |

---

## 📚 Related Documentation

- [README.md](README.md) - Project overview
- [QUICKSTART.md](obsidian_sync/QUICKSTART.md) - Getting started guide
- [Artifact/MANDATE.md](Artifact/MANDATE.md) - Operational mandate
- [Artifact/CONTEXT.md](Artifact/CONTEXT.md) - Current context
- [obsidian_sync/NAVIGATION.md](obsidian_sync/NAVIGATION.md) - Repository navigation

---

*Generated: 2026-01-11 | Gladius Command Reference v1.0*
