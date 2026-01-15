# Quick Start Guide

[![Time](https://img.shields.io/badge/setup%20time-5%20minutes-blue.svg)]()
[![Difficulty](https://img.shields.io/badge/difficulty-easy-green.svg)]()

Get SENTINEL up and running in 5 minutes.

## Prerequisites

- Python 3.8+
- pip package manager
- 8GB RAM (16GB recommended)
- 10GB free disk space

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/Artifact-Virtual/SENTINEL.git
cd SENTINEL
```

### 2. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Verify Installation

```bash
python3 asas_cli.py --help
```

You should see the command list.

### 4. Check System Status

```bash
python3 asas_cli.py status
```

## Basic Usage

### Start SENTINEL

```bash
python3 asas_cli.py start
```

### Run a Security Scan

```bash
python3 asas_cli.py scan --type full
```

### Add a Protection Target

```bash
# Protect a critical file
python3 asas_cli.py target-add "Database" file /path/to/db --priority 10

# Protect a network port
python3 asas_cli.py target-add "WebServer" network_port 443 --priority 8
```

### View Protected Targets

```bash
python3 asas_cli.py target-list
```

### Monitor System

```bash
python3 asas_cli.py monitor
```

Press `Ctrl+C` to exit monitoring.

## Next Steps

- Read the [CLI Reference](CLI_REFERENCE.md) for all commands
- Learn about [Target Management](TARGET_MANAGEMENT.md)
- Understand the [Architecture](ARCHITECTURE.md)
- Review [Security Best Practices](SECURITY.md)

## Troubleshooting

### Import Errors

```bash
pip3 install -r requirements.txt --upgrade
```

### Permission Denied

Run with elevated privileges:
```bash
sudo python3 asas_cli.py start
```

### Port Already in Use

Check if another instance is running:
```bash
python3 asas_cli.py status
```

## Support

- [Full Documentation](../README.md)
- [GitHub Issues](https://github.com/Artifact-Virtual/SENTINEL/issues)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

---

<div align="center">
  <p><em>You're ready to use SENTINEL!</em></p>
</div>
