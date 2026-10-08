import { expect, test } from '@playwright/test';

test('SimpsonExplorer: la paradoja aparece con la mezcla real y desaparece con la misma mezcla', async ({
  page,
}) => {
  await page.goto('teoria/eda/03-paradoja-de-simpson/');
  const explorer = page
    .getByRole('figure')
    .filter({ hasText: 'Explorador de la paradoja de Simpson' });
  await explorer.scrollIntoViewIfNeeded();
  await expect(explorer.getByRole('status')).toContainText('Paradoja de Simpson');

  const sliders = explorer.getByRole('slider');
  await sliders.nth(0).fill('50');
  await sliders.nth(1).fill('50');
  await expect(explorer.getByRole('status')).not.toContainText('Paradoja de Simpson');
  await expect(explorer.getByRole('status')).toContainText('gana Escritorio');
});

test('VegaChart: el cuarteto de Anscombe se dibuja (cuatro paneles)', async ({ page }) => {
  await page.goto('teoria/eda/02-relaciones-correlacion-y-segmentacion/');
  const chart = page.getByRole('img', { name: /cuarteto de Anscombe/ });
  await chart.scrollIntoViewIfNeeded();
  await expect(chart.locator('svg')).toBeVisible({ timeout: 30_000 });
  await expect(chart.locator('svg g.mark-symbol').first()).toBeVisible();
});
