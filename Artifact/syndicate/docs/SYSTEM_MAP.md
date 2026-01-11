# Syndicate System Map (updated 2026-01-11)

This document summarizes the runtime components, data flows, and recent robustness improvements. PDF artifacts are intentionally omitted — use the repo for diagrams and source files.

## Components

- LLM Workers (`scripts/llm_worker.py`)
  - Consume `llm_tasks` table
  - Support provider preference/fallback (Gemini, Ollama, Local)
  - Sanitizes generated content and writes final documents to `output/`
  - Notion push and Automata client notifications are best-effort and are logged when unavailable

- Executor Daemon (`scripts/executor_daemon.py`)
  - Executes action insights derived from content
  - Recovers orphan tasks on startup
  - Heartbeat and leader election to support HA

- Organizer (`scripts/organizer.py`) — new
  - Idempotently mirrors `s y n d i c a t e/output` into `syndicate-legacy/output` layout
  - Produces `file_index.json` manifest

- Publisher / Run Loop (`run.py`)
  - Runs extraction → LLM generation → organization → publishing (Notion)
  - Publishing may be disabled or purposely misconfigured for testing (publish errors are recorded)

- Monitoring / Ops
  - `scripts/smoke_runner.py` — deterministic reruns for smoke-testing (LLM processing + organization)
  - Tests added: `tests/test_llm_worker_io.py`, `tests/test_organizer.py`, Automata publish-worker test

## Recent fixes (2026-01-11)
- LLM worker now creates parent directories before writing files to avoid FileNotFoundError.
- LLM worker handles Automata client push failures gracefully without crashing the task (exceptions are logged).
- NameError and try/except mismatches in `llm_worker` were fixed.
- Added unit tests for directory creation, Automata failure handling, publisher failure recording, and an organizer with idempotency tests.
- Created an `organizer` script that mirrors outputs into the legacy layout, preserving formatting and file structure.
- Added `smoke_runner` to re-run multiple iterations to surface issues.

## Operational guidance
- Keep publish connectors disabled or misconfigured in test environments to ensure publish failures are observed and logged (we deliberately preserve failing publish paths in CI/test).
- For full end-to-end real publishing, enable platform connectors (e.g., LinkedIn) in a controlled environment with proper credentials.
- Run `scripts/smoke_runner.py --iterations N` to run a quick smoke test across pipeline stages.

## Next work items
- Enhance chart generation step with TA annotations (support/resistance, trendlines, annotations) — this requires instrument-level annotation logic and drawing helpers.
- Add integration tests for Notion/Automata push when services are available (optional test mode with mock endpoints).
- Expand documentation diagrams (mermaid / dot) to include organizer and executor details.

---
For any changes you want to be applied to the legacy layout or manifest format (e.g., specific metadata fields), tell me the exact structure and I will update the organizer to match it exactly.
