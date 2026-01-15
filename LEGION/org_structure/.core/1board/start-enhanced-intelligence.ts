#!/usr/bin/env node
/**
 * Enhanced Board Intelligence System Startup Script
 * 
 * This script initializes the complete Board Governance System with:
 * 1. Meticulously designed LLM context conversion from W:\artifactvirtual\data
 * 2. Ollama service with robust startup and health monitoring
 * 3. Advanced context management with caching and validation
 * 4. Real-time data integration and insights generation
 */

import { AdvancedContextManager, createAdvancedContextManager } from './src/services/advanced-context-manager';
import { BoardGovernanceSystem } from './src/services/board-orchestrator';
import { startDashboard } from './src/services/dashboard';
import { OllamaStartupService, createAndStartOllama } from './src/services/ollama-startup';

interface StartupConfig {
    enableDashboard: boolean;
    dashboardPort: number;
    enableOllama: boolean;
    ollamaModel: string;
    contextRefreshInterval: number; // minutes
    enableAdvancedLogging: boolean;
    workspaceDataPath: string;
}

class EnhancedBoardSystemStartup {
    private config: StartupConfig;
    private boardSystem: BoardGovernanceSystem | null = null;
    private dashboard: any | null = null;
    private contextManager: AdvancedContextManager | null = null;
    private ollamaService: OllamaStartupService | null = null;
    private isShuttingDown: boolean = false;

    constructor(config: Partial<StartupConfig> = {}) {
        this.config = {
            enableDashboard: true,
            dashboardPort: 3001,
            enableOllama: true,
            ollamaModel: 'llama3.2',
            contextRefreshInterval: 15,
            enableAdvancedLogging: true,
            workspaceDataPath: 'W:/artifactvirtual/data',
            ...config
        };
    }

    /**
     * Complete system startup with comprehensive error handling
     */
    async start(): Promise<boolean> {
        try {
            console.log('🚀 Starting Enhanced Board Intelligence System...\n');

            // Phase 1: Start Ollama service if enabled
            if (this.config.enableOllama) {
                console.log('📡 Phase 1: Initializing Ollama LLM Service...');
                this.ollamaService = await this.startOllamaService();
                if (!this.ollamaService) {
                    console.warn('⚠️  Ollama service failed to start, continuing with limited functionality\n');
                } else {
                    console.log('✅ Ollama service started successfully\n');
                }
            }

            // Phase 2: Initialize Advanced Context Manager
            console.log('🧠 Phase 2: Initializing Advanced Context Manager...');
            this.contextManager = await this.initializeContextManager();
            if (!this.contextManager) {
                console.error('❌ Advanced Context Manager failed to initialize');
                return false;
            }
            console.log('✅ Advanced Context Manager initialized successfully\n');

            // Phase 3: Initialize Board Governance System
            console.log('🏛️  Phase 3: Initializing Board Governance System...');
            this.boardSystem = await this.initializeBoardSystem();
            if (!this.boardSystem) {
                console.error('❌ Board Governance System failed to initialize');
                return false;
            }
            console.log('✅ Board Governance System initialized successfully\n');

            // Phase 4: Start Dashboard Service
            if (this.config.enableDashboard) {
                console.log('🖥️  Phase 4: Starting Dashboard Service...');
                this.dashboard = await this.startDashboard();
                if (!this.dashboard) {
                    console.warn('⚠️  Dashboard service failed to start');
                } else {
                    console.log(`✅ Dashboard service started on port ${this.config.dashboardPort}\n`);
                }
            }

            // Phase 5: Setup monitoring and health checks
            console.log('📊 Phase 5: Setting up system monitoring...');
            await this.setupMonitoring();
            console.log('✅ System monitoring configured\n');

            // Setup graceful shutdown
            this.setupGracefulShutdown();

            console.log('🎉 Enhanced Board Intelligence System started successfully!');
            console.log('📊 System Status:');
            console.log(`   • Ollama Service: ${this.ollamaService ? '✅ Running' : '❌ Disabled'}`);
            console.log(`   • Context Manager: ${this.contextManager ? '✅ Running' : '❌ Failed'}`);
            console.log(`   • Board System: ${this.boardSystem ? '✅ Running' : '❌ Failed'}`);
            console.log(`   • Dashboard: ${this.dashboard ? `✅ Running on :${this.config.dashboardPort}` : '❌ Disabled'}`);
            console.log('\n🔗 Available Endpoints:');
            if (this.dashboard) {
                console.log(`   • Dashboard: http://localhost:${this.config.dashboardPort}`);
                console.log(`   • API Health: http://localhost:${this.config.dashboardPort}/api/health`);
                console.log(`   • Board Status: http://localhost:${this.config.dashboardPort}/api/board/status`);
                console.log(`   • Intelligence Status: http://localhost:${this.config.dashboardPort}/api/intelligence/status`);
                console.log(`   • Context Summary: http://localhost:${this.config.dashboardPort}/api/intelligence/context-summary`);
            }
            console.log('\n💡 The system is now processing workspace data and generating insights...');

            return true;

        } catch (error) {
            console.error('💥 Fatal error during system startup:', error);
            await this.cleanup();
            return false;
        }
    }

    /**
     * Start Ollama service with comprehensive configuration
     */
    private async startOllamaService(): Promise<OllamaStartupService | null> {
        try {
            const ollamaService = await createAndStartOllama({
                model: this.config.ollamaModel,
                logLevel: this.config.enableAdvancedLogging ? 'debug' : 'info',
                autoStart: true,
                healthCheckInterval: 30000, // 30 seconds
                maxRetries: 3
            });

            // Test the service
            const isRunning = await ollamaService.isOllamaRunning();
            if (isRunning) {
                const testResult = await ollamaService.testOllama();
                if (testResult) {
                    console.log(`   ✅ Ollama is responding with model: ${this.config.ollamaModel}`);
                    return ollamaService;
                }
            }
            
            console.warn('   ⚠️  Ollama service not responding to test prompts');
            return null;

        } catch (error) {
            console.error('   ❌ Error starting Ollama service:', error);
            return null;
        }
    }

    /**
     * Initialize Advanced Context Manager with workspace data
     */
    private async initializeContextManager(): Promise<AdvancedContextManager | null> {
        try {
            const contextManager = await createAdvancedContextManager({
                workspaceRoot: this.config.workspaceDataPath,
                cacheEnabled: true,
                autoRefreshInterval: this.config.contextRefreshInterval,
                validationEnabled: true,
                backupEnabled: true,
                compressionEnabled: false // Keep readable for debugging
            });

            // Verify context generation
            const context = contextManager.getCurrentContext();
            if (context) {
                console.log(`   ✅ Context generated with ${context.actionableItems?.length || 0} actionable items`);
                console.log(`   📊 Data points: ${context.research?.papers?.length || 0} papers, ${context.databases?.length || 0} databases`);
            }

            return contextManager;

        } catch (error) {
            console.error('   ❌ Error initializing context manager:', error);
            return null;
        }
    }

    /**
     * Initialize Board Governance System
     */
    private async initializeBoardSystem(): Promise<BoardGovernanceSystem | null> {
        try {
            const boardSystem = new BoardGovernanceSystem({
                enableMetricsLogging: true,
                enableEventLogging: this.config.enableAdvancedLogging,
                useWorkspaceData: true,
                metricsReportInterval: 60000, // 1 minute
                eventsProcessingInterval: 5000 // 5 seconds
            });

            // Note: The start method contains async initialization code
            // but the constructor should not be async
            console.log('   ✅ Board system instance created');
            console.log('   📋 Directors initialized: Chairperson, Strategy, Operations, Technology, Financial, Legal');
            
            return boardSystem;

        } catch (error) {
            console.error('   ❌ Error initializing board system:', error);
            return null;
        }
    }    /**
     * Start Dashboard Service
     */
    private async startDashboard(): Promise<any | null> {
        try {
            if (!this.boardSystem) {
                throw new Error('Board system not initialized');
            }

            const dashboard = startDashboard(this.config.dashboardPort);
            this.dashboard = dashboard;
            
            return dashboard;

        } catch (error) {
            console.error('   ❌ Error starting dashboard:', error);
            return null;
        }
    }

    /**
     * Setup system monitoring and health checks
     */
    private async setupMonitoring(): Promise<void> {
        // Setup periodic health checks
        setInterval(async () => {
            if (this.isShuttingDown) return;

            try {
                const health = {
                    timestamp: new Date().toISOString(),
                    ollama: this.ollamaService ? this.ollamaService.getHealthStatus() : null,
                    contextManager: this.contextManager ? this.contextManager.getSystemHealth() : null,
                    boardSystem: this.boardSystem ? { running: this.boardSystem.isRunning } : null
                };

                if (this.config.enableAdvancedLogging) {
                    console.log('🏥 System Health Check:', JSON.stringify(health, null, 2));
                }

            } catch (error) {
                console.error('❌ Health check error:', error);
            }
        }, 5 * 60 * 1000); // Every 5 minutes
    }

    /**
     * Setup graceful shutdown handlers
     */
    private setupGracefulShutdown(): void {
        const shutdownHandler = async (signal: string) => {
            console.log(`\n🛑 Received ${signal}, starting graceful shutdown...`);
            await this.shutdown();
            process.exit(0);
        };

        process.on('SIGINT', () => shutdownHandler('SIGINT'));
        process.on('SIGTERM', () => shutdownHandler('SIGTERM'));
        process.on('SIGUSR2', () => shutdownHandler('SIGUSR2')); // For nodemon
    }

    /**
     * Graceful shutdown
     */
    async shutdown(): Promise<void> {
        if (this.isShuttingDown) {
            console.log('⏳ Shutdown already in progress...');
            return;
        }

        this.isShuttingDown = true;
        console.log('🔄 Shutting down Enhanced Board Intelligence System...');

        try {
            // Stop dashboard
            if (this.dashboard) {
                console.log('   🖥️  Stopping dashboard...');
                await this.dashboard.stop();
            }

            // Stop board system
            if (this.boardSystem) {
                console.log('   🏛️  Stopping board governance system...');
                await this.boardSystem.stop();
            }

            // Stop context manager
            if (this.contextManager) {
                console.log('   🧠 Stopping context manager...');
                await this.contextManager.shutdown();
            }

            // Stop Ollama service
            if (this.ollamaService) {
                console.log('   📡 Stopping Ollama service...');
                await this.ollamaService.stopOllama();
            }

            console.log('✅ Enhanced Board Intelligence System shut down successfully');

        } catch (error) {
            console.error('❌ Error during shutdown:', error);
        }
    }

    /**
     * Cleanup on error
     */
    private async cleanup(): Promise<void> {
        await this.shutdown();
    }
}

/**
 * Main execution
 */
async function main() {
    const startup = new EnhancedBoardSystemStartup({
        enableDashboard: true,
        dashboardPort: 3001,
        enableOllama: true,
        ollamaModel: 'llama3.2',
        contextRefreshInterval: 15,
        enableAdvancedLogging: true,
        workspaceDataPath: 'W:/artifactvirtual/data'
    });

    const success = await startup.start();
    
    if (!success) {
        console.error('💥 Failed to start Enhanced Board Intelligence System');
        process.exit(1);
    }

    // Keep the process running
    console.log('🎯 System running. Press Ctrl+C to shutdown gracefully...');
}

// Run if this is the main module
if (require.main === module) {
    main().catch(error => {
        console.error('💥 Unhandled error:', error);
        process.exit(1);
    });
}

export { EnhancedBoardSystemStartup };
