import React, { useState, useEffect } from 'react';

/**
 * SystemStatusPanel - Core system status overview
 * 
 * Displays critical system metrics, health indicators, and status information
 * for the enterprise operations platform.
 */
const SystemStatusPanel = ({ status, metrics = {}, emergencyMode = false }) => {
  const [cpuUsage, setCpuUsage] = useState(0);
  const [memoryUsage, setMemoryUsage] = useState(0);
  const [diskUsage, setDiskUsage] = useState(0);
  const [networkStatus, setNetworkStatus] = useState('healthy');

  // Simulate real-time metrics updates
  useEffect(() => {
    if (metrics.cpu !== undefined) setCpuUsage(metrics.cpu);
    if (metrics.memory !== undefined) setMemoryUsage(metrics.memory);
    if (metrics.disk !== undefined) setDiskUsage(metrics.disk);
    if (metrics.network !== undefined) setNetworkStatus(metrics.network);
  }, [metrics]);

  // Get status color and icon
  const getStatusIndicator = (value, thresholds = { warning: 70, critical: 90 }) => {
    if (value < thresholds.warning) return { color: 'healthy', icon: '✅' };
    if (value < thresholds.critical) return { color: 'warning', icon: '⚠️' };
    return { color: 'critical', icon: '🚨' };
  };

  const cpuIndicator = getStatusIndicator(cpuUsage);
  const memoryIndicator = getStatusIndicator(memoryUsage);
  const diskIndicator = getStatusIndicator(diskUsage, { warning: 80, critical: 95 });

  // System uptime formatting
  const formatUptime = (seconds) => {
    if (!seconds) return 'Unknown';
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  // Overall system health calculation
  const calculateSystemHealth = () => {
    if (status === 'error') return 'critical';
    if (status === 'loading') return 'loading';
    
    const avgUsage = (cpuUsage + memoryUsage + diskUsage) / 3;
    if (avgUsage < 50) return 'excellent';
    if (avgUsage < 70) return 'healthy';
    if (avgUsage < 85) return 'warning';
    return 'critical';
  };

  const systemHealth = calculateSystemHealth();

  return (
    <div className={`system-status-panel ${emergencyMode ? 'emergency' : ''}`}>
      <div className="panel-header">
        <h3 className="panel-title">
          <span className="title-icon">🖥️</span>
          System Status
        </h3>
        <div className={`health-badge ${systemHealth}`}>
          {systemHealth.toUpperCase()}
        </div>
      </div>

      <div className="status-grid">
        {/* CPU Usage */}
        <div className="status-metric">
          <div className="metric-header">
            <span className="metric-icon">{cpuIndicator.icon}</span>
            <span className="metric-label">CPU Usage</span>
          </div>
          <div className="metric-value">
            <span className="value-number">{cpuUsage.toFixed(1)}%</span>
            <div className="progress-bar">
              <div 
                className={`progress-fill ${cpuIndicator.color}`}
                style={{ width: `${cpuUsage}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Memory Usage */}
        <div className="status-metric">
          <div className="metric-header">
            <span className="metric-icon">{memoryIndicator.icon}</span>
            <span className="metric-label">Memory Usage</span>
          </div>
          <div className="metric-value">
            <span className="value-number">{memoryUsage.toFixed(1)}%</span>
            <div className="progress-bar">
              <div 
                className={`progress-fill ${memoryIndicator.color}`}
                style={{ width: `${memoryUsage}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Disk Usage */}
        <div className="status-metric">
          <div className="metric-header">
            <span className="metric-icon">{diskIndicator.icon}</span>
            <span className="metric-label">Disk Usage</span>
          </div>
          <div className="metric-value">
            <span className="value-number">{diskUsage.toFixed(1)}%</span>
            <div className="progress-bar">
              <div 
                className={`progress-fill ${diskIndicator.color}`}
                style={{ width: `${diskUsage}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Network Status */}
        <div className="status-metric">
          <div className="metric-header">
            <span className="metric-icon">
              {networkStatus === 'healthy' ? '🌐' : networkStatus === 'degraded' ? '⚠️' : '🚨'}
            </span>
            <span className="metric-label">Network</span>
          </div>
          <div className="metric-value">
            <span className={`value-text ${networkStatus}`}>
              {networkStatus.toUpperCase()}
            </span>
          </div>
        </div>
      </div>

      {/* System Information */}
      <div className="system-info-section">
        <div className="info-grid">
          <div className="info-item">
            <span className="info-label">Uptime</span>
            <span className="info-value">{formatUptime(metrics.uptime)}</span>
          </div>
          
          <div className="info-item">
            <span className="info-label">Load Average</span>
            <span className="info-value">{metrics.loadAverage || 'N/A'}</span>
          </div>
          
          <div className="info-item">
            <span className="info-label">Active Processes</span>
            <span className="info-value">{metrics.activeProcesses || 0}</span>
          </div>
          
          <div className="info-item">
            <span className="info-label">System Version</span>
            <span className="info-value">{metrics.version || 'v1.0.0'}</span>
          </div>
        </div>
      </div>

      {/* Critical Alerts Summary */}
      {(metrics.criticalAlerts && metrics.criticalAlerts.length > 0) && (
        <div className="critical-alerts-summary">
          <div className="alerts-header">
            <span className="alert-icon">🚨</span>
            <span className="alert-count">{metrics.criticalAlerts.length} Critical Alert{metrics.criticalAlerts.length !== 1 ? 's' : ''}</span>
          </div>
          <div className="alerts-list">
            {metrics.criticalAlerts.slice(0, 3).map((alert, index) => (
              <div key={index} className="alert-item">
                <span className="alert-dot"></span>
                <span className="alert-message">{alert.message}</span>
              </div>
            ))}
            {metrics.criticalAlerts.length > 3 && (
              <div className="alert-item more">
                <span className="alert-dot"></span>
                <span className="alert-message">+{metrics.criticalAlerts.length - 3} more alerts</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* System Actions */}
      <div className="system-actions">
        <button 
          className="action-button refresh"
          onClick={() => window.location.reload()}
          disabled={emergencyMode}
        >
          🔄 Refresh
        </button>
        
        <button 
          className="action-button diagnostics"
          onClick={() => console.log('Running system diagnostics...')}
        >
          🔍 Diagnostics
        </button>
        
        {emergencyMode && (
          <button 
            className="action-button emergency-stop"
            onClick={() => console.log('Emergency stop initiated...')}
          >
            🛑 Emergency Stop
          </button>
        )}
      </div>

      {/* Real-time indicator */}
      <div className="realtime-indicator">
        <span className="indicator-dot"></span>
        <span className="indicator-text">Live Data</span>
      </div>
    </div>
  );
};

export default SystemStatusPanel;
