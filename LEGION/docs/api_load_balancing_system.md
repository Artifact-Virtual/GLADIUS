# API Load Balancing & Connection Management System

## 🏗️ System Architecture Overview

**Purpose**: Intelligent load balancing, connection management, and failover system for 8+ external APIs  
**Goal**: Maximize reliability, minimize costs, optimize performance across all API integrations  
**Design**: Circuit breaker pattern, request queuing, intelligent failover, connection pooling

## 🔄 Connection Management Architecture

### 1. Connection Pool Manager (`src/services/ConnectionPoolManager.js`)

```javascript
class ConnectionPoolManager {
  constructor() {
    this.pools = new Map(); // API name -> connection pool
    this.connectionLimits = {
      concurrent: 10,      // Max concurrent connections per API
      keepAlive: 30000,    // Keep-alive timeout (30s)
      timeout: 15000,      // Request timeout (15s)
      retryAttempts: 3     // Max retry attempts
    };
    this.activeConnections = new Map();
    this.metrics = new ConnectionMetrics();
  }

  async createPool(apiName, config) {
    const pool = new ConnectionPool({
      baseURL: config.baseUrl,
      maxConnections: this.connectionLimits.concurrent,
      keepAlive: this.connectionLimits.keepAlive,
      timeout: this.connectionLimits.timeout,
      headers: this.buildHeaders(config),
      interceptors: this.setupInterceptors(apiName)
    });
    
    this.pools.set(apiName, pool);
    return pool;
  }

  async acquireConnection(apiName) {
    const pool = this.pools.get(apiName);
    if (!pool) throw new Error(`No connection pool for ${apiName}`);
    
    return await pool.acquire();
  }

  async releaseConnection(apiName, connection) {
    const pool = this.pools.get(apiName);
    if (pool) await pool.release(connection);
  }

  getPoolMetrics(apiName) {
    return {
      activeConnections: this.activeConnections.get(apiName) || 0,
      queuedRequests: this.getQueuedRequests(apiName),
      totalRequests: this.metrics.getTotalRequests(apiName),
      averageResponseTime: this.metrics.getAverageResponseTime(apiName)
    };
  }
}
```

### 2. Load Balancer Engine (`src/services/LoadBalancerEngine.js`)

```javascript
class LoadBalancerEngine {
  constructor() {
    this.strategies = {
      roundRobin: new RoundRobinStrategy(),
      leastConnections: new LeastConnectionsStrategy(),
      weightedResponse: new WeightedResponseStrategy(),
      healthBased: new HealthBasedStrategy()
    };
    this.currentStrategy = 'healthBased';
    this.serverGroups = new Map();
    this.healthChecker = new HealthChecker();
  }

  async selectServer(apiName, alternatives = []) {
    const serverGroup = this.getServerGroup(apiName, alternatives);
    const strategy = this.strategies[this.currentStrategy];
    
    // Filter healthy servers
    const healthyServers = await this.filterHealthyServers(serverGroup);
    if (healthyServers.length === 0) {
      throw new Error(`No healthy servers available for ${apiName}`);
    }

    // Apply load balancing strategy
    const selectedServer = await strategy.select(healthyServers);
    await this.recordSelection(apiName, selectedServer);
    
    return selectedServer;
  }

  async registerAlternativeProvider(apiName, provider) {
    // Register backup/alternative API providers
    if (!this.serverGroups.has(apiName)) {
      this.serverGroups.set(apiName, []);
    }
    
    this.serverGroups.get(apiName).push({
      ...provider,
      weight: provider.tier === 'tier1' ? 100 : 
              provider.tier === 'tier2' ? 75 : 50,
      priority: provider.tier === 'tier1' ? 1 : 
                provider.tier === 'tier2' ? 2 : 3
    });
  }
}
```

### 3. Circuit Breaker System (`src/services/CircuitBreakerSystem.js`)

```javascript
class CircuitBreakerSystem {
  constructor() {
    this.circuitBreakers = new Map();
    this.defaultConfig = {
      failureThreshold: 5,      // Failures before opening circuit
      successThreshold: 3,      // Successes needed to close circuit
      timeout: 60000,          // Circuit breaker timeout (60s)
      monitoringPeriod: 30000  // Monitoring window (30s)
    };
  }

  createCircuitBreaker(apiName, config = {}) {
    const breakerConfig = { ...this.defaultConfig, ...config };
    const breaker = new CircuitBreaker(apiName, breakerConfig);
    
    breaker.on('open', () => this.onCircuitOpen(apiName));
    breaker.on('halfOpen', () => this.onCircuitHalfOpen(apiName));
    breaker.on('close', () => this.onCircuitClose(apiName));
    
    this.circuitBreakers.set(apiName, breaker);
    return breaker;
  }

  async executeWithBreaker(apiName, requestFunction, fallbackFunction = null) {
    const breaker = this.circuitBreakers.get(apiName);
    if (!breaker) {
      throw new Error(`No circuit breaker configured for ${apiName}`);
    }

    try {
      return await breaker.execute(requestFunction);
    } catch (error) {
      if (breaker.isOpen() && fallbackFunction) {
        console.warn(`Circuit breaker open for ${apiName}, using fallback`);
        return await fallbackFunction();
      }
      throw error;
    }
  }

  getCircuitState(apiName) {
    const breaker = this.circuitBreakers.get(apiName);
    return breaker ? {
      state: breaker.getState(),
      failures: breaker.getFailureCount(),
      successes: breaker.getSuccessCount(),
      lastFailure: breaker.getLastFailureTime(),
      nextAttempt: breaker.getNextAttemptTime()
    } : null;
  }
}
```

## ⚖️ Load Balancing Strategies

### 1. Health-Based Strategy (Primary)

```javascript
class HealthBasedStrategy {
  async select(servers) {
    // Score servers based on health metrics
    const scoredServers = await Promise.all(
      servers.map(async server => {
        const health = await this.calculateHealthScore(server);
        return { server, score: health };
      })
    );

    // Sort by health score (descending)
    scoredServers.sort((a, b) => b.score - a.score);
    
    // Use weighted random selection from top 50%
    const topServers = scoredServers.slice(0, Math.ceil(scoredServers.length / 2));
    return this.weightedRandomSelect(topServers);
  }

  async calculateHealthScore(server) {
    const metrics = await server.getMetrics();
    const weights = {
      uptime: 0.4,
      responseTime: 0.3,
      errorRate: 0.2,
      cost: 0.1
    };

    return (
      (metrics.uptime * weights.uptime) +
      ((1000 / metrics.avgResponseTime) * weights.responseTime) +
      ((1 - metrics.errorRate) * weights.errorRate) +
      (server.costEfficiency * weights.cost)
    );
  }
}
```

### 2. Least Connections Strategy

```javascript
class LeastConnectionsStrategy {
  async select(servers) {
    const connectionCounts = await Promise.all(
      servers.map(async server => ({
        server,
        connections: await server.getActiveConnections()
      }))
    );

    // Sort by connection count (ascending)
    connectionCounts.sort((a, b) => a.connections - b.connections);
    
    return connectionCounts[0].server;
  }
}
```

### 3. Weighted Response Time Strategy

```javascript
class WeightedResponseStrategy {
  async select(servers) {
    const responseTimes = await Promise.all(
      servers.map(async server => {
        const metrics = await server.getMetrics();
        return {
          server,
          weight: 1000 / (metrics.avgResponseTime || 1000) // Inverse response time
        };
      })
    );

    return this.weightedRandomSelect(responseTimes);
  }

  weightedRandomSelect(weightedItems) {
    const totalWeight = weightedItems.reduce((sum, item) => sum + item.weight, 0);
    const random = Math.random() * totalWeight;
    
    let currentWeight = 0;
    for (const item of weightedItems) {
      currentWeight += item.weight;
      if (random <= currentWeight) {
        return item.server;
      }
    }
    
    return weightedItems[0].server; // Fallback
  }
}
```

## 🔄 Request Queue Management

### Request Queue System (`src/services/RequestQueueSystem.js`)

```javascript
class RequestQueueSystem {
  constructor() {
    this.queues = new Map(); // API name -> priority queue
    this.processors = new Map(); // API name -> queue processor
    this.queueConfig = {
      maxSize: 1000,
      priorities: ['critical', 'high', 'normal', 'low'],
      processInterval: 100, // Process queue every 100ms
      batchSize: 5 // Process up to 5 requests per batch
    };
  }

  async enqueueRequest(apiName, request, priority = 'normal') {
    const queue = this.getOrCreateQueue(apiName);
    
    if (queue.size >= this.queueConfig.maxSize) {
      throw new Error(`Request queue full for ${apiName}`);
    }

    const queueItem = {
      id: this.generateRequestId(),
      request,
      priority,
      timestamp: Date.now(),
      retryCount: 0,
      resolve: null,
      reject: null
    };

    return new Promise((resolve, reject) => {
      queueItem.resolve = resolve;
      queueItem.reject = reject;
      queue.enqueue(queueItem, priority);
    });
  }

  async processQueue(apiName) {
    const queue = this.queues.get(apiName);
    if (!queue || queue.isEmpty()) return;

    const batch = [];
    for (let i = 0; i < this.queueConfig.batchSize && !queue.isEmpty(); i++) {
      batch.push(queue.dequeue());
    }

    await Promise.all(batch.map(item => this.executeRequest(apiName, item)));
  }

  async executeRequest(apiName, queueItem) {
    try {
      const result = await this.makeAPIRequest(apiName, queueItem.request);
      queueItem.resolve(result);
    } catch (error) {
      if (queueItem.retryCount < 3) {
        queueItem.retryCount++;
        // Re-enqueue with lower priority
        this.requeueRequest(apiName, queueItem, 'low');
      } else {
        queueItem.reject(error);
      }
    }
  }
}
```

## 🔄 Alternative Provider Management

### Provider Registry (`src/config/alternativeProviders.js`)

```javascript
const ALTERNATIVE_PROVIDERS = {
  financial: {
    stocks: [
      {
        name: 'polygon',
        tier: 'tier1',
        endpoints: ['stocks', 'forex', 'crypto'],
        cost: 'paid',
        reliability: 0.998
      },
      {
        name: 'marketstack',
        tier: 'tier3',
        endpoints: ['stocks'],
        cost: 'limited_free',
        reliability: 0.95
      },
      {
        name: 'finnhub',
        tier: 'tier2',
        endpoints: ['stocks', 'forex'],
        cost: 'freemium',
        reliability: 0.97
      }
    ],
    crypto: [
      {
        name: 'coingecko',
        tier: 'tier1',
        endpoints: ['prices', 'history', 'market_data'],
        cost: 'free',
        reliability: 0.999
      },
      {
        name: 'coinapi',
        tier: 'tier2',
        endpoints: ['prices', 'history', 'ohlcv'],
        cost: 'paid',
        reliability: 0.995
      }
    ]
  },
  news: [
    {
      name: 'newsapi',
      tier: 'tier3',
      endpoints: ['headlines', 'everything'],
      cost: 'limited_free',
      reliability: 0.92
    },
    {
      name: 'gnews',
      tier: 'tier2',
      endpoints: ['top_headlines', 'search'],
      cost: 'freemium',
      reliability: 0.94
    },
    {
      name: 'mediastack',
      tier: 'tier2',
      endpoints: ['news', 'sources'],
      cost: 'freemium',
      reliability: 0.93
    }
  ]
};
```

### Failover Logic (`src/services/FailoverManager.js`)

```javascript
class FailoverManager {
  constructor(loadBalancer, circuitBreaker) {
    this.loadBalancer = loadBalancer;
    this.circuitBreaker = circuitBreaker;
    this.failoverRules = new Map();
    this.activeFailovers = new Map();
  }

  async executeWithFailover(apiName, requestFunction, options = {}) {
    const providers = this.getAlternativeProviders(apiName);
    let lastError = null;

    // Try primary provider first
    try {
      const primaryProvider = providers.find(p => p.tier === 'tier1');
      if (primaryProvider && !this.circuitBreaker.isOpen(primaryProvider.name)) {
        return await this.circuitBreaker.executeWithBreaker(
          primaryProvider.name, 
          requestFunction
        );
      }
    } catch (error) {
      lastError = error;
      console.warn(`Primary provider failed for ${apiName}:`, error.message);
    }

    // Try alternative providers in order of reliability
    const sortedProviders = providers
      .filter(p => p.tier !== 'tier1' && !this.circuitBreaker.isOpen(p.name))
      .sort((a, b) => b.reliability - a.reliability);

    for (const provider of sortedProviders) {
      try {
        console.info(`Failing over to ${provider.name} for ${apiName}`);
        const adaptedRequest = await this.adaptRequestForProvider(
          requestFunction, 
          provider
        );
        
        const result = await this.circuitBreaker.executeWithBreaker(
          provider.name,
          adaptedRequest
        );

        this.recordSuccessfulFailover(apiName, provider.name);
        return result;
      } catch (error) {
        lastError = error;
        console.warn(`Failover provider ${provider.name} failed:`, error.message);
      }
    }

    // All providers failed, throw the last error
    throw lastError || new Error(`All providers failed for ${apiName}`);
  }

  async adaptRequestForProvider(requestFunction, provider) {
    // Adapt request format/parameters for different providers
    return async () => {
      // Provider-specific request transformation logic
      const providerAdapter = this.getProviderAdapter(provider.name);
      return await providerAdapter.execute(requestFunction);
    };
  }
}
```

## 📊 Connection Metrics & Monitoring

### Connection Metrics Collector (`src/services/ConnectionMetrics.js`)

```javascript
class ConnectionMetrics {
  constructor() {
    this.metrics = new Map();
    this.historySize = 1000; // Keep last 1000 requests per API
  }

  recordRequest(apiName, startTime, endTime, success, error = null) {
    if (!this.metrics.has(apiName)) {
      this.metrics.set(apiName, {
        requests: [],
        totalRequests: 0,
        successfulRequests: 0,
        failedRequests: 0,
        totalResponseTime: 0,
        minResponseTime: Infinity,
        maxResponseTime: 0
      });
    }

    const apiMetrics = this.metrics.get(apiName);
    const responseTime = endTime - startTime;

    // Update counters
    apiMetrics.totalRequests++;
    if (success) {
      apiMetrics.successfulRequests++;
    } else {
      apiMetrics.failedRequests++;
    }

    // Update response time metrics
    apiMetrics.totalResponseTime += responseTime;
    apiMetrics.minResponseTime = Math.min(apiMetrics.minResponseTime, responseTime);
    apiMetrics.maxResponseTime = Math.max(apiMetrics.maxResponseTime, responseTime);

    // Add to request history
    apiMetrics.requests.push({
      timestamp: endTime,
      responseTime,
      success,
      error: error?.message
    });

    // Maintain history size limit
    if (apiMetrics.requests.length > this.historySize) {
      apiMetrics.requests.shift();
    }
  }

  getMetrics(apiName, timeRange = 3600000) { // Default: last hour
    const apiMetrics = this.metrics.get(apiName);
    if (!apiMetrics) return null;

    const cutoff = Date.now() - timeRange;
    const recentRequests = apiMetrics.requests.filter(r => r.timestamp >= cutoff);

    return {
      totalRequests: apiMetrics.totalRequests,
      successRate: apiMetrics.successfulRequests / apiMetrics.totalRequests,
      errorRate: apiMetrics.failedRequests / apiMetrics.totalRequests,
      averageResponseTime: apiMetrics.totalResponseTime / apiMetrics.totalRequests,
      minResponseTime: apiMetrics.minResponseTime,
      maxResponseTime: apiMetrics.maxResponseTime,
      recentRequests: recentRequests.length,
      recentSuccessRate: recentRequests.filter(r => r.success).length / recentRequests.length,
      recentAverageResponseTime: recentRequests.reduce((sum, r) => sum + r.responseTime, 0) / recentRequests.length
    };
  }
}
```

## 🎛️ Configuration Management

### Load Balancer Configuration (`src/config/loadBalancerConfig.js`)

```javascript
const LOAD_BALANCER_CONFIG = {
  strategies: {
    default: 'healthBased',
    fallback: 'roundRobin'
  },
  
  circuitBreaker: {
    failureThreshold: 5,
    successThreshold: 3,
    timeout: 60000,
    monitoringPeriod: 30000
  },
  
  connectionPool: {
    maxConnections: 10,
    keepAliveTimeout: 30000,
    requestTimeout: 15000,
    retryAttempts: 3,
    retryDelay: 1000
  },
  
  requestQueue: {
    maxSize: 1000,
    processInterval: 100,
    batchSize: 5,
    priorities: {
      critical: 1,
      high: 2,
      normal: 3,
      low: 4
    }
  },
  
  healthCheck: {
    interval: 30000,
    timeout: 5000,
    retries: 2
  },
  
  failover: {
    maxAttempts: 3,
    backoffMultiplier: 2,
    maxBackoffTime: 30000
  }
};
```

## 📊 Dashboard Integration

### Load Balancer Status Widget (`src/components/LoadBalancerStatus.jsx`)

```jsx
function LoadBalancerStatus({ apis }) {
  const [connections, setConnections] = useState(new Map());
  const [circuitStates, setCircuitStates] = useState(new Map());
  const [queueStates, setQueueStates] = useState(new Map());

  return (
    <div className="load-balancer-status">
      <h3>Connection Management</h3>
      
      {apis.map(api => (
        <div key={api.name} className="api-connection-status">
          <div className="api-header">
            <h4>{api.name}</h4>
            <StatusIndicator status={getConnectionStatus(api.name)} />
          </div>
          
          <div className="connection-metrics">
            <MetricItem 
              label="Active Connections" 
              value={connections.get(api.name)?.active || 0}
              max={connections.get(api.name)?.limit || 10}
            />
            
            <MetricItem 
              label="Queue Size" 
              value={queueStates.get(api.name)?.size || 0}
              status={getQueueStatus(api.name)}
            />
            
            <CircuitBreakerIndicator 
              state={circuitStates.get(api.name)}
            />
          </div>
          
          <div className="performance-indicators">
            <ResponseTimeGraph apiName={api.name} />
            <ThroughputGraph apiName={api.name} />
          </div>
        </div>
      ))}
    </div>
  );
}
```

## 🎯 Success Metrics

### Performance Targets
- **Connection Efficiency**: >95% connection pool utilization
- **Response Time**: <500ms average including load balancing overhead
- **Failover Speed**: <2 seconds to detect failure and switch providers
- **Queue Processing**: <100ms average queue wait time

### Reliability Targets
- **Circuit Breaker Accuracy**: <5% false positive circuit opens
- **Failover Success Rate**: >98% successful automatic failovers
- **Connection Stability**: >99% successful connection establishments
- **Load Distribution**: ±10% variance in load across healthy providers

### Cost Optimization
- **Provider Cost Efficiency**: Optimal provider selection for cost/performance ratio
- **Request Batching**: >80% of eligible requests processed in batches
- **Redundancy Management**: Minimal backup provider usage while maintaining reliability

This comprehensive load balancing and connection management system ensures maximum reliability, performance, and cost efficiency for all external API integrations while providing transparent monitoring and control through the dashboard interface.
