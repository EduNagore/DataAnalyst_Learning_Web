import { useId, useMemo, useState } from 'react';
import { simulateCoverage } from '../../lib/inference';

const TRIALS = 100;
const SIZES = [10, 30, 100, 400];
const LEVELS = [0.8, 0.9, 0.95, 0.99];
const pct = (v: number) => `${(v * 100).toFixed(0)} %`;
const eur = (v: number) => `${Math.round(v).toLocaleString('es-ES')} €`;

/**
 * Simula 100 muestras de una población asimétrica (importes de pedido) y dibuja el
 * intervalo de confianza de la media de cada una, para ver qué significa «95 % de confianza».
 */
export default function CoverageExplorer() {
  const [n, setN] = useState(30);
  const [level, setLevel] = useState(0.95);
  const [seed, setSeed] = useState(1);
  const nId = useId();
  const levelId = useId();

  const sim = useMemo(() => simulateCoverage(n, level, TRIALS, seed), [n, level, seed]);
  const hits = sim.intervals.filter((i) => i.hit).length;
  const min = Math.min(...sim.intervals.map((i) => i.lo), sim.trueMean);
  const max = Math.max(...sim.intervals.map((i) => i.hi), sim.trueMean);
  const span = max - min || 1;
  const x = (v: number) => 4 + ((v - min) / span) * 92;
  const rowH = 4;

  return (
    <figure className="not-prose my-6 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-raised)] p-4">
      <figcaption className="mb-3 text-sm font-semibold text-[var(--color-text)]">
        Explorador de intervalos de confianza · {TRIALS} muestras de una población asimétrica
      </figcaption>

      <div className="flex flex-wrap items-end gap-x-6 gap-y-3 text-sm">
        <label htmlFor={nId} className="flex flex-col gap-1 text-[var(--color-text-muted)]">
          Tamaño de cada muestra
          <select
            id={nId}
            value={n}
            onChange={(e) => setN(Number(e.target.value))}
            className="rounded border border-[var(--color-border)] bg-[var(--color-bg)] px-2 py-1 text-[var(--color-text)]"
          >
            {SIZES.map((s) => (
              <option key={s} value={s}>
                n = {s}
              </option>
            ))}
          </select>
        </label>
        <label htmlFor={levelId} className="flex flex-col gap-1 text-[var(--color-text-muted)]">
          Nivel de confianza
          <select
            id={levelId}
            value={level}
            onChange={(e) => setLevel(Number(e.target.value))}
            className="rounded border border-[var(--color-border)] bg-[var(--color-bg)] px-2 py-1 text-[var(--color-text)]"
          >
            {LEVELS.map((l) => (
              <option key={l} value={l}>
                {pct(l)}
              </option>
            ))}
          </select>
        </label>
        <button
          type="button"
          onClick={() => setSeed((s) => s + 1)}
          className="rounded-md border border-[var(--color-border)] px-3 py-1.5 font-semibold text-[var(--color-text)] hover:border-[var(--color-accent)]"
        >
          Nuevas muestras
        </button>
      </div>

      <svg
        viewBox={`0 0 100 ${TRIALS * rowH + 4}`}
        className="mt-4 w-full"
        role="img"
        aria-label={`${hits} de ${TRIALS} intervalos de confianza del ${pct(level)} contienen la media verdadera de ${eur(sim.trueMean)}; los que fallan se muestran en rojo.`}
        preserveAspectRatio="none"
        style={{ height: 260 }}
      >
        <line
          x1={x(sim.trueMean)}
          x2={x(sim.trueMean)}
          y1={0}
          y2={TRIALS * rowH + 4}
          stroke="var(--color-text)"
          strokeWidth={0.4}
          strokeDasharray="1.5 1"
        />
        {sim.intervals.map((iv, i) => (
          <line
            key={i}
            x1={x(iv.lo)}
            x2={x(iv.hi)}
            y1={i * rowH + 3}
            y2={i * rowH + 3}
            stroke={iv.hit ? 'var(--color-accent)' : 'var(--color-danger)'}
            strokeWidth={iv.hit ? 0.9 : 1.4}
            strokeLinecap="round"
          />
        ))}
      </svg>

      <p className="mt-2 text-sm text-[var(--color-text)]" aria-live="polite">
        <strong>
          {hits} de {TRIALS}
        </strong>{' '}
        intervalos contienen la media verdadera ({eur(sim.trueMean)}, línea discontinua).{' '}
        <span className="text-[var(--color-text-muted)]">
          Cobertura teórica: {pct(level)}. Con muestras pequeñas y datos muy asimétricos, la
          cobertura real suele quedarse por debajo.
        </span>
      </p>
    </figure>
  );
}
