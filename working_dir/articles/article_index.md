# Article Index — Derived from the Architectural Mandate

Purpose: Exhaustive list of article topics (unique, non-redundant) that can be produced from the mandate. Organized horizontally by theme, and vertically by depth (short blog → tutorial → deep technical / research). Use this index as a content roadmap.

Format: Title — short description (type: blog/tut/guide/whitepaper/case-study; assets: diagrams/code/benchmarks)

---

## A. Strategy & Positioning

1. The SLM-First Paradigm: Why Local Models Win in Regulated Fintech — (whitepaper; assets: cost model, latency benchmarks)
2. The Agentic Execution Trilemma: Autonomy vs Latency vs Compliance — (blog/think-piece; assets: diagrams)
3. From Research to Production: Closing the Agentic Reality Gap — (case-study; assets: checklist, migration steps)
4. Responsible Autonomy: Embedding Human-in-the-Loop Controls — (guide; assets: policy checklist, runbook snippets)
5. Economic Case for Hybrid LLMs: Token Costs, Quotas, and Unit Economics — (analysis; assets: pricing models)

## B. Architecture & Design Patterns

6. Building Deterministic Agent Workflows: State Machines and Provenance — (tut/guide; assets: example state machine, tests)
7. Idempotency in Financial Systems: Patterns and Pitfalls — (tutorial; assets: code samples, test cases)
8. Circuit Breakers and Fallbacks for Trading Agents — (guide; assets: diagrams, pseudocode)
9. Semantic Routing: Designing a vLLM Intent Router — (technical guide; assets: mermaid flow, sample classifier)
10. Scheduling & Adaptive Task Allocation for Low-Latency Workloads — (how-to; assets: scheduler configs, metrics)

## C. Model Infrastructure & Runtime

11. Llama.cpp vs Ollama vs Cloud LLMs: Deployment Tradeoffs — (comparative guide; assets: install recipes)
12. Best Practices for Local SLM Deployment and Monitoring — (guide; assets: runbooks, metrics list)
13. Quantization Deep Dive: Q4_K_M and Practical Performance Tips — (technical deep-dive; assets: benchmarks)
14. Model Orchestration: Escalation Policies from SLM → LLM — (guide; assets: policy templates)
15. Benchmarks for Time-to-First-Token and Sustain Throughput — (benchmark report; assets: charts, reproducible scripts)

## D. Retrieval & Knowledge Layers

16. RAG for Compliance: How to Build Audit-Friendly Retrieval Pipelines — (guide; assets: architecture, NER/lineage)
17. Choosing & Evaluating Embedding Models for Finance — (analysis; assets: evaluation metrics)
18. Vector Database Patterns at Scale: HNSW, PQ, pgvector, Qdrant — (technical guide; assets: tuning checklist)
19. Retrieval QA: Measuring Recall & Precision in Financial RAG — (tut; assets: tests, datasets)
20. Embedding Maintenance: Reindexing, Churn, and Incremental Updates — (operations; assets: scripts)

## E. Data, Pipelines & Quant Ops

21. Data Normalization for Financial Workflows — (guide; assets: canonical schema)
22. Building a Reproducible Analysis Pipeline (ingest → report → archive) — (tutorial; assets: code examples)
23. Quant Performance Engineering: Numba & NumPy Optimizations — (how-to; assets: before/after benchmarks)
24. Backtesting vs Real-Time Execution: Bridging the Gap — (analysis; assets: experiments)
25. Technical Indicators at Scale: Efficient Implementations and Tests — (tutorial; assets: code)

## F. Execution & Herald (Trading Agent)

26. Introducing `Herald`: Design and Safety Considerations for a Trading Executor — (whitepaper; assets: safety checklist)
27. Exchange Integration Patterns: Safe Order Execution & Idempotency — (guide; assets: API patterns)
28. Testing Execution Agents: Simulation, Replay, and Shadow Modes — (tut; assets: test harness)
29. Training and Evaluating Execution Models on BTCUSD — (case-study; assets: dataset notes)
30. Operational Playbook for Live Execution: Rollbacks and Incident Response — (runbook; assets: checklist)

## G. Observability, Monitoring & Runbooks

31. Metrics that Matter: Agent-Specific Observability (Step Efficiency, Tool Correctness) — (guide; assets: Grafana dashboards)
32. Alerting & Runbooks for Autonomous Agents — (how-to; assets: alert rules)
33. Logging, Traceability, and Audit Logs for Agent Decisions — (tut; assets: sample logs, schema)
34. Integrating Prometheus, Grafana, Loki for Fintech Agents — (guide; assets: docker-compose snippets)
35. Incident Response Example: Handling a Model Drift or Data Breakage — (case-study; assets: playbook)

## H. Governance, Compliance & Risk

36. Applying the EU AI Act to Agentic Trading Systems — (policy brief; assets: compliance checklist)
37. SEC Considerations: Human Oversight and Advice Screening — (guide; assets: HIL policy template)
38. Auditing AI Output: Traceability, Explainability, and Evidence — (how-to; assets: evidence capture patterns)
39. Privacy & Data Sovereignty: Architectures for Air-Gapped Inference — (technical guide; assets: deployment steps)
40. Responsible DeFi Agents: Compliance Challenges for Decentralized Finance — (analysis; assets: risk map)

## I. Security & Confidentiality

41. Secure Model Storage and Attestation (SBOM & Signing) — (guide; assets: process checklist)
42. Secrets Management for LLM Integration: Vaults and Runtime Secrets — (tut; assets: examples)
43. Threat Modeling for Agentic Systems — (framework; assets: threat matrix)
44. Hardening the VM Runtime: Kernel, Containers, and Network Policies — (operations; assets: checklist)

## J. Developer Experience & Tooling

45. Developer Workflows: Local Iteration, Testing, and Reproducibility — (guide; assets: docker development recipes)
46. CI/CD for Model & Image Publishing: GH Actions for Multi-arch Builds — (how-to; assets: workflows)
47. Writing Effective Integration Tests for Agent Interaction Patterns — (tut; assets: test templates)
48. Creating a Pipeline Audit Tool: Implementation Walkthrough — (tutorial; assets: code review)
49. Frontmatter & Metadata Best Practices for Archival Pipelines — (how-to; assets: frontmatter schema)

## K. Research & Advanced Topics

50. Measuring Hallucination in RAG-Enabled Financial Summaries — (research; assets: experimental protocol)
51. Specialized Financial Embeddings: Building and Fine-Tuning a FinBERT2-Like Encoder — (research; assets: dataset recipe)
52. Semantic & Quota-Aware Routing Algorithms — (research; assets: algorithm sketches)
53. Cost-Accuracy Frontier: When to Escalate to Frontier LLMs — (analysis; assets: decision curve)
54. Hierarchical Agent Design: Decomposing Complex Work for Verifiability — (whitepaper; assets: diagrams)

## L. Outreach, Governance, and Education

55. Creating a Public Notion Archive: Best Practices for Research Transparency — (guide; assets: Notion schema)
56. How to Communicate AI Limitations to Traders — (blog; assets: checklist)
57. Workshop: From Mandate to PRs — Running a Sprint to Operationalize the Mandate — (workshop; assets: agenda)
58. Checklist for Publishing a Release (docs, changelog, docker, release notes) — (ops; assets: checklist)

---

Notes:
- Each listed title is unique; topics are organized to scale horizontally (different topical pillars) and vertically (simple blog → implementation tutorial → deep research paper).
- If you want, I can now expand any chosen title into a full article outline (headings, required assets, target audience, estimated effort).
- This file is intended as a private content index — per your instruction I will not push it to GitHub unless you say so.
