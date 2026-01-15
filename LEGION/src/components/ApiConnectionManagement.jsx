// components/ApiConnectionManagement.jsx

import React, { useState, useEffect } from 'react';

const ApiConnectionManagement = () => {
  const [connectionData, setConnectionData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedConnection, setSelectedConnection] = useState(null);
  const [viewMode, setViewMode] = useState('overview'); // overview, connections, pools, settings
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [showConnectionModal, setShowConnectionModal] = useState(false);
  const [connectionAction, setConnectionAction] = useState(null);

  // Generate comprehensive connection management data
  const generateConnectionData = () => {
    const connections = [
      {
        id: 'conn_coingecko_primary',
        name: 'CoinGecko Primary Connection',
        apiId: 'coingecko',
        apiName: 'CoinGecko API',
        status: 'active',
        connectionType: 'HTTPS',
        endpoint: 'https://api.coingecko.com/api/v3',
        region: 'US-East',
        priority: 1,
        maxConnections: 100,
        currentConnections: 45,
        connectionPool: 'financial_primary',
        created: '2024-12-15T10:30:00Z',
        lastActivity: new Date(Date.now() - 30000).toISOString(),
        performance: {
          avgResponseTime: 245,
          successRate: 99.88,
          requestsPerMinute: 52.4,
          errorRate: 0.12,
          bandwidth: 2.3, // MB/min
          uptime: 99.95
        },
        health: {
          score: 98.2,
          status: 'excellent',
          lastHealthCheck: new Date(Date.now() - 15000).toISOString(),
          issues: []
        },
        security: {
          tlsVersion: 'TLS 1.3',
          certificateValid: true,
          certificateExpiry: '2025-12-15T00:00:00Z',
          authMethod: 'bearer_token',
          lastSecurityCheck: new Date(Date.now() - 300000).toISOString()
        },
        configuration: {
          timeout: 5000,
          retries: 3,
          backoffStrategy: 'exponential',
          rateLimitPerMinute: 60,
          keepAliveTimeout: 30000,
          enableCompression: true,
          enableCaching: true,
          cacheTimeout: 300
        },
        metrics: {
          totalRequests24h: 75428,
          averageLatency: 245,
          p95Latency: 420,
          p99Latency: 650,
          errorsLast24h: 91,
          timeouts: 5,
          retries: 23
        }
      },
      {
        id: 'conn_coingecko_backup',
        name: 'CoinGecko Backup Connection',
        apiId: 'coingecko',
        apiName: 'CoinGecko API',
        status: 'standby',
        connectionType: 'HTTPS',
        endpoint: 'https://api-backup.coingecko.com/api/v3',
        region: 'EU-West',
        priority: 2,
        maxConnections: 50,
        currentConnections: 0,
        connectionPool: 'financial_backup',
        created: '2024-12-15T10:35:00Z',
        lastActivity: new Date(Date.now() - 3600000).toISOString(),
        performance: {
          avgResponseTime: 0,
          successRate: 100,
          requestsPerMinute: 0,
          errorRate: 0,
          bandwidth: 0,
          uptime: 100
        },
        health: {
          score: 100,
          status: 'excellent',
          lastHealthCheck: new Date(Date.now() - 30000).toISOString(),
          issues: []
        },
        security: {
          tlsVersion: 'TLS 1.3',
          certificateValid: true,
          certificateExpiry: '2025-12-15T00:00:00Z',
          authMethod: 'bearer_token',
          lastSecurityCheck: new Date(Date.now() - 300000).toISOString()
        },
        configuration: {
          timeout: 5000,
          retries: 3,
          backoffStrategy: 'exponential',
          rateLimitPerMinute: 60,
          keepAliveTimeout: 30000,
          enableCompression: true,
          enableCaching: true,
          cacheTimeout: 300
        },
        metrics: {
          totalRequests24h: 0,
          averageLatency: 0,
          p95Latency: 0,
          p99Latency: 0,
          errorsLast24h: 0,
          timeouts: 0,
          retries: 0
        }
      },
      {
        id: 'conn_polygon_primary',
        name: 'Polygon.io Primary Connection',
        apiId: 'polygon',
        apiName: 'Polygon.io API',
        status: 'active',
        connectionType: 'HTTPS',
        endpoint: 'https://api.polygon.io',
        region: 'US-West',
        priority: 1,
        maxConnections: 80,
        currentConnections: 32,
        connectionPool: 'financial_primary',
        created: '2024-12-15T10:32:00Z',
        lastActivity: new Date(Date.now() - 45000).toISOString(),
        performance: {
          avgResponseTime: 425,
          successRate: 99.72,
          requestsPerMinute: 33.5,
          errorRate: 0.28,
          bandwidth: 1.8,
          uptime: 99.85
        },
        health: {
          score: 95.1,
          status: 'good',
          lastHealthCheck: new Date(Date.now() - 20000).toISOString(),
          issues: [
            {
              type: 'performance',
              severity: 'low',
              message: 'Slight increase in response time',
              detected: new Date(Date.now() - 7200000).toISOString()
            }
          ]
        },
        security: {
          tlsVersion: 'TLS 1.2',
          certificateValid: true,
          certificateExpiry: '2025-11-30T00:00:00Z',
          authMethod: 'api_key',
          lastSecurityCheck: new Date(Date.now() - 300000).toISOString()
        },
        configuration: {
          timeout: 8000,
          retries: 3,
          backoffStrategy: 'linear',
          rateLimitPerMinute: 45,
          keepAliveTimeout: 60000,
          enableCompression: true,
          enableCaching: true,
          cacheTimeout: 180
        },
        metrics: {
          totalRequests24h: 48265,
          averageLatency: 425,
          p95Latency: 750,
          p99Latency: 980,
          errorsLast24h: 135,
          timeouts: 8,
          retries: 42
        }
      },
      {
        id: 'conn_alpha_vantage',
        name: 'Alpha Vantage Connection',
        apiId: 'alpha_vantage',
        apiName: 'Alpha Vantage API',
        status: 'degraded',
        connectionType: 'HTTPS',
        endpoint: 'https://www.alphavantage.co',
        region: 'US-East',
        priority: 1,
        maxConnections: 25,
        currentConnections: 8,
        connectionPool: 'financial_primary',
        created: '2024-12-15T10:38:00Z',
        lastActivity: new Date(Date.now() - 120000).toISOString(),
        performance: {
          avgResponseTime: 1240,
          successRate: 97.2,
          requestsPerMinute: 10.3,
          errorRate: 2.8,
          bandwidth: 0.8,
          uptime: 97.85
        },
        health: {
          score: 71.4,
          status: 'warning',
          lastHealthCheck: new Date(Date.now() - 45000).toISOString(),
          issues: [
            {
              type: 'performance',
              severity: 'high',
              message: 'High response times detected',
              detected: new Date(Date.now() - 14400000).toISOString()
            },
            {
              type: 'rate_limit',
              severity: 'medium',
              message: 'Approaching rate limit threshold',
              detected: new Date(Date.now() - 7200000).toISOString()
            }
          ]
        },
        security: {
          tlsVersion: 'TLS 1.2',
          certificateValid: true,
          certificateExpiry: '2026-01-15T00:00:00Z',
          authMethod: 'api_key',
          lastSecurityCheck: new Date(Date.now() - 300000).toISOString()
        },
        configuration: {
          timeout: 15000,
          retries: 5,
          backoffStrategy: 'exponential',
          rateLimitPerMinute: 12,
          keepAliveTimeout: 45000,
          enableCompression: false,
          enableCaching: true,
          cacheTimeout: 600
        },
        metrics: {
          totalRequests24h: 14847,
          averageLatency: 1240,
          p95Latency: 2100,
          p99Latency: 2800,
          errorsLast24h: 415,
          timeouts: 28,
          retries: 89
        }
      },
      {
        id: 'conn_virustotal',
        name: 'VirusTotal Connection',
        apiId: 'virustotal',
        apiName: 'VirusTotal API',
        status: 'active',
        connectionType: 'HTTPS',
        endpoint: 'https://www.virustotal.com',
        region: 'Global-CDN',
        priority: 1,
        maxConnections: 60,
        currentConnections: 18,
        connectionPool: 'security_primary',
        created: '2024-12-15T10:40:00Z',
        lastActivity: new Date(Date.now() - 25000).toISOString(),
        performance: {
          avgResponseTime: 680,
          successRate: 99.55,
          requestsPerMinute: 14.8,
          errorRate: 0.45,
          bandwidth: 1.2,
          uptime: 99.65
        },
        health: {
          score: 94.8,
          status: 'good',
          lastHealthCheck: new Date(Date.now() - 12000).toISOString(),
          issues: []
        },
        security: {
          tlsVersion: 'TLS 1.3',
          certificateValid: true,
          certificateExpiry: '2025-10-20T00:00:00Z',
          authMethod: 'api_key',
          lastSecurityCheck: new Date(Date.now() - 300000).toISOString()
        },
        configuration: {
          timeout: 10000,
          retries: 3,
          backoffStrategy: 'exponential',
          rateLimitPerMinute: 20,
          keepAliveTimeout: 30000,
          enableCompression: true,
          enableCaching: true,
          cacheTimeout: 900
        },
        metrics: {
          totalRequests24h: 21312,
          averageLatency: 680,
          p95Latency: 950,
          p99Latency: 1100,
          errorsLast24h: 96,
          timeouts: 3,
          retries: 18
        }
      },
      {
        id: 'conn_newsapi_failed',
        name: 'NewsAPI Connection',
        apiId: 'newsapi',
        apiName: 'NewsAPI',
        status: 'failed',
        connectionType: 'HTTPS',
        endpoint: 'https://newsapi.org',
        region: 'Global-CDN',
        priority: 1,
        maxConnections: 30,
        currentConnections: 0,
        connectionPool: 'content_primary',
        created: '2024-12-15T10:42:00Z',
        lastActivity: new Date(Date.now() - 1800000).toISOString(),
        performance: {
          avgResponseTime: 0,
          successRate: 0,
          requestsPerMinute: 0,
          errorRate: 100,
          bandwidth: 0,
          uptime: 91.3
        },
        health: {
          score: 0,
          status: 'critical',
          lastHealthCheck: new Date(Date.now() - 60000).toISOString(),
          issues: [
            {
              type: 'connection',
              severity: 'critical',
              message: 'Connection timeout - service unavailable',
              detected: new Date(Date.now() - 3600000).toISOString()
            },
            {
              type: 'service',
              severity: 'critical',
              message: 'HTTP 500 errors from API endpoint',
              detected: new Date(Date.now() - 3600000).toISOString()
            }
          ]
        },
        security: {
          tlsVersion: 'TLS 1.2',
          certificateValid: true,
          certificateExpiry: '2025-08-15T00:00:00Z',
          authMethod: 'api_key',
          lastSecurityCheck: new Date(Date.now() - 300000).toISOString()
        },
        configuration: {
          timeout: 12000,
          retries: 3,
          backoffStrategy: 'exponential',
          rateLimitPerMinute: 30,
          keepAliveTimeout: 30000,
          enableCompression: true,
          enableCaching: true,
          cacheTimeout: 300
        },
        metrics: {
          totalRequests24h: 0,
          averageLatency: 0,
          p95Latency: 0,
          p99Latency: 0,
          errorsLast24h: 1247,
          timeouts: 847,
          retries: 2541
        }
      }
    ];

    const pools = [
      {
        id: 'financial_primary',
        name: 'Financial APIs Primary Pool',
        connections: connections.filter(c => c.connectionPool === 'financial_primary'),
        status: 'healthy',
        totalConnections: 225,
        activeConnections: 85,
        maxCapacity: 300,
        utilizationPercent: 37.8,
        loadBalancingStrategy: 'least_connections',
        healthCheckInterval: 30,
        created: '2024-12-15T10:00:00Z'
      },
      {
        id: 'financial_backup',
        name: 'Financial APIs Backup Pool',
        connections: connections.filter(c => c.connectionPool === 'financial_backup'),
        status: 'standby',
        totalConnections: 50,
        activeConnections: 0,
        maxCapacity: 100,
        utilizationPercent: 0,
        loadBalancingStrategy: 'round_robin',
        healthCheckInterval: 60,
        created: '2024-12-15T10:05:00Z'
      },
      {
        id: 'security_primary',
        name: 'Security APIs Primary Pool',
        connections: connections.filter(c => c.connectionPool === 'security_primary'),
        status: 'healthy',
        totalConnections: 60,
        activeConnections: 18,
        maxCapacity: 120,
        utilizationPercent: 30.0,
        loadBalancingStrategy: 'weighted_round_robin',
        healthCheckInterval: 30,
        created: '2024-12-15T10:10:00Z'
      },
      {
        id: 'content_primary',
        name: 'Content APIs Primary Pool',
        connections: connections.filter(c => c.connectionPool === 'content_primary'),
        status: 'critical',
        totalConnections: 30,
        activeConnections: 0,
        maxCapacity: 60,
        utilizationPercent: 0,
        loadBalancingStrategy: 'least_response_time',
        healthCheckInterval: 15,
        created: '2024-12-15T10:15:00Z'
      }
    ];

    const summary = {
      totalConnections: connections.length,
      activeConnections: connections.filter(c => c.status === 'active').length,
      standbyConnections: connections.filter(c => c.status === 'standby').length,
      failedConnections: connections.filter(c => c.status === 'failed').length,
      degradedConnections: connections.filter(c => c.status === 'degraded').length,
      totalPools: pools.length,
      healthyPools: pools.filter(p => p.status === 'healthy').length,
      criticalPools: pools.filter(p => p.status === 'critical').length,
      totalCapacity: pools.reduce((sum, pool) => sum + pool.maxCapacity, 0),
      currentUtilization: pools.reduce((sum, pool) => sum + pool.activeConnections, 0),
      avgResponseTime: Math.round(connections.filter(c => c.status === 'active').reduce((sum, c) => sum + c.performance.avgResponseTime, 0) / connections.filter(c => c.status === 'active').length),
      totalRequests24h: connections.reduce((sum, c) => sum + c.metrics.totalRequests24h, 0),
      totalErrors24h: connections.reduce((sum, c) => sum + c.metrics.errorsLast24h, 0)
    };

    return {
      timestamp: new Date().toISOString(),
      connections,
      pools,
      summary
    };
  };

  useEffect(() => {
    const loadData = () => {
      setConnectionData(generateConnectionData());
      setLoading(false);
    };

    loadData();

    if (autoRefresh) {
      const interval = setInterval(loadData, 15000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return '#28a745';
      case 'standby': return '#17a2b8';
      case 'degraded': return '#ffc107';
      case 'failed': case 'critical': return '#dc3545';
      case 'healthy': return '#28a745';
      default: return '#6c757d';
    }
  };

  const getHealthScoreColor = (score) => {
    if (score >= 95) return '#28a745';
    if (score >= 85) return '#20c997';
    if (score >= 75) return '#17a2b8';
    if (score >= 65) return '#ffc107';
    if (score >= 50) return '#fd7e14';
    return '#dc3545';
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const handleConnectionAction = (connection, action) => {
    setSelectedConnection(connection);
    setConnectionAction(action);
    setShowConnectionModal(true);
  };

  if (loading) {
    return (
      <div className="api-connection-management loading">
        <div className="loading-spinner">
          <i className="fas fa-plug fa-pulse"></i>
          <p>Loading connection management...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="api-connection-management">
      <div className="connection-header">
        <div className="header-info">
          <h2>
            <i className="fas fa-plug"></i>
            API Connection Management
          </h2>
          <p>Comprehensive connection pool management, health monitoring, and configuration control</p>
        </div>

        <div className="header-controls">
          <div className="view-toggle">
            {['overview', 'connections', 'pools', 'settings'].map(mode => (
              <button
                key={mode}
                className={`view-btn ${viewMode === mode ? 'active' : ''}`}
                onClick={() => setViewMode(mode)}
              >
                {mode}
              </button>
            ))}
          </div>

          <div className="refresh-control">
            <label>
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
              />
              Auto Refresh
            </label>
          </div>
        </div>
      </div>

      <div className="connection-summary">
        <div className="summary-cards">
          <div className="summary-card total">
            <div className="card-icon">
              <i className="fas fa-network-wired"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{connectionData.summary.totalConnections}</div>
              <div className="card-label">Total Connections</div>
            </div>
          </div>

          <div className="summary-card active">
            <div className="card-icon">
              <i className="fas fa-check-circle"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{connectionData.summary.activeConnections}</div>
              <div className="card-label">Active Connections</div>
            </div>
          </div>

          <div className="summary-card utilization">
            <div className="card-icon">
              <i className="fas fa-chart-pie"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{Math.round((connectionData.summary.currentUtilization / connectionData.summary.totalCapacity) * 100)}%</div>
              <div className="card-label">Pool Utilization</div>
            </div>
          </div>

          <div className="summary-card response-time">
            <div className="card-icon">
              <i className="fas fa-clock"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{connectionData.summary.avgResponseTime}ms</div>
              <div className="card-label">Avg Response Time</div>
            </div>
          </div>

          <div className="summary-card requests">
            <div className="card-icon">
              <i className="fas fa-exchange-alt"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{formatNumber(connectionData.summary.totalRequests24h)}</div>
              <div className="card-label">Requests 24h</div>
            </div>
          </div>

          <div className="summary-card errors">
            <div className="card-icon">
              <i className="fas fa-exclamation-triangle"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{connectionData.summary.totalErrors24h}</div>
              <div className="card-label">Errors 24h</div>
            </div>
          </div>
        </div>
      </div>

      {viewMode === 'overview' && (
        <div className="overview-section">
          <div className="pools-overview">
            <h3>Connection Pools Overview</h3>
            <div className="pools-grid">
              {connectionData.pools.map(pool => (
                <div key={pool.id} className="pool-overview-card">
                  <div className="pool-header">
                    <div className="pool-info">
                      <h4>{pool.name}</h4>
                      <span className="pool-strategy">{pool.loadBalancingStrategy}</span>
                    </div>
                    <div 
                      className="pool-status"
                      style={{ color: getStatusColor(pool.status) }}
                    >
                      <i className={`fas fa-circle ${pool.status === 'healthy' ? 'fa-pulse' : ''}`}></i>
                      {pool.status}
                    </div>
                  </div>

                  <div className="pool-metrics">
                    <div className="pool-utilization">
                      <div className="utilization-bar">
                        <div 
                          className="utilization-fill"
                          style={{ 
                            width: `${pool.utilizationPercent}%`,
                            backgroundColor: getStatusColor(pool.status)
                          }}
                        ></div>
                      </div>
                      <div className="utilization-text">
                        {pool.activeConnections}/{pool.maxCapacity} ({pool.utilizationPercent}%)
                      </div>
                    </div>

                    <div className="pool-details">
                      <div className="pool-detail">
                        <span className="detail-label">Connections:</span>
                        <span className="detail-value">{pool.connections.length}</span>
                      </div>
                      <div className="pool-detail">
                        <span className="detail-label">Health Check:</span>
                        <span className="detail-value">{pool.healthCheckInterval}s</span>
                      </div>
                      <div className="pool-detail">
                        <span className="detail-label">Created:</span>
                        <span className="detail-value">{new Date(pool.created).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>

                  <div className="pool-actions">
                    <button className="pool-btn primary">Manage</button>
                    <button className="pool-btn secondary">Configure</button>
                    <button className="pool-btn tertiary">Monitor</button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="recent-activity">
            <h3>Recent Connection Activity</h3>
            <div className="activity-feed">
              {connectionData.connections
                .sort((a, b) => new Date(b.lastActivity) - new Date(a.lastActivity))
                .slice(0, 8)
                .map(connection => (
                  <div key={connection.id} className="activity-item">
                    <div className="activity-icon">
                      <i className={`fas ${connection.status === 'active' ? 'fa-check' : 
                                           connection.status === 'failed' ? 'fa-times' : 'fa-pause'}`}
                         style={{ color: getStatusColor(connection.status) }}></i>
                    </div>
                    <div className="activity-content">
                      <div className="activity-title">{connection.name}</div>
                      <div className="activity-description">
                        {connection.status === 'active' ? 'Processing requests' :
                         connection.status === 'failed' ? 'Connection failed' :
                         connection.status === 'degraded' ? 'Performance degraded' : 'On standby'}
                      </div>
                    </div>
                    <div className="activity-time">
                      {new Date(connection.lastActivity).toLocaleTimeString()}
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}

      {viewMode === 'connections' && (
        <div className="connections-section">
          <div className="connections-header">
            <h3>All Connections</h3>
            <div className="connections-actions">
              <button className="action-btn primary">
                <i className="fas fa-plus"></i>
                Add Connection
              </button>
              <button className="action-btn secondary">
                <i className="fas fa-sync"></i>
                Test All
              </button>
            </div>
          </div>

          <div className="connections-grid">
            {connectionData.connections.map(connection => (
              <div key={connection.id} className="connection-card">
                <div className="connection-header">
                  <div className="connection-info">
                    <h4>{connection.name}</h4>
                    <span className="connection-endpoint">{connection.endpoint}</span>
                    <span className="connection-region">{connection.region}</span>
                  </div>
                  <div 
                    className="connection-status"
                    style={{ color: getStatusColor(connection.status) }}
                  >
                    <i className={`fas fa-circle ${connection.status === 'active' ? 'fa-pulse' : ''}`}></i>
                    {connection.status}
                  </div>
                </div>

                <div className="connection-metrics">
                  <div className="metrics-row">
                    <div className="metric">
                      <span className="metric-label">Response Time:</span>
                      <span className="metric-value">{connection.performance.avgResponseTime}ms</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Success Rate:</span>
                      <span className="metric-value">{connection.performance.successRate}%</span>
                    </div>
                  </div>
                  <div className="metrics-row">
                    <div className="metric">
                      <span className="metric-label">Connections:</span>
                      <span className="metric-value">{connection.currentConnections}/{connection.maxConnections}</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Health Score:</span>
                      <span 
                        className="metric-value"
                        style={{ color: getHealthScoreColor(connection.health.score) }}
                      >
                        {connection.health.score}/100
                      </span>
                    </div>
                  </div>
                </div>

                <div className="connection-usage">
                  <div className="usage-bar">
                    <div 
                      className="usage-fill"
                      style={{ 
                        width: `${(connection.currentConnections / connection.maxConnections) * 100}%`,
                        backgroundColor: getStatusColor(connection.status)
                      }}
                    ></div>
                  </div>
                </div>

                {connection.health.issues.length > 0 && (
                  <div className="connection-issues">
                    <div className="issues-header">Issues:</div>
                    {connection.health.issues.slice(0, 2).map((issue, index) => (
                      <div key={index} className="issue-item">
                        <span className={`issue-severity ${issue.severity}`}>
                          {issue.severity}
                        </span>
                        <span className="issue-message">{issue.message}</span>
                      </div>
                    ))}
                  </div>
                )}

                <div className="connection-actions">
                  <button 
                    className="connection-btn primary"
                    onClick={() => handleConnectionAction(connection, 'details')}
                  >
                    <i className="fas fa-info-circle"></i>
                    Details
                  </button>
                  <button 
                    className="connection-btn secondary"
                    onClick={() => handleConnectionAction(connection, 'test')}
                  >
                    <i className="fas fa-vial"></i>
                    Test
                  </button>
                  <button 
                    className="connection-btn tertiary"
                    onClick={() => handleConnectionAction(connection, 'configure')}
                  >
                    <i className="fas fa-cog"></i>
                    Config
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {viewMode === 'pools' && (
        <div className="pools-section">
          <div className="pools-header">
            <h3>Connection Pools Management</h3>
            <div className="pools-actions">
              <button className="action-btn primary">
                <i className="fas fa-plus"></i>
                Create Pool
              </button>
              <button className="action-btn secondary">
                <i className="fas fa-balance-scale"></i>
                Rebalance All
              </button>
            </div>
          </div>

          <div className="pools-detailed-grid">
            {connectionData.pools.map(pool => (
              <div key={pool.id} className="pool-detailed-card">
                <div className="pool-detailed-header">
                  <div className="pool-detailed-info">
                    <h4>{pool.name}</h4>
                    <span className="pool-detailed-strategy">{pool.loadBalancingStrategy}</span>
                  </div>
                  <div 
                    className="pool-detailed-status"
                    style={{ color: getStatusColor(pool.status) }}
                  >
                    <i className={`fas fa-circle ${pool.status === 'healthy' ? 'fa-pulse' : ''}`}></i>
                    {pool.status}
                  </div>
                </div>

                <div className="pool-capacity-overview">
                  <div className="capacity-chart">
                    <div className="capacity-ring">
                      <div className="capacity-percentage">{pool.utilizationPercent}%</div>
                    </div>
                  </div>
                  <div className="capacity-details">
                    <div className="capacity-item">
                      <span className="capacity-label">Active:</span>
                      <span className="capacity-value">{pool.activeConnections}</span>
                    </div>
                    <div className="capacity-item">
                      <span className="capacity-label">Total:</span>
                      <span className="capacity-value">{pool.totalConnections}</span>
                    </div>
                    <div className="capacity-item">
                      <span className="capacity-label">Max:</span>
                      <span className="capacity-value">{pool.maxCapacity}</span>
                    </div>
                  </div>
                </div>

                <div className="pool-connections-list">
                  <div className="connections-list-header">
                    <span>Connections ({pool.connections.length})</span>
                  </div>
                  <div className="connections-list">
                    {pool.connections.map(connection => (
                      <div key={connection.id} className="connection-list-item">
                        <div className="connection-list-info">
                          <span className="connection-list-name">{connection.name}</span>
                          <span className="connection-list-endpoint">{connection.endpoint}</span>
                        </div>
                        <div 
                          className="connection-list-status"
                          style={{ color: getStatusColor(connection.status) }}
                        >
                          {connection.status}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="pool-detailed-actions">
                  <button className="pool-detailed-btn primary">Manage Connections</button>
                  <button className="pool-detailed-btn secondary">Configure Pool</button>
                  <button className="pool-detailed-btn tertiary">View Analytics</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {viewMode === 'settings' && (
        <div className="settings-section">
          <div className="settings-panels">
            <div className="settings-panel">
              <h3>Global Connection Settings</h3>
              <div className="settings-form">
                <div className="setting-group">
                  <label>Default Connection Timeout:</label>
                  <input type="number" defaultValue="5000" />
                  <span className="setting-unit">ms</span>
                </div>
                <div className="setting-group">
                  <label>Default Retry Count:</label>
                  <input type="number" defaultValue="3" />
                </div>
                <div className="setting-group">
                  <label>Health Check Interval:</label>
                  <input type="number" defaultValue="30" />
                  <span className="setting-unit">seconds</span>
                </div>
                <div className="setting-group">
                  <label>Connection Pool Size:</label>
                  <input type="number" defaultValue="100" />
                </div>
              </div>
            </div>

            <div className="settings-panel">
              <h3>Load Balancing Settings</h3>
              <div className="settings-form">
                <div className="setting-group">
                  <label>Default Strategy:</label>
                  <select defaultValue="least_connections">
                    <option value="round_robin">Round Robin</option>
                    <option value="least_connections">Least Connections</option>
                    <option value="weighted_round_robin">Weighted Round Robin</option>
                    <option value="least_response_time">Least Response Time</option>
                  </select>
                </div>
                <div className="setting-group">
                  <label>Failover Timeout:</label>
                  <input type="number" defaultValue="10" />
                  <span className="setting-unit">seconds</span>
                </div>
                <div className="setting-group">
                  <label>Auto-scaling Threshold:</label>
                  <input type="number" defaultValue="80" />
                  <span className="setting-unit">%</span>
                </div>
              </div>
            </div>

            <div className="settings-panel">
              <h3>Monitoring & Alerts</h3>
              <div className="settings-form">
                <div className="setting-group">
                  <label>
                    <input type="checkbox" defaultChecked />
                    Enable Connection Monitoring
                  </label>
                </div>
                <div className="setting-group">
                  <label>
                    <input type="checkbox" defaultChecked />
                    Alert on Connection Failures
                  </label>
                </div>
                <div className="setting-group">
                  <label>
                    <input type="checkbox" defaultChecked />
                    Performance Degradation Alerts
                  </label>
                </div>
                <div className="setting-group">
                  <label>Alert Threshold (Response Time):</label>
                  <input type="number" defaultValue="2000" />
                  <span className="setting-unit">ms</span>
                </div>
              </div>
            </div>
          </div>

          <div className="settings-actions">
            <button className="settings-btn primary">Save Settings</button>
            <button className="settings-btn secondary">Reset to Defaults</button>
            <button className="settings-btn tertiary">Export Configuration</button>
          </div>
        </div>
      )}

      {/* Connection Detail Modal */}
      {showConnectionModal && selectedConnection && (
        <div className="connection-modal-overlay">
          <div className="connection-modal">
            <div className="modal-header">
              <h3>{selectedConnection.name} - {connectionAction}</h3>
              <button 
                className="modal-close"
                onClick={() => setShowConnectionModal(false)}
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
            
            <div className="modal-content">
              {connectionAction === 'details' && (
                <div className="connection-details">
                  <div className="details-section">
                    <h4>Connection Information</h4>
                    <div className="details-grid">
                      <div className="detail-item">
                        <span className="detail-label">Endpoint:</span>
                        <span className="detail-value">{selectedConnection.endpoint}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">Type:</span>
                        <span className="detail-value">{selectedConnection.connectionType}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">Region:</span>
                        <span className="detail-value">{selectedConnection.region}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">Priority:</span>
                        <span className="detail-value">{selectedConnection.priority}</span>
                      </div>
                    </div>
                  </div>

                  <div className="details-section">
                    <h4>Performance Metrics</h4>
                    <div className="metrics-grid">
                      <div className="metric-item">
                        <span className="metric-label">Average Response Time:</span>
                        <span className="metric-value">{selectedConnection.performance.avgResponseTime}ms</span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">Success Rate:</span>
                        <span className="metric-value">{selectedConnection.performance.successRate}%</span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">Requests/Minute:</span>
                        <span className="metric-value">{selectedConnection.performance.requestsPerMinute}</span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">Bandwidth:</span>
                        <span className="metric-value">{selectedConnection.performance.bandwidth} MB/min</span>
                      </div>
                    </div>
                  </div>

                  <div className="details-section">
                    <h4>Security Information</h4>
                    <div className="security-grid">
                      <div className="security-item">
                        <span className="security-label">TLS Version:</span>
                        <span className="security-value">{selectedConnection.security.tlsVersion}</span>
                      </div>
                      <div className="security-item">
                        <span className="security-label">Certificate Valid:</span>
                        <span className={`security-value ${selectedConnection.security.certificateValid ? 'valid' : 'invalid'}`}>
                          {selectedConnection.security.certificateValid ? 'Yes' : 'No'}
                        </span>
                      </div>
                      <div className="security-item">
                        <span className="security-label">Certificate Expires:</span>
                        <span className="security-value">
                          {selectedConnection.security.certificateExpiry ? 
                            new Date(selectedConnection.security.certificateExpiry).toLocaleDateString() : 'N/A'}
                        </span>
                      </div>
                      <div className="security-item">
                        <span className="security-label">Auth Method:</span>
                        <span className="security-value">{selectedConnection.security.authMethod}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {connectionAction === 'test' && (
                <div className="connection-test">
                  <div className="test-controls">
                    <button className="test-btn primary">Run Connection Test</button>
                    <button className="test-btn secondary">Performance Test</button>
                    <button className="test-btn tertiary">Security Scan</button>
                  </div>
                  <div className="test-results">
                    <div className="test-result-placeholder">
                      <i className="fas fa-vial"></i>
                      <p>Connection test results will appear here</p>
                    </div>
                  </div>
                </div>
              )}

              {connectionAction === 'configure' && (
                <div className="connection-config">
                  <div className="config-form">
                    <div className="config-section">
                      <h4>Connection Settings</h4>
                      <div className="config-group">
                        <label>Timeout (ms):</label>
                        <input type="number" value={selectedConnection.configuration.timeout} />
                      </div>
                      <div className="config-group">
                        <label>Max Retries:</label>
                        <input type="number" value={selectedConnection.configuration.retries} />
                      </div>
                      <div className="config-group">
                        <label>Backoff Strategy:</label>
                        <select value={selectedConnection.configuration.backoffStrategy}>
                          <option value="linear">Linear</option>
                          <option value="exponential">Exponential</option>
                          <option value="fixed">Fixed</option>
                        </select>
                      </div>
                    </div>

                    <div className="config-section">
                      <h4>Rate Limiting</h4>
                      <div className="config-group">
                        <label>Rate Limit (per minute):</label>
                        <input type="number" value={selectedConnection.configuration.rateLimitPerMinute} />
                      </div>
                      <div className="config-group">
                        <label>Keep-Alive Timeout (ms):</label>
                        <input type="number" value={selectedConnection.configuration.keepAliveTimeout} />
                      </div>
                    </div>

                    <div className="config-section">
                      <h4>Optimization</h4>
                      <div className="config-group">
                        <label>
                          <input type="checkbox" checked={selectedConnection.configuration.enableCompression} />
                          Enable Compression
                        </label>
                      </div>
                      <div className="config-group">
                        <label>
                          <input type="checkbox" checked={selectedConnection.configuration.enableCaching} />
                          Enable Caching
                        </label>
                      </div>
                      <div className="config-group">
                        <label>Cache Timeout (seconds):</label>
                        <input type="number" value={selectedConnection.configuration.cacheTimeout} />
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="modal-actions">
              <button className="modal-btn primary">Apply Changes</button>
              <button className="modal-btn secondary">Reset</button>
              <button 
                className="modal-btn tertiary"
                onClick={() => setShowConnectionModal(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiConnectionManagement;
