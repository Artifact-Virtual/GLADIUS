# Artifact Deployment Guide (Arty + Ingest Integration)

This document supplements `arty/docs/DEPLOYMENT.md` with Artifact-specific steps to set up Ingest + Arty Store and an hourly ingest schedule.

1) Initialize Arty Store

- Ensure Node.js (18+) is installed
- Run:

  cd /home/adam/worxpace/gladius/Artifact/arty/store
  npm install
  node init-databases.js

- Confirm DB files appear in `arty/store` (e.g., `research.db`, `vector.db`).

2) Configure `ingest_bot` to write into the Arty store

- Set an environment variable (recommended in systemd or service env file):

  ARTY_STORE_DIR=/home/adam/worxpace/gladius/Artifact/arty/store

- When `ARTY_STORE_DIR` is set, `ingest_bot` will write manifests/records to that path and automatically update `ingest_links.json` (a manifest of DB files under the store).

3) Enable hourly ingest via systemd timer

- Use the template in `ingest_bot/deploy/ingest-bot@.service` and `ingest_bot/deploy/ingest-bot.timer`.
- Example commands to enable hourly ingest for `prices` source:

  sudo cp gladius/Artifact/arty/ingest_bot/deploy/ingest-bot@.service /etc/systemd/system/ingest-bot@.service
  sudo cp gladius/Artifact/arty/ingest_bot/deploy/ingest-bot.timer /etc/systemd/system/ingest-bot.timer
  sudo systemctl daemon-reload
  sudo systemctl enable --now ingest-bot@prices.timer

- The timer triggers `ingest-bot@prices.service` hourly and runs `run_ingest.sh prices` which respects the `ARTY_STORE_DIR` env if set in the environment of the service.

4) Dashboard & discovery

- Dashboard endpoint `/api/arty/dbs` lists discovered database files and writes `ingest_links.json` on ingest activity. Point the dashboard at the running flask server to view ingest sources and storage stats.

5) Monitoring & backups

- Add a cron to back up `arty/store/*.db` nightly and add `ingest_links.json` to backup manifest.
- Add PM2 configs for Arty modules (see `arty/docs/DEPLOYMENT.md`).

6) Testing the integration

- Temporarily set `ARTY_STORE_DIR` in your shell and run a one-shot ingest:

  export ARTY_STORE_DIR=/home/adam/worxpace/gladius/Artifact/arty/store
  cd /home/adam/worxpace/gladius/Artifact/arty/ingest_bot
  ./.venv/bin/python -m ingest_bot.orchestrator --once --source btcusd --adapter yfinance_adapter --since 2026-01-01T00:00:00 --save-records

- Confirm `arty/store/btcusd/records.json`, `manifest.json`, and `ingest_links.json` were written.

Notes
- For production, prefer non-root service users and place the `ARTY_STORE_DIR` env into a systemd drop-in or `/etc/environment` managed securely.
- If you want ingests to also insert rows into the Arty SQLite DBs, we can add that next (requires schema decisions and robust deduplication logic).
