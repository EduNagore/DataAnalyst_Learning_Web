import { useStore } from '@nanostores/react';
import { useEffect } from 'react';
import { hydrateProgress, progressStore } from '../../lib/progress';

export default function CaseStatus({ caseId, total }: { caseId: string; total: number }) {
  const progress = useStore(progressStore);
  useEffect(() => {
    hydrateProgress();
  }, []);
  const c = progress.cases[caseId];
  if (c?.completed)
    return <span className="text-xs text-[var(--color-success)]">Completado ✔</span>;
  if (c)
    return (
      <span className="text-xs text-[var(--color-text-muted)]">
        En curso ({Math.min(c.step, total)}/{total})
      </span>
    );
  return <span className="text-xs text-[var(--color-text-muted)]">Sin empezar</span>;
}
