/**
 * Legion Enterprise Inter-Agent Message Monitoring Service
 * 
 * Comprehensive monitoring and analysis of inter-agent communications,
 * providing real-time insights into message flows, collaboration patterns,
 * and communication efficiency across the enterprise agent network.
 * 
 * Features:
 * - Real-time inter-agent message monitoring
 * - Communication matrix and flow analysis
 * - Message pattern recognition and analytics
 * - Collaboration efficiency tracking
 * - Communication bottleneck identification
 * - Security and compliance monitoring
 * - Predictive communication insights
 * - Performance optimization recommendations
 * 
 * @version 2.0.0
 * @since 2024
 */

class InterAgentMessageMonitoringService {
    constructor() {
        this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
        this.cache = new Map();
        this.cacheTimeout = 15000; // 15 seconds for real-time data
        this.subscribers = new Map();
        this.messageBuffer = new Map();
        this.communicationAnalyzer = new CommunicationAnalyzer();
        this.flowOptimizer = new MessageFlowOptimizer();
        this.securityMonitor = new CommunicationSecurityMonitor();
        
        // Initialize monitoring systems
        this.startMessageMonitoring();
        this.startFlowAnalysis();
        this.startSecurityMonitoring();
    }

    // === CORE MESSAGE MONITORING ===

    /**
     * Get all inter-agent messages with real-time updates
     * @param {Object} filters - Message filtering options
     * @returns {Promise<Array>} Array of inter-agent messages
     */
    async getInterAgentMessages(filters = {}) {
        try {
            const cacheKey = `messages_${JSON.stringify(filters)}`;
            const cached = this.getCachedData(cacheKey);
            if (cached) return cached;

            const queryParams = new URLSearchParams(filters);
            const response = await fetch(`${this.baseUrl}/api/enterprise/inter-agent-messages?${queryParams}`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch inter-agent messages: ${response.statusText}`);
            }

            const messages = await response.json();
            const enhancedMessages = this.enhanceMessageData(messages);
            
            this.setCachedData(cacheKey, enhancedMessages);
            this.updateMessageBuffer(enhancedMessages);
            this.notifySubscribers('messages_updated', enhancedMessages);
            
            return enhancedMessages;
        } catch (error) {
            console.error('Error fetching inter-agent messages:', error);
            this.handleMonitoringError('fetch_messages', error);
            throw error;
        }
    }

    /**
     * Get communication matrix showing department-to-department message flows
     * @returns {Promise<Object>} Communication matrix with flow metrics
     */
    async getCommunicationMatrix() {
        try {
            const cacheKey = 'communication_matrix';
            const cached = this.getCachedData(cacheKey);
            if (cached) return cached;

            const response = await fetch(`${this.baseUrl}/api/enterprise/inter-agent-communication-matrix`);
            if (!response.ok) {
                throw new Error(`Failed to fetch communication matrix: ${response.statusText}`);
            }

            const matrix = await response.json();
            const enhancedMatrix = this.enhanceCommunicationMatrix(matrix);
            
            this.setCachedData(cacheKey, enhancedMatrix);
            this.notifySubscribers('matrix_updated', enhancedMatrix);
            
            return enhancedMatrix;
        } catch (error) {
            console.error('Error fetching communication matrix:', error);
            this.handleMonitoringError('fetch_matrix', error);
            throw error;
        }
    }

    /**
     * Get detailed message flow analytics and patterns
     * @returns {Promise<Object>} Comprehensive flow analytics
     */
    async getMessageFlowAnalytics() {
        try {
            const cacheKey = 'flow_analytics';
            const cached = this.getCachedData(cacheKey);
            if (cached) return cached;

            const response = await fetch(`${this.baseUrl}/api/enterprise/message-flow-analytics`);
            if (!response.ok) {
                throw new Error(`Failed to fetch flow analytics: ${response.statusText}`);
            }

            const analytics = await response.json();
            const enhancedAnalytics = await this.enhanceFlowAnalytics(analytics);
            
            this.setCachedData(cacheKey, enhancedAnalytics);
            this.notifySubscribers('analytics_updated', enhancedAnalytics);
            
            return enhancedAnalytics;
        } catch (error) {
            console.error('Error fetching flow analytics:', error);
            this.handleMonitoringError('fetch_analytics', error);
            throw error;
        }
    }

    /**
     * Get message history for specific agent
     * @param {string} agentId - Agent identifier
     * @param {Object} options - History options (timeframe, limit, etc.)
     * @returns {Promise<Object>} Agent message history
     */
    async getAgentMessageHistory(agentId, options = {}) {
        try {
            const cacheKey = `agent_history_${agentId}_${JSON.stringify(options)}`;
            const cached = this.getCachedData(cacheKey);
            if (cached) return cached;

            const queryParams = new URLSearchParams(options);
            const response = await fetch(`${this.baseUrl}/api/enterprise/agent-message-history/${agentId}?${queryParams}`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch message history for ${agentId}: ${response.statusText}`);
            }

            const history = await response.json();
            const enhancedHistory = this.enhanceAgentHistory(history);
            
            this.setCachedData(cacheKey, enhancedHistory);
            this.notifySubscribers('agent_history_updated', { agentId, history: enhancedHistory });
            
            return enhancedHistory;
        } catch (error) {
            console.error(`Error fetching message history for agent ${agentId}:`, error);
            this.handleMonitoringError('fetch_agent_history', error, { agentId });
            throw error;
        }
    }

    // === MESSAGE ANALYSIS AND ENHANCEMENT ===

    /**
     * Enhance message data with additional analytics
     * @param {Array} messages - Raw message data
     * @returns {Array} Enhanced message data
     */
    enhanceMessageData(messages) {
        return messages.map(message => ({
            ...message,
            analytics: {
                communication_efficiency: this.calculateCommunicationEfficiency(message),
                business_impact_score: this.assessBusinessImpact(message),
                workflow_significance: this.assessWorkflowSignificance(message),
                response_prediction: this.predictResponseBehavior(message),
                anomaly_score: this.detectCommunicationAnomalies(message)
            },
            enhanced_context: {
                department_relationship: this.analyzeDepartmentRelationship(message.sender.department, message.receiver.department),
                collaboration_pattern: this.identifyCollaborationPattern(message),
                priority_justification: this.analyzePriorityJustification(message),
                optimization_suggestions: this.generateOptimizationSuggestions(message)
            },
            real_time_metrics: {
                current_queue_position: this.estimateQueuePosition(message),
                estimated_processing_time: this.estimateProcessingTime(message),
                alternative_routes: this.identifyAlternativeRoutes(message),
                congestion_level: this.assessCongestionLevel(message.sender.department, message.receiver.department)
            }
        }));
    }

    /**
     * Enhance communication matrix with analytics
     * @param {Object} matrix - Raw matrix data
     * @returns {Object} Enhanced matrix with insights
     */
    enhanceCommunicationMatrix(matrix) {
        const enhanced = { ...matrix };
        
        // Add network analysis
        enhanced.network_analysis = {
            connectivity_score: this.calculateNetworkConnectivity(matrix.matrix),
            communication_hubs: this.identifyCommunicationHubs(matrix.matrix),
            bottleneck_paths: this.identifyBottleneckPaths(matrix.matrix),
            redundancy_analysis: this.analyzeRedundancy(matrix.matrix),
            efficiency_score: this.calculateNetworkEfficiency(matrix.matrix)
        };

        // Add flow optimization recommendations
        enhanced.optimization_recommendations = this.generateMatrixOptimizations(matrix.matrix);
        
        // Add trend predictions
        enhanced.trend_predictions = this.predictCommunicationTrends(matrix.matrix);
        
        return enhanced;
    }

    /**
     * Enhance flow analytics with predictive insights
     * @param {Object} analytics - Raw analytics data
     * @returns {Object} Enhanced analytics
     */
    async enhanceFlowAnalytics(analytics) {
        const enhanced = { ...analytics };
        
        // Add machine learning insights
        enhanced.ml_insights = {
            pattern_recognition: await this.recognizeCommunicationPatterns(analytics),
            anomaly_detection: this.detectFlowAnomalies(analytics),
            efficiency_optimization: this.optimizeFlowEfficiency(analytics),
            capacity_planning: this.planCapacity(analytics)
        };

        // Add behavioral analysis
        enhanced.behavioral_analysis = {
            agent_communication_profiles: this.createAgentProfiles(analytics),
            collaboration_effectiveness: this.assessCollaborationEffectiveness(analytics),
            workflow_coordination_quality: this.assessCoordinationQuality(analytics)
        };

        return enhanced;
    }

    // === REAL-TIME MONITORING ===

    /**
     * Start real-time message monitoring
     */
    startMessageMonitoring() {
        this.messageMonitoringInterval = setInterval(async () => {
            try {
                await this.updateMessageStreams();
                await this.analyzeRealtimePatterns();
                await this.checkCommunicationHealth();
                await this.updatePerformanceMetrics();
            } catch (error) {
                console.error('Error in message monitoring cycle:', error);
            }
        }, 15000); // Every 15 seconds
    }

    /**
     * Start flow analysis monitoring
     */
    startFlowAnalysis() {
        this.flowAnalysisInterval = setInterval(async () => {
            try {
                await this.analyzeFlowPatterns();
                await this.optimizeMessageRouting();
                await this.updateEfficiencyMetrics();
                await this.predictFlowBottlenecks();
            } catch (error) {
                console.error('Error in flow analysis cycle:', error);
            }
        }, 60000); // Every minute
    }

    /**
     * Start security monitoring
     */
    startSecurityMonitoring() {
        this.securityMonitoringInterval = setInterval(async () => {
            try {
                await this.monitorSecurityMetrics();
                await this.detectSecurityAnomalies();
                await this.validateEncryption();
                await this.auditCommunicationCompliance();
            } catch (error) {
                console.error('Error in security monitoring cycle:', error);
            }
        }, 30000); // Every 30 seconds
    }

    // === ANALYTICS METHODS ===

    /**
     * Calculate communication efficiency between agents
     * @param {Object} message - Message data
     * @returns {number} Efficiency score (0-100)
     */
    calculateCommunicationEfficiency(message) {
        const processingTime = message.message_details.processing_time_ms || 0;
        const retryCount = message.message_details.retry_count || 0;
        const priorityWeight = this.getPriorityWeight(message.message_details.priority);
        
        // Base efficiency calculation
        let efficiency = 100;
        
        // Penalize slow processing
        if (processingTime > 1000) efficiency -= 20;
        else if (processingTime > 500) efficiency -= 10;
        
        // Penalize retries
        efficiency -= (retryCount * 15);
        
        // Apply priority weighting
        efficiency = efficiency * priorityWeight;
        
        return Math.max(0, Math.min(100, efficiency));
    }

    /**
     * Assess business impact of message
     * @param {Object} message - Message data
     * @returns {number} Impact score (1-10)
     */
    assessBusinessImpact(message) {
        const type = message.message_details.type;
        const priority = message.message_details.priority;
        const hasWorkflow = message.workflow_context.workflow_id !== null;
        
        let impact = 5; // Base impact
        
        // Type-based impact
        const typeImpacts = {
            'task_delegation': 8,
            'result_sharing': 7,
            'coordination': 6,
            'data_request': 5,
            'status_update': 4,
            'alert': 9,
            'notification': 3
        };
        
        impact = typeImpacts[type] || 5;
        
        // Priority boost
        if (priority === 'critical') impact += 2;
        else if (priority === 'high') impact += 1;
        else if (priority === 'low') impact -= 1;
        
        // Workflow boost
        if (hasWorkflow) impact += 1;
        
        return Math.max(1, Math.min(10, impact));
    }

    /**
     * Identify bottleneck paths in communication matrix
     * @param {Object} matrix - Communication matrix
     * @returns {Array} Bottleneck paths
     */
    identifyBottleneckPaths(matrix) {
        const bottlenecks = [];
        
        Object.keys(matrix).forEach(sender => {
            Object.keys(matrix[sender]).forEach(receiver => {
                if (sender !== receiver) {
                    const path = matrix[sender][receiver];
                    const responseTime = path.avg_response_time_ms || 0;
                    const successRate = path.success_rate_percent || 100;
                    
                    // Identify bottlenecks based on poor performance
                    if (responseTime > 1500 || successRate < 90) {
                        bottlenecks.push({
                            from: sender,
                            to: receiver,
                            response_time: responseTime,
                            success_rate: successRate,
                            severity: this.calculateBottleneckSeverity(responseTime, successRate),
                            recommended_action: this.recommendBottleneckAction(responseTime, successRate)
                        });
                    }
                }
            });
        });
        
        return bottlenecks.sort((a, b) => b.severity - a.severity);
    }

    /**
     * Calculate bottleneck severity
     * @param {number} responseTime - Response time in ms
     * @param {number} successRate - Success rate percentage
     * @returns {number} Severity score (1-10)
     */
    calculateBottleneckSeverity(responseTime, successRate) {
        let severity = 1;
        
        // Response time impact
        if (responseTime > 3000) severity += 4;
        else if (responseTime > 2000) severity += 3;
        else if (responseTime > 1500) severity += 2;
        else if (responseTime > 1000) severity += 1;
        
        // Success rate impact
        if (successRate < 80) severity += 4;
        else if (successRate < 85) severity += 3;
        else if (successRate < 90) severity += 2;
        else if (successRate < 95) severity += 1;
        
        return Math.min(10, severity);
    }

    /**
     * Generate optimization suggestions for messages
     * @param {Object} message - Message data
     * @returns {Array} Optimization suggestions
     */
    generateOptimizationSuggestions(message) {
        const suggestions = [];
        const details = message.message_details;
        const performance = message.performance_metrics;
        
        // Processing time optimization
        if (details.processing_time_ms > 1000) {
            suggestions.push({
                type: 'performance',
                priority: 'high',
                suggestion: 'Optimize message processing pipeline',
                estimated_improvement: '40-60% processing time reduction'
            });
        }
        
        // Retry optimization
        if (details.retry_count > 0) {
            suggestions.push({
                type: 'reliability',
                priority: 'medium',
                suggestion: 'Implement circuit breaker pattern',
                estimated_improvement: '70% reduction in failed retries'
            });
        }
        
        // Content size optimization
        if (details.content_size_bytes > 3000) {
            suggestions.push({
                type: 'efficiency',
                priority: 'medium',
                suggestion: 'Implement message compression',
                estimated_improvement: '30-50% bandwidth reduction'
            });
        }
        
        // Priority optimization
        if (details.priority === 'low' && performance.impact_score > 7) {
            suggestions.push({
                type: 'priority',
                priority: 'low',
                suggestion: 'Consider upgrading message priority',
                estimated_improvement: 'Better resource allocation'
            });
        }
        
        return suggestions;
    }

    // === SUBSCRIPTION MANAGEMENT ===

    /**
     * Subscribe to message monitoring updates
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
     * Unsubscribe from monitoring updates
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
     * Get priority weight for calculations
     * @param {string} priority - Message priority
     * @returns {number} Weight multiplier
     */
    getPriorityWeight(priority) {
        const weights = {
            'critical': 1.2,
            'high': 1.1,
            'medium': 1.0,
            'low': 0.9
        };
        return weights[priority] || 1.0;
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
     * Handle monitoring errors
     * @param {string} operation - Operation that failed
     * @param {Error} error - Error object
     * @param {Object} context - Additional context
     */
    handleMonitoringError(operation, error, context = {}) {
        const errorData = {
            operation,
            error: error.message,
            context,
            timestamp: new Date().toISOString()
        };

        console.error('Message monitoring error:', errorData);
        this.notifySubscribers('monitoring_error', errorData);
    }

    /**
     * Cleanup resources
     */
    cleanup() {
        if (this.messageMonitoringInterval) {
            clearInterval(this.messageMonitoringInterval);
        }
        if (this.flowAnalysisInterval) {
            clearInterval(this.flowAnalysisInterval);
        }
        if (this.securityMonitoringInterval) {
            clearInterval(this.securityMonitoringInterval);
        }
        this.cache.clear();
        this.subscribers.clear();
        this.messageBuffer.clear();
    }
}

/**
 * Communication Analyzer
 * Advanced analytics for communication patterns and efficiency
 */
class CommunicationAnalyzer {
    constructor() {
        this.patterns = new Map();
        this.efficiency = new Map();
    }

    /**
     * Analyze communication patterns
     * @param {Array} messages - Message data
     * @returns {Object} Pattern analysis results
     */
    analyzePatterns(messages) {
        const patterns = {
            temporal: this.analyzeTemporalPatterns(messages),
            departmental: this.analyzeDepartmentalPatterns(messages),
            workflow: this.analyzeWorkflowPatterns(messages),
            priority: this.analyzePriorityPatterns(messages)
        };

        return patterns;
    }

    /**
     * Analyze temporal communication patterns
     * @param {Array} messages - Message data
     * @returns {Object} Temporal pattern analysis
     */
    analyzeTemporalPatterns(messages) {
        const hourlyDistribution = new Array(24).fill(0);
        const dailyTrends = new Map();
        
        messages.forEach(message => {
            const timestamp = new Date(message.timestamp);
            const hour = timestamp.getHours();
            const day = timestamp.toDateString();
            
            hourlyDistribution[hour]++;
            dailyTrends.set(day, (dailyTrends.get(day) || 0) + 1);
        });

        return {
            hourly_distribution: hourlyDistribution,
            peak_hours: this.identifyPeakHours(hourlyDistribution),
            daily_trends: Object.fromEntries(dailyTrends),
            activity_score: this.calculateActivityScore(hourlyDistribution)
        };
    }

    /**
     * Identify peak communication hours
     * @param {Array} hourlyDistribution - Hourly message counts
     * @returns {Array} Peak hours
     */
    identifyPeakHours(hourlyDistribution) {
        const average = hourlyDistribution.reduce((sum, count) => sum + count, 0) / 24;
        const threshold = average * 1.5;
        
        return hourlyDistribution
            .map((count, hour) => ({ hour, count }))
            .filter(({ count }) => count > threshold)
            .sort((a, b) => b.count - a.count)
            .slice(0, 5);
    }

    /**
     * Calculate overall activity score
     * @param {Array} hourlyDistribution - Hourly message counts
     * @returns {number} Activity score (0-100)
     */
    calculateActivityScore(hourlyDistribution) {
        const total = hourlyDistribution.reduce((sum, count) => sum + count, 0);
        const activeHours = hourlyDistribution.filter(count => count > 0).length;
        const distribution = activeHours / 24;
        const intensity = total / activeHours;
        
        return Math.round((distribution * 50) + (Math.min(intensity / 10, 1) * 50));
    }
}

/**
 * Message Flow Optimizer
 * Optimizes message routing and flow efficiency
 */
class MessageFlowOptimizer {
    constructor() {
        this.routes = new Map();
        this.optimizations = new Map();
    }

    /**
     * Optimize message flow based on current patterns
     * @param {Object} matrix - Communication matrix
     * @returns {Object} Optimization recommendations
     */
    optimizeFlow(matrix) {
        const optimizations = {
            routing_improvements: this.optimizeRouting(matrix),
            load_balancing: this.optimizeLoadBalancing(matrix),
            caching_opportunities: this.identifyCachingOpportunities(matrix),
            bandwidth_optimization: this.optimizeBandwidth(matrix)
        };

        return optimizations;
    }

    /**
     * Optimize message routing
     * @param {Object} matrix - Communication matrix
     * @returns {Array} Routing optimizations
     */
    optimizeRouting(matrix) {
        const optimizations = [];
        
        Object.keys(matrix).forEach(sender => {
            Object.keys(matrix[sender]).forEach(receiver => {
                if (sender !== receiver) {
                    const path = matrix[sender][receiver];
                    if (path.avg_response_time_ms > 1000) {
                        optimizations.push({
                            path: `${sender} -> ${receiver}`,
                            current_time: path.avg_response_time_ms,
                            optimization: 'direct_connection',
                            estimated_improvement: '40-60%'
                        });
                    }
                }
            });
        });

        return optimizations;
    }
}

/**
 * Communication Security Monitor
 * Monitors security aspects of inter-agent communications
 */
class CommunicationSecurityMonitor {
    constructor() {
        this.securityMetrics = new Map();
        this.threats = new Map();
    }

    /**
     * Monitor communication security
     * @param {Array} messages - Message data
     * @returns {Object} Security analysis
     */
    monitorSecurity(messages) {
        return {
            encryption_coverage: this.analyzeEncryption(messages),
            authentication_success: this.analyzeAuthentication(messages),
            anomaly_detection: this.detectAnomalies(messages),
            compliance_status: this.checkCompliance(messages)
        };
    }

    /**
     * Analyze encryption coverage
     * @param {Array} messages - Message data
     * @returns {Object} Encryption analysis
     */
    analyzeEncryption(messages) {
        const encryptionLevels = messages.reduce((acc, message) => {
            const level = message.security_context?.encryption_level || 'none';
            acc[level] = (acc[level] || 0) + 1;
            return acc;
        }, {});

        const total = messages.length;
        const encrypted = total - (encryptionLevels.none || 0);
        
        return {
            coverage_percentage: total > 0 ? (encrypted / total) * 100 : 100,
            encryption_distribution: encryptionLevels,
            compliance_score: this.calculateEncryptionCompliance(encryptionLevels, total)
        };
    }

    /**
     * Calculate encryption compliance score
     * @param {Object} encryptionLevels - Encryption level distribution
     * @param {number} total - Total messages
     * @returns {number} Compliance score (0-100)
     */
    calculateEncryptionCompliance(encryptionLevels, total) {
        if (total === 0) return 100;
        
        const weights = {
            'maximum': 100,
            'enhanced': 85,
            'standard': 70,
            'none': 0
        };
        
        let weightedSum = 0;
        Object.entries(encryptionLevels).forEach(([level, count]) => {
            weightedSum += (weights[level] || 0) * count;
        });
        
        return Math.round(weightedSum / total);
    }

    /**
     * Get current state from backend API
     * This method fetches real-time messaging data from the enterprise backend
     */
    async getCurrentState() {
        try {
            // For now, return basic messaging state from system status
            const response = await fetch('http://localhost:5001/api/enterprise/system-status');
            if (!response.ok) {
                throw new Error(`Backend API error: ${response.status}`);
            }
            
            const backendData = await response.json();
            
            // Transform backend data to expected messaging format
            return {
                messaging: {
                    total_messages: backendData.total_requests || 0,
                    active_channels: Math.ceil((backendData.active_agents || 0) / 2), // Estimate based on agents
                    message_rate: `${Math.round((backendData.total_requests || 0) / 60)}/min`,
                    avg_latency: backendData.avg_response_time || '0ms',
                    error_rate: backendData.error_rate || 0
                },
                alerts: [],
                timestamp: new Date().toISOString()
            };
            
        } catch (error) {
            console.error('❌ Failed to fetch messaging data from backend:', error);
            
            // Return fallback data with error indication
            return {
                messaging: {
                    total_messages: 0,
                    active_channels: 0,
                    message_rate: '0/min',
                    avg_latency: 'N/A',
                    error_rate: 100
                },
                alerts: [{
                    id: `messaging_error_${Date.now()}`,
                    type: 'error',
                    message: `Failed to connect to messaging API: ${error.message}`,
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
export default InterAgentMessageMonitoringService;
export { CommunicationAnalyzer, MessageFlowOptimizer, CommunicationSecurityMonitor };
