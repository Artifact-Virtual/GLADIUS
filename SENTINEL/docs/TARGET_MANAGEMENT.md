# Target Management Guide

[![Target Types](https://img.shields.io/badge/target%20types-14-blue.svg)]()
[![Priority Levels](https://img.shields.io/badge/priority%20levels-10-green.svg)]()

Complete guide to SENTINEL's target management system.

## Overview

SENTINEL can protect **14 different target types** from individual files to entire mesh universes using a simple, unified interface.

## Target Types

| Type | Description | Use Case |
|------|-------------|----------|
| `file` | Individual files | Databases, configs, executables |
| `directory` | Directories/folders | Application directories, data folders |
| `process` | Running processes | Critical services, daemons |
| `network_port` | Network ports | HTTP, HTTPS, SSH, custom ports |
| `network_address` | IP addresses | Specific hosts, subnets |
| `system` | Entire systems | Servers, workstations |
| `container` | Docker containers | Microservices |
| `virtual_machine` | VM instances | Virtual environments |
| `cluster` | System clusters | Kubernetes, Docker Swarm |
| `service` | System services | systemd services, Windows services |
| `database` | Database instances | PostgreSQL, MySQL, MongoDB |
| `api_endpoint` | API endpoints | REST APIs, GraphQL endpoints |
| `mesh_node` | Mesh network nodes | Distributed systems |
| `persistent_universe` | Virtual universes | Game worlds, simulations |

## Quick Start

### Add a Target

```bash
python3 asas_cli.py target-add NAME TYPE PATH [OPTIONS]
```

**Example**:
```bash
python3 asas_cli.py target-add "ProductionDB" file /data/main.db --priority 10
```

### List Targets

```bash
python3 asas_cli.py target-list
```

### Check Target Status

```bash
python3 asas_cli.py target-check <TARGET_ID>
```

## Priority Levels

Assign priorities 1-10:

- **10 (Critical)**: Core databases, authentication, payment systems
- **8-9 (High)**: Production services, APIs, critical infrastructure
- **5-7 (Medium)**: Supporting services, caches, logs
- **1-4 (Low)**: Development, testing, non-critical

## Usage Scenarios

### Protect a Web Application

```bash
# Application directory
python3 asas_cli.py target-add "WebApp" directory /var/www/app --priority 8

# Database
python3 asas_cli.py target-add "AppDB" file /var/lib/db/app.db --priority 10

# API service
python3 asas_cli.py target-add "API" process "app-api" --priority 9

# Ports
python3 asas_cli.py target-add "HTTPS" network_port 443 --priority 8
python3 asas_cli.py target-add "API" network_port 8080 --priority 7
```

### Protect a Microservices Cluster

```bash
# Cluster
python3 asas_cli.py target-add "K8sCluster" cluster "10.0.0.0/24" --priority 10

# Services
python3 asas_cli.py target-add "AuthService" service "auth" --priority 10
python3 asas_cli.py target-add "PaymentService" service "payment" --priority 10

# API Gateway
python3 asas_cli.py target-add "Gateway" api_endpoint "https://api.company.com" --priority 9
```

### Protect a Gaming Universe

```bash
# Universe
python3 asas_cli.py target-add "MainUniverse" persistent_universe "universe-prime" \
  --priority 10 --metadata '{"servers": 100, "regions": 5}'

# Mesh nodes
python3 asas_cli.py target-add "RegionEU" mesh_node "eu-mesh-01" --priority 9
python3 asas_cli.py target-add "RegionUS" mesh_node "us-mesh-01" --priority 9
```

## Target Status Codes

- `active`: Target added, being monitored
- `protected`: Target confirmed safe
- `compromised`: Target shows compromise signs
- `quarantined`: Target isolated
- `inactive`: Monitoring disabled
- `unknown`: Status undetermined

## Automatic Monitoring

When SENTINEL starts, it automatically monitors all enabled targets:

```bash
python3 asas_cli.py start
```

**Monitoring includes**:
- Existence verification
- Accessibility checks
- Status changes
- Threat detection
- Performance tracking

## Event Tracking

View target events:

```bash
python3 asas_cli.py target-info <TARGET_ID> --events
```

Events include:
- Target missing
- Access denied
- Status changes
- Threats detected
- Response actions

## Best Practices

### 1. Naming Convention
Use clear, descriptive names:
- ✅ `ProductionDB`, `AuthService`, `PaymentAPI`
- ❌ `DB1`, `Service`, `Thing`

### 2. Priority Assignment
- Critical infrastructure: 10
- Production services: 8-9
- Supporting services: 5-7
- Development: 1-4

### 3. Metadata Usage
Add context:
```json
{
  "environment": "production",
  "owner": "team-platform",
  "sla": "99.99%"
}
```

### 4. Regular Reviews
```bash
python3 asas_cli.py target-list --status compromised
```

## Integration

Targets integrate with:
- **Threat Engine**: Priority-based threat correlation
- **Auto Response**: Automatic actions for compromised targets
- **System Controller**: Overall health scoring
- **Monitoring**: Dashboard status

## Troubleshooting

### Target Not Monitored
1. Check if monitoring enabled
2. Verify SENTINEL is running
3. Check target events

### Target Shows Compromised
1. Check detailed status
2. Review events
3. Verify target still exists

## See Also

- [CLI Reference](CLI_REFERENCE.md)
- [Architecture](ARCHITECTURE.md)
- [Quick Start](QUICKSTART.md)

---

<div align="center">
  <p><em>Protect anything from a single file to entire universes</em></p>
</div>
