/**
 * Validación previa de las consultas del alumno en los labs y el Playground.
 *
 * DuckDB-WASM corre en el navegador del propio alumno, así que el riesgo no
 * es de seguridad del servidor sino de que una consulta mal escrita rompa su
 * sesión (borrar una vista, adjuntar un fichero...). Solo se permiten
 * consultas de lectura de una sola sentencia.
 */

const ALLOWED_FIRST_KEYWORDS = new Set([
  'select',
  'with',
  'from',
  'values',
  'table',
  'describe',
  'summarize',
  'show',
  'explain',
]);

const FORBIDDEN_KEYWORDS = [
  'attach',
  'detach',
  'install',
  'load',
  'copy',
  'export',
  'import',
  'pragma',
  'set',
  'create',
  'drop',
  'alter',
  'insert',
  'update',
  'delete',
  'truncate',
  'call',
];

/** Quita comentarios y literales de texto (un solo recorrido: respeta que `--` dentro de un literal no es un comentario). */
export function stripCommentsAndStrings(sql: string): string {
  let out = '';
  let i = 0;
  while (i < sql.length) {
    const c = sql[i];
    const next = sql[i + 1];
    if (c === '-' && next === '-') {
      while (i < sql.length && sql[i] !== '\n') i++;
      out += ' ';
    } else if (c === '/' && next === '*') {
      const end = sql.indexOf('*/', i + 2);
      i = end === -1 ? sql.length : end + 2;
      out += ' ';
    } else if (c === "'" || c === '"') {
      i++;
      while (i < sql.length) {
        if (sql[i] === c && sql[i + 1] === c) i += 2;
        else if (sql[i] === c) break;
        else i++;
      }
      i++;
      out += c + c;
    } else {
      out += c;
      i++;
    }
  }
  return out;
}

export type GuardResult = { ok: true; sql: string } | { ok: false; message: string };

export function guardSql(raw: string): GuardResult {
  const cleaned = stripCommentsAndStrings(raw)
    .trim()
    .replace(/;+\s*$/, '');
  if (cleaned === '') return { ok: false, message: 'Escribe una consulta primero.' };
  if (cleaned.includes(';')) {
    return {
      ok: false,
      message: 'Solo se admite una sentencia por ejecución (quita los `;` intermedios).',
    };
  }
  const first = cleaned.split(/\s+/)[0].replace(/^\(+/, '').toLowerCase();
  if (!ALLOWED_FIRST_KEYWORDS.has(first)) {
    return {
      ok: false,
      message: `Solo se permiten consultas de lectura (SELECT, WITH...). "${first.toUpperCase()}" no está permitido.`,
    };
  }
  for (const word of FORBIDDEN_KEYWORDS) {
    if (new RegExp(`\\b${word}\\b`, 'i').test(cleaned)) {
      return {
        ok: false,
        message: `La palabra "${word.toUpperCase()}" no está permitida en este entorno de solo lectura.`,
      };
    }
  }
  return { ok: true, sql: raw.trim().replace(/;+\s*$/, '') };
}
