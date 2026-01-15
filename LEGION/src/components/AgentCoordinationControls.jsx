import React, { useState, useEffect } from 'react';
import RealTimeAPIService from '../services/RealTimeAPIService';

/**
 * Agent Coordination Controls Component
 * Manages agent coordination, task distribution, and team workflows
 */
const AgentCoordinationControls = () => {
  const [coordinationData, setCoordinationData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    const fetchCoordinationData = async () => {
      try {
        setIsLoading(true);
        const [agentHealth, workflowStatus] = await Promise.allSettled([
          RealTimeAPIService.makeRequest('/api/enterprise/agent-health'),
          RealTimeAPIService.makeRequest('/api/enterprise/workflow-status')
        ]);

        const data = {
          agents: agentHealth.value || null,
          workflows: workflowStatus.value || null
        };

        setCoordinationData(data);
        setConnectionStatus('connected');
        setLastUpdate(new Date().toISOString());
      } catch (error) {
        console.error('Failed to fetch coordination data:', error);
        setConnectionStatus('error');
      } finally {
        setIsLoading(false);
      }
    };

    fetchCoordinationData();
    const interval = setInterval(fetchCoordinationData, 3000); // Update every 3 seconds
    
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className="theme-card">
        <div className="theme-loading"></div>
        <p>Loading agent coordination data...</p>
      </div>
    );
  }

  return (
    <div className="agent-coordination-controls">
      <div className="theme-card">
        <h3>🤝 Agent Coordination Controls</h3>
        <div className="connection-status">
          Status: <span className={`theme-status-${connectionStatus === 'connected' ? 'operational' : 'error'}`}>
            {connectionStatus}
          </span>
          {lastUpdate && (
            <span style={{ marginLeft: '10px', fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>
              Last updated: {new Date(lastUpdate).toLocaleTimeString()}
            </span>
          )}
        </div>
        
        {/* Agent Status Grid */}
        {coordinationData?.agents?.agents?.length > 0 ? (
          <div className="agent-grid">
            <h4>Active Agents</h4>
            <div className="theme-grid theme-grid-cols-3">
              {coordinationData.agents.agents.slice(0, 9).map((agent, index) => (
                <div key={agent.id || index} className="theme-metric-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: '500' }}>
                      {agent.name || agent.id || `Agent ${index + 1}`}
                    </span>
                    <span className={`theme-status-${agent.status === 'operational' ? 'operational' : 
                      agent.status === 'warning' ? 'warning' : 'error'}`}>
                      ● {agent.status || 'unknown'}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                    Department: {agent.department || 'Unknown'}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>
                    Tasks: {agent.tasks_completed || 0} | Load: {agent.current_load || 0}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="theme-text-secondary">No agent data available</div>
        )}

        {/* Workflow Coordination */}
        {coordinationData?.workflows?.length > 0 ? (
          <div className="workflow-coordination theme-mt-lg">
            <h4>Active Workflows</h4>
            <div className="theme-grid theme-grid-cols-2">
              {coordinationData.workflows.slice(0, 6).map((workflow, index) => (
                <div key={workflow.id || index} className="theme-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: '500' }}>
                      {workflow.name || `Workflow ${index + 1}`}
                    </span>
                    <span className={`theme-status-${workflow.status === 'running' ? 'operational' : 
                      workflow.status === 'pending' ? 'warning' : 'error'}`}>
                      ● {workflow.status || 'unknown'}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                    Progress: {workflow.progress || 0}% | Agents: {workflow.assigned_agents || 0}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>
                    Started: {workflow.start_time ? new Date(workflow.start_time).toLocaleString() : 'Unknown'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="theme-text-secondary theme-mt-lg">No workflow data available</div>
        )}
      </div>
    </div>
  );
};

export default AgentCoordinationControls;
