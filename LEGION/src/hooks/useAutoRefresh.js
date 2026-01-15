// src/hooks/useAutoRefresh.js
// Enterprise Auto-Refresh Hook for Static Data Management

import { useState, useEffect, useRef, useCallback } from 'react';

const useAutoRefresh = ({
  fetchFunction,
  interval = 30000, // 30 seconds default
  enabled = true,
  dependencies = [],
  onError = null,
  onSuccess = null,
  retryAttempts = 3,
  retryDelay = 1000,
  refreshOnFocus = true,
  refreshOnReconnect = true
}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [refreshCount, setRefreshCount] = useState(0);
  const [nextRefresh, setNextRefresh] = useState(null);

  const intervalRef = useRef(null);
  const mountedRef = useRef(true);
  const retryTimeoutRef = useRef(null);
  const fetchAttemptRef = useRef(0);

  // Manual refresh trigger
  const [manualRefreshTrigger, setManualRefreshTrigger] = useState(0);

  // Calculate next refresh time
  const calculateNextRefresh = useCallback(() => {
    if (interval > 0) {
      return new Date(Date.now() + interval);
    }
    return null;
  }, [interval]);

  // Fetch data with retry logic
  const fetchData = useCallback(async (isRetry = false) => {
    if (!fetchFunction || !mountedRef.current) return;

    if (!isRetry) {
      setLoading(true);
      setError(null);
      fetchAttemptRef.current = 0;
    }

    try {
      const result = await fetchFunction();
      
      if (mountedRef.current) {
        setData(result);
        setError(null);
        setLastUpdate(new Date());
        setRefreshCount(prev => prev + 1);
        setNextRefresh(calculateNextRefresh());
        fetchAttemptRef.current = 0;
        
        if (onSuccess) {
          onSuccess(result);
        }
      }
    } catch (err) {
      if (!mountedRef.current) return;

      fetchAttemptRef.current += 1;
      
      if (fetchAttemptRef.current < retryAttempts) {
        // Retry with exponential backoff
        const delay = retryDelay * Math.pow(2, fetchAttemptRef.current - 1);
        
        retryTimeoutRef.current = setTimeout(() => {
          if (mountedRef.current) {
            fetchData(true);
          }
        }, delay);
      } else {
        // Max retries reached
        setError(err);
        setLastUpdate(new Date());
        fetchAttemptRef.current = 0;
        
        if (onError) {
          onError(err);
        }
      }
    } finally {
      if (!isRetry && mountedRef.current) {
        setLoading(false);
      }
    }
  }, [fetchFunction, retryAttempts, retryDelay, onError, onSuccess, calculateNextRefresh]);

  // Start auto-refresh interval
  const startInterval = useCallback(() => {
    if (interval > 0 && enabled) {
      intervalRef.current = setInterval(() => {
        fetchData();
      }, interval);
      
      setNextRefresh(calculateNextRefresh());
    }
  }, [interval, enabled, fetchData, calculateNextRefresh]);

  // Stop auto-refresh interval
  const stopInterval = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }
    
    setNextRefresh(null);
  }, []);

  // Manual refresh
  const refresh = useCallback(() => {
    setManualRefreshTrigger(prev => prev + 1);
    fetchData();
  }, [fetchData]);

  // Force refresh (bypasses loading state)
  const forceRefresh = useCallback(async () => {
    try {
      const result = await fetchFunction();
      
      if (mountedRef.current) {
        setData(result);
        setError(null);
        setLastUpdate(new Date());
        setRefreshCount(prev => prev + 1);
        
        if (onSuccess) {
          onSuccess(result);
        }
      }
      
      return result;
    } catch (err) {
      if (mountedRef.current) {
        setError(err);
      }
      throw err;
    }
  }, [fetchFunction, onSuccess]);

  // Pause auto-refresh
  const pause = useCallback(() => {
    stopInterval();
  }, [stopInterval]);

  // Resume auto-refresh
  const resume = useCallback(() => {
    if (enabled) {
      startInterval();
    }
  }, [enabled, startInterval]);

  // Handle visibility change (refresh on focus)
  useEffect(() => {
    if (!refreshOnFocus) return;

    const handleVisibilityChange = () => {
      if (!document.hidden && enabled) {
        // Refresh if more than half the interval has passed
        const timeSinceLastUpdate = lastUpdate ? Date.now() - lastUpdate.getTime() : Infinity;
        if (timeSinceLastUpdate > interval / 2) {
          fetchData();
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [refreshOnFocus, enabled, lastUpdate, interval, fetchData]);

  // Handle online/offline status
  useEffect(() => {
    if (!refreshOnReconnect) return;

    const handleOnline = () => {
      if (enabled) {
        fetchData();
        startInterval();
      }
    };

    const handleOffline = () => {
      stopInterval();
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [refreshOnReconnect, enabled, fetchData, startInterval, stopInterval]);

  // Initial fetch and interval setup
  useEffect(() => {
    if (fetchFunction && enabled) {
      fetchData();
      startInterval();
    }

    return () => {
      stopInterval();
    };
  }, [fetchFunction, enabled, startInterval, stopInterval, ...dependencies]);

  // Handle manual refresh trigger
  useEffect(() => {
    if (manualRefreshTrigger > 0) {
      stopInterval();
      startInterval();
    }
  }, [manualRefreshTrigger, stopInterval, startInterval]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      mountedRef.current = false;
      stopInterval();
    };
  }, [stopInterval]);

  // Calculate time until next refresh
  const timeUntilNextRefresh = nextRefresh ? Math.max(0, nextRefresh.getTime() - Date.now()) : null;

  return {
    // Data
    data,
    loading,
    error,
    lastUpdate,
    refreshCount,
    nextRefresh,
    timeUntilNextRefresh,
    
    // Status
    isActive: !!intervalRef.current,
    isPaused: enabled && !intervalRef.current,
    isOnline: navigator.onLine,
    
    // Actions
    refresh,
    forceRefresh,
    pause,
    resume,
    
    // Info
    getStatus: () => ({
      enabled,
      interval,
      refreshCount,
      lastUpdate,
      nextRefresh,
      isActive: !!intervalRef.current,
      retryAttempt: fetchAttemptRef.current,
      error: error?.message
    })
  };
};

export default useAutoRefresh;
