/**
 * Department Activities Monitoring Service
 * Real-time monitoring and analytics for department operations across the enterprise
 */

import EnterpriseDatabase from './EnterpriseDatabase';
import webSocketService, { WEBSOCKET_CHANNELS, DATA_TYPES } from './WebSocketService';

class DepartmentActivitiesMonitoringService {
    constructor() {
        this.isMonitoring = false;
        this.monitoringInterval = null;
        this.departments = new Map();
        this.activityHistory = new Map();
        this.performanceMetrics = new Map();
        this.alertThresholds = {
            maxInactivityTime: 3600000, // 1 hour
            minCompletionRate: 75, // 75%
            maxErrorRate: 10, // 10%
            criticalPriorityThreshold: 8
        };
        
        this.departmentList = [
            'strategy', 'marketing', 'finance', 'operations',
            'business_intelligence', 'communication', 'legal', 'automation'
        ];
        
        this.activityTypes = [
            'task_execution', 'research', 'analysis', 'communication',
            'planning', 'optimization', 'reporting', 'coordination'
        ];
        
        this.initializeDepartments();
        this.startMonitoring();
        this.setupEventListeners();
    }

    /**
     * Initialize department tracking structures
     */
    initializeDepartments() {
        for (const dept of this.departmentList) {
            this.departments.set(dept, {
                name: dept,
                status: 'active',
                activeAgents: 0,
                completedTasks: 0,
                pendingTasks: 0,
                errorCount: 0,
                lastActivity: null,
                currentPriority: 'normal',
                performanceScore: 100,
                efficiency: 0,
                resourceUtilization: 0,
                collaborationIndex: 0
            });
            
            this.activityHistory.set(dept, []);
            this.performanceMetrics.set(dept, {
                hourly: [],
                daily: [],
                weekly: []
            });
        }
    }

    /**
     * Start comprehensive monitoring
     */
    startMonitoring() {
        if (this.isMonitoring) return;
        
        this.isMonitoring = true;
        
        // Monitor every 60 seconds for detailed analysis
        this.monitoringInterval = setInterval(async () => {
            await this.performDepartmentAnalysis();
        }, 60000);
        
        // Initial load
        this.loadDepartmentActivities();
        
        console.log('Department Activities Monitoring Service started');
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
        console.log('Department Activities Monitoring Service stopped');
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Listen for agent updates that affect departments
        window.addEventListener('agent-update', (event) => {
            this.handleAgentUpdate(event.detail);
        });

        // Listen for task completions
        window.addEventListener('task-completion', (event) => {
            this.handleTaskCompletion(event.detail);
        });

        // Listen for workflow executions
        window.addEventListener('workflow-execution', (event) => {
            this.handleWorkflowExecution(event.detail);
        });
    }

    /**
     * Load department activities from database
     */
    async loadDepartmentActivities() {
        try {
            const activities = await EnterpriseDatabase.getDepartmentActivities();
            
            for (const activity of activities) {
                await this.processActivity(activity);
            }
            
            console.log(`Loaded ${activities.length} department activities`);
        } catch (error) {
            console.error('Failed to load department activities:', error);
        }
    }

    /**
     * Process individual activity record
     */
    async processActivity(activity) {
        const department = activity.department || 'unknown';
        
        if (!this.departments.has(department)) {
            this.initializeDepartment(department);
        }
        
        const deptData = this.departments.get(department);
        const activityTime = new Date(activity.created_at || activity.timestamp);
        
        // Update department status
        deptData.lastActivity = activityTime.toISOString();
        
        // Analyze activity type and impact
        const activityAnalysis = this.analyzeActivity(activity);
        
        // Update metrics
        this.updateDepartmentMetrics(department, activityAnalysis);
        
        // Store in history
        this.addActivityToHistory(department, {
            ...activity,
            analysis: activityAnalysis,
            processed_at: new Date().toISOString()
        });
        
        // Check for alerts
        await this.checkDepartmentAlerts(department, activityAnalysis);
    }

    /**
     * Analyze activity for performance metrics
     */
    analyzeActivity(activity) {
        const analysis = {
            type: this.classifyActivityType(activity),
            impact: this.calculateActivityImpact(activity),
            complexity: this.assessActivityComplexity(activity),
            collaboration: this.assessCollaboration(activity),
            efficiency: this.calculateEfficiency(activity),
            quality: this.assessQuality(activity),
            timestamp: new Date().toISOString()
        };
        
        return analysis;
    }

    /**
     * Classify activity type
     */
    classifyActivityType(activity) {
        const description = (activity.description || '').toLowerCase();
        const operationType = (activity.operation_type || '').toLowerCase();
        
        // Pattern matching for activity classification
        if (description.includes('research') || description.includes('analysis')) {
            return 'research_analysis';
        } else if (description.includes('communication') || description.includes('message')) {
            return 'communication';
        } else if (description.includes('planning') || description.includes('strategy')) {
            return 'planning';
        } else if (description.includes('optimization') || description.includes('improve')) {
            return 'optimization';
        } else if (description.includes('report') || description.includes('documentation')) {
            return 'reporting';
        } else if (operationType.includes('workflow') || operationType.includes('coordination')) {
            return 'coordination';
        } else if (operationType.includes('task') || operationType.includes('execution')) {
            return 'task_execution';
        }
        
        return 'general';
    }

    /**
     * Calculate activity impact on business objectives
     */
    calculateActivityImpact(activity) {
        const priority = activity.priority || 5;
        const dataSize = activity.data ? JSON.stringify(activity.data).length : 0;
        
        // Higher priority and more comprehensive data indicates higher impact
        let impact = priority * 10;
        
        if (dataSize > 1000) impact += 20;
        if (dataSize > 5000) impact += 30;
        
        // Normalize to 0-100 scale
        return Math.min(100, Math.max(0, impact));
    }

    /**
     * Assess activity complexity
     */
    assessActivityComplexity(activity) {
        let complexity = 20; // Base complexity
        
        const description = activity.description || '';
        const data = activity.data || {};
        
        // Text analysis for complexity indicators
        const complexityKeywords = ['analysis', 'research', 'optimization', 'coordination', 'integration'];
        complexity += complexityKeywords.filter(keyword => 
            description.toLowerCase().includes(keyword)
        ).length * 15;
        
        // Data structure complexity
        if (typeof data === 'object' && data !== null) {
            complexity += Object.keys(data).length * 5;
        }
        
        return Math.min(100, complexity);
    }

    /**
     * Assess collaboration level
     */
    assessCollaboration(activity) {
        const description = (activity.description || '').toLowerCase();
        const data = activity.data || {};
        
        let collaboration = 0;
        
        // Look for collaboration indicators
        if (description.includes('team') || description.includes('department')) collaboration += 25;
        if (description.includes('coordination') || description.includes('communication')) collaboration += 30;
        if (description.includes('cross-department') || description.includes('multi-agent')) collaboration += 45;
        
        // Check data for collaboration indicators
        if (data.agents && Array.isArray(data.agents) && data.agents.length > 1) {
            collaboration += data.agents.length * 10;
        }
        
        return Math.min(100, collaboration);
    }

    /**
     * Calculate efficiency score
     */
    calculateEfficiency(activity) {
        const createdAt = new Date(activity.created_at || Date.now());
        const now = new Date();
        const ageHours = (now - createdAt) / (1000 * 60 * 60);
        
        // More recent activities score higher for efficiency
        let efficiency = Math.max(20, 100 - (ageHours * 2));
        
        // Higher priority indicates more efficient resource allocation
        const priority = activity.priority || 5;
        efficiency += priority * 5;
        
        return Math.min(100, Math.max(0, efficiency));
    }

    /**
     * Assess quality indicators
     */
    assessQuality(activity) {
        let quality = 70; // Base quality score
        
        const description = activity.description || '';
        const data = activity.data || {};
        
        // Quality indicators
        if (description.length > 50) quality += 10; // Detailed description
        if (Object.keys(data).length > 3) quality += 15; // Rich data
        if (activity.priority >= 8) quality += 15; // High priority execution
        
        return Math.min(100, quality);
    }

    /**
     * Update department metrics
     */
    updateDepartmentMetrics(department, analysis) {
        const deptData = this.departments.get(department);
        if (!deptData) return;
        
        // Update counters
        deptData.completedTasks += 1;
        
        // Update performance score (weighted average)
        const newScore = (analysis.impact + analysis.efficiency + analysis.quality) / 3;
        deptData.performanceScore = (deptData.performanceScore * 0.9) + (newScore * 0.1);
        
        // Update efficiency
        deptData.efficiency = (deptData.efficiency * 0.8) + (analysis.efficiency * 0.2);
        
        // Update collaboration index
        deptData.collaborationIndex = (deptData.collaborationIndex * 0.8) + (analysis.collaboration * 0.2);
        
        // Update resource utilization based on activity frequency
        this.updateResourceUtilization(department);
    }

    /**
     * Update resource utilization metrics
     */
    updateResourceUtilization(department) {
        const history = this.activityHistory.get(department) || [];
        const recentActivities = history.filter(activity => {
            const activityTime = new Date(activity.processed_at);
            const oneHourAgo = new Date(Date.now() - 3600000);
            return activityTime > oneHourAgo;
        });
        
        const deptData = this.departments.get(department);
        // Calculate utilization based on recent activity frequency
        deptData.resourceUtilization = Math.min(100, recentActivities.length * 8);
    }

    /**
     * Add activity to department history
     */
    addActivityToHistory(department, activity) {
        const history = this.activityHistory.get(department) || [];
        history.push(activity);
        
        // Keep last 1000 activities per department
        if (history.length > 1000) {
            history.shift();
        }
        
        this.activityHistory.set(department, history);
    }

    /**
     * Perform comprehensive department analysis
     */
    async performDepartmentAnalysis() {
        try {
            for (const [department, deptData] of this.departments) {
                await this.analyzeDepartmentPerformance(department, deptData);
                await this.updatePerformanceMetrics(department);
                await this.checkDepartmentHealth(department);
            }
            
            // Broadcast comprehensive update
            this.broadcastDepartmentSummary();
            
        } catch (error) {
            console.error('Error during department analysis:', error);
        }
    }

    /**
     * Analyze individual department performance
     */
    async analyzeDepartmentPerformance(department, deptData) {
        const history = this.activityHistory.get(department) || [];
        const recentHistory = this.getRecentHistory(department, 3600000); // Last hour
        
        // Calculate activity trends
        const trends = this.calculateActivityTrends(recentHistory);
        
        // Update status based on activity and trends
        deptData.status = this.determineDepartmentStatus(deptData, trends);
        deptData.currentPriority = this.calculateCurrentPriority(recentHistory);
        
        // Update active agents count (simulated based on activity)
        deptData.activeAgents = this.estimateActiveAgents(recentHistory);
        
        // Calculate pending tasks (simulated based on activity patterns)
        deptData.pendingTasks = this.estimatePendingTasks(department, trends);
    }

    /**
     * Get recent activity history
     */
    getRecentHistory(department, timeWindow) {
        const history = this.activityHistory.get(department) || [];
        const cutoff = new Date(Date.now() - timeWindow);
        
        return history.filter(activity => {
            const activityTime = new Date(activity.processed_at);
            return activityTime > cutoff;
        });
    }

    /**
     * Calculate activity trends
     */
    calculateActivityTrends(recentHistory) {
        const now = Date.now();
        const intervals = [
            { name: 'last_15_min', duration: 900000 },
            { name: 'last_30_min', duration: 1800000 },
            { name: 'last_hour', duration: 3600000 }
        ];
        
        const trends = {};
        
        for (const interval of intervals) {
            const cutoff = new Date(now - interval.duration);
            const activities = recentHistory.filter(activity => 
                new Date(activity.processed_at) > cutoff
            );
            
            trends[interval.name] = {
                count: activities.length,
                avg_impact: activities.reduce((sum, a) => sum + (a.analysis?.impact || 0), 0) / Math.max(1, activities.length),
                avg_efficiency: activities.reduce((sum, a) => sum + (a.analysis?.efficiency || 0), 0) / Math.max(1, activities.length)
            };
        }
        
        return trends;
    }

    /**
     * Determine department status
     */
    determineDepartmentStatus(deptData, trends) {
        const lastActivityTime = deptData.lastActivity ? new Date(deptData.lastActivity) : null;
        const timeSinceLastActivity = lastActivityTime ? Date.now() - lastActivityTime.getTime() : Infinity;
        
        // Check for inactivity
        if (timeSinceLastActivity > this.alertThresholds.maxInactivityTime) {
            return 'inactive';
        }
        
        // Check performance score
        if (deptData.performanceScore < 50) {
            return 'critical';
        } else if (deptData.performanceScore < 70) {
            return 'warning';
        }
        
        // Check recent activity trends
        if (trends.last_15_min.count === 0 && trends.last_30_min.count === 0) {
            return 'idle';
        }
        
        // High activity indicates active status
        if (trends.last_15_min.count > 5) {
            return 'very_active';
        } else if (trends.last_30_min.count > 3) {
            return 'active';
        }
        
        return 'normal';
    }

    /**
     * Calculate current priority level
     */
    calculateCurrentPriority(recentHistory) {
        if (recentHistory.length === 0) return 'low';
        
        const avgPriority = recentHistory.reduce((sum, activity) => 
            sum + (activity.priority || 5), 0
        ) / recentHistory.length;
        
        if (avgPriority >= 8) return 'critical';
        if (avgPriority >= 6) return 'high';
        if (avgPriority >= 4) return 'medium';
        return 'low';
    }

    /**
     * Estimate active agents based on activity patterns
     */
    estimateActiveAgents(recentHistory) {
        // Estimate based on activity volume and diversity
        const activityCount = recentHistory.length;
        const uniqueTypes = new Set(recentHistory.map(a => a.analysis?.type)).size;
        
        return Math.min(6, Math.max(1, Math.floor(activityCount / 3) + uniqueTypes));
    }

    /**
     * Estimate pending tasks
     */
    estimatePendingTasks(department, trends) {
        // Simulate pending tasks based on department activity patterns
        const baseLoad = {
            'strategy': 8,
            'marketing': 12,
            'finance': 6,
            'operations': 15,
            'business_intelligence': 10,
            'communication': 8,
            'legal': 4,
            'automation': 7
        };
        
        const base = baseLoad[department] || 5;
        const activityModifier = trends.last_hour.count > 5 ? -2 : 
                               trends.last_hour.count < 2 ? 3 : 0;
        
        return Math.max(0, base + activityModifier + Math.floor(Math.random() * 3));
    }

    /**
     * Update performance metrics history
     */
    async updatePerformanceMetrics(department) {
        const deptData = this.departments.get(department);
        const metrics = this.performanceMetrics.get(department);
        
        const currentMetric = {
            timestamp: new Date().toISOString(),
            performance_score: deptData.performanceScore,
            efficiency: deptData.efficiency,
            resource_utilization: deptData.resourceUtilization,
            collaboration_index: deptData.collaborationIndex,
            completed_tasks: deptData.completedTasks,
            active_agents: deptData.activeAgents
        };
        
        // Add to hourly metrics
        metrics.hourly.push(currentMetric);
        if (metrics.hourly.length > 24) metrics.hourly.shift(); // Keep 24 hours
        
        // Aggregate daily metrics (every 24 entries)
        if (metrics.hourly.length % 24 === 0) {
            const dailyMetric = this.aggregateMetrics(metrics.hourly);
            metrics.daily.push(dailyMetric);
            if (metrics.daily.length > 30) metrics.daily.shift(); // Keep 30 days
        }
        
        // Aggregate weekly metrics (every 7 daily entries)
        if (metrics.daily.length % 7 === 0 && metrics.daily.length > 0) {
            const weeklyMetric = this.aggregateMetrics(metrics.daily.slice(-7));
            metrics.weekly.push(weeklyMetric);
            if (metrics.weekly.length > 12) metrics.weekly.shift(); // Keep 12 weeks
        }
    }

    /**
     * Aggregate metrics for time periods
     */
    aggregateMetrics(metricsArray) {
        const count = metricsArray.length;
        if (count === 0) return null;
        
        return {
            timestamp: new Date().toISOString(),
            avg_performance_score: metricsArray.reduce((sum, m) => sum + m.performance_score, 0) / count,
            avg_efficiency: metricsArray.reduce((sum, m) => sum + m.efficiency, 0) / count,
            avg_resource_utilization: metricsArray.reduce((sum, m) => sum + m.resource_utilization, 0) / count,
            avg_collaboration_index: metricsArray.reduce((sum, m) => sum + m.collaboration_index, 0) / count,
            total_completed_tasks: Math.max(...metricsArray.map(m => m.completed_tasks)),
            max_active_agents: Math.max(...metricsArray.map(m => m.active_agents))
        };
    }

    /**
     * Check department health and generate alerts
     */
    async checkDepartmentHealth(department) {
        const deptData = this.departments.get(department);
        const alerts = [];
        
        // Performance alerts
        if (deptData.performanceScore < 50) {
            alerts.push({
                type: 'performance_critical',
                severity: 'critical',
                message: `${department} department performance critically low: ${deptData.performanceScore.toFixed(1)}%`
            });
        } else if (deptData.performanceScore < 70) {
            alerts.push({
                type: 'performance_warning',
                severity: 'warning',
                message: `${department} department performance below threshold: ${deptData.performanceScore.toFixed(1)}%`
            });
        }
        
        // Inactivity alerts
        if (deptData.status === 'inactive') {
            alerts.push({
                type: 'department_inactive',
                severity: 'critical',
                message: `${department} department has been inactive for over 1 hour`
            });
        }
        
        // Resource utilization alerts
        if (deptData.resourceUtilization > 90) {
            alerts.push({
                type: 'resource_overload',
                severity: 'warning',
                message: `${department} department resource utilization at ${deptData.resourceUtilization.toFixed(1)}%`
            });
        }
        
        // Process alerts
        for (const alert of alerts) {
            await this.processAlert(department, alert);
        }
    }

    /**
     * Process and broadcast alerts
     */
    async processAlert(department, alert) {
        const alertRecord = {
            id: `dept_${department}_${alert.type}_${Date.now()}`,
            department: department,
            alert_type: alert.type,
            severity: alert.severity,
            message: alert.message,
            timestamp: new Date().toISOString(),
            acknowledged: false
        };
        
        // Broadcast alert
        const event = new CustomEvent('department-alert', {
            detail: alertRecord
        });
        window.dispatchEvent(event);
        
        // Log to database
        try {
            await EnterpriseDatabase.logDepartmentAlert(alertRecord);
        } catch (error) {
            console.error('Failed to log department alert:', error);
        }
    }

    /**
     * Check department alerts based on thresholds
     */
    async checkDepartmentAlerts(department, analysis) {
        // Implementation would check various thresholds and generate alerts
        // This integrates with the existing alert system
    }

    /**
     * Handle agent update events
     */
    handleAgentUpdate(detail) {
        const { agent_id, department, message_type, content } = detail;
        
        if (department && this.departments.has(department)) {
            const deptData = this.departments.get(department);
            deptData.lastActivity = new Date().toISOString();
            
            // Update based on message type
            if (message_type === 'task_completion') {
                deptData.completedTasks += 1;
            } else if (message_type === 'error_report') {
                deptData.errorCount += 1;
            }
        }
    }

    /**
     * Handle task completion events
     */
    handleTaskCompletion(detail) {
        const { agent_id, department, success } = detail;
        
        if (department && this.departments.has(department)) {
            const deptData = this.departments.get(department);
            deptData.completedTasks += 1;
            
            if (!success) {
                deptData.errorCount += 1;
            }
        }
    }

    /**
     * Handle workflow execution events
     */
    handleWorkflowExecution(detail) {
        const { departments, status } = detail;
        
        if (departments && Array.isArray(departments)) {
            for (const dept of departments) {
                if (this.departments.has(dept)) {
                    const deptData = this.departments.get(dept);
                    deptData.lastActivity = new Date().toISOString();
                    
                    if (status === 'completed') {
                        deptData.completedTasks += 1;
                    }
                }
            }
        }
    }

    /**
     * Broadcast department summary
     */
    broadcastDepartmentSummary() {
        const summary = {
            departments: Object.fromEntries(this.departments),
            totalDepartments: this.departments.size,
            activeDepartments: Array.from(this.departments.values()).filter(d => d.status === 'active' || d.status === 'very_active').length,
            criticalDepartments: Array.from(this.departments.values()).filter(d => d.status === 'critical').length,
            averagePerformance: Array.from(this.departments.values()).reduce((sum, d) => sum + d.performanceScore, 0) / this.departments.size,
            totalCompletedTasks: Array.from(this.departments.values()).reduce((sum, d) => sum + d.completedTasks, 0),
            totalActiveAgents: Array.from(this.departments.values()).reduce((sum, d) => sum + d.activeAgents, 0),
            timestamp: new Date().toISOString()
        };
        
        const event = new CustomEvent('department-summary', {
            detail: summary
        });
        window.dispatchEvent(event);
    }

    /**
     * Initialize new department
     */
    initializeDepartment(department) {
        this.departments.set(department, {
            name: department,
            status: 'active',
            activeAgents: 0,
            completedTasks: 0,
            pendingTasks: 0,
            errorCount: 0,
            lastActivity: null,
            currentPriority: 'normal',
            performanceScore: 100,
            efficiency: 0,
            resourceUtilization: 0,
            collaborationIndex: 0
        });
        
        this.activityHistory.set(department, []);
        this.performanceMetrics.set(department, {
            hourly: [],
            daily: [],
            weekly: []
        });
    }

    /**
     * Get department data
     */
    getDepartmentData(department) {
        return this.departments.get(department) || null;
    }

    /**
     * Get all departments data
     */
    getAllDepartments() {
        return new Map(this.departments);
    }

    /**
     * Get department activity history
     */
    getDepartmentHistory(department, limit = 100) {
        const history = this.activityHistory.get(department) || [];
        return history.slice(-limit);
    }

    /**
     * Get department performance metrics
     */
    getDepartmentMetrics(department, timeframe = 'hourly') {
        const metrics = this.performanceMetrics.get(department);
        return metrics ? metrics[timeframe] || [] : [];
    }

    /**
     * Get monitoring status
     */
    getMonitoringStatus() {
        return {
            isMonitoring: this.isMonitoring,
            totalDepartments: this.departments.size,
            activeDepartments: Array.from(this.departments.values()).filter(d => 
                d.status === 'active' || d.status === 'very_active'
            ).length,
            alertThresholds: this.alertThresholds,
            lastAnalysis: new Date().toISOString()
        };
    }

    /**
     * Update alert thresholds
     */
    updateAlertThresholds(newThresholds) {
        this.alertThresholds = { ...this.alertThresholds, ...newThresholds };
    }

    /**
     * Cleanup resources
     */
    cleanup() {
        this.stopMonitoring();
        this.departments.clear();
        this.activityHistory.clear();
        this.performanceMetrics.clear();
    }
}

// Create singleton instance
const departmentActivitiesMonitoringService = new DepartmentActivitiesMonitoringService();

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    departmentActivitiesMonitoringService.cleanup();
});

export default departmentActivitiesMonitoringService;
