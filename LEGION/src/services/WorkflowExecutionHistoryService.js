/**
 * Workflow Execution History Service
 * Comprehensive tracking and analysis of enterprise workflow executions
 */

import EnterpriseDatabase from './EnterpriseDatabase';
import webSocketService, { WEBSOCKET_CHANNELS, DATA_TYPES } from './WebSocketService';

class WorkflowExecutionHistoryService {
    constructor() {
        this.workflowHistory = new Map();
        this.executionMetrics = new Map();
        this.performanceAnalytics = new Map();
        this.workflowTemplates = new Map();
        this.executionAlerts = [];
        this.isTracking = false;
        this.trackingInterval = null;
        
        // Performance thresholds
        this.performanceThresholds = {
            maxExecutionTime: 300000, // 5 minutes
            minSuccessRate: 90, // 90%
            maxFailureRate: 10, // 10%
            maxQueueTime: 60000, // 1 minute
            maxRetryAttempts: 3
        };
        
        // Workflow categories
        this.workflowCategories = [
            'business_process',
            'data_analysis',
            'communication',
            'research',
            'optimization',
            'reporting',
            'coordination',
            'automation'
        ];
        
        this.initializeService();
        this.startTracking();
    }

    /**
     * Initialize workflow tracking service
     */
    async initializeService() {
        try {
            // Load existing workflow executions
            await this.loadWorkflowHistory();
            
            // Initialize workflow templates
            await this.initializeWorkflowTemplates();
            
            // Calculate baseline metrics
            await this.calculateBaselineMetrics();
            
            // Setup event listeners
            this.setupEventListeners();
            
            console.log('Workflow Execution History Service initialized');
        } catch (error) {
            console.error('Failed to initialize workflow service:', error);
        }
    }

    /**
     * Start workflow tracking
     */
    startTracking() {
        if (this.isTracking) return;
        
        this.isTracking = true;
        
        // Track workflow metrics every 2 minutes
        this.trackingInterval = setInterval(async () => {
            await this.updateWorkflowMetrics();
        }, 120000);
        
        // Initial metrics update
        this.updateWorkflowMetrics();
        
        console.log('Workflow execution tracking started');
    }

    /**
     * Stop tracking
     */
    stopTracking() {
        if (this.trackingInterval) {
            clearInterval(this.trackingInterval);
            this.trackingInterval = null;
        }
        
        this.isTracking = false;
        console.log('Workflow execution tracking stopped');
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Listen for workflow execution events
        window.addEventListener('workflow-execution', (event) => {
            this.handleWorkflowExecution(event.detail);
        });

        // Listen for workflow status updates
        window.addEventListener('workflow-status-update', (event) => {
            this.handleWorkflowStatusUpdate(event.detail);
        });

        // Listen for workflow completion events
        window.addEventListener('workflow-completion', (event) => {
            this.handleWorkflowCompletion(event.detail);
        });
    }

    /**
     * Load workflow history from database
     */
    async loadWorkflowHistory() {
        try {
            // Load from enterprise database
            const enterpriseWorkflows = await EnterpriseDatabase.getWorkflowExecutions();
            
            for (const workflow of enterpriseWorkflows) {
                await this.processWorkflowRecord(workflow, 'enterprise');
            }
            
            // Load from legion database (if available)
            try {
                const legionWorkflows = await this.loadLegionWorkflows();
                for (const workflow of legionWorkflows) {
                    await this.processWorkflowRecord(workflow, 'legion');
                }
            } catch (error) {
                console.warn('Could not load legion workflows:', error);
            }
            
            console.log(`Loaded ${this.workflowHistory.size} workflow executions`);
        } catch (error) {
            console.error('Failed to load workflow history:', error);
        }
    }

    /**
     * Load workflows from legion database
     */
    async loadLegionWorkflows() {
        // This would connect to legion database in production
        // For now, we'll simulate some workflow data
        return [];
    }

    /**
     * Process individual workflow record
     */
    async processWorkflowRecord(workflow, source) {
        const workflowId = workflow.id || workflow.workflow_id || `${source}_${Date.now()}`;
        
        const processedWorkflow = {
            id: workflowId,
            name: workflow.name || workflow.workflow_name || 'Unknown Workflow',
            type: workflow.type || workflow.workflow_type || 'general',
            category: this.categorizeWorkflow(workflow),
            source: source,
            status: workflow.status || 'unknown',
            started_at: workflow.started_at || workflow.created_at,
            completed_at: workflow.completed_at || workflow.finished_at,
            duration: this.calculateDuration(workflow),
            success: this.determineSuccess(workflow),
            error_message: workflow.error_message || workflow.error,
            participants: this.extractParticipants(workflow),
            departments: this.extractDepartments(workflow),
            priority: workflow.priority || 5,
            complexity: this.assessComplexity(workflow),
            efficiency_score: 0, // Will be calculated
            quality_score: 0, // Will be calculated
            business_impact: this.assessBusinessImpact(workflow),
            resource_usage: this.assessResourceUsage(workflow),
            metadata: workflow.data || workflow.metadata || {},
            created_at: workflow.created_at || new Date().toISOString(),
            last_updated: new Date().toISOString()
        };
        
        // Calculate derived metrics
        processedWorkflow.efficiency_score = this.calculateEfficiencyScore(processedWorkflow);
        processedWorkflow.quality_score = this.calculateQualityScore(processedWorkflow);
        
        this.workflowHistory.set(workflowId, processedWorkflow);
        
        // Update execution metrics
        this.updateExecutionMetrics(processedWorkflow);
    }

    /**
     * Categorize workflow based on content
     */
    categorizeWorkflow(workflow) {
        const name = (workflow.name || workflow.workflow_name || '').toLowerCase();
        const type = (workflow.type || workflow.workflow_type || '').toLowerCase();
        const description = (workflow.description || '').toLowerCase();
        
        const content = `${name} ${type} ${description}`;
        
        if (content.includes('research') || content.includes('analysis')) {
            return 'research';
        } else if (content.includes('communication') || content.includes('message')) {
            return 'communication';
        } else if (content.includes('business') || content.includes('process')) {
            return 'business_process';
        } else if (content.includes('data') || content.includes('analytics')) {
            return 'data_analysis';
        } else if (content.includes('report') || content.includes('documentation')) {
            return 'reporting';
        } else if (content.includes('optimization') || content.includes('improve')) {
            return 'optimization';
        } else if (content.includes('coordination') || content.includes('orchestration')) {
            return 'coordination';
        } else if (content.includes('automation') || content.includes('automated')) {
            return 'automation';
        }
        
        return 'general';
    }

    /**
     * Calculate workflow duration
     */
    calculateDuration(workflow) {
        const startTime = workflow.started_at || workflow.created_at;
        const endTime = workflow.completed_at || workflow.finished_at;
        
        if (!startTime) return null;
        if (!endTime && workflow.status !== 'completed') return null;
        
        const start = new Date(startTime);
        const end = endTime ? new Date(endTime) : new Date();
        
        return Math.max(0, end.getTime() - start.getTime());
    }

    /**
     * Determine workflow success
     */
    determineSuccess(workflow) {
        const status = (workflow.status || '').toLowerCase();
        
        if (status === 'completed' || status === 'success' || status === 'finished') {
            return !workflow.error_message && !workflow.error;
        }
        
        return status !== 'failed' && status !== 'error' && !workflow.error_message;
    }

    /**
     * Extract workflow participants
     */
    extractParticipants(workflow) {
        const participants = [];
        
        // Extract from metadata
        if (workflow.data || workflow.metadata) {
            const data = workflow.data || workflow.metadata;
            if (data.agents) {
                participants.push(...data.agents);
            }
            if (data.participants) {
                participants.push(...data.participants);
            }
        }
        
        // Extract from workflow name/description
        if (workflow.name || workflow.description) {
            const content = `${workflow.name || ''} ${workflow.description || ''}`;
            const agentPattern = /agent[_\s]*(\w+)/gi;
            const matches = content.match(agentPattern);
            if (matches) {
                participants.push(...matches);
            }
        }
        
        return [...new Set(participants)]; // Remove duplicates
    }

    /**
     * Extract departments involved
     */
    extractDepartments(workflow) {
        const departments = [];
        const content = `${workflow.name || ''} ${workflow.description || ''} ${JSON.stringify(workflow.data || {})}`.toLowerCase();
        
        const departmentKeywords = {
            'strategy': ['strategy', 'planning', 'strategic'],
            'marketing': ['marketing', 'promotion', 'brand'],
            'finance': ['finance', 'financial', 'revenue', 'budget'],
            'operations': ['operations', 'operational', 'process'],
            'business_intelligence': ['intelligence', 'analysis', 'research', 'data'],
            'communication': ['communication', 'message', 'email', 'social'],
            'legal': ['legal', 'compliance', 'regulatory'],
            'automation': ['automation', 'automated', 'orchestration']
        };
        
        for (const [dept, keywords] of Object.entries(departmentKeywords)) {
            if (keywords.some(keyword => content.includes(keyword))) {
                departments.push(dept);
            }
        }
        
        return departments.length > 0 ? departments : ['general'];
    }

    /**
     * Assess workflow complexity
     */
    assessComplexity(workflow) {
        let complexity = 1; // Base complexity
        
        // Participants complexity
        const participants = this.extractParticipants(workflow);
        complexity += participants.length * 0.5;
        
        // Departments complexity
        const departments = this.extractDepartments(workflow);
        complexity += departments.length * 0.3;
        
        // Duration complexity
        const duration = this.calculateDuration(workflow);
        if (duration) {
            const hours = duration / (1000 * 60 * 60);
            complexity += Math.min(2, hours / 24); // Max 2 points for duration
        }
        
        // Data complexity
        if (workflow.data || workflow.metadata) {
            const dataSize = JSON.stringify(workflow.data || workflow.metadata).length;
            complexity += Math.min(1, dataSize / 10000); // Max 1 point for data size
        }
        
        // Priority complexity
        const priority = workflow.priority || 5;
        complexity += priority / 10;
        
        return Math.min(10, Math.max(1, complexity));
    }

    /**
     * Assess business impact
     */
    assessBusinessImpact(workflow) {
        let impact = 5; // Base impact
        
        // Priority impact
        const priority = workflow.priority || 5;
        impact += priority * 0.5;
        
        // Department impact
        const departments = this.extractDepartments(workflow);
        if (departments.includes('finance') || departments.includes('strategy')) {
            impact += 2;
        }
        
        // Success impact
        if (this.determineSuccess(workflow)) {
            impact += 1;
        } else {
            impact -= 2;
        }
        
        // Category impact
        const category = this.categorizeWorkflow(workflow);
        const highImpactCategories = ['business_process', 'optimization', 'research'];
        if (highImpactCategories.includes(category)) {
            impact += 1.5;
        }
        
        return Math.min(10, Math.max(1, impact));
    }

    /**
     * Assess resource usage
     */
    assessResourceUsage(workflow) {
        let usage = 3; // Base usage
        
        // Participants usage
        const participants = this.extractParticipants(workflow);
        usage += participants.length * 0.8;
        
        // Duration usage
        const duration = this.calculateDuration(workflow);
        if (duration) {
            const hours = duration / (1000 * 60 * 60);
            usage += Math.min(3, hours / 12); // Max 3 points for 12+ hours
        }
        
        // Complexity usage
        const complexity = this.assessComplexity(workflow);
        usage += complexity * 0.3;
        
        return Math.min(10, Math.max(1, usage));
    }

    /**
     * Calculate efficiency score
     */
    calculateEfficiencyScore(workflow) {
        let efficiency = 100; // Start with perfect score
        
        // Duration efficiency
        const duration = workflow.duration;
        if (duration) {
            const expectedDuration = this.getExpectedDuration(workflow.category, workflow.complexity);
            if (duration > expectedDuration) {
                const overrun = (duration - expectedDuration) / expectedDuration;
                efficiency -= Math.min(30, overrun * 50);
            } else if (duration < expectedDuration * 0.8) {
                efficiency += 10; // Bonus for being fast
            }
        }
        
        // Success efficiency
        if (!workflow.success) {
            efficiency -= 40;
        }
        
        // Resource efficiency
        const resourceScore = 10 - workflow.resource_usage;
        efficiency += resourceScore * 2;
        
        // Complexity efficiency
        if (workflow.complexity > 7 && workflow.success) {
            efficiency += 10; // Bonus for handling complex workflows
        }
        
        return Math.min(100, Math.max(0, efficiency));
    }

    /**
     * Calculate quality score
     */
    calculateQualityScore(workflow) {
        let quality = 80; // Base quality
        
        // Success quality
        if (workflow.success) {
            quality += 15;
        } else {
            quality -= 25;
        }
        
        // Business impact quality
        quality += workflow.business_impact * 1.5;
        
        // Complexity handling quality
        if (workflow.complexity > 6 && workflow.success) {
            quality += 10;
        }
        
        // Multi-department coordination quality
        if (workflow.departments.length > 1 && workflow.success) {
            quality += 5;
        }
        
        // Error handling quality
        if (workflow.error_message && workflow.error_message.length < 100) {
            quality -= 10; // Poor error documentation
        }
        
        return Math.min(100, Math.max(0, quality));
    }

    /**
     * Get expected duration for workflow category
     */
    getExpectedDuration(category, complexity) {
        const baseDurations = {
            'business_process': 3600000, // 1 hour
            'data_analysis': 7200000, // 2 hours
            'communication': 1800000, // 30 minutes
            'research': 10800000, // 3 hours
            'optimization': 5400000, // 1.5 hours
            'reporting': 2700000, // 45 minutes
            'coordination': 1800000, // 30 minutes
            'automation': 900000, // 15 minutes
            'general': 3600000 // 1 hour
        };
        
        const baseDuration = baseDurations[category] || baseDurations.general;
        return baseDuration * complexity;
    }

    /**
     * Update execution metrics
     */
    updateExecutionMetrics(workflow) {
        const category = workflow.category;
        
        if (!this.executionMetrics.has(category)) {
            this.executionMetrics.set(category, {
                total_executions: 0,
                successful_executions: 0,
                failed_executions: 0,
                total_duration: 0,
                average_duration: 0,
                average_efficiency: 0,
                average_quality: 0,
                average_complexity: 0,
                average_business_impact: 0,
                success_rate: 0,
                last_execution: null,
                trend: 'stable'
            });
        }
        
        const metrics = this.executionMetrics.get(category);
        
        // Update counters
        metrics.total_executions += 1;
        if (workflow.success) {
            metrics.successful_executions += 1;
        } else {
            metrics.failed_executions += 1;
        }
        
        // Update durations
        if (workflow.duration) {
            metrics.total_duration += workflow.duration;
            metrics.average_duration = metrics.total_duration / metrics.total_executions;
        }
        
        // Update averages
        metrics.average_efficiency = this.calculateCategoryAverage(category, 'efficiency_score');
        metrics.average_quality = this.calculateCategoryAverage(category, 'quality_score');
        metrics.average_complexity = this.calculateCategoryAverage(category, 'complexity');
        metrics.average_business_impact = this.calculateCategoryAverage(category, 'business_impact');
        
        // Update success rate
        metrics.success_rate = (metrics.successful_executions / metrics.total_executions) * 100;
        
        // Update last execution
        metrics.last_execution = workflow.started_at || workflow.created_at;
    }

    /**
     * Calculate category average for a metric
     */
    calculateCategoryAverage(category, metric) {
        const categoryWorkflows = Array.from(this.workflowHistory.values())
            .filter(w => w.category === category);
        
        if (categoryWorkflows.length === 0) return 0;
        
        const sum = categoryWorkflows.reduce((total, workflow) => total + (workflow[metric] || 0), 0);
        return sum / categoryWorkflows.length;
    }

    /**
     * Initialize workflow templates
     */
    async initializeWorkflowTemplates() {
        const templates = [
            {
                id: 'market_research',
                name: 'Market Research Workflow',
                category: 'research',
                estimated_duration: 7200000, // 2 hours
                complexity: 6,
                departments: ['business_intelligence', 'strategy'],
                steps: ['data_collection', 'analysis', 'reporting'],
                success_criteria: ['report_generated', 'insights_extracted']
            },
            {
                id: 'content_creation',
                name: 'Content Creation Workflow',
                category: 'communication',
                estimated_duration: 3600000, // 1 hour
                complexity: 4,
                departments: ['marketing', 'communication'],
                steps: ['topic_research', 'content_writing', 'review', 'publishing'],
                success_criteria: ['content_published', 'engagement_metrics']
            },
            {
                id: 'financial_analysis',
                name: 'Financial Analysis Workflow',
                category: 'data_analysis',
                estimated_duration: 5400000, // 1.5 hours
                complexity: 7,
                departments: ['finance', 'business_intelligence'],
                steps: ['data_extraction', 'calculation', 'visualization', 'reporting'],
                success_criteria: ['analysis_complete', 'recommendations_generated']
            },
            {
                id: 'process_optimization',
                name: 'Process Optimization Workflow',
                category: 'optimization',
                estimated_duration: 10800000, // 3 hours
                complexity: 8,
                departments: ['operations', 'automation'],
                steps: ['current_state_analysis', 'bottleneck_identification', 'solution_design', 'implementation'],
                success_criteria: ['efficiency_improved', 'metrics_validated']
            }
        ];
        
        for (const template of templates) {
            this.workflowTemplates.set(template.id, template);
        }
    }

    /**
     * Calculate baseline metrics
     */
    async calculateBaselineMetrics() {
        const workflows = Array.from(this.workflowHistory.values());
        
        this.performanceAnalytics.set('overall', {
            total_workflows: workflows.length,
            success_rate: workflows.filter(w => w.success).length / Math.max(1, workflows.length) * 100,
            average_duration: workflows.reduce((sum, w) => sum + (w.duration || 0), 0) / Math.max(1, workflows.length),
            average_efficiency: workflows.reduce((sum, w) => sum + w.efficiency_score, 0) / Math.max(1, workflows.length),
            average_quality: workflows.reduce((sum, w) => sum + w.quality_score, 0) / Math.max(1, workflows.length),
            average_complexity: workflows.reduce((sum, w) => sum + w.complexity, 0) / Math.max(1, workflows.length),
            most_common_category: this.getMostCommonCategory(),
            department_distribution: this.getDepartmentDistribution(),
            trend_analysis: this.calculateTrends()
        });
    }

    /**
     * Get most common workflow category
     */
    getMostCommonCategory() {
        const categoryCounts = {};
        
        for (const workflow of this.workflowHistory.values()) {
            categoryCounts[workflow.category] = (categoryCounts[workflow.category] || 0) + 1;
        }
        
        return Object.entries(categoryCounts)
            .sort(([,a], [,b]) => b - a)[0]?.[0] || 'general';
    }

    /**
     * Get department distribution
     */
    getDepartmentDistribution() {
        const distribution = {};
        
        for (const workflow of this.workflowHistory.values()) {
            for (const dept of workflow.departments) {
                distribution[dept] = (distribution[dept] || 0) + 1;
            }
        }
        
        return distribution;
    }

    /**
     * Calculate trends
     */
    calculateTrends() {
        const workflows = Array.from(this.workflowHistory.values())
            .sort((a, b) => new Date(a.started_at) - new Date(b.started_at));
        
        if (workflows.length < 5) return { trend: 'insufficient_data' };
        
        const recentWorkflows = workflows.slice(-10);
        const olderWorkflows = workflows.slice(-20, -10);
        
        const recentSuccessRate = recentWorkflows.filter(w => w.success).length / recentWorkflows.length * 100;
        const olderSuccessRate = olderWorkflows.filter(w => w.success).length / Math.max(1, olderWorkflows.length) * 100;
        
        const recentEfficiency = recentWorkflows.reduce((sum, w) => sum + w.efficiency_score, 0) / recentWorkflows.length;
        const olderEfficiency = olderWorkflows.reduce((sum, w) => sum + w.efficiency_score, 0) / Math.max(1, olderWorkflows.length);
        
        return {
            success_rate_trend: recentSuccessRate > olderSuccessRate * 1.05 ? 'improving' : 
                              recentSuccessRate < olderSuccessRate * 0.95 ? 'declining' : 'stable',
            efficiency_trend: recentEfficiency > olderEfficiency * 1.05 ? 'improving' :
                            recentEfficiency < olderEfficiency * 0.95 ? 'declining' : 'stable',
            volume_trend: recentWorkflows.length > olderWorkflows.length ? 'increasing' :
                        recentWorkflows.length < olderWorkflows.length ? 'decreasing' : 'stable'
        };
    }

    /**
     * Update workflow metrics
     */
    async updateWorkflowMetrics() {
        try {
            // Refresh workflow history
            await this.loadWorkflowHistory();
            
            // Recalculate performance analytics
            await this.calculateBaselineMetrics();
            
            // Check for alerts
            await this.checkWorkflowAlerts();
            
            // Broadcast updates
            this.broadcastWorkflowUpdate();
            
        } catch (error) {
            console.error('Error updating workflow metrics:', error);
        }
    }

    /**
     * Check workflow alerts
     */
    async checkWorkflowAlerts() {
        const alerts = [];
        const analytics = this.performanceAnalytics.get('overall');
        
        if (analytics) {
            // Success rate alert
            if (analytics.success_rate < this.performanceThresholds.minSuccessRate) {
                alerts.push({
                    type: 'low_success_rate',
                    severity: analytics.success_rate < 70 ? 'critical' : 'warning',
                    message: `Workflow success rate at ${analytics.success_rate.toFixed(1)}%`,
                    value: analytics.success_rate
                });
            }
            
            // Average duration alert
            if (analytics.average_duration > this.performanceThresholds.maxExecutionTime) {
                alerts.push({
                    type: 'long_execution_time',
                    severity: 'warning',
                    message: `Average workflow duration ${(analytics.average_duration / 60000).toFixed(1)} minutes`,
                    value: analytics.average_duration
                });
            }
            
            // Efficiency alert
            if (analytics.average_efficiency < 60) {
                alerts.push({
                    type: 'low_efficiency',
                    severity: analytics.average_efficiency < 40 ? 'critical' : 'warning',
                    message: `Average workflow efficiency at ${analytics.average_efficiency.toFixed(1)}%`,
                    value: analytics.average_efficiency
                });
            }
        }
        
        // Category-specific alerts
        for (const [category, metrics] of this.executionMetrics) {
            if (metrics.success_rate < 80) {
                alerts.push({
                    type: 'category_performance',
                    severity: 'warning',
                    message: `${category} workflows success rate at ${metrics.success_rate.toFixed(1)}%`,
                    category: category,
                    value: metrics.success_rate
                });
            }
        }
        
        this.executionAlerts = alerts.map(alert => ({
            ...alert,
            id: `workflow_${alert.type}_${Date.now()}`,
            timestamp: new Date().toISOString(),
            acknowledged: false
        }));
        
        if (alerts.length > 0) {
            this.broadcastWorkflowAlerts();
        }
    }

    /**
     * Event handlers
     */
    handleWorkflowExecution(detail) {
        // Handle new workflow execution
        this.processWorkflowRecord(detail, 'realtime');
    }

    handleWorkflowStatusUpdate(detail) {
        const { workflow_id, status, progress } = detail;
        const workflow = this.workflowHistory.get(workflow_id);
        
        if (workflow) {
            workflow.status = status;
            workflow.progress = progress;
            workflow.last_updated = new Date().toISOString();
        }
    }

    handleWorkflowCompletion(detail) {
        const { workflow_id, success, duration, result } = detail;
        const workflow = this.workflowHistory.get(workflow_id);
        
        if (workflow) {
            workflow.status = 'completed';
            workflow.success = success;
            workflow.duration = duration;
            workflow.completed_at = new Date().toISOString();
            workflow.result = result;
            
            // Recalculate scores
            workflow.efficiency_score = this.calculateEfficiencyScore(workflow);
            workflow.quality_score = this.calculateQualityScore(workflow);
            
            // Update metrics
            this.updateExecutionMetrics(workflow);
        }
    }

    /**
     * Broadcast updates
     */
    broadcastWorkflowUpdate() {
        const summary = this.getWorkflowSummary();
        
        const event = new CustomEvent('workflow-update', {
            detail: summary
        });
        window.dispatchEvent(event);
    }

    broadcastWorkflowAlerts() {
        const event = new CustomEvent('workflow-alerts', {
            detail: {
                alerts: this.executionAlerts,
                count: this.executionAlerts.length,
                critical: this.executionAlerts.filter(a => a.severity === 'critical').length,
                timestamp: new Date().toISOString()
            }
        });
        window.dispatchEvent(event);
    }

    /**
     * Public API methods
     */
    getWorkflowSummary() {
        return {
            total_workflows: this.workflowHistory.size,
            execution_metrics: Object.fromEntries(this.executionMetrics),
            performance_analytics: Object.fromEntries(this.performanceAnalytics),
            workflow_templates: Object.fromEntries(this.workflowTemplates),
            recent_executions: this.getRecentExecutions(10),
            alerts: this.executionAlerts,
            last_updated: new Date().toISOString()
        };
    }

    getRecentExecutions(limit = 50) {
        return Array.from(this.workflowHistory.values())
            .sort((a, b) => new Date(b.started_at) - new Date(a.started_at))
            .slice(0, limit);
    }

    getWorkflowsByCategory(category) {
        return Array.from(this.workflowHistory.values())
            .filter(w => w.category === category);
    }

    getWorkflowsByDepartment(department) {
        return Array.from(this.workflowHistory.values())
            .filter(w => w.departments.includes(department));
    }

    getWorkflowMetrics(category = null) {
        if (category) {
            return this.executionMetrics.get(category) || null;
        }
        return new Map(this.executionMetrics);
    }

    getPerformanceAnalytics() {
        return new Map(this.performanceAnalytics);
    }

    getAlerts() {
        return this.executionAlerts.filter(alert => !alert.acknowledged);
    }

    acknowledgeAlert(alertId) {
        const alert = this.executionAlerts.find(a => a.id === alertId);
        if (alert) {
            alert.acknowledged = true;
            alert.acknowledged_at = new Date().toISOString();
        }
    }

    getTrackingStatus() {
        return {
            isTracking: this.isTracking,
            totalWorkflows: this.workflowHistory.size,
            categoriesTracked: this.executionMetrics.size,
            activeAlerts: this.executionAlerts.filter(a => !a.acknowledged).length,
            lastUpdate: new Date().toISOString()
        };
    }

    cleanup() {
        this.stopTracking();
        this.workflowHistory.clear();
        this.executionMetrics.clear();
        this.performanceAnalytics.clear();
        this.workflowTemplates.clear();
        this.executionAlerts = [];
    }
}

// Create singleton instance
const workflowExecutionHistoryService = new WorkflowExecutionHistoryService();

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    workflowExecutionHistoryService.cleanup();
});

export default workflowExecutionHistoryService;
