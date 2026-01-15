import React, { useState, useEffect, useCallback } from 'react';

const ActiveWorkflowDisplay = () => {
  const [activeWorkflows, setActiveWorkflows] = useState([]);
  const [workflowDetails, setWorkflowDetails] = useState({});
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [filters, setFilters] = useState({
    priority: 'all',
    type: 'all',
    status: 'all',
    owner: 'all'
  });
  const [sortBy, setSortBy] = useState('priority');
  const [viewMode, setViewMode] = useState('cards'); // cards, table, timeline

  const generateActiveWorkflows = useCallback(() => {
    const workflowTypes = ['business-process', 'data-pipeline', 'automation', 'integration', 'analysis', 'reporting'];
    const activeStatuses = ['running', 'queued', 'paused', 'starting'];
    const priorities = ['critical', 'high', 'medium', 'low'];
    const owners = ['John Smith', 'Sarah Johnson', 'Mike Chen', 'Emily Davis', 'Alex Rodriguez'];
    
    const workflowNames = [
      'Customer Onboarding Process', 'Lead Qualification Pipeline', 'Financial Reporting Automation',
      'Market Research Analysis', 'Content Creation Workflow', 'Sales Performance Review',
      'Compliance Audit Process', 'Strategic Planning Pipeline', 'Employee Performance Review',
      'Product Launch Coordination', 'Customer Support Escalation', 'Revenue Recognition Process',
      'Marketing Campaign Automation', 'Risk Assessment Pipeline', 'Data Quality Management',
      'Customer Feedback Analysis', 'Inventory Management Process', 'Security Compliance Check'
    ];

    return Array.from({ length: 18 }, (_, index) => ({
      id: `active-workflow-${index + 1}`,
      name: workflowNames[index] || `Active Workflow ${index + 1}`,
      type: workflowTypes[Math.floor(Math.random() * workflowTypes.length)],
      status: activeStatuses[Math.floor(Math.random() * activeStatuses.length)],
      priority: priorities[Math.floor(Math.random() * priorities.length)],
      owner: owners[Math.floor(Math.random() * owners.length)],
      department: ['marketing', 'sales', 'finance', 'operations', 'research', 'strategy'][Math.floor(Math.random() * 6)],
      startedAt: new Date(Date.now() - Math.random() * 86400000).toISOString(),
      estimatedCompletion: new Date(Date.now() + Math.random() * 86400000).toISOString(),
      progress: Math.floor(Math.random() * 100),
      currentStep: Math.floor(Math.random() * 10) + 1,
      totalSteps: Math.floor(Math.random() * 15) + 5,
      executionTime: Math.floor(Math.random() * 3600) + 300, // seconds
      resourceUsage: {
        cpu: Math.floor(Math.random() * 80) + 10,
        memory: Math.floor(Math.random() * 70) + 20,
        network: Math.floor(Math.random() * 60) + 5
      },
      assignedAgents: Array.from({ length: Math.floor(Math.random() * 5) + 1 }, () => 
        `agent-${Math.floor(Math.random() * 20) + 1}`
      ),
      logs: Array.from({ length: Math.floor(Math.random() * 10) + 5 }, (_, logIndex) => ({
        timestamp: new Date(Date.now() - Math.random() * 3600000).toISOString(),
        level: ['INFO', 'WARN', 'ERROR', 'DEBUG'][Math.floor(Math.random() * 4)],
        message: `Step ${logIndex + 1} execution status update`,
        component: ['workflow-engine', 'agent-coordinator', 'data-processor'][Math.floor(Math.random() * 3)]
      })),
      metrics: {
        throughput: (Math.random() * 100 + 10).toFixed(0) + '/min',
        errorRate: (Math.random() * 5).toFixed(2) + '%',
        responseTime: (Math.random() * 1000 + 100).toFixed(0) + 'ms',
        successRate: (Math.random() * 30 + 70).toFixed(1) + '%'
      },
      dependencies: Array.from({ length: Math.floor(Math.random() * 3) }, () => 
        `workflow-${Math.floor(Math.random() * 10) + 1}`
      ),
      nextActions: [
        'Data validation in progress',
        'Waiting for agent response',
        'Processing user input',
        'Executing business rules',
        'Generating report'
      ].slice(0, Math.floor(Math.random() * 3) + 1),
      alerts: Math.floor(Math.random() * 5),
      warnings: Math.floor(Math.random() * 3),
      lastActivity: new Date(Date.now() - Math.random() * 60000).toISOString(),
      healthScore: Math.floor(Math.random() * 40) + 60,
      environment: ['production', 'staging', 'development'][Math.floor(Math.random() * 3)],
      version: `v${Math.floor(Math.random() * 5) + 1}.${Math.floor(Math.random() * 10)}`
    }));
  }, []);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        await new Promise(resolve => setTimeout(resolve, 1000));
        setActiveWorkflows(generateActiveWorkflows());
        setLoading(false);
      } catch (error) {
        setLoading(false);
        console.error('Error loading active workflows:', error);
      }
    };

    loadData();
  }, [generateActiveWorkflows]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 800));
      setActiveWorkflows(generateActiveWorkflows());
    } catch (error) {
      console.error('Error refreshing workflows:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const filteredWorkflows = activeWorkflows.filter(workflow => {
    return (filters.priority === 'all' || workflow.priority === filters.priority) &&
           (filters.type === 'all' || workflow.type === filters.type) &&
           (filters.status === 'all' || workflow.status === filters.status) &&
           (filters.owner === 'all' || workflow.owner === filters.owner);
  });

  const sortedWorkflows = [...filteredWorkflows].sort((a, b) => {
    switch (sortBy) {
      case 'priority':
        const priorityOrder = { critical: 4, high: 3, medium: 2, low: 1 };
        return priorityOrder[b.priority] - priorityOrder[a.priority];
      case 'progress':
        return b.progress - a.progress;
      case 'startTime':
        return new Date(b.startedAt) - new Date(a.startedAt);
      case 'name':
        return a.name.localeCompare(b.name);
      default:
        return 0;
    }
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return '#28a745';
      case 'queued': return '#6c757d';
      case 'paused': return '#ffc107';
      case 'starting': return '#17a2b8';
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

  const renderCardView = () => (
    <div className="workflows-grid">
      {sortedWorkflows.map(workflow => (
        <div key={workflow.id} className="active-workflow-card">
          <div className="workflow-header">
            <div className="workflow-title">
              <h3>{workflow.name}</h3>
              <span className="workflow-version">{workflow.version}</span>
            </div>
            <div className="workflow-badges">
              <span className="status-badge" style={{backgroundColor: getStatusColor(workflow.status)}}>
                {workflow.status}
              </span>
              <span className="priority-badge" style={{backgroundColor: getPriorityColor(workflow.priority)}}>
                {workflow.priority}
              </span>
            </div>
          </div>

          <div className="workflow-meta">
            <span className="workflow-type">{workflow.type}</span>
            <span className="workflow-owner">{workflow.owner}</span>
            <span className="workflow-department">{workflow.department}</span>
          </div>

          <div className="workflow-progress">
            <div className="progress-info">
              <span className="progress-label">Progress: {workflow.progress}%</span>
              <span className="step-info">{workflow.currentStep}/{workflow.totalSteps} steps</span>
            </div>
            <div className="progress-bar">
              <div className="progress-fill" style={{width: `${workflow.progress}%`}}></div>
            </div>
          </div>

          <div className="workflow-metrics">
            <div className="metric-item">
              <span className="metric-label">Health:</span>
              <span className="metric-value">{workflow.healthScore}%</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Runtime:</span>
              <span className="metric-value">{Math.floor(workflow.executionTime / 60)}m</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Agents:</span>
              <span className="metric-value">{workflow.assignedAgents.length}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Alerts:</span>
              <span className="metric-value">{workflow.alerts}</span>
            </div>
          </div>

          <div className="workflow-resources">
            <div className="resource-usage">
              <div className="resource-item">
                <span className="resource-label">CPU:</span>
                <div className="resource-bar">
                  <div className="resource-fill" style={{width: `${workflow.resourceUsage.cpu}%`}}></div>
                </div>
                <span className="resource-value">{workflow.resourceUsage.cpu}%</span>
              </div>
              <div className="resource-item">
                <span className="resource-label">Memory:</span>
                <div className="resource-bar">
                  <div className="resource-fill" style={{width: `${workflow.resourceUsage.memory}%`}}></div>
                </div>
                <span className="resource-value">{workflow.resourceUsage.memory}%</span>
              </div>
            </div>
          </div>

          <div className="workflow-actions">
            <button className="action-btn pause">
              <i className="fas fa-pause"></i>
              Pause
            </button>
            <button className="action-btn stop">
              <i className="fas fa-stop"></i>
              Stop
            </button>
            <button 
              className="action-btn details"
              onClick={() => setSelectedWorkflow(workflow)}
            >
              <i className="fas fa-info-circle"></i>
              Details
            </button>
          </div>

          <div className="workflow-footer">
            <span className="last-activity">
              Last activity: {new Date(workflow.lastActivity).toLocaleTimeString()}
            </span>
            <span className="next-completion">
              ETC: {new Date(workflow.estimatedCompletion).toLocaleTimeString()}
            </span>
          </div>
        </div>
      ))}
    </div>
  );

  const renderTableView = () => (
    <div className="workflows-table">
      <div className="table-header">
        <div className="header-cell">Name</div>
        <div className="header-cell">Status</div>
        <div className="header-cell">Priority</div>
        <div className="header-cell">Progress</div>
        <div className="header-cell">Health</div>
        <div className="header-cell">Runtime</div>
        <div className="header-cell">Actions</div>
      </div>
      <div className="table-body">
        {sortedWorkflows.map(workflow => (
          <div key={workflow.id} className="table-row">
            <div className="table-cell">
              <div className="workflow-info">
                <strong>{workflow.name}</strong>
                <small>{workflow.type} - {workflow.owner}</small>
              </div>
            </div>
            <div className="table-cell">
              <span className="status-indicator" style={{backgroundColor: getStatusColor(workflow.status)}}>
                {workflow.status}
              </span>
            </div>
            <div className="table-cell">
              <span className="priority-indicator" style={{backgroundColor: getPriorityColor(workflow.priority)}}>
                {workflow.priority}
              </span>
            </div>
            <div className="table-cell">
              <div className="progress-mini">
                <div className="progress-bar-mini">
                  <div className="progress-fill-mini" style={{width: `${workflow.progress}%`}}></div>
                </div>
                <span>{workflow.progress}%</span>
              </div>
            </div>
            <div className="table-cell">
              <span className="health-score">{workflow.healthScore}%</span>
            </div>
            <div className="table-cell">
              <span>{Math.floor(workflow.executionTime / 60)}m {workflow.executionTime % 60}s</span>
            </div>
            <div className="table-cell">
              <div className="table-actions">
                <button className="table-action-btn pause">
                  <i className="fas fa-pause"></i>
                </button>
                <button className="table-action-btn stop">
                  <i className="fas fa-stop"></i>
                </button>
                <button 
                  className="table-action-btn details"
                  onClick={() => setSelectedWorkflow(workflow)}
                >
                  <i className="fas fa-info-circle"></i>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderTimelineView = () => (
    <div className="workflows-timeline">
      {sortedWorkflows.map(workflow => (
        <div key={workflow.id} className="timeline-item">
          <div className="timeline-marker" style={{backgroundColor: getStatusColor(workflow.status)}}></div>
          <div className="timeline-content">
            <div className="timeline-header">
              <h4>{workflow.name}</h4>
              <span className="timeline-time">{new Date(workflow.startedAt).toLocaleString()}</span>
            </div>
            <div className="timeline-details">
              <span className="timeline-type">{workflow.type}</span>
              <span className="timeline-progress">{workflow.progress}% complete</span>
              <span className="timeline-health">Health: {workflow.healthScore}%</span>
            </div>
            <div className="timeline-status">
              <span className="status-badge" style={{backgroundColor: getStatusColor(workflow.status)}}>
                {workflow.status}
              </span>
              <span className="priority-badge" style={{backgroundColor: getPriorityColor(workflow.priority)}}>
                {workflow.priority}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  if (loading) {
    return (
      <div className="active-workflow-display loading">
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading active workflows...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="active-workflow-display">
      <div className="display-header">
        <div className="header-left">
          <h2>Active Workflows</h2>
          <p>{sortedWorkflows.length} workflows currently running</p>
        </div>
        <div className="header-actions">
          <div className="view-mode-toggle">
            <button 
              className={`view-btn ${viewMode === 'cards' ? 'active' : ''}`}
              onClick={() => setViewMode('cards')}
            >
              <i className="fas fa-th-large"></i>
            </button>
            <button 
              className={`view-btn ${viewMode === 'table' ? 'active' : ''}`}
              onClick={() => setViewMode('table')}
            >
              <i className="fas fa-table"></i>
            </button>
            <button 
              className={`view-btn ${viewMode === 'timeline' ? 'active' : ''}`}
              onClick={() => setViewMode('timeline')}
            >
              <i className="fas fa-stream"></i>
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

      <div className="display-controls">
        <div className="filter-controls">
          <select value={filters.status} onChange={(e) => setFilters({...filters, status: e.target.value})}>
            <option value="all">All Statuses</option>
            <option value="running">Running</option>
            <option value="queued">Queued</option>
            <option value="paused">Paused</option>
            <option value="starting">Starting</option>
          </select>

          <select value={filters.priority} onChange={(e) => setFilters({...filters, priority: e.target.value})}>
            <option value="all">All Priorities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          <select value={filters.type} onChange={(e) => setFilters({...filters, type: e.target.value})}>
            <option value="all">All Types</option>
            <option value="business-process">Business Process</option>
            <option value="data-pipeline">Data Pipeline</option>
            <option value="automation">Automation</option>
            <option value="integration">Integration</option>
          </select>

          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="priority">Sort by Priority</option>
            <option value="progress">Sort by Progress</option>
            <option value="startTime">Sort by Start Time</option>
            <option value="name">Sort by Name</option>
          </select>
        </div>
      </div>

      <div className="display-content">
        {viewMode === 'cards' && renderCardView()}
        {viewMode === 'table' && renderTableView()}
        {viewMode === 'timeline' && renderTimelineView()}
      </div>

      {selectedWorkflow && (
        <div className="modal-overlay" onClick={() => setSelectedWorkflow(null)}>
          <div className="workflow-detail-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{selectedWorkflow.name}</h3>
              <button className="close-btn" onClick={() => setSelectedWorkflow(null)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-content">
              <div className="detail-section">
                <h4>Current Status</h4>
                <div className="status-grid">
                  <div className="status-item">
                    <span className="label">Status:</span>
                    <span className="value" style={{color: getStatusColor(selectedWorkflow.status)}}>
                      {selectedWorkflow.status}
                    </span>
                  </div>
                  <div className="status-item">
                    <span className="label">Progress:</span>
                    <span className="value">{selectedWorkflow.progress}%</span>
                  </div>
                  <div className="status-item">
                    <span className="label">Health Score:</span>
                    <span className="value">{selectedWorkflow.healthScore}%</span>
                  </div>
                  <div className="status-item">
                    <span className="label">Runtime:</span>
                    <span className="value">{Math.floor(selectedWorkflow.executionTime / 60)}m</span>
                  </div>
                </div>
              </div>

              <div className="detail-section">
                <h4>Next Actions</h4>
                <ul className="actions-list">
                  {selectedWorkflow.nextActions.map((action, index) => (
                    <li key={index}>{action}</li>
                  ))}
                </ul>
              </div>

              <div className="detail-section">
                <h4>Recent Logs</h4>
                <div className="logs-container">
                  {selectedWorkflow.logs.slice(0, 5).map((log, index) => (
                    <div key={index} className={`log-entry ${log.level.toLowerCase()}`}>
                      <span className="log-time">{new Date(log.timestamp).toLocaleTimeString()}</span>
                      <span className="log-level">{log.level}</span>
                      <span className="log-message">{log.message}</span>
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

export default ActiveWorkflowDisplay;
