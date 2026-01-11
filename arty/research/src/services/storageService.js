/**
 * Storage Service
 * Handles database operations for research system
 */

const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

class StorageService {
  constructor() {
    const dbPath = process.env.DATABASE_PATH || path.join(__dirname, '../../../store/research.db');
    
    if (!fs.existsSync(dbPath)) {
      throw new Error(`Database not found at ${dbPath}. Run 'cd store && npm run init' first.`);
    }
    
    this.db = new sqlite3.Database(dbPath);
    this.fileSystemPath = process.env.FILE_SYSTEM_PATH || path.join(__dirname, '../../../store/file_system');
  }

  /**
   * Create a new research session
   */
  async createSession(data) {
    return new Promise((resolve, reject) => {
      const sql = `INSERT INTO research_sessions (broad_field, targeted_field, status) VALUES (?, ?, ?)`;
      this.db.run(sql, [data.broad_field, data.targeted_field, 'running'], function(err) {
        if (err) reject(err);
        else resolve(this.lastID);
      });
    });
  }

  /**
   * Update research session
   */
  async updateSession(sessionId, data) {
    return new Promise((resolve, reject) => {
      const fields = Object.keys(data).map(k => `${k} = ?`).join(', ');
      const values = Object.values(data);
      
      const sql = `UPDATE research_sessions SET ${fields} WHERE id = ?`;
      this.db.run(sql, [...values, sessionId], (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  }

  /**
   * Save search results
   */
  async saveSearchResults(sessionId, results) {
    return new Promise((resolve, reject) => {
      const stmt = this.db.prepare(`
        INSERT INTO search_results (session_id, query, title, url, snippet, source)
        VALUES (?, ?, ?, ?, ?, ?)
      `);

      results.forEach(result => {
        stmt.run(sessionId, result.query || '', result.title, result.url, result.snippet, result.source);
      });

      stmt.finalize((err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  }

  /**
   * Save extracted keywords
   */
  async saveKeywords(sessionId, keywords, iteration) {
    return new Promise((resolve, reject) => {
      const stmt = this.db.prepare(`
        INSERT INTO keywords (session_id, keyword, frequency, relevance, iteration)
        VALUES (?, ?, ?, ?, ?)
      `);

      keywords.forEach(kw => {
        stmt.run(sessionId, kw.keyword, kw.frequency, kw.relevance, iteration);
      });

      stmt.finalize((err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  }

  /**
   * Save article
   */
  async saveArticle(sessionId, article) {
    return new Promise((resolve, reject) => {
      // Save to file system
      const timestamp = new Date().toISOString().split('T')[0];
      const filename = `${timestamp}-${article.title.replace(/[^a-z0-9]/gi, '-').toLowerCase()}.md`;
      const filePath = path.join(this.fileSystemPath, 'articles', filename);
      
      fs.writeFileSync(filePath, article.content);

      // Save to database
      const sql = `
        INSERT INTO articles (session_id, title, content, url, author, published_date, source_domain, word_count, file_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
      `;
      
      this.db.run(sql, [
        sessionId,
        article.title,
        article.content,
        article.url,
        article.author,
        article.published_date,
        article.source_domain,
        article.word_count,
        filePath
      ], function(err) {
        if (err) reject(err);
        else resolve(this.lastID);
      });
    });
  }

  /**
   * Save drafts
   */
  async saveDrafts(sessionId, drafts, platform) {
    return new Promise((resolve, reject) => {
      const stmt = this.db.prepare(`
        INSERT INTO drafts (session_id, platform, content, metadata, status)
        VALUES (?, ?, ?, ?, ?)
      `);

      drafts.forEach(draft => {
        const metadata = JSON.stringify(draft.metadata || {});
        stmt.run(sessionId, platform, draft.content, metadata, 'pending');
      });

      stmt.finalize((err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  }

  /**
   * Get recent keywords
   */
  async getRecentKeywords(limit = 20) {
    return new Promise((resolve, reject) => {
      const sql = `
        SELECT keyword, relevance, frequency 
        FROM keywords 
        ORDER BY created_at DESC 
        LIMIT ?
      `;
      
      this.db.all(sql, [limit], (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });
  }

  /**
   * Get pending drafts
   */
  async getPendingDrafts(platform, limit = 10) {
    return new Promise((resolve, reject) => {
      const sql = `
        SELECT id, content, metadata, created_at
        FROM drafts
        WHERE platform = ? AND status = 'pending'
        ORDER BY created_at DESC
        LIMIT ?
      `;
      
      this.db.all(sql, [platform, limit], (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });
  }

  /**
   * Mark draft as published
   */
  async markDraftPublished(draftId) {
    return new Promise((resolve, reject) => {
      const sql = `UPDATE drafts SET status = 'published', published_at = CURRENT_TIMESTAMP WHERE id = ?`;
      this.db.run(sql, [draftId], (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  }

  /**
   * Close database connection
   */
  close() {
    this.db.close();
  }
}

module.exports = StorageService;
