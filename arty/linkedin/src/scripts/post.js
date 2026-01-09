#!/usr/bin/env node
import { config } from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import LinkedInManager from '../index.js';
import logger from '../utils/logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

config({ path: path.join(__dirname, '../../../.env') });

// Parse command line arguments
const args = process.argv.slice(2);

if (args.length < 1) {
  console.log(`
Usage: node post.js [options] "Post content here"

Options:
  --media path1,path2,...    Include media files (images/videos/documents)
  --visibility PUBLIC|CONNECTIONS   Post visibility (default: PUBLIC)
  --author urn:li:...        Author URN (optional, uses env var if not provided)
  
Examples:
  node post.js "Hello LinkedIn! #networking"
  node post.js --media ./image.jpg "Check out this image!"
  node post.js --visibility CONNECTIONS "Post for my connections only"
  `);
  process.exit(1);
}

async function main() {
  try {
    // Parse arguments
    let content = '';
    let mediaPaths = null;
    let visibility = 'PUBLIC';
    let authorUrn = null;

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
      } else if (!arg.startsWith('--')) {
        content = arg;
      }
    }

    if (!content) {
      throw new Error('Post content is required');
    }

    // Initialize manager
    logger.info('Initializing LinkedIn Manager...');
    const manager = new LinkedInManager();
    await manager.initialize();

    // Post immediately
    logger.info('Creating post...');
    let result;

    if (mediaPaths && mediaPaths.length > 0) {
      result = await manager.postWithMedia(content, mediaPaths, authorUrn, visibility);
    } else {
      result = await manager.postNow(content, authorUrn, visibility);
    }

    if (result.success) {
      console.log('\n✅ Post published successfully!');
      console.log(`Post ID: ${result.postId}`);
      console.log(`Content: ${content.substring(0, 100)}...`);
      if (mediaPaths) {
        console.log(`Media: ${mediaPaths.length} file(s)`);
      }
    }

    await manager.shutdown();
    process.exit(0);
  } catch (error) {
    console.error('\n❌ Failed to post:', error.message);
    logger.error('Post failed:', error);
    process.exit(1);
  }
}

main();
