# Gladius Discord Bot

A comprehensive, autonomous Discord server management bot with extensive features including moderation, economy, leveling, music, tickets, and much more.

## 🌟 Features

### 🛡️ Moderation
- **User Management**: Kick, ban, timeout, warn users
- **Auto-Moderation**: Anti-spam, bad word filtering, link filtering, excessive mentions/emoji detection
- **Temporary Actions**: Temporary bans and mutes with automatic expiration
- **Warning System**: Track and manage user warnings with configurable thresholds
- **Moderation Logs**: Comprehensive logging of all moderation actions

### 🎭 Server Management
- **Role Management**: Assign, remove, and manage roles
- **Channel Management**: Create, delete, and configure channels
- **Reaction Roles**: Self-assignable roles via reactions
- **Welcome/Goodbye Messages**: Customizable messages with embeds
- **Auto-Role**: Automatically assign roles to new members
- **Backup/Restore**: Automatic server backups with restoration capabilities

### 💰 Economy System
- **Virtual Currency**: Full economy system with balance tracking
- **Daily Rewards**: Claim daily coins
- **Work System**: Earn coins through work commands
- **Shop System**: Buy items, roles, and perks
- **Bank System**: Store coins safely
- **Leaderboards**: View top earners

### 📊 Leveling System
- **XP System**: Gain XP from messages with anti-spam cooldown
- **Level Roles**: Automatically assign roles based on level
- **Leaderboards**: View server rankings
- **Customizable**: Configure XP rates and level-up messages

### 🎵 Music System
- **Playback Control**: Play, pause, skip, stop, loop
- **Queue Management**: View and manage music queue
- **YouTube Support**: Play music from YouTube
- **Spotify Support**: Play from Spotify (requires API key)
- **Audio Filters**: Bassboost, nightcore, vaporwave, 8D audio
- **Volume Control**: Adjust playback volume

### 🎫 Ticket System
- **Support Tickets**: Users can create tickets for help
- **Multiple Types**: Support, reports, applications, etc.
- **Transcripts**: Save ticket conversations
- **Staff Notifications**: Alert support staff when tickets are created
- **Ticket Limits**: Prevent spam with per-user limits

### 🎉 Engagement Features
- **Giveaways**: Create and manage giveaways with automatic winner selection
- **Polls**: Create polls with multiple options and automatic result calculation
- **Reminders**: Set reminders for yourself or the server
- **Custom Commands**: Create custom text commands

### 📝 Logging
- **Message Logs**: Deleted and edited messages
- **Member Logs**: Joins, leaves, bans, unbans
- **Server Logs**: Role/channel changes, server updates
- **Voice Logs**: Voice state changes
- **Moderation Logs**: All moderation actions

### 📊 Statistics
- **Real-time Stats**: Live-updating statistics channels
- **Member Count**: Total members, online members, bot count
- **Server Info**: Channel count, role count, and more

### 🔧 Utility
- **Server Info**: Detailed server information
- **User Info**: Detailed user information
- **Role Info**: Role details and members
- **Avatar**: Display user avatars
- **Ping**: Check bot latency and uptime

### 🔗 Webhook Integration
- **Webhook Logging**: Send logs via webhooks
- **Announcements**: Post announcements via webhooks
- **Moderation Webhooks**: Separate moderation logs
- **Welcome Webhooks**: Custom welcome messages

## 📋 Requirements

- **Node.js**: v18.0.0 or higher
- **Discord Bot Token**: From [Discord Developer Portal](https://discord.com/developers/applications)
- **Linux**: Base Linux architecture (as specified)

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/amuzetnoM/gladius.git
cd gladius/discord-bot
```

### 2. Install dependencies

```bash
npm install
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
nano .env
```

**Required variables:**
```env
DISCORD_TOKEN=your_bot_token_here
CLIENT_ID=your_client_id_here
GUILD_ID=your_guild_id_here  # For testing
```

**Edit these variables in your `.env` file:**
- `DISCORD_TOKEN`: Your bot token from Discord Developer Portal
- `CLIENT_ID`: Your bot's application ID
- `GUILD_ID`: Your Discord server ID (for slash command testing)
- `OWNER_ID`: Your Discord user ID

### 4. Configure bot settings

Copy `config.example.json` to `config.json` and customize:

```bash
cp config.example.json config.json
nano config.json
```

**Edit these settings in `config.json`:**
- Bot name, description, and branding
- Enable/disable features
- Configure welcome/goodbye messages
- Set up auto-moderation rules
- Configure economy and leveling settings
- Set up logging channels
- Configure webhook URLs

### 5. Deploy slash commands

For development (instant updates to your test server):
```bash
npm run deploy-commands
```

For production (global commands, takes up to 1 hour):
```bash
npm run deploy-commands -- --global
```

### 6. Start the bot

```bash
npm start
```

For development with auto-restart:
```bash
npm run dev
```

## 🔐 Required Bot Permissions

The bot requires the following permissions:
- `Administrator` (recommended for full functionality)

Or individual permissions:
- Manage Server
- Manage Roles
- Manage Channels
- Kick Members
- Ban Members
- Moderate Members (Timeout)
- Manage Messages
- Read Messages/View Channels
- Send Messages
- Send Messages in Threads
- Embed Links
- Attach Files
- Read Message History
- Add Reactions
- Use External Emojis
- Connect (Voice)
- Speak (Voice)
- Use Voice Activity

## 📁 Project Structure

```
discord-bot/
├── src/
│   ├── commands/          # Command files
│   │   ├── admin/         # Admin commands
│   │   ├── moderation/    # Moderation commands
│   │   ├── utility/       # Utility commands
│   │   ├── fun/          # Fun commands
│   │   ├── economy/      # Economy commands
│   │   └── music/        # Music commands
│   ├── events/           # Event handlers
│   ├── handlers/         # Command/event loaders
│   ├── services/         # Background services
│   ├── utils/            # Utility functions
│   ├── index.js          # Main bot file
│   └── deploy-commands.js # Command deployment
├── config/               # Configuration files
├── data/                # Database files
├── logs/                # Log files
├── backups/             # Server backups
├── .env.example         # Environment variables template
├── config.example.json  # Configuration template
├── package.json         # Dependencies
└── README.md           # This file
```

## 🎮 Usage

### Prefix Commands

Default prefix: `!` (configurable)

Examples:
```
!help              - Show all commands
!ping              - Check bot latency
!kick @user        - Kick a user
!ban @user         - Ban a user
!warn @user reason - Warn a user
```

### Slash Commands

Use `/` to access slash commands:
```
/help              - Show all commands
/ping              - Check bot latency
/kick user:@user   - Kick a user
/ban user:@user    - Ban a user
```

## 🔧 Configuration Guide

### Setting Up Auto-Moderation

Edit `config.json`:
```json
{
  "features": {
    "automod": {
      "enabled": true,
      "maxMentions": 5,
      "maxEmoji": 10,
      "badWords": ["word1", "word2"],
      "actions": {
        "delete": true,
        "warn": true
      }
    }
  }
}
```

### Setting Up Welcome Messages

Edit `config.json`:
```json
{
  "features": {
    "welcome": {
      "enabled": true,
      "channelId": "your_channel_id",
      "message": "Welcome {user} to {server}!",
      "embedEnabled": true
    }
  }
}
```

### Setting Up Webhooks

Edit `.env`:
```env
WEBHOOK_LOG_URL=https://discord.com/api/webhooks/...
WEBHOOK_MODERATION_URL=https://discord.com/api/webhooks/...
```

Edit `config.json`:
```json
{
  "webhooks": {
    "logging": {
      "enabled": true,
      "url": ""  # Uses .env value
    }
  }
}
```

## 🐛 Troubleshooting

### Bot doesn't respond to commands
- Ensure the bot has proper permissions
- Check that slash commands are deployed
- Verify the bot token is correct
- Check console for error messages

### Slash commands not showing up
- Run `npm run deploy-commands`
- Wait a few minutes for Discord to sync
- For global commands, it can take up to 1 hour

### Database errors
- Ensure the `data/` directory exists
- Check file permissions
- Verify SQLite is properly installed

### Music not working
- Install FFmpeg: `sudo apt install ffmpeg`
- Ensure voice permissions are granted
- Check YouTube API limits

## 📊 Database

The bot uses SQLite for data persistence:
- **Location**: `./data/bot.db`
- **Tables**: guilds, economy, levels, warnings, mutes, bans, tickets, giveaways, polls, reminders, etc.
- **Backups**: Automatic daily backups (if enabled)

## 🔄 Updates

To update the bot:

```bash
git pull origin main
npm install
npm run deploy-commands
```

## 📝 Logging

Logs are stored in the `logs/` directory:
- `combined-YYYY-MM-DD.log` - All logs
- `error-YYYY-MM-DD.log` - Error logs only
- `commands-YYYY-MM-DD.log` - Command usage logs

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License.

## ⚠️ Disclaimer

This bot is provided as-is. Always test in a development server before deploying to production. The developers are not responsible for any misuse or damage caused by this bot.

## 🆘 Support

For support, please:
- Open an issue on GitHub
- Check existing documentation
- Review the troubleshooting section

## 🙏 Credits

Built with:
- [Discord.js](https://discord.js.org/) - Discord API library
- [Node.js](https://nodejs.org/) - JavaScript runtime
- [SQLite](https://www.sqlite.org/) - Database engine
- [Winston](https://github.com/winstonjs/winston) - Logging library

---

**Made with ❤️ for the Discord community**
