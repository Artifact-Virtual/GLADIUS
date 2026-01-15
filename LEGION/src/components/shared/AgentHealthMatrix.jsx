import React, { useState, useEffect } from 'react';

/**
 * AgentHealthMatrix - Visual matrix of all enterprise agents and their health status
 * 
 * Provides real-time monitoring of 32+ agents across 8 business domains
 * with interactive drill-down capabilities and performance metrics.
 */
const AgentHealthMatrix = ({ agents = [], overallHealth = 0, emergencyMode = false }) => {
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // 'grid', 'list', 'departments'
  const [filterStatus, setFilterStatus] = useState('all'); // 'all', 'healthy', 'warning', 'critical'

  // Group agents by department
  const agentsByDepartment = agents.reduce((acc, agent) => {
    const dept = agent.department || 'Unknown';
    if (!acc[dept]) acc[dept] = [];
    acc[dept].push(agent);
    return acc;
  }, {});

  // Filter agents based on status filter
  const getFilteredAgents = () => {
    if (filterStatus === 'all') return agents;
    return agents.filter(agent => agent.status === filterStatus);
  };

  // Get agent status color and icon
  const getAgentStatusInfo = (agent) => {
    const { status, responseTime, errorRate } = agent;
    
    if (status === 'offline' || status === 'error') {
      return { color: 'critical', icon: '🔴', text: 'OFFLINE' };
    }
    
    if (status === 'degraded' || errorRate > 10 || responseTime > 2000) {
      return { color: 'warning', icon: '🟡', text: 'WARNING' };
    }
    
    if (status === 'healthy' || status === 'online') {
      return { color: 'healthy', icon: '🟢', text: 'HEALTHY' };
    }
    
    return { color: 'unknown', icon: '⚪', text: 'UNKNOWN' };
  };

  // Calculate department health
  const getDepartmentHealth = (deptAgents) => {
    if (!deptAgents.length) return 'unknown';
    
    const healthyCount = deptAgents.filter(agent => 
      getAgentStatusInfo(agent).color === 'healthy'
    ).length;
    
    const warningCount = deptAgents.filter(agent => 
      getAgentStatusInfo(agent).color === 'warning'
    ).length;
    
    const criticalCount = deptAgents.filter(agent => 
      getAgentStatusInfo(agent).color === 'critical'
    ).length;
    
    if (criticalCount > 0) return 'critical';
    if (warningCount > healthyCount * 0.3) return 'warning';
    if (healthyCount / deptAgents.length > 0.8) return 'excellent';
    return 'healthy';
  };

  // Agent performance score calculation
  const calculatePerformanceScore = (agent) => {
    const { responseTime = 0, uptime = 0, errorRate = 0, taskCompletion = 0 } = agent.metrics || {};
    
    const responseScore = Math.max(0, 100 - (responseTime / 20)); // 2000ms = 0 score
    const uptimeScore = uptime;
    const errorScore = Math.max(0, 100 - (errorRate * 5));
    const completionScore = taskCompletion;
    
    return Math.round((responseScore + uptimeScore + errorScore + completionScore) / 4);
  };

  return (
    <div className={`agent-health-matrix ${emergencyMode ? 'emergency' : ''}`}>
      <div className="matrix-header">
        <div className="header-left">
          <h3 className="matrix-title">
            <span className="title-icon">🤖</span>
            Agent Health Matrix
          </h3>
          <div className="overall-health">
            <span className="health-label">Overall Health:</span>
            <div className={`health-score ${overallHealth > 80 ? 'excellent' : overallHealth > 60 ? 'healthy' : overallHealth > 40 ? 'warning' : 'critical'}`}>
              {overallHealth.toFixed(1)}%
            </div>
          </div>
        </div>
        
        <div className="header-controls">
          <div className="view-controls">
            <button 
              className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
              onClick={() => setViewMode('grid')}
            >
              ⊞ Grid
            </button>
            <button 
              className={`view-btn ${viewMode === 'departments' ? 'active' : ''}`}
              onClick={() => setViewMode('departments')}
            >
              🏢 Departments
            </button>
            <button 
              className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
              onClick={() => setViewMode('list')}
            >
              ☰ List
            </button>
          </div>
          
          <div className="filter-controls">
            <select 
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="status-filter"
            >
              <option value="all">All Agents ({agents.length})</option>
              <option value="healthy">Healthy ({agents.filter(a => getAgentStatusInfo(a).color === 'healthy').length})</option>
              <option value="warning">Warning ({agents.filter(a => getAgentStatusInfo(a).color === 'warning').length})</option>
              <option value="critical">Critical ({agents.filter(a => getAgentStatusInfo(a).color === 'critical').length})</option>
            </select>
          </div>
        </div>
      </div>

      {/* Grid View */}
      {viewMode === 'grid' && (
        <div className="agents-grid">
          {getFilteredAgents().map((agent, index) => {
            const statusInfo = getAgentStatusInfo(agent);
            const performanceScore = calculatePerformanceScore(agent);
            
            return (
              <div 
                key={agent.id || index}
                className={`agent-card ${statusInfo.color} ${selectedAgent?.id === agent.id ? 'selected' : ''}`}
                onClick={() => setSelectedAgent(agent)}
              >
                <div className="agent-header">
                  <div className="agent-status">
                    <span className="status-icon">{statusInfo.icon}</span>
                  </div>
                  <div className="agent-info">
                    <div className="agent-name">{agent.name}</div>
                    <div className="agent-department">{agent.department}</div>
                  </div>
                </div>
                
                <div className="agent-metrics">
                  <div className="metric-item">
                    <span className="metric-label">Performance</span>
                    <div className="metric-bar">
                      <div 
                        className={`metric-fill ${performanceScore > 80 ? 'excellent' : performanceScore > 60 ? 'healthy' : performanceScore > 40 ? 'warning' : 'critical'}`}
                        style={{ width: `${performanceScore}%` }}
                      ></div>
                    </div>
                    <span className="metric-value">{performanceScore}%</span>
                  </div>
                  
                  <div className="agent-stats">
                    <div className="stat-item">
                      <span className="stat-icon">⚡</span>
                      <span className="stat-value">{agent.metrics?.responseTime || 0}ms</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-icon">📈</span>
                      <span className="stat-value">{agent.metrics?.uptime || 0}%</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-icon">❌</span>
                      <span className="stat-value">{agent.metrics?.errorRate || 0}%</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Departments View */}
      {viewMode === 'departments' && (
        <div className="departments-view">
          {Object.entries(agentsByDepartment).map(([department, deptAgents]) => {
            const deptHealth = getDepartmentHealth(deptAgents);
            const avgPerformance = deptAgents.reduce((sum, agent) => 
              sum + calculatePerformanceScore(agent), 0) / deptAgents.length;
            
            return (
              <div key={department} className={`department-section ${deptHealth}`}>
                <div className="department-header">
                  <div className="dept-info">
                    <h4 className="dept-name">{department}</h4>
                    <span className="dept-count">{deptAgents.length} Agents</span>
                  </div>
                  <div className="dept-health">
                    <div className={`health-indicator ${deptHealth}`}>
                      {deptHealth.toUpperCase()}
                    </div>
                    <div className="performance-score">
                      {avgPerformance.toFixed(1)}% Performance
                    </div>
                  </div>
                </div>
                
                <div className="department-agents">
                  {deptAgents.map((agent, index) => {
                    const statusInfo = getAgentStatusInfo(agent);
                    
                    return (
                      <div 
                        key={agent.id || index}
                        className={`dept-agent ${statusInfo.color}`}
                        onClick={() => setSelectedAgent(agent)}
                      >
                        <span className="agent-status-icon">{statusInfo.icon}</span>
                        <span className="agent-name">{agent.name}</span>
                        <span className="agent-performance">{calculatePerformanceScore(agent)}%</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* List View */}
      {viewMode === 'list' && (
        <div className="agents-list">
          <div className="list-header">
            <div className="col-header">Agent</div>
            <div className="col-header">Department</div>
            <div className="col-header">Status</div>
            <div className="col-header">Performance</div>
            <div className="col-header">Response Time</div>
            <div className="col-header">Uptime</div>
            <div className="col-header">Error Rate</div>
          </div>
          
          {getFilteredAgents().map((agent, index) => {
            const statusInfo = getAgentStatusInfo(agent);
            const performanceScore = calculatePerformanceScore(agent);
            
            return (
              <div 
                key={agent.id || index}
                className={`list-row ${statusInfo.color} ${selectedAgent?.id === agent.id ? 'selected' : ''}`}
                onClick={() => setSelectedAgent(agent)}
              >
                <div className="col-data agent-name">
                  <span className="status-icon">{statusInfo.icon}</span>
                  {agent.name}
                </div>
                <div className="col-data">{agent.department}</div>
                <div className="col-data">
                  <span className={`status-badge ${statusInfo.color}`}>
                    {statusInfo.text}
                  </span>
                </div>
                <div className="col-data">
                  <div className="performance-bar">
                    <div 
                      className={`perf-fill ${performanceScore > 80 ? 'excellent' : performanceScore > 60 ? 'healthy' : performanceScore > 40 ? 'warning' : 'critical'}`}
                      style={{ width: `${performanceScore}%` }}
                    ></div>
                    <span className="perf-text">{performanceScore}%</span>
                  </div>
                </div>
                <div className="col-data">{agent.metrics?.responseTime || 0}ms</div>
                <div className="col-data">{agent.metrics?.uptime || 0}%</div>
                <div className="col-data">{agent.metrics?.errorRate || 0}%</div>
              </div>
            );
          })}
        </div>
      )}

      {/* Agent Details Panel */}
      {selectedAgent && (
        <div className="agent-details-panel">
          <div className="details-header">
            <h4>Agent Details: {selectedAgent.name}</h4>
            <button 
              className="close-details"
              onClick={() => setSelectedAgent(null)}
            >
              ✕
            </button>
          </div>
          
          <div className="details-content">
            <div className="details-section">
              <h5>Basic Information</h5>
              <div className="details-grid">
                <div className="detail-item">
                  <span className="detail-label">Status:</span>
                  <span className={`detail-value ${getAgentStatusInfo(selectedAgent).color}`}>
                    {getAgentStatusInfo(selectedAgent).text}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Department:</span>
                  <span className="detail-value">{selectedAgent.department}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Last Seen:</span>
                  <span className="detail-value">{selectedAgent.lastSeen || 'Unknown'}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Version:</span>
                  <span className="detail-value">{selectedAgent.version || 'N/A'}</span>
                </div>
              </div>
            </div>
            
            <div className="details-section">
              <h5>Performance Metrics</h5>
              <div className="metrics-grid">
                <div className="metric-card">
                  <span className="metric-icon">⚡</span>
                  <span className="metric-name">Response Time</span>
                  <span className="metric-value">{selectedAgent.metrics?.responseTime || 0}ms</span>
                </div>
                <div className="metric-card">
                  <span className="metric-icon">📈</span>
                  <span className="metric-name">Uptime</span>
                  <span className="metric-value">{selectedAgent.metrics?.uptime || 0}%</span>
                </div>
                <div className="metric-card">
                  <span className="metric-icon">❌</span>
                  <span className="metric-name">Error Rate</span>
                  <span className="metric-value">{selectedAgent.metrics?.errorRate || 0}%</span>
                </div>
                <div className="metric-card">
                  <span className="metric-icon">✅</span>
                  <span className="metric-name">Task Completion</span>
                  <span className="metric-value">{selectedAgent.metrics?.taskCompletion || 0}%</span>
                </div>
              </div>
            </div>
            
            <div className="details-actions">
              <button className="action-btn restart">🔄 Restart Agent</button>
              <button className="action-btn logs">📋 View Logs</button>
              <button className="action-btn config">⚙️ Configuration</button>
            </div>
          </div>
        </div>
      )}

      {/* Real-time indicator */}
      <div className="matrix-realtime-indicator">
        <span className="indicator-dot"></span>
        <span className="indicator-text">Real-time Agent Monitoring</span>
      </div>
    </div>
  );
};

export default AgentHealthMatrix;
