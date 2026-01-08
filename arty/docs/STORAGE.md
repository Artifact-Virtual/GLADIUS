# Storage Layer

Arty's central storage system with dual databases and organized file system.

## Architecture

```
store/
├── research.db         # SQLite3 - structured data
├── vector.db          # pgvector - embeddings (neural net ready)
├── file_system/       # Organized document storage
└── init-databases.js  # Database initialization script
```

## SQLite3 Database

**12 tables for structured data:**

### Research Management
- **research_sessions**: Track research cycles and status
- **keywords**: Extracted keywords with frequency and relevance scores
- **search_results**: Web search results with metadata
- **articles**: Downloaded and processed articles
- **papers**: Academic papers and studies
- **analysis_cache**: Cached analysis results

### Content Management
- **notes**: Research notes and extracts
- **drafts**: Content drafts for posting
- **blueprints**: System blueprints and schemas
- **topics**: Discussion topics for engagement

### Scheduling & Context
- **post_queue**: Scheduled posts across platforms
- **engagement_context**: Conversation context for Discord

## pgvector Database

**3 tables for vector embeddings:**

- **document_embeddings**: Document vector representations
- **keyword_embeddings**: Keyword semantic embeddings
- **similarity_cache**: Pre-computed similarity scores

**Neural Network Ready:**
- Infrastructure prepared for embedding models
- Similarity search capabilities
- Future ML integration path

## File System Organization

```
file_system/
├── articles/          # Researched articles (markdown, HTML)
├── notes/             # Research notes and extracts
├── papers/            # Academic papers (PDF, DOCX)
├── drafts/            # Content drafts awaiting publication
├── blueprints/        # System schemas and blueprints
└── settings/
    └── context.json   # Complete Arty file structure map
```

### Context.json Structure

Contains complete system state:
```json
{
  "arty": {
    "modules": ["discord", "linkedin", "research", "store"],
    "structure": { /* complete file tree */ },
    "lastUpdate": "2026-01-08T21:00:00Z",
    "version": "1.0.0"
  }
}
```

## Initialization

```bash
cd store
node init-databases.js
```

Creates both databases with complete schemas.

## Database Access

### From Research Engine

```javascript
const db = require('./utils/database');

// SQLite queries
const results = await db.query('SELECT * FROM keywords WHERE relevance > 0.8');

// Vector similarity
const similar = await db.vectorSimilarity('document_embeddings', embedding, 10);
```

### From Discord/LinkedIn

Modules access storage through research integration services:
- `researchEngagementService.js` (Discord)
- `researchContentService.js` (LinkedIn)

## Data Flow

```
Web Search → SQLite (search_results)
           ↓
     Content Analysis → SQLite (keywords, articles)
                     ↓
              Vector Embeddings → pgvector (embeddings)
                                ↓
                         File System (articles, notes)
                                ↓
                     Content Generation → SQLite (drafts, post_queue)
                                       ↓
                               Platform Publishing
```

## Maintenance

### Cleanup

Automated cleanup configured in `research/config.json`:
```json
{
  "cleanup": {
    "oldArticles": "30d",
    "oldDrafts": "7d",
    "oldSearchResults": "14d"
  }
}
```

### Backup

```bash
# Backup databases
cp store/research.db store/backups/research-$(date +%Y%m%d).db
cp store/vector.db store/backups/vector-$(date +%Y%m%d).db

# Backup file system
tar -czf store/backups/filesystem-$(date +%Y%m%d).tar.gz store/file_system/
```

## Performance

- **SQLite**: Handles 100K+ records efficiently
- **pgvector**: Optimized for similarity search
- **File System**: Organized for quick access
- **Indexes**: All tables properly indexed

## Future Evolution

Path to neural network integration:
1. ✅ Vector storage infrastructure (pgvector)
2. ✅ Embedding table schemas
3. ✅ Similarity search queries
4. 🔄 Integrate transformer models
5. 🔄 Train on historical data
6. 🔄 Implement reinforcement learning

See [Database Schema](DATABASE_SCHEMA.md) for complete schema reference.
