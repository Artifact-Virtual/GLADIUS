// src/services/EnterpriseDataService.js
// LEGION Enterprise Dashboard - Enterprise Data Service
// Comprehensive business data management and analytics service

/**
 * Enterprise Data Service
 * Provides comprehensive business data management, analytics, and real-time monitoring
 * for the LEGION Enterprise Dashboard system
 */
class EnterpriseDataService {
  constructor() {
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
    this.cache = new Map();
    this.subscribers = new Map();
    this.wsConnections = new Map();
    this.retryAttempts = 3;
    this.retryDelay = 1000;
    this.cacheTimeout = 300000; // 5 minutes
    this.isOnline = navigator.onLine;
    
    // Initialize connection monitoring
    this.initializeConnectionMonitoring();
    
    // Initialize data refresh intervals
    this.refreshIntervals = new Map();
    
    console.log('EnterpriseDataService initialized');
  }

  /**
   * Initialize connection monitoring and offline handling
   */
  initializeConnectionMonitoring() {
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.reconnectWebSockets();
      this.notifySubscribers('connection', { status: 'online' });
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      this.notifySubscribers('connection', { status: 'offline' });
    });
  }

  /**
   * Business Operations Data
   */
  async getBusinessObjectives() {
    return this.fetchWithCache('business-objectives', '/api/enterprise/business-objectives', {
      refresh: 30000, // 30 seconds
      priority: 'high'
    });
  }

  async updateBusinessObjective(objectiveId, data) {
    const response = await this.makeRequest(`/api/enterprise/business-objectives/${objectiveId}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
    
    // Invalidate related cache
    this.invalidateCache(['business-objectives', 'department-activities']);
    
    return response;
  }

  /**
   * Revenue and Financial Data
   */
  async getRevenueMetrics(timeRange = '30d') {
    return this.fetchWithCache(`revenue-metrics-${timeRange}`, `/api/enterprise/revenue-metrics?range=${timeRange}`, {
      refresh: 60000, // 1 minute
      priority: 'high'
    });
  }

  async getFinancialForecasts() {
    return this.fetchWithCache('financial-forecasts', '/api/enterprise/financial-forecasts', {
      refresh: 300000, // 5 minutes
      priority: 'medium'
    });
  }

  async getRevenueBreakdown(type = 'product') {
    return this.fetchWithCache(`revenue-breakdown-${type}`, `/api/enterprise/revenue-breakdown?type=${type}`, {
      refresh: 120000, // 2 minutes
      priority: 'medium'
    });
  }

  /**
   * Department and Team Data
   */
  async getDepartmentActivities() {
    return this.fetchWithCache('department-activities', '/api/enterprise/department-activities', {
      refresh: 45000, // 45 seconds
      priority: 'high'
    });
  }

  async getDepartmentMetrics(departmentId) {
    return this.fetchWithCache(`department-metrics-${departmentId}`, `/api/enterprise/departments/${departmentId}/metrics`, {
      refresh: 60000, // 1 minute
      priority: 'medium'
    });
  }

  async getTeamPerformance(teamId) {
    return this.fetchWithCache(`team-performance-${teamId}`, `/api/enterprise/teams/${teamId}/performance`, {
      refresh: 90000, // 1.5 minutes
      priority: 'medium'
    });
  }

  /**
   * Project and Workflow Data
   */
  async getProjectStatuses() {
    return this.fetchWithCache('project-statuses', '/api/enterprise/projects', {
      refresh: 60000, // 1 minute
      priority: 'high'
    });
  }

  async getProjectTimeline(projectId) {
    return this.fetchWithCache(`project-timeline-${projectId}`, `/api/enterprise/projects/${projectId}/timeline`, {
      refresh: 120000, // 2 minutes
      priority: 'medium'
    });
  }

  async getWorkflowExecutions(status = 'all') {
    return this.fetchWithCache(`workflow-executions-${status}`, `/api/enterprise/workflows/executions?status=${status}`, {
      refresh: 30000, // 30 seconds
      priority: 'high'
    });
  }

  /**
   * Lead and Sales Data
   */
  async getLeadPipeline() {
    return this.fetchWithCache('lead-pipeline', '/api/enterprise/leads/pipeline', {
      refresh: 60000, // 1 minute
      priority: 'high'
    });
  }

  async getLeadMetrics(timeRange = '30d') {
    return this.fetchWithCache(`lead-metrics-${timeRange}`, `/api/enterprise/leads/metrics?range=${timeRange}`, {
      refresh: 120000, // 2 minutes
      priority: 'medium'
    });
  }

  async getSalesForecasts() {
    return this.fetchWithCache('sales-forecasts', '/api/enterprise/sales/forecasts', {
      refresh: 300000, // 5 minutes
      priority: 'medium'
    });
  }

  /**
   * Business Intelligence and Analytics
   */
  async getBusinessInsights(category = 'all') {
    return this.fetchWithCache(`business-insights-${category}`, `/api/enterprise/insights?category=${category}`, {
      refresh: 180000, // 3 minutes
      priority: 'medium'
    });
  }

  async getMarketAnalysis() {
    return this.fetchWithCache('market-analysis', '/api/enterprise/market-analysis', {
      refresh: 600000, // 10 minutes
      priority: 'low'
    });
  }

  async getCompetitiveIntelligence() {
    return this.fetchWithCache('competitive-intelligence', '/api/enterprise/competitive-intelligence', {
      refresh: 900000, // 15 minutes
      priority: 'low'
    });
  }

  /**
   * System Health and Performance Data
   */
  async getSystemHealth() {
    return this.fetchWithCache('system-health', '/api/enterprise/system/health', {
      refresh: 15000, // 15 seconds
      priority: 'critical'
    });
  }

  async getPerformanceMetrics(timeRange = '1h') {
    return this.fetchWithCache(`performance-metrics-${timeRange}`, `/api/enterprise/system/performance?range=${timeRange}`, {
      refresh: 30000, // 30 seconds
      priority: 'high'
    });
  }

  async getResourceUtilization() {
    return this.fetchWithCache('resource-utilization', '/api/enterprise/system/resources', {
      refresh: 60000, // 1 minute
      priority: 'medium'
    });
  }

  /**
   * Configuration and Settings Data
   */
  async getSystemConfiguration() {
    return this.fetchWithCache('system-configuration', '/api/enterprise/configuration', {
      refresh: 600000, // 10 minutes
      priority: 'low'
    });
  }

  async updateConfiguration(section, data) {
    const response = await this.makeRequest(`/api/enterprise/configuration/${section}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
    
    // Invalidate configuration cache
    this.invalidateCache(['system-configuration']);
    
    return response;
  }

  /**
   * Real-time Data Subscriptions
   */
  subscribeToBusinessMetrics(callback) {
    return this.subscribe('business-metrics', callback, {
      endpoint: '/ws/enterprise/business-metrics',
      reconnect: true
    });
  }

  subscribeToSystemHealth(callback) {
    return this.subscribe('system-health', callback, {
      endpoint: '/ws/enterprise/system-health',
      reconnect: true
    });
  }

  subscribeToRevenueUpdates(callback) {
    return this.subscribe('revenue-updates', callback, {
      endpoint: '/ws/enterprise/revenue',
      reconnect: true
    });
  }

  subscribeToProjectUpdates(callback) {
    return this.subscribe('project-updates', callback, {
      endpoint: '/ws/enterprise/projects',
      reconnect: true
    });
  }

  /**
   * Data Export and Reporting
   */
  async exportBusinessData(format = 'xlsx', filters = {}) {
    const queryParams = new URLSearchParams({
      format,
      ...filters
    });

    const response = await this.makeRequest(`/api/enterprise/export?${queryParams}`, {
      responseType: 'blob'
    });

    return response;
  }

  async generateReport(reportType, parameters = {}) {
    return this.makeRequest('/api/enterprise/reports/generate', {
      method: 'POST',
      body: JSON.stringify({
        type: reportType,
        parameters
      })
    });
  }

  async getReportStatus(reportId) {
    return this.fetchWithCache(`report-status-${reportId}`, `/api/enterprise/reports/${reportId}/status`, {
      refresh: 5000, // 5 seconds
      priority: 'high'
    });
  }

  /**
   * Data Analytics and Aggregation
   */
  async getBusinessAnalytics(metric, timeRange = '30d', granularity = 'day') {
    return this.fetchWithCache(
      `analytics-${metric}-${timeRange}-${granularity}`,
      `/api/enterprise/analytics/${metric}?range=${timeRange}&granularity=${granularity}`,
      {
        refresh: 120000, // 2 minutes
        priority: 'medium'
      }
    );
  }

  async getKPIDashboard() {
    return this.fetchWithCache('kpi-dashboard', '/api/enterprise/kpi/dashboard', {
      refresh: 60000, // 1 minute
      priority: 'high'
    });
  }

  async getTrendAnalysis(metrics, timeRange = '90d') {
    return this.fetchWithCache(
      `trend-analysis-${metrics.join(',')}-${timeRange}`,
      `/api/enterprise/analytics/trends`,
      {
        method: 'POST',
        body: JSON.stringify({ metrics, timeRange }),
        refresh: 300000, // 5 minutes
        priority: 'medium'
      }
    );
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

      // Set up auto-refresh if specified
      if (options.refresh && !this.refreshIntervals.has(cacheKey)) {
        const interval = setInterval(async () => {
          try {
            const freshData = await this.makeRequest(url, options);
            this.cache.set(cacheKey, {
              data: freshData,
              timestamp: Date.now()
            });
            this.notifySubscribers(key, freshData);
          } catch (error) {
            console.warn(`Auto-refresh failed for ${key}:`, error);
          }
        }, options.refresh);
        
        this.refreshIntervals.set(cacheKey, interval);
      }

      return data;
    } catch (error) {
      // Return cached data if available during error
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
    // Add to subscribers
    if (!this.subscribers.has(channel)) {
      this.subscribers.set(channel, new Set());
    }
    this.subscribers.get(channel).add(callback);

    // Create WebSocket connection if needed
    if (options.endpoint && !this.wsConnections.has(channel)) {
      this.createWebSocketConnection(channel, options.endpoint, options.reconnect);
    }

    // Return unsubscribe function
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
        console.log(`WebSocket connected: ${channel}`);
        this.notifySubscribers(channel, { type: 'connected' });
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.notifySubscribers(channel, data);
        } catch (error) {
          console.error(`WebSocket message parse error (${channel}):`, error);
        }
      };

      ws.onclose = () => {
        console.log(`WebSocket disconnected: ${channel}`);
        this.wsConnections.delete(channel);
        
        if (reconnect && this.isOnline) {
          setTimeout(() => {
            this.createWebSocketConnection(channel, endpoint, reconnect);
          }, 5000);
        }
      };

      ws.onerror = (error) => {
        console.error(`WebSocket error (${channel}):`, error);
      };

      this.wsConnections.set(channel, ws);
    } catch (error) {
      console.error(`Failed to create WebSocket connection (${channel}):`, error);
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
          console.error(`Subscriber callback error (${channel}):`, error);
        }
      });
    }
  }

  reconnectWebSockets() {
    // Reconnect all WebSocket connections when coming back online
    this.wsConnections.forEach((ws, channel) => {
      if (ws.readyState === WebSocket.CLOSED) {
        this.createWebSocketConnection(channel, ws.url.replace(this.wsUrl, ''), true);
      }
    });
  }

  invalidateCache(keys = []) {
    if (keys.length === 0) {
      this.cache.clear();
      this.refreshIntervals.forEach(interval => clearInterval(interval));
      this.refreshIntervals.clear();
    } else {
      keys.forEach(key => {
        // Remove all cache entries that start with the key
        Array.from(this.cache.keys())
          .filter(cacheKey => cacheKey.startsWith(key))
          .forEach(cacheKey => {
            this.cache.delete(cacheKey);
            const interval = this.refreshIntervals.get(cacheKey);
            if (interval) {
              clearInterval(interval);
              this.refreshIntervals.delete(cacheKey);
            }
          });
      });
    }
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Cleanup method
   */
  destroy() {
    // Close all WebSocket connections
    this.wsConnections.forEach(ws => ws.close());
    this.wsConnections.clear();

    // Clear all intervals
    this.refreshIntervals.forEach(interval => clearInterval(interval));
    this.refreshIntervals.clear();

    // Clear cache and subscribers
    this.cache.clear();
    this.subscribers.clear();

    console.log('EnterpriseDataService destroyed');
  }

  /**
   * Health check method
   */
  async healthCheck() {
    try {
      const response = await fetch(`${this.baseUrl}/api/health`);
      return {
        status: response.ok ? 'healthy' : 'unhealthy',
        timestamp: new Date().toISOString(),
        responseTime: response.headers.get('X-Response-Time') || 'unknown'
      };
    } catch (error) {
      return {
        status: 'error',
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * Get service statistics
   */
  getStatistics() {
    return {
      cacheSize: this.cache.size,
      activeSubscriptions: Array.from(this.subscribers.values()).reduce((sum, set) => sum + set.size, 0),
      activeWebSockets: this.wsConnections.size,
      isOnline: this.isOnline,
      refreshIntervals: this.refreshIntervals.size
    };
  }
}

// Create singleton instance
const enterpriseDataService = new EnterpriseDataService();

export default enterpriseDataService;
export { EnterpriseDataService };
