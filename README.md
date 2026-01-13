# Gladius

> Autonomous Enterprise Operating System for AI Research & Trading

A comprehensive autonomous enterprise system managing multiple artifacts (business units) through unified context, native vectorization, and semantic memory. Features native C++ vector database (Hektor), llama.cpp inference, and ONNX Runtime for fully local AI operations.

---

## 🚀 Quick Start (Operators)

```bash
cd /home/adam/worxpace/gladius

# Start all services (includes automatic health check)
./gladius.sh start

# Check system status
./gladius.sh status

# Stop all services (includes regression verification)
./gladius.sh stop

# Test Infra API specifically
./gladius.sh infra
```

**Access Points**:
- Dashboard: http://localhost:3000
- API Docs: http://localhost:7000/docs
- Backend API: http://localhost:5000

---

## 🏗️ Architecture

```
                    ┌─────────────────────────────────────┐
                    │           GLADIUS                   │
                    │   Context • Vectorization • Memory  │
                    │   Hektor VDB • llama.cpp • ONNX     │
                    └───────────────┬─────────────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           ▼                        ▼                        ▼
    ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
    │   ALPHA     │          │    BETA     │          │   THETA     │
    │  Syndicate  │          │   Cthulu    │          │  (Future)   │
    │  Research   │          │   Trading   │          │  Publishing │
    └─────────────┘          └─────────────┘          └─────────────┘
```

---

## 📋 Quick Navigation

### Operational Guides
- **[COMMANDS.md](COMMANDS.md)** - Complete command reference for developers
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture & design
- **[MANDATE.md](MANDATE.md)** - Operational mandate
- **[CONTEXT.md](CONTEXT.md)** - Current system context

### Documentation
- [Main Repository README](obsidian_sync/README.md)
- [Official Documentation](docs/readme.md)
- [License](LICENSE.md)

### Scripts
- [gladius.sh](gladius.sh) - Unified control script (start, stop, health, status)

---

## 🏗️ Core Systems

| System | Description | Status |
|--------|-------------|--------|
| **Hektor VDB** | Native C++ vector database (SIMD, HNSW, BM25) | ✅ Production |
| **Cognition Engine** | Semantic memory with hybrid search | ✅ Production |
| **Infra API** (7000) | Market data, portfolios, assets | ✅ Production |
| **Automata Dashboard** (5000) | Control panel, content management | ✅ Production |
| **Syndicate** (Alpha) | Market intelligence pipeline | ✅ Production |
| **Cthulu** (Beta) | MQL5/MT5 trading execution | ✅ Staging |
| **Memory Module** | Multi-DB access, native tool calling (16 tools) | ✅ Production |
| **Prediction Learning** | Pattern recognition, feedback loops | ✅ Production |

---

## 🔧 Hektor VDB (Native C++)

Build and use the native vector database:

```bash
# Build with all features
cd Artifact/hektor
mkdir -p build && cd build
cmake .. -DVDB_BUILD_PYTHON=ON -DVDB_USE_LLAMA_CPP=ON -DVDB_USE_ONNX_RUNTIME=ON
make -j$(nproc)
```

```python
# Python usage
from cognition.hektor_store import get_vector_store
store = get_vector_store("./vectors", dim=384, prefer_hektor=True)
store.add_text("doc1", "Gold broke above resistance", {"type": "journal"})
results = store.hybrid_search("gold breakout", k=5)
```

---

## 🧠 Prediction Learning System

The cognition engine learns from predictions through a feedback loop:

```python
from cognition.syndicate_integration import SyndicateCognition

cognition = SyndicateCognition(data_dir='./data', output_dir='./output')

# Record prediction
cognition.learn_from_prediction(
    prediction_date='2026-01-13',
    predicted_bias='BULLISH',
    actual_outcome='PENDING',
    gold_price_then=2680.0,
    gold_price_now=2695.0,
    market_context='Gold testing 2700 resistance'
)

# Get pattern success rate
pattern = cognition.get_pattern_success_rate('gold bullish breakout')
print(f"Success rate: {pattern['success_rate']}%")

# Generate learning feedback for AI
feedback = cognition.generate_learning_feedback()
```

**Learning Features**:
- Pattern recognition from historical outcomes
- Similar market condition search
- Adaptive recommendations based on win rates
- Confidence scoring with streak tracking

---

## 📚 Research Articles

### Core Philosophy & Design
- [Article Index](00_article_index.md) - Complete article listing
- [The SLM-First Paradigm](01_the_slm_first_paradigm.md)
- [The Agentic Execution Trilemma](02_the_agentic_execution_trilemma.md)
- [From Research to Production](03_from_research_to_production.md)
- [Responsible Autonomy](04_responsible_autonomy.md)

### System Design & Infrastructure
- [Economic Case for Hybrid LLMs](05_economic_case_for_hybrid_llms.md)
- [Deterministic Agent Workflows](06_deterministic_agent_workflows.md)
- [Idempotency in Financial Systems](07_idempotency_in_financial_systems.md)
- [Circuit Breakers and Fallbacks](08_circuit_breakers_and_fallbacks.md)
- [Semantic Routing](09_semantic_routing.md)

### Model Deployment & Operations
- [Local SLM Deployment Best Practices](12_local_slm_deployment_best_practices.md)
- [Model Orchestration & Escalation Policies](14_model_orchestration_escalation_policies_.md)
- [RAG for Compliance](16_rag_for_compliance_building_audit_friend.md)
- [Vector Database Patterns at Scale](18_vector_database_patterns_at_scale_hnsw_p.md)

### Trading Systems & Execution
- [Introducing Herald](26_introducing_herald_design_and_safety_for.md)
- [Exchange Integration Patterns](27_exchange_integration_patterns_safe_order.md)
- [Testing Execution Agents](28_testing_execution_agents_simulation_repl.md)
- [Operational Playbook for Live Execution](30_operational_playbook_for_live_execution_.md)

### Compliance & Security
- [Applying the EU AI Act to Agentic Trading](36_applying_the_eu_ai_act_to_agentic_tradin.md)
- [SEC Considerations](37_sec_considerations_human_oversight_and_a.md)
- [Auditing AI Output](38_auditing_ai_output_traceability_explaina.md)
- [Privacy and Data Sovereignty](39_privacy_and_data_sovereignty_air_gapped_.md)
- [Secure Model Storage and Attestation](41_secure_model_storage_and_attestation_sbo.md)
- [Threat Modeling for Agentic Systems](43_threat_modeling_for_agentic_systems.md)

---

## 📊 MQL5 Trading Strategy Handbook

### Overview
- [MQL5 Handbook README](obsidian_sync/dev_docs/mql5_handbook/README.md)
- [Manifest](obsidian_sync/dev_docs/mql5_handbook/manifest.md)

### Phase 1: Foundations
- [Classic Strategies](mql5_handbook/phase1/articles/)
- Moving Average systems and reimagined approaches

### Phase 2: Risk Management
- [Risk Management Fundamentals](16820-Risk-Management-Part-1-Fundamentals-for-Building-a-Risk-Management-Class.md)
- [Lot Calculation in Graphical Interface](16985-Risk-Management-Part-2-Implementing-Lot-Calculation-in-a-Graphical-Interface.md)
- [Managing Gains Through Structured Trade Exits](19693-Building-a-Trading-System-Part-5-Managing-Gains-Through-Structured-Trade-Exits.md)

### Phase 3: Advanced Strategies
- [Session-Based Opening Range Breakout](noid-Automating-Trading-Strategies-in-MQL5-Part-42-Session-Based-Opening-Range-Breakout-ORB-System.md)
- [Adaptive Linear Regression Channel](noid-Automating-Trading-Strategies-in-MQL5-Part-43-Adaptive-Linear-Regression-Channel-Strategy.md)
- [Price Action Analysis Toolkit](noid-Price-Action-Analysis-Toolkit-Development-Part-39-Automating-BOS-and-ChoCH-Detection-in-MQL5.md)
- [Statistical Arbitrage Through Cointegrated Stocks](noid-Statistical-Arbitrage-Through-Cointegrated-Stocks-Part-8-Rolling-Windows-Eigenvector-Comparison-for-Portfolio-Rebalancing.md)

---

## 🔬 Research Materials

### Technical Research
- [Research Index](obsidian_sync/dev_docs/research/INDEX.md)
- [Research README](obsidian_sync/dev_docs/research/README.md)
- [HNSW Algorithm](hnsw_algorithm.md)
- [Vector Space Theory](vector_space_theory.md)

### Papers & References
- [Research Papers](research/papers/)
- [Reference Materials](research/references/)

---

## 🗒️ Research Notes

- [System Report](dev_docs/_dev/SYSTEM_REPORT.md)
- [Completion Report](completion_report.md)
- [Note 1](note_1.md)
- [Note 2](note_2.md)

---

## 🏗️ Project Builds

### Cthulu Trading System
- [Subprogram Recommendations](/_build/cthulu/SUBPROGRAM_RECOMMENDATIONS.md)
- [GCP Access Control](/_build/cthulu/gcp_accesscontrol.md)
- **System Review:**
  - [Executive Summary](/_build/cthulu/review/EXECUTIVE_SUMMARY.md)
  - [Comprehensive System Review](/_build/cthulu/review/COMPREHENSIVE_SYSTEM_REVIEW.md)
  - [System Overview Compact](/_build/cthulu/review/SYSTEM_OVERVIEW_COMPACT.md)
  - [Review Summary Table](/_build/cthulu/review/REVIEW_SUMMARY_TABLE.md)

### Herald Execution Agent
- [Config Wizard](/_build/herald/config/wizard.py)

---

## 🖥️ Virtual Machine & Infrastructure

### GCP VM Setup
- [VM Access Guide](vm_access.md)
- [SSH Setup Guide](ssh_setup_guide.md)
- [Development Secrets](DEV_SECRETS.md)

### Current Deployment
- [Cthulu Node Access Control](cthulu_node_AC.md)

---

## 📐 Architecture & Technical Documentation

- [Architectural Mandate](architectural_mandate.md)
- [RPC Documentation](dev_docs/_dev/rpc.md)
- [Windows Access](ACCESS_WINDOWS.md)
- [Windows Sudo Access](ACCESS_WINDOWS_SUDO.md)

---

## 🔧 Scripts & Utilities

### PowerShell Scripts
- [Configure GH Global](configure_gh_global.ps1)
- [Create Desktop Shortcut](create_desktop_shortcut.ps1)
- [Desktop Launch Herald and MT5](desktop_launch_herald_and_mt5.ps1)
- [Fix PowerShell Profile](fix_powershell_profile.ps1)
- [Verify PowerShell Setup](verify_powershell_setup.ps1)
- [Integration Run Dry](integration_run_dry.ps1)
- [Run Herald Wizard Foreground](run_herald_wizard_foreground.ps1)

### Shell Scripts
- [Append Key](append_key.sh)
- [GCP Startup Odyssey](gcp_startup_odyssey.sh)
- [GCP Startup Soundwave](gcp_startup_soundwave.sh)
- [MT5 Automate](mt5_automate.sh)

### Python Scripts
- [Generate Sample Charts](generate_sample_charts.py)

---

## 🚀 GoldMax Project

> A system that refuses to lie - continuous market memory for disciplined decision-making

- [GoldMax Broadcast](broadcast.md) - Detailed system overview

---

## 📝 Release Management

- [Release Guide](release_guide.md)
- [Release Tools](release_tools.md)

---

## 🔄 Work in Progress

- [To Do](to do.md)

---

*Last updated: 2026-01-13*
