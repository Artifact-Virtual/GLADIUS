import cron from 'node-cron';
import logger from '../utils/logger.js';
import { queries, getDatabase } from '../utils/database.js';
import LinkedInService from './linkedinService.js';
import { readFileSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class SchedulerService {
  constructor(linkedInService, config) {
    this.linkedInService = linkedInService;
    this.config = config;
    this.isRunning = false;
  }
  
  /**
   * Start the scheduler
   */
  start() {
    if (this.isRunning) {
      logger.warn('Scheduler is already running');
      return;
    }
    
    this.isRunning = true;
    logger.info('Starting LinkedIn post scheduler...');
    
    // Check for scheduled posts every minute
    const checkInterval = this.config.scheduling?.checkInterval || 60000;
    this.schedulerInterval = setInterval(() => {
      this.checkScheduledPosts();
    }, checkInterval);
    
    logger.info(`Scheduler started with check interval: ${checkInterval}ms`);
  }
  
  /**
   * Stop the scheduler
   */
  stop() {
    if (!this.isRunning) {
      logger.warn('Scheduler is not running');
      return;
    }
    
    if (this.schedulerInterval) {
      clearInterval(this.schedulerInterval);
      this.schedulerInterval = null;
    }
    
    this.isRunning = false;
    logger.info('Scheduler stopped');
  }
  
  /**
   * Check for posts that need to be published
   */
  async checkScheduledPosts() {
    try {
      const now = Math.floor(Date.now() / 1000);
      const pendingPosts = queries.getPendingScheduledPosts(now);
      
      if (pendingPosts.length === 0) {
        logger.debug('No scheduled posts to publish');
        return;
      }
      
      logger.info(`Found ${pendingPosts.length} scheduled post(s) to publish`);
      
      for (const scheduledPost of pendingPosts) {
        await this.publishScheduledPost(scheduledPost);
      }
    } catch (error) {
      logger.error('Error checking scheduled posts:', error);
    }
  }
  
  /**
   * Publish a scheduled post
   */
  async publishScheduledPost(scheduledPost) {
    try {
      logger.schedule('PUBLISHING', scheduledPost.id, new Date(scheduledPost.scheduled_time * 1000).toISOString());
      
      // Check rate limits
      if (!this.linkedInService.checkRateLimit('/ugcPosts')) {
        logger.warn(`Rate limit reached, deferring post ${scheduledPost.id}`);
        queries.updateScheduledPostStatus(scheduledPost.id, 'deferred', null, 'Rate limit reached');
        return;
      }
      
      let postResult;
      
      // Check if post has media
      if (scheduledPost.media_paths) {
        const mediaPaths = JSON.parse(scheduledPost.media_paths);
        const mediaAssets = [];
        
        // Upload all media
        for (const mediaPath of mediaPaths) {
          try {
            const uploadResult = await this.linkedInService.uploadMedia(mediaPath, scheduledPost.author_urn);
            mediaAssets.push(uploadResult.asset);
          } catch (error) {
            logger.error(`Failed to upload media ${mediaPath}:`, error);
            throw error;
          }
        }
        
        // Create post with media
        postResult = await this.linkedInService.createMediaPost(
          scheduledPost.content,
          scheduledPost.author_urn,
          mediaAssets,
          scheduledPost.visibility
        );
      } else {
        // Create text-only post
        postResult = await this.linkedInService.createTextPost(
          scheduledPost.content,
          scheduledPost.author_urn,
          scheduledPost.visibility
        );
      }
      
      if (postResult.success) {
        // Update scheduled post status
        queries.updateScheduledPostStatus(scheduledPost.id, 'published', postResult.postId, null);
        
        // Create post record
        queries.createPost(postResult.postId, scheduledPost.content, scheduledPost.author_urn, scheduledPost.visibility);
        queries.updatePostStatus(postResult.postId, 'published', Math.floor(Date.now() / 1000), null, null);
        
        logger.post('PUBLISHED', postResult.postId, { scheduledId: scheduledPost.id });
        
        // Clean up media if configured
        if (scheduledPost.media_paths && this.config.media?.autoCleanup?.afterPost) {
          await this.cleanupMedia(JSON.parse(scheduledPost.media_paths));
        }
      }
    } catch (error) {
      logger.error(`Failed to publish scheduled post ${scheduledPost.id}:`, error);
      
      // Update scheduled post with error
      const maxRetries = this.config.rateLimiting?.backoff?.maxRetries || 3;
      const newStatus = scheduledPost.attempts >= maxRetries ? 'failed' : 'pending';
      
      queries.updateScheduledPostStatus(
        scheduledPost.id,
        newStatus,
        null,
        error.message
      );
    }
  }
  
  /**
   * Schedule a new post
   */
  schedulePost(content, authorUrn, scheduledTime, visibility = 'PUBLIC', mediaPaths = null) {
    try {
      const postId = `scheduled_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const scheduledTimestamp = Math.floor(new Date(scheduledTime).getTime() / 1000);
      
      // Validate scheduled time
      const now = Math.floor(Date.now() / 1000);
      const minScheduleAhead = this.config.scheduling?.minScheduleAheadTime || 300000; // 5 minutes
      
      if (scheduledTimestamp < now + (minScheduleAhead / 1000)) {
        throw new Error('Scheduled time must be at least 5 minutes in the future');
      }
      
      const maxScheduleAheadDays = this.config.scheduling?.maxScheduleAheadDays || 90;
      const maxScheduleTimestamp = now + (maxScheduleAheadDays * 86400);
      
      if (scheduledTimestamp > maxScheduleTimestamp) {
        throw new Error(`Scheduled time cannot be more than ${maxScheduleAheadDays} days in the future`);
      }
      
      // Create scheduled post
      const mediaPathsStr = mediaPaths ? JSON.stringify(mediaPaths) : null;
      queries.createScheduledPost(postId, content, authorUrn, scheduledTimestamp, visibility, mediaPathsStr);
      
      logger.schedule('CREATED', postId, new Date(scheduledTimestamp * 1000).toISOString());
      
      return {
        success: true,
        scheduledPostId: postId,
        scheduledTime: new Date(scheduledTimestamp * 1000).toISOString()
      };
    } catch (error) {
      logger.error('Failed to schedule post:', error);
      throw error;
    }
  }
  
  /**
   * Cancel a scheduled post
   */
  cancelScheduledPost(scheduledPostId) {
    try {
      queries.updateScheduledPostStatus(scheduledPostId, 'cancelled', null, 'Cancelled by user');
      logger.schedule('CANCELLED', scheduledPostId, null);
      
      return {
        success: true,
        message: 'Scheduled post cancelled'
      };
    } catch (error) {
      logger.error('Failed to cancel scheduled post:', error);
      throw error;
    }
  }
  
  /**
   * Clean up media files
   */
  async cleanupMedia(mediaPaths) {
    if (!process.env.AUTO_DELETE_MEDIA_AFTER_POST) return;
    
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
}

export default SchedulerService;
