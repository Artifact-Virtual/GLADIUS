# Research Module

Autonomous research engine for Arty - self-guided learning with zero human intervention.

## Quick Start

```bash
# Copy configuration files
cp .env.example .env
cp config.example.json config.json

# Edit .env with your API keys
# Edit config.json with your research fields

# Install dependencies
npm install

# Initialize database (run this from store/ directory first)
cd ../store && npm install && npm run init && cd ../research

# Run a research cycle
npm run cycle
```

## Configuration

### .env File

Add at least one search API key:
- Brave Search API: https://brave.com/search/api/
- Serper: https://serper.dev/
- SerpAPI: https://serpapi.com/

### config.json

Configure your research fields:
```json
{
  "research": {
    "broadField": "your field here",
    "targetedField": "specific topic (optional)",
    "iterations": 3,
    "keywordsPerIteration": 10
  }
}
```

## Commands

```bash
# Run single research cycle
npm run cycle

# Run multi-day batch (cost-optimized)
npm run cycle -- --batch 3

# Continuous mode
npm start
```

## How It Works

1. **Initial Search**: Searches web for broad + targeted fields
2. **Keyword Extraction**: Uses TF-IDF to extract relevant keywords
3. **Refined Search**: Searches again with extracted keywords
4. **Content Generation**: Creates posts for LinkedIn and Discord
5. **Storage**: Saves everything to database and file system

## Output

- **Database**: All research data in `../store/research.db`
- **Files**: Articles and notes in `../store/file_system/`
- **Logs**: Daily logs in `logs/research-YYYY-MM-DD.log`

## Architecture

```
research/
├── src/
│   ├── index.js              # Main research engine
│   ├── services/
│   │   ├── searchService.js  # Web search
│   │   ├── analysisService.js # Keyword extraction
│   │   ├── storageService.js  # Database operations
│   │   └── contentGenerator.js # Post generation
│   ├── utils/
│   │   └── logger.js          # Logging utility
│   └── scripts/
│       └── run-cycle.js       # CLI script
├── logs/                      # Daily log files
├── .env                       # API keys (create from .env.example)
├── config.json                # Research configuration
└── package.json
```

## Integration

Other modules can access research data:

```javascript
const StorageService = require('./research/src/services/storageService');
const storage = new StorageService();

// Get recent keywords
const keywords = await storage.getRecentKeywords(20);

// Get pending drafts for a platform
const drafts = await storage.getPendingDrafts('discord', 10);
```

See [Documentation](../docs/RESEARCH.md) for complete details.
