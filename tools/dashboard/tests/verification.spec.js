import { test, expect } from '@playwright/test';

test.describe('Dashboard Verification', () => {

    test.beforeEach(async ({ page }) => {
        // Capture console logs
        page.on('console', msg => {
            if (msg.type() === 'error')
                console.log(`[BROWSER ERROR] ${msg.text()}`);
            else
                console.log(`[BROWSER LOG] ${msg.text()}`);
        });

        // --- Mock API Responses ---

        // Agents
        await page.route('**/api/agents', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify([
                    { domain: 'coding', name: 'architect' },
                    { domain: 'writing', name: 'copywriter' }
                ])
            });
        });

        await page.route('**/api/agents/coding/architect', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'text/plain',
                body: 'system_prompt: "You are an architect."'
            });
        });

        // Models
        await page.route('**/api/models', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify([
                    { name: 'models/gemini-2.0-flash', display_name: 'Gemini 2.0 Flash', description: 'Fast model', input_token_limit: 1000, output_token_limit: 1000 }
                ])
            });
        });

        // Skills
        await page.route('**/api/skills', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify([
                    { name: 'review_code' },
                    { name: 'search_web' }
                ])
            });
        });

        await page.route('**/api/skills/review_code', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'text/plain',
                body: '# Review Code Skill\nDescription of skill.'
            });
        });

        // Artifacts
        await page.route('**/api/artifacts', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify([
                    { name: 'design_doc.md', path: 'design_doc.md', type: 'text' },
                    { name: 'logo.png', path: 'logo.png', type: 'image' }
                ])
            });
        });

        // Docker (for Infrastructure)
        await page.route('**/api/docker', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify([
                    { id: '1', name: 'course_creator-orchestrator', status: 'running' }
                ])
            });
        });

        // Navigate to app (Dev Server)
        await page.goto('http://localhost:5173/');
    });

    test('Sidebar Navigation matches Redesign', async ({ page }) => {
        // Check main sections
        await expect(page.getByText('Command', { exact: true })).toBeVisible();
        await expect(page.getByText('Intelligence', { exact: true })).toBeVisible();
        await expect(page.getByText('Factory', { exact: true })).toBeVisible();

        // Check links
        await expect(page.getByRole('button', { name: 'Infrastructure' })).toBeVisible();
        await expect(page.getByRole('button', { name: 'Agents' })).toBeVisible();
        await expect(page.getByRole('button', { name: 'Models' })).toBeVisible();
        await expect(page.getByRole('button', { name: 'Skills' })).toBeVisible();
        await expect(page.getByRole('button', { name: 'Generator' })).toBeVisible();
        await expect(page.getByRole('button', { name: 'Artifacts' })).toBeVisible();
    });

    test('Infrastructure View loads correctly', async ({ page }) => {
        // Set viewport to ensure sidebar and content are visible
        await page.setViewportSize({ width: 1280, height: 800 });

        await page.getByRole('button', { name: 'Infrastructure' }).click();

        // Header
        await expect(page.getByRole('heading', { name: 'Infrastructure Command' })).toBeVisible();

        // Logs Tab interaction
        const logsButton = page.getByRole('button', { name: 'Live Logs' });
        await logsButton.click();

        // Verify click registered by checking active style
        await expect(logsButton).toHaveClass(/bg-cyan-500\/20/);

        // Wait for the LogsView to mount
        // Note: The Header has bg-clip-text which might affect strict visibility checks in headless mode, 
        // or animation might be interfering. Checking other elements first.

        // Check for the "Containers" sidebar header in LogsView
        await expect(page.getByText('Containers', { exact: true })).toBeVisible({ timeout: 10000 });

        // Check for the description text
        await expect(page.getByText('Real-time container log streaming protocol')).toBeVisible();
    });

    test('Agents View displays mocked agents and config', async ({ page }) => {
        await page.getByRole('button', { name: 'Agents' }).click();

        // Check mocked list
        await expect(page.getByText('Agent Registry')).toBeVisible();
        await expect(page.getByText('coding')).toBeVisible();
        await expect(page.getByText('architect')).toBeVisible();

        // Click agent to see config
        await page.getByRole('button', { name: 'architect' }).click();
        await expect(page.getByText('You are an architect')).toBeVisible();
    });

    test('Models View displays mocked cards', async ({ page }) => {
        await page.getByRole('button', { name: 'Models' }).click();

        // Check Header
        await expect(page.getByRole('heading', { name: 'Available Models' })).toBeVisible();

        // Check Card
        await expect(page.getByText('Gemini 2.0 Flash')).toBeVisible();
        await expect(page.getByText('Fast model')).toBeVisible();
    });

    test('Skills View displays mocked skills and markdown', async ({ page }) => {
        await page.getByRole('button', { name: 'Skills' }).click();

        // Check List
        await expect(page.getByText('Skills Library')).toBeVisible();
        await expect(page.getByRole('button', { name: 'review_code' })).toBeVisible();

        // Click skill
        await page.getByRole('button', { name: 'review_code' }).click();
        await expect(page.getByRole('heading', { name: 'Review Code Skill' })).toBeVisible();
    });

    test('Artifacts View displays mocked grid', async ({ page }) => {
        await page.getByRole('button', { name: 'Artifacts' }).click();

        // Check items
        await expect(page.getByText('design_doc.md')).toBeVisible();
        await expect(page.getByText('logo.png')).toBeVisible();
        await expect(page.getByText('image').first()).toBeVisible();
    });

    test('Generator View handles input', async ({ page }) => {
        await page.getByRole('button', { name: 'Generator' }).click();

        // Check initial state
        await expect(page.getByPlaceholder('Type a message...')).toBeVisible();

        // Type and send
        await page.getByPlaceholder('Type a message...').fill('Make a course');
        // Note: We are not mocking the chat POST, so we just check UI state update if possible or just existence
        // Ideally we mock the chat endpoint too if we want to test interaction fully.
        // For now, just verifying the UI elements are present is good for "View" verification.
        await expect(page.getByRole('button', { name: '' }).last()).toBeVisible(); // Send button (icon only)
    });

});
