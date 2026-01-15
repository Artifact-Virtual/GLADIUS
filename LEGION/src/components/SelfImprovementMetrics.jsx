// components/SelfImprovementMetrics.jsx

import React, { useState, useEffect } from 'react';

const SelfImprovementMetrics = () => {
  const [metricsData, setMetricsData] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [timeFrame, setTimeFrame] = useState('7d');

  // Generate comprehensive self-improvement metrics
  const generateMetricsData = (category, timeframe) => {
    const data = {
      timestamp: new Date().toISOString(),
      timeframe: timeframe,
      overall_score: Math.floor(Math.random() * 15) + 80,
      improvement_rate: (Math.random() * 3 + 2).toFixed(1),
      categories: {
        automation: {
          name: 'Process Automation',
          score: Math.floor(Math.random() * 20) + 75,
          trend: 'improving',
          metrics: {
            automated_tasks: Math.floor(Math.random() * 50) + 120,
            automation_rate: Math.floor(Math.random() * 15) + 78,
            time_saved_hours: Math.floor(Math.random() * 20) + 40,
            error_reduction: Math.floor(Math.random() * 10) + 25
          },
          improvements: [
            'Automated 15 new routine tasks this week',
            'Reduced manual intervention by 23%',
            'Implemented smart scheduling algorithms',
            'Enhanced error detection and auto-correction'
          ]
        },
        learning: {
          name: 'Machine Learning',
          score: Math.floor(Math.random() * 18) + 82,
          trend: 'improving',
          metrics: {
            model_accuracy: (Math.random() * 5 + 92).toFixed(1),
            learning_cycles: Math.floor(Math.random() * 10) + 25,
            data_processed_gb: Math.floor(Math.random() * 500) + 1200,
            adaptation_speed: (Math.random() * 0.5 + 2.1).toFixed(1)
          },
          improvements: [
            'Improved prediction accuracy by 8.5%',
            'Reduced false positives by 15%',
            'Enhanced pattern recognition algorithms',
            'Implemented continuous learning pipeline'
          ]
        },
        optimization: {
          name: 'System Optimization',
          score: Math.floor(Math.random() * 16) + 79,
          trend: 'stable',
          metrics: {
            performance_gain: Math.floor(Math.random() * 8) + 12,
            resource_efficiency: Math.floor(Math.random() * 12) + 83,
            latency_reduction: Math.floor(Math.random() * 20) + 35,
            throughput_increase: Math.floor(Math.random() * 15) + 28
          },
          improvements: [
            'Optimized database queries reducing load by 30%',
            'Implemented intelligent caching strategies',
            'Enhanced load balancing algorithms',
            'Reduced memory footprint by 18%'
          ]
        },
        adaptation: {
          name: 'Adaptive Intelligence',
          score: Math.floor(Math.random() * 22) + 73,
          trend: 'improving',
          metrics: {
            context_awareness: Math.floor(Math.random() * 10) + 87,
            decision_quality: Math.floor(Math.random() * 8) + 89,
            response_relevance: Math.floor(Math.random() * 6) + 91,
            learning_retention: Math.floor(Math.random() * 12) + 84
          },
          improvements: [
            'Enhanced contextual understanding by 12%',
            'Improved decision-making algorithms',
            'Better user behavior adaptation',
            'Increased response personalization'
          ]
        },
        security: {
          name: 'Security Enhancement',
          score: Math.floor(Math.random() * 14) + 85,
          trend: 'improving',
          metrics: {
            threat_detection: Math.floor(Math.random() * 8) + 94,
            vulnerability_patching: Math.floor(Math.random() * 5) + 96,
            security_score: Math.floor(Math.random() * 6) + 92,
            incident_response: (Math.random() * 0.8 + 1.2).toFixed(1)
          },
          improvements: [
            'Implemented AI-powered threat detection',
            'Automated security patch management',
            'Enhanced intrusion detection systems',
            'Improved incident response time by 45%'
          ]
        },
        efficiency: {
          name: 'Operational Efficiency',
          score: Math.floor(Math.random() * 17) + 81,
          trend: 'stable',
          metrics: {
            cost_reduction: Math.floor(Math.random() * 12) + 18,
            energy_efficiency: Math.floor(Math.random() * 8) + 87,
            process_speed: Math.floor(Math.random() * 20) + 125,
            resource_utilization: Math.floor(Math.random() * 10) + 88
          },
          improvements: [
            'Reduced operational costs by 22%',
            'Improved energy efficiency by 15%',
            'Streamlined workflow processes',
            'Enhanced resource allocation algorithms'
          ]
        }
      },
      achievements: [
        {
          title: 'Automation Milestone',
          description: 'Successfully automated 100+ routine tasks',
          date: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
          impact: 'high',
          category: 'automation'
        },
        {
          title: 'Learning Algorithm Breakthrough',
          description: 'Achieved 95%+ accuracy in predictive models',
          date: new Date(Date.now() - Math.random() * 14 * 24 * 60 * 60 * 1000).toISOString(),
          impact: 'high',
          category: 'learning'
        },
        {
          title: 'Performance Optimization',
          description: 'Reduced system response time by 40%',
          date: new Date(Date.now() - Math.random() * 5 * 24 * 60 * 60 * 1000).toISOString(),
          impact: 'medium',
          category: 'optimization'
        },
        {
          title: 'Security Enhancement',
          description: 'Implemented zero-day vulnerability protection',
          date: new Date(Date.now() - Math.random() * 3 * 24 * 60 * 60 * 1000).toISOString(),
          impact: 'high',
          category: 'security'
        }
      ],
      goals: {
        current: [
          {
            title: 'Achieve 95% Automation Rate',
            progress: Math.floor(Math.random() * 20) + 75,
            deadline: '2024-02-15',
            priority: 'high'
          },
          {
            title: 'Reduce Response Time by 50%',
            progress: Math.floor(Math.random() * 15) + 60,
            deadline: '2024-02-28',
            priority: 'medium'
          },
          {
            title: 'Implement Advanced ML Models',
            progress: Math.floor(Math.random() * 25) + 45,
            deadline: '2024-03-10',
            priority: 'high'
          }
        ],
        completed: Math.floor(Math.random() * 15) + 28,
        in_progress: Math.floor(Math.random() * 8) + 12,
        planned: Math.floor(Math.random() * 6) + 18
      }
    };

    return data;
  };

  useEffect(() => {
    const loadData = () => {
      setMetricsData(generateMetricsData(selectedCategory, timeFrame));
    };

    loadData();
    const interval = setInterval(loadData, 45000); // Update every 45 seconds

    return () => clearInterval(interval);
  }, [selectedCategory, timeFrame]);

  const getTrendColor = (trend) => {
    switch (trend) {
      case 'improving': return '#28a745';
      case 'declining': return '#dc3545';
      case 'stable': return '#ffc107';
      default: return '#6c757d';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 90) return '#28a745';
    if (score >= 80) return '#17a2b8';
    if (score >= 70) return '#ffc107';
    return '#dc3545';
  };

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'high': return '#dc3545';
      case 'medium': return '#ffc107';
      case 'low': return '#28a745';
      default: return '#6c757d';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#dc3545';
      case 'medium': return '#ffc107';
      case 'low': return '#28a745';
      default: return '#6c757d';
    }
  };

  const filteredCategories = selectedCategory === 'all' 
    ? Object.entries(metricsData?.categories || {})
    : Object.entries(metricsData?.categories || {}).filter(([key]) => key === selectedCategory);

  if (!metricsData) {
    return (
      <div className="self-improvement-metrics loading">
        <div className="loading-spinner">
          <i className="fas fa-brain"></i>
          <p>Loading self-improvement metrics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="self-improvement-metrics">
      <div className="metrics-header">
        <div className="header-left">
          <h2>
            <i className="fas fa-brain"></i>
            Self-Improvement Metrics
          </h2>
          <p>AI-driven system enhancement and learning analytics</p>
        </div>
        
        <div className="header-controls">
          <div className="timeframe-selector">
            {['24h', '7d', '30d'].map(period => (
              <button
                key={period}
                className={`time-btn ${timeFrame === period ? 'active' : ''}`}
                onClick={() => setTimeFrame(period)}
              >
                {period}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="metrics-content">
        <div className="overview-section">
          <div className="overall-score-card">
            <div className="score-display">
              <div className="score-circle" style={{ borderColor: getScoreColor(metricsData.overall_score) }}>
                <span className="score-value">{metricsData.overall_score}</span>
                <span className="score-label">Overall Score</span>
              </div>
              <div className="improvement-rate">
                <i className="fas fa-arrow-up"></i>
                <span>+{metricsData.improvement_rate}% improvement rate</span>
              </div>
            </div>
          </div>

          <div className="goals-summary-card">
            <h3>Goals Summary</h3>
            <div className="goals-stats">
              <div className="goal-stat">
                <span className="stat-number">{metricsData.goals.completed}</span>
                <span className="stat-label">Completed</span>
              </div>
              <div className="goal-stat">
                <span className="stat-number">{metricsData.goals.in_progress}</span>
                <span className="stat-label">In Progress</span>
              </div>
              <div className="goal-stat">
                <span className="stat-number">{metricsData.goals.planned}</span>
                <span className="stat-label">Planned</span>
              </div>
            </div>
          </div>
        </div>

        <div className="category-filter">
          <label>Category Filter:</label>
          <select 
            value={selectedCategory} 
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="category-select"
          >
            <option value="all">All Categories</option>
            {Object.entries(metricsData.categories).map(([key, category]) => (
              <option key={key} value={key}>{category.name}</option>
            ))}
          </select>
        </div>

        <div className="categories-grid">
          {filteredCategories.map(([key, category]) => (
            <div key={key} className="category-card">
              <div className="category-header">
                <h3>{category.name}</h3>
                <div className="category-score" style={{ color: getScoreColor(category.score) }}>
                  {category.score}
                </div>
              </div>
              
              <div className="trend-indicator" style={{ color: getTrendColor(category.trend) }}>
                <i className={`fas fa-arrow-${category.trend === 'improving' ? 'up' : category.trend === 'declining' ? 'down' : 'right'}`}></i>
                <span>{category.trend}</span>
              </div>

              <div className="category-metrics">
                {Object.entries(category.metrics).map(([metricKey, value]) => (
                  <div key={metricKey} className="metric-item">
                    <span className="metric-name">{metricKey.replace(/_/g, ' ')}</span>
                    <span className="metric-value">
                      {typeof value === 'string' ? value : value}
                      {metricKey.includes('rate') || metricKey.includes('efficiency') || metricKey.includes('accuracy') ? '%' : ''}
                    </span>
                  </div>
                ))}
              </div>

              <div className="improvements-section">
                <h4>Recent Improvements</h4>
                <div className="improvements-list">
                  {category.improvements.map((improvement, index) => (
                    <div key={index} className="improvement-item">
                      <i className="fas fa-check-circle"></i>
                      <span>{improvement}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="achievements-section">
          <h3>Recent Achievements</h3>
          <div className="achievements-grid">
            {metricsData.achievements.map((achievement, index) => (
              <div key={index} className="achievement-card">
                <div className="achievement-header">
                  <h4>{achievement.title}</h4>
                  <div 
                    className="impact-badge" 
                    style={{ backgroundColor: getImpactColor(achievement.impact) }}
                  >
                    {achievement.impact}
                  </div>
                </div>
                <p className="achievement-description">{achievement.description}</p>
                <div className="achievement-meta">
                  <span className="achievement-date">
                    {new Date(achievement.date).toLocaleDateString()}
                  </span>
                  <span className="achievement-category">
                    {metricsData.categories[achievement.category]?.name || achievement.category}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="current-goals-section">
          <h3>Current Goals</h3>
          <div className="goals-list">
            {metricsData.goals.current.map((goal, index) => (
              <div key={index} className="goal-card">
                <div className="goal-header">
                  <h4>{goal.title}</h4>
                  <div 
                    className="priority-badge"
                    style={{ backgroundColor: getPriorityColor(goal.priority) }}
                  >
                    {goal.priority}
                  </div>
                </div>
                
                <div className="goal-progress">
                  <div className="progress-info">
                    <span>Progress: {goal.progress}%</span>
                    <span>Deadline: {new Date(goal.deadline).toLocaleDateString()}</span>
                  </div>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ 
                        width: `${goal.progress}%`,
                        backgroundColor: getPriorityColor(goal.priority)
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SelfImprovementMetrics;
