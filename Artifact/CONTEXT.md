# Artifact
> Working context and operational notes

This document captures the current context for the Artifact workspace and the key systems we operate here. It is intended to be a concise, living reference for operators and developers.

## Overview
- Root: `/home/adam/worxpace/gladius/Artifact`
- Primary subsystems:
  - `arty/` — Arty automation and store (research, store DBs, social integrations, etc.)
  - `arty/ingest_bot/` — Ingest bot (yfinance, FRED adapters) that writes `records.json` and `manifest.json` and can POST price updates to infra API when `INFRA_API_URL` is set
  - `deployment/` — Deployment and operational scripts (systemd timers, run scripts, infra scaffolding)
  - `deployment/infra/` — Business infrastructure (markets, assets, portfolios) with SQLite-backed **Markets/Assets** and a FastAPI HTTP API at `http://127.0.0.1:7000` (see `infra/api/app.py`)
  - `deployment/automata/` — Orchestration & dashboard (Automata), offers JWT-protected endpoints and start/stop control for automation

## Environment variables and important paths
- ARTY_STORE_DIR — path to Arty store (e.g. `/home/adam/worxpace/gladius/Artifact/arty/store`)
- INFRA_API_URL — URL of infra API (e.g. `http://127.0.0.1:7000`) — when set, ingest writer posts latest price to `/prices`
- ENTERPRISE_CONFIG — Automata config file (used to set admin credentials during dev)
- OPENAI_API_KEY / AI_* — AI provider keys (required for some Automata subsystems)

## Recent changes (what's done)
- Implemented SQLite-backed repositories for Markets & Assets (`infra/repositories/sql_repository.py`).
- Added FastAPI infra API (`infra/api/app.py`) with endpoints for:
  - Markets: `POST /markets`, `GET /markets`
  - Assets: `POST /assets`, `GET /assets`
  - Portfolios: `POST /portfolios`, `POST /portfolios/{id}/positions`, `GET /portfolios`, `GET /portfolios/{id}`
  - Price ingestion: `POST /prices` (updates matching open positions)
- Seeded `COMEX` (Gold) and `BINANCE` (Bitcoin) markets and corresponding `GOLD` and `BTC-USD` assets via `infra/scripts/seed_gold_bitcoin.py`.
- Wired ingest writer (`ingest_bot.pipeline.writer.write_ingest_records`) to POST price updates to `INFRA_API_URL` when present.
- Validated end-to-end flow: ingest -> infra API -> portfolio position update -> portfolio P&L change.

## Quick operational commands
- Start infra API (dev):
  - `cd Artifact/deployment && uvicorn infra.api.app:app --host 127.0.0.1 --port 7000`
- Seed sample data and open positions:
  - `python infra/scripts/seed_gold_bitcoin.py`
- Simulate an ingest that posts to infra (writer):
  - `PYTHONPATH=Artifact/arty INFRA_API_URL=http://127.0.0.1:7000 python -c "from ingest_bot.pipeline.writer import write_ingest_records; write_ingest_records('prices',[{'timestamp':'2026-...','ticker':'BTC-USD','close':42500}], dest_dir='Artifact/arty/ingest_bot/data/ingest')"`
- Check portfolio performance:
  - `curl http://127.0.0.1:7000/portfolios/{id}`

## Current limitations / TODOs
- Portfolios and positions are currently stored in-memory (Repository-backed in `infra/repositories/portfolio_repository.py`). Plan: implement `PortfolioSqlRepository` to persist portfolios & positions to SQLite.
- Add authentication/authorization to infra API (currently open in dev).
- Add healthcheck and monitoring endpoints and a small set of integration tests for the end-to-end flow.

## Next steps (short list)
- Persist portfolios & positions to SQLite and migrate test data.
- Add API authentication (JWT or API-keys) and minimal audit logging for trading actions.
- Add CI job to run the seed + ingest flow and assert expected P&L calculations.
- Operationalize `Artifact/syndicate` as a first-class research pipeline: update deployment configs to consider `PREFER_OLLAMA=1` for Ollama-first operation and add systemd/unit templates from `Artifact/syndicate/deploy` to our deployment manifests.

## Contact & owner notes
- See `Artifact/deployment/README.md` and `arty/docs/DEPLOYMENT.md` for module owners and operational contacts.

*Last updated: 2026-01-11*