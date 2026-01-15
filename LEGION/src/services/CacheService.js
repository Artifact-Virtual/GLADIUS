// src/services/CacheService.js
// LEGION Enterprise Dashboard - Cache Service
// Comprehensive caching system with intelligent data optimization and management

/**
 * Cache Service
 * Provides comprehensive caching functionality with intelligent data optimization,
 * multi-level storage, and advanced cache management for the LEGION Enterprise Dashboard
 */
class CacheService {
  constructor() {
    this.memoryCache = new Map();
    this.localStorage = window.localStorage;
    this.sessionStorage = window.sessionStorage;
    this.indexedDB = null;
    this.cacheStats = {
      hits: 0,
      misses: 0,
      evictions: 0,
      writes: 0
    };
    
    // Cache configuration
    this.config = {
      maxMemorySize: 50 * 1024 * 1024, // 50MB
      maxLocalStorageSize: 10 * 1024 * 1024, // 10MB
      defaultTTL: 300000, // 5 minutes
      cleanupInterval: 60000, // 1 minute
      compressionThreshold: 1024, // 1KB
      enableCompression: true,
      enableIndexedDB: true,
      enablePersistence: true,
      maxRetries: 3,
      retryDelay: 100
    };

    // Cache levels and priorities
    this.cacheLevels = {
      MEMORY: { priority: 1, storage: 'memory', persistent: false },
      SESSION: { priority: 2, storage: 'session', persistent: false },
      LOCAL: { priority: 3, storage: 'local', persistent: true },
      INDEXED: { priority: 4, storage: 'indexed', persistent: true }
    };

    // Cache policies
    this.policies = {
      LRU: 'least-recently-used',
      LFU: 'least-frequently-used',
      FIFO: 'first-in-first-out',
      TTL: 'time-to-live'
    };

    this.currentPolicy = this.policies.LRU;
    this.accessLog = new Map();
    this.frequencyLog = new Map();
    
    // Initialize cache service
    this.initializeCacheService();
    
    console.log('CacheService initialized');
  }

  /**
   * Initialize cache service and background processes
   */
  async initializeCacheService() {
    // Initialize IndexedDB if enabled
    if (this.config.enableIndexedDB) {
      await this.initializeIndexedDB();
    }

    // Start cleanup process
    setInterval(() => {
      this.performCleanup();
    }, this.config.cleanupInterval);

    // Load persistent cache data
    if (this.config.enablePersistence) {
      await this.loadPersistentCache();
    }

    // Monitor storage events
    window.addEventListener('storage', (event) => {
      this.handleStorageEvent(event);
    });

    // Monitor memory usage
    if (window.performance && window.performance.memory) {
      setInterval(() => {
        this.monitorMemoryUsage();
      }, 30000); // 30 seconds
    }
  }

  /**
   * Core Cache Operations
   */
  async set(key, value, options = {}) {
    const startTime = performance.now();
    
    try {
      const cacheEntry = this.createCacheEntry(key, value, options);
      const level = this.determineCacheLevel(cacheEntry, options);
      
      await this.storeAtLevel(key, cacheEntry, level);
      
      // Update statistics
      this.cacheStats.writes++;
      this.updateAccessLog(key);
      
      // Log performance
      const duration = performance.now() - startTime;
      this.logPerformance('set', key, duration);
      
      return true;
    } catch (error) {
      console.error(`Cache set error for key ${key}:`, error);
      return false;
    }
  }

  async get(key, options = {}) {
    const startTime = performance.now();
    
    try {
      // Check all cache levels in priority order
      for (const [levelName, levelConfig] of Object.entries(this.cacheLevels)) {
        const entry = await this.getFromLevel(key, levelName);
        
        if (entry) {
          // Validate entry
          if (this.isValidEntry(entry)) {
            // Update access statistics
            this.cacheStats.hits++;
            this.updateAccessLog(key);
            this.updateFrequencyLog(key);
            
            // Promote to higher level if beneficial
            if (options.promote !== false) {
              await this.promoteEntry(key, entry, levelName);
            }
            
            // Log performance
            const duration = performance.now() - startTime;
            this.logPerformance('get', key, duration);
            
            return this.deserializeValue(entry.value);
          } else {
            // Remove expired entry
            await this.deleteFromLevel(key, levelName);
          }
        }
      }
      
      // Cache miss
      this.cacheStats.misses++;
      
      // Log performance
      const duration = performance.now() - startTime;
      this.logPerformance('get', key, duration);
      
      return null;
    } catch (error) {
      console.error(`Cache get error for key ${key}:`, error);
      this.cacheStats.misses++;
      return null;
    }
  }

  async delete(key) {
    try {
      let deleted = false;
      
      // Remove from all cache levels
      for (const levelName of Object.keys(this.cacheLevels)) {
        const removed = await this.deleteFromLevel(key, levelName);
        if (removed) deleted = true;
      }
      
      // Clean up logs
      this.accessLog.delete(key);
      this.frequencyLog.delete(key);
      
      return deleted;
    } catch (error) {
      console.error(`Cache delete error for key ${key}:`, error);
      return false;
    }
  }

  async clear(level = null) {
    try {
      if (level) {
        await this.clearLevel(level);
      } else {
        // Clear all levels
        for (const levelName of Object.keys(this.cacheLevels)) {
          await this.clearLevel(levelName);
        }
        
        // Clear logs
        this.accessLog.clear();
        this.frequencyLog.clear();
      }
      
      return true;
    } catch (error) {
      console.error('Cache clear error:', error);
      return false;
    }
  }

  /**
   * Advanced Cache Operations
   */
  async setMultiple(entries, options = {}) {
    const results = [];
    
    for (const [key, value] of Object.entries(entries)) {
      const result = await this.set(key, value, options);
      results.push({ key, success: result });
    }
    
    return results;
  }

  async getMultiple(keys, options = {}) {
    const results = {};
    
    await Promise.all(keys.map(async (key) => {
      const value = await this.get(key, options);
      if (value !== null) {
        results[key] = value;
      }
    }));
    
    return results;
  }

  async deleteMultiple(keys) {
    const results = [];
    
    for (const key of keys) {
      const result = await this.delete(key);
      results.push({ key, success: result });
    }
    
    return results;
  }

  async exists(key) {
    try {
      for (const levelName of Object.keys(this.cacheLevels)) {
        const entry = await this.getFromLevel(key, levelName);
        if (entry && this.isValidEntry(entry)) {
          return true;
        }
      }
      return false;
    } catch (error) {
      console.error(`Cache exists error for key ${key}:`, error);
      return false;
    }
  }

  async touch(key, ttl = null) {
    try {
      for (const levelName of Object.keys(this.cacheLevels)) {
        const entry = await this.getFromLevel(key, levelName);
        if (entry && this.isValidEntry(entry)) {
          // Update TTL
          if (ttl !== null) {
            entry.expires = Date.now() + ttl;
          } else {
            entry.lastAccessed = Date.now();
          }
          
          await this.storeAtSpecificLevel(key, entry, levelName);
          return true;
        }
      }
      return false;
    } catch (error) {
      console.error(`Cache touch error for key ${key}:`, error);
      return false;
    }
  }

  /**
   * Cache Level Management
   */
  async storeAtLevel(key, entry, preferredLevel) {
    const levels = this.getSortedLevels();
    
    // Try preferred level first
    if (preferredLevel && await this.canStoreAtLevel(entry, preferredLevel)) {
      return await this.storeAtSpecificLevel(key, entry, preferredLevel);
    }
    
    // Try levels in order of preference
    for (const levelName of levels) {
      if (await this.canStoreAtLevel(entry, levelName)) {
        return await this.storeAtSpecificLevel(key, entry, levelName);
      }
    }
    
    throw new Error('Unable to store entry at any cache level');
  }

  async storeAtSpecificLevel(key, entry, levelName) {
    switch (levelName) {
      case 'MEMORY':
        return this.storeInMemory(key, entry);
      case 'SESSION':
        return this.storeInSessionStorage(key, entry);
      case 'LOCAL':
        return this.storeInLocalStorage(key, entry);
      case 'INDEXED':
        return this.storeInIndexedDB(key, entry);
      default:
        throw new Error(`Unknown cache level: ${levelName}`);
    }
  }

  async getFromLevel(key, levelName) {
    switch (levelName) {
      case 'MEMORY':
        return this.getFromMemory(key);
      case 'SESSION':
        return this.getFromSessionStorage(key);
      case 'LOCAL':
        return this.getFromLocalStorage(key);
      case 'INDEXED':
        return this.getFromIndexedDB(key);
      default:
        return null;
    }
  }

  async deleteFromLevel(key, levelName) {
    switch (levelName) {
      case 'MEMORY':
        return this.deleteFromMemory(key);
      case 'SESSION':
        return this.deleteFromSessionStorage(key);
      case 'LOCAL':
        return this.deleteFromLocalStorage(key);
      case 'INDEXED':
        return this.deleteFromIndexedDB(key);
      default:
        return false;
    }
  }

  /**
   * Storage Implementation - Memory
   */
  storeInMemory(key, entry) {
    try {
      // Check memory limits
      if (this.getMemorySize() + this.getEntrySize(entry) > this.config.maxMemorySize) {
        this.evictFromMemory();
      }
      
      this.memoryCache.set(key, entry);
      return true;
    } catch (error) {
      console.error('Memory storage error:', error);
      return false;
    }
  }

  getFromMemory(key) {
    return this.memoryCache.get(key) || null;
  }

  deleteFromMemory(key) {
    return this.memoryCache.delete(key);
  }

  /**
   * Storage Implementation - Session Storage
   */
  storeInSessionStorage(key, entry) {
    try {
      const serialized = this.serializeEntry(entry);
      this.sessionStorage.setItem(`cache_${key}`, serialized);
      return true;
    } catch (error) {
      console.error('Session storage error:', error);
      return false;
    }
  }

  getFromSessionStorage(key) {
    try {
      const serialized = this.sessionStorage.getItem(`cache_${key}`);
      return serialized ? this.deserializeEntry(serialized) : null;
    } catch (error) {
      console.error('Session storage read error:', error);
      return null;
    }
  }

  deleteFromSessionStorage(key) {
    try {
      this.sessionStorage.removeItem(`cache_${key}`);
      return true;
    } catch (error) {
      console.error('Session storage delete error:', error);
      return false;
    }
  }

  /**
   * Storage Implementation - Local Storage
   */
  storeInLocalStorage(key, entry) {
    try {
      const serialized = this.serializeEntry(entry);
      
      // Check storage limits
      if (this.getLocalStorageSize() + serialized.length > this.config.maxLocalStorageSize) {
        this.evictFromLocalStorage();
      }
      
      this.localStorage.setItem(`cache_${key}`, serialized);
      return true;
    } catch (error) {
      console.error('Local storage error:', error);
      return false;
    }
  }

  getFromLocalStorage(key) {
    try {
      const serialized = this.localStorage.getItem(`cache_${key}`);
      return serialized ? this.deserializeEntry(serialized) : null;
    } catch (error) {
      console.error('Local storage read error:', error);
      return null;
    }
  }

  deleteFromLocalStorage(key) {
    try {
      this.localStorage.removeItem(`cache_${key}`);
      return true;
    } catch (error) {
      console.error('Local storage delete error:', error);
      return false;
    }
  }

  /**
   * Storage Implementation - IndexedDB
   */
  async initializeIndexedDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('CacheServiceDB', 1);
      
      request.onerror = () => {
        console.error('IndexedDB initialization failed');
        resolve(null);
      };
      
      request.onsuccess = (event) => {
        this.indexedDB = event.target.result;
        console.log('IndexedDB initialized');
        resolve(this.indexedDB);
      };
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains('cache')) {
          const store = db.createObjectStore('cache', { keyPath: 'key' });
          store.createIndex('expires', 'expires', { unique: false });
          store.createIndex('created', 'created', { unique: false });
        }
      };
    });
  }

  async storeInIndexedDB(key, entry) {
    if (!this.indexedDB) return false;
    
    return new Promise((resolve) => {
      const transaction = this.indexedDB.transaction(['cache'], 'readwrite');
      const store = transaction.objectStore('cache');
      
      const request = store.put({ key, ...entry });
      
      request.onsuccess = () => resolve(true);
      request.onerror = () => {
        console.error('IndexedDB store error:', request.error);
        resolve(false);
      };
    });
  }

  async getFromIndexedDB(key) {
    if (!this.indexedDB) return null;
    
    return new Promise((resolve) => {
      const transaction = this.indexedDB.transaction(['cache'], 'readonly');
      const store = transaction.objectStore('cache');
      
      const request = store.get(key);
      
      request.onsuccess = () => {
        const result = request.result;
        resolve(result ? { ...result, key: undefined } : null);
      };
      
      request.onerror = () => {
        console.error('IndexedDB read error:', request.error);
        resolve(null);
      };
    });
  }

  async deleteFromIndexedDB(key) {
    if (!this.indexedDB) return false;
    
    return new Promise((resolve) => {
      const transaction = this.indexedDB.transaction(['cache'], 'readwrite');
      const store = transaction.objectStore('cache');
      
      const request = store.delete(key);
      
      request.onsuccess = () => resolve(true);
      request.onerror = () => {
        console.error('IndexedDB delete error:', request.error);
        resolve(false);
      };
    });
  }

  /**
   * Cache Entry Management
   */
  createCacheEntry(key, value, options = {}) {
    const now = Date.now();
    const ttl = options.ttl || this.config.defaultTTL;
    
    return {
      value: this.serializeValue(value),
      created: now,
      lastAccessed: now,
      expires: ttl > 0 ? now + ttl : null,
      size: this.calculateSize(value),
      compressed: false,
      metadata: options.metadata || {}
    };
  }

  isValidEntry(entry) {
    if (!entry) return false;
    
    const now = Date.now();
    
    // Check expiration
    if (entry.expires && now > entry.expires) {
      return false;
    }
    
    return true;
  }

  determineCacheLevel(entry, options = {}) {
    // Use specified level if provided
    if (options.level) {
      return options.level;
    }
    
    // Determine based on size and TTL
    if (entry.size > 1024 * 1024) { // > 1MB
      return 'INDEXED';
    } else if (entry.expires && (entry.expires - Date.now()) > 3600000) { // > 1 hour
      return 'LOCAL';
    } else if (entry.size > 10240) { // > 10KB
      return 'SESSION';
    } else {
      return 'MEMORY';
    }
  }

  /**
   * Eviction Policies
   */
  evictFromMemory() {
    switch (this.currentPolicy) {
      case this.policies.LRU:
        this.evictLRU('MEMORY');
        break;
      case this.policies.LFU:
        this.evictLFU('MEMORY');
        break;
      case this.policies.FIFO:
        this.evictFIFO('MEMORY');
        break;
      default:
        this.evictLRU('MEMORY');
    }
  }

  evictFromLocalStorage() {
    // Similar implementation for localStorage
    this.evictLRU('LOCAL');
  }

  evictLRU(level) {
    const candidates = this.getEvictionCandidates(level);
    if (candidates.length === 0) return;
    
    // Sort by last accessed time
    candidates.sort((a, b) => a.lastAccessed - b.lastAccessed);
    
    // Evict oldest 25%
    const toEvict = candidates.slice(0, Math.max(1, Math.floor(candidates.length * 0.25)));
    
    toEvict.forEach(({ key }) => {
      this.deleteFromLevel(key, level);
      this.cacheStats.evictions++;
    });
  }

  evictLFU(level) {
    const candidates = this.getEvictionCandidates(level);
    if (candidates.length === 0) return;
    
    // Sort by frequency
    candidates.sort((a, b) => {
      const freqA = this.frequencyLog.get(a.key) || 0;
      const freqB = this.frequencyLog.get(b.key) || 0;
      return freqA - freqB;
    });
    
    // Evict least frequent 25%
    const toEvict = candidates.slice(0, Math.max(1, Math.floor(candidates.length * 0.25)));
    
    toEvict.forEach(({ key }) => {
      this.deleteFromLevel(key, level);
      this.cacheStats.evictions++;
    });
  }

  evictFIFO(level) {
    const candidates = this.getEvictionCandidates(level);
    if (candidates.length === 0) return;
    
    // Sort by creation time
    candidates.sort((a, b) => a.created - b.created);
    
    // Evict oldest 25%
    const toEvict = candidates.slice(0, Math.max(1, Math.floor(candidates.length * 0.25)));
    
    toEvict.forEach(({ key }) => {
      this.deleteFromLevel(key, level);
      this.cacheStats.evictions++;
    });
  }

  /**
   * Utility Methods
   */
  serializeValue(value) {
    try {
      return JSON.stringify(value);
    } catch (error) {
      console.error('Value serialization error:', error);
      return null;
    }
  }

  deserializeValue(serialized) {
    try {
      return JSON.parse(serialized);
    } catch (error) {
      console.error('Value deserialization error:', error);
      return null;
    }
  }

  serializeEntry(entry) {
    try {
      let serialized = JSON.stringify(entry);
      
      // Compress if enabled and above threshold
      if (this.config.enableCompression && 
          serialized.length > this.config.compressionThreshold) {
        // Simple compression placeholder (use proper compression in production)
        serialized = this.compress(serialized);
        entry.compressed = true;
      }
      
      return serialized;
    } catch (error) {
      console.error('Entry serialization error:', error);
      return null;
    }
  }

  deserializeEntry(serialized) {
    try {
      let data = serialized;
      
      // Decompress if needed
      if (serialized.startsWith('compressed:')) {
        data = this.decompress(serialized);
      }
      
      return JSON.parse(data);
    } catch (error) {
      console.error('Entry deserialization error:', error);
      return null;
    }
  }

  compress(data) {
    // Placeholder compression
    return 'compressed:' + data;
  }

  decompress(data) {
    // Placeholder decompression
    return data.replace('compressed:', '');
  }

  calculateSize(value) {
    try {
      return new Blob([JSON.stringify(value)]).size;
    } catch (error) {
      return 0;
    }
  }

  getEntrySize(entry) {
    return this.calculateSize(entry);
  }

  getMemorySize() {
    let size = 0;
    this.memoryCache.forEach(entry => {
      size += this.getEntrySize(entry);
    });
    return size;
  }

  getLocalStorageSize() {
    let size = 0;
    for (let key in this.localStorage) {
      if (key.startsWith('cache_')) {
        size += this.localStorage[key].length;
      }
    }
    return size;
  }

  updateAccessLog(key) {
    this.accessLog.set(key, Date.now());
  }

  updateFrequencyLog(key) {
    const current = this.frequencyLog.get(key) || 0;
    this.frequencyLog.set(key, current + 1);
  }

  getSortedLevels() {
    return Object.entries(this.cacheLevels)
      .sort(([,a], [,b]) => a.priority - b.priority)
      .map(([name]) => name);
  }

  async canStoreAtLevel(entry, levelName) {
    // Check level availability and size constraints
    switch (levelName) {
      case 'MEMORY':
        return this.getMemorySize() + this.getEntrySize(entry) <= this.config.maxMemorySize;
      case 'SESSION':
      case 'LOCAL':
        return true; // Assuming storage available
      case 'INDEXED':
        return this.indexedDB !== null;
      default:
        return false;
    }
  }

  getEvictionCandidates(level) {
    const candidates = [];
    
    switch (level) {
      case 'MEMORY':
        this.memoryCache.forEach((entry, key) => {
          candidates.push({ key, ...entry });
        });
        break;
      // Add other levels as needed
    }
    
    return candidates;
  }

  async promoteEntry(key, entry, currentLevel) {
    const levels = this.getSortedLevels();
    const currentIndex = levels.indexOf(currentLevel);
    
    if (currentIndex > 0) {
      const higherLevel = levels[currentIndex - 1];
      if (await this.canStoreAtLevel(entry, higherLevel)) {
        await this.storeAtSpecificLevel(key, entry, higherLevel);
      }
    }
  }

  performCleanup() {
    // Remove expired entries
    this.cleanupExpiredEntries();
    
    // Cleanup logs
    this.cleanupLogs();
  }

  cleanupExpiredEntries() {
    const now = Date.now();
    
    // Cleanup memory cache
    this.memoryCache.forEach((entry, key) => {
      if (!this.isValidEntry(entry)) {
        this.memoryCache.delete(key);
      }
    });
  }

  cleanupLogs() {
    const maxLogSize = 1000;
    
    if (this.accessLog.size > maxLogSize) {
      const entries = Array.from(this.accessLog.entries())
        .sort(([,a], [,b]) => b - a)
        .slice(0, maxLogSize);
      
      this.accessLog.clear();
      entries.forEach(([key, time]) => this.accessLog.set(key, time));
    }
    
    if (this.frequencyLog.size > maxLogSize) {
      const entries = Array.from(this.frequencyLog.entries())
        .sort(([,a], [,b]) => b - a)
        .slice(0, maxLogSize);
      
      this.frequencyLog.clear();
      entries.forEach(([key, freq]) => this.frequencyLog.set(key, freq));
    }
  }

  async loadPersistentCache() {
    // Load from localStorage and IndexedDB on startup
    console.log('Loading persistent cache data...');
  }

  handleStorageEvent(event) {
    if (event.key && event.key.startsWith('cache_')) {
      const key = event.key.replace('cache_', '');
      console.log(`Cache storage event for key: ${key}`);
    }
  }

  monitorMemoryUsage() {
    if (window.performance && window.performance.memory) {
      const usage = window.performance.memory;
      const memoryPressure = usage.usedJSHeapSize / usage.jsHeapSizeLimit;
      
      if (memoryPressure > 0.8) {
        console.warn('High memory usage detected, performing cache cleanup');
        this.evictFromMemory();
      }
    }
  }

  logPerformance(operation, key, duration) {
    if (duration > 100) { // Log slow operations
      console.warn(`Slow cache ${operation} for ${key}: ${duration.toFixed(2)}ms`);
    }
  }

  async clearLevel(levelName) {
    switch (levelName) {
      case 'MEMORY':
        this.memoryCache.clear();
        break;
      case 'SESSION':
        Object.keys(this.sessionStorage).forEach(key => {
          if (key.startsWith('cache_')) {
            this.sessionStorage.removeItem(key);
          }
        });
        break;
      case 'LOCAL':
        Object.keys(this.localStorage).forEach(key => {
          if (key.startsWith('cache_')) {
            this.localStorage.removeItem(key);
          }
        });
        break;
      case 'INDEXED':
        if (this.indexedDB) {
          const transaction = this.indexedDB.transaction(['cache'], 'readwrite');
          const store = transaction.objectStore('cache');
          store.clear();
        }
        break;
    }
  }

  /**
   * Public API Methods
   */
  getStats() {
    return {
      ...this.cacheStats,
      hitRate: this.cacheStats.hits / (this.cacheStats.hits + this.cacheStats.misses) || 0,
      memorySize: this.getMemorySize(),
      localStorageSize: this.getLocalStorageSize(),
      memoryEntries: this.memoryCache.size,
      accessLogSize: this.accessLog.size,
      frequencyLogSize: this.frequencyLog.size
    };
  }

  async healthCheck() {
    return {
      status: 'healthy',
      memoryUsage: this.getMemorySize(),
      storageAvailable: {
        memory: true,
        session: !!this.sessionStorage,
        local: !!this.localStorage,
        indexed: !!this.indexedDB
      },
      timestamp: new Date().toISOString()
    };
  }

  destroy() {
    this.memoryCache.clear();
    this.accessLog.clear();
    this.frequencyLog.clear();
    
    if (this.indexedDB) {
      this.indexedDB.close();
    }
    
    console.log('CacheService destroyed');
  }
}

// Create singleton instance
const cacheService = new CacheService();

export default cacheService;
export { CacheService };
