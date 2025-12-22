import { test, expect } from '@playwright/test';

test('loads the dashboard', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('Nomisma')).toBeVisible();
});

test('health endpoint responds', async ({ request }) => {
    const baseUrl = process.env.API_BASE_URL || 'http://localhost:8000';
    const response = await request.get(`${baseUrl}/health`);

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body).toEqual({ status: 'healthy' });
});
