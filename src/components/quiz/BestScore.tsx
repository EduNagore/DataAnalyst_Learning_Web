import { useStore } from '@nanostores/react';
import { useEffect } from 'react';
import { hydrateProgress, progressStore } from '../../lib/progress';

/** Mejor puntuación guardada de un quiz (o "Sin intentar"). */
export default function BestScore({ quizId }: { quizId: string }) {
  const progress = useStore(progressStore);
  useEffect(() => {
    hydrateProgress();
  }, []);
  const score = progress.quizScores[quizId];
  if (!score) return <span className="text-xs text-[var(--color-text-muted)]">Sin intentar</span>;
  const pct = Math.round(score.best * 100);
  return (
    <span className="text-xs text-[var(--color-text-muted)]">
      Mejor: <strong className="text-[var(--color-text)]">{pct} %</strong>
      {pct >= 80 ? ' · Aprobado' : ''} · {score.attempts}{' '}
      {score.attempts === 1 ? 'intento' : 'intentos'}
    </span>
  );
}
