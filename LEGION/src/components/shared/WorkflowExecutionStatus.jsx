import React, { useState, useEffect } from 'react';

/**
 * WorkflowExecutionStatus - Real-time workflow monitoring and execution tracking
 * 
 * Displays active workflows, execution history, and provides workflow control capabilities
 * for the enterprise agent orchestration system.
 */
const WorkflowExecutionStatus = ({ 
  workflows = [], 
  executionHistory = [], 
  emergencyMode = false 
}) => {
  const [activeTab, setActiveTab] = useState('active'); // 'active', 'history', 'analytics'
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all'); // 'all', 'running', 'completed', 'failed', 'paused'
  const [timeRange, setTimeRange] = useState('24h'); // '1h', '24h', '7d', '30d'

  // Filter workflows based on status
  const getFilteredWorkflows = () => {
    const workflowList = activeTab === 'active' ? workflows : executionHistory;
    if (filterStatus === 'all') return workflowList;
    return workflowList.filter(workflow => workflow.status === filterStatus);
  };

  // Get workflow status information
  const getWorkflowStatusInfo = (workflow) => {
    const { status, progress = 0, errors = [] } = workflow;
    
    switch (status) {
      case 'running':
        return { 
          color: 'running', 
          icon: '🔄', 
          text: 'RUNNING',
          bgColor: 'rgba(23, 162, 184, 0.1)' 
        };
      case 'completed':
        return { 
          color: 'completed', 
          icon: '✅', 
          text: 'COMPLETED',
          bgColor: 'rgba(40, 167, 69, 0.1)' 
        };
      case 'failed':
        return { 
          color: 'failed', 
          icon: '❌', 
          text: 'FAILED',
          bgColor: 'rgba(220, 53, 69, 0.1)' 
        };
      case 'paused':
        return { 
          color: 'paused', 
          icon: '⏸️', 
          text: 'PAUSED',
          bgColor: 'rgba(255, 193, 7, 0.1)' 
        };
      case 'pending':
        return { 
          color: 'pending', 
          icon: '⏳', 
          text: 'PENDING',
          bgColor: 'rgba(108, 117, 125, 0.1)' 
        };
      default:
        return { 
          color: 'unknown', 
          icon: '❓', 
          text: 'UNKNOWN',
          bgColor: 'rgba(108, 117, 125, 0.1)' 
        };
    }
  };

  // Calculate workflow priority
  const getWorkflowPriority = (workflow) => {
    const { priority = 5, businessImpact = 'medium' } = workflow;
    
    if (priority >= 8 || businessImpact === 'critical') return 'critical';
    if (priority >= 6 || businessImpact === 'high') return 'high';
    if (priority >= 4 || businessImpact === 'medium') return 'medium';
    return 'low';
  };

  // Format duration
  const formatDuration = (seconds) => {
    if (!seconds) return '0s';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) return `${hours}h ${minutes}m`;
    if (minutes > 0) return `${minutes}m ${secs}s`;
    return `${secs}s`;
  };

  // Calculate workflow metrics
  const calculateMetrics = () => {
    const total = workflows.length;
    const running = workflows.filter(w => w.status === 'running').length;
    const completed = workflows.filter(w => w.status === 'completed').length;
    const failed = workflows.filter(w => w.status === 'failed').length;
    const avgDuration = executionHistory.length > 0 
      ? executionHistory.reduce((sum, w) => sum + (w.duration || 0), 0) / executionHistory.length 
      : 0;
    
    return { total, running, completed, failed, avgDuration };
  };

  const metrics = calculateMetrics();

  return (
    <div className={`workflow-execution-status ${emergencyMode ? 'emergency' : ''}`}>
      <div className="workflow-header">
        <div className="header-left">
          <h3 className="workflow-title">
            <span className="title-icon">⚡</span>
            Workflow Execution
          </h3>
          <div className="workflow-metrics">
            <div className="metric-item">
              <span className="metric-value">{metrics.total}</span>
              <span className="metric-label">Total</span>
            </div>
            <div className="metric-item running">
              <span className="metric-value">{metrics.running}</span>
              <span className="metric-label">Running</span>
            </div>
            <div className="metric-item completed">
              <span className="metric-value">{metrics.completed}</span>
              <span className="metric-label">Completed</span>
            </div>
            <div className="metric-item failed">
              <span className="metric-value">{metrics.failed}</span>
              <span className="metric-label">Failed</span>
            </div>
          </div>
        </div>
        
        <div className="header-controls">
          <div className="tab-controls">
            <button 
              className={`tab-btn ${activeTab === 'active' ? 'active' : ''}`}
              onClick={() => setActiveTab('active')}
            >
              Active ({workflows.length})
            </button>
            <button 
              className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
              onClick={() => setActiveTab('history')}
            >
              History ({executionHistory.length})
            </button>
            <button 
              className={`tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
              onClick={() => setActiveTab('analytics')}
            >
              Analytics
            </button>
          </div>
          
          <div className="filter-controls">
            <select 
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="status-filter"
            >
              <option value="all">All Status</option>
              <option value="running">Running</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
              <option value="paused">Paused</option>
            </select>
            
            {activeTab === 'history' && (
              <select 
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="time-filter"
              >
                <option value="1h">Last Hour</option>
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
              </select>
            )}
          </div>
        </div>
      </div>

      {/* Active Workflows Tab */}
      {activeTab === 'active' && (
        <div className="workflows-container">
          {getFilteredWorkflows().length === 0 ? (
            <div className="empty-state">
              <span className="empty-icon">🔄</span>
              <h4>No Active Workflows</h4>
              <p>All workflows are currently idle or completed.</p>
            </div>
          ) : (
            <div className="workflows-grid">
              {getFilteredWorkflows().map((workflow, index) => {
                const statusInfo = getWorkflowStatusInfo(workflow);
                const priority = getWorkflowPriority(workflow);
                
                return (
                  <div 
                    key={workflow.id || index}
                    className={`workflow-card ${statusInfo.color} ${priority}-priority ${selectedWorkflow?.id === workflow.id ? 'selected' : ''}`}
                    onClick={() => setSelectedWorkflow(workflow)}
                    style={{ background: statusInfo.bgColor }}
                  >
                    <div className="workflow-card-header">
                      <div className="workflow-status">
                        <span className="status-icon">{statusInfo.icon}</span>
                        <span className="status-text">{statusInfo.text}</span>
                      </div>
                      <div className={`priority-badge ${priority}`}>
                        {priority.toUpperCase()}
                      </div>
                    </div>
                    
                    <div className="workflow-info">
                      <h4 className="workflow-name">{workflow.name}</h4>
                      <p className="workflow-description">{workflow.description}</p>
                      
                      <div className="workflow-details">
                        <div className="detail-item">
                          <span className="detail-label">Trigger:</span>
                          <span className="detail-value">{workflow.trigger}</span>
                        </div>
                        <div className="detail-item">
                          <span className="detail-label">Duration:</span>
                          <span className="detail-value">{formatDuration(workflow.duration || 0)}</span>
                        </div>
                        <div className="detail-item">
                          <span className="detail-label">Agents:</span>
                          <span className="detail-value">{workflow.agents?.length || 0}</span>
                        </div>
                      </div>
                      
                      {workflow.status === 'running' && (
                        <div className="progress-section">
                          <div className="progress-header">
                            <span className="progress-label">Progress</span>
                            <span className="progress-percentage">{workflow.progress || 0}%</span>
                          </div>
                          <div className="progress-bar">
                            <div 
                              className="progress-fill"
                              style={{ width: `${workflow.progress || 0}%` }}
                            ></div>
                          </div>
                          {workflow.currentStep && (
                            <div className="current-step">
                              Current: {workflow.currentStep}
                            </div>
                          )}
                        </div>
                      )}
                      
                      {workflow.errors && workflow.errors.length > 0 && (
                        <div className="errors-section">
                          <span className="errors-count">
                            ⚠️ {workflow.errors.length} Error{workflow.errors.length !== 1 ? 's' : ''}
                          </span>
                        </div>
                      )}
                    </div>
                    
                    <div className="workflow-actions">
                      {workflow.status === 'running' && (
                        <>
                          <button className="action-btn pause">⏸️ Pause</button>
                          <button className="action-btn stop">🛑 Stop</button>
                        </>
                      )}
                      {workflow.status === 'paused' && (
                        <button className="action-btn resume">▶️ Resume</button>
                      )}
                      {workflow.status === 'failed' && (
                        <button className="action-btn retry">🔄 Retry</button>
                      )}
                      <button className="action-btn details">📋 Details</button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* History Tab */}
      {activeTab === 'history' && (
        <div className="history-container">
          <div className="history-header">
            <h4>Execution History - {timeRange.toUpperCase()}</h4>
            <div className="history-stats">
              <span>Total: {executionHistory.length}</span>
              <span>•</span>
              <span>Avg Duration: {formatDuration(metrics.avgDuration)}</span>
              <span>•</span>
              <span>Success Rate: {executionHistory.length > 0 ? 
                ((executionHistory.filter(w => w.status === 'completed').length / executionHistory.length) * 100).toFixed(1) 
                : 0}%</span>
            </div>
          </div>
          
          <div className="history-list">
            {getFilteredWorkflows().map((workflow, index) => {
              const statusInfo = getWorkflowStatusInfo(workflow);
              
              return (
                <div 
                  key={workflow.id || index}
                  className={`history-item ${statusInfo.color}`}
                  onClick={() => setSelectedWorkflow(workflow)}
                >
                  <div className="history-status">
                    <span className="status-icon">{statusInfo.icon}</span>
                  </div>
                  
                  <div className="history-info">
                    <div className="history-main">
                      <h5 className="history-name">{workflow.name}</h5>
                      <span className="history-time">
                        {new Date(workflow.startedAt).toLocaleString()}
                      </span>
                    </div>
                    <div className="history-details">
                      <span>Duration: {formatDuration(workflow.duration || 0)}</span>
                      <span>•</span>
                      <span>Trigger: {workflow.trigger}</span>
                      <span>•</span>
                      <span>Agents: {workflow.agents?.length || 0}</span>
                    </div>
                  </div>
                  
                  <div className="history-metrics">
                    <div className="metric-badge">
                      {statusInfo.text}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && (
        <div className="analytics-container">
          <div className="analytics-grid">
            <div className="analytics-card">
              <h4>Execution Trends</h4>
              <div className="trend-chart">
                <div className="chart-placeholder">
                  📊 Execution trends chart would go here
                </div>
              </div>
            </div>
            
            <div className="analytics-card">
              <h4>Performance Metrics</h4>
              <div className="metrics-list">
                <div className="metric-row">
                  <span className="metric-name">Average Duration</span>
                  <span className="metric-value">{formatDuration(metrics.avgDuration)}</span>
                </div>
                <div className="metric-row">
                  <span className="metric-name">Success Rate</span>
                  <span className="metric-value">
                    {executionHistory.length > 0 ? 
                      ((executionHistory.filter(w => w.status === 'completed').length / executionHistory.length) * 100).toFixed(1) 
                      : 0}%
                  </span>
                </div>
                <div className="metric-row">
                  <span className="metric-name">Total Executions</span>
                  <span className="metric-value">{executionHistory.length}</span>
                </div>
                <div className="metric-row">
                  <span className="metric-name">Active Workflows</span>
                  <span className="metric-value">{metrics.running}</span>
                </div>
              </div>
            </div>
            
            <div className="analytics-card">
              <h4>Popular Triggers</h4>
              <div className="triggers-list">
                {['revenue_milestone', 'lead_qualification', 'daily_operations', 'compliance_alert'].map(trigger => (
                  <div key={trigger} className="trigger-item">
                    <span className="trigger-name">{trigger}</span>
                    <span className="trigger-count">
                      {executionHistory.filter(w => w.trigger === trigger).length}
                    </span>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="analytics-card">
              <h4>Agent Utilization</h4>
              <div className="utilization-chart">
                <div className="chart-placeholder">
                  🤖 Agent utilization chart would go here
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Real-time indicator */}
      <div className="workflow-realtime-indicator">
        <span className="indicator-dot"></span>
        <span className="indicator-text">Live Workflow Monitoring</span>
      </div>
    </div>
  );
};

export default WorkflowExecutionStatus;
