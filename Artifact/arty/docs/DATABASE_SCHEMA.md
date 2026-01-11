# Database Schema

Complete database schema documentation for all Arty modules.

## Research Database (SQLite3)

**Location:** `arty/store/research.db`

### research_sessions

Tracks research cycles and execution status.

```sql
CREATE TABLE research_sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  broad_field TEXT NOT NULL,
  targeted_field TEXT,
  status TEXT DEFAULT 'pending',
  iterations_completed INTEGER DEFAULT 0,
  keywords_extracted INTEGER DEFAULT 0,
  articles_found INTEGER DEFAULT 0,
  posts_generated INTEGER DEFAULT 0,
  started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  completed_at DATETIME,
  error TEXT
);
```

### keywords

Extracted keywords with relevance scores.

```sql
CREATE TABLE keywords (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER,
  keyword TEXT NOT NULL,
  frequency INTEGER DEFAULT 1,
  relevance REAL DEFAULT 0.5,
  iteration INTEGER DEFAULT 1,
  source TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES research_sessions(id)
);

CREATE INDEX idx_keywords_relevance ON keywords(relevance DESC);
CREATE INDEX idx_keywords_keyword ON keywords(keyword);
```

### search_results

Web search results and metadata.

```sql
CREATE TABLE search_results (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER,
  query TEXT NOT NULL,
  title TEXT,
  url TEXT,
  snippet TEXT,
  source TEXT,
  relevance_score REAL,
  fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES research_sessions(id)
);

CREATE INDEX idx_search_results_session ON search_results(session_id);
```

### articles

Downloaded and processed articles.

```sql
CREATE TABLE articles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER,
  title TEXT NOT NULL,
  content TEXT,
  url TEXT UNIQUE,
  author TEXT,
  published_date DATETIME,
  source_domain TEXT,
  word_count INTEGER,
  processed BOOLEAN DEFAULT 0,
  file_path TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES research_sessions(id)
);

CREATE INDEX idx_articles_processed ON articles(processed);
CREATE INDEX idx_articles_created ON articles(created_at DESC);
```

### papers

Academic papers and studies.

```sql
CREATE TABLE papers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER,
  title TEXT NOT NULL,
  abstract TEXT,
  authors TEXT,
  publication TEXT,
  doi TEXT,
  arxiv_id TEXT,
  pdf_url TEXT,
  file_path TEXT,
  citations INTEGER,
  published_date DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES research_sessions(id)
);
```

### notes

Research notes and extracts.

```sql
CREATE TABLE notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER,
  article_id INTEGER,
  note_type TEXT DEFAULT 'extract',
  content TEXT NOT NULL,
  relevance REAL,
  tags TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES research_sessions(id),
  FOREIGN KEY (article_id) REFERENCES articles(id)
);
```

### drafts

Content drafts for posting.

```sql
CREATE TABLE drafts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER,
  platform TEXT NOT NULL,
  content TEXT NOT NULL,
  metadata TEXT,
  status TEXT DEFAULT 'pending',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  published_at DATETIME,
  FOREIGN KEY (session_id) REFERENCES research_sessions(id)
);

CREATE INDEX idx_drafts_status ON drafts(status);
CREATE INDEX idx_drafts_platform ON drafts(platform);
```

### blueprints

System blueprints and schemas.

```sql
CREATE TABLE blueprints (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  type TEXT,
  content TEXT,
  version TEXT,
  file_path TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### topics

Discussion topics for engagement.

```sql
CREATE TABLE topics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER,
  platform TEXT NOT NULL,
  content TEXT NOT NULL,
  keywords TEXT,
  relevance REAL,
  used BOOLEAN DEFAULT 0,
  used_at DATETIME,
  engagement_count INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES research_sessions(id)
);

CREATE INDEX idx_topics_platform_used ON topics(platform, used);
```

### post_queue

Scheduled posts across platforms.

```sql
CREATE TABLE post_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  draft_id INTEGER,
  platform TEXT NOT NULL,
  content TEXT NOT NULL,
  media_paths TEXT,
  scheduled_time DATETIME NOT NULL,
  status TEXT DEFAULT 'pending',
  posted_at DATETIME,
  post_id TEXT,
  error TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (draft_id) REFERENCES drafts(id)
);

CREATE INDEX idx_post_queue_scheduled ON post_queue(scheduled_time);
CREATE INDEX idx_post_queue_status ON post_queue(status);
```

### engagement_context

Conversation context for Discord.

```sql
CREATE TABLE engagement_context (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  channel_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  message_content TEXT,
  message_id TEXT,
  topic_id INTEGER,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (topic_id) REFERENCES topics(id)
);

CREATE INDEX idx_engagement_channel ON engagement_context(channel_id, timestamp DESC);
```

### analysis_cache

Cached analysis results.

```sql
CREATE TABLE analysis_cache (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cache_key TEXT UNIQUE NOT NULL,
  cache_type TEXT,
  data TEXT,
  expires_at DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cache_key ON analysis_cache(cache_key);
CREATE INDEX idx_cache_expires ON analysis_cache(expires_at);
```

## Vector Database (pgvector)

**Location:** `arty/store/vector.db`

### document_embeddings

Document vector representations.

```sql
CREATE TABLE document_embeddings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  article_id INTEGER,
  embedding vector(384),
  model TEXT DEFAULT 'all-MiniLM-L6-v2',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (article_id) REFERENCES articles(id)
);

CREATE INDEX idx_doc_embeddings_article ON document_embeddings(article_id);
```

### keyword_embeddings

Keyword semantic embeddings.

```sql
CREATE TABLE keyword_embeddings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  keyword_id INTEGER,
  keyword TEXT,
  embedding vector(384),
  model TEXT DEFAULT 'all-MiniLM-L6-v2',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (keyword_id) REFERENCES keywords(id)
);
```

### similarity_cache

Pre-computed similarity scores.

```sql
CREATE TABLE similarity_cache (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  doc1_id INTEGER,
  doc2_id INTEGER,
  similarity REAL,
  computed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (doc1_id, doc2_id)
);
```

## Discord Database (SQLite3)

**Location:** `arty/discord/data/discord.db`

### guilds

Server configurations.

```sql
CREATE TABLE guilds (
  id TEXT PRIMARY KEY,
  name TEXT,
  prefix TEXT DEFAULT '!',
  welcome_channel TEXT,
  goodbye_channel TEXT,
  log_channel TEXT,
  mod_log_channel TEXT,
  config TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### users

User profiles and statistics.

```sql
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  username TEXT,
  discriminator TEXT,
  avatar TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### levels

User leveling data.

```sql
CREATE TABLE levels (
  user_id TEXT,
  guild_id TEXT,
  xp INTEGER DEFAULT 0,
  level INTEGER DEFAULT 0,
  messages INTEGER DEFAULT 0,
  last_message DATETIME,
  PRIMARY KEY (user_id, guild_id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (guild_id) REFERENCES guilds(id)
);

CREATE INDEX idx_levels_xp ON levels(guild_id, xp DESC);
```

### economy

User economy data.

```sql
CREATE TABLE economy (
  user_id TEXT,
  guild_id TEXT,
  wallet INTEGER DEFAULT 0,
  bank INTEGER DEFAULT 0,
  last_daily DATETIME,
  last_work DATETIME,
  PRIMARY KEY (user_id, guild_id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (guild_id) REFERENCES guilds(id)
);
```

### warnings

Moderation warnings.

```sql
CREATE TABLE warnings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT,
  guild_id TEXT,
  moderator_id TEXT,
  reason TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (guild_id) REFERENCES guilds(id)
);

CREATE INDEX idx_warnings_user ON warnings(user_id, guild_id);
```

### moderation_logs

Moderation action logs.

```sql
CREATE TABLE moderation_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  guild_id TEXT,
  user_id TEXT,
  moderator_id TEXT,
  action TEXT,
  reason TEXT,
  duration INTEGER,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (guild_id) REFERENCES guilds(id)
);
```

### reminders

User reminders.

```sql
CREATE TABLE reminders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT,
  channel_id TEXT,
  message TEXT,
  remind_at DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  completed BOOLEAN DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_reminders_time ON reminders(remind_at) WHERE completed = 0;
```

### giveaways, polls, tickets

Additional feature tables (see Discord database.js for complete schemas).

## LinkedIn Database (SQLite3)

**Location:** `arty/linkedin/data/linkedin.db`

### posts

Published posts tracking.

```sql
CREATE TABLE posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_urn TEXT UNIQUE,
  author_type TEXT,
  content TEXT,
  visibility TEXT,
  media_urns TEXT,
  status TEXT DEFAULT 'published',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  published_at DATETIME
);
```

### scheduled_posts

Queued posts for publishing.

```sql
CREATE TABLE scheduled_posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  content TEXT NOT NULL,
  author_type TEXT DEFAULT 'person',
  visibility TEXT DEFAULT 'PUBLIC',
  media_paths TEXT,
  scheduled_time DATETIME NOT NULL,
  status TEXT DEFAULT 'pending',
  retries INTEGER DEFAULT 0,
  error TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  published_at DATETIME
);

CREATE INDEX idx_scheduled_time ON scheduled_posts(scheduled_time) WHERE status = 'pending';
```

### media

Uploaded media assets.

```sql
CREATE TABLE media (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  file_path TEXT,
  media_urn TEXT,
  media_type TEXT,
  file_size INTEGER,
  uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  deleted BOOLEAN DEFAULT 0
);
```

### analytics

Post performance metrics.

```sql
CREATE TABLE analytics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_id INTEGER,
  impressions INTEGER DEFAULT 0,
  clicks INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  shares INTEGER DEFAULT 0,
  engagement_rate REAL DEFAULT 0,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (post_id) REFERENCES posts(id)
);
```

### rate_limits

API call tracking.

```sql
CREATE TABLE rate_limits (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  endpoint TEXT,
  calls INTEGER DEFAULT 1,
  window_start DATETIME DEFAULT CURRENT_TIMESTAMP,
  reset_at DATETIME
);
```

### oauth_tokens

Authentication tokens.

```sql
CREATE TABLE oauth_tokens (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  access_token TEXT,
  refresh_token TEXT,
  expires_at DATETIME,
  scope TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Query Examples

### Research Queries

```sql
-- Top keywords from recent sessions
SELECT keyword, AVG(relevance) as avg_relevance, COUNT(*) as frequency
FROM keywords
WHERE created_at > datetime('now', '-7 days')
GROUP BY keyword
ORDER BY avg_relevance DESC, frequency DESC
LIMIT 20;

-- Articles needing processing
SELECT id, title, url
FROM articles
WHERE processed = 0
ORDER BY created_at DESC;

-- Pending posts by platform
SELECT platform, COUNT(*) as count, MIN(scheduled_time) as next_post
FROM post_queue
WHERE status = 'pending'
GROUP BY platform;
```

### Discord Queries

```sql
-- Leaderboard
SELECT u.username, l.level, l.xp, l.messages
FROM levels l
JOIN users u ON l.user_id = u.id
WHERE l.guild_id = ?
ORDER BY l.xp DESC
LIMIT 10;

-- User warnings
SELECT COUNT(*) as warning_count
FROM warnings
WHERE user_id = ? AND guild_id = ?
AND created_at > datetime('now', '-30 days');
```

### LinkedIn Queries

```sql
-- Post performance
SELECT p.content, a.likes, a.comments, a.shares, a.engagement_rate
FROM posts p
JOIN analytics a ON p.id = a.post_id
WHERE p.created_at > datetime('now', '-30 days')
ORDER BY a.engagement_rate DESC;

-- Upcoming scheduled posts
SELECT content, scheduled_time
FROM scheduled_posts
WHERE status = 'pending'
AND scheduled_time BETWEEN datetime('now') AND datetime('now', '+24 hours')
ORDER BY scheduled_time;
```

## Database Maintenance

### Vacuum

```sql
VACUUM;  -- Reclaim space
ANALYZE; -- Update query planner statistics
```

### Backup

```bash
sqlite3 store/research.db ".backup backups/research_$(date +%Y%m%d).db"
```

### Integrity Check

```sql
PRAGMA integrity_check;
```

See [Storage Layer](STORAGE.md) for more details on database management.
