# API Health Monitoring System Architecture

## 🏗️ System Architecture Overview

**Purpose**: Comprehensive monitoring and management system for 8+ external APIs integrated into the API MONITORING tab  
**Design Philosophy**: Real-time monitoring, intelligent fallbacks, proactive alerting, cost optimization  
**Integration**: Seamlessly embedded in enterprise dashboard transformation

## 📊 Architecture Components

### 1. API Health Service Core (`src/services/ApiHealthService.js`)

```javascript
class ApiHealthService {
  constructor() {
    this.apis = new Map();
    this.healthChecks = new Map();
    this.alertThresholds = {
      responseTime: 5000,    // 5 seconds
      errorRate: 0.05,       // 5% error rate
      uptimeThreshold: 0.995 // 99.5% uptime
    };
    this.checkInterval = 30000; // 30 seconds
    this.eventEmitter = new EventTarget();
  }

  // Core monitoring methods
  async registerAPI(apiConfig) { /* Register API for monitoring */ }
  async performHealthCheck(apiName) { /* Execute health check */ }
  async calculateHealthScore(apiName) { /* Compute overall health score */ }
  async getApiMetrics(apiName, timeRange) { /* Retrieve metrics */ }
  async triggerAlert(apiName, severity, message) { /* Alert system */ }
}
```

**Key Responsibilities:**
- Real-time API health monitoring
- Performance metrics collection  
- Error rate tracking and alerting
- Rate limit management
- Cost tracking and optimization

### 2. API Registry & Configuration (`src/config/apiRegistry.js`)

```javascript
const API_REGISTRY = {
  polygon: {
    name: 'Polygon.io',
    baseUrl: 'https://api.polygon.io',
    category: 'financial',
    tier: 'tier1',
    rateLimit: { requests: 5, period: 60000 }, // 5 requests/minute
    healthCheck: {
      endpoint: '/v2/reference/tickers',
      method: 'GET',
      expectedStatus: 200
    },
    authentication: {
      type: 'apikey',
      keyLocation: 'query',
      keyName: 'apikey'
    },
    cost: { tier: 'paid', monthlyLimit: 1000 }
  },
  coingecko: {
    name: 'CoinGecko',
    baseUrl: 'https://api.coingecko.com/api/v3',
    category: 'financial',
    tier: 'tier1',
    rateLimit: { requests: 50, period: 60000 }, // 50 requests/minute
    healthCheck: {
      endpoint: '/ping',
      method: 'GET',
      expectedStatus: 200
    },
    authentication: { type: 'none' },
    cost: { tier: 'free', monthlyLimit: null }
  },
  // ... configuration for all 8 APIs
};
```

**Configuration Features:**
- Centralized API configuration management
- Tier-based reliability classification  
- Rate limit and cost tracking parameters
- Health check endpoint definitions
- Authentication method specifications

### 3. Real-Time Monitoring Engine (`src/services/ApiMonitoringEngine.js`)

```javascript
class ApiMonitoringEngine {
  constructor(healthService) {
    this.healthService = healthService;
    this.monitors = new Map();
    this.alertSystem = new AlertSystem();
    this.metricsCollector = new MetricsCollector();
    this.webSocketServer = null;
  }

  async startMonitoring() {
    // Initialize health checks for all APIs
    // Start real-time monitoring loops
    // Setup WebSocket broadcasting
  }

  async collectMetrics(apiName) {
    // Response time measurement
    // Success/error rate calculation
    // Rate limit usage tracking
    // Cost accumulation
  }

  async broadcastHealthUpdate(apiName, healthData) {
    // WebSocket broadcast to dashboard
    // Update Redis cache
    // Trigger alerts if needed
  }
}
```

**Monitoring Features:**
- Continuous health status polling
- Real-time metrics collection
- Automated failure detection
- WebSocket-based live updates
- Historical performance tracking

### 4. Alert & Notification System (`src/services/ApiAlertSystem.js`)

```javascript
class ApiAlertSystem {
  constructor() {
    this.alertRules = new Map();
    this.notificationChannels = ['dashboard', 'email', 'webhook'];
    this.alertHistory = [];
    this.suppressionRules = new Map();
  }

  async processAlert(apiName, metrics, thresholds) {
    // Evaluate alert conditions
    // Apply suppression rules
    // Route notifications
    // Update alert history
  }

  async defineAlertRule(rule) {
    // Custom alert rule configuration
    // Threshold management
    // Escalation policies
  }
}
```

**Alert Categories:**
- **Critical**: API completely down, authentication failures
- **Warning**: High response times, elevated error rates  
- **Info**: Rate limit approaching, quota usage updates
- **Cost**: Budget threshold exceeded, usage anomalies

### 5. Request Management & Throttling (`src/services/ApiRequestManager.js`)

```javascript
class ApiRequestManager {
  constructor() {
    this.requestQueues = new Map();
    this.rateLimiters = new Map();
    this.circuitBreakers = new Map();
    this.cacheService = new CacheService();
  }

  async makeRequest(apiName, endpoint, options) {
    // Rate limit enforcement
    // Circuit breaker logic
    // Request queuing
    // Response caching
    // Automatic retries
  }

  async enforceRateLimit(apiName) {
    // Token bucket algorithm
    // Request throttling
    // Queue management
  }

  async handleCircuitBreaker(apiName) {
    // Failure threshold monitoring
    // Circuit state management
    // Automatic recovery
  }
}
```

**Request Features:**
- Intelligent rate limit enforcement
- Circuit breaker pattern for reliability
- Request queuing and prioritization
- Automatic retry logic with backoff
- Response caching strategies

## 🔄 Data Flow Architecture

### 1. Request Flow
```
Dashboard Component → ApiRequestManager → Rate Limiter → Circuit Breaker → External API
                                     ↓
Cache Service ← Response Processing ← API Response
     ↓
Dashboard Update ← WebSocket Broadcast ← Metrics Collection
```

### 2. Monitoring Flow  
```
ApiMonitoringEngine → Health Checks (30s intervals) → Metrics Collection
                                ↓
Alert System ← Threshold Evaluation ← Performance Analysis
     ↓
Dashboard Notifications + Historical Storage + External Alerts
```

### 3. Configuration Flow
```
API Registry → Health Service → Monitoring Engine → Request Manager
                    ↓                    ↓              ↓
              Health Checks      Live Monitoring   Rate Limiting
```

## 🎛️ Dashboard Integration

### API Health Dashboard Component (`src/components/ApiHealthDashboard.jsx`)

```jsx
function ApiHealthDashboard() {
  const [apiStatuses, setApiStatuses] = useState(new Map());
  const [healthMetrics, setHealthMetrics] = useState(new Map());
  const [alerts, setAlerts] = useState([]);

  return (
    <DashboardGrid>
      <ApiStatusGrid apis={apiStatuses} />
      <MetricsVisualization data={healthMetrics} />
      <AlertPanel alerts={alerts} />
      <RequestsChart />
      <CostTracker />
      <ConfigurationPanel />
    </DashboardGrid>
  );
}
```

**Dashboard Features:**
- **Real-Time Status Grid**: Visual health indicators for all APIs
- **Performance Metrics**: Response time, success rate, error distribution
- **Request Analytics**: Usage patterns, rate limit tracking  
- **Cost Monitoring**: Budget tracking, usage optimization
- **Alert Management**: Active alerts, alert history, configuration
- **API Configuration**: Key management, endpoint testing

### Widget Components

1. **ApiStatusIndicator.jsx**
```jsx
<ApiStatusIndicator 
  api="polygon"
  status="healthy|warning|critical"
  responseTime={245}
  uptime={99.8}
  requests={1247}
  errors={3}
/>
```

2. **RequestsChart.jsx**  
```jsx
<RequestsChart
  apiName="coingecko"
  timeRange="24h"
  showRateLimit={true}
  realTime={true}
/>
```

3. **CostTracker.jsx**
```jsx
<CostTracker
  apis={['polygon', 'newsapi']}
  budgetLimit={500}
  currentSpend={234}
  projectedSpend={456}
/>
```

## 💾 Data Storage Strategy

### 1. Real-Time Data (Redis Cache)
```javascript
// API health snapshots (30 second intervals)
api_health:{apiName}:{timestamp} = {
  status: 'healthy|warning|critical',
  responseTime: 245,
  uptime: 99.8,
  requestCount: 1247,
  errorRate: 0.02
}

// Rate limit tracking
rate_limit:{apiName} = {
  requests: 45,
  limit: 50,
  resetTime: 1627849200,
  remaining: 5
}
```

### 2. Historical Data (SQLite Database)
```sql
-- API performance metrics table
CREATE TABLE api_metrics (
    id INTEGER PRIMARY KEY,
    api_name TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    response_time INTEGER,
    status_code INTEGER,
    success BOOLEAN,
    error_message TEXT,
    request_type TEXT,
    INDEX idx_api_timestamp (api_name, timestamp)
);

-- API health snapshots table  
CREATE TABLE api_health_snapshots (
    id INTEGER PRIMARY KEY,
    api_name TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    health_score REAL,
    uptime_percentage REAL,
    avg_response_time INTEGER,
    request_count INTEGER,
    error_count INTEGER,
    INDEX idx_api_health_timestamp (api_name, timestamp)
);

-- API alerts history
CREATE TABLE api_alerts (
    id INTEGER PRIMARY KEY,
    api_name TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT,
    triggered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME NULL,
    INDEX idx_api_alerts_timestamp (api_name, triggered_at)
);
```

### 3. Configuration Data (JSON Files)
```javascript
// API configurations
{
  "apiConfigs": { /* API registry */ },
  "alertRules": { /* Alert thresholds */ },
  "rateLimits": { /* Rate limit configs */ },
  "costBudgets": { /* Budget settings */ }
}
```

## 🔧 Implementation Strategy

### Phase 1: Core Infrastructure (Week 1)
1. **ApiHealthService.js** - Basic health monitoring
2. **API Registry Configuration** - All 8 APIs registered
3. **Basic Dashboard Widget** - Status indicators only
4. **Database Schema** - Metrics and health tables

### Phase 2: Monitoring Engine (Week 1-2)
1. **ApiMonitoringEngine.js** - Continuous monitoring
2. **Real-Time Updates** - WebSocket integration
3. **Metrics Collection** - Performance tracking
4. **Basic Alerting** - Critical alerts only

### Phase 3: Advanced Features (Week 2)
1. **Request Management** - Rate limiting, circuit breakers
2. **Alert System** - Full alert rule engine
3. **Cost Tracking** - Budget monitoring
4. **Dashboard Enhancement** - All widgets and features

### Phase 4: Integration & Testing (Week 2)
1. **Enterprise Dashboard Integration** - API MONITORING tab
2. **Component Migration** - Move existing API widgets
3. **Testing & Optimization** - Performance tuning
4. **Documentation** - User guides and API docs

## 🎯 Success Metrics

### System Health Metrics
- **API Uptime**: Target 99.5% availability across all APIs
- **Response Time**: <2 second average across all endpoints  
- **Error Rate**: <5% failed requests system-wide
- **Alert Response**: <30 second detection and notification time

### User Experience Metrics
- **Dashboard Load Time**: <3 seconds for API MONITORING tab
- **Real-Time Updates**: <5 second data freshness
- **Alert Relevance**: <10% false positive rate
- **Cost Efficiency**: Stay within API budget limits

### System Performance Metrics
- **Monitoring Overhead**: <5% CPU usage for monitoring engine
- **Memory Usage**: <100MB for all monitoring services
- **Storage Growth**: <10MB/day metrics data growth
- **Network Efficiency**: <1MB/minute monitoring traffic

This comprehensive architecture ensures our valuable external API work is not only preserved but significantly enhanced with professional-grade monitoring, alerting, and management capabilities integrated seamlessly into the enterprise dashboard.
