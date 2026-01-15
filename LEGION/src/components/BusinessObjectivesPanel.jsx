import React, { useState, useEffect } from 'react';

const BusinessObjectivesPanel = () => {
  const [objectives, setObjectives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('quarter');
  const [viewMode, setViewMode] = useState('progress'); // 'progress', 'status', 'timeline'

  useEffect(() => {
    const loadObjectives = async () => {
      try {
        setLoading(true);
        setError(null);

        // Simulate API call to enterprise backend
        const response = await fetch(`/api/enterprise/business-objectives?timeRange=${timeRange}`);
        if (!response.ok) throw new Error('Failed to load business objectives');
        
        const data = await response.json();
        setObjectives(data.objectives || []);
      } catch (err) {
        console.error('Error loading business objectives:', err);
        setError(err.message);
        // Mock data for development
        setObjectives([
          {
            id: 'obj_001',
            title: 'Increase Annual Revenue',
            description: 'Achieve 25% growth in annual recurring revenue',
            category: 'Revenue',
            priority: 'High',
            target: 1250000,
            current: 987500,
            unit: 'USD',
            startDate: '2024-01-01',
            endDate: '2024-12-31',
            status: 'On Track',
            progress: 79,
            owner: 'Sales Team',
            department: 'Sales',
            milestones: [
              { id: 'm1', title: 'Q1 Target', target: 312500, achieved: 315000, date: '2024-03-31', status: 'Completed' },
              { id: 'm2', title: 'Q2 Target', target: 625000, achieved: 630000, date: '2024-06-30', status: 'Completed' },
              { id: 'm3', title: 'Q3 Target', target: 937500, achieved: 987500, date: '2024-09-30', status: 'Completed' },
              { id: 'm4', title: 'Q4 Target', target: 1250000, achieved: 0, date: '2024-12-31', status: 'In Progress' }
            ],
            kpis: [
              { name: 'Monthly Recurring Revenue', value: 82292, target: 104167, unit: 'USD' },
              { name: 'Customer Acquisition Rate', value: 87, target: 100, unit: 'customers/month' },
              { name: 'Revenue per Customer', value: 946, target: 1042, unit: 'USD' }
            ],
            risks: [
              { level: 'Medium', description: 'Q4 seasonal slowdown may impact final quarter targets' }
            ],
            lastUpdated: new Date().toISOString()
          },
          {
            id: 'obj_002',
            title: 'Market Expansion',
            description: 'Enter 3 new geographical markets',
            category: 'Growth',
            priority: 'High',
            target: 3,
            current: 2,
            unit: 'markets',
            startDate: '2024-01-01',
            endDate: '2024-12-31',
            status: 'Behind Schedule',
            progress: 67,
            owner: 'Marketing Team',
            department: 'Marketing',
            milestones: [
              { id: 'm1', title: 'Market Research', target: 1, achieved: 1, date: '2024-02-28', status: 'Completed' },
              { id: 'm2', title: 'First Market Entry', target: 1, achieved: 1, date: '2024-06-30', status: 'Completed' },
              { id: 'm3', title: 'Second Market Entry', target: 2, achieved: 2, date: '2024-09-30', status: 'Completed' },
              { id: 'm4', title: 'Third Market Entry', target: 3, achieved: 0, date: '2024-12-31', status: 'At Risk' }
            ],
            kpis: [
              { name: 'Market Penetration Rate', value: 12, target: 20, unit: '%' },
              { name: 'Local Partnerships', value: 8, target: 12, unit: 'partners' },
              { name: 'Regional Revenue', value: 156000, target: 250000, unit: 'USD' }
            ],
            risks: [
              { level: 'High', description: 'Regulatory approval delays in target market 3' },
              { level: 'Medium', description: 'Competition intensifying in newly entered markets' }
            ],
            lastUpdated: new Date().toISOString()
          },
          {
            id: 'obj_003',
            title: 'Operational Efficiency',
            description: 'Reduce operational costs by 15%',
            category: 'Efficiency',
            priority: 'Medium',
            target: 15,
            current: 11.2,
            unit: '%',
            startDate: '2024-01-01',
            endDate: '2024-12-31',
            status: 'On Track',
            progress: 75,
            owner: 'Operations Team',
            department: 'Operations',
            milestones: [
              { id: 'm1', title: 'Process Automation', target: 5, achieved: 6.2, date: '2024-04-30', status: 'Completed' },
              { id: 'm2', title: 'Supply Chain Optimization', target: 10, achieved: 11.2, date: '2024-08-31', status: 'Completed' },
              { id: 'm3', title: 'Technology Upgrades', target: 15, achieved: 0, date: '2024-12-31', status: 'In Progress' }
            ],
            kpis: [
              { name: 'Cost per Unit', value: 42.50, target: 38.25, unit: 'USD' },
              { name: 'Process Efficiency', value: 87, target: 92, unit: '%' },
              { name: 'Automation Rate', value: 68, target: 80, unit: '%' }
            ],
            risks: [
              { level: 'Low', description: 'Technology implementation timeline may extend' }
            ],
            lastUpdated: new Date().toISOString()
          },
          {
            id: 'obj_004',
            title: 'Customer Satisfaction',
            description: 'Achieve 95% customer satisfaction score',
            category: 'Quality',
            priority: 'High',
            target: 95,
            current: 91.8,
            unit: '%',
            startDate: '2024-01-01',
            endDate: '2024-12-31',
            status: 'On Track',
            progress: 97,
            owner: 'Customer Success Team',
            department: 'Customer Success',
            milestones: [
              { id: 'm1', title: 'Service Standards Review', target: 85, achieved: 87, date: '2024-03-31', status: 'Completed' },
              { id: 'm2', title: 'Staff Training Program', target: 90, achieved: 91.8, date: '2024-06-30', status: 'Completed' },
              { id: 'm3', title: 'System Improvements', target: 95, achieved: 0, date: '2024-12-31', status: 'In Progress' }
            ],
            kpis: [
              { name: 'Response Time', value: 2.3, target: 2.0, unit: 'hours' },
              { name: 'Resolution Rate', value: 94, target: 97, unit: '%' },
              { name: 'Customer Retention', value: 96.5, target: 98, unit: '%' }
            ],
            risks: [
              { level: 'Low', description: 'Seasonal support volume increases may affect response times' }
            ],
            lastUpdated: new Date().toISOString()
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    loadObjectives();
    const interval = setInterval(loadObjectives, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [timeRange]);

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'completed': return '#48bb78';
      case 'on track': return '#4299e1';
      case 'behind schedule': return '#ed8936';
      case 'at risk': return '#e53e3e';
      case 'in progress': return '#38b2ac';
      default: return '#a0aec0';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority.toLowerCase()) {
      case 'high': return '#e53e3e';
      case 'medium': return '#ed8936';
      case 'low': return '#48bb78';
      default: return '#a0aec0';
    }
  };

  const getRiskColor = (level) => {
    switch (level.toLowerCase()) {
      case 'high': return '#e53e3e';
      case 'medium': return '#ed8936';
      case 'low': return '#48bb78';
      default: return '#a0aec0';
    }
  };

  const formatNumber = (value, unit) => {
    if (unit === 'USD') {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(value);
    }
    if (unit === '%') {
      return `${value.toFixed(1)}%`;
    }
    return `${value.toLocaleString()} ${unit}`;
  };

  if (loading) {
    return (
      <div className="business-objectives-panel loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading business objectives...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="business-objectives-panel error">
        <div className="error-message">
          <h3>Error Loading Objectives</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="business-objectives-panel">
      {/* Header */}
      <div className="panel-header">
        <div className="header-content">
          <h2>Business Objectives Progress</h2>
          <p>Track and monitor strategic business goals and key performance indicators</p>
        </div>
        <div className="header-controls">
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-range-selector"
          >
            <option value="month">This Month</option>
            <option value="quarter">This Quarter</option>
            <option value="year">This Year</option>
            <option value="all">All Time</option>
          </select>
          <select 
            value={viewMode} 
            onChange={(e) => setViewMode(e.target.value)}
            className="view-mode-selector"
          >
            <option value="progress">Progress View</option>
            <option value="status">Status View</option>
            <option value="timeline">Timeline View</option>
          </select>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="summary-cards">
        <div className="summary-card">
          <div className="summary-icon">📊</div>
          <div className="summary-content">
            <h3>{objectives.length}</h3>
            <p>Active Objectives</p>
          </div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">✅</div>
          <div className="summary-content">
            <h3>{objectives.filter(obj => obj.status === 'On Track').length}</h3>
            <p>On Track</p>
          </div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">⚠️</div>
          <div className="summary-content">
            <h3>{objectives.filter(obj => obj.status === 'Behind Schedule' || obj.status === 'At Risk').length}</h3>
            <p>At Risk</p>
          </div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">📈</div>
          <div className="summary-content">
            <h3>{Math.round(objectives.reduce((sum, obj) => sum + obj.progress, 0) / objectives.length)}%</h3>
            <p>Avg Progress</p>
          </div>
        </div>
      </div>

      {/* Objectives List */}
      <div className="objectives-container">
        {objectives.map((objective) => (
          <div key={objective.id} className="objective-card">
            {/* Objective Header */}
            <div className="objective-header">
              <div className="objective-title">
                <h3>{objective.title}</h3>
                <p>{objective.description}</p>
              </div>
              <div className="objective-badges">
                <span 
                  className="priority-badge"
                  style={{ backgroundColor: getPriorityColor(objective.priority) }}
                >
                  {objective.priority}
                </span>
                <span 
                  className="status-badge"
                  style={{ backgroundColor: getStatusColor(objective.status) }}
                >
                  {objective.status}
                </span>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="progress-section">
              <div className="progress-header">
                <span className="progress-label">
                  Progress: {formatNumber(objective.current, objective.unit)} / {formatNumber(objective.target, objective.unit)}
                </span>
                <span className="progress-percentage">{objective.progress}%</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ 
                    width: `${objective.progress}%`,
                    backgroundColor: getStatusColor(objective.status)
                  }}
                ></div>
              </div>
            </div>

            {/* Objective Details */}
            <div className="objective-details">
              <div className="detail-section">
                <h4>Owner & Timeline</h4>
                <div className="detail-row">
                  <span className="detail-label">Owner:</span>
                  <span className="detail-value">{objective.owner} ({objective.department})</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Timeline:</span>
                  <span className="detail-value">
                    {new Date(objective.startDate).toLocaleDateString()} - {new Date(objective.endDate).toLocaleDateString()}
                  </span>
                </div>
              </div>

              {/* Milestones */}
              {objective.milestones && objective.milestones.length > 0 && (
                <div className="detail-section">
                  <h4>Milestones</h4>
                  <div className="milestones-list">
                    {objective.milestones.map((milestone) => (
                      <div key={milestone.id} className="milestone-item">
                        <div className="milestone-header">
                          <span className="milestone-title">{milestone.title}</span>
                          <span 
                            className="milestone-status"
                            style={{ color: getStatusColor(milestone.status) }}
                          >
                            {milestone.status}
                          </span>
                        </div>
                        <div className="milestone-details">
                          <span>Target: {formatNumber(milestone.target, objective.unit)}</span>
                          {milestone.achieved > 0 && (
                            <span>Achieved: {formatNumber(milestone.achieved, objective.unit)}</span>
                          )}
                          <span>Due: {new Date(milestone.date).toLocaleDateString()}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* KPIs */}
              {objective.kpis && objective.kpis.length > 0 && (
                <div className="detail-section">
                  <h4>Key Performance Indicators</h4>
                  <div className="kpis-grid">
                    {objective.kpis.map((kpi, index) => (
                      <div key={index} className="kpi-item">
                        <div className="kpi-name">{kpi.name}</div>
                        <div className="kpi-values">
                          <span className="kpi-current">{formatNumber(kpi.value, kpi.unit)}</span>
                          <span className="kpi-target">/ {formatNumber(kpi.target, kpi.unit)}</span>
                        </div>
                        <div className="kpi-progress">
                          <div 
                            className="kpi-progress-bar"
                            style={{ 
                              width: `${Math.min((kpi.value / kpi.target) * 100, 100)}%`,
                              backgroundColor: (kpi.value / kpi.target) >= 0.9 ? '#48bb78' : 
                                              (kpi.value / kpi.target) >= 0.7 ? '#ed8936' : '#e53e3e'
                            }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Risks */}
              {objective.risks && objective.risks.length > 0 && (
                <div className="detail-section">
                  <h4>Risk Assessment</h4>
                  <div className="risks-list">
                    {objective.risks.map((risk, index) => (
                      <div key={index} className="risk-item">
                        <span 
                          className="risk-level"
                          style={{ backgroundColor: getRiskColor(risk.level) }}
                        >
                          {risk.level}
                        </span>
                        <span className="risk-description">{risk.description}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Last Updated */}
            <div className="objective-footer">
              <span className="last-updated">
                Last Updated: {new Date(objective.lastUpdated).toLocaleString()}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BusinessObjectivesPanel;
