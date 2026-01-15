// components/ApiHealthMonitoring.jsx

import React, { useState, useEffect } from 'react';

const ApiHealthMonitoring = () => {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('grid'); // grid, list, detailed
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30000); // 30 seconds

  // Generate comprehensive API health data
  const generateHealthData = () => {
    const apis = [
      // Financial APIs
      {
        id: 'coingecko',
        name: 'CoinGecko API',
        category: 'Financial',
        status: 'healthy',
        endpoint: 'https://api.coingecko.com/api/v3',
        responseTime: 245,
        uptime: 99.8,
        lastChecked: new Date(Date.now() - Math.random() * 60000).toISOString(),
        statusCode: 200,
        errorRate: 0.12,
        availability: 99.95,
        ssl: {
          valid: true,
          expiresAt: '2025-12-15T00:00:00Z',
          issuer: 'Let\'s Encrypt'
        },
        healthChecks: [
          { endpoint: '/simple/price', status: 'healthy', responseTime: 180, lastCheck: new Date().toISOString() },
          { endpoint: '/coins/markets', status: 'healthy', responseTime: 320, lastCheck: new Date().toISOString() },
          { endpoint: '/coins/{id}', status: 'healthy', responseTime: 290, lastCheck: new Date().toISOString() }
        ],
        metrics: {
          requests24h: 45628,
          successRate: 99.88,
          avgResponseTime: 245,
          errorCount: 55,
          maxResponseTime: 850,
          minResponseTime: 120
        },
        incidents: []
      },
      {
        id: 'polygon',
        name: 'Polygon.io API',
        category: 'Financial', 
        status: 'healthy',
        endpoint: 'https://api.polygon.io',
        responseTime: 425,
        uptime: 99.5,
        lastChecked: new Date(Date.now() - Math.random() * 60000).toISOString(),
        statusCode: 200,
        errorRate: 0.28,
        availability: 99.72,
        ssl: {
          valid: true,
          expiresAt: '2025-11-30T00:00:00Z',
          issuer: 'DigiCert'
        },
        healthChecks: [
          { endpoint: '/v2/aggs/ticker', status: 'healthy', responseTime: 380, lastCheck: new Date().toISOString() },
          { endpoint: '/v3/reference/tickers', status: 'healthy', responseTime: 450, lastCheck: new Date().toISOString() },
          { endpoint: '/v2/snapshot/locale', status: 'warning', responseTime: 680, lastCheck: new Date().toISOString() }
        ],
        metrics: {
          requests24h: 28947,
          successRate: 99.72,
          avgResponseTime: 425,
          errorCount: 81,
          maxResponseTime: 1200,
          minResponseTime: 180
        },
        incidents: [
          {
            id: 'inc_001',
            type: 'performance',
            message: 'Increased latency on snapshot endpoints',
            startTime: new Date(Date.now() - 7200000).toISOString(),
            status: 'investigating'
          }
        ]
      },
      {
        id: 'alpha_vantage',
        name: 'Alpha Vantage API',
        category: 'Financial',
        status: 'warning',
        endpoint: 'https://www.alphavantage.co',
        responseTime: 1240,
        uptime: 97.2,
        lastChecked: new Date(Date.now() - Math.random() * 60000).toISOString(),
        statusCode: 200,
        errorRate: 2.8,
        availability: 97.85,
        ssl: {
          valid: true,
          expiresAt: '2026-01-15T00:00:00Z',
          issuer: 'CloudFlare'
        },
        healthChecks: [
          { endpoint: '/query?function=TIME_SERIES_DAILY', status: 'warning', responseTime: 1850, lastCheck: new Date().toISOString() },
          { endpoint: '/query?function=GLOBAL_QUOTE', status: 'healthy', responseTime: 980, lastCheck: new Date().toISOString() },
          { endpoint: '/query?function=CURRENCY_EXCHANGE_RATE', status: 'critical', responseTime: 2400, lastCheck: new Date().toISOString() }
        ],
        metrics: {
          requests24h: 8947,
          successRate: 97.2,
          avgResponseTime: 1240,
          errorCount: 250,
          maxResponseTime: 3500,
          minResponseTime: 680
        },
        incidents: [
          {
            id: 'inc_002',
            type: 'rate_limit',
            message: 'Rate limiting causing increased response times',
            startTime: new Date(Date.now() - 14400000).toISOString(),
            status: 'identified'
          }
        ]
      },
      // Cybersecurity APIs
      {
        id: 'virustotal',
        name: 'VirusTotal API',
        category: 'Cybersecurity',
        status: 'healthy',
        endpoint: 'https://www.virustotal.com',
        responseTime: 680,
        uptime: 99.1,
        lastChecked: new Date(Date.now() - Math.random() * 60000).toISOString(),
        statusCode: 200,
        errorRate: 0.45,
        availability: 99.55,
        ssl: {
          valid: true,
          expiresAt: '2025-10-20T00:00:00Z',
          issuer: 'GlobalSign'
        },
        healthChecks: [
          { endpoint: '/api/v3/files', status: 'healthy', responseTime: 580, lastCheck: new Date().toISOString() },
          { endpoint: '/api/v3/urls', status: 'healthy', responseTime: 720, lastCheck: new Date().toISOString() },
          { endpoint: '/api/v3/domains', status: 'healthy', responseTime: 640, lastCheck: new Date().toISOString() }
        ],
        metrics: {
          requests24h: 12847,
          successRate: 99.55,
          avgResponseTime: 680,
          errorCount: 58,
          maxResponseTime: 1200,
          minResponseTime: 340
        },
        incidents: []
      },
      {
        id: 'shodan',
        name: 'Shodan API',
        category: 'Cybersecurity',
        status: 'healthy',
        endpoint: 'https://api.shodan.io',
        responseTime: 920,
        uptime: 98.7,
        lastChecked: new Date(Date.now() - Math.random() * 60000).toISOString(),
        statusCode: 200,
        errorRate: 1.2,
        availability: 98.88,
        ssl: {
          valid: true,
          expiresAt: '2025-09-30T00:00:00Z',
          issuer: 'Let\'s Encrypt'
        },
        healthChecks: [
          { endpoint: '/shodan/host/search', status: 'healthy', responseTime: 1100, lastCheck: new Date().toISOString() },
          { endpoint: '/shodan/host/{ip}', status: 'healthy', responseTime: 780, lastCheck: new Date().toISOString() },
          { endpoint: '/api-info', status: 'healthy', responseTime: 340, lastCheck: new Date().toISOString() }
        ],
        metrics: {
          requests24h: 6789,
          successRate: 98.8,
          avgResponseTime: 920,
          errorCount: 82,
          maxResponseTime: 2100,
          minResponseTime: 290
        },
        incidents: []
      },
      // News APIs
      {
        id: 'newsapi',
        name: 'NewsAPI',
        category: 'News',
        status: 'critical',
        endpoint: 'https://newsapi.org',
        responseTime: 2850,
        uptime: 94.3,
        lastChecked: new Date(Date.now() - Math.random() * 60000).toISOString(),
        statusCode: 500,
        errorRate: 8.7,
        availability: 91.3,
        ssl: {
          valid: true,
          expiresAt: '2025-08-15T00:00:00Z',
          issuer: 'CloudFlare'
        },
        healthChecks: [
          { endpoint: '/v2/everything', status: 'critical', responseTime: 3200, lastCheck: new Date().toISOString() },
          { endpoint: '/v2/top-headlines', status: 'warning', responseTime: 2100, lastCheck: new Date().toISOString() },
          { endpoint: '/v2/sources', status: 'healthy', responseTime: 890, lastCheck: new Date().toISOString() }
        ],
        metrics: {
          requests24h: 2847,
          successRate: 91.3,
          avgResponseTime: 2850,
          errorCount: 248,
          maxResponseTime: 5000,
          minResponseTime: 650
        },
        incidents: [
          {
            id: 'inc_003',
            type: 'outage',
            message: 'Partial service outage affecting /v2/everything endpoint',
            startTime: new Date(Date.now() - 3600000).toISOString(),
            status: 'ongoing'
          }
        ]
      },
      // Science APIs
      {
        id: 'nasa',
        name: 'NASA Open Data API',
        category: 'Science',
        status: 'healthy',
        endpoint: 'https://api.nasa.gov',
        responseTime: 450,
        uptime: 99.9,
        lastChecked: new Date(Date.now() - Math.random() * 60000).toISOString(),
        statusCode: 200,
        errorRate: 0.05,
        availability: 99.95,
        ssl: {
          valid: true,
          expiresAt: '2026-03-20T00:00:00Z',
          issuer: 'DigiCert'
        },
        healthChecks: [
          { endpoint: '/planetary/apod', status: 'healthy', responseTime: 380, lastCheck: new Date().toISOString() },
          { endpoint: '/planetary/earth/imagery', status: 'healthy', responseTime: 520, lastCheck: new Date().toISOString() },
          { endpoint: '/neo/rest/v1/feed', status: 'healthy', responseTime: 450, lastCheck: new Date().toISOString() }
        ],
        metrics: {
          requests24h: 9847,
          successRate: 99.95,
          avgResponseTime: 450,
          errorCount: 5,
          maxResponseTime: 780,
          minResponseTime: 220
        },
        incidents: []
      },
      // Internal APIs
      {
        id: 'enterprise_backend',
        name: 'Enterprise Backend API',
        category: 'Internal',
        status: 'healthy',
        endpoint: 'http://localhost:5000',
        responseTime: 125,
        uptime: 99.99,
        lastChecked: new Date(Date.now() - Math.random() * 60000).toISOString(),
        statusCode: 200,
        errorRate: 0.01,
        availability: 99.99,
        ssl: {
          valid: false,
          expiresAt: null,
          issuer: 'Self-Signed'
        },
        healthChecks: [
          { endpoint: '/api/enterprise/health', status: 'healthy', responseTime: 120, lastCheck: new Date().toISOString() },
          { endpoint: '/api/enterprise/status', status: 'healthy', responseTime: 130, lastCheck: new Date().toISOString() },
          { endpoint: '/api/enterprise/metrics', status: 'healthy', responseTime: 125, lastCheck: new Date().toISOString() }
        ],
        metrics: {
          requests24h: 125847,
          successRate: 99.99,
          avgResponseTime: 125,
          errorCount: 12,
          maxResponseTime: 250,
          minResponseTime: 85
        },
        incidents: []
      }
    ];

    const data = {
      timestamp: new Date().toISOString(),
      apis: apis,
      summary: {
        total: apis.length,
        healthy: apis.filter(api => api.status === 'healthy').length,
        warning: apis.filter(api => api.status === 'warning').length,
        critical: apis.filter(api => api.status === 'critical').length,
        avgResponseTime: Math.round(apis.reduce((sum, api) => sum + api.responseTime, 0) / apis.length),
        avgUptime: (apis.reduce((sum, api) => sum + api.uptime, 0) / apis.length).toFixed(1),
        totalRequests24h: apis.reduce((sum, api) => sum + api.metrics.requests24h, 0),
        avgSuccessRate: (apis.reduce((sum, api) => sum + api.metrics.successRate, 0) / apis.length).toFixed(1)
      },
      categories: {
        Financial: apis.filter(api => api.category === 'Financial'),
        Cybersecurity: apis.filter(api => api.category === 'Cybersecurity'),
        News: apis.filter(api => api.category === 'News'),
        Science: apis.filter(api => api.category === 'Science'),
        Internal: apis.filter(api => api.category === 'Internal')
      },
      incidents: apis.flatMap(api => api.incidents.map(incident => ({ ...incident, apiName: api.name }))),
      sslStatus: {
        valid: apis.filter(api => api.ssl.valid).length,
        expiringSoon: apis.filter(api => {
          if (!api.ssl.expiresAt) return false;
          const expiryDate = new Date(api.ssl.expiresAt);
          const thirtyDaysFromNow = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000);
          return expiryDate < thirtyDaysFromNow;
        }).length,
        expired: apis.filter(api => {
          if (!api.ssl.expiresAt) return false;
          return new Date(api.ssl.expiresAt) < new Date();
        }).length
      }
    };

    return data;
  };

  useEffect(() => {
    const loadHealthData = () => {
      setHealthData(generateHealthData());
      setLoading(false);
    };

    loadHealthData();

    if (autoRefresh) {
      const interval = setInterval(loadHealthData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return '#28a745';
      case 'warning': return '#ffc107';
      case 'critical': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const getResponseTimeColor = (responseTime) => {
    if (responseTime < 500) return '#28a745';
    if (responseTime < 1000) return '#17a2b8';
    if (responseTime < 2000) return '#ffc107';
    return '#dc3545';
  };

  const filteredApis = healthData?.apis.filter(api => {
    const categoryMatch = filterCategory === 'all' || api.category === filterCategory;
    const statusMatch = filterStatus === 'all' || api.status === filterStatus;
    return categoryMatch && statusMatch;
  }) || [];

  if (loading) {
    return (
      <div className="api-health-monitoring loading">
        <div className="loading-spinner">
          <i className="fas fa-heartbeat fa-pulse"></i>
          <p>Loading API health data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="api-health-monitoring">
      <div className="health-header">
        <div className="header-info">
          <h2>
            <i className="fas fa-heartbeat"></i>
            API Health Monitoring
          </h2>
          <p>Comprehensive real-time API health status and performance monitoring</p>
        </div>
        
        <div className="header-controls">
          <div className="view-toggle">
            {['grid', 'list', 'detailed'].map(mode => (
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

      <div className="health-summary">
        <div className="summary-cards">
          <div className="summary-card total">
            <div className="card-icon">
              <i className="fas fa-network-wired"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{healthData.summary.total}</div>
              <div className="card-label">Total APIs</div>
            </div>
          </div>

          <div className="summary-card healthy">
            <div className="card-icon">
              <i className="fas fa-check-circle"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{healthData.summary.healthy}</div>
              <div className="card-label">Healthy</div>
            </div>
          </div>

          <div className="summary-card warning">
            <div className="card-icon">
              <i className="fas fa-exclamation-triangle"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{healthData.summary.warning}</div>
              <div className="card-label">Warning</div>
            </div>
          </div>

          <div className="summary-card critical">
            <div className="card-icon">
              <i className="fas fa-times-circle"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{healthData.summary.critical}</div>
              <div className="card-label">Critical</div>
            </div>
          </div>

          <div className="summary-card info">
            <div className="card-icon">
              <i className="fas fa-clock"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{healthData.summary.avgResponseTime}ms</div>
              <div className="card-label">Avg Response</div>
            </div>
          </div>

          <div className="summary-card info">
            <div className="card-icon">
              <i className="fas fa-chart-line"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{healthData.summary.avgSuccessRate}%</div>
              <div className="card-label">Success Rate</div>
            </div>
          </div>
        </div>
      </div>

      <div className="health-filters">
        <div className="filter-group">
          <label>Category:</label>
          <select 
            value={filterCategory} 
            onChange={(e) => setFilterCategory(e.target.value)}
          >
            <option value="all">All Categories</option>
            <option value="Financial">Financial</option>
            <option value="Cybersecurity">Cybersecurity</option>
            <option value="News">News</option>
            <option value="Science">Science</option>
            <option value="Internal">Internal</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label>Status:</label>
          <select 
            value={filterStatus} 
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="all">All Status</option>
            <option value="healthy">Healthy</option>
            <option value="warning">Warning</option>
            <option value="critical">Critical</option>
          </select>
        </div>
      </div>

      <div className={`apis-container ${viewMode}`}>
        {filteredApis.map(api => (
          <div key={api.id} className="api-health-card">
            <div className="api-card-header">
              <div className="api-info">
                <h3>{api.name}</h3>
                <span className="api-category">{api.category}</span>
              </div>
              <div 
                className="status-badge"
                style={{ 
                  backgroundColor: getStatusColor(api.status),
                  color: 'white'
                }}
              >
                {api.status}
              </div>
            </div>

            <div className="api-metrics">
              <div className="metric-row">
                <span className="metric-label">Response Time:</span>
                <span 
                  className="metric-value"
                  style={{ color: getResponseTimeColor(api.responseTime) }}
                >
                  {api.responseTime}ms
                </span>
              </div>
              <div className="metric-row">
                <span className="metric-label">Uptime:</span>
                <span className="metric-value">{api.uptime}%</span>
              </div>
              <div className="metric-row">
                <span className="metric-label">Success Rate:</span>
                <span className="metric-value">{api.metrics.successRate}%</span>
              </div>
              <div className="metric-row">
                <span className="metric-label">24h Requests:</span>
                <span className="metric-value">{api.metrics.requests24h.toLocaleString()}</span>
              </div>
              <div className="metric-row">
                <span className="metric-label">Error Rate:</span>
                <span className="metric-value">{api.errorRate}%</span>
              </div>
              <div className="metric-row">
                <span className="metric-label">Last Checked:</span>
                <span className="metric-value">
                  {new Date(api.lastChecked).toLocaleTimeString()}
                </span>
              </div>
            </div>

            {viewMode === 'detailed' && (
              <div className="api-details">
                <div className="ssl-info">
                  <div className="ssl-status">
                    <span className="ssl-label">SSL:</span>
                    <span 
                      className={`ssl-badge ${api.ssl.valid ? 'valid' : 'invalid'}`}
                    >
                      {api.ssl.valid ? 'Valid' : 'Invalid'}
                    </span>
                  </div>
                  {api.ssl.expiresAt && (
                    <div className="ssl-expiry">
                      Expires: {new Date(api.ssl.expiresAt).toLocaleDateString()}
                    </div>
                  )}
                </div>

                <div className="endpoints-health">
                  <div className="endpoints-header">Endpoint Health:</div>
                  {api.healthChecks.slice(0, 3).map((check, index) => (
                    <div key={index} className="endpoint-check">
                      <span className="endpoint-path">{check.endpoint}</span>
                      <span 
                        className="endpoint-status"
                        style={{ color: getStatusColor(check.status) }}
                      >
                        {check.status} ({check.responseTime}ms)
                      </span>
                    </div>
                  ))}
                </div>

                {api.incidents.length > 0 && (
                  <div className="incidents">
                    <div className="incidents-header">Active Incidents:</div>
                    {api.incidents.map(incident => (
                      <div key={incident.id} className="incident-item">
                        <div className="incident-type">{incident.type}</div>
                        <div className="incident-message">{incident.message}</div>
                        <div className="incident-status">{incident.status}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            <div className="api-actions">
              <button className="action-btn primary">
                <i className="fas fa-chart-bar"></i>
                View Details
              </button>
              <button className="action-btn secondary">
                <i className="fas fa-sync"></i>
                Refresh
              </button>
              <button className="action-btn tertiary">
                <i className="fas fa-cog"></i>
                Configure
              </button>
            </div>
          </div>
        ))}
      </div>

      {healthData.incidents.length > 0 && (
        <div className="incidents-section">
          <h3>Active Incidents</h3>
          <div className="incidents-list">
            {healthData.incidents.map(incident => (
              <div key={incident.id} className="incident-card">
                <div className="incident-header">
                  <span className="incident-api">{incident.apiName}</span>
                  <span className={`incident-status ${incident.status}`}>
                    {incident.status}
                  </span>
                </div>
                <div className="incident-message">{incident.message}</div>
                <div className="incident-time">
                  Started: {new Date(incident.startTime).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiHealthMonitoring;
