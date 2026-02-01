import { FullConfig } from '@playwright/test';

/**
 * Global setup for E2E tests.
 * Verifies that required services are running before tests execute.
 */
async function globalSetup(_config: FullConfig) {
    const apiUrl = process.env.API_URL || 'http://localhost:8010';
    const frontendUrl = process.env.FRONTEND_URL || 'http://localhost:5173';
    const maxRetries = 30; // 60 seconds total (2s intervals)
    
    console.log('🔍 Checking service health before running tests...');
    
    // Check Dashboard API
    let apiHealthy = false;
    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await fetch(`${apiUrl}/health`);
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ Dashboard API is healthy: ${JSON.stringify(data)}`);
                apiHealthy = true;
                break;
            }
        } catch {
            // Service not ready yet
        }
        if (i < maxRetries - 1) {
            await new Promise(resolve => setTimeout(resolve, 2000));
            process.stdout.write('.');
        }
    }
    
    if (!apiHealthy) {
        console.error(`\n❌ Dashboard API (${apiUrl}) is not responding after ${maxRetries * 2} seconds`);
        console.error('   Make sure Docker stack is running: make dev-up');
        console.error('   And Dashboard API is running: uv run python dashboard_api/server.py');
        throw new Error('Dashboard API is not available');
    }
    
    // Check Frontend (optional - may not be needed if using built assets)
    let frontendHealthy = false;
    for (let i = 0; i < 10; i++) {
        try {
            const response = await fetch(frontendUrl);
            if (response.ok || response.status === 200) {
                console.log(`✅ Frontend is accessible at ${frontendUrl}`);
                frontendHealthy = true;
                break;
            }
        } catch {
            // Frontend not ready yet
        }
        if (i < 9) {
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
    }
    
    if (!frontendHealthy) {
        console.warn(`\n⚠️  Frontend (${frontendUrl}) is not accessible`);
        console.warn('   Tests may still run if frontend is served differently');
    }
    
    console.log('\n✅ All required services are ready. Starting tests...\n');
}

export default globalSetup;
