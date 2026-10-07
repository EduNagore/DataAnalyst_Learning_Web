import { useEffect, useMemo, useRef, useState } from 'react';
import {
  PASS_THRESHOLD,
  parseNumberEs,
  scoreQuiz,
  type QuizQuestion,
  type QuizResponse,
  type QuizResult,
} from '../../lib/quiz';
import { hydrateProgress, recordExam, recordQuizScore, recordSrsResult } from '../../lib/progress';
import InlineText from './InlineText';
import QuestionView, { type ClientQuestion, type UiAnswer } from './QuestionView';

interface Props {
  /** Clave de progreso (lección, módulo...). Para 'review' se ignora. */
  quizId: string;
  questions: ClientQuestion[];
  mode: 'lesson' | 'module' | 'exam' | 'review';
  title?: string;
  passThreshold?: number;
  /** Solo examen: tiempo máximo en minutos (0 o ausente = sin límite). */
  timeLimitMinutes?: number;
  /** Se llama con el resultado al comprobar (para informes por módulo, etc.). */
  onFinish?: (result: QuizResult) => void;
}

function toResponse(q: QuizQuestion, answer: UiAnswer): QuizResponse | undefined {
  if (answer === undefined) return undefined;
  if (q.type === 'numeric') {
    if (typeof answer !== 'string') return undefined;
    const n = parseNumberEs(answer);
    return Number.isNaN(n) ? undefined : n;
  }
  if (q.type === 'order') return Array.isArray(answer) && answer.length > 0 ? answer : undefined;
  if (q.type === 'multiple') return Array.isArray(answer) && answer.length > 0 ? answer : undefined;
  return typeof answer === 'number' ? answer : undefined;
}

function formatCorrect(q: QuizQuestion): string {
  const answers = Array.isArray(q.answer) ? q.answer : [q.answer];
  if (q.type === 'numeric') return String(answers[0]).replace('.', ',');
  const opts = q.options ?? [];
  if (q.type === 'order') return answers.map((i, n) => `${n + 1}. ${opts[i]}`).join('  →  ');
  return answers.map((i) => opts[i]).join(' · ');
}

export default function Quiz({
  quizId,
  questions,
  mode,
  title,
  passThreshold = PASS_THRESHOLD,
  timeLimitMinutes = 0,
  onFinish,
}: Props) {
  const [answers, setAnswers] = useState<Record<string, UiAnswer>>({});
  const [result, setResult] = useState<QuizResult | null>(null);
  const [attempt, setAttempt] = useState(0);
  const [secondsLeft, setSecondsLeft] = useState(timeLimitMinutes * 60);
  const resultRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    hydrateProgress();
  }, []);

  const responses = useMemo(() => {
    const out: Record<string, QuizResponse> = {};
    for (const q of questions) {
      const r = toResponse(q, answers[q.id]);
      if (r !== undefined) out[q.id] = r;
    }
    return out;
  }, [answers, questions]);

  const unanswered = questions.length - Object.keys(responses).length;

  function finish() {
    const scored = scoreQuiz(questions, responses);
    setResult(scored);
    onFinish?.(scored);
    for (const q of questions) {
      if (responses[q.id] !== undefined || mode !== 'review') {
        recordSrsResult(q.id, scored.byQuestion[q.id]);
      }
    }
    if (mode === 'lesson' || mode === 'module') recordQuizScore(quizId, scored.score);
    if (mode === 'exam') {
      const byModule: Record<string, number> = {};
      const totals: Record<string, number> = {};
      for (const q of questions) {
        const m = q.module ?? 'otros';
        totals[m] = (totals[m] ?? 0) + 1;
        if (scored.byQuestion[q.id]) byModule[m] = (byModule[m] ?? 0) + 1;
      }
      for (const m of Object.keys(totals)) byModule[m] = (byModule[m] ?? 0) / totals[m];
      recordExam({
        date: new Date().toISOString(),
        score: scored.correctCount,
        total: scored.total,
        byModule,
      });
    }
    setTimeout(() => resultRef.current?.focus(), 0);
  }

  // Cuenta atrás del examen: al llegar a 0 se corrige solo.
  useEffect(() => {
    if (mode !== 'exam' || !timeLimitMinutes || result) return;
    const id = setInterval(() => {
      setSecondsLeft((s) => {
        if (s <= 1) {
          clearInterval(id);
          return 0;
        }
        return s - 1;
      });
    }, 1000);
    return () => clearInterval(id);
  }, [mode, timeLimitMinutes, result, attempt]);

  useEffect(() => {
    if (mode === 'exam' && timeLimitMinutes && secondsLeft === 0 && !result) finish();
  }, [secondsLeft]);

  function reset() {
    setAnswers({});
    setResult(null);
    setAttempt((a) => a + 1);
    setSecondsLeft(timeLimitMinutes * 60);
  }

  const passed = result ? result.score >= passThreshold : false;
  const mm = String(Math.floor(secondsLeft / 60)).padStart(2, '0');
  const ss = String(secondsLeft % 60).padStart(2, '0');

  return (
    <section aria-label={title ?? 'Test'} className="my-8">
      {title && <h2 className="text-xl font-bold text-[var(--color-text)]">{title}</h2>}

      {mode === 'exam' && timeLimitMinutes > 0 && !result && (
        <p
          className="mt-2 font-mono text-sm text-[var(--color-text)]"
          role="timer"
          aria-label="Tiempo restante"
        >
          Tiempo restante: {mm}:{ss}
        </p>
      )}

      <div ref={resultRef} tabIndex={-1} aria-live="polite" className="outline-none">
        {result && (
          <div
            className={
              'mt-4 rounded-lg border p-4 ' +
              (mode === 'review' || passed
                ? 'border-[var(--color-success)] bg-[var(--color-success)]/10'
                : 'border-[var(--color-warning)] bg-[var(--color-warning)]/10')
            }
          >
            <p className="text-lg font-semibold text-[var(--color-text)]">
              {result.correctCount} de {result.total} ({Math.round(result.score * 100)} %)
            </p>
            <p className="mt-1 text-sm text-[var(--color-text)]">
              {mode === 'review'
                ? 'Las preguntas acertadas avanzan de caja; las falladas vuelven a la caja 1.'
                : passed
                  ? `Aprobado (umbral: ${Math.round(passThreshold * 100)} %).`
                  : `Por debajo del umbral de aprobado (${Math.round(passThreshold * 100)} %). Repasa las secciones enlazadas y vuelve a intentarlo.`}
            </p>
          </div>
        )}
      </div>

      <div className="mt-4 space-y-4">
        {questions.map((q, i) => {
          const ok = result?.byQuestion[q.id];
          return (
            <div key={`${q.id}:${attempt}`}>
              <QuestionView
                question={q}
                index={i}
                answer={answers[q.id]}
                onChange={(v) => setAnswers((prev) => ({ ...prev, [q.id]: v }))}
                disabled={result !== null}
                seed={String(attempt)}
              />
              {result && (
                <div
                  className={
                    'mt-2 rounded-md border-l-4 p-3 text-sm ' +
                    (ok
                      ? 'border-[var(--color-success)] bg-[var(--color-success)]/10'
                      : 'border-[var(--color-danger)] bg-[var(--color-danger)]/10')
                  }
                >
                  <p className="font-semibold text-[var(--color-text)]">
                    {ok ? 'Correcta' : 'Incorrecta'}
                    {!ok && (
                      <span className="font-normal">
                        {' '}
                        — respuesta correcta: <InlineText text={formatCorrect(q)} />
                      </span>
                    )}
                  </p>
                  <p className="mt-1 text-[var(--color-text)]">
                    <InlineText text={q.explanation} />
                  </p>
                  {q.refUrl && (
                    <a
                      href={q.refUrl}
                      className="mt-1 inline-block text-[var(--color-accent)] hover:underline"
                    >
                      Repasa esta sección{q.lessonTitle ? ` (${q.lessonTitle})` : ''} →
                    </a>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-3">
        {!result ? (
          <button
            type="button"
            onClick={finish}
            className="rounded-md bg-[var(--color-accent)] px-4 py-2 text-sm font-semibold text-[var(--color-accent-contrast)] hover:opacity-90"
          >
            Comprobar respuestas
          </button>
        ) : (
          <button
            type="button"
            onClick={reset}
            className="rounded-md border border-[var(--color-border)] px-4 py-2 text-sm font-semibold text-[var(--color-text)] hover:bg-[var(--color-bg-subtle)]"
          >
            Volver a intentarlo
          </button>
        )}
        {!result && unanswered > 0 && (
          <span className="text-xs text-[var(--color-text-muted)]">
            {unanswered} sin responder (contarán como falladas)
          </span>
        )}
      </div>
    </section>
  );
}
