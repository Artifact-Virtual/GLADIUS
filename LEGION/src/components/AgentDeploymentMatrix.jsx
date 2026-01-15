import React, { useState, useEffect, useCallback } from 'react';

const AgentDeploymentMatrix = () => {
  const [agents, setAgents] = useState([]);
  const [deployments, setDeployments] = useState([]);
  const [environments, setEnvironments] = useState([]);
  const [regions, setRegions] = useState([]);
  const [statusMatrix, setStatusMatrix] = useState([]);
  const [selectedView, setSelectedView] = useState('matrix');
  const [matrixFilters, setMatrixFilters] = useState({
    environment: 'all',
    status: 'all',
    region: 'all',
    agentType: 'all',
    deployment: 'all'
  });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [selectedCell, setSelectedCell] = useState(null);
  const [deploymentModal, setDeploymentModal] = useState(false);
  const [selectedDeployment, setSelectedDeployment] = useState(null);

  // Mock data generators
  const generateEnvironments = useCallback(() => {
    return [
      { id: 'prod', name: 'Production', priority: 'critical', color: '#dc3545' },
      { id: 'staging', name: 'Staging', priority: 'high', color: '#fd7e14' },
      { id: 'dev', name: 'Development', priority: 'medium', color: '#ffc107' },
      { id: 'test', name: 'Testing', priority: 'low', color: '#28a745' }
    ];
  }, []);

  const generateRegions = useCallback(() => {
    return [
      { id: 'us-east', name: 'US East', zone: 'america' },
      { id: 'us-west', name: 'US West', zone: 'america' },
      { id: 'eu-central', name: 'EU Central', zone: 'europe' },
      { id: 'asia-pacific', name: 'Asia Pacific', zone: 'asia' }
    ];
  }, []);

  const generateAgents = useCallback(() => {
    const agentTypes = ['analytics', 'automation', 'communication', 'research', 'optimization', 'monitoring'];
    const statuses = ['deployed', 'deploying', 'failed', 'pending', 'terminated', 'updating'];
    
    const agentNames = [
      'Analytics Engine Alpha', 'Data Processor Beta', 'Market Intelligence Gamma', 'Financial Analysis Delta',
      'Customer Insight Epsilon', 'Performance Monitor Zeta', 'Automation Controller Eta', 'Communication Hub Theta',
      'Research Coordinator Iota', 'Optimization Agent Kappa', 'Security Monitor Lambda', 'Resource Manager Mu',
      'Workflow Agent Nu', 'Integration Agent Xi', 'Quality Assurance Omicron', 'Business Intelligence Pi'
    ];

    return Array.from({ length: 16 }, (_, index) => ({
      id: `agent-${index + 1}`,
      name: agentNames[index] || `Agent ${index + 1}`,
      type: agentTypes[Math.floor(Math.random() * agentTypes.length)],
      version: `v${Math.floor(Math.random() * 5) + 1}.${Math.floor(Math.random() * 10)}.${Math.floor(Math.random() * 10)}`,
      description: `Enterprise ${agentTypes[Math.floor(Math.random() * agentTypes.length)]} agent for business operations coordination`,
      requiredResources: {
        cpu: Math.floor(Math.random() * 4) + 1,
        memory: `${Math.floor(Math.random() * 8) + 2}GB`,
        storage: `${Math.floor(Math.random() * 50) + 10}GB`,
        network: Math.floor(Math.random() * 100) + 100
      },
      dependencies: Math.floor(Math.random() * 3),
      healthcheckEndpoint: `/api/agents/${index + 1}/health`,
      configurationHash: `cfg-${Math.random().toString(36).substring(7)}`,
      createdAt: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString(),
      lastModified: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      tags: ['production-ready', 'enterprise', 'scalable', 'monitored'].slice(0, Math.floor(Math.random() * 3) + 2)
    }));
  }, []);

  const generateDeployments = useCallback(() => {
    const deploymentStatuses = ['active', 'inactive', 'failed', 'pending', 'updating', 'rolling-back'];
    const environmentIds = ['prod', 'staging', 'dev', 'test'];
    const regionIds = ['us-east', 'us-west', 'eu-central', 'asia-pacific'];
    
    return Array.from({ length: 64 }, (_, index) => {
      const agentId = `agent-${(index % 16) + 1}`;
      const environmentId = environmentIds[Math.floor(index / 16)];
      const regionId = regionIds[Math.floor(Math.random() * regionIds.length)];
      const status = deploymentStatuses[Math.floor(Math.random() * deploymentStatuses.length)];
      
      return {
        id: `deploy-${index + 1}`,
        agentId,
        environmentId,
        regionId,
        status,
        version: `v${Math.floor(Math.random() * 5) + 1}.${Math.floor(Math.random() * 10)}.${Math.floor(Math.random() * 10)}`,
        deployedAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
        lastChecked: new Date(Date.now() - Math.random() * 60 * 60 * 1000).toISOString(),
        uptime: Math.floor(Math.random() * 100),
        healthStatus: ['healthy', 'warning', 'critical'][Math.floor(Math.random() * 3)],
        performanceScore: Math.floor(Math.random() * 40) + 60,
        resourceUsage: {
          cpu: Math.floor(Math.random() * 80) + 10,
          memory: Math.floor(Math.random() * 70) + 20,
          storage: Math.floor(Math.random() * 60) + 15,
          network: Math.floor(Math.random() * 90) + 10
        },
        metrics: {
          requestsPerSecond: Math.floor(Math.random() * 1000) + 100,
          responseTime: (Math.random() * 500 + 50).toFixed(0) + 'ms',
          errorRate: (Math.random() * 5).toFixed(2) + '%',
          throughput: (Math.random() * 10000 + 1000).toFixed(0) + '/hr'
        },
        configuration: {
          replicas: Math.floor(Math.random() * 5) + 1,
          autoScaling: Math.random() > 0.3,
          loadBalancing: Math.random() > 0.2,
          monitoring: Math.random() > 0.1
        },
        alerts: Math.floor(Math.random() * 10),
        warnings: Math.floor(Math.random() * 5),
        deploymentTime: (Math.random() * 600 + 120).toFixed(0) + 's',
        rollbackAvailable: Math.random() > 0.2,
        canUpdate: Math.random() > 0.3,
        logs: Math.floor(Math.random() * 1000) + 100,
        endpoint: `https://api-${regionId}.enterprise.local/agents/${agentId}`,
        instanceId: `i-${Math.random().toString(36).substring(7)}`,
        containerId: `cnt-${Math.random().toString(36).substring(7)}`
      };
    });
  }, []);

  const generateStatusMatrix = useCallback(() => {
    const environmentIds = ['prod', 'staging', 'dev', 'test'];
    const regionIds = ['us-east', 'us-west', 'eu-central', 'asia-pacific'];
    
    return environmentIds.flatMap(envId => 
      regionIds.map(regionId => ({
        id: `${envId}-${regionId}`,
        environmentId: envId,
        regionId,
        agentCount: Math.floor(Math.random() * 8) + 2,
        healthyCount: Math.floor(Math.random() * 6) + 1,
        warningCount: Math.floor(Math.random() * 2),
        criticalCount: Math.floor(Math.random() * 2),
        totalCapacity: Math.floor(Math.random() * 100) + 50,
        usedCapacity: Math.floor(Math.random() * 80) + 20,
        averagePerformance: Math.floor(Math.random() * 30) + 70,
        lastUpdate: new Date(Date.now() - Math.random() * 60 * 60 * 1000).toISOString(),
        status: ['optimal', 'degraded', 'critical'][Math.floor(Math.random() * 3)]
      }))
    );
  }, []);

  // Data loading
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setEnvironments(generateEnvironments());
        setRegions(generateRegions());
        setAgents(generateAgents());
        setDeployments(generateDeployments());
        setStatusMatrix(generateStatusMatrix());
        
      } catch (error) {
        console.error('Error loading deployment data:', error);
        setError('Failed to load deployment matrix. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [generateEnvironments, generateRegions, generateAgents, generateDeployments, generateStatusMatrix]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await new Promise(resolve => setTimeout(resolve, 800));
    
    setDeployments(generateDeployments());
    setStatusMatrix(generateStatusMatrix());
    
    setRefreshing(false);
  };

  const getDeploymentsByEnvironmentAndRegion = (envId, regionId) => {
    return deployments.filter(d => d.environmentId === envId && d.regionId === regionId);
  };

  const getStatusColor = (status) => {
    const colors = {
      active: '#28a745',
      deployed: '#28a745',
      inactive: '#6c757d',
      failed: '#dc3545',
      pending: '#ffc107',
      updating: '#17a2b8',
      'rolling-back': '#fd7e14',
      deploying: '#17a2b8',
      terminated: '#6c757d',
      healthy: '#28a745',
      warning: '#ffc107',
      critical: '#dc3545',
      optimal: '#28a745',
      degraded: '#ffc107'
    };
    return colors[status] || '#666';
  };

  const getHealthScore = (deploymentGroup) => {
    const total = deploymentGroup.length;
    if (total === 0) return 0;
    
    const healthy = deploymentGroup.filter(d => d.healthStatus === 'healthy').length;
    return Math.round((healthy / total) * 100);
  };

  const renderMatrixView = () => (
    <div className="matrix-content">
      <div className="matrix-controls">
        <div className="filter-group">
          <select 
            value={matrixFilters.environment} 
            onChange={(e) => setMatrixFilters({...matrixFilters, environment: e.target.value})}
          >
            <option value="all">All Environments</option>
            {environments.map(env => (
              <option key={env.id} value={env.id}>{env.name}</option>
            ))}
          </select>
          
          <select 
            value={matrixFilters.status} 
            onChange={(e) => setMatrixFilters({...matrixFilters, status: e.target.value})}
          >
            <option value="all">All Statuses</option>
            <option value="active">Active</option>
            <option value="failed">Failed</option>
            <option value="pending">Pending</option>
            <option value="updating">Updating</option>
          </select>
          
          <select 
            value={matrixFilters.region} 
            onChange={(e) => setMatrixFilters({...matrixFilters, region: e.target.value})}
          >
            <option value="all">All Regions</option>
            {regions.map(region => (
              <option key={region.id} value={region.id}>{region.name}</option>
            ))}
          </select>
        </div>
        
        <div className="matrix-legend">
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#28a745' }}></span>
            <span>Healthy</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#ffc107' }}></span>
            <span>Warning</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#dc3545' }}></span>
            <span>Critical</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#6c757d' }}></span>
            <span>Inactive</span>
          </div>
        </div>
      </div>

      <div className="deployment-matrix">
        <div className="matrix-header">
          <div className="matrix-corner">Environment / Region</div>
          {regions.map(region => (
            <div key={region.id} className="region-header">
              <h4>{region.name}</h4>
              <span className="region-zone">{region.zone}</span>
            </div>
          ))}
        </div>
        
        <div className="matrix-body">
          {environments.map(environment => (
            <div key={environment.id} className="matrix-row">
              <div className="environment-header">
                <h4 style={{ color: environment.color }}>{environment.name}</h4>
                <span className="env-priority">{environment.priority}</span>
              </div>
              
              {regions.map(region => {
                const deploymentGroup = getDeploymentsByEnvironmentAndRegion(environment.id, region.id);
                const healthScore = getHealthScore(deploymentGroup);
                const statusCounts = deploymentGroup.reduce((acc, d) => {
                  acc[d.status] = (acc[d.status] || 0) + 1;
                  return acc;
                }, {});
                
                return (
                  <div 
                    key={`${environment.id}-${region.id}`} 
                    className="matrix-cell"
                    onClick={() => {
                      setSelectedCell({environment, region, deployments: deploymentGroup});
                      setDeploymentModal(true);
                    }}
                  >
                    <div className="cell-summary">
                      <div className="cell-count">{deploymentGroup.length}</div>
                      <div className="cell-label">agents</div>
                    </div>
                    
                    <div className="cell-health">
                      <div className="health-bar">
                        <div 
                          className="health-fill" 
                          style={{ 
                            width: `${healthScore}%`,
                            backgroundColor: healthScore > 80 ? '#28a745' : healthScore > 60 ? '#ffc107' : '#dc3545'
                          }}
                        ></div>
                      </div>
                      <span className="health-score">{healthScore}%</span>
                    </div>
                    
                    <div className="cell-status-indicators">
                      {Object.entries(statusCounts).map(([status, count]) => (
                        <div key={status} className="status-indicator">
                          <span 
                            className="status-dot" 
                            style={{ backgroundColor: getStatusColor(status) }}
                          ></span>
                          <span className="status-count">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderStatusView = () => (
    <div className="status-content">
      <div className="status-overview">
        <div className="status-metrics">
          <div className="status-metric">
            <div className="metric-icon">
              <i className="fas fa-server"></i>
            </div>
            <div className="metric-data">
              <h3>{deployments.length}</h3>
              <p>Total Deployments</p>
              <span>{deployments.filter(d => d.status === 'active').length} active</span>
            </div>
          </div>
          
          <div className="status-metric">
            <div className="metric-icon">
              <i className="fas fa-globe"></i>
            </div>
            <div className="metric-data">
              <h3>{environments.length}</h3>
              <p>Environments</p>
              <span>{regions.length} regions</span>
            </div>
          </div>
          
          <div className="status-metric">
            <div className="metric-icon">
              <i className="fas fa-heartbeat"></i>
            </div>
            <div className="metric-data">
              <h3>{Math.round((deployments.filter(d => d.healthStatus === 'healthy').length / deployments.length) * 100)}%</h3>
              <p>Health Score</p>
              <span>{deployments.filter(d => d.healthStatus === 'healthy').length} healthy</span>
            </div>
          </div>
          
          <div className="status-metric">
            <div className="metric-icon">
              <i className="fas fa-chart-line"></i>
            </div>
            <div className="metric-data">
              <h3>{Math.round(deployments.reduce((sum, d) => sum + d.performanceScore, 0) / deployments.length)}%</h3>
              <p>Avg Performance</p>
              <span>{deployments.filter(d => d.performanceScore > 80).length} high</span>
            </div>
          </div>
        </div>
      </div>

      <div className="status-breakdown">
        <div className="breakdown-section">
          <h3>Deployment Status Distribution</h3>
          <div className="status-chart">
            {['active', 'pending', 'failed', 'updating'].map(status => {
              const count = deployments.filter(d => d.status === status).length;
              const percentage = deployments.length > 0 ? (count / deployments.length) * 100 : 0;
              
              return (
                <div key={status} className="status-bar">
                  <div className="bar-header">
                    <span className="status-name">{status}</span>
                    <span className="status-count">{count}</span>
                  </div>
                  <div className="bar-container">
                    <div 
                      className="bar-fill" 
                      style={{ 
                        width: `${percentage}%`,
                        backgroundColor: getStatusColor(status)
                      }}
                    ></div>
                  </div>
                  <span className="bar-percentage">{percentage.toFixed(1)}%</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="breakdown-section">
          <h3>Regional Distribution</h3>
          <div className="region-breakdown">
            {regions.map(region => {
              const regionDeployments = deployments.filter(d => d.regionId === region.id);
              const healthyCount = regionDeployments.filter(d => d.healthStatus === 'healthy').length;
              const healthPercentage = regionDeployments.length > 0 ? (healthyCount / regionDeployments.length) * 100 : 0;
              
              return (
                <div key={region.id} className="region-card">
                  <h4>{region.name}</h4>
                  <div className="region-stats">
                    <div className="stat">
                      <span className="stat-value">{regionDeployments.length}</span>
                      <span className="stat-label">deployments</span>
                    </div>
                    <div className="stat">
                      <span className="stat-value">{healthPercentage.toFixed(0)}%</span>
                      <span className="stat-label">healthy</span>
                    </div>
                  </div>
                  <div className="region-health-bar">
                    <div 
                      className="region-health-fill" 
                      style={{ 
                        width: `${healthPercentage}%`,
                        backgroundColor: healthPercentage > 80 ? '#28a745' : healthPercentage > 60 ? '#ffc107' : '#dc3545'
                      }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (selectedView) {
      case 'matrix':
        return renderMatrixView();
      case 'status':
        return renderStatusView();
      default:
        return renderMatrixView();
    }
  };

  if (loading) {
    return (
      <div className="deployment-matrix-container loading">
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading deployment matrix...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="deployment-matrix-container error">
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="deployment-matrix-container">
      <div className="matrix-header-section">
        <div className="header-left">
          <h2>Agent Deployment Matrix</h2>
          <p>Real-time deployment status across environments and regions</p>
        </div>
        <div className="header-right">
          <button 
            className={`refresh-btn ${refreshing ? 'refreshing' : ''}`}
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <i className="fas fa-sync-alt"></i>
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      <div className="matrix-navigation">
        <div className="nav-buttons">
          <button 
            className={`nav-button ${selectedView === 'matrix' ? 'active' : ''}`}
            onClick={() => setSelectedView('matrix')}
          >
            <i className="fas fa-th"></i>
            Deployment Matrix
          </button>
          <button 
            className={`nav-button ${selectedView === 'status' ? 'active' : ''}`}
            onClick={() => setSelectedView('status')}
          >
            <i className="fas fa-chart-bar"></i>
            Status Overview
          </button>
        </div>
      </div>

      <div className="matrix-main">
        {renderContent()}
      </div>

      {/* Deployment Details Modal */}
      {deploymentModal && selectedCell && (
        <div className="modal-overlay" onClick={() => setDeploymentModal(false)}>
          <div className="deployment-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>
                {selectedCell.environment.name} - {selectedCell.region.name}
              </h3>
              <button 
                className="close-button"
                onClick={() => setDeploymentModal(false)}
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
            
            <div className="modal-content">
              <div className="deployment-list">
                {selectedCell.deployments.map(deployment => (
                  <div key={deployment.id} className="deployment-item">
                    <div className="deployment-header">
                      <div className="deployment-info">
                        <h4>Agent {deployment.agentId.split('-')[1]}</h4>
                        <span className="deployment-version">{deployment.version}</span>
                      </div>
                      <div className="deployment-badges">
                        <span 
                          className="status-badge" 
                          style={{ backgroundColor: getStatusColor(deployment.status) }}
                        >
                          {deployment.status}
                        </span>
                        <span 
                          className="health-badge" 
                          style={{ backgroundColor: getStatusColor(deployment.healthStatus) }}
                        >
                          {deployment.healthStatus}
                        </span>
                      </div>
                    </div>
                    
                    <div className="deployment-metrics">
                      <div className="metric-group">
                        <span className="metric-label">Performance:</span>
                        <span className="metric-value">{deployment.performanceScore}%</span>
                      </div>
                      <div className="metric-group">
                        <span className="metric-label">Uptime:</span>
                        <span className="metric-value">{deployment.uptime}%</span>
                      </div>
                      <div className="metric-group">
                        <span className="metric-label">CPU:</span>
                        <span className="metric-value">{deployment.resourceUsage.cpu}%</span>
                      </div>
                      <div className="metric-group">
                        <span className="metric-label">Memory:</span>
                        <span className="metric-value">{deployment.resourceUsage.memory}%</span>
                      </div>
                    </div>
                    
                    <div className="deployment-actions">
                      <button className="action-btn">
                        <i className="fas fa-eye"></i>
                        View Logs
                      </button>
                      <button className="action-btn">
                        <i className="fas fa-chart-line"></i>
                        Metrics
                      </button>
                      <button className="action-btn">
                        <i className="fas fa-redo"></i>
                        Restart
                      </button>
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

export default AgentDeploymentMatrix;
