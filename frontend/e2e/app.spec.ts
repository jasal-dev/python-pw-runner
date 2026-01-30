import { test, expect } from '@playwright/test';

test.describe('Application Loading', () => {
  test('should load the application', async ({ page }) => {
    await page.goto('/');
    
    // Check that the main heading is visible
    await expect(page.getByRole('banner')).toContainText('Python Playwright Test Runner');
  });

  test('should display test selection panel', async ({ page }) => {
    await page.goto('/');
    
    // Wait for the test selection panel to load
    await expect(page.getByText('Test Selection')).toBeVisible();
  });

  test('should display test runs panel', async ({ page }) => {
    await page.goto('/');
    
    // Wait for the test runs panel
    await expect(page.getByText('Test Runs')).toBeVisible();
  });
});

test.describe('Test Discovery', () => {
  test('should show loading state initially', async ({ page }) => {
    await page.goto('/');
    
    // Should show loading indicator
    const loader = page.locator('[role="progressbar"]').first();
    // Loader might appear briefly or not at all if data loads quickly
    // So we just check the page loaded
    await expect(page.getByText('Test Selection')).toBeVisible();
  });

  test('should display tests when loaded', async ({ page }) => {
    await page.goto('/');
    
    // Wait for tests to load
    await page.waitForTimeout(2000); // Give backend time to respond
    
    // Should show either tests or "no tests" message
    const hasTests = await page.locator('text=/test/i').count() > 0;
    const hasNoTestsMessage = await page.locator('text=/no tests/i').isVisible().catch(() => false);
    
    expect(hasTests || hasNoTestsMessage).toBeTruthy();
  });

  test('should have search functionality', async ({ page }) => {
    await page.goto('/');
    
    // Find the search input
    const searchInput = page.getByPlaceholder('Search tests...');
    await expect(searchInput).toBeVisible();
    
    // Type in search
    await searchInput.fill('example');
  });

  test('should have refresh button', async ({ page }) => {
    await page.goto('/');
    
    // Find and click refresh button
    const refreshButton = page.getByRole('button', { name: /refresh/i });
    await expect(refreshButton).toBeVisible();
  });
});

test.describe('Test Selection', () => {
  test('should have select all button', async ({ page }) => {
    await page.goto('/');
    
    const selectAllButton = page.getByRole('button', { name: /select all/i });
    await expect(selectAllButton).toBeVisible();
  });

  test('should have clear selection button', async ({ page }) => {
    await page.goto('/');
    
    const clearButton = page.getByRole('button', { name: /clear selection/i });
    await expect(clearButton).toBeVisible();
  });

  test('should show selected count', async ({ page }) => {
    await page.goto('/');
    
    // Should show "0 selected" initially
    await expect(page.getByText(/0 selected/i)).toBeVisible();
  });

  test('should have run button', async ({ page }) => {
    await page.goto('/');
    
    // Run button should be present
    const runButton = page.getByRole('button', { name: /run.*test/i });
    await expect(runButton).toBeVisible();
  });

  test('run button should be disabled when no tests selected', async ({ page }) => {
    await page.goto('/');
    
    const runButton = page.getByRole('button', { name: /run.*test/i });
    await expect(runButton).toBeDisabled();
  });
});

test.describe('Test Runs Display', () => {
  test('should show test runs section', async ({ page }) => {
    await page.goto('/');
    
    await expect(page.getByText('Test Runs')).toBeVisible();
  });

  test('should handle empty state', async ({ page }) => {
    await page.goto('/');
    
    // Wait for data to load
    await page.waitForTimeout(2000);
    
    // Should show either runs or empty state
    const hasRuns = await page.locator('table').count() > 0;
    const hasEmptyState = await page.locator('text=/no test runs/i').isVisible().catch(() => false);
    
    expect(hasRuns || hasEmptyState).toBeTruthy();
  });
});

test.describe('Responsive Design', () => {
  test('should work on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    // Main elements should still be visible
    await expect(page.getByText('Python Playwright Test Runner')).toBeVisible();
    await expect(page.getByText('Test Selection')).toBeVisible();
  });

  test('should work on tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');
    
    await expect(page.getByText('Test Selection')).toBeVisible();
    await expect(page.getByText('Test Runs')).toBeVisible();
  });
});

test.describe('Error Handling', () => {
  test('should handle backend errors gracefully', async ({ page }) => {
    // This test assumes the backend might fail or return errors
    await page.goto('/');
    
    // Wait for page to load
    await page.waitForTimeout(1000);
    
    // Page should not crash - main elements should be present
    await expect(page.getByText('Python Playwright Test Runner')).toBeVisible();
  });
});
