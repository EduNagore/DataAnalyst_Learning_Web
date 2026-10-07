import { useState } from 'react';

interface Props {
  /** p.ej. { duckdb: '...', postgres: '...', bigquery: '...' }. La primera clave es el dialecto por defecto (el que usan los labs). */
  dialects: Record<string, string>;
}

const LABELS: Record<string, string> = {
  duckdb: 'DuckDB',
  postgres: 'PostgreSQL',
  bigquery: 'BigQuery',
  snowflake: 'Snowflake',
  tsql: 'T-SQL',
};

/** Comparación de SQL entre motores (ver docs/CONTENT_GUIDELINES.md §4). */
export default function DialectTabs({ dialects }: Props) {
  const keys = Object.keys(dialects);
  const [active, setActive] = useState(keys[0]);

  return (
    <div className="my-5 overflow-hidden rounded-md border border-[var(--color-border)]">
      <div
        role="tablist"
        className="flex gap-1 border-b border-[var(--color-border)] bg-[var(--color-bg-subtle)] px-2 pt-2"
      >
        {keys.map((key) => (
          <button
            key={key}
            role="tab"
            type="button"
            aria-selected={active === key}
            onClick={() => setActive(key)}
            className={
              'rounded-t-md px-3 py-1.5 text-xs font-medium transition-colors ' +
              (active === key
                ? 'bg-[var(--color-bg-raised)] text-[var(--color-text)]'
                : 'text-[var(--color-text-muted)] hover:text-[var(--color-text)]')
            }
          >
            {LABELS[key] ?? key}
          </button>
        ))}
      </div>
      <pre className="overflow-x-auto bg-[var(--color-bg-raised)] p-4 font-mono text-sm text-[var(--color-text)]">
        <code>{dialects[active]}</code>
      </pre>
    </div>
  );
}
