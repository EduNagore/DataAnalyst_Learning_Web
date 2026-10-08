import { useId, useState } from 'react';
import { aggregateRate, isSimpson, winner } from '../../lib/simpson';

interface Props {
  /** Nombres de los dos grupos que se comparan (A, B). */
  groups: [string, string];
  /** Nombres de los dos estratos. */
  strata: [string, string];
  /** Tasa (%) de cada grupo en cada estrato: rates[grupo][estrato]. */
  rates: [[number, number], [number, number]];
  /** % de las observaciones de cada grupo que caen en el primer estrato. */
  initialShare: [number, number];
  metric: string;
}

const pct = (v: number) => `${v.toFixed(1).replace('.', ',')} %`;

/** Muestra cómo la mezcla de estratos invierte una comparación (paradoja de Simpson). */
export default function SimpsonExplorer({ groups, strata, rates, initialShare, metric }: Props) {
  const [shareA, setShareA] = useState(initialShare[0]);
  const [shareB, setShareB] = useState(initialShare[1]);
  const idA = useId();
  const idB = useId();

  const aggA = aggregateRate(rates[0], shareA / 100);
  const aggB = aggregateRate(rates[1], shareB / 100);
  const paradox = isSimpson(rates[0], rates[1], aggA, aggB);
  const maxRate = Math.max(...rates.flat(), aggA, aggB, 1);
  const wAgg = winner(aggA, aggB);
  const wins = (w: 'A' | 'B' | 'empate') =>
    w === 'empate' ? 'empate' : w === 'A' ? groups[0] : groups[1];

  const bar = (label: string, value: number, tone: 'a' | 'b') => (
    <div className="flex items-center gap-3 text-sm" key={label}>
      <span className="w-40 shrink-0 text-[var(--color-text-muted)]">{label}</span>
      <div className="h-4 flex-1 rounded bg-[var(--color-bg-subtle)]">
        <div
          className={`h-4 rounded ${tone === 'a' ? 'bg-[var(--color-accent)]' : 'bg-[var(--color-warning)]'}`}
          style={{ width: `${(value / maxRate) * 100}%` }}
        />
      </div>
      <span className="w-16 text-right font-mono">{pct(value)}</span>
    </div>
  );

  return (
    <figure className="not-prose my-6 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-raised)] p-4">
      <figcaption className="mb-3 text-sm font-semibold text-[var(--color-text)]">
        Explorador de la paradoja de Simpson · {metric}
      </figcaption>

      <div className="space-y-2">
        <p className="text-xs font-semibold tracking-wide text-[var(--color-text-muted)] uppercase">
          Dentro de cada estrato (la tasa no cambia)
        </p>
        {strata.map((s, i) => (
          <div key={s} className="space-y-1">
            {bar(`${groups[0]} · ${s}`, rates[0][i], 'a')}
            {bar(`${groups[1]} · ${s}`, rates[1][i], 'b')}
          </div>
        ))}
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <label htmlFor={idA} className="text-sm">
          <span className="block text-[var(--color-text-muted)]">
            % de {groups[0]} que viene de {strata[0]}:{' '}
            <strong className="text-[var(--color-text)]">{pct(shareA)}</strong>
          </span>
          <input
            id={idA}
            type="range"
            min={0}
            max={100}
            step={0.1}
            value={shareA}
            onChange={(e) => setShareA(Number(e.target.value))}
            className="w-full"
          />
        </label>
        <label htmlFor={idB} className="text-sm">
          <span className="block text-[var(--color-text-muted)]">
            % de {groups[1]} que viene de {strata[0]}:{' '}
            <strong className="text-[var(--color-text)]">{pct(shareB)}</strong>
          </span>
          <input
            id={idB}
            type="range"
            min={0}
            max={100}
            step={0.1}
            value={shareB}
            onChange={(e) => setShareB(Number(e.target.value))}
            className="w-full"
          />
        </label>
      </div>

      <div className="mt-4 space-y-2">
        <p className="text-xs font-semibold tracking-wide text-[var(--color-text-muted)] uppercase">
          Agregado (sin separar por {strata[0]} / {strata[1]})
        </p>
        {bar(groups[0], aggA, 'a')}
        {bar(groups[1], aggB, 'b')}
      </div>

      <p
        role="status"
        aria-live="polite"
        className={`mt-4 rounded-md border-l-4 p-3 text-sm ${
          paradox
            ? 'border-[var(--color-danger)] bg-[var(--color-danger)]/10'
            : 'border-[var(--color-accent)] bg-[var(--color-accent)]/10'
        }`}
      >
        {paradox ? (
          <>
            <strong>Paradoja de Simpson.</strong> {wins(winner(rates[0][0], rates[1][0]))} gana en{' '}
            {strata[0]} y en {strata[1]}, pero en el agregado gana <strong>{wins(wAgg)}</strong>. La
            causa es la mezcla: cada grupo reparte su tráfico de forma distinta entre los estratos.
          </>
        ) : (
          <>
            En el agregado {wAgg === 'empate' ? 'hay empate' : `gana ${wins(wAgg)}`}. Mueve los
            deslizadores para ver cómo la mezcla de estratos puede invertir la comparación aunque
            las tasas dentro de cada estrato no cambien.
          </>
        )}
      </p>
    </figure>
  );
}
