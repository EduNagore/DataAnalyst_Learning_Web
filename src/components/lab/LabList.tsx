import { useStore } from '@nanostores/react';
import { useEffect, useState } from 'react';
import { hydrateProgress, progressStore } from '../../lib/progress';
import { url } from '../../lib/url';

export interface LabSummary {
  id: string;
  title: string;
  description: string;
  language: 'sql' | 'python';
  difficulty: 1 | 2 | 3;
  estimatedMinutes: number;
  moduleTitle: string;
}

const DIFFICULTY = ['', 'Fácil', 'Media', 'Difícil'];

export default function LabList({ labs }: { labs: LabSummary[] }) {
  const progress = useStore(progressStore);
  const [language, setLanguage] = useState('all');
  const [difficulty, setDifficulty] = useState('all');
  const [status, setStatus] = useState('all');

  useEffect(() => {
    hydrateProgress();
  }, []);

  const shown = labs.filter((l) => {
    const st = progress.labs[l.id]?.status;
    return (
      (language === 'all' || l.language === language) &&
      (difficulty === 'all' || String(l.difficulty) === difficulty) &&
      (status === 'all' ||
        (status === 'passed' && st === 'passed') ||
        (status === 'pending' && st !== 'passed'))
    );
  });

  const select =
    'rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-2 py-1 text-sm text-[var(--color-text)]';

  return (
    <div>
      <div className="flex flex-wrap gap-4">
        <label className="text-xs text-[var(--color-text-muted)]">
          Lenguaje
          <select
            className={`${select} mt-1 block`}
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
          >
            <option value="all">Todos</option>
            <option value="sql">SQL</option>
            <option value="python">Python</option>
          </select>
        </label>
        <label className="text-xs text-[var(--color-text-muted)]">
          Dificultad
          <select
            className={`${select} mt-1 block`}
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
          >
            <option value="all">Todas</option>
            <option value="1">Fácil</option>
            <option value="2">Media</option>
            <option value="3">Difícil</option>
          </select>
        </label>
        <label className="text-xs text-[var(--color-text-muted)]">
          Estado
          <select
            className={`${select} mt-1 block`}
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <option value="all">Todos</option>
            <option value="pending">Pendientes</option>
            <option value="passed">Superados</option>
          </select>
        </label>
      </div>

      <ul className="mt-6 space-y-3">
        {shown.map((l) => {
          const st = progress.labs[l.id]?.status;
          return (
            <li key={l.id}>
              <a
                href={url(`/practica/labs/${l.id}/`)}
                className="block rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-raised)] p-4 hover:border-[var(--color-accent)]"
              >
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <span className="font-medium text-[var(--color-text)]">{l.title}</span>
                  <span className="text-xs text-[var(--color-text-muted)]">
                    {l.language === 'sql' ? 'SQL' : 'Python'} · {DIFFICULTY[l.difficulty]} ·{' '}
                    {l.estimatedMinutes} min ·{' '}
                    {st === 'passed' ? 'Superado ✔' : st === 'started' ? 'En curso' : 'Sin empezar'}
                  </span>
                </div>
                <p className="mt-1 text-sm text-[var(--color-text-muted)]">{l.description}</p>
                <p className="mt-1 text-xs text-[var(--color-text-muted)]">{l.moduleTitle}</p>
              </a>
            </li>
          );
        })}
        {shown.length === 0 && (
          <li className="text-sm text-[var(--color-text-muted)]">
            Ningún laboratorio coincide con los filtros.
          </li>
        )}
      </ul>
    </div>
  );
}
