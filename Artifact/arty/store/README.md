# Store Module

Central storage layer for Arty with SQLite3 database and organized file system.

## Quick Start

```bash
# Initialize database
npm run init

# Or directly
node init-databases.js
```

## Structure

```
store/
├── research.db         # SQLite3 database (created on init)
├── init-databases.js   # Database initialization script
├── package.json        # Dependencies
└── file_system/        # Organized document storage
    ├── articles/       # Researched articles
    ├── notes/          # Research notes
    ├── papers/         # Academic papers
    ├── drafts/         # Content drafts
    ├── blueprints/     # System blueprints
    └── settings/       # Configuration files
```

## Database Schema

12 tables for research management:
- `research_sessions` - Track research cycles
- `keywords` - Extracted keywords with relevance
- `search_results` - Web search results
- `articles` - Downloaded articles
- `papers` - Academic papers
- `notes` - Research notes
- `drafts` - Content drafts
- `blueprints` - System schemas
- `topics` - Discussion topics
- `post_queue` - Scheduled posts
- `engagement_context` - Conversation context
- `analysis_cache` - Cached analysis

See [Database Schema](../docs/DATABASE_SCHEMA.md) for complete reference.

## Usage

```javascript
const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./research.db');

// Query research sessions
db.all('SELECT * FROM research_sessions', [], (err, rows) => {
  if (err) throw err;
  console.log(rows);
});
```

## File System

Articles, notes, and papers are stored in organized directories with metadata in the database.

Example article file: `file_system/articles/20260111-quantum-computing.md`
Database record points to this file via `file_path` column.
