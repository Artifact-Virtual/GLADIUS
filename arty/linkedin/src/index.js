import { config } from 'dotenv';
import { readFileSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import logger from './utils/logger.js';
import { initializeDatabase } from './utils/database.js';
import LinkedInService from './services/linkedinService.js';
import SchedulerService from './services/schedulerService.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables
config();

// Load configuration
let linkedinConfig;
try {
  const configPath = path.join(path.dirname(__dirname), 'config.json');
  linkedinConfig = JSON.parse(readFileSync(configPath, 'utf-8'));
} catch (error) {
  const examplePath = path.join(path.dirname(__dirname), 'config.example.json');
  linkedinConfig = JSON.parse(readFileSync(examplePath, 'utf-8'));
  logger.warn('config.json not found, using config.example.json. Please create config.json from config.example.json');
}

class LinkedInManager {
  constructor() {
    this.config = linkedinConfig;
    this.linkedInService = null;
    this.schedulerService = null;
    this.isInitialized = false;
  }
  
  async initialize() {
    try {
      logger.info('Initializing LinkedIn Manager...');
      
      // Initialize database
      logger.info('Initializing database...');
      await initializeDatabase();
      
      // Check for access token
      const accessToken = process.env.LINKEDIN_ACCESS_TOKEN;
      if (!accessToken) {
        throw new Error('LINKEDIN_ACCESS_TOKEN not found in environment variables');
      }
      
      // Initialize LinkedIn service
      logger.info('Initializing LinkedIn service...');
      this.linkedInService = new LinkedInService(accessToken, this.config);
      
      // Initialize scheduler service
      if (this.config.scheduling?.enabled) {
        logger.info('Initializing scheduler service...');
        this.schedulerService = new SchedulerService(this.linkedInService, this.config);
        
        if (process.env.SCHEDULER_ENABLED !== 'false') {
          this.schedulerService.start();
        }
      }
      
      this.isInitialized = true;
      logger.info('LinkedIn Manager initialized successfully');
      
      return this;
    } catch (error) {
      logger.error('Failed to initialize LinkedIn Manager:', error);
      throw error;
    }
  }
  
  /**
   * Create and publish a text post immediately
   */
  async postNow(content, authorUrn = null, visibility = 'PUBLIC') {
    if (!this.isInitialized) {
      throw new Error('LinkedIn Manager not initialized. Call initialize() first.');
    }
    
    const author = authorUrn || process.env.LINKEDIN_PERSON_URN || process.env.LINKEDIN_ORGANIZATION_URN;
    if (!author) {
      throw new Error('Author URN not provided and not found in environment variables');
    }
    
    try {
      const result = await this.linkedInService.createTextPost(content, author, visibility);
      return result;
    } catch (error) {
      logger.error('Failed to post:', error);
      throw error;
    }
  }
  
  /**
   * Create and publish a post with media immediately
   */
  async postWithMedia(content, mediaPaths, authorUrn = null, visibility = 'PUBLIC') {
    if (!this.isInitialized) {
      throw new Error('LinkedIn Manager not initialized. Call initialize() first.');
    }
    
    const author = authorUrn || process.env.LINKEDIN_PERSON_URN || process.env.LINKEDIN_ORGANIZATION_URN;
    if (!author) {
      throw new Error('Author URN not provided and not found in environment variables');
    }
    
    try {
      // Upload all media
      const mediaAssets = [];
      for (const mediaPath of mediaPaths) {
        const uploadResult = await this.linkedInService.uploadMedia(mediaPath, author);
        mediaAssets.push(uploadResult.asset);
      }
      
      // Create post with media
      const result = await this.linkedInService.createMediaPost(content, author, mediaAssets, visibility);
      
      // Clean up media if configured
      if (this.config.media?.autoCleanup?.afterPost) {
        await this.cleanupMedia(mediaPaths);
      }
      
      return result;
    } catch (error) {
      logger.error('Failed to post with media:', error);
      throw error;
    }
  }
  
  /**
   * Schedule a post for later
   */
  async schedulePost(content, scheduledTime, mediaPaths = null, authorUrn = null, visibility = 'PUBLIC') {
    if (!this.isInitialized) {
      throw new Error('LinkedIn Manager not initialized. Call initialize() first.');
    }
    
    if (!this.schedulerService) {
      throw new Error('Scheduler service not initialized. Enable scheduling in config.');
    }
    
    const author = authorUrn || process.env.LINKEDIN_PERSON_URN || process.env.LINKEDIN_ORGANIZATION_URN;
    if (!author) {
      throw new Error('Author URN not provided and not found in environment variables');
    }
    
    try {
      const result = this.schedulerService.schedulePost(content, author, scheduledTime, visibility, mediaPaths);
      return result;
    } catch (error) {
      logger.error('Failed to schedule post:', error);
      throw error;
    }
  }
  
  /**
   * Cancel a scheduled post
   */
  async cancelScheduledPost(scheduledPostId) {
    if (!this.schedulerService) {
      throw new Error('Scheduler service not initialized');
    }
    
    return this.schedulerService.cancelScheduledPost(scheduledPostId);
  }
  
  /**
   * Get post analytics
   */
  async getAnalytics(postUrn) {
    if (!this.isInitialized) {
      throw new Error('LinkedIn Manager not initialized');
    }
    
    return this.linkedInService.getPostAnalytics(postUrn);
  }
  
  /**
   * Delete a post
   */
  async deletePost(postUrn) {
    if (!this.isInitialized) {
      throw new Error('LinkedIn Manager not initialized');
    }
    
    return this.linkedInService.deletePost(postUrn);
  }
  
  /**
   * Clean up media files
   */
  async cleanupMedia(mediaPaths) {
    const { unlink } = await import('fs/promises');
    
    for (const mediaPath of mediaPaths) {
      try {
        await unlink(mediaPath);
        logger.info(`Cleaned up media file: ${mediaPath}`);
      } catch (error) {
        logger.error(`Failed to cleanup media ${mediaPath}:`, error);
      }
    }
  }
  
  /**
   * Shutdown the manager gracefully
   */
  async shutdown() {
    logger.info('Shutting down LinkedIn Manager...');
    
    if (this.schedulerService) {
      this.schedulerService.stop();
    }
    
    logger.info('LinkedIn Manager shut down successfully');
  }
}

// Handle process events
process.on('SIGINT', async () => {
  logger.info('Received SIGINT, shutting down gracefully...');
  if (global.linkedInManager) {
    await global.linkedInManager.shutdown();
  }
  process.exit(0);
});

process.on('SIGTERM', async () => {
  logger.info('Received SIGTERM, shutting down gracefully...');
  if (global.linkedInManager) {
    await global.linkedInManager.shutdown();
  }
  process.exit(0);
});

// Export for use as a module
export default LinkedInManager;

// If run directly, initialize and start
if (import.meta.url === `file://${process.argv[1]}`) {
  (async () => {
    try {
      const manager = new LinkedInManager();
      await manager.initialize();
      global.linkedInManager = manager;
      
      logger.info('LinkedIn Manager is running. Press Ctrl+C to stop.');
    } catch (error) {
      logger.error('Fatal error:', error);
      process.exit(1);
    }
  })();
}
