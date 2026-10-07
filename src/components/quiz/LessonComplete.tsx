import { useStore } from '@nanostores/react';
import { useEffect } from 'react';
import { hydrateProgress, markLessonRead, progressStore } from '../../lib/progress';

/** Botón "Marcar lección como completada" (estado en localStorage). */
export default function LessonComplete({ lessonId }: { lessonId: string }) {
  const progress = useStore(progressStore);
  useEffect(() => {
    hydrateProgress();
  }, []);

  const doneAt = progress.lessonsRead[lessonId];

  return (
    <div className="my-6 flex flex-wrap items-center gap-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-subtle)] p-4">
      {doneAt ? (
        <p className="text-sm text-[var(--color-text)]" role="status">
          Lección completada el {new Date(doneAt).toLocaleDateString('es-ES')}.
        </p>
      ) : (
        <>
          <p className="text-sm text-[var(--color-text-muted)]">
            ¿Has terminado de leer esta lección?
          </p>
          <button
            type="button"
            onClick={() => markLessonRead(lessonId)}
            className="rounded-md bg-[var(--color-accent)] px-3 py-1.5 text-sm font-semibold text-[var(--color-accent-contrast)] hover:opacity-90"
          >
            Marcar como completada
          </button>
        </>
      )}
    </div>
  );
}
