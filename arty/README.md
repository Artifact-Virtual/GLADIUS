# Arty - Autonomous Research Team

**Self-guided learning system with multi-platform automation**

## Overview

Arty (Autonomous Research Team) is a fully autonomous system that learns independently through iterative web research, keyword extraction, content analysis, and intelligent engagement across platforms. Zero human intervention required.

**Core Philosophy**: Social media integrations (Discord, LinkedIn) are drivers and adapters for a deeper research intelligence core.

## Quick Links

📘 **[Complete Documentation](docs/README.md)** - Start here for full guides

🚀 **[Quick Start](docs/QUICKSTART.md)** - Get running in 5 minutes

📖 **[Introduction](docs/INTRODUCTION.md)** - Understand Arty's architecture

## Modules

### 🧠 Research Engine
Autonomous learning loop with zero human intervention
- Self-guided keyword extraction and refinement
- Multi-iteration research cycles  
- No LLM required (statistical analysis)
- Cost-optimized batch processing

### 💾 Storage Layer
Central storage with dual databases
- SQLite3 for structured data (12 tables)
- pgvector for embeddings (neural network ready)
- Organized file system (articles, notes, papers, drafts)

### 💬 Discord Bot
Full-featured server management with research integration
- 15 commands (moderation, utility, economy, admin, fun)
- Research-driven engagement every 3 hours
- Context-aware responses (5-message window)
- Auto-moderation, economy, leveling systems

### 💼 LinkedIn Automation
Complete LinkedIn API integration with research content
- Automated posting (text, images, videos, documents)
- Advanced scheduling with timezone support
- Rate limiting and analytics tracking
- Research-based content generation

## Quick Start

```bash
# Install all modules
npm install

# Initialize storage
cd store && node init-databases.js && cd ..

# Configure research (required)
cd research
cp .env.example .env
cp config.example.json config.json
# Edit with your search API key and research fields

# Run research cycle
npm start

# Optional: Setup Discord
cd ../discord
cp .env.example .env
cp config.example.json config.json
npm run deploy-commands
npm start

# Optional: Setup LinkedIn
cd ../linkedin
cp .env.example .env
cp config.example.json config.json
npm start
```

## Documentation

### Getting Started
- **[Introduction](docs/INTRODUCTION.md)** - Core concepts and architecture
- **[Quick Start](docs/QUICKSTART.md)** - 5-minute setup guide

### Core Systems
- **[Storage Layer](docs/STORAGE.md)** - SQLite3, pgvector, file system
- **[Research Engine](docs/RESEARCH.md)** - Autonomous learning loop
- **[Configuration](docs/CONFIGURATION.md)** - Complete config reference

### Platform Guides
- **[Discord Bot](docs/DISCORD.md)** - Commands, features, setup
- **[LinkedIn Automation](docs/LINKEDIN.md)** - Posting, scheduling, analytics

### Operations
- **[Deployment](docs/DEPLOYMENT.md)** - Production deployment (PM2, systemd)
- **[Testing](docs/TESTING.md)** - Running and interpreting tests
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

### Reference
- **[API Reference](docs/API_REFERENCE.md)** - Module APIs and integration
- **[Database Schema](docs/DATABASE_SCHEMA.md)** - Complete schema docs

## Key Features

### Autonomous Research
- Configuration-driven fields (broad + targeted)
- Iterative keyword extraction (no LLM)
- Multi-iteration research cycles
- Automated content generation
- Cross-platform scheduling

### Intelligent Engagement
- Discord: Research topics every 3 hours
- Context-aware responses
- Conversation memory (5 messages)
- LinkedIn: Research-based posts

### Cost Optimization
- Batch processing (single run every 2-3 days)
- Generates all content at once
- Intelligent caching
- Minimizes API costs by 70%

### Neural Network Ready
- pgvector infrastructure
- Vector similarity search
- Modular ML integration path
- Future evolution prepared

## Workspace Commands

```bash
# Research
npm run research:cycle        # Run research cycle
npm run research:start        # Continuous mode

# Discord
npm run discord:deploy        # Deploy commands
npm run discord:start         # Start bot
npm run discord:test          # Run tests

# LinkedIn
npm run linkedin:start        # Start scheduler
npm run linkedin:post         # Post now
npm run linkedin:test         # Run tests

# All tests
npm test
```

## Testing

Comprehensive test suites with 91.7% coverage:
- **Discord**: 47 tests (83%, 100% functional)
- **LinkedIn**: 49 tests (100%)
- **Overall**: 88/96 tests passing

```bash
npm test
```

## Architecture

```
arty/
├── store/              # Central storage (SQLite3 + pgvector)
├── research/           # Autonomous research engine
├── discord/            # Discord bot with research integration
├── linkedin/           # LinkedIn automation with research content
├── docs/               # Complete documentation
└── package.json        # Workspace configuration
```

## Requirements

- Node.js 16+
- Linux/macOS environment
- Search API key (Brave, Serper, or SerpAPI)
- Optional: Discord bot token, LinkedIn API credentials

## Production Ready

- ✅ Comprehensive error handling
- ✅ Database persistence (SQLite3 + pgvector)
- ✅ Daily log rotation
- ✅ PM2 support
- ✅ Health monitoring
- ✅ Automatic backups
- ✅ 91.7% test coverage

See **[Deployment Guide](docs/DEPLOYMENT.md)** for production setup.

## Support

- **Documentation**: [docs/](docs/)
- **Troubleshooting**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- **API Reference**: [docs/API_REFERENCE.md](docs/API_REFERENCE.md)
