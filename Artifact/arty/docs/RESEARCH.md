# Research Engine

Autonomous learning system with zero human intervention.

## Overview

The Research Engine conducts self-guided research through iterative web searches, keyword extraction, and content analysis - no LLM required.

## Configuration

### Research Fields

In `research/config.json`:
```json
{
  "research": {
    "broadField": "artificial intelligence",
    "targetedField": "reinforcement learning",
    "enabled": true,
    "cycleFrequency": "daily",
    "iterations": 3,
    "keywordsPerIteration": 10,
    "maxResultsPerSearch": 20,
    "contentGeneration": {
      "enabled": true,
      "postsPerCycle": 5,
      "platforms": ["linkedin", "discord"]
    }
  }
}
```

**Fields:**
- `broadField`: General research area (required)
- `targetedField`: Specific focus (optional, leave blank for open exploration)
- `cycleFrequency`: `"daily"`, `"2d"`, `"weekly"`
- `iterations`: Number of search refinement cycles (3-5 recommended)

### API Keys

In `research/.env`:
```env
# Choose one or more
BRAVE_SEARCH_API_KEY=your_key
SERPER_API_KEY=your_key
SERPAPI_KEY=your_key
```

## Intelligence Loop

### Phase 1: Initial Search
```
Config: broadField = "quantum computing"
      ↓
Keyword Search: ["quantum computing", "quantum", "computing"]
      ↓
Web Results: 20 articles
```

### Phase 2: Keyword Extraction
```
Analyze 20 articles
      ↓
TF-IDF Analysis → Extract top keywords
      ↓
Keywords: ["qubit", "superposition", "entanglement", "quantum gate", ...]
      ↓
Store in SQLite (keywords table)
```

### Phase 3: Refined Search
```
Combine: broadField + targetedField + extracted keywords
      ↓
New Searches: "quantum computing qubit", "quantum gate superposition", ...
      ↓
200+ new articles
```

### Phase 4: Deep Analysis
```
Analyze 200+ articles
      ↓
Extract entities, concepts, relationships
      ↓
Store: articles → SQLite, embeddings → pgvector
```

### Phase 5: Content Generation
```
Research insights
      ↓
Generate posts (5-10 per cycle)
      ↓
Apply formatting, frontmatter
      ↓
Store in drafts/, schedule in post_queue
```

### Phase 6: Distribution
```
Scheduled posts
      ↓
LinkedIn: Auto-publish
Discord: Extract topics for engagement
```

## No LLM - Statistical Analysis

### Keyword Extraction
- **TF-IDF**: Term frequency-inverse document frequency
- **Statistical significance**: Chi-square test
- **Co-occurrence graphs**: Relationship mapping

### Entity Recognition
- **Pattern matching**: Named entity patterns
- **Frequency analysis**: Entity mention counts
- **Context windows**: Entity relationship extraction

### Content Analysis
- **Sentiment scoring**: Polarity detection
- **Topic clustering**: K-means clustering
- **Relevance ranking**: Cosine similarity

## Operation Modes

### Daily Cycle (Recommended)
```bash
npm run research:cycle
```
- Runs complete loop once
- Generates 5-10 posts
- Schedules for next 24 hours

### Multi-Day Batch (Cost-Optimized)
```bash
npm run research:cycle -- --batch 3
```
- Runs once every 3 days
- Generates 15-30 posts
- Schedules entire period
- **Minimizes API costs by 70%**

### Continuous Mode
```bash
npm start
```
- Runs on schedule from config
- Autonomous 24/7 operation
- Auto-restart on errors

## Output

### Generated Files
```
file_system/
├── articles/
│   ├── 20260108-quantum-computing-basics.md
│   ├── 20260108-qubit-technology.md
│   └── ...
├── notes/
│   ├── 20260108-research-session-1.md
│   └── ...
└── drafts/
    ├── linkedin-post-1.md
    ├── discord-topic-1.md
    └── ...
```

### Database Records
- **keywords**: 50-100 keywords per cycle
- **articles**: 200+ articles per cycle
- **drafts**: 5-10 posts per cycle
- **topics**: 5-15 topics per cycle

## Monitoring

### Logs

```bash
tail -f research/logs/research-YYYY-MM-DD.log
```

### Database Queries

```bash
sqlite3 store/research.db

# Recent sessions
SELECT * FROM research_sessions ORDER BY created_at DESC LIMIT 10;

# Top keywords
SELECT keyword, relevance FROM keywords ORDER BY relevance DESC LIMIT 20;

# Articles count
SELECT COUNT(*) FROM articles WHERE created_at > datetime('now', '-7 days');
```

## Integration

### Discord Integration

Research engine populates topics for Discord engagement:
```javascript
// discord/src/services/researchEngagementService.js
const topics = await researchDb.getTopics(5);
// Send to Discord every 3 hours
```

### LinkedIn Integration

Research generates LinkedIn posts:
```javascript
// linkedin/src/services/researchContentService.js
const drafts = await researchDb.getDrafts('linkedin', 5);
// Schedule to LinkedIn queue
```

## Performance

- **Single cycle**: 5-10 minutes
- **API calls**: ~50 per cycle
- **Storage**: ~50MB per cycle
- **Posts generated**: 5-10 per cycle

## Cost Optimization

### Batch Processing
- Run every 2-3 days instead of daily
- Generate all content in one batch
- **Saves 60-70% on API costs**

### Caching
- Search results cached 24 hours
- Keyword relationships cached
- Analysis results cached

### Efficient Queries
- Pagination for large result sets
- Incremental processing
- Database indexes

## Troubleshooting

**No results:**
- Check API key validity
- Verify internet connection
- Review broadField configuration

**Too few keywords:**
- Increase `iterations` in config
- Adjust `keywordsPerIteration`
- Check article content quality

**Poor content quality:**
- Refine `targetedField`
- Increase `maxResultsPerSearch`
- Add keyword filters

See [Troubleshooting Guide](TROUBLESHOOTING.md) for more solutions.
