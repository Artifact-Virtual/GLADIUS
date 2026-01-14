# GLADIUS ENTERPRISE SYSTEM - MASTER DOCUMENTATION

> **Version**: 1.0.0  
> **Last Updated**: 2026-01-14  
> **Author**: Artifact Virtual Systems

---

## TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Component Reference](#component-reference)
4. [GLADIUS - Native AI Model](#gladius---native-ai-model)
5. [SENTINEL - Guardian Process](#sentinel---guardian-process)
6. [LEGION - Agent Ecosystem](#legion---agent-ecosystem)
7. [ARTIFACT - Enterprise Infrastructure](#artifact---enterprise-infrastructure)
8. [Integration Matrix](#integration-matrix)
9. [Command Reference](#command-reference)
10. [Configuration](#configuration)
11. [Deployment Guide](#deployment-guide)

---

## SYSTEM OVERVIEW

### Core Philosophy

| Entity | Role | Description |
|--------|------|-------------|
| **GLADIUS** | The Brain | Native AI model that powers all intelligent operations |
| **ARTIFACT VIRTUAL** | The Body | Enterprise infrastructure (social, ERP, research, publishing) |
| **SENTINEL** | The Guardian | Security, learning daemon, process watchdog |
| **LEGION** | The Workforce | 26 specialized AI agents for enterprise operations |

### Recursive Self-Improvement

```
GLADIUS uses ARTIFACT → ARTIFACT improves GLADIUS → GLADIUS improves ARTIFACT
                    ↑                                              ↓
                    └──────────────── CONTINUOUS LOOP ─────────────┘
```

---

## ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ARTIFACT VIRTUAL                                 │
│                     (Enterprise Infrastructure)                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        GLADIUS                                   │   │
│  │                   (Native AI - The Brain)                        │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │   │
│  │  │ Cognition│ │  Memory  │ │  Router  │ │  Model   │           │   │
│  │  │  Engine  │ │  Module  │ │  (GGUF)  │ │ Trainer  │           │   │
│  │  │  37+ tools│ │  VDB     │ │  <2ms   │ │  LoRA    │           │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│         ┌────────────────────┼────────────────────┐                    │
│         ▼                    ▼                    ▼                    │
│  ┌────────────┐       ┌────────────┐       ┌────────────┐              │
│  │  SENTINEL  │       │   LEGION   │       │  SYNDICATE │              │
│  │ (Guardian) │       │  (Agents)  │       │ (Research) │              │
│  └────────────┘       └────────────┘       └────────────┘              │
│         │                    │                    │                    │
│         └────────────────────┼────────────────────┘                    │
│                              ▼                                          │
│                       ┌────────────┐                                   │
│                       │  AUTOMATA  │                                   │
│                       │ (Publish)  │                                   │
│                       └────────────┘                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## COMPONENT REFERENCE

### Directory Structure

```
/home/adam/worxpace/gladius/
├── gladius.sh                    # Master control script
├── README.md                     # Main documentation
├── .env                          # Environment variables
│
├── GLADIUS/                      # 🧠 NATIVE AI MODEL
│   ├── __init__.py              
│   ├── SYSTEM_MAPPING.md        
│   ├── models/                   # GGUF model files
│   │   ├── production/          
│   │   ├── staging/             
│   │   └── base/                
│   ├── training/                 
│   │   ├── data/                
│   │   ├── harness.py           
│   │   └── generator.py         
│   ├── router/                   
│   │   ├── pattern_router.py    # 100% accuracy, <2ms
│   │   └── __init__.py          
│   └── docs/                     
│       └── MODEL.md             
│
├── SENTINEL/                     # 🛡️ GUARDIAN PROCESS
│   ├── asas_cli.py              # Main CLI
│   ├── system_controller.py     
│   ├── security_monitor.py      
│   ├── threat_engine.py         
│   ├── auto_response.py         
│   ├── basenet_connector.py     
│   ├── gladius_provider.py      # GLADIUS integration
│   ├── platform_interface.py    
│   ├── SYSTEM_MAPPING.md        
│   ├── config/                   
│   │   └── constitutional_rules.json
│   └── services/                 # Background daemons
│       ├── __init__.py          
│       ├── learning_daemon.py   # Continuous learning
│       ├── watchdog.py          # Process monitor
│       └── config/              
│           ├── learning_config.json
│           └── watchdog_config.json
│
├── LEGION/                       # 🤖 AGENT ECOSYSTEM
│   ├── legion/                   
│   │   ├── cli.py               
│   │   ├── core_framework.py    
│   │   ├── enhanced_orchestrator.py
│   │   ├── enterprise_registry.py
│   │   ├── message_bus.py       
│   │   └── agents/              # 7 enterprise agents
│   ├── automation/              
│   ├── marketing/               
│   ├── finance/                 
│   ├── config/                  
│   └── SYSTEM_MAPPING.md        
│
├── Artifact/                     # 📦 ENTERPRISE INFRASTRUCTURE
│   ├── syndicate/               # Research Pipeline
│   │   └── src/cognition/       # GLADIUS cognition
│   │
│   ├── deployment/              # Automation Suite
│   │   └── automata/            
│   │       ├── social_media/    # Platform connectors
│   │       │   └── platforms/   
│   │       │       ├── discord_connector.py
│   │       │       ├── twitter_connector.py
│   │       │       ├── linkedin_connector.py
│   │       │       ├── facebook_connector.py
│   │       │       ├── instagram_connector.py
│   │       │       └── youtube_connector.py
│   │       ├── erp_integrations/
│   │       ├── publishing/      
│   │       └── scheduler/       
│   │
│   └── arty/                    # Autonomous Bots
│       ├── discord/             # Discord bot
│       └── linkedin/            
│
├── docs/                         # Documentation
├── scripts/                      # Utility scripts
├── logs/                         # System logs
└── data/                         # Persistent data
```

---

## GLADIUS - Native AI Model

### Purpose
GLADIUS is the native AI model that powers all intelligent operations. It provides:
- Tool routing with 100% accuracy at <2ms latency
- Task execution and planning
- Self-improvement through training
- Research analysis

### Components

| Component | File | Purpose |
|-----------|------|---------|
| Pattern Router | `router/pattern_router.py` | TF-IDF based tool selection |
| Training Harness | `training/harness.py` | Isolated model training |
| Data Generator | `training/generator.py` | Synthetic training data |
| Model Files | `models/` | GGUF production/staging models |

### Performance Metrics

| Metric | Value |
|--------|-------|
| Tool Routing Accuracy | 100% |
| Average Latency | 0.93ms |
| P99 Latency | 2.28ms |
| Training Examples | 914+ |
| Total Tools | 37+ |

### CLI Commands

```bash
./gladius.sh gladius status          # Model status
./gladius.sh gladius benchmark       # Run benchmark
./gladius.sh gladius train           # Start training
./gladius.sh gladius route "query"   # Test routing
```

---

## SENTINEL - Guardian Process

### Purpose
SENTINEL is the guardian process that ensures system security and continuous learning.

### Features
1. **Constitutional AI** - Ethical decision framework
2. **Security Monitoring** - Real-time threat detection
3. **Learning Daemon** - Continuous autonomous learning
4. **Watchdog** - Turing-safe process monitoring

### Components

| Component | File | Purpose |
|-----------|------|---------|
| Main CLI | `asas_cli.py` | 24+ CLI commands |
| Security Monitor | `security_monitor.py` | Threat detection |
| Threat Engine | `threat_engine.py` | ML-based analysis |
| Auto Response | `auto_response.py` | Automated response |
| GLADIUS Provider | `gladius_provider.py` | Native AI integration |
| Learning Daemon | `services/learning_daemon.py` | Background learning |
| Watchdog | `services/watchdog.py` | Process monitor |

### Learning Loop

```
DISCOVER → LEARN → TRAIN → UPGRADE → REVIEW → (repeat)
    │         │        │        │         │
    │         │        │        │         └── Update research targets
    │         │        │        └── Promote model if threshold met
    │         │        └── Generate training data
    │         └── Extract insights using GLADIUS
    └── Web research (arXiv, GitHub)
```

### Turing Safety

The daemon is "nuke-proof":
- **Password-protected kill**: Requires `SENTINEL_KILL_PASSWORD` environment variable
- **Auto-restart**: Watchdog automatically restarts crashed processes
- **Checkpoint system**: State saved to SQLite, recovers on restart
- **Only killed by**: Power loss OR explicit password command

### CLI Commands

```bash
# Core
./gladius.sh sentinel start
./gladius.sh sentinel stop
./gladius.sh sentinel status
./gladius.sh sentinel monitor

# Security
./gladius.sh sentinel scan
./gladius.sh sentinel alert <level>
./gladius.sh sentinel block <ip>
./gladius.sh sentinel unblock <ip>

# Learning Daemon
python SENTINEL/services/learning_daemon.py start
python SENTINEL/services/learning_daemon.py cycle
python SENTINEL/services/learning_daemon.py status

# Watchdog
python SENTINEL/services/watchdog.py start
python SENTINEL/services/watchdog.py stop --password="..."
```

### Configuration

**learning_config.json:**
```json
{
  "cycle_interval_minutes": 60,
  "research_keywords": ["GGUF", "LLM", "fine-tuning", "tool-use"],
  "auto_train_threshold": 100,
  "sources": {
    "arxiv": {"enabled": true, "categories": ["cs.AI", "cs.LG"]},
    "github": {"enabled": true, "topics": ["llm", "gguf"]}
  }
}
```

---

## LEGION - Agent Ecosystem

### Purpose
LEGION provides 26 specialized AI agents for enterprise operations.

### Core Agents

| Agent | File | Purpose |
|-------|------|---------|
| Anomaly Detection | `agents/anomaly_detection_agent.py` | Detect anomalies |
| Cloud Integration | `agents/cloud_integration_agent.py` | Cloud ops |
| CRM Integration | `agents/crm_integration_agent.py` | CRM sync |
| Customer Insights | `agents/customer_insights_agent.py` | Customer analytics |
| ERP Integration | `agents/erp_integration_agent.py` | ERP operations |
| Forecasting | `agents/forecasting_agent.py` | Predictions |
| Supply Chain | `agents/supply_chain_agent.py` | Supply chain mgmt |

### Automation Agents

| Agent | File | Purpose |
|-------|------|---------|
| Resource Optimization | `automation/resource_optimization_agent.py` | Resource mgmt |
| Task Scheduling | `automation/task_scheduling_agent.py` | Task scheduling |
| Workflow Orchestration | `automation/workflow_orchestration_agent.py` | Workflow mgmt |

### CLI Commands

```bash
./gladius.sh legion start
./gladius.sh legion stop
./gladius.sh legion status
./gladius.sh legion agents list
./gladius.sh legion agents status <name>
./gladius.sh legion orchestrate <workflow>
```

---

## ARTIFACT - Enterprise Infrastructure

### Purpose
Artifact provides the enterprise infrastructure that GLADIUS operates within.

### Subsystems

#### 1. SYNDICATE (Research Pipeline)
- Market research and analysis
- Chart generation
- Journal publishing
- Gold analysis (GOST)

#### 2. AUTOMATA (Publishing & Automation)
- Social media connectors
- ERP integrations
- Content publishing
- Smart scheduling

#### 3. ARTY (Autonomous Bots)
- Discord bot (fully configured)
- LinkedIn automation
- Data ingestion

### Social Media Integrations

| Platform | File | Status |
|----------|------|--------|
| Discord | `arty/discord/` | ✅ Configured |
| Twitter/X | `social_media/platforms/twitter_connector.py` | ✅ Ready |
| LinkedIn | `social_media/platforms/linkedin_connector.py` | ✅ Ready |
| Facebook | `social_media/platforms/facebook_connector.py` | ✅ Ready |
| Instagram | `social_media/platforms/instagram_connector.py` | ✅ Ready |
| YouTube | `social_media/platforms/youtube_connector.py` | ✅ Ready |

### ERP Integrations

| Integration | Status |
|-------------|--------|
| Customer Sync | ✅ Ready |
| Product Sync | ✅ Ready |
| Order Sync | ✅ Ready |
| Inventory Sync | ✅ Ready |

### CLI Commands

```bash
./gladius.sh artifact syndicate run
./gladius.sh artifact publish
./gladius.sh artifact social post
./gladius.sh artifact erp sync
./gladius.sh artifact scheduler start
```

---

## INTEGRATION MATRIX

### How Components Connect

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│   GLADIUS   │  SENTINEL   │   LEGION    │  ARTIFACT   │
├─────────────┼─────────────┼─────────────┼─────────────┤
│ GLADIUS     │ Provider    │ AI Backend  │ Cognition   │
│             │ (native AI) │ (routing)   │ (analysis)  │
├─────────────┼─────────────┼─────────────┼─────────────┤
│ SENTINEL    │ -           │ Security    │ Monitoring  │
│             │             │ monitoring  │ + Learning  │
├─────────────┼─────────────┼─────────────┼─────────────┤
│ LEGION      │ Uses        │ -           │ Automation  │
│             │ GLADIUS     │             │ via Automata│
├─────────────┼─────────────┼─────────────┼─────────────┤
│ ARTIFACT    │ Improves    │ Protected   │ -           │
│             │ via data    │ by SENTINEL │             │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### LEGION → ARTIFACT Integration Points

| LEGION Agent | ARTIFACT Component | Integration |
|--------------|-------------------|-------------|
| CRM Integration | ERP Integrations | Direct API calls |
| ERP Integration | ERP Integrations | Direct API calls |
| Marketing | Social Media | Uses platform connectors |
| Customer Insights | Syndicate | Research data |
| Automation | Scheduler | Task scheduling |

---

## COMMAND REFERENCE

### Master Control

```bash
./gladius.sh <namespace> <command> [options]
```

### Namespaces

| Namespace | Commands | Description |
|-----------|----------|-------------|
| `gladius` | 12 | Native AI operations |
| `sentinel` | 24 | Security & learning |
| `legion` | 18 | Agent ecosystem |
| `artifact` | 40+ | Enterprise operations |

### Full Command List

See `docs/COMMAND_REFERENCE.md` for complete list.

---

## CONFIGURATION

### Environment Variables (.env)

```bash
# GLADIUS
GLADIUS_MODEL_PATH=./GLADIUS/models/production
GLADIUS_FALLBACK_ENABLED=true

# SENTINEL
SENTINEL_KILL_PASSWORD=<sha256_hash>
SENTINEL_LOG_LEVEL=INFO

# Social Media
DISCORD_BOT_TOKEN=...
DISCORD_GUILD_ID=...
TWITTER_API_KEY=...
LINKEDIN_CLIENT_ID=...

# ERP
ERP_ENABLED=true
ERP_SYNC_INTERVAL=60

# SMTP
SMTP_HOST=...
SMTP_PORT=587
SMTP_USER=ali.shakil@artifactvirtual.com
SMTP_PASSWORD=...
```

### Service Configurations

| Config File | Purpose |
|-------------|---------|
| `SENTINEL/services/config/learning_config.json` | Learning daemon settings |
| `SENTINEL/services/config/watchdog_config.json` | Watchdog settings |
| `SENTINEL/config/constitutional_rules.json` | Ethical AI rules |
| `Artifact/deployment/automata/.env` | Automata credentials |

---

## DEPLOYMENT GUIDE

### Prerequisites

```bash
# Python 3.11+
python3 --version

# Required packages
pip install -r requirements.txt
```

### Quick Start

```bash
# 1. Configure environment
cp .env.template .env
# Edit .env with your credentials

# 2. Start SENTINEL (guardian)
./gladius.sh sentinel start

# 3. Start learning daemon
cd SENTINEL && python services/learning_daemon.py start &

# 4. Start LEGION agents
./gladius.sh legion start

# 5. Start syndicate
./gladius.sh artifact syndicate run
```

### Production Deployment

```bash
# Use watchdog for Turing-safe operation
cd SENTINEL && python services/watchdog.py start

# Set kill password (hash your password first)
export SENTINEL_KILL_PASSWORD=$(echo -n "your_password" | sha256sum | cut -d' ' -f1)
```

---

## APPENDIX

### File Counts

| Component | Files | Lines of Code |
|-----------|-------|---------------|
| GLADIUS | 12 | ~3,000 |
| SENTINEL | 15 | ~8,000 |
| LEGION | 50+ | ~15,000 |
| Artifact | 100+ | ~25,000 |

### Health Checks

```bash
# Check all components
./gladius.sh status

# Individual checks
./gladius.sh gladius health
./gladius.sh sentinel status
./gladius.sh legion status
```

---

*Generated by Gladius Documentation System*
