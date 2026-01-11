/**
 * Search Service
 * Handles web search via Brave, Serper, or SerpAPI
 */

const axios = require('axios');
const logger = require('../utils/logger');

class SearchService {
  constructor(config) {
    this.config = config;
    this.defaultAPI = process.env.DEFAULT_SEARCH_API || config.defaultAPI || 'brave';
  }

  /**
   * Search the web
   * @param {string} query - Search query
   * @param {Object} options - Search options
   * @returns {Promise<Array>} Search results
   */
  async search(query, options = {}) {
    const { maxResults = 20, api = this.defaultAPI } = options;
    
    try {
      logger.info(`🔍 Searching: "${query}" via ${api}`);
      
      switch (api) {
        case 'brave':
          return await this.searchBrave(query, maxResults);
        case 'serper':
          return await this.searchSerper(query, maxResults);
        case 'serpapi':
          return await this.searchSerpAPI(query, maxResults);
        default:
          throw new Error(`Unknown search API: ${api}`);
      }
    } catch (error) {
      logger.error(`Search failed for "${query}":`, error.message);
      return [];
    }
  }

  /**
   * Brave Search API
   */
  async searchBrave(query, maxResults) {
    const apiKey = process.env.BRAVE_SEARCH_API_KEY;
    if (!apiKey) {
      logger.warn('Brave API key not configured, skipping search');
      return [];
    }

    try {
      const response = await axios.get('https://api.search.brave.com/res/v1/web/search', {
        headers: {
          'Accept': 'application/json',
          'X-Subscription-Token': apiKey
        },
        params: {
          q: query,
          count: Math.min(maxResults, 20)
        },
        timeout: this.config.timeout || 30000
      });

      return response.data.web?.results?.map(result => ({
        title: result.title,
        url: result.url,
        snippet: result.description,
        source: 'brave'
      })) || [];
    } catch (error) {
      logger.error('Brave search error:', error.message);
      return [];
    }
  }

  /**
   * Serper API
   */
  async searchSerper(query, maxResults) {
    const apiKey = process.env.SERPER_API_KEY;
    if (!apiKey) {
      logger.warn('Serper API key not configured, skipping search');
      return [];
    }

    try {
      const response = await axios.post('https://google.serper.dev/search', {
        q: query,
        num: Math.min(maxResults, 100)
      }, {
        headers: {
          'X-API-KEY': apiKey,
          'Content-Type': 'application/json'
        },
        timeout: this.config.timeout || 30000
      });

      return response.data.organic?.map(result => ({
        title: result.title,
        url: result.link,
        snippet: result.snippet,
        source: 'serper'
      })) || [];
    } catch (error) {
      logger.error('Serper search error:', error.message);
      return [];
    }
  }

  /**
   * SerpAPI
   */
  async searchSerpAPI(query, maxResults) {
    const apiKey = process.env.SERPAPI_KEY;
    if (!apiKey) {
      logger.warn('SerpAPI key not configured, skipping search');
      return [];
    }

    try {
      const response = await axios.get('https://serpapi.com/search', {
        params: {
          q: query,
          api_key: apiKey,
          num: Math.min(maxResults, 100)
        },
        timeout: this.config.timeout || 30000
      });

      return response.data.organic_results?.map(result => ({
        title: result.title,
        url: result.link,
        snippet: result.snippet,
        source: 'serpapi'
      })) || [];
    } catch (error) {
      logger.error('SerpAPI search error:', error.message);
      return [];
    }
  }

  /**
   * Batch search multiple queries
   */
  async batchSearch(queries, options = {}) {
    const results = [];
    
    for (const query of queries) {
      const queryResults = await this.search(query, options);
      results.push(...queryResults);
      
      // Rate limiting: wait 1 second between searches
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    return results;
  }
}

module.exports = SearchService;
