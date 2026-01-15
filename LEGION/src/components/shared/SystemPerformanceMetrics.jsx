import React, { useState, useEffect } from 'react';

/**
 * SystemPerformanceMetrics - Real-time system performance monitoring and metrics display
 * 
 * Monitors CPU, memory, network, storage, and enterprise-specific performance metrics
 * with trend analysis and performance optimization recommendations.
 */
const SystemPerformanceMetrics = ({ 
  performanceData = {},
  historicalData = [],
  emergencyMode = false,
  onPerformanceAction = () => {} 
}) => {
  const [viewMode, setViewMode] = useState('overview'); // 'overview', 'detailed', 'trends', 'alerts'
  const [timeRange, setTimeRange] = useState('1h'); // '5m', '1h', '6h', '24h', '7d'
  const [selectedMetrics, setSelectedMetrics] = useState(['cpu', 'memory', 'network', 'storage']);
  const [alertThresholds, setAlertThresholds] = useState({
    cpu: 80,
    memory: 85,
    network: 90,
    storage: 80,
    response_time: 1000
  });

  // Calculate performance health scores
  const calculateHealthScore = (metrics) => {
    if (!metrics) return 0;
    
    const scores = {
      cpu: Math.max(0, 100 - (metrics.cpu_usage || 0)),
      memory: Math.max(0, 100 - (metrics.memory_usage || 0)),
      network: Math.max(0, 100 - (metrics.network_usage || 0)),
      storage: Math.max(0, 100 - (metrics.storage_usage || 0)),
      response: metrics.avg_response_time ? Math.max(0, 100 - (metrics.avg_response_time / 10)) : 100
    };
    
    return Math.round(Object.values(scores).reduce((sum, score) => sum + score, 0) / Object.keys(scores).length);
  };

  // Get performance status based on metrics
  const getPerformanceStatus = (value, threshold, inverted = false) => {
    const critical = threshold * 1.1;
    const warning = threshold * 0.8;
    
    if (inverted) {
      if (value < warning) return { status: 'critical', color: '#dc3545' };
      if (value < threshold) return { status: 'warning', color: '#ffc107' };
      return { status: 'good', color: '#28a745' };
    } else {
      if (value > critical) return { status: 'critical', color: '#dc3545' };
      if (value > threshold) return { status: 'warning', color: '#ffc107' };
      return { status: 'good', color: '#28a745' };
    }
  };

  // Format performance values
  const formatValue = (value, type) => {
    switch (type) {
      case 'percentage':
        return `${Math.round(value || 0)}%`;
      case 'bytes':
        return formatBytes(value || 0);
      case 'time':
        return `${Math.round(value || 0)}ms`;
      case 'rate':
        return `${Math.round(value || 0)}/s`;
      default:
        return Math.round(value || 0);
    }
  };

  // Format bytes
  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  // Get trend direction
  const getTrendDirection = (current, previous) => {
    if (!previous || current === previous) return 'stable';
    return current > previous ? 'up' : 'down';
  };

  // Get trend icon
  const getTrendIcon = (direction, isGoodWhenUp = false) => {
    if (direction === 'stable') return '➡️';
    if (direction === 'up') return isGoodWhenUp ? '📈' : '📊';
    return isGoodWhenUp ? '📉' : '📈';
  };

  const currentMetrics = performanceData.current || {};
  const previousMetrics = performanceData.previous || {};
  const healthScore = calculateHealthScore(currentMetrics);

  return (
    <div className={`system-performance-metrics ${emergencyMode ? 'emergency' : ''}`}>
      <div className="metrics-header">
        <div className="header-left">
          <h3 className="metrics-title">
            <span className="title-icon">📊</span>
            System Performance
          </h3>
          <div className="overall-health">
            <div className={`health-score ${healthScore > 80 ? 'good' : healthScore > 60 ? 'warning' : 'critical'}`}>
              <span className="score-value">{healthScore}</span>
              <span className="score-label">Health Score</span>
            </div>
          </div>
        </div>

        <div className="header-controls">
          <div className="view-controls">
            <select
              value={viewMode}
              onChange={(e) => setViewMode(e.target.value)}
              className="view-select"
            >
              <option value="overview">Overview</option>
              <option value="detailed">Detailed Metrics</option>
              <option value="trends">Performance Trends</option>
              <option value="alerts">Alert Configuration</option>
            </select>

            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="time-select"
            >
              <option value="5m">Last 5 minutes</option>
              <option value="1h">Last hour</option>
              <option value="6h">Last 6 hours</option>
              <option value="24h">Last 24 hours</option>
              <option value="7d">Last 7 days</option>
            </select>
          </div>

          <div className="action-controls">
            <button 
              className="action-btn optimize"
              onClick={() => onPerformanceAction('optimize')}
            >
              🔧 Optimize System
            </button>
            
            <button 
              className="action-btn cleanup"
              onClick={() => onPerformanceAction('cleanup')}
            >
              🧹 Cleanup Resources
            </button>
          </div>
        </div>
      </div>

      <div className="metrics-content">
        {viewMode === 'overview' && (
          <div className="overview-grid">
            {/* CPU Metrics */}
            <div className="metric-card cpu">
              <div className="card-header">
                <span className="metric-icon">💻</span>
                <div className="metric-info">
                  <h4>CPU Usage</h4>
                  <span className="metric-description">Processor utilization</span>
                </div>
                <span className="trend-icon">
                  {getTrendIcon(getTrendDirection(currentMetrics.cpu_usage, previousMetrics.cpu_usage))}
                </span>
              </div>
              
              <div className="metric-value-section">
                <div className="primary-value">
                  <span className="value">{formatValue(currentMetrics.cpu_usage, 'percentage')}</span>
                  <div 
                    className="value-bar"
                    style={{ 
                      width: `${Math.min(100, currentMetrics.cpu_usage || 0)}%`,
                      backgroundColor: getPerformanceStatus(currentMetrics.cpu_usage, alertThresholds.cpu).color
                    }}
                  ></div>
                </div>
                
                <div className="secondary-metrics">
                  <div className="secondary-metric">
                    <span className="label">Load Avg:</span>
                    <span className="value">{currentMetrics.load_average || '0.00'}</span>
                  </div>
                  <div className="secondary-metric">
                    <span className="label">Cores:</span>
                    <span className="value">{currentMetrics.cpu_cores || 'N/A'}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Memory Metrics */}
            <div className="metric-card memory">
              <div className="card-header">
                <span className="metric-icon">🧠</span>
                <div className="metric-info">
                  <h4>Memory Usage</h4>
                  <span className="metric-description">RAM utilization</span>
                </div>
                <span className="trend-icon">
                  {getTrendIcon(getTrendDirection(currentMetrics.memory_usage, previousMetrics.memory_usage))}
                </span>
              </div>
              
              <div className="metric-value-section">
                <div className="primary-value">
                  <span className="value">{formatValue(currentMetrics.memory_usage, 'percentage')}</span>
                  <div 
                    className="value-bar"
                    style={{ 
                      width: `${Math.min(100, currentMetrics.memory_usage || 0)}%`,
                      backgroundColor: getPerformanceStatus(currentMetrics.memory_usage, alertThresholds.memory).color
                    }}
                  ></div>
                </div>
                
                <div className="secondary-metrics">
                  <div className="secondary-metric">
                    <span className="label">Used:</span>
                    <span className="value">{formatBytes(currentMetrics.memory_used)}</span>
                  </div>
                  <div className="secondary-metric">
                    <span className="label">Total:</span>
                    <span className="value">{formatBytes(currentMetrics.memory_total)}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Network Metrics */}
            <div className="metric-card network">
              <div className="card-header">
                <span className="metric-icon">🌐</span>
                <div className="metric-info">
                  <h4>Network Activity</h4>
                  <span className="metric-description">Data transfer rates</span>
                </div>
                <span className="trend-icon">
                  {getTrendIcon(getTrendDirection(currentMetrics.network_usage, previousMetrics.network_usage))}
                </span>
              </div>
              
              <div className="metric-value-section">
                <div className="primary-value">
                  <span className="value">{formatValue(currentMetrics.network_usage, 'percentage')}</span>
                  <div 
                    className="value-bar"
                    style={{ 
                      width: `${Math.min(100, currentMetrics.network_usage || 0)}%`,
                      backgroundColor: getPerformanceStatus(currentMetrics.network_usage, alertThresholds.network).color
                    }}
                  ></div>
                </div>
                
                <div className="secondary-metrics">
                  <div className="secondary-metric">
                    <span className="label">In:</span>
                    <span className="value">{formatBytes(currentMetrics.network_in)}/s</span>
                  </div>
                  <div className="secondary-metric">
                    <span className="label">Out:</span>
                    <span className="value">{formatBytes(currentMetrics.network_out)}/s</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Storage Metrics */}
            <div className="metric-card storage">
              <div className="card-header">
                <span className="metric-icon">💾</span>
                <div className="metric-info">
                  <h4>Storage Usage</h4>
                  <span className="metric-description">Disk space utilization</span>
                </div>
                <span className="trend-icon">
                  {getTrendIcon(getTrendDirection(currentMetrics.storage_usage, previousMetrics.storage_usage))}
                </span>
              </div>
              
              <div className="metric-value-section">
                <div className="primary-value">
                  <span className="value">{formatValue(currentMetrics.storage_usage, 'percentage')}</span>
                  <div 
                    className="value-bar"
                    style={{ 
                      width: `${Math.min(100, currentMetrics.storage_usage || 0)}%`,
                      backgroundColor: getPerformanceStatus(currentMetrics.storage_usage, alertThresholds.storage).color
                    }}
                  ></div>
                </div>
                
                <div className="secondary-metrics">
                  <div className="secondary-metric">
                    <span className="label">Used:</span>
                    <span className="value">{formatBytes(currentMetrics.storage_used)}</span>
                  </div>
                  <div className="secondary-metric">
                    <span className="label">Free:</span>
                    <span className="value">{formatBytes(currentMetrics.storage_free)}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Response Time Metrics */}
            <div className="metric-card response-time">
              <div className="card-header">
                <span className="metric-icon">⚡</span>
                <div className="metric-info">
                  <h4>Response Time</h4>
                  <span className="metric-description">System responsiveness</span>
                </div>
                <span className="trend-icon">
                  {getTrendIcon(getTrendDirection(currentMetrics.avg_response_time, previousMetrics.avg_response_time), true)}
                </span>
              </div>
              
              <div className="metric-value-section">
                <div className="primary-value">
                  <span className="value">{formatValue(currentMetrics.avg_response_time, 'time')}</span>
                  <div 
                    className="value-bar"
                    style={{ 
                      width: `${Math.min(100, (currentMetrics.avg_response_time || 0) / 10)}%`,
                      backgroundColor: getPerformanceStatus(currentMetrics.avg_response_time, alertThresholds.response_time).color
                    }}
                  ></div>
                </div>
                
                <div className="secondary-metrics">
                  <div className="secondary-metric">
                    <span className="label">Min:</span>
                    <span className="value">{formatValue(currentMetrics.min_response_time, 'time')}</span>
                  </div>
                  <div className="secondary-metric">
                    <span className="label">Max:</span>
                    <span className="value">{formatValue(currentMetrics.max_response_time, 'time')}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Enterprise Specific Metrics */}
            <div className="metric-card enterprise">
              <div className="card-header">
                <span className="metric-icon">🏢</span>
                <div className="metric-info">
                  <h4>Enterprise Metrics</h4>
                  <span className="metric-description">Business system performance</span>
                </div>
              </div>
              
              <div className="enterprise-metrics">
                <div className="enterprise-metric">
                  <span className="metric-name">Active Agents</span>
                  <span className="metric-value">{currentMetrics.active_agents || 0}</span>
                </div>
                <div className="enterprise-metric">
                  <span className="metric-name">Workflows/min</span>
                  <span className="metric-value">{currentMetrics.workflows_per_minute || 0}</span>
                </div>
                <div className="enterprise-metric">
                  <span className="metric-name">DB Queries/s</span>
                  <span className="metric-value">{currentMetrics.db_queries_per_second || 0}</span>
                </div>
                <div className="enterprise-metric">
                  <span className="metric-name">API Calls/min</span>
                  <span className="metric-value">{currentMetrics.api_calls_per_minute || 0}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {viewMode === 'detailed' && (
          <div className="detailed-metrics">
            <div className="metrics-table">
              <div className="table-header">
                <h4>Detailed System Metrics</h4>
                <span className="last-updated">Last updated: {new Date().toLocaleTimeString()}</span>
              </div>
              
              <div className="metrics-grid">
                {Object.entries(currentMetrics).map(([key, value]) => {
                  const previous = previousMetrics[key];
                  const trend = getTrendDirection(value, previous);
                  
                  return (
                    <div key={key} className="detailed-metric">
                      <div className="metric-name">{key.replace(/_/g, ' ').toUpperCase()}</div>
                      <div className="metric-value">
                        <span className="current-value">{value}</span>
                        {previous && (
                          <span className={`trend ${trend}`}>
                            {trend === 'up' ? '↗' : trend === 'down' ? '↘' : '→'}
                            {Math.abs(((value - previous) / previous * 100)).toFixed(1)}%
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {viewMode === 'trends' && (
          <div className="trends-view">
            <div className="trends-header">
              <h4>Performance Trends</h4>
              <div className="trend-controls">
                <div className="metric-selector">
                  {['cpu', 'memory', 'network', 'storage', 'response_time'].map(metric => (
                    <label key={metric} className="metric-checkbox">
                      <input
                        type="checkbox"
                        checked={selectedMetrics.includes(metric)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedMetrics([...selectedMetrics, metric]);
                          } else {
                            setSelectedMetrics(selectedMetrics.filter(m => m !== metric));
                          }
                        }}
                      />
                      <span className="metric-label">{metric.toUpperCase()}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="trends-charts">
              <div className="chart-placeholder">
                <span className="placeholder-icon">📈</span>
                <h4>Performance Trend Charts</h4>
                <p>Historical performance data visualization for {timeRange}</p>
                <p>Selected metrics: {selectedMetrics.join(', ')}</p>
              </div>
            </div>
          </div>
        )}

        {viewMode === 'alerts' && (
          <div className="alerts-config">
            <div className="config-header">
              <h4>Performance Alert Thresholds</h4>
              <p>Configure warning and critical thresholds for system metrics</p>
            </div>
            
            <div className="threshold-settings">
              {Object.entries(alertThresholds).map(([metric, threshold]) => (
                <div key={metric} className="threshold-setting">
                  <label className="threshold-label">
                    {metric.replace(/_/g, ' ').toUpperCase()}
                  </label>
                  <div className="threshold-controls">
                    <input
                      type="range"
                      min="0"
                      max={metric === 'response_time' ? '5000' : '100'}
                      value={threshold}
                      onChange={(e) => setAlertThresholds({
                        ...alertThresholds,
                        [metric]: parseInt(e.target.value)
                      })}
                      className="threshold-slider"
                    />
                    <span className="threshold-value">
                      {formatValue(threshold, metric === 'response_time' ? 'time' : 'percentage')}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="config-actions">
              <button 
                className="config-btn save"
                onClick={() => onPerformanceAction('save_thresholds', alertThresholds)}
              >
                💾 Save Thresholds
              </button>
              <button 
                className="config-btn reset"
                onClick={() => setAlertThresholds({
                  cpu: 80,
                  memory: 85,
                  network: 90,
                  storage: 80,
                  response_time: 1000
                })}
              >
                🔄 Reset to Defaults
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Real-time indicator */}
      <div className="metrics-realtime-indicator">
        <span className="indicator-dot"></span>
        <span className="indicator-text">Live Performance Monitoring</span>
        <span className="update-frequency">Updates every 5s</span>
      </div>

      {/* Performance alerts */}
      {emergencyMode && healthScore < 60 && (
        <div className="performance-alert-banner">
          <div className="alert-content">
            <span className="alert-icon">⚠️</span>
            <span className="alert-text">
              SYSTEM PERFORMANCE DEGRADED - Health Score: {healthScore}%
            </span>
            <button 
              className="alert-action"
              onClick={() => onPerformanceAction('emergency_optimize')}
            >
              OPTIMIZE NOW
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SystemPerformanceMetrics;
