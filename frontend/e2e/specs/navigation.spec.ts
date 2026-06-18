import { expect, test } from '@playwright/test';

test.describe('Navigation', () => {
  test('home page loads with chat interface', async ({ page }) => {
    await page.goto('/');
    // / redirects to /chat
    await page.waitForURL(/\/chat$/);
    await expect(page.getByText('Generative Business Intelligence')).toBeVisible();
    await expect(page.getByPlaceholder(/question/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /send/i })).toBeVisible();
  });

  test('sidebar has New Chat button and nav links', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('button', { name: /new chat/i })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Datasets' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Questions' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Dashboards' })).toBeVisible();
  });

  test('navigates to datasets page', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('link', { name: 'Datasets' }).click();
    await expect(page).toHaveURL(/\/datasets/);
    await expect(page.getByText('Register a Dataset')).toBeVisible();
  });

  test('New Chat button navigates to /chat', async ({ page }) => {
    await page.goto('/datasets');
    await page.getByRole('button', { name: /new chat/i }).click();
    await expect(page).toHaveURL(/\/chat$/);
    await expect(page.getByPlaceholder(/question/i)).toBeVisible();
  });

  test('active nav link is highlighted', async ({ page }) => {
    await page.goto('/datasets');
    const datasetsLink = page.getByRole('link', { name: 'Datasets' });
    await expect(datasetsLink).toBeVisible();
    await page.getByRole('button', { name: /new chat/i }).click();
    await expect(page).toHaveURL(/\/chat$/);
  });
});
