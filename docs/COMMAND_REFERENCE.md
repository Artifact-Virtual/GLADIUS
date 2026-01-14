# GLADIUS UNIFIED COMMAND REFERENCE

> **Generated**: 2026-01-14T17:45:00Z
> **Purpose**: Complete command reference for all Gladius subsystems

---

## Master Control

All commands are accessed via the master script with namespace prefixes:

```bash
./gladius.sh <system> <command> [args]
```

| System | Purpose | Commands |
|--------|---------|----------|
| `gladius` | Native AI Model | train, benchmark, status, deploy |
| `sentinel` | Guardian/Security | start, stop, scan, target, ai-query |
| `legion` | Agent Ecosystem | system, agent, message, operation |
| `artifact` | Enterprise Ops | syndicate, publish, research, automata |

---

## GLADIUS (Native AI Model)

Namespace: `./gladius.sh gladius <command>`

### Model Operations
```bash
# Check model status
./gladius.sh gladius status

# Run benchmark
./gladius.sh gladius benchmark [--cycles N]

# Start training
./gladius.sh gladius train [--data PATH]

# Deploy new model
./gladius.sh gladius deploy [--version VERSION]

# Rollback model
./gladius.sh gladius rollback [--to VERSION]
```

### Tool Router
```bash
# Test tool routing
./gladius.sh gladius route "<query>"

# List available tools
./gladius.sh gladius tools [--category CAT]

# Export tool schemas
./gladius.sh gladius export-tools [--format json|openai]
```

### Cognition Cycle
```bash
# Run single cognition cycle
./gladius.sh gladius cognition

# Run autonomous mode
./gladius.sh gladius autonomous [--hours N]

# Generate training data
./gladius.sh gladius generate-training
```

---

## SENTINEL (Guardian Process)

Namespace: `./gladius.sh sentinel <command>`

### Core System (7 commands)
```bash
# Start SENTINEL
./gladius.sh sentinel start

# Stop SENTINEL
./gladius.sh sentinel stop

# System status
./gladius.sh sentinel status

# Real-time monitoring
./gladius.sh sentinel monitor

# Security scan
./gladius.sh sentinel scan [--type full|quick|targeted]

# Configuration
./gladius.sh sentinel config [--show|--set KEY VALUE]

# View logs
./gladius.sh sentinel logs [--tail N]
```

### Threat Management (2 commands)
```bash
# Analyze threats
./gladius.sh sentinel threat-analyze

# Manage signatures
./gladius.sh sentinel threat-signatures [--add|--remove|--list]
```

### Response Management (2 commands)
```bash
# Response history
./gladius.sh sentinel response-history [--limit N]

# Rollback response
./gladius.sh sentinel response-rollback <action_id>
```

### Platform Operations (4 commands)
```bash
# Platform info
./gladius.sh sentinel platform-info

# List processes
./gladius.sh sentinel platform-processes

# Network connections
./gladius.sh sentinel platform-network

# Execute command
./gladius.sh sentinel platform-execute "<command>"
```

### AI Integration (2 commands)
```bash
# Query AI (uses Gladius when ready)
./gladius.sh sentinel ai-query "<prompt>"

# AI query history
./gladius.sh sentinel ai-history [--limit N]
```

### Hardware/System (2 commands)
```bash
# Hardware metrics
./gladius.sh sentinel hardware-metrics

# Admin action
./gladius.sh sentinel system-admin <action>
```

### Target Management (5 commands)
```bash
# Add target
./gladius.sh sentinel target-add "<name>" <type> <value> [--priority N]

# Remove target
./gladius.sh sentinel target-remove <target_id>

# List targets
./gladius.sh sentinel target-list [--status protected|inactive]

# Check target
./gladius.sh sentinel target-check <target_id>

# Target info
./gladius.sh sentinel target-info <target_id>
```

### Learning Daemon (NEW)
```bash
# Start learning daemon
./gladius.sh sentinel learn start

# Stop learning daemon
./gladius.sh sentinel learn stop [--password PASS]

# Learning status
./gladius.sh sentinel learn status

# Force cycle
./gladius.sh sentinel learn cycle
```

---

## LEGION (Agent Ecosystem)

Namespace: `./gladius.sh legion <command>`

### System Commands
```bash
# System status
./gladius.sh legion system status

# System health
./gladius.sh legion system health
```

### Agent Commands
```bash
# List agents
./gladius.sh legion agent list

# Agent status
./gladius.sh legion agent status <agent_id>
```

### Message Commands
```bash
# Send message
./gladius.sh legion message send --to <agent_id> --content "<msg>" [--priority N]

# Message statistics
./gladius.sh legion message stats
```

### Memory Commands
```bash
# Query memory
./gladius.sh legion memory query <agent_id> <type> [--limit N]

# Search memory
./gladius.sh legion memory search <agent_id> "<query>" [--limit N]
```

### Trace Commands
```bash
# List traces
./gladius.sh legion trace list [--limit N]

# Get trace
./gladius.sh legion trace get <trace_id>

# Trace stats
./gladius.sh legion trace stats
```

### Improvement Commands
```bash
# View insights
./gladius.sh legion improvement insights [--limit N]

# Get suggestions
./gladius.sh legion improvement suggest [--agent <id>]

# Apply improvement
./gladius.sh legion improvement apply <suggestion_id>
```

### Operation Commands
```bash
# Start continuous operation
./gladius.sh legion operation start

# Stop operation
./gladius.sh legion operation stop

# Operation status
./gladius.sh legion operation status
```

### Config Commands
```bash
# Show config
./gladius.sh legion config show [--section SECTION]

# Set config
./gladius.sh legion config set <key> <value>
```

---

## ARTIFACT (Enterprise Operations)

Namespace: `./gladius.sh artifact <command>`

### Syndicate (Market Intelligence)
```bash
# Run full analysis
./gladius.sh artifact syndicate run [--asset XAUUSD]

# Generate journal
./gladius.sh artifact syndicate journal [--date DATE]

# Generate charts
./gladius.sh artifact syndicate charts [--symbol SYMBOL]

# List syndicates
./gladius.sh artifact syndicate list

# Create new syndicate
./gladius.sh artifact syndicate create <name> --asset <SYMBOL>
```

### Publishing Pipeline
```bash
# Ingest content
./gladius.sh artifact publish ingest

# Approve content
./gladius.sh artifact publish approve <content_id>

# Schedule content
./gladius.sh artifact publish schedule <content_id> [--time TIME]

# Publish now
./gladius.sh artifact publish now <content_id> [--platforms discord,twitter]

# Test platforms
./gladius.sh artifact publish test
```

### Social Media
```bash
# Test connections
./gladius.sh artifact social test

# Post to platform
./gladius.sh artifact social post "<content>" --platform <platform>

# Get analytics
./gladius.sh artifact social analytics [--platform <platform>]
```

### ERP Integration
```bash
# Sync customers
./gladius.sh artifact erp sync customers [--system SAP|Odoo|NetSuite]

# Sync products
./gladius.sh artifact erp sync products [--system SAP]

# Sync orders
./gladius.sh artifact erp sync orders [--from DATE]

# ERP status
./gladius.sh artifact erp status
```

### Research Pipeline (NEW)
```bash
# Run research cycle
./gladius.sh artifact research run

# Fetch from arXiv
./gladius.sh artifact research arxiv [--query "<keywords>"]

# Fetch from MIT
./gladius.sh artifact research mit

# Extract keywords
./gladius.sh artifact research keywords [--from PATH]

# Research status
./gladius.sh artifact research status
```

### Consensus System
```bash
# Create proposal
./gladius.sh artifact consensus create --title "<title>" --summary "<summary>" --impact <low|medium|high|critical>

# List proposals
./gladius.sh artifact consensus list [--status open|closed]

# Vote on proposal
./gladius.sh artifact consensus vote <proposal_id> <approve|reject|abstain>

# Check results
./gladius.sh artifact consensus results <proposal_id>
```

---

## DIRECT SHORTCUTS

For convenience, common commands have shortcuts:

```bash
# Gladius shortcuts
./gladius.sh status           # → gladius status + sentinel status + legion system status
./gladius.sh health           # → All health checks
./gladius.sh benchmark N      # → gladius benchmark --cycles N
./gladius.sh autonomous       # → gladius autonomous
./gladius.sh cognition        # → gladius cognition

# Syndicate shortcuts
./gladius.sh syndicate        # → artifact syndicate run
./gladius.sh journal          # → artifact syndicate journal
./gladius.sh charts           # → artifact syndicate charts

# Publishing shortcuts
./gladius.sh publish          # → artifact publish test + ingest
./gladius.sh discord "<msg>"  # → artifact social post --platform discord

# Security shortcuts
./gladius.sh scan             # → sentinel scan --type full
./gladius.sh monitor          # → sentinel monitor
```

---

## COMMAND COUNT SUMMARY

| System | Commands | Status |
|--------|----------|--------|
| GLADIUS | 12 | ✅ |
| SENTINEL | 24 | ✅ |
| LEGION | 18 | ✅ |
| ARTIFACT | 28 | ✅ |
| Shortcuts | 12 | ✅ |
| **TOTAL** | **94** | ✅ |

---

## NO CONFLICTS

All commands are namespaced to prevent overlap:
- `gladius status` vs `sentinel status` vs `legion system status`
- `gladius train` vs `sentinel learn`
- `legion agent` vs `artifact syndicate`

---

## ENVIRONMENT VARIABLES

All systems share the unified `.env` file:

```bash
# System enables
GLADIUS_ENABLED=true
SENTINEL_ENABLED=true
LEGION_ENABLED=true
ARTIFACT_ENABLED=true

# Paths
GLADIUS_MODEL_PATH=./GLADIUS/models/production
SENTINEL_CONFIG=./SENTINEL/config
LEGION_DB_PATH=./LEGION/data
ARTIFACT_ROOT=./Artifact

# API Keys (existing)
# ... all existing .env variables ...
```

---

*Generated by Gladius System Mapper*
