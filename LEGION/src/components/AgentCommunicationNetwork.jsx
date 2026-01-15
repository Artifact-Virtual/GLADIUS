import React, { useState, useEffect, useCallback, useRef } from 'react';

const AgentCommunicationNetwork = () => {
  const [activeView, setActiveView] = useState('network');
  const [networkData, setNetworkData] = useState({ nodes: [], links: [] });
  const [communicationFlow, setCommunicationFlow] = useState([]);
  const [protocolStats, setProtocolStats] = useState([]);
  const [networkMetrics, setNetworkMetrics] = useState({});
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedConnection, setSelectedConnection] = useState(null);
  const [filters, setFilters] = useState({
    protocol: 'all',
    status: 'all',
    priority: 'all',
    department: 'all',
    messageType: 'all'
  });
  const [networkLayout, setNetworkLayout] = useState('force');
  const [showTraffic, setShowTraffic] = useState(true);
  const [networkModal, setNetworkModal] = useState(false);
  const [connectionModal, setConnectionModal] = useState(false);
  const networkRef = useRef(null);
  const animationRef = useRef(null);

  // Mock data generators
  const generateNetworkData = useCallback(() => {
    const agentTypes = ['analytics', 'automation', 'communication', 'research', 'optimization', 'monitoring'];
    const departments = ['marketing', 'sales', 'finance', 'operations', 'research', 'strategy'];
    const statuses = ['active', 'idle', 'busy', 'maintenance', 'offline'];
    
    const agentNames = [
      'Analytics Agent Alpha', 'Research Agent Beta', 'Marketing Agent Gamma', 'Finance Agent Delta',
      'Operations Agent Epsilon', 'Strategy Agent Zeta', 'Customer Agent Eta', 'Data Agent Theta',
      'Communication Agent Iota', 'Automation Agent Kappa', 'Optimization Agent Lambda', 'Monitoring Agent Mu',
      'Business Agent Nu', 'Intelligence Agent Xi', 'Processing Agent Omicron', 'Coordination Agent Pi'
    ];

    // Generate nodes (agents)
    const nodes = agentNames.map((name, index) => ({
      id: `agent-${index + 1}`,
      name: name,
      type: agentTypes[Math.floor(Math.random() * agentTypes.length)],
      department: departments[Math.floor(Math.random() * departments.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      x: Math.random() * 800 + 100,
      y: Math.random() * 600 + 100,
      connections: Math.floor(Math.random() * 8) + 2,
      messagesSent: Math.floor(Math.random() * 1000) + 100,
      messagesReceived: Math.floor(Math.random() * 1200) + 150,
      bandwidth: (Math.random() * 100 + 50).toFixed(1),
      latency: (Math.random() * 50 + 10).toFixed(1),
      reliability: (Math.random() * 20 + 80).toFixed(1),
      load: Math.floor(Math.random() * 100),
      protocols: ['http', 'websocket', 'message-queue', 'direct'].slice(0, Math.floor(Math.random() * 3) + 1),
      lastSeen: new Date(Date.now() - Math.random() * 3600000).toISOString(),
      uptime: (Math.random() * 99 + 95).toFixed(2),
      errorRate: (Math.random() * 5).toFixed(2)
    }));

    // Generate links (connections)
    const links = [];
    const protocols = ['http', 'websocket', 'message-queue', 'direct', 'broadcast'];
    const priorities = ['critical', 'high', 'normal', 'low'];
    const messageTypes = ['data', 'command', 'status', 'alert', 'heartbeat'];
    
    for (let i = 0; i < nodes.length; i++) {
      const connectionsCount = Math.floor(Math.random() * 6) + 2;
      const connectedNodes = new Set();
      
      for (let j = 0; j < connectionsCount; j++) {
        let targetIndex;
        do {
          targetIndex = Math.floor(Math.random() * nodes.length);
        } while (targetIndex === i || connectedNodes.has(targetIndex));
        
        if (targetIndex !== i) {
          connectedNodes.add(targetIndex);
          
          const messageCount = Math.floor(Math.random() * 500) + 50;
          const bandwidth = Math.random() * 100 + 20;
          
          links.push({
            id: `link-${i}-${targetIndex}`,
            source: nodes[i].id,
            target: nodes[targetIndex].id,
            protocol: protocols[Math.floor(Math.random() * protocols.length)],
            priority: priorities[Math.floor(Math.random() * priorities.length)],
            messageType: messageTypes[Math.floor(Math.random() * messageTypes.length)],
            messageCount: messageCount,
            bandwidth: bandwidth.toFixed(1),
            latency: (Math.random() * 30 + 5).toFixed(1),
            packetLoss: (Math.random() * 2).toFixed(2),
            status: Math.random() > 0.1 ? 'active' : Math.random() > 0.5 ? 'congested' : 'error',
            strength: Math.random() * 0.8 + 0.2,
            encrypted: Math.random() > 0.3,
            compressed: Math.random() > 0.4,
            retries: Math.floor(Math.random() * 5),
            lastActivity: new Date(Date.now() - Math.random() * 1800000).toISOString(),
            throughput: (bandwidth * (Math.random() * 0.4 + 0.6)).toFixed(1),
            errorCount: Math.floor(Math.random() * 10)
          });
        }
      }
    }

    return { nodes, links };
  }, []);

  const generateCommunicationFlow = useCallback(() => {
    const flowTypes = ['request-response', 'publish-subscribe', 'point-to-point', 'broadcast', 'multicast'];
    const directions = ['bidirectional', 'unidirectional'];
    
    return Array.from({ length: 20 }, (_, index) => ({
      id: `flow-${index + 1}`,
      name: `Communication Flow ${index + 1}`,
      type: flowTypes[Math.floor(Math.random() * flowTypes.length)],
      direction: directions[Math.floor(Math.random() * directions.length)],
      participants: Math.floor(Math.random() * 6) + 2,
      messageRate: (Math.random() * 100 + 10).toFixed(1),
      avgLatency: (Math.random() * 100 + 20).toFixed(1),
      reliability: (Math.random() * 20 + 80).toFixed(1),
      dataVolume: (Math.random() * 1000 + 100).toFixed(0),
      status: ['active', 'congested', 'idle', 'error'][Math.floor(Math.random() * 4)],
      priority: ['critical', 'high', 'normal', 'low'][Math.floor(Math.random() * 4)],
      protocol: ['http', 'websocket', 'message-queue', 'direct', 'broadcast'][Math.floor(Math.random() * 5)],
      startTime: new Date(Date.now() - Math.random() * 86400000).toISOString(),
      duration: Math.floor(Math.random() * 3600) + 300, // seconds
      nodes: Array.from({ length: Math.floor(Math.random() * 4) + 2 }, (_, i) => `agent-${Math.floor(Math.random() * 16) + 1}`),
      metrics: {
        messagesProcessed: Math.floor(Math.random() * 10000) + 1000,
        averageHops: Math.floor(Math.random() * 4) + 1,
        bandwidth: (Math.random() * 50 + 10).toFixed(1),
        jitter: (Math.random() * 10 + 1).toFixed(1)
      }
    }));
  }, []);

  const generateProtocolStats = useCallback(() => {
    const protocols = ['http', 'websocket', 'message-queue', 'direct', 'broadcast'];
    
    return protocols.map(protocol => ({
      name: protocol,
      usage: (Math.random() * 30 + 10).toFixed(1),
      connections: Math.floor(Math.random() * 50) + 10,
      messageRate: (Math.random() * 200 + 50).toFixed(1),
      averageLatency: (Math.random() * 80 + 20).toFixed(1),
      reliability: (Math.random() * 15 + 85).toFixed(1),
      bandwidth: (Math.random() * 100 + 50).toFixed(1),
      errorRate: (Math.random() * 3).toFixed(2),
      overhead: (Math.random() * 20 + 5).toFixed(1),
      security: protocol === 'message-queue' || protocol === 'direct' ? 'high' : 
                protocol === 'websocket' ? 'medium' : 'standard',
      scalability: protocol === 'broadcast' || protocol === 'message-queue' ? 'high' :
                   protocol === 'websocket' ? 'medium' : 'standard'
    }));
  }, []);

  const generateNetworkMetrics = useCallback(() => {
    return {
      totalNodes: 16,
      activeConnections: 42,
      totalMessages: 15750,
      messageRate: (Math.random() * 50 + 25).toFixed(1),
      averageLatency: (Math.random() * 40 + 15).toFixed(1),
      bandwidth: (Math.random() * 200 + 100).toFixed(1),
      networkReliability: (Math.random() * 10 + 90).toFixed(1),
      packetLoss: (Math.random() * 2).toFixed(2),
      congestionLevel: (Math.random() * 30 + 5).toFixed(1),
      protocolDistribution: {
        http: 28.5,
        websocket: 35.2,
        messageQueue: 22.1,
        direct: 14.2
      },
      topology: {
        clusters: 4,
        averagePathLength: 2.8,
        clusteringCoefficient: 0.65,
        networkDensity: 0.42
      },
      performance: {
        uptime: '99.97%',
        throughput: '1.2 GB/s',
        errorRate: '0.03%',
        responseTime: '45ms'
      },
      trends: {
        messageVolume: '+12.3%',
        latency: '-8.5%',
        reliability: '+2.1%',
        connections: '+5.7%'
      }
    };
  }, []);

  // Initialize data
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        await new Promise(resolve => setTimeout(resolve, 1200));
        setNetworkData(generateNetworkData());
        setCommunicationFlow(generateCommunicationFlow());
        setProtocolStats(generateProtocolStats());
        setNetworkMetrics(generateNetworkMetrics());
        setError(null);
      } catch (err) {
        setError('Failed to load network data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [generateNetworkData, generateCommunicationFlow, generateProtocolStats, generateNetworkMetrics]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      setNetworkData(generateNetworkData());
      setCommunicationFlow(generateCommunicationFlow());
      setProtocolStats(generateProtocolStats());
      setNetworkMetrics(generateNetworkMetrics());
    } catch (err) {
      setError('Failed to refresh data');
    } finally {
      setRefreshing(false);
    }
  };

  const handleNodeSelect = (node) => {
    setSelectedNode(node);
    setNetworkModal(true);
  };

  const handleConnectionSelect = (connection) => {
    setSelectedConnection(connection);
    setConnectionModal(true);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return '#28a745';
      case 'idle': return '#17a2b8';
      case 'busy': return '#ffc107';
      case 'maintenance': return '#fd7e14';
      case 'offline': return '#6c757d';
      case 'congested': return '#fd7e14';
      case 'error': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical': return '#dc3545';
      case 'high': return '#fd7e14';
      case 'normal': return '#28a745';
      case 'low': return '#6c757d';
      default: return '#6c757d';
    }
  };

  const filterNetworkData = () => {
    const filteredNodes = networkData.nodes.filter(node => {
      if (filters.status !== 'all' && node.status !== filters.status) return false;
      if (filters.department !== 'all' && node.department !== filters.department) return false;
      return true;
    });

    const filteredLinks = networkData.links.filter(link => {
      if (filters.protocol !== 'all' && link.protocol !== filters.protocol) return false;
      if (filters.priority !== 'all' && link.priority !== filters.priority) return false;
      if (filters.messageType !== 'all' && link.messageType !== filters.messageType) return false;
      
      // Only show links where both nodes are visible
      const sourceVisible = filteredNodes.some(node => node.id === link.source);
      const targetVisible = filteredNodes.some(node => node.id === link.target);
      return sourceVisible && targetVisible;
    });

    return { nodes: filteredNodes, links: filteredLinks };
  };

  const renderNetworkVisualization = () => {
    const filteredData = filterNetworkData();
    
    return (
      <div className="network-visualization">
        <div className="network-controls">
          <div className="layout-controls">
            <button 
              className={`layout-btn ${networkLayout === 'force' ? 'active' : ''}`}
              onClick={() => setNetworkLayout('force')}
            >
              <i className="fas fa-project-diagram"></i>
              Force Layout
            </button>
            <button 
              className={`layout-btn ${networkLayout === 'circular' ? 'active' : ''}`}
              onClick={() => setNetworkLayout('circular')}
            >
              <i className="fas fa-circle"></i>
              Circular
            </button>
            <button 
              className={`layout-btn ${networkLayout === 'hierarchical' ? 'active' : ''}`}
              onClick={() => setNetworkLayout('hierarchical')}
            >
              <i className="fas fa-sitemap"></i>
              Hierarchical
            </button>
          </div>
          
          <div className="view-controls">
            <button 
              className={`control-btn ${showTraffic ? 'active' : ''}`}
              onClick={() => setShowTraffic(!showTraffic)}
            >
              <i className="fas fa-exchange-alt"></i>
              {showTraffic ? 'Hide' : 'Show'} Traffic
            </button>
            <button className="control-btn">
              <i className="fas fa-expand-arrows-alt"></i>
              Full Screen
            </button>
          </div>
        </div>

        <div className="network-canvas" ref={networkRef}>
          <svg width="100%" height="600" viewBox="0 0 1000 600">
            {/* Connection lines */}
            {showTraffic && filteredData.links.map(link => {
              const sourceNode = filteredData.nodes.find(n => n.id === link.source);
              const targetNode = filteredData.nodes.find(n => n.id === link.target);
              
              if (!sourceNode || !targetNode) return null;
              
              return (
                <g key={link.id}>
                  <line
                    x1={sourceNode.x}
                    y1={sourceNode.y}
                    x2={targetNode.x}
                    y2={targetNode.y}
                    stroke={getStatusColor(link.status)}
                    strokeWidth={Math.max(1, link.strength * 4)}
                    opacity={0.6}
                    className="connection-line"
                    onClick={() => handleConnectionSelect(link)}
                  />
                  {link.status === 'active' && (
                    <circle
                      r="3"
                      fill="#fff"
                      opacity={0.8}
                      className="traffic-dot"
                    >
                      <animateMotion
                        dur={`${5 + Math.random() * 5}s`}
                        repeatCount="indefinite"
                        path={`M${sourceNode.x},${sourceNode.y} L${targetNode.x},${targetNode.y}`}
                      />
                    </circle>
                  )}
                </g>
              );
            })}
            
            {/* Agent nodes */}
            {filteredData.nodes.map(node => (
              <g key={node.id} className="agent-node" onClick={() => handleNodeSelect(node)}>
                <circle
                  cx={node.x}
                  cy={node.y}
                  r="20"
                  fill={getStatusColor(node.status)}
                  stroke="#fff"
                  strokeWidth="2"
                  opacity={0.9}
                />
                <circle
                  cx={node.x}
                  cy={node.y}
                  r="25"
                  fill="none"
                  stroke={getStatusColor(node.status)}
                  strokeWidth="1"
                  opacity={0.3}
                  className="node-pulse"
                />
                <text
                  x={node.x}
                  y={node.y + 35}
                  textAnchor="middle"
                  fill="#ffffff"
                  fontSize="12"
                  fontWeight="500"
                >
                  {node.name.split(' ')[0]}
                </text>
              </g>
            ))}
          </svg>
        </div>

        <div className="network-legend">
          <div className="legend-section">
            <h4>Node Status</h4>
            <div className="legend-items">
              <div className="legend-item">
                <div className="legend-color" style={{backgroundColor: '#28a745'}}></div>
                <span>Active</span>
              </div>
              <div className="legend-item">
                <div className="legend-color" style={{backgroundColor: '#17a2b8'}}></div>
                <span>Idle</span>
              </div>
              <div className="legend-item">
                <div className="legend-color" style={{backgroundColor: '#ffc107'}}></div>
                <span>Busy</span>
              </div>
              <div className="legend-item">
                <div className="legend-color" style={{backgroundColor: '#dc3545'}}></div>
                <span>Error</span>
              </div>
            </div>
          </div>
          
          <div className="legend-section">
            <h4>Connection Status</h4>
            <div className="legend-items">
              <div className="legend-item">
                <div className="legend-line active"></div>
                <span>Active Flow</span>
              </div>
              <div className="legend-item">
                <div className="legend-line congested"></div>
                <span>Congested</span>
              </div>
              <div className="legend-item">
                <div className="legend-line error"></div>
                <span>Error</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderFlowAnalysis = () => (
    <div className="flow-analysis">
      <div className="flow-overview">
        <h3>Communication Flow Analysis</h3>
        <p>Real-time analysis of communication patterns and flow efficiency</p>
      </div>

      <div className="flow-metrics">
        <div className="flow-metric-card">
          <div className="metric-icon">
            <i className="fas fa-stream"></i>
          </div>
          <div className="metric-info">
            <h4>{communicationFlow.length}</h4>
            <p>Active Flows</p>
            <span className="trend positive">+8.3%</span>
          </div>
        </div>

        <div className="flow-metric-card">
          <div className="metric-icon">
            <i className="fas fa-tachometer-alt"></i>
          </div>
          <div className="metric-info">
            <h4>{networkMetrics.messageRate}/s</h4>
            <p>Message Rate</p>
            <span className="trend positive">+12.1%</span>
          </div>
        </div>

        <div className="flow-metric-card">
          <div className="metric-icon">
            <i className="fas fa-clock"></i>
          </div>
          <div className="metric-info">
            <h4>{networkMetrics.averageLatency}ms</h4>
            <p>Avg Latency</p>
            <span className="trend negative">-5.2%</span>
          </div>
        </div>

        <div className="flow-metric-card">
          <div className="metric-icon">
            <i className="fas fa-shield-alt"></i>
          </div>
          <div className="metric-info">
            <h4>{networkMetrics.networkReliability}%</h4>
            <p>Reliability</p>
            <span className="trend positive">+2.1%</span>
          </div>
        </div>
      </div>

      <div className="flow-table">
        <div className="table-header">
          <div className="header-cell">Flow Name</div>
          <div className="header-cell">Type</div>
          <div className="header-cell">Participants</div>
          <div className="header-cell">Rate</div>
          <div className="header-cell">Latency</div>
          <div className="header-cell">Volume</div>
          <div className="header-cell">Status</div>
          <div className="header-cell">Actions</div>
        </div>
        
        <div className="table-body">
          {communicationFlow.map(flow => (
            <div key={flow.id} className="table-row">
              <div className="table-cell">
                <div className="flow-name">
                  <strong>{flow.name}</strong>
                  <small>{flow.protocol.toUpperCase()}</small>
                </div>
              </div>
              
              <div className="table-cell">
                <span className="flow-type">{flow.type}</span>
              </div>
              
              <div className="table-cell">
                <span className="participant-count">{flow.participants} agents</span>
              </div>
              
              <div className="table-cell">
                <span className="rate-value">{flow.messageRate}/s</span>
              </div>
              
              <div className="table-cell">
                <span className="latency-value">{flow.avgLatency}ms</span>
              </div>
              
              <div className="table-cell">
                <span className="volume-value">{flow.dataVolume} MB</span>
              </div>
              
              <div className="table-cell">
                <span className={`status-badge ${flow.status}`}>
                  {flow.status}
                </span>
              </div>
              
              <div className="table-cell">
                <button className="action-btn">
                  <i className="fas fa-chart-line"></i>
                </button>
                <button className="action-btn">
                  <i className="fas fa-cog"></i>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderProtocolAnalysis = () => (
    <div className="protocol-analysis">
      <div className="protocol-overview">
        <h3>Protocol Performance Analysis</h3>
        <p>Detailed analysis of communication protocols and their efficiency</p>
      </div>

      <div className="protocol-distribution">
        <div className="distribution-chart">
          <h4>Protocol Usage Distribution</h4>
          <div className="pie-chart-placeholder">
            {protocolStats.map((protocol, index) => (
              <div key={protocol.name} className="protocol-segment">
                <div className="segment-info">
                  <span className="protocol-name">{protocol.name.toUpperCase()}</span>
                  <span className="protocol-usage">{protocol.usage}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="protocol-comparison">
        {protocolStats.map(protocol => (
          <div key={protocol.name} className="protocol-card">
            <div className="protocol-header">
              <h4>{protocol.name.toUpperCase()}</h4>
              <div className="protocol-badges">
                <span className={`security-badge ${protocol.security}`}>
                  {protocol.security} security
                </span>
                <span className={`scalability-badge ${protocol.scalability}`}>
                  {protocol.scalability} scalability
                </span>
              </div>
            </div>

            <div className="protocol-metrics">
              <div className="metric-row">
                <span className="metric-label">Connections:</span>
                <span className="metric-value">{protocol.connections}</span>
              </div>
              <div className="metric-row">
                <span className="metric-label">Message Rate:</span>
                <span className="metric-value">{protocol.messageRate}/s</span>
              </div>
              <div className="metric-row">
                <span className="metric-label">Avg Latency:</span>
                <span className="metric-value">{protocol.averageLatency}ms</span>
              </div>
              <div className="metric-row">
                <span className="metric-label">Reliability:</span>
                <span className="metric-value">{protocol.reliability}%</span>
              </div>
              <div className="metric-row">
                <span className="metric-label">Bandwidth:</span>
                <span className="metric-value">{protocol.bandwidth} Mbps</span>
              </div>
              <div className="metric-row">
                <span className="metric-label">Error Rate:</span>
                <span className="metric-value error">{protocol.errorRate}%</span>
              </div>
            </div>

            <div className="protocol-performance">
              <div className="performance-bar">
                <div className="performance-label">Performance Score</div>
                <div className="bar-container">
                  <div 
                    className="performance-fill"
                    style={{width: `${protocol.reliability}%`}}
                  ></div>
                </div>
                <div className="performance-score">{protocol.reliability}%</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeView) {
      case 'network':
        return renderNetworkVisualization();
      case 'flow':
        return renderFlowAnalysis();
      case 'protocols':
        return renderProtocolAnalysis();
      default:
        return renderNetworkVisualization();
    }
  };

  if (loading) {
    return (
      <div className="agent-communication-network loading">
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading network visualization...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="agent-communication-network error">
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="agent-communication-network">
      <div className="network-header">
        <div className="header-left">
          <h2>Agent Communication Network</h2>
          <p>Visualize and analyze agent communication patterns and network topology</p>
        </div>
        <div className="header-actions">
          <div className="network-filters">
            <select 
              value={filters.protocol} 
              onChange={(e) => setFilters({...filters, protocol: e.target.value})}
            >
              <option value="all">All Protocols</option>
              <option value="http">HTTP</option>
              <option value="websocket">WebSocket</option>
              <option value="message-queue">Message Queue</option>
              <option value="direct">Direct</option>
              <option value="broadcast">Broadcast</option>
            </select>
            
            <select 
              value={filters.status} 
              onChange={(e) => setFilters({...filters, status: e.target.value})}
            >
              <option value="all">All Statuses</option>
              <option value="active">Active</option>
              <option value="idle">Idle</option>
              <option value="busy">Busy</option>
              <option value="maintenance">Maintenance</option>
              <option value="offline">Offline</option>
            </select>
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
      </div>

      <div className="network-navigation">
        <div className="nav-buttons">
          <button 
            className={`nav-button ${activeView === 'network' ? 'active' : ''}`}
            onClick={() => setActiveView('network')}
          >
            <i className="fas fa-project-diagram"></i>
            Network Map
          </button>
          <button 
            className={`nav-button ${activeView === 'flow' ? 'active' : ''}`}
            onClick={() => setActiveView('flow')}
          >
            <i className="fas fa-stream"></i>
            Flow Analysis
          </button>
          <button 
            className={`nav-button ${activeView === 'protocols' ? 'active' : ''}`}
            onClick={() => setActiveView('protocols')}
          >
            <i className="fas fa-layer-group"></i>
            Protocols
          </button>
        </div>
      </div>

      <div className="network-main">
        {renderContent()}
      </div>

      {/* Network Metrics Sidebar */}
      <div className="network-sidebar">
        <div className="sidebar-section">
          <h3>Network Overview</h3>
          <div className="overview-stats">
            <div className="stat-item">
              <span className="label">Total Nodes</span>
              <span className="value">{networkMetrics.totalNodes}</span>
            </div>
            <div className="stat-item">
              <span className="label">Active Connections</span>
              <span className="value">{networkMetrics.activeConnections}</span>
            </div>
            <div className="stat-item">
              <span className="label">Messages/Hour</span>
              <span className="value">{networkMetrics.totalMessages}</span>
            </div>
            <div className="stat-item">
              <span className="label">Packet Loss</span>
              <span className="value">{networkMetrics.packetLoss}%</span>
            </div>
          </div>
        </div>

        <div className="sidebar-section">
          <h3>Performance</h3>
          <div className="performance-stats">
            <div className="perf-item">
              <span className="label">Uptime</span>
              <span className="value">{networkMetrics.performance?.uptime}</span>
            </div>
            <div className="perf-item">
              <span className="label">Throughput</span>
              <span className="value">{networkMetrics.performance?.throughput}</span>
            </div>
            <div className="perf-item">
              <span className="label">Error Rate</span>
              <span className="value">{networkMetrics.performance?.errorRate}</span>
            </div>
            <div className="perf-item">
              <span className="label">Response Time</span>
              <span className="value">{networkMetrics.performance?.responseTime}</span>
            </div>
          </div>
        </div>

        <div className="sidebar-section">
          <h3>Topology</h3>
          <div className="topology-stats">
            <div className="topo-item">
              <span className="label">Clusters</span>
              <span className="value">{networkMetrics.topology?.clusters}</span>
            </div>
            <div className="topo-item">
              <span className="label">Avg Path Length</span>
              <span className="value">{networkMetrics.topology?.averagePathLength}</span>
            </div>
            <div className="topo-item">
              <span className="label">Network Density</span>
              <span className="value">{networkMetrics.topology?.networkDensity}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Node Detail Modal */}
      {networkModal && selectedNode && (
        <div className="modal-overlay" onClick={() => setNetworkModal(false)}>
          <div className="network-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{selectedNode.name}</h3>
              <button 
                className="close-button" 
                onClick={() => setNetworkModal(false)}
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-content">
              <div className="node-details">
                <div className="detail-section">
                  <h4>Agent Information</h4>
                  <div className="info-grid">
                    <div className="info-item">
                      <span className="label">Type:</span>
                      <span className="value">{selectedNode.type}</span>
                    </div>
                    <div className="info-item">
                      <span className="label">Department:</span>
                      <span className="value">{selectedNode.department}</span>
                    </div>
                    <div className="info-item">
                      <span className="label">Status:</span>
                      <span className={`value status ${selectedNode.status}`}>
                        {selectedNode.status}
                      </span>
                    </div>
                    <div className="info-item">
                      <span className="label">Uptime:</span>
                      <span className="value">{selectedNode.uptime}%</span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Communication Stats</h4>
                  <div className="stats-grid">
                    <div className="stat-card">
                      <span className="stat-label">Messages Sent</span>
                      <span className="stat-value">{selectedNode.messagesSent}</span>
                    </div>
                    <div className="stat-card">
                      <span className="stat-label">Messages Received</span>
                      <span className="stat-value">{selectedNode.messagesReceived}</span>
                    </div>
                    <div className="stat-card">
                      <span className="stat-label">Connections</span>
                      <span className="stat-value">{selectedNode.connections}</span>
                    </div>
                    <div className="stat-card">
                      <span className="stat-label">Error Rate</span>
                      <span className="stat-value">{selectedNode.errorRate}%</span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Performance Metrics</h4>
                  <div className="performance-details">
                    <div className="metric-item">
                      <span className="label">Bandwidth:</span>
                      <span className="value">{selectedNode.bandwidth} Mbps</span>
                    </div>
                    <div className="metric-item">
                      <span className="label">Latency:</span>
                      <span className="value">{selectedNode.latency} ms</span>
                    </div>
                    <div className="metric-item">
                      <span className="label">Reliability:</span>
                      <span className="value">{selectedNode.reliability}%</span>
                    </div>
                    <div className="metric-item">
                      <span className="label">Load:</span>
                      <span className="value">{selectedNode.load}%</span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Supported Protocols</h4>
                  <div className="protocol-tags">
                    {selectedNode.protocols.map(protocol => (
                      <span key={protocol} className="protocol-tag">
                        {protocol.toUpperCase()}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Connection Detail Modal */}
      {connectionModal && selectedConnection && (
        <div className="modal-overlay" onClick={() => setConnectionModal(false)}>
          <div className="connection-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Connection Details</h3>
              <button 
                className="close-button" 
                onClick={() => setConnectionModal(false)}
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-content">
              <div className="connection-details">
                <div className="connection-info">
                  <div className="endpoint">
                    <h4>Source</h4>
                    <p>{selectedConnection.source}</p>
                  </div>
                  <div className="connection-flow">
                    <i className="fas fa-arrow-right"></i>
                    <span>{selectedConnection.protocol.toUpperCase()}</span>
                  </div>
                  <div className="endpoint">
                    <h4>Target</h4>
                    <p>{selectedConnection.target}</p>
                  </div>
                </div>

                <div className="connection-metrics">
                  <div className="metric-row">
                    <span className="label">Status:</span>
                    <span className={`value status ${selectedConnection.status}`}>
                      {selectedConnection.status}
                    </span>
                  </div>
                  <div className="metric-row">
                    <span className="label">Message Count:</span>
                    <span className="value">{selectedConnection.messageCount}</span>
                  </div>
                  <div className="metric-row">
                    <span className="label">Bandwidth:</span>
                    <span className="value">{selectedConnection.bandwidth} Mbps</span>
                  </div>
                  <div className="metric-row">
                    <span className="label">Latency:</span>
                    <span className="value">{selectedConnection.latency} ms</span>
                  </div>
                  <div className="metric-row">
                    <span className="label">Packet Loss:</span>
                    <span className="value">{selectedConnection.packetLoss}%</span>
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

export default AgentCommunicationNetwork;
