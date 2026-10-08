import { readdirSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { expect, test, type Page } from '@playwright/test';
import YAML from 'yaml';

// Resuelve cada caso guiado de principio a fin con las respuestas publicadas: si una respuesta,
// una opción o el flujo de pasos se rompe, el caso deja de poder completarse.
const DIR = path.join(process.cwd(), 'src', 'content', 'cases');
const CASES = readdirSync(DIR)
  .filter((f) => f.endsWith('.mdx'))
  .map((f) => ({
    id: f.replace(/\.mdx$/, ''),
    front: YAML.parse(readFileSync(path.join(DIR, f), 'utf-8').split('---')[1]),
  }));

async function waitForHydration(page: Page) {
  await page.waitForFunction(() => !document.querySelector('astro-island[ssr]'));
}

for (const { id, front } of CASES) {
  test(`caso «${id}»: se completa con las respuestas publicadas`, async ({ page }) => {
    test.setTimeout(120_000);
    await page.goto(`practica/casos/${id}/`);
    await waitForHydration(page);
    const total = front.steps.length;

    for (const [i, step] of front.steps.entries()) {
      await expect(page.getByText(`Paso ${i + 1} de ${total}`)).toBeVisible();
      if (step.answerType === 'numeric') {
        await page.getByLabel(/Tu respuesta \(número/).fill(String(step.answer).replace('.', ','));
        await page.getByRole('button', { name: 'Comprobar' }).click();
      } else if (step.answerType === 'single') {
        const option = step.options[Array.isArray(step.answer) ? step.answer[0] : step.answer];
        await page.getByRole('radio', { name: option, exact: true }).check();
        await page.getByRole('button', { name: 'Comprobar' }).click();
      } else if (step.answerType === 'multiple') {
        for (const a of step.answer as number[]) {
          await page.getByRole('checkbox', { name: step.options[a], exact: true }).check();
        }
        await page.getByRole('button', { name: 'Comprobar' }).click();
      } else {
        await page
          .getByRole('textbox', { name: 'Tu respuesta' })
          .fill('Respuesta de prueba del caso.');
        await page.getByRole('button', { name: 'Continuar' }).click();
      }
    }
    await expect(page.getByRole('heading', { name: 'Tu informe' })).toBeVisible();
  });
}
