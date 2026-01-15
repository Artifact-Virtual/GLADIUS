import React, { useState, useEffect } from 'react';

/**
 * EmergencyControls - Critical system override and emergency management interface
 * 
 * Provides emergency system controls, shutdown procedures, override capabilities,
 * and critical system recovery options for enterprise operations.
 */
const EmergencyControls = ({ 
  systemStatus = {},
  emergencyMode = false,
  userRole = 'operator', // 'operator', 'admin', 'emergency'
  onEmergencyAction = () => {} 
}) => {
  const [confirmationMode, setConfirmationMode] = useState(null);
  const [emergencyCode, setEmergencyCode] = useState('');
  const [shutdownTimer, setShutdownTimer] = useState(null);
  const [overrideActive, setOverrideActive] = useState(false);
  const [emergencyLog, setEmergencyLog] = useState([]);

  // Emergency action types with risk levels
  const emergencyActions = {
    // System Control Actions
    emergency_stop: {
      label: 'EMERGENCY STOP',
      icon: '🛑',
      description: 'Immediately halt all system operations',
      riskLevel: 'critical',
      requiresCode: true,
      minRole: 'admin'
    },
    system_shutdown: {
      label: 'SYSTEM SHUTDOWN',
      icon: '⚡',
      description: 'Graceful system shutdown with data preservation',
      riskLevel: 'high',
      requiresCode: true,
      minRole: 'admin'
    },
    restart_services: {
      label: 'RESTART SERVICES',
      icon: '🔄',
      description: 'Restart all enterprise services',
      riskLevel: 'medium',
      requiresCode: false,
      minRole: 'operator'
    },
    
    // Agent Control Actions
    pause_all_agents: {
      label: 'PAUSE ALL AGENTS',
      icon: '⏸️',
      description: 'Temporarily pause all agent operations',
      riskLevel: 'medium',
      requiresCode: false,
      minRole: 'operator'
    },
    kill_rogue_agents: {
      label: 'KILL ROGUE AGENTS',
      icon: '💀',
      description: 'Forcefully terminate malfunctioning agents',
      riskLevel: 'high',
      requiresCode: true,
      minRole: 'admin'
    },
    
    // Database Actions
    lock_databases: {
      label: 'LOCK DATABASES',
      icon: '🔒',
      description: 'Lock all database connections (read-only mode)',
      riskLevel: 'high',
      requiresCode: true,
      minRole: 'admin'
    },
    backup_critical_data: {
      label: 'EMERGENCY BACKUP',
      icon: '💾',
      description: 'Create immediate backup of critical data',
      riskLevel: 'low',
      requiresCode: false,
      minRole: 'operator'
    },
    
    // Network Actions
    isolate_network: {
      label: 'NETWORK ISOLATION',
      icon: '🌐',
      description: 'Isolate system from external networks',
      riskLevel: 'critical',
      requiresCode: true,
      minRole: 'emergency'
    },
    throttle_connections: {
      label: 'THROTTLE CONNECTIONS',
      icon: '🚥',
      description: 'Limit network connections to essential only',
      riskLevel: 'medium',
      requiresCode: false,
      minRole: 'operator'
    },
    
    // Recovery Actions
    restore_from_backup: {
      label: 'RESTORE SYSTEM',
      icon: '📥',
      description: 'Restore system from latest backup',
      riskLevel: 'critical',
      requiresCode: true,
      minRole: 'emergency'
    },
    reset_to_safe_mode: {
      label: 'SAFE MODE',
      icon: '🛡️',
      description: 'Reset system to safe operational mode',
      riskLevel: 'high',
      requiresCode: true,
      minRole: 'admin'
    }
  };

  // Get risk level styling
  const getRiskStyling = (riskLevel) => {
    switch (riskLevel) {
      case 'critical':
        return {
          bgColor: 'rgba(220, 53, 69, 0.1)',
          borderColor: '#dc3545',
          textColor: '#ff6b7a'
        };
      case 'high':
        return {
          bgColor: 'rgba(255, 193, 7, 0.1)',
          borderColor: '#ffc107',
          textColor: '#ffd93d'
        };
      case 'medium':
        return {
          bgColor: 'rgba(23, 162, 184, 0.1)',
          borderColor: '#17a2b8',
          textColor: '#5bc0de'
        };
      case 'low':
        return {
          bgColor: 'rgba(40, 167, 69, 0.1)',
          borderColor: '#28a745',
          textColor: '#7ee88f'
        };
      default:
        return {
          bgColor: 'rgba(108, 117, 125, 0.1)',
          borderColor: '#6c757d',
          textColor: '#adb5bd'
        };
    }
  };

  // Check if user can perform action
  const canPerformAction = (action) => {
    const roleHierarchy = { operator: 1, admin: 2, emergency: 3 };
    return roleHierarchy[userRole] >= roleHierarchy[action.minRole];
  };

  // Handle emergency action initiation
  const initiateAction = (actionKey) => {
    const action = emergencyActions[actionKey];
    
    if (!canPerformAction(action)) {
      addToEmergencyLog(`ACCESS DENIED: Insufficient privileges for ${action.label}`, 'error');
      return;
    }

    setConfirmationMode(actionKey);
    if (action.requiresCode) {
      setEmergencyCode('');
    }
  };

  // Execute emergency action
  const executeAction = (actionKey) => {
    const action = emergencyActions[actionKey];
    
    if (action.requiresCode && !emergencyCode) {
      addToEmergencyLog(`VERIFICATION REQUIRED: Emergency code needed for ${action.label}`, 'warning');
      return;
    }

    addToEmergencyLog(`EXECUTING: ${action.label} - ${action.description}`, 'info');
    onEmergencyAction(actionKey, {
      code: emergencyCode,
      timestamp: new Date().toISOString(),
      user: userRole
    });
    
    setConfirmationMode(null);
    setEmergencyCode('');

    // Special handling for shutdown timer
    if (actionKey === 'system_shutdown') {
      setShutdownTimer(30); // 30 second countdown
    }
  };

  // Add entry to emergency log
  const addToEmergencyLog = (message, type) => {
    const logEntry = {
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString(),
      message,
      type,
      user: userRole
    };
    
    setEmergencyLog(prev => [logEntry, ...prev.slice(0, 19)]); // Keep last 20 entries
  };

  // Handle shutdown timer
  useEffect(() => {
    if (shutdownTimer > 0) {
      const interval = setInterval(() => {
        setShutdownTimer(prev => prev - 1);
      }, 1000);
      return () => clearInterval(interval);
    } else if (shutdownTimer === 0) {
      addToEmergencyLog('SYSTEM SHUTDOWN COMPLETED', 'critical');
      setShutdownTimer(null);
    }
  }, [shutdownTimer]);

  // Cancel confirmation
  const cancelAction = () => {
    addToEmergencyLog(`CANCELLED: Emergency action cancelled by user`, 'info');
    setConfirmationMode(null);
    setEmergencyCode('');
  };

  // Get system health status
  const getSystemHealth = () => {
    const { cpu = 0, memory = 0, agents = 0, databases = 0 } = systemStatus;
    const avgHealth = (cpu + memory + agents + databases) / 4;
    
    if (avgHealth > 80) return { status: 'healthy', color: '#28a745', icon: '✅' };
    if (avgHealth > 60) return { status: 'warning', color: '#ffc107', icon: '⚠️' };
    return { status: 'critical', color: '#dc3545', icon: '🚨' };
  };

  const systemHealth = getSystemHealth();

  return (
    <div className={`emergency-controls ${emergencyMode ? 'emergency-active' : ''}`}>
      <div className="controls-header">
        <div className="header-left">
          <h3 className="controls-title">
            <span className="title-icon">🚨</span>
            Emergency Controls
          </h3>
          <div className="system-health-indicator">
            <span className="health-icon" style={{ color: systemHealth.color }}>
              {systemHealth.icon}
            </span>
            <span className="health-text" style={{ color: systemHealth.color }}>
              System: {systemHealth.status.toUpperCase()}
            </span>
            <span className="user-role">Role: {userRole.toUpperCase()}</span>
          </div>
        </div>

        <div className="emergency-status">
          {emergencyMode && (
            <div className="emergency-banner">
              <span className="emergency-icon">🚨</span>
              <span className="emergency-text">EMERGENCY MODE ACTIVE</span>
            </div>
          )}
          
          {shutdownTimer !== null && (
            <div className="shutdown-timer">
              <span className="timer-icon">⏰</span>
              <span className="timer-text">
                SHUTDOWN IN: {shutdownTimer}s
              </span>
              <button 
                className="cancel-shutdown"
                onClick={() => setShutdownTimer(null)}
              >
                CANCEL
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="controls-content">
        <div className="action-panels">
          {/* System Control Panel */}
          <div className="action-panel system-control">
            <div className="panel-header">
              <h4>System Control</h4>
              <span className="panel-description">Critical system operations</span>
            </div>
            
            <div className="action-grid">
              {['emergency_stop', 'system_shutdown', 'restart_services', 'reset_to_safe_mode'].map(actionKey => {
                const action = emergencyActions[actionKey];
                const styling = getRiskStyling(action.riskLevel);
                const canPerform = canPerformAction(action);
                
                return (
                  <button
                    key={actionKey}
                    className={`emergency-action-btn ${action.riskLevel} ${!canPerform ? 'disabled' : ''}`}
                    style={{
                      background: styling.bgColor,
                      borderColor: styling.borderColor,
                      color: canPerform ? styling.textColor : '#666'
                    }}
                    onClick={() => initiateAction(actionKey)}
                    disabled={!canPerform}
                  >
                    <span className="action-icon">{action.icon}</span>
                    <div className="action-info">
                      <span className="action-label">{action.label}</span>
                      <span className="action-description">{action.description}</span>
                    </div>
                    {action.requiresCode && (
                      <span className="code-required">🔐</span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Agent Control Panel */}
          <div className="action-panel agent-control">
            <div className="panel-header">
              <h4>Agent Control</h4>
              <span className="panel-description">Agent management and recovery</span>
            </div>
            
            <div className="action-grid">
              {['pause_all_agents', 'kill_rogue_agents'].map(actionKey => {
                const action = emergencyActions[actionKey];
                const styling = getRiskStyling(action.riskLevel);
                const canPerform = canPerformAction(action);
                
                return (
                  <button
                    key={actionKey}
                    className={`emergency-action-btn ${action.riskLevel} ${!canPerform ? 'disabled' : ''}`}
                    style={{
                      background: styling.bgColor,
                      borderColor: styling.borderColor,
                      color: canPerform ? styling.textColor : '#666'
                    }}
                    onClick={() => initiateAction(actionKey)}
                    disabled={!canPerform}
                  >
                    <span className="action-icon">{action.icon}</span>
                    <div className="action-info">
                      <span className="action-label">{action.label}</span>
                      <span className="action-description">{action.description}</span>
                    </div>
                    {action.requiresCode && (
                      <span className="code-required">🔐</span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Data & Network Panel */}
          <div className="action-panel data-network">
            <div className="panel-header">
              <h4>Data & Network</h4>
              <span className="panel-description">Database and network emergency controls</span>
            </div>
            
            <div className="action-grid">
              {['lock_databases', 'backup_critical_data', 'isolate_network', 'throttle_connections'].map(actionKey => {
                const action = emergencyActions[actionKey];
                const styling = getRiskStyling(action.riskLevel);
                const canPerform = canPerformAction(action);
                
                return (
                  <button
                    key={actionKey}
                    className={`emergency-action-btn ${action.riskLevel} ${!canPerform ? 'disabled' : ''}`}
                    style={{
                      background: styling.bgColor,
                      borderColor: styling.borderColor,
                      color: canPerform ? styling.textColor : '#666'
                    }}
                    onClick={() => initiateAction(actionKey)}
                    disabled={!canPerform}
                  >
                    <span className="action-icon">{action.icon}</span>
                    <div className="action-info">
                      <span className="action-label">{action.label}</span>
                      <span className="action-description">{action.description}</span>
                    </div>
                    {action.requiresCode && (
                      <span className="code-required">🔐</span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Recovery Panel */}
          <div className="action-panel recovery">
            <div className="panel-header">
              <h4>System Recovery</h4>
              <span className="panel-description">Disaster recovery and restoration</span>
            </div>
            
            <div className="action-grid">
              {['restore_from_backup'].map(actionKey => {
                const action = emergencyActions[actionKey];
                const styling = getRiskStyling(action.riskLevel);
                const canPerform = canPerformAction(action);
                
                return (
                  <button
                    key={actionKey}
                    className={`emergency-action-btn ${action.riskLevel} ${!canPerform ? 'disabled' : ''}`}
                    style={{
                      background: styling.bgColor,
                      borderColor: styling.borderColor,
                      color: canPerform ? styling.textColor : '#666'
                    }}
                    onClick={() => initiateAction(actionKey)}
                    disabled={!canPerform}
                  >
                    <span className="action-icon">{action.icon}</span>
                    <div className="action-info">
                      <span className="action-label">{action.label}</span>
                      <span className="action-description">{action.description}</span>
                    </div>
                    {action.requiresCode && (
                      <span className="code-required">🔐</span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Emergency Log */}
        <div className="emergency-log">
          <div className="log-header">
            <h4>Emergency Log</h4>
            <span className="log-description">Recent emergency actions and system events</span>
          </div>
          
          <div className="log-entries">
            {emergencyLog.length === 0 ? (
              <div className="no-entries">
                <span className="no-entries-icon">📋</span>
                <p>No emergency actions recorded</p>
              </div>
            ) : (
              emergencyLog.map(entry => (
                <div key={entry.id} className={`log-entry ${entry.type}`}>
                  <span className="log-timestamp">{entry.timestamp}</span>
                  <span className="log-message">{entry.message}</span>
                  <span className="log-user">{entry.user}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Confirmation Modal */}
      {confirmationMode && (
        <div className="confirmation-overlay">
          <div className="confirmation-modal">
            <div className="modal-header">
              <h3>⚠️ Confirm Emergency Action</h3>
            </div>
            
            <div className="modal-content">
              <div className="action-preview">
                <span className="action-icon-large">
                  {emergencyActions[confirmationMode].icon}
                </span>
                <div className="action-details">
                  <h4>{emergencyActions[confirmationMode].label}</h4>
                  <p>{emergencyActions[confirmationMode].description}</p>
                  <div className={`risk-level ${emergencyActions[confirmationMode].riskLevel}`}>
                    Risk Level: {emergencyActions[confirmationMode].riskLevel.toUpperCase()}
                  </div>
                </div>
              </div>

              {emergencyActions[confirmationMode].requiresCode && (
                <div className="code-input-section">
                  <label htmlFor="emergency-code">Emergency Authorization Code:</label>
                  <input
                    id="emergency-code"
                    type="password"
                    value={emergencyCode}
                    onChange={(e) => setEmergencyCode(e.target.value)}
                    placeholder="Enter emergency code"
                    className="emergency-code-input"
                    autoFocus
                  />
                </div>
              )}

              <div className="confirmation-warning">
                <strong>WARNING:</strong> This action cannot be undone. Are you sure you want to proceed?
              </div>
            </div>
            
            <div className="modal-actions">
              <button
                className="confirm-btn execute"
                onClick={() => executeAction(confirmationMode)}
                disabled={emergencyActions[confirmationMode].requiresCode && !emergencyCode}
              >
                🚨 EXECUTE ACTION
              </button>
              <button
                className="confirm-btn cancel"
                onClick={cancelAction}
              >
                ❌ CANCEL
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Override Status Indicator */}
      {overrideActive && (
        <div className="override-indicator">
          <span className="override-icon">🔓</span>
          <span className="override-text">EMERGENCY OVERRIDE ACTIVE</span>
        </div>
      )}
    </div>
  );
};

export default EmergencyControls;
