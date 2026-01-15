/**
 * Board Intelligence Startup Script
 * Initializes the complete board governance system with LLM intelligence
 */

import { BoardGovernanceSystem } from './src/services/board-orchestrator';

/**
 * Main startup function
 */
async function startBoardIntelligenceSystem(): Promise<void> {
    console.log('🚀 Starting Board Intelligence System with LLM & Ollama Integration...\n');

    try {
        // Initialize the board governance system with intelligence enabled
        const boardSystem = new BoardGovernanceSystem({
            enableMetricsLogging: true,
            enableEventLogging: true,
            metricsReportInterval: 30000, // 30 seconds for demo
            eventsProcessingInterval: 5000, // 5 seconds
            useWorkspaceData: true, // Enable W:\artifactvirtual\data integration
            dataSourcePaths: [
                'W:/artifactvirtual/data/real_research',
                'W:/artifactvirtual/data/enterprise',
                'W:/artifactvirtual/data/dao',
                'W:/artifactvirtual/debates'
            ]
        });

        console.log('📊 Board system configured with workspace data integration');

        // Start the board system (this will automatically initialize Board Intelligence)
        await boardSystem.start();

        console.log('✅ Board Governance System started successfully!');
        console.log('🤖 Board Intelligence Service with LLM analysis is running');
        console.log('📈 Real-time metrics collection from W:\\artifactvirtual\\data');
        console.log('🔗 Ollama integration for AI-powered insights');
        console.log('\n--- System Status ---');

        // Display initial status
        await displaySystemStatus(boardSystem);

        // Generate initial board analysis
        console.log('\n🧠 Generating initial board analysis with LLM...');
        try {
            const insights = await boardSystem.generateBoardAnalysis({
                templateType: 'executive-summary',
                forceRefresh: true
            });
            
            console.log(`✨ Generated ${insights.length} initial insights:`);
            insights.slice(0, 3).forEach((insight, index) => {
                console.log(`  ${index + 1}. [${insight.priority.toUpperCase()}] ${insight.title}`);
                console.log(`     ${insight.description.substring(0, 100)}...`);
            });
        } catch (error) {
            console.log('⚠️  LLM analysis not available:', error.message);
        }

        // Display available endpoints
        console.log('\n🌐 Available API Endpoints:');
        console.log('  - GET  /api/intelligence/status        - Board Intelligence status');
        console.log('  - POST /api/intelligence/analyze       - Generate LLM analysis');
        console.log('  - POST /api/intelligence/recommendations - Get area-specific recommendations');
        console.log('  - GET  /api/intelligence/context-summary - Workspace context summary');
        console.log('  - POST /api/intelligence/refresh        - Refresh intelligence');
        console.log('  - GET  /api/intelligence/insights       - Current insights');
        console.log('  - GET  /api/intelligence/templates      - Available templates');
        console.log('  - GET  /api/intelligence/focus-areas    - Available focus areas');

        // Set up periodic status updates
        setInterval(async () => {
            try {
                await displaySystemStatus(boardSystem);
            } catch (error) {
                console.error('Error displaying status:', error);
            }
        }, 60000); // Every minute

        // Set up graceful shutdown
        process.on('SIGINT', async () => {
            console.log('\n🛑 Shutting down Board Intelligence System...');
            await boardSystem.stop();
            console.log('✅ System shut down gracefully');
            process.exit(0);
        });

        console.log('\n⏰ System running... (Press Ctrl+C to stop)');

    } catch (error) {
        console.error('❌ Failed to start Board Intelligence System:', error);
        process.exit(1);
    }
}

/**
 * Display current system status
 */
async function displaySystemStatus(boardSystem: BoardGovernanceSystem): Promise<void> {
    try {
        const isRunning = boardSystem.isRunning;
        const metrics = boardSystem.getCurrentMetrics();
        const intelligenceStatus = boardSystem.getBoardIntelligenceStatus();
        const workspaceStatus = await boardSystem.getWorkspaceDataStatus();

        console.log(`\n📊 System Status at ${new Date().toLocaleTimeString()}`);
        console.log(`  🔄 Running: ${isRunning ? '✅' : '❌'}`);
        console.log(`  🧠 Intelligence: ${intelligenceStatus.available ? '✅' : '❌'} ${intelligenceStatus.available ? '(Ollama: ' + intelligenceStatus.status?.ollamaService + ')' : ''}`);
        console.log(`  💾 Workspace Data: ${workspaceStatus.databases?.length || 0} databases, ${workspaceStatus.researchFiles?.length || 0} research files`);
        console.log(`  📈 Metrics: ${metrics.totalMetrics} total, confidence: ${(metrics.confidence * 100).toFixed(1)}%`);

        const insights = boardSystem.getCurrentBoardInsights();
        if (insights.length > 0) {
            const highPriorityCount = insights.filter(i => i.priority === 'high' || i.priority === 'critical').length;
            console.log(`  💡 Active Insights: ${insights.length} (${highPriorityCount} high priority)`);
        }

    } catch (error) {
        console.log(`  ⚠️  Status check failed: ${error.message}`);
    }
}

/**
 * Test Ollama connectivity
 */
async function testOllamaConnectivity(): Promise<boolean> {
    try {
        const axios = require('axios');
        const response = await axios.get('http://localhost:11434/api/tags', { timeout: 5000 });
        console.log('🤖 Ollama server is running');
        
        const models = response.data.models || [];
        if (models.length > 0) {
            console.log(`📚 Available models: ${models.map((m: any) => m.name).join(', ')}`);
        } else {
            console.log('📥 No models found, will download llama3.2 automatically');
        }
        
        return true;
    } catch (error) {
        console.log('⚠️  Ollama server not available - LLM features will be limited');
        console.log('   To enable full LLM capabilities, run: ollama serve');
        return false;
    }
}

/**
 * Display startup banner
 */
function displayBanner(): void {
    console.log('');
    console.log('╔══════════════════════════════════════════════════════════════════╗');
    console.log('║                    ARTIFACT VIRTUAL BOARD                       ║');
    console.log('║                  Intelligence System v2.0                       ║');
    console.log('║                                                                  ║');
    console.log('║  🧠 LLM-Powered Board Governance                                ║');
    console.log('║  📊 Real-time Workspace Data Integration                        ║');
    console.log('║  🤖 Ollama AI Analysis & Recommendations                        ║');
    console.log('║  📈 Automated Metrics & Insights                               ║');
    console.log('╚══════════════════════════════════════════════════════════════════╝');
    console.log('');
}

// Start the system
if (require.main === module) {
    displayBanner();
    
    // Test Ollama first
    testOllamaConnectivity().then(() => {
        // Start the board intelligence system
        startBoardIntelligenceSystem().catch(error => {
            console.error('❌ Fatal error:', error);
            process.exit(1);
        });
    });
}
