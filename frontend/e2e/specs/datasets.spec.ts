import { expect, test } from '@playwright/test';

test.describe('Datasets page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/datasets');
    await page.waitForLoadState('networkidle');
  });

  test('shows register dataset form', async ({ page }) => {
    await expect(page.getByText('Register a Dataset')).toBeVisible();
    await expect(page.getByPlaceholder('Dataset name')).toBeVisible();
    await expect(page.getByPlaceholder(/S3 URI/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /Register Dataset/i })).toBeVisible();
  });

  test('lists registered datasets from backend', async ({ page }) => {
    // Expects the 3 seeded datasets to be visible
    await expect(page.getByText('Registered Datasets')).toBeVisible();
    const rows = page.locator('table tbody tr');
    await expect(rows).toHaveCount(3);
  });

  test('shows dataset names and S3 locations', async ({ page }) => {
    // Use role=cell with exact match to avoid matching the URI cell too
    await expect(page.getByRole('cell', { name: 'sales', exact: true })).toBeVisible();
    await expect(page.getByRole('cell', { name: 'product', exact: true })).toBeVisible();
    await expect(page.getByRole('cell', { name: 'customer', exact: true })).toBeVisible();
    await expect(page.getByText(/s3:\/\/bi-data\/sales\.parquet/)).toBeVisible();
  });

  test('shows DuckDB view names for each dataset', async ({ page }) => {
    // View names follow pattern ds_{id_without_hyphens}
    const viewCells = page.locator('table tbody tr td:nth-child(2)');
    const count = await viewCells.count();
    for (let i = 0; i < count; i++) {
      const text = await viewCells.nth(i).textContent();
      expect(text).toMatch(/^ds_[0-9a-f]{32}$/);
    }
  });

  test('register button is disabled until both fields are filled', async ({ page }) => {
    const btn = page.getByRole('button', { name: /Register Dataset/i });
    // Button should be disabled when form is empty
    await expect(btn).toBeDisabled();
    // Fill name only - still disabled
    await page.getByPlaceholder('Dataset name').fill('test');
    await expect(btn).toBeDisabled();
    // Fill S3 URI too - button becomes enabled
    await page.getByPlaceholder(/S3 URI/i).fill('s3://bucket/file.parquet');
    await expect(btn).toBeEnabled();
  });
});
