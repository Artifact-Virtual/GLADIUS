// src/components/shared/RefreshControl.jsx
// Enterprise Manual Refresh Control Component

import React, { useState, useCallback, useRef, useEffect } from 'react';

const RefreshControl = ({
  // Refresh functionality
  onRefresh = null,
  refreshing = false,
  
  // Display options
  variant = 'button', // 'button', 'icon', 'dropdown', 'toolbar', 'floating'
  size = 'medium', // 'small', 'medium', 'large'
  position = 'top-right', // For floating variant
  
  // Content options
  label = 'Refresh',
  showLabel = true,
  showLastRefresh = false,
  lastRefresh = null,
  
  // Auto-refresh options
  enableAutoRefresh = false,
  autoRefreshInterval = 30000, // milliseconds
  autoRefreshEnabled = false,
  onToggleAutoRefresh = null,
  
  // Cooldown options
  cooldownTime = 1000, // milliseconds
  
  // Advanced options
  showProgress = false,
  progress = 0, // 0-100
  pullToRefresh = false,
  
  // Keyboard shortcuts
  shortcutKey = 'r', // Key for Ctrl/Cmd + key
  enableShortcut = true,
  
  // Styling
  className = '',
  style = {},
  disabled = false,
  
  // Accessibility
  ariaLabel = 'Refresh data'
}) => {
  const [isOnCooldown, setIsOnCooldown] = useState(false);
  const [pullDistance, setPullDistance] = useState(0);
  const [isPulling, setIsPulling] = useState(false);
  const cooldownTimeoutRef = useRef(null);
  const touchStartY = useRef(0);
  const lastRefreshTimeRef = useRef(lastRefresh);

  // Update last refresh time
  useEffect(() => {
    if (lastRefresh) {
      lastRefreshTimeRef.current = lastRefresh;
    }
  }, [lastRefresh]);

  // Handle keyboard shortcuts
  useEffect(() => {
    if (!enableShortcut) return;

    const handleKeydown = (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === shortcutKey.toLowerCase()) {
        event.preventDefault();
        handleRefresh();
      }
    };

    window.addEventListener('keydown', handleKeydown);
    return () => window.removeEventListener('keydown', handleKeydown);
  }, [enableShortcut, shortcutKey]);

  // Handle refresh with cooldown
  const handleRefresh = useCallback(async () => {
    if (refreshing || isOnCooldown || disabled) return;

    setIsOnCooldown(true);
    
    if (onRefresh) {
      try {
        await onRefresh();
        lastRefreshTimeRef.current = new Date().toISOString();
      } catch (error) {
        console.error('Refresh failed:', error);
      }
    }

    // Apply cooldown
    cooldownTimeoutRef.current = setTimeout(() => {
      setIsOnCooldown(false);
    }, cooldownTime);
  }, [refreshing, isOnCooldown, disabled, onRefresh, cooldownTime]);

  // Handle auto-refresh toggle
  const handleToggleAutoRefresh = useCallback(() => {
    if (onToggleAutoRefresh) {
      onToggleAutoRefresh(!autoRefreshEnabled);
    }
  }, [onToggleAutoRefresh, autoRefreshEnabled]);

  // Pull-to-refresh handlers
  const handleTouchStart = useCallback((event) => {
    if (!pullToRefresh) return;
    touchStartY.current = event.touches[0].clientY;
  }, [pullToRefresh]);

  const handleTouchMove = useCallback((event) => {
    if (!pullToRefresh || refreshing) return;
    
    const currentY = event.touches[0].clientY;
    const diff = currentY - touchStartY.current;
    
    if (diff > 0 && window.scrollY === 0) {
      event.preventDefault();
      const distance = Math.min(diff * 0.5, 100);
      setPullDistance(distance);
      setIsPulling(distance > 50);
    }
  }, [pullToRefresh, refreshing]);

  const handleTouchEnd = useCallback(() => {
    if (!pullToRefresh) return;
    
    if (isPulling && pullDistance > 50) {
      handleRefresh();
    }
    
    setPullDistance(0);
    setIsPulling(false);
  }, [pullToRefresh, isPulling, pullDistance, handleRefresh]);

  // Format last refresh time
  const formatLastRefresh = (timestamp) => {
    if (!timestamp) return 'Never';
    
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now - time;
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);

    if (diffSecs < 60) return `${diffSecs}s ago`;
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return time.toLocaleDateString();
  };

  // Cleanup
  useEffect(() => {
    return () => {
      if (cooldownTimeoutRef.current) {
        clearTimeout(cooldownTimeoutRef.current);
      }
    };
  }, []);

  // Icon variant
  if (variant === 'icon') {
    return (
      <button
        className={`
          refresh-control icon
          size-${size}
          ${refreshing ? 'refreshing' : ''}
          ${isOnCooldown ? 'cooldown' : ''}
          ${disabled ? 'disabled' : ''}
          ${className}
        `}
        style={style}
        onClick={handleRefresh}
        disabled={disabled || refreshing || isOnCooldown}
        title={`${ariaLabel} (${enableShortcut ? `Ctrl+${shortcutKey.toUpperCase()}` : 'Click'})`}
        aria-label={ariaLabel}
      >
        <i className={`fas fa-sync-alt ${refreshing ? 'fa-spin' : ''}`} />
      </button>
    );
  }

  // Floating variant
  if (variant === 'floating') {
    return (
      <div
        className={`
          refresh-control floating
          position-${position}
          size-${size}
          ${refreshing ? 'refreshing' : ''}
          ${isOnCooldown ? 'cooldown' : ''}
          ${className}
        `}
        style={style}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        {/* Pull to refresh indicator */}
        {pullToRefresh && pullDistance > 0 && (
          <div 
            className="pull-indicator"
            style={{ 
              transform: `translateY(${pullDistance}px)`,
              opacity: pullDistance / 100 
            }}
          >
            <i className={`fas ${isPulling ? 'fa-arrow-down' : 'fa-sync-alt'}`} />
            <span>{isPulling ? 'Release to refresh' : 'Pull to refresh'}</span>
          </div>
        )}

        <button
          className="floating-button"
          onClick={handleRefresh}
          disabled={disabled || refreshing || isOnCooldown}
          aria-label={ariaLabel}
        >
          <i className={`fas fa-sync-alt ${refreshing ? 'fa-spin' : ''}`} />
        </button>

        {/* Progress indicator */}
        {showProgress && refreshing && (
          <div className="progress-ring">
            <svg width="48" height="48">
              <circle
                cx="24"
                cy="24"
                r="20"
                fill="none"
                stroke="#e5e7eb"
                strokeWidth="4"
              />
              <circle
                cx="24"
                cy="24"
                r="20"
                fill="none"
                stroke="#3b82f6"
                strokeWidth="4"
                strokeDasharray={`${2 * Math.PI * 20}`}
                strokeDashoffset={`${2 * Math.PI * 20 * (1 - progress / 100)}`}
                transform="rotate(-90 24 24)"
              />
            </svg>
          </div>
        )}
      </div>
    );
  }

  // Dropdown variant
  if (variant === 'dropdown') {
    return (
      <div className={`refresh-control dropdown size-${size} ${className}`} style={style}>
        <button
          className={`
            dropdown-button
            ${refreshing ? 'refreshing' : ''}
            ${isOnCooldown ? 'cooldown' : ''}
            ${disabled ? 'disabled' : ''}
          `}
          onClick={handleRefresh}
          disabled={disabled || refreshing || isOnCooldown}
          aria-label={ariaLabel}
        >
          <i className={`fas fa-sync-alt ${refreshing ? 'fa-spin' : ''}`} />
          {showLabel && <span>{refreshing ? 'Refreshing...' : label}</span>}
          <i className="fas fa-chevron-down" />
        </button>

        <div className="dropdown-menu">
          <div className="dropdown-item" onClick={handleRefresh}>
            <i className="fas fa-sync-alt" />
            <span>Refresh Now</span>
            {enableShortcut && (
              <kbd>Ctrl+{shortcutKey.toUpperCase()}</kbd>
            )}
          </div>
          
          {enableAutoRefresh && (
            <div className="dropdown-item" onClick={handleToggleAutoRefresh}>
              <i className={`fas ${autoRefreshEnabled ? 'fa-pause' : 'fa-play'}`} />
              <span>{autoRefreshEnabled ? 'Disable' : 'Enable'} Auto-refresh</span>
            </div>
          )}
          
          {showLastRefresh && (
            <div className="dropdown-info">
              <span>Last refresh: {formatLastRefresh(lastRefreshTimeRef.current)}</span>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Toolbar variant
  if (variant === 'toolbar') {
    return (
      <div className={`refresh-control toolbar size-${size} ${className}`} style={style}>
        <div className="toolbar-group">
          <button
            className={`
              toolbar-button
              ${refreshing ? 'refreshing' : ''}
              ${isOnCooldown ? 'cooldown' : ''}
              ${disabled ? 'disabled' : ''}
            `}
            onClick={handleRefresh}
            disabled={disabled || refreshing || isOnCooldown}
            title={`${ariaLabel} (${enableShortcut ? `Ctrl+${shortcutKey.toUpperCase()}` : 'Click'})`}
          >
            <i className={`fas fa-sync-alt ${refreshing ? 'fa-spin' : ''}`} />
            {showLabel && <span>{refreshing ? 'Refreshing...' : label}</span>}
          </button>

          {enableAutoRefresh && (
            <button
              className={`
                toolbar-button auto-refresh
                ${autoRefreshEnabled ? 'active' : ''}
              `}
              onClick={handleToggleAutoRefresh}
              title={`${autoRefreshEnabled ? 'Disable' : 'Enable'} auto-refresh`}
            >
              <i className={`fas ${autoRefreshEnabled ? 'fa-pause' : 'fa-play'}`} />
            </button>
          )}
        </div>

        {showLastRefresh && (
          <div className="toolbar-info">
            <span>Last: {formatLastRefresh(lastRefreshTimeRef.current)}</span>
          </div>
        )}

        {showProgress && refreshing && (
          <div className="toolbar-progress">
            <div 
              className="progress-bar"
              style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
            />
          </div>
        )}
      </div>
    );
  }

  // Default button variant
  return (
    <button
      className={`
        refresh-control button
        size-${size}
        ${refreshing ? 'refreshing' : ''}
        ${isOnCooldown ? 'cooldown' : ''}
        ${disabled ? 'disabled' : ''}
        ${className}
      `}
      style={style}
      onClick={handleRefresh}
      disabled={disabled || refreshing || isOnCooldown}
      title={`${ariaLabel} (${enableShortcut ? `Ctrl+${shortcutKey.toUpperCase()}` : 'Click'})`}
      aria-label={ariaLabel}
    >
      <i className={`fas fa-sync-alt ${refreshing ? 'fa-spin' : ''}`} />
      {showLabel && (
        <span className="button-text">
          {refreshing ? 'Refreshing...' : label}
        </span>
      )}
      
      {showProgress && refreshing && (
        <div className="button-progress">
          <div 
            className="progress-fill"
            style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
          />
        </div>
      )}
    </button>
  );
};

// Refresh control hook for managing refresh state
export const useRefreshControl = ({
  onRefresh = null,
  autoRefreshInterval = 30000,
  enableAutoRefresh = false
} = {}) => {
  const [refreshing, setRefreshing] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(null);
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(false);
  const [progress, setProgress] = useState(0);
  
  const autoRefreshIntervalRef = useRef(null);
  const progressIntervalRef = useRef(null);

  // Handle manual refresh
  const handleRefresh = useCallback(async () => {
    if (refreshing) return;

    setRefreshing(true);
    setProgress(0);

    // Simulate progress if no real progress is provided
    progressIntervalRef.current = setInterval(() => {
      setProgress(prev => {
        const increment = Math.random() * 15 + 5; // 5-20% increments
        return Math.min(95, prev + increment);
      });
    }, 200);

    try {
      if (onRefresh) {
        await onRefresh();
      }
      setProgress(100);
      setLastRefresh(new Date().toISOString());
    } catch (error) {
      console.error('Refresh failed:', error);
      throw error;
    } finally {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
      
      setTimeout(() => {
        setRefreshing(false);
        setProgress(0);
      }, 500);
    }
  }, [refreshing, onRefresh]);

  // Handle auto-refresh toggle
  const toggleAutoRefresh = useCallback((enabled) => {
    setAutoRefreshEnabled(enabled);
    
    if (enabled && enableAutoRefresh) {
      autoRefreshIntervalRef.current = setInterval(() => {
        handleRefresh();
      }, autoRefreshInterval);
    } else if (autoRefreshIntervalRef.current) {
      clearInterval(autoRefreshIntervalRef.current);
      autoRefreshIntervalRef.current = null;
    }
  }, [enableAutoRefresh, autoRefreshInterval, handleRefresh]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (autoRefreshIntervalRef.current) {
        clearInterval(autoRefreshIntervalRef.current);
      }
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
    };
  }, []);

  return {
    refreshing,
    lastRefresh,
    autoRefreshEnabled,
    progress,
    handleRefresh,
    toggleAutoRefresh,
    setProgress
  };
};

export default RefreshControl;
