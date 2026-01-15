/**
 * Agent Status Monitoring Service
 * Comprehensive monitoring and health tracking for all enterprise agents
 */

import EnterpriseDatabase from './EnterpriseDatabase';
import agentCommunicationBridge from './AgentCommunicationBridge';

class AgentStatusMonitoringService {
    constructor() {
        this.monitoringInterval = null;
        this.alertThresholds = {
            healthScore: 70,
            responseTime: 5000,
            errorRate: 5.0,
            inactiveTime: 300000 // 5 minutes
        };
        
        this.agentMetrics = new Map();
        this.healthHistory = new Map();
        this.alertHistory = [];
        this.isMonitoring = false;
        
        // Initialize monitoring
        this.startMonitoring();
        this.setupEventListeners();
    }

    /**
     * Start comprehensive agent monitoring
     */
    startMonitoring() {
        if (this.isMonitoring) return;
        
        this.isMonitoring = true;
        
        // Monitor agents every 30 seconds
        this.monitoringInterval = setInterval(() => {
            this.performHealthCheck();
        }, 30000);
        
        console.log('Agent Status Monitoring Service started');
    }

    /**
     * Stop monitoring
     */
    stopMonitoring() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
        }
        
        this.isMonitoring = false;
        console.log('Agent Status Monitoring Service stopped');
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Listen for agent updates
        window.addEventListener('agent-update', (event) => {
            this.handleAgentUpdate(event.detail);
        });

        // Listen for agent errors
        window.addEventListener('agent-error', (event) => {
            this.handleAgentError(event.detail);
        });

        // Listen for task completions
        window.addEventListener('task-completion', (event) => {
            this.handleTaskCompletion(event.detail);
        });
    }

    /**
     * Perform comprehensive health check on all agents
     */
    async performHealthCheck() {
        try {
            const agentRegistry = agentCommunicationBridge.getAgentRegistry();
            const currentTime = Date.now();
            
            for (const [agentId, agentData] of agentRegistry) {
                await this.checkAgentHealth(agentId, agentData, currentTime);
            }
            
            // Clean up old metrics
            this.cleanupOldMetrics();
            
            // Broadcast health summary
            this.broadcastHealthSummary();
            
        } catch (error) {
            console.error('Error during agent health check:', error);
        }
    }

    /**
     * Check individual agent health
     */
    async checkAgentHealth(agentId, agentData, currentTime) {
        const lastSeenTime = new Date(agentData.last_seen || 0).getTime();
        const timeSinceLastSeen = currentTime - lastSeenTime;
        
        // Get current metrics
        const currentMetrics = this.calculateAgentMetrics(agentId, agentData, timeSinceLastSeen);
        
        // Store metrics
        this.agentMetrics.set(agentId, currentMetrics);
        
        // Update health history
        this.updateHealthHistory(agentId, currentMetrics);
        
        // Check for alerts
        await this.checkAgentAlerts(agentId, currentMetrics, agentData);
        
        // Update database
        await this.updateAgentHealthRecord(agentId, currentMetrics);
    }

    /**
     * Calculate agent metrics
     */
    calculateAgentMetrics(agentId, agentData, timeSinceLastSeen) {
        const healthScore = this.calculateHealthScore(agentData, timeSinceLastSeen);
        const status = this.determineAgentStatus(agentData, healthScore, timeSinceLastSeen);
        
        return {
            agent_id: agentId,
            health_score: healthScore,
            status: status,
            last_seen: agentData.last_seen,
            time_since_last_seen: timeSinceLastSeen,
            response_time: agentData.performance_metrics?.response_time || null,
            error_rate: agentData.performance_metrics?.error_rate || 0,
            tasks_completed: agentData.performance_metrics?.tasks_completed || 0,
            current_task: agentData.current_task || null,
            department: agentData.department || 'unknown',
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Calculate agent health score (0-100)
     */
    calculateHealthScore(agentData, timeSinceLastSeen) {
        let score = 100;
        
        // Deduct points for inactivity
        if (timeSinceLastSeen > 60000) { // 1 minute
            score -= Math.min(30, (timeSinceLastSeen / 60000) * 5);
        }
        
        // Consider error status
        if (agentData.status === 'error') {
            score -= 40;
        } else if (agentData.status === 'warning') {
            score -= 20;
        } else if (agentData.status === 'maintenance') {
            score -= 10;
        }
        
        // Consider error rate
        const errorRate = agentData.performance_metrics?.error_rate || 0;
        if (errorRate > 0) {
            score -= Math.min(20, errorRate * 4);
        }
        
        // Consider response time
        const responseTime = agentData.performance_metrics?.response_time || 0;
        if (responseTime > 1000) {
            score -= Math.min(15, (responseTime / 1000) * 3);
        }
        
        // Consider recent errors
        if (agentData.last_error) {
            const errorAge = Date.now() - new Date(agentData.last_error.timestamp).getTime();
            if (errorAge < 300000) { // Last 5 minutes
                score -= agentData.last_error.severity === 'high' ? 25 : 15;
            }
        }
        
        return Math.max(0, Math.round(score));
    }

    /**
     * Determine agent status based on metrics
     */
    determineAgentStatus(agentData, healthScore, timeSinceLastSeen) {
        // Check for explicit error status
        if (agentData.status === 'error') return 'error';
        
        // Check for timeout
        if (timeSinceLastSeen > this.alertThresholds.inactiveTime) {
            return 'timeout';
        }
        
        // Check health score
        if (healthScore < 50) return 'critical';
        if (healthScore < 70) return 'warning';
        if (agentData.status === 'maintenance') return 'maintenance';
        
        return 'operational';
    }

    /**
     * Update health history for trending
     */
    updateHealthHistory(agentId, metrics) {
        if (!this.healthHistory.has(agentId)) {
            this.healthHistory.set(agentId, []);
        }
        
        const history = this.healthHistory.get(agentId);
        history.push({
            timestamp: metrics.timestamp,
            health_score: metrics.health_score,
            status: metrics.status
        });
        
        // Keep only last 24 hours of data (assuming 30-second intervals)
        if (history.length > 2880) {
            history.shift();
        }
    }

    /**
     * Check for alert conditions
     */
    async checkAgentAlerts(agentId, metrics, agentData) {
        const alerts = [];
        
        // Health score alert
        if (metrics.health_score < this.alertThresholds.healthScore) {
            alerts.push({
                type: 'health_score',
                severity: metrics.health_score < 50 ? 'critical' : 'warning',
                message: `Health score dropped to ${metrics.health_score}%`,
                threshold: this.alertThresholds.healthScore
            });
        }
        
        // Response time alert
        if (metrics.response_time && metrics.response_time > this.alertThresholds.responseTime) {
            alerts.push({
                type: 'response_time',
                severity: 'warning',
                message: `Response time increased to ${metrics.response_time}ms`,
                threshold: this.alertThresholds.responseTime
            });
        }
        
        // Error rate alert
        if (metrics.error_rate > this.alertThresholds.errorRate) {
            alerts.push({
                type: 'error_rate',
                severity: 'warning',
                message: `Error rate increased to ${metrics.error_rate}%`,
                threshold: this.alertThresholds.errorRate
            });
        }
        
        // Inactivity alert
        if (metrics.time_since_last_seen > this.alertThresholds.inactiveTime) {
            alerts.push({
                type: 'inactivity',
                severity: 'critical',
                message: `Agent inactive for ${Math.round(metrics.time_since_last_seen / 60000)} minutes`,
                threshold: this.alertThresholds.inactiveTime / 60000
            });
        }
        
        // Process alerts
        for (const alert of alerts) {
            await this.processAlert(agentId, alert, metrics);
        }
    }

    /**
     * Process and broadcast alerts
     */
    async processAlert(agentId, alert, metrics) {
        const alertRecord = {
            id: `${agentId}_${alert.type}_${Date.now()}`,
            agent_id: agentId,
            alert_type: alert.type,
            severity: alert.severity,
            message: alert.message,
            threshold: alert.threshold,
            current_value: this.getCurrentValue(alert.type, metrics),
            timestamp: new Date().toISOString(),
            acknowledged: false
        };
        
        // Store alert
        this.alertHistory.push(alertRecord);
        
        // Keep alert history manageable
        if (this.alertHistory.length > 1000) {
            this.alertHistory = this.alertHistory.slice(-1000);
        }
        
        // Broadcast alert
        this.broadcastAlert(alertRecord);
        
        // Log to database
        await this.logAlert(alertRecord);
    }

    /**
     * Get current value for alert type
     */
    getCurrentValue(alertType, metrics) {
        switch (alertType) {
            case 'health_score': return metrics.health_score;
            case 'response_time': return metrics.response_time;
            case 'error_rate': return metrics.error_rate;
            case 'inactivity': return Math.round(metrics.time_since_last_seen / 60000);
            default: return null;
        }
    }

    /**
     * Handle agent update events
     */
    handleAgentUpdate(detail) {
        const { agent_id, message_type, content } = detail;
        
        // Update metrics based on message type
        if (message_type === 'performance_metrics') {
            this.updatePerformanceMetrics(agent_id, content);
        }
    }

    /**
     * Handle agent error events
     */
    handleAgentError(detail) {
        const { agent_id, error_type, error_message, severity } = detail;
        
        // Update error metrics
        const currentMetrics = this.agentMetrics.get(agent_id);
        if (currentMetrics) {
            currentMetrics.recent_errors = (currentMetrics.recent_errors || 0) + 1;
            currentMetrics.last_error = {
                type: error_type,
                message: error_message,
                severity: severity,
                timestamp: new Date().toISOString()
            };
        }
    }

    /**
     * Handle task completion events
     */
    handleTaskCompletion(detail) {
        const { agent_id, success } = detail;
        
        const currentMetrics = this.agentMetrics.get(agent_id);
        if (currentMetrics) {
            currentMetrics.tasks_completed = (currentMetrics.tasks_completed || 0) + 1;
            if (!success) {
                currentMetrics.failed_tasks = (currentMetrics.failed_tasks || 0) + 1;
            }
        }
    }

    /**
     * Update performance metrics
     */
    updatePerformanceMetrics(agentId, metrics) {
        const currentMetrics = this.agentMetrics.get(agentId);
        if (currentMetrics) {
            currentMetrics.response_time = metrics.response_time;
            currentMetrics.error_rate = metrics.error_rate;
            currentMetrics.throughput = metrics.throughput;
            currentMetrics.memory_usage = metrics.memory_usage;
            currentMetrics.cpu_usage = metrics.cpu_usage;
        }
    }

    /**
     * Update agent health record in database
     */
    async updateAgentHealthRecord(agentId, metrics) {
        try {
            await EnterpriseDatabase.updateAgentHealthRecord(agentId, metrics);
        } catch (error) {
            console.error(`Failed to update health record for ${agentId}:`, error);
        }
    }

    /**
     * Log alert to database
     */
    async logAlert(alertRecord) {
        try {
            await EnterpriseDatabase.logAgentAlert(alertRecord);
        } catch (error) {
            console.error('Failed to log alert:', error);
        }
    }

    /**
     * Broadcast alert to dashboard
     */
    broadcastAlert(alertRecord) {
        const event = new CustomEvent('agent-alert', {
            detail: alertRecord
        });
        window.dispatchEvent(event);
    }

    /**
     * Broadcast health summary
     */
    broadcastHealthSummary() {
        const summary = this.generateHealthSummary();
        
        const event = new CustomEvent('health-summary', {
            detail: summary
        });
        window.dispatchEvent(event);
    }

    /**
     * Generate health summary
     */
    generateHealthSummary() {
        const metrics = Array.from(this.agentMetrics.values());
        
        const summary = {
            total_agents: metrics.length,
            operational: metrics.filter(m => m.status === 'operational').length,
            warning: metrics.filter(m => m.status === 'warning').length,
            critical: metrics.filter(m => m.status === 'critical').length,
            error: metrics.filter(m => m.status === 'error').length,
            timeout: metrics.filter(m => m.status === 'timeout').length,
            maintenance: metrics.filter(m => m.status === 'maintenance').length,
            average_health_score: metrics.reduce((sum, m) => sum + m.health_score, 0) / metrics.length || 0,
            active_alerts: this.alertHistory.filter(a => !a.acknowledged).length,
            timestamp: new Date().toISOString()
        };
        
        return summary;
    }

    /**
     * Clean up old metrics
     */
    cleanupOldMetrics() {
        const oneHourAgo = Date.now() - (60 * 60 * 1000);
        
        // Clean up old alert history
        this.alertHistory = this.alertHistory.filter(alert => {
            return new Date(alert.timestamp).getTime() > oneHourAgo;
        });
    }

    /**
     * Get agent metrics
     */
    getAgentMetrics(agentId) {
        return this.agentMetrics.get(agentId) || null;
    }

    /**
     * Get all agent metrics
     */
    getAllAgentMetrics() {
        return new Map(this.agentMetrics);
    }

    /**
     * Get agent health history
     */
    getAgentHealthHistory(agentId, hours = 1) {
        const history = this.healthHistory.get(agentId) || [];
        const cutoff = Date.now() - (hours * 60 * 60 * 1000);
        
        return history.filter(entry => {
            return new Date(entry.timestamp).getTime() > cutoff;
        });
    }

    /**
     * Get active alerts
     */
    getActiveAlerts() {
        return this.alertHistory.filter(alert => !alert.acknowledged);
    }

    /**
     * Acknowledge alert
     */
    acknowledgeAlert(alertId) {
        const alert = this.alertHistory.find(a => a.id === alertId);
        if (alert) {
            alert.acknowledged = true;
            alert.acknowledged_at = new Date().toISOString();
        }
    }

    /**
     * Get monitoring status
     */
    getMonitoringStatus() {
        return {
            isMonitoring: this.isMonitoring,
            monitoredAgents: this.agentMetrics.size,
            activeAlerts: this.getActiveAlerts().length,
            alertThresholds: this.alertThresholds,
            lastCheck: new Date().toISOString()
        };
    }

    /**
     * Update alert thresholds
     */
    updateAlertThresholds(newThresholds) {
        this.alertThresholds = { ...this.alertThresholds, ...newThresholds };
    }

    /**
     * Get current state from backend API
     * This method fetches real-time agent data from the enterprise backend
     */
    async getCurrentState() {
        try {
            const response = await fetch('http://localhost:5001/api/enterprise/agent-health');
            if (!response.ok) {
                throw new Error(`Backend API error: ${response.status}`);
            }
            
            const backendData = await response.json();
            
            // Transform backend data to expected format
            const agentMetrics = {};
            const alerts = [];
            
            if (backendData.agents) {
                Object.entries(backendData.agents).forEach(([agentId, agentData]) => {
                    agentMetrics[agentId] = {
                        id: agentId,
                        name: agentData.name || agentId,
                        status: agentData.status || 'unknown',
                        health_score: agentData.health_score || 0,
                        last_seen: agentData.last_activity || new Date().toISOString(),
                        department: agentData.department || 'unknown',
                        avg_response_time: agentData.avg_response_time || '0ms',
                        error_rate: agentData.error_rate || 0,
                        tasks_completed: agentData.tasks_completed || 0,
                        uptime: agentData.uptime || '0m'
                    };
                    
                    // Generate alerts for unhealthy agents
                    if (agentData.health_score < 70) {
                        alerts.push({
                            id: `health_${agentId}_${Date.now()}`,
                            type: 'warning',
                            message: `Agent ${agentData.name || agentId} health score low: ${agentData.health_score}%`,
                            agent_id: agentId,
                            timestamp: new Date().toISOString(),
                            severity: agentData.health_score < 50 ? 'critical' : 'warning'
                        });
                    }
                });
            }
            
            return {
                agents: agentMetrics,
                alerts: alerts,
                summary: {
                    total_agents: Object.keys(agentMetrics).length,
                    healthy_agents: Object.values(agentMetrics).filter(a => a.health_score >= 70).length,
                    warning_agents: Object.values(agentMetrics).filter(a => a.health_score < 70 && a.health_score >= 50).length,
                    critical_agents: Object.values(agentMetrics).filter(a => a.health_score < 50).length,
                    avg_health_score: Object.values(agentMetrics).reduce((sum, a) => sum + a.health_score, 0) / Object.keys(agentMetrics).length || 0
                },
                timestamp: new Date().toISOString()
            };
            
        } catch (error) {
            console.error('❌ Failed to fetch agent status from backend:', error);
            
            // Return fallback data with error indication
            return {
                agents: {},
                alerts: [{
                    id: `backend_error_${Date.now()}`,
                    type: 'error',
                    message: `Failed to connect to backend API: ${error.message}`,
                    timestamp: new Date().toISOString(),
                    severity: 'critical'
                }],
                summary: {
                    total_agents: 0,
                    healthy_agents: 0,
                    warning_agents: 0,
                    critical_agents: 0,
                    avg_health_score: 0
                },
                timestamp: new Date().toISOString(),
                error: error.message
            };
        }
    }

    /**
     * Cleanup resources
     */
    cleanup() {
        this.stopMonitoring();
        this.agentMetrics.clear();
        this.healthHistory.clear();
        this.alertHistory = [];
    }
}

// Export the class directly for instantiation
export default AgentStatusMonitoringService;
