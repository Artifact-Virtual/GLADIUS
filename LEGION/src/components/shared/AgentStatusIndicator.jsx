// src/components/shared/AgentStatusIndicator.jsx
import React, { useState, useEffect } from 'react';

const AgentStatusIndicator = ({
  agentId,
  agentName,
  status = 'unknown', // 'active', 'idle', 'busy', 'offline', 'error', 'maintenance', 'unknown'
  health = 100, // 0-100 health score
  performance = null, // performance percentage
  lastActive = null,
  taskCount = 0,
  department = null,
  size = 'medium', // 'small', 'medium', 'large', 'compact'
  variant = 'default', // 'default', 'minimal', 'detailed', 'badge'
  showMetrics = true,
  showPulse = true,
  onClick = null,
  className = '',
  realTimeUpdate = false,
  customIcon = null,
  priority = 'normal', // 'low', 'normal', 'high', 'critical'
  ...props
}) => {
  const [currentStatus, setCurrentStatus] = useState(status);
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    if (realTimeUpdate && status !== currentStatus) {
      setIsUpdating(true);
      const timer = setTimeout(() => {
        setCurrentStatus(status);
        setIsUpdating(false);
      }, 300);
      return () => clearTimeout(timer);
    } else {
      setCurrentStatus(status);
    }
  }, [status, realTimeUpdate, currentStatus]);

  const getStatusConfig = () => {
    switch (currentStatus) {
      case 'active':
        return {
          color: '#28a745',
          icon: 'fas fa-circle',
          label: 'Active',
          description: 'Agent is active and processing tasks'
        };
      case 'idle':
        return {
          color: '#17a2b8',
          icon: 'fas fa-circle',
          label: 'Idle',
          description: 'Agent is idle and ready for tasks'
        };
      case 'busy':
        return {
          color: '#ffc107',
          icon: 'fas fa-circle',
          label: 'Busy',
          description: 'Agent is busy processing tasks'
        };
      case 'offline':
        return {
          color: '#6c757d',
          icon: 'fas fa-circle',
          label: 'Offline',
          description: 'Agent is offline'
        };
      case 'error':
        return {
          color: '#dc3545',
          icon: 'fas fa-exclamation-circle',
          label: 'Error',
          description: 'Agent has encountered an error'
        };
      case 'maintenance':
        return {
          color: '#fd7e14',
          icon: 'fas fa-tools',
          label: 'Maintenance',
          description: 'Agent is under maintenance'
        };
      default:
        return {
          color: '#6c757d',
          icon: 'fas fa-question-circle',
          label: 'Unknown',
          description: 'Agent status is unknown'
        };
    }
  };

  const getPriorityConfig = () => {
    switch (priority) {
      case 'critical':
        return { color: '#dc3545', border: '2px solid #dc3545' };
      case 'high':
        return { color: '#fd7e14', border: '2px solid #fd7e14' };
      case 'normal':
        return { color: '#17a2b8', border: '1px solid rgba(255, 255, 255, 0.2)' };
      case 'low':
        return { color: '#6c757d', border: '1px solid rgba(255, 255, 255, 0.1)' };
      default:
        return { color: '#17a2b8', border: '1px solid rgba(255, 255, 255, 0.2)' };
    }
  };

  const getHealthColor = () => {
    if (health >= 80) return '#28a745';
    if (health >= 60) return '#ffc107';
    if (health >= 40) return '#fd7e14';
    return '#dc3545';
  };

  const formatLastActive = () => {
    if (!lastActive) return 'Never';
    
    const now = new Date();
    const lastActiveDate = new Date(lastActive);
    const diffMs = now - lastActiveDate;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return lastActiveDate.toLocaleDateString();
  };

  const getDepartmentColor = () => {
    switch (department?.toLowerCase()) {
      case 'strategy': return '#6f42c1';
      case 'finance': return '#28a745';
      case 'communication': return '#17a2b8';
      case 'operations': return '#fd7e14';
      case 'intelligence': return '#e83e8c';
      case 'coordination': return '#20c997';
      case 'legal': return '#6c757d';
      default: return '#17a2b8';
    }
  };

  const statusConfig = getStatusConfig();
  const priorityConfig = getPriorityConfig();

  const indicatorClasses = [
    'agent-status-indicator',
    `status-${currentStatus}`,
    `priority-${priority}`,
    `size-${size}`,
    `variant-${variant}`,
    showPulse && (currentStatus === 'active' || currentStatus === 'busy') ? 'status-pulse' : '',
    isUpdating ? 'status-updating' : '',
    onClick ? 'status-clickable' : '',
    className
  ].filter(Boolean).join(' ');

  if (variant === 'badge') {
    return (
      <span 
        className={`${indicatorClasses} status-badge`}
        onClick={onClick}
        title={`${agentName}: ${statusConfig.description}`}
        {...props}
      >
        <i className={statusConfig.icon} style={{ color: statusConfig.color }}></i>
        <span className="badge-label">{statusConfig.label}</span>
      </span>
    );
  }

  if (variant === 'minimal') {
    return (
      <div 
        className={indicatorClasses}
        onClick={onClick}
        style={{ '--status-color': statusConfig.color, '--priority-border': priorityConfig.border }}
        {...props}
      >
        <div className="status-dot">
          <i className={customIcon || statusConfig.icon}></i>
        </div>
        <span className="agent-name">{agentName}</span>
      </div>
    );
  }

  return (
    <div 
      className={indicatorClasses}
      onClick={onClick}
      style={{ 
        '--status-color': statusConfig.color, 
        '--priority-border': priorityConfig.border,
        '--health-color': getHealthColor(),
        '--department-color': getDepartmentColor()
      }}
      {...props}
    >
      {/* Header */}
      <div className="status-header">
        <div className="status-main">
          <div className="status-dot">
            <i className={customIcon || statusConfig.icon}></i>
          </div>
          <div className="agent-info">
            <h4 className="agent-name">{agentName}</h4>
            {agentId && size !== 'compact' && (
              <span className="agent-id">ID: {agentId}</span>
            )}
          </div>
        </div>
        {department && (
          <div className="department-badge" style={{ backgroundColor: getDepartmentColor() }}>
            {department}
          </div>
        )}
      </div>

      {/* Metrics */}
      {showMetrics && variant === 'detailed' && (
        <div className="status-metrics">
          <div className="metric-item">
            <span className="metric-label">Health</span>
            <div className="metric-value">
              <div className="health-bar">
                <div 
                  className="health-fill"
                  style={{ 
                    width: `${health}%`,
                    backgroundColor: getHealthColor()
                  }}
                />
              </div>
              <span className="health-value">{health}%</span>
            </div>
          </div>

          {performance !== null && (
            <div className="metric-item">
              <span className="metric-label">Performance</span>
              <span className="metric-value">{performance}%</span>
            </div>
          )}

          <div className="metric-item">
            <span className="metric-label">Tasks</span>
            <span className="metric-value">{taskCount}</span>
          </div>

          <div className="metric-item">
            <span className="metric-label">Last Active</span>
            <span className="metric-value">{formatLastActive()}</span>
          </div>
        </div>
      )}

      {/* Status Info */}
      <div className="status-info">
        <div className="status-label">
          <span className="status-text">{statusConfig.label}</span>
          {showMetrics && variant !== 'detailed' && (
            <span className="task-count">{taskCount} tasks</span>
          )}
        </div>
        {variant === 'default' && lastActive && (
          <span className="last-active">Last active: {formatLastActive()}</span>
        )}
      </div>

      {/* Health Bar for non-detailed variants */}
      {showMetrics && variant !== 'detailed' && size !== 'compact' && (
        <div className="simple-health-bar">
          <div 
            className="simple-health-fill"
            style={{ 
              width: `${health}%`,
              backgroundColor: getHealthColor()
            }}
          />
        </div>
      )}
    </div>
  );
};

export default AgentStatusIndicator;
