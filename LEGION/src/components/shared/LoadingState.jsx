// src/components/shared/LoadingState.jsx
// Enterprise Loading State Component

import React from 'react';

const LoadingState = ({
  // Loading configuration
  variant = 'default', // 'default', 'minimal', 'skeleton', 'pulse', 'dots', 'spinner', 'progress'
  size = 'medium', // 'small', 'medium', 'large', 'full'
  
  // Content options
  message = 'Loading...',
  showMessage = true,
  showProgress = false,
  progress = 0, // 0-100
  
  // Skeleton options (for skeleton variant)
  skeletonLines = 3,
  skeletonHeight = 20,
  skeletonWidth = '100%',
  
  // Animation options
  animated = true,
  duration = 1500, // milliseconds
  
  // Display options
  overlay = false,
  blur = false,
  
  // Custom styling
  className = '',
  style = {},
  
  // Accessibility
  ariaLabel = 'Loading content'
}) => {
  // Render skeleton loading
  const renderSkeleton = () => (
    <div className="skeleton-container">
      {Array.from({ length: skeletonLines }).map((_, index) => (
        <div
          key={index}
          className="skeleton-line"
          style={{
            height: `${skeletonHeight}px`,
            width: Array.isArray(skeletonWidth) ? skeletonWidth[index] || '100%' : skeletonWidth,
            animationDelay: `${index * 0.1}s`
          }}
        />
      ))}
    </div>
  );

  // Render spinner
  const renderSpinner = () => (
    <div className="spinner-container">
      <div className="spinner" />
    </div>
  );

  // Render dots
  const renderDots = () => (
    <div className="dots-container">
      <div className="dot" style={{ animationDelay: '0s' }} />
      <div className="dot" style={{ animationDelay: '0.2s' }} />
      <div className="dot" style={{ animationDelay: '0.4s' }} />
    </div>
  );

  // Render pulse
  const renderPulse = () => (
    <div className="pulse-container">
      <div className="pulse-circle" />
    </div>
  );

  // Render progress bar
  const renderProgress = () => (
    <div className="progress-container">
      <div className="progress-bar">
        <div 
          className="progress-fill"
          style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
        />
      </div>
      {showProgress && (
        <div className="progress-text">
          {Math.round(progress)}%
        </div>
      )}
    </div>
  );

  // Get loading content based on variant
  const getLoadingContent = () => {
    switch (variant) {
      case 'skeleton':
        return renderSkeleton();
      case 'spinner':
        return renderSpinner();
      case 'dots':
        return renderDots();
      case 'pulse':
        return renderPulse();
      case 'progress':
        return renderProgress();
      case 'minimal':
        return (
          <div className="minimal-loader">
            <div className="minimal-dot" />
          </div>
        );
      default:
        return (
          <div className="default-loader">
            <div className="loader-icon">
              <i className="fas fa-spinner fa-spin" />
            </div>
          </div>
        );
    }
  };

  return (
    <div 
      className={`
        loading-state
        variant-${variant}
        size-${size}
        ${animated ? 'animated' : ''}
        ${overlay ? 'overlay' : ''}
        ${blur ? 'blur' : ''}
        ${className}
      `}
      style={{
        ...style,
        animationDuration: `${duration}ms`
      }}
      role="status"
      aria-label={ariaLabel}
      aria-live="polite"
    >
      {/* Loading Content */}
      <div className="loading-content">
        {getLoadingContent()}
        
        {/* Loading Message */}
        {showMessage && message && variant !== 'minimal' && variant !== 'skeleton' && (
          <div className="loading-message">
            {message}
          </div>
        )}
      </div>

      {/* Screen Reader Text */}
      <span className="sr-only">{ariaLabel}</span>
    </div>
  );
};

// Loading Overlay Component
export const LoadingOverlay = ({
  children,
  loading = false,
  loadingProps = {},
  className = '',
  style = {}
}) => {
  return (
    <div 
      className={`loading-overlay-container ${className}`}
      style={style}
    >
      {children}
      
      {loading && (
        <div className="loading-overlay-backdrop">
          <LoadingState
            variant="default"
            size="large"
            overlay={true}
            blur={true}
            {...loadingProps}
          />
        </div>
      )}
    </div>
  );
};

// Loading Button Component
export const LoadingButton = ({
  children,
  loading = false,
  loadingText = 'Loading...',
  disabled = false,
  onClick = null,
  className = '',
  style = {},
  variant = 'primary',
  size = 'medium',
  ...props
}) => {
  return (
    <button
      className={`
        loading-button
        variant-${variant}
        size-${size}
        ${loading ? 'loading' : ''}
        ${className}
      `}
      style={style}
      disabled={disabled || loading}
      onClick={loading ? undefined : onClick}
      {...props}
    >
      {loading ? (
        <div className="button-loading-content">
          <LoadingState
            variant="minimal"
            size="small"
            showMessage={false}
            animated={true}
          />
          {loadingText && <span>{loadingText}</span>}
        </div>
      ) : (
        children
      )}
    </button>
  );
};

// Loading Card Component
export const LoadingCard = ({
  loading = false,
  children,
  skeletonLines = 3,
  className = '',
  style = {},
  ...props
}) => {
  return (
    <div 
      className={`loading-card ${loading ? 'loading' : ''} ${className}`}
      style={style}
      {...props}
    >
      {loading ? (
        <LoadingState
          variant="skeleton"
          skeletonLines={skeletonLines}
          showMessage={false}
          animated={true}
        />
      ) : (
        children
      )}
    </div>
  );
};

// Loading Table Component
export const LoadingTable = ({
  loading = false,
  rows = 5,
  columns = 4,
  className = '',
  style = {}
}) => {
  if (!loading) return null;

  return (
    <div className={`loading-table ${className}`} style={style}>
      <div className="table-header">
        {Array.from({ length: columns }).map((_, index) => (
          <div key={index} className="header-cell">
            <LoadingState
              variant="skeleton"
              skeletonLines={1}
              skeletonHeight={16}
              showMessage={false}
            />
          </div>
        ))}
      </div>
      
      <div className="table-body">
        {Array.from({ length: rows }).map((_, rowIndex) => (
          <div key={rowIndex} className="table-row">
            {Array.from({ length: columns }).map((_, colIndex) => (
              <div key={colIndex} className="table-cell">
                <LoadingState
                  variant="skeleton"
                  skeletonLines={1}
                  skeletonHeight={14}
                  showMessage={false}
                  style={{ animationDelay: `${(rowIndex * columns + colIndex) * 0.05}s` }}
                />
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default LoadingState;
