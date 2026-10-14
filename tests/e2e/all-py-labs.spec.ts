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

// En serie (un solo navegador pesado a la vez), pero cada lab se reintenta dentro de su test: un fallo de red
// o de CPU puntual (cada lab descarga Pyodide y sus paquetes de un CDN) no debe saltarse el resto de la suite.
test.describe.configure({ mode: 'serial' });

for (const id of pyLabs) {
  test(`solución de referencia de «${id}» en Pyodide`, async ({ context }) => {
    test.setTimeout(420_000);
    const solution = readFileSync(`${labsDir}/${id}/solution.py`, 'utf-8');
    let ultimoError: unknown;
    for (let intento = 1; intento <= 3; intento++) {
      const page = await context.newPage();
      try {
        await page.goto(`practica/labs/${id}/`);
        await page.waitForFunction(() => !document.querySelector('astro-island[ssr]'));
        const editor = page.locator('.cm-content').first();
        await editor.click();
        await page.keyboard.press('ControlOrMeta+A');
        await page.keyboard.insertText(solution);
        await page.getByRole('button', { name: 'Comprobar' }).click();
        await expect(page.getByText('¡Lab superado!')).toBeVisible({ timeout: 100_000 });
        return;
      } catch (error) {
        ultimoError = error;
      } finally {
        await page.close();
      }
    }
    throw ultimoError;
  });
}
