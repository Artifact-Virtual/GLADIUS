/**
 * Agent Task Queue Monitoring Service
 * 
 * Provides comprehensive real-time monitoring and analytics for agent task queues
 * across the Legion Enterprise system. Features include:
 * - Real-time queue status monitoring
 * - Task lifecycle tracking
 * - Performance analytics and optimization
 * - Capacity planning and scaling insights
 * - Queue health monitoring and alerting
 * - Predictive analytics for bottleneck prevention
 */

class AgentTaskQueueMonitoringService {
    constructor() {
        this.subscribers = new Set();
        this.isMonitoring = false;
        this.monitoringInterval = null;
        this.analyticsInterval = null;
        this.optimizationInterval = null;
        this.healthCheckInterval = null;
        
        // Monitoring configuration
        this.config = {
            queueMonitoringInterval: 15000,     // 15 seconds for real-time updates
            analyticsUpdateInterval: 60000,     // 1 minute for analytics
            optimizationCheckInterval: 300000,  // 5 minutes for optimization analysis
            healthCheckInterval: 30000,         // 30 seconds for health monitoring
            maxRetries: 3,
            retryDelay: 5000
        };
        
        // Current monitoring state
        this.state = {
            taskQueues: new Map(),
            systemAnalytics: null,
            lifecycleTracking: null,
            healthMetrics: new Map(),
            lastUpdate: null,
            optimizationRecommendations: [],
            alertsGenerated: []
        };
        
        // Performance tracking
        this.performance = {
            apiCallDuration: [],
            processingLatency: [],
            updateFrequency: 0,
            errorRate: 0
        };
        
        // Initialize monitoring components
        this.queueAnalyzer = new QueueAnalysisEngine();
        this.performanceOptimizer = new TaskQueueOptimizer();
        this.capacityPlanner = new CapacityPlanningEngine();
        this.healthMonitor = new QueueHealthMonitor();
        
        console.log('🔄 Agent Task Queue Monitoring Service initialized');
    }

    /**
     * Start comprehensive task queue monitoring
     */
    async startMonitoring() {
        if (this.isMonitoring) {
            console.log('⚠️ Task queue monitoring already active');
            return;
        }

        console.log('🚀 Starting agent task queue monitoring...');
        this.isMonitoring = true;

        try {
            // Initial data load
            await this.performFullSystemUpdate();

            // Start monitoring intervals
            this.monitoringInterval = setInterval(() => {
                this.updateTaskQueues();
            }, this.config.queueMonitoringInterval);

            this.analyticsInterval = setInterval(() => {
                this.updateSystemAnalytics();
            }, this.config.analyticsUpdateInterval);

            this.optimizationInterval = setInterval(() => {
                this.performOptimizationAnalysis();
            }, this.config.optimizationCheckInterval);

            this.healthCheckInterval = setInterval(() => {
                this.performHealthChecks();
            }, this.config.healthCheckInterval);

            console.log('✅ Agent task queue monitoring started successfully');
            this.notifySubscribers('monitoring_started', { timestamp: new Date().toISOString() });

        } catch (error) {
            console.error('❌ Failed to start task queue monitoring:', error);
            this.isMonitoring = false;
            throw error;
        }
    }

    /**
     * Stop task queue monitoring
     */
    stopMonitoring() {
        if (!this.isMonitoring) return;

        console.log('🛑 Stopping agent task queue monitoring...');
        
        clearInterval(this.monitoringInterval);
        clearInterval(this.analyticsInterval);
        clearInterval(this.optimizationInterval);
        clearInterval(this.healthCheckInterval);
        
        this.isMonitoring = false;
        console.log('✅ Task queue monitoring stopped');
        this.notifySubscribers('monitoring_stopped', { timestamp: new Date().toISOString() });
    }

    /**
     * Perform full system update with all task queue data
     */
    async performFullSystemUpdate() {
        console.log('🔄 Performing full task queue system update...');
        
        try {
            const startTime = Date.now();
            
            // Fetch all task queue data in parallel
            const [taskQueues, analytics, lifecycle] = await Promise.all([
                this.fetchTaskQueues(),
                this.fetchSystemAnalytics(),
                this.fetchLifecycleTracking()
            ]);

            // Update state
            this.processTaskQueueData(taskQueues);
            this.state.systemAnalytics = analytics;
            this.state.lifecycleTracking = lifecycle;
            this.state.lastUpdate = new Date().toISOString();

            // Perform analysis
            await this.performComprehensiveAnalysis();

            const duration = Date.now() - startTime;
            this.performance.apiCallDuration.push(duration);
            
            console.log(`✅ Full system update completed in ${duration}ms`);
            this.notifySubscribers('full_update', {
                taskQueues: Array.from(this.state.taskQueues.values()),
                analytics: this.state.systemAnalytics,
                lifecycle: this.state.lifecycleTracking,
                updateTime: this.state.lastUpdate
            });

        } catch (error) {
            console.error('❌ Full system update failed:', error);
            this.performance.errorRate++;
            throw error;
        }
    }

    /**
     * Update task queue monitoring data
     */
    async updateTaskQueues() {
        try {
            const taskQueues = await this.fetchTaskQueues();
            this.processTaskQueueData(taskQueues);
            
            // Analyze queue changes
            const analysis = await this.queueAnalyzer.analyzeQueueChanges(
                Array.from(this.state.taskQueues.values())
            );
            
            this.notifySubscribers('queue_update', {
                queues: Array.from(this.state.taskQueues.values()),
                analysis: analysis,
                timestamp: new Date().toISOString()
            });

        } catch (error) {
            console.error('❌ Task queue update failed:', error);
            this.performance.errorRate++;
        }
    }

    /**
     * Update system analytics
     */
    async updateSystemAnalytics() {
        try {
            const analytics = await this.fetchSystemAnalytics();
            this.state.systemAnalytics = analytics;
            
            // Generate performance insights
            const insights = await this.performanceOptimizer.generateInsights(analytics);
            
            this.notifySubscribers('analytics_update', {
                analytics: analytics,
                insights: insights,
                timestamp: new Date().toISOString()
            });

        } catch (error) {
            console.error('❌ Analytics update failed:', error);
        }
    }

    /**
     * Perform optimization analysis
     */
    async performOptimizationAnalysis() {
        try {
            console.log('🔍 Performing task queue optimization analysis...');
            
            const recommendations = await this.performanceOptimizer.analyzeSystemOptimization({
                taskQueues: Array.from(this.state.taskQueues.values()),
                analytics: this.state.systemAnalytics,
                lifecycle: this.state.lifecycleTracking
            });
            
            this.state.optimizationRecommendations = recommendations;
            
            this.notifySubscribers('optimization_analysis', {
                recommendations: recommendations,
                timestamp: new Date().toISOString()
            });

        } catch (error) {
            console.error('❌ Optimization analysis failed:', error);
        }
    }

    /**
     * Perform health checks on all task queues
     */
    async performHealthChecks() {
        try {
            const healthResults = await this.healthMonitor.checkAllQueues(
                Array.from(this.state.taskQueues.values())
            );
            
            // Update health metrics
            healthResults.forEach(result => {
                this.state.healthMetrics.set(result.agentId, result);
            });
            
            // Check for alerts
            const alerts = await this.healthMonitor.generateAlerts(healthResults);
            if (alerts.length > 0) {
                this.state.alertsGenerated.push(...alerts);
                
                this.notifySubscribers('health_alerts', {
                    alerts: alerts,
                    timestamp: new Date().toISOString()
                });
            }

        } catch (error) {
            console.error('❌ Health check failed:', error);
        }
    }

    /**
     * Get detailed queue information for specific agent
     */
    async getAgentQueueDetail(agentId) {
        try {
            const response = await fetch(`/api/enterprise/agent-task-queue/${agentId}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const detail = await response.json();
            return detail;

        } catch (error) {
            console.error(`❌ Failed to fetch queue detail for ${agentId}:`, error);
            throw error;
        }
    }

    /**
     * Get capacity planning recommendations
     */
    async getCapacityRecommendations() {
        try {
            const recommendations = await this.capacityPlanner.generateRecommendations({
                taskQueues: Array.from(this.state.taskQueues.values()),
                analytics: this.state.systemAnalytics,
                healthMetrics: Array.from(this.state.healthMetrics.values())
            });
            
            return recommendations;

        } catch (error) {
            console.error('❌ Failed to generate capacity recommendations:', error);
            throw error;
        }
    }

    /**
     * Fetch task queues data from API
     */
    async fetchTaskQueues() {
        const response = await fetch('/api/enterprise/agent-task-queues');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    }

    /**
     * Fetch system analytics from API
     */
    async fetchSystemAnalytics() {
        const response = await fetch('/api/enterprise/agent-task-queue-analytics');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    }

    /**
     * Fetch lifecycle tracking data from API
     */
    async fetchLifecycleTracking() {
        const response = await fetch('/api/enterprise/task-lifecycle-tracking');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    }

    /**
     * Process and normalize task queue data
     */
    processTaskQueueData(taskQueues) {
        taskQueues.forEach(queue => {
            this.state.taskQueues.set(queue.agent_id, {
                ...queue,
                lastUpdated: new Date().toISOString(),
                healthScore: this.calculateQueueHealthScore(queue),
                loadLevel: this.calculateLoadLevel(queue),
                efficiencyRating: this.calculateEfficiencyRating(queue)
            });
        });
    }

    /**
     * Calculate queue health score
     */
    calculateQueueHealthScore(queue) {
        const queueStatus = queue.queue_status;
        const performance = queue.performance_metrics;
        
        let healthScore = 100;
        
        // Queue size impact
        if (queueStatus.total_tasks > 20) healthScore -= 10;
        if (queueStatus.total_tasks > 50) healthScore -= 20;
        
        // Performance impact
        if (performance.success_rate_percentage < 95) healthScore -= 15;
        if (performance.success_rate_percentage < 90) healthScore -= 25;
        
        // Wait time impact
        if (performance.average_wait_time_minutes > 10) healthScore -= 10;
        if (performance.average_wait_time_minutes > 30) healthScore -= 20;
        
        return Math.max(0, healthScore);
    }

    /**
     * Calculate load level
     */
    calculateLoadLevel(queue) {
        const capacity = queue.capacity_metrics;
        const loadPercentage = capacity.current_capacity_usage;
        
        if (loadPercentage < 50) return 'low';
        if (loadPercentage < 75) return 'medium';
        if (loadPercentage < 90) return 'high';
        return 'critical';
    }

    /**
     * Calculate efficiency rating
     */
    calculateEfficiencyRating(queue) {
        const performance = queue.performance_metrics;
        const utilization = performance.resource_utilization_percentage;
        const successRate = performance.success_rate_percentage;
        
        const efficiency = (utilization * 0.4) + (successRate * 0.6);
        
        if (efficiency >= 90) return 'excellent';
        if (efficiency >= 80) return 'good';
        if (efficiency >= 70) return 'fair';
        return 'poor';
    }

    /**
     * Perform comprehensive analysis
     */
    async performComprehensiveAnalysis() {
        const analysis = {
            systemHealth: this.calculateSystemHealth(),
            bottleneckAnalysis: this.identifyBottlenecks(),
            optimizationOpportunities: this.identifyOptimizationOpportunities(),
            capacityStatus: this.assessCapacityStatus(),
            performanceTrends: this.analyzePerformanceTrends()
        };
        
        return analysis;
    }

    /**
     * Calculate overall system health
     */
    calculateSystemHealth() {
        const queues = Array.from(this.state.taskQueues.values());
        if (queues.length === 0) return 0;
        
        const avgHealth = queues.reduce((sum, queue) => sum + queue.healthScore, 0) / queues.length;
        return Math.round(avgHealth);
    }

    /**
     * Identify system bottlenecks
     */
    identifyBottlenecks() {
        const queues = Array.from(this.state.taskQueues.values());
        
        return queues
            .filter(queue => queue.loadLevel === 'critical' || queue.efficiencyRating === 'poor')
            .map(queue => ({
                agentId: queue.agent_id,
                issue: queue.loadLevel === 'critical' ? 'high_load' : 'low_efficiency',
                severity: queue.healthScore < 50 ? 'critical' : 'warning',
                recommendation: this.getBottleneckRecommendation(queue)
            }));
    }

    /**
     * Get bottleneck recommendation
     */
    getBottleneckRecommendation(queue) {
        if (queue.loadLevel === 'critical') {
            return 'Consider scaling up agent capacity or redistributing tasks';
        }
        if (queue.efficiencyRating === 'poor') {
            return 'Optimize task processing logic and resource allocation';
        }
        return 'Monitor queue performance and implement gradual improvements';
    }

    /**
     * Identify optimization opportunities
     */
    identifyOptimizationOpportunities() {
        const opportunities = [];
        const queues = Array.from(this.state.taskQueues.values());
        
        // Load balancing opportunities
        const overloaded = queues.filter(q => q.loadLevel === 'high' || q.loadLevel === 'critical');
        const underutilized = queues.filter(q => q.loadLevel === 'low');
        
        if (overloaded.length > 0 && underutilized.length > 0) {
            opportunities.push({
                type: 'load_balancing',
                description: 'Redistribute tasks from overloaded to underutilized agents',
                impact: 'high',
                effort: 'medium'
            });
        }
        
        // Efficiency improvements
        const inefficientQueues = queues.filter(q => q.efficiencyRating === 'fair' || q.efficiencyRating === 'poor');
        if (inefficientQueues.length > 0) {
            opportunities.push({
                type: 'efficiency_optimization',
                description: 'Optimize processing logic for underperforming agents',
                impact: 'medium',
                effort: 'high'
            });
        }
        
        return opportunities;
    }

    /**
     * Assess capacity status
     */
    assessCapacityStatus() {
        const analytics = this.state.systemAnalytics;
        if (!analytics) return null;
        
        const systemLoad = analytics.system_overview?.total_queued_tasks || 0;
        const processingCapacity = analytics.system_overview?.total_processing_tasks || 0;
        
        return {
            currentLoad: systemLoad,
            processingCapacity: processingCapacity,
            utilizationPercentage: Math.round((systemLoad / (systemLoad + processingCapacity)) * 100),
            status: systemLoad > processingCapacity * 2 ? 'overloaded' : 'normal',
            recommendation: systemLoad > processingCapacity * 2 ? 'immediate_scaling_required' : 'monitor_trends'
        };
    }

    /**
     * Analyze performance trends
     */
    analyzePerformanceTrends() {
        return {
            apiCallLatency: this.performance.apiCallDuration.slice(-10),
            errorRate: this.performance.errorRate,
            updateFrequency: this.performance.updateFrequency,
            overallTrend: this.performance.errorRate < 5 ? 'improving' : 'declining'
        };
    }

    /**
     * Subscribe to monitoring updates
     */
    subscribe(callback) {
        this.subscribers.add(callback);
        console.log(`📡 New subscriber added. Total: ${this.subscribers.size}`);
        
        return () => {
            this.subscribers.delete(callback);
            console.log(`📡 Subscriber removed. Total: ${this.subscribers.size}`);
        };
    }

    /**
     * Notify all subscribers of updates
     */
    notifySubscribers(eventType, data) {
        this.subscribers.forEach(callback => {
            try {
                callback({ eventType, data, timestamp: new Date().toISOString() });
            } catch (error) {
                console.error('❌ Subscriber notification failed:', error);
            }
        });
    }

    /**
     * Get current monitoring state
     */
    getCurrentState() {
        return {
            isMonitoring: this.isMonitoring,
            taskQueues: Array.from(this.state.taskQueues.values()),
            systemAnalytics: this.state.systemAnalytics,
            lifecycleTracking: this.state.lifecycleTracking,
            healthMetrics: Array.from(this.state.healthMetrics.values()),
            optimizationRecommendations: this.state.optimizationRecommendations,
            alerts: this.state.alertsGenerated.slice(-10), // Latest 10 alerts
            lastUpdate: this.state.lastUpdate,
            performance: this.performance
        };
    }

    /**
     * Get monitoring statistics
     */
    getMonitoringStats() {
        const queues = Array.from(this.state.taskQueues.values());
        
        return {
            totalAgents: queues.length,
            activeQueues: queues.filter(q => q.queue_status.total_tasks > 0).length,
            totalQueuedTasks: queues.reduce((sum, q) => sum + q.queue_status.total_tasks, 0),
            totalProcessingTasks: queues.reduce((sum, q) => sum + q.queue_status.processing_tasks, 0),
            averageQueueSize: queues.length > 0 ? 
                Math.round(queues.reduce((sum, q) => sum + q.queue_status.total_tasks, 0) / queues.length) : 0,
            systemHealthScore: this.calculateSystemHealth(),
            bottleneckCount: this.identifyBottlenecks().length,
            optimizationOpportunityCount: this.identifyOptimizationOpportunities().length
        };
    }
}

/**
 * Queue Analysis Engine
 * Analyzes queue patterns and changes
 */
class QueueAnalysisEngine {
    constructor() {
        this.previousState = new Map();
    }

    async analyzeQueueChanges(currentQueues) {
        const analysis = {
            changedQueues: [],
            trends: [],
            patterns: [],
            anomalies: []
        };

        currentQueues.forEach(queue => {
            const previous = this.previousState.get(queue.agent_id);
            if (previous) {
                const changes = this.detectChanges(previous, queue);
                if (changes.length > 0) {
                    analysis.changedQueues.push({
                        agentId: queue.agent_id,
                        changes: changes
                    });
                }
            }
            
            this.previousState.set(queue.agent_id, { ...queue });
        });

        return analysis;
    }

    detectChanges(previous, current) {
        const changes = [];
        
        // Queue size changes
        const sizeDiff = current.queue_status.total_tasks - previous.queue_status.total_tasks;
        if (Math.abs(sizeDiff) >= 5) {
            changes.push({
                type: 'queue_size',
                change: sizeDiff > 0 ? 'increased' : 'decreased',
                magnitude: Math.abs(sizeDiff)
            });
        }
        
        // Health score changes
        const healthDiff = current.healthScore - previous.healthScore;
        if (Math.abs(healthDiff) >= 10) {
            changes.push({
                type: 'health_score',
                change: healthDiff > 0 ? 'improved' : 'degraded',
                magnitude: Math.abs(healthDiff)
            });
        }
        
        return changes;
    }
}

/**
 * Task Queue Optimizer
 * Provides optimization recommendations and insights
 */
class TaskQueueOptimizer {
    async generateInsights(analytics) {
        return {
            performanceInsights: this.analyzePerformance(analytics),
            capacityInsights: this.analyzeCapacity(analytics),
            efficiencyInsights: this.analyzeEfficiency(analytics),
            optimizationRecommendations: this.generateOptimizationRecommendations(analytics)
        };
    }

    analyzePerformance(analytics) {
        const overview = analytics.system_overview;
        
        return {
            throughputRating: overview.system_throughput_tasks_per_hour > 100 ? 'high' : 'moderate',
            healthRating: overview.overall_system_health > 85 ? 'excellent' : 'good',
            efficiencyTrend: 'stable' // Could be calculated from historical data
        };
    }

    analyzeCapacity(analytics) {
        const capacity = analytics.capacity_planning;
        
        return {
            currentUtilization: capacity.current_system_load,
            scalingRecommendation: capacity.current_system_load > 80 ? 'scale_up' : 'monitor',
            bottleneckRisk: capacity.bottleneck_agents.length > 0 ? 'high' : 'low'
        };
    }

    analyzeEfficiency(analytics) {
        const queue = analytics.queue_health_metrics;
        
        return {
            overallEfficiency: queue.resource_efficiency_score,
            queueStability: queue.queue_stability_index,
            optimizationPotential: 100 - queue.resource_efficiency_score
        };
    }

    generateOptimizationRecommendations(analytics) {
        const recommendations = [];
        
        if (analytics.capacity_planning.current_system_load > 80) {
            recommendations.push({
                priority: 'high',
                category: 'capacity',
                action: 'Implement horizontal scaling for overloaded agents',
                expectedImpact: 'Reduce queue wait times by 30-50%'
            });
        }
        
        if (analytics.queue_health_metrics.resource_efficiency_score < 80) {
            recommendations.push({
                priority: 'medium',
                category: 'efficiency',
                action: 'Optimize task processing algorithms',
                expectedImpact: 'Improve resource utilization by 15-25%'
            });
        }
        
        return recommendations;
    }

    async analyzeSystemOptimization(systemData) {
        return {
            loadBalancing: this.analyzeLoadBalancing(systemData.taskQueues),
            resourceOptimization: this.analyzeResourceOptimization(systemData.analytics),
            performanceOptimization: this.analyzePerformanceOptimization(systemData.lifecycle),
            scalingRecommendations: this.generateScalingRecommendations(systemData)
        };
    }

    analyzeLoadBalancing(taskQueues) {
        const highLoad = taskQueues.filter(q => q.loadLevel === 'high' || q.loadLevel === 'critical');
        const lowLoad = taskQueues.filter(q => q.loadLevel === 'low');
        
        return {
            imbalanceDetected: highLoad.length > 0 && lowLoad.length > 0,
            overloadedAgents: highLoad.map(q => q.agent_id),
            underutilizedAgents: lowLoad.map(q => q.agent_id),
            recommendation: highLoad.length > 0 ? 'redistribute_tasks' : 'monitor'
        };
    }

    analyzeResourceOptimization(analytics) {
        if (!analytics) return null;
        
        return {
            memoryOptimization: 'Review memory-intensive tasks',
            cpuOptimization: 'Implement parallel processing where applicable',
            networkOptimization: 'Optimize external API calls and data transfers'
        };
    }

    analyzePerformanceOptimization(lifecycle) {
        if (!lifecycle) return null;
        
        return {
            bottleneckPoints: lifecycle.task_flow_analysis?.bottleneck_points || [],
            flowEfficiency: lifecycle.task_flow_analysis?.flow_efficiency || null,
            optimizationPotential: 'Implement intelligent task routing and dependency resolution'
        };
    }

    generateScalingRecommendations(systemData) {
        const totalLoad = systemData.taskQueues.reduce((sum, q) => sum + q.queue_status.total_tasks, 0);
        const avgLoad = totalLoad / systemData.taskQueues.length;
        
        if (avgLoad > 15) {
            return {
                action: 'scale_up',
                urgency: 'high',
                recommendation: 'Add additional agent instances for high-load departments'
            };
        } else if (avgLoad < 5) {
            return {
                action: 'optimize',
                urgency: 'low',
                recommendation: 'Focus on efficiency improvements rather than scaling'
            };
        }
        
        return {
            action: 'monitor',
            urgency: 'low',
            recommendation: 'Current capacity appears adequate'
        };
    }
}

/**
 * Capacity Planning Engine
 * Provides capacity planning and scaling recommendations
 */
class CapacityPlanningEngine {
    async generateRecommendations(systemData) {
        return {
            currentCapacity: this.assessCurrentCapacity(systemData),
            scalingRecommendations: this.generateScalingRecommendations(systemData),
            resourcePlanning: this.planResourceAllocation(systemData),
            futureProjections: this.projectFutureNeeds(systemData)
        };
    }

    assessCurrentCapacity(systemData) {
        const queues = systemData.taskQueues;
        const totalCapacity = queues.reduce((sum, q) => sum + q.capacity_metrics.max_concurrent_tasks, 0);
        const usedCapacity = queues.reduce((sum, q) => sum + q.queue_status.processing_tasks, 0);
        
        return {
            totalCapacity: totalCapacity,
            usedCapacity: usedCapacity,
            utilizationPercentage: Math.round((usedCapacity / totalCapacity) * 100),
            availableCapacity: totalCapacity - usedCapacity
        };
    }

    generateScalingRecommendations(systemData) {
        const capacity = this.assessCurrentCapacity(systemData);
        
        if (capacity.utilizationPercentage > 85) {
            return {
                action: 'immediate_scaling',
                recommendation: 'Add 20-30% more capacity immediately',
                priority: 'critical'
            };
        } else if (capacity.utilizationPercentage > 70) {
            return {
                action: 'planned_scaling',
                recommendation: 'Plan for 15-20% capacity increase',
                priority: 'high'
            };
        }
        
        return {
            action: 'monitor',
            recommendation: 'Monitor utilization trends',
            priority: 'low'
        };
    }

    planResourceAllocation(systemData) {
        const departments = {};
        
        systemData.taskQueues.forEach(queue => {
            const dept = queue.department;
            if (!departments[dept]) {
                departments[dept] = {
                    agents: 0,
                    totalTasks: 0,
                    avgUtilization: 0
                };
            }
            
            departments[dept].agents++;
            departments[dept].totalTasks += queue.queue_status.total_tasks;
            departments[dept].avgUtilization += queue.capacity_metrics.current_capacity_usage;
        });
        
        // Calculate averages
        Object.keys(departments).forEach(dept => {
            departments[dept].avgUtilization = 
                Math.round(departments[dept].avgUtilization / departments[dept].agents);
        });
        
        return departments;
    }

    projectFutureNeeds(systemData) {
        // Simple projection based on current trends
        const currentLoad = systemData.taskQueues.reduce((sum, q) => sum + q.queue_status.total_tasks, 0);
        
        return {
            projectedLoad24h: Math.round(currentLoad * 1.2), // 20% growth
            projectedLoad7d: Math.round(currentLoad * 1.5),  // 50% growth
            recommendedCapacityIncrease: '25-30%',
            timeToScaling: 'Within 2-3 weeks based on current trends'
        };
    }
}

/**
 * Queue Health Monitor
 * Monitors queue health and generates alerts
 */
class QueueHealthMonitor {
    async checkAllQueues(queues) {
        return queues.map(queue => this.checkQueueHealth(queue));
    }

    checkQueueHealth(queue) {
        const healthChecks = {
            queueSize: this.checkQueueSize(queue),
            processingTime: this.checkProcessingTime(queue),
            successRate: this.checkSuccessRate(queue),
            resourceUtilization: this.checkResourceUtilization(queue),
            waitTime: this.checkWaitTime(queue)
        };
        
        const overallHealth = this.calculateOverallHealth(healthChecks);
        
        return {
            agentId: queue.agent_id,
            healthScore: overallHealth.score,
            status: overallHealth.status,
            checks: healthChecks,
            recommendations: this.generateHealthRecommendations(healthChecks)
        };
    }

    checkQueueSize(queue) {
        const size = queue.queue_status.total_tasks;
        if (size > 50) return { status: 'critical', score: 0, message: 'Queue size critically high' };
        if (size > 25) return { status: 'warning', score: 50, message: 'Queue size elevated' };
        if (size > 10) return { status: 'caution', score: 75, message: 'Queue size moderate' };
        return { status: 'healthy', score: 100, message: 'Queue size normal' };
    }

    checkProcessingTime(queue) {
        const time = queue.performance_metrics.avg_processing_time_minutes;
        if (time > 30) return { status: 'critical', score: 0, message: 'Processing time too high' };
        if (time > 20) return { status: 'warning', score: 60, message: 'Processing time elevated' };
        if (time > 10) return { status: 'caution', score: 80, message: 'Processing time moderate' };
        return { status: 'healthy', score: 100, message: 'Processing time optimal' };
    }

    checkSuccessRate(queue) {
        const rate = queue.performance_metrics.success_rate_percentage;
        if (rate < 85) return { status: 'critical', score: 0, message: 'Success rate critically low' };
        if (rate < 92) return { status: 'warning', score: 60, message: 'Success rate below target' };
        if (rate < 97) return { status: 'caution', score: 80, message: 'Success rate acceptable' };
        return { status: 'healthy', score: 100, message: 'Success rate excellent' };
    }

    checkResourceUtilization(queue) {
        const util = queue.performance_metrics.resource_utilization_percentage;
        if (util > 90) return { status: 'critical', score: 20, message: 'Resource utilization critically high' };
        if (util > 80) return { status: 'warning', score: 60, message: 'Resource utilization high' };
        if (util > 70) return { status: 'caution', score: 80, message: 'Resource utilization moderate' };
        return { status: 'healthy', score: 100, message: 'Resource utilization optimal' };
    }

    checkWaitTime(queue) {
        const wait = queue.performance_metrics.average_wait_time_minutes;
        if (wait > 30) return { status: 'critical', score: 0, message: 'Wait time critically high' };
        if (wait > 15) return { status: 'warning', score: 60, message: 'Wait time elevated' };
        if (wait > 5) return { status: 'caution', score: 80, message: 'Wait time moderate' };
        return { status: 'healthy', score: 100, message: 'Wait time optimal' };
    }

    calculateOverallHealth(checks) {
        const scores = Object.values(checks).map(check => check.score);
        const avgScore = scores.reduce((sum, score) => sum + score, 0) / scores.length;
        
        let status = 'healthy';
        if (avgScore < 40) status = 'critical';
        else if (avgScore < 70) status = 'warning';
        else if (avgScore < 85) status = 'caution';
        
        return { score: Math.round(avgScore), status };
    }

    generateHealthRecommendations(checks) {
        const recommendations = [];
        
        Object.entries(checks).forEach(([checkType, result]) => {
            if (result.status === 'critical' || result.status === 'warning') {
                recommendations.push({
                    area: checkType,
                    priority: result.status === 'critical' ? 'high' : 'medium',
                    action: this.getRecommendationForCheck(checkType, result.status)
                });
            }
        });
        
        return recommendations;
    }

    getRecommendationForCheck(checkType, status) {
        const recommendations = {
            queueSize: {
                critical: 'Immediate load balancing required - redistribute tasks',
                warning: 'Monitor queue growth and consider task prioritization'
            },
            processingTime: {
                critical: 'Optimize processing algorithms and resource allocation',
                warning: 'Review task complexity and processing efficiency'
            },
            successRate: {
                critical: 'Investigate error patterns and implement fixes',
                warning: 'Review error logs and improve error handling'
            },
            resourceUtilization: {
                critical: 'Scale up resources immediately or reduce task load',
                warning: 'Monitor resource usage and plan for scaling'
            },
            waitTime: {
                critical: 'Implement priority queuing and parallel processing',
                warning: 'Optimize task scheduling and resource allocation'
            }
        };
        
        return recommendations[checkType]?.[status] || 'Monitor and optimize performance';
    }

    async generateAlerts(healthResults) {
        const alerts = [];
        
        healthResults.forEach(result => {
            if (result.status === 'critical') {
                alerts.push({
                    level: 'critical',
                    agentId: result.agentId,
                    message: `Critical health issue detected for ${result.agentId}`,
                    healthScore: result.healthScore,
                    timestamp: new Date().toISOString(),
                    recommendations: result.recommendations.filter(r => r.priority === 'high')
                });
            } else if (result.status === 'warning' && result.healthScore < 60) {
                alerts.push({
                    level: 'warning',
                    agentId: result.agentId,
                    message: `Performance degradation detected for ${result.agentId}`,
                    healthScore: result.healthScore,
                    timestamp: new Date().toISOString(),
                    recommendations: result.recommendations
                });
            }
        });
        
        return alerts;
    }

    /**
     * Get current state from backend API
     * This method fetches real-time queue data from the enterprise backend
     */
    async getCurrentState() {
        try {
            const response = await fetch('http://localhost:5001/api/enterprise/workflows');
            if (!response.ok) {
                throw new Error(`Backend API error: ${response.status}`);
            }
            
            const backendData = await response.json();
            
            // Transform backend data to expected queue format
            return {
                queues: backendData.active_workflows || {},
                summary: {
                    total_queues: Object.keys(backendData.active_workflows || {}).length,
                    total_tasks: Object.values(backendData.active_workflows || {}).reduce((sum, workflow) => sum + (workflow.tasks || 0), 0),
                    pending_tasks: Object.values(backendData.active_workflows || {}).reduce((sum, workflow) => sum + (workflow.pending || 0), 0),
                    completed_tasks: Object.values(backendData.active_workflows || {}).reduce((sum, workflow) => sum + (workflow.completed || 0), 0)
                },
                alerts: [],
                timestamp: new Date().toISOString()
            };
            
        } catch (error) {
            console.error('❌ Failed to fetch queue data from backend:', error);
            
            // Return fallback data with error indication
            return {
                queues: {},
                summary: {
                    total_queues: 0,
                    total_tasks: 0,
                    pending_tasks: 0,
                    completed_tasks: 0
                },
                alerts: [{
                    id: `queue_error_${Date.now()}`,
                    type: 'error',
                    message: `Failed to connect to queue API: ${error.message}`,
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
export default AgentTaskQueueMonitoringService;
