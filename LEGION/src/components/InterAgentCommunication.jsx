import React, { useState, useEffect, useCallback } from 'react';

const InterAgentCommunication = () => {
  const [communications, setCommunications] = useState([]);
  const [agents, setAgents] = useState([]);
  const [selectedView, setSelectedView] = useState('real-time');
  const [communicationFilters, setCommunicationFilters] = useState({
    type: 'all',
    protocol: 'all',
    priority: 'all',
    status: 'all',
    timeRange: '1h',
    sender: 'all',
    receiver: 'all'
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [selectedCommunication, setSelectedCommunication] = useState(null);
  const [communicationModal, setCommunicationModal] = useState(false);
  const [networkTopology, setNetworkTopology] = useState([]);
  const [communicationStats, setCommunicationStats] = useState({});
  const [realTimeData, setRealTimeData] = useState([]);

  // Mock data generators
  const generateAgents = useCallback(() => {
    const agentTypes = ['analytics', 'automation', 'communication', 'research', 'optimization', 'monitoring'];
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
      status: ['active', 'idle', 'busy', 'maintenance'][Math.floor(Math.random() * 4)],
      communicationCount: Math.floor(Math.random() * 200) + 50,
      lastCommunication: new Date(Date.now() - Math.random() * 60 * 60 * 1000).toISOString(),
      communicationRate: (Math.random() * 50 + 10).toFixed(1) + '/min',
      responseTime: (Math.random() * 200 + 50).toFixed(0) + 'ms',
      bandwidth: (Math.random() * 100 + 20).toFixed(0) + 'Mbps',
      reliability: Math.floor(Math.random() * 20) + 80,
      location: ['Cloud-1', 'Cloud-2', 'Edge-1', 'Edge-2'][Math.floor(Math.random() * 4)]
    }));
  }, []);

  const generateCommunications = useCallback(() => {
    const communicationTypes = ['inter-agent', 'system-notification', 'task-update', 'error-report', 'status-sync', 'coordination', 'heartbeat', 'data-transfer'];
    const protocols = ['http', 'websocket', 'message-queue', 'direct', 'broadcast', 'multicast'];
    const priorities = ['critical', 'high', 'normal', 'low'];
    const statuses = ['sent', 'delivered', 'acknowledged', 'failed', 'pending', 'timeout', 'retrying'];

    return Array.from({ length: 150 }, (_, index) => {
      const senderId = `agent-${Math.floor(Math.random() * 16) + 1}`;
      const receiverId = `agent-${Math.floor(Math.random() * 16) + 1}`;
      const type = communicationTypes[Math.floor(Math.random() * communicationTypes.length)];
      const protocol = protocols[Math.floor(Math.random() * protocols.length)];
      const priority = priorities[Math.floor(Math.random() * priorities.length)];
      const status = statuses[Math.floor(Math.random() * statuses.length)];
      
      return {
        id: `comm-${index + 1}`,
        type,
        protocol,
        priority,
        status,
        senderId,
        receiverId,
        timestamp: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString(),
        message: `${type.replace('-', ' ')} message for enterprise coordination`,
        messageSize: Math.floor(Math.random() * 1000) + 100,
        responseTime: (Math.random() * 1000 + 10).toFixed(0),
        retries: Math.floor(Math.random() * 4),
        latency: (Math.random() * 100 + 5).toFixed(1),
        bandwidth: (Math.random() * 50 + 10).toFixed(1),
        encryption: Math.random() > 0.2,
        compressed: Math.random() > 0.3,
        acknowledged: Math.random() > 0.1,
        errorCode: Math.random() > 0.8 ? `E${Math.floor(Math.random() * 1000) + 100}` : null,
        route: Math.floor(Math.random() * 3) + 1,
        hops: Math.floor(Math.random() * 5) + 1,
        queueTime: (Math.random() * 500 + 10).toFixed(0),
        processingTime: (Math.random() * 200 + 20).toFixed(0),
        deliveryTime: (Math.random() * 300 + 50).toFixed(0),
        correlationId: `corr-${Math.floor(Math.random() * 10000) + 1000}`,
        sessionId: `sess-${Math.floor(Math.random() * 1000) + 100}`,
        traceId: `trace-${Math.floor(Math.random() * 100000) + 10000}`,
        metadata: {
          userAgent: 'Legion-Agent/1.0',
          version: `v${Math.floor(Math.random() * 3) + 1}.0`,
          region: ['us-east', 'us-west', 'eu-central', 'asia-pacific'][Math.floor(Math.random() * 4)]
        }
      };
    });
  }, []);

  const generateNetworkTopology = useCallback(() => {
    const agents = Array.from({ length: 16 }, (_, i) => `agent-${i + 1}`);
    const connections = [];
    
    agents.forEach(agent => {
      const connectionCount = Math.floor(Math.random() * 5) + 2;
      const connectedAgents = [...agents].sort(() => 0.5 - Math.random()).slice(0, connectionCount);
      
      connectedAgents.forEach(connectedAgent => {
        if (agent !== connectedAgent) {
          connections.push({
            id: `${agent}-${connectedAgent}`,
            source: agent,
            target: connectedAgent,
            strength: Math.floor(Math.random() * 100) + 20,
            latency: (Math.random() * 50 + 5).toFixed(1),
            bandwidth: (Math.random() * 100 + 50).toFixed(0),
            reliability: Math.floor(Math.random() * 20) + 80,
            messageCount: Math.floor(Math.random() * 1000) + 100,
            lastActivity: new Date(Date.now() - Math.random() * 60 * 60 * 1000).toISOString(),
            status: ['active', 'idle', 'congested'][Math.floor(Math.random() * 3)]
          });
        }
      });
    });
    
    return connections;
  }, []);

  const generateCommunicationStats = useCallback(() => {
    return {
      totalMessages: Math.floor(Math.random() * 10000) + 5000,
      messagesPerSecond: (Math.random() * 50 + 10).toFixed(1),
      averageLatency: (Math.random() * 100 + 20).toFixed(1),
      successRate: (Math.random() * 10 + 90).toFixed(2),
      errorRate: (Math.random() * 5).toFixed(2),
      bandwidth: (Math.random() * 500 + 100).toFixed(0),
      activeConnections: Math.floor(Math.random() * 100) + 50,
      queuedMessages: Math.floor(Math.random() * 500) + 50,
      protocolDistribution: {
        http: Math.floor(Math.random() * 40) + 20,
        websocket: Math.floor(Math.random() * 30) + 15,
        messageQueue: Math.floor(Math.random() * 20) + 10,
        direct: Math.floor(Math.random() * 15) + 5,
        broadcast: Math.floor(Math.random() * 10) + 5
      },
      typeDistribution: {
        interAgent: Math.floor(Math.random() * 40) + 30,
        systemNotification: Math.floor(Math.random() * 20) + 15,
        taskUpdate: Math.floor(Math.random() * 15) + 10,
        errorReport: Math.floor(Math.random() * 10) + 5,
        statusSync: Math.floor(Math.random() * 10) + 5,
        heartbeat: Math.floor(Math.random() * 15) + 10
      },
      hourlyTrend: Array.from({ length: 24 }, (_, i) => ({
        hour: i,
        messages: Math.floor(Math.random() * 500) + 100,
        errors: Math.floor(Math.random() * 20) + 2,
        latency: (Math.random() * 50 + 20).toFixed(1)
      }))
    };
  }, []);

  const generateRealTimeData = useCallback(() => {
    return Array.from({ length: 10 }, (_, index) => ({
      id: `realtime-${index + 1}`,
      timestamp: new Date(Date.now() - index * 5000).toISOString(),
      senderId: `agent-${Math.floor(Math.random() * 16) + 1}`,
      receiverId: `agent-${Math.floor(Math.random() * 16) + 1}`,
      type: ['inter-agent', 'heartbeat', 'status-sync', 'task-update'][Math.floor(Math.random() * 4)],
      status: ['delivered', 'pending', 'acknowledged'][Math.floor(Math.random() * 3)],
      latency: (Math.random() * 100 + 10).toFixed(1),
      size: Math.floor(Math.random() * 500) + 100
    }));
  }, []);

  // Data loading
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        await new Promise(resolve => setTimeout(resolve, 1200));
        
        setAgents(generateAgents());
        setCommunications(generateCommunications());
        setNetworkTopology(generateNetworkTopology());
        setCommunicationStats(generateCommunicationStats());
        setRealTimeData(generateRealTimeData());
        
      } catch (error) {
        console.error('Error loading communication data:', error);
        setError('Failed to load communication data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [generateAgents, generateCommunications, generateNetworkTopology, generateCommunicationStats, generateRealTimeData]);

  // Real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      if (selectedView === 'real-time') {
        setRealTimeData(prev => {
          const newData = {
            id: `realtime-${Date.now()}`,
            timestamp: new Date().toISOString(),
            senderId: `agent-${Math.floor(Math.random() * 16) + 1}`,
            receiverId: `agent-${Math.floor(Math.random() * 16) + 1}`,
            type: ['inter-agent', 'heartbeat', 'status-sync', 'task-update'][Math.floor(Math.random() * 4)],
            status: ['delivered', 'pending', 'acknowledged'][Math.floor(Math.random() * 3)],
            latency: (Math.random() * 100 + 10).toFixed(1),
            size: Math.floor(Math.random() * 500) + 100
          };
          return [newData, ...prev.slice(0, 19)];
        });
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [selectedView]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    setCommunications(generateCommunications());
    setCommunicationStats(generateCommunicationStats());
    setNetworkTopology(generateNetworkTopology());
    
    setRefreshing(false);
  };

  const filteredCommunications = communications.filter(comm => {
    const matchesFilters = 
      (communicationFilters.type === 'all' || comm.type === communicationFilters.type) &&
      (communicationFilters.protocol === 'all' || comm.protocol === communicationFilters.protocol) &&
      (communicationFilters.priority === 'all' || comm.priority === communicationFilters.priority) &&
      (communicationFilters.status === 'all' || comm.status === communicationFilters.status) &&
      (communicationFilters.sender === 'all' || comm.senderId === communicationFilters.sender) &&
      (communicationFilters.receiver === 'all' || comm.receiverId === communicationFilters.receiver);
    
    const matchesSearch = !searchQuery || 
      comm.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
      comm.type.toLowerCase().includes(searchQuery.toLowerCase()) ||
      comm.correlationId.toLowerCase().includes(searchQuery.toLowerCase());
    
    // Time range filter
    const now = Date.now();
    const commTime = new Date(comm.timestamp).getTime();
    const timeRangeMs = {
      '1h': 60 * 60 * 1000,
      '6h': 6 * 60 * 60 * 1000,
      '24h': 24 * 60 * 60 * 1000,
      '7d': 7 * 24 * 60 * 60 * 1000
    }[communicationFilters.timeRange] || 60 * 60 * 1000;
    
    const matchesTimeRange = (now - commTime) <= timeRangeMs;
    
    return matchesFilters && matchesSearch && matchesTimeRange;
  });

  const getStatusColor = (status) => {
    const colors = {
      sent: '#17a2b8',
      delivered: '#28a745',
      acknowledged: '#20c997',
      failed: '#dc3545',
      pending: '#ffc107',
      timeout: '#fd7e14',
      retrying: '#6f42c1'
    };
    return colors[status] || '#666';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      critical: '#dc3545',
      high: '#fd7e14',
      normal: '#17a2b8',
      low: '#28a745'
    };
    return colors[priority] || '#666';
  };

  const renderRealTimeView = () => (
    <div className="real-time-content">
      <div className="real-time-stats">
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-paper-plane"></i>
          </div>
          <div className="stat-content">
            <h3>{communicationStats.messagesPerSecond}</h3>
            <p>Messages/sec</p>
            <span className="stat-trend">+12.3%</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-clock"></i>
          </div>
          <div className="stat-content">
            <h3>{communicationStats.averageLatency}ms</h3>
            <p>Avg Latency</p>
            <span className="stat-trend">-2.1%</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-check-circle"></i>
          </div>
          <div className="stat-content">
            <h3>{communicationStats.successRate}%</h3>
            <p>Success Rate</p>
            <span className="stat-trend">+0.5%</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-network-wired"></i>
          </div>
          <div className="stat-content">
            <h3>{communicationStats.activeConnections}</h3>
            <p>Active Connections</p>
            <span className="stat-trend">+8</span>
          </div>
        </div>
      </div>

      <div className="real-time-feed">
        <div className="feed-header">
          <h3>Live Communication Stream</h3>
          <div className="feed-controls">
            <button className="pause-btn">
              <i className="fas fa-pause"></i>
              Pause
            </button>
            <button className="clear-btn">
              <i className="fas fa-trash"></i>
              Clear
            </button>
          </div>
        </div>
        
        <div className="communication-stream">
          {realTimeData.map(comm => (
            <div key={comm.id} className="stream-item">
              <div className="stream-time">
                {new Date(comm.timestamp).toLocaleTimeString()}
              </div>
              <div className="stream-flow">
                <div className="stream-agent sender">
                  Agent {comm.senderId.split('-')[1]}
                </div>
                <div className="stream-arrow">
                  <i className="fas fa-arrow-right"></i>
                  <span className="stream-type">{comm.type}</span>
                </div>
                <div className="stream-agent receiver">
                  Agent {comm.receiverId.split('-')[1]}
                </div>
              </div>
              <div className="stream-details">
                <span className="stream-status" style={{ color: getStatusColor(comm.status) }}>
                  {comm.status}
                </span>
                <span className="stream-latency">{comm.latency}ms</span>
                <span className="stream-size">{comm.size}B</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderAnalyticsView = () => (
    <div className="analytics-content">
      <div className="analytics-overview">
        <div className="overview-cards">
          <div className="overview-card">
            <h3>Total Messages</h3>
            <div className="card-value">{communicationStats.totalMessages?.toLocaleString()}</div>
            <div className="card-detail">Last 24 hours</div>
          </div>
          <div className="overview-card">
            <h3>Error Rate</h3>
            <div className="card-value">{communicationStats.errorRate}%</div>
            <div className="card-detail">Within threshold</div>
          </div>
          <div className="overview-card">
            <h3>Bandwidth Usage</h3>
            <div className="card-value">{communicationStats.bandwidth} Mbps</div>
            <div className="card-detail">Peak utilization</div>
          </div>
          <div className="overview-card">
            <h3>Queue Length</h3>
            <div className="card-value">{communicationStats.queuedMessages}</div>
            <div className="card-detail">Pending messages</div>
          </div>
        </div>
      </div>

      <div className="analytics-charts">
        <div className="chart-section">
          <h3>Protocol Distribution</h3>
          <div className="protocol-chart">
            {Object.entries(communicationStats.protocolDistribution || {}).map(([protocol, count]) => {
              const total = Object.values(communicationStats.protocolDistribution || {}).reduce((sum, val) => sum + val, 0);
              const percentage = total > 0 ? (count / total) * 100 : 0;
              
              return (
                <div key={protocol} className="protocol-bar">
                  <div className="bar-label">
                    <span className="protocol-name">{protocol}</span>
                    <span className="protocol-count">{count}</span>
                  </div>
                  <div className="bar-container">
                    <div 
                      className="bar-fill" 
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                  <span className="bar-percentage">{percentage.toFixed(1)}%</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="chart-section">
          <h3>Message Type Distribution</h3>
          <div className="type-chart">
            {Object.entries(communicationStats.typeDistribution || {}).map(([type, count]) => {
              const total = Object.values(communicationStats.typeDistribution || {}).reduce((sum, val) => sum + val, 0);
              const percentage = total > 0 ? (count / total) * 100 : 0;
              
              return (
                <div key={type} className="type-item">
                  <div className="type-info">
                    <span className="type-name">{type.replace(/([A-Z])/g, ' $1').toLowerCase()}</span>
                    <span className="type-percentage">{percentage.toFixed(1)}%</span>
                  </div>
                  <div className="type-bar">
                    <div 
                      className="type-fill" 
                      style={{ width: `${percentage}%` }}
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

  const renderCommunicationsView = () => (
    <div className="communications-content">
      <div className="communications-controls">
        <div className="search-section">
          <div className="search-input">
            <i className="fas fa-search"></i>
            <input
              type="text"
              placeholder="Search communications..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        <div className="filter-section">
          <select value={communicationFilters.type} onChange={(e) => setCommunicationFilters({...communicationFilters, type: e.target.value})}>
            <option value="all">All Types</option>
            <option value="inter-agent">Inter-Agent</option>
            <option value="system-notification">System Notification</option>
            <option value="task-update">Task Update</option>
            <option value="error-report">Error Report</option>
            <option value="heartbeat">Heartbeat</option>
          </select>
          
          <select value={communicationFilters.protocol} onChange={(e) => setCommunicationFilters({...communicationFilters, protocol: e.target.value})}>
            <option value="all">All Protocols</option>
            <option value="http">HTTP</option>
            <option value="websocket">WebSocket</option>
            <option value="message-queue">Message Queue</option>
            <option value="direct">Direct</option>
            <option value="broadcast">Broadcast</option>
          </select>
          
          <select value={communicationFilters.status} onChange={(e) => setCommunicationFilters({...communicationFilters, status: e.target.value})}>
            <option value="all">All Statuses</option>
            <option value="delivered">Delivered</option>
            <option value="pending">Pending</option>
            <option value="failed">Failed</option>
            <option value="acknowledged">Acknowledged</option>
          </select>
          
          <select value={communicationFilters.timeRange} onChange={(e) => setCommunicationFilters({...communicationFilters, timeRange: e.target.value})}>
            <option value="1h">Last Hour</option>
            <option value="6h">Last 6 Hours</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
          </select>
        </div>
      </div>

      <div className="communications-table">
        <div className="table-header">
          <div className="header-cell">Time</div>
          <div className="header-cell">Type</div>
          <div className="header-cell">From → To</div>
          <div className="header-cell">Protocol</div>
          <div className="header-cell">Status</div>
          <div className="header-cell">Latency</div>
          <div className="header-cell">Size</div>
          <div className="header-cell">Actions</div>
        </div>
        
        <div className="table-body">
          {filteredCommunications.slice(0, 50).map(comm => (
            <div key={comm.id} className="table-row">
              <div className="table-cell">
                {new Date(comm.timestamp).toLocaleTimeString()}
              </div>
              <div className="table-cell">
                <span className="comm-type">{comm.type}</span>
              </div>
              <div className="table-cell">
                <div className="agent-flow">
                  <span className="agent-id">Agent {comm.senderId.split('-')[1]}</span>
                  <i className="fas fa-arrow-right"></i>
                  <span className="agent-id">Agent {comm.receiverId.split('-')[1]}</span>
                </div>
              </div>
              <div className="table-cell">
                <span className="protocol-badge">{comm.protocol}</span>
              </div>
              <div className="table-cell">
                <span 
                  className="status-badge" 
                  style={{ backgroundColor: getStatusColor(comm.status) }}
                >
                  {comm.status}
                </span>
              </div>
              <div className="table-cell">
                <span className="latency-value">{comm.latency}ms</span>
              </div>
              <div className="table-cell">
                <span className="size-value">{comm.messageSize}B</span>
              </div>
              <div className="table-cell">
                <button 
                  className="action-btn"
                  onClick={() => {
                    setSelectedCommunication(comm);
                    setCommunicationModal(true);
                  }}
                >
                  <i className="fas fa-eye"></i>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (selectedView) {
      case 'real-time':
        return renderRealTimeView();
      case 'analytics':
        return renderAnalyticsView();
      case 'communications':
        return renderCommunicationsView();
      default:
        return renderRealTimeView();
    }
  };

  if (loading) {
    return (
      <div className="inter-agent-communication loading">
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading communication monitoring...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="inter-agent-communication error">
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="inter-agent-communication">
      <div className="communication-header">
        <div className="header-left">
          <h2>Inter-Agent Communication Monitor</h2>
          <p>Real-time communication flow analysis and monitoring</p>
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

      <div className="communication-navigation">
        <div className="nav-buttons">
          <button 
            className={`nav-button ${selectedView === 'real-time' ? 'active' : ''}`}
            onClick={() => setSelectedView('real-time')}
          >
            <i className="fas fa-broadcast-tower"></i>
            Real-Time
          </button>
          <button 
            className={`nav-button ${selectedView === 'analytics' ? 'active' : ''}`}
            onClick={() => setSelectedView('analytics')}
          >
            <i className="fas fa-chart-bar"></i>
            Analytics
          </button>
          <button 
            className={`nav-button ${selectedView === 'communications' ? 'active' : ''}`}
            onClick={() => setSelectedView('communications')}
          >
            <i className="fas fa-list"></i>
            Communications
            <span className="count">{filteredCommunications.length}</span>
          </button>
        </div>
      </div>

      <div className="communication-main">
        {renderContent()}
      </div>

      {/* Communication Details Modal */}
      {communicationModal && selectedCommunication && (
        <div className="modal-overlay" onClick={() => setCommunicationModal(false)}>
          <div className="communication-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Communication Details</h3>
              <button 
                className="close-button"
                onClick={() => setCommunicationModal(false)}
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
            
            <div className="modal-content">
              <div className="communication-details">
                <div className="detail-section">
                  <h4>Basic Information</h4>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <span className="detail-label">ID:</span>
                      <span className="detail-value">{selectedCommunication.id}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Type:</span>
                      <span className="detail-value">{selectedCommunication.type}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Protocol:</span>
                      <span className="detail-value">{selectedCommunication.protocol}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Priority:</span>
                      <span className="detail-value" style={{ color: getPriorityColor(selectedCommunication.priority) }}>
                        {selectedCommunication.priority}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Communication Flow</h4>
                  <div className="flow-diagram">
                    <div className="flow-agent">
                      <i className="fas fa-robot"></i>
                      <span>Agent {selectedCommunication.senderId.split('-')[1]}</span>
                    </div>
                    <div className="flow-arrow">
                      <i className="fas fa-arrow-right"></i>
                      <span className="flow-message">{selectedCommunication.message}</span>
                    </div>
                    <div className="flow-agent">
                      <i className="fas fa-robot"></i>
                      <span>Agent {selectedCommunication.receiverId.split('-')[1]}</span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Performance Metrics</h4>
                  <div className="metrics-grid">
                    <div className="metric-item">
                      <span className="metric-label">Latency:</span>
                      <span className="metric-value">{selectedCommunication.latency}ms</span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Response Time:</span>
                      <span className="metric-value">{selectedCommunication.responseTime}ms</span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Message Size:</span>
                      <span className="metric-value">{selectedCommunication.messageSize} bytes</span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Retries:</span>
                      <span className="metric-value">{selectedCommunication.retries}</span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Technical Details</h4>
                  <div className="technical-info">
                    <div className="tech-item">
                      <span className="tech-label">Correlation ID:</span>
                      <span className="tech-value">{selectedCommunication.correlationId}</span>
                    </div>
                    <div className="tech-item">
                      <span className="tech-label">Trace ID:</span>
                      <span className="tech-value">{selectedCommunication.traceId}</span>
                    </div>
                    <div className="tech-item">
                      <span className="tech-label">Encrypted:</span>
                      <span className="tech-value">
                        <i className={`fas fa-${selectedCommunication.encryption ? 'lock' : 'unlock'}`}></i>
                        {selectedCommunication.encryption ? 'Yes' : 'No'}
                      </span>
                    </div>
                    <div className="tech-item">
                      <span className="tech-label">Compressed:</span>
                      <span className="tech-value">
                        <i className={`fas fa-${selectedCommunication.compressed ? 'compress' : 'expand'}`}></i>
                        {selectedCommunication.compressed ? 'Yes' : 'No'}
                      </span>
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

export default InterAgentCommunication;
