# AV Organizational Workflows & Checklists

                           +------------------------------+
                           |    High-level Acceptance     |
                           +------------------------------+
                                      ^
                                      |
                                 +----------+
                                 | Document |
                                 +----------+
                                      ^
                                      |
[Setup] -> [Build] -> [Automate] -> [Publish/Deploy] -> [Monitor] -> [Iterate] -> [Document]
   |
   +--> Research & Development (Organization-wide)
   |       - Research
   |       - Data Science & Analytics
   |
   +--> Engineering & DevOps
   |       - Platform & Infrastructure
   |       - Product Engineering
   |
   +--> Content & Communications
   |       - Content Production
   |       - Social Media & PR
   |
   +--> Product Management & Operations
   |       - Product / Roadmap
   |       - Operations & Support
   |
   +--> Quality Assurance & Testing
   +--> Security, Privacy & Compliance
   +--> Legal & Finance
   +--> People & Hiring
   +--> Cross-cutting: Monitoring, KPIs & Documentation
   |       - Monitoring & Alerts
   |       - Documentation & Knowledge
   |       - Continuous Improvement
   +--> Miscellaneous & Housekeeping

---

- Research & Development 
    - Research
        - [ ] Setup research agenda and priorities
        - [ ] Secure data sources, access, and legal/ethical approvals
        - [ ] Define success metrics and baseline hypotheses
        - [ ] Provision reproducible environments and repos
        - [ ] Implement data ingestion pipelines and schema validation
        - [ ] Develop experiments, analysis scripts, and prototypes
        - [ ] Automate experiment runs, training, and artifact storage
        - [ ] Publish results to internal reports, datasets, and dashboards
        - [ ] Monitor data quality, experiment drift, and result reproducibility
        - [ ] Establish peer review, retrospective cycles, and iteration plan
        - [ ] Document methods, reproducible notebooks, and SOPs
    - Data Science & Analytics
        - [ ] Define modeling objectives and evaluation metrics
        - [ ] Curate training/validation datasets and feature stores
        - [ ] Implement model development workflow (versioning, tests)
        - [ ] Set up CI for model training and validation
        - [ ] Deploy models (staging -> production) and CI/CD for models
        - [ ] Create monitoring (performance, concept drift, data drift)
        - [ ] Set automated alerts and rollback procedures
        - [ ] Maintain model registry, lineage, and documentation
        - [ ] Iterate on model improvements based on metrics and feedback
- Engineering & DevOps
    - Platform & Infrastructure
        - [ ] Provision infrastructure (cloud accounts, VPCs, IAM)
        - [ ] Establish repo structure, branching, and CI/CD pipelines
        - [ ] Implement infrastructure-as-code and secrets management
        - [ ] Deploy services, data pipelines, and job schedulers
        - [ ] Automate deployments, migrations, and scaling policies
        - [ ] Implement logging, tracing, and centralized telemetry
        - [ ] Monitor uptime, SLOs, and cost; set alerts and runbooks
        - [ ] Conduct chaos tests and incident response drills
        - [ ] Document runbooks, architecture diagrams, and onboarding guides
    - Product Engineering
        - [ ] Capture feature requirements and acceptance criteria
        - [ ] Design APIs, contracts, and integration points
        - [ ] Implement features with unit/integration tests
        - [ ] Automate test suites and build pipelines
        - [ ] Release schedule coordination and feature flags
        - [ ] Post-release monitoring and error tracking
        - [ ] Collect user feedback, prioritize backlog, and iterate
- Content & Communications
    - Content Production
        - [ ] Define audience, content objectives, and content calendar
        - [ ] Create style guidelines, branding assets, and templates
        - [ ] Assign content owners and review/approval workflows
        - [ ] Produce drafts (blogs, docs, social posts, whitepapers)
        - [ ] Implement editorial review, legal review, and approvals
        - [ ] Automate publishing workflows and scheduling
        - [ ] Distribute content across channels (website, social, newsletter)
        - [ ] Monitor engagement metrics, comments, and community signals
        - [ ] Incorporate feedback loops for content improvement
        - [ ] Document content SOPs and archive artifacts
    - Social Media & PR
        - [ ] Set up official social accounts and verification where possible
        - [ ] Create channel-specific asset packs and posting guidelines
        - [ ] Schedule automated posts and queues; confirm approvals
        - [ ] Monitor mentions, sentiment, and crisis signals
        - [ ] Configure alerts and escalation for PR issues
        - [ ] Track KPIs (reach, engagement, conversions) and iterate
- Product Management & Operations
    - Product / Roadmap
        - [ ] Define goals, KPIs, and success criteria for initiatives
        - [ ] Create release plans and cross-functional milestones
        - [ ] Coordinate handoffs between research, engineering, and content
        - [ ] Run regular reviews, demos, and stakeholder updates
        - [ ] Measure outcomes and iterate on roadmap based on data
    - Operations & Support
        - [ ] Establish support channels and SLAs
        - [ ] Document common issues and troubleshooting guides
        - [ ] Automate ticketing triage and escalation workflows
        - [ ] Monitor support metrics and feedback trends
        - [ ] Feed operational learnings back to product and engineering
- Quality Assurance & Testing
    - [ ] Define testing strategy (unit, integration, E2E, data sanity)
    - [ ] Implement test automation and test data management
    - [ ] Integrate tests into CI/CD and pre-release checks
    - [ ] Run pre-deployment validations and post-deploy smoke tests
    - [ ] Monitor test coverage, flaky tests, and quality KPIs
    - [ ] Document test plans and acceptance criteria
- Security, Privacy & Compliance
    - [ ] Perform security risk assessment and threat modeling
    - [ ] Implement access controls, encryption, and secret rotation
    - [ ] Apply compliance checks (GDPR, HIPAA, export controls as applicable)
    - [ ] Automate vulnerability scanning and dependency checks
    - [ ] Monitor security alerts and incident response workflows
    - [ ] Keep policy docs and audit logs up to date
- Legal & Finance
    - [ ] Review contracts, IP, licensing, and publisher agreements
    - [ ] Approve external partnerships and third-party data usage
    - [ ] Budget planning and cost monitoring for projects
    - [ ] Track ROI and financial KPIs; adjust investments accordingly
    - [ ] Document legal requirements and financial approvals
- People & Hiring
    - [ ] Identify required roles and staffing plan per initiative
    - [ ] Hire, onboard, and train contributors with role-specific docs
    - [ ] Establish mentorship, performance metrics, and growth plans
    - [ ] Schedule regular team retrospectives and knowledge sharing
- Cross-cutting: Monitoring, KPIs & Documentation
    - Monitoring & Alerts
        - [ ] Define organizational KPIs and SLOs per department
        - [ ] Implement centralized dashboards and alerting rules
        - [ ] Configure escalation paths and runbooks
        - [ ] Regularly review alerts, incidents, and postmortems
    - Documentation & Knowledge
        - [ ] Maintain a single source of truth for policies, SOPs, and assets
        - [ ] Keep onboarding guides, architecture docs, and playbooks current
        - [ ] Version and publish documentation in accessible locations
    - Continuous Improvement
        - [ ] Establish feedback loops from monitoring, users, and stakeholders
        - [ ] Prioritize iterative enhancements based on performance data
        - [ ] Schedule periodic audits and roadmap reviews
- Miscellaneous & Housekeeping
    - [ ] Maintain branding and asset libraries
    - [ ] Track and archive published content and datasets
    - [ ] Maintain an annual review schedule for compliance and goals
- High-level Acceptance
    - [ ] Ensure every department has linear setup -> build -> automate -> publish/deploy -> monitor -> iterate -> document workflow
    - [ ] Assign owners for KPIs, monitoring, and documentation for each workflow


## Artifact Operational Checklist (current priorities)

- Infrastructure & API
  - [x] Run infra API locally (dev): `uvicorn infra.api.app:app --host 127.0.0.1 --port 7000` and confirm `/markets`, `/assets`, `/prices`, `/portfolios` endpoints.
  - [x] Implement SQLite-backed repositories for Markets & Assets (`infra/repositories/sql_repository.py`).
  - [x] Seed COMEX/BINANCE and GOLD/BTC-USD assets using `infra/scripts/seed_gold_bitcoin.py`.
  - [ ] Persist portfolios & positions to SQLite (implement `PortfolioSqlRepository` and migration path).
  - [ ] Add API authentication and audit logging for infra endpoints (JWT or API keys).
  - [ ] Add healthcheck & metrics endpoints (`/health`, `/metrics`) and hook into monitoring/alerting.
  - [ ] Add scheduled backups for SQLite DB files and document restore runbook.

- Ingest & Data Flow
  - [x] Writer atomically writes `records.json` and `manifest.json` for each source.
  - [x] Writer posts latest price to infra (`INFRA_API_URL`) when set; ensure idempotency and retry behavior.
  - [ ] Add batch/stream ingestion and a queuing endpoint for high-throughput feeds.
  - [ ] Add ingestion integration tests (CI job): seed data → ingest -> assert portfolio P&L.

- Automata & Orchestration
  - [x] Automata backend can be started locally and responds to start/status endpoints (`dev_config.json` available for testing).
  - [ ] Harden Automata for production: run under a process manager, proper WSGI/ASGI server, secrets management, and monitoring.

- Dashboard, Reporting & Ops
  - [x] `ingest_bot` dashboard: runs locally and shows reports in `data/reports/`.
  - [ ] Add API endpoints to surface portfolio metrics for dashboards and alerts.
  - [ ] Add service unit templates for infra API, ingest workers and Automata for production flows.
- [ ] Operationalize `Artifact/syndicate` as a first-class research pipeline: add deploy units (systemd/docker) from `Artifact/syndicate/deploy` and prefer Ollama-first operation where appropriate (`PREFER_OLLAMA=1`).

- CI, Tests & Documentation
  - [ ] Add CI jobs for full end-to-end integration tests and a smoke test that seeds, ingests, and verifies portfolio calculations.
  - [ ] Keep MANDATE.md, CONTEXT.md, and this checklist up to date with runbooks and ownership.

*Last updated: 2026-01-11*



    ```mermaid

    flowchart TD
        RnD["Research & Development\n(Organization-wide)"]
        RnD --> Research[Research]
        RnD --> DS["Data Science & Analytics"]

        Eng["Engineering & DevOps"]
        Eng --> Platform["Platform & Infrastructure"]
        Eng --> ProdEng["Product Engineering"]

        Content["Content & Communications"]
        Content --> ContentProd["Content Production"]
        Content --> Social["Social Media & PR"]

        PMO["Product Management & Operations"]
        PMO --> Roadmap["Product / Roadmap"]
        PMO --> Ops["Operations & Support"]

        QA["Quality Assurance & Testing"]
        Sec["Security, Privacy & Compliance"]
        Legal["Legal & Finance"]
        People["People & Hiring"]

        Cross["Cross-cutting: Monitoring, KPIs & Documentation"]
        Cross --> Monitoring["Monitoring & Alerts"]
        Cross --> Docs["Documentation & Knowledge"]
        Cross --> CI["Continuous Improvement"]

        Misc["Miscellaneous & Housekeeping"]
        Acceptance["High-level Acceptance"]

        subgraph Workflow [Common workflow]
            Setup[Setup] --> Build[Build] --> Automate[Automate] --> Publish[Publish/Deploy] --> Monitor[Monitor] --> Iterate[Iterate] --> Document[Document]
        end

        %% Workflow applies across departments
        Setup --- RnD
        Setup --- Eng
        Setup --- Content
        Setup --- PMO
        Setup --- QA
        Setup --- Sec
        Setup --- Legal
        Setup --- People
        Setup --- Cross
        Setup --- Misc

        Document --- Acceptance

    ```