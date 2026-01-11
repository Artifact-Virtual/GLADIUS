< ML - PLEASE KEEP OVERRUNNING & OVERWRITE THIS DOCUMENT TO KEEP UPDATING HOW TO RUN AND OPERATE ARTIFACT - ML >

# ARTIFACT OPERATIONAL MANDATE

This document defines the operational mandate for the Artifact Virtual system in the Gladius project — the mission, responsibilities, current operational scope, and measurable expectations for the team that runs Artifact.

## Mission
- Provide reliable, auditable, and extensible infrastructure to ingest market and macro data, persist canonical market/asset metadata, manage portfolios and positions, and expose these capabilities to orchestration layers (Automata) and operator UI.

## Key Responsibilities
- Availability: Ensure core services (ingest, infra API, automata dashboard) are reachable and recoverable.
- Data integrity: Maintain canonical asset/market records and ensure ingest data is written atomically with manifests.
- Security & secrets: Do not commit secrets to git. Use environment variables and secure vaults for API keys.
- Observability: Provide simple health checks, logs, and runbooks for operators to debug failures quickly.

## Recent Progress (short)
- Added SQLite-backed **Markets** and **Assets** repositories for durable canonical storage.
- Added a **FastAPI** infra API (127.0.0.1:7000) exposing markets, assets, portfolios, and price ingestion endpoints.
- Seeded **Gold (GOLD)** and **Bitcoin (BTC-USD)** markets/assets and validated end-to-end ingest → portfolio update flow.
- Wired existing ingest writer to POST latest prices to the infra API when `INFRA_API_URL` is set.
- Brought up Automata dashboard and validated start/stop/status endpoints for orchestration.

## Runbook (Quick checks)
- Start infra API (development):
  - `uvicorn infra.api.app:app --host 127.0.0.1 --port 7000`
- Seed sample data and portfolio (dev):
  - `python infra/scripts/seed_gold_bitcoin.py`
- Force a price ingest (writer will post to infra API if `INFRA_API_URL` is set):
  - `INFRA_API_URL=http://127.0.0.1:7000 python -c "from ingest_bot.pipeline.writer import write_ingest_records; write_ingest_records('prices',[{'timestamp':'2026-...','ticker':'BTC-USD','close':42500}], dest_dir='Artifact/arty/ingest_bot/data/ingest')"`

## SLAs & Metrics (operational baseline)
- Service uptime target: 99% (dev → relaxed), increase for production deployments.
- Ingest latency: < 5s from writer POST to infra update for low-throughput flows.
- Data correctness: Every ingest writes `manifest.json` and `records.json` atomically; ingest links manifest must be refreshed after writes.

## Ownership & Contacts
- Maintainers: see `arty/docs/DEPLOYMENT.md` and `Artifact/deployment/README.md` for module owners and contact points.

## Immediate Next Actions
- Persist portfolios & positions to SQLite (next PR planned).
- Add API authentication and health endpoints.
- Add CI integration tests for the end-to-end ingest → infra → portfolio flow.

---
*Last updated: 2026-01-11*