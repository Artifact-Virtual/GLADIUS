// src/services/RealtimeService.js
// LEGION Enterprise Dashboard - Realtime Service
// Comprehensive real-time data streaming, WebSocket management, and live updates service

/**
 * Realtime Service
 * Provides comprehensive real-time data streaming, WebSocket connection management,
 * and live updates for the LEGION Enterprise Dashboard system
 */
class RealtimeService {
  constructor() {
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
    this.connections = new Map();
    this.subscribers = new Map();
    this.messageQueue = [];
    this.isOnline = navigator.onLine;
    this.reconnectAttempts = 5;
    this.reconnectDelay = 2000;
    this.heartbeatInterval = 30000; // 30 seconds
    this.maxQueueSize = 1000;
    this.dataStreams = new Map();
    this.streamBuffers = new Map();
    this.compressionEnabled = true;
    
    // Stream types and configurations
    this.streamTypes = {
      BUSINESS_METRICS: { endpoint: '/ws/business/metrics', buffer: true, compress: true },
      AGENT_STATUS: { endpoint: '/ws/agents/status', buffer: false, compress: true },
      WORKFLOW_UPDATES: { endpoint: '/ws/workflows/updates', buffer: true, compress: true },
      SYSTEM_METRICS: { endpoint: '/ws/system/metrics', buffer: true, compress: false },
      API_HEALTH: { endpoint: '/ws/apis/health', buffer: false, compress: true },
      USER_ACTIVITY: { endpoint: '/ws/users/activity', buffer: false, compress: true },
      NOTIFICATIONS: { endpoint: '/ws/notifications', buffer: false, compress: false },
      LOGS: { endpoint: '/ws/logs/stream', buffer: true, compress: true },
      EVENTS: { endpoint: '/ws/events/stream', buffer: true, compress: true },
      ALERTS: { endpoint: '/ws/alerts/stream', buffer: false, compress: false }
    };
    
    // Initialize real-time service
    this.initializeRealtimeService();
    
    console.log('RealtimeService initialized');
  }

  /**
   * Initialize real-time service and connection monitoring
   */
  initializeRealtimeService() {
    // Network status monitoring
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.reconnectAllStreams();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      this.handleOfflineMode();
    });

    // Heartbeat monitoring
    setInterval(() => {
      this.sendHeartbeats();
    }, this.heartbeatInterval);

    // Message queue processing
    setInterval(() => {
      this.processMessageQueue();
    }, 1000);

    // Buffer cleanup
    setInterval(() => {
      this.cleanupBuffers();
    }, 60000); // 1 minute
  }

  /**
   * Stream Management
   */
  async createStream(streamType, options = {}) {
    if (!this.streamTypes[streamType]) {
      throw new Error(`Unknown stream type: ${streamType}`);
    }

    const streamConfig = { ...this.streamTypes[streamType], ...options };
    const streamId = `${streamType}_${Date.now()}`;
    
    try {
      const connection = await this.createConnection(streamId, streamConfig);
      
      this.dataStreams.set(streamId, {
        type: streamType,
        config: streamConfig,
        connection,
        created: Date.now(),
        active: true,
        messageCount: 0,
        lastMessage: null
      });

      if (streamConfig.buffer) {
        this.streamBuffers.set(streamId, []);
      }

      console.log(`Stream created: ${streamType} (${streamId})`);
      
      return streamId;
    } catch (error) {
      console.error(`Failed to create stream ${streamType}:`, error);
      throw error;
    }
  }

  async destroyStream(streamId) {
    const stream = this.dataStreams.get(streamId);
    if (!stream) {
      console.warn(`Stream not found: ${streamId}`);
      return;
    }

    // Close connection
    if (stream.connection) {
      stream.connection.close();
    }

    // Cleanup
    this.dataStreams.delete(streamId);
    this.streamBuffers.delete(streamId);
    this.subscribers.delete(streamId);

    console.log(`Stream destroyed: ${streamId}`);
  }

  getStreamInfo(streamId) {
    const stream = this.dataStreams.get(streamId);
    if (!stream) {
      return null;
    }

    return {
      id: streamId,
      type: stream.type,
      active: stream.active,
      created: stream.created,
      messageCount: stream.messageCount,
      lastMessage: stream.lastMessage,
      connectionState: stream.connection ? stream.connection.readyState : 'unknown',
      bufferSize: this.streamBuffers.get(streamId)?.length || 0
    };
  }

  getAllStreams() {
    return Array.from(this.dataStreams.keys()).map(streamId => this.getStreamInfo(streamId));
  }

  /**
   * Subscription Management
   */
  subscribe(streamId, callback, options = {}) {
    if (!this.subscribers.has(streamId)) {
      this.subscribers.set(streamId, new Set());
    }

    const subscription = {
      callback,
      filter: options.filter,
      transform: options.transform,
      throttle: options.throttle,
      lastCall: 0,
      id: `sub_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };

    this.subscribers.get(streamId).add(subscription);

    // Send buffered messages if available
    if (options.includeBuffer && this.streamBuffers.has(streamId)) {
      const buffer = this.streamBuffers.get(streamId);
      buffer.forEach(message => {
        this.notifySubscriber(subscription, message);
      });
    }

    return () => {
      this.subscribers.get(streamId)?.delete(subscription);
      if (this.subscribers.get(streamId)?.size === 0) {
        this.subscribers.delete(streamId);
      }
    };
  }

  unsubscribe(streamId, subscriptionId) {
    const subscribers = this.subscribers.get(streamId);
    if (subscribers) {
      const subscription = Array.from(subscribers).find(sub => sub.id === subscriptionId);
      if (subscription) {
        subscribers.delete(subscription);
        return true;
      }
    }
    return false;
  }

  /**
   * Business Metrics Streaming
   */
  async streamBusinessMetrics(callback, options = {}) {
    const streamId = await this.createStream('BUSINESS_METRICS', options);
    return this.subscribe(streamId, callback, options);
  }

  async streamRevenueUpdates(callback, options = {}) {
    const streamId = await this.createStream('BUSINESS_METRICS', {
      ...options,
      filter: { type: 'revenue' }
    });
    return this.subscribe(streamId, callback, { ...options, filter: data => data.type === 'revenue' });
  }

  async streamKpiUpdates(callback, options = {}) {
    const streamId = await this.createStream('BUSINESS_METRICS', {
      ...options,
      filter: { type: 'kpi' }
    });
    return this.subscribe(streamId, callback, { ...options, filter: data => data.type === 'kpi' });
  }

  /**
   * Agent Status Streaming
   */
  async streamAgentStatus(callback, options = {}) {
    const streamId = await this.createStream('AGENT_STATUS', options);
    return this.subscribe(streamId, callback, options);
  }

  async streamAgentHealth(agentId, callback, options = {}) {
    const streamId = await this.createStream('AGENT_STATUS', {
      ...options,
      filter: { agentId }
    });
    return this.subscribe(streamId, callback, { 
      ...options, 
      filter: data => data.agentId === agentId && data.type === 'health' 
    });
  }

  async streamAgentPerformance(callback, options = {}) {
    const streamId = await this.createStream('AGENT_STATUS', {
      ...options,
      filter: { type: 'performance' }
    });
    return this.subscribe(streamId, callback, { ...options, filter: data => data.type === 'performance' });
  }

  /**
   * Workflow Updates Streaming
   */
  async streamWorkflowUpdates(callback, options = {}) {
    const streamId = await this.createStream('WORKFLOW_UPDATES', options);
    return this.subscribe(streamId, callback, options);
  }

  async streamWorkflowExecution(workflowId, callback, options = {}) {
    const streamId = await this.createStream('WORKFLOW_UPDATES', {
      ...options,
      filter: { workflowId }
    });
    return this.subscribe(streamId, callback, { 
      ...options, 
      filter: data => data.workflowId === workflowId 
    });
  }

  async streamWorkflowEvents(callback, options = {}) {
    const streamId = await this.createStream('WORKFLOW_UPDATES', {
      ...options,
      filter: { type: 'event' }
    });
    return this.subscribe(streamId, callback, { ...options, filter: data => data.type === 'event' });
  }

  /**
   * System Metrics Streaming
   */
  async streamSystemMetrics(callback, options = {}) {
    const streamId = await this.createStream('SYSTEM_METRICS', options);
    return this.subscribe(streamId, callback, options);
  }

  async streamPerformanceMetrics(callback, options = {}) {
    const streamId = await this.createStream('SYSTEM_METRICS', {
      ...options,
      filter: { category: 'performance' }
    });
    return this.subscribe(streamId, callback, { 
      ...options, 
      filter: data => data.category === 'performance' 
    });
  }

  async streamResourceUsage(callback, options = {}) {
    const streamId = await this.createStream('SYSTEM_METRICS', {
      ...options,
      filter: { category: 'resources' }
    });
    return this.subscribe(streamId, callback, { 
      ...options, 
      filter: data => data.category === 'resources' 
    });
  }

  /**
   * API Health Streaming
   */
  async streamApiHealth(callback, options = {}) {
    const streamId = await this.createStream('API_HEALTH', options);
    return this.subscribe(streamId, callback, options);
  }

  async streamApiStatus(apiId, callback, options = {}) {
    const streamId = await this.createStream('API_HEALTH', {
      ...options,
      filter: { apiId }
    });
    return this.subscribe(streamId, callback, { 
      ...options, 
      filter: data => data.apiId === apiId 
    });
  }

  /**
   * Notification Streaming
   */
  async streamNotifications(callback, options = {}) {
    const streamId = await this.createStream('NOTIFICATIONS', options);
    return this.subscribe(streamId, callback, options);
  }

  async streamAlerts(callback, options = {}) {
    const streamId = await this.createStream('ALERTS', options);
    return this.subscribe(streamId, callback, options);
  }

  async streamUserActivity(callback, options = {}) {
    const streamId = await this.createStream('USER_ACTIVITY', options);
    return this.subscribe(streamId, callback, options);
  }

  /**
   * Logs and Events Streaming
   */
  async streamLogs(callback, options = {}) {
    const streamId = await this.createStream('LOGS', options);
    return this.subscribe(streamId, callback, options);
  }

  async streamEvents(callback, options = {}) {
    const streamId = await this.createStream('EVENTS', options);
    return this.subscribe(streamId, callback, options);
  }

  async streamErrorLogs(callback, options = {}) {
    const streamId = await this.createStream('LOGS', {
      ...options,
      filter: { level: 'error' }
    });
    return this.subscribe(streamId, callback, { 
      ...options, 
      filter: data => data.level === 'error' 
    });
  }

  /**
   * Custom Stream Creation
   */
  async createCustomStream(endpoint, callback, options = {}) {
    const streamId = `custom_${Date.now()}`;
    
    try {
      const connection = await this.createConnection(streamId, {
        endpoint,
        ...options
      });
      
      this.dataStreams.set(streamId, {
        type: 'CUSTOM',
        config: { endpoint, ...options },
        connection,
        created: Date.now(),
        active: true,
        messageCount: 0,
        lastMessage: null
      });

      if (options.buffer) {
        this.streamBuffers.set(streamId, []);
      }

      return this.subscribe(streamId, callback, options);
    } catch (error) {
      console.error(`Failed to create custom stream:`, error);
      throw error;
    }
  }

  /**
   * Message Broadcasting
   */
  async broadcast(channel, message, options = {}) {
    try {
      const response = await fetch(`${this.baseUrl}/api/realtime/broadcast`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          channel,
          message,
          options
        })
      });

      if (!response.ok) {
        throw new Error(`Broadcast failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Broadcast failed:', error);
      throw error;
    }
  }

  async sendMessage(streamId, message) {
    const stream = this.dataStreams.get(streamId);
    if (!stream || !stream.connection) {
      throw new Error(`Stream not found or not connected: ${streamId}`);
    }

    if (stream.connection.readyState === WebSocket.OPEN) {
      const payload = this.compressionEnabled && stream.config.compress
        ? this.compressMessage(message)
        : JSON.stringify(message);
      
      stream.connection.send(payload);
      return true;
    } else {
      // Queue message for later
      this.messageQueue.push({
        streamId,
        message,
        timestamp: Date.now()
      });
      return false;
    }
  }

  /**
   * WebSocket Connection Management
   */
  async createConnection(streamId, config) {
    return new Promise((resolve, reject) => {
      try {
        const ws = new WebSocket(`${this.wsUrl}${config.endpoint}`);
        
        ws.onopen = () => {
          console.log(`WebSocket connected: ${streamId}`);
          
          // Send initial configuration if provided
          if (config.filter || config.options) {
            ws.send(JSON.stringify({
              type: 'configure',
              filter: config.filter,
              options: config.options
            }));
          }

          resolve(ws);
        };

        ws.onmessage = (event) => {
          this.handleMessage(streamId, event.data);
        };

        ws.onclose = (event) => {
          console.log(`WebSocket disconnected: ${streamId}`, event.code, event.reason);
          this.handleDisconnection(streamId, event);
        };

        ws.onerror = (error) => {
          console.error(`WebSocket error: ${streamId}`, error);
          reject(error);
        };

        // Store connection
        this.connections.set(streamId, ws);
        
      } catch (error) {
        reject(error);
      }
    });
  }

  handleMessage(streamId, rawData) {
    try {
      const stream = this.dataStreams.get(streamId);
      if (!stream) return;

      // Decompress if needed
      const data = stream.config.compress
        ? this.decompressMessage(rawData)
        : JSON.parse(rawData);

      // Update stream stats
      stream.messageCount++;
      stream.lastMessage = Date.now();

      // Buffer message if configured
      if (stream.config.buffer) {
        const buffer = this.streamBuffers.get(streamId) || [];
        buffer.push(data);
        
        // Limit buffer size
        if (buffer.length > 100) {
          buffer.shift();
        }
        
        this.streamBuffers.set(streamId, buffer);
      }

      // Notify subscribers
      this.notifySubscribers(streamId, data);

    } catch (error) {
      console.error(`Message handling error (${streamId}):`, error);
    }
  }

  handleDisconnection(streamId, event) {
    const stream = this.dataStreams.get(streamId);
    if (stream) {
      stream.active = false;
      
      // Attempt reconnection if not a clean close
      if (event.code !== 1000 && this.isOnline) {
        this.scheduleReconnect(streamId);
      }
    }
  }

  scheduleReconnect(streamId, attempt = 1) {
    if (attempt > this.reconnectAttempts) {
      console.error(`Max reconnection attempts reached for: ${streamId}`);
      return;
    }

    const delay = this.reconnectDelay * Math.pow(2, attempt - 1);
    
    setTimeout(async () => {
      try {
        const stream = this.dataStreams.get(streamId);
        if (!stream) return;

        console.log(`Reconnecting stream: ${streamId} (attempt ${attempt})`);
        
        const newConnection = await this.createConnection(streamId, stream.config);
        stream.connection = newConnection;
        stream.active = true;
        
        console.log(`Stream reconnected: ${streamId}`);
        
      } catch (error) {
        console.error(`Reconnection failed for ${streamId}:`, error);
        this.scheduleReconnect(streamId, attempt + 1);
      }
    }, delay);
  }

  /**
   * Subscriber Notification
   */
  notifySubscribers(streamId, data) {
    const subscribers = this.subscribers.get(streamId);
    if (!subscribers) return;

    subscribers.forEach(subscription => {
      this.notifySubscriber(subscription, data);
    });
  }

  notifySubscriber(subscription, data) {
    try {
      // Apply filter if configured
      if (subscription.filter && typeof subscription.filter === 'function') {
        if (!subscription.filter(data)) return;
      }

      // Apply throttling if configured
      if (subscription.throttle) {
        const now = Date.now();
        if (now - subscription.lastCall < subscription.throttle) return;
        subscription.lastCall = now;
      }

      // Apply transformation if configured
      let processedData = data;
      if (subscription.transform && typeof subscription.transform === 'function') {
        processedData = subscription.transform(data);
      }

      // Call subscriber callback
      subscription.callback(processedData);
      
    } catch (error) {
      console.error('Subscriber notification error:', error);
    }
  }

  /**
   * Utility Methods
   */
  sendHeartbeats() {
    this.connections.forEach((ws, streamId) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'heartbeat', timestamp: Date.now() }));
      }
    });
  }

  processMessageQueue() {
    if (this.messageQueue.length === 0) return;

    const messagesToProcess = this.messageQueue.splice(0, 10); // Process 10 at a time
    
    messagesToProcess.forEach(({ streamId, message }) => {
      this.sendMessage(streamId, message).catch(error => {
        console.error(`Failed to send queued message:`, error);
      });
    });
  }

  cleanupBuffers() {
    const maxAge = 300000; // 5 minutes
    const now = Date.now();

    this.streamBuffers.forEach((buffer, streamId) => {
      const filtered = buffer.filter(message => 
        message.timestamp && (now - message.timestamp) < maxAge
      );
      
      if (filtered.length !== buffer.length) {
        this.streamBuffers.set(streamId, filtered);
      }
    });
  }

  handleOfflineMode() {
    console.log('Entering offline mode');
    // Close all connections gracefully
    this.connections.forEach(ws => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close(1000, 'Going offline');
      }
    });
  }

  reconnectAllStreams() {
    console.log('Reconnecting all streams');
    this.dataStreams.forEach((stream, streamId) => {
      if (!stream.active) {
        this.scheduleReconnect(streamId);
      }
    });
  }

  compressMessage(message) {
    // Simple compression (in production, use a proper compression library)
    return JSON.stringify(message);
  }

  decompressMessage(data) {
    // Simple decompression
    return JSON.parse(data);
  }

  /**
   * Service Management
   */
  async healthCheck() {
    const activeStreams = Array.from(this.dataStreams.values()).filter(s => s.active).length;
    const totalConnections = this.connections.size;
    
    return {
      status: this.isOnline ? 'healthy' : 'offline',
      activeStreams,
      totalConnections,
      queueSize: this.messageQueue.length,
      timestamp: new Date().toISOString()
    };
  }

  getStatistics() {
    return {
      totalStreams: this.dataStreams.size,
      activeStreams: Array.from(this.dataStreams.values()).filter(s => s.active).length,
      totalConnections: this.connections.size,
      totalSubscribers: Array.from(this.subscribers.values()).reduce((sum, set) => sum + set.size, 0),
      queueSize: this.messageQueue.length,
      isOnline: this.isOnline,
      bufferSizes: Object.fromEntries(
        Array.from(this.streamBuffers.entries()).map(([id, buffer]) => [id, buffer.length])
      )
    };
  }

  destroy() {
    // Close all connections
    this.connections.forEach(ws => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close(1000, 'Service shutdown');
      }
    });

    // Clear all data
    this.connections.clear();
    this.subscribers.clear();
    this.dataStreams.clear();
    this.streamBuffers.clear();
    this.messageQueue = [];

    console.log('RealtimeService destroyed');
  }
}

// Create singleton instance
const realtimeService = new RealtimeService();

export default realtimeService;
export { RealtimeService };
