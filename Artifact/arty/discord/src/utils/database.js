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
    const dbPath = process.env.DATABASE_PATH || path.join(path.dirname(path.dirname(__dirname)), 'data', 'bot.db');
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
  // Guilds table
  db.exec(`
    CREATE TABLE IF NOT EXISTS guilds (
      guild_id TEXT PRIMARY KEY,
      prefix TEXT DEFAULT '!',
      welcome_channel_id TEXT,
      goodbye_channel_id TEXT,
      log_channel_id TEXT,
      mod_log_channel_id TEXT,
      muted_role_id TEXT,
      autorole_id TEXT,
      created_at INTEGER DEFAULT (strftime('%s', 'now'))
    )
  `);
  
  // Users/Economy table
  db.exec(`
    CREATE TABLE IF NOT EXISTS economy (
      user_id TEXT,
      guild_id TEXT,
      balance INTEGER DEFAULT 0,
      bank INTEGER DEFAULT 0,
      last_daily INTEGER DEFAULT 0,
      last_work INTEGER DEFAULT 0,
      inventory TEXT DEFAULT '[]',
      PRIMARY KEY (user_id, guild_id)
    )
  `);
  
  // Leveling table
  db.exec(`
    CREATE TABLE IF NOT EXISTS levels (
      user_id TEXT,
      guild_id TEXT,
      xp INTEGER DEFAULT 0,
      level INTEGER DEFAULT 0,
      last_xp_time INTEGER DEFAULT 0,
      messages INTEGER DEFAULT 0,
      PRIMARY KEY (user_id, guild_id)
    )
  `);
  
  // Warnings table
  db.exec(`
    CREATE TABLE IF NOT EXISTS warnings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id TEXT NOT NULL,
      guild_id TEXT NOT NULL,
      moderator_id TEXT NOT NULL,
      reason TEXT,
      timestamp INTEGER DEFAULT (strftime('%s', 'now'))
    )
  `);
  
  // Mutes table
  db.exec(`
    CREATE TABLE IF NOT EXISTS mutes (
      user_id TEXT,
      guild_id TEXT,
      moderator_id TEXT NOT NULL,
      reason TEXT,
      expires_at INTEGER,
      timestamp INTEGER DEFAULT (strftime('%s', 'now')),
      PRIMARY KEY (user_id, guild_id)
    )
  `);
  
  // Bans table
  db.exec(`
    CREATE TABLE IF NOT EXISTS bans (
      user_id TEXT,
      guild_id TEXT,
      moderator_id TEXT NOT NULL,
      reason TEXT,
      expires_at INTEGER,
      timestamp INTEGER DEFAULT (strftime('%s', 'now')),
      PRIMARY KEY (user_id, guild_id)
    )
  `);
  
  // Reaction roles table
  db.exec(`
    CREATE TABLE IF NOT EXISTS reaction_roles (
      message_id TEXT NOT NULL,
      guild_id TEXT NOT NULL,
      channel_id TEXT NOT NULL,
      emoji TEXT NOT NULL,
      role_id TEXT NOT NULL,
      PRIMARY KEY (message_id, emoji)
    )
  `);
  
  // Custom commands table
  db.exec(`
    CREATE TABLE IF NOT EXISTS custom_commands (
      guild_id TEXT NOT NULL,
      name TEXT NOT NULL,
      response TEXT NOT NULL,
      created_by TEXT NOT NULL,
      created_at INTEGER DEFAULT (strftime('%s', 'now')),
      PRIMARY KEY (guild_id, name)
    )
  `);
  
  // Tickets table
  db.exec(`
    CREATE TABLE IF NOT EXISTS tickets (
      ticket_id TEXT PRIMARY KEY,
      guild_id TEXT NOT NULL,
      channel_id TEXT NOT NULL,
      user_id TEXT NOT NULL,
      type TEXT DEFAULT 'support',
      status TEXT DEFAULT 'open',
      created_at INTEGER DEFAULT (strftime('%s', 'now')),
      closed_at INTEGER,
      closed_by TEXT
    )
  `);
  
  // Giveaways table
  db.exec(`
    CREATE TABLE IF NOT EXISTS giveaways (
      message_id TEXT PRIMARY KEY,
      guild_id TEXT NOT NULL,
      channel_id TEXT NOT NULL,
      prize TEXT NOT NULL,
      winner_count INTEGER DEFAULT 1,
      host_id TEXT NOT NULL,
      ends_at INTEGER NOT NULL,
      ended BOOLEAN DEFAULT 0,
      created_at INTEGER DEFAULT (strftime('%s', 'now'))
    )
  `);
  
  // Polls table
  db.exec(`
    CREATE TABLE IF NOT EXISTS polls (
      message_id TEXT PRIMARY KEY,
      guild_id TEXT NOT NULL,
      channel_id TEXT NOT NULL,
      question TEXT NOT NULL,
      options TEXT NOT NULL,
      creator_id TEXT NOT NULL,
      ends_at INTEGER,
      ended BOOLEAN DEFAULT 0,
      created_at INTEGER DEFAULT (strftime('%s', 'now'))
    )
  `);
  
  // Reminders table
  db.exec(`
    CREATE TABLE IF NOT EXISTS reminders (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id TEXT NOT NULL,
      guild_id TEXT,
      channel_id TEXT NOT NULL,
      message TEXT NOT NULL,
      remind_at INTEGER NOT NULL,
      created_at INTEGER DEFAULT (strftime('%s', 'now')),
      completed BOOLEAN DEFAULT 0
    )
  `);
  
  // Moderation logs table
  db.exec(`
    CREATE TABLE IF NOT EXISTS mod_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      guild_id TEXT NOT NULL,
      action TEXT NOT NULL,
      moderator_id TEXT NOT NULL,
      target_id TEXT NOT NULL,
      reason TEXT,
      timestamp INTEGER DEFAULT (strftime('%s', 'now'))
    )
  `);
  
  // Server backups table
  db.exec(`
    CREATE TABLE IF NOT EXISTS backups (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      guild_id TEXT NOT NULL,
      backup_data TEXT NOT NULL,
      created_by TEXT NOT NULL,
      created_at INTEGER DEFAULT (strftime('%s', 'now'))
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
  // Guild operations
  getGuild: (guildId) => {
    return db.prepare('SELECT * FROM guilds WHERE guild_id = ?').get(guildId);
  },
  
  upsertGuild: (guildId, data) => {
    const columns = Object.keys(data).join(', ');
    const placeholders = Object.keys(data).map(() => '?').join(', ');
    const updates = Object.keys(data).map(col => `${col} = excluded.${col}`).join(', ');
    
    return db.prepare(`
      INSERT INTO guilds (guild_id, ${columns})
      VALUES (?, ${placeholders})
      ON CONFLICT(guild_id) DO UPDATE SET ${updates}
    `).run(guildId, ...Object.values(data));
  },
  
  // Economy operations
  getEconomy: (userId, guildId) => {
    return db.prepare('SELECT * FROM economy WHERE user_id = ? AND guild_id = ?').get(userId, guildId);
  },
  
  upsertEconomy: (userId, guildId, data) => {
    const existing = queries.getEconomy(userId, guildId);
    if (existing) {
      const updates = Object.keys(data).map(col => `${col} = ?`).join(', ');
      return db.prepare(`UPDATE economy SET ${updates} WHERE user_id = ? AND guild_id = ?`)
        .run(...Object.values(data), userId, guildId);
    } else {
      const columns = Object.keys(data).join(', ');
      const placeholders = Object.keys(data).map(() => '?').join(', ');
      return db.prepare(`INSERT INTO economy (user_id, guild_id, ${columns}) VALUES (?, ?, ${placeholders})`)
        .run(userId, guildId, ...Object.values(data));
    }
  },
  
  // Leveling operations
  getLevel: (userId, guildId) => {
    return db.prepare('SELECT * FROM levels WHERE user_id = ? AND guild_id = ?').get(userId, guildId);
  },
  
  upsertLevel: (userId, guildId, data) => {
    const existing = queries.getLevel(userId, guildId);
    if (existing) {
      const updates = Object.keys(data).map(col => `${col} = ?`).join(', ');
      return db.prepare(`UPDATE levels SET ${updates} WHERE user_id = ? AND guild_id = ?`)
        .run(...Object.values(data), userId, guildId);
    } else {
      const columns = Object.keys(data).join(', ');
      const placeholders = Object.keys(data).map(() => '?').join(', ');
      return db.prepare(`INSERT INTO levels (user_id, guild_id, ${columns}) VALUES (?, ?, ${placeholders})`)
        .run(userId, guildId, ...Object.values(data));
    }
  },
  
  // Warning operations
  addWarning: (userId, guildId, moderatorId, reason) => {
    return db.prepare('INSERT INTO warnings (user_id, guild_id, moderator_id, reason) VALUES (?, ?, ?, ?)')
      .run(userId, guildId, moderatorId, reason);
  },
  
  getWarnings: (userId, guildId) => {
    return db.prepare('SELECT * FROM warnings WHERE user_id = ? AND guild_id = ? ORDER BY timestamp DESC')
      .all(userId, guildId);
  },
  
  clearWarnings: (userId, guildId) => {
    return db.prepare('DELETE FROM warnings WHERE user_id = ? AND guild_id = ?').run(userId, guildId);
  },
  
  // Moderation log
  addModLog: (guildId, action, moderatorId, targetId, reason) => {
    return db.prepare('INSERT INTO mod_logs (guild_id, action, moderator_id, target_id, reason) VALUES (?, ?, ?, ?, ?)')
      .run(guildId, action, moderatorId, targetId, reason);
  }
};

export default db;
