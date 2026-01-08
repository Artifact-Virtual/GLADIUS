# Arty - Extensible Bot Framework

Arty is a modular, extensible bot framework designed for managing and automating various platforms. Currently supports Discord with a comprehensive feature set, with architecture ready for future platform integrations.

## 🎯 Philosophy

Arty provides a unified, abstracted approach to bot management across multiple platforms:
- **Modular Architecture**: Each platform (Discord, Telegram, etc.) is isolated in its own module
- **Shared Utilities**: Common functionality (logging, database, configuration) is abstracted at the root level
- **Extensible Design**: Easy to add new platforms or features without affecting existing functionality
- **Production-Ready**: Robust error handling, logging, and monitoring built-in

## 📁 Project Structure

```
arty/
├── discord/              # Discord bot implementation
│   ├── src/             # Discord-specific bot code
│   ├── .env.example     # Discord bot environment template
│   ├── config.example.json  # Discord bot configuration template
│   ├── package.json     # Discord bot dependencies
│   └── README.md        # Discord bot documentation
├── telegram/            # Future: Telegram bot
├── slack/               # Future: Slack bot
├── shared/              # Future: Shared utilities across platforms
├── README.md            # This file
└── package.json         # Root workspace configuration
```

## 🚀 Current Features

### Discord Bot
A comprehensive, autonomous Discord server management bot with:
- **Moderation**: Kick, ban, timeout, warn, bulk message deletion, auto-moderation
- **Economy**: Virtual currency, daily rewards, shop system
- **Leveling**: XP system with role rewards and leaderboards
- **Automation**: Reminders, giveaways, polls, scheduled tasks
- **Logging**: Comprehensive event logging and audit trails
- **Webhooks**: External integrations and custom notifications

[See Discord Bot Documentation →](discord/README.md)

## 📋 Quick Start

### Discord Bot Setup

```bash
# Navigate to discord bot directory
cd arty/discord

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your bot token and settings

# Deploy slash commands
npm run deploy-commands

# Start the bot
npm start
```

For detailed setup instructions, see [Discord Setup Guide](discord/SETUP.md).

## 🔧 Development

### Adding a New Platform

1. Create a new directory for the platform (e.g., `telegram/`)
2. Implement platform-specific bot logic
3. Follow the modular structure used in `discord/`
4. Document setup and configuration

### Project Guidelines

- **Isolation**: Keep platform-specific code in platform directories
- **Abstraction**: Extract common functionality to shared utilities
- **Documentation**: Maintain comprehensive docs for each module
- **Testing**: Ensure robust error handling and logging

## 📚 Documentation

- [Discord Bot README](discord/README.md) - Full feature documentation
- [Discord Setup Guide](discord/SETUP.md) - Detailed setup instructions
- [Discord Quick Start](discord/QUICKSTART.md) - 5-minute deployment
- [Discord Configuration](discord/CONFIGURATION_GUIDE.md) - Configuration reference
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - Project overview

## 🏗️ Architecture

### Current Implementation

**Discord Bot** (`discord/`)
- Token-based authentication
- Webhook integration support
- SQLite database for persistence
- Winston logging with rotation
- Cron-based automation

### Future Extensions

**Planned Platforms:**
- Telegram bot with similar feature parity
- Slack bot for workspace management
- Generic webhook receiver for custom integrations

**Shared Components:**
- Unified database abstraction
- Common logging framework
- Shared configuration management
- Cross-platform analytics

## 🔐 Security

- All secrets managed via environment variables
- Platform-specific `.env` files (never committed)
- Comprehensive permission checks
- Audit logging for all actions
- Rate limiting and cooldown management

## 🤝 Contributing

When contributing:
1. Keep platform-specific code isolated
2. Follow existing patterns and conventions
3. Document all new features
4. Test thoroughly before submitting

## 📝 License

MIT License - See LICENSE file for details

## 🆘 Support

For platform-specific help:
- **Discord Bot**: See [discord/README.md](discord/README.md)
- **General**: Check [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

---

**Arty** - Extensible, maintainable, production-ready bot management
