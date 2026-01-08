# Discord Bot Guide

Complete guide for Discord bot setup, commands, and features.

## Setup

### 1. Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application", name it
3. Go to "Bot" section, click "Add Bot"
4. Copy bot token
5. Enable these **Privileged Gateway Intents**:
   - Presence Intent
   - Server Members Intent
   - Message Content Intent
6. Go to "OAuth2" → "URL Generator"
   - Scopes: `bot`, `applications.commands`
   - Permissions: Administrator (or specific permissions)
7. Copy generated URL, invite bot to your server

### 2. Configure Bot

```bash
cd arty/discord
cp .env.example .env
cp config.example.json config.json
```

**Edit `.env`:**
```env
DISCORD_TOKEN=your_bot_token_here
CLIENT_ID=your_application_id
GUILD_ID=your_server_id
OWNER_ID=your_discord_user_id
```

**Get IDs:**
- Enable Developer Mode in Discord (Settings → Advanced)
- Right-click server/user → Copy ID

**Edit `config.json`:**
```json
{
  "prefix": "!",
  "features": {
    "welcome": {
      "enabled": true,
      "channelId": "channel_id_here",
      "message": "Welcome {user} to {server}!"
    },
    "goodbye": {
      "enabled": true,
      "channelId": "channel_id_here"
    },
    "automod": {
      "enabled": true,
      "maxMentions": 5,
      "maxEmoji": 10
    },
    "economy": {
      "enabled": true,
      "dailyReward": 100
    },
    "leveling": {
      "enabled": true,
      "xpPerMessage": 15,
      "cooldown": 60
    }
  }
}
```

### 3. Deploy Commands

```bash
npm install
npm run deploy-commands
```

### 4. Start Bot

```bash
npm start
```

## Commands

### Moderation (5)

**`/kick <user> [reason]`**
- Kick user from server
- Requires: Kick Members permission

**`/ban <user> [reason] [duration]`**
- Ban user permanently or temporarily
- Duration: `1d`, `7d`, `30d`, etc.
- Requires: Ban Members permission

**`/warn <user> <reason>`**
- Issue warning to user
- Auto-action after threshold (config)
- Requires: Moderate Members permission

**`/timeout <user> <duration> [reason]`**
- Timeout user (Discord native)
- Duration: `1m`, `1h`, `1d`, etc.
- Requires: Moderate Members permission

**`/clear <amount>`**
- Bulk delete messages (1-100)
- Requires: Manage Messages permission

### Utility (6)

**`/help [command]`**
- Show all commands or specific help
- Available to everyone

**`/ping`**
- Check bot latency
- Available to everyone

**`/level [user]`**
- Show level and XP
- Available to everyone

**`/serverinfo`**
- Server statistics and info
- Available to everyone

**`/userinfo [user]`**
- User information and stats
- Available to everyone

**`/avatar [user]`**
- Display user avatar
- Available to everyone

### Economy (2)

**`/balance [user]`**
- Check currency balance
- Shows wallet + bank
- Available to everyone

**`/daily`**
- Claim daily reward
- Cooldown: 24 hours
- Available to everyone

### Admin (1)

**`/setup <feature> <action> [value]`**
- Configure bot features
- Features: `welcome`, `goodbye`, `logs`, `modlogs`, `prefix`
- Actions: `enable`, `disable`, `set`, `view`
- Requires: Administrator permission

### Fun (1)

**`/roll [sides]`**
- Roll dice (default: 6 sides)
- Available to everyone

## Features

### Auto-Moderation

Automatically detects and acts on:
- **Spam**: Repeated messages
- **Excessive mentions**: @mentions > threshold
- **Excessive emoji**: Emoji > threshold
- **Bad words**: Configurable word filter
- **Invite links**: Discord invite detection

**Actions:**
- Delete message
- Warn user
- Timeout user
- Log incident

### Economy System

- **Currency**: Earn from daily rewards, work
- **Wallet**: Active currency
- **Bank**: Stored currency
- **Transactions**: Send, receive, spend
- **Shop**: (Framework ready)

### Leveling System

- **XP from messages**: 15 XP per message (configurable)
- **Cooldown**: 60 seconds between XP gains
- **Level calculation**: `level = floor(sqrt(xp / 100))`
- **Role rewards**: Auto-assign roles at levels
- **Leaderboard**: Top users by level/XP

### Welcome/Goodbye

- **Custom messages**: Embed or plain text
- **Variables**: `{user}`, `{server}`, `{memberCount}`
- **Auto-role**: Assign roles on join
- **DM option**: Send welcome DM

### Logging

Logs all events to configured channels:
- **Message logs**: Delete, edit
- **Member logs**: Join, leave, ban, unban
- **Moderation logs**: Warns, kicks, bans, timeouts
- **Voice logs**: Join, leave, move

### Research Integration

**Intelligent Engagement:**
- Topics extracted from research database
- Messages sent every 3 hours
- Context-aware responses
- Maintains 5-message conversation window

**Configuration:**
```json
{
  "engagement": {
    "discord": {
      "enabled": true,
      "frequency": "3h",
      "topicsPerCycle": 5,
      "contextWindow": 5
    }
  }
}
```

**How it works:**
1. Research engine generates topics
2. Bot posts topic every 3 hours
3. Bot reads user responses
4. Bot responds using research knowledge
5. Maintains conversation context

## Testing

```bash
npm test
```

Runs 47 comprehensive tests covering:
- Configuration validation
- Command functionality
- Event handling
- Database operations
- Auto-moderation
- Economy/leveling systems

## Common Issues

**Bot doesn't respond:**
- Check token validity
- Verify intents enabled
- Ensure bot has permissions
- Check command deployment

**Commands not showing:**
- Run `npm run deploy-commands`
- Wait 1 hour for global commands
- Use GUILD_ID for instant testing

**Auto-mod not working:**
- Enable in config.json
- Check bot role hierarchy
- Verify permissions

See [Troubleshooting](TROUBLESHOOTING.md) for more solutions.

## Production Deployment

See [Deployment Guide](DEPLOYMENT.md) for PM2 setup and production best practices.
