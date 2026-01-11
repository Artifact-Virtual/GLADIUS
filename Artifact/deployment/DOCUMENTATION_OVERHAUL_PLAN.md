# Documentation Overhaul Plan

Goal: Transform this repository into a fully documented, DAO-grade knowledge base with no blind spots. Documentation must cover architecture, code, APIs, runbooks, security, governance, tests, and operational playbooks.

Scope
- All code under `gladius/` and top-level deployment scripts
- AI engine: providers, vector store, context engine, generator, reflection
- Dashboard: backend API, frontend templates, UI controls
- Ingest pipelines and scheduled jobs
- Devops: .env, systemd timers, deployment scripts, CI
- Tests and how to run them locally
- Governance: DAO roles, approval flows, changelog and decision records

Deliverables
1. `DOCUMENTATION_INVENTORY.md` — full repo inventory
2. `docs/` site (MkDocs) containing:
   - `index.md` (DOCUMENTATION_INDEX)
   - `architecture.md` (diagrams + data flow)
   - `api.md` (dashboard API reference + examples)
   - `components/` (per-subsystem docs)
   - `runbooks/` (deploy, restore, troubleshooting)
   - `governance.md` (DAO docs, ownership, decisions)
   - `tutorials/` (end-to-end workflows)
3. `mkdocs.yml` + CI workflow for doc build & link-checks
4. Doc tests and guidelines (STYLE_GUIDE.md)

Tooling Recommendation
- MkDocs with Material theme for readable site
- Mermaid for diagrams (can render in MkDocs)
- CI: run `mkdocs build` and link-check on PRs; run `pytest -q` for tests
- Keep docs in `docs/` and high-level index at `Artifact/deployment/DOCUMENTATION_INDEX.md`

Timeline (iterative)
1. Inventory & plan (this file) — DONE
2. Scaffold docs/ and add core pages (index, inventory) — NEXT
3. Add automated checks & CI — NEXT
4. Fill component docs & runbooks — iterative with SME review
5. Final review & sign-off

Acceptance Criteria
- Every public API endpoint documented with request/response examples
- All DB tables and schemas documented with purpose and usage
- Runbook for deploy, backup/restore, and incident playbook present
- Governance doc describing how decisions are taken and where to find change records
- Documentation builds successfully in CI and link-checks pass

---

Next immediate action: scaffold `docs/` and `mkdocs.yml`, add `DOCUMENTATION_INVENTORY.md` and `DOCUMENTATION_INDEX.md` summary pages. I will begin scaffolding now and then start the inventory scan.