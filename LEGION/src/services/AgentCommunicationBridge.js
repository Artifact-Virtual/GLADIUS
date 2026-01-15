/**
 * Agent Communication Bridge Service
 * Handles real-time communication between enterprise dashboard and agent systems
 */

import webSocketService, { WEBSOCKET_CHANNELS, DATA_TYPES } from './WebSocketService';
import EnterpriseDatabase from './EnterpriseDatabase';

class AgentCommunicationBridge {
    constructor() {
        this.isConnected = false;
        this.agentRegistry = new Map();
        this.messageQueue = [];
        this.heartbeatInterval = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        
        // Initialize connection
        this.connect();
        this.setupEventListeners();
    }

    /**
     * Connect to agent orchestrator via WebSocket
     */
    async connect() {
        try {
            // Connect to agent communication channel
            webSocketService.connect(WEBSOCKET_CHANNELS.AGENT_COMMUNICATIONS, {
                autoReconnect: true,
                heartbeat: true,
                heartbeatInterval: 15000
            });

            // Subscribe to agent communication data types
            webSocketService.subscribe(
                WEBSOCKET_CHANNELS.AGENT_COMMUNICATIONS,
                DATA_TYPES.AGENT_MESSAGE,
                this.handleAgentMessage.bind(this)
            );

            webSocketService.subscribe(
                WEBSOCKET_CHANNELS.AGENT_COMMUNICATIONS,
                DATA_TYPES.INTER_AGENT_COMM,
                this.handleInterAgentCommunication.bind(this)
            );

            this.isConnected = true;
            this.startHeartbeat();
            this.processMessageQueue();
            
            console.log('Agent Communication Bridge connected');
        } catch (error) {
            console.error('Failed to connect Agent Communication Bridge:', error);
            this.scheduleReconnect();
        }
    }

    /**
     * Setup event listeners for agent management
     */
    setupEventListeners() {
        // Listen for WebSocket connection status changes
        window.addEventListener('websocket-message', (event) => {
            const { channel, type, payload } = event.detail;
            
            if (channel === WEBSOCKET_CHANNELS.AGENT_COMMUNICATIONS) {
                this.handleWebSocketMessage(type, payload);
            }
        });

        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible' && !this.isConnected) {
                this.connect();
            }
        });
    }

    /**
     * Handle incoming agent messages
     */
    handleAgentMessage(payload, meta) {
        const { agent_id, message_type, content, timestamp, priority = 'normal' } = payload;
        
        // Update agent registry
        this.updateAgentStatus(agent_id, {
            last_message: timestamp,
            status: 'active',
            message_type: message_type
        });

        // Process different message types
        switch (message_type) {
            case 'status_update':
                this.handleStatusUpdate(agent_id, content);
                break;
            case 'task_completion':
                this.handleTaskCompletion(agent_id, content);
                break;
            case 'error_report':
                this.handleErrorReport(agent_id, content);
                break;
            case 'request_instruction':
                this.handleInstructionRequest(agent_id, content);
                break;
            case 'performance_metrics':
                this.handlePerformanceMetrics(agent_id, content);
                break;
            default:
                console.log(`Unknown message type from ${agent_id}: ${message_type}`);
        }

        // Broadcast to dashboard components
        this.broadcastAgentUpdate(agent_id, message_type, content, priority);
    }

    /**
     * Handle inter-agent communications
     */
    handleInterAgentCommunication(payload, meta) {
        const { source_agent, target_agent, message_type, content, timestamp } = payload;
        
        // Log inter-agent communication
        console.log(`Inter-agent comm: ${source_agent} → ${target_agent}: ${message_type}`);
        
        // Update both agents' communication logs
        this.logAgentCommunication(source_agent, target_agent, message_type, content, timestamp);
        
        // Broadcast to monitoring components
        this.broadcastInterAgentComm(source_agent, target_agent, message_type, content);
    }

    /**
     * Send command to specific agent
     */
    async sendAgentCommand(agentId, command, parameters = {}) {
        const message = {
            type: 'agent_command',
            payload: {
                target_agent: agentId,
                command: command,
                parameters: parameters,
                timestamp: new Date().toISOString(),
                message_id: this.generateMessageId()
            }
        };

        if (this.isConnected) {
            webSocketService.send(WEBSOCKET_CHANNELS.AGENT_COMMUNICATIONS, message);
        } else {
            this.messageQueue.push(message);
        }

        // Log command sending
        await this.logOutgoingCommand(agentId, command, parameters);
    }

    /**
     * Broadcast message to all agents in department
     */
    async broadcastToAgents(department, message, priority = 'normal') {
        const broadcastMessage = {
            type: 'department_broadcast',
            payload: {
                target_department: department,
                message: message,
                priority: priority,
                timestamp: new Date().toISOString(),
                message_id: this.generateMessageId()
            }
        };

        if (this.isConnected) {
            webSocketService.send(WEBSOCKET_CHANNELS.AGENT_COMMUNICATIONS, broadcastMessage);
        } else {
            this.messageQueue.push(broadcastMessage);
        }
    }

    /**
     * Request agent status update
     */
    async requestAgentStatus(agentId) {
        await this.sendAgentCommand(agentId, 'status_request', {
            include_metrics: true,
            include_current_tasks: true
        });
    }

    /**
     * Emergency agent shutdown
     */
    async emergencyAgentShutdown(agentId, reason) {
        await this.sendAgentCommand(agentId, 'emergency_shutdown', {
            reason: reason,
            immediate: true,
            save_state: true
        });
    }

    /**
     * Restart agent
     */
    async restartAgent(agentId, config = {}) {
        await this.sendAgentCommand(agentId, 'restart', {
            config: config,
            preserve_context: true
        });
    }

    /**
     * Handle agent status updates
     */
    handleStatusUpdate(agentId, content) {
        this.updateAgentStatus(agentId, {
            status: content.status,
            health_score: content.health_score,
            current_task: content.current_task,
            performance_metrics: content.performance_metrics,
            last_update: new Date().toISOString()
        });
    }

    /**
     * Handle task completion notifications
     */
    handleTaskCompletion(agentId, content) {
        const { task_id, result, duration, success } = content;
        
        // Update task tracking
        this.updateTaskCompletion(agentId, task_id, result, duration, success);
        
        // Notify relevant components
        this.broadcastTaskCompletion(agentId, task_id, result, success);
    }

    /**
     * Handle agent error reports
     */
    handleErrorReport(agentId, content) {
        const { error_type, error_message, context, severity = 'medium' } = content;
        
        // Log error
        console.error(`Agent ${agentId} error [${severity}]: ${error_message}`);
        
        // Update agent status
        this.updateAgentStatus(agentId, {
            status: severity === 'high' ? 'error' : 'warning',
            last_error: {
                type: error_type,
                message: error_message,
                timestamp: new Date().toISOString(),
                severity: severity
            }
        });

        // Broadcast error alert
        this.broadcastAgentError(agentId, error_type, error_message, severity);
    }

    /**
     * Handle agent instruction requests
     */
    handleInstructionRequest(agentId, content) {
        const { request_type, context, urgency = 'normal' } = content;
        
        // Broadcast instruction request to dashboard
        this.broadcastInstructionRequest(agentId, request_type, context, urgency);
    }

    /**
     * Handle performance metrics
     */
    handlePerformanceMetrics(agentId, content) {
        this.updateAgentStatus(agentId, {
            performance_metrics: content,
            metrics_timestamp: new Date().toISOString()
        });
    }

    /**
     * Update agent status in registry
     */
    updateAgentStatus(agentId, updates) {
        const current = this.agentRegistry.get(agentId) || {};
        const updated = { ...current, ...updates, last_seen: new Date().toISOString() };
        
        this.agentRegistry.set(agentId, updated);
        
        // Persist to database
        EnterpriseDatabase.updateAgentStatus(agentId, updated);
    }

    /**
     * Log agent communication
     */
    async logAgentCommunication(sourceAgent, targetAgent, messageType, content, timestamp) {
        try {
            await EnterpriseDatabase.logAgentCommunication({
                source_agent: sourceAgent,
                target_agent: targetAgent,
                message_type: messageType,
                content: content,
                timestamp: timestamp
            });
        } catch (error) {
            console.error('Failed to log agent communication:', error);
        }
    }

    /**
     * Log outgoing command
     */
    async logOutgoingCommand(agentId, command, parameters) {
        try {
            await EnterpriseDatabase.logAgentCommand({
                target_agent: agentId,
                command: command,
                parameters: parameters,
                timestamp: new Date().toISOString(),
                source: 'dashboard'
            });
        } catch (error) {
            console.error('Failed to log outgoing command:', error);
        }
    }

    /**
     * Broadcast agent update to dashboard
     */
    broadcastAgentUpdate(agentId, messageType, content, priority) {
        const event = new CustomEvent('agent-update', {
            detail: {
                agent_id: agentId,
                message_type: messageType,
                content: content,
                priority: priority,
                timestamp: new Date().toISOString()
            }
        });
        window.dispatchEvent(event);
    }

    /**
     * Broadcast inter-agent communication
     */
    broadcastInterAgentComm(sourceAgent, targetAgent, messageType, content) {
        const event = new CustomEvent('inter-agent-communication', {
            detail: {
                source_agent: sourceAgent,
                target_agent: targetAgent,
                message_type: messageType,
                content: content,
                timestamp: new Date().toISOString()
            }
        });
        window.dispatchEvent(event);
    }

    /**
     * Broadcast task completion
     */
    broadcastTaskCompletion(agentId, taskId, result, success) {
        const event = new CustomEvent('task-completion', {
            detail: {
                agent_id: agentId,
                task_id: taskId,
                result: result,
                success: success,
                timestamp: new Date().toISOString()
            }
        });
        window.dispatchEvent(event);
    }

    /**
     * Broadcast agent error
     */
    broadcastAgentError(agentId, errorType, errorMessage, severity) {
        const event = new CustomEvent('agent-error', {
            detail: {
                agent_id: agentId,
                error_type: errorType,
                error_message: errorMessage,
                severity: severity,
                timestamp: new Date().toISOString()
            }
        });
        window.dispatchEvent(event);
    }

    /**
     * Broadcast instruction request
     */
    broadcastInstructionRequest(agentId, requestType, context, urgency) {
        const event = new CustomEvent('instruction-request', {
            detail: {
                agent_id: agentId,
                request_type: requestType,
                context: context,
                urgency: urgency,
                timestamp: new Date().toISOString()
            }
        });
        window.dispatchEvent(event);
    }

    /**
     * Process queued messages
     */
    processMessageQueue() {
        while (this.messageQueue.length > 0 && this.isConnected) {
            const message = this.messageQueue.shift();
            webSocketService.send(WEBSOCKET_CHANNELS.AGENT_COMMUNICATIONS, message);
        }
    }

    /**
     * Start heartbeat monitoring
     */
    startHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
        }

        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected) {
                webSocketService.send(WEBSOCKET_CHANNELS.AGENT_COMMUNICATIONS, {
                    type: 'heartbeat',
                    timestamp: new Date().toISOString()
                });
            }
        }, 30000);
    }

    /**
     * Schedule reconnection attempt
     */
    scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached for Agent Communication Bridge');
            return;
        }

        const delay = Math.pow(2, this.reconnectAttempts) * 1000;
        setTimeout(() => {
            this.reconnectAttempts++;
            this.connect();
        }, delay);
    }

    /**
     * Handle WebSocket messages
     */
    handleWebSocketMessage(type, payload) {
        switch (type) {
            case 'connection_confirmed':
                this.isConnected = true;
                this.reconnectAttempts = 0;
                break;
            case 'connection_lost':
                this.isConnected = false;
                break;
            default:
                console.log(`Unhandled WebSocket message type: ${type}`);
        }
    }

    /**
     * Generate unique message ID
     */
    generateMessageId() {
        return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Get agent registry
     */
    getAgentRegistry() {
        return new Map(this.agentRegistry);
    }

    /**
     * Get specific agent status
     */
    getAgentStatus(agentId) {
        return this.agentRegistry.get(agentId) || null;
    }

    /**
     * Get connection status
     */
    getConnectionStatus() {
        return {
            isConnected: this.isConnected,
            registeredAgents: this.agentRegistry.size,
            queuedMessages: this.messageQueue.length,
            reconnectAttempts: this.reconnectAttempts
        };
    }

    /**
     * Cleanup resources
     */
    cleanup() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
        }
        
        this.isConnected = false;
        this.agentRegistry.clear();
        this.messageQueue = [];
    }
}

// Create singleton instance
const agentCommunicationBridge = new AgentCommunicationBridge();

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    agentCommunicationBridge.cleanup();
});

export default agentCommunicationBridge;
