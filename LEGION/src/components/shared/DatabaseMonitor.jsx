import React, { useState, useEffect } from 'react';

/**
 * DatabaseMonitor - Real-time database connection status and health monitoring
 * 
 * Monitors all enterprise database connections, displays health metrics,
 * connection pools, and provides database management capabilities.
 */
const DatabaseMonitor = ({ 
  databases = [], 
  connectionStats = {},
  emergencyMode = false,
  onDatabaseAction = () => {} 
}) => {
  const [selectedDatabase, setSelectedDatabase] = useState(null);
  const [viewMode, setViewMode] = useState('overview'); // 'overview', 'connections', 'performance', 'queries'
  const [refreshInterval, setRefreshInterval] = useState(5000); // 5 seconds
  const [sortBy, setSortBy] = useState('status'); // 'status', 'connections', 'latency', 'name'

  // Filter and sort databases
  const sortedDatabases = [...databases].sort((a, b) => {
    switch (sortBy) {
      case 'status':
        const statusOrder = { connected: 3, warning: 2, disconnected: 1, error: 0 };
        return (statusOrder[b.status] || 0) - (statusOrder[a.status] || 0);
      case 'connections':
        return (b.connections?.active || 0) - (a.connections?.active || 0);
      case 'latency':
        return (a.performance?.latency || 0) - (b.performance?.latency || 0);
      case 'name':
        return a.name.localeCompare(b.name);
      default:
        return 0;
    }
  });

  // Get database status information
  const getStatusInfo = (status) => {
    switch (status) {
      case 'connected':
        return {
          color: 'connected',
          icon: '✅',
          text: 'Connected',
          bgColor: 'rgba(40, 167, 69, 0.1)',
          borderColor: '#28a745'
        };
      case 'warning':
        return {
          color: 'warning',
          icon: '⚠️',
          text: 'Warning',
          bgColor: 'rgba(255, 193, 7, 0.1)',
          borderColor: '#ffc107'
        };
      case 'disconnected':
        return {
          color: 'disconnected',
          icon: '🔌',
          text: 'Disconnected',
          bgColor: 'rgba(108, 117, 125, 0.1)',
          borderColor: '#6c757d'
        };
      case 'error':
        return {
          color: 'error',
          icon: '❌',
          text: 'Error',
          bgColor: 'rgba(220, 53, 69, 0.1)',
          borderColor: '#dc3545'
        };
      default:
        return {
          color: 'unknown',
          icon: '❓',
          text: 'Unknown',
          bgColor: 'rgba(108, 117, 125, 0.1)',
          borderColor: '#6c757d'
        };
    }
  };

  // Get database type icon
  const getTypeIcon = (type) => {
    switch (type) {
      case 'sqlite': return '📁';
      case 'postgresql': return '🐘';
      case 'mysql': return '🐬';
      case 'mongodb': return '🍃';
      case 'redis': return '🔴';
      case 'elasticsearch': return '🔍';
      default: return '🗄️';
    }
  };

  // Format time duration
  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  // Format bytes
  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Calculate overall system health
  const systemHealth = {
    total: databases.length,
    connected: databases.filter(db => db.status === 'connected').length,
    warning: databases.filter(db => db.status === 'warning').length,
    disconnected: databases.filter(db => db.status === 'disconnected').length,
    error: databases.filter(db => db.status === 'error').length,
    totalConnections: databases.reduce((sum, db) => sum + (db.connections?.active || 0), 0),
    avgLatency: databases.length > 0 
      ? databases.reduce((sum, db) => sum + (db.performance?.latency || 0), 0) / databases.length 
      : 0
  };

  // Handle database actions
  const handleConnect = (dbName) => {
    onDatabaseAction(dbName, 'connect');
  };

  const handleDisconnect = (dbName) => {
    onDatabaseAction(dbName, 'disconnect');
  };

  const handleReconnect = (dbName) => {
    onDatabaseAction(dbName, 'reconnect');
  };

  const handleOptimize = (dbName) => {
    onDatabaseAction(dbName, 'optimize');
  };

  const handleBackup = (dbName) => {
    onDatabaseAction(dbName, 'backup');
  };

  return (
    <div className={`database-monitor ${emergencyMode ? 'emergency' : ''}`}>
      <div className="monitor-header">
        <div className="header-left">
          <h3 className="monitor-title">
            <span className="title-icon">🗄️</span>
            Database Monitor
          </h3>
          <div className="system-health-summary">
            <div className="health-stat connected">
              <span className="stat-value">{systemHealth.connected}</span>
              <span className="stat-label">Connected</span>
            </div>
            <div className="health-stat warning">
              <span className="stat-value">{systemHealth.warning}</span>
              <span className="stat-label">Warning</span>
            </div>
            <div className="health-stat error">
              <span className="stat-value">{systemHealth.error + systemHealth.disconnected}</span>
              <span className="stat-label">Issues</span>
            </div>
            <div className="health-stat connections">
              <span className="stat-value">{systemHealth.totalConnections}</span>
              <span className="stat-label">Connections</span>
            </div>
            <div className="health-stat latency">
              <span className="stat-value">{Math.round(systemHealth.avgLatency)}ms</span>
              <span className="stat-label">Avg Latency</span>
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
              <option value="connections">Connections</option>
              <option value="performance">Performance</option>
              <option value="queries">Active Queries</option>
            </select>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="sort-select"
            >
              <option value="status">Sort by Status</option>
              <option value="connections">Sort by Connections</option>
              <option value="latency">Sort by Latency</option>
              <option value="name">Sort by Name</option>
            </select>

            <select
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(parseInt(e.target.value))}
              className="refresh-select"
            >
              <option value="1000">1s refresh</option>
              <option value="5000">5s refresh</option>
              <option value="10000">10s refresh</option>
              <option value="30000">30s refresh</option>
            </select>
          </div>

          <div className="action-controls">
            <button 
              className="action-btn optimize-all"
              onClick={() => databases.forEach(db => handleOptimize(db.name))}
              disabled={systemHealth.connected === 0}
            >
              🔧 Optimize All
            </button>
            
            <button 
              className="action-btn backup-all"
              onClick={() => databases.forEach(db => handleBackup(db.name))}
              disabled={systemHealth.connected === 0}
            >
              💾 Backup All
            </button>
          </div>
        </div>
      </div>

      <div className="monitor-content">
        {viewMode === 'overview' && (
          <div className="databases-grid">
            {sortedDatabases.map((database) => {
              const statusInfo = getStatusInfo(database.status);
              
              return (
                <div
                  key={database.name}
                  className={`database-card ${statusInfo.color}`}
                  style={{ 
                    background: statusInfo.bgColor,
                    borderColor: statusInfo.borderColor 
                  }}
                  onClick={() => setSelectedDatabase(database)}
                >
                  <div className="card-header">
                    <div className="database-identity">
                      <span className="type-icon">{getTypeIcon(database.type)}</span>
                      <div className="identity-text">
                        <h4 className="database-name">{database.name}</h4>
                        <span className="database-type">{database.type.toUpperCase()}</span>
                      </div>
                    </div>
                    
                    <div className="status-indicator">
                      <span className="status-icon">{statusInfo.icon}</span>
                      <span className="status-text">{statusInfo.text}</span>
                    </div>
                  </div>

                  <div className="card-metrics">
                    <div className="metric-row">
                      <div className="metric">
                        <span className="metric-label">Connections</span>
                        <span className="metric-value">
                          {database.connections?.active || 0}/{database.connections?.max || 0}
                        </span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">Latency</span>
                        <span className="metric-value">{database.performance?.latency || 0}ms</span>
                      </div>
                    </div>
                    
                    <div className="metric-row">
                      <div className="metric">
                        <span className="metric-label">Queries/sec</span>
                        <span className="metric-value">{database.performance?.qps || 0}</span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">Uptime</span>
                        <span className="metric-value">
                          {formatDuration(database.uptime || 0)}
                        </span>
                      </div>
                    </div>

                    {database.storage && (
                      <div className="metric-row">
                        <div className="metric full-width">
                          <span className="metric-label">Storage</span>
                          <div className="storage-bar">
                            <div 
                              className="storage-fill"
                              style={{ 
                                width: `${(database.storage.used / database.storage.total) * 100}%`,
                                background: database.storage.used / database.storage.total > 0.8 ? '#dc3545' : '#28a745'
                              }}
                            ></div>
                            <span className="storage-text">
                              {formatBytes(database.storage.used)} / {formatBytes(database.storage.total)}
                            </span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="card-actions">
                    {database.status === 'connected' ? (
                      <button 
                        className="card-action-btn disconnect"
                        onClick={(e) => { e.stopPropagation(); handleDisconnect(database.name); }}
                      >
                        🔌 Disconnect
                      </button>
                    ) : (
                      <button 
                        className="card-action-btn connect"
                        onClick={(e) => { e.stopPropagation(); handleConnect(database.name); }}
                      >
                        ⚡ Connect
                      </button>
                    )}
                    
                    <button 
                      className="card-action-btn reconnect"
                      onClick={(e) => { e.stopPropagation(); handleReconnect(database.name); }}
                    >
                      🔄 Reconnect
                    </button>
                    
                    <button 
                      className="card-action-btn optimize"
                      onClick={(e) => { e.stopPropagation(); handleOptimize(database.name); }}
                      disabled={database.status !== 'connected'}
                    >
                      🔧 Optimize
                    </button>
                  </div>

                  {database.lastError && (
                    <div className="card-error">
                      <span className="error-icon">⚠️</span>
                      <span className="error-text">{database.lastError}</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {viewMode === 'connections' && (
          <div className="connections-view">
            <div className="connections-header">
              <h4>Active Database Connections</h4>
              <div className="connection-summary">
                Total: {systemHealth.totalConnections} active connections across {systemHealth.connected} databases
              </div>
            </div>
            
            <div className="connections-list">
              {sortedDatabases
                .filter(db => db.connections?.details)
                .map(database => (
                  <div key={database.name} className="connection-group">
                    <div className="group-header">
                      <span className="db-icon">{getTypeIcon(database.type)}</span>
                      <span className="db-name">{database.name}</span>
                      <span className="connection-count">
                        {database.connections.active}/{database.connections.max} connections
                      </span>
                    </div>
                    
                    <div className="connection-details">
                      {database.connections.details.map((conn, idx) => (
                        <div key={idx} className="connection-item">
                          <div className="conn-info">
                            <span className="conn-id">#{conn.id}</span>
                            <span className="conn-client">{conn.client}</span>
                            <span className="conn-duration">{formatDuration(conn.duration)}</span>
                          </div>
                          <div className="conn-status">
                            <span className={`conn-state ${conn.state}`}>{conn.state}</span>
                            {conn.query && <span className="conn-query">{conn.query}</span>}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))
              }
            </div>
          </div>
        )}

        {viewMode === 'performance' && (
          <div className="performance-view">
            <div className="performance-metrics">
              {sortedDatabases.map(database => (
                <div key={database.name} className="performance-card">
                  <div className="perf-header">
                    <span className="db-icon">{getTypeIcon(database.type)}</span>
                    <span className="db-name">{database.name}</span>
                    <span className={`status-badge ${getStatusInfo(database.status).color}`}>
                      {getStatusInfo(database.status).text}
                    </span>
                  </div>
                  
                  <div className="perf-metrics">
                    <div className="metric-grid">
                      <div className="perf-metric">
                        <span className="metric-name">Latency</span>
                        <span className="metric-value">{database.performance?.latency || 0}ms</span>
                      </div>
                      <div className="perf-metric">
                        <span className="metric-name">Throughput</span>
                        <span className="metric-value">{database.performance?.qps || 0} QPS</span>
                      </div>
                      <div className="perf-metric">
                        <span className="metric-name">CPU Usage</span>
                        <span className="metric-value">{database.performance?.cpu || 0}%</span>
                      </div>
                      <div className="perf-metric">
                        <span className="metric-name">Memory</span>
                        <span className="metric-value">{database.performance?.memory || 0}%</span>
                      </div>
                    </div>
                    
                    {database.performance?.slowQueries && (
                      <div className="slow-queries">
                        <span className="slow-queries-label">Slow Queries: {database.performance.slowQueries}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {viewMode === 'queries' && (
          <div className="queries-view">
            <div className="queries-header">
              <h4>Active Queries</h4>
              <div className="query-summary">
                Monitoring real-time database query execution
              </div>
            </div>
            
            <div className="queries-list">
              {sortedDatabases
                .filter(db => db.activeQueries && db.activeQueries.length > 0)
                .map(database => (
                  <div key={database.name} className="query-group">
                    <div className="group-header">
                      <span className="db-icon">{getTypeIcon(database.type)}</span>
                      <span className="db-name">{database.name}</span>
                      <span className="query-count">{database.activeQueries.length} active</span>
                    </div>
                    
                    <div className="query-details">
                      {database.activeQueries.map((query, idx) => (
                        <div key={idx} className="query-item">
                          <div className="query-header">
                            <span className="query-id">#{query.id}</span>
                            <span className="query-duration">{formatDuration(query.duration)}</span>
                            <span className={`query-type ${query.type}`}>{query.type}</span>
                          </div>
                          <div className="query-sql">
                            <code>{query.sql}</code>
                          </div>
                          {query.progress && (
                            <div className="query-progress">
                              <div className="progress-bar">
                                <div 
                                  className="progress-fill"
                                  style={{ width: `${query.progress}%` }}
                                ></div>
                              </div>
                              <span className="progress-text">{query.progress}%</span>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))
              }
              
              {sortedDatabases.every(db => !db.activeQueries || db.activeQueries.length === 0) && (
                <div className="no-queries">
                  <span className="no-queries-icon">⚡</span>
                  <h4>No Active Queries</h4>
                  <p>All databases are idle or queries are executing too quickly to display.</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Real-time indicator */}
      <div className="monitor-realtime-indicator">
        <span className="indicator-dot"></span>
        <span className="indicator-text">Live Database Monitoring</span>
        <span className="refresh-rate">Refresh: {refreshInterval / 1000}s</span>
      </div>

      {/* Emergency banner for critical database issues */}
      {emergencyMode && systemHealth.error > 0 && (
        <div className="emergency-db-banner">
          <div className="emergency-content">
            <span className="emergency-icon">🚨</span>
            <span className="emergency-text">
              {systemHealth.error} DATABASE{systemHealth.error !== 1 ? 'S' : ''} IN CRITICAL STATE
            </span>
            <button 
              className="emergency-action"
              onClick={() => {
                databases
                  .filter(db => db.status === 'error')
                  .forEach(db => handleReconnect(db.name));
              }}
            >
              RECONNECT ALL
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DatabaseMonitor;
