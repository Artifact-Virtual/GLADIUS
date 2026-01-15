/**
 * Board Intelligence Service
 * Integrates LLM Context Converter and Ollama Service
 * Provides high-level interface for AI-powered board governance insights
 */

import { BehaviorSubject, Observable } from 'rxjs';
import { LLMContext, LLMContextConverter } from './llm-context-converter';
import { BoardRecommendation, InsightRequest, OllamaService, createOllamaService } from './ollama-service';

export interface BoardIntelligenceConfig {
    workspaceRoot: string;
    ollamaConfig?: {
        baseUrl?: string;
        model?: string;
        temperature?: number;
        timeout?: number;
    };
    autoRefreshInterval?: number; // minutes
    enableCaching?: boolean;
}

export interface IntelligenceStatus {
    contextConverter: 'ready' | 'initializing' | 'error';
    ollamaService: 'ready' | 'starting' | 'unavailable' | 'error';
    lastContextUpdate: Date | null;
    lastAnalysis: Date | null;
    systemHealth: 'healthy' | 'degraded' | 'unhealthy';
}

export interface BoardInsight {
    id: string;
    type: 'strategic' | 'operational' | 'research' | 'financial' | 'governance' | 'risk' | 'opportunity';
    title: string;
    description: string;
    confidence: number;
    priority: 'critical' | 'high' | 'medium' | 'low';
    dataPoints: string[];
    recommendations: BoardRecommendation[];
    generatedAt: Date;
    validUntil: Date;
}

/**
 * Main Board Intelligence Service
 */
export class BoardIntelligenceService {
    private config: BoardIntelligenceConfig;
    private contextConverter: LLMContextConverter;
    private ollamaService: OllamaService;
    private statusSubject = new BehaviorSubject<IntelligenceStatus>({
        contextConverter: 'initializing',
        ollamaService: 'starting',
        lastContextUpdate: null,
        lastAnalysis: null,
        systemHealth: 'unhealthy'
    });
    private insightsSubject = new BehaviorSubject<BoardInsight[]>([]);
    private refreshInterval: NodeJS.Timeout | null = null;
    private currentContext: LLMContext | null = null;

    constructor(config: BoardIntelligenceConfig) {
        this.config = {
            autoRefreshInterval: 15, // 15 minutes default
            enableCaching: true,
            ...config
        };

        this.contextConverter = new LLMContextConverter(this.config.workspaceRoot);
        this.ollamaService = createOllamaService(this.config.ollamaConfig);
    }

    /**
     * Initialize the board intelligence system
     */
    async initialize(): Promise<boolean> {
        try {
            console.log('Initializing Board Intelligence Service...');
            
            // Initialize context converter
            this.updateStatus({ contextConverter: 'initializing' });
            this.currentContext = await this.contextConverter.convertToLLMContext();
            this.updateStatus({ 
                contextConverter: 'ready',
                lastContextUpdate: new Date()
            });

            // Initialize Ollama service
            this.updateStatus({ ollamaService: 'starting' });
            const ollamaReady = await this.ollamaService.startOllamaServer();
            
            if (ollamaReady) {
                this.updateStatus({ ollamaService: 'ready' });
            } else {
                this.updateStatus({ ollamaService: 'unavailable' });
                console.warn('Ollama service unavailable, continuing with limited functionality');
            }

            // Generate initial insights
            await this.generateInitialInsights();

            // Set up auto-refresh if enabled
            if (this.config.autoRefreshInterval) {
                this.setupAutoRefresh();
            }

            this.updateStatus({ systemHealth: 'healthy' });
            console.log('Board Intelligence Service initialized successfully');
            return true;

        } catch (error) {
            console.error('Failed to initialize Board Intelligence Service:', error);
            this.updateStatus({ 
                contextConverter: 'error',
                ollamaService: 'error',
                systemHealth: 'unhealthy'
            });
            return false;
        }
    }

    /**
     * Get current system status
     */
    getStatus(): Observable<IntelligenceStatus> {
        return this.statusSubject.asObservable();
    }

    /**
     * Get current insights
     */
    getInsights(): Observable<BoardInsight[]> {
        return this.insightsSubject.asObservable();
    }

    /**
     * Generate comprehensive board analysis
     */
    async generateBoardAnalysis(options: {
        focusArea?: string;
        priority?: string;
        templateType?: string;
        forceRefresh?: boolean;
    } = {}): Promise<BoardInsight[]> {
        try {
            // Refresh context if needed
            if (options.forceRefresh || !this.currentContext) {
                this.currentContext = await this.contextConverter.convertToLLMContext(true);
                this.updateStatus({ lastContextUpdate: new Date() });
            }

            // Check if Ollama is available
            const status = this.statusSubject.value;
            if (status.ollamaService !== 'ready') {
                console.warn('Ollama service not ready, returning cached insights');
                return this.insightsSubject.value;
            }

            // Generate insights using Ollama
            const request: InsightRequest = {
                context: this.currentContext,
                focusArea: options.focusArea as any,
                priority: options.priority as any,
                templateType: options.templateType as any
            };

            const recommendations = await this.ollamaService.generateBoardRecommendations(request);
            
            // Convert recommendations to insights
            const insights = this.convertRecommendationsToInsights(recommendations);
            
            // Update insights and status
            this.insightsSubject.next(insights);
            this.updateStatus({ lastAnalysis: new Date() });

            console.log(`Generated ${insights.length} board insights`);
            return insights;

        } catch (error) {
            console.error('Error generating board analysis:', error);
            throw error;
        }
    }

    /**
     * Get workspace context summary
     */
    async getContextSummary(): Promise<any> {
        if (!this.currentContext) {
            this.currentContext = await this.contextConverter.convertToLLMContext();
        }

        return {
            metadata: this.currentContext.metadata,
            summary: {
                totalDataPoints: this.currentContext.metadata.totalDataPoints,
                confidenceScore: this.currentContext.metadata.confidenceScore,
                lastUpdated: this.currentContext.metadata.lastUpdated,
                workspaceFiles: this.currentContext.workspace.structure.totalFiles,
                researchPapers: this.currentContext.research.papers.length,
                activeStrategies: this.currentContext.enterprise.strategies.length,
                databases: this.currentContext.databases.length,
                currentInsights: this.currentContext.insights.length,
                actionableItems: this.currentContext.actionableItems.length
            },
            healthIndicators: {
                dataFreshness: this.calculateDataFreshness(),
                systemIntegration: this.calculateSystemIntegration(),
                decisionReadiness: this.calculateDecisionReadiness()
            }
        };
    }

    /**
     * Refresh context and regenerate insights
     */
    async refreshIntelligence(): Promise<void> {
        try {
            console.log('Refreshing board intelligence...');
            
            // Refresh context
            this.currentContext = await this.contextConverter.convertToLLMContext(true);
            this.updateStatus({ lastContextUpdate: new Date() });

            // Regenerate insights
            await this.generateBoardAnalysis({ forceRefresh: false });
            
            console.log('Board intelligence refreshed successfully');

        } catch (error) {
            console.error('Error refreshing board intelligence:', error);
            this.updateStatus({ systemHealth: 'degraded' });
        }
    }

    /**
     * Get specific recommendations for a focus area
     */
    async getRecommendationsForArea(area: string, templateType: string = 'executive-summary'): Promise<BoardRecommendation[]> {
        if (!this.currentContext) {
            this.currentContext = await this.contextConverter.convertToLLMContext();
        }

        const status = this.statusSubject.value;
        if (status.ollamaService !== 'ready') {
            throw new Error('Ollama service not available for generating recommendations');
        }

        const request: InsightRequest = {
            context: this.currentContext,
            focusArea: area as any,
            templateType: templateType as any
        };

        return await this.ollamaService.generateBoardRecommendations(request);
    }

    /**
     * Shutdown the service
     */
    async shutdown(): Promise<void> {
        console.log('Shutting down Board Intelligence Service...');
        
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }

        this.statusSubject.complete();
        this.insightsSubject.complete();
        
        console.log('Board Intelligence Service shut down');
    }

    // Private helper methods

    private updateStatus(updates: Partial<IntelligenceStatus>): void {
        const current = this.statusSubject.value;
        this.statusSubject.next({ ...current, ...updates });
    }

    private async generateInitialInsights(): Promise<void> {
        try {
            if (!this.currentContext) {
                return;
            }

            // Generate basic insights from context data
            const insights: BoardInsight[] = [];

            // Strategic insight
            if (this.currentContext.enterprise.strategies.length > 0) {
                insights.push({
                    id: `insight-strategic-${Date.now()}`,
                    type: 'strategic',
                    title: 'Strategic Initiatives Status',
                    description: `${this.currentContext.enterprise.strategies.length} active strategic initiatives identified with varying progress levels`,
                    confidence: 0.8,
                    priority: 'high',
                    dataPoints: ['enterprise.strategies', 'dao.governance'],
                    recommendations: [],
                    generatedAt: new Date(),
                    validUntil: new Date(Date.now() + 24 * 60 * 60 * 1000) // 24 hours
                });
            }

            // Operational insight
            if (this.currentContext.databases.length > 0) {
                const totalRecords = this.currentContext.databases.reduce((sum, db) => sum + db.recordCount, 0);
                insights.push({
                    id: `insight-operational-${Date.now()}`,
                    type: 'operational',
                    title: 'Data Infrastructure Status',
                    description: `${this.currentContext.databases.length} active databases managing ${totalRecords} total records`,
                    confidence: 0.9,
                    priority: 'medium',
                    dataPoints: ['databases', 'workspace.metrics'],
                    recommendations: [],
                    generatedAt: new Date(),
                    validUntil: new Date(Date.now() + 24 * 60 * 60 * 1000)
                });
            }

            // Research insight
            if (this.currentContext.research.papers.length > 0) {
                insights.push({
                    id: `insight-research-${Date.now()}`,
                    type: 'research',
                    title: 'Research Portfolio Status',
                    description: `${this.currentContext.research.papers.length} research papers with ${this.currentContext.research.models.length} cognitive models available`,
                    confidence: 0.85,
                    priority: 'high',
                    dataPoints: ['research.papers', 'research.models', 'research.trends'],
                    recommendations: [],
                    generatedAt: new Date(),
                    validUntil: new Date(Date.now() + 24 * 60 * 60 * 1000)
                });
            }

            this.insightsSubject.next(insights);

        } catch (error) {
            console.warn('Error generating initial insights:', error);
        }
    }

    private convertRecommendationsToInsights(recommendations: BoardRecommendation[]): BoardInsight[] {
        return recommendations.map(rec => ({
            id: `insight-${rec.category}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            type: rec.category as any,
            title: rec.title,
            description: rec.summary,
            confidence: rec.confidence,
            priority: rec.priority,
            dataPoints: [`Generated from ${rec.category} analysis`],
            recommendations: [rec],
            generatedAt: rec.generatedAt,
            validUntil: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 7 days
        }));
    }

    private setupAutoRefresh(): void {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }

        const intervalMs = this.config.autoRefreshInterval! * 60 * 1000;
        this.refreshInterval = setInterval(() => {
            this.refreshIntelligence().catch(error => {
                console.error('Auto-refresh failed:', error);
            });
        }, intervalMs);

        console.log(`Auto-refresh enabled: every ${this.config.autoRefreshInterval} minutes`);
    }

    private calculateDataFreshness(): number {
        if (!this.currentContext) return 0;

        const lastUpdate = this.currentContext.metadata.lastUpdated;
        const now = new Date();
        const ageHours = (now.getTime() - lastUpdate.getTime()) / (1000 * 60 * 60);

        // Fresher data gets higher score
        if (ageHours < 1) return 1.0;
        if (ageHours < 6) return 0.8;
        if (ageHours < 24) return 0.6;
        if (ageHours < 72) return 0.4;
        return 0.2;
    }

    private calculateSystemIntegration(): number {
        if (!this.currentContext) return 0;

        const factors = [
            this.currentContext.databases.length > 0 ? 0.3 : 0,
            this.currentContext.research.papers.length > 0 ? 0.2 : 0,
            this.currentContext.enterprise.strategies.length > 0 ? 0.2 : 0,
            this.currentContext.dao.proposals.length > 0 ? 0.15 : 0,
            this.currentContext.insights.length > 0 ? 0.15 : 0
        ];

        return factors.reduce((sum, factor) => sum + factor, 0);
    }

    private calculateDecisionReadiness(): number {
        if (!this.currentContext) return 0;

        const status = this.statusSubject.value;
        let readiness = 0;

        if (status.contextConverter === 'ready') readiness += 0.4;
        if (status.ollamaService === 'ready') readiness += 0.3;
        if (this.currentContext.insights.length > 0) readiness += 0.2;
        if (this.currentContext.actionableItems.length > 0) readiness += 0.1;

        return readiness;
    }
}

/**
 * Factory function to create and initialize Board Intelligence Service
 */
export async function createBoardIntelligenceService(config: BoardIntelligenceConfig): Promise<BoardIntelligenceService> {
    const service = new BoardIntelligenceService(config);
    await service.initialize();
    return service;
}
