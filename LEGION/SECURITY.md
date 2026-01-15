# Security Configuration Guide

## API Keys and Secrets Management

### Environment Variables Required

The following environment variables must be set for the system to function properly:

#### External API Keys (Optional - for dashboard external data)
```bash
# Financial Market Data
export MARKETSTACK_API_KEY="your_marketstack_key"
export POLYGON_API_KEY="your_polygon_key"
export ALPHAVANTAGE_API_KEY="your_alphavantage_key"

# News and Information
export NEWSAPI_KEY="your_newsapi_key"

# Weather Data
export WEATHER_API_KEY="your_openweathermap_key"

# Security APIs
export VIRUSTOTAL_API_KEY="your_virustotal_key"
export ABUSEIPDB_API_KEY="your_abuseipdb_key"

# Space/NASA Data
export NASA_API_KEY="your_nasa_key"
```

#### Backend API Security (Required)
```bash
# Backend API authentication tokens
export API_ADMIN_TOKEN="generate_strong_random_token_here"
export API_MANAGER_TOKEN="generate_strong_random_token_here"  
export API_VIEWER_TOKEN="generate_strong_random_token_here"
```

### Security Best Practices

1. **Never commit `.env` files** - They are already in `.gitignore`
2. **Use strong random tokens** - Generate using: `openssl rand -hex 32`
3. **Rotate API keys regularly** - Update external API keys periodically
4. **Use different tokens per environment** - Dev/staging/prod should have different values
5. **Monitor for secret leaks** - Tools like GitGuardian help detect exposed secrets

### GitGuardian Secret Leak Fix

**COMPLETED**: Removed hardcoded API keys from:
- `/reporting/dashboards/.env` - Replaced with placeholder values
- Removed default token values from `backend_api.py`

### Setting Up Environment Variables

#### For Development (Linux/Mac):
```bash
# Copy the example file
cp reporting/dashboards/.env.example reporting/dashboards/.env

# Edit with your actual keys
nano reporting/dashboards/.env

# Set backend tokens
export API_ADMIN_TOKEN=$(openssl rand -hex 32)
export API_MANAGER_TOKEN=$(openssl rand -hex 32)
export API_VIEWER_TOKEN=$(openssl rand -hex 32)
```

#### For Production:
- Use your deployment platform's environment variable settings
- Never store secrets in code or config files
- Consider using secret management services (AWS Secrets Manager, Azure Key Vault, etc.)

### Emergency Response

If secrets are accidentally committed:
1. **Immediately revoke/regenerate** the exposed keys
2. **Remove from git history** using `git filter-branch` or BFG Repo-Cleaner
3. **Update environment variables** with new keys
4. **Monitor for unauthorized usage** of the old keys

### Contact Information

If you discover a security issue:
- Create a private issue in the repository
- Contact the development team immediately
- Do not publicly disclose until patched

---
**Last Updated**: July 22, 2025  
**Status**: All high entropy secrets removed from codebase

