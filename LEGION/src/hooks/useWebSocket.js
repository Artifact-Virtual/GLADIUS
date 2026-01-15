/**
 * React Hook for WebSocket Enterprise Data Subscriptions
 * Provides easy-to-use React integration for real-time data
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import webSocketService, { WEBSOCKET_CHANNELS, DATA_TYPES } from '../services/WebSocketService';

/**
 * Hook for subscribing to WebSocket data streams
 */
export const useWebSocket = (channel, dataTypes = [], options = {}) => {
    const [data, setData] = useState({});
    const [connectionStatus, setConnectionStatus] = useState('disconnected');
    const [error, setError] = useState(null);
    const [lastUpdate, setLastUpdate] = useState(null);
    
    const dataRef = useRef(data);
    const optionsRef = useRef(options);
    
    // Update refs when data changes
    useEffect(() => {
        dataRef.current = data;
    }, [data]);
    
    useEffect(() => {
        optionsRef.current = options;
    }, [options]);

    // Message handler callback
    const handleMessage = useCallback((payload, meta) => {
        setData(prevData => ({
            ...prevData,
            [meta.type]: {
                data: payload,
                timestamp: meta.timestamp || Date.now(),
                received_at: Date.now()
            }
        }));
        setLastUpdate(Date.now());
        setError(null);
    }, []);

    // Connect and subscribe to data types
    useEffect(() => {
        if (!channel || dataTypes.length === 0) return;

        try {
            // Connect to WebSocket
            webSocketService.connect(channel, options);
            
            // Subscribe to each data type
            dataTypes.forEach(dataType => {
                webSocketService.subscribe(channel, dataType, handleMessage);
            });

            // Monitor connection status
            const statusInterval = setInterval(() => {
                const status = webSocketService.getConnectionStatus(channel);
                setConnectionStatus(status);
            }, 1000);

            // Cleanup function
            return () => {
                clearInterval(statusInterval);
                dataTypes.forEach(dataType => {
                    webSocketService.unsubscribe(channel, dataType);
                });
            };

        } catch (err) {
            setError(err);
            setConnectionStatus('error');
        }
    }, [channel, JSON.stringify(dataTypes), handleMessage]);

    // Send message function
    const sendMessage = useCallback((message) => {
        try {
            webSocketService.send(channel, message);
        } catch (err) {
            setError(err);
        }
    }, [channel]);

    // Reconnect function
    const reconnect = useCallback(() => {
        try {
            webSocketService.disconnect(channel);
            setTimeout(() => {
                webSocketService.connect(channel, optionsRef.current);
                dataTypes.forEach(dataType => {
                    webSocketService.subscribe(channel, dataType, handleMessage);
                });
            }, 1000);
        } catch (err) {
            setError(err);
        }
    }, [channel, dataTypes, handleMessage]);

    return {
        data,
        connectionStatus,
        error,
        lastUpdate,
        sendMessage,
        reconnect,
        isConnected: connectionStatus === 'connected',
        isConnecting: connectionStatus === 'connecting'
    };
};

/**
 * Hook for system status monitoring
 */
export const useSystemStatus = () => {
    return useWebSocket(
        WEBSOCKET_CHANNELS.SYSTEM_STATUS,
        [DATA_TYPES.SYSTEM_HEALTH, DATA_TYPES.SERVICE_STATUS, DATA_TYPES.SECURITY_STATUS],
        { autoReconnect: true, heartbeat: true }
    );
};

/**
 * Hook for agent health monitoring
 */
export const useAgentHealth = () => {
    return useWebSocket(
        WEBSOCKET_CHANNELS.AGENT_HEALTH,
        [DATA_TYPES.AGENT_STATUS_UPDATE, DATA_TYPES.AGENT_PERFORMANCE, DATA_TYPES.AGENT_ERROR],
        { autoReconnect: true, heartbeat: true }
    );
};

/**
 * Hook for workflow execution monitoring
 */
export const useWorkflowExecution = () => {
    return useWebSocket(
        WEBSOCKET_CHANNELS.WORKFLOW_EXECUTION,
        [
            DATA_TYPES.WORKFLOW_STARTED,
            DATA_TYPES.WORKFLOW_PROGRESS,
            DATA_TYPES.WORKFLOW_COMPLETED,
            DATA_TYPES.WORKFLOW_FAILED
        ],
        { autoReconnect: true, heartbeat: true }
    );
};

/**
 * Hook for performance metrics monitoring
 */
export const usePerformanceMetrics = () => {
    return useWebSocket(
        WEBSOCKET_CHANNELS.PERFORMANCE_METRICS,
        [
            DATA_TYPES.CPU_USAGE,
            DATA_TYPES.MEMORY_USAGE,
            DATA_TYPES.NETWORK_IO,
            DATA_TYPES.DATABASE_PERFORMANCE
        ],
        { autoReconnect: true, heartbeat: true }
    );
};

/**
 * Hook for system alerts monitoring
 */
export const useSystemAlerts = () => {
    return useWebSocket(
        WEBSOCKET_CHANNELS.ALERTS,
        [
            DATA_TYPES.SYSTEM_ALERT,
            DATA_TYPES.SECURITY_ALERT,
            DATA_TYPES.PERFORMANCE_ALERT
        ],
        { autoReconnect: true, heartbeat: true }
    );
};

/**
 * Hook for database status monitoring
 */
export const useDatabaseStatus = () => {
    return useWebSocket(
        WEBSOCKET_CHANNELS.DATABASE_STATUS,
        [DATA_TYPES.DATABASE_CONNECTION, DATA_TYPES.QUERY_PERFORMANCE],
        { autoReconnect: true, heartbeat: true }
    );
};

/**
 * Hook for agent communications monitoring
 */
export const useAgentCommunications = () => {
    return useWebSocket(
        WEBSOCKET_CHANNELS.AGENT_COMMUNICATIONS,
        [DATA_TYPES.AGENT_MESSAGE, DATA_TYPES.INTER_AGENT_COMM],
        { autoReconnect: true, heartbeat: true }
    );
};

/**
 * Hook for comprehensive real-time monitoring
 * Combines multiple data streams for dashboard views
 */
export const useRealTimeMonitoring = () => {
    const systemStatus = useSystemStatus();
    const agentHealth = useAgentHealth();
    const workflowExecution = useWorkflowExecution();
    const performanceMetrics = usePerformanceMetrics();
    const systemAlerts = useSystemAlerts();
    const databaseStatus = useDatabaseStatus();

    const overallConnectionStatus = [
        systemStatus.connectionStatus,
        agentHealth.connectionStatus,
        workflowExecution.connectionStatus,
        performanceMetrics.connectionStatus,
        systemAlerts.connectionStatus,
        databaseStatus.connectionStatus
    ];

    const isFullyConnected = overallConnectionStatus.every(status => status === 'connected');
    const hasErrors = [
        systemStatus.error,
        agentHealth.error,
        workflowExecution.error,
        performanceMetrics.error,
        systemAlerts.error,
        databaseStatus.error
    ].some(error => error !== null);

    const lastUpdate = Math.max(
        systemStatus.lastUpdate || 0,
        agentHealth.lastUpdate || 0,
        workflowExecution.lastUpdate || 0,
        performanceMetrics.lastUpdate || 0,
        systemAlerts.lastUpdate || 0,
        databaseStatus.lastUpdate || 0
    );

    return {
        systemStatus: systemStatus.data,
        agentHealth: agentHealth.data,
        workflowExecution: workflowExecution.data,
        performanceMetrics: performanceMetrics.data,
        systemAlerts: systemAlerts.data,
        databaseStatus: databaseStatus.data,
        
        connectionStatuses: {
            systemStatus: systemStatus.connectionStatus,
            agentHealth: agentHealth.connectionStatus,
            workflowExecution: workflowExecution.connectionStatus,
            performanceMetrics: performanceMetrics.connectionStatus,
            systemAlerts: systemAlerts.connectionStatus,
            databaseStatus: databaseStatus.connectionStatus
        },
        
        isFullyConnected,
        hasErrors,
        lastUpdate,
        
        // Utility functions
        reconnectAll: () => {
            systemStatus.reconnect();
            agentHealth.reconnect();
            workflowExecution.reconnect();
            performanceMetrics.reconnect();
            systemAlerts.reconnect();
            databaseStatus.reconnect();
        }
    };
};

/**
 * Hook for WebSocket connection status monitoring
 */
export const useWebSocketStatus = () => {
    const [allStatuses, setAllStatuses] = useState({});
    const [lastCheck, setLastCheck] = useState(Date.now());

    useEffect(() => {
        const interval = setInterval(() => {
            const statuses = webSocketService.getAllConnectionStatuses();
            setAllStatuses(statuses);
            setLastCheck(Date.now());
        }, 2000);

        return () => clearInterval(interval);
    }, []);

    const connectedCount = Object.values(allStatuses).filter(status => status === 'connected').length;
    const totalCount = Object.keys(allStatuses).length;
    const isAllConnected = totalCount > 0 && connectedCount === totalCount;

    return {
        statuses: allStatuses,
        connectedCount,
        totalCount,
        isAllConnected,
        lastCheck,
        connectionHealth: totalCount > 0 ? (connectedCount / totalCount) * 100 : 0
    };
};
