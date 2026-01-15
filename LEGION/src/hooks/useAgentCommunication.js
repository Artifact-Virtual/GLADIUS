/**
 * React Hook for Agent Communication
 * Provides React integration for agent management and communication
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import agentCommunicationBridge from '../services/AgentCommunicationBridge';

/**
 * Hook for agent communication management
 */
export const useAgentCommunication = () => {
    const [connectionStatus, setConnectionStatus] = useState(agentCommunicationBridge.getConnectionStatus());
    const [agentRegistry, setAgentRegistry] = useState(new Map());
    const [recentMessages, setRecentMessages] = useState([]);
    const [recentErrors, setRecentErrors] = useState([]);
    const [instructionRequests, setInstructionRequests] = useState([]);
    
    const maxRecentMessages = 50;
    const maxRecentErrors = 20;
    const maxInstructionRequests = 10;

    // Update connection status periodically
    useEffect(() => {
        const interval = setInterval(() => {
            setConnectionStatus(agentCommunicationBridge.getConnectionStatus());
            setAgentRegistry(agentCommunicationBridge.getAgentRegistry());
        }, 2000);

        return () => clearInterval(interval);
    }, []);

    // Agent update event listener
    useEffect(() => {
        const handleAgentUpdate = (event) => {
            const { agent_id, message_type, content, priority, timestamp } = event.detail;
            
            const newMessage = {
                id: `${agent_id}_${timestamp}`,
                agent_id,
                message_type,
                content,
                priority,
                timestamp
            };

            setRecentMessages(prev => {
                const updated = [newMessage, ...prev].slice(0, maxRecentMessages);
                return updated;
            });
        };

        window.addEventListener('agent-update', handleAgentUpdate);
        return () => window.removeEventListener('agent-update', handleAgentUpdate);
    }, []);

    // Agent error event listener
    useEffect(() => {
        const handleAgentError = (event) => {
            const { agent_id, error_type, error_message, severity, timestamp } = event.detail;
            
            const newError = {
                id: `${agent_id}_${timestamp}`,
                agent_id,
                error_type,
                error_message,
                severity,
                timestamp
            };

            setRecentErrors(prev => {
                const updated = [newError, ...prev].slice(0, maxRecentErrors);
                return updated;
            });
        };

        window.addEventListener('agent-error', handleAgentError);
        return () => window.removeEventListener('agent-error', handleAgentError);
    }, []);

    // Instruction request event listener
    useEffect(() => {
        const handleInstructionRequest = (event) => {
            const { agent_id, request_type, context, urgency, timestamp } = event.detail;
            
            const newRequest = {
                id: `${agent_id}_${timestamp}`,
                agent_id,
                request_type,
                context,
                urgency,
                timestamp,
                status: 'pending'
            };

            setInstructionRequests(prev => {
                const updated = [newRequest, ...prev].slice(0, maxInstructionRequests);
                return updated;
            });
        };

        window.addEventListener('instruction-request', handleInstructionRequest);
        return () => window.removeEventListener('instruction-request', handleInstructionRequest);
    }, []);

    // Command sending functions
    const sendAgentCommand = useCallback(async (agentId, command, parameters = {}) => {
        try {
            await agentCommunicationBridge.sendAgentCommand(agentId, command, parameters);
            return { success: true };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }, []);

    const broadcastToAgents = useCallback(async (department, message, priority = 'normal') => {
        try {
            await agentCommunicationBridge.broadcastToAgents(department, message, priority);
            return { success: true };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }, []);

    const requestAgentStatus = useCallback(async (agentId) => {
        try {
            await agentCommunicationBridge.requestAgentStatus(agentId);
            return { success: true };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }, []);

    const emergencyAgentShutdown = useCallback(async (agentId, reason) => {
        try {
            await agentCommunicationBridge.emergencyAgentShutdown(agentId, reason);
            return { success: true };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }, []);

    const restartAgent = useCallback(async (agentId, config = {}) => {
        try {
            await agentCommunicationBridge.restartAgent(agentId, config);
            return { success: true };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }, []);

    // Helper functions
    const getAgentStatus = useCallback((agentId) => {
        return agentCommunicationBridge.getAgentStatus(agentId);
    }, []);

    const getAgentsByDepartment = useCallback((department) => {
        const agents = [];
        for (const [agentId, agentData] of agentRegistry) {
            if (agentData.department === department) {
                agents.push({ id: agentId, ...agentData });
            }
        }
        return agents;
    }, [agentRegistry]);

    const getActiveAgents = useCallback(() => {
        const activeAgents = [];
        for (const [agentId, agentData] of agentRegistry) {
            if (agentData.status === 'active' || agentData.status === 'operational') {
                activeAgents.push({ id: agentId, ...agentData });
            }
        }
        return activeAgents;
    }, [agentRegistry]);

    const getAgentsWithErrors = useCallback(() => {
        const errorAgents = [];
        for (const [agentId, agentData] of agentRegistry) {
            if (agentData.status === 'error' || agentData.last_error) {
                errorAgents.push({ id: agentId, ...agentData });
            }
        }
        return errorAgents;
    }, [agentRegistry]);

    const markInstructionRequestHandled = useCallback((requestId) => {
        setInstructionRequests(prev => 
            prev.map(req => 
                req.id === requestId 
                    ? { ...req, status: 'handled', handled_at: new Date().toISOString() }
                    : req
            )
        );
    }, []);

    const dismissError = useCallback((errorId) => {
        setRecentErrors(prev => prev.filter(error => error.id !== errorId));
    }, []);

    return {
        // Connection status
        connectionStatus,
        isConnected: connectionStatus.isConnected,
        
        // Agent data
        agentRegistry,
        registeredAgentsCount: connectionStatus.registeredAgents,
        
        // Recent activity
        recentMessages,
        recentErrors,
        instructionRequests,
        
        // Command functions
        sendAgentCommand,
        broadcastToAgents,
        requestAgentStatus,
        emergencyAgentShutdown,
        restartAgent,
        
        // Helper functions
        getAgentStatus,
        getAgentsByDepartment,
        getActiveAgents,
        getAgentsWithErrors,
        markInstructionRequestHandled,
        dismissError,
        
        // Statistics
        stats: {
            totalAgents: agentRegistry.size,
            activeAgents: getActiveAgents().length,
            errorAgents: getAgentsWithErrors().length,
            pendingRequests: instructionRequests.filter(req => req.status === 'pending').length,
            queuedMessages: connectionStatus.queuedMessages
        }
    };
};

/**
 * Hook for monitoring specific agent
 */
export const useAgentMonitoring = (agentId) => {
    const { agentRegistry, recentMessages, recentErrors, getAgentStatus } = useAgentCommunication();
    const [agentHistory, setAgentHistory] = useState([]);
    
    const agent = getAgentStatus(agentId);
    
    // Filter messages and errors for this agent
    const agentMessages = recentMessages.filter(msg => msg.agent_id === agentId);
    const agentErrors = recentErrors.filter(error => error.agent_id === agentId);
    
    // Update agent history
    useEffect(() => {
        if (agent) {
            setAgentHistory(prev => {
                const newEntry = {
                    timestamp: new Date().toISOString(),
                    status: agent.status,
                    health_score: agent.health_score,
                    current_task: agent.current_task
                };
                
                // Only add if status changed
                const lastEntry = prev[prev.length - 1];
                if (!lastEntry || lastEntry.status !== agent.status) {
                    return [...prev, newEntry].slice(-100); // Keep last 100 entries
                }
                
                return prev;
            });
        }
    }, [agent]);

    return {
        agent,
        agentMessages,
        agentErrors,
        agentHistory,
        isOnline: agent?.status === 'active' || agent?.status === 'operational',
        hasErrors: agentErrors.length > 0,
        lastSeen: agent?.last_seen,
        healthScore: agent?.health_score || 0
    };
};

/**
 * Hook for department-level agent management
 */
export const useDepartmentAgents = (department) => {
    const { getAgentsByDepartment, broadcastToAgents, recentMessages, recentErrors } = useAgentCommunication();
    
    const departmentAgents = getAgentsByDepartment(department);
    
    // Filter messages and errors for this department
    const departmentMessages = recentMessages.filter(msg => {
        const agent = departmentAgents.find(agent => agent.id === msg.agent_id);
        return agent !== undefined;
    });
    
    const departmentErrors = recentErrors.filter(error => {
        const agent = departmentAgents.find(agent => agent.id === error.agent_id);
        return agent !== undefined;
    });

    const broadcastToDepartment = useCallback((message, priority = 'normal') => {
        return broadcastToAgents(department, message, priority);
    }, [department, broadcastToAgents]);

    // Department statistics
    const stats = {
        totalAgents: departmentAgents.length,
        activeAgents: departmentAgents.filter(agent => agent.status === 'active' || agent.status === 'operational').length,
        errorAgents: departmentAgents.filter(agent => agent.status === 'error').length,
        warningAgents: departmentAgents.filter(agent => agent.status === 'warning').length,
        maintenanceAgents: departmentAgents.filter(agent => agent.status === 'maintenance').length,
        averageHealthScore: departmentAgents.reduce((sum, agent) => sum + (agent.health_score || 0), 0) / departmentAgents.length || 0
    };

    return {
        departmentAgents,
        departmentMessages,
        departmentErrors,
        broadcastToDepartment,
        stats
    };
};
