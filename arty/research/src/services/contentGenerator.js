/**
 * Content Generator
 * Generates posts from research insights
 */

class ContentGenerator {
  constructor() {
    this.templates = {
      linkedin: {
        educational: (topic, keywords) => 
          `🔍 Deep Dive: ${topic}\n\nKey insights:\n${keywords.slice(0, 3).map(k => `• ${k.keyword}`).join('\n')}\n\n#AI #Research #${topic.replace(/\s+/g, '')}`,
        
        insight: (topic, insight) =>
          `💡 Today's Research Insight\n\n${insight}\n\n${topic}\n\n#MachineLearning #Innovation`,
        
        trend: (topic, keywords) =>
          `📈 Trending in ${topic}\n\nEmerging topics:\n${keywords.slice(0, 4).map(k => `→ ${k.keyword}`).join('\n')}\n\n#TechTrends #AI`
      },
      
      discord: {
        question: (topic) => 
          `What are your thoughts on recent developments in ${topic}? 🤔`,
        
        discussion: (keywords) =>
          `Interesting topics for discussion:\n${keywords.slice(0, 3).map(k => `• ${k.keyword}`).join('\n')}\n\nWhich one interests you most?`,
        
        fact: (insight) =>
          `💡 Research finding:\n${insight}\n\nWhat's your take on this?`
      }
    };
  }

  /**
   * Generate content for platform
   * @param {Object} insights - Research insights
   * @param {string} platform - Target platform
   * @param {number} count - Number of posts to generate
   * @returns {Array} Generated posts
   */
  async generate(insights, platform, count) {
    const posts = [];
    const { keywords, broadField, targetedField } = insights;
    
    const topic = targetedField || broadField;
    const templateTypes = Object.keys(this.templates[platform] || {});
    
    for (let i = 0; i < count; i++) {
      const templateType = templateTypes[i % templateTypes.length];
      const template = this.templates[platform][templateType];
      
      let content;
      if (templateType === 'educational' || templateType === 'trend') {
        content = template(topic, keywords);
      } else if (templateType === 'question') {
        content = template(topic);
      } else if (templateType === 'discussion') {
        content = template(keywords);
      } else {
        // Generate a generic insight
        const randomKeyword = keywords[Math.floor(Math.random() * Math.min(5, keywords.length))];
        content = template(`Recent research in ${topic} highlights the importance of ${randomKeyword.keyword}`);
      }
      
      posts.push({
        content,
        metadata: {
          type: templateType,
          topic,
          keywords: keywords.slice(0, 5).map(k => k.keyword),
          generated_at: new Date().toISOString()
        }
      });
    }
    
    return posts;
  }

  /**
   * Generate topic for engagement
   * @param {Array} keywords - Keywords to base topic on
   * @returns {string} Topic text
   */
  generateTopic(keywords) {
    if (!keywords || keywords.length === 0) {
      return 'What are you researching today?';
    }
    
    const topKeyword = keywords[0].keyword;
    const templates = [
      `Let's discuss: ${topKeyword} 💭`,
      `Anyone working with ${topKeyword}? Share your experience!`,
      `${topKeyword} - what's the latest in this area?`,
      `Deep dive into ${topKeyword} - thoughts?`
    ];
    
    return templates[Math.floor(Math.random() * templates.length)];
  }
}

module.exports = ContentGenerator;
