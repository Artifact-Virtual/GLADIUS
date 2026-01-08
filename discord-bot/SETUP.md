# Discord Bot Setup Guide

This guide will help you set up and configure the Gladius Discord Bot.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Getting a Discord Bot Token](#getting-a-discord-bot-token)
3. [Environment Variables Setup](#environment-variables-setup)
4. [Configuration File Setup](#configuration-file-setup)
5. [Installing Dependencies](#installing-dependencies)
6. [Deploying Commands](#deploying-commands)
7. [Running the Bot](#running-the-bot)

## Prerequisites

- **Node.js** v18.0.0 or higher
- **npm** (comes with Node.js)
- **A Discord account**
- **A Linux server** (as specified in requirements)

## Getting a Discord Bot Token

### Step 1: Create a Discord Application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Give your application a name (e.g., "Gladius Bot")
4. Click "Create"

### Step 2: Create a Bot User

1. In your application, go to the "Bot" tab in the left sidebar
2. Click "Add Bot"
3. Confirm by clicking "Yes, do it!"
4. Under the bot's username, click "Reset Token" to reveal your bot token
5. **IMPORTANT**: Copy this token and save it securely. You'll need it for the `.env` file.
6. Never share your bot token publicly!

### Step 3: Configure Bot Settings

1. Under "Privileged Gateway Intents", enable:
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent
2. Click "Save Changes"

### Step 4: Get Your Client ID

1. Go to the "OAuth2" tab
2. Copy your "Client ID" - you'll need this for the `.env` file

### Step 5: Invite the Bot to Your Server

1. Still in the "OAuth2" tab, go to "URL Generator"
2. Under "Scopes", select:
   - `bot`
   - `applications.commands`
3. Under "Bot Permissions", select:
   - `Administrator` (recommended for full functionality)
   - Or select individual permissions as needed
4. Copy the generated URL at the bottom
5. Open the URL in your browser and select your server
6. Click "Authorize"

### Step 6: Get Your Guild ID

1. Open Discord
2. Go to User Settings → Advanced
3. Enable "Developer Mode"
4. Right-click your server icon
5. Click "Copy Server ID"

### Step 7: Get Your User ID (Owner ID)

1. With Developer Mode enabled
2. Right-click your username
3. Click "Copy User ID"

## Environment Variables Setup

### Step 1: Create .env File

Navigate to the `discord-bot` directory and create a `.env` file from the example:

```bash
cd /home/runner/work/gladius/gladius/discord-bot
cp .env.example .env
```

### Step 2: Edit .env File

Open the `.env` file and fill in your values:

```bash
nano .env
```

### Required Variables

Replace these values with your actual credentials:

```env
# REQUIRED: Your bot token from Discord Developer Portal
DISCORD_TOKEN=YOUR_ACTUAL_BOT_TOKEN_HERE

# REQUIRED: Your application's client ID
CLIENT_ID=YOUR_CLIENT_ID_HERE

# REQUIRED: Your Discord server/guild ID (for testing commands)
GUILD_ID=YOUR_GUILD_ID_HERE

# Bot Configuration
PREFIX=!
OWNER_ID=YOUR_USER_ID_HERE
```

### Example .env File

Here's what a filled-in `.env` file looks like (with fake values):

```env
DISCORD_TOKEN=YOUR_BOT_TOKEN_HERE_REPLACE_THIS
CLIENT_ID=1234567890123456789
GUILD_ID=9876543210987654321
PREFIX=!
OWNER_ID=1122334455667788990

# Database
DATABASE_PATH=./data/bot.db

# Logging
LOG_LEVEL=info
LOG_DIR=./logs

# Features
ENABLE_MUSIC=true
ENABLE_ECONOMY=true
ENABLE_LEVELING=true
```

### Optional Variables

These are optional but enhance functionality:

```env
# Webhook URLs for logging/notifications
WEBHOOK_LOG_URL=https://discord.com/api/webhooks/...
WEBHOOK_MODERATION_URL=https://discord.com/api/webhooks/...
WEBHOOK_ANNOUNCEMENTS_URL=https://discord.com/api/webhooks/...

# Music APIs (optional)
YOUTUBE_API_KEY=your_youtube_api_key
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# Other APIs (optional)
WEATHER_API_KEY=your_weather_api_key
GIPHY_API_KEY=your_giphy_api_key
```

## Configuration File Setup

### Step 1: Create config.json

```bash
cp config.example.json config.json
```

### Step 2: Edit config.json

Open and customize the configuration:

```bash
nano config.json
```

### Key Configuration Sections

#### Bot Information

```json
{
  "bot": {
    "name": "Gladius Bot",
    "description": "Your bot description",
    "prefix": "!",
    "embedColor": "#5865F2",
    "ownerIds": ["YOUR_USER_ID"]
  }
}
```

#### Welcome Messages

To enable welcome messages:

1. Create a channel for welcome messages
2. Right-click the channel → Copy Channel ID
3. Add to config.json:

```json
{
  "features": {
    "welcome": {
      "enabled": true,
      "channelId": "YOUR_WELCOME_CHANNEL_ID",
      "message": "Welcome {user} to {server}!",
      "embedEnabled": true
    }
  }
}
```

#### Logging

To enable logging:

1. Create dedicated log channels
2. Copy their IDs
3. Add to config.json:

```json
{
  "features": {
    "logging": {
      "enabled": true,
      "channels": {
        "moderation": "MOD_LOG_CHANNEL_ID",
        "messages": "MESSAGE_LOG_CHANNEL_ID",
        "members": "MEMBER_LOG_CHANNEL_ID",
        "server": "SERVER_LOG_CHANNEL_ID",
        "voice": "VOICE_LOG_CHANNEL_ID"
      }
    }
  }
}
```

## Installing Dependencies

Install all required packages:

```bash
npm install
```

This will install:
- discord.js - Discord API library
- dotenv - Environment variable loader
- winston - Logging library
- better-sqlite3 - Database
- node-cron - Scheduled tasks
- And more...

## Deploying Commands

Before running the bot, deploy slash commands:

### For Development/Testing (Instant)

Deploy to your test server (uses GUILD_ID from .env):

```bash
npm run deploy-commands
```

### For Production (Takes up to 1 hour)

Deploy globally to all servers:

```bash
npm run deploy-commands -- --global
```

**Note**: Global commands can take up to 1 hour to appear in Discord.

## Running the Bot

### Production Mode

Start the bot normally:

```bash
npm start
```

### Development Mode

Start with auto-restart on file changes:

```bash
npm run dev
```

### Using PM2 (Recommended for Production)

Install PM2:

```bash
npm install -g pm2
```

Start the bot with PM2:

```bash
pm2 start src/index.js --name "gladius-bot"
```

Useful PM2 commands:

```bash
pm2 logs gladius-bot    # View logs
pm2 restart gladius-bot # Restart bot
pm2 stop gladius-bot    # Stop bot
pm2 status              # View status
pm2 startup             # Auto-start on system boot
```

## Verifying the Bot is Running

1. Check the console output for:
   - "Bot is ready! Logged in as [Bot Name]"
   - "Connected to X guilds"
   - "Loaded X commands"

2. In Discord, the bot should appear online

3. Test with a command:
   - Type `!ping` or `/ping`
   - The bot should respond

## Troubleshooting

### Bot is offline
- Check your DISCORD_TOKEN in .env
- Ensure you copied the token correctly
- Make sure you saved the .env file

### Commands not working
- Run `npm run deploy-commands`
- Wait a few minutes
- Ensure bot has proper permissions

### Slash commands not appearing
- Deploy commands with `npm run deploy-commands`
- For guild commands, wait 1-2 minutes
- For global commands, wait up to 1 hour

### Permission errors
- Ensure bot has Administrator permission
- Check role hierarchy (bot's role should be high)
- Verify bot permissions in server settings

### Database errors
- Ensure the `data` directory exists
- Check file permissions
- Try deleting `data/bot.db` and restart

## Where to Edit Configuration

### To change environment variables:
**Edit**: `/home/runner/work/gladius/gladius/discord-bot/.env`

### To change bot configuration:
**Edit**: `/home/runner/work/gladius/gladius/discord-bot/config.json`

### After making changes:
1. Save the files
2. Restart the bot:
   ```bash
   # If running with npm start
   Press Ctrl+C, then run: npm start
   
   # If running with PM2
   pm2 restart gladius-bot
   ```

## Security Best Practices

1. **Never share your .env file** - It contains sensitive tokens
2. **Never commit .env to git** - It's already in .gitignore
3. **Regenerate tokens** if accidentally exposed
4. **Use environment-specific .env files** for dev/prod
5. **Limit bot permissions** to only what's needed
6. **Regularly update dependencies** for security patches

## Next Steps

After setup:

1. Configure features in config.json
2. Set up logging channels
3. Configure welcome/goodbye messages
4. Set up auto-moderation rules
5. Create custom commands
6. Test all features thoroughly

## Getting Help

If you encounter issues:

1. Check the console logs in `logs/` directory
2. Review the README.md for command documentation
3. Verify all configuration values
4. Check Discord API status
5. Review bot permissions

## File Locations Summary

| File | Location | Purpose |
|------|----------|---------|
| .env | `/home/runner/work/gladius/gladius/discord-bot/.env` | Environment variables |
| config.json | `/home/runner/work/gladius/gladius/discord-bot/config.json` | Bot configuration |
| package.json | `/home/runner/work/gladius/gladius/discord-bot/package.json` | Dependencies |
| Database | `/home/runner/work/gladius/gladius/discord-bot/data/bot.db` | SQLite database |
| Logs | `/home/runner/work/gladius/gladius/discord-bot/logs/` | Log files |
| Backups | `/home/runner/work/gladius/gladius/discord-bot/backups/` | Server backups |

---

**Ready to start!** Once configured, your bot will be fully operational with all features enabled.
