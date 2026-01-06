# Gladius

> **Personal AI Research & Trading Systems Development Repository**

A private research workspace for autonomous agent development, trading systems research, and algorithmic trading strategy implementation. This repository serves as a comprehensive knowledge base and operational hub for AI-driven financial systems research.

---

## 🎯 Repository Purpose

Gladius is a purpose-built research environment that combines:
- AI/ML systems research and development
- Algorithmic trading strategy research
- Trading system implementation (MQL5/MetaTrader)
- Infrastructure and deployment documentation
- Personal learning and growth documentation

---

## 📁 Repository Structure

```
gladius/
├── docs/                    # Main documentation and license
├── dev_docs/               # Development documentation and research
│   ├── articles/           # AI/Trading research articles (60+ articles)
│   ├── research/           # Research papers and references
│   ├── mql5_handbook/      # MQL5 trading strategy documentation
│   ├── notes/              # Research notes and reports
│   ├── _build/             # Project build documentation (Cthulu, Herald)
│   ├── virtual_machine/    # VM infrastructure documentation
│   ├── docs/               # Technical architecture documents
│   ├── github/             # GitHub release guides
│   ├── scripts/            # Utility scripts and tools
│   └── SUMMARY.md          # Documentation index
├── dev_dir/                # Lead developer workspace
│   └── goldmax/            # GoldMax project documentation
├── working_dir/            # Active work directory
└── README.md               # This file
```

---

## 🚀 Key Projects

### 1. **GoldMax** (`dev_dir/goldmax/`)
A continuous, evidence-driven market memory system that records and preserves market state for disciplined decision-making.
- **Architecture**: VM-based automated analysis pipeline
- **Output**: Daily charts, reports, and Notion journal entries
- **Status**: Active development
- See: [`dev_docs/broadcast.md`](dev_docs/broadcast.md) for detailed system overview

### 2. **Cthulu** (`dev_docs/_build/cthulu/`)
Trading system implementation and GCP VM deployment
- **Platform**: MQL5/MetaTrader 5
- **Infrastructure**: GCP n2-standard-2 instance
- **Status**: Build documentation and deployment guides available

### 3. **Herald** (`dev_docs/_build/herald/`)
Execution agent under development for automated trading
- **Training**: BTCUSD focused
- **Integration**: Works with GoldMax system
- **Status**: In development

---

## 📚 Documentation Index

### Research Articles (`dev_docs/articles/`)
60+ articles covering:
- **SLM-First Paradigm**: Local small language models for efficient AI systems
- **Agentic Systems**: Design patterns for autonomous trading agents
- **RAG & Embeddings**: Retrieval-augmented generation for financial compliance
- **Production Systems**: From research to production deployment
- **Security & Compliance**: EU AI Act, SEC considerations, audit requirements
- **Infrastructure**: VM hardening, CI/CD, model deployment

See [`dev_docs/articles/00_article_index.md`](dev_docs/articles/00_article_index.md) for complete list.

### MQL5 Handbook (`dev_docs/mql5_handbook/`)
Comprehensive trading strategy development documentation:
- **Phase 1**: Foundation articles on strategy implementation
- **Phase 2**: Risk management and trading system development
- **Phase 3**: Advanced strategies (ORB, linear regression, price action)

See [`dev_docs/mql5_handbook/README.md`](dev_docs/mql5_handbook/README.md) for details.

### Research Materials (`dev_docs/research/`)
Technical research papers and references:
- Vector space theory and HNSW algorithms
- Research paper archive
- Reference materials

---

## 🔒 Access & Security

**This is a private, access-controlled repository.**

- Repository owner: [`amuzetnoM`](https://github.com/amuzetnoM)
- Access requires explicit authorization
- All changes tracked and auditable
- See [`docs/LICENSE.md`](docs/LICENSE.md) for complete license terms

### Protected Workspaces
- `dev_dir/`: Lead Developer workspace with strict access controls
- `working_dir/`: Active development area

---

## 🛠️ Development Setup

### Infrastructure Documentation
- **VM Setup**: See [`dev_docs/virtual_machine/`](dev_docs/virtual_machine/) for GCP VM configuration
- **SSH Access**: [`dev_docs/virtual_machine/ssh_setup_guide.md`](dev_docs/virtual_machine/ssh_setup_guide.md)
- **Scripts**: Utility scripts in [`dev_docs/scripts/`](dev_docs/scripts/)

### Git Configuration
Use the PowerShell helper for machine-level Git/GH authentication:
```powershell
.\dev_docs\scripts\configure_gh_global.ps1
```

---

## 📖 Getting Started

1. **Start with the main documentation**: [`docs/readme.md`](docs/readme.md)
2. **Explore research articles**: [`dev_docs/articles/00_article_index.md`](dev_docs/articles/00_article_index.md)
3. **Review system architecture**: [`dev_docs/docs/architectural_mandate.md`](dev_docs/docs/architectural_mandate.md)
4. **Check project documentation**: 
   - GoldMax: [`dev_docs/broadcast.md`](dev_docs/broadcast.md)
   - MQL5: [`dev_docs/mql5_handbook/README.md`](dev_docs/mql5_handbook/README.md)

---

## 🎓 Research Areas

This repository covers research in:
- **AI/ML Systems**: SLM deployment, model orchestration, agentic workflows
- **Trading Systems**: Algorithmic strategies, risk management, execution systems
- **Infrastructure**: VM deployment, container orchestration, CI/CD
- **Compliance**: Financial regulations, audit requirements, responsible AI
- **Data Engineering**: Market data pipelines, normalization, analysis

---

## 📝 Contributing & AI Policy

This is a **private research repository**. Contributions are by invitation only and limited to authorized collaborators. All changes must be reviewed and approved by the Lead Developer before merging.

### AI Collaboration
- Autonomous agents may operate within designated areas
- All AI-generated content requires explicit attestation and provenance
- Strong separation between AI-operated areas and Lead Developer private spaces

---

## 📞 Contact

- **Lead Developer**: [`amuzetnoM`](https://github.com/amuzetnoM)
- **Repository Status**: Private Research Repository
- **License**: All Rights Reserved — Proprietary License (see [`docs/LICENSE.md`](docs/LICENSE.md))

---

*Designed for secure, auditable, machine-first research.*
