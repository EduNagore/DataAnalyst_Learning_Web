import { useStore } from '@nanostores/react';
import { useEffect, useMemo, useRef, useState } from 'react';
import type { CheckItem } from '../../lib/lab/sqlCheck';
import { hydrateProgress, progressStore, saveLabProgress } from '../../lib/progress';
import { PyEngine, type PyRunResult } from '../../lib/pyodide/client';
import { url } from '../../lib/url';
import Editor from './Editor';
import TestResults from './TestResults';

interface Props {
  labId: string;
  starter: string;
  hints: string[];
  /** Tablas de lumen/ que usa el lab. */
  tables: string[];
  /** Datasets de extra/ (sin extensión). */
  extras: string[];
  /** CSV «sucios» de lumen_raw/ (sin extensión). */
  raws: string[];
  packages: string[];
  needsVariant: boolean;
}

const FAILED_ATTEMPTS_FOR_SOLUTION = 3;

export default function PyLab({
  labId,
  starter,
  hints,
  tables,
  extras,
  raws,
  packages,
  needsVariant,
}: Props) {
  const progress = useStore(progressStore);
  const [code, setCode] = useState(starter);
  const [status, setStatus] = useState<string | null>(null);
  const [run, setRun] = useState<PyRunResult | null>(null);
  const [checks, setChecks] = useState<CheckItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [revealed, setRevealed] = useState(0);
  const [failed, setFailed] = useState(0);
  const [solution, setSolution] = useState<string | null>(null);
  const [tab, setTab] = useState<'output' | 'checks'>('output');
  const data = useRef<{ solution: string; tests: string } | null>(null);
  const saveTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  const engine = useMemo(
    () =>
      new PyEngine({
        packages,
        tables,
        extras,
        raws,
        withVariant: needsVariant,
        onStatus: setStatus,
      }),
    [packages, tables, extras, raws, needsVariant],
  );

  useEffect(() => {
    hydrateProgress();
    const saved = progressStore.get().labs[labId];
    if (saved?.code) setCode(saved.code);
    return () => engine.terminate();
  }, [labId, engine]);

  const labStatus = progress.labs[labId]?.status;

  function onChange(value: string) {
    setCode(value);
    clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(
      () =>
        saveLabProgress(
          labId,
          value,
          progressStore.get().labs[labId]?.status === 'passed' ? 'passed' : 'started',
        ),
      800,
    );
  }

  async function loadData() {
    if (!data.current) data.current = await (await fetch(url(`/labs-data/${labId}.json`))).json();
    return data.current!;
  }

  async function execute(withTests: boolean) {
    setBusy(true);
    setError(null);
    setTab(withTests ? 'checks' : 'output');
    setStatus('Iniciando Python (solo la primera vez, ~10 MB)…');
    try {
      const tests = withTests ? (await loadData()).tests : '';
      const result = await engine.run(code, tests);
      setStatus(null);
      setRun(result);
      if (withTests) {
        const items: CheckItem[] = result.error
          ? [{ name: 'Tu código se ejecuta', passed: false, message: result.error }]
          : result.tests.map((t) => ({
              name: t.name,
              passed: t.passed,
              message: t.message,
              hidden: t.hidden,
            }));
        setChecks(items);
        const ok = items.length > 0 && items.every((i) => i.passed);
        if (ok) saveLabProgress(labId, code, 'passed');
        else {
          setFailed((n) => n + 1);
          saveLabProgress(labId, code, labStatus === 'passed' ? 'passed' : 'started');
        }
      }
    } catch (err) {
      setStatus(null);
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  async function showSolution() {
    if (
      failed < FAILED_ATTEMPTS_FOR_SOLUTION &&
      !window.confirm(
        'Todavía no has agotado los intentos recomendados. ¿Ver la solución igualmente?',
      )
    )
      return;
    setSolution((await loadData()).solution);
  }

  const passedAll = checks ? checks.length > 0 && checks.every((c) => c.passed) : false;
  const btn =
    'rounded-md px-3 py-1.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-50';

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-xs text-[var(--color-text-muted)]">
          {labStatus === 'passed'
            ? 'Lab superado ✔'
            : progress.labs[labId]
              ? 'En curso'
              : 'Sin empezar'}{' '}
          · Ctrl/⌘ + Enter ejecuta
        </p>
        {status && (
          <p className="text-xs text-[var(--color-text-muted)]" role="status">
            {status}
          </p>
        )}
      </div>

      <Editor
        label="Editor Python"
        language="python"
        value={code}
        onChange={onChange}
        onRun={() => execute(false)}
        minHeight="16rem"
      />

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          disabled={busy}
          onClick={() => execute(false)}
          className={`${btn} border border-[var(--color-border)] text-[var(--color-text)] hover:bg-[var(--color-bg-subtle)]`}
        >
          Ejecutar
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={() => execute(true)}
          className={`${btn} bg-[var(--color-accent)] text-[var(--color-accent-contrast)] hover:opacity-90`}
        >
          Comprobar
        </button>
        <button
          type="button"
          disabled={revealed >= hints.length}
          onClick={() => setRevealed((n) => n + 1)}
          className={`${btn} border border-[var(--color-border)] text-[var(--color-text)] hover:bg-[var(--color-bg-subtle)]`}
        >
          Pista ({revealed}/{hints.length})
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
          onClick={() =>
            window.confirm('¿Volver al código inicial?') &&
            (setCode(starter), setRun(null), setChecks(null))
          }
          className={`${btn} text-[var(--color-text-muted)] hover:text-[var(--color-text)]`}
        >
          Reiniciar
        </button>
      </div>

      {revealed > 0 && (
        <ol className="space-y-1 rounded-md border border-[var(--color-border)] bg-[var(--color-bg-subtle)] p-3 text-sm text-[var(--color-text)]">
          {hints.slice(0, revealed).map((h, i) => (
            <li key={i}>
              <strong>Pista {i + 1}:</strong> {h}
            </li>
          ))}
        </ol>
      )}

      {solution && (
        <pre className="overflow-x-auto rounded-md border border-[var(--color-border)] bg-[var(--color-bg-subtle)] p-3 font-mono text-xs text-[var(--color-text)]">
          <code>{solution}</code>
        </pre>
      )}

      <div>
        <div role="tablist" className="flex gap-1 border-b border-[var(--color-border)]">
          {(
            [
              ['output', 'Salida'],
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
          {error && (
            <pre
              className="rounded-md border border-[var(--color-danger)] bg-[var(--color-danger)]/10 p-3 text-xs whitespace-pre-wrap text-[var(--color-text)]"
              role="alert"
            >
              {error}
            </pre>
          )}
          {tab === 'output' && (
            <pre className="min-h-16 overflow-x-auto rounded-md border border-[var(--color-border)] bg-[var(--color-bg-subtle)] p-3 font-mono text-xs whitespace-pre-wrap text-[var(--color-text)]">
              {run?.error ? `⚠ ${run.error}\n\n` : ''}
              {run?.stdout ||
                (run
                  ? '(sin salida: usa print() para ver valores)'
                  : 'Ejecuta tu código para ver la salida.')}
            </pre>
          )}
          {tab === 'checks' &&
            (checks ? (
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
            ))}
        </div>
      </div>
    </div>
  );
}
