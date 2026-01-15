import React, { useState, useEffect, useCallback } from 'react';

const AgentWorkloadDistribution = () => {
  const [activeView, setActiveView] = useState('distribution');
  const [workloadData, setWorkloadData] = useState([]);
  const [distributionMetrics, setDistributionMetrics] = useState({});
  const [balancingData, setBalancingData] = useState([]);
  const [capacityData, setCapacityData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [filters, setFilters] = useState({
    department: 'all',
    status: 'all',
    workloadLevel: 'all',
    timeRange: '24h'
  });
  const [sortBy, setSortBy] = useState('workload');
  const [sortOrder, setSortOrder] = useState('desc');
  const [workloadModal, setWorkloadModal] = useState(false);
  const [balancingModal, setBalancingModal] = useState(false);
  const [rebalanceMode, setRebalanceMode] = useState(false);
  const [selectedAgents, setSelectedAgents] = useState([]);

  // Mock data generators
  const generateWorkloadData = useCallback(() => {
    const agentTypes = ['analytics', 'automation', 'communication', 'research', 'optimization', 'monitoring'];
    const statuses = ['active', 'idle', 'busy', 'overloaded', 'maintenance'];
    const departments = ['marketing', 'sales', 'finance', 'operations', 'research', 'strategy'];
    
    const agentNames = [
      'Analytics Agent Alpha', 'Research Agent Beta', 'Marketing Agent Gamma', 'Finance Agent Delta',
      'Operations Agent Epsilon', 'Strategy Agent Zeta', 'Customer Agent Eta', 'Data Agent Theta',
      'Communication Agent Iota', 'Automation Agent Kappa', 'Optimization Agent Lambda', 'Monitoring Agent Mu',
      'Business Agent Nu', 'Intelligence Agent Xi', 'Processing Agent Omicron', 'Coordination Agent Pi'
    ];

    return agentNames.map((name, index) => {
      const currentWorkload = Math.floor(Math.random() * 100) + 5;
      const maxCapacity = Math.floor(Math.random() * 50) + 50;
      const workloadPercentage = Math.min((currentWorkload / maxCapacity) * 100, 100);
      
      return {
        id: `agent-${index + 1}`,
        name: name,
        type: agentTypes[Math.floor(Math.random() * agentTypes.length)],
        department: departments[Math.floor(Math.random() * departments.length)],
        status: workloadPercentage > 90 ? 'overloaded' : 
                workloadPercentage > 70 ? 'busy' : 
                workloadPercentage < 20 ? 'idle' : 'active',
        currentWorkload: currentWorkload,
        maxCapacity: maxCapacity,
        workloadPercentage: workloadPercentage,
        utilizationRate: (Math.random() * 40 + 60).toFixed(1),
        avgResponseTime: (Math.random() * 2000 + 100).toFixed(0),
        activeTasks: Math.floor(Math.random() * 15) + 1,
        queuedTasks: Math.floor(Math.random() * 25) + 2,
        completedTasks: Math.floor(Math.random() * 500) + 50,
        failedTasks: Math.floor(Math.random() * 20) + 1,
        resourceUsage: {
          cpu: (Math.random() * 80 + 10).toFixed(1),
          memory: (Math.random() * 90 + 5).toFixed(1),
          network: (Math.random() * 70 + 5).toFixed(1),
          storage: (Math.random() * 60 + 20).toFixed(1)
        },
        performance: {
          efficiency: (Math.random() * 30 + 70).toFixed(1),
          reliability: (Math.random() * 20 + 80).toFixed(1),
          speed: (Math.random() * 40 + 60).toFixed(1)
        },
        workloadHistory: Array.from({ length: 24 }, (_, i) => ({
          hour: i,
          workload: Math.floor(Math.random() * 100) + 5,
          tasks: Math.floor(Math.random() * 20) + 2
        })),
        lastUpdate: new Date(Date.now() - Math.random() * 3600000).toISOString(),
        uptime: Math.floor(Math.random() * 8760) + 100, // hours
        priority: ['high', 'normal', 'low'][Math.floor(Math.random() * 3)],
        tags: ['production', 'critical', 'scalable', 'optimized'].slice(0, Math.floor(Math.random() * 3) + 1)
      };
    });
  }, []);

  const generateDistributionMetrics = useCallback(() => {
    return {
      totalAgents: 16,
      activeAgents: 12,
      overloadedAgents: 3,
      idleAgents: 1,
      averageWorkload: 67.5,
      totalCapacity: 800,
      usedCapacity: 540,
      availableCapacity: 260,
      distributionEfficiency: 78.3,
      balancingScore: 85.7,
      optimalThreshold: 75,
      criticalThreshold: 90,
      rebalanceRecommendations: 4,
      workloadVariance: 23.4,
      peakWorkloadTime: '14:30',
      lowWorkloadTime: '03:15',
      trends: {
        workloadChange: '+5.2%',
        efficiencyChange: '+2.1%',
        balanceChange: '-1.8%'
      },
      predictions: {
        nextHourWorkload: 72.1,
        peakPrediction: '16:45',
        capacityAlert: false
      }
    };
  }, []);

  const generateBalancingData = useCallback(() => {
    const strategies = ['round-robin', 'least-connections', 'weighted', 'resource-based', 'priority-based'];
    const actions = ['redistribute', 'scale-up', 'scale-down', 'migrate', 'optimize'];
    
    return Array.from({ length: 8 }, (_, index) => ({
      id: `balance-${index + 1}`,
      strategy: strategies[Math.floor(Math.random() * strategies.length)],
      action: actions[Math.floor(Math.random() * actions.length)],
      sourceAgent: `agent-${Math.floor(Math.random() * 16) + 1}`,
      targetAgent: `agent-${Math.floor(Math.random() * 16) + 1}`,
      workloadAmount: Math.floor(Math.random() * 30) + 5,
      estimatedImprovement: (Math.random() * 25 + 5).toFixed(1),
      confidence: (Math.random() * 30 + 70).toFixed(1),
      executionTime: (Math.random() * 300 + 30).toFixed(0),
      status: ['recommended', 'in-progress', 'completed', 'failed'][Math.floor(Math.random() * 4)],
      priority: ['critical', 'high', 'medium', 'low'][Math.floor(Math.random() * 4)],
      impact: {
        performance: (Math.random() * 20 + 5).toFixed(1),
        efficiency: (Math.random() * 15 + 5).toFixed(1),
        stability: (Math.random() * 10 + 2).toFixed(1)
      },
      risks: ['performance-drop', 'resource-conflict', 'downtime', 'data-loss'].slice(0, Math.floor(Math.random() * 2) + 1),
      timestamp: new Date(Date.now() - Math.random() * 86400000).toISOString(),
      automated: Math.random() > 0.3,
      rollbackPlan: Math.random() > 0.2
    }));
  }, []);

  const generateCapacityData = useCallback(() => {
    return Array.from({ length: 6 }, (_, index) => ({
      id: `capacity-${index + 1}`,
      department: ['marketing', 'sales', 'finance', 'operations', 'research', 'strategy'][index],
      totalCapacity: Math.floor(Math.random() * 200) + 100,
      usedCapacity: Math.floor(Math.random() * 150) + 50,
      availableCapacity: function() { return this.totalCapacity - this.usedCapacity; },
      utilizationRate: function() { return ((this.usedCapacity / this.totalCapacity) * 100).toFixed(1); },
      agentCount: Math.floor(Math.random() * 5) + 2,
      avgWorkload: (Math.random() * 50 + 30).toFixed(1),
      peakCapacity: Math.floor(Math.random() * 300) + 200,
      scalingNeeded: Math.random() > 0.6,
      recommendations: ['add-agents', 'optimize-tasks', 'redistribute-load', 'upgrade-resources'].slice(0, Math.floor(Math.random() * 2) + 1),
      forecast: {
        nextWeek: (Math.random() * 20 + 80).toFixed(1),
        nextMonth: (Math.random() * 30 + 70).toFixed(1),
        growthRate: (Math.random() * 10 + 2).toFixed(1)
      }
    }));
  }, []);

  // Initialize data
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        await new Promise(resolve => setTimeout(resolve, 1000));
        setWorkloadData(generateWorkloadData());
        setDistributionMetrics(generateDistributionMetrics());
        setBalancingData(generateBalancingData());
        setCapacityData(generateCapacityData());
        setError(null);
      } catch (err) {
        setError('Failed to load workload distribution data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [generateWorkloadData, generateDistributionMetrics, generateBalancingData, generateCapacityData]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      setWorkloadData(generateWorkloadData());
      setDistributionMetrics(generateDistributionMetrics());
      setBalancingData(generateBalancingData());
      setCapacityData(generateCapacityData());
    } catch (err) {
      setError('Failed to refresh data');
    } finally {
      setRefreshing(false);
    }
  };

  const handleAgentSelect = (agent) => {
    setSelectedAgent(agent);
    setWorkloadModal(true);
  };

  const handleRebalance = () => {
    setRebalanceMode(!rebalanceMode);
    setSelectedAgents([]);
  };

  const getWorkloadColor = (percentage) => {
    if (percentage >= 90) return '#dc3545'; // Critical
    if (percentage >= 75) return '#fd7e14'; // Warning
    if (percentage >= 50) return '#28a745'; // Good
    if (percentage >= 25) return '#17a2b8'; // Light
    return '#6c757d'; // Minimal
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return '#28a745';
      case 'idle': return '#17a2b8';
      case 'busy': return '#ffc107';
      case 'overloaded': return '#dc3545';
      case 'maintenance': return '#6c757d';
      default: return '#6c757d';
    }
  };

  const filterAndSortData = (data) => {
    let filtered = data.filter(item => {
      if (filters.department !== 'all' && item.department !== filters.department) return false;
      if (filters.status !== 'all' && item.status !== filters.status) return false;
      if (filters.workloadLevel !== 'all') {
        if (filters.workloadLevel === 'high' && item.workloadPercentage < 75) return false;
        if (filters.workloadLevel === 'medium' && (item.workloadPercentage < 25 || item.workloadPercentage >= 75)) return false;
        if (filters.workloadLevel === 'low' && item.workloadPercentage >= 25) return false;
      }
      return true;
    });

    filtered.sort((a, b) => {
      let aValue, bValue;
      switch (sortBy) {
        case 'name':
          aValue = a.name;
          bValue = b.name;
          break;
        case 'workload':
          aValue = a.workloadPercentage;
          bValue = b.workloadPercentage;
          break;
        case 'capacity':
          aValue = a.maxCapacity;
          bValue = b.maxCapacity;
          break;
        case 'efficiency':
          aValue = parseFloat(a.performance.efficiency);
          bValue = parseFloat(b.performance.efficiency);
          break;
        case 'tasks':
          aValue = a.activeTasks;
          bValue = b.activeTasks;
          break;
        default:
          aValue = a.workloadPercentage;
          bValue = b.workloadPercentage;
      }

      if (typeof aValue === 'string') {
        return sortOrder === 'asc' ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
      }
      return sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
    });

    return filtered;
  };

  const renderDistributionView = () => (
    <div className="distribution-content">
      <div className="distribution-controls">
        <div className="filter-section">
          <select 
            value={filters.department} 
            onChange={(e) => setFilters({...filters, department: e.target.value})}
          >
            <option value="all">All Departments</option>
            <option value="marketing">Marketing</option>
            <option value="sales">Sales</option>
            <option value="finance">Finance</option>
            <option value="operations">Operations</option>
            <option value="research">Research</option>
            <option value="strategy">Strategy</option>
          </select>
          
          <select 
            value={filters.status} 
            onChange={(e) => setFilters({...filters, status: e.target.value})}
          >
            <option value="all">All Statuses</option>
            <option value="active">Active</option>
            <option value="idle">Idle</option>
            <option value="busy">Busy</option>
            <option value="overloaded">Overloaded</option>
            <option value="maintenance">Maintenance</option>
          </select>

          <select 
            value={filters.workloadLevel} 
            onChange={(e) => setFilters({...filters, workloadLevel: e.target.value})}
          >
            <option value="all">All Workload Levels</option>
            <option value="high">High (75%+)</option>
            <option value="medium">Medium (25-75%)</option>
            <option value="low">Low (&lt;25%)</option>
          </select>

          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="workload">Sort by Workload</option>
            <option value="name">Sort by Name</option>
            <option value="capacity">Sort by Capacity</option>
            <option value="efficiency">Sort by Efficiency</option>
            <option value="tasks">Sort by Tasks</option>
          </select>

          <button 
            className="sort-order-btn"
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
          >
            <i className={`fas fa-sort-amount-${sortOrder === 'asc' ? 'up' : 'down'}-alt`}></i>
          </button>
        </div>

        <div className="action-buttons">
          <button className="rebalance-btn" onClick={handleRebalance}>
            <i className="fas fa-balance-scale"></i>
            {rebalanceMode ? 'Cancel Rebalance' : 'Rebalance Mode'}
          </button>
          <button className="auto-balance-btn">
            <i className="fas fa-magic"></i>
            Auto Balance
          </button>
        </div>
      </div>

      <div className="distribution-overview">
        <div className="overview-metrics">
          <div className="metric-card">
            <div className="metric-icon">
              <i className="fas fa-robot"></i>
            </div>
            <div className="metric-content">
              <h3>{distributionMetrics.totalAgents}</h3>
              <p>Total Agents</p>
              <div className="metric-detail">
                <span className="active">{distributionMetrics.activeAgents} Active</span>
                <span className="overloaded">{distributionMetrics.overloadedAgents} Overloaded</span>
              </div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">
              <i className="fas fa-chart-line"></i>
            </div>
            <div className="metric-content">
              <h3>{distributionMetrics.averageWorkload}%</h3>
              <p>Average Workload</p>
              <div className="metric-detail">
                <span className="trend positive">{distributionMetrics.trends?.workloadChange}</span>
              </div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">
              <i className="fas fa-server"></i>
            </div>
            <div className="metric-content">
              <h3>{distributionMetrics.usedCapacity}/{distributionMetrics.totalCapacity}</h3>
              <p>Capacity Usage</p>
              <div className="metric-detail">
                <span>{distributionMetrics.availableCapacity} Available</span>
              </div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">
              <i className="fas fa-balance-scale"></i>
            </div>
            <div className="metric-content">
              <h3>{distributionMetrics.balancingScore}%</h3>
              <p>Balance Score</p>
              <div className="metric-detail">
                <span className="trend negative">{distributionMetrics.trends?.balanceChange}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="workload-distribution">
        <div className="distribution-header">
          <h3>Agent Workload Distribution</h3>
          <div className="legend">
            <div className="legend-item">
              <div className="legend-color" style={{backgroundColor: '#6c757d'}}></div>
              <span>Minimal (&lt;25%)</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{backgroundColor: '#17a2b8'}}></div>
              <span>Light (25-50%)</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{backgroundColor: '#28a745'}}></div>
              <span>Good (50-75%)</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{backgroundColor: '#fd7e14'}}></div>
              <span>Warning (75-90%)</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{backgroundColor: '#dc3545'}}></div>
              <span>Critical (90%+)</span>
            </div>
          </div>
        </div>

        <div className="agent-grid">
          {filterAndSortData(workloadData).map(agent => (
            <div 
              key={agent.id} 
              className={`agent-card ${rebalanceMode ? 'selectable' : ''} ${selectedAgents.includes(agent.id) ? 'selected' : ''}`}
              onClick={() => rebalanceMode ? 
                setSelectedAgents(prev => 
                  prev.includes(agent.id) 
                    ? prev.filter(id => id !== agent.id)
                    : [...prev, agent.id]
                ) : 
                handleAgentSelect(agent)
              }
            >
              <div className="agent-header">
                <div className="agent-info">
                  <h4>{agent.name}</h4>
                  <p className="agent-type">{agent.type} • {agent.department}</p>
                </div>
                <div className="agent-status">
                  <div 
                    className="status-dot"
                    style={{backgroundColor: getStatusColor(agent.status)}}
                  ></div>
                  <span className="status-text">{agent.status}</span>
                </div>
              </div>

              <div className="workload-visualization">
                <div className="workload-bar">
                  <div 
                    className="workload-fill"
                    style={{
                      width: `${agent.workloadPercentage}%`,
                      backgroundColor: getWorkloadColor(agent.workloadPercentage)
                    }}
                  ></div>
                </div>
                <div className="workload-info">
                  <span className="workload-percentage">{agent.workloadPercentage.toFixed(1)}%</span>
                  <span className="workload-details">{agent.currentWorkload}/{agent.maxCapacity}</span>
                </div>
              </div>

              <div className="agent-metrics">
                <div className="metric-item">
                  <i className="fas fa-tasks"></i>
                  <span>{agent.activeTasks} active</span>
                </div>
                <div className="metric-item">
                  <i className="fas fa-clock"></i>
                  <span>{agent.queuedTasks} queued</span>
                </div>
                <div className="metric-item">
                  <i className="fas fa-tachometer-alt"></i>
                  <span>{agent.performance.efficiency}% eff</span>
                </div>
                <div className="metric-item">
                  <i className="fas fa-stopwatch"></i>
                  <span>{agent.avgResponseTime}ms</span>
                </div>
              </div>

              <div className="resource-usage">
                <div className="resource-item">
                  <span>CPU</span>
                  <div className="resource-bar">
                    <div className="resource-fill" style={{width: `${agent.resourceUsage.cpu}%`}}></div>
                  </div>
                  <span>{agent.resourceUsage.cpu}%</span>
                </div>
                <div className="resource-item">
                  <span>Memory</span>
                  <div className="resource-bar">
                    <div className="resource-fill" style={{width: `${agent.resourceUsage.memory}%`}}></div>
                  </div>
                  <span>{agent.resourceUsage.memory}%</span>
                </div>
              </div>

              {rebalanceMode && (
                <div className="rebalance-controls">
                  <input 
                    type="checkbox" 
                    checked={selectedAgents.includes(agent.id)}
                    onChange={() => {}}
                  />
                  <span>Select for rebalancing</span>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderBalancingView = () => (
    <div className="balancing-content">
      <div className="balancing-overview">
        <h3>Load Balancing Recommendations</h3>
        <p>Intelligent workload balancing suggestions based on current distribution patterns</p>
      </div>

      <div className="balancing-controls">
        <div className="strategy-selector">
          <select>
            <option value="intelligent">Intelligent Balancing</option>
            <option value="round-robin">Round Robin</option>
            <option value="least-connections">Least Connections</option>
            <option value="weighted">Weighted Distribution</option>
            <option value="resource-based">Resource Based</option>
          </select>
        </div>
        <div className="action-buttons">
          <button className="execute-btn">
            <i className="fas fa-play"></i>
            Execute All
          </button>
          <button className="simulate-btn">
            <i className="fas fa-flask"></i>
            Simulate
          </button>
        </div>
      </div>

      <div className="balancing-recommendations">
        {balancingData.map(recommendation => (
          <div key={recommendation.id} className="recommendation-card">
            <div className="recommendation-header">
              <div className="recommendation-info">
                <h4>
                  <i className={`fas ${
                    recommendation.action === 'redistribute' ? 'fa-exchange-alt' :
                    recommendation.action === 'scale-up' ? 'fa-arrow-up' :
                    recommendation.action === 'scale-down' ? 'fa-arrow-down' :
                    recommendation.action === 'migrate' ? 'fa-share' :
                    'fa-cog'
                  }`}></i>
                  {recommendation.action.charAt(0).toUpperCase() + recommendation.action.slice(1)} Workload
                </h4>
                <p>{recommendation.strategy} strategy</p>
              </div>
              <div className="recommendation-status">
                <span className={`status-badge ${recommendation.status}`}>
                  {recommendation.status}
                </span>
                <span className={`priority-badge ${recommendation.priority}`}>
                  {recommendation.priority}
                </span>
              </div>
            </div>

            <div className="recommendation-details">
              <div className="agent-flow">
                <div className="source-agent">
                  <i className="fas fa-robot"></i>
                  <span>{recommendation.sourceAgent}</span>
                </div>
                <div className="flow-arrow">
                  <i className="fas fa-arrow-right"></i>
                  <span>{recommendation.workloadAmount} tasks</span>
                </div>
                <div className="target-agent">
                  <i className="fas fa-robot"></i>
                  <span>{recommendation.targetAgent}</span>
                </div>
              </div>

              <div className="recommendation-metrics">
                <div className="metric">
                  <span className="label">Improvement:</span>
                  <span className="value positive">+{recommendation.estimatedImprovement}%</span>
                </div>
                <div className="metric">
                  <span className="label">Confidence:</span>
                  <span className="value">{recommendation.confidence}%</span>
                </div>
                <div className="metric">
                  <span className="label">Execution Time:</span>
                  <span className="value">{recommendation.executionTime}s</span>
                </div>
              </div>

              <div className="impact-analysis">
                <h5>Expected Impact</h5>
                <div className="impact-metrics">
                  <div className="impact-item">
                    <span>Performance</span>
                    <span className="impact-value positive">+{recommendation.impact.performance}%</span>
                  </div>
                  <div className="impact-item">
                    <span>Efficiency</span>
                    <span className="impact-value positive">+{recommendation.impact.efficiency}%</span>
                  </div>
                  <div className="impact-item">
                    <span>Stability</span>
                    <span className="impact-value positive">+{recommendation.impact.stability}%</span>
                  </div>
                </div>
              </div>

              {recommendation.risks.length > 0 && (
                <div className="risk-analysis">
                  <h5>Potential Risks</h5>
                  <div className="risk-items">
                    {recommendation.risks.map((risk, index) => (
                      <span key={index} className="risk-tag">
                        <i className="fas fa-exclamation-triangle"></i>
                        {risk.replace('-', ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="recommendation-actions">
                <button className="accept-btn">
                  <i className="fas fa-check"></i>
                  Accept
                </button>
                <button className="modify-btn">
                  <i className="fas fa-edit"></i>
                  Modify
                </button>
                <button className="reject-btn">
                  <i className="fas fa-times"></i>
                  Reject
                </button>
                {recommendation.rollbackPlan && (
                  <button className="rollback-btn">
                    <i className="fas fa-undo"></i>
                    Rollback Plan
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderCapacityView = () => (
    <div className="capacity-content">
      <div className="capacity-overview">
        <h3>Capacity Planning & Forecasting</h3>
        <p>Department-wise capacity analysis with scaling recommendations</p>
      </div>

      <div className="capacity-grid">
        {capacityData.map(department => {
          const availableCapacity = department.availableCapacity();
          const utilizationRate = department.utilizationRate();
          
          return (
            <div key={department.id} className="capacity-card">
              <div className="capacity-header">
                <h4>{department.department.charAt(0).toUpperCase() + department.department.slice(1)}</h4>
                <div className="capacity-status">
                  {department.scalingNeeded && (
                    <span className="scaling-needed">
                      <i className="fas fa-exclamation-circle"></i>
                      Scaling Needed
                    </span>
                  )}
                </div>
              </div>

              <div className="capacity-metrics">
                <div className="primary-metrics">
                  <div className="metric">
                    <span className="label">Total Capacity</span>
                    <span className="value">{department.totalCapacity}</span>
                  </div>
                  <div className="metric">
                    <span className="label">Used</span>
                    <span className="value">{department.usedCapacity}</span>
                  </div>
                  <div className="metric">
                    <span className="label">Available</span>
                    <span className="value available">{availableCapacity}</span>
                  </div>
                </div>

                <div className="utilization-display">
                  <div className="utilization-bar">
                    <div 
                      className="utilization-fill"
                      style={{
                        width: `${utilizationRate}%`,
                        backgroundColor: utilizationRate > 90 ? '#dc3545' : 
                                       utilizationRate > 75 ? '#fd7e14' : '#28a745'
                      }}
                    ></div>
                  </div>
                  <span className="utilization-percentage">{utilizationRate}%</span>
                </div>
              </div>

              <div className="agent-info">
                <div className="agent-count">
                  <i className="fas fa-robot"></i>
                  <span>{department.agentCount} Agents</span>
                </div>
                <div className="avg-workload">
                  <i className="fas fa-chart-bar"></i>
                  <span>{department.avgWorkload}% Avg Load</span>
                </div>
              </div>

              <div className="capacity-forecast">
                <h5>Forecast</h5>
                <div className="forecast-metrics">
                  <div className="forecast-item">
                    <span>Next Week:</span>
                    <span className="forecast-value">{department.forecast.nextWeek}%</span>
                  </div>
                  <div className="forecast-item">
                    <span>Next Month:</span>
                    <span className="forecast-value">{department.forecast.nextMonth}%</span>
                  </div>
                  <div className="forecast-item">
                    <span>Growth Rate:</span>
                    <span className="forecast-value growth">+{department.forecast.growthRate}%</span>
                  </div>
                </div>
              </div>

              {department.recommendations.length > 0 && (
                <div className="capacity-recommendations">
                  <h5>Recommendations</h5>
                  <div className="recommendation-tags">
                    {department.recommendations.map((rec, index) => (
                      <span key={index} className="recommendation-tag">
                        {rec.replace('-', ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="scaling-actions">
        <h3>Scaling Actions</h3>
        <div className="action-cards">
          <div className="action-card">
            <div className="action-icon">
              <i className="fas fa-plus-circle"></i>
            </div>
            <div className="action-content">
              <h4>Add Agents</h4>
              <p>Deploy additional agents to departments approaching capacity limits</p>
              <button className="action-btn">Configure</button>
            </div>
          </div>
          
          <div className="action-card">
            <div className="action-icon">
              <i className="fas fa-arrows-alt"></i>
            </div>
            <div className="action-content">
              <h4>Redistribute Load</h4>
              <p>Move workload from overloaded to underutilized departments</p>
              <button className="action-btn">Execute</button>
            </div>
          </div>
          
          <div className="action-card">
            <div className="action-icon">
              <i className="fas fa-rocket"></i>
            </div>
            <div className="action-content">
              <h4>Upgrade Resources</h4>
              <p>Increase computing resources for existing agents</p>
              <button className="action-btn">Plan</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeView) {
      case 'distribution':
        return renderDistributionView();
      case 'balancing':
        return renderBalancingView();
      case 'capacity':
        return renderCapacityView();
      default:
        return renderDistributionView();
    }
  };

  if (loading) {
    return (
      <div className="agent-workload-distribution loading">
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading workload distribution data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="agent-workload-distribution error">
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="agent-workload-distribution">
      <div className="workload-header">
        <div className="header-left">
          <h2>Agent Workload Distribution</h2>
          <p>Monitor and optimize agent workload distribution across the enterprise</p>
        </div>
        <button 
          className={`refresh-btn ${refreshing ? 'refreshing' : ''}`}
          onClick={handleRefresh}
          disabled={refreshing}
        >
          <i className="fas fa-sync-alt"></i>
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="workload-navigation">
        <div className="nav-buttons">
          <button 
            className={`nav-button ${activeView === 'distribution' ? 'active' : ''}`}
            onClick={() => setActiveView('distribution')}
          >
            <i className="fas fa-chart-pie"></i>
            Distribution
          </button>
          <button 
            className={`nav-button ${activeView === 'balancing' ? 'active' : ''}`}
            onClick={() => setActiveView('balancing')}
          >
            <i className="fas fa-balance-scale"></i>
            Balancing
          </button>
          <button 
            className={`nav-button ${activeView === 'capacity' ? 'active' : ''}`}
            onClick={() => setActiveView('capacity')}
          >
            <i className="fas fa-server"></i>
            Capacity
          </button>
        </div>
      </div>

      <div className="workload-main">
        {renderContent()}
      </div>

      {/* Workload Detail Modal */}
      {workloadModal && selectedAgent && (
        <div className="modal-overlay" onClick={() => setWorkloadModal(false)}>
          <div className="workload-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{selectedAgent.name} - Workload Details</h3>
              <button 
                className="close-button" 
                onClick={() => setWorkloadModal(false)}
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-content">
              <div className="workload-details">
                <div className="detail-section">
                  <h4>Current Status</h4>
                  <div className="status-info">
                    <div className="status-item">
                      <span className="label">Status:</span>
                      <span className={`value status ${selectedAgent.status}`}>
                        {selectedAgent.status}
                      </span>
                    </div>
                    <div className="status-item">
                      <span className="label">Workload:</span>
                      <span className="value">{selectedAgent.workloadPercentage.toFixed(1)}%</span>
                    </div>
                    <div className="status-item">
                      <span className="label">Capacity:</span>
                      <span className="value">{selectedAgent.currentWorkload}/{selectedAgent.maxCapacity}</span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Performance Metrics</h4>
                  <div className="performance-grid">
                    <div className="performance-item">
                      <span className="label">Efficiency</span>
                      <span className="value">{selectedAgent.performance.efficiency}%</span>
                    </div>
                    <div className="performance-item">
                      <span className="label">Reliability</span>
                      <span className="value">{selectedAgent.performance.reliability}%</span>
                    </div>
                    <div className="performance-item">
                      <span className="label">Speed</span>
                      <span className="value">{selectedAgent.performance.speed}%</span>
                    </div>
                    <div className="performance-item">
                      <span className="label">Response Time</span>
                      <span className="value">{selectedAgent.avgResponseTime}ms</span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Resource Usage</h4>
                  <div className="resource-grid">
                    <div className="resource-item">
                      <span className="label">CPU</span>
                      <div className="resource-bar">
                        <div 
                          className="resource-fill" 
                          style={{width: `${selectedAgent.resourceUsage.cpu}%`}}
                        ></div>
                      </div>
                      <span className="value">{selectedAgent.resourceUsage.cpu}%</span>
                    </div>
                    <div className="resource-item">
                      <span className="label">Memory</span>
                      <div className="resource-bar">
                        <div 
                          className="resource-fill" 
                          style={{width: `${selectedAgent.resourceUsage.memory}%`}}
                        ></div>
                      </div>
                      <span className="value">{selectedAgent.resourceUsage.memory}%</span>
                    </div>
                    <div className="resource-item">
                      <span className="label">Network</span>
                      <div className="resource-bar">
                        <div 
                          className="resource-fill" 
                          style={{width: `${selectedAgent.resourceUsage.network}%`}}
                        ></div>
                      </div>
                      <span className="value">{selectedAgent.resourceUsage.network}%</span>
                    </div>
                    <div className="resource-item">
                      <span className="label">Storage</span>
                      <div className="resource-bar">
                        <div 
                          className="resource-fill" 
                          style={{width: `${selectedAgent.resourceUsage.storage}%`}}
                        ></div>
                      </div>
                      <span className="value">{selectedAgent.resourceUsage.storage}%</span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Task Statistics</h4>
                  <div className="task-stats">
                    <div className="stat-item">
                      <span className="label">Active Tasks</span>
                      <span className="value">{selectedAgent.activeTasks}</span>
                    </div>
                    <div className="stat-item">
                      <span className="label">Queued Tasks</span>
                      <span className="value">{selectedAgent.queuedTasks}</span>
                    </div>
                    <div className="stat-item">
                      <span className="label">Completed Tasks</span>
                      <span className="value">{selectedAgent.completedTasks}</span>
                    </div>
                    <div className="stat-item">
                      <span className="label">Failed Tasks</span>
                      <span className="value">{selectedAgent.failedTasks}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentWorkloadDistribution;
