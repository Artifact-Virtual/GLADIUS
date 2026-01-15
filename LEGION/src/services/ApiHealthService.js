// src/services/ApiHealthService.js
// LEGION Enterprise Dashboard - API Health Service
// Comprehensive external API health monitoring, performance tracking, and management service

/**
 * API Health Service
 * Provides comprehensive API health monitoring, performance tracking, and management
 * for external API integrations in the LEGION Enterprise Dashboard system
 */
class ApiHealthService {
  constructor() {
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
    this.cache = new Map();
    this.subscribers = new Map();
    this.wsConnections = new Map();
    this.apiRegistry = new Map();
    this.healthHistory = [];
    this.retryAttempts = 3;
    this.retryDelay = 1000;
    this.cacheTimeout = 45000; // 45 seconds for API health data
    this.healthCheckInterval = 60000; // 1 minute
    this.isOnline = navigator.onLine;
    
    // Initialize API health monitoring
    this.initializeApiHealthMonitoring();
    
    console.log('ApiHealthService initialized');
  }

  /**
   * Initialize API health monitoring and tracking
   */
  initializeApiHealthMonitoring() {
    // Start health check monitoring
    setInterval(() => {
      this.performHealthChecks();
    }, this.healthCheckInterval);

    // Initialize connection monitoring
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.reconnectApiConnections();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
    });
  }

  /**
   * API Discovery and Registration
   */
  async getRegisteredApis() {
    return this.fetchWithCache('registered-apis', '/api/external-apis/registry', {
      refresh: 120000, // 2 minutes
      priority: 'medium'
    });
  }

  async getApiDetails(apiId) {
    return this.fetchWithCache(`api-details-${apiId}`, `/api/external-apis/${apiId}`, {
      refresh: 300000, // 5 minutes
      priority: 'low'
    });
  }

  async getApisByCategory(category) {
    return this.fetchWithCache(`apis-category-${category}`, `/api/external-apis/category/${category}`, {
      refresh: 180000, // 3 minutes
      priority: 'medium'
    });
  }

  async registerApi(apiConfig) {
    const response = await this.makeRequest('/api/external-apis/register', {
      method: 'POST',
      body: JSON.stringify(apiConfig)
    });
    
    this.invalidateCache(['registered-apis']);
    
    return response;
  }

  /**
   * API Health Monitoring
   */
  async getApiHealth(apiId) {
    return this.fetchWithCache(`api-health-${apiId}`, `/api/external-apis/${apiId}/health`, {
      refresh: 30000, // 30 seconds
      priority: 'critical'
    });
  }

  async getAllApiHealth() {
    return this.fetchWithCache('all-api-health', '/api/external-apis/health/overview', {
      refresh: 45000, // 45 seconds
      priority: 'high'
    });
  }

  async getApiHealthHistory(apiId, timeRange = '24h') {
    return this.fetchWithCache(
      `api-health-history-${apiId}-${timeRange}`,
      `/api/external-apis/${apiId}/health/history?range=${timeRange}`,
      {
        refresh: 180000, // 3 minutes
        priority: 'medium'
      }
    );
  }

  async getHealthTrends(timeRange = '7d') {
    return this.fetchWithCache(
      `health-trends-${timeRange}`,
      `/api/external-apis/health/trends?range=${timeRange}`,
      {
        refresh: 300000, // 5 minutes
        priority: 'medium'
      }
    );
  }

  /**
   * API Performance Monitoring
   */
  async getApiPerformance(apiId, timeRange = '1h') {
    return this.fetchWithCache(
      `api-performance-${apiId}-${timeRange}`,
      `/api/external-apis/${apiId}/performance?range=${timeRange}`,
      {
        refresh: 60000, // 1 minute
        priority: 'high'
      }
    );
  }

  async getPerformanceMetrics(timeRange = '24h') {
    return this.fetchWithCache(
      `performance-metrics-${timeRange}`,
      `/api/external-apis/performance/metrics?range=${timeRange}`,
      {
        refresh: 120000, // 2 minutes
        priority: 'medium'
      }
    );
  }

  async getResponseTimeAnalysis(apiId, timeRange = '24h') {
    return this.fetchWithCache(
      `response-time-${apiId}-${timeRange}`,
      `/api/external-apis/${apiId}/response-time?range=${timeRange}`,
      {
        refresh: 180000, // 3 minutes
        priority: 'medium'
      }
    );
  }

  async getThroughputAnalysis(apiId, timeRange = '24h') {
    return this.fetchWithCache(
      `throughput-${apiId}-${timeRange}`,
      `/api/external-apis/${apiId}/throughput?range=${timeRange}`,
      {
        refresh: 180000, // 3 minutes
        priority: 'medium'
      }
    );
  }

  /**
   * API Availability and Uptime
   */
  async getApiUptime(apiId, timeRange = '30d') {
    return this.fetchWithCache(
      `api-uptime-${apiId}-${timeRange}`,
      `/api/external-apis/${apiId}/uptime?range=${timeRange}`,
      {
        refresh: 300000, // 5 minutes
        priority: 'medium'
      }
    );
  }

  async getAvailabilityReport(timeRange = '7d') {
    return this.fetchWithCache(
      `availability-report-${timeRange}`,
      `/api/external-apis/availability/report?range=${timeRange}`,
      {
        refresh: 600000, // 10 minutes
        priority: 'low'
      }
    );
  }

  async getDowntimeIncidents(apiId, timeRange = '30d') {
    return this.fetchWithCache(
      `downtime-incidents-${apiId}-${timeRange}`,
      `/api/external-apis/${apiId}/incidents?range=${timeRange}`,
      {
        refresh: 300000, // 5 minutes
        priority: 'medium'
      }
    );
  }

  /**
   * API Error Monitoring and Alerting
   */
  async getApiErrors(apiId, timeRange = '24h') {
    return this.fetchWithCache(
      `api-errors-${apiId}-${timeRange}`,
      `/api/external-apis/${apiId}/errors?range=${timeRange}`,
      {
        refresh: 120000, // 2 minutes
        priority: 'high'
      }
    );
  }

  async getErrorAnalysis(timeRange = '7d') {
    return this.fetchWithCache(
      `error-analysis-${timeRange}`,
      `/api/external-apis/errors/analysis?range=${timeRange}`,
      {
        refresh: 300000, // 5 minutes
        priority: 'medium'
      }
    );
  }

  async getErrorRateMetrics(apiId, timeRange = '24h') {
    return this.fetchWithCache(
      `error-rate-${apiId}-${timeRange}`,
      `/api/external-apis/${apiId}/error-rate?range=${timeRange}`,
      {
        refresh: 180000, // 3 minutes
        priority: 'medium'
      }
    );
  }

  async getApiAlerts() {
    return this.fetchWithCache('api-alerts', '/api/external-apis/alerts', {
      refresh: 60000, // 1 minute
      priority: 'high'
    });
  }

  /**
   * API Usage and Quota Management
   */
  async getApiUsage(apiId, timeRange = '30d') {
    return this.fetchWithCache(
      `api-usage-${apiId}-${timeRange}`,
      `/api/external-apis/${apiId}/usage?range=${timeRange}`,
      {
        refresh: 180000, // 3 minutes
        priority: 'medium'
      }
    );
  }

  async getQuotaStatus(apiId) {
    return this.fetchWithCache(`quota-status-${apiId}`, `/api/external-apis/${apiId}/quota`, {
      refresh: 300000, // 5 minutes
      priority: 'medium'
    });
  }

  async getAllQuotaStatus() {
    return this.fetchWithCache('all-quota-status', '/api/external-apis/quota/overview', {
      refresh: 300000, // 5 minutes
      priority: 'medium'
    });
  }

  async getCostAnalysis(timeRange = '30d') {
    return this.fetchWithCache(
      `cost-analysis-${timeRange}`,
      `/api/external-apis/cost/analysis?range=${timeRange}`,
      {
        refresh: 600000, // 10 minutes
        priority: 'low'
      }
    );
  }

  /**
   * API Load Balancing and Connection Management
   */
  async getLoadBalancerStatus() {
    return this.fetchWithCache('load-balancer-status', '/api/external-apis/load-balancer/status', {
      refresh: 60000, // 1 minute
      priority: 'high'
    });
  }

  async getConnectionPools() {
    return this.fetchWithCache('connection-pools', '/api/external-apis/connections/pools', {
      refresh: 120000, // 2 minutes
      priority: 'medium'
    });
  }

  async getConnectionMetrics(poolId, timeRange = '1h') {
    return this.fetchWithCache(
      `connection-metrics-${poolId}-${timeRange}`,
      `/api/external-apis/connections/${poolId}/metrics?range=${timeRange}`,
      {
        refresh: 90000, // 1.5 minutes
        priority: 'medium'
      }
    );
  }

  async updateLoadBalancerConfig(config) {
    const response = await this.makeRequest('/api/external-apis/load-balancer/config', {
      method: 'PUT',
      body: JSON.stringify(config)
    });
    
    this.invalidateCache(['load-balancer-status']);
    
    return response;
  }

  /**
   * API Testing and Validation
   */
  async testApiEndpoint(apiId, endpoint) {
    return this.makeRequest(`/api/external-apis/${apiId}/test`, {
      method: 'POST',
      body: JSON.stringify({ endpoint })
    });
  }

  async runHealthChecks(apiIds = []) {
    return this.makeRequest('/api/external-apis/health-check', {
      method: 'POST',
      body: JSON.stringify({ apiIds })
    });
  }

  async validateApiCredentials(apiId) {
    return this.makeRequest(`/api/external-apis/${apiId}/validate-credentials`, {
      method: 'POST'
    });
  }

  async getTestResults(testId) {
    return this.fetchWithCache(`test-results-${testId}`, `/api/external-apis/tests/${testId}/results`, {
      refresh: 30000, // 30 seconds
      priority: 'high'
    });
  }

  /**
   * API Configuration Management
   */
  async getApiConfiguration(apiId) {
    return this.fetchWithCache(`api-config-${apiId}`, `/api/external-apis/${apiId}/config`, {
      refresh: 600000, // 10 minutes
      priority: 'low'
    });
  }

  async updateApiConfiguration(apiId, config) {
    const response = await this.makeRequest(`/api/external-apis/${apiId}/config`, {
      method: 'PUT',
      body: JSON.stringify(config)
    });
    
    this.invalidateCache([`api-config-${apiId}`, `api-details-${apiId}`]);
    
    return response;
  }

  async getConfigurationTemplates() {
    return this.fetchWithCache('config-templates', '/api/external-apis/config/templates', {
      refresh: 900000, // 15 minutes
      priority: 'low'
    });
  }

  /**
   * Real-time API Monitoring Subscriptions
   */
  subscribeToApiHealth(callback) {
    return this.subscribe('api-health', callback, {
      endpoint: '/ws/external-apis/health',
      reconnect: true
    });
  }

  subscribeToPerformanceMetrics(callback) {
    return this.subscribe('performance-metrics', callback, {
      endpoint: '/ws/external-apis/performance',
      reconnect: true
    });
  }

  subscribeToApiAlerts(callback) {
    return this.subscribe('api-alerts', callback, {
      endpoint: '/ws/external-apis/alerts',
      reconnect: true
    });
  }

  subscribeToUsageMetrics(callback) {
    return this.subscribe('usage-metrics', callback, {
      endpoint: '/ws/external-apis/usage',
      reconnect: true
    });
  }

  subscribeToConnectionStatus(callback) {
    return this.subscribe('connection-status', callback, {
      endpoint: '/ws/external-apis/connections',
      reconnect: true
    });
  }

  /**
   * API Analytics and Reporting
   */
  async getApiAnalytics(timeRange = '30d') {
    return this.fetchWithCache(
      `api-analytics-${timeRange}`,
      `/api/external-apis/analytics?range=${timeRange}`,
      {
        refresh: 300000, // 5 minutes
        priority: 'medium'
      }
    );
  }

  async getUsagePatterns(apiId, timeRange = '7d') {
    return this.fetchWithCache(
      `usage-patterns-${apiId}-${timeRange}`,
      `/api/external-apis/${apiId}/usage/patterns?range=${timeRange}`,
      {
        refresh: 600000, // 10 minutes
        priority: 'low'
      }
    );
  }

  async generateApiReport(reportType, parameters = {}) {
    return this.makeRequest('/api/external-apis/reports/generate', {
      method: 'POST',
      body: JSON.stringify({
        type: reportType,
        parameters
      })
    });
  }

  async exportApiData(format = 'csv', filters = {}) {
    const queryParams = new URLSearchParams({
      format,
      ...filters
    });

    return this.makeRequest(`/api/external-apis/export?${queryParams}`, {
      responseType: 'blob'
    });
  }

  /**
   * Centralized Health Check Execution
   */
  async performHealthChecks() {
    try {
      const apis = await this.getRegisteredApis();
      const healthPromises = apis.map(api => 
        this.getApiHealth(api.id).catch(error => ({
          apiId: api.id,
          status: 'error',
          error: error.message,
          timestamp: Date.now()
        }))
      );

      const healthResults = await Promise.all(healthPromises);
      
      // Update API registry
      healthResults.forEach(result => {
        if (result.apiId) {
          this.apiRegistry.set(result.apiId, {
            ...this.apiRegistry.get(result.apiId),
            lastHealthCheck: Date.now(),
            health: result
          });
        }
      });

      // Store health history
      this.healthHistory.push({
        timestamp: Date.now(),
        results: healthResults
      });

      // Keep only last 100 health check results
      if (this.healthHistory.length > 100) {
        this.healthHistory = this.healthHistory.slice(-100);
      }

      // Notify subscribers of health updates
      this.notifySubscribers('health-check-complete', healthResults);

      return healthResults;
    } catch (error) {
      console.error('API health checks failed:', error);
      return [];
    }
  }

  /**
   * Core Service Methods
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
        console.log(`API Health WebSocket connected: ${channel}`);
        this.notifySubscribers(channel, { type: 'connected' });
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.notifySubscribers(channel, data);
        } catch (error) {
          console.error(`API Health WebSocket message parse error (${channel}):`, error);
        }
      };

      ws.onclose = () => {
        console.log(`API Health WebSocket disconnected: ${channel}`);
        this.wsConnections.delete(channel);
        
        if (reconnect && this.isOnline) {
          setTimeout(() => {
            this.createWebSocketConnection(channel, endpoint, reconnect);
          }, 5000);
        }
      };

      ws.onerror = (error) => {
        console.error(`API Health WebSocket error (${channel}):`, error);
      };

      this.wsConnections.set(channel, ws);
    } catch (error) {
      console.error(`Failed to create API Health WebSocket connection (${channel}):`, error);
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
          console.error(`API Health subscriber callback error (${channel}):`, error);
        }
      });
    }
  }

  reconnectApiConnections() {
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
    this.apiRegistry.clear();
    this.healthHistory = [];
    
    console.log('ApiHealthService destroyed');
  }

  async healthCheck() {
    try {
      const response = await fetch(`${this.baseUrl}/api/external-apis/health`);
      return {
        status: response.ok ? 'healthy' : 'unhealthy',
        timestamp: new Date().toISOString(),
        apiCount: this.apiRegistry.size
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
      apiRegistrySize: this.apiRegistry.size,
      healthHistorySize: this.healthHistory.length,
      isOnline: this.isOnline
    };
  }
}

// Create singleton instance
const apiHealthService = new ApiHealthService();

export default apiHealthService;
export { ApiHealthService };
