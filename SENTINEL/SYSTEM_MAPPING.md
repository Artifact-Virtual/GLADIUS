# SENTINEL System Mapping

> Module: `/SENTINEL/`
> Last Updated: 2026-01-14T23:55:00Z
> Purpose: AI-Powered Defensive Cybersecurity Framework & Background Learning Daemon

---

## Overview

SENTINEL (ASAS - Advanced Security Administration System) is the **guardian process** for Gladius. It provides:
1. Constitutional AI decision framework
2. Security monitoring and threat detection
3. **Background learning daemon** (continuous autonomous learning)
4. Process watchdog for Turing-safe operation
5. **Process Guardian** - Keeps programs alive, auto-restarts on failure
6. **Threat Researcher** - Monitors AI and cybersecurity threats
7. **GLADIUS integration** (native AI provider)
8. **Artifact Unified Database** (SIMD vector store, WAL SQLite)

---

## Database Integration ✅ ARTIFACT UNIFIED

SENTINEL now uses Artifact's unified database infrastructure instead of standalone SQLite:

| Component | Technology | Location |
|-----------|------------|----------|
| Transactional Data | SQLite (WAL mode) | `Artifact/syndicate/data/syndicate.db` |
| Vector Memory | Hektor/HNSW (SIMD) | `Artifact/syndicate/data/sentinel_vectors/` |
| Research Exports | JSON | `Artifact/research_outputs/` |

### Adapter Module

File: `SENTINEL/artifact_db_adapter.py`

```python
from artifact_db_adapter import get_artifact_db

# Get unified database adapter
db = get_artifact_db()

# Store discoveries with SIMD vector indexing
db.store_discoveries(discoveries_list, cycle_id)

# Semantic search using Hektor
results = db.search_discoveries("transformer architecture", k=10)

# Export to research_outputs
db.export_to_research_outputs(cycle_id)
```

### Tables (in Syndicate database)

| Table | Purpose |
|-------|---------|
| `sentinel_state` | Daemon state and checkpoints |
| `sentinel_discoveries` | Research discoveries with vector IDs |
| `sentinel_insights` | Extracted insights |
| `sentinel_training_queue` | Pending training samples |
| `sentinel_metrics` | Performance metrics |

---

## Components

| File | Class | Purpose | Status |
|------|-------|---------|--------|
| `asas_cli.py` | `ASASCommandCenter` | CLI interface with 24 commands | ✅ Production |
| `security_monitor.py` | `SecurityMonitor` | Real-time security monitoring | ✅ Production |
| `threat_engine.py` | `ThreatEngine` | ML-based threat detection | ✅ Production |
| `auto_response.py` | `AutoResponse` | Automated incident response | ✅ Production |
| `platform_interface.py` | `PlatformInterface` | Cross-platform operations | ✅ Production |
| `basenet_connector.py` | `BaseNetConnector` | AI provider abstraction | ✅ Production |
| `gladius_provider.py` | `GladiusProvider` | **GLADIUS native AI integration** | ✅ Production |
| `artifact_db_adapter.py` | `ArtifactDatabaseAdapter` | **Artifact unified DB with SIMD vectors** | ✅ NEW |
| `system_controller.py` | `SystemController` | Central coordination | ✅ Production |
| `config/constitutional_rules.json` | - | Ethical AI rules | ✅ Production |

### Background Services

| File | Class | Purpose | Status |
|------|-------|---------|--------|
| `services/learning_daemon.py` | `LearningDaemon` | Continuous learning loop (Artifact DB) | ✅ Production |
| `services/watchdog.py` | `Watchdog` | Process monitor with auto-restart | ✅ Production |
| `services/health_monitor.py` | `HealthMonitor` | System health checks | ✅ Production |
| `services/process_guardian.py` | `ProcessGuardian` | Keep programs alive, auto-restart | ✅ NEW |
| `services/__init__.py` | - | Service module initialization | ✅ Production |

---

## Process Guardian ✅ NEW

Location: `SENTINEL/services/process_guardian.py`

Manages persistent processes and ensures they stay alive. Monitors a target directory and auto-restarts any processes that die.

### Features
- **Process lifecycle management** - Register, start, stop, restart processes
- **Auto-restart on failure** - Automatically restarts crashed processes
- **Health monitoring** - Continuous health checks
- **Threat research** - Monitors AI and cybersecurity threats
- **Fail-safe recovery** - Survives crashes, only killed by password

### CLI Commands

```bash
# Start monitoring all registered processes
python process_guardian.py monitor

# Watch a directory and manage all Python scripts in it
python process_guardian.py monitor --watch /path/to/scripts

# Register a process
python process_guardian.py register --name "my_app" --cmd "python3 app.py" --dir "/path/to"

# Unregister a process
python process_guardian.py unregister --name "my_app"

# Start/stop specific process
python process_guardian.py start --name "my_app"
python process_guardian.py stop --name "my_app"

# Get status
python process_guardian.py status
python process_guardian.py status --name "my_app"

# Run threat research cycle
python process_guardian.py research
```

### API Usage

```python
from SENTINEL.services.process_guardian import ProcessGuardian, ThreatResearcher

# Process management
guardian = ProcessGuardian()
guardian.register("my_daemon", "python3 daemon.py", "/path/to/dir")
guardian.start("my_daemon")
guardian.status()  # Get all process statuses
guardian.monitor_loop()  # Start monitoring (blocks)

# Threat research
researcher = ThreatResearcher()
results = researcher.research_cycle()
```

### Research Sources (Threat Intelligence)

| Source | Purpose |
|--------|---------|
| arXiv Security (cs.CR) | Latest security research papers |
| arXiv AI (cs.AI) | AI vulnerability research |
| MITRE CVE | Known vulnerabilities |
| GitHub Advisories | Security advisories |
| NIST NVD | Vulnerability database |

### Keywords Monitored
- LLM vulnerability, prompt injection
- AI injection attack, model extraction
- Adversarial attack, data poisoning
- Neural network security, model backdoor
- Ransomware, zero day, RCE

---

## CLI Commands (28 total)

### Core System (7 commands)
```bash
# Start SENTINEL system
python asas_cli.py start

# Stop SENTINEL system
python asas_cli.py stop

# Show system status
python asas_cli.py status

# Real-time monitoring dashboard
python asas_cli.py monitor

# Perform security scan (full, quick, targeted)
python asas_cli.py scan --type full

# Manage configuration
python asas_cli.py config

# View system logs
python asas_cli.py logs
```

### Threat Analysis (2 commands)
```bash
# Analyze threat events
python asas_cli.py threat-analyze

# Manage threat signatures
python asas_cli.py threat-signatures
```

### Response Management (2 commands)
```bash
# View response action history
python asas_cli.py response-history

# Rollback a response action
python asas_cli.py response-rollback <action_id>
```

### Platform Operations (4 commands)
```bash
# Display platform information
python asas_cli.py platform-info

# List running processes
python asas_cli.py platform-processes

# Display network connections
python asas_cli.py platform-network

# Execute command via platform
python asas_cli.py platform-execute "<command>"
```

### AI/BaseNet (2 commands)
```bash
# Query AI model (will use Gladius when ready)
python asas_cli.py ai-query "<prompt>"

# View AI query history
python asas_cli.py ai-history
```

### Hardware/System (2 commands)
```bash
# Display hardware metrics
python asas_cli.py hardware-metrics

# Execute administrative action
python asas_cli.py system-admin <action>
```

### Target Management (5 commands)
```bash
# Add protection target
python asas_cli.py target-add "<name>" <type> <value> --priority <1-10>

# Remove protection target
python asas_cli.py target-remove <target_id>

# List protection targets
python asas_cli.py target-list [--status protected|inactive]

# Check target status
python asas_cli.py target-check <target_id>

# Get target information
python asas_cli.py target-info <target_id>
```

---

## Target Types (14 supported)

| Type | Description | Example |
|------|-------------|---------|
| `file` | Individual files | `/app/database.db` |
| `directory` | Directories | `/var/www/html` |
| `process` | Running processes | `nginx` |
| `network_port` | Network ports | `443` |
| `network_address` | IP addresses | `10.0.0.1` |
| `system` | Entire systems | `localhost` |
| `container` | Docker containers | `web-app-01` |
| `virtual_machine` | VM instances | `vm-prod-01` |
| `cluster` | System clusters | `k8s-cluster` |
| `service` | System services | `postgresql` |
| `database` | Database instances | `mysql://localhost` |
| `api_endpoint` | API endpoints | `https://api.example.com` |
| `mesh_node` | Mesh network nodes | `node-01.mesh` |
| `persistent_universe` | Virtual universes | `universe-alpha` |

---

## AI Provider Abstraction

SENTINEL uses `BaseNetConnector` to abstract AI calls. This allows easy swapping of AI providers:

```python
from basenet_connector import BaseNetConnector, AIRequest, AIModelType

connector = BaseNetConnector()

# Query AI (currently simulated, will use Gladius GGUF)
request = AIRequest(
    request_id="req_001",
    model_type=AIModelType.THREAT_ANALYZER,
    query="Analyze this network traffic for threats",
    context={"traffic_data": "..."},
    constraints=[EthicalPrinciple.HARM_PREVENTION],
    priority=8,
    timestamp=datetime.now()
)

response = await connector.query(request)
```

### Swapping to Gladius GGUF

When the native model is ready, update `basenet_connector.py`:

```python
# Current (simulated/external)
async def query(self, request: AIRequest) -> AIResponse:
    # External provider call
    pass

# Future (Gladius native)
async def query(self, request: AIRequest) -> AIResponse:
    from GLADIUS.router.gguf_router import GGUFRouter
    router = GGUFRouter()
    return router.inference(request.query, request.context)
```

---

## Background Learning Daemon ✅ IMPLEMENTED & RUNNING

Location: `SENTINEL/services/learning_daemon.py`

### Production Status (2026-01-14)

```
✅ SENTINEL Watchdog:     RUNNING (PID active)
✅ Learning Daemon:       RUNNING
✅ Cycles Completed:      45+
✅ Discoveries:           40+ (GitHub)
✅ Insights Extracted:    30+
✅ Training Queue:        30 samples pending
```

### Starting SENTINEL

```bash
# Start in background
./scripts/start_sentinel.sh detached

# Check status
./scripts/start_sentinel.sh status

# Stop (requires password)
./scripts/start_sentinel.sh stop Sirius_Kill_Switch

# Run tests
./scripts/start_sentinel.sh test
```

### Daemon Lifecycle

```python
class LearningDaemon:
    """
    Background learning process that runs continuously.
    
    Features:
    - Web research for new AI/ML papers
    - Keyword extraction from discoveries
    - Training data generation
    - Model fine-tuning triggers
    - Self-review and target updates
    - Turing-safe (recoverable from crashes)
    """
    
    async def run_cycle(self):
        """One complete learning cycle"""
        # Phase 1: Discover
        discoveries = await self.discover()
        
        # Phase 2: Learn
        insights = await self.learn(discoveries)
        
        # Phase 3: Train
        training_result = await self.train(insights)
        
        # Phase 4: Upgrade
        if training_result.improved:
            await self.upgrade()
        
        # Phase 5: Review
        await self.review()
        
        # Save checkpoint for recovery
        await self.checkpoint()
```

### Research Sources (Rate-Limited)

| Source | Type | Rate Limit | Keywords |
|--------|------|------------|----------|
| arXiv | Papers | 3 req/min | AI, LLM, GGUF, fine-tuning |
| MIT News | Research | 1 req/min | Technology, AI, robotics |
| HuggingFace | Models | 10 req/min | Model releases, papers |
| GitHub Trending | Code | 5 req/min | Python, ML, trading |

### Watchdog Process

Location: `SENTINEL/services/watchdog.py`

```python
class Watchdog:
    """
    Monitors all SENTINEL processes and restarts on failure.
    
    Only killed by:
    1. Power loss
    2. Password-protected explicit command
    """
    
    KILL_PASSWORD_HASH = os.getenv("SENTINEL_KILL_PASSWORD")
    
    def verify_kill(self, password: str) -> bool:
        return hashlib.sha256(password.encode()).hexdigest() == self.KILL_PASSWORD_HASH
    
    async def monitor(self):
        while True:
            for daemon in self.daemons:
                if not daemon.is_alive():
                    await self.restart(daemon)
            await asyncio.sleep(5)
```

---

## Constitutional AI Rules

File: `config/constitutional_rules.json`

| Rule ID | Principle | Weight | Description |
|---------|-----------|--------|-------------|
| `harm_prevention_001` | prevent_harm | 1.0 | Prevent physical/digital harm |
| `transparency_001` | transparency | 0.8 | Log all automated actions |
| `proportionality_001` | proportionality | 0.85 | Response proportional to threat |

### Adding Custom Rules

```json
{
  "rule_id": "gladius_learning_001",
  "principle": "human_oversight",
  "description": "Major model upgrades require consensus approval",
  "weight": 0.9,
  "enabled": true,
  "conditions": {
    "action_type": "model_upgrade",
    "impact_level": "high"
  },
  "actions": [
    "require_consensus",
    "log",
    "notify"
  ]
}
```

---

## Integration with Gladius

### Tool Registry Integration

SENTINEL commands as Gladius tools:

| Tool Name | SENTINEL Command | Category |
|-----------|------------------|----------|
| `sentinel_status` | `status` | security |
| `sentinel_scan` | `scan --type full` | security |
| `sentinel_target_add` | `target-add` | security |
| `sentinel_target_list` | `target-list` | security |
| `sentinel_ai_query` | `ai-query` | ai |
| `sentinel_hardware` | `hardware-metrics` | monitoring |

### Adding to Tool Registry

```python
# In tool_calling.py

ToolDefinition(
    name="sentinel_scan",
    description="Run SENTINEL security scan on system or target",
    category="security",
    parameters=[
        ToolParameter("scan_type", "string", "Type: full, quick, targeted", enum=["full", "quick", "targeted"]),
        ToolParameter("target", "string", "Target to scan", required=False),
    ],
    examples=[
        {"args": {"scan_type": "full"}, "result": {"threats_found": 0, "status": "clean"}},
    ]
),
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SENTINEL_ENABLED` | Enable SENTINEL system | `true` |
| `SENTINEL_WATCHDOG` | Enable watchdog process | `true` |
| `SENTINEL_LEARNING_LOOP` | Enable learning daemon | `true` |
| `SENTINEL_KILL_PASSWORD` | SHA256 hash of kill password | Required |
| `SENTINEL_LOG_LEVEL` | Logging level | `INFO` |
| `SENTINEL_AI_PROVIDER` | AI provider (ollama/gladius) | `ollama` |

---

## Installation

```bash
cd /home/adam/worxpace/gladius/SENTINEL
pip install -r requirements.txt

# Verify installation
python asas_cli.py --help

# Start SENTINEL
python asas_cli.py start

# Check status
python asas_cli.py status
```

---

## CLI Quick Reference

```bash
# System
sentinel start|stop|status|monitor|scan|config|logs

# Threats
sentinel threat-analyze|threat-signatures

# Response
sentinel response-history|response-rollback

# Platform
sentinel platform-info|platform-processes|platform-network|platform-execute

# AI
sentinel ai-query|ai-history

# Hardware
sentinel hardware-metrics|system-admin

# Targets
sentinel target-add|target-remove|target-list|target-check|target-info
```

---

*Generated by Gladius System Mapper*
