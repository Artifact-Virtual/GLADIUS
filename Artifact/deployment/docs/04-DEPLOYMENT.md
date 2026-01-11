# Deployment Guide

**Gold Standard Enterprise Suite v1.0.0**

---

## Production Deployment

### Prerequisites

- Ubuntu 20.04+ (or equivalent Linux distribution)
- Python 3.12+
- 8GB+ RAM
- 50GB+ storage
- PostgreSQL 14+ (recommended for production)
- Redis 6+ (optional, for caching)
- NGINX (for reverse proxy)

### Deployment Steps

#### 1. System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.12 python3.12-venv python3-pip postgresql redis-server nginx

# Create application user
sudo useradd -m -s /bin/bash appuser
sudo mkdir -p /opt/goldstandard
sudo chown appuser:appuser /opt/goldstandard
```

#### 2. Application Setup

```bash
# Clone/copy application
sudo -u appuser cp -r /path/to/_deployment /opt/goldstandard/

# Create virtual environment
cd /opt/goldstandard/_deployment/automata
sudo -u appuser python3.12 -m venv venv
sudo -u appuser venv/bin/pip install -r requirements.txt
```

#### 3. Database Setup

```bash
# Create database
sudo -u postgres createuser goldstandard
sudo -u postgres createdb goldstandard_prod -O goldstandard
sudo -u postgres psql -c "ALTER USER goldstandard WITH PASSWORD 'secure_password';"

# Initialize schema
cd /opt/goldstandard/_deployment
sudo -u appuser venv/bin/python scripts/init_database.py
```

#### 4. Configuration

```bash
# Create production config
sudo -u appuser cp automata/.env.template /opt/goldstandard/.env
sudo -u appuser chmod 600 /opt/goldstandard/.env

# Edit configuration
sudo -u appuser nano /opt/goldstandard/.env
```

**Production `.env` settings:**
```bash
# Environment
ENV=production
DEBUG=false

# Database
DATABASE_URL=postgresql://goldstandard:password@localhost/goldstandard_prod

# AI Provider
AI_PROVIDER=openai
AI_API_KEY=sk-...

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=generate-strong-random-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Monitoring
SENTRY_DSN=https://...
```

#### 5. Systemd Service

```bash
# Create service file
sudo cat > /etc/systemd/system/goldstandard.service << EOF
[Unit]
Description=Gold Standard Enterprise Suite
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/goldstandard/_deployment
Environment="PATH=/opt/goldstandard/_deployment/automata/venv/bin"
ExecStart=/opt/goldstandard/_deployment/automata/venv/bin/python -m automata.core.manager
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable goldstandard
sudo systemctl start goldstandard
sudo systemctl status goldstandard
```

#### 6. NGINX Configuration

```nginx
# /etc/nginx/sites-available/goldstandard
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/goldstandard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 7. SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "automata.core.manager"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/goldstandard
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./data:/app/data
  
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: goldstandard
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## Monitoring Setup

### Prometheus + Grafana

```bash
# Install Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
sudo mv prometheus-2.40.0.linux-amd64 /opt/prometheus

# Configure
cat > /opt/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'goldstandard'
    static_configs:
      - targets: ['localhost:9090']
EOF

# Install Grafana
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
sudo apt-get update
sudo apt-get install grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

---

## Backup Strategy

### Automated Backups

```bash
#!/bin/bash
# /opt/goldstandard/backup.sh

BACKUP_DIR="/backups/goldstandard"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump goldstandard_prod > "$BACKUP_DIR/db_$DATE.sql"

# Context database backup
cp ~/.automata/context.db "$BACKUP_DIR/context_$DATE.db"

# Configuration backup
cp /opt/goldstandard/.env "$BACKUP_DIR/env_$DATE"

# Compress
tar -czf "$BACKUP_DIR/full_backup_$DATE.tar.gz" "$BACKUP_DIR/"*_$DATE*

# Clean old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
```

### Cron Schedule

```bash
# Add to crontab
0 2 * * * /opt/goldstandard/backup.sh
```

---

**Document Version:** 1.0.0  
**Last Updated:** January 2026
