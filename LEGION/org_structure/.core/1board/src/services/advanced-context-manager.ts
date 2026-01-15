/**
 * Advanced Data Integration and Context Management Service
 * 
 * This service provides a meticulously designed abstraction layer for:
 * 1. Converting raw workspace data into LLM-readable JSON context
 * 2. Managing context updates without system disruption
 * 3. Providing versioned context schemas for backwards compatibility
 * 4. Optimizing data extraction and transformation processes
 * 5. Ensuring data quality and consistency
 */

import * as fs from 'fs';
import * as path from 'path';
import { CONTEXT_FORMAT_VERSION, LLMContext, LLMContextConverter } from './llm-context-converter';
import { OllamaService } from './ollama-service';
import { OllamaStartupService, createAndStartOllama } from './ollama-startup';

export interface ContextManagementConfig {
    workspaceRoot: string;
    cacheEnabled: boolean;
    cacheDirectory: string;
    maxCacheAge: number; // milliseconds
    contextVersion: string;
    autoRefreshInterval: number; // minutes
    compressionEnabled: boolean;
    validationEnabled: boolean;
    backupEnabled: boolean;
}

export interface ContextMetrics {
    lastUpdateTime: Date;
    contextSize: number;
    dataPointCount: number;
    processingTime: number;
    errorCount: number;
    validationScore: number;
    compressionRatio?: number;
}

export interface DataSourceHealth {
    source: string;
    isAvailable: boolean;
    lastChecked: Date;
    recordCount: number;
    dataQuality: number; // 0-1
    errorMessage?: string;
}

export interface ContextUpdate {
    version: string;
    timestamp: Date;
    changes: ContextChange[];
    affectedSources: string[];
    validationResult: ValidationResult;
    backupCreated: boolean;
}

export interface ContextChange {
    type: 'added' | 'modified' | 'removed';
    path: string;
    description: string;
    impact: 'low' | 'medium' | 'high';
}

export interface ValidationResult {
    isValid: boolean;
    score: number;
    issues: ValidationIssue[];
    warnings: string[];
}

export interface ValidationIssue {
    severity: 'error' | 'warning' | 'info';
    message: string;
    path: string;
    suggestion?: string;
}

/**
 * Advanced Context Management Service
 */
export class AdvancedContextManager {
    private config: ContextManagementConfig;
    private contextConverter: LLMContextConverter;
    private ollamaService: OllamaService;
    private ollamaStartup: OllamaStartupService | null = null;
    private currentContext: LLMContext | null = null;
    private contextCache: Map<string, any> = new Map();
    private metrics: ContextMetrics;
    private refreshTimer: NodeJS.Timeout | null = null;
    private isProcessing: boolean = false;
    private dataSourcesHealth: Map<string, DataSourceHealth> = new Map();

    constructor(config: Partial<ContextManagementConfig> = {}) {
        this.config = {
            workspaceRoot: 'w:\\artifactvirtual\\data',
            cacheEnabled: true,
            cacheDirectory: path.join(process.cwd(), '.context-cache'),
            maxCacheAge: 1800000, // 30 minutes
            contextVersion: CONTEXT_FORMAT_VERSION,
            autoRefreshInterval: 15, // 15 minutes
            compressionEnabled: true,
            validationEnabled: true,
            backupEnabled: true,
            ...config
        };

        this.contextConverter = new LLMContextConverter(this.config.workspaceRoot);
        this.ollamaService = new OllamaService();
        
        this.metrics = {
            lastUpdateTime: new Date(),
            contextSize: 0,
            dataPointCount: 0,
            processingTime: 0,
            errorCount: 0,
            validationScore: 0
        };

        this.ensureCacheDirectory();
    }

    /**
     * Initialize the context management system
     */
    async initialize(): Promise<boolean> {
        try {
            console.log('Initializing Advanced Context Manager...');

            // Start Ollama service
            console.log('Starting Ollama service...');
            this.ollamaStartup = await createAndStartOllama({
                model: 'llama3.2',
                logLevel: 'info',
                autoStart: true
            });

            const ollamaReady = await this.ollamaStartup.isOllamaRunning();
            if (!ollamaReady) {
                console.warn('Ollama service not ready, continuing with limited functionality');
            }

            // Perform initial health check
            await this.checkDataSourcesHealth();

            // Generate initial context
            await this.refreshContext();

            // Start auto-refresh if enabled
            if (this.config.autoRefreshInterval > 0) {
                this.startAutoRefresh();
            }

            console.log('Advanced Context Manager initialized successfully');
            return true;

        } catch (error) {
            console.error('Failed to initialize Advanced Context Manager:', error);
            return false;
        }
    }

    /**
     * Refresh the context with comprehensive error handling and optimization
     */
    async refreshContext(force: boolean = false): Promise<ContextUpdate> {
        if (this.isProcessing && !force) {
            throw new Error('Context refresh already in progress');
        }

        this.isProcessing = true;
        const startTime = Date.now();
        let contextUpdate: ContextUpdate;

        try {
            console.log('Starting context refresh...');

            // Check if cached context is still valid
            if (!force && this.isCacheValid()) {
                console.log('Using cached context');
                this.isProcessing = false;
                return this.createUpdateFromCache();
            }

            // Create backup if enabled
            let backupCreated = false;
            if (this.config.backupEnabled && this.currentContext) {
                backupCreated = await this.createContextBackup();
            }

            // Check data source health
            await this.checkDataSourcesHealth();

            // Generate new context
            const newContext = await this.contextConverter.convertToLLMContext();
            
            // Validate the new context
            const validationResult = this.config.validationEnabled ? 
                await this.validateContext(newContext) : 
                { isValid: true, score: 1.0, issues: [], warnings: [] };

            if (!validationResult.isValid) {
                throw new Error(`Context validation failed: ${validationResult.issues.map(i => i.message).join(', ')}`);
            }

            // Detect changes
            const changes = this.detectChanges(this.currentContext, newContext);

            // Update metrics
            const processingTime = Date.now() - startTime;
            this.updateMetrics(newContext, processingTime, validationResult.score);

            // Cache the new context
            if (this.config.cacheEnabled) {
                await this.cacheContext(newContext);
            }

            // Update current context
            this.currentContext = newContext;

            contextUpdate = {
                version: this.config.contextVersion,
                timestamp: new Date(),
                changes,
                affectedSources: this.getAffectedSources(changes),
                validationResult,
                backupCreated
            };

            console.log(`Context refreshed successfully in ${processingTime}ms`);
            return contextUpdate;

        } catch (error) {
            this.metrics.errorCount++;
            console.error('Error refreshing context:', error);
            throw error;
        } finally {
            this.isProcessing = false;
        }
    }

    /**
     * Get the current LLM context
     */
    getCurrentContext(): LLMContext | null {
        return this.currentContext;
    }

    /**
     * Get context optimized for specific use case
     */
    async getOptimizedContext(useCase: 'analysis' | 'reporting' | 'decision-making' | 'full'): Promise<LLMContext | null> {
        if (!this.currentContext) {
            await this.refreshContext();
        }

        if (!this.currentContext) {
            return null;
        }

        switch (useCase) {
            case 'analysis':
                return this.createAnalysisContext(this.currentContext);
            case 'reporting':
                return this.createReportingContext(this.currentContext);
            case 'decision-making':
                return this.createDecisionContext(this.currentContext);
            default:
                return this.currentContext;
        }
    }

    /**
     * Generate insights using Ollama with the current context
     */    async generateInsights(
        _prompt: string, 
        contextType: 'analysis' | 'reporting' | 'decision-making' | 'full' = 'full'
    ): Promise<string> {
        try {
            const context = await this.getOptimizedContext(contextType);
            if (!context) {
                throw new Error('No context available for insight generation');
            }
            
            const recommendations = await this.ollamaService.generateBoardRecommendations({
                context,
                focusArea: 'strategic',
                templateType: 'executive-summary'
            });
            
            return recommendations.map(rec => rec.summary).join('\n\n');
        } catch (error) {
            console.error('Error generating insights:', error);
            throw error;
        }
    }

    /**
     * Get system health and metrics
     */
    getSystemHealth() {
        return {
            contextManager: {
                isProcessing: this.isProcessing,
                lastUpdate: this.metrics.lastUpdateTime,
                errorCount: this.metrics.errorCount,
                validationScore: this.metrics.validationScore
            },
            ollama: this.ollamaStartup ? this.ollamaStartup.getHealthStatus() : null,
            dataSources: Array.from(this.dataSourcesHealth.values()),
            metrics: this.metrics
        };
    }

    /**
     * Shutdown the context manager
     */
    async shutdown(): Promise<void> {
        console.log('Shutting down Advanced Context Manager...');

        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }

        if (this.ollamaStartup) {
            await this.ollamaStartup.stopOllama();
        }

        console.log('Advanced Context Manager shut down successfully');
    }

    // Private helper methods

    private ensureCacheDirectory(): void {
        if (this.config.cacheEnabled && !fs.existsSync(this.config.cacheDirectory)) {
            fs.mkdirSync(this.config.cacheDirectory, { recursive: true });
        }
    }

    private isCacheValid(): boolean {
        if (!this.config.cacheEnabled || !this.currentContext) {
            return false;
        }

        const cacheAge = Date.now() - this.metrics.lastUpdateTime.getTime();
        return cacheAge < this.config.maxCacheAge;
    }

    private async createContextBackup(): Promise<boolean> {
        try {
            const backupPath = path.join(this.config.cacheDirectory, `context-backup-${Date.now()}.json`);
            fs.writeFileSync(backupPath, JSON.stringify(this.currentContext, null, 2));
            return true;
        } catch (error) {
            console.error('Error creating context backup:', error);
            return false;
        }
    }

    private async checkDataSourcesHealth(): Promise<void> {
        const sources = [
            { name: 'research_data', path: path.join(this.config.workspaceRoot, 'real_research') },
            { name: 'enterprise_data', path: path.join(this.config.workspaceRoot, 'enterprise') },
            { name: 'dao_data', path: path.join(this.config.workspaceRoot, 'dao') },
            { name: 'databases', path: this.config.workspaceRoot }
        ];

        for (const source of sources) {
            try {
                const exists = fs.existsSync(source.path);
                const stats = exists ? fs.statSync(source.path) : null;
                
                this.dataSourcesHealth.set(source.name, {
                    source: source.name,
                    isAvailable: exists,
                    lastChecked: new Date(),
                    recordCount: exists && stats?.isDirectory() ? fs.readdirSync(source.path).length : 0,
                    dataQuality: exists ? 1.0 : 0.0
                });
            } catch (error) {
                this.dataSourcesHealth.set(source.name, {
                    source: source.name,
                    isAvailable: false,
                    lastChecked: new Date(),
                    recordCount: 0,
                    dataQuality: 0.0,
                    errorMessage: String(error)
                });
            }
        }
    }

    private async validateContext(context: LLMContext): Promise<ValidationResult> {
        const issues: ValidationIssue[] = [];
        const warnings: string[] = [];
        let score = 1.0;

        // Validate required fields
        if (!context.metadata) {
            issues.push({
                severity: 'error',
                message: 'Missing metadata section',
                path: 'metadata'
            });
            score -= 0.2;
        }

        if (!context.workspace) {
            issues.push({
                severity: 'error',
                message: 'Missing workspace section',
                path: 'workspace'
            });
            score -= 0.2;
        }

        // Validate data completeness
        if (context.research?.papers && context.research.papers.length === 0) {
            warnings.push('No research papers found');
            score -= 0.1;
        }

        if (context.databases && context.databases.length === 0) {
            warnings.push('No database contexts found');
            score -= 0.1;
        }

        return {
            isValid: issues.filter(i => i.severity === 'error').length === 0,
            score: Math.max(0, score),
            issues,
            warnings
        };
    }

    private detectChanges(oldContext: LLMContext | null, newContext: LLMContext): ContextChange[] {
        const changes: ContextChange[] = [];

        if (!oldContext) {
            changes.push({
                type: 'added',
                path: 'context',
                description: 'Initial context created',
                impact: 'high'
            });
            return changes;
        }

        // Compare research papers
        const oldPaperCount = oldContext.research?.papers?.length || 0;
        const newPaperCount = newContext.research?.papers?.length || 0;
        
        if (newPaperCount > oldPaperCount) {
            changes.push({
                type: 'added',
                path: 'research.papers',
                description: `Added ${newPaperCount - oldPaperCount} research papers`,
                impact: 'medium'
            });
        }

        // Compare database contexts
        const oldDbCount = oldContext.databases?.length || 0;
        const newDbCount = newContext.databases?.length || 0;
        
        if (newDbCount !== oldDbCount) {
            changes.push({
                type: newDbCount > oldDbCount ? 'added' : 'removed',
                path: 'databases',
                description: `Database context changed: ${oldDbCount} -> ${newDbCount}`,
                impact: 'medium'
            });
        }

        return changes;
    }

    private getAffectedSources(changes: ContextChange[]): string[] {
        const sources = new Set<string>();
        
        for (const change of changes) {
            if (change.path.startsWith('research')) {
                sources.add('research_data');
            } else if (change.path.startsWith('enterprise')) {
                sources.add('enterprise_data');
            } else if (change.path.startsWith('dao')) {
                sources.add('dao_data');
            } else if (change.path.startsWith('databases')) {
                sources.add('databases');
            }
        }
        
        return Array.from(sources);
    }

    private updateMetrics(context: LLMContext, processingTime: number, validationScore: number): void {
        this.metrics = {
            lastUpdateTime: new Date(),
            contextSize: JSON.stringify(context).length,
            dataPointCount: this.countDataPoints(context),
            processingTime,
            errorCount: this.metrics.errorCount,
            validationScore
        };
    }

    private countDataPoints(context: LLMContext): number {
        let count = 0;
        
        count += context.research?.papers?.length || 0;
        count += context.enterprise?.kpis?.length || 0;
        count += context.databases?.length || 0;
        count += context.insights?.length || 0;
        count += context.actionableItems?.length || 0;
        
        return count;
    }

    private async cacheContext(context: LLMContext): Promise<void> {
        try {
            const cachePath = path.join(this.config.cacheDirectory, 'current-context.json');
            fs.writeFileSync(cachePath, JSON.stringify(context, null, 2));
        } catch (error) {
            console.error('Error caching context:', error);
        }
    }

    private createUpdateFromCache(): ContextUpdate {
        return {
            version: this.config.contextVersion,
            timestamp: this.metrics.lastUpdateTime,
            changes: [],
            affectedSources: [],
            validationResult: { isValid: true, score: 1.0, issues: [], warnings: [] },
            backupCreated: false
        };
    }

    private createAnalysisContext(context: LLMContext): LLMContext {
        return {
            ...context,
            research: context.research,
            databases: context.databases,
            insights: context.insights
        };
    }

    private createReportingContext(context: LLMContext): LLMContext {
        return {
            ...context,
            enterprise: context.enterprise,
            workspace: context.workspace,
            metadata: context.metadata
        };
    }

    private createDecisionContext(context: LLMContext): LLMContext {
        return {
            ...context,
            actionableItems: context.actionableItems,
            insights: context.insights,
            enterprise: context.enterprise
        };
    }

    private createContextSummary(context: LLMContext): any {
        return {
            metadata: context.metadata,
            workspace: {
                fileCount: context.workspace?.structure?.totalFiles || 0,
                directoryCount: context.workspace?.structure?.totalDirectories || 0
            },
            research: {
                paperCount: context.research?.papers?.length || 0,
                modelCount: context.research?.models?.length || 0
            },
            enterprise: {
                kpiCount: context.enterprise?.kpis?.length || 0,
                strategyCount: context.enterprise?.strategies?.length || 0
            },
            databaseCount: context.databases?.length || 0,
            insightCount: context.insights?.length || 0,
            actionItemCount: context.actionableItems?.length || 0
        };
    }

    private startAutoRefresh(): void {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }

        this.refreshTimer = setInterval(async () => {
            try {
                console.log('Auto-refreshing context...');
                await this.refreshContext();
            } catch (error) {
                console.error('Auto-refresh failed:', error);
            }
        }, this.config.autoRefreshInterval * 60 * 1000);

        console.log(`Auto-refresh started (interval: ${this.config.autoRefreshInterval} minutes)`);
    }
}

/**
 * Factory function to create and initialize the context manager
 */
export async function createAdvancedContextManager(config?: Partial<ContextManagementConfig>): Promise<AdvancedContextManager> {
    const manager = new AdvancedContextManager(config);
    await manager.initialize();
    return manager;
}
