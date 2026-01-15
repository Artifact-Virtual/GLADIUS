import React, { useState, useEffect } from 'react';

const DepartmentStatusBoard = ({ departments, onDepartmentClick }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('overview'); // 'overview', 'activities', 'performance'
  const [selectedDepartment, setSelectedDepartment] = useState(null);
  const [data, setData] = useState({
    departments: [],
    activities: [],
    performance: {},
    health: {}
  });

  useEffect(() => {
    const loadDepartmentData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Use provided departments or fetch from API
        if (departments) {
          setData(prev => ({ ...prev, departments }));
        } else {
          const response = await fetch('/api/enterprise/department-activities');
          if (!response.ok) throw new Error('Failed to load department data');
          
          const apiData = await response.json();
          setData(apiData);
        }
      } catch (err) {
        console.error('Error loading department data:', err);
        setError(err.message);
        
        // Mock data for development
        const mockData = {
          departments: [
            {
              id: 'strategy',
              name: 'Strategy',
              description: 'Strategic planning and business development',
              status: 'Active',
              priority: 'High',
              health: 92,
              activeAgents: 3,
              totalActivities: 8,
              completedActivities: 6,
              pendingActivities: 2,
              teamSize: 5,
              budget: 125000,
              budgetUsed: 87500,
              kpis: [
                { name: 'Strategic Goals Met', value: 85, target: 90, unit: '%' },
                { name: 'Planning Efficiency', value: 92, target: 88, unit: '%' },
                { name: 'Stakeholder Satisfaction', value: 88, target: 85, unit: '%' }
              ],
              recentActivity: [
                { type: 'milestone', title: 'Q3 Strategy Review Completed', timestamp: new Date().toISOString() },
                { type: 'update', title: 'Market Analysis Updated', timestamp: new Date(Date.now() - 3600000).toISOString() },
                { type: 'alert', title: 'Budget Review Required', timestamp: new Date(Date.now() - 7200000).toISOString() }
              ],
              currentFocus: 'Market expansion planning and competitive analysis'
            },
            {
              id: 'finance',
              name: 'Finance',
              description: 'Financial analysis and budget management',
              status: 'Active',
              priority: 'High',
              health: 95,
              activeAgents: 4,
              totalActivities: 12,
              completedActivities: 10,
              pendingActivities: 2,
              teamSize: 8,
              budget: 200000,
              budgetUsed: 145000,
              kpis: [
                { name: 'Budget Accuracy', value: 97, target: 95, unit: '%' },
                { name: 'Financial Reporting Timeliness', value: 99, target: 98, unit: '%' },
                { name: 'Cost Optimization', value: 88, target: 85, unit: '%' }
              ],
              recentActivity: [
                { type: 'milestone', title: 'Monthly Financial Report Generated', timestamp: new Date().toISOString() },
                { type: 'update', title: 'Revenue Projection Updated', timestamp: new Date(Date.now() - 1800000).toISOString() },
                { type: 'success', title: 'Cost Reduction Target Achieved', timestamp: new Date(Date.now() - 5400000).toISOString() }
              ],
              currentFocus: 'Revenue optimization and cost analysis for Q4'
            },
            {
              id: 'marketing',
              name: 'Marketing',
              description: 'Brand management and customer acquisition',
              status: 'Active',
              priority: 'Medium',
              health: 78,
              activeAgents: 2,
              totalActivities: 15,
              completedActivities: 11,
              pendingActivities: 4,
              teamSize: 6,
              budget: 180000,
              budgetUsed: 142000,
              kpis: [
                { name: 'Lead Generation', value: 82, target: 85, unit: '%' },
                { name: 'Campaign ROI', value: 156, target: 150, unit: '%' },
                { name: 'Brand Awareness', value: 74, target: 80, unit: '%' }
              ],
              recentActivity: [
                { type: 'campaign', title: 'Q3 Digital Campaign Launched', timestamp: new Date(Date.now() - 3600000).toISOString() },
                { type: 'update', title: 'Social Media Metrics Updated', timestamp: new Date(Date.now() - 7200000).toISOString() },
                { type: 'alert', title: 'Campaign Budget Review Needed', timestamp: new Date(Date.now() - 10800000).toISOString() }
              ],
              currentFocus: 'Digital transformation and lead nurturing optimization'
            },
            {
              id: 'operations',
              name: 'Operations',
              description: 'Process optimization and operational efficiency',
              status: 'Active',
              priority: 'High',
              health: 89,
              activeAgents: 5,
              totalActivities: 20,
              completedActivities: 16,
              pendingActivities: 4,
              teamSize: 12,
              budget: 250000,
              budgetUsed: 198000,
              kpis: [
                { name: 'Process Efficiency', value: 91, target: 90, unit: '%' },
                { name: 'Automation Rate', value: 67, target: 70, unit: '%' },
                { name: 'Quality Score', value: 94, target: 92, unit: '%' }
              ],
              recentActivity: [
                { type: 'automation', title: 'New Workflow Automated', timestamp: new Date(Date.now() - 1800000).toISOString() },
                { type: 'milestone', title: 'Process Optimization Milestone Reached', timestamp: new Date(Date.now() - 5400000).toISOString() },
                { type: 'update', title: 'Efficiency Metrics Updated', timestamp: new Date(Date.now() - 9000000).toISOString() }
              ],
              currentFocus: 'Automation rollout and process standardization'
            },
            {
              id: 'communication',
              name: 'Communication',
              description: 'Internal and external communication management',
              status: 'Active',
              priority: 'Medium',
              health: 85,
              activeAgents: 2,
              totalActivities: 10,
              completedActivities: 7,
              pendingActivities: 3,
              teamSize: 4,
              budget: 95000,
              budgetUsed: 71000,
              kpis: [
                { name: 'Message Delivery Rate', value: 98, target: 97, unit: '%' },
                { name: 'Response Time', value: 2.1, target: 2.5, unit: 'hours' },
                { name: 'Stakeholder Engagement', value: 87, target: 85, unit: '%' }
              ],
              recentActivity: [
                { type: 'content', title: 'Weekly Newsletter Published', timestamp: new Date(Date.now() - 3600000).toISOString() },
                { type: 'update', title: 'Communication Guidelines Updated', timestamp: new Date(Date.now() - 7200000).toISOString() },
                { type: 'milestone', title: 'Social Media Campaign Completed', timestamp: new Date(Date.now() - 14400000).toISOString() }
              ],
              currentFocus: 'Content strategy optimization and stakeholder communication'
            },
            {
              id: 'business_intelligence',
              name: 'Business Intelligence',
              description: 'Data analysis and business insights',
              status: 'Active',
              priority: 'High',
              health: 93,
              activeAgents: 5,
              totalActivities: 18,
              completedActivities: 14,
              pendingActivities: 4,
              teamSize: 7,
              budget: 175000,
              budgetUsed: 132000,
              kpis: [
                { name: 'Data Accuracy', value: 99, target: 98, unit: '%' },
                { name: 'Insight Generation', value: 87, target: 85, unit: '%' },
                { name: 'Report Timeliness', value: 95, target: 92, unit: '%' }
              ],
              recentActivity: [
                { type: 'analysis', title: 'Market Trend Analysis Completed', timestamp: new Date(Date.now() - 1800000).toISOString() },
                { type: 'report', title: 'Competitive Intelligence Report Generated', timestamp: new Date(Date.now() - 5400000).toISOString() },
                { type: 'update', title: 'Dashboard Metrics Refreshed', timestamp: new Date(Date.now() - 10800000).toISOString() }
              ],
              currentFocus: 'Predictive analytics and market intelligence gathering'
            }
          ],
          activities: [],
          performance: {},
          health: {}
        };
        setData(mockData);
      } finally {
        setLoading(false);
      }
    };

    loadDepartmentData();
    const interval = setInterval(loadDepartmentData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [departments]);

  const getHealthColor = (health) => {
    if (health >= 90) return '#48bb78';
    if (health >= 75) return '#4299e1';
    if (health >= 60) return '#ed8936';
    return '#e53e3e';
  };

  const getPriorityColor = (priority) => {
    switch (priority.toLowerCase()) {
      case 'high': return '#e53e3e';
      case 'medium': return '#ed8936';
      case 'low': return '#48bb78';
      default: return '#a0aec0';
    }
  };

  const getActivityTypeIcon = (type) => {
    const icons = {
      milestone: '🏆',
      update: '📝',
      alert: '⚠️',
      success: '✅',
      campaign: '📢',
      automation: '🤖',
      analysis: '📊',
      report: '📋',
      content: '📄'
    };
    return icons[type] || '📌';
  };

  const handleDepartmentClick = (department) => {
    setSelectedDepartment(department);
    if (onDepartmentClick) {
      onDepartmentClick(department);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatMetric = (value, unit) => {
    if (unit === '%') return `${value}%`;
    if (unit === 'hours') return `${value}h`;
    return `${value} ${unit}`;
  };

  if (loading) {
    return (
      <div className="department-status-board loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading department status...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="department-status-board error">
        <div className="error-message">
          <h3>Error Loading Department Data</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="department-status-board">
      {/* Header */}
      <div className="panel-header">
        <div className="header-content">
          <h2>Department Status Board</h2>
          <p>Monitor department activities, performance, and health metrics</p>
        </div>
        <div className="header-controls">
          <select 
            value={viewMode} 
            onChange={(e) => setViewMode(e.target.value)}
            className="view-mode-selector"
          >
            <option value="overview">Overview</option>
            <option value="activities">Activities</option>
            <option value="performance">Performance</option>
          </select>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="summary-stats">
        <div className="stat-card">
          <div className="stat-icon">🏢</div>
          <div className="stat-content">
            <h3>{data.departments.length}</h3>
            <p>Active Departments</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <h3>{data.departments.reduce((sum, dept) => sum + dept.activeAgents, 0)}</h3>
            <p>Active Agents</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <h3>{data.departments.reduce((sum, dept) => sum + dept.totalActivities, 0)}</h3>
            <p>Total Activities</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <h3>{Math.round(data.departments.reduce((sum, dept) => sum + dept.health, 0) / data.departments.length)}%</h3>
            <p>Avg Health</p>
          </div>
        </div>
      </div>

      {/* Department Grid */}
      <div className="departments-grid">
        {data.departments.map((department) => (
          <div 
            key={department.id} 
            className={`department-card ${selectedDepartment?.id === department.id ? 'selected' : ''}`}
            onClick={() => handleDepartmentClick(department)}
          >
            {/* Department Header */}
            <div className="department-header">
              <div className="department-info">
                <h3>{department.name}</h3>
                <p>{department.description}</p>
              </div>
              <div className="department-badges">
                <span 
                  className="priority-badge"
                  style={{ backgroundColor: getPriorityColor(department.priority) }}
                >
                  {department.priority}
                </span>
                <span className="status-badge active">
                  {department.status}
                </span>
              </div>
            </div>

            {/* Health Indicator */}
            <div className="health-section">
              <div className="health-header">
                <span className="health-label">Department Health</span>
                <span className="health-value">{department.health}%</span>
              </div>
              <div className="health-bar">
                <div 
                  className="health-fill"
                  style={{ 
                    width: `${department.health}%`,
                    backgroundColor: getHealthColor(department.health)
                  }}
                ></div>
              </div>
            </div>

            {/* Key Metrics */}
            <div className="metrics-section">
              <div className="metrics-grid">
                <div className="metric-item">
                  <span className="metric-label">Active Agents</span>
                  <span className="metric-value">{department.activeAgents}</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Team Size</span>
                  <span className="metric-value">{department.teamSize}</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Activities</span>
                  <span className="metric-value">{department.completedActivities}/{department.totalActivities}</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Budget Used</span>
                  <span className="metric-value">
                    {Math.round((department.budgetUsed / department.budget) * 100)}%
                  </span>
                </div>
              </div>
            </div>

            {/* Current Focus */}
            <div className="focus-section">
              <h4>Current Focus</h4>
              <p>{department.currentFocus}</p>
            </div>

            {/* KPIs */}
            {viewMode === 'performance' && (
              <div className="kpis-section">
                <h4>Key Performance Indicators</h4>
                <div className="kpis-list">
                  {department.kpis.map((kpi, index) => (
                    <div key={index} className="kpi-item">
                      <div className="kpi-header">
                        <span className="kpi-name">{kpi.name}</span>
                        <span className="kpi-values">
                          {formatMetric(kpi.value, kpi.unit)} / {formatMetric(kpi.target, kpi.unit)}
                        </span>
                      </div>
                      <div className="kpi-progress">
                        <div 
                          className="kpi-progress-bar"
                          style={{ 
                            width: `${Math.min((kpi.value / kpi.target) * 100, 100)}%`,
                            backgroundColor: (kpi.value / kpi.target) >= 1 ? '#48bb78' : 
                                            (kpi.value / kpi.target) >= 0.8 ? '#4299e1' : '#ed8936'
                          }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recent Activity */}
            {viewMode === 'activities' && (
              <div className="activity-section">
                <h4>Recent Activity</h4>
                <div className="activity-list">
                  {department.recentActivity.map((activity, index) => (
                    <div key={index} className="activity-item">
                      <div className="activity-icon">
                        {getActivityTypeIcon(activity.type)}
                      </div>
                      <div className="activity-content">
                        <div className="activity-title">{activity.title}</div>
                        <div className="activity-time">
                          {new Date(activity.timestamp).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Budget Progress */}
            {viewMode === 'overview' && (
              <div className="budget-section">
                <div className="budget-header">
                  <span className="budget-label">Budget Utilization</span>
                  <span className="budget-values">
                    {formatCurrency(department.budgetUsed)} / {formatCurrency(department.budget)}
                  </span>
                </div>
                <div className="budget-bar">
                  <div 
                    className="budget-fill"
                    style={{ 
                      width: `${(department.budgetUsed / department.budget) * 100}%`,
                      backgroundColor: (department.budgetUsed / department.budget) < 0.8 ? '#48bb78' : 
                                      (department.budgetUsed / department.budget) < 0.9 ? '#ed8936' : '#e53e3e'
                    }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Selected Department Details */}
      {selectedDepartment && (
        <div className="department-details-modal">
          <div className="modal-overlay" onClick={() => setSelectedDepartment(null)}></div>
          <div className="modal-content">
            <div className="modal-header">
              <h2>{selectedDepartment.name} - Detailed View</h2>
              <button 
                className="close-button"
                onClick={() => setSelectedDepartment(null)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="detail-sections">
                <div className="detail-section">
                  <h3>Department Overview</h3>
                  <div className="overview-grid">
                    <div className="overview-item">
                      <label>Description:</label>
                      <span>{selectedDepartment.description}</span>
                    </div>
                    <div className="overview-item">
                      <label>Status:</label>
                      <span className="status-badge">{selectedDepartment.status}</span>
                    </div>
                    <div className="overview-item">
                      <label>Priority:</label>
                      <span 
                        className="priority-badge"
                        style={{ backgroundColor: getPriorityColor(selectedDepartment.priority) }}
                      >
                        {selectedDepartment.priority}
                      </span>
                    </div>
                    <div className="overview-item">
                      <label>Health Score:</label>
                      <span style={{ color: getHealthColor(selectedDepartment.health) }}>
                        {selectedDepartment.health}%
                      </span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h3>Resource Allocation</h3>
                  <div className="resource-grid">
                    <div className="resource-item">
                      <label>Team Size:</label>
                      <span>{selectedDepartment.teamSize} members</span>
                    </div>
                    <div className="resource-item">
                      <label>Active Agents:</label>
                      <span>{selectedDepartment.activeAgents} agents</span>
                    </div>
                    <div className="resource-item">
                      <label>Total Budget:</label>
                      <span>{formatCurrency(selectedDepartment.budget)}</span>
                    </div>
                    <div className="resource-item">
                      <label>Budget Used:</label>
                      <span>{formatCurrency(selectedDepartment.budgetUsed)}</span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h3>Activity Summary</h3>
                  <div className="activity-summary">
                    <div className="activity-stat">
                      <span className="stat-value">{selectedDepartment.totalActivities}</span>
                      <span className="stat-label">Total Activities</span>
                    </div>
                    <div className="activity-stat">
                      <span className="stat-value completed">{selectedDepartment.completedActivities}</span>
                      <span className="stat-label">Completed</span>
                    </div>
                    <div className="activity-stat">
                      <span className="stat-value pending">{selectedDepartment.pendingActivities}</span>
                      <span className="stat-label">Pending</span>
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

export default DepartmentStatusBoard;
