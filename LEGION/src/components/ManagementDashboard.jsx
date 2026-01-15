import React, { useState, useEffect, useCallback } from 'react';
import RealTimeAPIService from '../services/RealTimeAPIService';

/**
 * MANAGEMENT Dashboard Component
 * Enterprise management oversight and control interface
 */
const ManagementDashboard = () => {
  const [managementData, setManagementData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [lastUpdate, setLastUpdate] = useState(null);
  const [error, setError] = useState(null);

  const fetchManagementData = useCallback(async () => {
    try {
      setError(null);
      if (!managementData) {
        setIsLoading(true);
      }
      
      const [systemStatus, performanceMetrics, agentHealth] = await Promise.allSettled([
        RealTimeAPIService.makeRequest('/api/enterprise/system-status'),
        RealTimeAPIService.makeRequest('/api/enterprise/performance-metrics'),
        RealTimeAPIService.makeRequest('/api/enterprise/agent-health')
      ]);

      const data = {
        system: systemStatus.status === 'fulfilled' ? systemStatus.value : null,
        performance: performanceMetrics.status === 'fulfilled' ? performanceMetrics.value : null,
        agents: agentHealth.status === 'fulfilled' ? agentHealth.value : []
      };

      setManagementData(data);
      setConnectionStatus('connected');
      setLastUpdate(new Date().toISOString());
    } catch (error) {
      console.error('Failed to fetch management data:', error);
      setConnectionStatus('error');
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  }, [managementData]);

  useEffect(() => {
    fetchManagementData();
    const interval = setInterval(fetchManagementData, 12000); // Update every 12 seconds instead of 5
    
    return () => clearInterval(interval);
  }, [fetchManagementData]);

  const handleRefresh = async () => {
    setIsLoading(true);
    setError(null);
    await fetchManagementData();
  };

  if (isLoading && !managementData) {
    return (
      <div className="theme-dashboard-container">
        <div className="theme-dashboard-content">
          <div className="theme-card theme-text-center">
            <div className="theme-loading"></div>
            <h2>Loading Management Dashboard...</h2>
            <p className="theme-text-secondary">Connecting to backend services...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error && !managementData) {
    return (
      <div className="theme-dashboard-container">
        <div className="theme-dashboard-content">
          <div className="theme-card theme-text-center">
            <i className="fas fa-exclamation-triangle theme-text-warning" style={{fontSize: '3rem', marginBottom: '1rem'}}></i>
            <h2>Connection Error</h2>
            <p className="theme-text-secondary">Failed to load management data: {error}</p>
            <button className="theme-btn theme-btn-primary" onClick={handleRefresh}>
              <i className="fas fa-retry"></i> Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="theme-dashboard-container">
      <div className="theme-dashboard-header">
        <div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: '300', margin: 0 }}>
            <i className="fas fa-building theme-icon-lg"></i> Management Center
          </h1>
          <p style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', margin: 0, fontWeight: '200' }}>
            Enterprise oversight, resource management, and strategic control
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className={`theme-status-${connectionStatus === 'connected' ? 'operational' : 'error'}`}>
            ● {connectionStatus === 'connected' ? 'Live' : 'Offline'}
          </span>
          {lastUpdate && (
            <span style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>
              Last: {new Date(lastUpdate).toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>

      <div className="theme-dashboard-content">
        {/* Management Overview */}
        <div className="theme-grid theme-grid-cols-4 theme-mb-lg">
          <div className="theme-metric-card">
            <div className="theme-metric-value">
              {managementData?.system?.total_agents || 0}
            </div>
            <div className="theme-metric-label">Total Agents</div>
          </div>
          
          <div className="theme-metric-card">
            <div className="theme-metric-value">
              {managementData?.system?.active_workflows || 0}
            </div>
            <div className="theme-metric-label">Active Workflows</div>
          </div>
          
          <div className="theme-metric-card">
            <div className="theme-metric-value">
              {managementData?.performance?.total_tasks || 0}
            </div>
            <div className="theme-metric-label">Tasks Completed</div>
          </div>
          
          <div className="theme-metric-card">
            <div className="theme-metric-value">
              {managementData?.system?.uptime || '0%'}
            </div>
            <div className="theme-metric-label">System Uptime</div>
          </div>
        </div>

        {/* System Health Overview */}
        <div className="theme-card theme-mb-lg">
          <h3 className="theme-mb-md">🏥 System Health Overview</h3>
          {managementData?.system ? (
            <div className="theme-grid theme-grid-cols-3">
              <div className="theme-metric-card">
                <div className="theme-metric-value">
                  {managementData.system.cpu_usage || 0}%
                </div>
                <div className="theme-metric-label">CPU Usage</div>
              </div>
              <div className="theme-metric-card">
                <div className="theme-metric-value">
                  {managementData.system.memory_usage || 0}%
                </div>
                <div className="theme-metric-label">Memory Usage</div>
              </div>
              <div className="theme-metric-card">
                <div className="theme-metric-value">
                  {managementData.system.disk_usage || 0}%
                </div>
                <div className="theme-metric-label">Disk Usage</div>
              </div>
            </div>
          ) : (
            <div className="theme-text-secondary">No system health data available</div>
          )}
        </div>

        {/* Agent Performance */}
        <div className="theme-card theme-mb-lg">
          <h3 className="theme-mb-md">👥 Agent Performance</h3>
          {Array.isArray(managementData?.agents) && managementData.agents.length > 0 ? (
            <div className="theme-grid theme-grid-cols-4">
              {managementData.agents.slice(0, 8).map((agent, index) => (
                <div key={agent.id || index} className="theme-metric-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>
                      {agent.name || agent.id || `Agent ${index + 1}`}
                    </span>
                    <span className={`theme-status-${agent.status === 'operational' ? 'operational' : 
                      agent.status === 'warning' ? 'warning' : 'error'}`}>
                      ●
                    </span>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                    Performance: {agent.performance_score || 0}%
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>
                    Tasks: {agent.tasks_completed || 0}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="theme-text-secondary">No agent performance data available</div>
          )}
        </div>

        {/* Resource Utilization */}
        <div className="theme-grid theme-grid-cols-2">
          <div className="theme-card">
            <h3 className="theme-mb-md">📊 Resource Utilization</h3>
            {managementData?.performance ? (
              <div className="theme-grid theme-grid-cols-2">
                <div className="theme-metric-card">
                  <div className="theme-metric-value">
                    {managementData.performance.database_connections || 0}
                  </div>
                  <div className="theme-metric-label">DB Connections</div>
                </div>
                <div className="theme-metric-card">
                  <div className="theme-metric-value">
                    {managementData.performance.api_calls || 0}
                  </div>
                  <div className="theme-metric-label">API Calls</div>
                </div>
                <div className="theme-metric-card">
                  <div className="theme-metric-value">
                    {managementData.performance.queue_size || 0}
                  </div>
                  <div className="theme-metric-label">Queue Size</div>
                </div>
                <div className="theme-metric-card">
                  <div className="theme-metric-value">
                    {managementData.performance.cache_hit_rate || 0}%
                  </div>
                  <div className="theme-metric-label">Cache Hit Rate</div>
                </div>
              </div>
            ) : (
              <div className="theme-text-secondary">No resource data available</div>
            )}
          </div>

          <div className="theme-card">
            <h3 className="theme-mb-md">⚡ Performance Metrics</h3>
            {managementData?.performance ? (
              <div className="theme-grid theme-grid-cols-2">
                <div className="theme-metric-card">
                  <div className="theme-metric-value">
                    {managementData.performance.avg_response_time || 0}ms
                  </div>
                  <div className="theme-metric-label">Avg Response</div>
                </div>
                <div className="theme-metric-card">
                  <div className="theme-metric-value">
                    {managementData.performance.throughput || 0}
                  </div>
                  <div className="theme-metric-label">Requests/sec</div>
                </div>
                <div className="theme-metric-card">
                  <div className="theme-metric-value">
                    {managementData.performance.error_rate || 0}%
                  </div>
                  <div className="theme-metric-label">Error Rate</div>
                </div>
                <div className="theme-metric-card">
                  <div className="theme-metric-value">
                    {managementData.performance.success_rate || 0}%
                  </div>
                  <div className="theme-metric-label">Success Rate</div>
                </div>
              </div>
            ) : (
              <div className="theme-text-secondary">No performance data available</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ManagementDashboard;
