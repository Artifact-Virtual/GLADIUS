// src/services/ErrorHandlingService.js
// LEGION Enterprise Dashboard - Error Handling Service
// Comprehensive error management, logging, recovery, and monitoring service

/**
 * Error Handling Service
 * Provides comprehensive error management, logging, recovery strategies,
 * and monitoring for the LEGION Enterprise Dashboard system
 */
class ErrorHandlingService {
  constructor() {
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.errorLog = [];
    this.errorHandlers = new Map();
    this.retryPolicies = new Map();
    this.circuitBreakers = new Map();
    this.errorStats = {
      totalErrors: 0,
      recoveredErrors: 0,
      criticalErrors: 0,
      networkErrors: 0,
      apiErrors: 0,
      systemErrors: 0
    };
    
    // Error configuration
    this.config = {
      maxLogSize: 10000,
      maxRetryAttempts: 5,
      retryDelay: 1000,
      circuitBreakerThreshold: 10,
      circuitBreakerTimeout: 60000,
      enableAutoRecovery: true,
      enableErrorReporting: true,
      logLevel: 'ERROR',
      persistErrors: true,
      enableMetrics: true
    };

    // Error categories and severity levels
    this.errorCategories = {
      NETWORK: { priority: 'HIGH', recoverable: true, autoRetry: true },
      API: { priority: 'HIGH', recoverable: true, autoRetry: true },
      AUTHENTICATION: { priority: 'CRITICAL', recoverable: false, autoRetry: false },
      AUTHORIZATION: { priority: 'HIGH', recoverable: false, autoRetry: false },
      VALIDATION: { priority: 'MEDIUM', recoverable: true, autoRetry: false },
      SYSTEM: { priority: 'CRITICAL', recoverable: false, autoRetry: false },
      BUSINESS_LOGIC: { priority: 'HIGH', recoverable: true, autoRetry: false },
      DATA: { priority: 'HIGH', recoverable: true, autoRetry: true },
      UI: { priority: 'LOW', recoverable: true, autoRetry: false },
      TIMEOUT: { priority: 'MEDIUM', recoverable: true, autoRetry: true }
    };

    this.logLevels = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'];
    
    // Initialize error handling service
    this.initializeErrorHandling();
    
    console.log('ErrorHandlingService initialized');
  }

  /**
   * Initialize error handling and monitoring
   */
  initializeErrorHandling() {
    // Global error handlers
    window.addEventListener('error', (event) => {
      this.handleGlobalError(event.error, 'SYSTEM', event);
    });

    window.addEventListener('unhandledrejection', (event) => {
      this.handleGlobalError(event.reason, 'SYSTEM', event);
    });

    // API error interceptor setup
    this.setupApiErrorInterception();

    // Periodic error log cleanup
    setInterval(() => {
      this.cleanupErrorLog();
    }, 300000); // 5 minutes

    // Circuit breaker monitoring
    setInterval(() => {
      this.monitorCircuitBreakers();
    }, 30000); // 30 seconds

    // Error metrics collection
    if (this.config.enableMetrics) {
      setInterval(() => {
        this.collectErrorMetrics();
      }, 60000); // 1 minute
    }
  }

  /**
   * Core Error Handling
   */
  handleError(error, category = 'SYSTEM', context = {}, options = {}) {
    try {
      const errorEntry = this.createErrorEntry(error, category, context, options);
      
      // Log error
      this.logError(errorEntry);
      
      // Update statistics
      this.updateErrorStats(errorEntry);
      
      // Attempt recovery if enabled
      if (this.shouldAttemptRecovery(errorEntry)) {
        return this.attemptRecovery(errorEntry);
      }
      
      // Check circuit breaker
      this.updateCircuitBreaker(category, errorEntry);
      
      // Notify error handlers
      this.notifyErrorHandlers(errorEntry);
      
      // Report error if enabled
      if (this.config.enableErrorReporting) {
        this.reportError(errorEntry);
      }
      
      return errorEntry;
    } catch (handlingError) {
      console.error('Error in error handling:', handlingError);
      return null;
    }
  }

  async handleAsyncError(asyncFunction, category = 'SYSTEM', context = {}, retryOptions = {}) {
    const maxRetries = retryOptions.maxRetries || this.config.maxRetryAttempts;
    const retryDelay = retryOptions.retryDelay || this.config.retryDelay;
    let lastError;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        const result = await asyncFunction();
        
        // Reset circuit breaker on success
        this.resetCircuitBreaker(category);
        
        return result;
      } catch (error) {
        lastError = error;
        
        const errorEntry = this.handleError(error, category, {
          ...context,
          attempt,
          maxRetries
        });

        // Check if we should retry
        if (attempt < maxRetries && this.shouldRetry(errorEntry, retryOptions)) {
          await this.delay(retryDelay * Math.pow(2, attempt - 1)); // Exponential backoff
          continue;
        }
        
        break;
      }
    }

    // All retries failed
    const finalErrorEntry = this.handleError(lastError, category, {
      ...context,
      finalAttempt: true,
      totalAttempts: maxRetries
    });

    throw lastError;
  }

  /**
   * Error Recovery Strategies
   */
  async attemptRecovery(errorEntry) {
    const { category, error, context } = errorEntry;
    
    try {
      switch (category) {
        case 'NETWORK':
          return await this.recoverFromNetworkError(errorEntry);
          
        case 'API':
          return await this.recoverFromApiError(errorEntry);
          
        case 'DATA':
          return await this.recoverFromDataError(errorEntry);
          
        case 'TIMEOUT':
          return await this.recoverFromTimeoutError(errorEntry);
          
        case 'VALIDATION':
          return await this.recoverFromValidationError(errorEntry);
          
        default:
          return await this.defaultRecovery(errorEntry);
      }
    } catch (recoveryError) {
      console.error('Error recovery failed:', recoveryError);
      errorEntry.recoveryFailed = true;
      errorEntry.recoveryError = recoveryError.message;
      return null;
    }
  }

  async recoverFromNetworkError(errorEntry) {
    const { context } = errorEntry;
    
    // Check network connectivity
    if (!navigator.onLine) {
      return this.handleOfflineMode(errorEntry);
    }
    
    // Retry with fallback URL if available
    if (context.fallbackUrl) {
      try {
        const response = await fetch(context.fallbackUrl, context.options);
        errorEntry.recovered = true;
        errorEntry.recoveryMethod = 'fallback_url';
        this.errorStats.recoveredErrors++;
        return response;
      } catch (fallbackError) {
        console.warn('Fallback URL also failed:', fallbackError);
      }
    }
    
    return null;
  }

  async recoverFromApiError(errorEntry) {
    const { error, context } = errorEntry;
    
    // Handle specific HTTP status codes
    if (error.status) {
      switch (error.status) {
        case 401:
          return await this.handleAuthenticationError(errorEntry);
          
        case 403:
          return await this.handleAuthorizationError(errorEntry);
          
        case 429:
          return await this.handleRateLimitError(errorEntry);
          
        case 500:
        case 502:
        case 503:
        case 504:
          return await this.handleServerError(errorEntry);
          
        default:
          return null;
      }
    }
    
    return null;
  }

  async recoverFromDataError(errorEntry) {
    const { context } = errorEntry;
    
    // Try to recover from cache
    if (context.cacheKey && window.cacheService) {
      try {
        const cachedData = await window.cacheService.get(context.cacheKey);
        if (cachedData) {
          errorEntry.recovered = true;
          errorEntry.recoveryMethod = 'cache_fallback';
          this.errorStats.recoveredErrors++;
          return cachedData;
        }
      } catch (cacheError) {
        console.warn('Cache recovery failed:', cacheError);
      }
    }
    
    // Try alternative data source
    if (context.alternativeSource) {
      try {
        const data = await context.alternativeSource();
        errorEntry.recovered = true;
        errorEntry.recoveryMethod = 'alternative_source';
        this.errorStats.recoveredErrors++;
        return data;
      } catch (altError) {
        console.warn('Alternative source failed:', altError);
      }
    }
    
    return null;
  }

  async recoverFromTimeoutError(errorEntry) {
    const { context } = errorEntry;
    
    // Increase timeout and retry
    if (context.originalTimeout && context.maxTimeout) {
      const newTimeout = Math.min(context.originalTimeout * 2, context.maxTimeout);
      
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), newTimeout);
        
        const response = await fetch(context.url, {
          ...context.options,
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        errorEntry.recovered = true;
        errorEntry.recoveryMethod = 'timeout_increase';
        this.errorStats.recoveredErrors++;
        return response;
      } catch (retryError) {
        console.warn('Timeout recovery failed:', retryError);
      }
    }
    
    return null;
  }

  async recoverFromValidationError(errorEntry) {
    const { context } = errorEntry;
    
    // Apply automatic data sanitization if available
    if (context.sanitizer && context.originalData) {
      try {
        const sanitizedData = context.sanitizer(context.originalData);
        errorEntry.recovered = true;
        errorEntry.recoveryMethod = 'data_sanitization';
        this.errorStats.recoveredErrors++;
        return sanitizedData;
      } catch (sanitizeError) {
        console.warn('Data sanitization failed:', sanitizeError);
      }
    }
    
    return null;
  }

  async defaultRecovery(errorEntry) {
    const { context } = errorEntry;
    
    // Generic recovery strategies
    if (context.defaultValue !== undefined) {
      errorEntry.recovered = true;
      errorEntry.recoveryMethod = 'default_value';
      this.errorStats.recoveredErrors++;
      return context.defaultValue;
    }
    
    return null;
  }

  /**
   * Specialized Error Handlers
   */
  async handleAuthenticationError(errorEntry) {
    // Attempt token refresh
    try {
      const newToken = await this.refreshAuthToken();
      if (newToken) {
        errorEntry.recovered = true;
        errorEntry.recoveryMethod = 'token_refresh';
        this.errorStats.recoveredErrors++;
        return { token: newToken };
      }
    } catch (refreshError) {
      console.error('Token refresh failed:', refreshError);
    }
    
    // Redirect to login if refresh fails
    this.redirectToLogin();
    return null;
  }

  async handleAuthorizationError(errorEntry) {
    // Log security incident
    this.logSecurityIncident(errorEntry);
    
    // Check if user has alternate permissions
    if (errorEntry.context.alternatePermissions) {
      try {
        const hasPermission = await this.checkAlternatePermissions(
          errorEntry.context.alternatePermissions
        );
        
        if (hasPermission) {
          errorEntry.recovered = true;
          errorEntry.recoveryMethod = 'alternate_permissions';
          this.errorStats.recoveredErrors++;
          return { authorized: true };
        }
      } catch (permError) {
        console.error('Permission check failed:', permError);
      }
    }
    
    return null;
  }

  async handleRateLimitError(errorEntry) {
    const { context } = errorEntry;
    
    // Extract retry-after header if available
    const retryAfter = context.headers?.['retry-after'] || 60;
    
    // Wait for rate limit reset
    await this.delay(retryAfter * 1000);
    
    errorEntry.recovered = true;
    errorEntry.recoveryMethod = 'rate_limit_wait';
    this.errorStats.recoveredErrors++;
    
    return { retryAfter };
  }

  async handleServerError(errorEntry) {
    const { context } = errorEntry;
    
    // Try alternative server endpoints
    if (context.alternativeEndpoints) {
      for (const endpoint of context.alternativeEndpoints) {
        try {
          const response = await fetch(endpoint, context.options);
          errorEntry.recovered = true;
          errorEntry.recoveryMethod = 'alternative_endpoint';
          this.errorStats.recoveredErrors++;
          return response;
        } catch (endpointError) {
          console.warn(`Alternative endpoint failed: ${endpoint}`, endpointError);
        }
      }
    }
    
    return null;
  }

  handleOfflineMode(errorEntry) {
    // Switch to offline mode
    if (window.cacheService) {
      const offlineData = window.cacheService.getOfflineData(errorEntry.context.cacheKey);
      if (offlineData) {
        errorEntry.recovered = true;
        errorEntry.recoveryMethod = 'offline_cache';
        this.errorStats.recoveredErrors++;
        return offlineData;
      }
    }
    
    return null;
  }

  /**
   * Circuit Breaker Pattern
   */
  updateCircuitBreaker(category, errorEntry) {
    if (!this.circuitBreakers.has(category)) {
      this.circuitBreakers.set(category, {
        state: 'CLOSED',
        failureCount: 0,
        lastFailure: null,
        nextAttempt: null
      });
    }
    
    const breaker = this.circuitBreakers.get(category);
    
    if (errorEntry.recovered) {
      // Reset on successful recovery
      breaker.failureCount = 0;
      breaker.state = 'CLOSED';
    } else {
      // Increment failure count
      breaker.failureCount++;
      breaker.lastFailure = Date.now();
      
      // Open circuit if threshold exceeded
      if (breaker.failureCount >= this.config.circuitBreakerThreshold) {
        breaker.state = 'OPEN';
        breaker.nextAttempt = Date.now() + this.config.circuitBreakerTimeout;
      }
    }
  }

  resetCircuitBreaker(category) {
    if (this.circuitBreakers.has(category)) {
      const breaker = this.circuitBreakers.get(category);
      breaker.failureCount = 0;
      breaker.state = 'CLOSED';
      breaker.nextAttempt = null;
    }
  }

  isCircuitBreakerOpen(category) {
    const breaker = this.circuitBreakers.get(category);
    if (!breaker) return false;
    
    if (breaker.state === 'OPEN') {
      if (Date.now() > breaker.nextAttempt) {
        breaker.state = 'HALF_OPEN';
        return false;
      }
      return true;
    }
    
    return false;
  }

  monitorCircuitBreakers() {
    this.circuitBreakers.forEach((breaker, category) => {
      if (breaker.state === 'OPEN' && Date.now() > breaker.nextAttempt) {
        breaker.state = 'HALF_OPEN';
        console.log(`Circuit breaker for ${category} moved to HALF_OPEN state`);
      }
    });
  }

  /**
   * Error Registration and Handlers
   */
  registerErrorHandler(category, handler) {
    if (!this.errorHandlers.has(category)) {
      this.errorHandlers.set(category, new Set());
    }
    this.errorHandlers.get(category).add(handler);
    
    return () => {
      this.errorHandlers.get(category)?.delete(handler);
    };
  }

  registerRetryPolicy(category, policy) {
    this.retryPolicies.set(category, policy);
  }

  notifyErrorHandlers(errorEntry) {
    const handlers = this.errorHandlers.get(errorEntry.category);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(errorEntry);
        } catch (handlerError) {
          console.error('Error handler failed:', handlerError);
        }
      });
    }
    
    // Also notify global handlers
    const globalHandlers = this.errorHandlers.get('GLOBAL');
    if (globalHandlers) {
      globalHandlers.forEach(handler => {
        try {
          handler(errorEntry);
        } catch (handlerError) {
          console.error('Global error handler failed:', handlerError);
        }
      });
    }
  }

  /**
   * Error Logging and Reporting
   */
  logError(errorEntry) {
    // Add to error log
    this.errorLog.push(errorEntry);
    
    // Console logging based on severity
    const logLevel = this.getLogLevel(errorEntry.severity);
    const message = this.formatErrorMessage(errorEntry);
    
    switch (logLevel) {
      case 'CRITICAL':
        console.error('[CRITICAL]', message, errorEntry);
        break;
      case 'ERROR':
        console.error('[ERROR]', message, errorEntry);
        break;
      case 'WARN':
        console.warn('[WARN]', message, errorEntry);
        break;
      case 'INFO':
        console.info('[INFO]', message, errorEntry);
        break;
      case 'DEBUG':
        console.debug('[DEBUG]', message, errorEntry);
        break;
    }
    
    // Persist to storage if enabled
    if (this.config.persistErrors) {
      this.persistError(errorEntry);
    }
  }

  async reportError(errorEntry) {
    try {
      // Only report non-sensitive errors
      if (!this.isSensitiveError(errorEntry)) {
        await fetch(`${this.baseUrl}/api/errors/report`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            ...errorEntry,
            userAgent: navigator.userAgent,
            url: window.location.href,
            timestamp: Date.now()
          })
        });
      }
    } catch (reportingError) {
      console.warn('Error reporting failed:', reportingError);
    }
  }

  /**
   * Utility Methods
   */
  createErrorEntry(error, category, context, options) {
    const now = Date.now();
    const categoryConfig = this.errorCategories[category] || this.errorCategories.SYSTEM;
    
    return {
      id: this.generateErrorId(),
      timestamp: now,
      error: {
        name: error.name || 'Unknown',
        message: error.message || 'Unknown error',
        stack: error.stack,
        status: error.status,
        code: error.code
      },
      category,
      severity: categoryConfig.priority,
      context: {
        ...context,
        url: window.location.href,
        userAgent: navigator.userAgent,
        timestamp: now
      },
      recoverable: categoryConfig.recoverable,
      autoRetry: categoryConfig.autoRetry,
      recovered: false,
      recoveryMethod: null,
      recoveryFailed: false,
      options
    };
  }

  shouldAttemptRecovery(errorEntry) {
    return this.config.enableAutoRecovery && 
           errorEntry.recoverable && 
           !this.isCircuitBreakerOpen(errorEntry.category);
  }

  shouldRetry(errorEntry, retryOptions) {
    const categoryPolicy = this.retryPolicies.get(errorEntry.category);
    
    if (categoryPolicy) {
      return categoryPolicy.shouldRetry(errorEntry, retryOptions);
    }
    
    // Default retry logic
    return errorEntry.autoRetry && 
           !this.isCircuitBreakerOpen(errorEntry.category) &&
           this.isRetryableError(errorEntry);
  }

  isRetryableError(errorEntry) {
    const { error, category } = errorEntry;
    
    // Network errors are generally retryable
    if (category === 'NETWORK' || category === 'TIMEOUT') {
      return true;
    }
    
    // API errors with certain status codes
    if (category === 'API' && error.status) {
      const retryableStatus = [408, 429, 500, 502, 503, 504];
      return retryableStatus.includes(error.status);
    }
    
    return false;
  }

  isSensitiveError(errorEntry) {
    const sensitiveCategories = ['AUTHENTICATION', 'AUTHORIZATION'];
    const sensitiveKeywords = ['password', 'token', 'key', 'secret'];
    
    if (sensitiveCategories.includes(errorEntry.category)) {
      return true;
    }
    
    const errorString = JSON.stringify(errorEntry).toLowerCase();
    return sensitiveKeywords.some(keyword => errorString.includes(keyword));
  }

  generateErrorId() {
    return `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  formatErrorMessage(errorEntry) {
    return `[${errorEntry.category}] ${errorEntry.error.message} (ID: ${errorEntry.id})`;
  }

  getLogLevel(severity) {
    switch (severity) {
      case 'CRITICAL':
        return 'CRITICAL';
      case 'HIGH':
        return 'ERROR';
      case 'MEDIUM':
        return 'WARN';
      case 'LOW':
        return 'INFO';
      default:
        return 'ERROR';
    }
  }

  updateErrorStats(errorEntry) {
    this.errorStats.totalErrors++;
    
    switch (errorEntry.category) {
      case 'NETWORK':
        this.errorStats.networkErrors++;
        break;
      case 'API':
        this.errorStats.apiErrors++;
        break;
      case 'SYSTEM':
        this.errorStats.systemErrors++;
        break;
    }
    
    if (errorEntry.severity === 'CRITICAL') {
      this.errorStats.criticalErrors++;
    }
  }

  cleanupErrorLog() {
    if (this.errorLog.length > this.config.maxLogSize) {
      this.errorLog = this.errorLog.slice(-this.config.maxLogSize);
    }
  }

  persistError(errorEntry) {
    try {
      const existingErrors = JSON.parse(localStorage.getItem('errorLog') || '[]');
      existingErrors.push(errorEntry);
      
      // Keep only recent errors
      const recentErrors = existingErrors.slice(-1000);
      localStorage.setItem('errorLog', JSON.stringify(recentErrors));
    } catch (storageError) {
      console.warn('Error persistence failed:', storageError);
    }
  }

  collectErrorMetrics() {
    const metrics = {
      timestamp: Date.now(),
      ...this.errorStats,
      circuitBreakers: Object.fromEntries(
        Array.from(this.circuitBreakers.entries()).map(([key, value]) => [
          key,
          { state: value.state, failures: value.failureCount }
        ])
      ),
      recentErrors: this.errorLog.slice(-100).length
    };
    
    // Send metrics to analytics service
    if (window.analyticsService) {
      window.analyticsService.trackErrorMetrics(metrics);
    }
  }

  setupApiErrorInterception() {
    // Intercept fetch requests for error handling
    const originalFetch = window.fetch;
    
    window.fetch = async (...args) => {
      try {
        const response = await originalFetch(...args);
        
        if (!response.ok) {
          const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
          error.status = response.status;
          error.response = response;
          
          this.handleError(error, 'API', {
            url: args[0],
            options: args[1],
            status: response.status
          });
        }
        
        return response;
      } catch (networkError) {
        this.handleError(networkError, 'NETWORK', {
          url: args[0],
          options: args[1]
        });
        throw networkError;
      }
    };
  }

  handleGlobalError(error, category, event) {
    this.handleError(error, category, {
      event: event.type,
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
      global: true
    });
  }

  async refreshAuthToken() {
    // Placeholder for token refresh logic
    return null;
  }

  redirectToLogin() {
    // Placeholder for login redirect
    console.log('Redirecting to login...');
  }

  logSecurityIncident(errorEntry) {
    console.warn('Security incident logged:', errorEntry);
  }

  async checkAlternatePermissions(permissions) {
    // Placeholder for permission checking
    return false;
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Public API
   */
  getErrorLog(filter = {}) {
    let filtered = this.errorLog;
    
    if (filter.category) {
      filtered = filtered.filter(e => e.category === filter.category);
    }
    
    if (filter.severity) {
      filtered = filtered.filter(e => e.severity === filter.severity);
    }
    
    if (filter.since) {
      filtered = filtered.filter(e => e.timestamp >= filter.since);
    }
    
    return filtered;
  }

  getErrorStats() {
    return { ...this.errorStats };
  }

  getCircuitBreakerStatus() {
    return Object.fromEntries(
      Array.from(this.circuitBreakers.entries()).map(([key, value]) => [
        key,
        {
          state: value.state,
          failureCount: value.failureCount,
          nextAttempt: value.nextAttempt
        }
      ])
    );
  }

  async healthCheck() {
    return {
      status: 'healthy',
      errorLog: this.errorLog.length,
      circuitBreakers: this.circuitBreakers.size,
      errorHandlers: this.errorHandlers.size,
      stats: this.errorStats,
      timestamp: new Date().toISOString()
    };
  }

  destroy() {
    this.errorLog = [];
    this.errorHandlers.clear();
    this.retryPolicies.clear();
    this.circuitBreakers.clear();
    
    console.log('ErrorHandlingService destroyed');
  }
}

// Create singleton instance
const errorHandlingService = new ErrorHandlingService();

export default errorHandlingService;
export { ErrorHandlingService };
