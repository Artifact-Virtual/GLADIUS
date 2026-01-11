# Security Guide

**Gold Standard Enterprise Suite v1.0.0**

---

## Security Overview

This document outlines security best practices and configurations for the Gold Standard Enterprise Suite.

---

## Authentication & Authorization

### SSH Key-Based Authentication

**Never use password authentication in production.**

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "goldstandard@enterprise" -f ~/.ssh/goldstandard_key

# Set proper permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/goldstandard_key
chmod 644 ~/.ssh/goldstandard_key.pub

# Add to authorized_keys on server
cat ~/.ssh/goldstandard_key.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### API Key Management

**Best Practices:**
1. Rotate keys every 90 days
2. Never commit keys to version control
3. Use environment variables
4. Implement key encryption at rest

```python
# Secure key storage
import os
from cryptography.fernet import Fernet

class SecureKeyStore:
    def __init__(self):
        self.cipher = Fernet(os.getenv('MASTER_KEY'))
    
    def encrypt_key(self, key: str) -> str:
        return self.cipher.encrypt(key.encode()).decode()
    
    def decrypt_key(self, encrypted: str) -> str:
        return self.cipher.decrypt(encrypted.encode()).decode()
```

### OAuth 2.0 Token Security

**Token Storage:**
- Encrypt tokens at rest
- Use secure session management
- Implement token rotation
- Monitor for token leakage

**Refresh Token Flow:**
```python
async def refresh_access_token(refresh_token: str) -> dict:
    """Securely refresh OAuth token."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://provider.com/oauth/token',
            data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': os.getenv('CLIENT_ID'),
                'client_secret': os.getenv('CLIENT_SECRET')
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        ) as response:
            return await response.json()
```

---

## Network Security

### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# IP Whitelisting
sudo ufw allow from 203.0.113.0/24 to any port 22
```

### TLS/SSL Configuration

**NGINX SSL Configuration:**
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL protocols
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # CSP
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
}
```

---

## Data Security

### Encryption at Rest

**Database Encryption:**
```sql
-- PostgreSQL encryption
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt sensitive columns
CREATE TABLE sensitive_data (
    id SERIAL PRIMARY KEY,
    data BYTEA NOT NULL,
    encrypted_at TIMESTAMP DEFAULT NOW()
);

-- Insert encrypted data
INSERT INTO sensitive_data (data) 
VALUES (pgp_sym_encrypt('sensitive text', 'encryption_key'));

-- Retrieve decrypted data
SELECT pgp_sym_decrypt(data, 'encryption_key') FROM sensitive_data;
```

**File Encryption:**
```python
from cryptography.fernet import Fernet
import os

def encrypt_file(file_path: str, key: bytes):
    """Encrypt file using Fernet."""
    cipher = Fernet(key)
    
    with open(file_path, 'rb') as f:
        data = f.read()
    
    encrypted = cipher.encrypt(data)
    
    with open(file_path + '.enc', 'wb') as f:
        f.write(encrypted)
```

### Encryption in Transit

**All external API calls must use HTTPS/TLS:**

```python
import aiohttp
import ssl

async def secure_api_call(url: str, data: dict):
    """Make secure API call with TLS verification."""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            json=data,
            ssl=ssl_context
        ) as response:
            return await response.json()
```

---

## Application Security

### Input Validation

```python
from typing import Any
import re

def validate_input(data: Any, data_type: str) -> bool:
    """Validate user input."""
    validators = {
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'phone': r'^\+?1?\d{9,15}$',
        'alphanumeric': r'^[a-zA-Z0-9]+$'
    }
    
    if data_type in validators:
        return bool(re.match(validators[data_type], str(data)))
    return False

def sanitize_input(data: str) -> str:
    """Sanitize user input to prevent injection."""
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", ';', '&', '|']
    for char in dangerous_chars:
        data = data.replace(char, '')
    return data.strip()
```

### SQL Injection Prevention

**Always use parameterized queries:**

```python
# BAD - Vulnerable to SQL injection
query = f"SELECT * FROM users WHERE email = '{email}'"

# GOOD - Parameterized query
query = "SELECT * FROM users WHERE email = %s"
cursor.execute(query, (email,))
```

### Password Security

```python
import bcrypt

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

---

## Audit Logging

### Security Event Logging

```python
import logging
import json
from datetime import datetime

class SecurityLogger:
    """Log security-relevant events."""
    
    def __init__(self):
        self.logger = logging.getLogger('security')
        handler = logging.FileHandler('/var/log/goldstandard/security.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_auth_attempt(self, user: str, success: bool, ip: str):
        """Log authentication attempt."""
        event = {
            'event_type': 'authentication',
            'user': user,
            'success': success,
            'ip_address': ip,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if success:
            self.logger.info(json.dumps(event))
        else:
            self.logger.warning(json.dumps(event))
    
    def log_api_access(self, endpoint: str, user: str, method: str):
        """Log API access."""
        event = {
            'event_type': 'api_access',
            'endpoint': endpoint,
            'user': user,
            'method': method,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.logger.info(json.dumps(event))
```

---

## Security Checklist

### Pre-Deployment

- [ ] All API keys rotated and secured
- [ ] SSH password authentication disabled
- [ ] Firewall configured and enabled
- [ ] SSL/TLS certificates installed
- [ ] Database encryption enabled
- [ ] Audit logging configured
- [ ] Security headers configured
- [ ] Input validation implemented
- [ ] Rate limiting enabled
- [ ] Backup encryption configured

### Regular Maintenance

- [ ] Review access logs weekly
- [ ] Rotate API keys quarterly
- [ ] Update dependencies monthly
- [ ] Review firewall rules monthly
- [ ] Test backup restoration quarterly
- [ ] Security audit annually
- [ ] Penetration testing annually

---

## Incident Response

### Security Incident Procedure

1. **Detection**: Monitor logs and alerts
2. **Assessment**: Determine scope and impact
3. **Containment**: Isolate affected systems
4. **Eradication**: Remove threat
5. **Recovery**: Restore systems
6. **Post-Incident**: Review and improve

### Contact Information

**Security Team**: security@goldstandard.enterprise  
**Emergency Hotline**: +1-XXX-XXX-XXXX

---

**Document Version:** 1.0.0  
**Last Updated:** January 2026
