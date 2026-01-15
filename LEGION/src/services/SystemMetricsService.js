// src/services/SystemMetricsService.js
// LEGION Enterprise Dashboard - System Metrics Service
// Comprehensive system performance monitoring, metrics collection, and analytics service

/**
 * System Metrics Service
 * Provides comprehensive system performance monitoring, metrics collection, and analytics
 * for the LEGION Enterprise Dashboard system
 */
class SystemMetricsService {
  constructor() {
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
    this.cache = new Map();
    this.subscribers = new Map();
    this.wsConnections = new Map();
    this.metricsBuffer = [];
    this.performanceBaseline = new Map();
    this.retryAttempts = 3;
    this.retryDelay = 1000;
    this.cacheTimeout = 30000; // 30 seconds for metrics data
    this.metricsInterval = 15000; // 15 seconds
    this.isOnline = navigator.onLine;
    
    // Initialize metrics collection
    this.initializeMetricsCollection();
    
    console.log('SystemMetricsService initialized');
  }

  /**
   * Initialize system metrics collection and monitoring
   */
  initializeMetricsCollection() {
    // Start metrics collection
    setInterval(() => {
      this.collectSystemMetrics();
    }, this.metricsInterval);

    // Initialize performance monitoring
    if (typeof window !== 'undefined' && window.performance) {
      this.initializePerformanceObserver();
    }

    // Initialize connection monitoring
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.reconnectMetricsConnections();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
    });
  }

  /**
   * Initialize performance observer for browser metrics
   */
  initializePerformanceObserver() {
    if (typeof PerformanceObserver !== 'undefined') {
      // Observe navigation timing
      const navigationObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach(entry => {
          this.recordClientMetric('navigation', {
            loadTime: entry.loadEventEnd - entry.navigationStart,
            domContentLoaded: entry.domContentLoadedEventEnd - entry.navigationStart,
            firstByte: entry.responseStart - entry.navigationStart,
            timestamp: Date.now()
          });
        });
      });
      navigationObserver.observe({ entryTypes: ['navigation'] });

      // Observe resource timing
      const resourceObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach(entry => {
          if (entry.name.includes('api') || entry.name.includes('ws')) {
            this.recordClientMetric('api_call', {
              url: entry.name,
              duration: entry.duration,
              size: entry.transferSize,
              timestamp: Date.now()
            });
          }
        });
      });
      resourceObserver.observe({ entryTypes: ['resource'] });
    }
  }

  /**
   * System Health Metrics
   */
  async getSystemHealth() {
    return this.fetchWithCache('system-health', '/api/metrics/system/health', {
      refresh: 10000, // 10 seconds
      priority: 'critical'
    });
  }

  async getSystemStatus() {
    return this.fetchWithCache('system-status', '/api/metrics/system/status', {
      refresh: 15000, // 15 seconds
      priority: 'critical'
    });
  }

  async getSystemUptime() {
    return this.fetchWithCache('system-uptime', '/api/metrics/system/uptime', {
      refresh: 60000, // 1 minute
      priority: 'high'
    });
  }

  async getSystemLoad() {
    return this.fetchWithCache('system-load', '/api/metrics/system/load', {
      refresh: 30000, // 30 seconds
      priority: 'high'
    });
  }

  /**
   * Performance Metrics
   */
  async getCPUMetrics(timeRange = '1h') {
    return this.fetchWithCache(
      `cpu-metrics-${timeRange}`,
      `/api/metrics/cpu?range=${timeRange}`,
      {
        refresh: 30000, // 30 seconds
        priority: 'high'
      }
    );
  }

  async getMemoryMetrics(timeRange = '1h') {
    return this.fetchWithCache(
      `memory-metrics-${timeRange}`,
      `/api/metrics/memory?range=${timeRange}`,
      {
        refresh: 30000, // 30 seconds
        priority: 'high'
      }
    );
  }

  async getDiskMetrics(timeRange = '1h') {
    return this.fetchWithCache(
      `disk-metrics-${timeRange}`,
      `/api/metrics/disk?range=${timeRange}`,
      {
        refresh: 60000, // 1 minute
        priority: 'medium'
      }
    );
  }

  async getNetworkMetrics(timeRange = '1h') {
    return this.fetchWithCache(
      `network-metrics-${timeRange}`,
      `/api/metrics/network?range=${timeRange}`,
      {
        refresh: 30000, // 30 seconds
        priority: 'high'
      }
    );
  }

  /**
   * Application Performance Metrics
   */
  async getApplicationMetrics(timeRange = '1h') {
    return this.fetchWithCache(
      `application-metrics-${timeRange}`,
      `/api/metrics/application?range=${timeRange}`,
      {
        refresh: 45000, // 45 seconds
        priority: 'high'
      }
    );
  }

  async getDatabaseMetrics(timeRange = '1h') {
    return this.fetchWithCache(
      `database-metrics-${timeRange}`,
      `/api/metrics/database?range=${timeRange}`,
      {
        refresh: 60000, // 1 minute
        priority: 'medium'
      }
    );
  }

  async getAPIMetrics(timeRange = '1h') {
    return this.fetchWithCache(
      `api-metrics-${timeRange}`,
      `/api/metrics/api?range=${timeRange}`,
      {
        refresh: 30000, // 30 seconds
        priority: 'high'
      }
    );
  }

  async getWebSocketMetrics(timeRange = '1h') {
    return this.fetchWithCache(
      `websocket-metrics-${timeRange}`,
      `/api/metrics/websocket?range=${timeRange}`,
      {
        refresh: 45000, // 45 seconds
        priority: 'medium'
      }
    );
  }

  /**
   * Resource Utilization Metrics
   */
  async getResourceUtilization() {
    return this.fetchWithCache('resource-utilization', '/api/metrics/resources/utilization', {
      refresh: 30000, // 30 seconds
      priority: 'high'
    });
  }

  async getResourceHistory(resource, timeRange = '24h') {
    return this.fetchWithCache(
      `resource-history-${resource}-${timeRange}`,
      `/api/metrics/resources/${resource}/history?range=${timeRange}`,
      {
        refresh: 120000, // 2 minutes
        priority: 'medium'
      }
    );
  }

  async getResourceThresholds() {
    return this.fetchWithCache('resource-thresholds', '/api/metrics/resources/thresholds', {
      refresh: 300000, // 5 minutes
      priority: 'low'
    });
  }

  async updateResourceThreshold(resource, threshold) {
    const response = await this.makeRequest(`/api/metrics/resources/${resource}/threshold`, {
      method: 'PUT',
      body: JSON.stringify(threshold)
    });
    
    this.invalidateCache(['resource-thresholds']);
    
    return response;
  }

  /**
   * Performance Analytics and Trends
   */
  async getPerformanceTrends(metric, timeRange = '7d') {
    return this.fetchWithCache(
      `performance-trends-${metric}-${timeRange}`,
      `/api/metrics/performance/trends?metric=${metric}&range=${timeRange}`,
      {
        refresh: 300000, // 5 minutes
        priority: 'medium'
      }
    );
  }

  async getPerformanceBaseline() {
    return this.fetchWithCache('performance-baseline', '/api/metrics/performance/baseline', {
      refresh: 600000, // 10 minutes
      priority: 'low'
    });
  }

  async getPerformanceAnomalies(timeRange = '24h') {
    return this.fetchWithCache(
      `performance-anomalies-${timeRange}`,
      `/api/metrics/performance/anomalies?range=${timeRange}`,
      {
        refresh: 180000, // 3 minutes
        priority: 'medium'
      }
    );
  }

  async getBottleneckAnalysis() {
    return this.fetchWithCache('bottleneck-analysis', '/api/metrics/performance/bottlenecks', {
      refresh: 300000, // 5 minutes
      priority: 'medium'
    });
  }

  /**
   * Custom Metrics and KPIs
   */
  async getCustomMetrics() {
    return this.fetchWithCache('custom-metrics', '/api/metrics/custom', {
      refresh: 120000, // 2 minutes
      priority: 'medium'
    });
  }

  async createCustomMetric(metricData) {
    const response = await this.makeRequest('/api/metrics/custom', {
      method: 'POST',
      body: JSON.stringify(metricData)
    });
    
    this.invalidateCache(['custom-metrics']);
    
    return response;
  }

  async recordCustomMetric(metricId, value, tags = {}) {
    return this.makeRequest(`/api/metrics/custom/${metricId}/record`, {
      method: 'POST',
      body: JSON.stringify({ value, tags, timestamp: Date.now() })
    });
  }

  async getKPIDashboard() {
    return this.fetchWithCache('kpi-dashboard', '/api/metrics/kpi/dashboard', {
      refresh: 60000, // 1 minute
      priority: 'high'
    });
  }

  /**
   * Agent Performance Metrics
   */
  async getAgentPerformanceMetrics(timeRange = '1h') {
    return this.fetchWithCache(
      `agent-performance-metrics-${timeRange}`,
      `/api/metrics/agents/performance?range=${timeRange}`,
      {
        refresh: 60000, // 1 minute
        priority: 'medium'
      }
    );
  }

  async getAgentResourceUsage(agentId, timeRange = '1h') {
    return this.fetchWithCache(
      `agent-resource-usage-${agentId}-${timeRange}`,
      `/api/metrics/agents/${agentId}/resources?range=${timeRange}`,
      {
        refresh: 90000, // 1.5 minutes
        priority: 'medium'
      }
    );
  }

  async getAgentEfficiencyMetrics() {
    return this.fetchWithCache('agent-efficiency-metrics', '/api/metrics/agents/efficiency', {
      refresh: 180000, // 3 minutes
      priority: 'medium'
    });
  }

  /**
   * Business Metrics and Analytics
   */
  async getBusinessMetrics(timeRange = '24h') {
    return this.fetchWithCache(
      `business-metrics-${timeRange}`,
      `/api/metrics/business?range=${timeRange}`,
      {
        refresh: 300000, // 5 minutes
        priority: 'medium'
      }
    );
  }

  async getRevenueMetrics(timeRange = '30d') {
    return this.fetchWithCache(
      `revenue-metrics-${timeRange}`,
      `/api/metrics/revenue?range=${timeRange}`,
      {
        refresh: 600000, // 10 minutes
        priority: 'low'
      }
    );
  }

  async getOperationalMetrics(timeRange = '24h') {
    return this.fetchWithCache(
      `operational-metrics-${timeRange}`,
      `/api/metrics/operational?range=${timeRange}`,
      {
        refresh: 180000, // 3 minutes
        priority: 'medium'
      }
    );
  }

  /**
   * Real-time Metrics Subscriptions
   */
  subscribeToSystemHealth(callback) {
    return this.subscribe('system-health', callback, {
      endpoint: '/ws/metrics/system/health',
      reconnect: true
    });
  }

  subscribeToPerformanceMetrics(callback) {
    return this.subscribe('performance-metrics', callback, {
      endpoint: '/ws/metrics/performance',
      reconnect: true
    });
  }

  subscribeToResourceUsage(callback) {
    return this.subscribe('resource-usage', callback, {
      endpoint: '/ws/metrics/resources',
      reconnect: true
    });
  }

  subscribeToAgentMetrics(callback) {
    return this.subscribe('agent-metrics', callback, {
      endpoint: '/ws/metrics/agents',
      reconnect: true
    });
  }

  subscribeToBusinessMetrics(callback) {
    return this.subscribe('business-metrics', callback, {
      endpoint: '/ws/metrics/business',
      reconnect: true
    });
  }

  /**
   * Alerts and Notifications
   */
  async getMetricAlerts() {
    return this.fetchWithCache('metric-alerts', '/api/metrics/alerts', {
      refresh: 60000, // 1 minute
      priority: 'high'
    });
  }

  async createAlert(alertConfig) {
    const response = await this.makeRequest('/api/metrics/alerts', {
      method: 'POST',
      body: JSON.stringify(alertConfig)
    });
    
    this.invalidateCache(['metric-alerts']);
    
    return response;
  }

  async updateAlert(alertId, alertConfig) {
    const response = await this.makeRequest(`/api/metrics/alerts/${alertId}`, {
      method: 'PUT',
      body: JSON.stringify(alertConfig)
    });
    
    this.invalidateCache(['metric-alerts']);
    
    return response;
  }

  async deleteAlert(alertId) {
    const response = await this.makeRequest(`/api/metrics/alerts/${alertId}`, {
      method: 'DELETE'
    });
    
    this.invalidateCache(['metric-alerts']);
    
    return response;
  }

  /**
   * Client-side Metrics Collection
   */
  recordClientMetric(type, data) {
    const metric = {
      type,
      data,
      timestamp: Date.now(),
      sessionId: this.getSessionId(),
      userAgent: navigator.userAgent
    };

    this.metricsBuffer.push(metric);

    // Flush buffer when it gets too large
    if (this.metricsBuffer.length >= 50) {
      this.flushMetricsBuffer();
    }
  }

  async flushMetricsBuffer() {
    if (this.metricsBuffer.length === 0) return;

    try {
      await this.makeRequest('/api/metrics/client/batch', {
        method: 'POST',
        body: JSON.stringify({
          metrics: this.metricsBuffer,
          timestamp: Date.now()
        })
      });

      this.metricsBuffer = [];
    } catch (error) {
      console.warn('Failed to flush metrics buffer:', error);
      // Keep buffer for retry
      if (this.metricsBuffer.length > 200) {
        this.metricsBuffer = this.metricsBuffer.slice(-100);
      }
    }
  }

  getSessionId() {
    let sessionId = sessionStorage.getItem('metrics_session_id');
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('metrics_session_id', sessionId);
    }
    return sessionId;
  }

  /**
   * System Metrics Collection
   */
  async collectSystemMetrics() {
    try {
      // Collect browser performance metrics
      if (typeof window !== 'undefined' && window.performance) {
        const memory = window.performance.memory;
        if (memory) {
          this.recordClientMetric('memory', {
            used: memory.usedJSHeapSize,
            total: memory.totalJSHeapSize,
            limit: memory.jsHeapSizeLimit
          });
        }

        // Record navigation timing
        const navigation = window.performance.getEntriesByType('navigation')[0];
        if (navigation) {
          this.recordClientMetric('page_load', {
            loadTime: navigation.loadEventEnd - navigation.loadEventStart,
            domReady: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
            responseTime: navigation.responseEnd - navigation.requestStart
          });
        }
      }

      // Collect connection metrics
      if (navigator.connection) {
        this.recordClientMetric('connection', {
          effectiveType: navigator.connection.effectiveType,
          downlink: navigator.connection.downlink,
          rtt: navigator.connection.rtt
        });
      }

    } catch (error) {
      console.warn('Failed to collect system metrics:', error);
    }
  }

  /**
   * Metrics Export and Reporting
   */
  async exportMetrics(filters = {}, format = 'csv') {
    const queryParams = new URLSearchParams({
      format,
      ...filters
    });

    return this.makeRequest(`/api/metrics/export?${queryParams}`, {
      responseType: 'blob'
    });
  }

  async generateMetricsReport(reportType, parameters = {}) {
    return this.makeRequest('/api/metrics/reports/generate', {
      method: 'POST',
      body: JSON.stringify({
        type: reportType,
        parameters
      })
    });
  }

  async getReportStatus(reportId) {
    return this.fetchWithCache(`report-status-${reportId}`, `/api/metrics/reports/${reportId}/status`, {
      refresh: 5000, // 5 seconds
      priority: 'high'
    });
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
        console.log(`Metrics WebSocket connected: ${channel}`);
        this.notifySubscribers(channel, { type: 'connected' });
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.notifySubscribers(channel, data);
        } catch (error) {
          console.error(`Metrics WebSocket message parse error (${channel}):`, error);
        }
      };

      ws.onclose = () => {
        console.log(`Metrics WebSocket disconnected: ${channel}`);
        this.wsConnections.delete(channel);
        
        if (reconnect && this.isOnline) {
          setTimeout(() => {
            this.createWebSocketConnection(channel, endpoint, reconnect);
          }, 5000);
        }
      };

      ws.onerror = (error) => {
        console.error(`Metrics WebSocket error (${channel}):`, error);
      };

      this.wsConnections.set(channel, ws);
    } catch (error) {
      console.error(`Failed to create metrics WebSocket connection (${channel}):`, error);
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
          console.error(`Metrics subscriber callback error (${channel}):`, error);
        }
      });
    }
  }

  reconnectMetricsConnections() {
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
    // Flush any remaining metrics
    this.flushMetricsBuffer();
    
    this.wsConnections.forEach(ws => ws.close());
    this.wsConnections.clear();
    this.cache.clear();
    this.subscribers.clear();
    this.performanceBaseline.clear();
    this.metricsBuffer = [];
    
    console.log('SystemMetricsService destroyed');
  }

  async healthCheck() {
    try {
      const response = await fetch(`${this.baseUrl}/api/metrics/health`);
      return {
        status: response.ok ? 'healthy' : 'unhealthy',
        timestamp: new Date().toISOString(),
        metricsBufferSize: this.metricsBuffer.length
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
      metricsBufferSize: this.metricsBuffer.length,
      performanceBaselineSize: this.performanceBaseline.size,
      isOnline: this.isOnline
    };
  }
}

// Create singleton instance
const systemMetricsService = new SystemMetricsService();

export default systemMetricsService;
export { SystemMetricsService };
