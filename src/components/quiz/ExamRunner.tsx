import { useEffect, useMemo, useState } from 'react';
import { seededShuffle, type QuizResult } from '../../lib/quiz';
import { url } from '../../lib/url';
import Quiz from './Quiz';
import type { ClientQuestion } from './QuestionView';

type Phase = 'loading' | 'setup' | 'running' | 'error';

/** Modo examen: elige módulos, nº de preguntas y temporizador; informe por módulo al terminar. */
export default function ExamRunner() {
  const [phase, setPhase] = useState<Phase>('loading');
  const [bank, setBank] = useState<ClientQuestion[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [count, setCount] = useState(20);
  const [timed, setTimed] = useState(false);
  const [exam, setExam] = useState<ClientQuestion[]>([]);
  const [run, setRun] = useState(0);
  const [report, setReport] = useState<QuizResult | null>(null);

  useEffect(() => {
    fetch(url('/practica/questions.json'))
      .then((r) => r.json())
      .then((data: ClientQuestion[]) => {
        setBank(data);
        setSelected([...new Set(data.map((q) => q.module ?? ''))]);
        setPhase('setup');
      })
      .catch(() => setPhase('error'));
  }, []);

  const modules = useMemo(() => {
    const map = new Map<string, string>();
    for (const q of bank) map.set(q.module ?? '', q.moduleTitle ?? q.module ?? '');
    return [...map.entries()].map(([id, title]) => ({ id, title }));
  }, [bank]);

  const pool = bank.filter((q) => selected.includes(q.module ?? ''));
  const countOptions = [20, 40, 60].filter((n) => n < pool.length);
  const effectiveCount = Math.min(count, pool.length);

  function start() {
    const picked = seededShuffle(pool, `exam:${Date.now()}`).slice(0, effectiveCount);
    setExam(picked);
    setReport(null);
    setRun((r) => r + 1);
    setPhase('running');
  }

  if (phase === 'loading')
    return <p className="text-sm text-[var(--color-text-muted)]">Cargando preguntas…</p>;
  if (phase === 'error')
    return (
      <p className="text-sm text-[var(--color-danger)]">No se pudo cargar el banco de preguntas.</p>
    );

  if (phase === 'setup') {
    return (
      <div className="space-y-6">
        <fieldset>
          <legend className="text-sm font-semibold text-[var(--color-text)]">Módulos</legend>
          <div className="mt-2 space-y-1">
            {modules.map((m) => (
              <label
                key={m.id}
                className="flex items-center gap-2 text-sm text-[var(--color-text)]"
              >
                <input
                  type="checkbox"
                  className="size-4 accent-[var(--color-accent)]"
                  checked={selected.includes(m.id)}
                  onChange={(e) =>
                    setSelected((prev) =>
                      e.target.checked ? [...prev, m.id] : prev.filter((x) => x !== m.id),
                    )
                  }
                />
                {m.title}
              </label>
            ))}
          </div>
        </fieldset>

        <div>
          <label htmlFor="exam-count" className="text-sm font-semibold text-[var(--color-text)]">
            Número de preguntas
          </label>
          <select
            id="exam-count"
            className="mt-1 block rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-2 py-1 text-sm text-[var(--color-text)]"
            value={effectiveCount}
            onChange={(e) => setCount(Number(e.target.value))}
          >
            {countOptions.map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
            <option value={pool.length}>Todas ({pool.length})</option>
          </select>
        </div>

        <label className="flex items-center gap-2 text-sm text-[var(--color-text)]">
          <input
            type="checkbox"
            className="size-4 accent-[var(--color-accent)]"
            checked={timed}
            onChange={(e) => setTimed(e.target.checked)}
          />
          Con temporizador (~1 minuto por pregunta)
        </label>

        <button
          type="button"
          disabled={pool.length === 0}
          onClick={start}
          className="rounded-md bg-[var(--color-accent)] px-4 py-2 text-sm font-semibold text-[var(--color-accent-contrast)] hover:opacity-90 disabled:opacity-50"
        >
          Empezar examen
        </button>
      </div>
    );
  }

  const byModule = report
    ? modules
        .map((m) => {
          const qs = exam.filter((q) => q.module === m.id);
          const right = qs.filter((q) => report.byQuestion[q.id]).length;
          return { ...m, total: qs.length, right };
        })
        .filter((m) => m.total > 0)
    : [];

  return (
    <div>
      <Quiz
        key={run}
        quizId="exam"
        mode="exam"
        title="Examen"
        questions={exam}
        timeLimitMinutes={timed ? exam.length : 0}
        onFinish={setReport}
      />
      {report && (
        <div className="mt-8 rounded-lg border border-[var(--color-border)] p-4">
          <h2 className="text-lg font-semibold text-[var(--color-text)]">Informe por módulo</h2>
          <table className="mt-3 w-full text-left text-sm">
            <thead>
              <tr className="border-b border-[var(--color-border)] text-xs text-[var(--color-text-muted)]">
                <th scope="col" className="py-1 font-medium">
                  Módulo
                </th>
                <th scope="col" className="py-1 font-medium">
                  Aciertos
                </th>
                <th scope="col" className="py-1 font-medium">
                  Repasar
                </th>
              </tr>
            </thead>
            <tbody>
              {byModule.map((m) => (
                <tr key={m.id} className="border-b border-[var(--color-border)]/50 last:border-0">
                  <td className="py-1.5 text-[var(--color-text)]">{m.title}</td>
                  <td className="py-1.5 text-[var(--color-text)]">
                    {m.right}/{m.total} ({Math.round((m.right / m.total) * 100)} %)
                  </td>
                  <td className="py-1.5">
                    <a
                      className="text-[var(--color-accent)] hover:underline"
                      href={url(`/teoria/${m.id}/`)}
                    >
                      Ir al módulo
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <button
            type="button"
            onClick={() => setPhase('setup')}
            className="mt-4 text-sm text-[var(--color-accent)] hover:underline"
          >
            Configurar otro examen
          </button>
        </div>
      )}
    </div>
  );
}
