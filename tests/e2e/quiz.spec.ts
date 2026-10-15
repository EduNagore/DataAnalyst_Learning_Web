import { expect, test, type Page } from '@playwright/test';

// Las islas con client:visible se hidratan al entrar en el viewport; hay que
// esperar a que no queden islas sin hidratar antes de interactuar.
async function waitForHydration(page: Page) {
  await page.waitForFunction(() => !document.querySelector('astro-island[ssr]'));
}

test('el quiz de una lección corrige, explica y guarda la puntuación', async ({ page }) => {
  await page.goto('teoria/sql-i/02-agregacion-group-by-having/');
  const check = page.getByRole('button', { name: 'Comprobar respuestas' });
  await check.scrollIntoViewIfNeeded();
  await waitForHydration(page);

  // Pregunta 4 (verdadero/falso): AVG ignora NULL -> "Verdadero"
  await page.getByRole('radio', { name: 'Verdadero' }).check();
  await check.click();

  await expect(page.getByText(/\d+ de 6 \(\d+ %\)/)).toBeVisible();
  await expect(page.getByText('Correcta', { exact: true }).first()).toBeVisible();
  await expect(page.getByRole('link', { name: /Repasa esta sección/ }).first()).toBeVisible();

  // La puntuación queda en localStorage y se ve en /progreso/
  await page.goto('progreso/');
  await expect(page.getByText('Tests intentados')).toBeVisible();
  await expect(
    page.getByText('Tests intentados').locator('..').getByText('1', { exact: true }),
  ).toBeVisible();
});

test('el modo examen permite configurar, hacer el examen y ver el informe por módulo', async ({
  page,
}) => {
  await page.goto('practica/examen/');
  await waitForHydration(page);
  // Con muchos módulos, un examen aleatorio de todo el temario no tiene por qué incluir SQL I:
  // se deja marcado solo ese módulo para que el informe sea determinista.
  await expect(page.getByRole('button', { name: 'Empezar examen' })).toBeVisible(); // el banco se carga tras hidratar
  const modulos = page.locator('fieldset').first().getByRole('checkbox');
  for (let i = 0; i < (await modulos.count()); i++) {
    const caja = modulos.nth(i);
    const esSqlI = (await caja.locator('xpath=..').innerText()).includes('SQL I — Fundamentos');
    if ((await caja.isChecked()) !== esSqlI) await caja.setChecked(esSqlI);
  }
  await page.getByRole('button', { name: 'Empezar examen' }).click();
  await page.getByRole('button', { name: 'Comprobar respuestas' }).click();
  await expect(page.getByRole('heading', { name: 'Informe por módulo' })).toBeVisible();
  await expect(page.getByRole('cell', { name: 'SQL I — Fundamentos' })).toBeVisible();
});

test('una pregunta fallada entra en el repaso espaciado', async ({ page }) => {
  await page.goto('teoria/sql-i/04-null-y-case/');
  const check = page.getByRole('button', { name: 'Comprobar respuestas' });
  await check.scrollIntoViewIfNeeded();
  await waitForHydration(page);
  await check.click(); // todo sin responder = todo fallado

  await page.goto('practica/repaso/');
  // Caja 1 = vuelve a tocar mañana: entra en el sistema pero aún no está pendiente.
  await expect(page.getByText(/6 en total en tu sistema de repaso/)).toBeVisible();
});
