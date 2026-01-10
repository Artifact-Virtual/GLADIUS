#!/usr/bin/env bash
# Wrapper script to run an ingest once. Usage: run_ingest.sh <source> <adapter> [dest-dir] [days]
set -euo pipefail
SOURCE=${1:-prices}
ADAPTER=${2:-yfinance_adapter}
DEST_DIR=${3:-/home/adam/worxpace/ingest_bot/data/ingest}
DAYS=${4:-1}
# compute since as UTC 'DAYS' ago
SINCE=$(python - <<PY
from datetime import datetime, timedelta
print((datetime.utcnow() - timedelta(days=int(${DAYS}))).strftime('%Y-%m-%dT%H:%M:%S'))
PY
)

# Use the repo venv python if present
if [ -x "$(pwd)/.venv/bin/python" ]; then
  PYTHON="$(pwd)/.venv/bin/python"
else
  PYTHON="python"
fi

exec "$PYTHON" -m ingest_bot.orchestrator --once --source "$SOURCE" --adapter "$ADAPTER" --since "$SINCE" --dest-dir "$DEST_DIR" --save-records
