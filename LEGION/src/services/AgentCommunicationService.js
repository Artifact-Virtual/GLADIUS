// src/services/AgentCommunicationService.js
// LEGION Enterprise Dashboard - Agent Communication Service
// Comprehensive agent monitoring, communication, and coordination service

/**
 * Agent Communication Service - Production Configuration
 * Provides comprehensive agent monitoring, communication tracking, and coordination
 * for the LEGION Enterprise Dashboard system
 */
class AgentCommunicationService {
  constructor() {
    // Production environment configuration
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:5001';
    this.wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:5002';
    this.cache = new Map();
    this.subscribers = new Map();
    this.wsConnections = new Map();
    this.agentRegistry = new Map();
    this.communicationHistory = [];
    
    // Production settings
    this.retryAttempts = parseInt(process.env.REACT_APP_MAX_RETRIES || '5');
    this.retryDelay = 2000; // Increased for production stability
    this.cacheTimeout = 300000; // 5 minutes for production
    this.heartbeatInterval = 30000; // 30 seconds
    this.connectionTimeout = 10000; // 10 seconds connection timeout
    this.isOnline = navigator.onLine;
    this.productionMode = process.env.NODE_ENV === 'production';
    
    // Performance monitoring
    this.performanceMetrics = {
      requestCount: 0,
      errorCount: 0,
      averageResponseTime: 0,
      lastHealthCheck: null
    };
    
    // Initialize agent monitoring with production settings
    this.initializeAgentMonitoring();
    
    console.log(`AgentCommunicationService initialized in ${this.productionMode ? 'PRODUCTION' : 'DEVELOPMENT'} mode`);
  }

  /**
   * Initialize agent monitoring and health tracking
   */
  initializeAgentMonitoring() {
    // Start heartbeat monitoring
    setInterval(() => {
      this.performHealthChecks();
    }, this.heartbeatInterval);

    // Initialize connection monitoring
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.reconnectAgentConnections();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
    });
  }

  /**
   * Agent Registry and Discovery
   */
  async getActiveAgents() {
    return this.fetchWithCache('active-agents', '/api/agents/active', {
      refresh: 15000, // 15 seconds
      priority: 'critical'
    });
  }

  async getAgentDetails(agentId) {
    return this.fetchWithCache(`agent-details-${agentId}`, `/api/agents/${agentId}`, {
      refresh: 30000, // 30 seconds
      priority: 'high'
    });
  }

  async getAgentsByDepartment(department) {
    return this.fetchWithCache(`agents-department-${department}`, `/api/agents/department/${department}`, {
      refresh: 60000, // 1 minute
      priority: 'medium'
    });
  }

  async getAgentCapabilities(agentId) {
    return this.fetchWithCache(`agent-capabilities-${agentId}`, `/api/agents/${agentId}/capabilities`, {
      refresh: 300000, // 5 minutes
      priority: 'low'
    });
  }

  /**
   * Agent Performance and Health Monitoring
   */
  async getAgentHealth(agentId) {
    return this.fetchWithCache(`agent-health-${agentId}`, `/api/agents/${agentId}/health`, {
      refresh: 10000, // 10 seconds
      priority: 'critical'
    });
  }

  async getAgentPerformanceMetrics(agentId, timeRange = '1h') {
    return this.fetchWithCache(
      `agent-performance-${agentId}-${timeRange}`,
      `/api/agents/${agentId}/performance?range=${timeRange}`,
      {
        refresh: 30000, // 30 seconds
        priority: 'high'
      }
    );
  }

  async getAgentStatusMatrix() {
    return this.fetchWithCache('agent-status-matrix', '/api/agents/status-matrix', {
      refresh: 20000, // 20 seconds
      priority: 'high'
    });
  }

  async getAgentWorkloadDistribution() {
    return this.fetchWithCache('agent-workload-distribution', '/api/agents/workload-distribution', {
      refresh: 45000, // 45 seconds
      priority: 'medium'
    });
  }

  /**
   * Inter-Agent Communication Monitoring
   */
  async getInterAgentCommunications(timeRange = '1h') {
    return this.fetchWithCache(
      `inter-agent-comms-${timeRange}`,
      `/api/agents/communications?range=${timeRange}`,
      {
        refresh: 15000, // 15 seconds
        priority: 'high'
      }
    );
  }

  async getCommunicationProtocols() {
    return this.fetchWithCache('communication-protocols', '/api/agents/protocols', {
      refresh: 300000, // 5 minutes
      priority: 'low'
    });
  }

  async getCommunicationFlow(fromAgent, toAgent, timeRange = '30m') {
    return this.fetchWithCache(
      `comm-flow-${fromAgent}-${toAgent}-${timeRange}`,
      `/api/agents/communication-flow?from=${fromAgent}&to=${toAgent}&range=${timeRange}`,
      {
        refresh: 30000, // 30 seconds
        priority: 'medium'
      }
    );
  }

  async getMessageTracing(messageId) {
    return this.fetchWithCache(`message-trace-${messageId}`, `/api/agents/messages/${messageId}/trace`, {
      refresh: 60000, // 1 minute
      priority: 'medium'
    });
  }

  /**
   * Agent Task and Queue Management
   */
  async getAgentTaskQueues() {
    return this.fetchWithCache('agent-task-queues', '/api/agents/task-queues', {
      refresh: 20000, // 20 seconds
      priority: 'high'
    });
  }

  async getAgentTaskHistory(agentId, limit = 100) {
    return this.fetchWithCache(
      `agent-task-history-${agentId}-${limit}`,
      `/api/agents/${agentId}/tasks/history?limit=${limit}`,
      {
        refresh: 60000, // 1 minute
        priority: 'medium'
      }
    );
  }

  async getTaskDelegationTracking() {
    return this.fetchWithCache('task-delegation-tracking', '/api/agents/task-delegation', {
      refresh: 30000, // 30 seconds
      priority: 'high'
    });
  }

  async assignTaskToAgent(agentId, taskData) {
    const response = await this.makeRequest(`/api/agents/${agentId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(taskData)
    });
    
    // Invalidate related cache
    this.invalidateCache(['agent-task-queues', `agent-task-history-${agentId}`]);
    
    return response;
  }

  /**
   * Agent Deployment and Environment Management
   */
  async getAgentDeployments() {
    return this.fetchWithCache('agent-deployments', '/api/agents/deployments', {
      refresh: 60000, // 1 minute
      priority: 'medium'
    });
  }

  async getDeploymentMatrix() {
    return this.fetchWithCache('deployment-matrix', '/api/agents/deployment-matrix', {
      refresh: 120000, // 2 minutes
      priority: 'medium'
    });
  }

  async deployAgent(agentConfig) {
    const response = await this.makeRequest('/api/agents/deploy', {
      method: 'POST',
      body: JSON.stringify(agentConfig)
    });
    
    // Invalidate deployment cache
    this.invalidateCache(['agent-deployments', 'deployment-matrix', 'active-agents']);
    
    return response;
  }

  async scaleAgent(agentId, instances) {
    const response = await this.makeRequest(`/api/agents/${agentId}/scale`, {
      method: 'POST',
      body: JSON.stringify({ instances })
    });
    
    this.invalidateCache(['agent-deployments', 'agent-workload-distribution']);
    
    return response;
  }

  /**
   * Agent Communication Network Analysis
   */
  async getCommunicationNetwork() {
    return this.fetchWithCache('communication-network', '/api/agents/network', {
      refresh: 90000, // 1.5 minutes
      priority: 'medium'
    });
  }

  async getNetworkTopology() {
    return this.fetchWithCache('network-topology', '/api/agents/network/topology', {
      refresh: 300000, // 5 minutes
      priority: 'low'
    });
  }

  async getNetworkPerformance(timeRange = '1h') {
    return this.fetchWithCache(
      `network-performance-${timeRange}`,
      `/api/agents/network/performance?range=${timeRange}`,
      {
        refresh: 60000, // 1 minute
        priority: 'medium'
      }
    );
  }

  async getNetworkBottlenecks() {
    return this.fetchWithCache('network-bottlenecks', '/api/agents/network/bottlenecks', {
      refresh: 120000, // 2 minutes
      priority: 'medium'
    });
  }

  /**
   * Agent Control and Coordination
   */
  async getCoordinationPolicies() {
    return this.fetchWithCache('coordination-policies', '/api/agents/coordination/policies', {
      refresh: 600000, // 10 minutes
      priority: 'low'
    });
  }

  async getResourceAllocation() {
    return this.fetchWithCache('resource-allocation', '/api/agents/resources/allocation', {
      refresh: 90000, // 1.5 minutes
      priority: 'medium'
    });
  }

  async executeEmergencyCommand(command, targets = []) {
    return this.makeRequest('/api/agents/emergency/execute', {
      method: 'POST',
      body: JSON.stringify({ command, targets })
    });
  }

  async pauseAgent(agentId, reason = '') {
    const response = await this.makeRequest(`/api/agents/${agentId}/pause`, {
      method: 'POST',
      body: JSON.stringify({ reason })
    });
    
    this.invalidateCache([`agent-health-${agentId}`, 'active-agents']);
    
    return response;
  }

  async resumeAgent(agentId) {
    const response = await this.makeRequest(`/api/agents/${agentId}/resume`, {
      method: 'POST'
    });
    
    this.invalidateCache([`agent-health-${agentId}`, 'active-agents']);
    
    return response;
  }

  /**
   * Real-time Agent Monitoring Subscriptions
   */
  subscribeToAgentHealth(callback) {
    return this.subscribe('agent-health', callback, {
      endpoint: '/ws/agents/health',
      reconnect: true
    });
  }

  subscribeToAgentCommunications(callback) {
    return this.subscribe('agent-communications', callback, {
      endpoint: '/ws/agents/communications',
      reconnect: true
    });
  }

  subscribeToTaskQueue(agentId, callback) {
    return this.subscribe(`task-queue-${agentId}`, callback, {
      endpoint: `/ws/agents/${agentId}/tasks`,
      reconnect: true
    });
  }

  subscribeToNetworkActivity(callback) {
    return this.subscribe('network-activity', callback, {
      endpoint: '/ws/agents/network/activity',
      reconnect: true
    });
  }

  subscribeToDeploymentUpdates(callback) {
    return this.subscribe('deployment-updates', callback, {
      endpoint: '/ws/agents/deployments',
      reconnect: true
    });
  }

  /**
   * Agent Analytics and Reporting
   */
  async getAgentAnalytics(timeRange = '24h') {
    return this.fetchWithCache(
      `agent-analytics-${timeRange}`,
      `/api/agents/analytics?range=${timeRange}`,
      {
        refresh: 180000, // 3 minutes
        priority: 'medium'
      }
    );
  }

  async getPerformanceComparison(agentIds, metric = 'efficiency') {
    return this.fetchWithCache(
      `performance-comparison-${agentIds.join(',')}-${metric}`,
      `/api/agents/performance/compare`,
      {
        method: 'POST',
        body: JSON.stringify({ agentIds, metric }),
        refresh: 300000, // 5 minutes
        priority: 'medium'
      }
    );
  }

  async generateAgentReport(reportType, parameters = {}) {
    return this.makeRequest('/api/agents/reports/generate', {
      method: 'POST',
      body: JSON.stringify({
        type: reportType,
        parameters
      })
    });
  }

  /**
   * Agent Communication History and Logs
   */
  async getCommunicationLogs(filters = {}) {
    const queryParams = new URLSearchParams(filters);
    return this.fetchWithCache(
      `communication-logs-${queryParams.toString()}`,
      `/api/agents/communication-logs?${queryParams}`,
      {
        refresh: 120000, // 2 minutes
        priority: 'medium'
      }
    );
  }

  async searchCommunications(query, filters = {}) {
    return this.makeRequest('/api/agents/communications/search', {
      method: 'POST',
      body: JSON.stringify({ query, filters })
    });
  }

  async exportCommunicationData(format = 'csv', filters = {}) {
    const queryParams = new URLSearchParams({
      format,
      ...filters
    });

    return this.makeRequest(`/api/agents/communications/export?${queryParams}`, {
      responseType: 'blob'
    });
  }

  /**
   * Agent Health Checks and Monitoring
   */
  async performHealthChecks() {
    try {
      const agents = await this.getActiveAgents();
      const healthPromises = agents.map(agent => 
        this.getAgentHealth(agent.id).catch(error => ({
          agentId: agent.id,
          status: 'error',
          error: error.message
        }))
      );

      const healthResults = await Promise.all(healthPromises);
      
      // Update agent registry
      healthResults.forEach(result => {
        if (result.agentId) {
          this.agentRegistry.set(result.agentId, {
            ...this.agentRegistry.get(result.agentId),
            lastHealthCheck: Date.now(),
            health: result
          });
        }
      });

      // Notify subscribers of health updates
      this.notifySubscribers('health-check-complete', healthResults);

      return healthResults;
    } catch (error) {
      console.error('Health check failed:', error);
      return [];
    }
  }

  /**
   * Core Service Methods (inherited pattern from EnterpriseDataService)
   */
  async fetchWithCache(key, url, options = {}) {
    const cacheKey = `${key}_${JSON.stringify(options)}`;
    const cached = this.cache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < (options.refresh || this.cacheTimeout)) {
      return cached.data;
    }

    try {
      const data = await this.makeRequest(url, options);
      
      this.cache.set(cacheKey, {
        data,
        timestamp: Date.now()
      });

      return data;
    } catch (error) {
      if (cached) {
        console.warn(`Using cached data for ${key} due to error:`, error);
        return cached.data;
      }
      throw error;
    }
  }

  async makeRequest(url, options = {}) {
    const config = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    let attempts = 0;
    while (attempts < this.retryAttempts) {
      try {
        const response = await fetch(`${this.baseUrl}${url}`, config);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        if (options.responseType === 'blob') {
          return await response.blob();
        }

        return await response.json();
      } catch (error) {
        attempts++;
        if (attempts >= this.retryAttempts) {
          throw error;
        }
        await this.delay(this.retryDelay * attempts);
      }
    }
  }

  subscribe(channel, callback, options = {}) {
    if (!this.subscribers.has(channel)) {
      this.subscribers.set(channel, new Set());
    }
    this.subscribers.get(channel).add(callback);

    if (options.endpoint && !this.wsConnections.has(channel)) {
      this.createWebSocketConnection(channel, options.endpoint, options.reconnect);
    }

    return () => {
      this.subscribers.get(channel)?.delete(callback);
      if (this.subscribers.get(channel)?.size === 0) {
        this.closeWebSocketConnection(channel);
      }
    };
  }

  createWebSocketConnection(channel, endpoint, reconnect = true) {
    try {
      const ws = new WebSocket(`${this.wsUrl}${endpoint}`);
      
      ws.onopen = () => {
        console.log(`Agent WebSocket connected: ${channel}`);
        this.notifySubscribers(channel, { type: 'connected' });
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.notifySubscribers(channel, data);
          
          // Store communication history
          if (channel === 'agent-communications') {
            this.communicationHistory.push({
              ...data,
              timestamp: Date.now()
            });
            
            // Keep only last 1000 communications
            if (this.communicationHistory.length > 1000) {
              this.communicationHistory = this.communicationHistory.slice(-1000);
            }
          }
        } catch (error) {
          console.error(`Agent WebSocket message parse error (${channel}):`, error);
        }
      };

      ws.onclose = () => {
        console.log(`Agent WebSocket disconnected: ${channel}`);
        this.wsConnections.delete(channel);
        
        if (reconnect && this.isOnline) {
          setTimeout(() => {
            this.createWebSocketConnection(channel, endpoint, reconnect);
          }, 5000);
        }
      };

      ws.onerror = (error) => {
        console.error(`Agent WebSocket error (${channel}):`, error);
      };

      this.wsConnections.set(channel, ws);
    } catch (error) {
      console.error(`Failed to create agent WebSocket connection (${channel}):`, error);
    }
  }

  closeWebSocketConnection(channel) {
    const ws = this.wsConnections.get(channel);
    if (ws) {
      ws.close();
      this.wsConnections.delete(channel);
    }
  }

  notifySubscribers(channel, data) {
    const subscribers = this.subscribers.get(channel);
    if (subscribers) {
      subscribers.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Agent subscriber callback error (${channel}):`, error);
        }
      });
    }
  }

  reconnectAgentConnections() {
    this.wsConnections.forEach((ws, channel) => {
      if (ws.readyState === WebSocket.CLOSED) {
        this.createWebSocketConnection(channel, ws.url.replace(this.wsUrl, ''), true);
      }
    });
  }

  invalidateCache(keys = []) {
    if (keys.length === 0) {
      this.cache.clear();
    } else {
      keys.forEach(key => {
        Array.from(this.cache.keys())
          .filter(cacheKey => cacheKey.startsWith(key))
          .forEach(cacheKey => this.cache.delete(cacheKey));
      });
    }
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Cleanup and statistics
   */
  destroy() {
    this.wsConnections.forEach(ws => ws.close());
    this.wsConnections.clear();
    this.cache.clear();
    this.subscribers.clear();
    this.agentRegistry.clear();
    this.communicationHistory = [];
    
    console.log('AgentCommunicationService destroyed');
  }

  async healthCheck() {
    try {
      const response = await fetch(`${this.baseUrl}/api/agents/health`);
      return {
        status: response.ok ? 'healthy' : 'unhealthy',
        timestamp: new Date().toISOString(),
        agentCount: this.agentRegistry.size
      };
    } catch (error) {
      return {
        status: 'error',
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  getStatistics() {
    return {
      cacheSize: this.cache.size,
      activeSubscriptions: Array.from(this.subscribers.values()).reduce((sum, set) => sum + set.size, 0),
      activeWebSockets: this.wsConnections.size,
      agentRegistrySize: this.agentRegistry.size,
      communicationHistorySize: this.communicationHistory.length,
      isOnline: this.isOnline
    };
  }
}

// Create singleton instance
const agentCommunicationService = new AgentCommunicationService();

export default agentCommunicationService;
export { AgentCommunicationService };
