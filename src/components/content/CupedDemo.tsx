import { useId, useMemo, useState } from 'react';
import { cupedAnalysis, simulateCupedSample } from '../../lib/inference';

const N = 400;
const EFFECT = 0.3;
const fmt = (v: number, d = 2) => v.toFixed(d).replace('.', ',');

/** Muestra cómo una covariable previa correlacionada con la métrica reduce el error estándar (CUPED). */
export default function CupedDemo() {
  const [rho, setRho] = useState(0.75);
  const [seed, setSeed] = useState(1);
  const rhoId = useId();

  const sample = useMemo(() => simulateCupedSample(rho, EFFECT, N, seed), [rho, seed]);
  const r = useMemo(() => cupedAnalysis(sample), [sample]);

  const xs = sample.x;
  const ys = sample.y;
  const lim = 3.2;
  const px = (v: number) => 50 + (Math.max(-lim, Math.min(lim, v)) / lim) * 46;
  const py = (v: number) => 50 - (Math.max(-lim, Math.min(lim, v)) / lim) * 46;

  const rangeMax = Math.max(Math.abs(r.rawEffect) + 2 * r.rawSe, EFFECT + 2.2 * r.rawSe, 0.2);
  const bx = (v: number) => 4 + ((v + rangeMax) / (2 * rangeMax)) * 92;
  const bar = (label: string, effect: number, se: number, color: string) => {
    const lo = effect - 1.96 * se;
    const hi = effect + 1.96 * se;
    return (
      <div className="flex items-center gap-3 text-sm" key={label}>
        <span className="w-24 shrink-0 text-[var(--color-text-muted)]">{label}</span>
        <svg viewBox="0 0 100 10" className="h-5 flex-1" aria-hidden="true">
          <line
            x1={bx(0)}
            x2={bx(0)}
            y1={0}
            y2={10}
            stroke="var(--color-border)"
            strokeWidth={0.6}
          />
          <line
            x1={bx(lo)}
            x2={bx(hi)}
            y1={5}
            y2={5}
            stroke={color}
            strokeWidth={2}
            strokeLinecap="round"
          />
          <circle cx={bx(effect)} cy={5} r={1.6} fill={color} />
        </svg>
        <span className="w-44 shrink-0 text-right font-mono text-xs">
          {fmt(effect)} ± {fmt(1.96 * se)}
        </span>
      </div>
    );
  };

  return (
    <figure className="not-prose my-6 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-raised)] p-4">
      <figcaption className="mb-3 text-sm font-semibold text-[var(--color-text)]">
        Demostración de CUPED · {N} usuarios, efecto verdadero {fmt(EFFECT)}
      </figcaption>

      <div className="flex flex-wrap items-end gap-x-6 gap-y-3 text-sm">
        <label htmlFor={rhoId} className="flex flex-col gap-1 text-[var(--color-text-muted)]">
          Correlación ρ entre la métrica previa y la actual: <strong>{fmt(rho)}</strong>
          <input
            id={rhoId}
            type="range"
            min={0}
            max={0.95}
            step={0.05}
            value={rho}
            onChange={(e) => setRho(Number(e.target.value))}
            className="w-64 accent-[var(--color-accent)]"
          />
        </label>
        <button
          type="button"
          onClick={() => setSeed((s) => s + 1)}
          className="rounded-md border border-[var(--color-border)] px-3 py-1.5 font-semibold text-[var(--color-text)] hover:border-[var(--color-accent)]"
        >
          Nueva muestra
        </button>
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]">
        <svg
          viewBox="0 0 100 100"
          className="w-full rounded border border-[var(--color-border)] bg-[var(--color-bg)]"
          role="img"
          aria-label={`Diagrama de dispersión de la métrica previa (horizontal) y la actual (vertical) de ${N} usuarios con correlación ${fmt(rho)}.`}
        >
          {xs.map((x, i) => (
            <circle
              key={i}
              cx={px(x)}
              cy={py(ys[i])}
              r={1.1}
              fill={sample.treated[i] ? 'var(--color-warning)' : 'var(--color-accent)'}
              fillOpacity={0.55}
            />
          ))}
        </svg>
        <div className="space-y-2">
          {bar('Sin ajustar', r.rawEffect, r.rawSe, 'var(--color-text-muted)')}
          {bar('Con CUPED', r.cupedEffect, r.cupedSe, 'var(--color-accent)')}
          <p className="pt-1 text-sm text-[var(--color-text)]" aria-live="polite">
            Varianza reducida: <strong>{fmt(r.varianceReduction * 100, 0)} %</strong> (teoría: 1 −
            ρ² → {fmt(rho * rho * 100, 0)} %). Error estándar:{' '}
            <strong>
              {fmt(r.rawSe, 3)} → {fmt(r.cupedSe, 3)}
            </strong>
            . Equivale a tener {fmt(1 / Math.max(0.05, 1 - rho * rho), 1)}× más usuarios.
          </p>
          <p className="text-xs text-[var(--color-text-muted)]">
            Azul: control · naranja: tratamiento. Las barras son intervalos del 95 % para el efecto.
          </p>
        </div>
      </div>
    </figure>
  );
}
