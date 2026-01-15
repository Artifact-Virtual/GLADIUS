// src/components/shared/ConnectionStatusIndicator.jsx
// Enterprise Connection Status Indicator Component

import React, { useState, useEffect } from 'react';

const ConnectionStatusIndicator = ({
  // Connection data
  connectionStatus = 'disconnected', // 'connected', 'connecting', 'disconnected', 'error', 'reconnecting', 'offline'
  lastUpdate = null,
  latency = null,
  retryCount = 0,
  
  // Display options
  variant = 'default', // 'default', 'minimal', 'detailed', 'badge'
  size = 'medium', // 'small', 'medium', 'large'
  showLabel = true,
  showLatency = false,
  showLastUpdate = false,
  showRetryCount = false,
  
  // Behavior options
  clickable = false,
  showTooltip = true,
  animated = true,
  
  // Event handlers
  onClick = null,
  onStatusChange = null,
  
  // Custom styling
  className = '',
  style = {}
}) => {
  const [tooltipVisible, setTooltipVisible] = useState(false);
  const [lastStatusChange, setLastStatusChange] = useState(Date.now());

  // Track status changes
  useEffect(() => {
    setLastStatusChange(Date.now());
    if (onStatusChange) {
      onStatusChange(connectionStatus);
    }
  }, [connectionStatus, onStatusChange]);

  // Get status configuration
  const getStatusConfig = () => {
    const configs = {
      connected: {
        color: '#28a745',
        icon: 'fas fa-circle',
        label: 'Connected',
        description: 'Connection is active and healthy',
        pulse: false
      },
      connecting: {
        color: '#17a2b8',
        icon: 'fas fa-circle',
        label: 'Connecting',
        description: 'Establishing connection...',
        pulse: true
      },
      disconnected: {
        color: '#6c757d',
        icon: 'fas fa-circle',
        label: 'Disconnected',
        description: 'No active connection',
        pulse: false
      },
      error: {
        color: '#dc3545',
        icon: 'fas fa-exclamation-circle',
        label: 'Error',
        description: 'Connection error occurred',
        pulse: true
      },
      reconnecting: {
        color: '#ffc107',
        icon: 'fas fa-circle',
        label: 'Reconnecting',
        description: `Reconnecting... (attempt ${retryCount + 1})`,
        pulse: true
      },
      offline: {
        color: '#6c757d',
        icon: 'fas fa-wifi',
        label: 'Offline',
        description: 'Network is unavailable',
        pulse: false
      }
    };

    return configs[connectionStatus] || configs.disconnected;
  };

  // Format latency
  const formatLatency = (ms) => {
    if (ms < 100) return `${ms}ms`;
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  // Format last update time
  const formatLastUpdate = (timestamp) => {
    if (!timestamp) return 'Never';
    
    const now = Date.now();
    const diff = now - (timestamp instanceof Date ? timestamp.getTime() : timestamp);
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return new Date(timestamp).toLocaleDateString();
  };

  const statusConfig = getStatusConfig();

  // Handle click
  const handleClick = (e) => {
    if (clickable && onClick) {
      e.preventDefault();
      onClick(connectionStatus);
    }
  };

  // Tooltip content
  const getTooltipContent = () => {
    const info = [statusConfig.description];
    
    if (showLatency && latency !== null) {
      info.push(`Latency: ${formatLatency(latency)}`);
    }
    
    if (showLastUpdate && lastUpdate) {
      info.push(`Last update: ${formatLastUpdate(lastUpdate)}`);
    }
    
    if (showRetryCount && retryCount > 0) {
      info.push(`Retry attempts: ${retryCount}`);
    }
    
    return info.join('\n');
  };

  return (
    <div 
      className={`
        connection-status-indicator
        status-${connectionStatus}
        variant-${variant}
        size-${size}
        ${clickable ? 'clickable' : ''}
        ${animated ? 'animated' : ''}
        ${className}
      `}
      style={style}
      onClick={handleClick}
      onMouseEnter={() => showTooltip && setTooltipVisible(true)}
      onMouseLeave={() => showTooltip && setTooltipVisible(false)}
      title={showTooltip ? getTooltipContent() : undefined}
    >
      {/* Status Indicator */}
      <div 
        className={`status-dot ${statusConfig.pulse ? 'pulse' : ''}`}
        style={{ color: statusConfig.color }}
      >
        <i className={statusConfig.icon} />
      </div>

      {/* Label and Details */}
      {variant !== 'minimal' && variant !== 'badge' && (
        <div className="status-info">
          {showLabel && (
            <span className="status-label">{statusConfig.label}</span>
          )}
          
          {variant === 'detailed' && (
            <div className="status-details">
              {showLatency && latency !== null && (
                <span className="status-detail latency">
                  <i className="fas fa-tachometer-alt" />
                  {formatLatency(latency)}
                </span>
              )}
              
              {showLastUpdate && lastUpdate && (
                <span className="status-detail last-update">
                  <i className="fas fa-clock" />
                  {formatLastUpdate(lastUpdate)}
                </span>
              )}
              
              {showRetryCount && retryCount > 0 && (
                <span className="status-detail retry-count">
                  <i className="fas fa-redo" />
                  {retryCount} retries
                </span>
              )}
            </div>
          )}
        </div>
      )}

      {/* Badge variant count */}
      {variant === 'badge' && retryCount > 0 && (
        <span className="retry-badge">{retryCount}</span>
      )}

      {/* Tooltip */}
      {showTooltip && tooltipVisible && variant === 'minimal' && (
        <div className="status-tooltip">
          {getTooltipContent().split('\n').map((line, index) => (
            <div key={index}>{line}</div>
          ))}
        </div>
      )}
    </div>
  );
};

// Connection Status Manager Component
export const ConnectionStatusManager = ({
  connections = [],
  className = '',
  style = {},
  maxVisible = 5,
  showSummary = true
}) => {
  // Calculate connection summary
  const summary = connections.reduce((acc, conn) => {
    acc[conn.status] = (acc[conn.status] || 0) + 1;
    acc.total += 1;
    return acc;
  }, { total: 0 });

  const connectedCount = summary.connected || 0;
  const healthPercentage = summary.total > 0 ? (connectedCount / summary.total * 100) : 0;

  return (
    <div className={`connection-status-manager ${className}`} style={style}>
      {showSummary && (
        <div className="connection-summary">
          <div className="summary-stats">
            <span className="connected-count">{connectedCount}/{summary.total}</span>
            <span className="health-percentage">{healthPercentage.toFixed(0)}%</span>
          </div>
          <div className="health-bar">
            <div 
              className="health-fill"
              style={{ width: `${healthPercentage}%` }}
            />
          </div>
        </div>
      )}

      <div className="connections-list">
        {connections.slice(0, maxVisible).map((connection, index) => (
          <ConnectionStatusIndicator
            key={connection.id || index}
            connectionStatus={connection.status}
            lastUpdate={connection.lastUpdate}
            latency={connection.latency}
            retryCount={connection.retryCount}
            variant="minimal"
            showTooltip={true}
            {...connection.props}
          />
        ))}
        
        {connections.length > maxVisible && (
          <div className="more-connections">
            +{connections.length - maxVisible} more
          </div>
        )}
      </div>
    </div>
  );
};

export default ConnectionStatusIndicator;
