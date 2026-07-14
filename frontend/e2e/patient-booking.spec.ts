import { test, expect } from '@playwright/test';

test.describe('Patient Booking Flow', () => {
  test('Search doctor and view slots', async ({ page }) => {
    // Log console errors to see what goes wrong in the browser
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
    
    // Log console errors to see what goes wrong in the browser
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
    page.on('response', async response => {
      if (response.url().includes('/api/v1/')) {
        console.log(`API ${response.request().method()} ${response.url()} -> ${response.status()}`);
        if (response.status() >= 400) {
          console.log('ERROR BODY:', await response.text());
        }
      }
    });
    
    await page.goto('/register');
    
    // Generate a unique email
    const uniqueEmail = `patient${Date.now()}@example.com`;
    
    await page.fill('#full_name', 'Test Patient'); // full_name
    await page.fill('input[type="email"]', uniqueEmail);
    await page.fill('input[type="password"]', 'TestPass123!');
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await expect(page.locator('text=Patient Dashboard')).toBeVisible({ timeout: 10000 });

    // Navigate to doctors search
    await page.goto('/patient/doctors');
    
    // We should see doctors listed because we seeded the DB with slots!
    await expect(page.locator('text=Book Appointment').first()).toBeVisible({ timeout: 10000 });
    
    // Click book appointment to go to slot selection
    await page.locator('text=Book Appointment').first().click();
    
    // Wait for the slot selection page to load
    await expect(page.locator('text=Select a Time Slot')).toBeVisible({ timeout: 10000 });
    
    // Select the first available slot (we have 96 slots seeded, so there should be many)
    // Time slots have text like '09:00' and must not be disabled
    await page.locator('button:has-text(":"):not(:disabled)').first().click();
    
    // Should navigate to Booking Review
    await expect(page.locator('text=Review & Confirm')).toBeVisible({ timeout: 10000 });
    
    // Fill out the symptom form
    await page.fill('textarea', 'I have a mild headache and fever for the past 2 days.');
    
    // Click confirm booking
    await page.locator('button:has-text("Confirm Booking")').click();
    
    // Wait for booking confirmation and redirect (e.g. to appointment details or dashboard)
    await expect(page.locator('text=Appointment Confirmed').or(page.locator('text=Patient Dashboard'))).toBeVisible({ timeout: 15000 });
  });
});
