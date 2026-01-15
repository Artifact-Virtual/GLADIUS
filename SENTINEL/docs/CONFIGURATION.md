# Configuration Guide

[![Config Files](https://img.shields.io/badge/config%20files-4-blue.svg)]()

Complete configuration guide for SENTINEL.

## Configuration Files

### System Controller (`config/system_controller_config.json`)

```json
{
  "monitoring_interval": 10,
  "alert_cooldown": 300,
  "auto_response_enabled": true,
  "constitutional_ai_enabled": true,
  "quantum_auth_required": false,
  "hardware_monitoring_enabled": true,
  "threat_correlation_enabled": true,
  "system_optimization_enabled": true,
  "target_check_interval": 60,
  "emergency_protocols": {
    "auto_quarantine": true,
    "emergency_shutdown": false,
    "network_isolation": true
  }
}
```

### Auto Response (`config/auto_response_config.json`)

```json
{
  "response_levels": {
    "low": ["log"],
    "medium": ["log", "alert"],
    "high": ["log", "alert", "isolate"],
    "critical": ["log", "alert", "isolate", "quarantine"]
  },
  "require_approval": false,
  "max_actions_per_hour": 100
}
```

### BaseNet Connector (`config/basenet_config.json`)

```json
{
  "ai_endpoint": "http://localhost:8080/ai",
  "timeout": 30,
  "retry_attempts": 3,
  "cache_enabled": true,
  "constitutional_validation": true
}
```

### Constitutional Rules (`config/constitutional_rules.json`)

```json
{
  "rules": [
    {
      "rule_id": "human_safety",
      "priority": 10,
      "principle": "human_safety",
      "constraints": ["never_harm_humans"],
      "enabled": true
    }
  ]
}
```

## Environment Variables

```bash
export ASAS_CONFIG_DIR=/etc/sentinel/config
export ASAS_DATA_DIR=/var/lib/sentinel/data
export ASAS_LOG_DIR=/var/log/sentinel
```

## CLI Configuration

View configuration:
```bash
python3 asas_cli.py config --show
```

Edit configuration:
```bash
python3 asas_cli.py config --edit
```

## Security Settings

### Authentication
- Enable multi-factor authentication
- Configure session timeouts
- Set password policies

### Encryption
- Enable TLS for communications
- Configure encryption keys
- Set key rotation policies

### Logging
- Configure log levels
- Set retention periods
- Enable audit logging

## Performance Tuning

### Monitoring Intervals
- Fast: 5 seconds (high CPU)
- Normal: 10 seconds (balanced)
- Slow: 30 seconds (low CPU)

### Resource Limits
- Max memory: 500MB
- Max CPU: 25%
- Max disk I/O: 10MB/s

## See Also

- [Quick Start](QUICKSTART.md)
- [Security](SECURITY.md)
- [Architecture](ARCHITECTURE.md)

---

<div align="center">
  <p><em>Configure SENTINEL for your environment</em></p>
</div>
