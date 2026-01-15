#!/usr/bin/env node
/**
 * Simple Enhanced Intelligence Startup
 * Starts the Board Intelligence System with data integration and Ollama
 */

// Start the dashboard and board system
async function startSystem() {
    try {
        console.log('🚀 Starting Enhanced Board Intelligence System...\n');

        // Import and start the dashboard
        const { startDashboard } = await import('./src/services/dashboard');
        console.log('🖥️  Starting Dashboard on port 3001...');
        const server = startDashboard(3001);
        
        if (server) {
            console.log('✅ Dashboard started successfully');
            console.log('📊 Available endpoints:');
            console.log('   • Dashboard: http://localhost:3001');
            console.log('   • API Health: http://localhost:3001/api/health');
            console.log('   • Board Status: http://localhost:3001/api/board/status');
            console.log('   • Intelligence: http://localhost:3001/api/intelligence/status');
            console.log('   • Context Summary: http://localhost:3001/api/intelligence/context-summary');
            console.log('\n💡 The system is now processing workspace data from W:\\artifactvirtual\\data');
            console.log('🎯 Press Ctrl+C to shutdown gracefully...\n');
        } else {
            console.error('❌ Failed to start dashboard');
            process.exit(1);
        }

        // Setup graceful shutdown
        process.on('SIGINT', () => {
            console.log('\n🛑 Received SIGINT, shutting down gracefully...');
            process.exit(0);
        });

        process.on('SIGTERM', () => {
            console.log('\n🛑 Received SIGTERM, shutting down gracefully...');
            process.exit(0);
        });

    } catch (error) {
        console.error('💥 Fatal error during startup:', error);
        process.exit(1);
    }
}

// Run if this is the main module
if (require.main === module) {
    startSystem().catch(error => {
        console.error('💥 Unhandled error:', error);
        process.exit(1);
    });
}
