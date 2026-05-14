import { expect, test } from '@playwright/test';

test('chat happy path with citation popover', async ({ page }) => {
  await page.goto('/documents');

  await page.setInputFiles('input[type="file"]', {
    name: 'note.md',
    mimeType: 'text/markdown',
    buffer: Buffer.from('# Capitals\n\nParis is the capital of France.'),
  });
  await page.getByRole('button', { name: 'Upload' }).click();
  await expect(page.getByText('note.md')).toBeVisible({ timeout: 30_000 });

  await page.goto('/');
  await page.getByRole('textbox').fill('What is the capital of France?');
  await page.getByRole('button', { name: 'Send' }).click();

  const pill = page.locator('button:has-text("1")').first();
  await expect(pill).toBeVisible({ timeout: 60_000 });
  await pill.click();

  await expect(page.getByText(/Paris is the capital/).last()).toBeVisible();
});


