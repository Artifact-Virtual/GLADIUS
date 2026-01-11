#!/usr/bin/env node
import { config } from 'dotenv';
import LinkedInManager from '../index.js';
import logger from '../utils/logger.js';

config();

// Parse command line arguments
const args = process.argv.slice(2);

if (args.length < 2) {
  console.log(`
Usage: node scheduler.js [options] "Post content" "Schedule time"

Options:
  --media path1,path2,...    Include media files
  --visibility PUBLIC|CONNECTIONS   Post visibility (default: PUBLIC)
  --author urn:li:...        Author URN (optional)
  --cancel <scheduled_id>    Cancel a scheduled post
  
Schedule time formats:
  - ISO 8601: "2026-01-10T14:00:00Z"
  - Relative: "2h" (2 hours), "1d" (1 day), "30m" (30 minutes)
  
Examples:
  node scheduler.js "Future post" "2026-01-10T14:00:00Z"
  node scheduler.js --media ./image.jpg "Scheduled post" "2h"
  node scheduler.js --cancel scheduled_12345
  `);
  process.exit(1);
}

function parseRelativeTime(timeStr) {
  const regex = /^(\d+)([mhd])$/;
  const match = timeStr.match(regex);
  
  if (!match) return null;
  
  const value = parseInt(match[1]);
  const unit = match[2];
  
  const multipliers = {
    'm': 60 * 1000,
    'h': 60 * 60 * 1000,
    'd': 24 * 60 * 60 * 1000
  };
  
  return new Date(Date.now() + value * multipliers[unit]);
}

async function main() {
  try {
    // Parse arguments
    let content = '';
    let scheduleTime = null;
    let mediaPaths = null;
    let visibility = 'PUBLIC';
    let authorUrn = null;
    let cancelId = null;
    
    for (let i = 0; i < args.length; i++) {
      const arg = args[i];
      
      if (arg === '--media' && args[i + 1]) {
        mediaPaths = args[i + 1].split(',').map(p => p.trim());
        i++;
      } else if (arg === '--visibility' && args[i + 1]) {
        visibility = args[i + 1].toUpperCase();
        i++;
      } else if (arg === '--author' && args[i + 1]) {
        authorUrn = args[i + 1];
        i++;
      } else if (arg === '--cancel' && args[i + 1]) {
        cancelId = args[i + 1];
        i++;
      } else if (!arg.startsWith('--')) {
        if (!content) {
          content = arg;
        } else if (!scheduleTime) {
          scheduleTime = arg;
        }
      }
    }
    
    // Initialize manager
    logger.info('Initializing LinkedIn Manager...');
    const manager = new LinkedInManager();
    await manager.initialize();
    
    // Handle cancel
    if (cancelId) {
      const result = await manager.cancelScheduledPost(cancelId);
      console.log('\n✅ Scheduled post cancelled successfully!');
      console.log(`Cancelled ID: ${cancelId}`);
      await manager.shutdown();
      process.exit(0);
      return;
    }
    
    // Validate inputs
    if (!content || !scheduleTime) {
      throw new Error('Post content and schedule time are required');
    }
    
    // Parse schedule time
    let parsedTime;
    
    // Try relative time first
    parsedTime = parseRelativeTime(scheduleTime);
    
    // If not relative, try ISO format
    if (!parsedTime) {
      parsedTime = new Date(scheduleTime);
      if (isNaN(parsedTime.getTime())) {
        throw new Error('Invalid schedule time format');
      }
    }
    
    // Schedule post
    logger.info('Scheduling post...');
    const result = await manager.schedulePost(content, parsedTime, mediaPaths, authorUrn, visibility);
    
    if (result.success) {
      console.log('\n✅ Post scheduled successfully!');
      console.log(`Scheduled ID: ${result.scheduledPostId}`);
      console.log(`Scheduled Time: ${result.scheduledTime}`);
      console.log(`Content: ${content.substring(0, 100)}...`);
      if (mediaPaths) {
        console.log(`Media: ${mediaPaths.length} file(s)`);
      }
      console.log('\nThe scheduler will automatically publish this post at the scheduled time.');
    }
    
    await manager.shutdown();
    process.exit(0);
  } catch (error) {
    console.error('\n❌ Failed to schedule post:', error.message);
    logger.error('Schedule failed:', error);
    process.exit(1);
  }
}

main();
