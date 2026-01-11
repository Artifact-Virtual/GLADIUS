# Quick Reference Guide

**Gold Standard Enterprise Suite v1.0.0**

Fast access to common commands and configurations.

---

## 🚀 Quick Start

```bash
# Clone/Navigate to deployment
cd /home/adam/worxpace/_deployment/automata

# Setup environment
./setup.sh

# Configure API keys
nano .env

# Run examples
python3 examples.py
```

---

## 📦 Installation Commands

### Ubuntu/Debian
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.12 python3.12-venv python3-pip postgresql redis-server nginx

# Install Python packages
pip3 install -r automata/requirements.txt
pip3 install -r infra/requirements.txt
```

### RHEL/CentOS
```bash
# Update system
sudo yum update -y

# Install dependencies
sudo yum install -y python3.12 python3-pip postgresql redis nginx

# Install Python packages
pip3 install -r automata/requirements.txt
pip3 install -r infra/requirements.txt
```

---

## ⚙️ Configuration

### Environment Variables (.env)

**Required:**
```bash
# AI Provider (choose one)
AI_PROVIDER=openai
AI_API_KEY=sk-...

# Or Anthropic
AI_PROVIDER=anthropic
AI_API_KEY=sk-ant-...

# Or Cohere
AI_PROVIDER=cohere
AI_API_KEY=...
```

**Social Media (Optional):**
```bash
# Twitter
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_TOKEN_SECRET=...

# LinkedIn
LINKEDIN_ACCESS_TOKEN=...
LINKEDIN_CLIENT_ID=...
LINKEDIN_CLIENT_SECRET=...

# Facebook
FACEBOOK_ACCESS_TOKEN=...
FACEBOOK_APP_ID=...
FACEBOOK_APP_SECRET=...
```

**ERP Systems (Optional):**
```bash
# SAP
SAP_URL=https://your-sap-server.com
SAP_USERNAME=...
SAP_PASSWORD=...

# Odoo
ODOO_URL=https://your-odoo.com
ODOO_DATABASE=production
ODOO_USERNAME=...
ODOO_PASSWORD=...
```

**Database (Production):**
```bash
DATABASE_URL=postgresql://user:password@localhost/goldstandard
REDIS_URL=redis://localhost:6379/0
```

---

## 🔧 Common Commands

### Service Management

```bash
# Start service
sudo systemctl start goldstandard

# Stop service
sudo systemctl stop goldstandard

# Restart service
sudo systemctl restart goldstandard

# View status
sudo systemctl status goldstandard

# View logs
sudo journalctl -u goldstandard -f
```

### Database Operations

```bash
# PostgreSQL backup
pg_dump goldstandard_prod > backup_$(date +%Y%m%d).sql

# Restore backup
psql goldstandard_prod < backup_20260103.sql

# Check database size
psql -c "SELECT pg_size_pretty(pg_database_size('goldstandard_prod'));"

# Vacuum database
psql -c "VACUUM ANALYZE;"
```

### Application Management

```bash
# Check Python version
python3 --version

# List installed packages
pip3 list

# Update packages
pip3 install --upgrade -r requirements.txt

# Run tests
cd automata && python3 -m pytest tests/
cd infra && python3 -m pytest tests/
```

---

## 📊 Monitoring

### Check System Resources

```bash
# CPU and memory
htop

# Disk usage
df -h

# Disk I/O
iostat -x 1

# Network
iftop

# Process list
ps aux --sort=-%cpu | head -20
```

### Application Logs

```bash
# System logs
tail -f ~/.enterprise_automation/logs/system.log

# Error logs
tail -f ~/.enterprise_automation/logs/errors.log

# AI generation logs
tail -f ~/.enterprise_automation/logs/ai_engine.log

# Social media logs
tail -f ~/.enterprise_automation/logs/social_media.log
```

### Database Monitoring

```bash
# PostgreSQL connections
psql -c "SELECT count(*) FROM pg_stat_activity;"

# Active queries
psql -c "SELECT pid, query, state FROM pg_stat_activity WHERE state != 'idle';"

# Database size
psql -c "SELECT pg_size_pretty(pg_database_size(current_database()));"
```

---

## 🛠️ Troubleshooting

### Common Issues

**Service won't start:**
```bash
# Check logs
sudo journalctl -u goldstandard -n 100

# Verify config
cd /opt/goldstandard/_deployment
python3 -c "from automata.core.config import AutomationConfig; AutomationConfig()"

# Check permissions
ls -la ~/.enterprise_automation/
```

**Database connection errors:**
```bash
# Test PostgreSQL connection
psql -h localhost -U username -d goldstandard_prod

# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql
```

**High memory usage:**
```bash
# Check memory
free -h

# Find memory hogs
ps aux --sort=-%mem | head -10

# Clear cache
sudo sync && sudo sysctl vm.drop_caches=3
```

**API errors:**
```bash
# Test OpenAI API
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $AI_API_KEY"

# Test social media API
cd automata
python3 -c "from social_media.platforms.twitter_connector import TwitterConnector; print('OK')"
```

---

## 📈 Performance Tuning

### PostgreSQL Optimization

```sql
-- In postgresql.conf
shared_buffers = 8GB
effective_cache_size = 24GB
maintenance_work_mem = 2GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 52MB
min_wal_size = 2GB
max_wal_size = 8GB
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
```

### NGINX Optimization

```nginx
# In nginx.conf
worker_processes auto;
worker_connections 1024;

# Enable gzip
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/json;

# Cache
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m;
proxy_cache_valid 200 60m;
```

### Application Tuning

```python
# In .env
CONTEXT_MAX_TOKENS=100000
CONTEXT_TRUNCATE_THRESHOLD=0.8
SCHEDULER_CHECK_INTERVAL=60
AI_REQUEST_TIMEOUT=30
ERP_SYNC_BATCH_SIZE=100
SOCIAL_MEDIA_MAX_RETRIES=3
```

---

## 🔐 Security Checklist

- [ ] SSH password authentication disabled
- [ ] Firewall configured (ufw/iptables)
- [ ] SSL/TLS certificates installed
- [ ] Environment variables secured
- [ ] Database encryption enabled
- [ ] Regular backups configured
- [ ] Audit logging enabled
- [ ] Security updates automated
- [ ] API keys rotated quarterly
- [ ] Access logs monitored

---

## 📞 Support Resources

### Documentation
- [README.md](README.md) - Main overview
- [SYSTEM_REQUIREMENTS.md](SYSTEM_REQUIREMENTS.md) - Hardware/software specs
- [docs/](docs/) - Complete documentation suite

### Getting Help
1. Check [Troubleshooting Guide](docs/06-TROUBLESHOOTING.md)
2. Review system logs
3. Search documentation
4. Contact: support@goldstandard.enterprise

---

## 🎯 System Requirements Summary

| Tier | CPU | RAM | Storage | Users | Cost/mo |
|------|-----|-----|---------|-------|---------|
| **Baseline** | 2 cores | 4 GB | 20 GB | 1-2 | $30-230 |
| **Optimal** | 8 cores | 32 GB | 600 GB | 10-20 | $610-660 |
| **Enterprise** | 16+ cores | 64+ GB | 1+ TB | 100+ | $2,200+ |

See [SYSTEM_REQUIREMENTS.md](SYSTEM_REQUIREMENTS.md) for complete specifications.

---

**Quick Reference v1.0.0**  
**Last Updated:** January 2026
