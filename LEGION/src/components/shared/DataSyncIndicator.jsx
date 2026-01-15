// src/components/shared/DataSyncIndicator.jsx
// Enterprise Data Synchronization Indicator Component

import React, { useState, useEffect, useCallback, useRef } from 'react';

const DataSyncIndicator = ({
  // Sync status
  status = 'idle', // 'idle', 'syncing', 'success', 'error', 'conflict', 'paused'
  
  // Display options
  variant = 'default', // 'default', 'minimal', 'detailed', 'badge', 'toast'
  size = 'medium', // 'small', 'medium', 'large'
  position = 'top-right', // 'top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'
  
  // Content
  message = '',
  showProgress = false,
  progress = 0, // 0-100
  
  // Sync metadata
  lastSync = null,
  nextSync = null,
  syncCount = 0,
  conflictCount = 0,
  
  // Auto-hide options
  autoHide = false,
  hideDelay = 3000, // milliseconds
  
  // Animation options
  animated = true,
  pulse = false,
  
  // Callbacks
  onRetry = null,
  onPause = null,
  onResume = null,
  onResolveConflict = null,
  
  // Styling
  className = '',
  style = {},
  
  // Accessibility
  ariaLabel = 'Data synchronization status'
}) => {
  const [visible, setVisible] = useState(true);
  const [expanded, setExpanded] = useState(false);
  const hideTimeoutRef = useRef(null);

  // Auto-hide functionality
  useEffect(() => {
    if (autoHide && (status === 'success' || status === 'error')) {
      hideTimeoutRef.current = setTimeout(() => {
        setVisible(false);
      }, hideDelay);
    }

    return () => {
      if (hideTimeoutRef.current) {
        clearTimeout(hideTimeoutRef.current);
      }
    };
  }, [status, autoHide, hideDelay]);

  // Reset visibility when status changes
  useEffect(() => {
    if (status === 'syncing') {
      setVisible(true);
      if (hideTimeoutRef.current) {
        clearTimeout(hideTimeoutRef.current);
      }
    }
  }, [status]);

  const handleToggleExpanded = useCallback(() => {
    setExpanded(!expanded);
  }, [expanded]);

  const handleRetry = useCallback(() => {
    if (onRetry) {
      onRetry();
    }
  }, [onRetry]);

  const handlePause = useCallback(() => {
    if (onPause) {
      onPause();
    }
  }, [onPause]);

  const handleResume = useCallback(() => {
    if (onResume) {
      onResume();
    }
  }, [onResume]);

  const handleResolveConflict = useCallback(() => {
    if (onResolveConflict) {
      onResolveConflict();
    }
  }, [onResolveConflict]);

  // Get status icon
  const getStatusIcon = () => {
    switch (status) {
      case 'syncing':
        return 'fas fa-sync-alt fa-spin';
      case 'success':
        return 'fas fa-check-circle';
      case 'error':
        return 'fas fa-exclamation-triangle';
      case 'conflict':
        return 'fas fa-exclamation-circle';
      case 'paused':
        return 'fas fa-pause-circle';
      default:
        return 'fas fa-circle';
    }
  };

  // Get status message
  const getStatusMessage = () => {
    if (message) return message;
    
    switch (status) {
      case 'syncing':
        return showProgress ? `Syncing... ${Math.round(progress)}%` : 'Syncing data...';
      case 'success':
        return 'Data synchronized successfully';
      case 'error':
        return 'Synchronization failed';
      case 'conflict':
        return `${conflictCount} conflict${conflictCount !== 1 ? 's' : ''} detected`;
      case 'paused':
        return 'Synchronization paused';
      default:
        return 'Ready to sync';
    }
  };

  // Format time ago
  const formatTimeAgo = (timestamp) => {
    if (!timestamp) return 'Never';
    
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now - time;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  // Format next sync time
  const formatNextSync = (timestamp) => {
    if (!timestamp) return 'Not scheduled';
    
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = time - now;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);

    if (diffMs < 0) return 'Overdue';
    if (diffMins < 1) return 'Now';
    if (diffMins < 60) return `In ${diffMins}m`;
    return `In ${diffHours}h`;
  };

  if (!visible) return null;

  // Minimal variant
  if (variant === 'minimal') {
    return (
      <div
        className={`
          sync-indicator minimal
          status-${status}
          size-${size}
          ${animated ? 'animated' : ''}
          ${pulse ? 'pulse' : ''}
          ${className}
        `}
        style={style}
        title={getStatusMessage()}
        aria-label={ariaLabel}
      >
        <i className={getStatusIcon()} />
      </div>
    );
  }

  // Badge variant
  if (variant === 'badge') {
    return (
      <div
        className={`
          sync-indicator badge
          status-${status}
          size-${size}
          ${animated ? 'animated' : ''}
          ${pulse ? 'pulse' : ''}
          ${className}
        `}
        style={style}
        title={getStatusMessage()}
        aria-label={ariaLabel}
      >
        <i className={getStatusIcon()} />
        <span className="badge-text">{getStatusMessage()}</span>
      </div>
    );
  }

  // Toast variant
  if (variant === 'toast') {
    return (
      <div
        className={`
          sync-indicator toast
          status-${status}
          position-${position}
          ${animated ? 'animated' : ''}
          ${className}
        `}
        style={style}
        role="alert"
        aria-live="polite"
      >
        <div className="toast-content">
          <div className="toast-icon">
            <i className={getStatusIcon()} />
          </div>
          <div className="toast-message">
            <div className="message-text">{getStatusMessage()}</div>
            {showProgress && status === 'syncing' && (
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
                />
              </div>
            )}
          </div>
          <button
            className="toast-close"
            onClick={() => setVisible(false)}
            aria-label="Close notification"
          >
            <i className="fas fa-times" />
          </button>
        </div>
      </div>
    );
  }

  // Default and detailed variants
  return (
    <div
      className={`
        sync-indicator default
        status-${status}
        size-${size}
        variant-${variant}
        ${animated ? 'animated' : ''}
        ${pulse ? 'pulse' : ''}
        ${expanded ? 'expanded' : ''}
        ${className}
      `}
      style={style}
      role="status"
      aria-label={ariaLabel}
      aria-live="polite"
    >
      {/* Main Content */}
      <div className="sync-content">
        <div className="sync-icon">
          <i className={getStatusIcon()} />
        </div>
        
        <div className="sync-info">
          <div className="sync-message">{getStatusMessage()}</div>
          
          {/* Progress Bar */}
          {showProgress && status === 'syncing' && (
            <div className="progress-container">
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
                />
              </div>
              <div className="progress-text">{Math.round(progress)}%</div>
            </div>
          )}
          
          {/* Detailed Info */}
          {variant === 'detailed' && (
            <div className="sync-details">
              <div className="detail-item">
                <span className="detail-label">Last sync:</span>
                <span className="detail-value">{formatTimeAgo(lastSync)}</span>
              </div>
              {nextSync && status !== 'paused' && (
                <div className="detail-item">
                  <span className="detail-label">Next sync:</span>
                  <span className="detail-value">{formatNextSync(nextSync)}</span>
                </div>
              )}
              {syncCount > 0 && (
                <div className="detail-item">
                  <span className="detail-label">Total syncs:</span>
                  <span className="detail-value">{syncCount}</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="sync-actions">
          {status === 'error' && onRetry && (
            <button
              className="action-button retry"
              onClick={handleRetry}
              title="Retry synchronization"
            >
              <i className="fas fa-redo" />
            </button>
          )}
          
          {status === 'syncing' && onPause && (
            <button
              className="action-button pause"
              onClick={handlePause}
              title="Pause synchronization"
            >
              <i className="fas fa-pause" />
            </button>
          )}
          
          {status === 'paused' && onResume && (
            <button
              className="action-button resume"
              onClick={handleResume}
              title="Resume synchronization"
            >
              <i className="fas fa-play" />
            </button>
          )}
          
          {status === 'conflict' && onResolveConflict && (
            <button
              className="action-button resolve"
              onClick={handleResolveConflict}
              title="Resolve conflicts"
            >
              <i className="fas fa-tools" />
            </button>
          )}
          
          {variant === 'default' && (
            <button
              className="action-button expand"
              onClick={handleToggleExpanded}
              title={expanded ? 'Show less' : 'Show more'}
            >
              <i className={`fas fa-chevron-${expanded ? 'up' : 'down'}`} />
            </button>
          )}
        </div>
      </div>

      {/* Expanded Details */}
      {expanded && variant === 'default' && (
        <div className="expanded-details">
          <div className="details-grid">
            <div className="detail-item">
              <span className="detail-label">Status:</span>
              <span className={`detail-value status-${status}`}>
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </span>
            </div>
            
            <div className="detail-item">
              <span className="detail-label">Last sync:</span>
              <span className="detail-value">{formatTimeAgo(lastSync)}</span>
            </div>
            
            {nextSync && (
              <div className="detail-item">
                <span className="detail-label">Next sync:</span>
                <span className="detail-value">{formatNextSync(nextSync)}</span>
              </div>
            )}
            
            <div className="detail-item">
              <span className="detail-label">Total syncs:</span>
              <span className="detail-value">{syncCount}</span>
            </div>
            
            {conflictCount > 0 && (
              <div className="detail-item">
                <span className="detail-label">Conflicts:</span>
                <span className="detail-value error">{conflictCount}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// Sync Status Manager Hook
export const useSyncStatus = (initialStatus = 'idle') => {
  const [status, setStatus] = useState(initialStatus);
  const [progress, setProgress] = useState(0);
  const [lastSync, setLastSync] = useState(null);
  const [syncCount, setSyncCount] = useState(0);
  const [conflictCount, setConflictCount] = useState(0);

  const startSync = useCallback(() => {
    setStatus('syncing');
    setProgress(0);
  }, []);

  const updateProgress = useCallback((newProgress) => {
    setProgress(Math.min(100, Math.max(0, newProgress)));
  }, []);

  const completeSync = useCallback(() => {
    setStatus('success');
    setProgress(100);
    setLastSync(new Date().toISOString());
    setSyncCount(prev => prev + 1);
  }, []);

  const failSync = useCallback(() => {
    setStatus('error');
    setProgress(0);
  }, []);

  const pauseSync = useCallback(() => {
    setStatus('paused');
  }, []);

  const resumeSync = useCallback(() => {
    setStatus('syncing');
  }, []);

  const detectConflict = useCallback((conflicts = 1) => {
    setStatus('conflict');
    setConflictCount(conflicts);
  }, []);

  const resolveConflicts = useCallback(() => {
    setStatus('idle');
    setConflictCount(0);
  }, []);

  return {
    status,
    progress,
    lastSync,
    syncCount,
    conflictCount,
    startSync,
    updateProgress,
    completeSync,
    failSync,
    pauseSync,
    resumeSync,
    detectConflict,
    resolveConflicts
  };
};

export default DataSyncIndicator;
