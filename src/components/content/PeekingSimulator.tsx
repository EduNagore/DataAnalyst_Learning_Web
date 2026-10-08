import { useId, useMemo, useState } from 'react';
import { OBF_CONSTANT, peekingRates, POCOCK_BOUNDARY, rng, zPath } from '../../lib/inference';

const LOOKS = [1, 2, 5, 10, 20];
const TRIALS = 2000;
const pct = (v: number) => `${(v * 100).toFixed(1).replace('.', ',')} %`;

/**
 * Simula experimentos A/A (sin efecto) revisados varias veces: mirar y parar en el primer
 * p < 0,05 infla los falsos positivos; los límites de grupo secuencial recuperan el 5 %.
 */
export default function PeekingSimulator() {
  const [looks, setLooks] = useState(10);
  const [seed, setSeed] = useState(1);
  const looksId = useId();

  const rates = useMemo(() => peekingRates(looks, TRIALS, seed * 1009), [looks, seed]);
  const path = useMemo(() => zPath(looks, rng(seed * 7 + 3)), [looks, seed]);

  const pocock = POCOCK_BOUNDARY[looks];
  const obfC = OBF_CONSTANT[looks];
  const zMax = 4.2;
  const x = (k: number) => 8 + (looks === 1 ? 0.5 : (k - 1) / (looks - 1)) * 84;
  const y = (z: number) => 50 - (Math.max(-zMax, Math.min(zMax, z)) / zMax) * 44;
  const crossed = path.findIndex((z) => Math.abs(z) > 1.96);

  const rule = (label: string, value: number, tone: string) => (
    <div className="flex items-center gap-3 text-sm" key={label}>
      <span className="w-48 shrink-0 text-[var(--color-text-muted)]">{label}</span>
      <div className="h-4 flex-1 rounded bg-[var(--color-bg-subtle)]">
        <div
          className="h-4 rounded"
          style={{ width: `${Math.min(100, value * 250)}%`, background: tone }}
        />
      </div>
      <span className="w-16 text-right font-mono">{pct(value)}</span>
    </div>
  );

  const obfPoints = path
    .map((_, i) => `${x(i + 1)},${y(obfC * Math.sqrt(looks / (i + 1)))}`)
    .join(' ');
  const obfNeg = path
    .map((_, i) => `${x(i + 1)},${y(-obfC * Math.sqrt(looks / (i + 1)))}`)
    .join(' ');

  return (
    <figure className="not-prose my-6 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-raised)] p-4">
      <figcaption className="mb-3 text-sm font-semibold text-[var(--color-text)]">
        Simulador de «mirar antes de tiempo» · {TRIALS} experimentos A/A (sin efecto real)
      </figcaption>

      <div className="flex flex-wrap items-end gap-x-6 gap-y-3 text-sm">
        <label htmlFor={looksId} className="flex flex-col gap-1 text-[var(--color-text-muted)]">
          Número de revisiones
          <select
            id={looksId}
            value={looks}
            onChange={(e) => setLooks(Number(e.target.value))}
            className="rounded border border-[var(--color-border)] bg-[var(--color-bg)] px-2 py-1 text-[var(--color-text)]"
          >
            {LOOKS.map((k) => (
              <option key={k} value={k}>
                {k}
              </option>
            ))}
          </select>
        </label>
        <button
          type="button"
          onClick={() => setSeed((s) => s + 1)}
          className="rounded-md border border-[var(--color-border)] px-3 py-1.5 font-semibold text-[var(--color-text)] hover:border-[var(--color-accent)]"
        >
          Repetir simulación
        </button>
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <div>
          <svg
            viewBox="0 0 100 100"
            className="w-full rounded border border-[var(--color-border)] bg-[var(--color-bg)]"
            role="img"
            aria-label={`Trayectoria del estadístico z de un experimento A/A con ${looks} revisiones, con los límites de ±1,96 y los de O’Brien-Fleming. ${
              crossed >= 0
                ? `Cruza ±1,96 en la revisión ${crossed + 1} aunque no hay efecto.`
                : 'No cruza ±1,96 en ninguna revisión.'
            }`}
          >
            {[1.96, -1.96].map((b) => (
              <line
                key={b}
                x1={4}
                x2={96}
                y1={y(b)}
                y2={y(b)}
                stroke="var(--color-danger)"
                strokeWidth={0.5}
                strokeDasharray="2 1.5"
              />
            ))}
            <line
              x1={4}
              x2={96}
              y1={y(0)}
              y2={y(0)}
              stroke="var(--color-border)"
              strokeWidth={0.5}
            />
            {looks > 1 && (
              <>
                <polyline
                  points={obfPoints}
                  fill="none"
                  stroke="var(--color-success)"
                  strokeWidth={0.7}
                />
                <polyline
                  points={obfNeg}
                  fill="none"
                  stroke="var(--color-success)"
                  strokeWidth={0.7}
                />
              </>
            )}
            <polyline
              points={path.map((z, i) => `${x(i + 1)},${y(z)}`).join(' ')}
              fill="none"
              stroke="var(--color-accent)"
              strokeWidth={1}
            />
            {path.map((z, i) => (
              <circle
                key={i}
                cx={x(i + 1)}
                cy={y(z)}
                r={1.2}
                fill={Math.abs(z) > 1.96 ? 'var(--color-danger)' : 'var(--color-accent)'}
              />
            ))}
          </svg>
          <p className="mt-1 text-xs text-[var(--color-text-muted)]">
            Línea azul: z acumulado de un A/A. Rojo discontinuo: ±1,96. Verde: límite de
            O’Brien-Fleming. Un punto rojo es un «ganador» falso si se parara ahí.
          </p>
        </div>
        <div className="space-y-2" aria-live="polite">
          {rule('Mirar solo al final', rates.finalOnly, 'var(--color-success)')}
          {rule('Parar al primer p < 0,05', rates.peeking, 'var(--color-danger)')}
          {pocock &&
            rule(
              `Pocock (z = ${pocock.toFixed(2).replace('.', ',')})`,
              rates.pocock,
              'var(--color-accent)',
            )}
          {obfC && rule('O’Brien-Fleming', rates.obf, 'var(--color-accent)')}
          <p className="pt-1 text-sm text-[var(--color-text)]">
            Con {looks} {looks === 1 ? 'revisión' : 'revisiones'}, parar en el primer p &lt; 0,05
            produce un <strong>{pct(rates.peeking)}</strong> de falsos positivos en lugar del 5 %
            nominal.
          </p>
        </div>
      </div>
    </figure>
  );
}
