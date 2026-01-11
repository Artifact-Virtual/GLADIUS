#!/usr/bin/env node
import { config } from 'dotenv';
import { readdir, unlink, stat } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import logger from '../utils/logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

config();

async function cleanupOldMedia() {
  const mediaPath = process.env.MEDIA_STORAGE_PATH || path.join(path.dirname(path.dirname(__dirname)), 'media');
  const olderThanDays = parseInt(process.env.CLEANUP_OLD_MEDIA_DAYS) || 30;
  const cutoffTime = Date.now() - (olderThanDays * 24 * 60 * 60 * 1000);
  
  try {
    const files = await readdir(mediaPath);
    let deletedCount = 0;
    let totalSize = 0;
    
    for (const file of files) {
      const filePath = path.join(mediaPath, file);
      const stats = await stat(filePath);
      
      if (stats.mtimeMs < cutoffTime) {
        const size = stats.size;
        await unlink(filePath);
        deletedCount++;
        totalSize += size;
        logger.info(`Deleted old media file: ${file} (${(size / 1024 / 1024).toFixed(2)} MB)`);
      }
    }
    
    console.log(`\n✅ Cleaned up ${deletedCount} old media file(s)`);
    console.log(`   Total space freed: ${(totalSize / 1024 / 1024).toFixed(2)} MB`);
  } catch (error) {
    logger.error('Failed to cleanup old media:', error);
    console.error('❌ Media cleanup failed:', error.message);
  }
}

async function cleanupOldLogs() {
  const logsPath = process.env.LOG_DIR || path.join(path.dirname(path.dirname(__dirname)), 'logs');
  const olderThanDays = parseInt(process.env.CLEANUP_OLD_LOGS_DAYS) || 30;
  const cutoffTime = Date.now() - (olderThanDays * 24 * 60 * 60 * 1000);
  
  try {
    const files = await readdir(logsPath);
    let deletedCount = 0;
    let totalSize = 0;
    
    for (const file of files) {
      // Skip the current day's logs
      if (file.includes(new Date().toISOString().split('T')[0])) {
        continue;
      }
      
      const filePath = path.join(logsPath, file);
      const stats = await stat(filePath);
      
      if (stats.mtimeMs < cutoffTime) {
        const size = stats.size;
        await unlink(filePath);
        deletedCount++;
        totalSize += size;
        logger.info(`Deleted old log file: ${file} (${(size / 1024).toFixed(2)} KB)`);
      }
    }
    
    console.log(`\n✅ Cleaned up ${deletedCount} old log file(s)`);
    console.log(`   Total space freed: ${(totalSize / 1024).toFixed(2)} KB`);
  } catch (error) {
    logger.error('Failed to cleanup old logs:', error);
    console.error('❌ Log cleanup failed:', error.message);
  }
}

async function cleanupTempFiles() {
  const tempPath = process.env.MEDIA_STORAGE_PATH 
    ? path.join(process.env.MEDIA_STORAGE_PATH, 'temp')
    : path.join(path.dirname(path.dirname(__dirname)), 'media', 'temp');
  
  try {
    const files = await readdir(tempPath);
    let deletedCount = 0;
    
    for (const file of files) {
      const filePath = path.join(tempPath, file);
      await unlink(filePath);
      deletedCount++;
      logger.info(`Deleted temp file: ${file}`);
    }
    
    console.log(`\n✅ Cleaned up ${deletedCount} temporary file(s)`);
  } catch (error) {
    // Temp directory might not exist yet
    if (error.code !== 'ENOENT') {
      logger.error('Failed to cleanup temp files:', error);
      console.error('❌ Temp cleanup failed:', error.message);
    }
  }
}

async function main() {
  console.log('🧹 Starting cleanup process...\n');
  
  const args = process.argv.slice(2);
  const cleanupMedia = args.includes('--media') || args.length === 0;
  const cleanupLogs = args.includes('--logs') || args.length === 0;
  const cleanupTemp = args.includes('--temp') || args.length === 0;
  
  if (cleanupMedia) {
    console.log('Cleaning up old media files...');
    await cleanupOldMedia();
  }
  
  if (cleanupLogs) {
    console.log('\nCleaning up old log files...');
    await cleanupOldLogs();
  }
  
  if (cleanupTemp) {
    console.log('\nCleaning up temporary files...');
    await cleanupTempFiles();
  }
  
  console.log('\n✨ Cleanup complete!');
}

// Show usage if --help
if (process.argv.includes('--help')) {
  console.log(`
Usage: node cleanup.js [options]

Options:
  --media     Clean up old media files
  --logs      Clean up old log files
  --temp      Clean up temporary files
  --help      Show this help message
  
If no options are provided, all cleanup tasks will run.

Configuration:
  CLEANUP_OLD_MEDIA_DAYS: ${process.env.CLEANUP_OLD_MEDIA_DAYS || 30} days
  CLEANUP_OLD_LOGS_DAYS: ${process.env.CLEANUP_OLD_LOGS_DAYS || 30} days
  `);
  process.exit(0);
}

main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
