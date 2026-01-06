# AI & Trading Research Articles

> Comprehensive collection of research articles on AI systems, trading automation, and infrastructure

This directory contains 60+ research articles covering the full spectrum of AI-driven trading system development, from foundational concepts to production deployment.

---

## 📚 Article Index

For a complete list of all articles with descriptions, see **[00_article_index.md](00_article_index.md)**

---

## 📑 Article Categories

### 🧠 Core Philosophy & Design (Articles 1-10)
Foundational concepts for building autonomous trading systems:
- The SLM-First Paradigm
- The Agentic Execution Trilemma
- From Research to Production
- Responsible Autonomy
- Economic Case for Hybrid LLMs
- Deterministic Agent Workflows
- Idempotency in Financial Systems
- Circuit Breakers and Fallbacks
- Semantic Routing
- Scheduling & Adaptive Task Allocation

### 🖥️ Model Deployment & Operations (Articles 11-15)
Local SLM deployment and infrastructure:
- Llama.cpp vs Ollama vs Cloud
- Local SLM Deployment Best Practices
- Quantization Deep Dive
- Model Orchestration & Escalation Policies
- Benchmarks for Time-to-First-Token

### 🔍 RAG & Vector Search (Articles 16-20)
Retrieval-augmented generation for compliance and analysis:
- RAG for Compliance
- Choosing and Evaluating Embedding Models
- Vector Database Patterns at Scale (HNSW, PQ)
- Retrieval QA: Measuring Recall and Precision
- Embedding Maintenance & Reindexing

### 📊 Data Engineering (Articles 21-25)
Building robust data pipelines:
- Data Normalization for Financial Workflows
- Building a Reproducible Analysis Pipeline
- Quant Performance Engineering (Numba, Polars)
- Backtesting vs Real-Time Execution
- Technical Indicators at Scale

### 🤖 Trading Execution (Articles 26-30)
Herald execution agent and live trading:
- Introducing Herald: Design and Safety
- Exchange Integration Patterns
- Testing Execution Agents
- Training and Evaluating Execution Models
- Operational Playbook for Live Execution

### 📈 Observability & Monitoring (Articles 31-35)
Metrics, logging, and incident response:
- Metrics That Matter: Agent-Specific Observability
- Alerting and Runbooks for Autonomous Agents
- Logging, Traceability, and Audit Logs
- Integrating Prometheus, Grafana, Loki
- Incident Response Example

### ⚖️ Compliance & Legal (Articles 36-40)
Regulatory considerations for AI trading:
- Applying the EU AI Act to Agentic Trading
- SEC Considerations: Human Oversight and Accountability
- Auditing AI Output: Traceability, Explainability
- Privacy and Data Sovereignty (Air-Gapped LLMs)
- Responsible DeFi Agents

### 🔒 Security (Articles 41-45)
Hardening AI trading systems:
- Secure Model Storage and Attestation (SBOM)
- Secrets Management for LLM Integration (Vault)
- Threat Modeling for Agentic Systems
- Hardening the VM Runtime (Kernel, Container, Network)
- Developer Workflows: Local Iteration, Testing

### 🛠️ DevOps & Testing (Articles 46-50)
CI/CD and development practices:
- CI/CD for Model and Image Publishing
- Writing Effective Integration Tests
- Creating a Pipeline Audit Tool
- Frontmatter and Metadata Best Practices
- Measuring Hallucination in RAG-Enabled Financial Systems

### 🎯 Advanced Topics (Articles 51-58)
Specialized and advanced concepts:
- Specialized Financial Embeddings
- Semantic and Quota-Aware Routing Algorithms
- Cost-Accuracy Frontier: When to Escalate to GPT-4
- Hierarchical Agent Design
- Creating a Public Notion Archive
- How to Communicate AI Limitations to Traders
- Workshop: From Mandate to PRs
- Checklist for Publishing a Release

---

## 🎓 How to Use This Collection

### For New Readers
Start with the foundational articles (1-10) to understand the core philosophy and design principles.

### For System Builders
Focus on categories relevant to your work:
- **AI/ML Engineers**: Articles 11-20 (Model Deployment, RAG)
- **Data Engineers**: Articles 21-25 (Data Engineering)
- **Trading System Developers**: Articles 26-30 (Execution)
- **DevOps/SRE**: Articles 31-35, 46-50 (Observability, DevOps)
- **Compliance Officers**: Articles 36-40 (Compliance & Legal)
- **Security Teams**: Articles 41-45 (Security)

### For Research
All articles are cross-referenced and build upon each other. Use the index to find related topics.

---

## 📝 Article Format

Each article follows a consistent structure:
- **Title & Overview**: Clear description of topic
- **Problem Statement**: What challenge does this address?
- **Technical Deep Dive**: Implementation details
- **Best Practices**: Practical recommendations
- **References**: Related articles and resources

---

## 🔗 Related Documentation

### Research Materials
- [Research Papers](../research/papers/) - Academic papers and references
- [Research Notes](../notes/) - System reports and completion notes
- [Vector Space Theory](../research/vector_space_theory.md)
- [HNSW Algorithm](../research/hnsw_algorithm.md)

### Practical Guides
- [MQL5 Handbook](../mql5_handbook/README.md) - Trading strategy implementation
- [Virtual Machine Setup](../virtual_machine/) - Infrastructure documentation
- [Scripts & Utilities](../scripts/) - Automation tools

### Projects
- [GoldMax](../../projects/goldmax/) - Market analysis system
- [Herald](../../projects/herald/) - Execution agent
- [Cthulu](../../projects/cthulu/) - MQL5 trading system

---

## 📚 Complete Index

**👉 [View Complete Article Index](00_article_index.md)**

The complete index includes:
- Full article titles
- Brief descriptions
- Article numbers for easy reference
- Cross-references to related articles

---

## 🤝 Contributing

This is a private research repository. Articles are written as part of ongoing research and development.

For questions or discussions about the articles, contact [`amuzetnoM`](https://github.com/amuzetnoM).

---

## 📄 License

All articles are proprietary and covered under the repository license. See [LICENSE.md](../../docs/LICENSE.md) for details.

---

*Part of the Gladius research repository*
