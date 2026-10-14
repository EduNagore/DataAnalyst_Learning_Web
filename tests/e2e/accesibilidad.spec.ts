import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';

// Rutas relativas sin barra inicial (ver navigation.spec.ts).
const PAGES = [
  './',
  'teoria/',
  'teoria/sql-i/03-joins-y-fan-out/',
  'teoria/experimentacion/03-cuped-y-reduccion-de-varianza/',
  'practica/',
  'practica/labs/sql-ent-pedidos-por-estado/',
  'practica/labs/py-evaluar-clasificador-de-tickets/',
  'practica/casos/define-cliente-activo/',
  'entrevistas/',
  'radar/',
  'glosario/',
  'cheatsheets/sql/',
  'proyectos/',
  'datos/',
  'ruta/',
  'fuentes/',
  'progreso/',
  'practica/tests/',
  'practica/sql/',
  'practica/llm/',
];

for (const scheme of ['light', 'dark'] as const) {
  test.describe(`accesibilidad (${scheme})`, () => {
    test.use({ colorScheme: scheme });

    for (const path of PAGES) {
      test(`${path} no tiene infracciones graves`, async ({ page }) => {
        await page.goto(path);
        await page.waitForLoadState('networkidle');
        const results = await new AxeBuilder({ page })
          .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
          .analyze();
        const serious = results.violations.filter((v) =>
          ['serious', 'critical'].includes(v.impact ?? ''),
        );
        expect(
          serious.map(
            (v) =>
              `${v.id}: ${v.nodes.length} nodos · ${v.help} · ${v.nodes
                .slice(0, 3)
                .map(
                  (n) =>
                    `${n.target.join(' ')} → ${(n.any[0]?.message ?? n.failureSummary ?? '').slice(0, 140)}`,
                )
                .join(' | ')}`,
          ),
          `${path} (${scheme})`,
        ).toEqual([]);
      });
    }
  });
}
