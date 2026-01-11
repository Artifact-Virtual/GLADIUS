# Troubleshooting Guide

Common issues and solutions for all Arty modules.

## General Issues

### Installation Fails

**Problem:** `npm install` fails with errors

**Solutions:**
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules
rm -rf node_modules package-lock.json

# Reinstall
npm install

# Try with legacy peer deps
npm install --legacy-peer-deps
```

### Node Version Issues

**Problem:** Incompatible Node.js version

**Solution:**
```bash
# Check version
node --version

# Install Node 18 LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify
node --version  # Should be 18.x or higher
```

### Database Locked

**Problem:** `Error: database is locked`

**Solutions:**
```bash
# Find process using database
fuser store/research.db

# Kill process
kill -9 <PID>

# Or restart all services
pm2 restart all
```

### Permission Denied

**Problem:** `EACCES: permission denied`

**Solutions:**
```bash
# Fix ownership
sudo chown -R $USER:$USER /path/to/arty

# Fix permissions
chmod 755 /path/to/arty
chmod 600 /path/to/arty/*/.env
chmod 644 /path/to/arty/*/config.json
```

## Discord Bot Issues

### Bot Doesn't Start

**Problem:** Bot crashes on startup

**Check:**
```bash
# View logs
pm2 logs arty-discord

# Or run directly
cd discord
node src/index.js
```

**Common causes:**
- Invalid token
- Missing intents
- Missing dependencies
- Database connection failure

**Solutions:**
```bash
# Verify token
echo $DISCORD_TOKEN

# Check .env file
cat discord/.env

# Reinstall dependencies
cd discord
rm -rf node_modules
npm install

# Initialize database
cd ../store
node init-databases.js
```

### Bot Not Responding

**Problem:** Bot online but doesn't respond to commands

**Solutions:**

1. **Check intents** in `discord/src/index.js`:
```javascript
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,  // Required!
    // ... other intents
  ]
});
```

2. **Deploy commands:**
```bash
cd discord
npm run deploy-commands
```

3. **Check bot permissions:**
- Administrator (or specific permissions)
- Role hierarchy (bot role above others)

4. **Verify command registration:**
```bash
# In Discord, type /
# Commands should appear in autocomplete
```

### Slash Commands Not Showing

**Problem:** `/command` doesn't show in Discord

**Solutions:**

1. **Deploy commands:**
```bash
cd discord
npm run deploy-commands
```

2. **Wait for propagation:**
- Guild commands: Instant
- Global commands: Up to 1 hour

3. **Use GUILD_ID for testing:**
```env
# In .env
GUILD_ID=your_test_server_id
```

4. **Check bot permissions:**
- Must have `applications.commands` scope

### Auto-Moderation Not Working

**Problem:** Auto-mod doesn't trigger

**Solutions:**

1. **Enable in config:**
```json
{
  "features": {
    "automod": {
      "enabled": true,
      "spam": { "enabled": true },
      "mentions": { "enabled": true }
    }
  }
}
```

2. **Check bot role position:**
- Bot role must be above target user roles
- Can't moderate server owner

3. **Verify permissions:**
- Manage Messages
- Moderate Members
- Kick Members (for kick action)

## LinkedIn Issues

### Authentication Failed

**Problem:** `401 Unauthorized` or `Invalid access token`

**Solutions:**

1. **Verify token:**
```bash
curl -X GET 'https://api.linkedin.com/v2/me' \
  -H "Authorization: Bearer $LINKEDIN_ACCESS_TOKEN"
```

2. **Token expired (90 days):**
- Regenerate access token
- Implement token refresh

3. **Check scopes:**
```env
# Required scopes
w_member_social
r_liteprofile
r_emailaddress
```

4. **Regenerate token:**
- Go to LinkedIn Developers
- Create new access token
- Update .env file

### Post Failed

**Problem:** Post creation fails

**Common causes:**
- Rate limit exceeded
- Invalid media format
- Content too long
- Missing required fields

**Solutions:**

1. **Check rate limits:**
```bash
sqlite3 linkedin/data/linkedin.db
SELECT * FROM rate_limits ORDER BY timestamp DESC LIMIT 10;
```

2. **Verify content length:**
```javascript
// Text posts: max 3,000 chars
console.log(content.length);
```

3. **Check media format:**
```bash
# Image: JPG, PNG, GIF, max 5MB
file image.jpg

# Video: MP4, AVI, MOV, max 200MB, 10 min
ffprobe video.mp4
```

4. **Review error logs:**
```bash
tail -f linkedin/logs/linkedin-$(date +%Y-%m-%d).log
```

### Scheduler Not Running

**Problem:** Scheduled posts not publishing

**Solutions:**

1. **Check service status:**
```bash
pm2 status arty-linkedin
pm2 logs arty-linkedin
```

2. **Verify scheduled posts:**
```bash
sqlite3 linkedin/data/linkedin.db
SELECT * FROM scheduled_posts WHERE status = 'pending';
```

3. **Check schedule times:**
```bash
# Times in UTC
SELECT scheduled_time FROM scheduled_posts 
WHERE status = 'pending' 
ORDER BY scheduled_time;
```

4. **Restart scheduler:**
```bash
pm2 restart arty-linkedin
```

## Research Engine Issues

### No Search Results

**Problem:** Research cycle returns no results

**Solutions:**

1. **Verify API key:**
```bash
# Test Brave Search
curl "https://api.search.brave.com/res/v1/web/search?q=test" \
  -H "X-Subscription-Token: $BRAVE_SEARCH_API_KEY"
```

2. **Check API limits:**
- Brave: 2,000/month free
- Serper: 2,500/month free
- SerpAPI: 100/month free

3. **Review configuration:**
```json
{
  "research": {
    "broadField": "must not be empty",
    "maxResultsPerSearch": 20
  }
}
```

4. **Check logs:**
```bash
tail -f research/logs/research-$(date +%Y-%m-%d).log
```

### Few Keywords Extracted

**Problem:** Only extracting 1-2 keywords

**Solutions:**

1. **Increase iterations:**
```json
{
  "research": {
    "iterations": 5,
    "keywordsPerIteration": 15
  }
}
```

2. **Lower threshold:**
```json
{
  "analysis": {
    "tfidfThreshold": 0.3,
    "minKeywordFrequency": 2
  }
}
```

3. **Check content quality:**
```bash
sqlite3 store/research.db
SELECT COUNT(*) FROM articles;
SELECT keyword, frequency FROM keywords ORDER BY frequency DESC LIMIT 20;
```

### Storage Full

**Problem:** Disk space exhausted

**Solutions:**

1. **Check disk usage:**
```bash
df -h
du -sh arty/store/*
```

2. **Run cleanup:**
```bash
cd research
npm run cleanup

# Or manual cleanup
find store/file_system/articles -mtime +30 -delete
find */logs -name "*.log" -mtime +60 -delete
```

3. **Vacuum databases:**
```bash
sqlite3 store/research.db "VACUUM;"
sqlite3 discord/data/discord.db "VACUUM;"
sqlite3 linkedin/data/linkedin.db "VACUUM;"
```

## Database Issues

### Corruption

**Problem:** `database disk image is malformed`

**Solutions:**

1. **Restore from backup:**
```bash
cp backups/research_20260108.db store/research.db
```

2. **Export and reimport:**
```bash
sqlite3 store/research.db .dump > dump.sql
mv store/research.db store/research.db.old
sqlite3 store/research.db < dump.sql
```

3. **Check integrity:**
```bash
sqlite3 store/research.db "PRAGMA integrity_check;"
```

### Slow Queries

**Problem:** Database operations very slow

**Solutions:**

1. **Analyze and optimize:**
```bash
sqlite3 store/research.db "ANALYZE;"
sqlite3 store/research.db "VACUUM;"
```

2. **Check indexes:**
```sql
SELECT * FROM sqlite_master WHERE type = 'index';
```

3. **Add indexes if missing:**
```sql
CREATE INDEX IF NOT EXISTS idx_keywords_relevance ON keywords(relevance);
CREATE INDEX IF NOT EXISTS idx_articles_created ON articles(created_at);
```

## Performance Issues

### High Memory Usage

**Problem:** Process using excessive memory

**Solutions:**

1. **Check memory:**
```bash
pm2 monit
top -p $(pgrep -f "node")
```

2. **Restart processes:**
```bash
pm2 restart all
```

3. **Increase memory limit:**
```javascript
// In ecosystem.config.js
max_memory_restart: '1G'
```

4. **Optimize batch size:**
```json
{
  "research": {
    "maxResultsPerSearch": 10,  // Reduce from 20
    "keywordsPerIteration": 5   // Reduce from 10
  }
}
```

### High CPU Usage

**Problem:** Process consuming 100% CPU

**Solutions:**

1. **Check for infinite loops:**
```bash
pm2 logs arty-research --lines 100
```

2. **Review cron jobs:**
```json
{
  "research": {
    "cycleFrequency": "daily"  // Not "1s"
  }
}
```

3. **Limit iterations:**
```json
{
  "research": {
    "iterations": 3  // Not 100
  }
}
```

## Logging Issues

### Logs Not Rotating

**Problem:** Log files grow too large

**Solutions:**

1. **Configure rotation:**
```json
{
  "logging": {
    "maxFiles": "14d",
    "maxSize": "20m"
  }
}
```

2. **Manual rotation:**
```bash
find */logs -name "*.log" -size +100M -delete
```

3. **Setup logrotate:**
```bash
# See DEPLOYMENT.md for logrotate config
sudo nano /etc/logrotate.d/arty
```

### Can't Find Logs

**Problem:** Log files missing or empty

**Solutions:**

1. **Check log path:**
```bash
ls -la discord/logs/
ls -la linkedin/logs/
ls -la research/logs/
```

2. **Verify permissions:**
```bash
chmod 755 discord/logs
chmod 644 discord/logs/*.log
```

3. **Check logging config:**
```json
{
  "logging": {
    "enabled": true,
    "level": "info"  // Not "silent"
  }
}
```

## Network Issues

### Connection Timeout

**Problem:** API calls timing out

**Solutions:**

1. **Check internet connection:**
```bash
ping -c 4 google.com
curl -I https://api.linkedin.com
```

2. **Increase timeout:**
```json
{
  "api": {
    "timeout": 30000  // 30 seconds
  }
}
```

3. **Check firewall:**
```bash
sudo ufw status
sudo ufw allow out 443/tcp
```

### Rate Limited

**Problem:** `429 Too Many Requests`

**Solutions:**

1. **Check rate limits:**
```bash
sqlite3 linkedin/data/linkedin.db
SELECT * FROM rate_limits ORDER BY timestamp DESC LIMIT 10;
```

2. **Enable backoff:**
```json
{
  "rateLimits": {
    "backoff": {
      "enabled": true,
      "multiplier": 2
    }
  }
}
```

3. **Reduce frequency:**
```json
{
  "research": {
    "cycleFrequency": "2d"  // Instead of "daily"
  }
}
```

## Getting Help

If issues persist:

1. **Check logs:**
```bash
pm2 logs
tail -f */logs/*.log
```

2. **Enable debug mode:**
```bash
DEBUG=* npm start
```

3. **Review documentation:**
- [Quick Start](QUICKSTART.md)
- [Configuration](CONFIGURATION.md)
- Module guides: [Discord](DISCORD.md), [LinkedIn](LINKEDIN.md), [Research](RESEARCH.md)

4. **Test suite:**
```bash
npm test
```

5. **Create issue:**
- Include logs
- Describe steps to reproduce
- List environment details
