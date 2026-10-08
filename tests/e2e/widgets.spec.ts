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

test('DistributionExplorer: cambia de distribución y muestra media y varianza coherentes', async ({
  page,
}) => {
  await page.goto('teoria/estadistica-descriptiva/02-distribuciones-que-aparecen-en-negocio/');
  const explorer = page.getByRole('figure').filter({ hasText: 'Explorador de distribuciones' });
  await explorer.scrollIntoViewIfNeeded();
  await expect(explorer.getByRole('status')).toContainText('354,38');
  await explorer.getByRole('button', { name: 'Poisson' }).click();
  await expect(explorer.getByRole('button', { name: 'Poisson' })).toHaveAttribute(
    'aria-pressed',
    'true',
  );
  const stats = explorer.getByRole('status');
  await expect(stats).toContainText('12,00');
  await expect(stats).toContainText('3,46');
});

test('CoverageExplorer: simula 100 intervalos y reporta la cobertura', async ({ page }) => {
  await page.goto('teoria/inferencia/01-muestreo-error-estandar-e-intervalos-de-confianza/');
  const explorer = page
    .getByRole('figure')
    .filter({ hasText: 'Explorador de intervalos de confianza' });
  await explorer.scrollIntoViewIfNeeded();
  const resumen = explorer.locator('p[aria-live="polite"]');
  await expect(resumen).toContainText('de 100');
  const antes = await resumen.innerText();
  await explorer.getByRole('combobox', { name: 'Tamaño de cada muestra' }).selectOption('400');
  await explorer.getByRole('button', { name: 'Nuevas muestras' }).click();
  await expect(resumen).not.toHaveText(antes);
  const hits = Number((await resumen.innerText()).match(/(\d+) de 100/)?.[1]);
  expect(hits).toBeGreaterThan(85);
});

const lessonsWithCharts = [
  'teoria/eda/01-preguntas-y-analisis-univariante/',
  'teoria/eda/02-relaciones-correlacion-y-segmentacion/',
  'teoria/estadistica-descriptiva/04-ley-de-grandes-numeros-y-teorema-central-del-limite/',
  'teoria/visualizacion/01-percepcion-y-eleccion-del-grafico/',
  'teoria/visualizacion/02-gramatica-de-graficos-anotaciones-y-titulos/',
  'teoria/visualizacion/03-color-accesibilidad-e-incertidumbre/',
  'teoria/visualizacion/04-como-mienten-los-graficos-y-herramientas/',
  'teoria/inferencia/02-contrastes-p-valor-errores-y-potencia/',
];

for (const url of lessonsWithCharts) {
  test(`gráficos Vega-Lite de ${url} se dibujan sin errores`, async ({ page }) => {
    const errores: string[] = [];
    page.on('pageerror', (e) => errores.push(e.message));
    await page.goto(url);
    const charts = page.locator('div[role="img"][aria-label]:has(> div)');
    const n = await charts.count();
    expect(n).toBeGreaterThan(0);
    for (let i = 0; i < n; i++) {
      const chart = charts.nth(i);
      await chart.scrollIntoViewIfNeeded();
      await expect(chart.locator('svg').first()).toBeVisible({ timeout: 30_000 });
    }
    expect(errores).toEqual([]);
  });
}
