import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { expect, test } from '@playwright/test';

/**
 * Ejecuta la solución de referencia de cada lab Python en Pyodide (el motor real del navegador)
 * y comprueba que supera todos sus tests, incluido el oculto. Los labs con prueba propia en
 * `labs.spec.ts` se omiten aquí.
 */
const labsDir = 'src/content/labs';
const yaCubiertos = new Set(['py-pandas-primeros-pasos', 'py-ab-test-statsmodels']);
const pyLabs = readdirSync(labsDir).filter(
  (id) => existsSync(`${labsDir}/${id}/solution.py`) && !yaCubiertos.has(id),
);

test.describe.configure({ mode: 'serial' });

for (const id of pyLabs) {
  test(`solución de referencia de «${id}» en Pyodide`, async ({ page }) => {
    test.setTimeout(420_000);
    const solution = readFileSync(`${labsDir}/${id}/solution.py`, 'utf-8');

    await page.goto(`practica/labs/${id}/`);
    await page.waitForFunction(() => !document.querySelector('astro-island[ssr]'));
    const editor = page.locator('.cm-content').first();
    await editor.click();
    await page.keyboard.press('ControlOrMeta+A');
    await page.keyboard.insertText(solution);

    await page.getByRole('button', { name: 'Comprobar' }).click();
    await expect(page.getByText('¡Lab superado!')).toBeVisible({ timeout: 400_000 });
  });
}
