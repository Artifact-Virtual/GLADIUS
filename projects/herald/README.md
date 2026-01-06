# Herald Execution Agent

> Automated trading execution agent under development

---

## 📁 Project Structure

### Configuration
- **[config/wizard.py](config/wizard.py)** - Configuration wizard for Herald setup

---

## 🎯 Project Overview

Herald is the execution agent component of the GoldMax trading system, responsible for automated trade execution based on market analysis.

### Current Status
🚧 **In Development** 🚧

### Training Focus
- **Primary Asset**: BTCUSD (Bitcoin/USD)
- **Purpose**: Automated execution based on GoldMax analysis
- **Deployment**: VM or executor container

---

## 🏗️ Architecture

### Integration with GoldMax
Herald works in coordination with the GoldMax market analysis system:

```
GoldMax (Analysis) → Herald (Execution) → Exchange/Broker
```

1. **GoldMax** provides market state analysis and evidence
2. **Herald** makes execution decisions based on analysis
3. **Execution** occurs through configured exchange/broker APIs

### Deployment Model
- **Primary Runtime**: Dedicated VM (same infrastructure as GoldMax)
- **Alternative**: Executor container deployment
- **State Management**: SQLite data volume on VM
- **Logging**: Persistent logs and audit trail

---

## 🔧 Configuration

### Setup Wizard
Use the configuration wizard to set up Herald:
```bash
python config/wizard.py
```

The wizard will guide you through:
- Exchange/broker API configuration
- Risk parameters
- Execution rules
- Monitoring and alerting setup

---

## 🔐 Safety & Risk Management

### Design Principles
- **Human Oversight**: Designed with human oversight requirements
- **Circuit Breakers**: Automatic stops for anomalous conditions
- **Position Limits**: Configurable maximum position sizes
- **Dry Run Mode**: Test execution without real trades

### Compliance
- Follows principles outlined in research articles:
  - [Introducing Herald](../../dev_docs/articles/26_introducing_herald_design_and_safety_for.md)
  - [Exchange Integration Patterns](../../dev_docs/articles/27_exchange_integration_patterns_safe_order.md)
  - [Testing Execution Agents](../../dev_docs/articles/28_testing_execution_agents_simulation_repl.md)

---

## 📚 Related Documentation

### Research Articles
- [Introducing Herald: Design and Safety](../../dev_docs/articles/26_introducing_herald_design_and_safety_for.md)
- [Exchange Integration Patterns](../../dev_docs/articles/27_exchange_integration_patterns_safe_order.md)
- [Testing Execution Agents](../../dev_docs/articles/28_testing_execution_agents_simulation_repl.md)
- [Training and Evaluating Execution Models](../../dev_docs/articles/29_training_and_evaluating_execution_models.md)
- [Operational Playbook for Live Execution](../../dev_docs/articles/30_operational_playbook_for_live_execution_.md)

### System Integration
- [GoldMax Project](../goldmax/README.md) - Market analysis system
- [Cthulu System](../cthulu/README.md) - MQL5/MT5 integration
- [Broadcast Documentation](../../dev_docs/broadcast.md) - Complete system overview

---

## 🛠️ Development

### Scripts & Utilities
Relevant scripts for Herald development:
- `run_herald_wizard_foreground.ps1` - Run configuration wizard
- `desktop_launch_herald_and_mt5.ps1` - Launch Herald with MT5
- `integration_run_dry.ps1` - Dry run integration test

### Testing
- **Simulation Mode**: Test execution without real trades
- **Replay Testing**: Test against historical data
- **Integration Tests**: Verify GoldMax → Herald → Exchange flow

---

## 🚀 Roadmap

### Current Phase: Development
- [ ] Complete BTCUSD training and validation
- [ ] Improve SLM inference latency
- [ ] Formalize execution rules and risk parameters
- [ ] Implement comprehensive logging and monitoring

### Future Enhancements
- [ ] Multi-asset support
- [ ] Advanced execution algorithms (TWAP, VWAP, etc.)
- [ ] Enhanced risk management features
- [ ] Real-time performance analytics

---

## ⚠️ Disclaimer

**This is experimental software for research purposes.**

- Not financial advice
- Use at your own risk
- Thoroughly test in simulation before any live deployment
- Ensure compliance with all applicable regulations
- Maintain appropriate human oversight

---

## 📞 Contact

For questions or contributions, contact: [`amuzetnoM`](https://github.com/amuzetnoM)

---

*Part of the Gladius research repository*
