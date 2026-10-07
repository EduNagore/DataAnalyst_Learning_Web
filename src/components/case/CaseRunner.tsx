import { useStore } from '@nanostores/react';
import { useEffect, useMemo, useRef, useState } from 'react';
import { SqlEngine, type QueryResult } from '../../lib/duckdb/client';
import { guardSql } from '../../lib/lab/sqlGuard';
import { hydrateProgress, progressStore, saveCaseProgress } from '../../lib/progress';
import { PyEngine } from '../../lib/pyodide/client';
import { checkAnswer, parseNumberEs, type QuizQuestion } from '../../lib/quiz';
import Editor from '../lab/Editor';
import ResultTable from '../lab/ResultTable';
import InlineText from '../quiz/InlineText';

export interface CaseStep {
  id: string;
  prompt: string;
  tool: 'sql' | 'python' | 'reasoning';
  answerType: 'numeric' | 'single' | 'multiple' | 'text-self-assessed';
  answer?: number | number[];
  tolerance?: number | string;
  options?: string[];
  hints: string[];
  explanation: string;
}

interface Props {
  caseId: string;
  brief: string;
  steps: CaseStep[];
  rubric: string[];
  modelReport: string;
  datasets: string[];
  packages: string[];
  schema: Record<string, string[]>;
}

type Answers = Record<string, unknown>;

function Paragraphs({ text }: { text: string }) {
  return (
    <>
      {text
        .trim()
        .split(/\n{2,}/)
        .map((p, i) => (
          <p key={i} className="mt-2 first:mt-0">
            <InlineText text={p.replace(/\*\*(.+?)\*\*/g, '$1')} />
          </p>
        ))}
    </>
  );
}

function asQuestion(step: CaseStep): QuizQuestion {
  return {
    id: step.id,
    type:
      step.answerType === 'numeric'
        ? 'numeric'
        : step.answerType === 'multiple'
          ? 'multiple'
          : 'single',
    difficulty: 1,
    prompt: step.prompt,
    options: step.options,
    answer: step.answer as number | number[],
    tolerance: step.tolerance,
    explanation: step.explanation,
  };
}

export default function CaseRunner({
  caseId,
  brief,
  steps,
  rubric,
  modelReport,
  datasets,
  packages,
  schema,
}: Props) {
  const progress = useStore(progressStore);
  const saved = progress.cases[caseId];
  const [answers, setAnswers] = useState<Answers>({});
  const [attempts, setAttempts] = useState<Record<string, number>>({});
  const [feedback, setFeedback] = useState<Record<string, boolean | null>>({});
  const [hints, setHints] = useState<Record<string, number>>({});
  const [outputs, setOutputs] = useState<Record<string, QueryResult | string>>({});
  const [errors, setErrors] = useState<Record<string, string | null>>({});
  const [busy, setBusy] = useState(false);
  const [showModel, setShowModel] = useState(false);
  const hydrated = useRef(false);

  const sqlEngine = useMemo(() => new SqlEngine({ tables: datasets }), [datasets]);
  const pyEngine = useMemo(
    () => new PyEngine({ packages, tables: datasets }),
    [packages, datasets],
  );

  useEffect(() => {
    hydrateProgress();
    const s = progressStore.get().cases[caseId];
    if (s) setAnswers(s.answers);
    hydrated.current = true;
    return () => {
      sqlEngine.terminate();
      pyEngine.terminate();
    };
  }, [caseId, sqlEngine, pyEngine]);

  const solved = (answers.__solved ?? {}) as Record<string, boolean>;
  const firstOpen = steps.findIndex((s) => !solved[s.id]);
  const current = firstOpen === -1 ? steps.length : firstOpen;
  const finished = current >= steps.length;

  function persist(next: Answers, completed = false) {
    const nextSolved = (next.__solved ?? {}) as Record<string, boolean>;
    const step = steps.findIndex((s) => !nextSolved[s.id]);
    saveCaseProgress(
      caseId,
      step === -1 ? steps.length : step,
      next,
      completed ? new Date().toISOString() : saved?.completed,
    );
  }

  function setAnswer(key: string, value: unknown) {
    const next = { ...answers, [key]: value };
    setAnswers(next);
    setFeedback((f) => ({ ...f, [key]: null }));
    persist(next);
  }

  async function runCode(step: CaseStep) {
    const code = String(answers[`${step.id}:code`] ?? '');
    setBusy(true);
    setErrors((e) => ({ ...e, [step.id]: null }));
    try {
      if (step.tool === 'sql') {
        const guard = guardSql(code);
        if (!guard.ok) throw new Error(guard.message);
        const result = await sqlEngine.query(guard.sql);
        setOutputs((o) => ({ ...o, [step.id]: result }));
      } else {
        const result = await pyEngine.run(code);
        setOutputs((o) => ({
          ...o,
          [step.id]: result.error ? `⚠ ${result.error}` : result.stdout || '(sin salida)',
        }));
      }
    } catch (err) {
      setErrors((e) => ({ ...e, [step.id]: err instanceof Error ? err.message : String(err) }));
    } finally {
      setBusy(false);
    }
  }

  function check(step: CaseStep) {
    const value = answers[step.id];
    let ok = false;
    if (step.answerType === 'text-self-assessed') {
      ok = typeof value === 'string' && value.trim().length >= 10;
    } else if (step.answerType === 'numeric') {
      const n = typeof value === 'string' ? parseNumberEs(value) : Number.NaN;
      ok = !Number.isNaN(n) && checkAnswer(asQuestion(step), n);
    } else if (step.answerType === 'multiple') {
      ok =
        Array.isArray(value) &&
        value.length > 0 &&
        checkAnswer(asQuestion(step), value as number[]);
    } else {
      ok = typeof value === 'number' && checkAnswer(asQuestion(step), value);
    }
    setFeedback((f) => ({ ...f, [step.id]: ok }));
    setAttempts((a) => ({ ...a, [step.id]: (a[step.id] ?? 0) + 1 }));
    if (ok) {
      const next = { ...answers, __solved: { ...solved, [step.id]: true } };
      setAnswers(next);
      persist(next);
    }
  }

  function revealAnswer(step: CaseStep) {
    const next = {
      ...answers,
      __solved: { ...solved, [step.id]: true },
      [`${step.id}:revealed`]: true,
    };
    setAnswers(next);
    persist(next);
  }

  const rubricChecked = (answers.__rubric ?? []) as boolean[];
  const btn = 'rounded-md px-3 py-1.5 text-sm font-semibold disabled:opacity-50';

  return (
    <div className="space-y-6">
      <div className="rounded-lg border-l-4 border-[var(--color-accent)] bg-[var(--color-bg-subtle)] p-4 text-sm text-[var(--color-text)]">
        <p className="mb-2 text-xs font-semibold tracking-wide text-[var(--color-accent)] uppercase">
          Mensaje del stakeholder
        </p>
        <Paragraphs text={brief} />
      </div>

      {steps.map((step, i) => {
        const isSolved = !!solved[step.id];
        const isCurrent = i === current;
        if (!isSolved && !isCurrent) return null;
        const fb = feedback[step.id];
        const tries = attempts[step.id] ?? 0;
        const revealed = !!answers[`${step.id}:revealed`];
        const out = outputs[step.id];
        return (
          <section
            key={step.id}
            aria-label={`Paso ${i + 1}`}
            className={
              'rounded-lg border p-5 ' +
              (isSolved
                ? 'border-[var(--color-success)]/50 bg-[var(--color-success)]/5'
                : 'border-[var(--color-border)] bg-[var(--color-bg-raised)]')
            }
          >
            <h2 className="text-sm font-semibold text-[var(--color-text)]">
              Paso {i + 1} de {steps.length}{' '}
              {isSolved && <span className="text-[var(--color-success)]">· completado ✔</span>}
            </h2>
            <div className="mt-2 text-sm text-[var(--color-text)]">
              <Paragraphs text={step.prompt} />
            </div>

            {step.tool !== 'reasoning' && (
              <div className="mt-4 space-y-3">
                <Editor
                  label={`Editor ${step.tool === 'sql' ? 'SQL' : 'Python'} del paso ${i + 1}`}
                  language={step.tool}
                  value={String(answers[`${step.id}:code`] ?? '')}
                  onChange={(v) => setAnswer(`${step.id}:code`, v)}
                  schema={schema}
                  onRun={() => runCode(step)}
                  minHeight="9rem"
                />
                <button
                  type="button"
                  disabled={busy}
                  onClick={() => runCode(step)}
                  className={`${btn} border border-[var(--color-border)] text-[var(--color-text)] hover:bg-[var(--color-bg-subtle)]`}
                >
                  {busy ? 'Ejecutando…' : 'Ejecutar'}
                </button>
                {errors[step.id] && (
                  <pre
                    className="overflow-x-auto rounded-md border border-[var(--color-danger)] bg-[var(--color-danger)]/10 p-3 text-xs whitespace-pre-wrap text-[var(--color-text)]"
                    role="alert"
                  >
                    {errors[step.id]}
                  </pre>
                )}
                {out && typeof out !== 'string' && <ResultTable {...out} />}
                {typeof out === 'string' && (
                  <pre className="overflow-x-auto rounded-md border border-[var(--color-border)] bg-[var(--color-bg-subtle)] p-3 font-mono text-xs whitespace-pre-wrap text-[var(--color-text)]">
                    {out}
                  </pre>
                )}
              </div>
            )}

            {!isSolved && (
              <div className="mt-4 space-y-3">
                {step.answerType === 'numeric' && (
                  <div>
                    <label
                      htmlFor={`ans-${step.id}`}
                      className="text-xs text-[var(--color-text-muted)]"
                    >
                      Tu respuesta (número; puedes usar coma decimal)
                    </label>
                    <input
                      id={`ans-${step.id}`}
                      type="text"
                      inputMode="decimal"
                      autoComplete="off"
                      className="mt-1 block w-48 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-2 py-1 text-sm text-[var(--color-text)]"
                      value={String(answers[step.id] ?? '')}
                      onChange={(e) => setAnswer(step.id, e.target.value)}
                    />
                  </div>
                )}
                {step.answerType === 'single' &&
                  (step.options ?? []).map((opt, k) => (
                    <label
                      key={k}
                      className="flex items-start gap-2 text-sm text-[var(--color-text)]"
                    >
                      <input
                        type="radio"
                        name={`ans-${step.id}`}
                        className="mt-0.5 size-4 accent-[var(--color-accent)]"
                        checked={answers[step.id] === k}
                        onChange={() => setAnswer(step.id, k)}
                      />
                      <InlineText text={opt} />
                    </label>
                  ))}
                {step.answerType === 'multiple' &&
                  (step.options ?? []).map((opt, k) => {
                    const sel = (answers[step.id] as number[] | undefined) ?? [];
                    return (
                      <label
                        key={k}
                        className="flex items-start gap-2 text-sm text-[var(--color-text)]"
                      >
                        <input
                          type="checkbox"
                          className="mt-0.5 size-4 accent-[var(--color-accent)]"
                          checked={sel.includes(k)}
                          onChange={(e) =>
                            setAnswer(
                              step.id,
                              e.target.checked ? [...sel, k].sort() : sel.filter((x) => x !== k),
                            )
                          }
                        />
                        <InlineText text={opt} />
                      </label>
                    );
                  })}
                {step.answerType === 'text-self-assessed' && (
                  <textarea
                    aria-label="Tu respuesta"
                    rows={5}
                    className="w-full rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] p-2 text-sm text-[var(--color-text)]"
                    value={String(answers[step.id] ?? '')}
                    onChange={(e) => setAnswer(step.id, e.target.value)}
                  />
                )}

                <div className="flex flex-wrap items-center gap-2">
                  <button
                    type="button"
                    onClick={() => check(step)}
                    className={`${btn} bg-[var(--color-accent)] text-[var(--color-accent-contrast)] hover:opacity-90`}
                  >
                    {step.answerType === 'text-self-assessed' ? 'Continuar' : 'Comprobar'}
                  </button>
                  <button
                    type="button"
                    disabled={(hints[step.id] ?? 0) >= step.hints.length}
                    onClick={() => setHints((h) => ({ ...h, [step.id]: (h[step.id] ?? 0) + 1 }))}
                    className={`${btn} border border-[var(--color-border)] text-[var(--color-text)] hover:bg-[var(--color-bg-subtle)]`}
                  >
                    Pista ({hints[step.id] ?? 0}/{step.hints.length})
                  </button>
                  {tries >= 2 && step.answerType !== 'text-self-assessed' && (
                    <button
                      type="button"
                      onClick={() => revealAnswer(step)}
                      className={`${btn} text-[var(--color-text-muted)] hover:text-[var(--color-text)]`}
                    >
                      Ver la respuesta
                    </button>
                  )}
                </div>
                {(hints[step.id] ?? 0) > 0 && (
                  <ol className="space-y-1 text-sm text-[var(--color-text)]">
                    {step.hints.slice(0, hints[step.id]).map((h, k) => (
                      <li key={k}>
                        <strong>Pista {k + 1}:</strong> <InlineText text={h} />
                      </li>
                    ))}
                  </ol>
                )}
                {fb === false && (
                  <p className="text-sm font-semibold text-[var(--color-danger)]" role="status">
                    No es correcto todavía. Revisa tu consulta y vuelve a intentarlo.
                  </p>
                )}
                {fb === false && step.answerType === 'text-self-assessed' && (
                  <p className="text-sm text-[var(--color-text-muted)]">
                    Escribe al menos una frase completa.
                  </p>
                )}
              </div>
            )}

            {isSolved && (
              <div className="mt-4 rounded-md border-l-4 border-[var(--color-success)] bg-[var(--color-success)]/10 p-3 text-sm text-[var(--color-text)]">
                {revealed && (
                  <p className="mb-1 font-semibold">
                    Respuesta:{' '}
                    {Array.isArray(step.answer)
                      ? step.answer.join(', ')
                      : String(step.answer).replace('.', ',')}
                  </p>
                )}
                <Paragraphs text={step.explanation} />
              </div>
            )}
          </section>
        );
      })}

      {finished && (
        <section
          aria-label="Informe final"
          className="rounded-lg border border-[var(--color-accent)]/40 bg-[var(--color-bg-raised)] p-5"
        >
          <h2 className="text-lg font-bold text-[var(--color-text)]">Tu informe</h2>
          <p className="mt-1 text-sm text-[var(--color-text-muted)]">
            Redacta tu recomendación para quien te escribió: la conclusión primero, luego la
            evidencia y los límites.
          </p>
          <textarea
            aria-label="Tu informe"
            rows={8}
            className="mt-3 w-full rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] p-2 text-sm text-[var(--color-text)]"
            value={String(answers.__report ?? '')}
            onChange={(e) => setAnswer('__report', e.target.value)}
          />
          <h3 className="mt-4 text-sm font-semibold text-[var(--color-text)]">Autoevaluación</h3>
          <ul className="mt-2 space-y-1">
            {rubric.map((item, k) => (
              <li key={k}>
                <label className="flex items-start gap-2 text-sm text-[var(--color-text)]">
                  <input
                    type="checkbox"
                    className="mt-0.5 size-4 accent-[var(--color-accent)]"
                    checked={!!rubricChecked[k]}
                    onChange={(e) => {
                      const next = rubric.map((_, j) =>
                        j === k ? e.target.checked : !!rubricChecked[j],
                      );
                      setAnswer('__rubric', next);
                    }}
                  />
                  {item}
                </label>
              </li>
            ))}
          </ul>
          <button
            type="button"
            onClick={() => {
              setShowModel(true);
              persist(answers, true);
            }}
            className={`${btn} mt-4 bg-[var(--color-accent)] text-[var(--color-accent-contrast)] hover:opacity-90`}
          >
            Ver el informe modelo y terminar el caso
          </button>
          {(showModel || saved?.completed) && (
            <div className="mt-4 rounded-md border border-[var(--color-border)] bg-[var(--color-bg-subtle)] p-4 text-sm text-[var(--color-text)]">
              <p className="mb-2 text-xs font-semibold tracking-wide text-[var(--color-text-muted)] uppercase">
                Informe modelo
              </p>
              <Paragraphs text={modelReport} />
            </div>
          )}
        </section>
      )}
    </div>
  );
}
