# Architecture Documentation

[![Components](https://img.shields.io/badge/components-6-blue.svg)]()
[![Functions](https://img.shields.io/badge/functions-83-green.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-100%25-success.svg)]()

SENTINEL's modular architecture ensures scalability, maintainability, and extensibility.

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    SENTINEL CLI Interface                    │
│                  24 Commands - 100% Coverage                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │ SecurityMonitor │  │  ThreatEngine    │  │AutoResponse│ │
│  │  11 functions   │  │  11 functions    │  │13 functions│ │
│  └─────────────────┘  └──────────────────┘  └────────────┘ │
│                                                               │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │PlatformInterface│  │ BaseNetConnector │  │SysController│ │
│  │  12 functions   │  │  13 functions    │  │23 functions│ │
│  └─────────────────┘  └──────────────────┘  └────────────┘ │
│                                                               │
│              Total: 83 Functions - 100% Accessible           │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### SecurityMonitor (11 functions)
**Purpose**: Real-time system integrity and security monitoring

**Key Functions**:
- `start_monitoring()` - Start monitoring thread
- `stop_monitoring()` - Stop monitoring thread
- `full_system_scan()` - Comprehensive security scan
- `get_security_status()` - Get current security state
- `_check_system_integrity()` - System integrity verification
- `_check_process_anomalies()` - Process behavior analysis
- `_check_network_anomalies()` - Network traffic analysis
- `_check_file_integrity()` - File integrity monitoring
- `_establish_baseline()` - Create security baseline

**Technologies**: psutil, ML anomaly detection, baseline comparison

---

### ThreatEngine (11 functions)
**Purpose**: AI-powered threat detection and classification

**Key Functions**:
- `analyze_events()` - Analyze security events
- `_signature_detection()` - Signature-based detection
- `_behavioral_analysis()` - Behavioral pattern analysis
- `_anomaly_detection()` - ML-based anomaly detection
- `_load_threat_signatures()` - Load signature database
- `_create_threat_assessment()` - Generate threat assessment

**Technologies**: scikit-learn (IsolationForest, DBSCAN), signature matching

---

### AutoResponse (13 functions)
**Purpose**: Automated incident response and remediation

**Key Functions**:
- `respond_to_threat()` - Execute threat response
- `analyze_threat_response()` - Determine response level
- `execute_response_action()` - Execute specific action
- `rollback_action()` - Rollback previous action
- `get_response_history()` - View action history
- `_kill_process()` - Terminate process
- `_quarantine_file()` - Isolate file
- `_block_network()` - Block network access

**Technologies**: Constitutional AI validation, action logging

---

### PlatformInterface (12 functions)
**Purpose**: Cross-platform system operations

**Key Functions**:
- `get_system_info()` - System information
- `get_process_list()` - List processes
- `get_network_connections()` - Network connections
- `execute_command()` - Execute system commands
- `kill_process()` - Terminate process
- `manage_service()` - Service management
- `block_network_address()` - Network filtering

**Technologies**: subprocess, psutil, OS-specific APIs

---

### BaseNetConnector (13 functions)
**Purpose**: Constitutional AI integration and ethical decision-making

**Key Functions**:
- `query_ai_model()` - Query AI
- `validate_security_action()` - Validate actions
- `get_ai_history()` - Query history
- `evaluate_ethical_compliance()` - Ethical validation
- `_load_constitutional_rules()` - Load rules
- `encrypt_payload()` / `decrypt_payload()` - Secure communication

**Technologies**: aiohttp, cryptography, Constitutional AI framework

---

### SystemController (23 functions)
**Purpose**: Centralized component coordination and target management

**Key Functions**:
- `start_monitoring()` / `stop_monitoring()` - Control monitoring
- `execute_administrative_action()` - Admin operations
- `get_system_status()` - System state
- `add_protection_target()` - Add target
- `remove_protection_target()` - Remove target
- `list_protection_targets()` - List targets
- `check_protection_target()` - Check target status
- Target monitoring loop, hardware monitoring, metrics collection

**Technologies**: Threading, SQLite, TargetManager, HardwareMonitor

---

## Data Flow

### 1. Monitoring Layer
- Continuous system observation
- Hardware metrics collection
- Process and network monitoring
- File integrity checking
- Target health verification

### 2. Analysis Layer
- Event collection
- ML-based threat detection
- Signature matching
- Behavioral analysis
- Anomaly scoring

### 3. Decision Layer
- Threat assessment creation
- Priority determination
- Constitutional AI validation
- Response level calculation

### 4. Action Layer
- Response execution
- Quarantine operations
- Network blocking
- Process termination
- System modifications

### 5. Storage Layer
- Event logging
- Metric persistence
- Action history
- Target database
- Configuration storage

---

## Database Schema

### Targets Database (`data/targets.db`)
```sql
CREATE TABLE targets (
    target_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    target_type TEXT NOT NULL,
    path_or_address TEXT NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 5,
    status TEXT DEFAULT 'active',
    created_at TEXT NOT NULL,
    last_checked TEXT,
    threat_count INTEGER DEFAULT 0,
    metadata TEXT,
    monitoring_enabled INTEGER DEFAULT 1,
    auto_response_enabled INTEGER DEFAULT 1
);

CREATE TABLE target_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    description TEXT,
    timestamp TEXT NOT NULL,
    resolved INTEGER DEFAULT 0
);
```

### Threat Intelligence Database (`data/threat_intelligence.db`)
- Threat signatures
- Historical assessments
- Pattern databases

### System Controller Database (`data/system_controller.db`)
- Administrative actions
- System metrics
- Hardware alerts

---

## Thread Architecture

### Main Thread
- CLI interface
- User interaction
- Command dispatch

### Monitoring Thread
- Security monitoring loop
- Hardware metrics collection
- System integrity checks

### Target Monitoring Thread
- Target health checks
- Status updates
- Event logging

### Response Thread (on-demand)
- Threat response execution
- Action coordination

---

## Configuration

### Config Files
- `config/system_controller_config.json` - System settings
- `config/auto_response_config.json` - Response settings
- `config/basenet_config.json` - AI settings
- `config/constitutional_rules.json` - Ethical rules

### Environment Variables
- `ASAS_CONFIG_DIR` - Config directory
- `ASAS_DATA_DIR` - Data directory
- `ASAS_LOG_DIR` - Log directory

---

## Performance Characteristics

- **Startup Time**: < 1 second
- **Memory Baseline**: 50-100MB
- **CPU Usage**: < 5% idle, < 20% active
- **Scan Performance**:
  - Quick: 1-2 seconds
  - Full: 5-10 seconds
  - Deep: 10-30 seconds

---

## Scalability

- **Targets**: 1 - 10,000+ targets
- **Events**: 100,000+ events/day
- **Concurrent Monitoring**: Real-time
- **Database Size**: Grows linearly with targets/events
- **Multi-node**: Planned for future releases

---

## Security Design

- **Principle of Least Privilege**: Minimal permissions required
- **Defense in Depth**: Multiple security layers
- **Fail Secure**: Safe defaults, secure failures
- **Audit Trail**: Complete action logging
- **Constitutional AI**: Ethical decision validation

---

## Extension Points

### Custom Threat Signatures
Add signatures to `data/threat_intelligence.db`

### Custom Response Actions
Extend `AutomatedResponseSystem` class

### Platform Support
Implement platform-specific methods in `PlatformInterface`

### AI Models
Integrate custom models in `ThreatEngine`

---

## See Also

- [CLI Reference](CLI_REFERENCE.md)
- [Target Management](TARGET_MANAGEMENT.md)
- [Security Documentation](SECURITY.md)
- [API Reference](API_REFERENCE.md)

---

<div align="center">
  <p><em>Architecture designed for security, scalability, and maintainability</em></p>
</div>
