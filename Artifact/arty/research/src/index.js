/**
 * Research Engine - Main Entry Point
 * Autonomous research system with zero human intervention
 */

const path = require('path');
const fs = require('fs');
require('dotenv').config();

// Load configuration
const configPath = path.join(__dirname, '../config.json');
let config;

if (fs.existsSync(configPath)) {
  config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
} else {
  console.error('❌ config.json not found. Copy config.example.json to config.json and configure it.');
  process.exit(1);
}

const SearchService = require('./services/searchService');
const AnalysisService = require('./services/analysisService');
const StorageService = require('./services/storageService');
const ContentGenerator = require('./services/contentGenerator');
const logger = require('./utils/logger');

class ResearchEngine {
  constructor(config) {
    this.config = config;
    this.searchService = new SearchService(config.search);
    this.analysisService = new AnalysisService(config.analysis);
    this.storageService = new StorageService();
    this.contentGenerator = new ContentGenerator();
  }

  /**
   * Run complete research cycle
   * @param {Object} options - Cycle options
   * @param {number} options.batch - Number of days to generate content for
   * @param {boolean} options.force - Force run even if recently executed
   */
  async runCycle(options = {}) {
    const { batch = 1, force = false } = options;
    
    logger.info('🚀 Starting research cycle...');
    logger.info(`   Broad Field: ${this.config.research.broadField}`);
    logger.info(`   Targeted Field: ${this.config.research.targetedField || 'None'}`);
    logger.info(`   Iterations: ${this.config.research.iterations}`);
    logger.info(`   Batch: ${batch} day(s)\n`);

    try {
      // Create research session
      const sessionId = await this.storageService.createSession({
        broad_field: this.config.research.broadField,
        targeted_field: this.config.research.targetedField
      });

      // Phase 1: Initial Search
      logger.info('📡 Phase 1: Initial search...');
      const initialKeywords = this.generateInitialKeywords();
      const initialResults = await this.searchService.search(
        initialKeywords.join(' '),
        { maxResults: this.config.research.maxResultsPerSearch }
      );
      
      await this.storageService.saveSearchResults(sessionId, initialResults);
      logger.info(`   Found ${initialResults.length} results\n`);

      // Phase 2: Keyword Extraction (iterative)
      logger.info('🔍 Phase 2: Keyword extraction...');
      let allKeywords = [];
      
      for (let i = 0; i < this.config.research.iterations; i++) {
        logger.info(`   Iteration ${i + 1}/${this.config.research.iterations}`);
        
        // Extract keywords from current results
        const keywords = await this.analysisService.extractKeywords(
          initialResults.map(r => r.snippet).join(' '),
          { maxKeywords: this.config.research.keywordsPerIteration }
        );
        
        allKeywords.push(...keywords);
        await this.storageService.saveKeywords(sessionId, keywords, i + 1);
        
        logger.info(`   Extracted ${keywords.length} keywords`);
      }
      
      await this.storageService.updateSession(sessionId, {
        iterations_completed: this.config.research.iterations,
        keywords_extracted: allKeywords.length
      });
      
      logger.info(`   Total keywords: ${allKeywords.length}\n`);

      // Phase 3: Refined Search
      logger.info('🔎 Phase 3: Refined search with extracted keywords...');
      const refinedQueries = this.buildRefinedQueries(initialKeywords, allKeywords);
      let allArticles = [];
      
      for (const query of refinedQueries.slice(0, 10)) { // Limit to prevent API overuse
        const results = await this.searchService.search(query, { maxResults: 10 });
        allArticles.push(...results);
        await this.storageService.saveSearchResults(sessionId, results);
      }
      
      logger.info(`   Found ${allArticles.length} additional articles\n`);

      // Phase 4: Content Generation
      if (this.config.research.contentGeneration.enabled) {
        logger.info('✍️  Phase 4: Content generation...');
        const postsToGenerate = this.config.research.contentGeneration.postsPerCycle * batch;
        
        const insights = {
          keywords: allKeywords.slice(0, 20),
          articles: allArticles.slice(0, 50),
          broadField: this.config.research.broadField,
          targetedField: this.config.research.targetedField
        };
        
        for (const platform of this.config.research.contentGeneration.platforms) {
          const posts = await this.contentGenerator.generate(insights, platform, postsToGenerate);
          await this.storageService.saveDrafts(sessionId, posts, platform);
          logger.info(`   Generated ${posts.length} posts for ${platform}`);
        }
        
        logger.info('');
      }

      // Complete session
      await this.storageService.updateSession(sessionId, {
        status: 'completed',
        completed_at: new Date().toISOString(),
        articles_found: allArticles.length,
        posts_generated: this.config.research.contentGeneration.postsPerCycle * batch * 
                        this.config.research.contentGeneration.platforms.length
      });

      logger.info('✨ Research cycle completed successfully!\n');
      return { sessionId, keywords: allKeywords.length, articles: allArticles.length };

    } catch (error) {
      logger.error('❌ Research cycle failed:', error);
      throw error;
    }
  }

  /**
   * Generate initial search keywords from configured fields
   */
  generateInitialKeywords() {
    const keywords = [this.config.research.broadField];
    if (this.config.research.targetedField) {
      keywords.push(this.config.research.targetedField);
    }
    return keywords;
  }

  /**
   * Build refined search queries combining initial and extracted keywords
   */
  buildRefinedQueries(initialKeywords, extractedKeywords) {
    const queries = [];
    const topKeywords = extractedKeywords
      .sort((a, b) => b.relevance - a.relevance)
      .slice(0, 15)
      .map(k => k.keyword);
    
    // Combine initial keywords with top extracted keywords
    for (const initial of initialKeywords) {
      for (const extracted of topKeywords.slice(0, 5)) {
        queries.push(`${initial} ${extracted}`);
      }
    }
    
    return queries;
  }
}

module.exports = ResearchEngine;

// Run if called directly
if (require.main === module) {
  const engine = new ResearchEngine(config);
  
  engine.runCycle({ batch: 1 })
    .then(() => {
      logger.info('🎉 Process complete');
      process.exit(0);
    })
    .catch((error) => {
      logger.error('💥 Fatal error:', error);
      process.exit(1);
    });
}
