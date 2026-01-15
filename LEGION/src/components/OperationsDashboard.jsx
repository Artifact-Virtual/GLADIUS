import React, { useState, useEffect, useCallback } from 'react';
import RealTimeAPIService from '../services/RealTimeAPIService';

/**
 * OPERATIONS Dashboard - Workflow & Task Management Center
 * 
 * Primary interface for workflow monitoring, task management, and operational oversight.
 * Focuses on active workflows, task execution, and operational metrics.
 */
const OperationsDashboard = () => {
  const [workflowData, setWorkflowData] = useState(null);
  const [taskData, setTaskData] = useState(null);
  const [performanceData, setPerformanceData] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [lastUpdate, setLastUpdate] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [alerts, setAlerts] = useState([]);

  // Initialize real-time data connection
  useEffect(() => {
    let unsubscribe = null;

    const initializeRealTimeData = async () => {
      console.log('🚀 Initializing Operations Dashboard with real-time data...');
      
      try {
        // Attempt to connect to backend
        const connected = await RealTimeAPIService.connect();
        
        if (connected) {
          setConnectionStatus('connected');
          
          // Subscribe to real-time updates
          unsubscribe = RealTimeAPIService.subscribe((data) => {
            console.log('📊 Received workflow update:', data);
            
            if (data.workflowStatus?.status === 'success') {
              setWorkflowData(data.workflowStatus.data);
            }
            
            if (data.performanceMetrics?.status === 'success') {
              setPerformanceData(data.performanceMetrics.data);
            }
            
            setLastUpdate(new Date().toISOString());
            setIsLoading(false);
          });
          
          // Start real-time polling  
          RealTimeAPIService.startPolling(1000); // Update every 1 second for operations
          
          // Initial data fetch - workflow and performance focused
          const initialData = await Promise.allSettled([
            RealTimeAPIService.makeRequest('/api/enterprise/workflow-status'),
            RealTimeAPIService.makeRequest('/api/enterprise/performance-metrics'),
            RealTimeAPIService.makeRequest('/api/enterprise/agent-performance')
          ]);
          
          if (initialData[0].value) {
            setWorkflowData(initialData[0].value);
          }
          if (initialData[1].value) {
            setPerformanceData(initialData[1].value);
          }
          if (initialData[2].value) {
            setTaskData(initialData[2].value);
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
        console.error('❌ Failed to initialize operations data:', error);
        setConnectionStatus('error');
        setIsLoading(false);
        setAlerts([{
          id: 'init-error',
          type: 'error',
          message: `Operations initialization failed: ${error.message}`,
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
      const [workflows, performance, tasks] = await Promise.allSettled([
        RealTimeAPIService.makeRequest('/api/enterprise/workflow-status'),
        RealTimeAPIService.makeRequest('/api/enterprise/performance-metrics'),
        RealTimeAPIService.makeRequest('/api/enterprise/agent-performance')
      ]);
      
      if (workflows.value) setWorkflowData(workflows.value);
      if (performance.value) setPerformanceData(performance.value);
      if (tasks.value) setTaskData(tasks.value);
      
      setLastUpdate(new Date().toISOString());
    } catch (error) {
      console.error('Refresh failed:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Render loading state
  if (isLoading) {
    return (
      <div className="theme-dashboard-container">
        <div className="theme-dashboard-content">
          <div className="theme-card theme-text-center">
            <div className="theme-loading" style={{ margin: '0 auto 16px' }}></div>
            <h2>Loading Operations Dashboard...</h2>
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
          <h1 style={{ fontSize: '1.5rem', fontWeight: '600', margin: 0 }}>
            ⚙️ Operations Center
          </h1>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', margin: 0 }}>
            Workflow execution, task management, and operational metrics
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
          >
            {isLoading ? 'Refreshing...' : '🔄 Refresh'}
          </button>
          {lastUpdate && (
            <span style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>
              Last: {new Date(lastUpdate).toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>

      <div className="theme-dashboard-content">
        {/* Operations Alerts */}
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

        {/* Operations Overview Grid */}
        <div className="theme-grid theme-grid-cols-4 theme-mb-lg">
          <div className="theme-metric-card">
            <div className="theme-metric-value theme-status-operational">
              {workflowData?.length || 0}
            </div>
            <div className="theme-metric-label">Active Workflows</div>
          </div>
          
          <div className="theme-metric-card">
            <div className="theme-metric-value">
              {performanceData?.agents?.active_count || 0}
            </div>
            <div className="theme-metric-label">Active Agents</div>
          </div>
          
          <div className="theme-metric-card">
            <div className="theme-metric-value">
              {taskData?.queue_size || 0}
            </div>
            <div className="theme-metric-label">Tasks in Queue</div>
          </div>
        </div>

        {/* Workflow Status */}
        <div className="theme-card theme-mb-lg">
          <h3 className="theme-mb-md">� Active Workflows</h3>
          {workflowData?.length > 0 ? (
            <div className="theme-grid theme-grid-cols-3">
              {workflowData.slice(0, 9).map((workflow, index) => (
                <div key={workflow.id || index} className="theme-metric-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: '500' }}>
                      {workflow.name || `Workflow ${index + 1}`}
                    </span>
                    <span className={`theme-status-${workflow.status === 'running' ? 'operational' : 
                      workflow.status === 'pending' ? 'warning' : 'error'}`}>
                      ● {workflow.status || 'unknown'}
                    </span>
                  </div>
                  {workflow.progress && (
                    <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                      Progress: {workflow.progress}%
                    </div>
                  )}
                  {workflow.last_updated && (
                    <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>
                      Updated: {new Date(workflow.last_updated).toLocaleTimeString()}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="theme-text-secondary">No workflow data available</div>
          )}
        </div>

        {/* Task Performance */}
        <div className="theme-card theme-mb-lg">
          <h3 className="theme-mb-md">⚡ Task Performance</h3>
          {taskData?.length > 0 ? (
            <div className="theme-grid theme-grid-cols-4">
              {taskData.slice(0, 12).map((task, index) => (
                <div key={task.id || index} className="theme-metric-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>
                      {task.name || task.type || `Task ${index + 1}`}
                    </span>
                    <span className={`theme-status-${task.status === 'completed' ? 'operational' : 
                      task.status === 'running' ? 'warning' : 'error'}`}>
                      ●
                    </span>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                    {task.agent || 'Unknown Agent'} • Duration: {task.duration || 'N/A'}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>
                    Priority: {task.priority || 'Normal'} • {task.completion_time || 'In Progress'}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="theme-text-secondary">No task data available</div>
          )}
        </div>

        {/* Performance Metrics */}
        <div className="theme-grid theme-grid-cols-2">
          <div className="theme-card">
            <h3 className="theme-mb-md">📊 System Performance</h3>
            <div className="theme-grid theme-grid-cols-2">
              <div className="theme-metric-card">
                <div className="theme-metric-value">{performanceData?.cpu_usage || 0}%</div>
                <div className="theme-metric-label">CPU</div>
              </div>
              <div className="theme-metric-card">
                <div className="theme-metric-value">{performanceData?.memory_usage || 0}%</div>
                <div className="theme-metric-label">Memory</div>
              </div>
              <div className="theme-metric-card">
                <div className="theme-metric-value">{performanceData?.disk_usage || 0}%</div>
                <div className="theme-metric-label">Disk</div>
              </div>
              <div className="theme-metric-card">
                <div className="theme-metric-value" style={{ fontSize: '1rem' }}>
                  {performanceData?.network_throughput || '0 MB/s'}
                </div>
                <div className="theme-metric-label">Network</div>
              </div>
            </div>
          </div>

          <div className="theme-card">
            <h3 className="theme-mb-md">� Operations Metrics</h3>
            <div className="theme-grid theme-grid-cols-2">
              <div className="theme-metric-card">
                <div className="theme-metric-value">
                  {performanceData?.throughput || 0}
                </div>
                <div className="theme-metric-label">Tasks/Hour</div>
              </div>
              <div className="theme-metric-card">
                <div className="theme-metric-value">{performanceData?.success_rate || 0}%</div>
                <div className="theme-metric-label">Success Rate</div>
              </div>
              <div className="theme-metric-card">
                <div className="theme-metric-value">{performanceData?.avg_response_time || 0}ms</div>
                <div className="theme-metric-label">Avg Response</div>
              </div>
              <div className="theme-metric-card">
                <div className="theme-metric-value">{performanceData?.error_count || 0}</div>
                <div className="theme-metric-label">Errors</div>
              </div>
            </div>
          </div>
        </div>

        {/* Debug Info (only in development) */}
        {process.env.NODE_ENV === 'development' && (
          <div className="theme-card theme-mt-lg">
            <h4>🔧 Debug Information</h4>
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

export default OperationsDashboard;
