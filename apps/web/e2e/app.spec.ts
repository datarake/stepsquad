import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('user can login with email in dev mode', async ({ page }) => {
    await page.goto('/login');
    
    // Check login form is visible
    await expect(page.getByRole('heading', { name: /sign in to stepsquad/i })).toBeVisible();
    
    // Enter email
    await page.getByLabel(/email address/i).fill('admin@stepsquad.com');
    
    // Submit form
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Should redirect to home page
    await expect(page).toHaveURL('/');
    
    // Should see user info in topbar
    await expect(page.getByText('admin@stepsquad.com')).toBeVisible();
    // Check for ADMIN role badge (more specific selector)
    await expect(page.locator('span:has-text("ADMIN")').filter({ hasText: /^ADMIN$/ })).toBeVisible();
  });

  test('user can logout', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.getByLabel(/email address/i).fill('admin@stepsquad.com');
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Wait for redirect
    await expect(page).toHaveURL('/');
    
    // Click logout
    await page.getByRole('button', { name: /logout/i }).click();
    
    // Should redirect to login
    await expect(page).toHaveURL('/login');
  });
});

test.describe('Competition Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto('/login');
    await page.getByLabel(/email address/i).fill('admin@stepsquad.com');
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL('/');
  });

  test('admin can see create competition button', async ({ page }) => {
    await expect(page.getByRole('link', { name: /create competition/i })).toBeVisible();
  });

  test('admin can create competition', async ({ page }) => {
    // Navigate to create page
    await page.getByRole('link', { name: /create competition/i }).click();
    await expect(page).toHaveURL('/competitions/new');
    
    // Generate unique competition ID to avoid conflicts
    const compId = 'e2e-' + Date.now();
    const compName = 'E2E Test Competition ' + Date.now();
    
    // Fill form
    await page.getByLabel(/competition id/i).fill(compId);
    await page.getByLabel(/competition name/i).fill(compName);
    await page.getByLabel(/registration open date/i).fill('2025-01-01');
    await page.getByLabel(/start date/i).fill('2025-02-01');
    await page.getByLabel(/end date/i).fill('2025-03-01');
    
    // Submit form (wait for button to be enabled)
    await page.getByRole('button', { name: /create/i }).waitFor({ state: 'visible' });
    await page.getByRole('button', { name: /create/i }).click();
    
    // Wait for navigation to home page (the form navigates after successful submission)
    await page.waitForURL('/', { timeout: 15000 });
    
    // Verify we're on home page
    await expect(page).toHaveURL('/');
    
    // Should see the new competition (using the unique name)
    await expect(page.getByText(compName)).toBeVisible({ timeout: 5000 });
  });

  test('member cannot access create page', async ({ page }) => {
    // Logout and login as member
    await page.getByRole('button', { name: /logout/i }).click();
    await expect(page).toHaveURL('/login');
    
    await page.getByLabel(/email address/i).fill('member@example.com');
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL('/');
    
    // Try to access create page directly
    await page.goto('/competitions/new');
    
    // Should show access denied message (not redirect to home)
    await expect(page.getByRole('heading', { name: /access denied/i })).toBeVisible();
    await expect(page.getByText("You don't have permission to access this page.")).toBeVisible();
  });
});
