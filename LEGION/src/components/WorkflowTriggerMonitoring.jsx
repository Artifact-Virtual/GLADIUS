import React, { useState, useEffect, useCallback } from 'react';

const WorkflowTriggerMonitoring = () => {
  const [triggers, setTriggers] = useState([]);
  const [triggerHistory, setTriggerHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTrigger, setSelectedTrigger] = useState(null);
  const [viewMode, setViewMode] = useState('active'); // active, history, analytics
  const [filters, setFilters] = useState({
    type: 'all',
    status: 'all',
    priority: 'all',
    source: 'all'
  });
  const [timeRange, setTimeRange] = useState('24h');
  const [refreshing, setRefreshing] = useState(false);
  const [analytics, setAnalytics] = useState({});

  const generateTriggers = useCallback(() => {
    const triggerTypes = ['schedule', 'event', 'webhook', 'manual', 'condition', 'api'];
    const statuses = ['active', 'inactive', 'pending', 'failed', 'disabled'];
    const priorities = ['critical', 'high', 'medium', 'low'];
    const sources = ['system', 'external-api', 'database', 'file-system', 'user', 'scheduler'];
    
    const triggerNames = [
      'Daily Sales Report Generation', 'Customer Data Sync', 'Inventory Level Check',
      'Payment Processing Webhook', 'Security Alert Monitor', 'Performance Metric Update',
      'Email Campaign Trigger', 'Database Backup Schedule', 'API Health Check',
      'User Activity Analysis', 'Market Data Refresh', 'Compliance Check Run',
      'Lead Scoring Update', 'Financial Close Process', 'Content Publication',
      'Integration Status Check', 'Quality Assurance Scan', 'Resource Optimization'
    ];

    return Array.from({ length: 18 }, (_, index) => ({
      id: `trigger-${index + 1}`,
      name: triggerNames[index] || `Trigger ${index + 1}`,
      type: triggerTypes[Math.floor(Math.random() * triggerTypes.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      priority: priorities[Math.floor(Math.random() * priorities.length)],
      source: sources[Math.floor(Math.random() * sources.length)],
      description: `Automated trigger for ${triggerNames[index] || 'workflow process'}`,
      schedule: index % 3 === 0 ? 'Every day at 9:00 AM' : index % 3 === 1 ? 'Every hour' : 'On demand',
      lastTriggered: new Date(Date.now() - Math.random() * 86400000).toISOString(),
      nextExecution: new Date(Date.now() + Math.random() * 86400000).toISOString(),
      executionCount: Math.floor(Math.random() * 1000) + 50,
      successRate: (Math.random() * 30 + 70).toFixed(1),
      avgExecutionTime: (Math.random() * 5000 + 500).toFixed(0),
      failureCount: Math.floor(Math.random() * 20),
      conditions: Array.from({ length: Math.floor(Math.random() * 4) + 1 }, () => 
        ['database_update', 'file_change', 'api_response', 'time_condition', 'metric_threshold'][Math.floor(Math.random() * 5)]
      ),
      associatedWorkflows: Array.from({ length: Math.floor(Math.random() * 3) + 1 }, () => 
        `workflow-${Math.floor(Math.random() * 20) + 1}`
      ),
      configuration: {
        retryAttempts: Math.floor(Math.random() * 5) + 1,
        timeout: Math.floor(Math.random() * 30000) + 5000,
        enabled: Math.random() > 0.2,
        webhookUrl: index % 4 === 0 ? `https://api.example.com/webhook/${index + 1}` : null,
        cronExpression: index % 3 === 0 ? '0 9 * * *' : index % 3 === 1 ? '0 * * * *' : null
      },
      monitoring: {
        healthStatus: ['healthy', 'warning', 'critical'][Math.floor(Math.random() * 3)],
        responseTime: Math.floor(Math.random() * 2000) + 100,
        errorRate: (Math.random() * 10).toFixed(2),
        availability: (Math.random() * 10 + 90).toFixed(1)
      },
      recentEvents: Array.from({ length: Math.floor(Math.random() * 8) + 2 }, (_, eventIndex) => ({
        timestamp: new Date(Date.now() - Math.random() * 86400000).toISOString(),
        type: ['success', 'failure', 'warning', 'info'][Math.floor(Math.random() * 4)],
        message: [
          'Trigger executed successfully',
          'Workflow initiated',
          'Condition met, executing action',
          'Timeout occurred during execution',
          'Retry attempt initiated'
        ][Math.floor(Math.random() * 5)],
        executionTime: Math.floor(Math.random() * 3000) + 200
      })),
      tags: Array.from({ length: Math.floor(Math.random() * 4) + 1 }, () => 
        ['production', 'automated', 'critical', 'monitoring', 'integration', 'scheduled'][Math.floor(Math.random() * 6)]
      ),
      owner: ['System Admin', 'Operations Team', 'Development Team', 'Business Analyst'][Math.floor(Math.random() * 4)],
      createdAt: new Date(Date.now() - Math.random() * 30 * 86400000).toISOString(),
      updatedAt: new Date(Date.now() - Math.random() * 7 * 86400000).toISOString()
    }));
  }, []);

  const generateTriggerHistory = useCallback(() => {
    return Array.from({ length: 50 }, (_, index) => ({
      id: `history-${index + 1}`,
      triggerId: `trigger-${Math.floor(Math.random() * 18) + 1}`,
      triggerName: `Trigger ${Math.floor(Math.random() * 18) + 1}`,
      executionTime: new Date(Date.now() - Math.random() * 7 * 86400000).toISOString(),
      status: ['success', 'failure', 'timeout', 'cancelled'][Math.floor(Math.random() * 4)],
      duration: Math.floor(Math.random() * 5000) + 200,
      workflowsTriggered: Math.floor(Math.random() * 5) + 1,
      result: 'Execution completed with expected results',
      errorMessage: Math.random() > 0.7 ? 'Connection timeout after 30 seconds' : null,
      metadata: {
        sourceIP: `192.168.1.${Math.floor(Math.random() * 254) + 1}`,
        userAgent: 'Enterprise-Workflow-Engine/1.0',
        requestId: `req-${Math.random().toString(36).substr(2, 9)}`
      }
    }));
  }, []);

  const generateAnalytics = useCallback(() => {
    return {
      totalTriggers: 18,
      activeTriggers: 14,
      failedTriggers: 2,
      avgSuccessRate: 87.3,
      executionsToday: 156,
      executionsThisWeek: 1247,
      topTriggers: [
        { name: 'Daily Sales Report', executions: 45, successRate: 98.2 },
        { name: 'Customer Data Sync', executions: 38, successRate: 94.7 },
        { name: 'Inventory Check', executions: 32, successRate: 89.1 }
      ],
      triggersByType: {
        schedule: 8,
        event: 4,
        webhook: 3,
        manual: 2,
        condition: 1
      },
      performanceMetrics: {
        avgResponseTime: 847,
        p95ResponseTime: 2340,
        errorRate: 2.7,
        availability: 99.2
      }
    };
  }, []);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        await new Promise(resolve => setTimeout(resolve, 1200));
        setTriggers(generateTriggers());
        setTriggerHistory(generateTriggerHistory());
        setAnalytics(generateAnalytics());
        setLoading(false);
      } catch (error) {
        setLoading(false);
        console.error('Error loading trigger data:', error);
      }
    };

    loadData();
  }, [generateTriggers, generateTriggerHistory, generateAnalytics]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setTriggers(generateTriggers());
      setTriggerHistory(generateTriggerHistory());
      setAnalytics(generateAnalytics());
    } catch (error) {
      console.error('Error refreshing data:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const filteredTriggers = triggers.filter(trigger => {
    return (filters.type === 'all' || trigger.type === filters.type) &&
           (filters.status === 'all' || trigger.status === filters.status) &&
           (filters.priority === 'all' || trigger.priority === filters.priority) &&
           (filters.source === 'all' || trigger.source === filters.source);
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return '#28a745';
      case 'inactive': return '#6c757d';
      case 'pending': return '#ffc107';
      case 'failed': return '#dc3545';
      case 'disabled': return '#e9ecef';
      default: return '#666';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical': return '#dc3545';
      case 'high': return '#fd7e14';
      case 'medium': return '#ffc107';
      case 'low': return '#28a745';
      default: return '#666';
    }
  };

  const getHealthColor = (health) => {
    switch (health) {
      case 'healthy': return '#28a745';
      case 'warning': return '#ffc107';
      case 'critical': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const renderActiveView = () => (
    <div className="triggers-grid">
      {filteredTriggers.map(trigger => (
        <div key={trigger.id} className="trigger-card">
          <div className="trigger-header">
            <div className="trigger-title">
              <h3>{trigger.name}</h3>
              <span className="trigger-type">{trigger.type}</span>
            </div>
            <div className="trigger-badges">
              <span className="status-badge" style={{backgroundColor: getStatusColor(trigger.status)}}>
                {trigger.status}
              </span>
              <span className="priority-badge" style={{backgroundColor: getPriorityColor(trigger.priority)}}>
                {trigger.priority}
              </span>
            </div>
          </div>

          <div className="trigger-description">
            <p>{trigger.description}</p>
          </div>

          <div className="trigger-schedule">
            <div className="schedule-info">
              <i className="fas fa-clock"></i>
              <span>{trigger.schedule}</span>
            </div>
            <div className="next-execution">
              Next: {new Date(trigger.nextExecution).toLocaleString()}
            </div>
          </div>

          <div className="trigger-metrics">
            <div className="metric-row">
              <div className="metric-item">
                <span className="metric-label">Executions:</span>
                <span className="metric-value">{trigger.executionCount}</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Success Rate:</span>
                <span className="metric-value">{trigger.successRate}%</span>
              </div>
            </div>
            <div className="metric-row">
              <div className="metric-item">
                <span className="metric-label">Avg Time:</span>
                <span className="metric-value">{trigger.avgExecutionTime}ms</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Failures:</span>
                <span className="metric-value">{trigger.failureCount}</span>
              </div>
            </div>
          </div>

          <div className="trigger-health">
            <div className="health-indicator">
              <div className="health-status" style={{backgroundColor: getHealthColor(trigger.monitoring.healthStatus)}}>
                <i className="fas fa-heartbeat"></i>
                <span>{trigger.monitoring.healthStatus}</span>
              </div>
              <div className="health-metrics">
                <span>RT: {trigger.monitoring.responseTime}ms</span>
                <span>Err: {trigger.monitoring.errorRate}%</span>
                <span>Up: {trigger.monitoring.availability}%</span>
              </div>
            </div>
          </div>

          <div className="trigger-conditions">
            <div className="conditions-label">Conditions:</div>
            <div className="conditions-tags">
              {trigger.conditions.map((condition, index) => (
                <span key={index} className="condition-tag">{condition}</span>
              ))}
            </div>
          </div>

          <div className="trigger-actions">
            <button className="action-btn test">
              <i className="fas fa-play"></i>
              Test
            </button>
            <button 
              className={`action-btn toggle ${trigger.configuration.enabled ? 'disable' : 'enable'}`}
            >
              <i className={`fas ${trigger.configuration.enabled ? 'fa-pause' : 'fa-play'}`}></i>
              {trigger.configuration.enabled ? 'Disable' : 'Enable'}
            </button>
            <button 
              className="action-btn details"
              onClick={() => setSelectedTrigger(trigger)}
            >
              <i className="fas fa-info-circle"></i>
              Details
            </button>
          </div>

          <div className="trigger-footer">
            <span className="last-triggered">
              Last: {new Date(trigger.lastTriggered).toLocaleString()}
            </span>
            <span className="owner">Owner: {trigger.owner}</span>
          </div>
        </div>
      ))}
    </div>
  );

  const renderHistoryView = () => (
    <div className="history-table">
      <div className="table-header">
        <div className="header-cell">Trigger</div>
        <div className="header-cell">Execution Time</div>
        <div className="header-cell">Status</div>
        <div className="header-cell">Duration</div>
        <div className="header-cell">Workflows</div>
        <div className="header-cell">Actions</div>
      </div>
      <div className="table-body">
        {triggerHistory.slice(0, 20).map(execution => (
          <div key={execution.id} className="table-row">
            <div className="table-cell">
              <strong>{execution.triggerName}</strong>
            </div>
            <div className="table-cell">
              <span>{new Date(execution.executionTime).toLocaleString()}</span>
            </div>
            <div className="table-cell">
              <span className={`execution-status ${execution.status}`}>
                {execution.status}
              </span>
            </div>
            <div className="table-cell">
              <span>{execution.duration}ms</span>
            </div>
            <div className="table-cell">
              <span>{execution.workflowsTriggered}</span>
            </div>
            <div className="table-cell">
              <button className="table-action-btn">
                <i className="fas fa-eye"></i>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderAnalyticsView = () => (
    <div className="analytics-dashboard">
      <div className="analytics-summary">
        <div className="summary-cards">
          <div className="summary-card">
            <div className="card-icon">
              <i className="fas fa-bolt"></i>
            </div>
            <div className="card-content">
              <h3>{analytics.totalTriggers}</h3>
              <p>Total Triggers</p>
            </div>
          </div>
          <div className="summary-card active">
            <div className="card-icon">
              <i className="fas fa-play-circle"></i>
            </div>
            <div className="card-content">
              <h3>{analytics.activeTriggers}</h3>
              <p>Active Triggers</p>
            </div>
          </div>
          <div className="summary-card failed">
            <div className="card-icon">
              <i className="fas fa-exclamation-triangle"></i>
            </div>
            <div className="card-content">
              <h3>{analytics.failedTriggers}</h3>
              <p>Failed Triggers</p>
            </div>
          </div>
          <div className="summary-card success">
            <div className="card-icon">
              <i className="fas fa-check-circle"></i>
            </div>
            <div className="card-content">
              <h3>{analytics.avgSuccessRate}%</h3>
              <p>Avg Success Rate</p>
            </div>
          </div>
        </div>
      </div>

      <div className="analytics-charts">
        <div className="chart-section">
          <h4>Top Performing Triggers</h4>
          <div className="top-triggers-list">
            {analytics.topTriggers && analytics.topTriggers.map((trigger, index) => (
              <div key={index} className="trigger-performance-item">
                <div className="performance-rank">#{index + 1}</div>
                <div className="performance-info">
                  <div className="performance-name">{trigger.name}</div>
                  <div className="performance-stats">
                    {trigger.executions} executions • {trigger.successRate}% success rate
                  </div>
                </div>
                <div className="performance-bar">
                  <div className="performance-fill" style={{width: `${trigger.successRate}%`}}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="chart-section">
          <h4>Triggers by Type</h4>
          <div className="type-distribution">
            {analytics.triggersByType && Object.entries(analytics.triggersByType).map(([type, count]) => (
              <div key={type} className="type-item">
                <span className="type-name">{type}</span>
                <span className="type-count">{count}</span>
                <div className="type-bar">
                  <div className="type-fill" style={{width: `${(count / analytics.totalTriggers) * 100}%`}}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="performance-metrics">
        <h4>Performance Metrics</h4>
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-label">Avg Response Time</div>
            <div className="metric-value">{analytics.performanceMetrics?.avgResponseTime}ms</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">P95 Response Time</div>
            <div className="metric-value">{analytics.performanceMetrics?.p95ResponseTime}ms</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Error Rate</div>
            <div className="metric-value">{analytics.performanceMetrics?.errorRate}%</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Availability</div>
            <div className="metric-value">{analytics.performanceMetrics?.availability}%</div>
          </div>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="workflow-trigger-monitoring loading">
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading trigger monitoring data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="workflow-trigger-monitoring">
      <div className="monitoring-header">
        <div className="header-left">
          <h2>Workflow Trigger Monitoring</h2>
          <p>Monitor and manage automated workflow triggers</p>
        </div>
        <div className="header-actions">
          <div className="view-toggle">
            <button 
              className={`view-btn ${viewMode === 'active' ? 'active' : ''}`}
              onClick={() => setViewMode('active')}
            >
              Active Triggers
            </button>
            <button 
              className={`view-btn ${viewMode === 'history' ? 'active' : ''}`}
              onClick={() => setViewMode('history')}
            >
              Execution History
            </button>
            <button 
              className={`view-btn ${viewMode === 'analytics' ? 'active' : ''}`}
              onClick={() => setViewMode('analytics')}
            >
              Analytics
            </button>
          </div>
          <button 
            className={`refresh-btn ${refreshing ? 'refreshing' : ''}`}
            onClick={handleRefresh}
          >
            <i className="fas fa-sync-alt"></i>
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {viewMode === 'active' && (
        <div className="monitoring-controls">
          <div className="filter-controls">
            <select value={filters.type} onChange={(e) => setFilters({...filters, type: e.target.value})}>
              <option value="all">All Types</option>
              <option value="schedule">Schedule</option>
              <option value="event">Event</option>
              <option value="webhook">Webhook</option>
              <option value="manual">Manual</option>
            </select>

            <select value={filters.status} onChange={(e) => setFilters({...filters, status: e.target.value})}>
              <option value="all">All Statuses</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="pending">Pending</option>
              <option value="failed">Failed</option>
            </select>

            <select value={filters.priority} onChange={(e) => setFilters({...filters, priority: e.target.value})}>
              <option value="all">All Priorities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>
      )}

      <div className="monitoring-content">
        {viewMode === 'active' && renderActiveView()}
        {viewMode === 'history' && renderHistoryView()}
        {viewMode === 'analytics' && renderAnalyticsView()}
      </div>

      {selectedTrigger && (
        <div className="modal-overlay" onClick={() => setSelectedTrigger(null)}>
          <div className="trigger-detail-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{selectedTrigger.name}</h3>
              <button className="close-btn" onClick={() => setSelectedTrigger(null)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-content">
              <div className="detail-section">
                <h4>Configuration</h4>
                <div className="config-grid">
                  <div className="config-item">
                    <span className="label">Type:</span>
                    <span className="value">{selectedTrigger.type}</span>
                  </div>
                  <div className="config-item">
                    <span className="label">Schedule:</span>
                    <span className="value">{selectedTrigger.schedule}</span>
                  </div>
                  <div className="config-item">
                    <span className="label">Retry Attempts:</span>
                    <span className="value">{selectedTrigger.configuration.retryAttempts}</span>
                  </div>
                  <div className="config-item">
                    <span className="label">Timeout:</span>
                    <span className="value">{selectedTrigger.configuration.timeout}ms</span>
                  </div>
                </div>
              </div>

              <div className="detail-section">
                <h4>Recent Events</h4>
                <div className="events-container">
                  {selectedTrigger.recentEvents.slice(0, 5).map((event, index) => (
                    <div key={index} className={`event-entry ${event.type}`}>
                      <span className="event-time">{new Date(event.timestamp).toLocaleString()}</span>
                      <span className="event-type">{event.type}</span>
                      <span className="event-message">{event.message}</span>
                      <span className="event-duration">{event.executionTime}ms</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkflowTriggerMonitoring;
