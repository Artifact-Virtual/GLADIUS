/**
 * Simple test to verify all directors have required methods
 */

import {
    ChairpersonDirector,
    ChiefFinancialDirector,
    ChiefLegalDirector,
    ChiefOperationsDirector,
    ChiefStrategyDirector,
    ChiefTechnologyDirector
} from './src/implementations/directors-clean';

async function testDirectors() {
    console.log('Testing directors implementation...');
    
    const directors = [
        new ChairpersonDirector(),
        new ChiefStrategyDirector(),
        new ChiefOperationsDirector(),
        new ChiefTechnologyDirector(),
        new ChiefFinancialDirector(),
        new ChiefLegalDirector()
    ];
    
    for (const director of directors) {
        console.log(`\n=== Testing ${director.getRole()} ===`);
        
        // Test monitorDomainMetrics
        try {
            const metrics$ = director.monitorDomainMetrics();
            const metrics = await metrics$.toPromise();
            console.log(`✓ monitorDomainMetrics() works - Overall Score: ${metrics?.overallScore}`);
        } catch (error) {
            console.error(`✗ monitorDomainMetrics() failed:`, error);
        }
        
        // Test executeOversight
        try {
            const oversight = await director.executeOversight();
            console.log(`✓ executeOversight() works - Status: ${oversight.status}`);
        } catch (error) {
            console.error(`✗ executeOversight() failed:`, error);
        }
        
        // Test canBackup
        try {
            const canBackup = director.canBackup('CEO' as any);
            console.log(`✓ canBackup() works - Can backup CEO: ${canBackup}`);
        } catch (error) {
            console.error(`✗ canBackup() failed:`, error);
        }
    }
    
    console.log('\n=== Directors test completed! ===');
}

testDirectors().catch(console.error);
