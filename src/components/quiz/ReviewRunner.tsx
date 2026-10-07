import { useStore } from '@nanostores/react';
import { useEffect, useState } from 'react';
import { hydrateProgress, progressStore } from '../../lib/progress';
import { LEITNER_INTERVALS_DAYS, dueCards } from '../../lib/srs';
import { url } from '../../lib/url';
import Quiz from './Quiz';
import type { ClientQuestion } from './QuestionView';

const SESSION_SIZE = 20;

/** Repaso espaciado Leitner de las preguntas falladas. */
export default function ReviewRunner() {
  const progress = useStore(progressStore);
  const [bank, setBank] = useState<ClientQuestion[] | null>(null);
  const [ready, setReady] = useState(false);
  const [session, setSession] = useState<ClientQuestion[] | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    hydrateProgress();
    setReady(true);
    fetch(url('/practica/questions.json'))
      .then((r) => r.json())
      .then(setBank)
      .catch(() => setError(true));
  }, []);

  if (error)
    return (
      <p className="text-sm text-[var(--color-danger)]">No se pudo cargar el banco de preguntas.</p>
    );
  if (!bank || !ready) return <p className="text-sm text-[var(--color-text-muted)]">Cargando…</p>;

  const srsIds = Object.keys(progress.srs);
  const knownIds = new Set(bank.map((q) => q.id));
  const due = dueCards(progress.srs).filter((id) => knownIds.has(id));
  const perBox = [1, 2, 3, 4, 5].map(
    (b) => srsIds.filter((id) => progress.srs[id].box === b && knownIds.has(id)).length,
  );

  if (session) {
    return (
      <Quiz
        key={session.map((q) => q.id).join()}
        quizId="review"
        mode="review"
        title="Repaso"
        questions={session}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-raised)] p-4">
        <p className="text-sm text-[var(--color-text)]">
          <strong>{due.length}</strong>{' '}
          {due.length === 1 ? 'pregunta pendiente' : 'preguntas pendientes'} de repasar hoy
          {srsIds.length > 0 && ` (${srsIds.length} en total en tu sistema de repaso)`}.
        </p>
        <table className="mt-3 text-left text-xs">
          <thead>
            <tr className="text-[var(--color-text-muted)]">
              {[1, 2, 3, 4, 5].map((b) => (
                <th key={b} scope="col" className="pr-6 font-medium">
                  Caja {b}{' '}
                  <span className="font-normal">
                    ({LEITNER_INTERVALS_DAYS[b as 1 | 2 | 3 | 4 | 5]} d)
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr className="text-[var(--color-text)]">
              {perBox.map((n, i) => (
                <td key={i} className="pr-6 text-base font-semibold">
                  {n}
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>

      {due.length > 0 ? (
        <button
          type="button"
          onClick={() => {
            const ids = due.slice(0, SESSION_SIZE);
            setSession(ids.map((id) => bank.find((q) => q.id === id)!).filter(Boolean));
          }}
          className="rounded-md bg-[var(--color-accent)] px-4 py-2 text-sm font-semibold text-[var(--color-accent-contrast)] hover:opacity-90"
        >
          Empezar repaso ({Math.min(due.length, SESSION_SIZE)} preguntas)
        </button>
      ) : (
        <p className="text-sm text-[var(--color-text-muted)]">
          No tienes nada pendiente. Las preguntas que falles en lecciones, tests y exámenes
          aparecerán aquí.{' '}
          <a className="text-[var(--color-accent)] hover:underline" href={url('/practica/tests/')}>
            Hacer un test
          </a>
        </p>
      )}
    </div>
  );
}
