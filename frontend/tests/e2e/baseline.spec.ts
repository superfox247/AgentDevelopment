import { test, expect } from '@playwright/test';

test.describe('Dashboard baseline', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:5173/');
    });

    test('app loads with header and agent selector', async ({ page }) => {
        await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
        await expect(page.getByText(/Chat with Researcher or Customer Service/)).toBeVisible();
        await expect(page.getByLabel('Select agent')).toBeVisible();
    });

    test('chat input and send are present', async ({ page }) => {
        await expect(page.getByPlaceholder('Type a message...')).toBeVisible();
        await expect(page.getByRole('button', { name: 'Send' })).toBeVisible();
    });

    test('agent options are Researcher and Customer Service', async ({ page }) => {
        const select = page.getByLabel('Select agent');
        await expect(select).toBeVisible();

        const options = select.locator('option');
        await expect(options).toHaveText(['Researcher', 'Customer Service']);
        const optionValues = await options.evaluateAll((nodes) =>
            nodes.map((node) => (node as HTMLOptionElement).value),
        );
        expect(optionValues).toEqual(['researcher_agent', 'customer_service_agent']);
    });
});
