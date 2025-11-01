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
    await expect(page.getByText('ADMIN')).toBeVisible();
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
    
    // Fill form
    await page.getByLabel(/competition id/i).fill('e2e-test-comp');
    await page.getByLabel(/competition name/i).fill('E2E Test Competition');
    await page.getByLabel(/registration open date/i).fill('2025-01-01');
    await page.getByLabel(/start date/i).fill('2025-02-01');
    await page.getByLabel(/end date/i).fill('2025-03-01');
    
    // Submit
    await page.getByRole('button', { name: /create/i }).click();
    
    // Should redirect to home and see the new competition
    await expect(page).toHaveURL('/');
    await expect(page.getByText('E2E Test Competition')).toBeVisible();
  });

  test('member cannot access create page', async ({ page }) => {
    // Logout and login as member
    await page.getByRole('button', { name: /logout/i }).click();
    await page.goto('/login');
    await page.getByLabel(/email address/i).fill('member@example.com');
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Try to access create page
    await page.goto('/competitions/new');
    
    // Should show access denied or redirect
    const url = page.url();
    expect(url).not.toContain('/competitions/new');
  });
});
