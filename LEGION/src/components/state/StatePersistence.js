// src/components/state/StatePersistence.js
// LEGION Enterprise Dashboard - State Persistence System

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';

/**
 * State persistence context
 */
const StatePersistenceContext = createContext({
  saveState: () => {},
  loadState: () => {},
  clearState: () => {},
  getStateSize: () => 0,
  isStorageAvailable: true
});

/**
 * Configuration for different storage strategies
 */
const STORAGE_CONFIG = {
  localStorage: {
    available: typeof localStorage !== 'undefined',
    maxSize: 5 * 1024 * 1024, // 5MB typical limit
    sync: true
  },
  sessionStorage: {
    available: typeof sessionStorage !== 'undefined',
    maxSize: 5 * 1024 * 1024,
    sync: true
  },
  indexedDB: {
    available: typeof indexedDB !== 'undefined',
    maxSize: 50 * 1024 * 1024, // Much larger limit
    sync: false
  }
};

/**
 * State persistence provider with multiple storage strategies
 */
export function StatePersistenceProvider({ children, strategy = 'localStorage' }) {
  const [storageAvailable, setStorageAvailable] = useState(false);
  const [storageUsage, setStorageUsage] = useState(0);

  // Check storage availability
  useEffect(() => {
    const checkStorageAvailability = () => {
      try {
        const storage = getStorageInterface(strategy);
        if (storage) {
          // Test write/read
          const testKey = '__legion_storage_test__';
          storage.setItem(testKey, 'test');
          storage.getItem(testKey);
          storage.removeItem(testKey);
          setStorageAvailable(true);
        }
      } catch (error) {
        console.warn(`Storage strategy '${strategy}' not available:`, error);
        setStorageAvailable(false);
      }
    };

    checkStorageAvailability();
  }, [strategy]);

  // Get storage interface based on strategy
  const getStorageInterface = (strategy) => {
    switch (strategy) {
      case 'localStorage':
        return STORAGE_CONFIG.localStorage.available ? localStorage : null;
      case 'sessionStorage':
        return STORAGE_CONFIG.sessionStorage.available ? sessionStorage : null;
      case 'indexedDB':
        // Simplified IndexedDB interface (would need full implementation)
        return null;
      default:
        return null;
    }
  };

  // Calculate storage usage
  const calculateStorageUsage = useCallback(() => {
    try {
      const storage = getStorageInterface(strategy);
      if (!storage) return 0;

      let totalSize = 0;
      for (let key in storage) {
        if (key.startsWith('legion_')) {
          totalSize += (storage.getItem(key) || '').length;
        }
      }
      return totalSize;
    } catch (error) {
      console.warn('Error calculating storage usage:', error);
      return 0;
    }
  }, [strategy]);

  // Update storage usage
  useEffect(() => {
    if (storageAvailable) {
      setStorageUsage(calculateStorageUsage());
    }
  }, [storageAvailable, calculateStorageUsage]);

  // Save state with compression and error handling
  const saveState = useCallback((key, data, options = {}) => {
    try {
      if (!storageAvailable) {
        console.warn('Storage not available for saving state');
        return false;
      }

      const storage = getStorageInterface(strategy);
      if (!storage) return false;

      const fullKey = `legion_${key}`;
      
      // Prepare data for storage
      const stateData = {
        data,
        timestamp: Date.now(),
        version: '1.0',
        metadata: {
          userAgent: navigator.userAgent,
          url: window.location.href,
          ...options.metadata
        }
      };

      // Add compression if data is large
      let serializedData = JSON.stringify(stateData);
      
      if (serializedData.length > 50000 && options.compress !== false) {
        // Basic compression (in real implementation, use LZ-string or similar)
        try {
          serializedData = JSON.stringify(stateData, null, 0); // Remove whitespace
        } catch (compressionError) {
          console.warn('Compression failed:', compressionError);
        }
      }

      // Check size limits
      const maxSize = STORAGE_CONFIG[strategy]?.maxSize || 5 * 1024 * 1024;
      if (serializedData.length > maxSize * 0.8) { // Use 80% of limit
        console.warn(`State data too large for ${strategy}: ${serializedData.length} bytes`);
        return false;
      }

      storage.setItem(fullKey, serializedData);
      setStorageUsage(calculateStorageUsage());
      
      return true;
    } catch (error) {
      console.error('Error saving state:', error);
      
      // Handle quota exceeded
      if (error.name === 'QuotaExceededError') {
        console.warn('Storage quota exceeded, attempting cleanup');
        cleanupOldStates();
        return false;
      }
      
      return false;
    }
  }, [storageAvailable, strategy, calculateStorageUsage]);

  // Load state with validation and migration
  const loadState = useCallback((key, defaultValue = null) => {
    try {
      if (!storageAvailable) return defaultValue;

      const storage = getStorageInterface(strategy);
      if (!storage) return defaultValue;

      const fullKey = `legion_${key}`;
      const storedData = storage.getItem(fullKey);
      
      if (!storedData) return defaultValue;

      const parsedData = JSON.parse(storedData);
      
      // Validate data structure
      if (!parsedData || typeof parsedData !== 'object') {
        return defaultValue;
      }

      // Check version compatibility
      if (parsedData.version && parsedData.version !== '1.0') {
        console.warn(`State version mismatch for ${key}: ${parsedData.version}`);
        // Could implement migration logic here
      }

      // Check data age
      const maxAge = 7 * 24 * 60 * 60 * 1000; // 7 days
      if (parsedData.timestamp && Date.now() - parsedData.timestamp > maxAge) {
        console.info(`Stale state data for ${key}, using default`);
        storage.removeItem(fullKey);
        return defaultValue;
      }

      return parsedData.data || defaultValue;
    } catch (error) {
      console.error('Error loading state:', error);
      return defaultValue;
    }
  }, [storageAvailable, strategy]);

  // Clear specific state
  const clearState = useCallback((key) => {
    try {
      if (!storageAvailable) return false;

      const storage = getStorageInterface(strategy);
      if (!storage) return false;

      const fullKey = `legion_${key}`;
      storage.removeItem(fullKey);
      setStorageUsage(calculateStorageUsage());
      
      return true;
    } catch (error) {
      console.error('Error clearing state:', error);
      return false;
    }
  }, [storageAvailable, strategy, calculateStorageUsage]);

  // Clear all legion states
  const clearAllStates = useCallback(() => {
    try {
      if (!storageAvailable) return false;

      const storage = getStorageInterface(strategy);
      if (!storage) return false;

      const keysToRemove = [];
      for (let key in storage) {
        if (key.startsWith('legion_')) {
          keysToRemove.push(key);
        }
      }

      keysToRemove.forEach(key => storage.removeItem(key));
      setStorageUsage(0);
      
      return true;
    } catch (error) {
      console.error('Error clearing all states:', error);
      return false;
    }
  }, [storageAvailable, strategy]);

  // Cleanup old states when storage is full
  const cleanupOldStates = useCallback(() => {
    try {
      if (!storageAvailable) return;

      const storage = getStorageInterface(strategy);
      if (!storage) return;

      const states = [];
      
      // Collect all legion states with timestamps
      for (let key in storage) {
        if (key.startsWith('legion_')) {
          try {
            const data = JSON.parse(storage.getItem(key) || '{}');
            states.push({
              key,
              timestamp: data.timestamp || 0,
              size: (storage.getItem(key) || '').length
            });
          } catch (parseError) {
            // Invalid state, mark for removal
            states.push({
              key,
              timestamp: 0,
              size: 0
            });
          }
        }
      }

      // Sort by timestamp (oldest first)
      states.sort((a, b) => a.timestamp - b.timestamp);

      // Remove oldest 25% of states
      const toRemove = Math.floor(states.length * 0.25);
      for (let i = 0; i < toRemove; i++) {
        storage.removeItem(states[i].key);
      }

      setStorageUsage(calculateStorageUsage());
    } catch (error) {
      console.error('Error during cleanup:', error);
    }
  }, [storageAvailable, strategy, calculateStorageUsage]);

  // Get storage statistics
  const getStorageStats = useCallback(() => {
    const maxSize = STORAGE_CONFIG[strategy]?.maxSize || 0;
    return {
      used: storageUsage,
      available: maxSize - storageUsage,
      maxSize,
      usagePercentage: maxSize > 0 ? (storageUsage / maxSize) * 100 : 0,
      strategy,
      isAvailable: storageAvailable
    };
  }, [storageUsage, strategy, storageAvailable]);

  const value = {
    saveState,
    loadState,
    clearState,
    clearAllStates,
    getStateSize: () => storageUsage,
    getStorageStats,
    isStorageAvailable: storageAvailable,
    cleanupOldStates
  };

  return (
    <StatePersistenceContext.Provider value={value}>
      {children}
    </StatePersistenceContext.Provider>
  );
}

/**
 * Hook to use state persistence
 */
export function useStatePersistence() {
  const context = useContext(StatePersistenceContext);
  if (!context) {
    throw new Error('useStatePersistence must be used within StatePersistenceProvider');
  }
  return context;
}

/**
 * Hook for persisting specific component state
 */
export function usePersistedState(key, defaultValue, options = {}) {
  const { saveState, loadState } = useStatePersistence();
  const [state, setState] = useState(() => loadState(key, defaultValue));

  // Save state when it changes
  useEffect(() => {
    if (state !== defaultValue) {
      saveState(key, state, options);
    }
  }, [state, key, defaultValue, saveState, options]);

  return [state, setState];
}

/**
 * Hook for tab-specific state persistence
 */
export function useTabState(tabId, stateKey, defaultValue) {
  const key = `tab_${tabId}_${stateKey}`;
  return usePersistedState(key, defaultValue, {
    metadata: { tabId, stateKey }
  });
}

/**
 * Storage monitoring component for development
 */
export function StorageMonitor({ className = '' }) {
  const { getStorageStats, clearAllStates } = useStatePersistence();
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const updateStats = () => {
      setStats(getStorageStats());
    };

    updateStats();
    const interval = setInterval(updateStats, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, [getStorageStats]);

  if (process.env.NODE_ENV !== 'development' || !stats) {
    return null;
  }

  return (
    <div className={`storage-monitor ${className}`} style={{
      position: 'fixed',
      bottom: '60px',
      right: '10px',
      background: 'rgba(0, 0, 0, 0.8)',
      color: 'white',
      padding: '8px 12px',
      borderRadius: '4px',
      fontSize: '11px',
      fontFamily: 'monospace',
      zIndex: 10000,
      minWidth: '200px'
    }}>
      <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>Storage Monitor</div>
      <div>Strategy: {stats.strategy}</div>
      <div>Used: {(stats.used / 1024).toFixed(1)}KB</div>
      <div>Usage: {stats.usagePercentage.toFixed(1)}%</div>
      <div>Available: {stats.isAvailable ? 'Yes' : 'No'}</div>
      {stats.usagePercentage > 80 && (
        <button 
          onClick={clearAllStates}
          style={{
            marginTop: '4px',
            padding: '2px 6px',
            background: '#e53e3e',
            border: 'none',
            borderRadius: '2px',
            color: 'white',
            fontSize: '10px',
            cursor: 'pointer'
          }}
        >
          Clear All
        </button>
      )}
    </div>
  );
}

export default StatePersistenceProvider;
