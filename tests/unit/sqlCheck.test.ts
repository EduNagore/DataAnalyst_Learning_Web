import { describe, expect, it } from 'vitest';
import { allPassed, runSqlChecks, type SqlRunner } from '../../src/lib/lab/sqlCheck';

/** Runner falso: devuelve filas según la consulta y el esquema pedidos. */
function fakeRunner(table: Record<string, Record<string, unknown>[]>): SqlRunner {
  return {
    async query(sql, opts) {
      const key = `${opts?.schema ?? 'main'}::${sql}`;
      if (sql.includes('BOOM')) throw new Error('Catalog Error: tabla inexistente');
      if (!(key in table)) throw new Error(`consulta no prevista: ${key}`);
      return { rows: table[key] };
    },
  };
}

describe('runSqlChecks', () => {
  const solution = 'SELECT n FROM sol';

  it('pasa cuando coincide en el dataset principal y en la variante', async () => {
    const runner = fakeRunner({
      'main::SELECT n FROM sol': [{ n: 5 }],
      'main::SELECT n FROM alumno': [{ n: 5 }],
      'variant::SELECT n FROM sol': [{ n: 2 }],
      'variant::SELECT n FROM alumno': [{ n: 2 }],
    });
    const items = await runSqlChecks(runner, 'SELECT n FROM alumno', solution, {
      hiddenOnVariant: true,
    });
    expect(allPassed(items)).toBe(true);
    expect(items.some((i) => i.hidden)).toBe(true);
  });

  it('detecta una respuesta hardcodeada con el test oculto', async () => {
    const runner = fakeRunner({
      'main::SELECT n FROM sol': [{ n: 5 }],
      'main::SELECT 5 AS n': [{ n: 5 }],
      'variant::SELECT n FROM sol': [{ n: 2 }],
      'variant::SELECT 5 AS n': [{ n: 5 }],
    });
    const items = await runSqlChecks(runner, 'SELECT 5 AS n', solution, { hiddenOnVariant: true });
    expect(allPassed(items)).toBe(false);
    const hidden = items.find((i) => i.hidden)!;
    expect(hidden.passed).toBe(false);
    expect(hidden.message).toMatch(/a mano/);
  });

  it('informa del error de ejecución y no sigue', async () => {
    const items = await runSqlChecks(fakeRunner({}), 'SELECT BOOM', solution, {});
    expect(items).toHaveLength(1);
    expect(items[0]).toMatchObject({ passed: false });
    expect(items[0].message).toMatch(/Catalog Error/);
  });

  it('aplica las aserciones de texto ignorando comentarios y literales', async () => {
    const runner = fakeRunner({
      'main::SELECT n FROM sol': [{ n: 1 }],
      "main::SELECT n FROM alumno -- DISTINCT\nWHERE x = 'DISTINCT'": [{ n: 1 }],
    });
    const items = await runSqlChecks(
      runner,
      "SELECT n FROM alumno -- DISTINCT\nWHERE x = 'DISTINCT'",
      solution,
      {
        assertions: [{ name: 'Sin DISTINCT', kind: 'query-text-not-contains', value: 'DISTINCT' }],
      },
    );
    expect(items.find((i) => i.name === 'Sin DISTINCT')?.passed).toBe(true);
  });

  it('el mensaje de diferencia es didáctico', async () => {
    const runner = fakeRunner({
      'main::SELECT n FROM sol': [{ n: 1 }, { n: 2 }],
      'main::SELECT n FROM alumno': [{ n: 1 }, { n: 2 }, { n: 3 }, { n: 4 }],
    });
    const items = await runSqlChecks(runner, 'SELECT n FROM alumno', solution, {});
    expect(items[1].passed).toBe(false);
    expect(items[1].message).toMatch(/sobran 2 filas/);
  });
});
