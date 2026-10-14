import { useEffect, useRef, useState } from 'react';

function format(total: number) {
  const sign = total < 0 ? '−' : '';
  const abs = Math.abs(total);
  const m = Math.floor(abs / 60);
  const s = abs % 60;
  return `${sign}${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

/** Cronómetro de cuenta atrás para los ejercicios de entrevista. No bloquea el lab: solo informa. */
export default function InterviewTimer({ minutes }: { minutes: number }) {
  const total = minutes * 60;
  const [left, setLeft] = useState(total);
  const [running, setRunning] = useState(false);
  const started = useRef(false);

  useEffect(() => {
    if (!running) return;
    const id = window.setInterval(() => setLeft((l) => l - 1), 1000);
    return () => window.clearInterval(id);
  }, [running]);

  const overtime = left < 0;
  const warning = !overtime && left <= total * 0.2;

  return (
    <div
      className="mt-4 flex flex-wrap items-center gap-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-subtle)] p-3"
      role="group"
      aria-label="Cronómetro de entrevista"
    >
      <span className="text-xs font-semibold tracking-wide text-[var(--color-text-muted)] uppercase">
        Modo entrevista
      </span>
      <span
        className="font-mono text-xl font-semibold tabular-nums"
        style={{
          color: overtime
            ? 'var(--color-danger)'
            : warning
              ? 'var(--color-warning)'
              : 'var(--color-text)',
        }}
        role="timer"
        aria-live="off"
      >
        {format(left)}
      </span>
      <button
        type="button"
        className="rounded-md border border-[var(--color-border)] bg-[var(--color-bg-raised)] px-3 py-1 text-sm text-[var(--color-text)] hover:border-[var(--color-accent)]"
        onClick={() => {
          started.current = true;
          setRunning((r) => !r);
        }}
      >
        {running ? 'Pausar' : started.current ? 'Reanudar' : 'Empezar'}
      </button>
      <button
        type="button"
        className="rounded-md border border-[var(--color-border)] bg-[var(--color-bg-raised)] px-3 py-1 text-sm text-[var(--color-text)] hover:border-[var(--color-accent)]"
        onClick={() => {
          setRunning(false);
          started.current = false;
          setLeft(total);
        }}
      >
        Reiniciar
      </button>
      <span className="text-xs text-[var(--color-text-muted)]">
        {overtime
          ? 'Tiempo agotado: puedes seguir, pero en una entrevista real tendrías que entregar.'
          : `Tiempo orientativo: ${minutes} min. Piensa en voz alta y valida el resultado antes de entregar.`}
      </span>
    </div>
  );
}
