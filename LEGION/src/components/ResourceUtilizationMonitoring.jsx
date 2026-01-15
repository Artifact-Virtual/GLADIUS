// components/ResourceUtilizationMonitoring.jsx

import React, { useState, useEffect } from 'react';

const ResourceUtilizationMonitoring = () => {
  const [resourceData, setResourceData] = useState(null);
  const [selectedResource, setSelectedResource] = useState('all');
  const [timeframe, setTimeframe] = useState('1h');
  const [alertsOnly, setAlertsOnly] = useState(false);
  const [viewMode, setViewMode] = useState('grid');

  // Generate comprehensive resource utilization data
  const generateResourceData = () => {
    const data = {
      timestamp: new Date().toISOString(),
      timeframe: timeframe,
      total_resources: {
        cpu_cores: 64,
        memory_gb: 256,
        storage_tb: 48,
        network_gbps: 100,
        gpu_count: 8
      },
      resource_categories: {
        compute: {
          name: 'Compute Resources',
          utilization: Math.floor(Math.random() * 25) + 65,
          capacity: Math.floor(Math.random() * 15) + 80,
          efficiency: Math.floor(Math.random() * 20) + 75,
          trend: 'stable',
          resources: {
            cpu: {
              name: 'CPU Cores',
              used: Math.floor(Math.random() * 20) + 40,
              total: 64,
              utilization: Math.floor(Math.random() * 25) + 65,
              peak_utilization: Math.floor(Math.random() * 15) + 82,
              temperature: Math.floor(Math.random() * 10) + 65,
              frequency: (Math.random() * 0.8 + 2.8).toFixed(1),
              power_consumption: Math.floor(Math.random() * 50) + 180,
              alerts: []
            },
            memory: {
              name: 'Memory (RAM)',
              used: Math.floor(Math.random() * 80) + 160,
              total: 256,
              utilization: Math.floor(Math.random() * 20) + 70,
              peak_utilization: Math.floor(Math.random() * 10) + 85,
              swap_usage: Math.floor(Math.random() * 5) + 2,
              cache_hit_ratio: Math.floor(Math.random() * 8) + 88,
              fragmentation: Math.floor(Math.random() * 8) + 5,
              alerts: Math.random() > 0.8 ? ['High fragmentation detected'] : []
            },
            gpu: {
              name: 'GPU Processors',
              used: Math.floor(Math.random() * 4) + 2,
              total: 8,
              utilization: Math.floor(Math.random() * 30) + 45,
              peak_utilization: Math.floor(Math.random() * 20) + 75,
              memory_usage: Math.floor(Math.random() * 25) + 60,
              temperature: Math.floor(Math.random() * 15) + 75,
              power_consumption: Math.floor(Math.random() * 100) + 250,
              alerts: Math.random() > 0.9 ? ['High temperature warning'] : []
            }
          }
        },
        storage: {
          name: 'Storage Systems',
          utilization: Math.floor(Math.random() * 20) + 70,
          capacity: Math.floor(Math.random() * 25) + 65,
          efficiency: Math.floor(Math.random() * 18) + 77,
          trend: 'increasing',
          resources: {
            ssd: {
              name: 'SSD Storage',
              used: Math.floor(Math.random() * 15) + 25,
              total: 48,
              utilization: Math.floor(Math.random() * 20) + 70,
              iops: Math.floor(Math.random() * 5000) + 15000,
              latency: (Math.random() * 2 + 1).toFixed(1),
              throughput: Math.floor(Math.random() * 200) + 800,
              health_score: Math.floor(Math.random() * 10) + 90,
              alerts: []
            },
            hdd: {
              name: 'HDD Storage',
              used: Math.floor(Math.random() * 8) + 12,
              total: 96,
              utilization: Math.floor(Math.random() * 15) + 60,
              iops: Math.floor(Math.random() * 200) + 300,
              latency: Math.floor(Math.random() * 5) + 8,
              throughput: Math.floor(Math.random() * 100) + 150,
              health_score: Math.floor(Math.random() * 15) + 82,
              alerts: Math.random() > 0.85 ? ['Disk health declining'] : []
            },
            cache: {
              name: 'Cache Storage',
              used: (Math.random() * 2 + 3).toFixed(1),
              total: 8,
              utilization: Math.floor(Math.random() * 25) + 65,
              hit_ratio: Math.floor(Math.random() * 8) + 88,
              miss_ratio: Math.floor(Math.random() * 8) + 5,
              eviction_rate: (Math.random() * 5 + 2).toFixed(1),
              alerts: []
            }
          }
        },
        network: {
          name: 'Network Infrastructure',
          utilization: Math.floor(Math.random() * 30) + 50,
          capacity: Math.floor(Math.random() * 20) + 75,
          efficiency: Math.floor(Math.random() * 15) + 80,
          trend: 'stable',
          resources: {
            bandwidth: {
              name: 'Network Bandwidth',
              used: Math.floor(Math.random() * 40) + 30,
              total: 100,
              utilization: Math.floor(Math.random() * 30) + 50,
              peak_utilization: Math.floor(Math.random() * 20) + 75,
              latency: Math.floor(Math.random() * 10) + 15,
              packet_loss: (Math.random() * 0.5).toFixed(2),
              throughput: Math.floor(Math.random() * 30) + 45,
              alerts: []
            },
            connections: {
              name: 'Active Connections',
              used: Math.floor(Math.random() * 2000) + 3000,
              total: 10000,
              utilization: Math.floor(Math.random() * 25) + 45,
              peak_connections: Math.floor(Math.random() * 1000) + 5500,
              connection_rate: Math.floor(Math.random() * 100) + 150,
              timeout_rate: (Math.random() * 2 + 1).toFixed(1),
              alerts: Math.random() > 0.9 ? ['High connection rate detected'] : []
            },
            ports: {
              name: 'Network Ports',
              used: Math.floor(Math.random() * 200) + 300,
              total: 65535,
              utilization: Math.floor(Math.random() * 5) + 2,
              listening_ports: Math.floor(Math.random() * 50) + 80,
              blocked_ports: Math.floor(Math.random() * 10) + 5,
              security_violations: Math.floor(Math.random() * 3) + 0,
              alerts: []
            }
          }
        },
        application: {
          name: 'Application Resources',
          utilization: Math.floor(Math.random() * 20) + 75,
          capacity: Math.floor(Math.random() * 18) + 77,
          efficiency: Math.floor(Math.random() * 22) + 73,
          trend: 'improving',
          resources: {
            processes: {
              name: 'System Processes',
              used: Math.floor(Math.random() * 50) + 120,
              total: 1000,
              utilization: Math.floor(Math.random() * 15) + 75,
              cpu_usage: Math.floor(Math.random() * 20) + 65,
              memory_usage: Math.floor(Math.random() * 25) + 70,
              zombie_processes: Math.floor(Math.random() * 3) + 0,
              alerts: []
            },
            threads: {
              name: 'Application Threads',
              used: Math.floor(Math.random() * 200) + 800,
              total: 2000,
              utilization: Math.floor(Math.random() * 25) + 65,
              active_threads: Math.floor(Math.random() * 150) + 700,
              blocked_threads: Math.floor(Math.random() * 20) + 10,
              deadlocks: Math.floor(Math.random() * 2) + 0,
              alerts: Math.random() > 0.9 ? ['Thread pool exhaustion warning'] : []
            },
            file_handles: {
              name: 'File Handles',
              used: Math.floor(Math.random() * 500) + 2000,
              total: 65536,
              utilization: Math.floor(Math.random() * 10) + 15,
              open_files: Math.floor(Math.random() * 400) + 1800,
              leaked_handles: Math.floor(Math.random() * 5) + 0,
              max_reached: false,
              alerts: []
            }
          }
        }
      },
      optimization_opportunities: [
        {
          resource: 'memory',
          opportunity: 'Memory defragmentation',
          potential_gain: '12% efficiency improvement',
          effort: 'low',
          impact: 'medium',
          estimated_time: '2 hours'
        },
        {
          resource: 'storage',
          opportunity: 'SSD cache optimization',
          potential_gain: '25% faster access times',
          effort: 'medium',
          impact: 'high',
          estimated_time: '4 hours'
        },
        {
          resource: 'network',
          opportunity: 'Connection pooling optimization',
          potential_gain: '18% bandwidth efficiency',
          effort: 'medium',
          impact: 'medium',
          estimated_time: '6 hours'
        },
        {
          resource: 'cpu',
          opportunity: 'Process affinity optimization',
          potential_gain: '8% performance boost',
          effort: 'low',
          impact: 'low',
          estimated_time: '1 hour'
        }
      ],
      resource_alerts: [
        {
          severity: 'warning',
          resource: 'memory',
          message: 'Memory fragmentation above 10%',
          timestamp: new Date(Date.now() - Math.random() * 300000).toISOString(),
          resolved: false
        },
        {
          severity: 'info',
          resource: 'storage',
          message: 'SSD optimization completed successfully',
          timestamp: new Date(Date.now() - Math.random() * 600000).toISOString(),
          resolved: true
        },
        {
          severity: 'critical',
          resource: 'network',
          message: 'High connection rate detected',
          timestamp: new Date(Date.now() - Math.random() * 120000).toISOString(),
          resolved: false
        }
      ].filter(alert => !alertsOnly || !alert.resolved)
    };

    return data;
  };

  useEffect(() => {
    const loadData = () => {
      setResourceData(generateResourceData());
    };

    loadData();
    const interval = setInterval(loadData, 15000); // Update every 15 seconds

    return () => clearInterval(interval);
  }, [selectedResource, timeframe, alertsOnly]);

  const getUtilizationColor = (utilization) => {
    if (utilization >= 90) return '#dc3545';
    if (utilization >= 80) return '#ffc107';
    if (utilization >= 70) return '#17a2b8';
    return '#28a745';
  };

  const getTrendColor = (trend) => {
    switch (trend) {
      case 'increasing': return '#dc3545';
      case 'decreasing': return '#28a745';
      case 'stable': return '#17a2b8';
      case 'improving': return '#28a745';
      default: return '#6c757d';
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return '#dc3545';
      case 'warning': return '#ffc107';
      case 'info': return '#17a2b8';
      default: return '#6c757d';
    }
  };

  const filteredCategories = selectedResource === 'all' 
    ? Object.entries(resourceData?.resource_categories || {})
    : Object.entries(resourceData?.resource_categories || {}).filter(([key]) => key === selectedResource);

  if (!resourceData) {
    return (
      <div className="resource-utilization-monitoring loading">
        <div className="loading-spinner">
          <i className="fas fa-server"></i>
          <p>Loading resource utilization data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="resource-utilization-monitoring">
      <div className="monitoring-header">
        <div className="header-left">
          <h2>
            <i className="fas fa-server"></i>
            Resource Utilization Monitoring
          </h2>
          <p>Comprehensive system resource monitoring and optimization analysis</p>
        </div>
        
        <div className="header-controls">
          <div className="timeframe-selector">
            {['1h', '6h', '24h', '7d'].map(period => (
              <button
                key={period}
                className={`time-btn ${timeframe === period ? 'active' : ''}`}
                onClick={() => setTimeframe(period)}
              >
                {period}
              </button>
            ))}
          </div>
          
          <div className="view-controls">
            <label className="alerts-toggle">
              <input
                type="checkbox"
                checked={alertsOnly}
                onChange={(e) => setAlertsOnly(e.target.checked)}
              />
              Alerts Only
            </label>
            
            <div className="view-mode-selector">
              {['grid', 'list'].map(mode => (
                <button
                  key={mode}
                  className={`mode-btn ${viewMode === mode ? 'active' : ''}`}
                  onClick={() => setViewMode(mode)}
                >
                  <i className={`fas fa-${mode === 'grid' ? 'th' : 'list'}`}></i>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="monitoring-content">
        <div className="resource-overview">
          <div className="overview-stats">
            <div className="stat-card">
              <div className="stat-icon">
                <i className="fas fa-microchip"></i>
              </div>
              <div className="stat-content">
                <div className="stat-value">{resourceData.total_resources.cpu_cores}</div>
                <div className="stat-label">CPU Cores</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">
                <i className="fas fa-memory"></i>
              </div>
              <div className="stat-content">
                <div className="stat-value">{resourceData.total_resources.memory_gb}GB</div>
                <div className="stat-label">Memory</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">
                <i className="fas fa-hdd"></i>
              </div>
              <div className="stat-content">
                <div className="stat-value">{resourceData.total_resources.storage_tb}TB</div>
                <div className="stat-label">Storage</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">
                <i className="fas fa-network-wired"></i>
              </div>
              <div className="stat-content">
                <div className="stat-value">{resourceData.total_resources.network_gbps}Gbps</div>
                <div className="stat-label">Network</div>
              </div>
            </div>
          </div>
        </div>

        <div className="resource-filter">
          <label>Resource Category:</label>
          <select 
            value={selectedResource} 
            onChange={(e) => setSelectedResource(e.target.value)}
          >
            <option value="all">All Resources</option>
            {Object.entries(resourceData.resource_categories).map(([key, category]) => (
              <option key={key} value={key}>{category.name}</option>
            ))}
          </select>
        </div>

        <div className={`resource-categories ${viewMode}`}>
          {filteredCategories.map(([key, category]) => (
            <div key={key} className="category-section">
              <div className="category-header">
                <h3>{category.name}</h3>
                <div className="category-metrics">
                  <div className="metric-item">
                    <span className="metric-label">Utilization</span>
                    <div className="metric-bar">
                      <div 
                        className="metric-fill"
                        style={{ 
                          width: `${category.utilization}%`,
                          backgroundColor: getUtilizationColor(category.utilization)
                        }}
                      ></div>
                      <span className="metric-value">{category.utilization}%</span>
                    </div>
                  </div>
                  <div className="trend-indicator" style={{ color: getTrendColor(category.trend) }}>
                    <i className={`fas fa-arrow-${category.trend === 'increasing' || category.trend === 'improving' ? 'up' : category.trend === 'decreasing' ? 'down' : 'right'}`}></i>
                    {category.trend}
                  </div>
                </div>
              </div>

              <div className="resources-grid">
                {Object.entries(category.resources).map(([resourceKey, resource]) => (
                  <div key={resourceKey} className="resource-card">
                    <div className="resource-header">
                      <h4>{resource.name}</h4>
                      {resource.alerts && resource.alerts.length > 0 && (
                        <div className="alert-indicator">
                          <i className="fas fa-exclamation-triangle"></i>
                          {resource.alerts.length}
                        </div>
                      )}
                    </div>

                    <div className="resource-utilization">
                      <div className="utilization-circle">
                        <span 
                          className="utilization-value"
                          style={{ color: getUtilizationColor(resource.utilization) }}
                        >
                          {resource.utilization}%
                        </span>
                        <span className="utilization-label">Used</span>
                      </div>
                      <div className="usage-info">
                        <span className="usage-text">
                          {resource.used} / {resource.total}
                          {resourceKey === 'cpu' || resourceKey === 'gpu' ? ' cores' : 
                           resourceKey === 'memory' || resourceKey === 'cache' ? ' GB' :
                           resourceKey === 'ssd' || resourceKey === 'hdd' ? ' TB' :
                           resourceKey === 'bandwidth' ? ' Gbps' :
                           resourceKey === 'connections' || resourceKey === 'processes' || resourceKey === 'threads' || resourceKey === 'file_handles' ? '' :
                           resourceKey === 'ports' ? ' ports' : ''}
                        </span>
                      </div>
                    </div>

                    <div className="resource-metrics">
                      {Object.entries(resource).map(([metricKey, value]) => {
                        if (['name', 'used', 'total', 'utilization', 'alerts'].includes(metricKey)) return null;
                        return (
                          <div key={metricKey} className="metric-row">
                            <span className="metric-name">{metricKey.replace(/_/g, ' ')}</span>
                            <span className="metric-value">
                              {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : 
                               typeof value === 'string' ? value : 
                               value}
                              {metricKey.includes('temperature') ? '°C' :
                               metricKey.includes('frequency') ? ' GHz' :
                               metricKey.includes('power') ? 'W' :
                               metricKey.includes('latency') ? 'ms' :
                               metricKey.includes('throughput') ? ' MB/s' :
                               metricKey.includes('iops') ? ' IOPS' :
                               metricKey.includes('ratio') || metricKey.includes('score') ? '%' : ''}
                            </span>
                          </div>
                        );
                      })}
                    </div>

                    {resource.alerts && resource.alerts.length > 0 && (
                      <div className="resource-alerts">
                        {resource.alerts.map((alert, index) => (
                          <div key={index} className="alert-item warning">
                            <i className="fas fa-exclamation-triangle"></i>
                            <span>{alert}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="optimization-section">
          <h3>Optimization Opportunities</h3>
          <div className="opportunities-grid">
            {resourceData.optimization_opportunities.map((opportunity, index) => (
              <div key={index} className="opportunity-card">
                <div className="opportunity-header">
                  <h4>{opportunity.opportunity}</h4>
                  <div className="opportunity-resource">{opportunity.resource}</div>
                </div>
                <div className="opportunity-gain">{opportunity.potential_gain}</div>
                <div className="opportunity-details">
                  <div className="detail-item">
                    <span className="detail-label">Effort:</span>
                    <span className={`detail-value effort-${opportunity.effort}`}>
                      {opportunity.effort}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Impact:</span>
                    <span className={`detail-value impact-${opportunity.impact}`}>
                      {opportunity.impact}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Time:</span>
                    <span className="detail-value">{opportunity.estimated_time}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {resourceData.resource_alerts.length > 0 && (
          <div className="alerts-section">
            <h3>Resource Alerts</h3>
            <div className="alerts-list">
              {resourceData.resource_alerts.map((alert, index) => (
                <div 
                  key={index} 
                  className={`alert-card ${alert.severity} ${alert.resolved ? 'resolved' : ''}`}
                >
                  <div className="alert-icon">
                    <i className={`fas fa-${alert.severity === 'critical' ? 'exclamation-circle' : alert.severity === 'warning' ? 'exclamation-triangle' : 'info-circle'}`}></i>
                  </div>
                  <div className="alert-content">
                    <div className="alert-message">{alert.message}</div>
                    <div className="alert-meta">
                      <span className="alert-resource">{alert.resource}</span>
                      <span className="alert-time">
                        {new Date(alert.timestamp).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <div className="alert-status">
                    {alert.resolved ? 'Resolved' : 'Active'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResourceUtilizationMonitoring;
