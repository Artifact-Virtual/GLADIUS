# Article Index
*Gladius Articles Collection* | *58 Articles* | *12 Sections*

> **Canonical Content Roadmap**
> Exhaustive list of article topics derived from the Architectural Mandate

Click any title to jump to the full article.

---

<p align="center">

[![Coverage](https://img.shields.io/badge/coverage-58%2F58%20articles-success?style=for-the-badge&logo=checkmarx&logoColor=white)](#)
[![Proofread](https://img.shields.io/badge/proofread-verified-blue?style=for-the-badge&logo=grammarly&logoColor=white)](#)
[![Peer Review](https://img.shields.io/badge/peer%20review-complete-purple?style=for-the-badge&logo=gitbook&logoColor=white)](#)
[![Citations](https://img.shields.io/badge/citations-internal-lightgrey?style=for-the-badge&logo=semanticscholar&logoColor=white)](#)

</p>

---

## Table of Contents

- [Section A: Strategy & Positioning](#section-a-strategy--positioning)
- [Section B: Architecture & Design Patterns](#section-b-architecture--design-patterns)
- [Section C: Model Infrastructure & Runtime](#section-c-model-infrastructure--runtime)
- [Section D: Retrieval & Knowledge Layers](#section-d-retrieval--knowledge-layers)
- [Section E: Data, Pipelines & Quant Ops](#section-e-data-pipelines--quant-ops)
- [Section F: Execution & Herald Trading Agent](#section-f-execution--herald-trading-agent)
- [Section G: Observability, Monitoring & Runbooks](#section-g-observability-monitoring--runbooks)
- [Section H: Governance, Compliance & Risk](#section-h-governance-compliance--risk)
- [Section I: Security & Confidentiality](#section-i-security--confidentiality)
- [Section J: Developer Experience & Tooling](#section-j-developer-experience--tooling)
- [Section K: Research & Advanced Topics](#section-k-research--advanced-topics)
- [Section L: Outreach, Governance & Education](#section-l-outreach-governance--education)

---

## Section A: Strategy & Positioning

| # | Title | Type | Assets |
|---|-------|------|--------|
| 1 | [The SLM-First Paradigm: Why Local Models Win in Regulated Fintech](01_the_slm_first_paradigm.md) | Whitepaper | Cost model, latency benchmarks |
| 2 | [The Agentic Execution Trilemma: Autonomy vs Latency vs Compliance](02_the_agentic_execution_trilemma.md) | Blog/Think-piece | Diagrams |
| 3 | [From Research to Production: Closing the Agentic Reality Gap](03_from_research_to_production.md) | Case Study | Checklist, migration steps |
| 4 | [Responsible Autonomy: Embedding Human-in-the-Loop Controls](04_responsible_autonomy.md) | Guide | Policy checklist, runbook snippets |
| 5 | [Economic Case for Hybrid LLMs: Token Costs, Quotas, and Unit Economics](05_economic_case_for_hybrid_llms.md) | Analysis | Pricing models |

---

## Section B: Architecture & Design Patterns

| # | Title | Type | Assets |
|---|-------|------|--------|
| 6 | [Building Deterministic Agent Workflows: State Machines and Provenance](06_deterministic_agent_workflows.md) | Tutorial/Guide | Example state machine, tests |
| 7 | [Idempotency in Financial Systems: Patterns and Pitfalls](07_idempotency_in_financial_systems.md) | Tutorial | Code samples, test cases |
| 8 | [Circuit Breakers and Fallbacks for Trading Agents](08_circuit_breakers_and_fallbacks.md) | Guide | Diagrams, pseudocode |
| 9 | [Semantic Routing: Designing a vLLM Intent Router](09_semantic_routing.md) | Technical Guide | Mermaid flow, sample classifier |
| 10 | [Scheduling & Adaptive Task Allocation for Low-Latency Workloads](10_scheduling_adaptive_task_allocation.md) | How-To | Scheduler configs, metrics |

---

## Section C: Model Infrastructure & Runtime

| # | Title | Type | Assets |
|---|-------|------|--------|
| 11 | [Llama.cpp vs Ollama vs Cloud LLMs: Deployment Tradeoffs](11_llama_cpp_vs_ollama_vs_cloud.md) | Comparative Guide | Install recipes |
| 12 | [Best Practices for Local SLM Deployment and Monitoring](12_local_slm_deployment_best_practices.md) | Guide | Runbooks, metrics list |
| 13 | [Quantization Deep Dive: Q4_K_M and Practical Performance Tips](13_quantization_deep_dive.md) | Technical Deep-Dive | Benchmarks |
| 14 | [Model Orchestration: Escalation Policies from SLM → LLM](14_model_orchestration_escalation_policies_.md) | Guide | Policy templates |
| 15 | [Benchmarks for Time-to-First-Token and Sustain Throughput](15_benchmarks_for_time_to_first_token_and_s.md) | Benchmark Report | Charts, reproducible scripts |

---

## Section D: Retrieval & Knowledge Layers

| # | Title | Type | Assets |
|---|-------|------|--------|
| 16 | [RAG for Compliance: How to Build Audit-Friendly Retrieval Pipelines](16_rag_for_compliance_building_audit_friend.md) | Guide | Architecture, NER/lineage |
| 17 | [Choosing & Evaluating Embedding Models for Finance](17_choosing_and_evaluating_embedding_models.md) | Analysis | Evaluation metrics |
| 18 | [Vector Database Patterns at Scale: HNSW, PQ, pgvector, Qdrant](18_vector_database_patterns_at_scale_hnsw_p.md) | Technical Guide | Tuning checklist |
| 19 | [Retrieval QA: Measuring Recall & Precision in Financial RAG](19_retrieval_qa_measuring_recall_and_precis.md) | Tutorial | Tests, datasets |
| 20 | [Embedding Maintenance: Reindexing, Churn, and Incremental Updates](20_embedding_maintenance_reindexing_churn_a.md) | Operations | Scripts |

---

## Section E: Data, Pipelines & Quant Ops

| # | Title | Type | Assets |
|---|-------|------|--------|
| 21 | [Data Normalization for Financial Workflows](21_data_normalization_for_financial_workflo.md) | Guide | Canonical schema |
| 22 | [Building a Reproducible Analysis Pipeline (ingest → report → archive)](22_building_a_reproducible_analysis_pipelin.md) | Tutorial | Code examples |
| 23 | [Quant Performance Engineering: Numba & NumPy Optimizations](23_quant_performance_engineering_numba_and_.md) | How-To | Before/after benchmarks |
| 24 | [Backtesting vs Real-Time Execution: Bridging the Gap](24_backtesting_vs_real_time_execution_bridg.md) | Analysis | Experiments |
| 25 | [Technical Indicators at Scale: Efficient Implementations and Tests](25_technical_indicators_at_scale_efficient_.md) | Tutorial | Code |

---

## Section F: Execution & Herald Trading Agent

| # | Title | Type | Assets |
|---|-------|------|--------|
| 26 | [Introducing Herald: Design and Safety Considerations for a Trading Executor](26_introducing_herald_design_and_safety_for.md) | Whitepaper | Safety checklist |
| 27 | [Exchange Integration Patterns: Safe Order Execution & Idempotency](27_exchange_integration_patterns_safe_order.md) | Guide | API patterns |
| 28 | [Testing Execution Agents: Simulation, Replay, and Shadow Modes](28_testing_execution_agents_simulation_repl.md) | Tutorial | Test harness |
| 29 | [Training and Evaluating Execution Models on BTCUSD](29_training_and_evaluating_execution_models.md) | Case Study | Dataset notes |
| 30 | [Operational Playbook for Live Execution: Rollbacks and Incident Response](30_operational_playbook_for_live_execution_.md) | Runbook | Checklist |

---

## Section G: Observability, Monitoring & Runbooks

| # | Title | Type | Assets |
|---|-------|------|--------|
| 31 | [Metrics that Matter: Agent-Specific Observability](31_metrics_that_matter_agent_specific_obser.md) | Guide | Grafana dashboards |
| 32 | [Alerting & Runbooks for Autonomous Agents](32_alerting_and_runbooks_for_autonomous_age.md) | How-To | Alert rules |
| 33 | [Logging, Traceability, and Audit Logs for Agent Decisions](33_logging_traceability_and_audit_logs_for_.md) | Tutorial | Sample logs, schema |
| 34 | [Integrating Prometheus, Grafana, Loki for Fintech Agents](34_integrating_prometheus_grafana_loki_for_.md) | Guide | docker-compose snippets |
| 35 | [Incident Response Example: Handling Model Drift or Data Breakage](35_incident_response_example_handling_model.md) | Case Study | Playbook |

---

## Section H: Governance, Compliance & Risk

| # | Title | Type | Assets |
|---|-------|------|--------|
| 36 | [Applying the EU AI Act to Agentic Trading Systems](36_applying_the_eu_ai_act_to_agentic_tradin.md) | Policy Brief | Compliance checklist |
| 37 | [SEC Considerations: Human Oversight and Advice Screening](37_sec_considerations_human_oversight_and_a.md) | Guide | HIL policy template |
| 38 | [Auditing AI Output: Traceability, Explainability, and Evidence](38_auditing_ai_output_traceability_explaina.md) | How-To | Evidence capture patterns |
| 39 | [Privacy & Data Sovereignty: Architectures for Air-Gapped Inference](39_privacy_and_data_sovereignty_air_gapped_.md) | Technical Guide | Deployment steps |
| 40 | [Responsible DeFi Agents: Compliance Challenges for Decentralized Finance](40_responsible_defi_agents_compliance_chall.md) | Analysis | Risk map |

---

## Section I: Security & Confidentiality

| # | Title | Type | Assets |
|---|-------|------|--------|
| 41 | [Secure Model Storage and Attestation (SBOM & Signing)](41_secure_model_storage_and_attestation_sbo.md) | Guide | Process checklist |
| 42 | [Secrets Management for LLM Integration: Vaults and Runtime Secrets](42_secrets_management_for_llm_integration_v.md) | Tutorial | Examples |
| 43 | [Threat Modeling for Agentic Systems](43_threat_modeling_for_agentic_systems.md) | Framework | Threat matrix |
| 44 | [Hardening the VM Runtime: Kernel, Containers, and Network Policies](44_hardening_the_vm_runtime_kernel_containe.md) | Operations | Checklist |

---

## Section J: Developer Experience & Tooling

| # | Title | Type | Assets |
|---|-------|------|--------|
| 45 | [Developer Workflows: Local Iteration, Testing, and Reproducibility](45_developer_workflows_local_iteration_test.md) | Guide | Docker development recipes |
| 46 | [CI/CD for Model & Image Publishing: GH Actions for Multi-arch Builds](46_ci_cd_for_model_and_image_publishing_git.md) | How-To | Workflows |
| 47 | [Writing Effective Integration Tests for Agent Interaction Patterns](47_writing_effective_integration_tests_for_.md) | Tutorial | Test templates |
| 48 | [Creating a Pipeline Audit Tool: Implementation Walkthrough](48_creating_a_pipeline_audit_tool_implement.md) | Tutorial | Code review |
| 49 | [Frontmatter & Metadata Best Practices for Archival Pipelines](49_frontmatter_and_metadata_best_practices_.md) | How-To | Frontmatter schema |

---

## Section K: Research & Advanced Topics

| # | Title | Type | Assets |
|---|-------|------|--------|
| 50 | [Measuring Hallucination in RAG-Enabled Financial Summaries](50_measuring_hallucination_in_rag_enabled_f.md) | Research | Experimental protocol |
| 51 | [Specialized Financial Embeddings: Building and Fine-Tuning a FinBERT2-Like Encoder](51_specialized_financial_embeddings_fine_tu.md) | Research | Dataset recipe |
| 52 | [Semantic & Quota-Aware Routing Algorithms](52_semantic_and_quota_aware_routing_algorit.md) | Research | Algorithm sketches |
| 53 | [Cost-Accuracy Frontier: When to Escalate to Frontier LLMs](53_cost_accuracy_frontier_when_to_escalate_.md) | Analysis | Decision curve |
| 54 | [Hierarchical Agent Design: Decomposing Complex Work for Verifiability](54_hierarchical_agent_design_decomposing_co.md) | Whitepaper | Diagrams |

---

## Section L: Outreach, Governance & Education

| # | Title | Type | Assets |
|---|-------|------|--------|
| 55 | [Creating a Public Notion Archive: Best Practices for Research Transparency](55_creating_a_public_notion_archive_researc.md) | Guide | Notion schema |
| 56 | [How to Communicate AI Limitations to Traders](56_how_to_communicate_ai_limitations_to_tra.md) | Blog | Checklist |
| 57 | [Workshop: From Mandate to PRs — Running a Sprint to Operationalize the Mandate](57_workshop_from_mandate_to_prs_running_a_s.md) | Workshop | Agenda |
| 58 | [Checklist for Publishing a Release (docs, changelog, docker, release notes)](58_checklist_for_publishing_a_release.md) | Operations | Checklist |

---

## Legend

| Type | Description |
|------|-------------|
| **Whitepaper** | Strategic analysis with economic models |
| **Guide** | Implementation guidance with checklists |
| **Tutorial** | Step-by-step technical implementation |
| **How-To** | Practical task-focused instructions |
| **Deep-Dive** | Detailed technical analysis |
| **Case Study** | Real-world applications and lessons learned |
| **Research** | Experimental and advanced topics |
| **Analysis** | Data-driven evaluation and comparison |
| **Operations** | Runbooks and operational guidance |

---

## Notes

- Each listed title is unique; topics are organized horizontally (topical pillars) and vertically (blog → tutorial → research)
- Click any article title to open the full content
- This index is the canonical source for article navigation

---

*Maintainer:* `amuzetnoM` — contact for editorial or publishing requests.
