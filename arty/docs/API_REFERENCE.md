# API Reference

Module APIs and integration points for Arty.

## Research Engine API

### ResearchEngine Class

**Location:** `research/src/index.js`

#### Methods

**`async runCycle(options)`**
```javascript
const engine = new ResearchEngine(config);
await engine.runCycle({
  batch: 1,           // Number of days to generate content for
  force: false        // Force run even if recently executed
});
```

**`async search(query, options)`**
```javascript
const results = await engine.search('quantum computing', {
  maxResults: 20,
  source: 'brave'  // 'brave', 'serper', or 'serpapi'
});
```

**`async extractKeywords(text, options)`**
```javascript
const keywords = await engine.extractKeywords(articleText, {
  maxKeywords: 10,
  minRelevance: 0.5
});
```

**`async generateContent(insights, platform)`**
```javascript
const posts = await engine.generateContent(researchInsights, 'linkedin');
// Returns array of formatted posts
```

### SearchService

**Location:** `research/src/services/searchService.js`

#### Methods

**`async search(query, api)`**
```javascript
const searchService = require('./services/searchService');
const results = await searchService.search('machine learning', 'brave');
```

**`async batchSearch(queries)`**
```javascript
const results = await searchService.batchSearch([
  'AI research',
  'neural networks',
  'deep learning'
]);
```

### AnalysisService

**Location:** `research/src/services/analysisService.js`

#### Methods

**`extractKeywords(text, options)`**
```javascript
const analysisService = require('./services/analysisService');
const keywords = analysisService.extractKeywords(text, {
  method: 'tfidf',
  maxKeywords: 10
});
```

**`extractEntities(text)`**
```javascript
const entities = analysisService.extractEntities(text);
// Returns: { persons: [], organizations: [], locations: [] }
```

**`calculateRelevance(keyword, document)`**
```javascript
const score = analysisService.calculateRelevance('quantum', documentText);
```

### StorageService

**Location:** `research/src/services/storageService.js`

#### Methods

**`async saveArticle(article)`**
```javascript
const storageService = require('./services/storageService');
await storageService.saveArticle({
  title: 'Article Title',
  content: 'Full text...',
  url: 'https://...',
  source: 'example.com'
});
```

**`async getKeywords(options)`**
```javascript
const keywords = await storageService.getKeywords({
  minRelevance: 0.7,
  limit: 20,
  orderBy: 'relevance'
});
```

**`async saveDraft(draft)`**
```javascript
await storageService.saveDraft({
  platform: 'linkedin',
  content: 'Post content...',
  metadata: { research_id: 123 }
});
```

## Discord Bot API

### Client Extensions

**Location:** `discord/src/index.js`

#### Collections

**`client.commands`**
```javascript
// Access registered commands
const pingCommand = client.commands.get('ping');
```

**`client.cooldowns`**
```javascript
// Manage command cooldowns
if (client.cooldowns.has(userId)) {
  // User on cooldown
}
```

### Research Engagement Service

**Location:** `discord/src/services/researchEngagementService.js`

#### Methods

**`async getTopics(count)`**
```javascript
const engagementService = require('./services/researchEngagementService');
const topics = await engagementService.getTopics(5);
```

**`async sendTopicMessage(channel, topic)`**
```javascript
await engagementService.sendTopicMessage(channelObj, topicData);
```

**`async handleResponse(message)`**
```javascript
await engagementService.handleResponse(messageObj);
// Analyzes response and maintains context
```

**`async getContextMessages(channelId, limit)`**
```javascript
const context = await engagementService.getContextMessages('channel_id', 5);
```

### Database Queries

**Location:** `discord/src/utils/database.js`

#### Guild Queries

```javascript
const db = require('./utils/database');

// Get guild config
const guild = await db.getGuild(guildId);

// Update guild settings
await db.updateGuild(guildId, { prefix: '!' });
```

#### User Queries

```javascript
// Get user level
const level = await db.getUserLevel(userId, guildId);

// Add XP
await db.addXP(userId, guildId, 15);

// Get user economy
const economy = await db.getUserEconomy(userId, guildId);
```

#### Moderation Queries

```javascript
// Add warning
await db.addWarning(userId, guildId, moderatorId, reason);

// Get warnings
const warnings = await db.getWarnings(userId, guildId);
```

## LinkedIn Automation API

### LinkedInManager Class

**Location:** `linkedin/src/index.js`

#### Methods

**`async post(content, options)`**
```javascript
const LinkedInManager = require('./src/index');
const manager = new LinkedInManager(config);

await manager.post('Hello LinkedIn!', {
  visibility: 'PUBLIC',
  author: 'person',
  media: ['./image.jpg']
});
```

**`async schedule(content, scheduledTime, options)`**
```javascript
await manager.schedule('Future post', '2026-01-10T14:00:00Z', {
  media: ['./video.mp4']
});
```

**`async getAnalytics(postId)`**
```javascript
const analytics = await manager.getAnalytics('post_urn');
// Returns: { likes, comments, shares, impressions }
```

**`async cleanup(options)`**
```javascript
await manager.cleanup({
  media: true,
  logs: true,
  olderThan: '7d'
});
```

### LinkedIn Service

**Location:** `linkedin/src/services/linkedinService.js`

#### Methods

**`async createTextPost(content, visibility)`**
```javascript
const linkedinService = require('./services/linkedinService');
const response = await linkedinService.createTextPost(
  'Post content',
  'PUBLIC'
);
```

**`async uploadMedia(filePath, type)`**
```javascript
const mediaUrn = await linkedinService.uploadMedia(
  './image.jpg',
  'image'
);
```

**`async getPostAnalytics(postUrn)`**
```javascript
const analytics = await linkedinService.getPostAnalytics('urn:li:share:123');
```

### Scheduler Service

**Location:** `linkedin/src/services/schedulerService.js`

#### Methods

**`start()`**
```javascript
const schedulerService = require('./services/schedulerService');
schedulerService.start();
```

**`stop()`**
```javascript
schedulerService.stop();
```

**`async checkScheduled()`**
```javascript
const dueP osts = await schedulerService.checkScheduled();
```

### Research Content Service

**Location:** `linkedin/src/services/researchContentService.js`

#### Methods

**`async generateFromResearch(count)`**
```javascript
const researchContent = require('./services/researchContentService');
const posts = await researchContent.generateFromResearch(5);
```

**`async scheduleResearchPosts(posts)`**
```javascript
await researchContent.scheduleResearchPosts(postsArray);
```

## Storage Layer API

### Database Utilities

**Location:** `store/init-databases.js` and module database files

#### SQLite Queries

```javascript
const sqlite3 = require('sqlite3');
const db = new sqlite3.Database('store/research.db');

// Prepared statement
db.run(
  'INSERT INTO keywords (keyword, relevance) VALUES (?, ?)',
  ['quantum', 0.85]
);

// Query with callback
db.all('SELECT * FROM keywords WHERE relevance > ?', [0.7], (err, rows) => {
  // Handle rows
});

// Using promises
const { promisify } = require('util');
const run = promisify(db.run.bind(db));
await run('INSERT INTO articles (title, content) VALUES (?, ?)', [title, content]);
```

#### pgvector Queries

```javascript
// Vector similarity search
const similarDocs = await db.all(`
  SELECT id, title, 
    1 - (embedding <=> ?) AS similarity
  FROM document_embeddings
  WHERE 1 - (embedding <=> ?) > 0.7
  ORDER BY similarity DESC
  LIMIT 10
`, [queryEmbedding, queryEmbedding]);
```

## Webhook Integration

### Discord Webhooks

```javascript
const { WebhookClient } = require('discord.js');

const webhook = new WebhookClient({ url: 'webhook_url' });

await webhook.send({
  content: 'Message content',
  username: 'Arty',
  avatarURL: 'avatar_url',
  embeds: [embed]
});
```

### LinkedIn Webhooks

```javascript
const webhookService = require('./services/webhookService');

await webhookService.send('event_type', {
  post_id: 'post_urn',
  status: 'published',
  analytics: analyticsData
});
```

## Event Emitters

### Research Engine Events

```javascript
const engine = new ResearchEngine(config);

engine.on('cycle:start', (data) => {
  console.log('Research cycle started');
});

engine.on('cycle:complete', (data) => {
  console.log('Research cycle complete', data);
});

engine.on('keywords:extracted', (keywords) => {
  console.log('Extracted keywords:', keywords);
});

engine.on('error', (error) => {
  console.error('Research error:', error);
});
```

### Discord Bot Events

```javascript
client.on('ready', () => {
  console.log('Bot ready');
});

client.on('interactionCreate', async (interaction) => {
  // Handle slash commands
});

client.on('messageCreate', async (message) => {
  // Handle messages
});
```

## Error Handling

### Standard Error Structure

```javascript
{
  code: 'ERROR_CODE',
  message: 'Human readable message',
  details: {},
  timestamp: '2026-01-08T21:00:00Z'
}
```

### Error Codes

**Research Engine:**
- `SEARCH_FAILED`: API search failed
- `NO_RESULTS`: No results found
- `KEYWORD_EXTRACTION_FAILED`: Analysis failed
- `STORAGE_ERROR`: Database error

**Discord Bot:**
- `PERMISSION_DENIED`: Insufficient permissions
- `COOLDOWN_ACTIVE`: Command on cooldown
- `INVALID_INPUT`: Invalid user input
- `DATABASE_ERROR`: Database error

**LinkedIn:**
- `AUTH_FAILED`: Authentication error
- `RATE_LIMITED`: Rate limit exceeded
- `UPLOAD_FAILED`: Media upload failed
- `POST_FAILED`: Post creation failed

## Integration Examples

### Research → LinkedIn

```javascript
// In linkedin/src/services/researchContentService.js
const ResearchEngine = require('../../../research/src/index');
const engine = new ResearchEngine(researchConfig);

const insights = await engine.runCycle({ batch: 1 });
const posts = await engine.generateContent(insights, 'linkedin');

for (const post of posts) {
  await linkedinManager.schedule(post.content, post.scheduledTime);
}
```

### Research → Discord

```javascript
// In discord/src/services/researchEngagementService.js
const db = require('../../../store/research.db');

const topics = await db.all(`
  SELECT * FROM topics 
  WHERE platform = 'discord' 
  AND used = 0 
  ORDER BY relevance DESC 
  LIMIT 5
`);

for (const topic of topics) {
  await channel.send(topic.content);
  await db.run('UPDATE topics SET used = 1 WHERE id = ?', [topic.id]);
}
```

## Configuration API

### Loading Configuration

```javascript
const fs = require('fs');
const path = require('path');

function loadConfig(modulePath) {
  const configPath = path.join(modulePath, 'config.json');
  return JSON.parse(fs.readFileSync(configPath, 'utf8'));
}

const config = loadConfig('./research');
```

### Environment Variables

```javascript
require('dotenv').config();

const token = process.env.DISCORD_TOKEN;
const apiKey = process.env.BRAVE_SEARCH_API_KEY;
```

## Logging API

### Winston Logger

```javascript
const logger = require('./utils/logger');

logger.info('Info message');
logger.warn('Warning message');
logger.error('Error message', { error: errorObj });
logger.debug('Debug message', { data: debugData });
```

### Custom Log Levels

```javascript
logger.log('custom', 'Custom level message');
```

See module-specific documentation for detailed APIs:
- [Discord Guide](DISCORD.md)
- [LinkedIn Guide](LINKEDIN.md)
- [Research Engine](RESEARCH.md)
