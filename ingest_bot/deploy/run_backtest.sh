#!/usr/bin/env bash
# Run ingest (fetch) + analysis + save report
set -euo pipefail
SOURCE=${1:-btc}
ADAPTER=${2:-yfinance_adapter}
DEST_DIR=${3:-/home/adam/worxpace/ingest_bot/data}
REPORT_DIR=${4:-/home/adam/worxpace/ingest_bot/data/reports}
DAYS=${5:-30}

SINCE=$(python - <<PY
from datetime import datetime, timedelta
print((datetime.utcnow() - timedelta(days=int(${DAYS}))).strftime('%Y-%m-%dT%H:%M:%S'))
PY
)

# Run orchestrator to fetch and save records
if [ -x "$(pwd)/.venv/bin/python" ]; then
  PYTHON="$(pwd)/.venv/bin/python"
else
  PYTHON="python"
fi

# Ensure the repo root is visible to python -m by setting PYTHONPATH
echo "Fetching ${SOURCE} via ${ADAPTER} since ${SINCE}..."
# Use a short Python runner that inserts the repo root to sys.path so module
# import by package name works even inside venvs. Resolve repo root relative to the script
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
"$PYTHON" - <<PY
import sys, os
repo_root = r"$REPO_ROOT"
print('PY repo_root=', repo_root, 'cwd=', os.getcwd())
sys.path.insert(0, repo_root)
from ingest_bot.orchestrator import main
rc = main(['--once','--source','$SOURCE','--adapter','$ADAPTER','--since','$SINCE','--dest-dir','$DEST_DIR','--save-records'])
raise SystemExit(rc)
PY

RECS="$DEST_DIR/$SOURCE/records.json"
REPORT_PATH="$REPORT_DIR/$SOURCE"
mkdir -p "$REPORT_PATH"

echo "Analyzing records and saving report to $REPORT_PATH"
"$PYTHON" - <<PY
import sys, os
sys.path.insert(0, r"$REPO_ROOT")
from pathlib import Path
from ingest_bot.analysis import analyze_records
from ingest_bot.reports import save_report
path = Path(r"$RECS")
rep = analyze_records(path, save_plots_to=Path(r"$REPORT_PATH"))
save_report(rep, Path(r"$REPORT_PATH"))
print('Report saved to', Path(r"$REPORT_PATH").resolve())
PY

echo "Backtest + report complete: $REPORT_PATH"
