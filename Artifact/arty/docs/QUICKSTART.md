# Quick Start Guide

Get Arty running in 5 minutes.

## Prerequisites

- Node.js 16+ and npm
- Linux/macOS environment
- API keys (see Configuration below)

## Installation

```bash
# Clone and navigate
cd arty

# Install all modules
npm install

# Or install individually
cd discord && npm install && cd ..
cd linkedin && npm install && cd ..
cd research && npm install && cd ..
```

## Basic Setup

### 1. Initialize Storage

```bash
cd store
node init-databases.js
cd ..
```

### 2. Configure Research Engine

```bash
cd research
cp .env.example .env
cp config.example.json config.json
```

Edit `config.json`:
```json
{
  "research": {
    "broadField": "your research topic",
    "targetedField": "specific area (optional)",
    "cycleFrequency": "daily"
  }
}
```

Edit `.env` with search API key (choose one):
```env
BRAVE_SEARCH_API_KEY=your_key
# OR
SERPER_API_KEY=your_key
# OR
SERPAPI_KEY=your_key
```

### 3. Optional: Setup Discord Bot

```bash
cd discord
cp .env.example .env
cp config.example.json config.json
```

Edit `.env`:
```env
DISCORD_TOKEN=your_bot_token
CLIENT_ID=your_client_id
GUILD_ID=your_server_id
OWNER_ID=your_user_id
```

Deploy commands:
```bash
npm run deploy-commands
```

### 4. Optional: Setup LinkedIn

```bash
cd linkedin
cp .env.example .env
cp config.example.json config.json
```

Edit `.env`:
```env
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_secret
LINKEDIN_ACCESS_TOKEN=your_token
LINKEDIN_PERSON_URN=urn:li:person:XXXXXXXX
```

## Running

### Research Engine (Recommended First)

```bash
cd research
npm run research:cycle    # Single cycle
# OR
npm start                 # Continuous mode
```

### Discord Bot

```bash
cd discord
npm start
```

### LinkedIn Automation

```bash
cd linkedin
npm start                 # Scheduler service
```

## Verify Installation

```bash
# Run tests
cd discord && npm test
cd ../linkedin && npm test
```

## What's Next?

- **Full configuration**: See [Configuration Guide](CONFIGURATION.md)
- **Discord setup**: See [Discord Guide](DISCORD.md)
- **LinkedIn setup**: See [LinkedIn Guide](LINKEDIN.md)
- **Research details**: See [Research Engine](RESEARCH.md)
- **Production deployment**: See [Deployment Guide](DEPLOYMENT.md)

## Quick Commands Reference

```bash
# Research
npm run research:cycle              # Run research cycle
npm run research:cycle -- --batch 3 # Multi-day batch

# Discord
npm run discord:start               # Start bot
npm run discord:deploy              # Deploy commands
npm run discord:test                # Run tests

# LinkedIn
npm run linkedin:start              # Start scheduler
npm run linkedin:post               # Post now
npm run linkedin:schedule           # Schedule post
npm run linkedin:test               # Run tests
```

All commands from workspace root (`arty/`).
