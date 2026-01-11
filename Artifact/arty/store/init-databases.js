#!/usr/bin/env node

/**
 * Database Initialization Script
 * Creates SQLite3 database with complete schema for Arty research system
 */

const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const DB_PATH = path.join(__dirname, 'research.db');

console.log('🔧 Initializing Arty Research Database...\n');

// Create database
const db = new sqlite3.Database(DB_PATH, (err) => {
  if (err) {
    console.error('❌ Error creating database:', err.message);
    process.exit(1);
  }
  console.log('✅ Connected to research.db');
});

// Schema definitions
const schema = {
  research_sessions: `
    CREATE TABLE IF NOT EXISTS research_sessions (
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
    )
  `,
  
  keywords: `
    CREATE TABLE IF NOT EXISTS keywords (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_id INTEGER,
      keyword TEXT NOT NULL,
      frequency INTEGER DEFAULT 1,
      relevance REAL DEFAULT 0.5,
      iteration INTEGER DEFAULT 1,
      source TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (session_id) REFERENCES research_sessions(id)
    )
  `,
  
  search_results: `
    CREATE TABLE IF NOT EXISTS search_results (
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
    )
  `,
  
  articles: `
    CREATE TABLE IF NOT EXISTS articles (
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
    )
  `,
  
  papers: `
    CREATE TABLE IF NOT EXISTS papers (
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
    )
  `,
  
  notes: `
    CREATE TABLE IF NOT EXISTS notes (
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
    )
  `,
  
  drafts: `
    CREATE TABLE IF NOT EXISTS drafts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_id INTEGER,
      platform TEXT NOT NULL,
      content TEXT NOT NULL,
      metadata TEXT,
      status TEXT DEFAULT 'pending',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      published_at DATETIME,
      FOREIGN KEY (session_id) REFERENCES research_sessions(id)
    )
  `,
  
  blueprints: `
    CREATE TABLE IF NOT EXISTS blueprints (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL,
      type TEXT,
      content TEXT,
      version TEXT,
      file_path TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `,
  
  topics: `
    CREATE TABLE IF NOT EXISTS topics (
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
    )
  `,
  
  post_queue: `
    CREATE TABLE IF NOT EXISTS post_queue (
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
    )
  `,
  
  engagement_context: `
    CREATE TABLE IF NOT EXISTS engagement_context (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      channel_id TEXT NOT NULL,
      user_id TEXT NOT NULL,
      message_content TEXT,
      message_id TEXT,
      topic_id INTEGER,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (topic_id) REFERENCES topics(id)
    )
  `,
  
  analysis_cache: `
    CREATE TABLE IF NOT EXISTS analysis_cache (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      cache_key TEXT UNIQUE NOT NULL,
      cache_type TEXT,
      data TEXT,
      expires_at DATETIME,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `
};

// Indexes for performance
const indexes = [
  'CREATE INDEX IF NOT EXISTS idx_keywords_relevance ON keywords(relevance DESC)',
  'CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON keywords(keyword)',
  'CREATE INDEX IF NOT EXISTS idx_search_results_session ON search_results(session_id)',
  'CREATE INDEX IF NOT EXISTS idx_articles_processed ON articles(processed)',
  'CREATE INDEX IF NOT EXISTS idx_articles_created ON articles(created_at DESC)',
  'CREATE INDEX IF NOT EXISTS idx_drafts_status ON drafts(status)',
  'CREATE INDEX IF NOT EXISTS idx_drafts_platform ON drafts(platform)',
  'CREATE INDEX IF NOT EXISTS idx_topics_platform_used ON topics(platform, used)',
  'CREATE INDEX IF NOT EXISTS idx_post_queue_scheduled ON post_queue(scheduled_time)',
  'CREATE INDEX IF NOT EXISTS idx_post_queue_status ON post_queue(status)',
  'CREATE INDEX IF NOT EXISTS idx_engagement_channel ON engagement_context(channel_id, timestamp DESC)'
];

// Create tables
db.serialize(() => {
  let tableCount = 0;
  const tableNames = Object.keys(schema);
  
  console.log(`\n📋 Creating ${tableNames.length} tables...\n`);
  
  tableNames.forEach((tableName) => {
    db.run(schema[tableName], (err) => {
      if (err) {
        console.error(`❌ Error creating ${tableName}:`, err.message);
      } else {
        tableCount++;
        console.log(`✅ Created table: ${tableName}`);
      }
    });
  });
  
  // Create indexes
  console.log(`\n🔍 Creating ${indexes.length} indexes...\n`);
  
  indexes.forEach((indexSQL, i) => {
    db.run(indexSQL, (err) => {
      if (err) {
        console.error(`❌ Error creating index ${i + 1}:`, err.message);
      } else {
        console.log(`✅ Created index ${i + 1}`);
      }
    });
  });
  
  // Verify tables
  db.all("SELECT name FROM sqlite_master WHERE type='table'", [], (err, rows) => {
    if (err) {
      console.error('❌ Error verifying tables:', err.message);
    } else {
      console.log('\n📊 Database Summary:');
      console.log(`   Tables created: ${rows.length}`);
      console.log(`   Indexes created: ${indexes.length}`);
      console.log(`   Database location: ${DB_PATH}\n`);
      console.log('✨ Database initialization complete!\n');
    }
    
    db.close();
  });
});
