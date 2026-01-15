import React, { useState, useEffect, useCallback } from 'react';

const AgentPerformanceScoreboard = () => {
  const [activeView, setActiveView] = useState('scoreboard');
  const [agents, setAgents] = useState([]);
  const [performanceHistory, setPerformanceHistory] = useState([]);
  const [rankings, setRankings] = useState([]);
  const [metrics, setMetrics] = useState([]);
  const [benchmarks, setBenchmarks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [selectedMetric, setSelectedMetric] = useState('overall');
  const [timeRange, setTimeRange] = useState('24h');
  const [performanceModal, setPerformanceModal] = useState(false);
  const [comparisonMode, setComparisonMode] = useState(false);
  const [selectedAgents, setSelectedAgents] = useState([]);
  const [filters, setFilters] = useState({
    department: 'all',
    type: 'all',
    status: 'all',
    performance: 'all'
  });
  const [sortBy, setSortBy] = useState('score');
  const [sortOrder, setSortOrder] = useState('desc');

  // Generate agent performance data
  const generateAgents = useCallback(() => {
    const agentTypes = ['analytics', 'automation', 'communication', 'research', 'optimization', 'monitoring'];
    const departments = ['marketing', 'sales', 'finance', 'operations', 'research', 'strategy'];
    const statuses = ['active', 'idle', 'busy', 'maintenance'];
    
    const agentNames = [
      'Analytics Agent Alpha', 'Research Agent Beta', 'Marketing Agent Gamma', 'Finance Agent Delta',
      'Operations Agent Epsilon', 'Strategy Agent Zeta', 'Customer Agent Eta', 'Data Agent Theta',
      'Communication Agent Iota', 'Automation Agent Kappa', 'Optimization Agent Lambda', 'Monitoring Agent Mu',
      'Business Agent Nu', 'Intelligence Agent Xi', 'Processing Agent Omicron', 'Coordination Agent Pi',
      'Integration Agent Rho', 'Analysis Agent Sigma', 'Workflow Agent Tau', 'Decision Agent Upsilon'
    ];

    return Array.from({ length: 20 }, (_, index) => {
      const baseScore = Math.random() * 40 + 60; // 60-100 base score
      const efficiency = Math.random() * 30 + 70;
      const reliability = Math.random() * 25 + 75;
      const speed = Math.random() * 35 + 65;
      const accuracy = Math.random() * 20 + 80;
      const availability = Math.random() * 15 + 85;
      
      return {
        id: `agent-${index + 1}`,
        name: agentNames[index] || `Agent ${index + 1}`,
        type: agentTypes[Math.floor(Math.random() * agentTypes.length)],
        department: departments[Math.floor(Math.random() * departments.length)],
        status: statuses[Math.floor(Math.random() * statuses.length)],
        rank: index + 1, // Will be recalculated
        previousRank: index + Math.floor(Math.random() * 5) - 2,
        overallScore: baseScore,
        performanceMetrics: {
          efficiency: efficiency,
          reliability: reliability,
          speed: speed,
          accuracy: accuracy,
          availability: availability,
          throughput: Math.random() * 1000 + 500,
          errorRate: Math.random() * 5,
          responseTime: Math.random() * 500 + 100,
          resourceUtilization: Math.random() * 40 + 60,
          taskCompletion: Math.random() * 25 + 75,
          qualityScore: Math.random() * 20 + 80,
          collaborationScore: Math.random() * 30 + 70,
          innovationScore: Math.random() * 25 + 75,
          adaptabilityScore: Math.random() * 35 + 65,
          leadershipScore: Math.random() * 30 + 70
        },
        kpis: {
          tasksCompleted: Math.floor(Math.random() * 500) + 100,
          tasksSuccess: Math.floor(Math.random() * 450) + 150,
          averageTaskTime: (Math.random() * 300 + 120).toFixed(0) + 's',
          uptime: Math.random() * 20 + 80,
          customerSatisfaction: Math.random() * 25 + 75,
          costEfficiency: Math.random() * 30 + 70,
          learningRate: Math.random() * 40 + 60,
          problemSolving: Math.random() * 25 + 75
        },
        trends: {
          scoreChange: (Math.random() * 20 - 10).toFixed(1),
          efficiencyTrend: (Math.random() * 15 - 7.5).toFixed(1),
          reliabilityTrend: (Math.random() * 10 - 5).toFixed(1),
          speedTrend: (Math.random() * 12 - 6).toFixed(1),
          accuracyTrend: (Math.random() * 8 - 4).toFixed(1)
        },
        achievements: [
          'Top Performer',
          'Efficiency Champion',
          'Reliability Expert',
          'Speed Master',
          'Accuracy Leader',
          'Innovation Award',
          'Team Player',
          'Problem Solver'
        ].slice(0, Math.floor(Math.random() * 5) + 2),
        lastActive: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString(),
        deployedSince: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString(),
        version: `v${Math.floor(Math.random() * 5) + 1}.${Math.floor(Math.random() * 10)}.${Math.floor(Math.random() * 10)}`,
        specializations: [
          'Machine Learning',
          'Data Processing',
          'Natural Language',
          'Real-time Analytics',
          'Workflow Automation',
          'API Integration'
        ].slice(0, Math.floor(Math.random() * 4) + 2),
        certifications: Math.floor(Math.random() * 8) + 2,
        trainingHours: Math.floor(Math.random() * 500) + 100,
        mentorshipScore: Math.random() * 30 + 70,
        feedbackScore: Math.random() * 25 + 75,
        goals: {
          current: Math.floor(Math.random() * 10) + 5,
          completed: Math.floor(Math.random() * 8) + 3,
          overdue: Math.floor(Math.random() * 3),
          upcoming: Math.floor(Math.random() * 5) + 2
        }
      };
    });
  }, []);

  const generatePerformanceHistory = useCallback(() => {
    return Array.from({ length: 30 }, (_, dayIndex) => {
      const date = new Date(Date.now() - (29 - dayIndex) * 24 * 60 * 60 * 1000);
      
      return {
        date: date.toISOString(),
        timestamp: date.getTime(),
        metrics: {
          averageScore: Math.random() * 20 + 75,
          totalTasks: Math.floor(Math.random() * 1000) + 500,
          completedTasks: Math.floor(Math.random() * 950) + 450,
          avgResponseTime: Math.random() * 200 + 150,
          avgEfficiency: Math.random() * 25 + 70,
          avgReliability: Math.random() * 20 + 75,
          avgAccuracy: Math.random() * 15 + 82,
          systemUptime: Math.random() * 15 + 85,
          resourceUsage: Math.random() * 30 + 60
        },
        agentMetrics: Array.from({ length: 20 }, (_, agentIndex) => ({
          agentId: `agent-${agentIndex + 1}`,
          score: Math.random() * 30 + 65,
          efficiency: Math.random() * 25 + 70,
          reliability: Math.random() * 20 + 75,
          accuracy: Math.random() * 15 + 80,
          tasks: Math.floor(Math.random() * 50) + 20
        }))
      };
    });
  }, []);

  const generateRankings = useCallback(() => {
    const categories = [
      'Overall Performance',
      'Efficiency',
      'Reliability',
      'Speed',
      'Accuracy',
      'Innovation',
      'Collaboration',
      'Problem Solving'
    ];

    return categories.map(category => ({
      category,
      rankings: Array.from({ length: 20 }, (_, index) => ({
        rank: index + 1,
        agentId: `agent-${Math.floor(Math.random() * 20) + 1}`,
        score: Math.random() * 30 + 70,
        change: Math.floor(Math.random() * 10) - 5,
        trend: ['up', 'down', 'stable'][Math.floor(Math.random() * 3)]
      })).sort((a, b) => b.score - a.score).map((item, index) => ({
        ...item,
        rank: index + 1
      }))
    }));
  }, []);

  const generateMetrics = useCallback(() => {
    const metricCategories = [
      'Performance',
      'Efficiency',
      'Quality',
      'Reliability',
      'Innovation',
      'Collaboration'
    ];

    return metricCategories.map(category => ({
      category,
      metrics: [
        {
          name: 'Task Completion Rate',
          value: Math.random() * 15 + 85,
          target: 90,
          unit: '%',
          trend: (Math.random() * 10 - 5).toFixed(1),
          status: 'good'
        },
        {
          name: 'Average Response Time',
          value: Math.random() * 200 + 150,
          target: 200,
          unit: 'ms',
          trend: (Math.random() * 50 - 25).toFixed(1),
          status: 'warning'
        },
        {
          name: 'Error Rate',
          value: Math.random() * 3 + 1,
          target: 2,
          unit: '%',
          trend: (Math.random() * 2 - 1).toFixed(2),
          status: 'critical'
        },
        {
          name: 'Resource Utilization',
          value: Math.random() * 30 + 65,
          target: 80,
          unit: '%',
          trend: (Math.random() * 8 - 4).toFixed(1),
          status: 'good'
        }
      ].slice(0, Math.floor(Math.random() * 3) + 2)
    }));
  }, []);

  const generateBenchmarks = useCallback(() => {
    return [
      {
        name: 'Industry Standard',
        description: 'Performance benchmark based on industry averages',
        metrics: {
          overallScore: 78,
          efficiency: 75,
          reliability: 82,
          speed: 73,
          accuracy: 85,
          availability: 88
        }
      },
      {
        name: 'Enterprise Target',
        description: 'Target performance levels for enterprise operations',
        metrics: {
          overallScore: 85,
          efficiency: 82,
          reliability: 88,
          speed: 80,
          accuracy: 90,
          availability: 95
        }
      },
      {
        name: 'Best in Class',
        description: 'Top-tier performance benchmark',
        metrics: {
          overallScore: 92,
          efficiency: 90,
          reliability: 94,
          speed: 88,
          accuracy: 95,
          availability: 98
        }
      }
    ];
  }, []);

  // Load data
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        await new Promise(resolve => setTimeout(resolve, 1200));
        
        const agentData = generateAgents();
        // Sort agents by overall score for ranking
        const sortedAgents = agentData.sort((a, b) => b.overallScore - a.overallScore);
        sortedAgents.forEach((agent, index) => {
          agent.rank = index + 1;
        });
        
        setAgents(sortedAgents);
        setPerformanceHistory(generatePerformanceHistory());
        setRankings(generateRankings());
        setMetrics(generateMetrics());
        setBenchmarks(generateBenchmarks());
        
      } catch (error) {
        console.error('Error loading performance data:', error);
        setError('Failed to load performance scoreboard data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [generateAgents, generatePerformanceHistory, generateRankings, generateMetrics, generateBenchmarks]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const agentData = generateAgents();
    const sortedAgents = agentData.sort((a, b) => b.overallScore - a.overallScore);
    sortedAgents.forEach((agent, index) => {
      agent.rank = index + 1;
    });
    
    setAgents(sortedAgents);
    setPerformanceHistory(generatePerformanceHistory());
    setRankings(generateRankings());
    setMetrics(generateMetrics());
    setBenchmarks(generateBenchmarks());
    
    setRefreshing(false);
  };

  // Filter and sort logic
  const filteredAgents = agents.filter(agent => {
    const matchesFilters = 
      (filters.department === 'all' || agent.department === filters.department) &&
      (filters.type === 'all' || agent.type === filters.type) &&
      (filters.status === 'all' || agent.status === filters.status) &&
      (filters.performance === 'all' || 
        (filters.performance === 'excellent' && agent.overallScore >= 90) ||
        (filters.performance === 'good' && agent.overallScore >= 80 && agent.overallScore < 90) ||
        (filters.performance === 'average' && agent.overallScore >= 70 && agent.overallScore < 80) ||
        (filters.performance === 'poor' && agent.overallScore < 70));
    
    return matchesFilters;
  });

  const sortData = (data) => {
    return data.sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'score':
          aValue = a.overallScore;
          bValue = b.overallScore;
          break;
        case 'rank':
          aValue = a.rank;
          bValue = b.rank;
          break;
        case 'efficiency':
          aValue = a.performanceMetrics.efficiency;
          bValue = b.performanceMetrics.efficiency;
          break;
        case 'reliability':
          aValue = a.performanceMetrics.reliability;
          bValue = b.performanceMetrics.reliability;
          break;
        case 'name':
          aValue = a.name;
          bValue = b.name;
          break;
        default:
          aValue = a.overallScore;
          bValue = b.overallScore;
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
  };

  const sortedAgents = sortData([...filteredAgents]);

  const getScoreColor = (score) => {
    if (score >= 90) return '#28a745';
    if (score >= 80) return '#17a2b8';
    if (score >= 70) return '#ffc107';
    if (score >= 60) return '#fd7e14';
    return '#dc3545';
  };

  const getScoreGrade = (score) => {
    if (score >= 95) return 'A+';
    if (score >= 90) return 'A';
    if (score >= 85) return 'A-';
    if (score >= 80) return 'B+';
    if (score >= 75) return 'B';
    if (score >= 70) return 'B-';
    if (score >= 65) return 'C+';
    if (score >= 60) return 'C';
    return 'C-';
  };

  const getTrendIcon = (trend) => {
    const value = parseFloat(trend);
    if (value > 2) return { icon: 'fas fa-arrow-up', color: '#28a745' };
    if (value < -2) return { icon: 'fas fa-arrow-down', color: '#dc3545' };
    return { icon: 'fas fa-minus', color: '#6c757d' };
  };

  const renderScoreboardView = () => (
    <div className="scoreboard-content">
      <div className="scoreboard-controls">
        <div className="filter-section">
          <select value={filters.department} onChange={(e) => setFilters({...filters, department: e.target.value})}>
            <option value="all">All Departments</option>
            <option value="marketing">Marketing</option>
            <option value="sales">Sales</option>
            <option value="finance">Finance</option>
            <option value="operations">Operations</option>
            <option value="research">Research</option>
            <option value="strategy">Strategy</option>
          </select>
          <select value={filters.type} onChange={(e) => setFilters({...filters, type: e.target.value})}>
            <option value="all">All Types</option>
            <option value="analytics">Analytics</option>
            <option value="automation">Automation</option>
            <option value="communication">Communication</option>
            <option value="research">Research</option>
            <option value="optimization">Optimization</option>
            <option value="monitoring">Monitoring</option>
          </select>
          <select value={filters.performance} onChange={(e) => setFilters({...filters, performance: e.target.value})}>
            <option value="all">All Performance</option>
            <option value="excellent">Excellent (90+)</option>
            <option value="good">Good (80-89)</option>
            <option value="average">Average (70-79)</option>
            <option value="poor">Poor (&lt;70)</option>
          </select>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="score">Sort by Score</option>
            <option value="rank">Sort by Rank</option>
            <option value="efficiency">Sort by Efficiency</option>
            <option value="reliability">Sort by Reliability</option>
            <option value="name">Sort by Name</option>
          </select>
        </div>
      </div>

      <div className="performance-overview">
        <div className="overview-stats">
          <div className="stat-card">
            <div className="stat-icon">
              <i className="fas fa-trophy"></i>
            </div>
            <div className="stat-content">
              <h3>{agents.filter(a => a.overallScore >= 90).length}</h3>
              <p>Top Performers</p>
              <span className="stat-detail">Score ≥ 90</span>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">
              <i className="fas fa-chart-line"></i>
            </div>
            <div className="stat-content">
              <h3>{(agents.reduce((sum, a) => sum + a.overallScore, 0) / agents.length || 0).toFixed(1)}</h3>
              <p>Average Score</p>
              <span className="stat-detail">All agents</span>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">
              <i className="fas fa-arrow-up"></i>
            </div>
            <div className="stat-content">
              <h3>{agents.filter(a => parseFloat(a.trends.scoreChange) > 0).length}</h3>
              <p>Improving</p>
              <span className="stat-detail">Positive trend</span>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">
              <i className="fas fa-medal"></i>
            </div>
            <div className="stat-content">
              <h3>{benchmarks[1].metrics.overallScore}</h3>
              <p>Target Score</p>
              <span className="stat-detail">Enterprise goal</span>
            </div>
          </div>
        </div>
      </div>

      <div className="scoreboard-leaderboard">
        <div className="leaderboard-header">
          <h3>Performance Leaderboard</h3>
          <div className="leaderboard-controls">
            <button 
              className={`compare-btn ${comparisonMode ? 'active' : ''}`}
              onClick={() => setComparisonMode(!comparisonMode)}
            >
              <i className="fas fa-balance-scale"></i>
              {comparisonMode ? 'Exit Compare' : 'Compare Mode'}
            </button>
          </div>
        </div>

        <div className="leaderboard-table">
          <div className="table-header">
            <div className="header-cell rank">Rank</div>
            <div className="header-cell agent">Agent</div>
            <div className="header-cell score">Score</div>
            <div className="header-cell grade">Grade</div>
            <div className="header-cell efficiency">Efficiency</div>
            <div className="header-cell reliability">Reliability</div>
            <div className="header-cell trend">Trend</div>
            <div className="header-cell actions">Actions</div>
          </div>
          <div className="table-body">
            {sortedAgents.map(agent => {
              const trendInfo = getTrendIcon(agent.trends.scoreChange);
              const rankChange = agent.rank - (agent.previousRank || agent.rank);
              
              return (
                <div 
                  key={agent.id} 
                  className={`table-row ${comparisonMode && selectedAgents.includes(agent.id) ? 'selected' : ''}`}
                  onClick={() => {
                    if (comparisonMode) {
                      if (selectedAgents.includes(agent.id)) {
                        setSelectedAgents(selectedAgents.filter(id => id !== agent.id));
                      } else if (selectedAgents.length < 3) {
                        setSelectedAgents([...selectedAgents, agent.id]);
                      }
                    }
                  }}
                >
                  <div className="table-cell rank">
                    <div className="rank-info">
                      <span className="rank-number">{agent.rank}</span>
                      {rankChange !== 0 && (
                        <span className={`rank-change ${rankChange > 0 ? 'up' : 'down'}`}>
                          <i className={`fas fa-arrow-${rankChange > 0 ? 'up' : 'down'}`}></i>
                          {Math.abs(rankChange)}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="table-cell agent">
                    <div className="agent-info">
                      <div className="agent-details">
                        <span className="agent-name">{agent.name}</span>
                        <span className="agent-meta">{agent.type} • {agent.department}</span>
                      </div>
                      <div className="agent-status">
                        <span className={`status-dot ${agent.status}`}></span>
                      </div>
                    </div>
                  </div>
                  <div className="table-cell score">
                    <div className="score-display">
                      <span 
                        className="score-value"
                        style={{ color: getScoreColor(agent.overallScore) }}
                      >
                        {agent.overallScore.toFixed(1)}
                      </span>
                      <div className="score-bar">
                        <div 
                          className="score-fill"
                          style={{ 
                            width: `${agent.overallScore}%`,
                            backgroundColor: getScoreColor(agent.overallScore)
                          }}
                        ></div>
                      </div>
                    </div>
                  </div>
                  <div className="table-cell grade">
                    <span 
                      className="grade-badge"
                      style={{ backgroundColor: getScoreColor(agent.overallScore) }}
                    >
                      {getScoreGrade(agent.overallScore)}
                    </span>
                  </div>
                  <div className="table-cell efficiency">
                    <span className="metric-value">{agent.performanceMetrics.efficiency.toFixed(1)}%</span>
                  </div>
                  <div className="table-cell reliability">
                    <span className="metric-value">{agent.performanceMetrics.reliability.toFixed(1)}%</span>
                  </div>
                  <div className="table-cell trend">
                    <div className="trend-info">
                      <i className={trendInfo.icon} style={{ color: trendInfo.color }}></i>
                      <span style={{ color: trendInfo.color }}>{agent.trends.scoreChange}%</span>
                    </div>
                  </div>
                  <div className="table-cell actions">
                    <button 
                      className="action-btn view"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedAgent(agent);
                        setPerformanceModal(true);
                      }}
                    >
                      <i className="fas fa-eye"></i>
                    </button>
                    {comparisonMode && (
                      <div className="comparison-checkbox">
                        <input 
                          type="checkbox"
                          checked={selectedAgents.includes(agent.id)}
                          onChange={() => {}}
                        />
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );

  const renderMetricsView = () => (
    <div className="metrics-content">
      <div className="metrics-overview">
        <h3>Performance Metrics Overview</h3>
        <div className="metrics-grid">
          {metrics.map(metricCategory => (
            <div key={metricCategory.category} className="metric-category">
              <h4>{metricCategory.category}</h4>
              <div className="category-metrics">
                {metricCategory.metrics.map(metric => (
                  <div key={metric.name} className="metric-item">
                    <div className="metric-header">
                      <span className="metric-name">{metric.name}</span>
                      <span className={`metric-status ${metric.status}`}></span>
                    </div>
                    <div className="metric-values">
                      <span className="current-value">
                        {metric.value.toFixed(1)} {metric.unit}
                      </span>
                      <span className="target-value">
                        Target: {metric.target} {metric.unit}
                      </span>
                    </div>
                    <div className="metric-progress">
                      <div className="progress-bar">
                        <div 
                          className="progress-fill"
                          style={{ 
                            width: `${(metric.value / metric.target) * 100}%`,
                            backgroundColor: metric.status === 'good' ? '#28a745' : 
                                           metric.status === 'warning' ? '#ffc107' : '#dc3545'
                          }}
                        ></div>
                      </div>
                    </div>
                    <div className="metric-trend">
                      <span className={`trend ${parseFloat(metric.trend) > 0 ? 'positive' : 'negative'}`}>
                        <i className={`fas fa-arrow-${parseFloat(metric.trend) > 0 ? 'up' : 'down'}`}></i>
                        {Math.abs(parseFloat(metric.trend))}% vs last period
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderBenchmarksView = () => (
    <div className="benchmarks-content">
      <div className="benchmarks-overview">
        <h3>Performance Benchmarks</h3>
        <p>Compare agent performance against industry standards and targets</p>
      </div>

      <div className="benchmark-comparison">
        {benchmarks.map(benchmark => (
          <div key={benchmark.name} className="benchmark-card">
            <div className="benchmark-header">
              <h4>{benchmark.name}</h4>
              <p>{benchmark.description}</p>
            </div>
            <div className="benchmark-metrics">
              {Object.entries(benchmark.metrics).map(([key, value]) => {
                const currentAvg = agents.length > 0 ? 
                  (key === 'overallScore' ? 
                    agents.reduce((sum, a) => sum + a.overallScore, 0) / agents.length :
                    agents.reduce((sum, a) => sum + (a.performanceMetrics[key] || 0), 0) / agents.length
                  ) : 0;
                
                const difference = currentAvg - value;
                const percentage = (currentAvg / value) * 100;
                
                return (
                  <div key={key} className="benchmark-metric">
                    <div className="metric-info">
                      <span className="metric-label">{key.charAt(0).toUpperCase() + key.slice(1)}</span>
                      <div className="metric-comparison">
                        <span className="benchmark-value">{value}</span>
                        <span className="current-value">{currentAvg.toFixed(1)}</span>
                        <span className={`difference ${difference >= 0 ? 'positive' : 'negative'}`}>
                          {difference >= 0 ? '+' : ''}{difference.toFixed(1)}
                        </span>
                      </div>
                    </div>
                    <div className="comparison-bar">
                      <div 
                        className="comparison-fill"
                        style={{ 
                          width: `${Math.min(percentage, 100)}%`,
                          backgroundColor: percentage >= 100 ? '#28a745' : 
                                         percentage >= 80 ? '#ffc107' : '#dc3545'
                        }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeView) {
      case 'scoreboard':
        return renderScoreboardView();
      case 'metrics':
        return renderMetricsView();
      case 'benchmarks':
        return renderBenchmarksView();
      default:
        return renderScoreboardView();
    }
  };

  if (loading) {
    return (
      <div className="agent-performance-scoreboard loading">
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading performance scoreboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="agent-performance-scoreboard error">
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          <p>{error}</p>
          <button onClick={handleRefresh}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="agent-performance-scoreboard">
      <div className="scoreboard-header">
        <div className="header-left">
          <h2>Agent Performance Scoreboard</h2>
          <p>Track and analyze agent performance metrics and rankings</p>
        </div>
        <div className="header-right">
          <button 
            className={`refresh-btn ${refreshing ? 'refreshing' : ''}`}
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <i className="fas fa-sync-alt"></i>
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      <div className="scoreboard-navigation">
        <div className="nav-buttons">
          <button 
            className={`nav-button ${activeView === 'scoreboard' ? 'active' : ''}`}
            onClick={() => setActiveView('scoreboard')}
          >
            <i className="fas fa-trophy"></i>
            Scoreboard
          </button>
          <button 
            className={`nav-button ${activeView === 'metrics' ? 'active' : ''}`}
            onClick={() => setActiveView('metrics')}
          >
            <i className="fas fa-chart-bar"></i>
            Metrics
          </button>
          <button 
            className={`nav-button ${activeView === 'benchmarks' ? 'active' : ''}`}
            onClick={() => setActiveView('benchmarks')}
          >
            <i className="fas fa-bullseye"></i>
            Benchmarks
          </button>
        </div>
      </div>

      <div className="scoreboard-main">
        {renderContent()}
      </div>

      {/* Performance Detail Modal */}
      {performanceModal && selectedAgent && (
        <div className="modal-overlay" onClick={() => setPerformanceModal(false)}>
          <div className="performance-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Performance Details: {selectedAgent.name}</h3>
              <button className="close-button" onClick={() => setPerformanceModal(false)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-content">
              <div className="performance-details">
                <div className="detail-section">
                  <h4>Overall Performance</h4>
                  <div className="performance-summary">
                    <div className="score-display large">
                      <span 
                        className="score-value"
                        style={{ color: getScoreColor(selectedAgent.overallScore) }}
                      >
                        {selectedAgent.overallScore.toFixed(1)}
                      </span>
                      <span 
                        className="score-grade"
                        style={{ backgroundColor: getScoreColor(selectedAgent.overallScore) }}
                      >
                        {getScoreGrade(selectedAgent.overallScore)}
                      </span>
                    </div>
                    <div className="rank-info">
                      <span className="rank-label">Current Rank:</span>
                      <span className="rank-value">#{selectedAgent.rank}</span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Performance Metrics</h4>
                  <div className="metrics-grid">
                    {Object.entries(selectedAgent.performanceMetrics).map(([key, value]) => (
                      <div key={key} className="metric-card">
                        <span className="metric-label">{key.charAt(0).toUpperCase() + key.slice(1)}:</span>
                        <span className="metric-value">{value.toFixed(1)}{typeof value === 'number' && value <= 100 ? '%' : ''}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Key Performance Indicators</h4>
                  <div className="kpi-grid">
                    {Object.entries(selectedAgent.kpis).map(([key, value]) => (
                      <div key={key} className="kpi-item">
                        <span className="kpi-label">{key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}:</span>
                        <span className="kpi-value">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Achievements</h4>
                  <div className="achievements-list">
                    {selectedAgent.achievements.map(achievement => (
                      <div key={achievement} className="achievement-badge">
                        <i className="fas fa-award"></i>
                        {achievement}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentPerformanceScoreboard;
