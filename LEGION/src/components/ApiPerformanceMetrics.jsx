// components/ApiPerformanceMetrics.jsx

import React, { useState, useEffect } from 'react';

const ApiPerformanceMetrics = () => {
  const [performanceData, setPerformanceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedApi, setSelectedApi] = useState('all');
  const [timeRange, setTimeRange] = useState('24h');
  const [metricType, setMetricType] = useState('response_time');
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Generate comprehensive performance metrics data
  const generatePerformanceData = () => {
    const generateTimeSeriesData = (baseValue, variance, points = 24) => {
      return Array.from({ length: points }, (_, i) => {
        const timestamp = new Date(Date.now() - (points - i - 1) * (timeRange === '24h' ? 3600000 : 
                                  timeRange === '7d' ? 86400000 : 604800000)).toISOString();
        const value = baseValue + (Math.random() - 0.5) * variance;
        return {
          timestamp,
          value: Math.max(0, Math.round(value))
        };
      });
    };

    const apis = [
      {
        id: 'coingecko',
        name: 'CoinGecko API',
        category: 'Financial',
        responseTime: {
          current: 245,
          average: 280,
          min: 120,
          max: 850,
          p95: 420,
          p99: 650,
          trend: 'improving',
          timeSeries: generateTimeSeriesData(245, 100)
        },
        throughput: {
          current: 1847,
          average: 1923,
          peak: 3200,
          requestsPerSecond: 52.4,
          trend: 'stable',
          timeSeries: generateTimeSeriesData(1847, 400)
        },
        errorRate: {
          current: 0.12,
          average: 0.15,
          peak: 2.3,
          trend: 'improving',
          timeSeries: generateTimeSeriesData(0.12, 0.05, 24).map(d => ({ ...d, value: Math.max(0, d.value) }))
        },
        availability: {
          current: 99.95,
          average: 99.8,
          sla: 99.9,
          uptime: '29d 23h 52m',
          trend: 'stable',
          timeSeries: generateTimeSeriesData(99.95, 0.5, 24).map(d => ({ ...d, value: Math.min(100, Math.max(95, d.value)) }))
        },
        performance_score: 94.2,
        endpoints: [
          {
            path: '/simple/price',
            responseTime: 180,
            requests24h: 15847,
            errorRate: 0.08,
            performance_score: 96.5
          },
          {
            path: '/coins/markets',
            responseTime: 320,
            requests24h: 12453,
            errorRate: 0.15,
            performance_score: 92.8
          },
          {
            path: '/coins/{id}',
            responseTime: 290,
            requests24h: 18328,
            errorRate: 0.12,
            performance_score: 94.1
          }
        ]
      },
      {
        id: 'polygon',
        name: 'Polygon.io API',
        category: 'Financial',
        responseTime: {
          current: 425,
          average: 480,
          min: 180,
          max: 1200,
          p95: 750,
          p99: 980,
          trend: 'degrading',
          timeSeries: generateTimeSeriesData(425, 150)
        },
        throughput: {
          current: 1205,
          average: 1347,
          peak: 2100,
          requestsPerSecond: 33.5,
          trend: 'decreasing',
          timeSeries: generateTimeSeriesData(1205, 300)
        },
        errorRate: {
          current: 0.28,
          average: 0.31,
          peak: 1.8,
          trend: 'stable',
          timeSeries: generateTimeSeriesData(0.28, 0.1, 24).map(d => ({ ...d, value: Math.max(0, d.value) }))
        },
        availability: {
          current: 99.72,
          average: 99.5,
          sla: 99.5,
          uptime: '29d 17h 28m',
          trend: 'stable',
          timeSeries: generateTimeSeriesData(99.72, 0.8, 24).map(d => ({ ...d, value: Math.min(100, Math.max(95, d.value)) }))
        },
        performance_score: 87.6,
        endpoints: [
          {
            path: '/v2/aggs/ticker',
            responseTime: 380,
            requests24h: 9847,
            errorRate: 0.22,
            performance_score: 89.3
          },
          {
            path: '/v3/reference/tickers',
            responseTime: 450,
            requests24h: 7834,
            errorRate: 0.31,
            performance_score: 85.2
          },
          {
            path: '/v2/snapshot/locale',
            responseTime: 680,
            requests24h: 11266,
            errorRate: 0.45,
            performance_score: 78.9
          }
        ]
      },
      {
        id: 'alpha_vantage',
        name: 'Alpha Vantage API',
        category: 'Financial',
        responseTime: {
          current: 1240,
          average: 1450,
          min: 680,
          max: 3500,
          p95: 2100,
          p99: 2800,
          trend: 'critical',
          timeSeries: generateTimeSeriesData(1240, 400)
        },
        throughput: {
          current: 372,
          average: 428,
          peak: 850,
          requestsPerSecond: 10.3,
          trend: 'decreasing',
          timeSeries: generateTimeSeriesData(372, 150)
        },
        errorRate: {
          current: 2.8,
          average: 3.2,
          peak: 8.7,
          trend: 'concerning',
          timeSeries: generateTimeSeriesData(2.8, 1.5, 24).map(d => ({ ...d, value: Math.max(0, d.value) }))
        },
        availability: {
          current: 97.85,
          average: 97.2,
          sla: 99.0,
          uptime: '28d 14h 32m',
          trend: 'degrading',
          timeSeries: generateTimeSeriesData(97.85, 2, 24).map(d => ({ ...d, value: Math.min(100, Math.max(90, d.value)) }))
        },
        performance_score: 71.4,
        endpoints: [
          {
            path: '/query?function=TIME_SERIES_DAILY',
            responseTime: 1850,
            requests24h: 3247,
            errorRate: 4.2,
            performance_score: 65.8
          },
          {
            path: '/query?function=GLOBAL_QUOTE',
            responseTime: 980,
            requests24h: 2834,
            errorRate: 1.8,
            performance_score: 78.6
          },
          {
            path: '/query?function=CURRENCY_EXCHANGE_RATE',
            responseTime: 2400,
            requests24h: 2866,
            errorRate: 6.5,
            performance_score: 58.2
          }
        ]
      },
      {
        id: 'virustotal',
        name: 'VirusTotal API',
        category: 'Cybersecurity',
        responseTime: {
          current: 680,
          average: 720,
          min: 340,
          max: 1200,
          p95: 950,
          p99: 1100,
          trend: 'stable',
          timeSeries: generateTimeSeriesData(680, 200)
        },
        throughput: {
          current: 534,
          average: 582,
          peak: 920,
          requestsPerSecond: 14.8,
          trend: 'stable',
          timeSeries: generateTimeSeriesData(534, 180)
        },
        errorRate: {
          current: 0.45,
          average: 0.52,
          peak: 2.1,
          trend: 'improving',
          timeSeries: generateTimeSeriesData(0.45, 0.2, 24).map(d => ({ ...d, value: Math.max(0, d.value) }))
        },
        availability: {
          current: 99.55,
          average: 99.1,
          sla: 99.0,
          uptime: '29d 21h 15m',
          trend: 'improving',
          timeSeries: generateTimeSeriesData(99.55, 0.6, 24).map(d => ({ ...d, value: Math.min(100, Math.max(95, d.value)) }))
        },
        performance_score: 91.8,
        endpoints: [
          {
            path: '/api/v3/files',
            responseTime: 580,
            requests24h: 4847,
            errorRate: 0.38,
            performance_score: 93.4
          },
          {
            path: '/api/v3/urls',
            responseTime: 720,
            requests24h: 3928,
            errorRate: 0.52,
            performance_score: 90.1
          },
          {
            path: '/api/v3/domains',
            responseTime: 640,
            requests24h: 4072,
            errorRate: 0.41,
            performance_score: 92.5
          }
        ]
      },
      {
        id: 'nasa',
        name: 'NASA Open Data API',
        category: 'Science',
        responseTime: {
          current: 450,
          average: 420,
          min: 220,
          max: 780,
          p95: 580,
          p99: 680,
          trend: 'excellent',
          timeSeries: generateTimeSeriesData(450, 80)
        },
        throughput: {
          current: 409,
          average: 445,
          peak: 750,
          requestsPerSecond: 11.4,
          trend: 'stable',
          timeSeries: generateTimeSeriesData(409, 120)
        },
        errorRate: {
          current: 0.05,
          average: 0.08,
          peak: 0.3,
          trend: 'excellent',
          timeSeries: generateTimeSeriesData(0.05, 0.02, 24).map(d => ({ ...d, value: Math.max(0, d.value) }))
        },
        availability: {
          current: 99.95,
          average: 99.9,
          sla: 99.5,
          uptime: '29d 23h 58m',
          trend: 'excellent',
          timeSeries: generateTimeSeriesData(99.95, 0.1, 24).map(d => ({ ...d, value: Math.min(100, Math.max(99, d.value)) }))
        },
        performance_score: 98.7,
        endpoints: [
          {
            path: '/planetary/apod',
            responseTime: 380,
            requests24h: 3487,
            errorRate: 0.03,
            performance_score: 99.2
          },
          {
            path: '/planetary/earth/imagery',
            responseTime: 520,
            requests24h: 3192,
            errorRate: 0.06,
            performance_score: 98.5
          },
          {
            path: '/neo/rest/v1/feed',
            responseTime: 450,
            requests24h: 3168,
            errorRate: 0.08,
            performance_score: 98.1
          }
        ]
      }
    ];

    // Calculate overall performance metrics
    const overall = {
      avgResponseTime: Math.round(apis.reduce((sum, api) => sum + api.responseTime.current, 0) / apis.length),
      totalThroughput: apis.reduce((sum, api) => sum + api.throughput.current, 0),
      avgErrorRate: (apis.reduce((sum, api) => sum + api.errorRate.current, 0) / apis.length).toFixed(2),
      avgAvailability: (apis.reduce((sum, api) => sum + api.availability.current, 0) / apis.length).toFixed(2),
      overallScore: (apis.reduce((sum, api) => sum + api.performance_score, 0) / apis.length).toFixed(1),
      totalRequests24h: apis.reduce((sum, api) => sum + api.throughput.current * 24, 0),
      healthyApis: apis.filter(api => api.performance_score >= 90).length,
      warningApis: apis.filter(api => api.performance_score >= 75 && api.performance_score < 90).length,
      criticalApis: apis.filter(api => api.performance_score < 75).length
    };

    return {
      timestamp: new Date().toISOString(),
      timeRange,
      apis,
      overall
    };
  };

  useEffect(() => {
    const loadPerformanceData = () => {
      setPerformanceData(generatePerformanceData());
      setLoading(false);
    };

    loadPerformanceData();

    if (autoRefresh) {
      const interval = setInterval(loadPerformanceData, 30000);
      return () => clearInterval(interval);
    }
  }, [timeRange, autoRefresh]);

  const getTrendColor = (trend) => {
    switch (trend) {
      case 'excellent': return '#28a745';
      case 'improving': return '#20c997';
      case 'stable': return '#17a2b8';
      case 'decreasing': return '#ffc107';
      case 'degrading': return '#fd7e14';
      case 'concerning': return '#dc3545';
      case 'critical': return '#721c24';
      default: return '#6c757d';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 95) return '#28a745';
    if (score >= 90) return '#20c997';
    if (score >= 80) return '#17a2b8';
    if (score >= 70) return '#ffc107';
    if (score >= 60) return '#fd7e14';
    return '#dc3545';
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const filteredApis = selectedApi === 'all' 
    ? performanceData?.apis || []
    : performanceData?.apis.filter(api => api.id === selectedApi) || [];

  if (loading) {
    return (
      <div className="api-performance-metrics loading">
        <div className="loading-spinner">
          <i className="fas fa-chart-line fa-pulse"></i>
          <p>Loading performance metrics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="api-performance-metrics">
      <div className="performance-header">
        <div className="header-info">
          <h2>
            <i className="fas fa-chart-line"></i>
            API Performance Metrics
          </h2>
          <p>Real-time performance analytics and trending for external API integrations</p>
        </div>

        <div className="header-controls">
          <div className="control-group">
            <label>API:</label>
            <select value={selectedApi} onChange={(e) => setSelectedApi(e.target.value)}>
              <option value="all">All APIs</option>
              {performanceData?.apis.map(api => (
                <option key={api.id} value={api.id}>{api.name}</option>
              ))}
            </select>
          </div>

          <div className="control-group">
            <label>Time Range:</label>
            <select value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
              <option value="1h">Last Hour</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
            </select>
          </div>

          <div className="control-group">
            <label>Metric:</label>
            <select value={metricType} onChange={(e) => setMetricType(e.target.value)}>
              <option value="response_time">Response Time</option>
              <option value="throughput">Throughput</option>
              <option value="error_rate">Error Rate</option>
              <option value="availability">Availability</option>
            </select>
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

      <div className="performance-overview">
        <div className="overview-cards">
          <div className="overview-card primary">
            <div className="card-icon">
              <i className="fas fa-tachometer-alt"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{performanceData.overall.overallScore}</div>
              <div className="card-label">Overall Score</div>
              <div className="card-trend">Performance Index</div>
            </div>
          </div>

          <div className="overview-card info">
            <div className="card-icon">
              <i className="fas fa-clock"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{performanceData.overall.avgResponseTime}ms</div>
              <div className="card-label">Avg Response Time</div>
              <div className="card-trend">Across all APIs</div>
            </div>
          </div>

          <div className="overview-card success">
            <div className="card-icon">
              <i className="fas fa-exchange-alt"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{formatNumber(performanceData.overall.totalThroughput)}</div>
              <div className="card-label">Total Throughput</div>
              <div className="card-trend">Requests/hour</div>
            </div>
          </div>

          <div className="overview-card warning">
            <div className="card-icon">
              <i className="fas fa-exclamation-triangle"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{performanceData.overall.avgErrorRate}%</div>
              <div className="card-label">Avg Error Rate</div>
              <div className="card-trend">System-wide</div>
            </div>
          </div>

          <div className="overview-card uptime">
            <div className="card-icon">
              <i className="fas fa-server"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{performanceData.overall.avgAvailability}%</div>
              <div className="card-label">Avg Availability</div>
              <div className="card-trend">Uptime average</div>
            </div>
          </div>

          <div className="overview-card requests">
            <div className="card-icon">
              <i className="fas fa-chart-bar"></i>
            </div>
            <div className="card-content">
              <div className="card-value">{formatNumber(performanceData.overall.totalRequests24h)}</div>
              <div className="card-label">Total Requests</div>
              <div className="card-trend">Last 24 hours</div>
            </div>
          </div>
        </div>
      </div>

      <div className="metrics-dashboard">
        {filteredApis.map(api => (
          <div key={api.id} className="api-metrics-card">
            <div className="api-metrics-header">
              <div className="api-info">
                <h3>{api.name}</h3>
                <span className="api-category">{api.category}</span>
              </div>
              <div 
                className="performance-score"
                style={{ color: getScoreColor(api.performance_score) }}
              >
                <span className="score-value">{api.performance_score}/100</span>
                <span className="score-label">Performance Score</span>
              </div>
            </div>

            <div className="metrics-grid">
              <div className="metric-card response-time">
                <div className="metric-header">
                  <i className="fas fa-clock"></i>
                  <span>Response Time</span>
                </div>
                <div className="metric-values">
                  <div className="primary-value">{api.responseTime.current}ms</div>
                  <div className="secondary-values">
                    <span>Avg: {api.responseTime.average}ms</span>
                    <span>P95: {api.responseTime.p95}ms</span>
                    <span>Range: {api.responseTime.min}-{api.responseTime.max}ms</span>
                  </div>
                </div>
                <div 
                  className="metric-trend"
                  style={{ color: getTrendColor(api.responseTime.trend) }}
                >
                  <i className={`fas fa-arrow-${api.responseTime.trend === 'improving' ? 'down' : 
                                api.responseTime.trend === 'degrading' || api.responseTime.trend === 'critical' ? 'up' : 'right'}`}></i>
                  {api.responseTime.trend}
                </div>
              </div>

              <div className="metric-card throughput">
                <div className="metric-header">
                  <i className="fas fa-exchange-alt"></i>
                  <span>Throughput</span>
                </div>
                <div className="metric-values">
                  <div className="primary-value">{api.throughput.current}/hr</div>
                  <div className="secondary-values">
                    <span>RPS: {api.throughput.requestsPerSecond}</span>
                    <span>Peak: {api.throughput.peak}/hr</span>
                    <span>Avg: {api.throughput.average}/hr</span>
                  </div>
                </div>
                <div 
                  className="metric-trend"
                  style={{ color: getTrendColor(api.throughput.trend) }}
                >
                  <i className={`fas fa-arrow-${api.throughput.trend === 'stable' ? 'right' : 
                                api.throughput.trend === 'decreasing' ? 'down' : 'up'}`}></i>
                  {api.throughput.trend}
                </div>
              </div>

              <div className="metric-card error-rate">
                <div className="metric-header">
                  <i className="fas fa-exclamation-circle"></i>
                  <span>Error Rate</span>
                </div>
                <div className="metric-values">
                  <div className="primary-value">{api.errorRate.current}%</div>
                  <div className="secondary-values">
                    <span>Avg: {api.errorRate.average}%</span>
                    <span>Peak: {api.errorRate.peak}%</span>
                    <span>Target: &lt;1%</span>
                  </div>
                </div>
                <div 
                  className="metric-trend"
                  style={{ color: getTrendColor(api.errorRate.trend) }}
                >
                  <i className={`fas fa-arrow-${api.errorRate.trend === 'improving' ? 'down' : 
                                api.errorRate.trend === 'concerning' ? 'up' : 'right'}`}></i>
                  {api.errorRate.trend}
                </div>
              </div>

              <div className="metric-card availability">
                <div className="metric-header">
                  <i className="fas fa-server"></i>
                  <span>Availability</span>
                </div>
                <div className="metric-values">
                  <div className="primary-value">{api.availability.current}%</div>
                  <div className="secondary-values">
                    <span>SLA: {api.availability.sla}%</span>
                    <span>Uptime: {api.availability.uptime}</span>
                    <span>Avg: {api.availability.average}%</span>
                  </div>
                </div>
                <div 
                  className="metric-trend"
                  style={{ color: getTrendColor(api.availability.trend) }}
                >
                  <i className={`fas fa-arrow-${api.availability.trend === 'improving' || api.availability.trend === 'excellent' ? 'up' : 
                                api.availability.trend === 'degrading' ? 'down' : 'right'}`}></i>
                  {api.availability.trend}
                </div>
              </div>
            </div>

            <div className="endpoints-performance">
              <div className="endpoints-header">
                <h4>Endpoint Performance</h4>
                <span className="endpoints-count">{api.endpoints.length} endpoints</span>
              </div>
              <div className="endpoints-list">
                {api.endpoints.map((endpoint, index) => (
                  <div key={index} className="endpoint-item">
                    <div className="endpoint-path">{endpoint.path}</div>
                    <div className="endpoint-metrics">
                      <span className="endpoint-response-time">{endpoint.responseTime}ms</span>
                      <span className="endpoint-requests">{formatNumber(endpoint.requests24h)} req/24h</span>
                      <span className="endpoint-errors">{endpoint.errorRate}% errors</span>
                      <span 
                        className="endpoint-score"
                        style={{ color: getScoreColor(endpoint.performance_score) }}
                      >
                        {endpoint.performance_score}/100
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="api-actions">
              <button className="action-btn primary">
                <i className="fas fa-chart-area"></i>
                View Detailed Charts
              </button>
              <button className="action-btn secondary">
                <i className="fas fa-download"></i>
                Export Metrics
              </button>
              <button className="action-btn tertiary">
                <i className="fas fa-bell"></i>
                Setup Alerts
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="performance-trends">
        <div className="trends-header">
          <h3>Performance Trends</h3>
          <p>Historical performance data over {timeRange}</p>
        </div>
        <div className="trends-chart-placeholder">
          <div className="chart-info">
            <i className="fas fa-chart-line"></i>
            <p>Interactive performance charts would be rendered here</p>
            <p>Showing {metricType.replace('_', ' ')} trends for {selectedApi === 'all' ? 'all APIs' : filteredApis[0]?.name}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ApiPerformanceMetrics;
