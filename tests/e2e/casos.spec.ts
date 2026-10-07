import { expect, test, type Page } from '@playwright/test';

async function waitForHydration(page: Page) {
  await page.waitForFunction(() => !document.querySelector('astro-island[ssr]'));
}

async function answerNumeric(page: Page, value: string) {
  await page.getByLabel(/Tu respuesta \(número/).fill(value);
  await page.getByRole('button', { name: 'Comprobar' }).click();
}

test('caso guiado: se avanza paso a paso, se corrige y se llega al informe modelo', async ({
  page,
}) => {
  await page.goto('practica/casos/ventas-marzo/');
  await waitForHydration(page);

  await expect(page.getByText('Mensaje del stakeholder')).toBeVisible();

  // Una respuesta incorrecta no desbloquea el siguiente paso.
  await answerNumeric(page, '-3');
  await expect(page.getByText('No es correcto todavía')).toBeVisible();
  await expect(page.getByText('Paso 2 de 8')).toHaveCount(0);

  // Respuestas correctas (con coma decimal, como las escribiría un usuario español).
  await answerNumeric(page, '-11,47');
  await expect(page.getByText('Paso 2 de 8')).toBeVisible();
  await answerNumeric(page, '-10,74');

  await expect(page.getByText('Paso 3 de 8')).toBeVisible();
  await page.getByRole('radio', { name: 'Electrónica' }).check();
  await page.getByRole('button', { name: 'Comprobar' }).click();

  await expect(page.getByText('Paso 4 de 8')).toBeVisible();
  await answerNumeric(page, '-54,71');
  await expect(page.getByText('Paso 5 de 8')).toBeVisible();
  await answerNumeric(page, '0,99');

  await expect(page.getByText('Paso 6 de 8')).toBeVisible();
  await page.getByRole('radio', { name: /Rotura de stock de Electrónica/ }).check();
  await page.getByRole('button', { name: 'Comprobar' }).click();

  await expect(page.getByText('Paso 7 de 8')).toBeVisible();
  await answerNumeric(page, '1,6');

  await expect(page.getByText('Paso 8 de 8')).toBeVisible();
  await page
    .getByRole('textbox', { name: 'Tu respuesta' })
    .fill('La caída se debe a una rotura de stock de Electrónica.');
  await page.getByRole('button', { name: 'Continuar' }).click();

  await expect(page.getByRole('heading', { name: 'Tu informe' })).toBeVisible();
  await page.getByRole('button', { name: /Ver el informe modelo/ }).click();
  await expect(page.getByText('Informe modelo', { exact: true })).toBeVisible();
});

test('caso guiado: el progreso se conserva al recargar', async ({ page }) => {
  await page.goto('practica/casos/ventas-marzo/');
  await waitForHydration(page);
  await answerNumeric(page, '-11.47');
  await expect(page.getByText('Paso 2 de 8')).toBeVisible();
  await page.reload();
  await waitForHydration(page);
  await expect(page.getByText('Paso 2 de 8')).toBeVisible();
  await expect(page.getByText(/completado ✔/)).toBeVisible();
});

test('caso guiado: un paso SQL ejecuta consultas sobre Lumen', async ({ page }) => {
  test.setTimeout(120_000);
  await page.goto('practica/casos/ventas-marzo/');
  await waitForHydration(page);
  const editor = page.locator('.cm-content').first();
  await editor.click();
  await page.keyboard.insertText(
    "SELECT COUNT(*) AS pedidos FROM orders WHERE status <> 'cancelado'",
  );
  await page.getByRole('button', { name: 'Ejecutar' }).click();
  await expect(page.getByRole('status').filter({ hasText: /1 fila/ })).toBeVisible({
    timeout: 90_000,
  });
});
