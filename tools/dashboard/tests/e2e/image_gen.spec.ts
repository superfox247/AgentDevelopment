import { test, expect } from '@playwright/test';

test('Multi-model image generation flow', async ({ page }) => {
    test.setTimeout(90000);

    // 1. Navigate
    await page.goto('http://localhost:5173/');
    await page.click('text=Generator');
    await page.click('button:has-text("Image Generator")');

    // DEBUG: Check what models are rendered
    // Print all button text
    const buttons = page.locator('button');
    const count = await buttons.count();
    for (let i = 0; i < count; ++i) {
        const txt = await buttons.nth(i).textContent();
        console.log(`Button ${i}: ${txt}`);
    }

    // 2. Click Imagen 3
    // Use loose text match to be sure we find it if it exists
    const imagen3Btn = page.locator('button').filter({ hasText: 'Imagen 3' }).first();
    if (await imagen3Btn.isVisible()) {
        await imagen3Btn.click();
    } else {
        console.log("Imagen 3 button NOT found!");
    }

    // 3. Verify Selection Count
    // Should serve as a robust check
    await expect(page.locator('text=selected')).toContainText('2 selected');

    // 4. Enter Prompt
    await page.fill('textarea[placeholder*="Describe the image"]', 'A futuristic city with flying cars');

    // 5. Generate
    const generateBtn = page.locator('button:has-text("Generate All")');
    await expect(generateBtn).toBeEnabled();
    await generateBtn.click();

    // 6. Verify Results
    await expect(page.locator('text=Generating...').first()).toBeVisible();
    await expect(page.locator('text=Generating...')).toHaveCount(0, { timeout: 60000 });
    await expect(page.locator('img[alt="Generated"]')).toHaveCount(2);
});
