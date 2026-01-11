# Artifact Virtual Enterprise Playbook

Purpose: Short operational guide for operators managing LLM-driven research and content pipelines across Artifact. This is the single-source-of-truth for: configuring provider order, enqueueing tasks, using provider hints, troubleshooting LLM failures, and safe restart/resume procedures.

---

## 1) Quick Config
- Preferred (local-first) operation: set environment variable `PREFER_OLLAMA=1` on services (Docker Compose / systemd templates provided under `Artifact/syndicate/deploy`).
- Force strict-only provider for a task: use `provider_hint="strict:<provider>"` when creating an LLM task (e.g., `strict:gemini`).
- Prefer a provider for a task (non-strict): use `provider_hint="<provider>"` (e.g., `gemini`, `ollama`, `local`). Legacy `gemini_only` / `ollama_only` are accepted and treated as non-strict preferences.

## 2) Enqueuing tasks (typical flow)
- Producers (scripts) should use `db.add_llm_task(document_path, prompt, provider_hint="<provider>")` to prefer a provider.
- For pre-market generations and other standard tasks, prefer non-strict hints so the system can fallback on transient failures.
- For regulatory or SLA-critical tasks that must use a single provider, use `strict:provider` explicitly.

## 3) Worker behavior (how tasks are processed)
- The worker will create a `FallbackLLMProvider` chain (default ordering: Gemini → Ollama → Local).
- If `PREFER_OLLAMA=1` is set, chain becomes: Ollama → Gemini → Local.
- If a task has `provider_hint="<provider>"`, the worker will instruct the provider chain to prefer that provider for the task; if the provider fails, the chain will fall back to the next provider automatically.
- If a task has `provider_hint="strict:<provider>"`, the worker will attempt to initialize/use only that provider and will fail if it cannot.

## 4) Health & Monitoring
- Metrics: Prometheus metrics names include `llm_queue_length`, `llm_tasks_processing`, and sanitizer counters (if sanitizer corrects numeric values).
- Health checks: Service health endpoints are present; use systemd `gold-standard-healthcheck.service` and Docker `healthcheck` for container verification.
- Alerts: Configure alerting on repeated `failed` task rates and increased sanitizer corrections.

## 5) Troubleshooting (common scenarios)
- Symptom: Tasks stuck with status `pending` or repeated `failed` errors.
  - Check provider availability: `PREFER_OLLAMA` and service logs (Ollama server status: `curl http://localhost:11434/v1/models`).
  - Check quota/keys: Gemini often errors if ADC or API key not configured—check `GEMINI_API_KEY` and ADC for Gemini.
  - If the provider is timing out: consider `Ollama` timeouts or offload to `local` (offloaded executor for GGUF models is provided).
- Symptom: Sanitizer flagged many corrections.
  - Inspect sanitizer audit logs (DB table from `save_llm_sanitizer_audit`) and review the report for correctness. If frequent, lower the trust level for that provider.

## 6) Emergency recovery & restart
- Prefer graceful restart: stop worker service (`systemctl stop gold-standard-llm-worker`), ensure queued tasks remain in DB, start worker service (`systemctl start ...`).
- If context memory or claim locks prevent progress: use the lock file path (`MEMORY_FILE`/`LOCK_FILE`) and follow runbook steps in `Artifact/syndicate/docs/virtual_machine/VM_RECOVERY.md` to clear stale claims.
- For persistent provider failures, flip `PREFER_OLLAMA=0` to return to Gemini-first or set `PREFER_LOCAL_LLM=1` if on-device models are required.

## 7) Operational notes & contacts
- Where to look: Logs under `Artifact/syndicate/output/` and `systemd` journal for services. Use `scripts/check_llms.py` for quick provider checks.
- Contacts: See `Artifact/MANDATE.md` maintainers list and `Artifact/syndicate/docs/` for module owners.

---

File: Artifact/docs/LLM_Fallback_Playbook.md
Last updated: 2026-01-11
