import { useId, useMemo, useState } from 'react';
import {
  binomialMoments,
  binomialPmf,
  lognormalCdf,
  lognormalMoments,
  lognormalPdf,
  normalCdf,
  normalMoments,
  normalPdf,
  poissonMoments,
  poissonPmf,
  type Moments,
} from '../../lib/distributions';

type Kind = 'normal' | 'lognormal' | 'poisson' | 'binomial';

interface Props {
  /** Distribución con la que arranca el explorador. */
  initial?: Kind;
}

const W = 560;
const H = 230;
const PAD = { l: 44, r: 12, t: 12, b: 30 };

const fmt = (v: number, d = 2) => v.toFixed(d).replace('.', ',');
const decimals = (step: number) => (String(step).split('.')[1] ?? '').length;

interface Curve {
  xs: number[];
  ys: number[];
  discrete: boolean;
  moments: Moments;
  tail: { label: string; value: number };
  xLabel: string;
}

function buildCurve(kind: Kind, a: number, b: number, threshold: number): Curve {
  const N = 160;
  if (kind === 'normal') {
    const lo = a - 4 * b;
    const hi = a + 4 * b;
    const xs = Array.from({ length: N }, (_, i) => lo + ((hi - lo) * i) / (N - 1));
    return {
      xs,
      ys: xs.map((x) => normalPdf(x, a, b)),
      discrete: false,
      moments: normalMoments(a, b),
      tail: { label: `P(X > ${fmt(threshold, 1)})`, value: 1 - normalCdf(threshold, a, b) },
      xLabel: 'x',
    };
  }
  if (kind === 'lognormal') {
    const hi = Math.exp(a + 2.2 * b);
    const xs = Array.from({ length: N }, (_, i) => (hi * i) / (N - 1));
    return {
      xs,
      ys: xs.map((x) => lognormalPdf(x, a, b)),
      discrete: false,
      moments: lognormalMoments(a, b),
      tail: { label: `P(X > ${fmt(threshold, 0)})`, value: 1 - lognormalCdf(threshold, a, b) },
      xLabel: 'importe (€)',
    };
  }
  if (kind === 'poisson') {
    const sd = Math.sqrt(a);
    const lo = Math.max(0, Math.floor(a - 4 * sd));
    const hi = Math.ceil(a + 4 * sd) + 1;
    const xs = Array.from({ length: hi - lo + 1 }, (_, i) => lo + i);
    let tail = 0;
    for (let k = Math.floor(threshold) + 1; k < hi + 200; k++) tail += poissonPmf(k, a);
    return {
      xs,
      ys: xs.map((k) => poissonPmf(k, a)),
      discrete: true,
      moments: poissonMoments(a),
      tail: { label: `P(X > ${fmt(threshold, 0)})`, value: tail },
      xLabel: 'nº de sucesos',
    };
  }
  const n = Math.round(a);
  const sd = Math.sqrt(n * b * (1 - b));
  const mean = n * b;
  const lo = Math.max(0, Math.floor(mean - 4 * sd));
  const hi = Math.min(n, Math.ceil(mean + 4 * sd) + 1);
  const xs = Array.from({ length: hi - lo + 1 }, (_, i) => lo + i);
  let tail = 0;
  for (let k = Math.floor(threshold) + 1; k <= n; k++) tail += binomialPmf(k, n, b);
  return {
    xs,
    ys: xs.map((k) => binomialPmf(k, n, b)),
    discrete: true,
    moments: binomialMoments(n, b),
    tail: { label: `P(X > ${fmt(threshold, 0)})`, value: tail },
    xLabel: 'nº de éxitos',
  };
}

const PRESETS: Record<
  Kind,
  {
    name: string;
    a: number;
    b: number;
    t: number;
    labels: [string, string];
    ranges: [number, number, number][];
  }
> = {
  normal: {
    name: 'Normal',
    a: 0,
    b: 1,
    t: 1.96,
    labels: ['media μ', 'desviación σ'],
    ranges: [
      [-10, 10, 0.1],
      [0.2, 5, 0.1],
      [-6, 6, 0.1],
    ],
  },
  lognormal: {
    name: 'Log-normal',
    a: 5.055,
    b: 1.277,
    t: 1000,
    labels: ['μ de ln(x)', 'σ de ln(x)'],
    ranges: [
      [3, 7, 0.01],
      [0.2, 2, 0.01],
      [10, 5000, 10],
    ],
  },
  poisson: {
    name: 'Poisson',
    a: 12,
    b: 0,
    t: 15,
    labels: ['tasa λ', ''],
    ranges: [
      [1, 80, 1],
      [0, 0, 1],
      [0, 120, 1],
    ],
  },
  binomial: {
    name: 'Binomial',
    a: 100,
    b: 0.0424,
    t: 6,
    labels: ['ensayos n', 'probabilidad p'],
    ranges: [
      [10, 1000, 1],
      [0.005, 0.9, 0.0005],
      [0, 300, 1],
    ],
  },
};

/** Explorador interactivo de distribuciones comunes en análisis de negocio. */
export default function DistributionExplorer({ initial = 'lognormal' }: Props) {
  const [kind, setKind] = useState<Kind>(initial);
  const [a, setA] = useState(PRESETS[initial].a);
  const [b, setB] = useState(PRESETS[initial].b);
  const [t, setT] = useState(PRESETS[initial].t);
  const idA = useId();
  const idB = useId();
  const idT = useId();

  const change = (k: Kind) => {
    setKind(k);
    setA(PRESETS[k].a);
    setB(PRESETS[k].b);
    setT(PRESETS[k].t);
  };

  const curve = useMemo(() => buildCurve(kind, a, b, t), [kind, a, b, t]);
  const preset = PRESETS[kind];

  const xMin = Math.min(...curve.xs);
  const xMax = Math.max(...curve.xs);
  const yMax = Math.max(...curve.ys, 1e-9) * 1.1;
  const sx = (x: number) => PAD.l + ((x - xMin) / (xMax - xMin || 1)) * (W - PAD.l - PAD.r);
  const sy = (y: number) => H - PAD.b - (y / yMax) * (H - PAD.t - PAD.b);
  const barW = curve.discrete ? Math.max(1, ((W - PAD.l - PAD.r) / curve.xs.length) * 0.8) : 0;

  const ticks = Array.from({ length: 5 }, (_, i) => xMin + ((xMax - xMin) * i) / 4);
  const path = !curve.discrete
    ? curve.xs
        .map((x, i) => `${i === 0 ? 'M' : 'L'}${sx(x).toFixed(1)},${sy(curve.ys[i]).toFixed(1)}`)
        .join(' ')
    : '';
  const sd = Math.sqrt(curve.moments.variance);

  const slider = (
    id: string,
    label: string,
    value: number,
    set: (v: number) => void,
    range: [number, number, number],
  ) => (
    <label htmlFor={id} className="text-sm">
      <span className="block text-[var(--color-text-muted)]">
        {label}:{' '}
        <strong className="text-[var(--color-text)]">{fmt(value, decimals(range[2]))}</strong>
      </span>
      <input
        id={id}
        type="range"
        min={range[0]}
        max={range[1]}
        step={range[2]}
        value={value}
        onChange={(e) => set(Number(e.target.value))}
        className="w-full"
      />
    </label>
  );

  return (
    <figure className="not-prose my-6 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-raised)] p-4">
      <figcaption className="mb-3 flex flex-wrap items-center gap-2 text-sm font-semibold text-[var(--color-text)]">
        Explorador de distribuciones
        <span className="flex flex-wrap gap-1" role="group" aria-label="Distribución">
          {(Object.keys(PRESETS) as Kind[]).map((k) => (
            <button
              key={k}
              type="button"
              onClick={() => change(k)}
              aria-pressed={kind === k}
              className={`rounded-md border px-2 py-0.5 text-xs font-medium ${
                kind === k
                  ? 'border-[var(--color-accent)] bg-[var(--color-accent)] text-[var(--color-accent-contrast)]'
                  : 'border-[var(--color-border)] text-[var(--color-text-muted)] hover:bg-[var(--color-bg-subtle)]'
              }`}
            >
              {PRESETS[k].name}
            </button>
          ))}
        </span>
      </figcaption>

      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="h-auto w-full"
        role="img"
        aria-label={`Gráfico de la distribución ${preset.name} con media ${fmt(curve.moments.mean)} y desviación ${fmt(sd)}`}
      >
        <line
          x1={PAD.l}
          y1={H - PAD.b}
          x2={W - PAD.r}
          y2={H - PAD.b}
          stroke="var(--color-border)"
        />
        <line x1={PAD.l} y1={PAD.t} x2={PAD.l} y2={H - PAD.b} stroke="var(--color-border)" />
        {ticks.map((x) => (
          <text
            key={x}
            x={sx(x)}
            y={H - PAD.b + 16}
            fontSize="11"
            textAnchor="middle"
            fill="var(--color-text-muted)"
          >
            {fmt(x, Math.abs(xMax - xMin) < 20 ? 1 : 0)}
          </text>
        ))}
        <text x={W / 2} y={H - 2} fontSize="11" textAnchor="middle" fill="var(--color-text-muted)">
          {curve.xLabel}
        </text>
        {curve.discrete ? (
          curve.xs.map((x, i) => (
            <rect
              key={x}
              x={sx(x) - barW / 2}
              y={sy(curve.ys[i])}
              width={barW}
              height={Math.max(0, H - PAD.b - sy(curve.ys[i]))}
              fill={x > t ? 'var(--color-warning)' : 'var(--color-accent)'}
              opacity={0.85}
            />
          ))
        ) : (
          <>
            <path d={path} fill="none" stroke="var(--color-accent)" strokeWidth="2" />
            <line
              x1={sx(Math.min(Math.max(t, xMin), xMax))}
              y1={PAD.t}
              x2={sx(Math.min(Math.max(t, xMin), xMax))}
              y2={H - PAD.b}
              stroke="var(--color-warning)"
              strokeDasharray="4 3"
            />
            <line
              x1={sx(curve.moments.mean)}
              y1={PAD.t}
              x2={sx(curve.moments.mean)}
              y2={H - PAD.b}
              stroke="var(--color-success)"
              strokeDasharray="2 3"
            />
          </>
        )}
      </svg>

      <div className="mt-2 grid gap-3 sm:grid-cols-3">
        {slider(idA, preset.labels[0], a, setA, preset.ranges[0])}
        {preset.labels[1] ? slider(idB, preset.labels[1], b, setB, preset.ranges[1]) : <span />}
        {slider(idT, 'umbral (cola)', t, setT, preset.ranges[2])}
      </div>

      <dl
        role="status"
        aria-live="polite"
        className="mt-3 grid grid-cols-2 gap-x-4 gap-y-1 text-sm sm:grid-cols-4"
      >
        <div>
          <dt className="text-xs text-[var(--color-text-muted)]">Media</dt>
          <dd className="font-mono">{fmt(curve.moments.mean)}</dd>
        </div>
        <div>
          <dt className="text-xs text-[var(--color-text-muted)]">Mediana</dt>
          <dd className="font-mono">{fmt(curve.moments.median)}</dd>
        </div>
        <div>
          <dt className="text-xs text-[var(--color-text-muted)]">Desviación típica</dt>
          <dd className="font-mono">{fmt(sd)}</dd>
        </div>
        <div>
          <dt className="text-xs text-[var(--color-text-muted)]">{curve.tail.label}</dt>
          <dd className="font-mono">{fmt(curve.tail.value * 100, 2)} %</dd>
        </div>
      </dl>
      <p className="mt-2 text-xs text-[var(--color-text-muted)]">
        {kind === 'lognormal'
          ? 'Valores iniciales: ajuste a los importes de pedido de Lumen (μ = 5,055; σ = 1,277). Observa cómo la media queda muy por encima de la mediana.'
          : kind === 'poisson'
            ? 'En una Poisson la media y la varianza son iguales (λ): comprueba si tus recuentos cumplen eso.'
            : kind === 'binomial'
              ? 'Valores iniciales: sesiones con compra de un día pequeño (p = 4,24 %, la conversión de Lumen).'
              : 'La regla 68-95-99,7: el 95 % queda a ±1,96 desviaciones de la media.'}
      </p>
    </figure>
  );
}
