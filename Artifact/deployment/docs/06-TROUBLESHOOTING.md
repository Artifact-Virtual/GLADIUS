# Troubleshooting Guide

**Gold Standard Enterprise Suite v1.0.0**

---

## Common Issues and Solutions

### AI Engine Issues

#### Problem: AI Generation Fails

**Symptoms:**
- "API key invalid" errors
- Timeout errors
- Empty responses

**Solutions:**

1. **Verify API Key**
```bash
# Check API key is set
echo $AI_API_KEY

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $AI_API_KEY"
```

2. **Check Provider Configuration**
```python
# Verify provider matches key
AI_PROVIDER=openai  # Must match your API key provider
AI_MODEL=gpt-4      # Must be available for your account
```

3. **Review Rate Limits**
```python
# Check rate limit headers in logs
# Implement exponential backoff
```

#### Problem: Context Database Locked

**Symptoms:**
- "database is locked" errors
- Slow response times

**Solutions:**

```bash
# Check database file
ls -lh ~/.automata/context.db

# Check for write permissions
chmod 600 ~/.automata/context.db

# If corrupted, restore from backup
cp ~/.automata/context.db.backup ~/.automata/context.db
```

---

### Social Media Integration Issues

#### Problem: OAuth Token Expired

**Symptoms:**
- 401 Unauthorized errors
- "Token invalid" messages

**Solutions:**

1. **Manual Token Refresh**
```python
from automata.social_media.platforms import LinkedInConnector

connector = LinkedInConnector(config)
await connector.authenticate()  # Will refresh token
```

2. **Update Tokens in Configuration**
```bash
# LinkedIn
LINKEDIN_ACCESS_TOKEN=new_token_here

# Twitter
TWITTER_ACCESS_TOKEN=new_token
TWITTER_ACCESS_TOKEN_SECRET=new_secret
```

#### Problem: Rate Limit Exceeded

**Symptoms:**
- "Rate limit exceeded" errors
- 429 status codes

**Solutions:**

1. **Adjust Posting Frequency**
```python
# In .env
TWITTER_MAX_POSTS_PER_DAY=10  # Reduce from default
LINKEDIN_MAX_POSTS_PER_DAY=5
```

2. **Check Scheduler Settings**
```python
# Increase delay between posts
SCHEDULER_CHECK_INTERVAL=300  # 5 minutes
```

---

### ERP Integration Issues

#### Problem: SAP Connection Timeout

**Symptoms:**
- Connection timeout errors
- "Unable to connect to SAP" messages

**Solutions:**

1. **Verify Network Connectivity**
```bash
# Test SAP endpoint
curl -v https://your-sap-server.com:port

# Check firewall rules
sudo ufw status
```

2. **Validate Credentials**
```bash
# Test basic auth
curl -u username:password https://your-sap-server.com/sap/opu/odata/sap/API_BUSINESS_PARTNER
```

3. **Increase Timeout**
```python
# In connector configuration
SAP_TIMEOUT=60  # Increase from default 30
```

#### Problem: Odoo XML-RPC Authentication Fails

**Symptoms:**
- "Authentication failed" errors
- Invalid UID returned

**Solutions:**

1. **Verify Database Name**
```python
ODOO_DATABASE=production  # Must match exact database name
```

2. **Test Connection**
```python
import xmlrpc.client

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(database, username, password, {})
print(f"UID: {uid}")  # Should return positive integer
```

---

### Database Issues

#### Problem: PostgreSQL Connection Pool Exhausted

**Symptoms:**
- "Too many connections" errors
- Slow database queries

**Solutions:**

1. **Increase Max Connections**
```sql
-- In postgresql.conf
max_connections = 200

-- Reload config
SELECT pg_reload_conf();
```

2. **Optimize Connection Pool**
```python
# In database configuration
SQLALCHEMY_POOL_SIZE=20
SQLALCHEMY_MAX_OVERFLOW=40
SQLALCHEMY_POOL_RECYCLE=3600
```

#### Problem: Database Migration Fails

**Symptoms:**
- Migration errors
- Schema inconsistencies

**Solutions:**

```bash
# Rollback last migration
alembic downgrade -1

# Check migration history
alembic history

# Force migration
alembic stamp head
alembic upgrade head
```

---

### Performance Issues

#### Problem: High Memory Usage

**Symptoms:**
- System slowdown
- Out of memory errors

**Solutions:**

1. **Check Memory Usage**
```bash
# Overall memory
free -h

# Per process
ps aux --sort=-%mem | head -10
```

2. **Optimize Context Engine**
```python
# Reduce context size
CONTEXT_MAX_TOKENS=50000  # Reduce from 100000

# Increase truncation frequency
CONTEXT_TRUNCATE_THRESHOLD=0.8  # Truncate at 80% full
```

3. **Enable Garbage Collection**
```python
import gc

# Force garbage collection
gc.collect()

# Adjust GC thresholds
gc.set_threshold(700, 10, 10)
```

#### Problem: Slow API Responses

**Symptoms:**
- Timeout errors
- Long response times

**Solutions:**

1. **Enable Caching**
```bash
# Redis configuration
REDIS_URL=redis://localhost:6379/0
CACHE_ENABLED=true
CACHE_TTL=300  # 5 minutes
```

2. **Optimize Database Queries**
```sql
-- Add indexes
CREATE INDEX idx_portfolio_owner ON portfolios(owner_id);
CREATE INDEX idx_position_portfolio ON positions(portfolio_id);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM portfolios WHERE owner_id = 'user_123';
```

---

### System Issues

#### Problem: Service Won't Start

**Symptoms:**
- Systemd service fails to start
- Process exits immediately

**Solutions:**

1. **Check Logs**
```bash
# Systemd logs
sudo journalctl -u goldstandard -n 50

# Application logs
tail -f ~/.automata/logs/system.log
tail -f ~/.automata/logs/errors.log
```

2. **Verify Configuration**
```bash
# Check environment file
cat /opt/goldstandard/.env | grep -v "PASSWORD\|KEY\|SECRET"

# Test configuration
cd /opt/goldstandard/_deployment
venv/bin/python -c "from automata.core.config import AutomationConfig; AutomationConfig()"
```

3. **Check Permissions**
```bash
# Verify file permissions
ls -la /opt/goldstandard/
ls -la ~/.automata/

# Fix if needed
sudo chown -R appuser:appuser /opt/goldstandard/
```

#### Problem: Disk Space Full

**Symptoms:**
- "No space left on device" errors
- Write failures

**Solutions:**

```bash
# Check disk usage
df -h

# Find large files
du -ah / | sort -rh | head -20

# Clean up logs
sudo journalctl --vacuum-time=7d
find ~/.automata/logs -name "*.log" -mtime +30 -delete

# Clean up old backups
find /backups -name "*.tar.gz" -mtime +90 -delete
```

---

## Debugging Tools

### Enable Debug Logging

```python
# In .env
DEBUG=true
LOG_LEVEL=DEBUG

# Or programmatically
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Python Debugger

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use built-in breakpoint()
breakpoint()
```

### Network Debugging

```bash
# Monitor network traffic
sudo tcpdump -i any port 443 -nn -A

# Test SSL/TLS
openssl s_client -connect api.openai.com:443

# DNS lookup
nslookup yourdomain.com
dig yourdomain.com
```

---

## Getting Help

### Before Requesting Support

1. Check logs for error messages
2. Review this troubleshooting guide
3. Test in isolation (minimal config)
4. Document steps to reproduce
5. Gather system information

### System Information Collection

```bash
#!/bin/bash
# collect_info.sh

echo "=== System Information ===" > debug_info.txt
uname -a >> debug_info.txt
cat /etc/os-release >> debug_info.txt

echo "=== Python Version ===" >> debug_info.txt
python --version >> debug_info.txt

echo "=== Installed Packages ===" >> debug_info.txt
pip list >> debug_info.txt

echo "=== Recent Logs ===" >> debug_info.txt
tail -100 ~/.automata/logs/errors.log >> debug_info.txt

echo "=== Configuration (sanitized) ===" >> debug_info.txt
cat .env | grep -v "PASSWORD\|KEY\|SECRET" >> debug_info.txt
```

### Support Channels

- **Documentation**: `/docs/` directory
- **Email**: support@goldstandard.enterprise
- **Emergency**: +1-XXX-XXX-XXXX

---

**Document Version:** 1.0.0  
**Last Updated:** January 2026
