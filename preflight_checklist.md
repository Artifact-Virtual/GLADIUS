# GLADIUS Enterprise — Preflight Checklist

_Last updated: 2026-01-20T18:11:39.968Z_

Use this checklist before every deployment or autonomous cycle to guarantee that the entire GLADIUS stack (Sentinel, Gladius core, Legion, Artifact, Arty, and shared services) is ready. Complete the sections in order; a downstream block assumes everything above it is ✅.

> **Legend**  
> - [ ] Pending validation  
> - [x] Completed validation  
> - _(cmd)_ Recommended verification command

---

# Quick Launch Dashboard

python3 -m venv .venv && . .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
python train_pipeline.py --resume --max-hours 24 --save-interval 1000 --eval-interval 500

## 0. Global Environment & Credentials

- [ ] Host clock synced (≤60 s skew) _(cmd: `timedatectl status`)_
- [ ] Free disk ≥ 10 GB under `/home/adam/worxpace/gladius` _(cmd: `df -h .`)_
- [ ] `.env` present, derived from `.env.example`, and validated _(cmd: `./scripts/validate_env.sh`)_
- [ ] All secret keys regenerated (SECRET_KEY, DASHBOARD_SECRET_KEY, JWT_SECRET_KEY, LEGION_SECRET_KEY)
- [ ] SMTP credentials populated and tested _(cmd: `python3 scripts/test_smtp_consensus.py --send-test-email`)_
- [ ] Discord webhook + channel IDs configured
- [ ] Social API tokens (Twitter, LinkedIn, FB, IG) set and unexpired
- [ ] Ollama / GGUF runtime (optional fallback) reachable if `GLADIUS_FALLBACK=ollama`
- [ ] Virtualenv `.venv` exists and activated for shared scripts _(cmd: `source .venv/bin/activate`)_
- [ ] Repo status clean or intentionally dirty (note outstanding diffs) _(cmd: `git status -sb`)_

## 1. Dependencies & Assets

### 1.1 Python / Node Packages
- [ ] Root: `pip install -r requirements.txt`
- [ ] SENTINEL: `pip install -r SENTINEL/requirements.txt`
- [ ] LEGION backend: `pip install -r LEGION/requirements.txt`
- [ ] Artifact services: `pip install -r Artifact/deployment/requirements.txt` (if present)
- [ ] GLADIUS training: `pip install -r GLADIUS/training/requirements.txt`
- [ ] Arty workspace: `cd Artifact/arty && npm install`
- [ ] LEGION dashboards / React apps: `cd LEGION && npm install`

### 1.2 Data, Models & Storage
- [ ] GLADIUS models (GGUF / safetensors) stored under `GLADIUS/models/**`
- [ ] Qwen operational checkpoints located at `Artifact/models/qwen/`
- [ ] Arty databases initialized (`Artifact/arty/store` `node init-databases.js`)
- [ ] SQLite files (`data/*.db`, `LEGION/data`, `SENTINEL/services/*.db`) present and backed up
- [ ] Logs directory writable (`logs/`)

---

## 2. SENTINEL Guardian (ASAS)

### 2.1 Configuration
- [ ] `SENTINEL_ENABLED=true` and `SENTINEL_KILL_PASSWORD` set in `.env`
- [ ] Target definitions current (`SENTINEL/config/targets.json` or CLI additions)
- [ ] Constitutional rules up to date (`SENTINEL/config/constitution/*.yml`)

### 2.2 Process Health
- [ ] Watchdog running with valid PID _(cmd: `./scripts/start_sentinel.sh status`)_
- [ ] Learning daemon active (≥1 cycle in last hour) _(cmd: `pgrep -f learning_daemon.py`)_
- [ ] Process guardian registered critical services (Infra API, dashboard, Syndicate, LEGION)
- [ ] Threat engine able to reach feeds (arXiv, GitHub, CVE) _(cmd: `python3 SENTINEL/threat_engine.py --self-test`)_
- [ ] Kill switch verified (dry-run) _(cmd: `./scripts/start_sentinel.sh stop <password> --dry-run`)_

### 2.3 CLI Diagnostics
- [ ] `python3 SENTINEL/asas_cli.py status`
- [ ] `python3 SENTINEL/asas_cli.py scan --type full`
- [ ] `python3 SENTINEL/asas_cli.py target-list`

---

## 3. GLADIUS Core (Native AI Brain)

### 3.1 Configuration
- [ ] `GLADIUS_ENABLED=true`
- [ ] Router patterns synced (`GLADIUS/router/pattern_router.py` tests pass)
- [ ] Growth tracker accessible (`GLADIUS/growth/growth_tracker.py status`)

### 3.2 Model Assets
- [ ] Latest safetensors present and checksums validated
- [ ] Training datasets accessible under `GLADIUS/training/**`
- [ ] Ollama / GGUF export path configured if deploying to edge devices

### 3.3 Interfaces
- [ ] Interactive CLI works _(cmd: `python3 GLADIUS/interactive.py --status`)_
- [ ] Speak interface outputs audio/text _(cmd: `python3 GLADIUS/speak.py --ping`)_
- [ ] Continuous mode dry-run _(cmd: `python3 GLADIUS/continuous.py --dry-run`)_
- [ ] Training harness smoke test _(cmd: `python3 GLADIUS/training/gladius_1b_trainer.py --dry-run`)_

---

## 4. LEGION Enterprise (Agent Ecosystem)

### 4.1 Services & APIs
- [ ] `LEGION/start_enterprise.py` completes dependency check
- [ ] Backend API reachable _(cmd: `python3 LEGION/backend_api.py --health`)_
- [ ] Websocket / server running _(cmd: `python3 LEGION/server.py --health`)_
- [ ] CLI available _(cmd: `cd LEGION/legion && python3 cli.py system status`)_

### 4.2 Data & Integrations
- [ ] SQLite databases (`LEGION/data/*.db`) migrated to latest schema _(cmd: `python3 LEGION/initialize_database_schema.py`)_
- [ ] Integration credentials stored in `LEGION/config/*`
- [ ] Rate limiter configured (`LEGION/rate_limiter.py`)

### 4.3 Frontend Dashboards
- [ ] `npm run start` (AMOLED dashboard) builds without error
- [ ] Static assets under `LEGION/public/` compiled

---

## 5. Artifact Layer (Syndicate, Automata, Qwen Operational)

### 5.1 Infra API & Automata
- [ ] `uvicorn infra.api.app:app --port 7000` starts (no port conflicts)
- [ ] Dashboard backend on 5000 passes `/health`
- [ ] Web UI (template server) responds at `:5002/api/status`
- [ ] Syndicate daemon configured (`Artifact/syndicate/run.py --interval-min 15`)
- [ ] Automata social connectors have tokens + scheduled content

### 5.2 Qwen Operational AI
- [ ] Checkpoint state file (`Artifact/models/qwen/checkpoints/qwen_state.json`) readable
- [ ] `python3 Artifact/qwen_operational.py --status` reports `ready`
- [ ] Training data under `Artifact/data/training/` up to date
- [ ] GPU/CPU resources available for LoRA fine-tune if needed

### 5.3 ERP / Publishing Bridges
- [ ] ERP credentials valid (`Artifact/deployment/automata/erp_integrations/.env`)
- [ ] Publishing endpoints (Discord, Email, Social) reachable

---

## 6. ARTY Autonomous Research Team

### 6.1 Research Engine
- [ ] `.env` and `config.json` configured under `Artifact/arty/research`
- [ ] Research cycle runs _(cmd: `npm run research:cycle`)_
- [ ] Storage layer reachable (SQLite + pgvector) _(cmd: `npm run store:status` if available)_

### 6.2 Discord Bot
- [ ] Tokens/config set in `Artifact/arty/discord/.env`
- [ ] Commands deployed _(cmd: `npm run discord:deploy`)_
- [ ] Bot login verified _(cmd: `npm run discord:start`)_

### 6.3 LinkedIn Automation
- [ ] API keys + organization/page IDs configured
- [ ] Scheduler running _(cmd: `npm run linkedin:start`)_
- [ ] Queue contains fresh research-derived content

---

## 7. Observability, QA & Safety

- [ ] Grafana (3001) reachable with dashboards refreshed
- [ ] Prometheus (9090) scraping Infra API, Sentinel, LEGION exporters
- [ ] Logs rotating under `logs/` (check file sizes)
- [ ] SMTP + Discord tests pass
- [ ] Sentinel + Legion integration tests _(cmd: `python3 SENTINEL/tests/test_sentinel.py`; `python3 LEGION/tests/test_legion_integration.py`)_
- [ ] Syndicate research results spot-checked
- [ ] Backup job executed (copy `data/`, `logs/`, `Artifact/arty/store/`, model weights)
- [ ] Kill-switch and rollback procedures documented for on-call

---

## 8. Launch Sequence (Run in Order)

1. [ ] Start Sentinel guardian  
   _(cmd: `./scripts/start_sentinel.sh detached`)_
2. [ ] `./gladius.sh start` — boot Infra API, dashboards, Syndicate, LEGION
3. [ ] `./gladius.sh health` — verify all green
4. [ ] Optional: `./gladius.sh cycle` (single pipeline proof)
5. [ ] Optional: `./gladius.sh autonomous` for continuous operations
6. [ ] Monitor Grafana + Sentinel for first 10 minutes, confirm no alerts

---

## Reference Commands

- Validate `.env`: `./scripts/validate_env.sh`
- Sentinel CLI: `python3 SENTINEL/asas_cli.py --help`
- GLADIUS interaction: `python3 GLADIUS/interactive.py --query "..."`
- LEGION status: `cd LEGION/legion && python3 cli.py system status`
- Artifact AI status: `python3 Artifact/qwen_operational.py --status`
- Arty workspace: `cd Artifact/arty && npm run <target>`

Complete every checkbox before initiating production or autonomous cycles to ensure a safe launch.
