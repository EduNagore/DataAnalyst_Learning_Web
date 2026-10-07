import { expect, test } from '@playwright/test';

// Importante: con un `baseURL` que incluye un sub-path (el `base` de
// GitHub Pages), las rutas de `page.goto()` deben ser RELATIVAS sin barra
// inicial ('teoria/', no '/teoria/'); una barra inicial resuelve contra la
// raíz del dominio y se salta el sub-path, dando 404.

test('la portada carga y enlaza a las secciones principales', async ({ page }) => {
  await page.goto('./');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('data analyst');

  await expect(page.getByRole('link', { name: 'Empieza por los fundamentos' })).toBeVisible();
});

test('la navegación principal lleva a Teoría', async ({ page }) => {
  await page.goto('./');
  await page.getByRole('link', { name: 'Teoría', exact: true }).first().click();
  await expect(page).toHaveURL(/\/teoria\/$/);
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Teoría');
});

test('el toggle de tema cambia data-theme en <html>', async ({ page }) => {
  await page.goto('./');
  const html = page.locator('html');
  await page.getByRole('button', { name: 'Cambiar tema claro/oscuro' }).click();
  await expect(html).toHaveAttribute('data-theme', /light|dark/);
});

test('las páginas de secciones en construcción no devuelven 404', async ({ page }) => {
  for (const path of ['practica/', 'proyectos/', 'entrevistas/', 'radar/', 'glosario/']) {
    const response = await page.goto(path);
    expect(response?.status(), `${path} debería responder 200`).toBe(200);
  }
});

test('una lección de M04 se renderiza con objetivos, fuentes y navegación', async ({ page }) => {
  await page.goto('teoria/sql-i/03-joins-y-fan-out/');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Joins');
  await expect(page.getByText('Objetivos', { exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Fuentes' })).toBeVisible();
  await expect(page.getByRole('link', { name: /NULL, lógica trivaluada/ }).last()).toBeVisible();
});

test('la página de módulo lista sus 5 lecciones', async ({ page }) => {
  await page.goto('teoria/sql-i/');
  await expect(
    page.getByRole('listitem').filter({ hasText: 'Joins y la trampa del fan-out' }),
  ).toBeVisible();
});

test('la página de datos muestra el diccionario de Lumen', async ({ page }) => {
  await page.goto('datos/');
  await expect(page.getByRole('heading', { name: 'orders', exact: true })).toBeVisible();
});
