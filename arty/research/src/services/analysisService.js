/**
 * Analysis Service
 * Keyword extraction, entity recognition, sentiment analysis
 * No LLM - uses statistical methods (TF-IDF, NLP)
 */

const natural = require('natural');
const TfIdf = natural.TfIdf;
const tokenizer = new natural.WordTokenizer();

class AnalysisService {
  constructor(config) {
    this.config = config;
    this.tfidf = new TfIdf();
    
    // Common stop words to filter out
    this.stopWords = new Set([
      'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
      'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
      'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
      'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'it',
      'its', 'their', 'there', 'they', 'them', 'we', 'our', 'you', 'your'
    ]);
  }

  /**
   * Extract keywords from text using TF-IDF
   * @param {string} text - Text to analyze
   * @param {Object} options - Extraction options
   * @returns {Array} Keywords with relevance scores
   */
  extractKeywords(text, options = {}) {
    const { maxKeywords = 10, minRelevance = 0.5 } = options;
    
    if (!text || text.trim().length === 0) {
      return [];
    }

    // Tokenize and clean text
    const tokens = tokenizer.tokenize(text.toLowerCase());
    const filtered = tokens.filter(token => 
      token.length > 3 && 
      !this.stopWords.has(token) &&
      /^[a-z]+$/.test(token) // Only alphabetic tokens
    );

    // Calculate word frequency
    const frequency = {};
    filtered.forEach(token => {
      frequency[token] = (frequency[token] || 0) + 1;
    });

    // Calculate TF-IDF scores (simplified)
    const keywords = Object.entries(frequency)
      .map(([keyword, freq]) => {
        // Simple relevance: frequency normalized by text length
        const relevance = freq / filtered.length;
        return {
          keyword,
          frequency: freq,
          relevance: Math.min(relevance * 10, 1.0) // Scale to 0-1
        };
      })
      .filter(k => k.relevance >= minRelevance)
      .sort((a, b) => b.relevance - a.relevance)
      .slice(0, maxKeywords);

    return keywords;
  }

  /**
   * Extract named entities from text
   * @param {string} text - Text to analyze
   * @returns {Object} Entities categorized by type
   */
  extractEntities(text) {
    const entities = {
      persons: [],
      organizations: [],
      locations: []
    };

    // Simple pattern matching for capitalized words
    const sentences = text.split(/[.!?]+/);
    
    sentences.forEach(sentence => {
      const words = sentence.trim().split(/\s+/);
      
      words.forEach((word, index) => {
        // Check if word starts with capital letter (not at sentence start)
        if (index > 0 && /^[A-Z][a-z]+$/.test(word) && word.length > 3) {
          // Simple heuristic: if followed by another capitalized word, likely a named entity
          if (index < words.length - 1 && /^[A-Z]/.test(words[index + 1])) {
            const entity = `${word} ${words[index + 1]}`;
            if (!entities.organizations.includes(entity)) {
              entities.organizations.push(entity);
            }
          }
        }
      });
    });

    return entities;
  }

  /**
   * Calculate relevance score for a keyword in a document
   * @param {string} keyword - Keyword to score
   * @param {string} document - Document text
   * @returns {number} Relevance score (0-1)
   */
  calculateRelevance(keyword, document) {
    const lowerKeyword = keyword.toLowerCase();
    const lowerDoc = document.toLowerCase();
    
    const occurrences = (lowerDoc.match(new RegExp(lowerKeyword, 'g')) || []).length;
    const words = document.split(/\s+/).length;
    
    if (words === 0) return 0;
    
    // Simple relevance: occurrences per 100 words
    return Math.min(occurrences / (words / 100), 1.0);
  }

  /**
   * Perform sentiment analysis (basic)
   * @param {string} text - Text to analyze
   * @returns {Object} Sentiment scores
   */
  analyzeSentiment(text) {
    const Analyzer = natural.SentimentAnalyzer;
    const stemmer = natural.PorterStemmer;
    const analyzer = new Analyzer('English', stemmer, 'afinn');
    
    const tokens = tokenizer.tokenize(text);
    const score = analyzer.getSentiment(tokens);
    
    return {
      score,
      polarity: score > 0 ? 'positive' : score < 0 ? 'negative' : 'neutral'
    };
  }

  /**
   * Extract topic clusters from multiple documents
   * @param {Array<string>} documents - Array of document texts
   * @param {number} numTopics - Number of topics to extract
   * @returns {Array} Topic clusters
   */
  extractTopics(documents, numTopics = 5) {
    // Create TF-IDF model
    const tfidf = new TfIdf();
    
    documents.forEach(doc => {
      tfidf.addDocument(doc);
    });

    // Get top terms for each document
    const topics = [];
    
    for (let i = 0; i < Math.min(numTopics, documents.length); i++) {
      const terms = [];
      tfidf.listTerms(i).slice(0, 5).forEach(item => {
        terms.push({ term: item.term, score: item.tfidf });
      });
      topics.push(terms);
    }

    return topics;
  }
}

module.exports = AnalysisService;
