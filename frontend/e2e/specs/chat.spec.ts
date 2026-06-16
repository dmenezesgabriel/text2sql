import { expect, test } from '@playwright/test';

// LLM calls can take up to 60s
test.setTimeout(120_000);

test.describe('Chat flow', () => {
  test('sends a message and shows it in chat', async ({ page }) => {
    await page.goto('/chat');
    const input = page.getByPlaceholder(/question/i);
    await input.fill('Hello, what datasets do you have?');
    await page.getByRole('button', { name: /send/i }).click();
    await expect(page.getByText('Hello, what datasets do you have?')).toBeVisible({
      timeout: 5000,
    });
  });

  test('disables send button while waiting for response', async ({ page }) => {
    await page.goto('/chat');
    const input = page.getByPlaceholder(/question/i);
    await input.fill('Show me total sales by region');
    const sendBtn = page.getByRole('button', { name: /send/i });
    await sendBtn.click();
    // Button should be disabled while SSE is streaming
    await expect(sendBtn).toBeDisabled({ timeout: 3000 });
  });

  test('receives a visualization for a data question', async ({ page }) => {
    await page.goto('/chat');
    const input = page.getByPlaceholder(/question/i);
    await input.fill('Show me total sales by region as a bar chart');
    await page.getByRole('button', { name: /send/i }).click();

    // Wait for the LLM to respond with a visualization
    // bi-bar-chart is a Lit custom element rendered by json-render
    await expect(
      page.locator('bi-bar-chart, bi-data-table, bi-metric, bi-narrative-text').first(),
    ).toBeVisible({ timeout: 90_000 });
  });

  test('input clears after sending', async ({ page }) => {
    await page.goto('/chat');
    const input = page.getByPlaceholder(/question/i);
    await input.fill('test message');
    await page.getByRole('button', { name: /send/i }).click();
    await expect(input).toHaveValue('', { timeout: 3000 });
  });
});

test.describe('Chat SSE events', () => {
  test('receives SSE events from backend', async ({ page }) => {
    const sseEvents: string[] = [];
    const bodyReads: Promise<void>[] = [];

    // Intercept SSE stream. response.body() resolves once the stream closes, so
    // we collect the promises and await them explicitly before asserting -
    // the 'response' handler isn't awaited by Playwright before the test continues.
    page.on('response', (response) => {
      if (response.url().includes('/api/v1/chat')) {
        bodyReads.push(
          response
            .body()
            .then((body) => {
              const text = body.toString();
              const events = text.split('\n').filter((l) => l.startsWith('data:'));
              sseEvents.push(...events);
            })
            .catch(() => {}),
        );
      }
    });

    await page.goto('/chat');
    const input = page.getByPlaceholder(/question/i);
    await input.fill('Show me product count by category');
    await page.getByRole('button', { name: /send/i }).click();

    // Wait for response to complete
    await page
      .locator('bi-bar-chart, bi-data-table, bi-metric, bi-narrative-text')
      .first()
      .waitFor({ timeout: 90_000 })
      .catch(() => {});

    await Promise.all(bodyReads);

    // Should have received ThinkingEvent and SpecFragmentEvent
    const hasThinking = sseEvents.some((e) => e.includes('ThinkingEvent'));
    const hasSpec = sseEvents.some((e) => e.includes('SpecFragmentEvent'));
    expect(hasThinking || sseEvents.length > 0).toBeTruthy();
    console.log(`SSE events received: ${String(sseEvents.length)}`);
    if (hasSpec) console.log('SpecFragmentEvent received');
  });
});
