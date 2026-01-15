// src/components/shared/SystemAlert.jsx

import React, { useState, useEffect } from 'react';

const SystemAlert = ({
  // Alert content
  title = 'System Alert',
  message = 'No alert message provided',
  type = 'info', // 'info', 'success', 'warning', 'error', 'critical'
  
  // Display options
  variant = 'default', // 'default', 'minimal', 'detailed', 'toast', 'banner'
  size = 'medium', // 'small', 'medium', 'large'
  dismissible = true,
  autoClose = false,
  autoCloseDelay = 5000,
  
  // Positioning
  position = 'top-right', // 'top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'
  
  // Data and metadata
  timestamp = new Date(),
  source = 'System',
  id = null,
  priority = 'normal', // 'low', 'normal', 'high', 'critical'
  category = 'general',
  
  // Actions
  actions = [],
  
  // Event handlers
  onDismiss = null,
  onAction = null,
  onView = null,
  
  // Visual options
  showIcon = true,
  showTimestamp = true,
  showSource = true,
  animated = true,
  persistent = false,
  
  // Custom styling
  className = '',
  style = {}
}) => {
  const [isVisible, setIsVisible] = useState(true);
  const [isAnimating, setIsAnimating] = useState(false);

  // Auto-close functionality
  useEffect(() => {
    if (autoClose && !persistent) {
      const timer = setTimeout(() => {
        handleDismiss();
      }, autoCloseDelay);

      return () => clearTimeout(timer);
    }
  }, [autoClose, autoCloseDelay, persistent]);

  // Get alert icon based on type
  const getIcon = () => {
    const icons = {
      info: 'fas fa-info-circle',
      success: 'fas fa-check-circle',
      warning: 'fas fa-exclamation-triangle',
      error: 'fas fa-exclamation-circle',
      critical: 'fas fa-skull-crossbones'
    };
    return icons[type] || icons.info;
  };

  // Get priority indicator
  const getPriorityColor = () => {
    const colors = {
      low: '#6c757d',
      normal: '#17a2b8',
      high: '#ffc107',
      critical: '#dc3545'
    };
    return colors[priority] || colors.normal;
  };

  // Handle dismiss
  const handleDismiss = () => {
    if (!dismissible) return;
    
    setIsAnimating(true);
    setTimeout(() => {
      setIsVisible(false);
      if (onDismiss) onDismiss(id);
    }, 300);
  };

  // Handle action click
  const handleAction = (action, index) => {
    if (onAction) {
      onAction(action, index, id);
    }
    if (action.dismissOnClick !== false) {
      handleDismiss();
    }
  };

  // Format timestamp
  const formatTimestamp = (date) => {
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  };

  if (!isVisible) return null;

  return (
    <div 
      className={`
        system-alert
        type-${type}
        variant-${variant}
        size-${size}
        position-${position}
        priority-${priority}
        ${animated ? 'animated' : ''}
        ${isAnimating ? 'dismissing' : ''}
        ${persistent ? 'persistent' : ''}
        ${className}
      `}
      style={style}
      onClick={onView ? () => onView(id) : undefined}
    >
      {/* Priority Indicator */}
      <div 
        className="alert-priority-bar"
        style={{ backgroundColor: getPriorityColor() }}
      />

      {/* Alert Content */}
      <div className="alert-content">
        {/* Header */}
        <div className="alert-header">
          {showIcon && (
            <div className="alert-icon">
              <i className={getIcon()} />
            </div>
          )}
          
          <div className="alert-title-section">
            <h4 className="alert-title">{title}</h4>
            
            {variant === 'detailed' && (
              <div className="alert-metadata">
                {showSource && (
                  <span className="alert-source">
                    <i className="fas fa-tag" />
                    {source}
                  </span>
                )}
                
                <span className="alert-category">
                  <i className="fas fa-folder" />
                  {category}
                </span>
                
                <span className="alert-priority">
                  <i className="fas fa-flag" />
                  {priority}
                </span>
              </div>
            )}
          </div>

          <div className="alert-controls">
            {showTimestamp && (
              <span className="alert-timestamp">
                <i className="fas fa-clock" />
                {formatTimestamp(timestamp)}
              </span>
            )}
            
            {dismissible && (
              <button 
                className="alert-dismiss"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDismiss();
                }}
                title="Dismiss alert"
              >
                <i className="fas fa-times" />
              </button>
            )}
          </div>
        </div>

        {/* Message */}
        {message && variant !== 'minimal' && (
          <div className="alert-message">
            {typeof message === 'string' ? (
              <p>{message}</p>
            ) : (
              message
            )}
          </div>
        )}

        {/* Actions */}
        {actions.length > 0 && variant !== 'minimal' && (
          <div className="alert-actions">
            {actions.map((action, index) => (
              <button
                key={index}
                className={`
                  alert-action
                  ${action.variant || 'default'}
                  ${action.primary ? 'primary' : ''}
                `}
                onClick={(e) => {
                  e.stopPropagation();
                  handleAction(action, index);
                }}
                disabled={action.disabled}
                title={action.tooltip}
              >
                {action.icon && <i className={action.icon} />}
                {action.label}
              </button>
            ))}
          </div>
        )}

        {/* Detailed Info */}
        {variant === 'detailed' && (
          <div className="alert-details">
            <div className="detail-grid">
              <div className="detail-item">
                <span className="detail-label">Alert ID:</span>
                <span className="detail-value">{id || 'N/A'}</span>
              </div>
              
              <div className="detail-item">
                <span className="detail-label">Type:</span>
                <span className="detail-value">{type}</span>
              </div>
              
              <div className="detail-item">
                <span className="detail-label">Created:</span>
                <span className="detail-value">
                  {timestamp.toLocaleString()}
                </span>
              </div>
              
              <div className="detail-item">
                <span className="detail-label">Auto-close:</span>
                <span className="detail-value">
                  {autoClose ? `${autoCloseDelay / 1000}s` : 'Manual'}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Progress bar for auto-close */}
      {autoClose && !persistent && (
        <div className="alert-progress">
          <div 
            className="alert-progress-bar"
            style={{ 
              animationDuration: `${autoCloseDelay}ms`,
              backgroundColor: getPriorityColor()
            }}
          />
        </div>
      )}
    </div>
  );
};

// System Alert Manager Component
export const SystemAlertManager = ({
  alerts = [],
  maxAlerts = 5,
  position = 'top-right',
  spacing = 12,
  onDismiss = null,
  onAction = null,
  className = ''
}) => {
  const [visibleAlerts, setVisibleAlerts] = useState(alerts);

  useEffect(() => {
    setVisibleAlerts(alerts.slice(0, maxAlerts));
  }, [alerts, maxAlerts]);

  const handleDismiss = (alertId) => {
    setVisibleAlerts(prev => prev.filter(alert => alert.id !== alertId));
    if (onDismiss) onDismiss(alertId);
  };

  const handleAction = (action, actionIndex, alertId) => {
    if (onAction) onAction(action, actionIndex, alertId);
  };

  return (
    <div 
      className={`system-alert-manager position-${position} ${className}`}
      style={{ '--spacing': `${spacing}px` }}
    >
      {visibleAlerts.map((alert, index) => (
        <SystemAlert
          key={alert.id || index}
          {...alert}
          position={position}
          onDismiss={handleDismiss}
          onAction={handleAction}
          style={{
            '--index': index,
            zIndex: 1000 - index,
            ...alert.style
          }}
        />
      ))}
    </div>
  );
};

// Quick alert creation utilities
export const createAlert = (type, title, message, options = {}) => ({
  id: `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
  type,
  title,
  message,
  timestamp: new Date(),
  ...options
});

export const createInfoAlert = (title, message, options = {}) => 
  createAlert('info', title, message, options);

export const createSuccessAlert = (title, message, options = {}) => 
  createAlert('success', title, message, options);

export const createWarningAlert = (title, message, options = {}) => 
  createAlert('warning', title, message, options);

export const createErrorAlert = (title, message, options = {}) => 
  createAlert('error', title, message, options);

export const createCriticalAlert = (title, message, options = {}) => 
  createAlert('critical', title, message, { priority: 'critical', persistent: true, ...options });

export default SystemAlert;
