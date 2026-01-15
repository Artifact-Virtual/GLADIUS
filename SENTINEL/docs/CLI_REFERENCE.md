# CLI Reference

[![Commands](https://img.shields.io/badge/commands-24-blue.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-100%25-success.svg)]()

Complete reference for all SENTINEL CLI commands.

## Table of Contents

- [Core System Commands](#core-system-commands)
- [Threat Analysis Commands](#threat-analysis-commands)
- [Response Management Commands](#response-management-commands)
- [Platform Operations Commands](#platform-operations-commands)
- [AI/BaseNet Commands](#aibasenet-commands)
- [Hardware/System Commands](#hardwaresystem-commands)
- [Target Management Commands](#target-management-commands)

---

## Core System Commands

### `start` - Start ASAS System

Start the SENTINEL security monitoring system.

**Syntax:**
```bash
python3 asas_cli.py start [--monitor]
```

**Options:**
- `--monitor`: Start with real-time monitoring dashboard

**Examples:**
```bash
# Start system
python3 asas_cli.py start

# Start with monitoring
python3 asas_cli.py start --monitor
```

---

### `stop` - Stop ASAS System

Stop the SENTINEL security monitoring system.

**Syntax:**
```bash
python3 asas_cli.py stop
```

**Examples:**
```bash
python3 asas_cli.py stop
```

---

### `status` - System Status

Display comprehensive system status including component health and metrics.

**Syntax:**
```bash
python3 asas_cli.py status
```

**Output:**
- Component status (ACTIVE/STANDBY/OFFLINE)
- System uptime
- CPU, memory, disk usage
- Current threat level
- Active threats count

**Examples:**
```bash
python3 asas_cli.py status
```

---

### `monitor` - Real-time Dashboard

Launch real-time security monitoring dashboard.

**Syntax:**
```bash
python3 asas_cli.py monitor
```

**Features:**
- Live threat level indicator
- Real-time system metrics
- Recent threat activity
- Auto-refresh every 2 seconds

**Controls:**
- `Ctrl+C`: Exit monitoring

**Examples:**
```bash
python3 asas_cli.py monitor
```

---

### `scan` - Security Scan

Perform comprehensive security scans.

**Syntax:**
```bash
python3 asas_cli.py scan --type [quick|full|deep]
```

**Scan Types:**
- `quick`: Fast scan of critical areas (1-2 seconds)
- `full`: Comprehensive system scan (5-10 seconds)
- `deep`: Deep forensic analysis (10-30 seconds)

**Examples:**
```bash
# Quick scan
python3 asas_cli.py scan --type quick

# Full scan
python3 asas_cli.py scan --type full

# Multiple scan types
python3 asas_cli.py scan --type quick full
```

---

### `config` - Configuration Management

Manage SENTINEL configuration.

**Syntax:**
```bash
python3 asas_cli.py config [--show | --edit]
```

**Options:**
- `--show`: Display current configuration
- `--edit`: Open configuration in editor

**Examples:**
```bash
# Show configuration
python3 asas_cli.py config --show

# Edit configuration
python3 asas_cli.py config --edit
```

---

### `logs` - View Logs

View system logs.

**Syntax:**
```bash
python3 asas_cli.py logs [--tail N]
```

**Options:**
- `--tail N`: Show last N lines

**Examples:**
```bash
# List log files
python3 asas_cli.py logs

# Show last 50 lines
python3 asas_cli.py logs --tail 50

# Show last 100 lines
python3 asas_cli.py logs --tail 100
```

---

## Threat Analysis Commands

### `threat-analyze` - Analyze Threats

Analyze recent security events for threats using ML models.

**Syntax:**
```bash
python3 asas_cli.py threat-analyze [--limit N]
```

**Options:**
- `--limit N`: Number of recent events to analyze (default: 10)

**Output:**
- Threat level assessment
- Confidence score
- Threat category
- Indicators of compromise
- Recommended actions

**Examples:**
```bash
# Analyze last 10 events
python3 asas_cli.py threat-analyze

# Analyze last 50 events
python3 asas_cli.py threat-analyze --limit 50
```

---

### `threat-signatures` - Manage Signatures

List or reload threat signatures.

**Syntax:**
```bash
python3 asas_cli.py threat-signatures [list|reload] [--limit N]
```

**Actions:**
- `list`: Display loaded signatures
- `reload`: Reload signatures from database

**Options:**
- `--limit N`: Number of signatures to display (default: 10)

**Examples:**
```bash
# List signatures
python3 asas_cli.py threat-signatures list

# List 20 signatures
python3 asas_cli.py threat-signatures list --limit 20

# Reload signatures
python3 asas_cli.py threat-signatures reload
```

---

## Response Management Commands

### `response-history` - Response History

View history of automated response actions.

**Syntax:**
```bash
python3 asas_cli.py response-history [--threat-id ID] [--limit N]
```

**Options:**
- `--threat-id ID`: Filter by specific threat ID
- `--limit N`: Number of records to show (default: 20)

**Output:**
- Timestamp
- Threat ID
- Action type
- Status
- Result

**Examples:**
```bash
# View last 20 actions
python3 asas_cli.py response-history

# View last 50 actions
python3 asas_cli.py response-history --limit 50

# Filter by threat ID
python3 asas_cli.py response-history --threat-id abc123
```

---

### `response-rollback` - Rollback Action

Rollback a previously executed response action.

**Syntax:**
```bash
python3 asas_cli.py response-rollback ACTION_ID [--confirm]
```

**Arguments:**
- `ACTION_ID`: ID of the action to rollback

**Options:**
- `--confirm`: Skip confirmation prompt

**Examples:**
```bash
# Rollback with confirmation
python3 asas_cli.py response-rollback 123

# Rollback without confirmation
python3 asas_cli.py response-rollback 123 --confirm
```

---

## Platform Operations Commands

### `platform-info` - Platform Information

Display detailed platform and system information.

**Syntax:**
```bash
python3 asas_cli.py platform-info [--hardware]
```

**Options:**
- `--hardware`: Include detailed hardware information

**Output:**
- OS type and version
- Architecture
- Hostname
- CPU count
- Memory total
- Running processes
- Hardware details (with --hardware flag)

**Examples:**
```bash
# Basic info
python3 asas_cli.py platform-info

# With hardware details
python3 asas_cli.py platform-info --hardware
```

---

### `platform-processes` - List Processes

List running processes.

**Syntax:**
```bash
python3 asas_cli.py platform-processes [--filter NAME] [--limit N]
```

**Options:**
- `--filter NAME`: Filter by process name
- `--limit N`: Number of processes to show (default: 50)

**Output:**
- PID
- Process name
- Status
- Memory usage percentage

**Examples:**
```bash
# List all processes
python3 asas_cli.py platform-processes

# Filter by name
python3 asas_cli.py platform-processes --filter python

# Limit to 20 processes
python3 asas_cli.py platform-processes --limit 20
```

---

### `platform-network` - Network Connections

Display active network connections.

**Syntax:**
```bash
python3 asas_cli.py platform-network [--state STATE] [--limit N]
```

**Options:**
- `--state STATE`: Filter by connection state (e.g., ESTABLISHED, LISTEN)
- `--limit N`: Number of connections to show (default: 50)

**Output:**
- Protocol
- Local address
- Remote address
- Connection status

**Examples:**
```bash
# Show all connections
python3 asas_cli.py platform-network

# Show only established connections
python3 asas_cli.py platform-network --state ESTABLISHED

# Limit to 30 connections
python3 asas_cli.py platform-network --limit 30
```

---

### `platform-execute` - Execute Command

Execute a command via platform interface.

**Syntax:**
```bash
python3 asas_cli.py platform-execute COMMAND [--timeout SECONDS] [--confirm]
```

**Arguments:**
- `COMMAND`: Command to execute

**Options:**
- `--timeout SECONDS`: Execution timeout (default: 30)
- `--confirm`: Skip confirmation prompt

**Output:**
- Exit code
- Standard output
- Standard error (if any)

**Examples:**
```bash
# Execute command with confirmation
python3 asas_cli.py platform-execute "ls -la"

# Execute without confirmation
python3 asas_cli.py platform-execute "ps aux" --confirm

# With timeout
python3 asas_cli.py platform-execute "long-command" --timeout 60 --confirm
```

⚠️ **Warning:** Use with caution. Always verify commands before execution.

---

## AI/BaseNet Commands

### `ai-query` - Query AI Model

Query the Constitutional AI model.

**Syntax:**
```bash
python3 asas_cli.py ai-query "QUERY_TEXT"
```

**Arguments:**
- `QUERY_TEXT`: Query or question for the AI

**Output:**
- AI response
- Confidence level
- Recommendations

**Examples:**
```bash
python3 asas_cli.py ai-query "analyze current security posture"
python3 asas_cli.py ai-query "what are the current threats?"
```

---

### `ai-history` - AI Query History

View history of AI queries and responses.

**Syntax:**
```bash
python3 asas_cli.py ai-history [--limit N]
```

**Options:**
- `--limit N`: Number of records to show (default: 20)

**Output:**
- Timestamp
- Request ID
- Model type
- Query text

**Examples:**
```bash
# View last 20 queries
python3 asas_cli.py ai-history

# View last 50 queries
python3 asas_cli.py ai-history --limit 50
```

---

## Hardware/System Commands

### `hardware-metrics` - Hardware Metrics

Display detailed hardware metrics.

**Syntax:**
```bash
python3 asas_cli.py hardware-metrics
```

**Output:**
- CPU usage and temperature
- Memory usage
- Disk usage by device
- Network activity by interface
- Security score
- Threat level
- GPU metrics (if available)

**Examples:**
```bash
python3 asas_cli.py hardware-metrics
```

---

### `system-admin` - Administrative Action

Execute administrative actions on the system.

**Syntax:**
```bash
python3 asas_cli.py system-admin ACTION TARGET [--parameters JSON] [--confirm]
```

**Arguments:**
- `ACTION`: Action type to execute
- `TARGET`: Target for the action

**Options:**
- `--parameters JSON`: JSON parameters for the action
- `--confirm`: Skip confirmation prompt

**Examples:**
```bash
# Restart service
python3 asas_cli.py system-admin restart nginx --confirm

# With parameters
python3 asas_cli.py system-admin backup database --parameters '{"path": "/backup"}' --confirm
```

⚠️ **Warning:** Administrative actions can affect system operation. Use with caution.

---

## Target Management Commands

### `target-add` - Add Protection Target

Add a new protection target.

**Syntax:**
```bash
python3 asas_cli.py target-add NAME TYPE PATH [OPTIONS]
```

**Arguments:**
- `NAME`: Human-readable name for the target
- `TYPE`: Target type (file, directory, process, network_port, network_address, system, container, virtual_machine, cluster, service, database, api_endpoint, mesh_node, persistent_universe)
- `PATH`: Path, address, or identifier

**Options:**
- `--description TEXT`: Description of the target
- `--priority N`: Priority level 1-10 (default: 5)
- `--metadata JSON`: Additional metadata as JSON

**Examples:**
```bash
# Protect file
python3 asas_cli.py target-add "DB" file /data/main.db --priority 10

# Protect network port
python3 asas_cli.py target-add "HTTPS" network_port 443 --priority 8

# Protect with metadata
python3 asas_cli.py target-add "API" service "api-server" \
  --priority 9 --metadata '{"version": "2.0"}'
```

---

### `target-remove` - Remove Target

Remove a protection target.

**Syntax:**
```bash
python3 asas_cli.py target-remove TARGET_ID [--confirm]
```

**Arguments:**
- `TARGET_ID`: Target ID to remove

**Options:**
- `--confirm`: Skip confirmation prompt

**Examples:**
```bash
# Remove with confirmation
python3 asas_cli.py target-remove abc123def456

# Remove without confirmation
python3 asas_cli.py target-remove abc123def456 --confirm
```

---

### `target-list` - List Targets

List protection targets.

**Syntax:**
```bash
python3 asas_cli.py target-list [--type TYPE] [--status STATUS] [--limit N]
```

**Options:**
- `--type TYPE`: Filter by target type
- `--status STATUS`: Filter by status
- `--limit N`: Number of targets to show (default: 50)

**Examples:**
```bash
# List all targets
python3 asas_cli.py target-list

# Filter by type
python3 asas_cli.py target-list --type file

# Filter by status
python3 asas_cli.py target-list --status protected

# Limit results
python3 asas_cli.py target-list --limit 10
```

---

### `target-check` - Check Target

Check the current status of a protection target.

**Syntax:**
```bash
python3 asas_cli.py target-check TARGET_ID
```

**Arguments:**
- `TARGET_ID`: Target ID to check

**Output:**
- Target status
- Existence check
- Accessibility check
- Type-specific details

**Examples:**
```bash
python3 asas_cli.py target-check abc123def456
```

---

### `target-info` - Target Information

Get detailed information about a target including history and events.

**Syntax:**
```bash
python3 asas_cli.py target-info TARGET_ID [--events]
```

**Arguments:**
- `TARGET_ID`: Target ID

**Options:**
- `--events`: Show recent events for the target

**Output:**
- Full target details
- Configuration
- Statistics
- Recent events (if --events flag used)

**Examples:**
```bash
# Basic info
python3 asas_cli.py target-info abc123def456

# Info with events
python3 asas_cli.py target-info abc123def456 --events
```

---

## Global Options

All commands support these global options:

- `-h, --help`: Show help message
- `--version`: Show version information

---

## Exit Codes

- `0`: Success
- `1`: General error
- `2`: Invalid arguments
- `130`: Interrupted by user (Ctrl+C)

---

## Environment Variables

- `ASAS_CONFIG_DIR`: Override config directory (default: `config/`)
- `ASAS_DATA_DIR`: Override data directory (default: `data/`)
- `ASAS_LOG_DIR`: Override log directory (default: `logs/`)

---

## See Also

- [Quick Start Guide](QUICKSTART.md)
- [Target Management Guide](TARGET_MANAGEMENT.md)
- [Architecture Documentation](ARCHITECTURE.md)
- [Security Documentation](SECURITY.md)

---

<div align="center">
  <p><em>For more information, visit the <a href="../README.md">main documentation</a></em></p>
</div>
