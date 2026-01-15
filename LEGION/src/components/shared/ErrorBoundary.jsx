// src/components/shared/ErrorBoundary.jsx
// Enterprise Error Boundary Component

import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null,
      retryCount: 0
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { 
      hasError: true,
      errorId: Date.now() + Math.random().toString(36).substr(2, 9)
    };
  }

  componentDidCatch(error, errorInfo) {
    // Store error details
    this.setState({
      error,
      errorInfo,
      hasError: true
    });

    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    // Report error to monitoring service
    this.reportError(error, errorInfo);
  }

  reportError = (error, errorInfo) => {
    try {
      // Enterprise error reporting
      const errorReport = {
        message: error?.message || 'Unknown error',
        stack: error?.stack || 'No stack trace',
        componentStack: errorInfo?.componentStack || 'No component stack',
        timestamp: new Date().toISOString(),
        url: window.location.href,
        userAgent: navigator.userAgent,
        errorId: this.state.errorId,
        retryCount: this.state.retryCount,
        props: this.props.reportProps ? JSON.stringify(this.props) : null
      };

      // Log to enterprise monitoring
      if (this.props.onError) {
        this.props.onError(errorReport);
      }

      // Store in session storage for debugging
      const errorHistory = JSON.parse(sessionStorage.getItem('errorHistory') || '[]');
      errorHistory.push(errorReport);
      // Keep only last 10 errors
      if (errorHistory.length > 10) {
        errorHistory.shift();
      }
      sessionStorage.setItem('errorHistory', JSON.stringify(errorHistory));

    } catch (reportingError) {
      console.error('Failed to report error:', reportingError);
    }
  };

  handleRetry = () => {
    this.setState(prevState => ({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: prevState.retryCount + 1
    }));

    // Call custom retry handler if provided
    if (this.props.onRetry) {
      this.props.onRetry(this.state.retryCount + 1);
    }
  };

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null,
      retryCount: 0
    });

    // Call custom reset handler if provided
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback(
          this.state.error,
          this.state.errorInfo,
          this.handleRetry,
          this.handleReset,
          this.state.retryCount
        );
      }

      // Render fallback UI based on variant
      return (
        <ErrorFallback
          error={this.state.error}
          errorInfo={this.state.errorInfo}
          errorId={this.state.errorId}
          retryCount={this.state.retryCount}
          onRetry={this.handleRetry}
          onReset={this.handleReset}
          variant={this.props.variant}
          size={this.props.size}
          showDetails={this.props.showDetails}
          showRetry={this.props.showRetry}
          showReset={this.props.showReset}
          title={this.props.title}
          message={this.props.message}
          className={this.props.className}
          style={this.props.style}
        />
      );
    }

    return this.props.children;
  }
}

// Error Fallback Component
const ErrorFallback = ({
  error,
  errorInfo,
  errorId,
  retryCount = 0,
  onRetry,
  onReset,
  variant = 'default', // 'default', 'minimal', 'detailed', 'card', 'inline'
  size = 'medium', // 'small', 'medium', 'large'
  showDetails = process.env.NODE_ENV === 'development',
  showRetry = true,
  showReset = true,
  title = 'Something went wrong',
  message = 'An unexpected error occurred. Please try again.',
  className = '',
  style = {}
}) => {
  const [detailsExpanded, setDetailsExpanded] = React.useState(false);

  const toggleDetails = () => {
    setDetailsExpanded(!detailsExpanded);
  };

  const copyErrorDetails = () => {
    const errorDetails = {
      message: error?.message || 'Unknown error',
      stack: error?.stack || 'No stack trace',
      componentStack: errorInfo?.componentStack || 'No component stack',
      errorId,
      timestamp: new Date().toISOString(),
      retryCount
    };

    navigator.clipboard.writeText(JSON.stringify(errorDetails, null, 2))
      .then(() => {
        // Show success feedback
        const button = document.querySelector('.copy-error-button');
        if (button) {
          const originalText = button.textContent;
          button.textContent = 'Copied!';
          button.classList.add('copied');
          setTimeout(() => {
            button.textContent = originalText;
            button.classList.remove('copied');
          }, 2000);
        }
      })
      .catch(err => {
        console.error('Failed to copy error details:', err);
      });
  };

  // Minimal variant
  if (variant === 'minimal') {
    return (
      <div className={`error-fallback minimal ${className}`} style={style}>
        <div className="error-icon">
          <i className="fas fa-exclamation-triangle" />
        </div>
        <span className="error-message">{message}</span>
        {showRetry && (
          <button
            className="retry-button minimal"
            onClick={onRetry}
            title="Retry"
          >
            <i className="fas fa-redo" />
          </button>
        )}
      </div>
    );
  }

  // Inline variant
  if (variant === 'inline') {
    return (
      <div className={`error-fallback inline ${className}`} style={style}>
        <div className="error-content">
          <i className="fas fa-exclamation-circle error-icon" />
          <span className="error-text">{message}</span>
          {showRetry && (
            <button className="retry-button inline" onClick={onRetry}>
              Try Again
            </button>
          )}
        </div>
      </div>
    );
  }

  // Default and other variants
  return (
    <div 
      className={`
        error-fallback 
        variant-${variant} 
        size-${size}
        ${className}
      `} 
      style={style}
      role="alert"
      aria-live="assertive"
    >
      {/* Error Icon */}
      <div className="error-icon-container">
        <div className="error-icon">
          <i className="fas fa-exclamation-triangle" />
        </div>
      </div>

      {/* Error Content */}
      <div className="error-content">
        <h3 className="error-title">{title}</h3>
        <p className="error-message">{message}</p>

        {/* Error ID */}
        {errorId && (
          <div className="error-id">
            <small>Error ID: {errorId}</small>
          </div>
        )}

        {/* Retry Count */}
        {retryCount > 0 && (
          <div className="retry-count">
            <small>Retry attempts: {retryCount}</small>
          </div>
        )}

        {/* Action Buttons */}
        <div className="error-actions">
          {showRetry && (
            <button
              className="retry-button"
              onClick={onRetry}
              disabled={retryCount >= 3}
            >
              <i className="fas fa-redo" />
              {retryCount >= 3 ? 'Max Retries Reached' : 'Try Again'}
            </button>
          )}

          {showReset && (
            <button
              className="reset-button"
              onClick={onReset}
            >
              <i className="fas fa-refresh" />
              Reset
            </button>
          )}

          {showDetails && (
            <button
              className="details-button"
              onClick={toggleDetails}
            >
              <i className={`fas fa-chevron-${detailsExpanded ? 'up' : 'down'}`} />
              {detailsExpanded ? 'Hide' : 'Show'} Details
            </button>
          )}
        </div>

        {/* Error Details */}
        {showDetails && detailsExpanded && (
          <div className="error-details">
            <div className="details-header">
              <h4>Error Details</h4>
              <button
                className="copy-error-button"
                onClick={copyErrorDetails}
                title="Copy error details to clipboard"
              >
                <i className="fas fa-copy" />
                Copy
              </button>
            </div>

            <div className="error-info">
              <div className="error-section">
                <h5>Error Message:</h5>
                <pre className="error-text">{error?.message || 'Unknown error'}</pre>
              </div>

              {error?.stack && (
                <div className="error-section">
                  <h5>Stack Trace:</h5>
                  <pre className="error-stack">{error.stack}</pre>
                </div>
              )}

              {errorInfo?.componentStack && (
                <div className="error-section">
                  <h5>Component Stack:</h5>
                  <pre className="component-stack">{errorInfo.componentStack}</pre>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Hook for error handling
export const useErrorHandler = (onError = null) => {
  const [error, setError] = React.useState(null);

  const handleError = React.useCallback((error, errorInfo = {}) => {
    setError({ error, errorInfo });
    
    if (onError) {
      onError(error, errorInfo);
    }
    
    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error caught by useErrorHandler:', error);
    }
  }, [onError]);

  const clearError = React.useCallback(() => {
    setError(null);
  }, []);

  const resetError = React.useCallback(() => {
    setError(null);
  }, []);

  return {
    error: error?.error || null,
    errorInfo: error?.errorInfo || null,
    hasError: !!error,
    handleError,
    clearError,
    resetError
  };
};

// Higher-order component for error boundaries
export const withErrorBoundary = (Component, errorBoundaryProps = {}) => {
  const WrappedComponent = React.forwardRef((props, ref) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <Component {...props} ref={ref} />
    </ErrorBoundary>
  ));

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;
  
  return WrappedComponent;
};

// Async error boundary for handling Promise rejections
export class AsyncErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidMount() {
    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', this.handleUnhandledRejection);
  }

  componentWillUnmount() {
    window.removeEventListener('unhandledrejection', this.handleUnhandledRejection);
  }

  handleUnhandledRejection = (event) => {
    this.setState({
      hasError: true,
      error: event.reason
    });
  };

  render() {
    if (this.state.hasError) {
      return (
        <ErrorFallback
          error={this.state.error}
          onRetry={() => this.setState({ hasError: false, error: null })}
          {...this.props}
        />
      );
    }

    return this.props.children;
  }
}

export { ErrorFallback };
export default ErrorBoundary;
