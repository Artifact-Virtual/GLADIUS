// src/services/WorkflowMonitoringService.js
// LEGION Enterprise Dashboard - Workflow Monitoring Service
// Comprehensive workflow orchestration, process monitoring, and automation service

/**
 * Workflow Monitoring Service
 * Provides comprehensive workflow tracking, process monitoring, and automation management
 * for the LEGION Enterprise Dashboard system
 */
class WorkflowMonitoringService {
  constructor() {
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
    this.cache = new Map();
    this.subscribers = new Map();
    this.wsConnections = new Map();
    this.workflowRegistry = new Map();
    this.executionHistory = [];
    this.retryAttempts = 3;
    this.retryDelay = 1000;
    this.cacheTimeout = 90000; // 1.5 minutes for workflow data
    this.monitoringInterval = 30000; // 30 seconds
    this.isOnline = navigator.onLine;
    
    // Initialize workflow monitoring
    this.initializeWorkflowMonitoring();
    
    console.log('WorkflowMonitoringService initialized');
  }

  /**
   * Initialize workflow monitoring and process tracking
   */
  initializeWorkflowMonitoring() {
    // Start workflow monitoring
    setInterval(() => {
      this.performWorkflowHealthChecks();
    }, this.monitoringInterval);

    // Initialize connection monitoring
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.reconnectWorkflowConnections();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
    });
  }

  /**
   * Active Workflow Monitoring
   */
  async getActiveWorkflows() {
    return this.fetchWithCache('active-workflows', '/api/workflows/active', {
      refresh: 20000, // 20 seconds
      priority: 'critical'
    });
  }

  async getWorkflowDetails(workflowId) {
    return this.fetchWithCache(`workflow-details-${workflowId}`, `/api/workflows/${workflowId}`, {
      refresh: 30000, // 30 seconds
      priority: 'high'
    });
  }

  async getWorkflowStatus(workflowId) {
    return this.fetchWithCache(`workflow-status-${workflowId}`, `/api/workflows/${workflowId}/status`, {
      refresh: 10000, // 10 seconds
      priority: 'critical'
    });
  }

  async getWorkflowsByStatus(status = 'running') {
    return this.fetchWithCache(`workflows-status-${status}`, `/api/workflows/status/${status}`, {
      refresh: 30000, // 30 seconds
      priority: 'high'
    });
  }

  /**
   * Workflow Execution History and Analytics
   */
  async getWorkflowExecutions(timeRange = '24h', limit = 100) {
    return this.fetchWithCache(
      `workflow-executions-${timeRange}-${limit}`,
      `/api/workflows/executions?range=${timeRange}&limit=${limit}`,
      {
        refresh: 60000, // 1 minute
        priority: 'medium'
      }
    );
  }

  async getExecutionHistory(workflowId, limit = 50) {
    return this.fetchWithCache(
      `execution-history-${workflowId}-${limit}`,
      `/api/workflows/${workflowId}/executions?limit=${limit}`,
      {
        refresh: 90000, // 1.5 minutes
        priority: 'medium'
      }
    );
  }

  async getExecutionDetails(executionId) {
    return this.fetchWithCache(`execution-details-${executionId}`, `/api/workflows/executions/${executionId}`, {
      refresh: 60000, // 1 minute
      priority: 'medium'
    });
  }

  async getExecutionLogs(executionId) {
    return this.fetchWithCache(`execution-logs-${executionId}`, `/api/workflows/executions/${executionId}/logs`, {
      refresh: 30000, // 30 seconds
      priority: 'high'
    });
  }

  /**
   * Workflow Performance Monitoring
   */
  async getWorkflowPerformanceMetrics(workflowId, timeRange = '7d') {
    return this.fetchWithCache(
      `workflow-performance-${workflowId}-${timeRange}`,
      `/api/workflows/${workflowId}/performance?range=${timeRange}`,
      {
        refresh: 120000, // 2 minutes
        priority: 'medium'
      }
    );
  }

  async getOverallPerformanceMetrics(timeRange = '24h') {
    return this.fetchWithCache(
      `overall-performance-${timeRange}`,
      `/api/workflows/performance/overview?range=${timeRange}`,
      {
        refresh: 180000, // 3 minutes
        priority: 'medium'
      }
    );
  }

  async getPerformanceTrends(metric = 'success_rate', timeRange = '30d') {
    return this.fetchWithCache(
      `performance-trends-${metric}-${timeRange}`,
      `/api/workflows/performance/trends?metric=${metric}&range=${timeRange}`,
      {
        refresh: 300000, // 5 minutes
        priority: 'low'
      }
    );
  }

  async getBottleneckAnalysis() {
    return this.fetchWithCache('bottleneck-analysis', '/api/workflows/analysis/bottlenecks', {
      refresh: 300000, // 5 minutes
      priority: 'medium'
    });
  }

  /**
   * Workflow Templates and Configuration
   */
  async getWorkflowTemplates() {
    return this.fetchWithCache('workflow-templates', '/api/workflows/templates', {
      refresh: 600000, // 10 minutes
      priority: 'low'
    });
  }

  async getTemplateDetails(templateId) {
    return this.fetchWithCache(`template-details-${templateId}`, `/api/workflows/templates/${templateId}`, {
      refresh: 600000, // 10 minutes
      priority: 'low'
    });
  }

  async createWorkflowFromTemplate(templateId, parameters = {}) {
    const response = await this.makeRequest('/api/workflows/create-from-template', {
      method: 'POST',
      body: JSON.stringify({
        templateId,
        parameters
      })
    });
    
    // Invalidate related cache
    this.invalidateCache(['active-workflows', 'workflow-templates']);
    
    return response;
  }

  async updateWorkflowTemplate(templateId, templateData) {
    const response = await this.makeRequest(`/api/workflows/templates/${templateId}`, {
      method: 'PUT',
      body: JSON.stringify(templateData)
    });
    
    this.invalidateCache(['workflow-templates', `template-details-${templateId}`]);
    
    return response;
  }

  /**
   * Workflow Trigger Management
   */
  async getWorkflowTriggers() {
    return this.fetchWithCache('workflow-triggers', '/api/workflows/triggers', {
      refresh: 120000, // 2 minutes
      priority: 'medium'
    });
  }

  async getTriggerHistory(triggerId, timeRange = '24h') {
    return this.fetchWithCache(
      `trigger-history-${triggerId}-${timeRange}`,
      `/api/workflows/triggers/${triggerId}/history?range=${timeRange}`,
      {
        refresh: 90000, // 1.5 minutes
        priority: 'medium'
      }
    );
  }

  async getTriggerPerformance() {
    return this.fetchWithCache('trigger-performance', '/api/workflows/triggers/performance', {
      refresh: 180000, // 3 minutes
      priority: 'medium'
    });
  }

  async enableTrigger(triggerId) {
    const response = await this.makeRequest(`/api/workflows/triggers/${triggerId}/enable`, {
      method: 'POST'
    });
    
    this.invalidateCache(['workflow-triggers']);
    
    return response;
  }

  async disableTrigger(triggerId) {
    const response = await this.makeRequest(`/api/workflows/triggers/${triggerId}/disable`, {
      method: 'POST'
    });
    
    this.invalidateCache(['workflow-triggers']);
    
    return response;
  }

  /**
   * Workflow Control and Management
   */
  async startWorkflow(workflowId, parameters = {}) {
    const response = await this.makeRequest(`/api/workflows/${workflowId}/start`, {
      method: 'POST',
      body: JSON.stringify(parameters)
    });
    
    this.invalidateCache(['active-workflows', `workflow-status-${workflowId}`]);
    
    return response;
  }

  async pauseWorkflow(workflowId, reason = '') {
    const response = await this.makeRequest(`/api/workflows/${workflowId}/pause`, {
      method: 'POST',
      body: JSON.stringify({ reason })
    });
    
    this.invalidateCache([`workflow-status-${workflowId}`, 'active-workflows']);
    
    return response;
  }

  async resumeWorkflow(workflowId) {
    const response = await this.makeRequest(`/api/workflows/${workflowId}/resume`, {
      method: 'POST'
    });
    
    this.invalidateCache([`workflow-status-${workflowId}`, 'active-workflows']);
    
    return response;
  }

  async stopWorkflow(workflowId, force = false) {
    const response = await this.makeRequest(`/api/workflows/${workflowId}/stop`, {
      method: 'POST',
      body: JSON.stringify({ force })
    });
    
    this.invalidateCache([`workflow-status-${workflowId}`, 'active-workflows']);
    
    return response;
  }

  async retryWorkflow(workflowId, fromStep = null) {
    const response = await this.makeRequest(`/api/workflows/${workflowId}/retry`, {
      method: 'POST',
      body: JSON.stringify({ fromStep })
    });
    
    this.invalidateCache([`workflow-status-${workflowId}`, 'active-workflows']);
    
    return response;
  }

  /**
   * Workflow Scheduling and Automation
   */
  async getScheduledWorkflows() {
    return this.fetchWithCache('scheduled-workflows', '/api/workflows/scheduled', {
      refresh: 180000, // 3 minutes
      priority: 'medium'
    });
  }

  async getWorkflowSchedule(workflowId) {
    return this.fetchWithCache(`workflow-schedule-${workflowId}`, `/api/workflows/${workflowId}/schedule`, {
      refresh: 300000, // 5 minutes
      priority: 'low'
    });
  }

  async scheduleWorkflow(workflowId, scheduleConfig) {
    const response = await this.makeRequest(`/api/workflows/${workflowId}/schedule`, {
      method: 'POST',
      body: JSON.stringify(scheduleConfig)
    });
    
    this.invalidateCache(['scheduled-workflows', `workflow-schedule-${workflowId}`]);
    
    return response;
  }

  async unscheduleWorkflow(workflowId) {
    const response = await this.makeRequest(`/api/workflows/${workflowId}/unschedule`, {
      method: 'DELETE'
    });
    
    this.invalidateCache(['scheduled-workflows', `workflow-schedule-${workflowId}`]);
    
    return response;
  }

  /**
   * Workflow Dependencies and Orchestration
   */
  async getWorkflowDependencies(workflowId) {
    return this.fetchWithCache(`workflow-dependencies-${workflowId}`, `/api/workflows/${workflowId}/dependencies`, {
      refresh: 300000, // 5 minutes
      priority: 'low'
    });
  }

  async getDependencyGraph() {
    return this.fetchWithCache('dependency-graph', '/api/workflows/dependencies/graph', {
      refresh: 600000, // 10 minutes
      priority: 'low'
    });
  }

  async getOrchestrationStatus() {
    return this.fetchWithCache('orchestration-status', '/api/workflows/orchestration/status', {
      refresh: 60000, // 1 minute
      priority: 'high'
    });
  }

  async updateDependencies(workflowId, dependencies) {
    const response = await this.makeRequest(`/api/workflows/${workflowId}/dependencies`, {
      method: 'PUT',
      body: JSON.stringify(dependencies)
    });
    
    this.invalidateCache([`workflow-dependencies-${workflowId}`, 'dependency-graph']);
    
    return response;
  }

  /**
   * Workflow Analytics and Reporting
   */
  async getWorkflowAnalytics(timeRange = '30d') {
    return this.fetchWithCache(
      `workflow-analytics-${timeRange}`,
      `/api/workflows/analytics?range=${timeRange}`,
      {
        refresh: 300000, // 5 minutes
        priority: 'medium'
      }
    );
  }

  async getSuccessRateAnalysis(timeRange = '7d') {
    return this.fetchWithCache(
      `success-rate-${timeRange}`,
      `/api/workflows/analytics/success-rate?range=${timeRange}`,
      {
        refresh: 180000, // 3 minutes
        priority: 'medium'
      }
    );
  }

  async getDurationAnalysis(workflowId, timeRange = '30d') {
    return this.fetchWithCache(
      `duration-analysis-${workflowId}-${timeRange}`,
      `/api/workflows/${workflowId}/analytics/duration?range=${timeRange}`,
      {
        refresh: 300000, // 5 minutes
        priority: 'medium'
      }
    );
  }

  async generateWorkflowReport(reportType, parameters = {}) {
    return this.makeRequest('/api/workflows/reports/generate', {
      method: 'POST',
      body: JSON.stringify({
        type: reportType,
        parameters
      })
    });
  }

  /**
   * Real-time Workflow Monitoring Subscriptions
   */
  subscribeToWorkflowExecutions(callback) {
    return this.subscribe('workflow-executions', callback, {
      endpoint: '/ws/workflows/executions',
      reconnect: true
    });
  }

  subscribeToWorkflowStatus(workflowId, callback) {
    return this.subscribe(`workflow-status-${workflowId}`, callback, {
      endpoint: `/ws/workflows/${workflowId}/status`,
      reconnect: true
    });
  }

  subscribeToTriggerEvents(callback) {
    return this.subscribe('trigger-events', callback, {
      endpoint: '/ws/workflows/triggers',
      reconnect: true
    });
  }

  subscribeToPerformanceMetrics(callback) {
    return this.subscribe('performance-metrics', callback, {
      endpoint: '/ws/workflows/performance',
      reconnect: true
    });
  }

  subscribeToOrchestrationEvents(callback) {
    return this.subscribe('orchestration-events', callback, {
      endpoint: '/ws/workflows/orchestration',
      reconnect: true
    });
  }

  /**
   * Workflow Error Handling and Recovery
   */
  async getWorkflowErrors(timeRange = '24h') {
    return this.fetchWithCache(
      `workflow-errors-${timeRange}`,
      `/api/workflows/errors?range=${timeRange}`,
      {
        refresh: 120000, // 2 minutes
        priority: 'high'
      }
    );
  }

  async getErrorDetails(errorId) {
    return this.fetchWithCache(`error-details-${errorId}`, `/api/workflows/errors/${errorId}`, {
      refresh: 300000, // 5 minutes
      priority: 'medium'
    });
  }

  async getRecoveryOptions(workflowId, errorId) {
    return this.makeRequest(`/api/workflows/${workflowId}/recovery-options`, {
      method: 'POST',
      body: JSON.stringify({ errorId })
    });
  }

  async executeRecoveryAction(workflowId, action, parameters = {}) {
    const response = await this.makeRequest(`/api/workflows/${workflowId}/recover`, {
      method: 'POST',
      body: JSON.stringify({ action, parameters })
    });
    
    this.invalidateCache([`workflow-status-${workflowId}`, 'workflow-errors']);
    
    return response;
  }

  /**
   * Workflow Health Monitoring
   */
  async performWorkflowHealthChecks() {
    try {
      const activeWorkflows = await this.getActiveWorkflows();
      const healthPromises = activeWorkflows.map(workflow => 
        this.getWorkflowStatus(workflow.id).catch(error => ({
          workflowId: workflow.id,
          status: 'error',
          error: error.message
        }))
      );

      const healthResults = await Promise.all(healthPromises);
      
      // Update workflow registry
      healthResults.forEach(result => {
        if (result.workflowId) {
          this.workflowRegistry.set(result.workflowId, {
            ...this.workflowRegistry.get(result.workflowId),
            lastHealthCheck: Date.now(),
            health: result
          });
        }
      });

      // Notify subscribers of health updates
      this.notifySubscribers('workflow-health-check', healthResults);

      return healthResults;
    } catch (error) {
      console.error('Workflow health check failed:', error);
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
        console.log(`Workflow WebSocket connected: ${channel}`);
        this.notifySubscribers(channel, { type: 'connected' });
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.notifySubscribers(channel, data);
          
          // Store execution history for workflow events
          if (channel === 'workflow-executions') {
            this.executionHistory.push({
              ...data,
              timestamp: Date.now()
            });
            
            // Keep only last 500 executions
            if (this.executionHistory.length > 500) {
              this.executionHistory = this.executionHistory.slice(-500);
            }
          }
        } catch (error) {
          console.error(`Workflow WebSocket message parse error (${channel}):`, error);
        }
      };

      ws.onclose = () => {
        console.log(`Workflow WebSocket disconnected: ${channel}`);
        this.wsConnections.delete(channel);
        
        if (reconnect && this.isOnline) {
          setTimeout(() => {
            this.createWebSocketConnection(channel, endpoint, reconnect);
          }, 5000);
        }
      };

      ws.onerror = (error) => {
        console.error(`Workflow WebSocket error (${channel}):`, error);
      };

      this.wsConnections.set(channel, ws);
    } catch (error) {
      console.error(`Failed to create workflow WebSocket connection (${channel}):`, error);
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
          console.error(`Workflow subscriber callback error (${channel}):`, error);
        }
      });
    }
  }

  reconnectWorkflowConnections() {
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
    this.workflowRegistry.clear();
    this.executionHistory = [];
    
    console.log('WorkflowMonitoringService destroyed');
  }

  async healthCheck() {
    try {
      const response = await fetch(`${this.baseUrl}/api/workflows/health`);
      return {
        status: response.ok ? 'healthy' : 'unhealthy',
        timestamp: new Date().toISOString(),
        workflowCount: this.workflowRegistry.size
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
      workflowRegistrySize: this.workflowRegistry.size,
      executionHistorySize: this.executionHistory.length,
      isOnline: this.isOnline
    };
  }
}

// Create singleton instance
const workflowMonitoringService = new WorkflowMonitoringService();

export default workflowMonitoringService;
export { WorkflowMonitoringService };
