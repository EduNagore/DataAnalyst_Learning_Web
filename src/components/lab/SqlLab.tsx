import { useStore } from '@nanostores/react';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { SqlEngine, type QueryResult } from '../../lib/duckdb/client';
import { allPassed, runSqlChecks, type CheckItem, type LabChecks } from '../../lib/lab/sqlCheck';
import { guardSql } from '../../lib/lab/sqlGuard';
import { hydrateProgress, progressStore, saveLabProgress } from '../../lib/progress';
import { url } from '../../lib/url';
import Editor from './Editor';
import ResultTable from './ResultTable';
import TestResults from './TestResults';

interface Props {
  labId: string;
  starter: string;
  hints: string[];
  /** Tablas de lumen/ que usa el lab. */
  datasets: string[];
  /** { tabla: [columnas] } para el autocompletado. */
  schema: Record<string, string[]>;
  /** Si true, carga también lumen_variant para el test oculto. */
  needsVariant: boolean;
}

interface LabData {
  solution: string;
  checks: LabChecks;
}

const FAILED_ATTEMPTS_FOR_SOLUTION = 3;

export default function SqlLab({ labId, starter, hints, datasets, schema, needsVariant }: Props) {
  const progress = useStore(progressStore);
  const [code, setCode] = useState(starter);
  const [loadedSaved, setLoadedSaved] = useState(false);
  const [engineStatus, setEngineStatus] = useState<'idle' | 'loading' | 'ready' | 'error'>('idle');
  const [result, setResult] = useState<QueryResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [checks, setChecks] = useState<CheckItem[] | null>(null);
  const [busy, setBusy] = useState(false);
  const [revealedHints, setRevealedHints] = useState(0);
  const [failedAttempts, setFailedAttempts] = useState(0);
  const [solution, setSolution] = useState<string | null>(null);
  const [tab, setTab] = useState<'result' | 'checks'>('result');
  const labData = useRef<LabData | null>(null);
  const saveTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  const engine = useMemo(
    () => new SqlEngine({ tables: datasets, withVariant: needsVariant }),
    [datasets, needsVariant],
  );

  // Cargar código guardado (autoguardado en el progreso).
  useEffect(() => {
    hydrateProgress();
    const saved = progressStore.get().labs[labId];
    if (saved?.code) setCode(saved.code);
    setLoadedSaved(true);
    return () => engine.terminate();
  }, [labId, engine]);

  const status = progress.labs[labId]?.status;

  const persist = useCallback(
    (nextCode: string, nextStatus: 'started' | 'passed') => {
      saveLabProgress(labId, nextCode, nextStatus);
    },
    [labId],
  );

  function onCodeChange(value: string) {
    setCode(value);
    clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(
      () =>
        persist(value, progressStore.get().labs[labId]?.status === 'passed' ? 'passed' : 'started'),
      800,
    );
  }

  async function ensureEngine() {
    if (engineStatus === 'ready') return;
    setEngineStatus('loading');
    try {
      await engine.ready();
      setEngineStatus('ready');
    } catch (err) {
      setEngineStatus('error');
      throw err;
    }
  }

  async function run() {
    setBusy(true);
    setError(null);
    setTab('result');
    const guard = guardSql(code);
    if (!guard.ok) {
      setError(guard.message);
      setResult(null);
      setBusy(false);
      return;
    }
    try {
      await ensureEngine();
      setResult(await engine.query(guard.sql));
    } catch (err) {
      setResult(null);
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  async function loadLabData(): Promise<LabData> {
    if (!labData.current) {
      const response = await fetch(url(`/labs-data/${labId}.json`));
      labData.current = await response.json();
    }
    return labData.current!;
  }

  async function check() {
    setBusy(true);
    setError(null);
    setTab('checks');
    const guard = guardSql(code);
    if (!guard.ok) {
      setChecks([{ name: 'La consulta es válida', passed: false, message: guard.message }]);
      setBusy(false);
      return;
    }
    try {
      await ensureEngine();
      const data = await loadLabData();
      const items = await runSqlChecks(engine, guard.sql, data.solution, data.checks);
      setChecks(items);
      if (allPassed(items)) {
        persist(code, 'passed');
      } else {
        setFailedAttempts((n) => n + 1);
        persist(code, progressStore.get().labs[labId]?.status === 'passed' ? 'passed' : 'started');
      }
    } catch (err) {
      setChecks([
        {
          name: 'La comprobación se pudo ejecutar',
          passed: false,
          message: err instanceof Error ? err.message : String(err),
        },
      ]);
    } finally {
      setBusy(false);
    }
  }

  async function showSolution() {
    if (failedAttempts < FAILED_ATTEMPTS_FOR_SOLUTION) {
      const ok = window.confirm(
        'Todavía no has agotado los intentos recomendados. Ver la solución ahora te quita la mitad del aprendizaje. ¿Seguro?',
      );
      if (!ok) return;
    }
    setSolution((await loadLabData()).solution);
  }

  function reset() {
    if (window.confirm('¿Volver al código inicial? Perderás lo que has escrito.')) {
      setCode(starter);
      setResult(null);
      setChecks(null);
      setError(null);
    }
  }

  const passedAll = checks ? allPassed(checks) : false;
  const btn =
    'rounded-md px-3 py-1.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-50';

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-xs text-[var(--color-text-muted)]">
          {status === 'passed'
            ? 'Lab superado ✔'
            : loadedSaved && progress.labs[labId]
              ? 'En curso'
              : 'Sin empezar'}
          {' · '}Ctrl/⌘ + Enter ejecuta
        </p>
        {engineStatus === 'loading' && (
          <p className="text-xs text-[var(--color-text-muted)]" role="status">
            Cargando DuckDB (solo la primera vez)…
          </p>
        )}
      </div>

      <Editor
        label="Editor SQL"
        language="sql"
        value={code}
        onChange={onCodeChange}
        schema={schema}
        onRun={run}
        minHeight="14rem"
      />

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          disabled={busy}
          onClick={run}
          className={`${btn} border border-[var(--color-border)] text-[var(--color-text)] hover:bg-[var(--color-bg-subtle)]`}
        >
          Ejecutar
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={check}
          className={`${btn} bg-[var(--color-accent)] text-[var(--color-accent-contrast)] hover:opacity-90`}
        >
          Comprobar
        </button>
        <button
          type="button"
          disabled={revealedHints >= hints.length}
          onClick={() => setRevealedHints((n) => n + 1)}
          className={`${btn} border border-[var(--color-border)] text-[var(--color-text)] hover:bg-[var(--color-bg-subtle)]`}
        >
          Pista {hints.length > 0 ? `(${revealedHints}/${hints.length})` : ''}
        </button>
        <button
          type="button"
          onClick={showSolution}
          className={`${btn} text-[var(--color-text-muted)] hover:text-[var(--color-text)]`}
        >
          Ver solución
        </button>
        <button
          type="button"
          onClick={reset}
          className={`${btn} text-[var(--color-text-muted)] hover:text-[var(--color-text)]`}
        >
          Reiniciar
        </button>
      </div>

      {revealedHints > 0 && (
        <ol className="space-y-1 rounded-md border border-[var(--color-border)] bg-[var(--color-bg-subtle)] p-3 text-sm text-[var(--color-text)]">
          {hints.slice(0, revealedHints).map((h, i) => (
            <li key={i}>
              <strong>Pista {i + 1}:</strong> {h}
            </li>
          ))}
        </ol>
      )}

      {solution && (
        <div>
          <p className="mb-1 text-sm font-semibold text-[var(--color-text)]">
            Solución de referencia
          </p>
          <pre className="overflow-x-auto rounded-md border border-[var(--color-border)] bg-[var(--color-bg-subtle)] p-3 font-mono text-xs text-[var(--color-text)]">
            <code>{solution}</code>
          </pre>
        </div>
      )}

      <div>
        <div role="tablist" className="flex gap-1 border-b border-[var(--color-border)]">
          {(
            [
              ['result', 'Resultado'],
              ['checks', `Comprobación${checks ? (passedAll ? ' ✔' : ' ✘') : ''}`],
            ] as const
          ).map(([id, label]) => (
            <button
              key={id}
              role="tab"
              type="button"
              aria-selected={tab === id}
              onClick={() => setTab(id)}
              className={
                'px-3 py-1.5 text-sm font-medium ' +
                (tab === id
                  ? 'border-b-2 border-[var(--color-accent)] text-[var(--color-text)]'
                  : 'text-[var(--color-text-muted)] hover:text-[var(--color-text)]')
              }
            >
              {label}
            </button>
          ))}
        </div>
        <div className="mt-3" role="tabpanel">
          {tab === 'result' && (
            <>
              {error && (
                <pre
                  className="overflow-x-auto rounded-md border border-[var(--color-danger)] bg-[var(--color-danger)]/10 p-3 text-xs whitespace-pre-wrap text-[var(--color-text)]"
                  role="alert"
                >
                  {error}
                </pre>
              )}
              {result && <ResultTable {...result} />}
              {!error && !result && (
                <p className="text-sm text-[var(--color-text-muted)]">
                  Ejecuta tu consulta para ver el resultado.
                </p>
              )}
            </>
          )}
          {tab === 'checks' && (
            <>
              {checks ? (
                <>
                  <TestResults items={checks} />
                  {passedAll && (
                    <p
                      className="mt-3 text-sm font-semibold text-[var(--color-success)]"
                      role="status"
                    >
                      ¡Lab superado! Tu progreso se ha guardado.
                    </p>
                  )}
                </>
              ) : (
                <p className="text-sm text-[var(--color-text-muted)]">
                  Pulsa «Comprobar» para validar tu solución.
                </p>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
