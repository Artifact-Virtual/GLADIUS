#!/usr/bin/env node

/**
 * Run Research Cycle Script
 * Execute a complete research cycle
 */

const path = require('path');
const fs = require('fs');
require('dotenv').config({ path: path.join(__dirname, '../../.env') });

// Load configuration
const configPath = path.join(__dirname, '../../config.json');
if (!fs.existsSync(configPath)) {
  console.error('❌ config.json not found. Copy config.example.json to config.json first.');
  process.exit(1);
}

const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
const ResearchEngine = require('../index');
const logger = require('../utils/logger');

// Parse command line arguments
const args = process.argv.slice(2);
const options = {
  batch: 1,
  force: false
};

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--batch' && args[i + 1]) {
    options.batch = parseInt(args[i + 1], 10);
    i++;
  } else if (args[i] === '--force') {
    options.force = true;
  }
}

// Run cycle
logger.info('=' .repeat(60));
logger.info('ARTY RESEARCH CYCLE');
logger.info('=' .repeat(60));

const engine = new ResearchEngine(config);

engine.runCycle(options)
  .then((result) => {
    logger.info('=' .repeat(60));
    logger.info('✨ Research cycle completed successfully!');
    logger.info(`   Session ID: ${result.sessionId}`);
    logger.info(`   Keywords extracted: ${result.keywords}`);
    logger.info(`   Articles found: ${result.articles}`);
    logger.info('=' .repeat(60));
    process.exit(0);
  })
  .catch((error) => {
    logger.error('=' .repeat(60));
    logger.error('❌ Research cycle failed');
    logger.error(error);
    logger.error('=' .repeat(60));
    process.exit(1);
  });
