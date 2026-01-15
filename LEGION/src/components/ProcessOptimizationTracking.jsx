import React, { useState, useEffect, useCallback } from 'react';

const ProcessOptimizationTracking = () => {
  const [optimizations, setOptimizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('dashboard'); // dashboard, process, trends, recommendations
  const [filters, setFilters] = useState({
    status: 'all',
    impact: 'all',
    category: 'all',
    priority: 'all'
  });
  const [selectedOptimization, setSelectedOptimization] = useState(null);
  const [timeRange, setTimeRange] = useState('7d');

  const generateOptimizations = useCallback(() => {
    const categories = ['workflow', 'resource', 'performance', 'automation', 'integration', 'security'];
    const statuses = ['active', 'completed', 'planned', 'analyzing', 'implementing'];
    const impacts = ['high', 'medium', 'low', 'critical'];
    const priorities = ['critical', 'high', 'medium', 'low'];
    
    const optimizationNames = [
      'Workflow Execution Optimization', 'Resource Allocation Improvement', 'Database Query Enhancement',
      'API Response Time Reduction', 'Memory Usage Optimization', 'CPU Utilization Enhancement',
      'Network Bandwidth Optimization', 'Cache Hit Rate Improvement', 'Error Rate Reduction',
      'Throughput Enhancement', 'Latency Optimization', 'Scalability Improvement',
      'Security Protocol Enhancement', 'Data Processing Speed Up', 'Automation Efficiency',
      'Integration Performance Boost', 'Load Balancing Optimization', 'Backup Process Enhancement'
    ];

    return Array.from({ length: 18 }, (_, index) => ({
      id: `optimization-${index + 1}`,
      name: optimizationNames[index] || `Optimization ${index + 1}`,
      description: `Comprehensive optimization initiative to improve ${categories[Math.floor(Math.random() * categories.length)]} efficiency and performance`,
      category: categories[Math.floor(Math.random() * categories.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      impact: impacts[Math.floor(Math.random() * impacts.length)],
      priority: priorities[Math.floor(Math.random() * priorities.length)],
      progress: Math.floor(Math.random() * 100),
      targetMetric: ['Response Time', 'Throughput', 'Error Rate', 'Resource Usage', 'Cost Reduction'][Math.floor(Math.random() * 5)],
      currentValue: (Math.random() * 1000 + 100).toFixed(2),
      targetValue: (Math.random() * 800 + 50).toFixed(2),
      improvement: (Math.random() * 50 + 10).toFixed(1),
      estimatedImpact: {
        performance: Math.floor(Math.random() * 40) + 10,
        cost: Math.floor(Math.random() * 30) + 5,
        efficiency: Math.floor(Math.random() * 50) + 20,
        reliability: Math.floor(Math.random() * 35) + 15
      },
      timeline: {
        started: new Date(Date.now() - Math.random() * 30 * 86400000).toISOString(),
        planned: new Date(Date.now() + Math.random() * 60 * 86400000).toISOString(),
        duration: Math.floor(Math.random() * 90) + 7 // days
      },
      metrics: {
        baseline: (Math.random() * 1000 + 200).toFixed(2),
        current: (Math.random() * 800 + 150).toFixed(2),
        target: (Math.random() * 500 + 100).toFixed(2),
        achieved: (Math.random() * 40 + 10).toFixed(1)
      },
      recommendations: Array.from({ length: Math.floor(Math.random() * 5) + 2 }, (_, i) => ({
        id: `rec-${i + 1}`,
        title: ['Implement caching layer', 'Optimize database queries', 'Upgrade hardware resources', 'Refactor code structure', 'Add monitoring tools', 'Enhance error handling'][i % 6],
        impact: ['high', 'medium', 'low'][Math.floor(Math.random() * 3)],
        effort: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)],
        roi: (Math.random() * 200 + 50).toFixed(0)
      })),
      affectedProcesses: Array.from({ length: Math.floor(Math.random() * 4) + 1 }, () => 
        ['Data Processing', 'User Authentication', 'Report Generation', 'API Integration', 'File Processing'][Math.floor(Math.random() * 5)]
      ),
      kpis: {
        responseTime: (Math.random() * 2000 + 100).toFixed(0) + 'ms',
        throughput: (Math.random() * 1000 + 100).toFixed(0) + '/min',
        errorRate: (Math.random() * 5).toFixed(2) + '%',
        resourceUsage: Math.floor(Math.random() * 80) + 10 + '%',
        availability: (Math.random() * 10 + 90).toFixed(1) + '%'
      },
      owner: ['System Admin', 'DevOps Team', 'Performance Team', 'Architecture Team'][Math.floor(Math.random() * 4)],
      stakeholders: ['Operations', 'Development', 'Business', 'Infrastructure'].slice(0, Math.floor(Math.random() * 3) + 1),
      costs: {
        estimated: Math.floor(Math.random() * 50000) + 5000,
        actual: Math.floor(Math.random() * 45000) + 3000,
        savings: Math.floor(Math.random() * 100000) + 10000
      },
      risks: [
        'Performance degradation during implementation',
        'Temporary service disruption',
        'Resource allocation conflicts',
        'Integration complexity'
      ].slice(0, Math.floor(Math.random() * 3) + 1),
      successCriteria: [
        '50% improvement in response time',
        '90% reduction in error rate',
        '30% cost savings achieved',
        'Zero service downtime'
      ].slice(0, Math.floor(Math.random() * 3) + 1),
      tags: ['performance', 'optimization', 'efficiency', 'cost-reduction', 'automation', 'monitoring'].slice(0, Math.floor(Math.random() * 4) + 2),
      createdAt: new Date(Date.now() - Math.random() * 90 * 86400000).toISOString(),
      updatedAt: new Date(Date.now() - Math.random() * 7 * 86400000).toISOString(),
      history: Array.from({ length: Math.floor(Math.random() * 10) + 3 }, (_, histIndex) => ({
        timestamp: new Date(Date.now() - Math.random() * 30 * 86400000).toISOString(),
        action: ['Status Updated', 'Metric Improved', 'Recommendation Added', 'Progress Made'][Math.floor(Math.random() * 4)],
        details: `Optimization progress update with ${Math.floor(Math.random() * 20) + 5}% improvement in target metrics`,
        user: ['admin', 'system', 'optimizer'][Math.floor(Math.random() * 3)]
      }))
    }));
  }, []);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        await new Promise(resolve => setTimeout(resolve, 1000));
        setOptimizations(generateOptimizations());
        setLoading(false);
      } catch (error) {
        setLoading(false);
        console.error('Error loading optimization data:', error);
      }
    };

    loadData();
  }, [generateOptimizations]);

  const filteredOptimizations = optimizations.filter(opt => {
    return (filters.status === 'all' || opt.status === filters.status) &&
           (filters.impact === 'all' || opt.impact === filters.impact) &&
           (filters.category === 'all' || opt.category === filters.category) &&
           (filters.priority === 'all' || opt.priority === filters.priority);
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return '#28a745';
      case 'completed': return '#17a2b8';
      case 'planned': return '#ffc107';
      case 'analyzing': return '#6f42c1';
      case 'implementing': return '#fd7e14';
      default: return '#6c757d';
    }
  };

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'critical': return '#dc3545';
      case 'high': return '#fd7e14';
      case 'medium': return '#ffc107';
      case 'low': return '#28a745';
      default: return '#6c757d';
    }
  };

  const renderDashboardView = () => {
    const summaryStats = {
      total: optimizations.length,
      active: optimizations.filter(o => o.status === 'active').length,
      completed: optimizations.filter(o => o.status === 'completed').length,
      avgImprovement: (optimizations.reduce((sum, o) => sum + parseFloat(o.improvement), 0) / optimizations.length).toFixed(1)
    };

    return (
      <div className="optimization-dashboard">
        <div className="summary-cards">
          <div className="summary-card total">
            <div className="card-icon">
              <i className="fas fa-chart-line"></i>
            </div>
            <div className="card-content">
              <h3>{summaryStats.total}</h3>
              <p>Total Optimizations</p>
            </div>
          </div>
          <div className="summary-card active">
            <div className="card-icon">
              <i className="fas fa-cog"></i>
            </div>
            <div className="card-content">
              <h3>{summaryStats.active}</h3>
              <p>Active Projects</p>
            </div>
          </div>
          <div className="summary-card completed">
            <div className="card-icon">
              <i className="fas fa-check-circle"></i>
            </div>
            <div className="card-content">
              <h3>{summaryStats.completed}</h3>
              <p>Completed</p>
            </div>
          </div>
          <div className="summary-card improvement">
            <div className="card-icon">
              <i className="fas fa-arrow-up"></i>
            </div>
            <div className="card-content">
              <h3>{summaryStats.avgImprovement}%</h3>
              <p>Avg Improvement</p>
            </div>
          </div>
        </div>

        <div className="optimization-grid">
          {filteredOptimizations.slice(0, 12).map(optimization => (
            <div key={optimization.id} className="optimization-card">
              <div className="optimization-header">
                <div className="optimization-title">
                  <h3>{optimization.name}</h3>
                  <span className="optimization-category">{optimization.category}</span>
                </div>
                <div className="optimization-badges">
                  <span className="status-badge" style={{backgroundColor: getStatusColor(optimization.status)}}>
                    {optimization.status}
                  </span>
                  <span className="impact-badge" style={{backgroundColor: getImpactColor(optimization.impact)}}>
                    {optimization.impact}
                  </span>
                </div>
              </div>

              <div className="optimization-progress">
                <div className="progress-info">
                  <span>Progress: {optimization.progress}%</span>
                  <span>Target: {optimization.improvement}% improvement</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{width: `${optimization.progress}%`}}></div>
                </div>
              </div>

              <div className="optimization-metrics">
                <div className="metric-item">
                  <span className="metric-label">Current:</span>
                  <span className="metric-value">{optimization.currentValue}</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Target:</span>
                  <span className="metric-value">{optimization.targetValue}</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Improvement:</span>
                  <span className="metric-value">{optimization.improvement}%</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">ROI:</span>
                  <span className="metric-value">${(optimization.costs.savings / optimization.costs.actual * 100).toFixed(0)}%</span>
                </div>
              </div>

              <div className="optimization-actions">
                <button 
                  className="action-btn details"
                  onClick={() => setSelectedOptimization(optimization)}
                >
                  <i className="fas fa-info-circle"></i>
                  Details
                </button>
                <button className="action-btn analyze">
                  <i className="fas fa-chart-bar"></i>
                  Analyze
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderProcessView = () => (
    <div className="process-optimization-list">
      {filteredOptimizations.map(optimization => (
        <div key={optimization.id} className="process-item">
          <div className="process-header">
            <div className="process-info">
              <h3>{optimization.name}</h3>
              <p>{optimization.description}</p>
            </div>
            <div className="process-status">
              <span className="status-badge" style={{backgroundColor: getStatusColor(optimization.status)}}>
                {optimization.status}
              </span>
              <span className="priority-badge" style={{backgroundColor: getImpactColor(optimization.priority)}}>
                {optimization.priority}
              </span>
            </div>
          </div>

          <div className="process-details">
            <div className="detail-section">
              <h4>Impact Analysis</h4>
              <div className="impact-grid">
                <div className="impact-item">
                  <span className="impact-label">Performance:</span>
                  <div className="impact-bar">
                    <div className="impact-fill" style={{width: `${optimization.estimatedImpact.performance}%`}}></div>
                  </div>
                  <span className="impact-value">{optimization.estimatedImpact.performance}%</span>
                </div>
                <div className="impact-item">
                  <span className="impact-label">Cost:</span>
                  <div className="impact-bar">
                    <div className="impact-fill" style={{width: `${optimization.estimatedImpact.cost}%`}}></div>
                  </div>
                  <span className="impact-value">{optimization.estimatedImpact.cost}%</span>
                </div>
                <div className="impact-item">
                  <span className="impact-label">Efficiency:</span>
                  <div className="impact-bar">
                    <div className="impact-fill" style={{width: `${optimization.estimatedImpact.efficiency}%`}}></div>
                  </div>
                  <span className="impact-value">{optimization.estimatedImpact.efficiency}%</span>
                </div>
                <div className="impact-item">
                  <span className="impact-label">Reliability:</span>
                  <div className="impact-bar">
                    <div className="impact-fill" style={{width: `${optimization.estimatedImpact.reliability}%`}}></div>
                  </div>
                  <span className="impact-value">{optimization.estimatedImpact.reliability}%</span>
                </div>
              </div>
            </div>

            <div className="detail-section">
              <h4>Key Performance Indicators</h4>
              <div className="kpi-grid">
                {Object.entries(optimization.kpis).map(([key, value]) => (
                  <div key={key} className="kpi-item">
                    <div className="kpi-label">{key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}</div>
                    <div className="kpi-value">{value}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="detail-section">
              <h4>Affected Processes</h4>
              <div className="processes-tags">
                {optimization.affectedProcesses.map((process, index) => (
                  <span key={index} className="process-tag">{process}</span>
                ))}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  const renderTrendsView = () => {
    const trendData = {
      completionRate: 76.5,
      avgTimeToComplete: 45,
      costSavings: 2340000,
      performanceGain: 34.2
    };

    return (
      <div className="trends-dashboard">
        <div className="trend-summary">
          <div className="trend-card">
            <h4>Completion Rate</h4>
            <div className="trend-value">{trendData.completionRate}%</div>
            <div className="trend-change positive">+12.3% vs last quarter</div>
          </div>
          <div className="trend-card">
            <h4>Avg Time to Complete</h4>
            <div className="trend-value">{trendData.avgTimeToComplete} days</div>
            <div className="trend-change negative">-8.7% vs last quarter</div>
          </div>
          <div className="trend-card">
            <h4>Cost Savings</h4>
            <div className="trend-value">${(trendData.costSavings / 1000000).toFixed(1)}M</div>
            <div className="trend-change positive">+45.2% vs last quarter</div>
          </div>
          <div className="trend-card">
            <h4>Performance Gain</h4>
            <div className="trend-value">{trendData.performanceGain}%</div>
            <div className="trend-change positive">+23.1% vs last quarter</div>
          </div>
        </div>

        <div className="trend-charts">
          <div className="chart-section">
            <h4>Optimization Categories Distribution</h4>
            <div className="category-distribution">
              {['workflow', 'resource', 'performance', 'automation', 'integration', 'security'].map(category => {
                const count = optimizations.filter(o => o.category === category).length;
                const percentage = ((count / optimizations.length) * 100).toFixed(1);
                return (
                  <div key={category} className="category-item">
                    <span className="category-name">{category}</span>
                    <div className="category-bar">
                      <div className="category-fill" style={{width: `${percentage}%`}}></div>
                    </div>
                    <span className="category-count">{count} ({percentage}%)</span>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="chart-section">
            <h4>Impact vs Effort Matrix</h4>
            <div className="matrix-chart">
              <div className="matrix-grid">
                {filteredOptimizations.slice(0, 12).map((opt, index) => (
                  <div 
                    key={opt.id} 
                    className="matrix-point"
                    style={{
                      left: `${Math.random() * 80 + 10}%`,
                      bottom: `${Math.random() * 80 + 10}%`
                    }}
                    title={opt.name}
                  >
                    <div className="point-indicator" style={{backgroundColor: getImpactColor(opt.impact)}}></div>
                  </div>
                ))}
              </div>
              <div className="matrix-labels">
                <div className="x-label">Effort Required</div>
                <div className="y-label">Business Impact</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderRecommendationsView = () => (
    <div className="recommendations-dashboard">
      <div className="recommendations-header">
        <h3>AI-Powered Optimization Recommendations</h3>
        <p>Intelligent suggestions for process improvements based on performance analysis</p>
      </div>

      <div className="recommendations-grid">
        {filteredOptimizations.slice(0, 8).map(optimization => (
          <div key={optimization.id} className="recommendation-card">
            <div className="recommendation-header">
              <h4>{optimization.name}</h4>
              <span className="recommendation-impact" style={{backgroundColor: getImpactColor(optimization.impact)}}>
                {optimization.impact} impact
              </span>
            </div>

            <div className="recommendations-list">
              {optimization.recommendations.slice(0, 3).map(rec => (
                <div key={rec.id} className="recommendation-item">
                  <div className="recommendation-title">{rec.title}</div>
                  <div className="recommendation-details">
                    <span className="rec-impact">Impact: {rec.impact}</span>
                    <span className="rec-effort">Effort: {rec.effort}</span>
                    <span className="rec-roi">ROI: {rec.roi}%</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="recommendation-metrics">
              <div className="metric-small">
                <span className="label">Potential Savings:</span>
                <span className="value">${(optimization.costs.savings / 1000).toFixed(0)}K</span>
              </div>
              <div className="metric-small">
                <span className="label">Time to Implement:</span>
                <span className="value">{optimization.timeline.duration} days</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="process-optimization-tracking loading">
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading optimization data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="process-optimization-tracking">
      <div className="tracking-header">
        <div className="header-left">
          <h2>Process Optimization Tracking</h2>
          <p>Monitor and track process efficiency improvements</p>
        </div>
        <div className="header-actions">
          <div className="view-toggle">
            <button 
              className={`view-btn ${viewMode === 'dashboard' ? 'active' : ''}`}
              onClick={() => setViewMode('dashboard')}
            >
              Dashboard
            </button>
            <button 
              className={`view-btn ${viewMode === 'process' ? 'active' : ''}`}
              onClick={() => setViewMode('process')}
            >
              Processes
            </button>
            <button 
              className={`view-btn ${viewMode === 'trends' ? 'active' : ''}`}
              onClick={() => setViewMode('trends')}
            >
              Trends
            </button>
            <button 
              className={`view-btn ${viewMode === 'recommendations' ? 'active' : ''}`}
              onClick={() => setViewMode('recommendations')}
            >
              Recommendations
            </button>
          </div>
        </div>
      </div>

      <div className="tracking-controls">
        <div className="filter-controls">
          <select value={filters.status} onChange={(e) => setFilters({...filters, status: e.target.value})}>
            <option value="all">All Statuses</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
            <option value="planned">Planned</option>
            <option value="analyzing">Analyzing</option>
          </select>

          <select value={filters.impact} onChange={(e) => setFilters({...filters, impact: e.target.value})}>
            <option value="all">All Impacts</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          <select value={filters.category} onChange={(e) => setFilters({...filters, category: e.target.value})}>
            <option value="all">All Categories</option>
            <option value="workflow">Workflow</option>
            <option value="resource">Resource</option>
            <option value="performance">Performance</option>
            <option value="automation">Automation</option>
          </select>

          <select value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="1y">Last Year</option>
          </select>
        </div>
      </div>

      <div className="tracking-content">
        {viewMode === 'dashboard' && renderDashboardView()}
        {viewMode === 'process' && renderProcessView()}
        {viewMode === 'trends' && renderTrendsView()}
        {viewMode === 'recommendations' && renderRecommendationsView()}
      </div>

      {selectedOptimization && (
        <div className="modal-overlay" onClick={() => setSelectedOptimization(null)}>
          <div className="optimization-detail-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{selectedOptimization.name}</h3>
              <button className="close-btn" onClick={() => setSelectedOptimization(null)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-content">
              <div className="detail-tabs">
                <div className="detail-section">
                  <h4>Overview</h4>
                  <div className="overview-grid">
                    <div className="overview-item">
                      <span className="label">Status:</span>
                      <span className="value" style={{color: getStatusColor(selectedOptimization.status)}}>
                        {selectedOptimization.status}
                      </span>
                    </div>
                    <div className="overview-item">
                      <span className="label">Progress:</span>
                      <span className="value">{selectedOptimization.progress}%</span>
                    </div>
                    <div className="overview-item">
                      <span className="label">Owner:</span>
                      <span className="value">{selectedOptimization.owner}</span>
                    </div>
                    <div className="overview-item">
                      <span className="label">Duration:</span>
                      <span className="value">{selectedOptimization.timeline.duration} days</span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Success Criteria</h4>
                  <ul className="criteria-list">
                    {selectedOptimization.successCriteria.map((criteria, index) => (
                      <li key={index} className="criteria-item">
                        <i className="fas fa-check-circle"></i>
                        {criteria}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="detail-section">
                  <h4>Financial Impact</h4>
                  <div className="financial-grid">
                    <div className="financial-item">
                      <span className="label">Estimated Cost:</span>
                      <span className="value">${selectedOptimization.costs.estimated.toLocaleString()}</span>
                    </div>
                    <div className="financial-item">
                      <span className="label">Actual Cost:</span>
                      <span className="value">${selectedOptimization.costs.actual.toLocaleString()}</span>
                    </div>
                    <div className="financial-item">
                      <span className="label">Expected Savings:</span>
                      <span className="value">${selectedOptimization.costs.savings.toLocaleString()}</span>
                    </div>
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

export default ProcessOptimizationTracking;
