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

- New: `deep-reflect@.service` and `deep-reflect.timer` added for nightly deep reflection and export. To enable:

```bash
# copy service and timer to user systemd
cp Artifact/arty/ingest_bot/deploy/deep-reflect@.service ~/.config/systemd/user/
cp Artifact/arty/ingest_bot/deploy/deep-reflect.timer ~/.config/systemd/user/
# enable and start
systemctl --user daemon-reload
systemctl --user enable --now deep-reflect.timer
```

The timer runs a user-level script that calls `Artifact/tools/run_deep_reflect_and_export.py` to run ingest, feed the ARTY store, trigger reflections (with optional parameter sweep) and export reflections to `Artifact/research_outputs/`.

- Embeddings & similarity: ContextEngine now prefers a Hektor (`pyvdb`) vector database for similarity search and stores vectors there when available. If Hektor is not installed or available, ContextEngine falls back to SQLite-based embeddings (`context_embeddings` table) and performs brute-force cosine similarity. If you have GEMINI/OpenAI keys available the provider will generate embeddings; otherwise embeddings fall back to a zero-vector (no effect). Database schema will be updated automatically on next run.

Hektor (optional, recommended for production):
- Clone and build Hektor Python bindings and install `pyvdb` in the runtime venv following `gladius/vendor/hektor/docs/22_PYTHON_BINDINGS.md` (see `create_database` / `create_gold_standard_db`).
- Configure `vector_db_path` in Automata config to point to the Hektor DB directory, e.g. `~/.automata/hektor_db`.
- When `pyvdb` is available, ContextEngine will automatically use it for indexing and sub-millisecond searches.

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
