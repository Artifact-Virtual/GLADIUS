import React, { useState, useEffect, useCallback } from 'react';

const WorkflowPerformanceAnalytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview'); // overview, performance, trends, insights
  const [timeRange, setTimeRange] = useState('7d'); // 1d, 7d, 30d, 90d
  const [selectedWorkflow, setSelectedWorkflow] = useState('all');
  const [filters, setFilters] = useState({
    status: 'all',
    category: 'all',
    priority: 'all'
  });

  const generateAnalyticsData = useCallback(() => {
    const workflows = [
      'Customer Onboarding', 'Data Processing', 'Report Generation',
      'Email Campaign', 'Quality Assurance', 'Security Audit',
      'Backup Process', 'Invoice Processing', 'System Monitoring',
      'Content Publishing', 'User Registration', 'Order Processing',
      'Inventory Update', 'Payment Processing', 'Notification System',
      'File Transfer', 'Database Sync', 'API Integration'
    ];

    const categories = ['business', 'technical', 'marketing', 'finance', 'operations'];
    const statuses = ['completed', 'failed', 'cancelled', 'timeout'];

    const generateExecutions = (days) => {
      const executions = [];
      for (let i = 0; i < days; i++) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        
        workflows.forEach(workflow => {
          const executionCount = Math.floor(Math.random() * 20) + 5;
          for (let j = 0; j < executionCount; j++) {
            executions.push({
              id: `exec-${i}-${workflow}-${j}`,
              workflow,
              date: date.toISOString().split('T')[0],
              timestamp: new Date(date.getTime() - Math.random() * 86400000).toISOString(),
              status: statuses[Math.floor(Math.random() * statuses.length)],
              duration: Math.floor(Math.random() * 3600) + 60, // 1-60 minutes in seconds
              category: categories[Math.floor(Math.random() * categories.length)],
              priority: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)],
              resourceUsage: {
                cpu: Math.floor(Math.random() * 100),
                memory: Math.floor(Math.random() * 100),
                network: Math.floor(Math.random() * 100)
              },
              errorCode: Math.random() > 0.8 ? `ERR_${Math.floor(Math.random() * 1000)}` : null,
              triggeredBy: ['schedule', 'manual', 'api', 'event'][Math.floor(Math.random() * 4)],
              steps: Math.floor(Math.random() * 10) + 3,
              stepsCompleted: function() {
                return this.status === 'completed' ? this.steps : Math.floor(Math.random() * this.steps);
              }()
            });
          }
        });
      }
      return executions;
    };

    const days = timeRange === '1d' ? 1 : timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 90;
    const executions = generateExecutions(days);

    // Calculate analytics
    const totalExecutions = executions.length;
    const completedExecutions = executions.filter(e => e.status === 'completed').length;
    const failedExecutions = executions.filter(e => e.status === 'failed').length;
    const successRate = ((completedExecutions / totalExecutions) * 100).toFixed(1);
    const averageDuration = (executions.reduce((sum, e) => sum + e.duration, 0) / totalExecutions / 60).toFixed(1);

    // Workflow performance metrics
    const workflowMetrics = workflows.map(workflow => {
      const workflowExecutions = executions.filter(e => e.workflow === workflow);
      const completed = workflowExecutions.filter(e => e.status === 'completed').length;
      const failed = workflowExecutions.filter(e => e.status === 'failed').length;
      const avgDuration = workflowExecutions.length > 0 
        ? (workflowExecutions.reduce((sum, e) => sum + e.duration, 0) / workflowExecutions.length / 60).toFixed(1)
        : 0;
      
      return {
        name: workflow,
        executions: workflowExecutions.length,
        completed,
        failed,
        successRate: workflowExecutions.length > 0 ? ((completed / workflowExecutions.length) * 100).toFixed(1) : 0,
        avgDuration: parseFloat(avgDuration),
        avgResourceUsage: workflowExecutions.length > 0 
          ? Math.round(workflowExecutions.reduce((sum, e) => sum + e.resourceUsage.cpu, 0) / workflowExecutions.length)
          : 0,
        category: categories[Math.floor(Math.random() * categories.length)],
        trend: Math.random() > 0.5 ? 'up' : 'down',
        trendPercentage: (Math.random() * 20 + 5).toFixed(1)
      };
    });

    // Daily trends
    const dailyTrends = Array.from({ length: days }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (days - 1 - i));
      const dayExecutions = executions.filter(e => e.date === date.toISOString().split('T')[0]);
      
      return {
        date: date.toISOString().split('T')[0],
        executions: dayExecutions.length,
        completed: dayExecutions.filter(e => e.status === 'completed').length,
        failed: dayExecutions.filter(e => e.status === 'failed').length,
        avgDuration: dayExecutions.length > 0 
          ? (dayExecutions.reduce((sum, e) => sum + e.duration, 0) / dayExecutions.length / 60).toFixed(1)
          : 0
      };
    });

    // Performance insights
    const insights = [
      {
        type: 'success',
        title: 'High Success Rate',
        description: `${successRate}% of workflows completed successfully in the last ${timeRange}`,
        impact: 'positive',
        recommendation: 'Continue current optimization strategies'
      },
      {
        type: 'warning',
        title: 'Resource Usage Spike',
        description: 'CPU usage increased by 15% compared to previous period',
        impact: 'neutral',
        recommendation: 'Monitor resource allocation and consider scaling'
      },
      {
        type: 'info',
        title: 'Peak Usage Hours',
        description: 'Most workflows execute between 9 AM - 11 AM',
        impact: 'neutral',
        recommendation: 'Consider load balancing during peak hours'
      },
      {
        type: 'error',
        title: 'Frequent Failures',
        description: 'API Integration workflow has 20% failure rate',
        impact: 'negative',
        recommendation: 'Review error handling and timeout configurations'
      },
      {
        type: 'success',
        title: 'Performance Improvement',
        description: 'Average execution time reduced by 12% this week',
        impact: 'positive',
        recommendation: 'Document and replicate optimization techniques'
      }
    ];

    // Resource utilization trends
    const resourceTrends = Array.from({ length: 24 }, (_, hour) => ({
      hour,
      cpu: Math.floor(Math.random() * 40) + 30 + (hour >= 9 && hour <= 17 ? 20 : 0),
      memory: Math.floor(Math.random() * 50) + 25 + (hour >= 9 && hour <= 17 ? 15 : 0),
      network: Math.floor(Math.random() * 60) + 20 + (hour >= 9 && hour <= 17 ? 10 : 0),
      activeWorkflows: Math.floor(Math.random() * 15) + 5 + (hour >= 9 && hour <= 17 ? 10 : 0)
    }));

    return {
      overview: {
        totalExecutions,
        completedExecutions,
        failedExecutions,
        successRate: parseFloat(successRate),
        averageDuration: parseFloat(averageDuration),
        activeWorkflows: workflows.length,
        totalProcessingTime: Math.round(executions.reduce((sum, e) => sum + e.duration, 0) / 3600), // hours
        errorRate: ((failedExecutions / totalExecutions) * 100).toFixed(1)
      },
      workflowMetrics: workflowMetrics.sort((a, b) => b.executions - a.executions),
      dailyTrends,
      insights,
      resourceTrends,
      categoryBreakdown: categories.map(category => ({
        category,
        executions: executions.filter(e => e.category === category).length,
        successRate: (() => {
          const categoryExecs = executions.filter(e => e.category === category);
          const completed = categoryExecs.filter(e => e.status === 'completed').length;
          return categoryExecs.length > 0 ? ((completed / categoryExecs.length) * 100).toFixed(1) : 0;
        })()
      })),
      statusDistribution: statuses.map(status => ({
        status,
        count: executions.filter(e => e.status === status).length,
        percentage: ((executions.filter(e => e.status === status).length / totalExecutions) * 100).toFixed(1)
      })),
      triggerAnalysis: ['schedule', 'manual', 'api', 'event'].map(trigger => ({
        trigger,
        count: executions.filter(e => e.triggeredBy === trigger).length,
        avgDuration: (() => {
          const triggerExecs = executions.filter(e => e.triggeredBy === trigger);
          return triggerExecs.length > 0 
            ? (triggerExecs.reduce((sum, e) => sum + e.duration, 0) / triggerExecs.length / 60).toFixed(1)
            : 0;
        })()
      })),
      recentExecutions: executions
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
        .slice(0, 20)
    };
  }, [timeRange]);

  useEffect(() => {
    const loadAnalytics = async () => {
      setLoading(true);
      try {
        await new Promise(resolve => setTimeout(resolve, 1000));
        const analyticsData = generateAnalyticsData();
        setAnalytics(analyticsData);
        setLoading(false);
      } catch (error) {
        setLoading(false);
        console.error('Error loading analytics:', error);
      }
    };

    loadAnalytics();
  }, [generateAnalyticsData]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#28a745';
      case 'failed': return '#dc3545';
      case 'cancelled': return '#ffc107';
      case 'timeout': return '#fd7e14';
      default: return '#6c757d';
    }
  };

  const getInsightIcon = (type) => {
    switch (type) {
      case 'success': return 'fas fa-check-circle';
      case 'warning': return 'fas fa-exclamation-triangle';
      case 'error': return 'fas fa-times-circle';
      case 'info': return 'fas fa-info-circle';
      default: return 'fas fa-circle';
    }
  };

  const getInsightColor = (impact) => {
    switch (impact) {
      case 'positive': return '#28a745';
      case 'negative': return '#dc3545';
      case 'neutral': return '#ffc107';
      default: return '#6c757d';
    }
  };

  const filteredWorkflowMetrics = analytics?.workflowMetrics.filter(workflow => {
    const matchesWorkflow = selectedWorkflow === 'all' || workflow.name === selectedWorkflow;
    const matchesStatus = filters.status === 'all' || 
      (filters.status === 'high-success' && workflow.successRate >= 90) ||
      (filters.status === 'low-success' && workflow.successRate < 90);
    const matchesCategory = filters.category === 'all' || workflow.category === filters.category;
    
    return matchesWorkflow && matchesStatus && matchesCategory;
  }) || [];

  const renderOverviewTab = () => (
    <div className="overview-tab">
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">
            <i className="fas fa-play-circle"></i>
          </div>
          <div className="metric-content">
            <div className="metric-value">{analytics?.overview.totalExecutions?.toLocaleString()}</div>
            <div className="metric-label">Total Executions</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon success">
            <i className="fas fa-check-circle"></i>
          </div>
          <div className="metric-content">
            <div className="metric-value">{analytics?.overview.successRate}%</div>
            <div className="metric-label">Success Rate</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon warning">
            <i className="fas fa-clock"></i>
          </div>
          <div className="metric-content">
            <div className="metric-value">{analytics?.overview.averageDuration}min</div>
            <div className="metric-label">Avg Duration</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon info">
            <i className="fas fa-cogs"></i>
          </div>
          <div className="metric-content">
            <div className="metric-value">{analytics?.overview.activeWorkflows}</div>
            <div className="metric-label">Active Workflows</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon error">
            <i className="fas fa-exclamation-triangle"></i>
          </div>
          <div className="metric-content">
            <div className="metric-value">{analytics?.overview.errorRate}%</div>
            <div className="metric-label">Error Rate</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon primary">
            <i className="fas fa-hourglass-half"></i>
          </div>
          <div className="metric-content">
            <div className="metric-value">{analytics?.overview.totalProcessingTime}h</div>
            <div className="metric-label">Total Processing Time</div>
          </div>
        </div>
      </div>

      <div className="charts-section">
        <div className="chart-container">
          <h3>Daily Execution Trends</h3>
          <div className="trend-chart">
            {analytics?.dailyTrends.map(day => (
              <div key={day.date} className="trend-bar">
                <div className="trend-value" style={{height: `${(day.executions / Math.max(...analytics.dailyTrends.map(d => d.executions))) * 100}%`}}>
                  <div className="completed-portion" style={{height: `${(day.completed / day.executions) * 100}%`}}></div>
                </div>
                <div className="trend-date">{new Date(day.date).toLocaleDateString('en-US', {month: 'short', day: 'numeric'})}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="status-distribution">
          <h3>Status Distribution</h3>
          <div className="status-chart">
            {analytics?.statusDistribution.map(status => (
              <div key={status.status} className="status-item">
                <div className="status-bar">
                  <div 
                    className="status-fill" 
                    style={{
                      width: `${status.percentage}%`,
                      backgroundColor: getStatusColor(status.status)
                    }}
                  ></div>
                </div>
                <div className="status-info">
                  <span className="status-name">{status.status}</span>
                  <span className="status-count">{status.count} ({status.percentage}%)</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="category-breakdown">
        <h3>Performance by Category</h3>
        <div className="category-grid">
          {analytics?.categoryBreakdown.map(category => (
            <div key={category.category} className="category-card">
              <div className="category-name">{category.category}</div>
              <div className="category-metrics">
                <div className="category-executions">{category.executions} executions</div>
                <div className="category-success">{category.successRate}% success</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderPerformanceTab = () => (
    <div className="performance-tab">
      <div className="workflow-filters">
        <select 
          value={selectedWorkflow} 
          onChange={(e) => setSelectedWorkflow(e.target.value)}
        >
          <option value="all">All Workflows</option>
          {analytics?.workflowMetrics.map(workflow => (
            <option key={workflow.name} value={workflow.name}>{workflow.name}</option>
          ))}
        </select>

        <select 
          value={filters.status} 
          onChange={(e) => setFilters({...filters, status: e.target.value})}
        >
          <option value="all">All Performance</option>
          <option value="high-success">High Success (≥90%)</option>
          <option value="low-success">Low Success (&lt;90%)</option>
        </select>

        <select 
          value={filters.category} 
          onChange={(e) => setFilters({...filters, category: e.target.value})}
        >
          <option value="all">All Categories</option>
          <option value="business">Business</option>
          <option value="technical">Technical</option>
          <option value="marketing">Marketing</option>
          <option value="finance">Finance</option>
          <option value="operations">Operations</option>
        </select>
      </div>

      <div className="workflow-performance-list">
        {filteredWorkflowMetrics.map(workflow => (
          <div key={workflow.name} className="workflow-performance-card">
            <div className="workflow-header">
              <div className="workflow-name">
                <h4>{workflow.name}</h4>
                <span className="workflow-category">{workflow.category}</span>
              </div>
              <div className="workflow-trend">
                <i className={`fas fa-arrow-${workflow.trend === 'up' ? 'up' : 'down'}`}></i>
                <span className={workflow.trend}>{workflow.trendPercentage}%</span>
              </div>
            </div>

            <div className="workflow-metrics">
              <div className="metric-item">
                <div className="metric-label">Executions</div>
                <div className="metric-value">{workflow.executions}</div>
              </div>
              <div className="metric-item">
                <div className="metric-label">Success Rate</div>
                <div className="metric-value success">{workflow.successRate}%</div>
              </div>
              <div className="metric-item">
                <div className="metric-label">Avg Duration</div>
                <div className="metric-value">{workflow.avgDuration}min</div>
              </div>
              <div className="metric-item">
                <div className="metric-label">Resource Usage</div>
                <div className="metric-value">{workflow.avgResourceUsage}%</div>
              </div>
            </div>

            <div className="workflow-progress-bars">
              <div className="progress-item">
                <div className="progress-label">Success Rate</div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill success" 
                    style={{width: `${workflow.successRate}%`}}
                  ></div>
                </div>
              </div>
              <div className="progress-item">
                <div className="progress-label">Resource Usage</div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill warning" 
                    style={{width: `${workflow.avgResourceUsage}%`}}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderTrendsTab = () => (
    <div className="trends-tab">
      <div className="resource-trends">
        <h3>Resource Utilization (24h)</h3>
        <div className="resource-chart">
          {analytics?.resourceTrends.map(hour => (
            <div key={hour.hour} className="hour-bar">
              <div className="resource-bars">
                <div 
                  className="cpu-bar" 
                  style={{height: `${hour.cpu}%`}}
                  title={`CPU: ${hour.cpu}%`}
                ></div>
                <div 
                  className="memory-bar" 
                  style={{height: `${hour.memory}%`}}
                  title={`Memory: ${hour.memory}%`}
                ></div>
                <div 
                  className="network-bar" 
                  style={{height: `${hour.network}%`}}
                  title={`Network: ${hour.network}%`}
                ></div>
              </div>
              <div className="hour-label">{hour.hour}:00</div>
            </div>
          ))}
        </div>
        <div className="resource-legend">
          <div className="legend-item">
            <div className="legend-color cpu"></div>
            <span>CPU</span>
          </div>
          <div className="legend-item">
            <div className="legend-color memory"></div>
            <span>Memory</span>
          </div>
          <div className="legend-item">
            <div className="legend-color network"></div>
            <span>Network</span>
          </div>
        </div>
      </div>

      <div className="trigger-analysis">
        <h3>Trigger Analysis</h3>
        <div className="trigger-grid">
          {analytics?.triggerAnalysis.map(trigger => (
            <div key={trigger.trigger} className="trigger-card">
              <div className="trigger-icon">
                <i className={`fas fa-${trigger.trigger === 'schedule' ? 'calendar' : 
                                        trigger.trigger === 'manual' ? 'user' :
                                        trigger.trigger === 'api' ? 'plug' : 'bolt'}`}></i>
              </div>
              <div className="trigger-info">
                <div className="trigger-name">{trigger.trigger}</div>
                <div className="trigger-stats">
                  <div className="trigger-count">{trigger.count} executions</div>
                  <div className="trigger-duration">{trigger.avgDuration}min avg</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="recent-executions">
        <h3>Recent Executions</h3>
        <div className="executions-list">
          {analytics?.recentExecutions.slice(0, 10).map(execution => (
            <div key={execution.id} className="execution-item">
              <div className="execution-status">
                <div 
                  className="status-indicator" 
                  style={{backgroundColor: getStatusColor(execution.status)}}
                ></div>
              </div>
              <div className="execution-info">
                <div className="execution-workflow">{execution.workflow}</div>
                <div className="execution-details">
                  <span className="execution-time">{Math.round(execution.duration / 60)}min</span>
                  <span className="execution-steps">{execution.stepsCompleted}/{execution.steps} steps</span>
                  <span className="execution-trigger">{execution.triggeredBy}</span>
                </div>
              </div>
              <div className="execution-timestamp">
                {new Date(execution.timestamp).toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderInsightsTab = () => (
    <div className="insights-tab">
      <div className="insights-grid">
        {analytics?.insights.map((insight, index) => (
          <div key={index} className="insight-card" data-impact={insight.impact}>
            <div className="insight-header">
              <div className="insight-icon">
                <i className={getInsightIcon(insight.type)} style={{color: getInsightColor(insight.impact)}}></i>
              </div>
              <div className="insight-title">{insight.title}</div>
            </div>
            <div className="insight-description">{insight.description}</div>
            <div className="insight-recommendation">
              <strong>Recommendation:</strong> {insight.recommendation}
            </div>
          </div>
        ))}
      </div>

      <div className="performance-recommendations">
        <h3>Performance Optimization Recommendations</h3>
        <div className="recommendations-list">
          <div className="recommendation-item high-priority">
            <div className="recommendation-icon">
              <i className="fas fa-exclamation-triangle"></i>
            </div>
            <div className="recommendation-content">
              <div className="recommendation-title">Optimize High-Failure Workflows</div>
              <div className="recommendation-description">
                3 workflows have failure rates above 15%. Focus on error handling improvements.
              </div>
              <div className="recommendation-impact">High Impact</div>
            </div>
          </div>

          <div className="recommendation-item medium-priority">
            <div className="recommendation-icon">
              <i className="fas fa-chart-line"></i>
            </div>
            <div className="recommendation-content">
              <div className="recommendation-title">Implement Load Balancing</div>
              <div className="recommendation-description">
                Peak hour resource usage reaches 85%. Consider implementing load balancing.
              </div>
              <div className="recommendation-impact">Medium Impact</div>
            </div>
          </div>

          <div className="recommendation-item low-priority">
            <div className="recommendation-icon">
              <i className="fas fa-clock"></i>
            </div>
            <div className="recommendation-content">
              <div className="recommendation-title">Schedule Optimization</div>
              <div className="recommendation-description">
                Distribute scheduled workflows more evenly throughout the day.
              </div>
              <div className="recommendation-impact">Low Impact</div>
            </div>
          </div>
        </div>
      </div>

      <div className="predictive-insights">
        <h3>Predictive Insights</h3>
        <div className="predictions-grid">
          <div className="prediction-card">
            <div className="prediction-metric">Resource Usage</div>
            <div className="prediction-value">↗ +12%</div>
            <div className="prediction-timeframe">Next 7 days</div>
            <div className="prediction-confidence">85% confidence</div>
          </div>

          <div className="prediction-card">
            <div className="prediction-metric">Failure Rate</div>
            <div className="prediction-value">↘ -5%</div>
            <div className="prediction-timeframe">Next 30 days</div>
            <div className="prediction-confidence">72% confidence</div>
          </div>

          <div className="prediction-card">
            <div className="prediction-metric">Execution Volume</div>
            <div className="prediction-value">↗ +18%</div>
            <div className="prediction-timeframe">Next 14 days</div>
            <div className="prediction-confidence">91% confidence</div>
          </div>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="workflow-performance-analytics loading">
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading performance analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="workflow-performance-analytics">
      <div className="analytics-header">
        <div className="header-left">
          <h2>Workflow Performance Analytics</h2>
          <p>Comprehensive insights into workflow performance and optimization opportunities</p>
        </div>
        <div className="header-controls">
          <div className="time-range-selector">
            <button 
              className={`time-btn ${timeRange === '1d' ? 'active' : ''}`}
              onClick={() => setTimeRange('1d')}
            >
              1 Day
            </button>
            <button 
              className={`time-btn ${timeRange === '7d' ? 'active' : ''}`}
              onClick={() => setTimeRange('7d')}
            >
              7 Days
            </button>
            <button 
              className={`time-btn ${timeRange === '30d' ? 'active' : ''}`}
              onClick={() => setTimeRange('30d')}
            >
              30 Days
            </button>
            <button 
              className={`time-btn ${timeRange === '90d' ? 'active' : ''}`}
              onClick={() => setTimeRange('90d')}
            >
              90 Days
            </button>
          </div>
        </div>
      </div>

      <div className="analytics-nav">
        <button 
          className={`nav-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <i className="fas fa-chart-pie"></i>
          Overview
        </button>
        <button 
          className={`nav-btn ${activeTab === 'performance' ? 'active' : ''}`}
          onClick={() => setActiveTab('performance')}
        >
          <i className="fas fa-tachometer-alt"></i>
          Performance
        </button>
        <button 
          className={`nav-btn ${activeTab === 'trends' ? 'active' : ''}`}
          onClick={() => setActiveTab('trends')}
        >
          <i className="fas fa-chart-line"></i>
          Trends
        </button>
        <button 
          className={`nav-btn ${activeTab === 'insights' ? 'active' : ''}`}
          onClick={() => setActiveTab('insights')}
        >
          <i className="fas fa-lightbulb"></i>
          Insights
        </button>
      </div>

      <div className="analytics-content">
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'performance' && renderPerformanceTab()}
        {activeTab === 'trends' && renderTrendsTab()}
        {activeTab === 'insights' && renderInsightsTab()}
      </div>
    </div>
  );
};

export default WorkflowPerformanceAnalytics;
