/**
 * Main entry point for the Autonomous Board Governance System
 * Starts both the board system and the dashboard
 */

import { boardSystem } from './services/board-orchestrator';
import { startDashboard } from './services/dashboard';

const PORT = 3000;

async function main() {
    console.log('===============================================');
    console.log('  Artifact Virtual - Board Governance System');
    console.log('===============================================');
    
    try {
        // Start the board system
        console.log('Starting board governance system...');
        await boardSystem.start();
        console.log('Board governance system started successfully.');
        
        // Start the dashboard
        console.log(`Starting dashboard on port ${PORT}...`);
        const server = startDashboard(PORT);
        console.log(`Dashboard running at http://localhost:${PORT}`);
        
        // Handle graceful shutdown
        const shutdown = async () => {
            console.log('Shutting down...');
            boardSystem.stop();
            server.close();
            console.log('System stopped.');
            process.exit(0);
        };
        
        process.on('SIGINT', shutdown);
        process.on('SIGTERM', shutdown);
        
        console.log('System is running. Press Ctrl+C to stop.');
    } catch (error) {
        console.error('Error starting system:', error);
        process.exit(1);
    }
}

// Run the main function
main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});
