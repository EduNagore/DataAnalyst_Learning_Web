import { useEffect, useMemo, useRef, useState } from 'react';
import { ALL_TABLES, SqlEngine, type QueryResult } from '../../lib/duckdb/client';
import { guardSql } from '../../lib/lab/sqlGuard';
import Editor from './Editor';
import ResultTable from './ResultTable';

interface TableInfo {
  name: string;
  description: string;
  rowCount: number;
  columns: Record<string, string>;
}

const HISTORY_KEY = 'daa:sql-history:v1';
const HISTORY_MAX = 20;

const EXAMPLES: { label: string; sql: string }[] = [
  {
    label: 'Pedidos por año y canal',
    sql: `SELECT year(order_date) AS anio, channel, COUNT(*) AS pedidos
FROM orders
GROUP BY anio, channel
ORDER BY anio, channel`,
  },
  {
    label: 'Ingresos por categoría',
    sql: `SELECT cat.name AS categoria, ROUND(SUM(oi.quantity * oi.unit_price)) AS ingresos
FROM order_items AS oi
JOIN products   AS p   ON p.product_id = oi.product_id
JOIN categories AS sub ON sub.category_id = p.category_id
JOIN categories AS cat ON cat.category_id = sub.parent_category_id
GROUP BY cat.name
ORDER BY ingresos DESC`,
  },
  {
    label: 'Funnel de sesiones (eventos)',
    sql: `SELECT event_type, COUNT(*) AS eventos, COUNT(DISTINCT session_id) AS sesiones
FROM events
GROUP BY event_type
ORDER BY sesiones DESC`,
  },
  { label: 'Explorar una tabla', sql: 'SELECT * FROM customers LIMIT 20' },
];

function readHistory(): string[] {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) ?? '[]');
  } catch {
    return [];
  }
}

function toCsv(result: QueryResult): string {
  const esc = (v: unknown) => {
    const s = v === null || v === undefined ? '' : String(v);
    return /[",\n;]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  return [
    result.columns.join(','),
    ...result.rows.map((r) => result.columns.map((c) => esc(r[c])).join(',')),
  ].join('\n');
}

export default function Playground({ tables }: { tables: TableInfo[] }) {
  const [code, setCode] = useState(EXAMPLES[0].sql);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<string[]>([]);
  const [open, setOpen] = useState<string | null>(null);
  const engine = useRef(new SqlEngine({ tables: ALL_TABLES }));

  useEffect(() => {
    setHistory(readHistory());
    const current = engine.current;
    return () => current.terminate();
  }, []);

  const schema = useMemo(
    () => Object.fromEntries(tables.map((t) => [t.name, Object.keys(t.columns)])),
    [tables],
  );

  function remember(sql: string) {
    const next = [sql, ...history.filter((h) => h !== sql)].slice(0, HISTORY_MAX);
    setHistory(next);
    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(next));
    } catch {
      // almacenamiento no disponible
    }
  }

  async function run() {
    setError(null);
    const guard = guardSql(code);
    if (!guard.ok) {
      setError(guard.message);
      setResult(null);
      return;
    }
    setBusy(true);
    setLoading(true);
    try {
      await engine.current.ready();
      setLoading(false);
      setResult(await engine.current.query(guard.sql));
      remember(code);
    } catch (err) {
      setResult(null);
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
      setLoading(false);
    }
  }

  function download() {
    if (!result) return;
    const blob = new Blob([toCsv(result)], { type: 'text/csv;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'resultado.csv';
    a.click();
    URL.revokeObjectURL(a.href);
  }

  const btn = 'rounded-md px-3 py-1.5 text-sm font-semibold disabled:opacity-50';

  return (
    <div className="grid gap-6 lg:grid-cols-[16rem_minmax(0,1fr)]">
      <aside aria-label="Esquema de datos" className="text-sm">
        <h2 className="font-semibold text-[var(--color-text)]">Tablas de Lumen</h2>
        <ul className="mt-2 space-y-1">
          {tables.map((t) => (
            <li key={t.name}>
              <button
                type="button"
                aria-expanded={open === t.name}
                onClick={() => setOpen(open === t.name ? null : t.name)}
                className="flex w-full items-baseline justify-between rounded px-1 py-0.5 text-left font-mono text-xs text-[var(--color-text)] hover:bg-[var(--color-bg-subtle)]"
              >
                {t.name}
                <span className="font-sans text-[10px] text-[var(--color-text-muted)]">
                  {t.rowCount.toLocaleString('es-ES')}
                </span>
              </button>
              {open === t.name && (
                <ul className="mt-1 mb-2 ml-2 space-y-0.5 border-l border-[var(--color-border)] pl-2">
                  {Object.entries(t.columns).map(([col, desc]) => (
                    <li
                      key={col}
                      className="text-[11px] text-[var(--color-text-muted)]"
                      title={desc}
                    >
                      <span className="font-mono text-[var(--color-text)]">{col}</span>
                    </li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ul>
      </aside>

      <div className="min-w-0 space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <label className="text-xs text-[var(--color-text-muted)]">
            Ejemplos{' '}
            <select
              className="ml-1 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-2 py-1 text-sm text-[var(--color-text)]"
              value=""
              onChange={(e) => e.target.value && setCode(EXAMPLES[Number(e.target.value)].sql)}
            >
              <option value="">Elegir…</option>
              {EXAMPLES.map((ex, i) => (
                <option key={ex.label} value={i}>
                  {ex.label}
                </option>
              ))}
            </select>
          </label>
          {history.length > 0 && (
            <label className="text-xs text-[var(--color-text-muted)]">
              Historial{' '}
              <select
                className="ml-1 max-w-48 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-2 py-1 text-sm text-[var(--color-text)]"
                value=""
                onChange={(e) => e.target.value && setCode(history[Number(e.target.value)])}
              >
                <option value="">Consultas recientes…</option>
                {history.map((h, i) => (
                  <option key={i} value={i}>
                    {h.replace(/\s+/g, ' ').slice(0, 60)}
                  </option>
                ))}
              </select>
            </label>
          )}
          {loading && (
            <span className="text-xs text-[var(--color-text-muted)]" role="status">
              Cargando DuckDB (solo la primera vez)…
            </span>
          )}
        </div>

        <Editor
          label="Editor SQL"
          language="sql"
          value={code}
          onChange={setCode}
          schema={schema}
          onRun={run}
          minHeight="12rem"
        />

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            disabled={busy}
            onClick={run}
            className={`${btn} bg-[var(--color-accent)] text-[var(--color-accent-contrast)] hover:opacity-90`}
          >
            Ejecutar (Ctrl/⌘ + Enter)
          </button>
          <button
            type="button"
            disabled={!result}
            onClick={download}
            className={`${btn} border border-[var(--color-border)] text-[var(--color-text)] hover:bg-[var(--color-bg-subtle)]`}
          >
            Exportar CSV
          </button>
        </div>

        {error && (
          <pre
            className="overflow-x-auto rounded-md border border-[var(--color-danger)] bg-[var(--color-danger)]/10 p-3 text-xs whitespace-pre-wrap text-[var(--color-text)]"
            role="alert"
          >
            {error}
          </pre>
        )}
        {result && <ResultTable {...result} />}
      </div>
    </div>
  );
}
