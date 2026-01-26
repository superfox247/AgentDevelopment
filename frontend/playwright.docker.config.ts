import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for E2E tests against the Docker stack.
 * 
 * This config assumes:
 * - Docker containers are running (make dev-up)
 * - Dashboard API is running on port 8010
 * - Frontend is built and served (or running via preview)
 * 
 * Usage:
 *   pnpm exec playwright test --config=playwright.docker.config.ts
 */
export default defineConfig({
    testDir: './tests/e2e',
    fullyParallel: true,
    forbidOnly: !!process.env.CI,
    retries: process.env.CI ? 2 : 0,
    workers: process.env.CI ? 1 : undefined,
    reporter: process.env.CI ? 'github' : 'list',
    timeout: 30 * 1000, // 30 seconds per test
    use: {
        baseURL: process.env.FRONTEND_URL || 'http://localhost:5173',
        trace: 'on-first-retry',
        screenshot: 'only-on-failure',
        video: 'retain-on-failure',
    },
    projects: [
        {
            name: 'chromium',
            use: { ...devices['Desktop Chrome'] },
        },
    ],
    // Health check before running tests
    globalSetup: require.resolve('./tests/e2e/global-setup.ts'),
    // Expect API to be available
    expect: {
        timeout: 5000,
    },
});
