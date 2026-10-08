import { expect, test } from '@playwright/test';

const WORKBOOKS = [
  'matrices-dinamicas-y-buscarx',
  'let-lambda-escenarios',
  'agrupar-y-pivotar',
  'auditoria-de-un-modelo',
  'verificar-el-trabajo-de-una-ia',
];

test('el índice de hojas de cálculo lista los cinco libros', async ({ page }) => {
  await page.goto('practica/hojas-de-calculo/');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Hojas de cálculo');
  for (const id of WORKBOOKS) {
    await expect(page.locator(`a[href$="/practica/hojas-de-calculo/${id}/"]`)).toHaveCount(1);
  }
});

for (const id of WORKBOOKS) {
  test(`el libro «${id}» tiene página y descargas válidas`, async ({ page, request }) => {
    await page.goto(`practica/hojas-de-calculo/${id}/`);
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    for (const name of ['Descargar el libro de trabajo', 'Descargar la solución']) {
      const href = await page.getByRole('link', { name }).getAttribute('href');
      expect(href).toMatch(/\.xlsx$/);
      const res = await request.get(href!);
      expect(res.ok()).toBeTruthy();
      expect((await res.body()).subarray(0, 2).toString()).toBe('PK'); // un .xlsx es un zip
    }
  });
}

test('una lección de hojas de cálculo enlaza a su libro de práctica', async ({ page }) => {
  await page.goto('teoria/hojas-de-calculo/01-tablas-estructuradas-y-formulas-dinamicas/');
  await expect(
    page.locator('a[href$="/practica/hojas-de-calculo/matrices-dinamicas-y-buscarx/"]'),
  ).toBeVisible();
});
