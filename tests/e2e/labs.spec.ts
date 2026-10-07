import { expect, test, type Page } from '@playwright/test';

// DuckDB-WASM se descarga de jsDelivr y lee los Parquet por HTTP: damos margen.
test.setTimeout(120_000);

async function waitForHydration(page: Page) {
  await page.waitForFunction(() => !document.querySelector('astro-island[ssr]'));
}

/** Sustituye el contenido del editor CodeMirror por `sql` (una sola línea). */
async function typeInEditor(page: Page, sql: string) {
  const editor = page.locator('.cm-content').first();
  await editor.click();
  await page.keyboard.press('ControlOrMeta+A');
  await page.keyboard.insertText(sql);
}

test('lab SQL: una consulta correcta pasa todas las comprobaciones, incluida la oculta', async ({
  page,
}) => {
  await page.goto('practica/labs/sql-primeras-consultas/');
  await waitForHydration(page);

  await typeInEditor(
    page,
    "SELECT channel, COUNT(*) AS pedidos FROM orders WHERE order_date >= DATE '2025-01-01' AND order_date < DATE '2026-01-01' GROUP BY channel",
  );

  await page.getByRole('button', { name: 'Ejecutar' }).click();
  await expect(page.getByRole('status').filter({ hasText: /2 filas/ })).toBeVisible({
    timeout: 90_000,
  });

  await page.getByRole('button', { name: 'Comprobar' }).click();
  await expect(page.getByText('¡Lab superado!')).toBeVisible({ timeout: 90_000 });
  await expect(page.getByText('Funciona también con otros datos')).toBeVisible();
});

test('lab SQL: una respuesta incorrecta recibe un mensaje didáctico', async ({ page }) => {
  await page.goto('practica/labs/sql-primeras-consultas/');
  await waitForHydration(page);

  // Sin filtro de año: las cifras no coinciden.
  await typeInEditor(page, 'SELECT channel, COUNT(*) AS pedidos FROM orders GROUP BY channel');
  await page.getByRole('button', { name: 'Comprobar' }).click();
  await expect(page.getByText('El resultado coincide con el esperado')).toBeVisible({
    timeout: 90_000,
  });
  await expect(page.getByText(/Ninguna fila del resultado coincide/)).toBeVisible();
  await expect(page.getByText('¡Lab superado!')).toHaveCount(0);
});

test('lab SQL: las sentencias que no son de lectura se bloquean', async ({ page }) => {
  await page.goto('practica/labs/sql-primeras-consultas/');
  await waitForHydration(page);
  await typeInEditor(page, 'DROP VIEW orders');
  await page.getByRole('button', { name: 'Ejecutar' }).click();
  await expect(page.getByRole('alert')).toContainText('DROP');
});

test('lab Python: la solución de referencia pasa todos los tests (Pyodide en el navegador)', async ({
  page,
}) => {
  test.setTimeout(360_000);
  const { readFileSync } = await import('node:fs');
  const solution = readFileSync('src/content/labs/py-pandas-primeros-pasos/solution.py', 'utf-8');

  await page.goto('practica/labs/py-pandas-primeros-pasos/');
  await waitForHydration(page);
  const editor = page.locator('.cm-content').first();
  await editor.click();
  await page.keyboard.press('ControlOrMeta+A');
  await page.keyboard.insertText(solution);

  await page.getByRole('button', { name: 'Comprobar' }).click();
  await expect(page.getByText('¡Lab superado!')).toBeVisible({ timeout: 300_000 });
  await expect(page.getByText('Funciona también con otro conjunto de datos')).toBeVisible();
});

test('lab Python: el starter no pasa y muestra mensajes en español', async ({ page }) => {
  test.setTimeout(360_000);
  await page.goto('practica/labs/py-pandas-primeros-pasos/');
  await waitForHydration(page);
  await page.getByRole('button', { name: 'Comprobar' }).click();
  await expect(page.getByText('pedidos_por_canal_y_anio devuelve las columnas')).toBeVisible({
    timeout: 300_000,
  });
  await expect(page.getByText('¡Lab superado!')).toHaveCount(0);
});

test('lab Python con statsmodels/scipy: la solución del análisis A/B pasa en el navegador', async ({
  page,
}) => {
  test.setTimeout(420_000);
  const { readFileSync } = await import('node:fs');
  const solution = readFileSync('src/content/labs/py-ab-test-statsmodels/solution.py', 'utf-8');

  await page.goto('practica/labs/py-ab-test-statsmodels/');
  await waitForHydration(page);
  const editor = page.locator('.cm-content').first();
  await editor.click();
  await page.keyboard.press('ControlOrMeta+A');
  await page.keyboard.insertText(solution);
  await page.getByRole('button', { name: 'Comprobar' }).click();
  await expect(page.getByText('¡Lab superado!')).toBeVisible({ timeout: 400_000 });
});

test('SQL Playground: ejecuta un ejemplo y exporta el resultado', async ({ page }) => {
  await page.goto('practica/sql/');
  await waitForHydration(page);
  await page.getByRole('button', { name: /^Ejecutar/ }).click();
  await expect(page.getByRole('status').filter({ hasText: /filas/ })).toBeVisible({
    timeout: 90_000,
  });
  await expect(page.getByRole('columnheader', { name: 'pedidos' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Exportar CSV' })).toBeEnabled();
});
