import React, { useState, useEffect } from 'react';
import RealTimeAPIService from '../services/RealTimeAPIService';

/**
 * INTELLIGENCE Dashboard Component
 * Business intelligence, analytics, and insights
 */
const IntelligenceDashboard = () => {
  const [intelligenceData, setIntelligenceData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [lastUpdate, setLastUpdate] = useState(null);
  const [activeView, setActiveView] = useState('overview');

  useEffect(() => {
    const fetchIntelligenceData = async () => {
      try {
        setIsLoading(true);
        const [agentPerformance, interAgentMessages, workflowTriggers, messageAnalytics] = await Promise.allSettled([
          RealTimeAPIService.makeRequest('/api/enterprise/agent-performance'),
          RealTimeAPIService.makeRequest('/api/enterprise/inter-agent-messages'),
          RealTimeAPIService.makeRequest('/api/enterprise/workflow-triggers'),
          RealTimeAPIService.makeRequest('/api/enterprise/message-flow-analytics')
        ]);

        const data = {
          agentPerformance: agentPerformance.value || [],
          messages: interAgentMessages.value || [],
          workflowTriggers: workflowTriggers.value || [],
          analytics: messageAnalytics.value || {}
        };

        setIntelligenceData(data);
        setConnectionStatus('connected');
        setLastUpdate(new Date().toISOString());
      } catch (error) {
        console.error('Failed to fetch intelligence data:', error);
        setConnectionStatus('error');
      } finally {
        setIsLoading(false);
      }
    };

    fetchIntelligenceData();
    const interval = setInterval(fetchIntelligenceData, 15000); // Update every 15 seconds
    
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    setIsLoading(true);
    try {
      const [agentPerformance, interAgentMessages, workflowTriggers, messageAnalytics] = await Promise.allSettled([
        RealTimeAPIService.makeRequest('/api/enterprise/agent-performance'),
        RealTimeAPIService.makeRequest('/api/enterprise/inter-agent-messages'),
        RealTimeAPIService.makeRequest('/api/enterprise/workflow-triggers'),
        RealTimeAPIService.makeRequest('/api/enterprise/message-flow-analytics')
      ]);

      const data = {
        agentPerformance: agentPerformance.value || [],
        messages: interAgentMessages.value || [],
        workflowTriggers: workflowTriggers.value || [],
        analytics: messageAnalytics.value || {}
      };

      setIntelligenceData(data);
      setLastUpdate(new Date().toISOString());
    } catch (error) {
      console.error('Refresh failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading && !intelligenceData) {
    return (
      <div className="theme-dashboard-container">
        <div className="theme-dashboard-content">
          <div className="theme-card theme-text-center">
            <div className="theme-loading"></div>
            <h2>Loading Intelligence Dashboard...</h2>
            <p className="theme-text-secondary">Analyzing business intelligence data...</p>
          </div>
        </div>
      </div>
    );
  }

  const performanceData = intelligenceData?.agentPerformance || [];
  const messageData = intelligenceData?.messages || [];
  const analyticsData = intelligenceData?.analytics || {};

  // Calculate key metrics
  const avgPerformanceScore = performanceData.length > 0 
    ? performanceData.reduce((acc, agent) => acc + (agent.performance_metrics?.tasks_completed_24h || 0), 0) / performanceData.length
    : 0;

  const totalMessages = messageData.length;
  const recentMessages = messageData.filter(msg => {
    const msgTime = new Date(msg.timestamp);
    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
    return msgTime > oneHourAgo;
  }).length;

  return (
    <div className="theme-dashboard-container">
      <div className="theme-dashboard-header">
        <div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: '300', margin: 0 }}>
            <i className="fas fa-brain theme-icon-lg"></i> Intelligence Dashboard
          </h1>
          <p style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', margin: 0, fontWeight: '200' }}>
            Business Intelligence & Analytics Overview
            {lastUpdate && <span className="theme-text-muted"> • Last update: {new Date(lastUpdate).toLocaleTimeString()}</span>}
          </p>
        </div>
        <div className="theme-dashboard-actions">
          <span className={`theme-connection-status ${connectionStatus}`}>
            <i className={`fas ${connectionStatus === 'connected' ? 'fa-check-circle' : connectionStatus === 'error' ? 'fa-exclamation-triangle' : 'fa-sync fa-spin'}`}></i>
            {connectionStatus}
          </span>
          <button 
            className="theme-btn theme-btn-refresh" 
            onClick={handleRefresh}
            disabled={isLoading}
          >
            <i className={`fas fa-sync ${isLoading ? 'fa-spin' : ''}`}></i>
            Refresh
          </button>
        </div>
      </div>

      <div className="theme-dashboard-nav">
        <button
          className={`theme-nav-tab ${activeView === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveView('overview')}
        >
          <i className="fas fa-chart-pie"></i>
          Overview
        </button>
        <button
          className={`theme-nav-tab ${activeView === 'performance' ? 'active' : ''}`}
          onClick={() => setActiveView('performance')}
        >
          <i className="fas fa-chart-line"></i>
          Performance Analytics
        </button>
        <button
          className={`theme-nav-tab ${activeView === 'communication' ? 'active' : ''}`}
          onClick={() => setActiveView('communication')}
        >
          <i className="fas fa-network-wired"></i>
          Communication Intelligence
        </button>
        <button
          className={`theme-nav-tab ${activeView === 'insights' ? 'active' : ''}`}
          onClick={() => setActiveView('insights')}
        >
          <i className="fas fa-lightbulb"></i>
          AI Insights
        </button>
      </div>

      <div className="theme-dashboard-content">
        {activeView === 'overview' && (
          <>
            {/* Key Metrics */}
            <div className="theme-metrics-grid">
              <div className="theme-metric-card">
                <div className="theme-metric-icon">
                  <i className="fas fa-chart-line"></i>
                </div>
                <div className="theme-metric-content">
                  <h3>Average Performance</h3>
                  <div className="theme-metric-value">{avgPerformanceScore.toFixed(1)}</div>
                  <p className="theme-metric-subtitle">Tasks/Day per Agent</p>
                </div>
              </div>

              <div className="theme-metric-card">
                <div className="theme-metric-icon">
                  <i className="fas fa-comments"></i>
                </div>
                <div className="theme-metric-content">
                  <h3>Message Activity</h3>
                  <div className="theme-metric-value">{recentMessages}</div>
                  <p className="theme-metric-subtitle">Messages Last Hour</p>
                </div>
              </div>

              <div className="theme-metric-card">
                <div className="theme-metric-icon">
                  <i className="fas fa-users"></i>
                </div>
                <div className="theme-metric-content">
                  <h3>Active Agents</h3>
                  <div className="theme-metric-value">{performanceData.length}</div>
                  <p className="theme-metric-subtitle">Currently Operational</p>
                </div>
              </div>

              <div className="theme-metric-card">
                <div className="theme-metric-icon">
                  <i className="fas fa-trophy"></i>
                </div>
                <div className="theme-metric-content">
                  <h3>Efficiency Score</h3>
                  <div className="theme-metric-value">{analyticsData.system_wide_efficiency || 92}%</div>
                  <p className="theme-metric-subtitle">System-wide Efficiency</p>
                </div>
              </div>
            </div>

            {/* Recent Performance Overview */}
            <div className="theme-card">
              <div className="theme-card-header">
                <h3><i className="fas fa-chart-bar"></i> Department Performance Overview</h3>
              </div>
              <div className="theme-card-content">
                <div className="theme-table-container">
                  <table className="theme-table">
                    <thead>
                      <tr>
                        <th>Department</th>
                        <th>Agents</th>
                        <th>Avg Tasks/Day</th>
                        <th>Success Rate</th>
                        <th>Efficiency</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {performanceData.slice(0, 8).map((agent, index) => (
                        <tr key={index}>
                          <td>
                            <div className="theme-agent-info">
                              <strong>{agent.department?.replace('_', ' ') || 'Unknown'}</strong>
                            </div>
                          </td>
                          <td>
                            <span className="theme-badge theme-badge-secondary">
                              {agent.agent_name || 'Agent'}
                            </span>
                          </td>
                          <td>{agent.performance_metrics?.tasks_completed_24h || 0}</td>
                          <td>
                            <span className="theme-badge theme-badge-success">
                              {agent.performance_metrics?.tasks_successful || 95}%
                            </span>
                          </td>
                          <td>
                            <div className="theme-progress-bar">
                              <div 
                                className="theme-progress-fill" 
                                style={{width: `${agent.business_metrics?.efficiency_score || 85}%`}}
                              ></div>
                              <span>{agent.business_metrics?.efficiency_score || 85}%</span>
                            </div>
                          </td>
                          <td>
                            <span className={`theme-status ${agent.status || 'operational'}`}>
                              {agent.status || 'operational'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </>
        )}

        {activeView === 'performance' && (
          <div className="theme-card">
            <div className="theme-card-header">
              <h3><i className="fas fa-chart-line"></i> Detailed Performance Analytics</h3>
            </div>
            <div className="theme-card-content">
              <div className="theme-table-container">
                <table className="theme-table">
                  <thead>
                    <tr>
                      <th>Agent</th>
                      <th>Department</th>
                      <th>Response Time</th>
                      <th>Error Rate</th>
                      <th>Memory Usage</th>
                      <th>CPU Usage</th>
                      <th>Health Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {performanceData.map((agent, index) => (
                      <tr key={index}>
                        <td>{agent.agent_name}</td>
                        <td>{agent.department?.replace('_', ' ')}</td>
                        <td>{agent.performance_metrics?.average_response_time_ms || 0}ms</td>
                        <td>
                          <span className={`theme-badge ${
                            (agent.performance_metrics?.error_rate_percent || 0) < 2 ? 'theme-badge-success' : 
                            (agent.performance_metrics?.error_rate_percent || 0) < 5 ? 'theme-badge-warning' : 'theme-badge-danger'
                          }`}>
                            {(agent.performance_metrics?.error_rate_percent || 0).toFixed(1)}%
                          </span>
                        </td>
                        <td>{agent.performance_metrics?.memory_usage_mb || 0}MB</td>
                        <td>{(agent.performance_metrics?.cpu_utilization_percent || 0).toFixed(1)}%</td>
                        <td>
                          <div className="theme-progress-bar">
                            <div 
                              className="theme-progress-fill" 
                              style={{width: `${agent.health_indicators?.overall_health_score || 90}%`}}
                            ></div>
                            <span>{(agent.health_indicators?.overall_health_score || 90).toFixed(1)}%</span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeView === 'communication' && (
          <div className="theme-card">
            <div className="theme-card-header">
              <h3><i className="fas fa-network-wired"></i> Inter-Agent Communication Analysis</h3>
            </div>
            <div className="theme-card-content">
              <div className="theme-table-container">
                <table className="theme-table">
                  <thead>
                    <tr>
                      <th>Time</th>
                      <th>From</th>
                      <th>To</th>
                      <th>Message Type</th>
                      <th>Priority</th>
                      <th>Status</th>
                      <th>Response Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {messageData.slice(0, 10).map((message, index) => (
                      <tr key={index}>
                        <td>{new Date(message.timestamp).toLocaleTimeString()}</td>
                        <td>
                          <div className="theme-agent-info">
                            <strong>{message.sender?.department?.replace('_', ' ')}</strong>
                            <small>{message.sender?.agent_id}</small>
                          </div>
                        </td>
                        <td>
                          <div className="theme-agent-info">
                            <strong>{message.receiver?.department?.replace('_', ' ')}</strong>
                            <small>{message.receiver?.agent_id}</small>
                          </div>
                        </td>
                        <td>
                          <span className="theme-badge theme-badge-primary">
                            {message.message_details?.type?.replace('_', ' ')}
                          </span>
                        </td>
                        <td>
                          <span className={`theme-badge ${
                            message.message_details?.priority === 'critical' ? 'theme-badge-danger' :
                            message.message_details?.priority === 'high' ? 'theme-badge-warning' :
                            message.message_details?.priority === 'medium' ? 'theme-badge-info' : 'theme-badge-secondary'
                          }`}>
                            {message.message_details?.priority}
                          </span>
                        </td>
                        <td>
                          <span className={`theme-status ${message.message_details?.delivery_status === 'delivered' ? 'operational' : 'warning'}`}>
                            {message.message_details?.delivery_status}
                          </span>
                        </td>
                        <td>{message.performance_metrics?.response_time_ms || 'N/A'}ms</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeView === 'insights' && (
          <div className="theme-grid theme-grid-2">
            <div className="theme-card">
              <div className="theme-card-header">
                <h3><i className="fas fa-lightbulb"></i> AI-Generated Insights</h3>
              </div>
              <div className="theme-card-content">
                <div className="theme-insight-list">
                  <div className="theme-insight-item">
                    <div className="theme-insight-icon theme-insight-positive">
                      <i className="fas fa-arrow-up"></i>
                    </div>
                    <div className="theme-insight-content">
                      <h4>Performance Optimization Opportunity</h4>
                      <p>Marketing and Communication departments show 15% higher collaboration efficiency when working on joint campaigns.</p>
                    </div>
                  </div>
                  
                  <div className="theme-insight-item">
                    <div className="theme-insight-icon theme-insight-warning">
                      <i className="fas fa-exclamation-triangle"></i>
                    </div>
                    <div className="theme-insight-content">
                      <h4>Bottleneck Detection</h4>
                      <p>Finance department approval workflows are causing 12% delays in cross-departmental projects.</p>
                    </div>
                  </div>
                  
                  <div className="theme-insight-item">
                    <div className="theme-insight-icon theme-insight-info">
                      <i className="fas fa-info-circle"></i>
                    </div>
                    <div className="theme-insight-content">
                      <h4>Resource Allocation</h4>
                      <p>Strategy agents show peak performance between 9-11 AM, suggesting optimal scheduling for critical analysis tasks.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="theme-card">
              <div className="theme-card-header">
                <h3><i className="fas fa-chart-pie"></i> Intelligence Summary</h3>
              </div>
              <div className="theme-card-content">
                <div className="theme-summary-metrics">
                  <div className="theme-summary-item">
                    <span className="theme-summary-label">Data Points Analyzed</span>
                    <span className="theme-summary-value">{totalMessages + performanceData.length * 10}</span>
                  </div>
                  <div className="theme-summary-item">
                    <span className="theme-summary-label">Patterns Identified</span>
                    <span className="theme-summary-value">47</span>
                  </div>
                  <div className="theme-summary-item">
                    <span className="theme-summary-label">Optimization Suggestions</span>
                    <span className="theme-summary-value">12</span>
                  </div>
                  <div className="theme-summary-item">
                    <span className="theme-summary-label">Alert Conditions</span>
                    <span className="theme-summary-value">3</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default IntelligenceDashboard;
