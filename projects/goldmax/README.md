# GoldMax Project

> **A System That Refuses to Lie**

A continuous, evidence-driven market memory system that records and preserves market state for disciplined decision-making.

---

## 📁 Project Files

### Core Documentation
- **[Broadcast.md](broadcast.md)** - Complete system overview and philosophy (main documentation)
- **[Architecture.md](projects/goldmax/Architecture.md)** - System architecture and technical design
- **[Blueprint.md](projects/goldmax/Blueprint.md)** - Implementation blueprint
- **[Foundation.md](projects/goldmax/Foundation.md)** - Foundation principles
- **[Thesis.md](projects/goldmax/Thesis.md)** - Core thesis and approach

### Research & Articles
- **[argmax-syndrome_article.md](projects/goldmax/argmax-syndrome_article.md)** - Research on decision-making patterns

### Assets
- System diagrams and visualizations

---

## 🎯 Project Overview

**One-line summary:** A continuous, evidence-driven market memory that records and preserves market state for disciplined decision-making.

⚠️ **Disclaimer:** Not financial advice. This documentation explains system behavior and is not investment guidance.

---

## ✨ Key Features

- ✅ Runs unattended on a dedicated VM; stores every run permanently in Notion and on disk
- 📊 Produces six reproducible charts and a concise written report each run
- 🔍 Provides deterministic evidence for human review; does not make trading calls
- 🤖 Integrates with `Herald`, the execution agent under development; VM is the canonical runtime

---

## 🏗️ Architecture

### VM Infrastructure
- **Platform**: Dedicated Virtual Machine (persistent, stateful)
- **Runtime**: Unattended, automated execution
- **Storage**: SQLite data volume, persistent artifacts
- **Integration**: Notion sync, optional Herald executor

### Pipeline Flow
```
Ingest → Normalize → Analyze → Chart → Report → Archive
```

Each run follows deterministic steps:
1. Pull market data
2. Normalize and structure it
3. Analyze price behavior (not predictions)
4. Generate charts (6 per run)
5. Generate written reports
6. Store everything permanently in Notion

---

## 📊 Outputs

### Six Charts (Every Run)
1. **Price Structure** - Local bands and structural levels
2. **Volatility** - Observed volatility over time
3. **Range/Expansion** - Rolling range indicating expansion vs contraction
4. **Multi-timeframe Context** - Structural context across timeframes
5. **Risk Profile** - Returns distribution and risk assessment
6. **Comparative Behavior** - Asset behavior snapshots

### Written Reports
Descriptions of market state:
- What changed
- What didn't
- What matters now
- What is fragile
- What is stable

Reports are intentionally boring and evidence-based, not predictive or opinion-based.

---

## 🔄 Integration with Herald

**Herald** is the execution agent under development:
- **Training**: Focused on BTCUSD
- **Deployment**: From VM or executor container
- **Purpose**: Automated trading execution based on GoldMax analysis
- **Status**: In development

---

## 📚 Documentation

For complete system documentation, philosophy, and implementation details, see:
- **[dev_docs/broadcast.md](broadcast.md)** - Main GoldMax documentation

---

## 🎓 Design Principles

1. **Unattended Operation**: System runs whether anyone is watching or not
2. **No Selective Attention**: Automation removes emotional filtering
3. **Evidence Over Narrative**: Charts and reports are evidence, not decoration
4. **Persistent Memory**: Nothing is overwritten; every run is preserved
5. **No Predictions**: System describes state, doesn't predict outcomes

---

## 🔒 Purpose

Gold Standard exists to **remember**, not to predict.

It was designed to:
- Preserve reality without bias
- Remove dependency on human attention
- Create auditable, reproducible market observations
- Provide structure for disciplined decision-making

---

## 📞 Contact

For questions or contributions, contact the repository owner: [`amuzetnoM`](https://github.com/amuzetnoM)

---

*Part of the Gladius research repository*
