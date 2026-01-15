/**
 * Revenue Tracking and KPI Data Services
 * Comprehensive financial performance monitoring and business intelligence
 */

import EnterpriseDatabase from './EnterpriseDatabase';
import webSocketService, { WEBSOCKET_CHANNELS, DATA_TYPES } from './WebSocketService';

class RevenueTrackingService {
    constructor() {
        this.revenueData = new Map();
        this.kpiMetrics = new Map();
        this.forecastModels = new Map();
        this.performanceTargets = new Map();
        this.alerts = [];
        this.isTracking = false;
        this.trackingInterval = null;
        
        // Financial KPI thresholds
        this.kpiThresholds = {
            revenueGrowthRate: 15, // 15% monthly growth target
            conversionRate: 3, // 3% minimum conversion rate
            averageDealSize: 5000, // $5K average deal size
            salesCycleLength: 45, // 45 days maximum
            customerLifetimeValue: 25000, // $25K CLV target
            costPerAcquisition: 1000, // $1K maximum CAC
            monthlyRecurringRevenue: 10000, // $10K MRR target
            churnRate: 5 // 5% maximum monthly churn
        };
        
        // Revenue streams and categories
        this.revenueStreams = [
            'consulting_services',
            'ai_automation',
            'research_reports',
            'software_licensing',
            'training_workshops',
            'subscription_services'
        ];
        
        this.initializeTracking();
        this.startTracking();
    }

    /**
     * Initialize revenue tracking system
     */
    async initializeTracking() {
        try {
            // Load existing revenue data
            await this.loadRevenueData();
            
            // Initialize performance targets
            await this.initializePerformanceTargets();
            
            // Load KPI definitions
            await this.initializeKPIMetrics();
            
            // Generate revenue forecasts
            await this.generateRevenueForecasts();
            
            console.log('Revenue Tracking Service initialized');
        } catch (error) {
            console.error('Failed to initialize revenue tracking:', error);
        }
    }

    /**
     * Start revenue tracking
     */
    startTracking() {
        if (this.isTracking) return;
        
        this.isTracking = true;
        
        // Track revenue metrics every 5 minutes
        this.trackingInterval = setInterval(async () => {
            await this.updateRevenueMetrics();
        }, 300000);
        
        // Initial update
        this.updateRevenueMetrics();
        
        console.log('Revenue tracking started');
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
        console.log('Revenue tracking stopped');
    }

    /**
     * Load revenue data from database
     */
    async loadRevenueData() {
        try {
            const revenueRecords = await EnterpriseDatabase.getRevenueTracking();
            
            for (const record of revenueRecords) {
                const key = `${record.year}-${record.month.toString().padStart(2, '0')}`;
                
                this.revenueData.set(key, {
                    period: key,
                    year: record.year,
                    month: record.month,
                    target: record.target_revenue,
                    actual: record.actual_revenue || 0,
                    projected: record.projected_revenue || record.target_revenue,
                    pipeline: record.pipeline_value || 0,
                    closed_deals: record.closed_deals || 0,
                    active_opportunities: record.active_opportunities || 0,
                    conversion_rate: this.calculateConversionRate(record),
                    growth_rate: 0, // Will be calculated
                    variance: this.calculateVariance(record.target_revenue, record.actual_revenue || 0),
                    last_updated: new Date().toISOString()
                });
            }
            
            // Calculate growth rates
            this.calculateGrowthRates();
            
            console.log(`Loaded ${revenueRecords.length} revenue records`);
        } catch (error) {
            console.error('Failed to load revenue data:', error);
        }
    }

    /**
     * Initialize performance targets
     */
    async initializePerformanceTargets() {
        const currentYear = new Date().getFullYear();
        const currentMonth = new Date().getMonth() + 1;
        
        // Set monthly targets for the next 12 months
        for (let i = 0; i < 12; i++) {
            let targetMonth = currentMonth + i;
            let targetYear = currentYear;
            
            if (targetMonth > 12) {
                targetMonth -= 12;
                targetYear += 1;
            }
            
            const key = `${targetYear}-${targetMonth.toString().padStart(2, '0')}`;
            
            // Progressive growth targets
            const baseTarget = 4167; // Starting target from database
            const growthMultiplier = 1 + (i * 0.15); // 15% monthly growth
            const monthlyTarget = Math.round(baseTarget * growthMultiplier);
            
            this.performanceTargets.set(key, {
                period: key,
                revenue_target: monthlyTarget,
                deals_target: Math.ceil(monthlyTarget / 5000), // $5K average deal
                pipeline_target: monthlyTarget * 3, // 3x pipeline coverage
                conversion_target: 3.0, // 3% conversion rate
                customer_acquisition_target: Math.ceil(monthlyTarget / 25000), // $25K CLV
                mrr_growth_target: 15 // 15% MRR growth
            });
        }
    }

    /**
     * Initialize KPI metrics
     */
    async initializeKPIMetrics() {
        const kpiDefinitions = [
            {
                id: 'monthly_recurring_revenue',
                name: 'Monthly Recurring Revenue',
                category: 'revenue',
                formula: 'sum(subscription_revenue)',
                target: this.kpiThresholds.monthlyRecurringRevenue,
                unit: 'currency',
                frequency: 'monthly'
            },
            {
                id: 'customer_acquisition_cost',
                name: 'Customer Acquisition Cost',
                category: 'efficiency',
                formula: 'total_marketing_spend / new_customers',
                target: this.kpiThresholds.costPerAcquisition,
                unit: 'currency',
                frequency: 'monthly'
            },
            {
                id: 'customer_lifetime_value',
                name: 'Customer Lifetime Value',
                category: 'value',
                formula: 'average_revenue_per_customer * average_customer_lifespan',
                target: this.kpiThresholds.customerLifetimeValue,
                unit: 'currency',
                frequency: 'quarterly'
            },
            {
                id: 'conversion_rate',
                name: 'Lead to Customer Conversion Rate',
                category: 'performance',
                formula: 'customers_acquired / total_leads * 100',
                target: this.kpiThresholds.conversionRate,
                unit: 'percentage',
                frequency: 'monthly'
            },
            {
                id: 'revenue_growth_rate',
                name: 'Month-over-Month Revenue Growth',
                category: 'growth',
                formula: '(current_month_revenue - previous_month_revenue) / previous_month_revenue * 100',
                target: this.kpiThresholds.revenueGrowthRate,
                unit: 'percentage',
                frequency: 'monthly'
            },
            {
                id: 'sales_cycle_length',
                name: 'Average Sales Cycle Length',
                category: 'efficiency',
                formula: 'average(days_from_lead_to_close)',
                target: this.kpiThresholds.salesCycleLength,
                unit: 'days',
                frequency: 'monthly'
            },
            {
                id: 'pipeline_velocity',
                name: 'Pipeline Velocity',
                category: 'performance',
                formula: 'pipeline_value / sales_cycle_length',
                target: 1000, // $1K daily pipeline velocity
                unit: 'currency_per_day',
                frequency: 'weekly'
            },
            {
                id: 'win_rate',
                name: 'Opportunity Win Rate',
                category: 'performance',
                formula: 'won_opportunities / total_opportunities * 100',
                target: 25, // 25% win rate
                unit: 'percentage',
                frequency: 'monthly'
            }
        ];
        
        for (const kpi of kpiDefinitions) {
            this.kpiMetrics.set(kpi.id, {
                ...kpi,
                current_value: 0,
                previous_value: 0,
                trend: 'stable',
                last_calculated: null,
                historical_values: []
            });
        }
    }

    /**
     * Update revenue metrics
     */
    async updateRevenueMetrics() {
        try {
            // Refresh revenue data
            await this.loadRevenueData();
            
            // Calculate current period metrics
            await this.calculateCurrentPeriodMetrics();
            
            // Update KPI values
            await this.updateKPIValues();
            
            // Generate forecasts
            await this.updateRevenueForecasts();
            
            // Check for alerts
            await this.checkRevenueAlerts();
            
            // Broadcast updates
            this.broadcastRevenueUpdate();
            
        } catch (error) {
            console.error('Error updating revenue metrics:', error);
        }
    }

    /**
     * Calculate current period metrics
     */
    async calculateCurrentPeriodMetrics() {
        const currentDate = new Date();
        const currentKey = `${currentDate.getFullYear()}-${(currentDate.getMonth() + 1).toString().padStart(2, '0')}`;
        
        let currentPeriod = this.revenueData.get(currentKey);
        if (!currentPeriod) {
            // Create current period if it doesn't exist
            const target = this.performanceTargets.get(currentKey);
            currentPeriod = {
                period: currentKey,
                year: currentDate.getFullYear(),
                month: currentDate.getMonth() + 1,
                target: target?.revenue_target || 4167,
                actual: 0,
                projected: 0,
                pipeline: 0,
                closed_deals: 0,
                active_opportunities: 0,
                conversion_rate: 0,
                growth_rate: 0,
                variance: 0,
                last_updated: new Date().toISOString()
            };
            this.revenueData.set(currentKey, currentPeriod);
        }
        
        // Simulate current period progress (in production, get from real data)
        const dayOfMonth = currentDate.getDate();
        const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
        const monthProgress = dayOfMonth / daysInMonth;
        
        // Simulate actual revenue based on month progress and some variance
        const baseProgress = currentPeriod.target * monthProgress;
        const variance = (Math.random() - 0.5) * 0.2; // ±10% variance
        currentPeriod.actual = Math.max(0, Math.round(baseProgress * (1 + variance)));
        
        // Project end-of-month revenue
        if (monthProgress > 0) {
            currentPeriod.projected = Math.round(currentPeriod.actual / monthProgress);
        }
        
        // Simulate pipeline and deals
        currentPeriod.pipeline = Math.round(currentPeriod.target * (2.5 + Math.random())); // 2.5-3.5x pipeline
        currentPeriod.closed_deals = Math.floor(currentPeriod.actual / 5000); // $5K average deal
        currentPeriod.active_opportunities = Math.floor(currentPeriod.pipeline / 8000); // $8K average opportunity
        
        // Calculate metrics
        currentPeriod.conversion_rate = this.calculateConversionRate(currentPeriod);
        currentPeriod.variance = this.calculateVariance(currentPeriod.target, currentPeriod.actual);
        currentPeriod.last_updated = new Date().toISOString();
        
        // Update growth rate
        this.calculateGrowthRates();
    }

    /**
     * Update KPI values
     */
    async updateKPIValues() {
        for (const [kpiId, kpi] of this.kpiMetrics) {
            const previousValue = kpi.current_value;
            const newValue = await this.calculateKPIValue(kpiId);
            
            kpi.previous_value = previousValue;
            kpi.current_value = newValue;
            kpi.trend = this.determineTrend(previousValue, newValue);
            kpi.last_calculated = new Date().toISOString();
            
            // Store historical value
            kpi.historical_values.push({
                value: newValue,
                timestamp: new Date().toISOString()
            });
            
            // Keep only last 100 values
            if (kpi.historical_values.length > 100) {
                kpi.historical_values.shift();
            }
        }
    }

    /**
     * Calculate individual KPI value
     */
    async calculateKPIValue(kpiId) {
        const currentPeriod = this.getCurrentPeriod();
        const previousPeriod = this.getPreviousPeriod();
        
        switch (kpiId) {
            case 'monthly_recurring_revenue':
                return currentPeriod?.actual * 0.6 || 0; // 60% of revenue is recurring
                
            case 'customer_acquisition_cost':
                // Simulate based on revenue and acquisition efficiency
                return Math.round(1200 - (currentPeriod?.conversion_rate || 0) * 100);
                
            case 'customer_lifetime_value':
                // Calculate based on average revenue and retention
                const avgMonthlyRevenue = currentPeriod?.actual || 0;
                const avgCustomerLifespan = 24; // 24 months average
                return Math.round((avgMonthlyRevenue / (currentPeriod?.closed_deals || 1)) * avgCustomerLifespan);
                
            case 'conversion_rate':
                return currentPeriod?.conversion_rate || 0;
                
            case 'revenue_growth_rate':
                if (!currentPeriod || !previousPeriod || previousPeriod.actual === 0) return 0;
                return ((currentPeriod.actual - previousPeriod.actual) / previousPeriod.actual) * 100;
                
            case 'sales_cycle_length':
                // Simulate based on efficiency metrics
                const baseLength = 60;
                const efficiencyFactor = (currentPeriod?.conversion_rate || 0) / 5;
                return Math.max(30, Math.round(baseLength - efficiencyFactor));
                
            case 'pipeline_velocity':
                const salesCycle = await this.calculateKPIValue('sales_cycle_length');
                return Math.round((currentPeriod?.pipeline || 0) / Math.max(1, salesCycle));
                
            case 'win_rate':
                if (!currentPeriod || currentPeriod.active_opportunities === 0) return 0;
                return (currentPeriod.closed_deals / currentPeriod.active_opportunities) * 100;
                
            default:
                return 0;
        }
    }

    /**
     * Generate revenue forecasts
     */
    async generateRevenueForecasts() {
        const forecastPeriods = 6; // Forecast 6 months ahead
        const historicalData = Array.from(this.revenueData.values())
            .sort((a, b) => a.year - b.year || a.month - b.month);
        
        if (historicalData.length < 3) {
            console.warn('Insufficient historical data for accurate forecasting');
            return;
        }
        
        // Linear regression forecast
        const linearForecast = this.generateLinearForecast(historicalData, forecastPeriods);
        
        // Seasonal adjustment forecast
        const seasonalForecast = this.generateSeasonalForecast(historicalData, forecastPeriods);
        
        // Machine learning-style polynomial forecast
        const polynomialForecast = this.generatePolynomialForecast(historicalData, forecastPeriods);
        
        // Store forecasts
        this.forecastModels.set('linear', linearForecast);
        this.forecastModels.set('seasonal', seasonalForecast);
        this.forecastModels.set('polynomial', polynomialForecast);
        
        // Generate ensemble forecast (weighted average)
        const ensembleForecast = this.generateEnsembleForecast([
            { model: linearForecast, weight: 0.3 },
            { model: seasonalForecast, weight: 0.4 },
            { model: polynomialForecast, weight: 0.3 }
        ]);
        
        this.forecastModels.set('ensemble', ensembleForecast);
    }

    /**
     * Generate linear regression forecast
     */
    generateLinearForecast(historicalData, periods) {
        const n = historicalData.length;
        let sumX = 0, sumY = 0, sumXY = 0, sumXX = 0;
        
        historicalData.forEach((data, index) => {
            const x = index;
            const y = data.actual || data.target;
            sumX += x;
            sumY += y;
            sumXY += x * y;
            sumXX += x * x;
        });
        
        const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
        const intercept = (sumY - slope * sumX) / n;
        
        const forecast = [];
        for (let i = 0; i < periods; i++) {
            const x = n + i;
            const predictedValue = Math.max(0, Math.round(slope * x + intercept));
            
            const futureDate = this.addMonths(new Date(), i + 1);
            forecast.push({
                period: `${futureDate.getFullYear()}-${(futureDate.getMonth() + 1).toString().padStart(2, '0')}`,
                predicted_revenue: predictedValue,
                confidence: Math.max(60, 90 - (i * 5)), // Decreasing confidence
                model: 'linear'
            });
        }
        
        return forecast;
    }

    /**
     * Generate seasonal forecast
     */
    generateSeasonalForecast(historicalData, periods) {
        // Calculate seasonal factors
        const monthlyFactors = new Array(12).fill(1);
        const monthlyData = new Array(12).fill(null).map(() => []);
        
        historicalData.forEach(data => {
            const monthIndex = (data.month - 1) % 12;
            monthlyData[monthIndex].push(data.actual || data.target);
        });
        
        const overallAverage = historicalData.reduce((sum, data) => 
            sum + (data.actual || data.target), 0) / historicalData.length;
        
        monthlyData.forEach((monthData, index) => {
            if (monthData.length > 0) {
                const monthAverage = monthData.reduce((sum, val) => sum + val, 0) / monthData.length;
                monthlyFactors[index] = monthAverage / overallAverage;
            }
        });
        
        // Generate forecast with seasonal adjustment
        const trendData = this.generateLinearForecast(historicalData, periods);
        
        return trendData.map(forecast => {
            const monthIndex = parseInt(forecast.period.split('-')[1]) - 1;
            const seasonalFactor = monthlyFactors[monthIndex];
            
            return {
                ...forecast,
                predicted_revenue: Math.round(forecast.predicted_revenue * seasonalFactor),
                model: 'seasonal'
            };
        });
    }

    /**
     * Generate polynomial forecast
     */
    generatePolynomialForecast(historicalData, periods) {
        // Simplified polynomial regression (quadratic)
        const n = historicalData.length;
        const x = historicalData.map((_, index) => index);
        const y = historicalData.map(data => data.actual || data.target);
        
        // Calculate polynomial coefficients (simplified approach)
        const avgGrowthRate = this.calculateAverageGrowthRate(historicalData);
        const baseValue = y[y.length - 1];
        
        const forecast = [];
        for (let i = 0; i < periods; i++) {
            const futureDate = this.addMonths(new Date(), i + 1);
            const growthFactor = Math.pow(1 + avgGrowthRate / 100, i + 1);
            const predictedValue = Math.round(baseValue * growthFactor);
            
            forecast.push({
                period: `${futureDate.getFullYear()}-${(futureDate.getMonth() + 1).toString().padStart(2, '0')}`,
                predicted_revenue: predictedValue,
                confidence: Math.max(50, 85 - (i * 8)),
                model: 'polynomial'
            });
        }
        
        return forecast;
    }

    /**
     * Generate ensemble forecast
     */
    generateEnsembleForecast(models) {
        const periods = models[0].model.length;
        const ensemble = [];
        
        for (let i = 0; i < periods; i++) {
            let weightedSum = 0;
            let totalWeight = 0;
            let avgConfidence = 0;
            
            models.forEach(({ model, weight }) => {
                weightedSum += model[i].predicted_revenue * weight;
                totalWeight += weight;
                avgConfidence += model[i].confidence * weight;
            });
            
            ensemble.push({
                period: models[0].model[i].period,
                predicted_revenue: Math.round(weightedSum / totalWeight),
                confidence: Math.round(avgConfidence / totalWeight),
                model: 'ensemble'
            });
        }
        
        return ensemble;
    }

    /**
     * Check revenue alerts
     */
    async checkRevenueAlerts() {
        const alerts = [];
        const currentPeriod = this.getCurrentPeriod();
        const currentDate = new Date();
        const dayOfMonth = currentDate.getDate();
        const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
        const monthProgress = dayOfMonth / daysInMonth;
        
        if (currentPeriod) {
            // Revenue target variance alert
            if (Math.abs(currentPeriod.variance) > 20) {
                alerts.push({
                    type: 'revenue_variance',
                    severity: Math.abs(currentPeriod.variance) > 30 ? 'critical' : 'warning',
                    message: `Revenue variance ${currentPeriod.variance > 0 ? '+' : ''}${currentPeriod.variance.toFixed(1)}% from target`,
                    value: currentPeriod.variance
                });
            }
            
            // Month progress alert
            const expectedProgress = currentPeriod.target * monthProgress;
            const actualProgress = currentPeriod.actual;
            const progressGap = ((actualProgress - expectedProgress) / expectedProgress) * 100;
            
            if (Math.abs(progressGap) > 15 && monthProgress > 0.25) {
                alerts.push({
                    type: 'monthly_progress',
                    severity: Math.abs(progressGap) > 25 ? 'critical' : 'warning',
                    message: `Monthly revenue ${progressGap > 0 ? 'ahead' : 'behind'} by ${Math.abs(progressGap).toFixed(1)}%`,
                    value: progressGap
                });
            }
            
            // Pipeline coverage alert
            const pipelineCoverage = currentPeriod.pipeline / currentPeriod.target;
            if (pipelineCoverage < 2) {
                alerts.push({
                    type: 'pipeline_coverage',
                    severity: pipelineCoverage < 1.5 ? 'critical' : 'warning',
                    message: `Pipeline coverage only ${pipelineCoverage.toFixed(1)}x of monthly target`,
                    value: pipelineCoverage
                });
            }
        }
        
        // KPI threshold alerts
        for (const [kpiId, kpi] of this.kpiMetrics) {
            if (kpi.target && kpi.current_value !== null) {
                const variance = ((kpi.current_value - kpi.target) / kpi.target) * 100;
                
                if (Math.abs(variance) > 20) {
                    alerts.push({
                        type: 'kpi_threshold',
                        severity: Math.abs(variance) > 30 ? 'critical' : 'warning',
                        message: `${kpi.name} ${variance > 0 ? 'exceeds' : 'below'} target by ${Math.abs(variance).toFixed(1)}%`,
                        kpi: kpiId,
                        value: variance
                    });
                }
            }
        }
        
        // Store alerts
        this.alerts = alerts.map(alert => ({
            ...alert,
            id: `revenue_${alert.type}_${Date.now()}`,
            timestamp: new Date().toISOString(),
            acknowledged: false
        }));
        
        // Broadcast alerts
        if (alerts.length > 0) {
            this.broadcastRevenueAlerts();
        }
    }

    /**
     * Broadcast revenue update
     */
    broadcastRevenueUpdate() {
        const summary = this.getRevenueSummary();
        
        const event = new CustomEvent('revenue-update', {
            detail: summary
        });
        window.dispatchEvent(event);
    }

    /**
     * Broadcast revenue alerts
     */
    broadcastRevenueAlerts() {
        const event = new CustomEvent('revenue-alerts', {
            detail: {
                alerts: this.alerts,
                count: this.alerts.length,
                critical: this.alerts.filter(a => a.severity === 'critical').length,
                timestamp: new Date().toISOString()
            }
        });
        window.dispatchEvent(event);
    }

    /**
     * Helper functions
     */
    calculateConversionRate(record) {
        if (!record.active_opportunities || record.active_opportunities === 0) return 0;
        return (record.closed_deals / record.active_opportunities) * 100;
    }

    calculateVariance(target, actual) {
        if (target === 0) return 0;
        return ((actual - target) / target) * 100;
    }

    calculateGrowthRates() {
        const sortedData = Array.from(this.revenueData.values())
            .sort((a, b) => a.year - b.year || a.month - b.month);
        
        for (let i = 1; i < sortedData.length; i++) {
            const current = sortedData[i];
            const previous = sortedData[i - 1];
            
            if (previous.actual > 0) {
                current.growth_rate = ((current.actual - previous.actual) / previous.actual) * 100;
            }
        }
    }

    calculateAverageGrowthRate(data) {
        const growthRates = [];
        for (let i = 1; i < data.length; i++) {
            const current = data[i].actual || data[i].target;
            const previous = data[i - 1].actual || data[i - 1].target;
            if (previous > 0) {
                growthRates.push(((current - previous) / previous) * 100);
            }
        }
        return growthRates.length > 0 ? growthRates.reduce((sum, rate) => sum + rate, 0) / growthRates.length : 0;
    }

    determineTrend(previous, current) {
        if (current > previous * 1.05) return 'increasing';
        if (current < previous * 0.95) return 'decreasing';
        return 'stable';
    }

    addMonths(date, months) {
        const newDate = new Date(date);
        newDate.setMonth(newDate.getMonth() + months);
        return newDate;
    }

    getCurrentPeriod() {
        const currentDate = new Date();
        const currentKey = `${currentDate.getFullYear()}-${(currentDate.getMonth() + 1).toString().padStart(2, '0')}`;
        return this.revenueData.get(currentKey);
    }

    getPreviousPeriod() {
        const currentDate = new Date();
        const previousDate = this.addMonths(currentDate, -1);
        const previousKey = `${previousDate.getFullYear()}-${(previousDate.getMonth() + 1).toString().padStart(2, '0')}`;
        return this.revenueData.get(previousKey);
    }

    /**
     * Update revenue forecasts
     */
    async updateRevenueForecasts() {
        await this.generateRevenueForecasts();
    }

    /**
     * Public API methods
     */
    getRevenueSummary() {
        const currentPeriod = this.getCurrentPeriod();
        const previousPeriod = this.getPreviousPeriod();
        
        return {
            current_period: currentPeriod,
            previous_period: previousPeriod,
            kpi_metrics: Object.fromEntries(this.kpiMetrics),
            forecasts: Object.fromEntries(this.forecastModels),
            performance_targets: Object.fromEntries(this.performanceTargets),
            alerts: this.alerts,
            summary: {
                total_revenue_ytd: Array.from(this.revenueData.values())
                    .filter(d => d.year === new Date().getFullYear())
                    .reduce((sum, d) => sum + d.actual, 0),
                average_monthly_growth: this.calculateAverageGrowthRate(Array.from(this.revenueData.values())),
                pipeline_coverage: currentPeriod ? currentPeriod.pipeline / currentPeriod.target : 0,
                target_achievement: currentPeriod ? (currentPeriod.actual / currentPeriod.target) * 100 : 0
            },
            last_updated: new Date().toISOString()
        };
    }

    getKPIMetrics() {
        return new Map(this.kpiMetrics);
    }

    getForecasts(model = 'ensemble') {
        return this.forecastModels.get(model) || [];
    }

    getAlerts() {
        return this.alerts.filter(alert => !alert.acknowledged);
    }

    acknowledgeAlert(alertId) {
        const alert = this.alerts.find(a => a.id === alertId);
        if (alert) {
            alert.acknowledged = true;
            alert.acknowledged_at = new Date().toISOString();
        }
    }

    getTrackingStatus() {
        return {
            isTracking: this.isTracking,
            revenuePeriodsTracked: this.revenueData.size,
            kpiMetricsTracked: this.kpiMetrics.size,
            activeAlerts: this.alerts.filter(a => !a.acknowledged).length,
            lastUpdate: new Date().toISOString()
        };
    }

    cleanup() {
        this.stopTracking();
        this.revenueData.clear();
        this.kpiMetrics.clear();
        this.forecastModels.clear();
        this.performanceTargets.clear();
        this.alerts = [];
    }
}

// Create singleton instance
const revenueTrackingService = new RevenueTrackingService();

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    revenueTrackingService.cleanup();
});

export default revenueTrackingService;
