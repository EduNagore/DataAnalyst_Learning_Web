/**
 * Corrección de labs SQL (ver PLAN.md §7.4 y §6, `checks.yaml`).
 *
 * Ejecuta la consulta del alumno y la de la solución, compara los result sets
 * con `resultCompare.ts` y, si el lab lo pide, repite la comparación contra
 * `lumen_variant` (otra semilla) para detectar respuestas "hardcodeadas".
 */
import { compareResultSets, type CompareOptions, type SqlRow } from '../resultCompare';
import { stripCommentsAndStrings } from './sqlGuard';

export interface LabChecks {
  compare?: CompareOptions;
  /** Re-ejecuta alumno y solución contra lumen_variant (check oculto). */
  hiddenOnVariant?: boolean;
  assertions?: TextAssertion[];
}

export interface TextAssertion {
  name: string;
  kind: 'query-text-not-contains' | 'query-text-contains';
  /** Texto a buscar, sin distinguir mayúsculas y fuera de comentarios y literales. */
  value: string;
}

export interface CheckItem {
  name: string;
  passed: boolean;
  message: string;
  hidden?: boolean;
}

export interface SqlRunner {
  query(
    sql: string,
    opts?: { maxRows?: number; timeoutMs?: number; schema?: 'main' | 'variant' },
  ): Promise<{ rows: Record<string, unknown>[] }>;
}

const MAX_COMPARE_ROWS = 100_000;

export async function runSqlChecks(
  runner: SqlRunner,
  studentSql: string,
  solutionSql: string,
  checks: LabChecks,
): Promise<CheckItem[]> {
  const items: CheckItem[] = [];

  const structure = stripCommentsAndStrings(studentSql).toLowerCase();
  for (const a of checks.assertions ?? []) {
    const found = structure.includes(a.value.toLowerCase());
    const passed = a.kind === 'query-text-contains' ? found : !found;
    items.push({
      name: a.name,
      passed,
      message: passed
        ? 'Correcto.'
        : a.kind === 'query-text-contains'
          ? `Tu consulta debería usar \`${a.value}\`.`
          : `Tu consulta no debería usar \`${a.value}\` para este ejercicio.`,
    });
  }

  let actual: SqlRow[];
  try {
    actual = (await runner.query(studentSql, { maxRows: MAX_COMPARE_ROWS })).rows;
  } catch (err) {
    items.unshift({
      name: 'La consulta se ejecuta',
      passed: false,
      message: err instanceof Error ? err.message : String(err),
    });
    return items;
  }
  items.unshift({ name: 'La consulta se ejecuta', passed: true, message: 'Sin errores.' });

  const expected = (await runner.query(solutionSql, { maxRows: MAX_COMPARE_ROWS })).rows;
  const comparison = compareResultSets(expected, actual, checks.compare);
  items.push({
    name: 'El resultado coincide con el esperado',
    passed: comparison.match,
    message: comparison.match
      ? `${actual.length} ${actual.length === 1 ? 'fila' : 'filas'}, todas correctas.`
      : (comparison.message ?? 'El resultado no coincide.'),
  });

  if (checks.hiddenOnVariant && comparison.match) {
    try {
      const variantExpected = (
        await runner.query(solutionSql, { maxRows: MAX_COMPARE_ROWS, schema: 'variant' })
      ).rows;
      const variantActual = (
        await runner.query(studentSql, { maxRows: MAX_COMPARE_ROWS, schema: 'variant' })
      ).rows;
      const variant = compareResultSets(variantExpected, variantActual, checks.compare);
      items.push({
        name: 'Funciona también con otros datos (test oculto)',
        passed: variant.match,
        hidden: true,
        message: variant.match
          ? 'Tu consulta generaliza bien.'
          : 'Tu consulta da el resultado correcto con los datos de este ejercicio, pero no con otro conjunto de datos del mismo esquema. ¿Has escrito alguna cifra o identificador a mano en lugar de calcularlo?',
      });
    } catch (err) {
      items.push({
        name: 'Funciona también con otros datos (test oculto)',
        passed: false,
        hidden: true,
        message: `Falla con otro conjunto de datos: ${err instanceof Error ? err.message : String(err)}`,
      });
    }
  }
  return items;
}

export function allPassed(items: CheckItem[]): boolean {
  return items.length > 0 && items.every((i) => i.passed);
}
