import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { expect, test } from '@playwright/test';

/**
 * Ejecuta la solución de referencia de CADA lab SQL en el motor real del navegador
 * (DuckDB-WASM) y comprueba que supera todas sus comprobaciones, incluido el test oculto.
 * Garantiza que lo que `pytest` valida con DuckDB de CPython también funciona en WASM
 * (las versiones del motor pueden diferir).
 */
const labsDir = 'src/content/labs';
const sqlLabs = readdirSync(labsDir).filter((id) => existsSync(`${labsDir}/${id}/solution.sql`));

test.describe.configure({ mode: 'serial' });

for (const id of sqlLabs) {
  test(`solución de referencia de «${id}» en DuckDB-WASM`, async ({ page }) => {
    test.setTimeout(180_000);
    const solution = readFileSync(`${labsDir}/${id}/solution.sql`, 'utf-8');

    await page.goto(`practica/labs/${id}/`);
    await page.waitForFunction(() => !document.querySelector('astro-island[ssr]'));
    const editor = page.locator('.cm-content').first();
    await editor.click();
    await page.keyboard.press('ControlOrMeta+A');
    await page.keyboard.insertText(solution);

    await page.getByRole('button', { name: 'Comprobar' }).click();
    await expect(page.getByText('¡Lab superado!')).toBeVisible({ timeout: 150_000 });
  });

  test(`el starter de «${id}» NO supera la comprobación`, async ({ page }) => {
    test.setTimeout(180_000);
    await page.goto(`practica/labs/${id}/`);
    await page.waitForFunction(() => !document.querySelector('astro-island[ssr]'));
    await page.getByRole('button', { name: 'Comprobar' }).click();
    await expect(page.getByRole('tab', { name: /Comprobación (✘|✔)/ })).toBeVisible({
      timeout: 150_000,
    });
    await expect(page.getByText('¡Lab superado!')).toHaveCount(0);
  });
}
