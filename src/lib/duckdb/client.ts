/**
 * Motor SQL del navegador: DuckDB-WASM en un Web Worker (ver PLAN.md §7.4).
 *
 * - Se carga SOLO al abrir un lab SQL o el Playground (import dinámico).
 * - Las tablas de Lumen se registran como vistas sobre los Parquet servidos
 *   por HTTP (lectura por rangos: solo se descargan las columnas y los
 *   bloques que la consulta necesita).
 * - Cada ejecución tiene timeout; si se excede, se termina el worker y se
 *   recrea en la siguiente consulta (DuckDB-WASM no permite cancelar de otro
 *   modo una consulta en curso).
 */
import type * as DuckDB from '@duckdb/duckdb-wasm';
import { url } from '../url';

export interface QueryResult {
  columns: string[];
  rows: Record<string, unknown>[];
  /** true si hubo más filas que `maxRows` y se recortó el resultado. */
  truncated: boolean;
  elapsedMs: number;
}

export class QueryTimeoutError extends Error {
  constructor(public readonly timeoutMs: number) {
    super(`La consulta superó el límite de ${Math.round(timeoutMs / 1000)} s y se canceló.`);
  }
}

export interface EngineOptions {
  /** Tablas de `lumen/` a exponer como vistas (por defecto, todas las de TABLES). */
  tables: string[];
  /** Si true, registra también un esquema `variant` con `lumen_variant/` (checks ocultos). */
  withVariant?: boolean;
}

// Arrow Type ids (apache-arrow): Date = 8, Timestamp = 10.
const ARROW_DATE = 8;
const ARROW_TIMESTAMP = 10;

export const ALL_TABLES = [
  'customers',
  'categories',
  'products',
  'stores',
  'orders',
  'order_items',
  'returns',
  'shipments',
  'inventory_snapshots',
  'web_sessions',
  'events',
  'marketing_spend',
  'campaigns',
  'experiments',
  'experiment_assignments',
  'experiment_metrics',
  'subscriptions',
  'support_tickets',
  'calendar',
];

function absoluteUrl(path: string): string {
  return new URL(url(path), window.location.origin).href;
}

export class SqlEngine {
  private duckdb: typeof DuckDB | null = null;
  private db: DuckDB.AsyncDuckDB | null = null;
  private conn: DuckDB.AsyncDuckDBConnection | null = null;
  private worker: Worker | null = null;
  private starting: Promise<void> | null = null;

  constructor(private readonly options: EngineOptions) {}

  /** Inicia el motor (idempotente). */
  ready(): Promise<void> {
    if (!this.starting) {
      this.starting = this.start().catch((err) => {
        this.starting = null;
        throw err;
      });
    }
    return this.starting;
  }

  private async start(): Promise<void> {
    const duckdb = await import('@duckdb/duckdb-wasm');
    this.duckdb = duckdb;
    const bundle = await duckdb.selectBundle(duckdb.getJsDelivrBundles());
    const workerUrl = URL.createObjectURL(
      new Blob([`importScripts("${bundle.mainWorker!}");`], { type: 'text/javascript' }),
    );
    this.worker = new Worker(workerUrl);
    const db = new duckdb.AsyncDuckDB(new duckdb.VoidLogger(), this.worker);
    await db.instantiate(bundle.mainModule, bundle.pthreadWorker);
    URL.revokeObjectURL(workerUrl);
    await db.open({ query: { castBigIntToDouble: true, castDecimalToDouble: true } });
    this.db = db;
    this.conn = await db.connect();

    // ICU (zonas horarias) es una extensión que DuckDB-WASM autocarga en el
    // primer uso, y esa primera consulta falla. Cargarla de antemano evita
    // que el alumno tropiece con ello. Si no hay red para descargarla, el
    // resto del motor funciona igual (solo faltan las zonas horarias).
    try {
      await this.conn.query('LOAD icu');
      await this.conn.query("SET TimeZone = 'UTC'");
    } catch {
      // sin ICU
    }

    await this.registerViews('lumen', 'main', '');
    if (this.options.withVariant) {
      await this.conn.query('CREATE SCHEMA IF NOT EXISTS variant');
      await this.registerViews('lumen_variant', 'variant', 'variant_');
    }
  }

  private async registerViews(folder: string, schema: string, filePrefix: string): Promise<void> {
    const db = this.db!;
    const conn = this.conn!;
    for (const table of this.options.tables) {
      const file = `${filePrefix}${table}.parquet`;
      await db.registerFileURL(
        file,
        absoluteUrl(`/data/${folder}/${table}.parquet`),
        this.duckdb!.DuckDBDataProtocol.HTTP,
        false,
      );
      await conn.query(
        `CREATE OR REPLACE VIEW ${schema}.${table} AS SELECT * FROM read_parquet('${file}')`,
      );
    }
  }

  /** Ejecuta una consulta de lectura con límite de filas y de tiempo. */
  async query(
    sql: string,
    opts: { maxRows?: number; timeoutMs?: number; schema?: 'main' | 'variant' } = {},
  ): Promise<QueryResult> {
    const { maxRows = 1000, timeoutMs = 10_000, schema = 'main' } = opts;
    await this.ready();
    const conn = this.conn!;
    const started = performance.now();

    let timer: ReturnType<typeof setTimeout> | undefined;
    const timeout = new Promise<never>((_, reject) => {
      timer = setTimeout(() => reject(new QueryTimeoutError(timeoutMs)), timeoutMs);
    });

    try {
      await conn.query(`SET search_path = '${schema}'`);
      const table = await Promise.race([conn.query(sql), timeout]);
      const columns = table.schema.fields.map((f) => f.name);
      const types = table.schema.fields.map((f) => f.type.typeId as number);
      const total = table.numRows;
      const limit = Math.min(total, maxRows);
      const rows: Record<string, unknown>[] = [];
      for (let r = 0; r < limit; r++) {
        const row = table.get(r)!;
        const out: Record<string, unknown> = {};
        columns.forEach((col, c) => {
          out[col] = normalizeValue(row[col], types[c]);
        });
        rows.push(out);
      }
      return { columns, rows, truncated: total > maxRows, elapsedMs: performance.now() - started };
    } catch (err) {
      if (err instanceof QueryTimeoutError) {
        // Único modo de cancelar: matar el worker y recrearlo en la próxima consulta.
        this.terminate();
      }
      throw err;
    } finally {
      clearTimeout(timer);
    }
  }

  terminate(): void {
    this.worker?.terminate();
    this.worker = null;
    this.db = null;
    this.conn = null;
    this.starting = null;
  }
}

function normalizeValue(value: unknown, typeId: number): unknown {
  if (value === null || value === undefined) return null;
  if (typeof value === 'bigint') return Number(value);
  if (typeId === ARROW_DATE && typeof value === 'number') {
    return new Date(value).toISOString().slice(0, 10);
  }
  if (typeId === ARROW_TIMESTAMP && typeof value === 'number') {
    return new Date(value)
      .toISOString()
      .replace('T', ' ')
      .replace(/\.000Z$/, '')
      .replace('Z', '');
  }
  return value;
}
