import Database from 'better-sqlite3';
import { mkdirSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import logger from './logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let db;

export async function initializeDatabase() {
  try {
    const dbPath = process.env.DATABASE_PATH || path.join(path.dirname(path.dirname(__dirname)), 'data', 'linkedin.db');
    const dbDir = path.dirname(dbPath);
    
    // Ensure data directory exists
    mkdirSync(dbDir, { recursive: true });
    
    // Create database connection
    db = new Database(dbPath);
    db.pragma('journal_mode = WAL');
    
    // Create tables
    createTables();
    
    logger.info(`Database initialized at ${dbPath}`);
    return db;
  } catch (error) {
    logger.error('Failed to initialize database:', error);
    throw error;
  }
}

function createTables() {
  // Posts table
  db.exec(`
    CREATE TABLE IF NOT EXISTS posts (
      id TEXT PRIMARY KEY,
      content TEXT NOT NULL,
      author_urn TEXT NOT NULL,
      visibility TEXT DEFAULT 'PUBLIC',
      media_ids TEXT,
      post_url TEXT,
      status TEXT DEFAULT 'draft',
      created_at INTEGER DEFAULT (strftime('%s', 'now')),
      posted_at INTEGER,
      error_message TEXT
    )
  `);
  
  // Scheduled posts table
  db.exec(`
    CREATE TABLE IF NOT EXISTS scheduled_posts (
      id TEXT PRIMARY KEY,
      content TEXT NOT NULL,
      author_urn TEXT NOT NULL,
      visibility TEXT DEFAULT 'PUBLIC',
      media_paths TEXT,
      scheduled_time INTEGER NOT NULL,
      timezone TEXT DEFAULT 'UTC',
      status TEXT DEFAULT 'pending',
      attempts INTEGER DEFAULT 0,
      last_attempt INTEGER,
      created_at INTEGER DEFAULT (strftime('%s', 'now')),
      posted_at INTEGER,
      post_id TEXT,
      error_message TEXT
    )
  `);
  
  // Media table
  db.exec(`
    CREATE TABLE IF NOT EXISTS media (
      id TEXT PRIMARY KEY,
      file_path TEXT NOT NULL,
      file_type TEXT NOT NULL,
      file_size INTEGER,
      upload_url TEXT,
      asset_urn TEXT,
      status TEXT DEFAULT 'pending',
      uploaded_at INTEGER,
      post_id TEXT,
      created_at INTEGER DEFAULT (strftime('%s', 'now'))
    )
  `);
  
  // Analytics table
  db.exec(`
    CREATE TABLE IF NOT EXISTS analytics (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      post_id TEXT NOT NULL,
      impressions INTEGER DEFAULT 0,
      clicks INTEGER DEFAULT 0,
      likes INTEGER DEFAULT 0,
      comments INTEGER DEFAULT 0,
      shares INTEGER DEFAULT 0,
      engagement_rate REAL DEFAULT 0.0,
      fetched_at INTEGER DEFAULT (strftime('%s', 'now')),
      FOREIGN KEY (post_id) REFERENCES posts(id)
    )
  `);
  
  // Rate limits table
  db.exec(`
    CREATE TABLE IF NOT EXISTS rate_limits (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      endpoint TEXT NOT NULL,
      count INTEGER DEFAULT 1,
      window_start INTEGER NOT NULL,
      window_end INTEGER NOT NULL
    )
  `);
  
  // OAuth tokens table
  db.exec(`
    CREATE TABLE IF NOT EXISTS oauth_tokens (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      access_token TEXT NOT NULL,
      refresh_token TEXT,
      expires_at INTEGER NOT NULL,
      scope TEXT,
      created_at INTEGER DEFAULT (strftime('%s', 'now')),
      updated_at INTEGER DEFAULT (strftime('%s', 'now'))
    )
  `);
  
  logger.info('Database tables created/verified');
}

export function getDatabase() {
  if (!db) {
    throw new Error('Database not initialized. Call initializeDatabase() first.');
  }
  return db;
}

// Helper functions for common database operations
export const queries = {
  // Post operations
  createPost: (id, content, authorUrn, visibility = 'PUBLIC') => {
    return db.prepare('INSERT INTO posts (id, content, author_urn, visibility) VALUES (?, ?, ?, ?)')
      .run(id, content, authorUrn, visibility);
  },
  
  getPost: (id) => {
    return db.prepare('SELECT * FROM posts WHERE id = ?').get(id);
  },
  
  updatePostStatus: (id, status, postedAt = null, postUrl = null, error = null) => {
    if (postedAt) {
      return db.prepare('UPDATE posts SET status = ?, posted_at = ?, post_url = ?, error_message = ? WHERE id = ?')
        .run(status, postedAt, postUrl, error, id);
    } else {
      return db.prepare('UPDATE posts SET status = ?, error_message = ? WHERE id = ?')
        .run(status, error, id);
    }
  },
  
  // Scheduled post operations
  createScheduledPost: (id, content, authorUrn, scheduledTime, visibility = 'PUBLIC', mediaPaths = null) => {
    return db.prepare('INSERT INTO scheduled_posts (id, content, author_urn, scheduled_time, visibility, media_paths) VALUES (?, ?, ?, ?, ?, ?)')
      .run(id, content, authorUrn, scheduledTime, visibility, mediaPaths);
  },
  
  getPendingScheduledPosts: (currentTime) => {
    return db.prepare('SELECT * FROM scheduled_posts WHERE status = ? AND scheduled_time <= ?')
      .all('pending', currentTime);
  },
  
  updateScheduledPostStatus: (id, status, postId = null, error = null) => {
    const now = Math.floor(Date.now() / 1000);
    if (postId) {
      return db.prepare('UPDATE scheduled_posts SET status = ?, post_id = ?, posted_at = ?, error_message = ? WHERE id = ?')
        .run(status, postId, now, error, id);
    } else {
      return db.prepare('UPDATE scheduled_posts SET status = ?, attempts = attempts + 1, last_attempt = ?, error_message = ? WHERE id = ?')
        .run(status, now, error, id);
    }
  },
  
  // Media operations
  createMedia: (id, filePath, fileType, fileSize) => {
    return db.prepare('INSERT INTO media (id, file_path, file_type, file_size) VALUES (?, ?, ?, ?)')
      .run(id, filePath, fileType, fileSize);
  },
  
  updateMediaStatus: (id, status, assetUrn = null) => {
    const now = Math.floor(Date.now() / 1000);
    return db.prepare('UPDATE media SET status = ?, asset_urn = ?, uploaded_at = ? WHERE id = ?')
      .run(status, assetUrn, now, id);
  },
  
  getMedia: (id) => {
    return db.prepare('SELECT * FROM media WHERE id = ?').get(id);
  },
  
  // Analytics operations
  upsertAnalytics: (postId, metrics) => {
    const now = Math.floor(Date.now() / 1000);
    return db.prepare(`
      INSERT INTO analytics (post_id, impressions, clicks, likes, comments, shares, engagement_rate, fetched_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      ON CONFLICT(post_id) DO UPDATE SET
        impressions = excluded.impressions,
        clicks = excluded.clicks,
        likes = excluded.likes,
        comments = excluded.comments,
        shares = excluded.shares,
        engagement_rate = excluded.engagement_rate,
        fetched_at = excluded.fetched_at
    `).run(postId, metrics.impressions, metrics.clicks, metrics.likes, metrics.comments, metrics.shares, metrics.engagement_rate, now);
  },
  
  // Rate limit operations
  checkRateLimit: (endpoint, limit, windowMs) => {
    const now = Date.now();
    const windowStart = now - windowMs;
    
    const count = db.prepare('SELECT COUNT(*) as count FROM rate_limits WHERE endpoint = ? AND window_start >= ?')
      .get(endpoint, windowStart);
    
    return count.count < limit;
  },
  
  recordApiCall: (endpoint) => {
    const now = Date.now();
    return db.prepare('INSERT INTO rate_limits (endpoint, window_start, window_end) VALUES (?, ?, ?)')
      .run(endpoint, now, now + 3600000);
  },
  
  // OAuth token operations
  saveToken: (accessToken, refreshToken, expiresAt, scope) => {
    return db.prepare('INSERT INTO oauth_tokens (access_token, refresh_token, expires_at, scope) VALUES (?, ?, ?, ?)')
      .run(accessToken, refreshToken, expiresAt, scope);
  },
  
  getLatestToken: () => {
    return db.prepare('SELECT * FROM oauth_tokens ORDER BY created_at DESC LIMIT 1').get();
  }
};

export default db;
