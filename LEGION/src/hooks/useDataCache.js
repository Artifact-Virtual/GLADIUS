// src/hooks/useDataCache.js
// Enterprise Data Caching and Offline Handling Hook

import { useState, useEffect, useRef, useCallback } from 'react';

const useDataCache = ({
  key,
  fetchFunction,
  cacheTimeout = 300000, // 5 minutes default
  enablePersistence = true,
  enableOfflineMode = true,
  offlineTimeout = 86400000, // 24 hours offline cache
  onCacheHit = null,
  onCacheMiss = null,
  onOfflineMode = null,
  validateCache = null,
  maxCacheSize = 100,
  enableCompression = false
}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isFromCache, setIsFromCache] = useState(false);
  const [isOffline, setIsOffline] = useState(!navigator.onLine);
  const [cacheInfo, setCacheInfo] = useState(null);

  const cacheRef = useRef(new Map());
  const persistentStorageRef = useRef(null);
  const mountedRef = useRef(true);

  // Initialize persistent storage
  useEffect(() => {
    if (enablePersistence && typeof Storage !== 'undefined') {
      try {
        persistentStorageRef.current = localStorage;
      } catch (e) {
        console.warn('Persistent storage not available:', e);
      }
    }
  }, [enablePersistence]);

  // Handle online/offline events
  useEffect(() => {
    const handleOnline = () => {
      setIsOffline(false);
    };

    const handleOffline = () => {
      setIsOffline(true);
      if (onOfflineMode) {
        onOfflineMode(true);
      }
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [onOfflineMode]);

  // Generate cache key
  const getCacheKey = useCallback((baseKey) => {
    return `enterprise_cache_${baseKey}`;
  }, []);

  // Compress data if enabled
  const compressData = useCallback((data) => {
    if (!enableCompression) return data;
    
    try {
      return JSON.stringify(data);
    } catch (e) {
      return data;
    }
  }, [enableCompression]);

  // Decompress data if enabled
  const decompressData = useCallback((data) => {
    if (!enableCompression) return data;
    
    try {
      return typeof data === 'string' ? JSON.parse(data) : data;
    } catch (e) {
      return data;
    }
  }, [enableCompression]);

  // Get cache entry
  const getCacheEntry = useCallback((cacheKey) => {
    // Check memory cache first
    const memoryEntry = cacheRef.current.get(cacheKey);
    if (memoryEntry) {
      return memoryEntry;
    }

    // Check persistent storage
    if (persistentStorageRef.current) {
      try {
        const stored = persistentStorageRef.current.getItem(getCacheKey(cacheKey));
        if (stored) {
          const parsed = JSON.parse(stored);
          // Restore to memory cache
          cacheRef.current.set(cacheKey, parsed);
          return parsed;
        }
      } catch (e) {
        console.warn('Failed to read from persistent cache:', e);
      }
    }

    return null;
  }, [getCacheKey]);

  // Set cache entry
  const setCacheEntry = useCallback((cacheKey, data, metadata = {}) => {
    const entry = {
      data: compressData(data),
      timestamp: Date.now(),
      key: cacheKey,
      metadata: {
        size: JSON.stringify(data).length,
        ...metadata
      }
    };

    // Store in memory cache
    cacheRef.current.set(cacheKey, entry);

    // Store in persistent storage
    if (persistentStorageRef.current) {
      try {
        persistentStorageRef.current.setItem(getCacheKey(cacheKey), JSON.stringify(entry));
      } catch (e) {
        console.warn('Failed to write to persistent cache:', e);
        // If storage is full, try to clear old entries
        clearOldEntries();
      }
    }

    // Manage cache size
    if (cacheRef.current.size > maxCacheSize) {
      clearOldEntries();
    }

    setCacheInfo({
      key: cacheKey,
      timestamp: entry.timestamp,
      size: entry.metadata.size,
      isCompressed: enableCompression
    });
  }, [compressData, getCacheKey, maxCacheSize, enableCompression]);

  // Clear old cache entries
  const clearOldEntries = useCallback(() => {
    const now = Date.now();
    const entries = Array.from(cacheRef.current.entries());
    
    // Sort by timestamp (oldest first)
    entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
    
    // Remove oldest entries until we're under the limit
    const toRemove = Math.max(0, entries.length - maxCacheSize + 10); // Remove extra for buffer
    
    for (let i = 0; i < toRemove; i++) {
      const [key] = entries[i];
      cacheRef.current.delete(key);
      
      // Also remove from persistent storage
      if (persistentStorageRef.current) {
        try {
          persistentStorageRef.current.removeItem(getCacheKey(key));
        } catch (e) {
          console.warn('Failed to remove from persistent cache:', e);
        }
      }
    }
  }, [maxCacheSize, getCacheKey]);

  // Check if cache entry is valid
  const isCacheValid = useCallback((entry, isOfflineMode = false) => {
    if (!entry) return false;

    const now = Date.now();
    const age = now - entry.timestamp;
    const timeout = isOfflineMode ? offlineTimeout : cacheTimeout;

    // Check if expired
    if (age > timeout) return false;

    // Run custom validation if provided
    if (validateCache) {
      try {
        return validateCache(decompressData(entry.data), entry.metadata, age);
      } catch (e) {
        console.warn('Cache validation failed:', e);
        return false;
      }
    }

    return true;
  }, [cacheTimeout, offlineTimeout, validateCache, decompressData]);

  // Fetch data with caching
  const fetchData = useCallback(async (forceRefresh = false) => {
    if (!key || !fetchFunction) return;

    setLoading(true);
    setError(null);

    try {
      // Check cache first (unless force refresh)
      if (!forceRefresh) {
        const cachedEntry = getCacheEntry(key);
        
        if (cachedEntry && isCacheValid(cachedEntry, isOffline)) {
          const cachedData = decompressData(cachedEntry.data);
          setData(cachedData);
          setIsFromCache(true);
          setLoading(false);
          
          if (onCacheHit) {
            onCacheHit(cachedData, cachedEntry.metadata);
          }
          
          return cachedData;
        }
      }

      // If offline and no valid cache, return error
      if (isOffline && !forceRefresh) {
        const offlineError = new Error('Data not available offline');
        setError(offlineError);
        setLoading(false);
        return null;
      }

      // Fetch fresh data
      if (onCacheMiss) {
        onCacheMiss(key);
      }

      const freshData = await fetchFunction();
      
      if (mountedRef.current) {
        setData(freshData);
        setIsFromCache(false);
        setLoading(false);
        
        // Cache the fresh data
        setCacheEntry(key, freshData, {
          fetchedAt: Date.now(),
          online: !isOffline
        });
      }

      return freshData;

    } catch (err) {
      if (!mountedRef.current) return;

      // Try to return cached data on error if available
      const cachedEntry = getCacheEntry(key);
      if (cachedEntry && isCacheValid(cachedEntry, true)) { // Use offline timeout
        const cachedData = decompressData(cachedEntry.data);
        setData(cachedData);
        setIsFromCache(true);
        setError(null); // Clear error since we have cached data
        
        console.warn('Using cached data due to fetch error:', err);
      } else {
        setError(err);
        setData(null);
      }
      
      setLoading(false);
      return null;
    }
  }, [key, fetchFunction, getCacheEntry, isCacheValid, isOffline, decompressData, onCacheHit, onCacheMiss, setCacheEntry]);

  // Clear specific cache entry
  const clearCache = useCallback((specificKey = null) => {
    const targetKey = specificKey || key;
    
    if (targetKey) {
      cacheRef.current.delete(targetKey);
      
      if (persistentStorageRef.current) {
        try {
          persistentStorageRef.current.removeItem(getCacheKey(targetKey));
        } catch (e) {
          console.warn('Failed to clear persistent cache:', e);
        }
      }
    }
  }, [key, getCacheKey]);

  // Clear all cache
  const clearAllCache = useCallback(() => {
    cacheRef.current.clear();
    
    if (persistentStorageRef.current) {
      try {
        const keys = Object.keys(persistentStorageRef.current);
        keys.forEach(storageKey => {
          if (storageKey.startsWith('enterprise_cache_')) {
            persistentStorageRef.current.removeItem(storageKey);
          }
        });
      } catch (e) {
        console.warn('Failed to clear all persistent cache:', e);
      }
    }
    
    setCacheInfo(null);
  }, []);

  // Get cache statistics
  const getCacheStats = useCallback(() => {
    const memorySize = cacheRef.current.size;
    let persistentSize = 0;
    let totalSize = 0;

    if (persistentStorageRef.current) {
      try {
        const keys = Object.keys(persistentStorageRef.current);
        keys.forEach(storageKey => {
          if (storageKey.startsWith('enterprise_cache_')) {
            const item = persistentStorageRef.current.getItem(storageKey);
            if (item) {
              persistentSize++;
              totalSize += item.length;
            }
          }
        });
      } catch (e) {
        console.warn('Failed to calculate cache stats:', e);
      }
    }

    return {
      memoryEntries: memorySize,
      persistentEntries: persistentSize,
      totalSize,
      maxSize: maxCacheSize,
      compressionEnabled: enableCompression,
      persistenceEnabled: enablePersistence,
      offlineModeEnabled: enableOfflineMode
    };
  }, [maxCacheSize, enableCompression, enablePersistence, enableOfflineMode]);

  // Initial data fetch
  useEffect(() => {
    if (key && fetchFunction) {
      fetchData();
    }

    return () => {
      mountedRef.current = false;
    };
  }, [key, fetchFunction]); // Only depend on key and fetchFunction

  return {
    // Data state
    data,
    loading,
    error,
    isFromCache,
    isOffline,
    cacheInfo,
    
    // Actions
    refetch: () => fetchData(true),
    refresh: () => fetchData(false),
    clearCache,
    clearAllCache,
    
    // Cache management
    getCacheStats,
    isCacheValid: (customKey) => {
      const entry = getCacheEntry(customKey || key);
      return isCacheValid(entry, isOffline);
    },
    
    // Status helpers
    getCacheAge: () => {
      const entry = getCacheEntry(key);
      return entry ? Date.now() - entry.timestamp : null;
    },
    
    getStatus: () => ({
      hasData: !!data,
      isFromCache,
      isOffline,
      cacheAge: (() => {
        const entry = getCacheEntry(key);
        return entry ? Date.now() - entry.timestamp : null;
      })(),
      cacheValid: (() => {
        const entry = getCacheEntry(key);
        return isCacheValid(entry, isOffline);
      })()
    })
  };
};

export default useDataCache;
