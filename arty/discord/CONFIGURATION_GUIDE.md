# Configuration and Environment Variables - Edit Locations

This document tells you exactly where to make changes to configure your Discord bot.

## 📍 Files You Need to Edit

### 1. Environment Variables (.env)

**Location:** `/home/runner/work/gladius/gladius/discord-bot/.env`

**How to create:**
```bash
cd /home/runner/work/gladius/gladius/discord-bot
cp .env.example .env
nano .env
```

**What to edit:**

| Variable | What to Put | Where to Get It |
|----------|-------------|----------------|
| `DISCORD_TOKEN` | Your bot's token | Discord Developer Portal → Bot tab → Reset Token |
| `CLIENT_ID` | Your application ID | Discord Developer Portal → OAuth2 tab → Client ID |
| `GUILD_ID` | Your server ID | Right-click server → Copy Server ID (need Dev Mode on) |
| `OWNER_ID` | Your Discord user ID | Right-click your name → Copy User ID |
| `PREFIX` | Command prefix (e.g., `!`) | Your choice (default: `!`) |

**Example .env file (with your actual values):**
```env
DISCORD_TOKEN=YOUR_ACTUAL_TOKEN_HERE
CLIENT_ID=123456789012345678
GUILD_ID=987654321098765432
OWNER_ID=111222333444555666
PREFIX=!
```

### 2. Bot Configuration (config.json)

**Location:** `/home/runner/work/gladius/gladius/discord-bot/config.json`

**How to create:**
```bash
cd /home/runner/work/gladius/gladius/discord-bot
cp config.example.json config.json
nano config.json
```

**What to edit:**

#### Bot Information
```json
{
  "bot": {
    "name": "Your Bot Name",           ← Change this
    "description": "Your description", ← Change this
    "prefix": "!",                     ← Change this (optional)
    "embedColor": "#5865F2",           ← Change color (optional)
    "ownerIds": ["YOUR_USER_ID"],      ← Add your user ID
    "supportServerId": "",             ← Add support server ID (optional)
    "inviteUrl": ""                    ← Add bot invite URL (optional)
  }
}
```

#### Enable/Disable Features
```json
{
  "features": {
    "music": { "enabled": true },      ← Change to false to disable
    "economy": { "enabled": true },    ← Change to false to disable
    "leveling": { "enabled": true },   ← Change to false to disable
    "automod": { "enabled": true },    ← Change to false to disable
    "welcome": { "enabled": true },    ← Change to false to disable
    "logging": { "enabled": true }     ← Change to false to disable
  }
}
```

#### Welcome Messages
```json
{
  "features": {
    "welcome": {
      "enabled": true,
      "channelId": "CHANNEL_ID_HERE",           ← Add your channel ID
      "message": "Welcome {user} to {server}!", ← Customize message
      "embedEnabled": true,                     ← true for embed, false for text
      "embedTitle": "Welcome!",                 ← Customize title
      "embedDescription": "Thanks for joining!" ← Customize description
    }
  }
}
```

#### Logging Channels
```json
{
  "features": {
    "logging": {
      "enabled": true,
      "channels": {
        "moderation": "CHANNEL_ID_HERE",  ← Add mod log channel ID
        "messages": "CHANNEL_ID_HERE",    ← Add message log channel ID
        "members": "CHANNEL_ID_HERE",     ← Add member log channel ID
        "server": "CHANNEL_ID_HERE",      ← Add server log channel ID
        "voice": "CHANNEL_ID_HERE"        ← Add voice log channel ID
      }
    }
  }
}
```

#### Economy Settings
```json
{
  "features": {
    "economy": {
      "enabled": true,
      "currency": {
        "name": "coins",        ← Change currency name
        "symbol": "🪙"         ← Change currency symbol
      },
      "dailyReward": 100,      ← Change daily reward amount
      "workReward": {
        "min": 50,             ← Change minimum work reward
        "max": 200             ← Change maximum work reward
      }
    }
  }
}
```

#### Auto-Moderation Rules
```json
{
  "features": {
    "automod": {
      "enabled": true,
      "maxMentions": 5,        ← Change max mentions before deletion
      "maxEmoji": 10,          ← Change max emojis before deletion
      "maxLines": 20,          ← Change max lines before deletion
      "spamThreshold": 5,      ← Change spam detection threshold
      "badWords": [],          ← Add bad words: ["word1", "word2"]
      "linkWhitelist": []      ← Add allowed domains
    }
  }
}
```

## 🔄 After Making Changes

### If you edited .env:
```bash
# Stop the bot (Ctrl+C if running)
# Restart it
npm start
```

### If you edited config.json:
```bash
# Stop the bot (Ctrl+C if running)
# Restart it
npm start
```

### If you're using PM2:
```bash
pm2 restart gladius-bot
```

## 📋 Quick Setup Checklist

- [ ] Copy `.env.example` to `.env`
- [ ] Add `DISCORD_TOKEN` to `.env`
- [ ] Add `CLIENT_ID` to `.env`
- [ ] Add `GUILD_ID` to `.env`
- [ ] Add `OWNER_ID` to `.env`
- [ ] Copy `config.example.json` to `config.json`
- [ ] Customize bot name in `config.json`
- [ ] Set up welcome channel in `config.json` (optional)
- [ ] Set up logging channels in `config.json` (optional)
- [ ] Run `npm install`
- [ ] Run `npm run deploy-commands`
- [ ] Run `npm start`

## 🎯 Common Edits

### Change Bot Prefix
**Edit:** `.env` → Change `PREFIX=!` to your preferred prefix

### Change Welcome Message
**Edit:** `config.json` → Find `features.welcome.message`

### Add Bad Words Filter
**Edit:** `config.json` → Find `features.automod.badWords` → Add words

### Change Currency Name
**Edit:** `config.json` → Find `features.economy.currency.name`

### Enable/Disable a Feature
**Edit:** `config.json` → Find `features.[feature].enabled` → Set to `true` or `false`

## 📁 File Summary

| File | Purpose | Must Edit? |
|------|---------|-----------|
| `.env` | Secrets and tokens | ✅ Yes |
| `config.json` | Bot behavior and features | ✅ Yes |
| `package.json` | Dependencies | ❌ No |
| `src/index.js` | Main bot code | ❌ No |
| Other `.js` files | Bot functionality | ❌ No |

## ⚠️ Important Notes

1. **NEVER share your .env file** - It contains your bot token
2. **NEVER commit .env to git** - It's already in .gitignore
3. **Always restart the bot** after changing .env or config.json
4. **Keep backups** of your working .env and config.json files
5. **Test changes** in a test server before production

## 🆘 Getting Channel/Role IDs

### Enable Developer Mode
1. Open Discord
2. User Settings → Advanced
3. Enable "Developer Mode"

### Get Channel ID
1. Right-click any channel
2. Click "Copy Channel ID"

### Get Role ID
1. Server Settings → Roles
2. Right-click any role
3. Click "Copy Role ID"

### Get User ID
1. Right-click any user
2. Click "Copy User ID"

## 📞 Support

If you need help:
1. Check logs in `/home/runner/work/gladius/gladius/discord-bot/logs/`
2. Read the error messages carefully
3. Verify all IDs are correct
4. Ensure bot has proper permissions

---

**Remember:** Only edit `.env` and `config.json` - everything else is code!
