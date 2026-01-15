import React, { useState, useEffect, useCallback } from 'react';
import RealTimeAPIService from '../services/RealTimeAPIService';

/**
 * COMMAND Dashboard - System Command Center with Real Live Data
 * 
 * Primary interface for system oversight, agent coordination, and real-time monitoring.
 * Now connects to actual backend APIs for live metrics.
 */
const CommandDashboard = () => {
  const [systemData, setSystemData] = useState(null);
  const [agentData, setAgentData] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [lastUpdate, setLastUpdate] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [alerts, setAlerts] = useState([]);

  // Initialize real-time data connection
  useEffect(() => {
    let unsubscribe = null;

    const initializeRealTimeData = async () => {
      console.log('🚀 Initializing Command Dashboard with real-time data...');
      
      try {
        // Attempt to connect to backend
        const connected = await RealTimeAPIService.connect();
        
        if (connected) {
          setConnectionStatus('connected');
          
          // Subscribe to real-time updates
          unsubscribe = RealTimeAPIService.subscribe((data) => {
            console.log('📊 Received real-time update:', data);
            
            if (data.systemStatus?.status === 'success') {
              setSystemData(data.systemStatus.data);
            }
            
            if (data.agentHealth?.status === 'success') {
              setAgentData(data.agentHealth.data);
            }
            
            // Update alerts from various sources
            const newAlerts = [];
            if (data.systemStatus?.data?.alerts) {
              newAlerts.push(...data.systemStatus.data.alerts);
            }
            if (data.systemStatus?.status === 'error') {
              newAlerts.push({
                id: 'system-error',
                type: 'error',
                message: `System status error: ${data.systemStatus.error}`,
                timestamp: new Date().toISOString()
              });
            }
            if (data.agentHealth?.status === 'error') {
              newAlerts.push({
                id: 'agent-error',
                type: 'warning',
                message: `Agent health monitoring error: ${data.agentHealth.error}`,
                timestamp: new Date().toISOString()
              });
            }
            
            setAlerts(newAlerts);
            setLastUpdate(new Date().toISOString());
            setIsLoading(false);
          });
          
          // Start real-time polling with 1 second updates for live metrics
          RealTimeAPIService.startPolling(1000); // Update every 1 second
          
          // Initial data fetch
          const initialData = await Promise.allSettled([
            RealTimeAPIService.getSystemStatus(),
            RealTimeAPIService.getAgentHealth()
          ]);
          
          if (initialData[0].value?.status === 'success') {
            setSystemData(initialData[0].value.data);
          }
          if (initialData[1].value?.status === 'success') {
            setAgentData(initialData[1].value.data);
          }
          
        } else {
          setConnectionStatus('disconnected');
          setAlerts([{
            id: 'connection-failed',
            type: 'error',
            message: 'Failed to connect to backend services. Displaying offline mode.',
            timestamp: new Date().toISOString()
          }]);
        }
        
        setIsLoading(false);
        
      } catch (error) {
        console.error('❌ Failed to initialize real-time data:', error);
        setConnectionStatus('error');
        setIsLoading(false);
        setAlerts([{
          id: 'init-error',
          type: 'error',
          message: `Initialization failed: ${error.message}`,
          timestamp: new Date().toISOString()
        }]);
      }
    };

    initializeRealTimeData();

    // Cleanup on unmount
    return () => {
      if (unsubscribe) {
        unsubscribe();
      }
      RealTimeAPIService.stopPolling();
    };
  }, []);

  // Manual refresh function
  const handleRefresh = useCallback(async () => {
    setIsLoading(true);
    try {
      const [systemStatus, agentHealth] = await Promise.allSettled([
        RealTimeAPIService.getSystemStatus(),
        RealTimeAPIService.getAgentHealth()
      ]);
      
      if (systemStatus.value?.status === 'success') {
        setSystemData(systemStatus.value.data);
      }
      if (agentHealth.value?.status === 'success') {
        setAgentData(agentHealth.value.data);
      }
      
      setLastUpdate(new Date().toISOString());
    } catch (error) {
      console.error('Refresh failed:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Render loading state
  if (isLoading && !systemData) {
    return (
      <div className="theme-dashboard-container">
        <div className="theme-dashboard-content">
          <div className="theme-card theme-text-center">
            <div className="theme-loading" style={{ margin: '0 auto 16px' }}></div>
            <h2>Loading Command Dashboard...</h2>
            <p className="theme-text-secondary">Connecting to backend services...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="theme-dashboard-container">
      {/* Dashboard Header */}
      <div className="theme-dashboard-header">
        <div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: '300', margin: 0 }}>
            <i className="fas fa-terminal theme-icon-lg"></i> Command Center
          </h1>
          <p style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', margin: 0, fontWeight: '200' }}>
            Real-time system monitoring and control
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className={`theme-status-${connectionStatus === 'connected' ? 'operational' : 'error'}`}>
            ● {connectionStatus === 'connected' ? 'Live' : 'Offline'}
          </span>
          <button 
            onClick={handleRefresh} 
            className="theme-button-secondary"
            disabled={isLoading}
            style={{ fontSize: '0.75rem', padding: '0.375rem 0.75rem' }}
          >
            <i className="fas fa-sync-alt theme-icon-sm"></i> {isLoading ? 'Refreshing...' : 'Refresh'}
          </button>
          {lastUpdate && (
            <span style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>
              Last: {new Date(lastUpdate).toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>

      <div className="theme-dashboard-content">
        {/* System Alerts */}
        {alerts.length > 0 && (
          <div className="theme-mb-lg">
            {alerts.map(alert => (
              <div key={alert.id} className={`theme-alert-${alert.type}`}>
                <strong>{alert.type.toUpperCase()}:</strong> {alert.message}
                <span style={{ float: 'right', fontSize: '0.75rem' }}>
                  {new Date(alert.timestamp).toLocaleTimeString()}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Service Status */}
        <div className="theme-card theme-mb-lg">
          <h3 className="theme-mb-md" style={{ fontSize: '1rem', fontWeight: '300' }}>
            <i className="fas fa-cogs theme-icon-md"></i> Service Status
          </h3>
          <div className="theme-grid theme-grid-cols-3">
            {systemData?.services ? Object.entries(systemData.services).map(([serviceName, service]) => (
              <div key={serviceName} className="theme-metric-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: '500' }}>
                    {serviceName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                  <span className={`theme-status-${service.status === 'operational' ? 'operational' : 'error'}`}>
                    ● {service.status}
                  </span>
                </div>
                {service.response_time && (
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                    Response: {service.response_time}
                  </div>
                )}
                {service.uptime && (
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                    Uptime: {service.uptime}
                  </div>
                )}
              </div>
            )) : (
              <div className="theme-text-secondary">No service data available</div>
            )}
          </div>
        </div>

        {/* Agent Health Matrix */}
        <div className="theme-card theme-mb-lg">
          <h3 className="theme-mb-md" style={{ fontSize: '1rem', fontWeight: '300' }}>
            <i className="fas fa-users theme-icon-md"></i> Agent Health Matrix
          </h3>
          {agentData?.agents?.length > 0 ? (
            <div className="theme-grid theme-grid-cols-4">
              {agentData.agents.slice(0, 12).map(agent => (
                <div key={agent.id} className="theme-metric-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>
                      {agent.name || agent.id}
                    </span>
                    <span className={`theme-status-${agent.status === 'operational' ? 'operational' : 
                      agent.status === 'warning' ? 'warning' : 'error'}`}>
                      ●
                    </span>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                    {agent.department} • Health: {agent.health_score || 0}%
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>
                    Tasks: {agent.tasks_completed || 0} • {agent.avg_response_time || 'N/A'}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="theme-text-secondary">No agent data available</div>
          )}
        </div>

        {/* Performance Metrics */}
        <div className="theme-grid theme-grid-cols-2">
          <div className="theme-card">
            <h3 className="theme-mb-md" style={{ fontSize: '1rem', fontWeight: '300' }}>
              <i className="fas fa-chart-line theme-icon-md"></i> System Performance
            </h3>
            <div className="theme-grid theme-grid-cols-2">
              <div className="theme-metric-card">
                <div className="theme-metric-value">{systemData?.performance?.cpu || 0}%</div>
                <div className="theme-metric-label">CPU</div>
              </div>
              <div className="theme-metric-card">
                <div className="theme-metric-value">{systemData?.performance?.memory || 0}%</div>
                <div className="theme-metric-label">Memory</div>
              </div>
              <div className="theme-metric-card">
                <div className="theme-metric-value">{systemData?.performance?.disk || 0}%</div>
                <div className="theme-metric-label">Disk</div>
              </div>
              <div className="theme-metric-card">
                <div className="theme-metric-value" style={{ fontSize: '1rem' }}>
                  {systemData?.performance?.network || '0 MB/s'}
                </div>
                <div className="theme-metric-label">Network</div>
              </div>
            </div>
          </div>

          <div className="theme-card">
            <h3 className="theme-mb-md" style={{ fontSize: '1rem', fontWeight: '300' }}>
              <i className="fas fa-shield-alt theme-icon-md"></i> Security Status
            </h3>
            <div className="theme-grid theme-grid-cols-2">
              <div className="theme-metric-card">
                <div className="theme-metric-value theme-status-operational">
                  {systemData?.security?.threat_level || 'Unknown'}
                </div>
                <div className="theme-metric-label">Threat Level</div>
              </div>
              <div className="theme-metric-card">
                <div className="theme-metric-value">{systemData?.security?.active_sessions || 0}</div>
                <div className="theme-metric-label">Active Sessions</div>
              </div>
              <div className="theme-metric-card">
                <div className="theme-metric-value">{systemData?.security?.failed_auth_attempts || 0}</div>
                <div className="theme-metric-label">Failed Auth</div>
              </div>
              <div className="theme-metric-card">
                <div className="theme-metric-value">{systemData?.security?.firewall_blocks || 0}</div>
                <div className="theme-metric-label">Firewall Blocks</div>
              </div>
            </div>
          </div>
        </div>

        {/* Debug Info (only in development) */}
        {process.env.NODE_ENV === 'development' && (
          <div className="theme-card theme-mt-lg">
            <h4 style={{ fontSize: '0.875rem', fontWeight: '300' }}>
              <i className="fas fa-bug theme-icon-sm"></i> Debug Information
            </h4>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>
              <div>Connection: {RealTimeAPIService.getConnectionInfo().status}</div>
              <div>Polling: {RealTimeAPIService.getConnectionInfo().isPolling ? 'Active' : 'Inactive'}</div>
              <div>Subscribers: {RealTimeAPIService.getConnectionInfo().subscriberCount}</div>
              <div>API URL: {RealTimeAPIService.getConnectionInfo().baseURL}</div>
              {RealTimeAPIService.getConnectionInfo().lastError && (
                <div>Last Error: {RealTimeAPIService.getConnectionInfo().lastError}</div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CommandDashboard;
