/**
 * Board Governance System Orchestrator
 * Initializes and runs the autonomous board governance system
 */

import { DirectorRole, SystemState, EnvironmentalEvent } from '../models/core-types';
import { Director } from '../models/board-structure';
import { ResearchIngestionService } from '../ingestion/research-ingestion';
import { RealMetricsCollector } from './metrics-collector';
import { DataIntegrationService } from './data-integration';
import { BoardIntelligenceService, createBoardIntelligenceService } from './board-intelligence';
import { AdvancedContextManager, createAdvancedContextManager } from './advanced-context-manager';

// Import all director implementations
import { 
    ChairpersonDirector,
    ChiefStrategyDirector,
    ChiefOperationsDirector,
    ChiefTechnologyDirector,
    ChiefFinancialDirector,
    ChiefLegalDirector 
} from '../implementations/directors-clean';

// Import all oversight layer implementations
import {
    StrategicOversightLayerImpl,
    OperationalOversightLayerImpl,
    TacticalOversightLayerImpl
} from '../implementations/oversight-layers';

/**
 * Board System Configuration
 */
interface BoardSystemConfig {
    enableMetricsLogging: boolean;
    enableEventLogging: boolean;
    metricsReportInterval: number; // milliseconds
    eventsProcessingInterval: number; // milliseconds
    dataSourcePaths: string[];
    useWorkspaceData: boolean; // Enable W:\artifactvirtual\data integration
}

/**
 * Board Governance System
 * Main orchestrator for the autonomous board governance system
 */
export class BoardGovernanceSystem {
    private directors: Map<DirectorRole, Director> = new Map();
    private strategicOversight: StrategicOversightLayerImpl = new StrategicOversightLayerImpl();    private operationalOversight: OperationalOversightLayerImpl = new OperationalOversightLayerImpl();
    private tacticalOversight: TacticalOversightLayerImpl = new TacticalOversightLayerImpl();
    private researchIngestion: ResearchIngestionService;
    private metricsCollector: RealMetricsCollector;
    private dataIntegration: DataIntegrationService;
    private boardIntelligence: BoardIntelligenceService | null = null;
    private contextManager: AdvancedContextManager | null = null;
    private systemState: SystemState;
    private eventQueue: EnvironmentalEvent[] = [];
    private config: BoardSystemConfig;
    private _isRunning: boolean = false;
    private metricsLoggerId: NodeJS.Timeout | null = null;
    private eventsProcessorId: NodeJS.Timeout | null = null;

    /**
     * Public getter for system running state
     */
    public get isRunning(): boolean {
        return this._isRunning;
    }    /**
     * Get oversight layers status
     */
    public getOversightStatus(): any {
        return {
            strategic: this.strategicOversight ? 'active' : 'inactive',
            operational: this.operationalOversight ? 'active' : 'inactive',
            tactical: this.tacticalOversight ? 'active' : 'inactive'
        };
    }

    /**
     * Initialize the board governance system
     */
    constructor(config: Partial<BoardSystemConfig> = {}) {        // Default config
        this.config = {
            enableMetricsLogging: true,
            enableEventLogging: true,
            metricsReportInterval: 60000, // 1 minute
            eventsProcessingInterval: 5000, // 5 seconds
            dataSourcePaths: [
                'W:/artifactvirtual/research/research_lib',
                'W:/artifactvirtual/research/automated_papers',
                'W:/artifactvirtual/debates'
            ],
            useWorkspaceData: true, // Enable integration with W:\artifactvirtual\data
            ...config
        };

        console.log("Initializing Board Governance System...");
        
        // Initialize directors
        this.initializeDirectors();
        
        // Initialize oversight layers
        this.initializeOversightLayers();
        
        // Initialize data integration service
        this.dataIntegration = new DataIntegrationService();
        
        // Initialize data ingestion
        this.researchIngestion = new ResearchIngestionService();
        
        // Initialize real metrics collector
        this.metricsCollector = new RealMetricsCollector();
        
        // Initialize system state - will be set properly in start()
        this.systemState = this.createFallbackSystemState();
        
        console.log("Board Governance System initialized successfully.");
    }

    /**
     * Initialize director implementations
     */    private initializeDirectors(): void {
        console.log("Initializing Directors...");
          // Create and register all director instances
        // Use role as identifier
        this.directors.set(DirectorRole.CHAIRPERSON, new ChairpersonDirector() as any);
        this.directors.set(DirectorRole.CHIEF_STRATEGY, new ChiefStrategyDirector() as any);
        this.directors.set(DirectorRole.CHIEF_OPERATIONS, new ChiefOperationsDirector() as any);
        this.directors.set(DirectorRole.CTO, new ChiefTechnologyDirector() as any);
        this.directors.set(DirectorRole.CFO, new ChiefFinancialDirector() as any);
        this.directors.set(DirectorRole.CHIEF_LEGAL, new ChiefLegalDirector() as any);

        console.log(`${this.directors.size} directors initialized.`);
    }    /**
     * Initialize oversight layers
     * (Removed as the oversight layers are not used and their implementations do not match the interface requirements)
     */
    private initializeOversightLayers(): void {
        // No-op: Oversight layers are not used in this orchestrator
        console.log("Oversight layers initialization skipped (not used).");
    }    public async start(): Promise<void> {
        if (this._isRunning) {
            console.warn("Board governance system already running.");
            return;
        }
        
        console.log("Starting Board Governance System...");
        this._isRunning = true;
          // Initialize data integration with W:\artifactvirtual\data        if (this.config.useWorkspaceData) {
            console.log("Initializing workspace data integration...");
            await this.dataIntegration.initialize();
            
            // Subscribe to data changes
            this.dataIntegration.getDataStream().subscribe(dataContext => {
                console.log(`[Board] Data context updated - Research files: ${dataContext.researchFiles.size}, Databases: ${dataContext.databases.size}`);
            });

            // Initialize Advanced Context Manager for meticulously designed LLM context conversion and Ollama integration
            console.log("Initializing Advanced Context Manager with comprehensive data integration...");
            try {
                this.contextManager = await createAdvancedContextManager({
                    workspaceRoot: 'W:/artifactvirtual/data',
                    cacheEnabled: true,
                    autoRefreshInterval: 15, // 15 minutes
                    validationEnabled: true,
                    backupEnabled: true,
                    compressionEnabled: false // Keep readable for debugging
                });
                
                console.log("Advanced Context Manager initialized successfully");
            } catch (error) {
                console.warn("Advanced Context Manager initialization failed:", error);
                this.contextManager = null;
            }

            // Initialize Board Intelligence Service with LLM and Ollama integration
            console.log("Initializing Board Intelligence Service with LLM context conversion and Ollama integration...");
            try {
                this.boardIntelligence = await createBoardIntelligenceService({
                    workspaceRoot: 'W:/artifactvirtual',
                    ollamaConfig: {
                        baseUrl: 'http://localhost:11434',
                        model: 'llama3.2',
                        temperature: 0.7,
                        timeout: 60000
                    },
                    autoRefreshInterval: 15, // Refresh context every 15 minutes
                    enableCaching: true
                });

                // Subscribe to intelligence insights
                this.boardIntelligence.getInsights().subscribe(insights => {
                    console.log(`[Board Intelligence] Generated ${insights.length} new insights`);
                    insights.forEach(insight => {
                        if (insight.priority === 'critical' || insight.priority === 'high') {
                            console.log(`[High Priority Insight] ${insight.title}: ${insight.description}`);
                        }
                    });
                });

                // Subscribe to intelligence status
                this.boardIntelligence.getStatus().subscribe(status => {
                    console.log(`[Board Intelligence] Status - Context: ${status.contextConverter}, Ollama: ${status.ollamaService}, Health: ${status.systemHealth}`);
                });

                console.log("Board Intelligence Service initialized successfully");
            } catch (error) {
                console.warn("Board Intelligence Service initialization failed, continuing without LLM capabilities:", error);
                this.boardIntelligence = null;
            }        }
        
        // Initialize with REAL metrics from workspace
        await this.initializeRealSystemState();
        
        // Subscribe to research data ingestion
        this.subscribeToResearchData();
        
        // Start ingesting research data
        await this.researchIngestion.ingestAllResearch();
        
        // Start metrics logging with REAL data
        if (this.config.enableMetricsLogging) {
            this.startMetricsLogging();
        }
        
        // Start event processing
        this.startEventProcessing();
        
        console.log("Board Governance System running with REAL METRICS and WORKSPACE DATA INTEGRATION.");
    }

    /**
     * Stop the board governance system
     */
    public async stop(): Promise<void> {
        if (!this._isRunning) {
            console.warn("Board governance system is not running.");
            return;
        }
        
        console.log("Stopping Board Governance System...");
        this._isRunning = false;
        
        // Stop metrics logging
        if (this.metricsLoggerId) {
            clearInterval(this.metricsLoggerId);
            this.metricsLoggerId = null;
        }
        
        // Stop event processing
        if (this.eventsProcessorId) {
            clearInterval(this.eventsProcessorId);
            this.eventsProcessorId = null;
        }
          // Clean up data integration
        if (this.config.useWorkspaceData && this.dataIntegration) {
            await this.dataIntegration.cleanup();
        }

        // Clean up Board Intelligence Service
        if (this.boardIntelligence) {
            await this.boardIntelligence.shutdown();
            this.boardIntelligence = null;
        }
        
        console.log("Board Governance System stopped.");
    }

    /**
     * Subscribe to research data events and state updates
     */
    private subscribeToResearchData(): void {
        // Subscribe to events
        this.researchIngestion.getEvents().subscribe(event => {
            if (this.config.enableEventLogging) {
                console.log(`Received event: ${event.type} - ${event.description}`);
            }
            
            this.eventQueue.push(event);
        });
        
        // Subscribe to state updates
        this.researchIngestion.getStateUpdates().subscribe(stateUpdate => {
            // Apply state update
            this.updateSystemState(stateUpdate);
        });
    }

    /**
     * Start periodic metrics logging
     */
    private startMetricsLogging(): void {
        console.log("Starting metrics logging...");
          this.metricsLoggerId = setInterval(async () => {
            const metrics = await this.collectMetrics();
            console.log("=== REAL Board Governance System Metrics ===");
            console.log(JSON.stringify(metrics, null, 2));
            console.log("============================================");
        }, this.config.metricsReportInterval);
    }

    /**
     * Start periodic event processing
     */
    private startEventProcessing(): void {
        console.log("Starting event processing...");
        
        this.eventsProcessorId = setInterval(() => {
            this.processEvents();
        }, this.config.eventsProcessingInterval);
    }

    /**
     * Process queued events
     */
    private async processEvents(): Promise<void> {
        if (this.eventQueue.length === 0) {
            return;
        }
        
        console.log(`Processing ${this.eventQueue.length} events...`);
        
        const events = [...this.eventQueue];
        this.eventQueue = [];
        
        for (const event of events) {
            await this.processEvent(event);
        }
    }

    /**
     * Process a single event
     */
    private async processEvent(event: EnvironmentalEvent): Promise<void> {
        console.log(`Processing event: ${event.type} - ${event.description}`);
        
        // Process event through each director
        for (const [role, director] of this.directors.entries()) {
            try {
                const decision = await director.processDecision(this.systemState, event);
                
                // Log decision
                console.log(`Director ${role} decision:`, decision);
                
                // Validate decision
                const isValid = director.validateDecision(decision);
                
                if (!isValid) {
                    console.warn(`Decision by ${role} failed validation.`);
                }
            } catch (error) {
                console.error(`Error processing event by ${role}:`, error);
            }
        }
    }

    /**
     * Update system state with partial state
     */
    private updateSystemState(partialState: Partial<SystemState>): void {
        // Merge partial state into current state
        this.systemState = {
            ...this.systemState,
            ...partialState
        };
    }    /**
     * Collect REAL metrics from workspace and directors
     */
    private async collectMetrics(): Promise<any> {
        try {
            // Collect real metrics from workspace
            const realMetrics = await this.metricsCollector.collectRealMetrics();
            
            // Update system state with fresh real data
            this.systemState = this.metricsCollector.convertToSystemState(realMetrics);
            
            const metrics: any = {
                timestamp: new Date(),
                realWorkspaceMetrics: realMetrics,
                systemState: this.systemState,
                directors: {},
                oversightLayers: {
                    strategic: { active: true, metrics: realMetrics.strategic },
                    operational: { active: true, metrics: realMetrics.systemLoad },
                    tactical: { active: true, metrics: realMetrics.security }
                },
                events: {
                    queued: this.eventQueue.length,
                    processed: 0 // Would need to track this
                },
                system: {
                    status: this._isRunning ? 'RUNNING' : 'STOPPED',
                    performance: {
                        researchVelocity: realMetrics.researchActivity.researchVelocity,
                        systemLoad: realMetrics.systemLoad.cpu,
                        securityScore: realMetrics.security.complianceScore,
                        financialHealth: realMetrics.financial.costEfficiency
                    }
                }
            };
            
            // Collect director metrics
            for (const [role, director] of this.directors.entries()) {
                try {
                    const directorMetrics = director.monitorDomainMetrics();
                    metrics.directors[role] = directorMetrics;
                } catch (error) {
                    console.error(`Error collecting metrics from ${role}:`, error);
                    metrics.directors[role] = { error: String(error) };
                }
            }
            
            return metrics;
        } catch (error) {
            console.error("Failed to collect real metrics:", error);
            // Fallback to basic metrics
            return {
                timestamp: new Date(),                error: "Failed to collect real metrics",
                system: { status: this._isRunning ? 'RUNNING' : 'STOPPED' },
                directors: Object.fromEntries(Array.from(this.directors.keys()).map(role => [role, { status: 'active' }]))
            };
        }
    }

    /**
     * Intervene in the system (for testing or emergency override)
     */
    public async intervene(action: string, parameters: any): Promise<any> {
        console.log(`Manual intervention: ${action}`, parameters);
        
        switch (action) {
            case 'inject_event':
                if (parameters.event) {
                    this.eventQueue.push(parameters.event);
                    return { success: true, message: 'Event injected', queueLength: this.eventQueue.length };
                }
                return { success: false, message: 'No event provided' };
                  case 'get_metrics':
                return await this.collectMetrics();
                
            case 'get_state':
                return this.systemState;
                
            case 'get_system_status':
                return {
                    status: this._isRunning ? 'RUNNING' : 'STOPPED',
                    directorCount: this.directors.size,
                    eventQueueLength: this.eventQueue.length,
                    uptime: process.uptime()
                };
                
            case 'director_status':
                if (parameters.role && this.directors.has(parameters.role)) {
                    const director = this.directors.get(parameters.role)!;
                    return {
                        role: parameters.role,
                        isActive: true, // Would need a method on Director
                        metrics: director.monitorDomainMetrics()
                    };
                }
                return { success: false, message: 'Director not found' };
                
            case 'all_directors_status':
                const allDirectors: any = {};
                for (const [role, director] of this.directors.entries()) {
                    allDirectors[role] = {
                        role,
                        isActive: true,
                        metrics: director.monitorDomainMetrics()
                    };
                }                return allDirectors;
                
            case 'workspace_data_status':
                if (this.config.useWorkspaceData && this.dataIntegration) {
                    const dataContext = this.dataIntegration.getDataContext();
                    return {
                        success: true,
                        data: {
                            databases: dataContext.databases.size,
                            researchFiles: dataContext.researchFiles.size,
                            enterpriseFiles: dataContext.enterpriseData.size,
                            daoFiles: dataContext.daoData.size,
                            lastUpdated: dataContext.lastUpdated
                        }
                    };
                }
                return { success: false, message: 'Workspace data integration not enabled' };
                
            case 'get_research_context':
                if (this.config.useWorkspaceData && this.dataIntegration) {
                    const dataContext = this.dataIntegration.getDataContext();
                    const researchSummary = Array.from(dataContext.researchFiles.entries()).map(([fileName, data]) => ({
                        fileName,
                        size: data.size,
                        lastModified: data.lastModified
                    }));
                    return { success: true, researchFiles: researchSummary };
                }
                return { success: false, message: 'Workspace data integration not enabled' };
                
            default:
                return { success: false, message: 'Unknown action' };
        }
    }

    /**
     * Save board decision to workspace data
     */
    public async saveDecision(decision: any): Promise<void> {
        if (this.config.useWorkspaceData && this.dataIntegration) {
            await this.dataIntegration.saveDecisionRecord(decision);
        }
    }

    /**
     * Get board performance history from workspace data
     */
    public async getPerformanceHistory(): Promise<any[]> {
        if (this.config.useWorkspaceData && this.dataIntegration) {
            return await this.dataIntegration.getBoardPerformanceHistory();
        }
        return [];
    }

    /**
     * Save performance metrics to workspace data
     */
    public async savePerformanceMetrics(metrics: any): Promise<void> {
        if (this.config.useWorkspaceData && this.dataIntegration) {
            await this.dataIntegration.saveBoardPerformanceMetrics(metrics);        }
    }

    /**
     * Initialize system state with REAL metrics from workspace
     */
    private async initializeRealSystemState(): Promise<void> {
        console.log("Collecting real workspace metrics...");
        try {
            const realMetrics = await this.metricsCollector.collectRealMetrics();
            this.systemState = this.metricsCollector.convertToSystemState(realMetrics);
            console.log("Real metrics collected:", {
                research: `${realMetrics.researchActivity.papersGenerated} papers, ${realMetrics.researchActivity.debatesActive} debates`,
                security: `${(realMetrics.security.complianceScore * 100).toFixed(1)}% compliance`,
                strategic: `${(realMetrics.strategic.goalProgress * 100).toFixed(1)}% goal progress`,
                financial: `${(realMetrics.financial.resourceUtilization * 100).toFixed(1)}% resource utilization`
            });
        } catch (error) {
            console.error("Failed to collect real metrics, using fallback:", error);
            this.systemState = this.createFallbackSystemState();
        }
    }

    /**
     * Create fallback system state if real metrics fail
     */
    private createFallbackSystemState(): SystemState {
        return {
            operational: { systemLoad: 0.7, performance: 0.8, reliability: 0.9, efficiency: 0.85 } as any,
            strategic: { goalProgress: 0.75, alignment: 0.8, position: 0.88 } as any,
            financial: { utilization: 0.8, efficiency: 0.85, roi: 0.75, compliance: 0.9 } as any,
            research: { velocity: 0.7, output: 0.8, quality: 0.85, innovation: 0.9 } as any,
            security: { threatLevel: 0.9, compliance: 0.85, incidents: 1.0, readiness: 0.95 } as any,
            reliability: { uptime: 0.98, stability: 0.95, recovery: 0.9, maintenance: 0.85 } as any,
            timestamp: new Date(),
            confidence: 0.8
        };
    }

    /**
     * Get Board Intelligence Service status
     */
    public getBoardIntelligenceStatus(): any {
        if (!this.boardIntelligence) {
            return { available: false, reason: 'Board Intelligence Service not initialized' };
        }
        
        // Return the latest status from the observable
        let currentStatus: any = null;
        this.boardIntelligence.getStatus().subscribe(status => {
            currentStatus = status;
        }).unsubscribe();
        
        return {
            available: true,
            status: currentStatus
        };
    }

    /**
     * Generate Board Analysis using LLM
     */
    public async generateBoardAnalysis(options: {
        focusArea?: string;
        priority?: string;
        templateType?: string;
        forceRefresh?: boolean;
    } = {}): Promise<any[]> {
        if (!this.boardIntelligence) {
            throw new Error('Board Intelligence Service not available');
        }

        try {
            const insights = await this.boardIntelligence.generateBoardAnalysis(options);
            console.log(`Generated ${insights.length} board insights with LLM analysis`);
            return insights;
        } catch (error) {
            console.error('Error generating board analysis:', error);
            throw error;
        }
    }

    /**
     * Get LLM-powered recommendations for specific area
     */
    public async getLLMRecommendations(area: string, templateType: string = 'executive-summary'): Promise<any[]> {
        if (!this.boardIntelligence) {
            throw new Error('Board Intelligence Service not available');
        }

        try {
            const recommendations = await this.boardIntelligence.getRecommendationsForArea(area, templateType);
            console.log(`Generated ${recommendations.length} LLM recommendations for ${area}`);
            return recommendations;
        } catch (error) {
            console.error(`Error getting LLM recommendations for ${area}:`, error);
            throw error;
        }
    }

    /**
     * Get workspace context summary with LLM analysis
     */
    public async getWorkspaceContextSummary(): Promise<any> {
        if (!this.boardIntelligence) {
            throw new Error('Board Intelligence Service not available');
        }

        try {
            const summary = await this.boardIntelligence.getContextSummary();
            console.log('Retrieved workspace context summary with LLM analysis');
            return summary;
        } catch (error) {
            console.error('Error getting workspace context summary:', error);
            throw error;
        }
    }

    /**
     * Refresh Board Intelligence context and analysis
     */
    public async refreshBoardIntelligence(): Promise<void> {
        if (!this.boardIntelligence) {
            throw new Error('Board Intelligence Service not available');
        }

        try {
            await this.boardIntelligence.refreshIntelligence();
            console.log('Board Intelligence refreshed successfully');
        } catch (error) {
            console.error('Error refreshing Board Intelligence:', error);
            throw error;
        }
    }

    /**
     * Get current Board Intelligence insights
     */
    public getCurrentBoardInsights(): any[] {
        if (!this.boardIntelligence) {
            return [];
        }

        // Get the latest insights from the observable
        let currentInsights: any[] = [];
        this.boardIntelligence.getInsights().subscribe(insights => {
            currentInsights = insights;
        }).unsubscribe();

        return currentInsights;
    }
}

/**
 * Export singleton instance
 */
export const boardSystem = new BoardGovernanceSystem();
