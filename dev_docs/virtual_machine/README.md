# Virtual Machine & Infrastructure Documentation

> GCP VM setup, access control, and deployment documentation

This directory contains all documentation related to virtual machine infrastructure, including GCP deployment, SSH access, and development environment setup.

---

## 📁 Directory Contents

### 🔑 Access & Authentication
- **[vm_access.md](vm_access.md)** - VM access guide and credentials
- **[ssh_setup_guide.md](ssh_setup_guide.md)** - SSH key setup and configuration
- **[DEV_SECRETS.md](DEV_SECRETS.md)** - Development secrets and credentials (private)

---

## 🖥️ Current Infrastructure

### Cthulu Reign Node (GCP VM)
**Instance**: `cthulu-reign-node`
- **Type**: n2-standard-2 Spot instance
- **OS**: Ubuntu 22.04 host
- **Container**: Windows 11 VM for MetaTrader 5
- **External IP**: 34.171.231.16
- **Region**: (See vm_access.md for details)

### Access Points
| Service | URL | Port | Purpose |
|---------|-----|------|---------|
| Windows 11 Desktop | http://34.171.231.16:8006 | 8006 | Remote desktop access |
| VS Code Server | http://34.171.231.16:8443 | 8443 | Remote development |
| SSH | 34.171.231.16 | 22 | Terminal access |

---

## 🚀 Quick Start

### First Time Setup
1. **SSH Key Configuration**
   ```bash
   # Follow the SSH setup guide
   # See: ssh_setup_guide.md
   ```

2. **Access Windows Desktop**
   - Navigate to: http://34.171.231.16:8006
   - Complete Windows 11 setup if prompted
   - Default: No password on first boot

3. **VS Code Server**
   - Navigate to: http://34.171.231.16:8443
   - Password: (See DEV_SECRETS.md)
   - Remote development environment ready

### Regular Access
```bash
# SSH into the VM
ssh username@34.171.231.16

# Check running services
sudo systemctl status

# Access workspace
cd ~/workspace/cthulu
```

---

## 📚 Detailed Guides

### SSH Setup
Comprehensive SSH configuration guide:
- Key generation
- SSH config file setup
- Public key installation
- Connection testing
- Troubleshooting

**👉 [Read SSH Setup Guide](ssh_setup_guide.md)**

### VM Access
Complete access documentation:
- Service URLs and ports
- Credentials and authentication
- First-time setup checklist
- Windows VM access
- VS Code Server configuration

**👉 [Read VM Access Guide](vm_access.md)**

### Development Secrets
Private credentials and secrets (restricted access):
- API keys
- Database passwords
- Service credentials
- SSH keys

**👉 [View Dev Secrets](DEV_SECRETS.md)** *(Authorized users only)*

---

## 🔧 Installed Software

### Linux Host (Ubuntu 22.04)
- Python 3.10+
- Git
- Docker & Docker Compose
- VS Code Server
- SSH Server

### Windows 11 Container
- MetaTrader 5
- Python (for Cthulu system)
- Git for Windows
- Development tools

---

## 🛠️ Deployment Scripts

Automated startup and configuration scripts are available in [`../scripts/`](../scripts/):

### GCP Startup Scripts
- **[gcp_startup_odyssey.sh](../scripts/gcp_startup_odyssey.sh)** - Main startup script
- **[gcp_startup_soundwave.sh](../scripts/gcp_startup_soundwave.sh)** - Alternative startup

### MetaTrader Automation
- **[mt5_automate.sh](../scripts/mt5_automate.sh)** - MT5 automation script
- **[mt5linux_trace.log](../scripts/mt5linux_trace.log)** - MT5 trace logs

### Windows Scripts (PowerShell)
- **[desktop_launch_herald_and_mt5.ps1](../scripts/desktop_launch_herald_and_mt5.ps1)** - Launch trading system
- **[create_desktop_shortcut.ps1](../scripts/create_desktop_shortcut.ps1)** - Create shortcuts
- **[fix_powershell_profile.ps1](../scripts/fix_powershell_profile.ps1)** - PowerShell configuration

---

## 🏗️ Architecture

### Infrastructure Overview
```
┌─────────────────────────────────────┐
│     GCP Cloud (us-central1-a)       │
│  ┌───────────────────────────────┐  │
│  │   cthulu-reign-node (VM)      │  │
│  │                               │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │  Ubuntu 22.04 Host      │  │  │
│  │  │  - Python, Git, Docker  │  │  │
│  │  │  - VS Code Server :8443 │  │  │
│  │  │  - SSH :22              │  │  │
│  │  └─────────────────────────┘  │  │
│  │                               │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │  Windows 11 Container   │  │  │
│  │  │  - MetaTrader 5         │  │  │
│  │  │  - Remote Desktop :8006 │  │  │
│  │  │  - Cthulu System        │  │  │
│  │  └─────────────────────────┘  │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Network Configuration
- **External IP**: 34.171.231.16 (Ephemeral)
- **Firewall**: Ports 22, 8006, 8443 open
- **SSH**: Key-based authentication only
- **Services**: Systemd managed

---

## 📊 Projects Using This Infrastructure

### GoldMax
Continuous market analysis system:
- Runs on the VM
- SQLite data storage
- Automated Notion sync
- Scheduled execution

**👉 [GoldMax Project](../../projects/goldmax/)**

### Cthulu
MQL5/MetaTrader 5 trading system:
- Windows 11 container
- MetaTrader 5 platform
- Strategy execution

**👉 [Cthulu Project](../../projects/cthulu/)**

### Herald
Execution agent (in development):
- VM or container deployment
- BTCUSD focused
- Integration with GoldMax

**👉 [Herald Project](../../projects/herald/)**

---

## 🔒 Security

### Access Control
- SSH key authentication (no passwords)
- Restricted IP access (configurable)
- Private repository credentials
- Service-specific passwords

### Best Practices
1. Never commit credentials to Git
2. Use SSH keys for authentication
3. Rotate passwords regularly
4. Monitor access logs
5. Keep software updated

### Secrets Management
- Store secrets in DEV_SECRETS.md (not in Git)
- Use environment variables for runtime secrets
- Consider using a vault system for production

---

## 🔧 Maintenance

### Regular Tasks
- [ ] Check VM disk usage
- [ ] Review access logs
- [ ] Update system packages
- [ ] Verify backup integrity
- [ ] Monitor service health

### Monitoring
```bash
# Check system resources
htop

# Check disk usage
df -h

# Check service status
sudo systemctl status

# View logs
journalctl -u service-name
```

---

## 📞 Support

For VM access issues or infrastructure questions:
- Contact: [`amuzetnoM`](https://github.com/amuzetnoM)
- Check: [vm_access.md](vm_access.md) for current status
- Review: [ssh_setup_guide.md](ssh_setup_guide.md) for troubleshooting

---

## 🔗 Related Documentation

- [Architecture Documentation](../docs/architectural_mandate.md)
- [Deployment Scripts](../scripts/)
- [Projects Documentation](../../projects/)
- [Main Repository README](../../README.md)

---

*Part of the Gladius research repository*
