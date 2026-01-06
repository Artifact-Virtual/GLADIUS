# Quick Start Guide

> Get up and running with the Gladius research repository

This guide will help you navigate the repository and get started with the projects and documentation.

---

## 📚 First Steps

### 1. Understand the Repository Structure

```
gladius/
├── README.md              ← Start here!
├── docs/                  ← License and official documentation
├── dev_docs/              ← Research articles and technical docs
│   ├── articles/          ← 60+ AI/Trading research articles
│   ├── mql5_handbook/     ← Trading strategy implementation
│   ├── research/          ← Research papers and algorithms
│   ├── virtual_machine/   ← Infrastructure documentation
│   └── ...
├── projects/              ← Active projects (GoldMax, Cthulu, Herald)
├── dev_dir/               ← Lead developer workspace
└── working_dir/           ← Active work directory
```

### 2. Read the Main Documentation
- **[Repository README](../README.md)** - Overview of the entire repository
- **[Official Documentation](../docs/readme.md)** - Formal project documentation
- **[License](../docs/LICENSE.md)** - Proprietary license terms

### 3. Explore the Projects
- **[Projects Overview](../projects/README.md)** - All active projects
- **[GoldMax](../projects/goldmax/)** - Market analysis system
- **[Cthulu](../projects/cthulu/)** - MQL5 trading system
- **[Herald](../projects/herald/)** - Execution agent

---

## 🎯 Choose Your Path

### For AI/ML Engineers
**Goal**: Understand the AI infrastructure and model deployment

1. Start with core philosophy:
   - [The SLM-First Paradigm](dev_docs/articles/01_the_slm_first_paradigm.md)
   - [Model Deployment Best Practices](dev_docs/articles/12_local_slm_deployment_best_practices.md)

2. Learn about RAG systems:
   - [RAG for Compliance](dev_docs/articles/16_rag_for_compliance_building_audit_friend.md)
   - [Vector Database Patterns](dev_docs/articles/18_vector_database_patterns_at_scale_hnsw_p.md)

3. Explore research:
   - [Vector Space Theory](dev_docs/research/vector_space_theory.md)
   - [HNSW Algorithm](dev_docs/research/hnsw_algorithm.md)

### For Trading System Developers
**Goal**: Build and deploy trading strategies

1. Learn the platform:
   - [MQL5 Handbook](dev_docs/mql5_handbook/README.md)
   - [Strategy Examples](dev_docs/mql5_handbook/phase3/articles/)

2. Understand the system:
   - [GoldMax System](projects/goldmax/) - Market analysis
   - [Herald Agent](projects/herald/) - Execution
   - [Cthulu Platform](projects/cthulu/) - MQL5 implementation

3. Study execution:
   - [Introducing Herald](dev_docs/articles/26_introducing_herald_design_and_safety_for.md)
   - [Exchange Integration](dev_docs/articles/27_exchange_integration_patterns_safe_order.md)

### For Infrastructure Engineers
**Goal**: Deploy and maintain the systems

1. Infrastructure setup:
   - [Virtual Machine Documentation](dev_docs/virtual_machine/)
   - [SSH Setup Guide](dev_docs/virtual_machine/ssh_setup_guide.md)
   - [VM Access](dev_docs/virtual_machine/vm_access.md)

2. Deployment:
   - [GCP Startup Scripts](dev_docs/scripts/)
   - [Architecture Documentation](dev_docs/docs/architectural_mandate.md)

3. Monitoring:
   - [Observability](dev_docs/articles/31_metrics_that_matter_agent_specific_obser.md)
   - [Alerting & Runbooks](dev_docs/articles/32_alerting_and_runbooks_for_autonomous_age.md)

### For Compliance/Legal
**Goal**: Understand regulatory requirements

1. Compliance framework:
   - [EU AI Act Application](dev_docs/articles/36_applying_the_eu_ai_act_to_agentic_tradin.md)
   - [SEC Considerations](dev_docs/articles/37_sec_considerations_human_oversight_and_a.md)

2. Auditing:
   - [Auditing AI Output](dev_docs/articles/38_auditing_ai_output_traceability_explaina.md)
   - [Logging & Traceability](dev_docs/articles/33_logging_traceability_and_audit_logs_for_.md)

3. Security:
   - [Threat Modeling](dev_docs/articles/43_threat_modeling_for_agentic_systems.md)
   - [Privacy & Data Sovereignty](dev_docs/articles/39_privacy_and_data_sovereignty_air_gapped_.md)

### For Researchers
**Goal**: Build on existing research

1. Read the research materials:
   - [Research Directory](dev_docs/research/)
   - [Research Papers](dev_docs/research/papers/)
   - [Technical Articles](dev_docs/articles/)

2. Understand the systems:
   - [GoldMax Architecture](projects/goldmax/Architecture.md)
   - [System Design Articles](dev_docs/articles/README.md)

3. Explore the theory:
   - [Vector Space Theory](dev_docs/research/vector_space_theory.md)
   - [HNSW Algorithm](dev_docs/research/hnsw_algorithm.md)

---

## 🚀 Common Tasks

### Access the VM
```bash
# Follow the SSH setup guide first
# See: dev_docs/virtual_machine/ssh_setup_guide.md

# Then connect
ssh username@34.171.231.16

# Access Windows desktop
# Navigate to: http://34.171.231.16:8006

# Access VS Code Server
# Navigate to: http://34.171.231.16:8443
```

### Read Research Articles
All 60+ articles are in [`dev_docs/articles/`](dev_docs/articles/):
- [Article Index](dev_docs/articles/00_article_index.md) - Complete listing
- [Articles README](dev_docs/articles/README.md) - Organized by category

### Deploy a Project
1. Review project documentation:
   - [Projects Overview](projects/README.md)
   - Specific project README (GoldMax, Cthulu, or Herald)

2. Follow setup instructions in project directory

3. Use deployment scripts in [`dev_docs/scripts/`](dev_docs/scripts/)

### Explore Trading Strategies
1. Start with the [MQL5 Handbook](dev_docs/mql5_handbook/README.md)
2. Browse strategies by phase:
   - [Phase 1](dev_docs/mql5_handbook/phase1/) - Foundations
   - [Phase 2](dev_docs/mql5_handbook/phase2/) - Risk management
   - [Phase 3](dev_docs/mql5_handbook/phase3/) - Advanced strategies

---

## 📖 Documentation Navigation

### Main Indexes
- **[Documentation Index](dev_docs/SUMMARY.md)** - Complete table of contents
- **[Article Index](dev_docs/articles/00_article_index.md)** - All research articles
- **[MQL5 Manifest](dev_docs/mql5_handbook/manifest.md)** - Trading strategies catalog

### By Topic
- **AI/ML**: [Articles](dev_docs/articles/), [Research](dev_docs/research/)
- **Trading**: [MQL5 Handbook](dev_docs/mql5_handbook/), [Projects](projects/)
- **Infrastructure**: [Virtual Machine](dev_docs/virtual_machine/), [Scripts](dev_docs/scripts/)
- **Compliance**: Articles 36-40 in [Articles](dev_docs/articles/)
- **Security**: Articles 41-45 in [Articles](dev_docs/articles/)

---

## 🔑 Key Concepts

### GoldMax System
A continuous market analysis system that:
- Runs unattended on a VM
- Generates 6 charts per run
- Produces written market reports
- Archives everything to Notion
- Does NOT make predictions

**Learn more**: [GoldMax Broadcast](dev_docs/broadcast.md)

### Herald Agent
Execution agent that:
- Makes trading decisions based on GoldMax
- Focuses on BTCUSD (currently)
- Includes safety mechanisms
- Logs all operations

**Learn more**: [Herald Project](projects/herald/)

### Cthulu Platform
MQL5/MetaTrader 5 system that:
- Executes trades via MT5
- Runs on GCP VM
- Integrates with Herald

**Learn more**: [Cthulu Project](projects/cthulu/)

---

## 🛠️ Tools & Scripts

### Deployment Scripts
Located in [`dev_docs/scripts/`](dev_docs/scripts/):
- `configure_gh_global.ps1` - Git/GitHub setup
- `gcp_startup_*.sh` - GCP VM startup
- `mt5_automate.sh` - MT5 automation
- `desktop_launch_herald_and_mt5.ps1` - Launch trading system

### Configuration
- VM credentials: [`dev_docs/virtual_machine/DEV_SECRETS.md`](dev_docs/virtual_machine/DEV_SECRETS.md)
- Access guide: [`dev_docs/virtual_machine/vm_access.md`](dev_docs/virtual_machine/vm_access.md)

---

## ⚠️ Important Notes

### Security
- This is a **private repository** with restricted access
- Never commit credentials to Git
- Use SSH keys for VM access
- Store secrets in DEV_SECRETS.md (not in Git)

### Development
- Follow the repository's development practices
- Test in simulation before live deployment
- Maintain comprehensive logging
- Document all changes

### Compliance
- Not financial advice
- Use at your own risk
- Ensure regulatory compliance
- Maintain human oversight

---

## 📞 Getting Help

### Documentation
- Check the [Documentation Index](dev_docs/SUMMARY.md)
- Search the [Article Index](dev_docs/articles/00_article_index.md)
- Review project-specific READMEs

### Issues
- Contact: [`amuzetnoM`](https://github.com/amuzetnoM)
- Repository owner for access and permissions

---

## 🎓 Learning Path

### Week 1: Orientation
- [ ] Read main README
- [ ] Explore documentation structure
- [ ] Review one project (GoldMax recommended)
- [ ] Read 3-5 foundational articles

### Week 2: Deep Dive
- [ ] Choose your focus area (AI, Trading, Infrastructure)
- [ ] Read 10-15 relevant articles
- [ ] Study related project documentation
- [ ] Experiment with tools and scripts

### Week 3: Hands-On
- [ ] Access the VM (if needed)
- [ ] Deploy a test system
- [ ] Run through examples
- [ ] Start contributing

---

## 🔄 Next Steps

After completing this quick start:
1. Choose your path from the options above
2. Read relevant documentation in depth
3. Explore code and examples
4. Start building or contributing

---

*Part of the Gladius research repository*
