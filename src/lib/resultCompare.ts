/**
 * Comparación de result sets SQL para los labs de DuckDB-WASM (PLAN.md §7.4).
 *
 * Compara la salida de la consulta del alumno con la de `solution.sql`
 * según las reglas de `checks.yaml` del lab, y devuelve un mensaje de
 * error didáctico en español en lugar de un simple true/false.
 */

export type SqlRow = Record<string, unknown>;

export interface CompareOptions {
  /** Si el enunciado exige un ORDER BY concreto. Por defecto, false
   * (se compara como multiconjunto de filas). */
  orderMatters?: boolean;
  /** Compara solo por posición de columna, ignorando sus nombres. */
  ignoreColumnNames?: boolean;
  /** Tolerancia absoluta para comparar números de coma flotante. */
  floatTolerance?: number;
  /** Subconjunto de columnas a comparar (por nombre); el resto se ignora. */
  columns?: string[];
}

export interface CompareResult {
  match: boolean;
  message?: string;
}

const DEFAULT_FLOAT_TOLERANCE = 1e-6;

function formatValue(value: unknown): string {
  if (typeof value === 'number') {
    return value.toLocaleString('es-ES', { maximumFractionDigits: 6 });
  }
  if (value === null || value === undefined) return 'NULL';
  return String(value);
}

function valuesEqual(a: unknown, b: unknown, floatTolerance: number): boolean {
  if (typeof a === 'number' && typeof b === 'number') {
    return Math.abs(a - b) <= floatTolerance;
  }
  if (a === null || a === undefined) return b === null || b === undefined;
  return String(a) === String(b);
}

/** Proyecta una fila a un array de valores según las opciones de comparación. */
function projectRow(row: SqlRow, columnOrder: string[], ignoreColumnNames: boolean): unknown[] {
  if (ignoreColumnNames) return Object.values(row);
  return columnOrder.map((col) => row[col]);
}

function rowsEqual(a: unknown[], b: unknown[], floatTolerance: number): boolean {
  if (a.length !== b.length) return false;
  return a.every((v, i) => valuesEqual(v, b[i], floatTolerance));
}

export function compareResultSets(
  expected: SqlRow[],
  actual: SqlRow[],
  options: CompareOptions = {},
): CompareResult {
  const floatTolerance = options.floatTolerance ?? DEFAULT_FLOAT_TOLERANCE;
  const ignoreColumnNames = options.ignoreColumnNames ?? false;

  if (expected.length === 0 && actual.length === 0) return { match: true };

  const expectedColumns = options.columns ?? Object.keys(expected[0] ?? {});

  if (!ignoreColumnNames && expected.length > 0) {
    const actualColumns = new Set(Object.keys(actual[0] ?? {}));
    const missing = expectedColumns.filter((c) => !actualColumns.has(c));
    if (missing.length > 0) {
      return {
        match: false,
        message: `Faltan columnas en el resultado: ${missing.join(', ')}.`,
      };
    }
  }

  if (expected.length !== actual.length) {
    const diff = actual.length - expected.length;
    const word = Math.abs(diff) === 1 ? 'fila' : 'filas';
    return {
      match: false,
      message:
        diff > 0
          ? `Te sobran ${diff} ${word}: se esperaban ${expected.length} y el resultado tiene ${actual.length}.`
          : `Te faltan ${Math.abs(diff)} ${word}: se esperaban ${expected.length} y el resultado tiene ${actual.length}.`,
    };
  }

  const expectedProjected = expected.map((row) =>
    projectRow(row, expectedColumns, ignoreColumnNames),
  );
  const actualProjected = actual.map((row) => projectRow(row, expectedColumns, ignoreColumnNames));

  if (options.orderMatters) {
    for (let i = 0; i < expectedProjected.length; i++) {
      if (!rowsEqual(expectedProjected[i], actualProjected[i], floatTolerance)) {
        const colIdx = expectedProjected[i].findIndex(
          (v, j) => !valuesEqual(v, actualProjected[i][j], floatTolerance),
        );
        const colName = ignoreColumnNames ? `columna ${colIdx + 1}` : expectedColumns[colIdx];
        return {
          match: false,
          message: `La fila ${i + 1} no coincide en ${colName}: esperado ${formatValue(
            expectedProjected[i][colIdx],
          )}, obtenido ${formatValue(actualProjected[i][colIdx])}. ¿Falta un ORDER BY?`,
        };
      }
    }
    return { match: true };
  }

  // orderMatters = false: comparación como multiconjunto. Emparejamos cada
  // fila esperada con una fila real no usada todavía.
  const usedActual = new Set<number>();
  for (let i = 0; i < expectedProjected.length; i++) {
    const matchIdx = actualProjected.findIndex(
      (row, j) => !usedActual.has(j) && rowsEqual(expectedProjected[i], row, floatTolerance),
    );
    if (matchIdx === -1) {
      const colNames = ignoreColumnNames
        ? expectedProjected[i].map((_, j) => `col${j + 1}`)
        : expectedColumns;
      const rowDescription = colNames
        .map((name, j) => `${name}=${formatValue(expectedProjected[i][j])}`)
        .join(', ');
      return {
        match: false,
        message: `Ninguna fila del resultado coincide con la esperada (${rowDescription}).`,
      };
    }
    usedActual.add(matchIdx);
  }

  return { match: true };
}
