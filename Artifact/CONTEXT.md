# Artifact
> High-level Architecture

This file captures the working context for the Artifact workspace and the key systems we operate here.

Overview
- Root: `/home/adam/worxpace/gladius/Artifact`
- Primary subsystems:
  - `arty/` — Arty automation framework (Research, Store, Discord, LinkedIn, etc.)
  - `ingest_bot/` (moved under `arty/ingest_bot`) — Minimal standalone ingest bot used to fetch market & macro data
  - `deployment/` — Organization-wide deployment and operational docs


Policy and environment
- The workspace relies on `.env` files present under each module (`arty/research/.env`, `arty/discord/.env`, etc.). Do not commit secrets to git.
- Use environment var `ARTY_STORE_DIR` to force ingestion/storage to the desired Arty store path (absolute path recommended). Example:

  export ARTY_STORE_DIR=/home/adam/worxpace/gladius/Artifact/arty/store

Immediate next steps (to be executed):
- Run `node store/init-databases.js` to initialize the Arty store DB files.
- Set `ARTY_STORE_DIR` and re-run an ingest to verify `records.json` and `manifest.json` are written in `arty/store/<source>/`.
- Enable hourly ingest timer (systemd) or PM2 cron that triggers `ingest_bot/deploy/run_ingest.sh` for your desired sources.

Contact
- Maintainers: see `arty/docs/DEPLOYMENT.md` and `arty/README.md` for module owners and contact points.
