# Changelog

## Unreleased

### 2025-12-24 — Background jobs & dashboard robustness
- **Added:** File-backed job registry and background job manager (`ingest_bot.jobs`) which persists jobs to `data/jobs.json` to survive restarts and provides `submit_job`, `get_job`, and `list_jobs` APIs.
- **Added:** Async parameter-surface endpoints and dashboard integration:
  - POST `/api/report/<name>/surface/compute` starts a background job and returns a job id.
  - GET `/api/report/<name>/surface/status/<job_id>` returns job status/result/error.
  - Dashboard UI polls job status and displays computed surface when finished.
- **Added:** Fallback behavior for surface computation: if `data/<name>/records.json` is missing the computation will use `data/reports/<name>/report.json`'s `last_rows` when available.
- **Added tests:** `test_jobs_persistence`, `test_surface_job_runs_and_finishes` to verify job persistence and that async surface jobs complete successfully in test environments.

### Changed
- **Changed (robustness):** Heavy ML model imports (`sklearn`) are now imported lazily inside functions to avoid import-time failures in minimal worker environments.
- **Changed (worker default):** Background surface compute now uses a lightweight NumPy-based least-squares linear predictor by default to reduce dependency footprint for workers that may not have full ML stacks installed.

### Fixed
- **Fixed:** Background surface jobs failing with import errors (e.g., "No module named 'sklearn'") by deferring heavy imports and using safe fallbacks; added tests to assert job completion.
- **Fixed:** Atomically persist job registry (`jobs.json`) to avoid corruption on concurrent writes.

---

### Added
- Robust manifest writer with configurable `dest_dir`, timestamp validation, and atomic writes.
- `ingest_bot.orchestrator` CLI supporting `--once --source --records-file/--adapter --since --dest-dir`.
- `ingest_bot/adapters` package with adapters:
  - `fred` (uses `fredapi` — requires `FRED_API_KEY`/`FRED_SERIES` when used)
  - `yfinance_adapter` (uses `yfinance` — requires `YFINANCE_TICKERS` when used)
- Integration tests for live adapters (skipped by default unless env vars set).
- Unit tests and integration tests under `ingest_bot/tests/`.
- `pyproject.toml` with console script `ingest-bot`.
- `README.md` documenting adapter configuration and integration test instructions.

### Changed
- Adapters now always require the real client libraries (`fredapi`, `yfinance`) and will raise `ImportError` if missing.
- Tests that interact with real libraries are skipped unless the corresponding libraries/env variables are present.

### Fixed
- Ensure manifest writes are atomic and include last ingest timestamp.
- Improve CLI error handling and exit codes for missing arguments.

---

Release notes:
- This change makes `ingest_bot` a self-contained, testable ingest + analysis utility with robust background job handling and dashboard integration. Integration tests are available but opt-in to avoid network/API key requirements in CI by default.
