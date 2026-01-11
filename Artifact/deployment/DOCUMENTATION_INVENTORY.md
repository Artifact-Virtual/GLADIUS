# Documentation Inventory (initial scan)

This is the initial inventory of code, endpoints, DB tables, services, and docs to be expanded into full documentation pages.

## API Endpoints (found via `@app.route` scan)
- Ingest dashboard (arty):
  - `/api/reports`, `/api/ingests`, `/api/ingest/<name>/records`, `/api/ingest/<name>/run` etc. (Artifact/arty/ingest_bot/dashboard.py)
- Main dashboard API (Artifact/deployment/automata/dashboard/backend/app.py):
  - Auth: `POST /api/auth/login`, `GET /api/auth/verify`
  - Status & control: `GET /api/status`, `POST /api/status/start`, `POST /api/status/stop`
  - Config: `GET /api/config`, `PUT /api/config`, `GET /api/config/platforms`
  - Content: `POST /api/content/generate`, `POST /api/content/editorial`, `GET /api/content/drafts`, `POST /api/content/drafts`, `POST /api/content/drafts/<id>/finalize`, `POST /api/content/publish`
  - Context & reflection: `/api/context/*`, `/api/context/reflect`

## DB tables (discovered)
- Context DB (`~/.automata/context.db`) tables created by `ContextEngine`:
  - `context_entries`, `context_summaries`, `meta_summaries`, `context_analytics`, `reflections`, `context_embeddings`, `content_items`
- Other DBs / scripts that create tables (cthulu): `trades`, `signals`, `metrics`, `webhooks`, `market_data` (various scripts)

## Workers & Backgrounds
- `EditorialWorker` (`ai_engine/editorial_worker.py`) — polls `content_items` status='draft', finalizes.
- `PublishWorker` (`ai_engine/publish_worker.py`) — polls `content_items` status='final' and publishes.
- Orchestrator / scheduler: `scheduler/orchestrator.py` — schedules posts and runs periodic loops.

## Key Files & Locations
- AI Engine: `Artifact/deployment/automata/ai_engine/` (providers.py, generator.py, context_engine.py, content_store.py)
- Dashboard backend: `Artifact/deployment/automata/dashboard/backend/app.py`
- Dashboard frontend template: `Artifact/deployment/automata/dashboard/backend/templates/context_ui.html`
- CLI tools: `Artifact/tools/generate_articles.py`
- Hektor (vendor): `gladius/vendor/hektor` (notes in STATUS_HEKTOR.md)

## System / Deployment
- `.env` template: `Artifact/deployment/automata/.env.template` and current `.env` with provider choices
- Systemd unit files for scheduled jobs in `Artifact/deployment/` (and `arty/ingest_bot/deploy/`)
- Service run scripts: `dashboard/backend/run.py`

## Tests
- Unit tests for content flows: `Artifact/deployment/automata/tests/` (content store & worker tests)

---

This inventory is the starting point. Next: expand each item into a full doc page with examples, diagrams, ownership, and runbook steps.
