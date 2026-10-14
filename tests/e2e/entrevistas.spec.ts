import { expect, test } from '@playwright/test';

test('la zona de entrevistas lista preguntas, SQL cronometrado y casos', async ({ page }) => {
  await page.goto('entrevistas/');
  await page.waitForLoadState('networkidle');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Entrevistas');
  await expect(page.getByText('150 de 150 preguntas')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'SQL cronometrado sobre Lumen' })).toBeVisible();
  await expect(
    page.getByRole('link', { name: /Investigar la caída de una métrica/ }),
  ).toBeVisible();
});

test('filtrar por tema y cambiar de idioma muestra la respuesta correspondiente', async ({
  page,
}) => {
  await page.goto('entrevistas/');
  await page.waitForLoadState('networkidle');
  await page.getByLabel('Tema', { exact: true }).selectOption('Conductuales');
  await expect(page.getByText('13 de 150 preguntas')).toBeVisible();
  await page.getByRole('button', { name: 'Mostrar respuesta' }).first().click();
  await expect(page.getByText('Respuesta modelo').first()).toBeVisible();
  await page.getByRole('button', { name: 'EN', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Show answer' }).first()).toBeVisible();
});

test('el modo flashcards avanza con las marcas', async ({ page }) => {
  await page.goto('entrevistas/');
  await page.waitForLoadState('networkidle');
  await page.getByRole('button', { name: 'Flashcards' }).click();
  await expect(page.getByText(/Tarjeta 1 de 150/)).toBeVisible();
  await page.getByRole('button', { name: 'Mostrar respuesta' }).click();
  await page.getByRole('button', { name: 'La sabía' }).click();
  await expect(page.getByText(/Tarjeta 2 de 150/)).toBeVisible();
});

test('un caso de entrevista muestra marco, errores típicos y la visión sénior', async ({
  page,
}) => {
  await page.goto('entrevistas/casos/disenar-un-test-ab/');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Diseñar un test A/B');
  await expect(page.getByRole('heading', { name: 'Marco de respuesta' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Errores típicos' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Qué diría un sénior' })).toBeVisible();
});

test('los ejercicios de entrevista incluyen un cronómetro', async ({ page }) => {
  await page.goto('practica/labs/sql-ent-pedidos-por-estado/');
  const timer = page.getByRole('timer');
  await expect(timer).toHaveText('08:00');
  await page.getByRole('button', { name: 'Empezar' }).click();
  await expect(timer).not.toHaveText('08:00', { timeout: 5000 });
});

test('la página de proyectos lista los ocho proyectos y abre uno', async ({ page }) => {
  await page.goto('proyectos/');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Proyectos de portfolio');
  await expect(page.getByRole('heading', { level: 2 })).toHaveCount(8);
  await page.goto('proyectos/asistente-analitico-mcp/');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('servidor MCP');
  await expect(page.getByRole('link', { name: 'Ver el código inicial en GitHub' })).toBeVisible();
});

test('cheat sheets, glosario y fuentes están disponibles', async ({ page }) => {
  await page.goto('cheatsheets/sql/');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('SQL');
  await page.goto('glosario/');
  await expect(page.getByText('Ley de Twyman').first()).toBeVisible();
  await page.goto('fuentes/');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Fuentes');
  await page.goto('novedades/');
  await expect(page.getByText('Lanzamiento de Data Analyst Academy')).toBeVisible();
});
