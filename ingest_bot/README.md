# ingest_bot

Minimal standalone ingest bot with adapters.

## Adapters

### FRED
- Requires `fredapi` installed and `FRED_API_KEY` environment variable set if required by your client.
- Configure default series with `FRED_SERIES` (comma-separated list of series ids) or pass series_ids directly to adapter calls.
- Example run:

```
export FRED_API_KEY=<your-key>
export FRED_SERIES=SERIES1,SERIES2
python -m ingest_bot.orchestrator --once --source fred --adapter fred --since 2020-01-01T00:00:00
```

### YFinance
- Requires `yfinance` installed.
- Configure default tickers with `YFINANCE_TICKERS` (comma-separated) or pass tickers to adapter functions if expanded.
- Example run (no API key needed):

```
export YFINANCE_TICKERS=AAPL,MSFT
python -m ingest_bot.orchestrator --once --source prices --adapter yfinance_adapter --since 2025-01-01T00:00:00
```

## Integration tests

Integration tests exercise live libraries and network calls and are skipped by default. To run them, set environment variables:

- For yfinance:

```
export RUN_INTEGRATION=1
export YFINANCE_TICKERS=BTC-USD
PYTHONPATH=$(pwd) pytest ingest_bot/tests/integration/test_yfinance_integration.py -q
```

- For FRED (requires API key and series):

```
export RUN_FRED_INTEGRATION=1
export FRED_API_KEY=<your-key>
export FRED_SERIES=SERIES1
PYTHONPATH=$(pwd) pytest ingest_bot/tests/integration/test_fred_integration.py -q
```

Note: the test suite will skip integration tests unless the corresponding `RUN_*_INTEGRATION` variable is set to `1`.

## Dashboard & Scheduled backtests

Dashboard:
- Run the interactive dashboard locally:

```
PYTHONPATH=$(pwd) ./.venv/bin/python -m ingest_bot.dashboard --host 0.0.0.0 --port 8050
```

- The dashboard serves saved reports under `data/reports/<source>/` and will show charts and summary.

Scheduled backtests:
- Use `deploy/run_backtest.sh` to run ingest + analysis + persist a report to `data/reports/<source>/`.
- Systemd unit templates are provided in `deploy/`:
  - `deploy/backtest@.service` and `deploy/backtest.timer` (timer triggers `backtest@btc.service` daily)
  - `deploy/dashboard.service` to run the Flask dashboard as a service

- To enable scheduling and dashboard as systemd services, copy the unit files to `/etc/systemd/system/` and `systemctl enable --now backtest@btc.timer` (or `dashboard.service`).

Be careful: enabling systemd services requires appropriate privileges; I did not enable them for you.

## Background jobs

- The dashboard supports starting asynchronous, file-backed background computations (e.g., parameter-surface computations) via the API: POST `/api/report/<name>/surface/compute`. Jobs are managed by `ingest_bot.jobs` and job state is persisted to `data/jobs.json` so jobs survive process restarts and can be polled via GET `/api/report/<name>/surface/status/<job_id>`.

- Deployment recommendation: for robust long-running or compute-heavy jobs, run background workers as dedicated processes or containers with the full ML dependency stack installed (e.g., `scikit-learn`, `statsmodels`, `numpy`). Recommended options:
  - Use a task queue such as **RQ (Redis Queue)** or **Celery** to run workers separately from the web process, enabling retries, monitoring, and scaling.
  - Containerize workers (Docker) with pinned dependency images so workers run in reproducible environments and can be deployed independently from the dashboard service.

- Short-term fallback: the dashboard will use a lightweight NumPy-based predictor for jobs when heavy ML packages are unavailable, but this provides a reduced feature set (no RF/ARIMA). For full-featured analyses, ensure workers include the required libraries.

- Operational notes: persist `data/jobs.json` on durable storage, ensure service accounts have write permissions, and consider supervisory tooling (systemd, supervisor, or container orchestration) to restart failed workers.
