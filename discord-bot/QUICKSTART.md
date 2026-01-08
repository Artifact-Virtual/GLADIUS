# Quick Start Guide

Get your Discord bot up and running in 5 minutes!

## Prerequisites
- Node.js v18+ installed
- A Discord account
- A Discord server where you have admin permissions

## 1. Get Discord Bot Credentials (2 minutes)

### Create Bot Application
1. Visit [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** → Name it → **"Create"**
3. Go to **"Bot"** tab → **"Add Bot"** → **"Yes, do it!"**
4. Click **"Reset Token"** → **Copy the token** (save it!)
5. Enable these intents:
   - ☑️ Presence Intent
   - ☑️ Server Members Intent  
   - ☑️ Message Content Intent
6. **Save Changes**

### Get IDs
- **Client ID**: Go to "OAuth2" tab → Copy "Client ID"
- **Guild ID**: In Discord → Enable Developer Mode (User Settings → Advanced) → Right-click your server → Copy Server ID
- **Owner ID**: Right-click your username → Copy User ID

### Invite Bot
1. In "OAuth2" → "URL Generator"
2. Select: `bot` + `applications.commands`
3. Permissions: Select `Administrator`
4. Copy URL → Open in browser → Select server → Authorize

## 2. Configure the Bot (1 minute)

```bash
cd /home/runner/work/gladius/gladius/discord-bot

# Copy and edit environment file
cp .env.example .env
nano .env
```

**Update these 4 lines in .env:**
```env
DISCORD_TOKEN=paste_your_token_here
CLIENT_ID=paste_your_client_id_here
GUILD_ID=paste_your_guild_id_here
OWNER_ID=paste_your_user_id_here
```

Save: `Ctrl+O` → `Enter` → `Ctrl+X`

```bash
# Copy configuration file
cp config.example.json config.json
```

## 3. Install & Deploy (1 minute)

```bash
# Install dependencies
npm install

# Deploy commands to your server (instant)
npm run deploy-commands
```

## 4. Start the Bot (30 seconds)

```bash
npm start
```

You should see:
```
Bot is ready! Logged in as YourBot#1234
Connected to 1 guilds
Loaded X commands
```

## 5. Test It! (30 seconds)

In your Discord server, type:
```
/ping
```

or

```
!help
```

🎉 **Your bot is now running!**

## What's Next?

### Customize Welcome Messages
1. Create a welcome channel
2. Copy its channel ID (right-click channel → Copy Channel ID)
3. Edit `config.json`:
```json
{
  "features": {
    "welcome": {
      "enabled": true,
      "channelId": "YOUR_CHANNEL_ID_HERE"
    }
  }
}
```
4. Restart bot

### Set Up Logging
1. Create log channels: #mod-logs, #message-logs, #member-logs
2. Copy their IDs
3. Edit `config.json`:
```json
{
  "features": {
    "logging": {
      "enabled": true,
      "channels": {
        "moderation": "MOD_LOG_CHANNEL_ID",
        "messages": "MESSAGE_LOG_CHANNEL_ID",
        "members": "MEMBER_LOG_CHANNEL_ID"
      }
    }
  }
}
```
4. Restart bot

### Enable Features

Edit `config.json` to enable/disable features:
```json
{
  "features": {
    "economy": { "enabled": true },
    "leveling": { "enabled": true },
    "automod": { "enabled": true },
    "welcome": { "enabled": true },
    "logging": { "enabled": true }
  }
}
```

## Essential Commands

### Moderation
- `/kick @user [reason]` - Kick a member
- `/ban @user [reason]` - Ban a member
- `/warn @user reason` - Warn a member

### Utility
- `/ping` - Check bot latency
- `/help` - Show all commands
- `/serverinfo` - Server information
- `/level [@user]` - Check level/rank

### Economy
- `/balance [@user]` - Check balance
- `/daily` - Claim daily reward

### Prefix Commands (also work!)
- `!ping`, `!help`, `!kick`, `!ban`, etc.

## Troubleshooting

**Bot offline?**
- Check your token in `.env`
- Make sure you saved the file

**Commands not working?**
- Run `npm run deploy-commands`
- Wait 1-2 minutes

**Permission errors?**
- Make sure bot has Administrator permission
- Check bot's role is above other roles

## Running in Background

### Option 1: Use screen
```bash
screen -S discord-bot
npm start
# Press Ctrl+A then D to detach
# To reattach: screen -r discord-bot
```

### Option 2: Use PM2 (recommended)
```bash
npm install -g pm2
pm2 start src/index.js --name gladius-bot
pm2 save
pm2 startup
```

## Need More Help?

- Read [README.md](README.md) for full feature documentation
- Read [SETUP.md](SETUP.md) for detailed setup guide
- Check logs in `logs/` directory

---

**That's it!** Your bot is ready to manage your Discord server. 🚀

Configure more features in `config.json` as you explore!
