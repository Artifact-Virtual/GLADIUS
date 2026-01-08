# Deployment Guide

Production deployment guide for all Arty modules.

## Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Node.js 16+ and npm
- PM2 for process management
- Nginx for reverse proxy (optional)
- SQLite3 installed

## System Setup

### 1. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js 18 LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2 globally
sudo npm install -g pm2

# Install SQLite3
sudo apt install -y sqlite3
```

### 2. Clone and Setup

```bash
# Clone repository
git clone <repository_url>
cd gladius/arty

# Install all modules
npm install
cd discord && npm install && cd ..
cd linkedin && npm install && cd ..
cd research && npm install && cd ..
```

### 3. Configure Environment

```bash
# Copy environment files
cp discord/.env.example discord/.env
cp linkedin/.env.example linkedin/.env
cp research/.env.example research/.env

# Copy config files
cp discord/config.example.json discord/config.json
cp linkedin/config.example.json linkedin/config.json
cp research/config.example.json research/config.json

# Edit with production values
nano discord/.env
nano linkedin/.env
nano research/.env
```

### 4. Initialize Storage

```bash
cd store
node init-databases.js
cd ..
```

## PM2 Deployment

### Discord Bot

**Create `discord/ecosystem.config.js`:**
```javascript
module.exports = {
  apps: [{
    name: 'arty-discord',
    script: './src/index.js',
    cwd: '/path/to/arty/discord',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'production'
    },
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
  }]
};
```

**Start:**
```bash
cd discord
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### LinkedIn Automation

**Create `linkedin/ecosystem.config.js`:**
```javascript
module.exports = {
  apps: [{
    name: 'arty-linkedin',
    script: './src/index.js',
    cwd: '/path/to/arty/linkedin',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '300M',
    env: {
      NODE_ENV: 'production'
    },
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log'
  }]
};
```

**Start:**
```bash
cd linkedin
pm2 start ecosystem.config.js
pm2 save
```

### Research Engine

**Create `research/ecosystem.config.js`:**
```javascript
module.exports = {
  apps: [{
    name: 'arty-research',
    script: './src/index.js',
    cwd: '/path/to/arty/research',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '800M',
    env: {
      NODE_ENV: 'production'
    },
    cron_restart: '0 2 * * *',  // Restart at 2 AM daily
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log'
  }]
};
```

**Start:**
```bash
cd research
pm2 start ecosystem.config.js
pm2 save
```

## PM2 Management

```bash
# View all processes
pm2 list

# Monitor
pm2 monit

# View logs
pm2 logs arty-discord
pm2 logs arty-linkedin
pm2 logs arty-research

# Restart
pm2 restart arty-discord
pm2 restart all

# Stop
pm2 stop arty-discord
pm2 stop all

# Delete
pm2 delete arty-discord
pm2 delete all
```

## Systemd Service (Alternative)

### Discord Bot Service

**Create `/etc/systemd/system/arty-discord.service`:**
```ini
[Unit]
Description=Arty Discord Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/arty/discord
ExecStart=/usr/bin/node src/index.js
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=arty-discord

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable arty-discord
sudo systemctl start arty-discord
sudo systemctl status arty-discord
```

## Nginx Reverse Proxy (Optional)

If exposing webhook endpoints:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /webhooks/discord {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /webhooks/linkedin {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
```

## Monitoring

### Log Rotation

**Create `/etc/logrotate.d/arty`:**
```
/path/to/arty/*/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
    postrotate
        pm2 reloadLogs
    endscript
}
```

### Health Checks

**Create `health-check.sh`:**
```bash
#!/bin/bash

# Check Discord bot
if ! pm2 describe arty-discord | grep -q "online"; then
    echo "Discord bot is down!"
    pm2 restart arty-discord
fi

# Check LinkedIn
if ! pm2 describe arty-linkedin | grep -q "online"; then
    echo "LinkedIn is down!"
    pm2 restart arty-linkedin
fi

# Check Research
if ! pm2 describe arty-research | grep -q "online"; then
    echo "Research is down!"
    pm2 restart arty-research
fi
```

**Add to crontab:**
```bash
*/5 * * * * /path/to/health-check.sh >> /path/to/health.log 2>&1
```

### Database Backup

**Create `backup.sh`:**
```bash
#!/bin/bash

BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup databases
cp /path/to/arty/store/research.db "$BACKUP_DIR/research_$DATE.db"
cp /path/to/arty/store/vector.db "$BACKUP_DIR/vector_$DATE.db"
cp /path/to/arty/discord/data/discord.db "$BACKUP_DIR/discord_$DATE.db"
cp /path/to/arty/linkedin/data/linkedin.db "$BACKUP_DIR/linkedin_$DATE.db"

# Backup file system
tar -czf "$BACKUP_DIR/filesystem_$DATE.tar.gz" /path/to/arty/store/file_system

# Delete backups older than 30 days
find "$BACKUP_DIR" -name "*.db" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
```

**Add to crontab:**
```bash
0 2 * * * /path/to/backup.sh >> /path/to/backup.log 2>&1
```

## Security

### File Permissions

```bash
# Restrict .env files
chmod 600 discord/.env
chmod 600 linkedin/.env
chmod 600 research/.env

# Restrict config files
chmod 644 discord/config.json
chmod 644 linkedin/config.json
chmod 644 research/config.json

# Restrict databases
chmod 600 store/*.db
chmod 600 discord/data/*.db
chmod 600 linkedin/data/*.db
```

### Firewall

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS (if using webhooks)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### Environment Variables

Consider using a secrets manager:
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- Doppler

## Performance Optimization

### Node.js

```bash
# Increase memory limit
NODE_OPTIONS="--max-old-space-size=2048" pm2 start ecosystem.config.js
```

### Database

```bash
# Optimize SQLite
sqlite3 store/research.db "VACUUM;"
sqlite3 store/research.db "ANALYZE;"
```

### Caching

Enable Redis for caching (optional):
```bash
sudo apt install redis-server
sudo systemctl enable redis-server
```

## Scaling

### Multiple Servers

- **Load Balancer**: Nginx/HAProxy
- **Shared Database**: PostgreSQL instead of SQLite
- **Shared Storage**: NFS/S3 for file_system
- **Message Queue**: RabbitMQ/Redis for tasks

### Database Migration

When scaling, migrate from SQLite to PostgreSQL:
```bash
# Export data
sqlite3 store/research.db .dump > research.sql

# Import to PostgreSQL
psql -U postgres -d arty_research -f research.sql
```

## Troubleshooting

**Process crashes:**
```bash
pm2 logs arty-discord --err --lines 100
```

**High memory:**
```bash
pm2 restart arty-discord --update-env
```

**Database locked:**
```bash
fuser store/research.db
kill -9 <PID>
```

See [Troubleshooting Guide](TROUBLESHOOTING.md) for more solutions.

## Update Procedure

```bash
# Pull latest changes
git pull origin main

# Stop services
pm2 stop all

# Update dependencies
cd discord && npm install && cd ..
cd linkedin && npm install && cd ..
cd research && npm install && cd ..

# Backup databases
./backup.sh

# Restart services
pm2 restart all

# Verify
pm2 status
```

## Production Checklist

- [ ] All `.env` files configured
- [ ] All `config.json` files configured
- [ ] Databases initialized
- [ ] PM2 configured and running
- [ ] Logs rotating
- [ ] Backups scheduled
- [ ] Health checks active
- [ ] Firewall configured
- [ ] File permissions set
- [ ] Monitoring in place
- [ ] Tests passing
- [ ] Documentation updated
