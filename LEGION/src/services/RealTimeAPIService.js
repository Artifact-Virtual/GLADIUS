/**
 * Real API Service for Live Dashboard Data
 * Connects to actual backend endpoints for real-time metrics
 */

class RealTimeAPIService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:5001';
    this.updateCallbacks = new Set();
    this.isPolling = false;
    this.pollingInterval = null;
    this.connectionStatus = 'disconnected';
    this.lastError = null;
    this.requestQueue = [];
    this.isProcessingQueue = false;
  }

  // Connection management
  async connect() {
    try {
      console.log('🔌 Connecting to backend API...');
      const response = await this.makeRequest('/api/enterprise/system-status', { timeout: 5000 });
      
      if (response && response.overall_health) {
        this.connectionStatus = 'connected';
        this.lastError = null;
        console.log('✅ Successfully connected to backend API');
        return true;
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      console.error('❌ Failed to connect to backend API:', error);
      this.connectionStatus = 'error';
      this.lastError = error.message;
      return false;
    }
  }

  // Generic API request with error handling and retry logic
  async makeRequest(endpoint, options = {}) {
    const { timeout = 10000, retries = 3, ...fetchOptions } = options;
    
    const url = `${this.baseURL}${endpoint}`;
    const requestOptions = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...fetchOptions.headers
      },
      ...fetchOptions
    };

    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        console.log(`🌐 API Request [${attempt}/${retries}]: ${endpoint}`);
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        
        const response = await fetch(url, {
          ...requestOptions,
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log(`✅ API Response: ${endpoint}`, data);
        return data;
        
      } catch (error) {
        console.warn(`⚠️ API Request failed [${attempt}/${retries}]:`, error.message);
        
        if (attempt === retries) {
          throw error;
        }
        
        // Exponential backoff
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
      }
    }
  }

  // System Status (Command Dashboard)
  async getSystemStatus() {
    try {
      const data = await this.makeRequest('/api/enterprise/system-status');
      return {
        status: 'success',
        data: {
          systemStatus: data.overall_health || 'unknown',
          timestamp: data.timestamp || new Date().toISOString(),
          services: data.services || {},
          performance: {
            cpu: data.performance?.cpu_usage || 0,
            memory: data.performance?.memory_usage || 0,
            disk: data.performance?.disk_usage || 0,
            network: data.performance?.network_throughput || '0 MB/s'
          },
          security: data.security || {},
          alerts: data.alerts || []
        }
      };
    } catch (error) {
      console.error('Failed to fetch system status:', error);
      return {
        status: 'error',
        error: error.message,
        data: this.getFallbackSystemStatus()
      };
    }
  }

  // Performance Metrics (Operations Dashboard)
  async getPerformanceMetrics() {
    try {
      const data = await this.makeRequest('/api/enterprise/performance-metrics');
      return {
        status: 'success',
        data: {
          timestamp: data.timestamp || new Date().toISOString(),
          system: data.system || {},
          database: data.database || {},
          api: data.api || {},
          agents: data.agents || {}
        }
      };
    } catch (error) {
      console.error('Failed to fetch performance metrics:', error);
      return {
        status: 'error',
        error: error.message,
        data: this.getFallbackPerformanceMetrics()
      };
    }
  }

  // Agent Health Data
  async getAgentHealth() {
    try {
      const data = await this.makeRequest('/api/enterprise/agent-health');
      return {
        status: 'success',
        data: {
          agents: Array.isArray(data) ? data : [],
          summary: this.calculateAgentSummary(data),
          timestamp: new Date().toISOString()
        }
      };
    } catch (error) {
      console.error('Failed to fetch agent health:', error);
      return {
        status: 'error',
        error: error.message,
        data: this.getFallbackAgentHealth()
      };
    }
  }

  // Agent Performance Data
  async getAgentPerformance() {
    try {
      const data = await this.makeRequest('/api/enterprise/agent-performance');
      return {
        status: 'success',
        data: {
          agents: Array.isArray(data) ? data : [],
          timestamp: new Date().toISOString()
        }
      };
    } catch (error) {
      console.error('Failed to fetch agent performance:', error);
      return {
        status: 'error',
        error: error.message,
        data: this.getFallbackAgentPerformance()
      };
    }
  }

  // Workflow Status
  async getWorkflowStatus() {
    try {
      const data = await this.makeRequest('/api/enterprise/workflow-status');
      return {
        status: 'success',
        data: {
          workflows: Array.isArray(data) ? data : [],
          timestamp: new Date().toISOString()
        }
      };
    } catch (error) {
      console.error('Failed to fetch workflow status:', error);
      return {
        status: 'error',
        error: error.message,
        data: this.getFallbackWorkflowStatus()
      };
    }
  }

  // Database Status
  async getDatabaseStatus() {
    try {
      const data = await this.makeRequest('/api/enterprise/database-status');
      return {
        status: 'success',
        data: data
      };
    } catch (error) {
      console.error('Failed to fetch database status:', error);
      return {
        status: 'error',
        error: error.message,
        data: this.getFallbackDatabaseStatus()
      };
    }
  }

  // Real-time polling
  startPolling(interval = 5000) {
    if (this.isPolling) {
      console.log('⏰ Polling already active');
      return;
    }

    console.log(`⏰ Starting real-time polling (${interval}ms interval)`);
    this.isPolling = true;
    
    this.pollingInterval = setInterval(async () => {
      try {
        // Fetch all data in parallel
        const [systemStatus, performance, agentHealth, agentPerformance, workflowStatus] = await Promise.allSettled([
          this.getSystemStatus(),
          this.getPerformanceMetrics(),
          this.getAgentHealth(),
          this.getAgentPerformance(),
          this.getWorkflowStatus()
        ]);

        // Notify all subscribers with fresh data
        const updateData = {
          systemStatus: systemStatus.value,
          performance: performance.value,
          agentHealth: agentHealth.value,
          agentPerformance: agentPerformance.value,
          workflowStatus: workflowStatus.value,
          timestamp: new Date().toISOString()
        };

        this.notifySubscribers(updateData);
        
      } catch (error) {
        console.error('⚠️ Polling error:', error);
      }
    }, interval);
  }

  stopPolling() {
    if (this.pollingInterval) {
      console.log('⏹️ Stopping real-time polling');
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
      this.isPolling = false;
    }
  }

  // Subscription management
  subscribe(callback) {
    this.updateCallbacks.add(callback);
    console.log(`📡 New subscriber added (${this.updateCallbacks.size} total)`);
    
    // Return unsubscribe function
    return () => {
      this.updateCallbacks.delete(callback);
      console.log(`📡 Subscriber removed (${this.updateCallbacks.size} total)`);
    };
  }

  notifySubscribers(data) {
    console.log(`📡 Notifying ${this.updateCallbacks.size} subscribers with fresh data`);
    this.updateCallbacks.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error('Subscriber callback error:', error);
      }
    });
  }

  // Helper methods for calculating summaries
  calculateAgentSummary(agents) {
    if (!Array.isArray(agents) || agents.length === 0) {
      return { totalAgents: 0, activeAgents: 0, healthyAgents: 0, averageHealth: 0 };
    }

    const totalAgents = agents.length;
    const activeAgents = agents.filter(agent => agent.status === 'operational').length;
    const healthyAgents = agents.filter(agent => agent.health_score >= 80).length;
    const averageHealth = agents.reduce((sum, agent) => sum + (agent.health_score || 0), 0) / totalAgents;

    return {
      totalAgents,
      activeAgents,
      healthyAgents,
      averageHealth: Math.round(averageHealth)
    };
  }

  // Fallback data methods
  getFallbackSystemStatus() {
    return {
      systemStatus: 'offline',
      timestamp: new Date().toISOString(),
      services: {
        database: { status: 'unknown', response_time: 'N/A' },
        legion_core: { status: 'unknown', uptime: 'N/A' },
        api_gateway: { status: 'unknown', requests_per_min: 0 },
        workflow_engine: { status: 'unknown', active_workflows: 0 },
        agent_mesh: { status: 'unknown', active_agents: 0 }
      },
      performance: { cpu: 0, memory: 0, disk: 0, network: '0 MB/s' },
      security: { threat_level: 'unknown', active_sessions: 0, failed_auth_attempts: 0 },
      alerts: [{
        id: 'connection-error',
        type: 'error',
        message: 'Unable to connect to backend services',
        timestamp: new Date().toISOString()
      }]
    };
  }

  getFallbackPerformanceMetrics() {
    return {
      timestamp: new Date().toISOString(),
      system: { cpu_usage: 0, memory_usage: 0, disk_usage: 0, network_io: { inbound_mbps: 0, outbound_mbps: 0 } },
      database: { connections: 0, queries_per_second: 0, avg_query_time: 'N/A', cache_hit_rate: '0%' },
      api: { requests_per_minute: 0, avg_response_time: 'N/A', error_rate: '0%', active_connections: 0 },
      agents: { active_count: 0, avg_task_completion_time: 'N/A', success_rate: '0%', queue_size: 0 }
    };
  }

  getFallbackAgentHealth() {
    return {
      agents: [],
      summary: { totalAgents: 0, activeAgents: 0, healthyAgents: 0, averageHealth: 0 },
      timestamp: new Date().toISOString()
    };
  }

  getFallbackAgentPerformance() {
    return {
      agents: [],
      timestamp: new Date().toISOString()
    };
  }

  getFallbackWorkflowStatus() {
    return {
      workflows: [],
      timestamp: new Date().toISOString()
    };
  }

  getFallbackDatabaseStatus() {
    return {
      status: 'unknown',
      connections: 0,
      timestamp: new Date().toISOString()
    };
  }

  // Get connection info for debugging
  getConnectionInfo() {
    return {
      baseURL: this.baseURL,
      status: this.connectionStatus,
      isPolling: this.isPolling,
      subscriberCount: this.updateCallbacks.size,
      lastError: this.lastError
    };
  }
}

// Create singleton instance
const realTimeAPI = new RealTimeAPIService();

export default realTimeAPI;
