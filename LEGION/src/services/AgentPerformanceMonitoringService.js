/**
 * Legion Enterprise Agent Performance Monitoring Service
 * 
 * Comprehensive agent performance tracking, analytics, and monitoring system
 * providing real-time insights into agent health, efficiency, and business impact.
 * 
 * Features:
 * - Real-time agent performance monitoring
 * - Comprehensive metrics aggregation and analysis
 * - Predictive analytics and health forecasting
 * - SLA compliance tracking and reporting
 * - Performance optimization recommendations
 * - Inter-agent collaboration analysis
 * - Resource utilization monitoring
 * - Alert generation and notification system
 * 
 * @version 2.0.0
 * @since 2024
 */

class AgentPerformanceMonitoringService {
    constructor() {
        this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
        this.cache = new Map();
        this.cacheTimeout = 30000; // 30 seconds
        this.subscribers = new Map();
        this.alertThresholds = this.initializeAlertThresholds();
        this.performanceHistory = new Map();
        this.aggregationEngine = new PerformanceAggregationEngine();
        this.predictiveAnalytics = new AgentPredictiveAnalytics();
        this.slaMonitor = new SLAComplianceMonitor();
        
        // Initialize monitoring intervals
        this.startPerformanceMonitoring();
        this.startTrendAnalysis();
        this.startPredictiveModeling();
    }

    // === CORE PERFORMANCE MONITORING ===

    /**
     * Get comprehensive performance data for all agents
     * @returns {Promise<Array>} Array of agent performance objects
     */
    async getAllAgentPerformance() {
        try {
            const cacheKey = 'all_agent_performance';
            const cached = this.getCachedData(cacheKey);
            if (cached) return cached;

            const response = await fetch(`${this.baseUrl}/api/enterprise/agent-performance`);
            if (!response.ok) {
                throw new Error(`Failed to fetch agent performance: ${response.statusText}`);
            }

            const data = await response.json();
            const enhancedData = await this.enhancePerformanceData(data);
            
            this.setCachedData(cacheKey, enhancedData);
            this.notifySubscribers('agent_performance_updated', enhancedData);
            
            return enhancedData;
        } catch (error) {
            console.error('Error fetching agent performance:', error);
            this.handlePerformanceError('fetch_all_performance', error);
            throw error;
        }
    }

    /**
     * Get detailed performance metrics for specific agent
     * @param {string} agentId - The agent identifier
     * @returns {Promise<Object>} Detailed agent performance object
     */
    async getAgentPerformance(agentId) {
        try {
            const cacheKey = `agent_performance_${agentId}`;
            const cached = this.getCachedData(cacheKey);
            if (cached) return cached;

            const response = await fetch(`${this.baseUrl}/api/enterprise/agent-performance/${agentId}`);
            if (!response.ok) {
                throw new Error(`Failed to fetch performance for agent ${agentId}: ${response.statusText}`);
            }

            const data = await response.json();
            const enhancedData = await this.enhanceAgentData(data);
            
            this.setCachedData(cacheKey, enhancedData);
            this.updatePerformanceHistory(agentId, enhancedData);
            this.notifySubscribers('specific_agent_updated', { agentId, data: enhancedData });
            
            return enhancedData;
        } catch (error) {
            console.error(`Error fetching performance for agent ${agentId}:`, error);
            this.handlePerformanceError('fetch_agent_performance', error, { agentId });
            throw error;
        }
    }

    /**
     * Get system-wide agent performance summary
     * @returns {Promise<Object>} Performance summary with aggregated metrics
     */
    async getPerformanceSummary() {
        try {
            const cacheKey = 'performance_summary';
            const cached = this.getCachedData(cacheKey);
            if (cached) return cached;

            const response = await fetch(`${this.baseUrl}/api/enterprise/agent-performance-summary`);
            if (!response.ok) {
                throw new Error(`Failed to fetch performance summary: ${response.statusText}`);
            }

            const data = await response.json();
            const enhancedSummary = await this.enhanceSummaryData(data);
            
            this.setCachedData(cacheKey, enhancedSummary);
            this.notifySubscribers('summary_updated', enhancedSummary);
            
            return enhancedSummary;
        } catch (error) {
            console.error('Error fetching performance summary:', error);
            this.handlePerformanceError('fetch_summary', error);
            throw error;
        }
    }

    /**
     * Get historical performance data for agent
     * @param {string} agentId - The agent identifier
     * @param {string} timeframe - Time period ('24h', '7d', '30d')
     * @returns {Promise<Object>} Historical performance data
     */
    async getAgentPerformanceHistory(agentId, timeframe = '24h') {
        try {
            const cacheKey = `history_${agentId}_${timeframe}`;
            const cached = this.getCachedData(cacheKey);
            if (cached) return cached;

            const response = await fetch(`${this.baseUrl}/api/enterprise/agent-performance-history/${agentId}?timeframe=${timeframe}`);
            if (!response.ok) {
                throw new Error(`Failed to fetch history for agent ${agentId}: ${response.statusText}`);
            }

            const data = await response.json();
            const processedHistory = this.processHistoricalData(data, timeframe);
            
            this.setCachedData(cacheKey, processedHistory);
            return processedHistory;
        } catch (error) {
            console.error(`Error fetching history for agent ${agentId}:`, error);
            this.handlePerformanceError('fetch_history', error, { agentId, timeframe });
            throw error;
        }
    }

    // === PERFORMANCE ANALYTICS ===

    /**
     * Analyze performance trends across all agents
     * @param {string} timeframe - Analysis period
     * @returns {Object} Trend analysis results
     */
    async analyzePerformanceTrends(timeframe = '7d') {
        try {
            const agents = await this.getAllAgentPerformance();
            const trendAnalysis = {
                overall_trends: this.calculateOverallTrends(agents),
                department_trends: this.analyzeDepartmentTrends(agents),
                performance_patterns: this.identifyPerformancePatterns(agents),
                efficiency_insights: this.generateEfficiencyInsights(agents),
                bottleneck_analysis: this.identifyBottlenecks(agents),
                optimization_opportunities: this.identifyOptimizationOpportunities(agents)
            };

            this.notifySubscribers('trends_analyzed', trendAnalysis);
            return trendAnalysis;
        } catch (error) {
            console.error('Error analyzing performance trends:', error);
            throw error;
        }
    }

    /**
     * Generate comprehensive performance report
     * @param {string} reportType - Type of report ('executive', 'technical', 'operational')
     * @param {string} timeframe - Report period
     * @returns {Object} Formatted performance report
     */
    async generatePerformanceReport(reportType = 'operational', timeframe = '7d') {
        try {
            const summary = await this.getPerformanceSummary();
            const agents = await this.getAllAgentPerformance();
            const trends = await this.analyzePerformanceTrends(timeframe);

            const report = {
                metadata: {
                    report_type: reportType,
                    timeframe: timeframe,
                    generated_at: new Date().toISOString(),
                    data_freshness: this.calculateDataFreshness()
                },
                executive_summary: this.generateExecutiveSummary(summary, trends),
                key_metrics: this.extractKeyMetrics(summary, agents),
                performance_highlights: this.identifyPerformanceHighlights(agents),
                areas_for_improvement: this.identifyImprovementAreas(agents, trends),
                recommendations: this.generateRecommendations(summary, trends),
                sla_compliance: await this.slaMonitor.generateComplianceReport(),
                risk_assessment: this.assessPerformanceRisks(agents, trends),
                cost_analysis: this.analyzeCostEfficiency(agents, summary),
                forecast: await this.predictiveAnalytics.generatePerformanceForecast(agents)
            };

            this.notifySubscribers('report_generated', { reportType, report });
            return report;
        } catch (error) {
            console.error('Error generating performance report:', error);
            throw error;
        }
    }

    // === REAL-TIME MONITORING ===

    /**
     * Start real-time performance monitoring
     */
    startPerformanceMonitoring() {
        this.monitoringInterval = setInterval(async () => {
            try {
                await this.performHealthChecks();
                await this.updatePerformanceMetrics();
                await this.checkAlertConditions();
                await this.updatePredictiveModels();
            } catch (error) {
                console.error('Error in performance monitoring cycle:', error);
            }
        }, 30000); // Every 30 seconds
    }

    /**
     * Perform health checks on all agents
     */
    async performHealthChecks() {
        try {
            const agents = await this.getAllAgentPerformance();
            const healthStatus = {
                timestamp: new Date().toISOString(),
                healthy_agents: 0,
                warning_agents: 0,
                critical_agents: 0,
                offline_agents: 0,
                health_issues: []
            };

            agents.forEach(agent => {
                const health = this.assessAgentHealth(agent);
                healthStatus[`${health.status}_agents`]++;
                
                if (health.issues.length > 0) {
                    healthStatus.health_issues.push({
                        agent_id: agent.agent_id,
                        issues: health.issues,
                        severity: health.severity
                    });
                }
            });

            this.notifySubscribers('health_check_completed', healthStatus);
            return healthStatus;
        } catch (error) {
            console.error('Error performing health checks:', error);
            throw error;
        }
    }

    /**
     * Check alert conditions and trigger notifications
     */
    async checkAlertConditions() {
        try {
            const agents = await this.getAllAgentPerformance();
            const summary = await this.getPerformanceSummary();
            const alerts = [];

            // Check individual agent alerts
            agents.forEach(agent => {
                const agentAlerts = this.checkAgentAlerts(agent);
                alerts.push(...agentAlerts);
            });

            // Check system-wide alerts
            const systemAlerts = this.checkSystemAlerts(summary);
            alerts.push(...systemAlerts);

            // Process and notify about alerts
            if (alerts.length > 0) {
                await this.processAlerts(alerts);
                this.notifySubscribers('alerts_triggered', alerts);
            }

            return alerts;
        } catch (error) {
            console.error('Error checking alert conditions:', error);
            throw error;
        }
    }

    // === PREDICTIVE ANALYTICS ===

    /**
     * Start trend analysis and predictive modeling
     */
    startTrendAnalysis() {
        this.trendInterval = setInterval(async () => {
            try {
                await this.updateTrendModels();
                await this.generatePredictions();
                await this.updateCapacityForecasts();
            } catch (error) {
                console.error('Error in trend analysis cycle:', error);
            }
        }, 300000); // Every 5 minutes
    }

    /**
     * Start predictive modeling
     */
    startPredictiveModeling() {
        this.predictionInterval = setInterval(async () => {
            try {
                const agents = await this.getAllAgentPerformance();
                const predictions = await this.predictiveAnalytics.generatePredictions(agents);
                this.notifySubscribers('predictions_updated', predictions);
            } catch (error) {
                console.error('Error in predictive modeling:', error);
            }
        }, 600000); // Every 10 minutes
    }

    // === SUBSCRIPTION MANAGEMENT ===

    /**
     * Subscribe to performance updates
     * @param {string} eventType - Type of event to subscribe to
     * @param {Function} callback - Callback function
     * @returns {string} Subscription ID
     */
    subscribe(eventType, callback) {
        const subscriptionId = `${eventType}_${Date.now()}_${Math.random()}`;
        
        if (!this.subscribers.has(eventType)) {
            this.subscribers.set(eventType, new Map());
        }
        
        this.subscribers.get(eventType).set(subscriptionId, callback);
        return subscriptionId;
    }

    /**
     * Unsubscribe from performance updates
     * @param {string} eventType - Type of event
     * @param {string} subscriptionId - Subscription ID
     */
    unsubscribe(eventType, subscriptionId) {
        if (this.subscribers.has(eventType)) {
            this.subscribers.get(eventType).delete(subscriptionId);
        }
    }

    /**
     * Notify subscribers of events
     * @param {string} eventType - Type of event
     * @param {any} data - Event data
     */
    notifySubscribers(eventType, data) {
        if (this.subscribers.has(eventType)) {
            this.subscribers.get(eventType).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in subscriber callback for ${eventType}:`, error);
                }
            });
        }
    }

    // === UTILITY METHODS ===

    /**
     * Enhance performance data with additional analytics
     * @param {Array} data - Raw performance data
     * @returns {Array} Enhanced performance data
     */
    async enhancePerformanceData(data) {
        return data.map(agent => ({
            ...agent,
            computed_metrics: this.computeAdditionalMetrics(agent),
            health_score: this.calculateHealthScore(agent),
            efficiency_rating: this.calculateEfficiencyRating(agent),
            risk_assessment: this.assessAgentRisk(agent),
            optimization_suggestions: this.generateOptimizationSuggestions(agent)
        }));
    }

    /**
     * Calculate comprehensive health score for agent
     * @param {Object} agent - Agent performance data
     * @returns {number} Health score (0-100)
     */
    calculateHealthScore(agent) {
        const metrics = agent.performance_metrics || {};
        const business = agent.business_metrics || {};
        const health = agent.health_indicators || {};

        // Weighted health calculation
        const weights = {
            uptime: 0.25,
            error_rate: 0.20,
            response_time: 0.15,
            efficiency: 0.15,
            quality: 0.15,
            resource_usage: 0.10
        };

        const scores = {
            uptime: Math.min(100, (metrics.uptime_hours || 0) / 168 * 100),
            error_rate: Math.max(0, 100 - (metrics.error_rate_percent || 0) * 20),
            response_time: Math.max(0, 100 - (metrics.average_response_time_ms || 0) / 10),
            efficiency: business.efficiency_score || 75,
            quality: business.quality_score || 75,
            resource_usage: Math.max(0, 100 - (metrics.cpu_utilization_percent || 0))
        };

        const weightedScore = Object.keys(weights).reduce((total, key) => {
            return total + (scores[key] * weights[key]);
        }, 0);

        return Math.round(weightedScore * 100) / 100;
    }

    /**
     * Initialize alert thresholds
     * @returns {Object} Alert threshold configuration
     */
    initializeAlertThresholds() {
        return {
            critical: {
                error_rate_percent: 10,
                response_time_ms: 2000,
                cpu_utilization_percent: 95,
                memory_usage_mb: 900,
                uptime_hours: 1
            },
            warning: {
                error_rate_percent: 5,
                response_time_ms: 1000,
                cpu_utilization_percent: 80,
                memory_usage_mb: 700,
                uptime_hours: 24
            },
            info: {
                efficiency_drop_percent: 10,
                quality_drop_percent: 15,
                task_completion_drop_percent: 20
            }
        };
    }

    /**
     * Get cached data if valid
     * @param {string} key - Cache key
     * @returns {any} Cached data or null
     */
    getCachedData(key) {
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.data;
        }
        return null;
    }

    /**
     * Set data in cache
     * @param {string} key - Cache key
     * @param {any} data - Data to cache
     */
    setCachedData(key, data) {
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });
    }

    /**
     * Handle performance monitoring errors
     * @param {string} operation - Operation that failed
     * @param {Error} error - Error object
     * @param {Object} context - Additional context
     */
    handlePerformanceError(operation, error, context = {}) {
        const errorData = {
            operation,
            error: error.message,
            context,
            timestamp: new Date().toISOString()
        };

        console.error('Performance monitoring error:', errorData);
        this.notifySubscribers('monitoring_error', errorData);
    }

    /**
     * Cleanup resources
     */
    cleanup() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
        }
        if (this.trendInterval) {
            clearInterval(this.trendInterval);
        }
        if (this.predictionInterval) {
            clearInterval(this.predictionInterval);
        }
        this.cache.clear();
        this.subscribers.clear();
        this.performanceHistory.clear();
    }
}

/**
 * Performance Aggregation Engine
 * Handles complex data aggregation and metric calculations
 */
class PerformanceAggregationEngine {
    constructor() {
        this.aggregationRules = this.initializeAggregationRules();
    }

    /**
     * Initialize aggregation rules for different metrics
     * @returns {Object} Aggregation rules configuration
     */
    initializeAggregationRules() {
        return {
            sum: ['tasks_completed_24h', 'error_count', 'api_calls_made'],
            average: ['response_time_ms', 'cpu_utilization_percent', 'efficiency_score'],
            max: ['peak_cpu_percent', 'peak_memory_mb'],
            min: ['min_response_time_ms'],
            weighted_average: ['quality_score', 'performance_score']
        };
    }

    /**
     * Aggregate metrics across multiple agents
     * @param {Array} agents - Array of agent performance data
     * @param {Array} metrics - Metrics to aggregate
     * @returns {Object} Aggregated metrics
     */
    aggregateMetrics(agents, metrics) {
        const aggregated = {};
        
        metrics.forEach(metric => {
            const rule = this.getAggregationRule(metric);
            aggregated[metric] = this.applyAggregationRule(agents, metric, rule);
        });

        return aggregated;
    }

    /**
     * Get aggregation rule for metric
     * @param {string} metric - Metric name
     * @returns {string} Aggregation rule
     */
    getAggregationRule(metric) {
        for (const [rule, metricList] of Object.entries(this.aggregationRules)) {
            if (metricList.includes(metric)) {
                return rule;
            }
        }
        return 'average'; // Default
    }

    /**
     * Apply aggregation rule to metric values
     * @param {Array} agents - Agent data
     * @param {string} metric - Metric name
     * @param {string} rule - Aggregation rule
     * @returns {number} Aggregated value
     */
    applyAggregationRule(agents, metric, rule) {
        const values = this.extractMetricValues(agents, metric);
        
        switch (rule) {
            case 'sum':
                return values.reduce((sum, val) => sum + val, 0);
            case 'average':
                return values.length > 0 ? values.reduce((sum, val) => sum + val, 0) / values.length : 0;
            case 'max':
                return values.length > 0 ? Math.max(...values) : 0;
            case 'min':
                return values.length > 0 ? Math.min(...values) : 0;
            case 'weighted_average':
                return this.calculateWeightedAverage(agents, metric);
            default:
                return values.length > 0 ? values.reduce((sum, val) => sum + val, 0) / values.length : 0;
        }
    }

    /**
     * Extract metric values from agents
     * @param {Array} agents - Agent data
     * @param {string} metric - Metric name
     * @returns {Array} Metric values
     */
    extractMetricValues(agents, metric) {
        return agents.map(agent => {
            // Navigate nested metric structure
            const parts = metric.split('.');
            let value = agent;
            
            for (const part of parts) {
                value = value?.[part];
                if (value === undefined) break;
            }
            
            return typeof value === 'number' ? value : 0;
        }).filter(val => !isNaN(val));
    }

    /**
     * Calculate weighted average based on agent importance/load
     * @param {Array} agents - Agent data
     * @param {string} metric - Metric name
     * @returns {number} Weighted average
     */
    calculateWeightedAverage(agents, metric) {
        let weightedSum = 0;
        let totalWeight = 0;

        agents.forEach(agent => {
            const value = this.extractMetricValues([agent], metric)[0] || 0;
            const weight = this.calculateAgentWeight(agent);
            
            weightedSum += value * weight;
            totalWeight += weight;
        });

        return totalWeight > 0 ? weightedSum / totalWeight : 0;
    }

    /**
     * Calculate weight for agent based on its load and importance
     * @param {Object} agent - Agent data
     * @returns {number} Agent weight
     */
    calculateAgentWeight(agent) {
        const metrics = agent.performance_metrics || {};
        const business = agent.business_metrics || {};
        
        // Weight based on task volume and business value
        const taskWeight = (metrics.tasks_completed_24h || 0) / 50; // Normalize to typical range
        const valueWeight = (business.value_generated_usd || 0) / 1000; // Normalize to typical range
        
        return Math.max(0.1, Math.min(2.0, taskWeight + valueWeight)); // Keep weight between 0.1 and 2.0
    }
}

/**
 * Agent Predictive Analytics Engine
 * Provides forecasting and predictive insights for agent performance
 */
class AgentPredictiveAnalytics {
    constructor() {
        this.models = new Map();
        this.predictionHorizon = 24; // hours
    }

    /**
     * Generate performance predictions for agents
     * @param {Array} agents - Current agent data
     * @returns {Object} Prediction results
     */
    async generatePredictions(agents) {
        const predictions = {
            individual_forecasts: {},
            system_forecast: {},
            risk_predictions: {},
            capacity_forecast: {},
            optimization_predictions: {}
        };

        // Generate individual agent forecasts
        for (const agent of agents) {
            predictions.individual_forecasts[agent.agent_id] = await this.forecastAgentPerformance(agent);
        }

        // Generate system-wide forecasts
        predictions.system_forecast = this.forecastSystemPerformance(agents);
        predictions.risk_predictions = this.predictRisks(agents);
        predictions.capacity_forecast = this.forecastCapacityNeeds(agents);
        predictions.optimization_predictions = this.predictOptimizationOpportunities(agents);

        return predictions;
    }

    /**
     * Forecast individual agent performance
     * @param {Object} agent - Agent data
     * @returns {Object} Agent performance forecast
     */
    async forecastAgentPerformance(agent) {
        const metrics = agent.performance_metrics || {};
        const trends = agent.trend_data || {};
        
        return {
            agent_id: agent.agent_id,
            forecast_horizon_hours: this.predictionHorizon,
            predicted_metrics: {
                task_completion_rate: this.predictTaskCompletion(metrics, trends),
                error_rate_forecast: this.predictErrorRate(metrics, trends),
                resource_utilization: this.predictResourceUsage(metrics, trends),
                efficiency_projection: this.predictEfficiency(agent),
                availability_forecast: this.predictAvailability(agent)
            },
            confidence_level: this.calculatePredictionConfidence(agent),
            risk_factors: this.identifyRiskFactors(agent),
            recommendations: this.generatePredictiveRecommendations(agent)
        };
    }

    /**
     * Predict task completion rates
     * @param {Object} metrics - Performance metrics
     * @param {Object} trends - Trend data
     * @returns {Object} Task completion prediction
     */
    predictTaskCompletion(metrics, trends) {
        const current = metrics.tasks_completed_24h || 0;
        const trendMultiplier = this.getTrendMultiplier(trends.performance_trend_7d);
        
        return {
            next_hour: Math.round(current / 24 * trendMultiplier),
            next_4_hours: Math.round(current / 6 * trendMultiplier),
            next_24_hours: Math.round(current * trendMultiplier),
            confidence: 0.75
        };
    }

    /**
     * Get trend multiplier based on trend direction
     * @param {string} trend - Trend direction
     * @returns {number} Multiplier value
     */
    getTrendMultiplier(trend) {
        switch (trend) {
            case 'increasing': return 1.1;
            case 'decreasing': return 0.9;
            case 'stable':
            default: return 1.0;
        }
    }

    /**
     * Calculate prediction confidence level
     * @param {Object} agent - Agent data
     * @returns {number} Confidence level (0-1)
     */
    calculatePredictionConfidence(agent) {
        const health = agent.health_indicators || {};
        const uptime = health.uptime_hours || 0;
        const stability = Math.min(1, uptime / 168); // Based on weekly uptime
        
        const dataQuality = this.assessDataQuality(agent);
        const variance = this.calculateMetricVariance(agent);
        
        return Math.max(0.5, Math.min(1.0, stability * dataQuality * (1 - variance)));
    }

    /**
     * Assess data quality for predictions
     * @param {Object} agent - Agent data
     * @returns {number} Data quality score (0-1)
     */
    assessDataQuality(agent) {
        const requiredFields = [
            'performance_metrics.tasks_completed_24h',
            'performance_metrics.error_rate_percent',
            'performance_metrics.cpu_utilization_percent',
            'health_indicators.uptime_hours'
        ];

        const availableFields = requiredFields.filter(field => {
            const value = this.getNestedValue(agent, field);
            return value !== undefined && value !== null;
        });

        return availableFields.length / requiredFields.length;
    }

    /**
     * Get nested object value by path
     * @param {Object} obj - Object to traverse
     * @param {string} path - Dot-separated path
     * @returns {any} Value at path
     */
    getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => current?.[key], obj);
    }

    /**
     * Calculate metric variance for stability assessment
     * @param {Object} agent - Agent data
     * @returns {number} Variance score (0-1)
     */
    calculateMetricVariance(agent) {
        // Simple variance estimation based on trend stability
        const trends = agent.trend_data || {};
        let instabilityCount = 0;
        const totalTrends = Object.keys(trends).length;

        Object.values(trends).forEach(trend => {
            if (trend === 'increasing' || trend === 'decreasing') {
                instabilityCount++;
            }
        });

        return totalTrends > 0 ? instabilityCount / totalTrends : 0.5;
    }

    /**
     * Generate predictive recommendations
     * @param {Object} agent - Agent data
     * @returns {Array} Array of recommendations
     */
    generatePredictiveRecommendations(agent) {
        const recommendations = [];
        const metrics = agent.performance_metrics || {};
        const trends = agent.trend_data || {};

        // Error rate recommendations
        if (trends.error_trend_24h === 'increasing') {
            recommendations.push({
                type: 'warning',
                priority: 'high',
                message: 'Error rate trending upward - recommend investigation',
                action: 'investigate_errors'
            });
        }

        // Performance optimization
        if (metrics.cpu_utilization_percent > 80) {
            recommendations.push({
                type: 'optimization',
                priority: 'medium',
                message: 'High CPU utilization detected - consider optimization',
                action: 'optimize_cpu_usage'
            });
        }

        // Capacity planning
        if (trends.load_trend === 'increasing') {
            recommendations.push({
                type: 'capacity',
                priority: 'medium',
                message: 'Load trending upward - plan capacity increase',
                action: 'plan_capacity_expansion'
            });
        }

        return recommendations;
    }
}

/**
 * SLA Compliance Monitor
 * Tracks and reports on Service Level Agreement compliance
 */
class SLAComplianceMonitor {
    constructor() {
        this.slaTargets = this.initializeSLATargets();
    }

    /**
     * Initialize SLA targets
     * @returns {Object} SLA target configuration
     */
    initializeSLATargets() {
        return {
            availability: 99.5, // 99.5% uptime
            response_time: 500, // 500ms average response time
            error_rate: 1.0, // 1% maximum error rate
            throughput: 100, // 100 tasks per hour minimum
            quality_score: 85 // 85% minimum quality score
        };
    }

    /**
     * Generate SLA compliance report
     * @returns {Object} SLA compliance report
     */
    async generateComplianceReport() {
        const agents = await this.getAllAgents(); // This would be injected
        
        return {
            overall_compliance: this.calculateOverallCompliance(agents),
            metric_compliance: this.calculateMetricCompliance(agents),
            violations: this.identifyViolations(agents),
            trends: this.analyzeSLATrends(agents),
            recommendations: this.generateSLARecommendations(agents)
        };
    }

    /**
     * Calculate overall SLA compliance percentage
     * @param {Array} agents - Agent performance data
     * @returns {number} Overall compliance percentage
     */
    calculateOverallCompliance(agents) {
        const compliantAgents = agents.filter(agent => this.isAgentCompliant(agent));
        return agents.length > 0 ? (compliantAgents.length / agents.length) * 100 : 100;
    }

    /**
     * Check if agent meets SLA requirements
     * @param {Object} agent - Agent performance data
     * @returns {boolean} True if compliant
     */
    isAgentCompliant(agent) {
        const metrics = agent.performance_metrics || {};
        const business = agent.business_metrics || {};
        const health = agent.health_indicators || {};

        // Calculate availability percentage
        const availability = Math.min(100, (metrics.uptime_hours || 0) / 168 * 100);
        
        return (
            availability >= this.slaTargets.availability &&
            (metrics.average_response_time_ms || 0) <= this.slaTargets.response_time &&
            (metrics.error_rate_percent || 0) <= this.slaTargets.error_rate &&
            (metrics.tasks_completed_24h || 0) >= this.slaTargets.throughput / 24 &&
            (business.quality_score || 0) >= this.slaTargets.quality_score
        );
    }

    /**
     * Get current state from backend API
     * This method fetches real-time performance data from the enterprise backend
     */
    async getCurrentState() {
        try {
            const response = await fetch('http://localhost:5001/api/enterprise/system-status');
            if (!response.ok) {
                throw new Error(`Backend API error: ${response.status}`);
            }
            
            const backendData = await response.json();
            
            // Transform backend data to expected performance format
            return {
                performance: {
                    overall_health: backendData.overall_health || 'unknown',
                    active_agents: backendData.active_agents || 0,
                    active_workflows: backendData.active_workflows || 0,
                    system_load: backendData.system_load || 0,
                    avg_response_time: backendData.avg_response_time || '0ms',
                    total_requests: backendData.total_requests || 0,
                    error_rate: backendData.error_rate || 0,
                    uptime: backendData.uptime || '0m'
                },
                alerts: [],
                timestamp: new Date().toISOString()
            };
            
        } catch (error) {
            console.error('❌ Failed to fetch performance data from backend:', error);
            
            // Return fallback data with error indication
            return {
                performance: {
                    overall_health: 'error',
                    active_agents: 0,
                    active_workflows: 0,
                    system_load: 0,
                    avg_response_time: 'N/A',
                    total_requests: 0,
                    error_rate: 100,
                    uptime: '0m'
                },
                alerts: [{
                    id: `performance_error_${Date.now()}`,
                    type: 'error',
                    message: `Failed to connect to performance API: ${error.message}`,
                    timestamp: new Date().toISOString(),
                    severity: 'critical'
                }],
                timestamp: new Date().toISOString(),
                error: error.message
            };
        }
    }
}

// Export the service
export default AgentPerformanceMonitoringService;
export { PerformanceAggregationEngine, AgentPredictiveAnalytics, SLAComplianceMonitor };
