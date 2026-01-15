// components/ApiLoadBalancing.jsx

import React, { useState, useEffect } from 'react';

const ApiLoadBalancing = () => {
  const [loadBalancingData, setLoadBalancingData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedPool, setSelectedPool] = useState('all');
  const [viewMode, setViewMode] = useState('topology'); // topology, metrics, configuration
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Generate comprehensive load balancing data
  const generateLoadBalancingData = () => {
    const pools = [
      {
        id: 'financial_pool',
        name: 'Financial APIs Pool',
        algorithm: 'Round Robin',
        status: 'healthy',
        totalEndpoints: 9,
        activeEndpoints: 8,
        failedEndpoints: 1,
        totalRequests: 45628,
        averageResponseTime: 425,
        throughput: 3847,
        endpoints: [
          {
            id: 'coingecko_primary',
            name: 'CoinGecko Primary',
            url: 'https://api.coingecko.com/api/v3',
            status: 'active',
            weight: 30,
            currentConnections: 245,
            maxConnections: 1000,
            responseTime: 245,
            requestsPerSecond: 52.4,
            successRate: 99.88,
            healthScore: 98.2,
            region: 'US-East',
            priority: 1,
            lastHealthCheck: new Date(Date.now() - 15000).toISOString(),
            metrics: {
              cpu: 45,
              memory: 62,
              network: 78,
              requests24h: 15847
            }
          },
          {
            id: 'coingecko_backup',
            name: 'CoinGecko Backup',
            url: 'https://api-backup.coingecko.com/api/v3',
            status: 'standby',
            weight: 10,
            currentConnections: 0,
            maxConnections: 500,
            responseTime: 0,
            requestsPerSecond: 0,
            successRate: 100,
            healthScore: 100,
            region: 'EU-West',
            priority: 2,
            lastHealthCheck: new Date(Date.now() - 30000).toISOString(),
            metrics: {
              cpu: 15,
              memory: 32,
              network: 25,
              requests24h: 0
            }
          },
          {
            id: 'polygon_primary',
            name: 'Polygon.io Primary',
            url: 'https://api.polygon.io',
            status: 'active',
            weight: 25,
            currentConnections: 180,
            maxConnections: 800,
            responseTime: 425,
            requestsPerSecond: 33.5,
            successRate: 99.72,
            healthScore: 95.1,
            region: 'US-West',
            priority: 1,
            lastHealthCheck: new Date(Date.now() - 20000).toISOString(),
            metrics: {
              cpu: 68,
              memory: 71,
              network: 85,
              requests24h: 9847
            }
          },
          {
            id: 'polygon_backup',
            name: 'Polygon.io Backup',
            url: 'https://backup.polygon.io',
            status: 'active',
            weight: 15,
            currentConnections: 95,
            maxConnections: 600,
            responseTime: 380,
            requestsPerSecond: 28.2,
            successRate: 99.85,
            healthScore: 96.8,
            region: 'US-Central',
            priority: 2,
            lastHealthCheck: new Date(Date.now() - 10000).toISOString(),
            metrics: {
              cpu: 52,
              memory: 58,
              network: 65,
              requests24h: 7892
            }
          },
          {
            id: 'alpha_vantage_primary',
            name: 'Alpha Vantage Primary',
            url: 'https://www.alphavantage.co',
            status: 'degraded',
            weight: 20,
            currentConnections: 45,
            maxConnections: 400,
            responseTime: 1240,
            requestsPerSecond: 10.3,
            successRate: 97.2,
            healthScore: 71.4,
            region: 'US-East',
            priority: 1,
            lastHealthCheck: new Date(Date.now() - 45000).toISOString(),
            metrics: {
              cpu: 89,
              memory: 91,
              network: 95,
              requests24h: 3247
            }
          },
          {
            id: 'alpha_vantage_backup',
            name: 'Alpha Vantage Backup',
            url: 'https://backup.alphavantage.co',
            status: 'failed',
            weight: 0,
            currentConnections: 0,
            maxConnections: 400,
            responseTime: 0,
            requestsPerSecond: 0,
            successRate: 0,
            healthScore: 0,
            region: 'EU-Central',
            priority: 2,
            lastHealthCheck: new Date(Date.now() - 300000).toISOString(),
            metrics: {
              cpu: 0,
              memory: 0,
              network: 0,
              requests24h: 0
            }
          }
        ]
      },
      {
        id: 'security_pool',
        name: 'Cybersecurity APIs Pool',
        algorithm: 'Least Connections',
        status: 'healthy',
        totalEndpoints: 4,
        activeEndpoints: 4,
        failedEndpoints: 0,
        totalRequests: 19636,
        averageResponseTime: 800,
        throughput: 1072,
        endpoints: [
          {
            id: 'virustotal_primary',
            name: 'VirusTotal Primary',
            url: 'https://www.virustotal.com',
            status: 'active',
            weight: 40,
            currentConnections: 125,
            maxConnections: 600,
            responseTime: 680,
            requestsPerSecond: 14.8,
            successRate: 99.55,
            healthScore: 94.8,
            region: 'Global-CDN',
            priority: 1,
            lastHealthCheck: new Date(Date.now() - 12000).toISOString(),
            metrics: {
              cpu: 58,
              memory: 67,
              network: 72,
              requests24h: 4847
            }
          },
          {
            id: 'virustotal_backup',
            name: 'VirusTotal Backup',
            url: 'https://backup.virustotal.com',
            status: 'active',
            weight: 20,
            currentConnections: 68,
            maxConnections: 400,
            responseTime: 720,
            requestsPerSecond: 12.3,
            successRate: 99.45,
            healthScore: 93.2,
            region: 'EU-West',
            priority: 2,
            lastHealthCheck: new Date(Date.now() - 18000).toISOString(),
            metrics: {
              cpu: 45,
              memory: 54,
              network: 61,
              requests24h: 3928
            }
          },
          {
            id: 'shodan_primary',
            name: 'Shodan Primary',
            url: 'https://api.shodan.io',
            status: 'active',
            weight: 30,
            currentConnections: 95,
            maxConnections: 500,
            responseTime: 920,
            requestsPerSecond: 11.2,
            successRate: 98.8,
            healthScore: 90.5,
            region: 'US-West',
            priority: 1,
            lastHealthCheck: new Date(Date.now() - 8000).toISOString(),
            metrics: {
              cpu: 62,
              memory: 69,
              network: 74,
              requests24h: 3789
            }
          },
          {
            id: 'shodan_backup',
            name: 'Shodan Backup',
            url: 'https://backup.shodan.io',
            status: 'active',
            weight: 10,
            currentConnections: 28,
            maxConnections: 300,
            responseTime: 850,
            requestsPerSecond: 8.9,
            successRate: 99.1,
            healthScore: 92.1,
            region: 'EU-Central',
            priority: 2,
            lastHealthCheck: new Date(Date.now() - 25000).toISOString(),
            metrics: {
              cpu: 38,
              memory: 42,
              network: 48,
              requests24h: 2072
            }
          }
        ]
      },
      {
        id: 'content_pool',
        name: 'Content APIs Pool',
        algorithm: 'Weighted Round Robin',
        status: 'warning',
        totalEndpoints: 4,
        activeEndpoints: 3,
        failedEndpoints: 1,
        totalRequests: 12694,
        averageResponseTime: 1650,
        throughput: 518,
        endpoints: [
          {
            id: 'newsapi_primary',
            name: 'NewsAPI Primary',
            url: 'https://newsapi.org',
            status: 'degraded',
            weight: 25,
            currentConnections: 35,
            maxConnections: 200,
            responseTime: 2850,
            requestsPerSecond: 3.2,
            successRate: 91.3,
            healthScore: 68.7,
            region: 'Global-CDN',
            priority: 1,
            lastHealthCheck: new Date(Date.now() - 60000).toISOString(),
            metrics: {
              cpu: 95,
              memory: 88,
              network: 92,
              requests24h: 1847
            }
          },
          {
            id: 'newsapi_backup',
            name: 'NewsAPI Backup',
            url: 'https://backup.newsapi.org',
            status: 'failed',
            weight: 0,
            currentConnections: 0,
            maxConnections: 150,
            responseTime: 0,
            requestsPerSecond: 0,
            successRate: 0,
            healthScore: 0,
            region: 'US-East',
            priority: 2,
            lastHealthCheck: new Date(Date.now() - 600000).toISOString(),
            metrics: {
              cpu: 0,
              memory: 0,
              network: 0,
              requests24h: 0
            }
          },
          {
            id: 'nasa_primary',
            name: 'NASA API Primary',
            url: 'https://api.nasa.gov',
            status: 'active',
            weight: 35,
            currentConnections: 85,
            maxConnections: 400,
            responseTime: 450,
            requestsPerSecond: 11.4,
            successRate: 99.95,
            healthScore: 98.7,
            region: 'US-Gov',
            priority: 1,
            lastHealthCheck: new Date(Date.now() - 5000).toISOString(),
            metrics: {
              cpu: 42,
              memory: 55,
              network: 58,
              requests24h: 3487
            }
          },
          {
            id: 'nasa_backup',
            name: 'NASA API Backup',
            url: 'https://backup.api.nasa.gov',
            status: 'active',
            weight: 15,
            currentConnections: 22,
            maxConnections: 200,
            responseTime: 520,
            requestsPerSecond: 8.7,
            successRate: 99.8,
            healthScore: 97.2,
            region: 'US-Gov-West',
            priority: 2,
            lastHealthCheck: new Date(Date.now() - 15000).toISOString(),
            metrics: {
              cpu: 28,
              memory: 35,
              network: 41,
              requests24h: 2360
            }
          }
        ]
      }
    ];

    const loadBalancers = [
      {
        id: 'lb_primary',
        name: 'Primary Load Balancer',
        status: 'active',
        region: 'US-East',
        requestsPerSecond: 127.3,
        connections: 892,
        uptime: '47d 12h 35m',
        version: '2.4.1',
        pools: ['financial_pool', 'security_pool', 'content_pool']
      },
      {
        id: 'lb_backup',
        name: 'Backup Load Balancer',
        status: 'standby',
        region: 'US-West',
        requestsPerSecond: 0,
        connections: 0,
        uptime: '47d 12h 35m',
        version: '2.4.1',
        pools: ['financial_pool', 'security_pool', 'content_pool']
      }
    ];

    const summary = {
      totalPools: pools.length,
      totalEndpoints: pools.reduce((sum, pool) => sum + pool.totalEndpoints, 0),
      activeEndpoints: pools.reduce((sum, pool) => sum + pool.activeEndpoints, 0),
      failedEndpoints: pools.reduce((sum, pool) => sum + pool.failedEndpoints, 0),
      totalRequests: pools.reduce((sum, pool) => sum + pool.totalRequests, 0),
      averageResponseTime: Math.round(pools.reduce((sum, pool) => sum + pool.averageResponseTime, 0) / pools.length),
      totalThroughput: pools.reduce((sum, pool) => sum + pool.throughput, 0),
      healthyPools: pools.filter(pool => pool.status === 'healthy').length,
      warningPools: pools.filter(pool => pool.status === 'warning').length,
      criticalPools: pools.filter(pool => pool.status === 'critical').length
    };

    return {
      timestamp: new Date().toISOString(),
      pools,
      loadBalancers,
      summary
    };
  };

  useEffect(() => {
    const loadData = () => {
      setLoadBalancingData(generateLoadBalancingData());
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
      case 'active': case 'healthy': return '#28a745';
      case 'standby': return '#17a2b8';
      case 'degraded': case 'warning': return '#ffc107';
      case 'failed': case 'critical': return '#dc3545';
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

  const filteredPools = selectedPool === 'all' 
    ? loadBalancingData?.pools || []
    : loadBalancingData?.pools.filter(pool => pool.id === selectedPool) || [];

  if (loading) {
    return (
      <div className="api-load-balancing loading">
        <div className="loading-spinner">
          <i className="fas fa-balance-scale fa-pulse"></i>
          <p>Loading load balancer configuration...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="api-load-balancing">
      <div className="load-balancing-header">
        <div className="header-info">
          <h2>
            <i className="fas fa-balance-scale"></i>
            API Load Balancing
          </h2>
          <p>Real-time load balancer status, pool management, and endpoint distribution visualization</p>
        </div>

        <div className="header-controls">
          <div className="control-group">
            <label>Pool:</label>
            <select value={selectedPool} onChange={(e) => setSelectedPool(e.target.value)}>
              <option value="all">All Pools</option>
              {loadBalancingData?.pools.map(pool => (
                <option key={pool.id} value={pool.id}>{pool.name}</option>
              ))}
            </select>
          </div>

          <div className="view-toggle">
            {['topology', 'metrics', 'configuration'].map(mode => (
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

      <div className="load-balancer-summary">
        <div className="summary-cards">
          <div className="summary-card total">
            <div className="card-icon">
              <i className="fas fa-layer-group"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{loadBalancingData.summary.totalPools}</div>
              <div className="card-label">Total Pools</div>
            </div>
          </div>

          <div className="summary-card endpoints">
            <div className="card-icon">
              <i className="fas fa-server"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{loadBalancingData.summary.activeEndpoints}/{loadBalancingData.summary.totalEndpoints}</div>
              <div className="card-label">Active Endpoints</div>
            </div>
          </div>

          <div className="summary-card throughput">
            <div className="card-icon">
              <i className="fas fa-exchange-alt"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{formatNumber(loadBalancingData.summary.totalThroughput)}</div>
              <div className="card-label">Total Throughput</div>
            </div>
          </div>

          <div className="summary-card response-time">
            <div className="card-icon">
              <i className="fas fa-clock"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{loadBalancingData.summary.averageResponseTime}ms</div>
              <div className="card-label">Avg Response Time</div>
            </div>
          </div>

          <div className="summary-card requests">
            <div className="card-icon">
              <i className="fas fa-chart-bar"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{formatNumber(loadBalancingData.summary.totalRequests)}</div>
              <div className="card-label">Total Requests</div>
            </div>
          </div>

          <div className="summary-card failed">
            <div className="card-icon">
              <i className="fas fa-exclamation-triangle"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{loadBalancingData.summary.failedEndpoints}</div>
              <div className="card-label">Failed Endpoints</div>
            </div>
          </div>
        </div>
      </div>

      {viewMode === 'topology' && (
        <div className="topology-view">
          <div className="load-balancers-section">
            <h3>Load Balancers</h3>
            <div className="load-balancers">
              {loadBalancingData.loadBalancers.map(lb => (
                <div key={lb.id} className="load-balancer-node">
                  <div className="node-header">
                    <div className="node-info">
                      <h4>{lb.name}</h4>
                      <span className="node-region">{lb.region}</span>
                    </div>
                    <div 
                      className="node-status"
                      style={{ color: getStatusColor(lb.status) }}
                    >
                      <i className={`fas fa-circle ${lb.status === 'active' ? 'fa-pulse' : ''}`}></i>
                      {lb.status}
                    </div>
                  </div>
                  <div className="node-metrics">
                    <div className="metric">
                      <span className="metric-label">RPS:</span>
                      <span className="metric-value">{lb.requestsPerSecond}</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Connections:</span>
                      <span className="metric-value">{lb.connections}</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Uptime:</span>
                      <span className="metric-value">{lb.uptime}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="pools-topology">
            {filteredPools.map(pool => (
              <div key={pool.id} className="pool-container">
                <div className="pool-header">
                  <div className="pool-info">
                    <h3>{pool.name}</h3>
                    <span className="pool-algorithm">{pool.algorithm}</span>
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
                  <div className="pool-metric">
                    <span>Endpoints: {pool.activeEndpoints}/{pool.totalEndpoints}</span>
                  </div>
                  <div className="pool-metric">
                    <span>Throughput: {formatNumber(pool.throughput)}/hr</span>
                  </div>
                  <div className="pool-metric">
                    <span>Avg Response: {pool.averageResponseTime}ms</span>
                  </div>
                </div>

                <div className="endpoints-grid">
                  {pool.endpoints.map(endpoint => (
                    <div key={endpoint.id} className="endpoint-node">
                      <div className="endpoint-header">
                        <div className="endpoint-info">
                          <h4>{endpoint.name}</h4>
                          <span className="endpoint-region">{endpoint.region}</span>
                        </div>
                        <div 
                          className="endpoint-status"
                          style={{ color: getStatusColor(endpoint.status) }}
                        >
                          <i className={`fas fa-circle ${endpoint.status === 'active' ? 'fa-pulse' : ''}`}></i>
                        </div>
                      </div>

                      <div className="endpoint-details">
                        <div className="endpoint-url">{endpoint.url}</div>
                        <div className="endpoint-weight">Weight: {endpoint.weight}%</div>
                      </div>

                      <div className="endpoint-metrics">
                        <div className="endpoint-metric">
                          <span className="metric-label">Connections:</span>
                          <span className="metric-value">{endpoint.currentConnections}/{endpoint.maxConnections}</span>
                        </div>
                        <div className="endpoint-metric">
                          <span className="metric-label">Response Time:</span>
                          <span className="metric-value">{endpoint.responseTime}ms</span>
                        </div>
                        <div className="endpoint-metric">
                          <span className="metric-label">Success Rate:</span>
                          <span className="metric-value">{endpoint.successRate}%</span>
                        </div>
                        <div className="endpoint-metric">
                          <span className="metric-label">Health Score:</span>
                          <span 
                            className="metric-value"
                            style={{ color: getHealthScoreColor(endpoint.healthScore) }}
                          >
                            {endpoint.healthScore}/100
                          </span>
                        </div>
                      </div>

                      <div className="connection-bar">
                        <div 
                          className="connection-fill"
                          style={{ 
                            width: `${(endpoint.currentConnections / endpoint.maxConnections) * 100}%`,
                            backgroundColor: getStatusColor(endpoint.status)
                          }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {viewMode === 'metrics' && (
        <div className="metrics-view">
          <div className="metrics-dashboard">
            {filteredPools.map(pool => (
              <div key={pool.id} className="pool-metrics-card">
                <div className="pool-metrics-header">
                  <h3>{pool.name}</h3>
                  <span className="pool-algorithm">{pool.algorithm}</span>
                </div>

                <div className="pool-charts">
                  <div className="chart-placeholder">
                    <div className="chart-info">
                      <i className="fas fa-chart-area"></i>
                      <p>Traffic Distribution Chart</p>
                      <p>Real-time request routing visualization</p>
                    </div>
                  </div>
                  
                  <div className="chart-placeholder">
                    <div className="chart-info">
                      <i className="fas fa-chart-pie"></i>
                      <p>Load Distribution</p>
                      <p>Endpoint weight and utilization</p>
                    </div>
                  </div>
                </div>

                <div className="endpoint-metrics-table">
                  <div className="table-header">
                    <div className="col-endpoint">Endpoint</div>
                    <div className="col-status">Status</div>
                    <div className="col-weight">Weight</div>
                    <div className="col-connections">Connections</div>
                    <div className="col-response">Response</div>
                    <div className="col-health">Health</div>
                  </div>
                  {pool.endpoints.map(endpoint => (
                    <div key={endpoint.id} className="table-row">
                      <div className="col-endpoint">
                        <div className="endpoint-name">{endpoint.name}</div>
                        <div className="endpoint-region">{endpoint.region}</div>
                      </div>
                      <div className="col-status">
                        <span 
                          className="status-badge"
                          style={{ backgroundColor: getStatusColor(endpoint.status) }}
                        >
                          {endpoint.status}
                        </span>
                      </div>
                      <div className="col-weight">{endpoint.weight}%</div>
                      <div className="col-connections">
                        {endpoint.currentConnections}/{endpoint.maxConnections}
                      </div>
                      <div className="col-response">{endpoint.responseTime}ms</div>
                      <div className="col-health">
                        <span style={{ color: getHealthScoreColor(endpoint.healthScore) }}>
                          {endpoint.healthScore}/100
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {viewMode === 'configuration' && (
        <div className="configuration-view">
          <div className="config-sections">
            <div className="config-section">
              <h3>Load Balancer Configuration</h3>
              <div className="config-cards">
                {loadBalancingData.loadBalancers.map(lb => (
                  <div key={lb.id} className="config-card">
                    <div className="config-header">
                      <h4>{lb.name}</h4>
                      <span className="config-version">v{lb.version}</span>
                    </div>
                    <div className="config-details">
                      <div className="config-item">
                        <span className="config-label">Status:</span>
                        <span className="config-value">{lb.status}</span>
                      </div>
                      <div className="config-item">
                        <span className="config-label">Region:</span>
                        <span className="config-value">{lb.region}</span>
                      </div>
                      <div className="config-item">
                        <span className="config-label">Pools:</span>
                        <span className="config-value">{lb.pools.length}</span>
                      </div>
                    </div>
                    <div className="config-actions">
                      <button className="config-btn primary">Edit Config</button>
                      <button className="config-btn secondary">View Logs</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="config-section">
              <h3>Pool Configurations</h3>
              <div className="pool-configs">
                {filteredPools.map(pool => (
                  <div key={pool.id} className="pool-config-card">
                    <div className="pool-config-header">
                      <h4>{pool.name}</h4>
                      <span className="pool-config-algorithm">{pool.algorithm}</span>
                    </div>
                    
                    <div className="pool-config-settings">
                      <div className="setting-group">
                        <label>Load Balancing Algorithm:</label>
                        <select defaultValue={pool.algorithm.toLowerCase().replace(' ', '_')}>
                          <option value="round_robin">Round Robin</option>
                          <option value="least_connections">Least Connections</option>
                          <option value="weighted_round_robin">Weighted Round Robin</option>
                          <option value="ip_hash">IP Hash</option>
                          <option value="least_response_time">Least Response Time</option>
                        </select>
                      </div>
                      
                      <div className="setting-group">
                        <label>Health Check Interval:</label>
                        <input type="number" defaultValue="30" />
                        <span className="setting-unit">seconds</span>
                      </div>
                      
                      <div className="setting-group">
                        <label>Max Retries:</label>
                        <input type="number" defaultValue="3" />
                      </div>
                      
                      <div className="setting-group">
                        <label>Timeout:</label>
                        <input type="number" defaultValue="5000" />
                        <span className="setting-unit">ms</span>
                      </div>
                    </div>

                    <div className="pool-config-endpoints">
                      <h5>Endpoint Configuration</h5>
                      {pool.endpoints.map(endpoint => (
                        <div key={endpoint.id} className="endpoint-config">
                          <div className="endpoint-config-header">
                            <span className="endpoint-config-name">{endpoint.name}</span>
                            <span className="endpoint-config-weight">Weight: {endpoint.weight}%</span>
                          </div>
                          <div className="endpoint-config-url">{endpoint.url}</div>
                          <div className="endpoint-config-controls">
                            <button className="endpoint-btn">Edit</button>
                            <button className="endpoint-btn">Test</button>
                            <button className="endpoint-btn">Remove</button>
                          </div>
                        </div>
                      ))}
                      <button className="add-endpoint-btn">
                        <i className="fas fa-plus"></i>
                        Add Endpoint
                      </button>
                    </div>

                    <div className="pool-config-actions">
                      <button className="config-btn primary">Save Changes</button>
                      <button className="config-btn secondary">Reset</button>
                      <button className="config-btn tertiary">Delete Pool</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiLoadBalancing;
