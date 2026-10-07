import { useStore } from '@nanostores/react';
import { useEffect, useRef, useState } from 'react';
import {
  exportProgress,
  hydrateProgress,
  importProgress,
  progressStore,
  resetProgress,
} from '../../lib/progress';

interface LessonInfo {
  id: string;
  title: string;
  module: string;
  moduleTitle: string;
  url: string;
}

export default function ProgressPanel({ lessons }: { lessons: LessonInfo[] }) {
  const progress = useStore(progressStore);
  const fileRef = useRef<HTMLInputElement>(null);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    hydrateProgress();
  }, []);

  const read = lessons.filter((l) => progress.lessonsRead[l.id]);
  const modules = [...new Map(lessons.map((l) => [l.module, l.moduleTitle])).entries()];
  const quizEntries = Object.entries(progress.quizScores);
  const labs = Object.values(progress.labs);
  const labsPassed = labs.filter((l) => l.status === 'passed').length;
  const srsCount = Object.keys(progress.srs).length;

  function download() {
    const blob = new Blob([exportProgress()], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `data-analyst-academy-progreso-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  async function onImport(file: File | undefined) {
    if (!file) return;
    const result = importProgress(await file.text());
    setMessage(
      result.ok ? 'Progreso importado correctamente.' : `No se pudo importar: ${result.error}`,
    );
  }

  const card = 'rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-raised)] p-5';

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-4">
        {[
          ['Lecciones leídas', `${read.length}/${lessons.length}`],
          ['Tests intentados', String(quizEntries.length)],
          ['Labs superados', String(labsPassed)],
          ['En repaso espaciado', String(srsCount)],
        ].map(([label, value]) => (
          <div key={label} className={card}>
            <p className="text-xs text-[var(--color-text-muted)]">{label}</p>
            <p className="mt-1 text-2xl font-bold text-[var(--color-text)]">{value}</p>
          </div>
        ))}
      </div>

      <div className={card}>
        <h2 className="font-semibold text-[var(--color-text)]">Por módulo</h2>
        {modules.length === 0 && (
          <p className="mt-2 text-sm text-[var(--color-text-muted)]">
            Aún no hay módulos publicados.
          </p>
        )}
        <ul className="mt-3 space-y-3">
          {modules.map(([id, title]) => {
            const mine = lessons.filter((l) => l.module === id);
            const done = mine.filter((l) => progress.lessonsRead[l.id]).length;
            const pct = Math.round((done / mine.length) * 100);
            const best = progress.quizScores[`module:${id}`]?.best;
            return (
              <li key={id}>
                <div className="flex flex-wrap items-baseline justify-between gap-2 text-sm">
                  <span className="font-medium text-[var(--color-text)]">{title}</span>
                  <span className="text-xs text-[var(--color-text-muted)]">
                    {done}/{mine.length} lecciones
                    {best !== undefined && ` · test: ${Math.round(best * 100)} %`}
                  </span>
                </div>
                <div
                  className="mt-1 h-2 overflow-hidden rounded-full bg-[var(--color-bg-subtle)]"
                  role="progressbar"
                  aria-valuenow={pct}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label={`Progreso de ${title}`}
                >
                  <div className="h-full bg-[var(--color-accent)]" style={{ width: `${pct}%` }} />
                </div>
              </li>
            );
          })}
        </ul>
      </div>

      {progress.exams.length > 0 && (
        <div className={card}>
          <h2 className="font-semibold text-[var(--color-text)]">Exámenes</h2>
          <ul className="mt-3 space-y-1 text-sm text-[var(--color-text)]">
            {[...progress.exams]
              .reverse()
              .slice(0, 10)
              .map((e) => (
                <li key={e.date}>
                  {new Date(e.date).toLocaleString('es-ES')} — {e.score}/{e.total} (
                  {Math.round((e.score / e.total) * 100)} %)
                </li>
              ))}
          </ul>
        </div>
      )}

      <div className={card}>
        <h2 className="font-semibold text-[var(--color-text)]">Tus datos</h2>
        <p className="mt-1 text-sm text-[var(--color-text-muted)]">
          Todo se guarda solo en este navegador (sin cuenta ni servidor). Exporta una copia para
          llevarla a otro dispositivo o como copia de seguridad.
        </p>
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={download}
            className="rounded-md bg-[var(--color-accent)] px-3 py-1.5 text-sm font-semibold text-[var(--color-accent-contrast)] hover:opacity-90"
          >
            Exportar JSON
          </button>
          <button
            type="button"
            onClick={() => fileRef.current?.click()}
            className="rounded-md border border-[var(--color-border)] px-3 py-1.5 text-sm font-semibold text-[var(--color-text)] hover:bg-[var(--color-bg-subtle)]"
          >
            Importar JSON
          </button>
          <input
            ref={fileRef}
            type="file"
            accept="application/json"
            className="hidden"
            aria-label="Archivo de progreso a importar"
            onChange={(e) => onImport(e.target.files?.[0])}
          />
          <button
            type="button"
            onClick={() => {
              if (window.confirm('¿Borrar todo tu progreso? Esta acción no se puede deshacer.')) {
                resetProgress();
                setMessage('Progreso borrado.');
              }
            }}
            className="rounded-md px-3 py-1.5 text-sm font-semibold text-[var(--color-danger)] hover:underline"
          >
            Borrar progreso
          </button>
        </div>
        <p className="mt-2 text-sm text-[var(--color-text)]" role="status">
          {message}
        </p>
      </div>
    </div>
  );
}
