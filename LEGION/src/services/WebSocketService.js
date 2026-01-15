/**
 * WebSocket Service for Real-Time Enterprise Data
 * Manages persistent WebSocket connections for live system monitoring
 */

class WebSocketService {
    constructor() {
        this.connections = new Map();
        this.reconnectAttempts = new Map();
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.subscriptions = new Map();
        this.messageHandlers = new Map();
        this.isReconnecting = false;
    }

    /**
     * Create WebSocket connection for a specific data stream
     */
    connect(channel, options = {}) {
        const {
            url = this.getWebSocketUrl(channel),
            autoReconnect = true,
            heartbeat = true,
            heartbeatInterval = 30000
        } = options;

        if (this.connections.has(channel)) {
            console.warn(`WebSocket connection for ${channel} already exists`);
            return this.connections.get(channel);
        }

        try {
            const ws = new WebSocket(url);
            
            ws.onopen = () => {
                console.log(`WebSocket connected: ${channel}`);
                this.reconnectAttempts.set(channel, 0);
                this.setupHeartbeat(channel, ws, heartbeat, heartbeatInterval);
                this.sendSubscriptionRequest(channel, ws);
            };

            ws.onmessage = (event) => {
                this.handleMessage(channel, event.data);
            };

            ws.onclose = (event) => {
                console.log(`WebSocket closed: ${channel}`, event.code, event.reason);
                this.connections.delete(channel);
                
                if (autoReconnect && !event.wasClean) {
                    this.scheduleReconnect(channel, options);
                }
            };

            ws.onerror = (error) => {
                console.error(`WebSocket error: ${channel}`, error);
            };

            this.connections.set(channel, ws);
            return ws;

        } catch (error) {
            console.error(`Failed to create WebSocket connection for ${channel}:`, error);
            throw error;
        }
    }

    /**
     * Subscribe to specific data updates
     */
    subscribe(channel, dataType, callback) {
        if (!this.subscriptions.has(channel)) {
            this.subscriptions.set(channel, new Map());
        }
        
        if (!this.messageHandlers.has(channel)) {
            this.messageHandlers.set(channel, new Map());
        }

        this.subscriptions.get(channel).set(dataType, true);
        this.messageHandlers.get(channel).set(dataType, callback);

        // If connection exists, send subscription update
        const ws = this.connections.get(channel);
        if (ws && ws.readyState === WebSocket.OPEN) {
            this.sendSubscriptionRequest(channel, ws);
        }
    }

    /**
     * Unsubscribe from data updates
     */
    unsubscribe(channel, dataType) {
        if (this.subscriptions.has(channel)) {
            this.subscriptions.get(channel).delete(dataType);
        }
        
        if (this.messageHandlers.has(channel)) {
            this.messageHandlers.get(channel).delete(dataType);
        }

        // Update server subscription
        const ws = this.connections.get(channel);
        if (ws && ws.readyState === WebSocket.OPEN) {
            this.sendSubscriptionRequest(channel, ws);
        }
    }

    /**
     * Send message to WebSocket
     */
    send(channel, message) {
        const ws = this.connections.get(channel);
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(message));
        } else {
            console.warn(`Cannot send message to ${channel}: connection not ready`);
        }
    }

    /**
     * Close WebSocket connection
     */
    disconnect(channel) {
        const ws = this.connections.get(channel);
        if (ws) {
            ws.close(1000, 'Client disconnect');
            this.connections.delete(channel);
            this.subscriptions.delete(channel);
            this.messageHandlers.delete(channel);
            this.reconnectAttempts.delete(channel);
        }
    }

    /**
     * Close all WebSocket connections
     */
    disconnectAll() {
        for (const channel of this.connections.keys()) {
            this.disconnect(channel);
        }
    }

    /**
     * Get WebSocket URL for channel
     */
    getWebSocketUrl(channel) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = process.env.NODE_ENV === 'development' 
            ? 'localhost:5001' 
            : window.location.host;
        
        return `${protocol}//${host}/ws/${channel}`;
    }

    /**
     * Handle incoming WebSocket messages
     */
    handleMessage(channel, data) {
        try {
            const message = JSON.parse(data);
            const { type, payload, timestamp } = message;

            // Handle heartbeat responses
            if (type === 'heartbeat') {
                return;
            }

            // Route message to appropriate handler
            const handlers = this.messageHandlers.get(channel);
            if (handlers && handlers.has(type)) {
                const callback = handlers.get(type);
                callback(payload, { type, timestamp });
            }

            // Broadcast to global listeners
            this.broadcastMessage(channel, type, payload);

        } catch (error) {
            console.error(`Failed to parse WebSocket message from ${channel}:`, error);
        }
    }

    /**
     * Send subscription request to server
     */
    sendSubscriptionRequest(channel, ws) {
        const subscriptions = this.subscriptions.get(channel);
        if (subscriptions) {
            const message = {
                type: 'subscribe',
                payload: {
                    subscriptions: Array.from(subscriptions.keys())
                }
            };
            ws.send(JSON.stringify(message));
        }
    }

    /**
     * Setup heartbeat mechanism
     */
    setupHeartbeat(channel, ws, enabled, interval) {
        if (!enabled) return;

        const heartbeatTimer = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: 'heartbeat', timestamp: Date.now() }));
            } else {
                clearInterval(heartbeatTimer);
            }
        }, interval);
    }

    /**
     * Schedule reconnection attempt
     */
    scheduleReconnect(channel, options) {
        const attempts = this.reconnectAttempts.get(channel) || 0;
        
        if (attempts >= this.maxReconnectAttempts) {
            console.error(`Max reconnection attempts reached for ${channel}`);
            return;
        }

        const delay = this.reconnectDelay * Math.pow(2, attempts); // Exponential backoff
        
        setTimeout(() => {
            console.log(`Attempting to reconnect ${channel} (attempt ${attempts + 1})`);
            this.reconnectAttempts.set(channel, attempts + 1);
            this.connect(channel, options);
        }, delay);
    }

    /**
     * Broadcast message to global event listeners
     */
    broadcastMessage(channel, type, payload) {
        const event = new CustomEvent('websocket-message', {
            detail: { channel, type, payload }
        });
        window.dispatchEvent(event);
    }

    /**
     * Get connection status
     */
    getConnectionStatus(channel) {
        const ws = this.connections.get(channel);
        if (!ws) return 'disconnected';
        
        switch (ws.readyState) {
            case WebSocket.CONNECTING: return 'connecting';
            case WebSocket.OPEN: return 'connected';
            case WebSocket.CLOSING: return 'closing';
            case WebSocket.CLOSED: return 'disconnected';
            default: return 'unknown';
        }
    }

    /**
     * Get all connection statuses
     */
    getAllConnectionStatuses() {
        const statuses = {};
        for (const channel of this.connections.keys()) {
            statuses[channel] = this.getConnectionStatus(channel);
        }
        return statuses;
    }
}

// Enterprise-specific WebSocket channels and data types
export const WEBSOCKET_CHANNELS = {
    SYSTEM_STATUS: 'system-status',
    AGENT_HEALTH: 'agent-health', 
    WORKFLOW_EXECUTION: 'workflow-execution',
    PERFORMANCE_METRICS: 'performance-metrics',
    ALERTS: 'alerts',
    DATABASE_STATUS: 'database-status',
    AGENT_COMMUNICATIONS: 'agent-communications'
};

export const DATA_TYPES = {
    // System status data types
    SYSTEM_HEALTH: 'system_health',
    SERVICE_STATUS: 'service_status',
    SECURITY_STATUS: 'security_status',
    
    // Agent health data types
    AGENT_STATUS_UPDATE: 'agent_status_update',
    AGENT_PERFORMANCE: 'agent_performance',
    AGENT_ERROR: 'agent_error',
    
    // Workflow data types
    WORKFLOW_STARTED: 'workflow_started',
    WORKFLOW_PROGRESS: 'workflow_progress',
    WORKFLOW_COMPLETED: 'workflow_completed',
    WORKFLOW_FAILED: 'workflow_failed',
    
    // Performance data types
    CPU_USAGE: 'cpu_usage',
    MEMORY_USAGE: 'memory_usage',
    NETWORK_IO: 'network_io',
    DATABASE_PERFORMANCE: 'database_performance',
    
    // Alert data types
    SYSTEM_ALERT: 'system_alert',
    SECURITY_ALERT: 'security_alert',
    PERFORMANCE_ALERT: 'performance_alert',
    
    // Database data types
    DATABASE_CONNECTION: 'database_connection',
    QUERY_PERFORMANCE: 'query_performance',
    
    // Communication data types
    AGENT_MESSAGE: 'agent_message',
    INTER_AGENT_COMM: 'inter_agent_comm'
};

// Create singleton instance
const webSocketService = new WebSocketService();

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    webSocketService.disconnectAll();
});

export default webSocketService;
