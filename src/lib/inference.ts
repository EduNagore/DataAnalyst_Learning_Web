/** Utilidades de inferencia estadística para los widgets (intervalos, potencia, peeking). */
import { logGamma, normalCdf } from './distributions';

/** Generador pseudoaleatorio determinista (mulberry32). */
export function rng(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Normal estándar con Box-Muller a partir de un generador uniforme. */
export function randn(u: () => number): number {
  const a = Math.max(u(), 1e-12);
  return Math.sqrt(-2 * Math.log(a)) * Math.cos(2 * Math.PI * u());
}

/** Función beta incompleta regularizada I_x(a, b) (fracción continua de Lentz). */
export function regIncBeta(x: number, a: number, b: number): number {
  if (x <= 0) return 0;
  if (x >= 1) return 1;
  const lbeta = logGamma(a) + logGamma(b) - logGamma(a + b);
  const front = Math.exp(Math.log(x) * a + Math.log(1 - x) * b - lbeta);
  const cf = (xx: number, aa: number, bb: number): number => {
    const tiny = 1e-30;
    let c = 1;
    let d = 1 - ((aa + bb) * xx) / (aa + 1);
    if (Math.abs(d) < tiny) d = tiny;
    d = 1 / d;
    let h = d;
    for (let m = 1; m <= 300; m++) {
      const m2 = 2 * m;
      let num = (m * (bb - m) * xx) / ((aa + m2 - 1) * (aa + m2));
      d = 1 + num * d;
      if (Math.abs(d) < tiny) d = tiny;
      c = 1 + num / c;
      if (Math.abs(c) < tiny) c = tiny;
      d = 1 / d;
      h *= d * c;
      num = (-(aa + m) * (aa + bb + m) * xx) / ((aa + m2) * (aa + m2 + 1));
      d = 1 + num * d;
      if (Math.abs(d) < tiny) d = tiny;
      c = 1 + num / c;
      if (Math.abs(c) < tiny) c = tiny;
      d = 1 / d;
      const delta = d * c;
      h *= delta;
      if (Math.abs(delta - 1) < 1e-14) break;
    }
    return h;
  };
  return x < (a + 1) / (a + b + 2) ? (front * cf(x, a, b)) / a : 1 - (front * cf(1 - x, b, a)) / b;
}

/** Función de distribución de la t de Student. */
export function tCdf(t: number, df: number): number {
  const x = df / (df + t * t);
  const p = 0.5 * regIncBeta(x, df / 2, 0.5);
  return t > 0 ? 1 - p : p;
}

/** Cuantil de la t de Student (bisección sobre la CDF). */
export function tQuantile(p: number, df: number): number {
  let lo = -200;
  let hi = 200;
  for (let i = 0; i < 100; i++) {
    const mid = (lo + hi) / 2;
    if (tCdf(mid, df) < p) lo = mid;
    else hi = mid;
  }
  return (lo + hi) / 2;
}

/** Cuantil de la normal estándar (algoritmo de Acklam, error < 1,2e-9). */
export function normalQuantile(p: number): number {
  const a = [
    -39.69683028665376, 220.9460984245205, -275.9285104469687, 138.357751867269, -30.66479806614716,
    2.506628277459239,
  ];
  const b = [
    -54.47609879822406, 161.5858368580409, -155.6989798598866, 66.80131188771972,
    -13.28068155288572,
  ];
  const c = [
    -0.007784894002430293, -0.3223964580411365, -2.400758277161838, -2.549732539343734,
    4.374664141464968, 2.938163982698783,
  ];
  const d = [0.007784695709041462, 0.3224671290700398, 2.445134137142996, 3.754408661907416];
  const plow = 0.02425;
  if (p < plow) {
    const q = Math.sqrt(-2 * Math.log(p));
    return (
      (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) /
      ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    );
  }
  if (p > 1 - plow) return -normalQuantile(1 - p);
  const q = p - 0.5;
  const r = q * q;
  return (
    ((((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q) /
    (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
  );
}

export interface Interval {
  mean: number;
  lo: number;
  hi: number;
  hit: boolean;
}

/** Media de una muestra con su intervalo t y si contiene la media poblacional. */
export function meanInterval(sample: number[], level: number, mu: number): Interval {
  const n = sample.length;
  const mean = sample.reduce((s, v) => s + v, 0) / n;
  const variance = sample.reduce((s, v) => s + (v - mean) ** 2, 0) / (n - 1);
  const half = tQuantile(1 - (1 - level) / 2, n - 1) * Math.sqrt(variance / n);
  return { mean, lo: mean - half, hi: mean + half, hit: mean - half <= mu && mu <= mean + half };
}

/** Población lognormal(mu, sigma): asimétrica, como los importes de pedido. */
export function lognormalMean(mu: number, sigma: number): number {
  return Math.exp(mu + (sigma * sigma) / 2);
}

/** Simula `trials` intervalos de confianza de la media con muestras de tamaño `n`. */
export function simulateCoverage(
  n: number,
  level: number,
  trials: number,
  seed: number,
  mu = 5,
  sigma = 0.9,
): { intervals: Interval[]; coverage: number; trueMean: number } {
  const u = rng(seed);
  const trueMean = lognormalMean(mu, sigma);
  const intervals: Interval[] = [];
  for (let t = 0; t < trials; t++) {
    const sample = Array.from({ length: n }, () => Math.exp(mu + sigma * randn(u)));
    intervals.push(meanInterval(sample, level, trueMean));
  }
  return { intervals, coverage: intervals.filter((i) => i.hit).length / trials, trueMean };
}

/** Tamaño de muestra por grupo para comparar dos proporciones (bilateral, z no agrupado). */
export function sampleSizeProportions(
  p1: number,
  relMde: number,
  alpha = 0.05,
  power = 0.8,
): number {
  const p2 = p1 * (1 + relMde);
  const za = normalQuantile(1 - alpha / 2);
  const zb = normalQuantile(power);
  const variance = p1 * (1 - p1) + p2 * (1 - p2);
  return Math.ceil(((za + zb) ** 2 * variance) / (p2 - p1) ** 2);
}

/** Potencia aproximada de la comparación de dos proporciones con `n` por grupo. */
export function powerProportions(p1: number, relMde: number, n: number, alpha = 0.05): number {
  const p2 = p1 * (1 + relMde);
  const se = Math.sqrt((p1 * (1 - p1) + p2 * (1 - p2)) / n);
  const za = normalQuantile(1 - alpha / 2);
  const z = Math.abs(p2 - p1) / se;
  return normalCdf(z - za, 0, 1) + normalCdf(-z - za, 0, 1);
}

/** Estadístico χ² de bondad de ajuste y p-valor (1 grado de libertad) para un SRM 2 grupos. */
export function srmTest(control: number, treatment: number, expectedShare = 0.5) {
  const n = control + treatment;
  const e1 = n * expectedShare;
  const e2 = n * (1 - expectedShare);
  const chi2 = (control - e1) ** 2 / e1 + (treatment - e2) ** 2 / e2;
  const z = Math.sqrt(chi2);
  const p = 2 * (1 - normalCdf(z, 0, 1));
  return { chi2, p };
}

export interface CupedSample {
  x: number[];
  y: number[];
  treated: boolean[];
}

export interface CupedResult {
  rawEffect: number;
  rawSe: number;
  cupedEffect: number;
  cupedSe: number;
  theta: number;
  rho: number;
  varianceReduction: number;
}

/** Genera una muestra con covariable previa X, métrica Y correlacionada (ρ) y un efecto aditivo. */
export function simulateCupedSample(
  rho: number,
  effect: number,
  n: number,
  seed: number,
): CupedSample {
  const u = rng(seed);
  const x: number[] = [];
  const y: number[] = [];
  const treated: boolean[] = [];
  for (let i = 0; i < n; i++) {
    const xi = randn(u);
    const t = i % 2 === 1;
    const yi = rho * xi + Math.sqrt(Math.max(0, 1 - rho * rho)) * randn(u) + (t ? effect : 0);
    x.push(xi);
    y.push(yi);
    treated.push(t);
  }
  return { x, y, treated };
}

const mean = (a: number[]) => a.reduce((s, v) => s + v, 0) / a.length;
const variance = (a: number[]) => {
  const m = mean(a);
  return a.reduce((s, v) => s + (v - m) ** 2, 0) / (a.length - 1);
};

/** Efecto y error estándar (Welch) con y sin ajuste CUPED con la covariable previa. */
export function cupedAnalysis(sample: CupedSample): CupedResult {
  const { x, y, treated } = sample;
  const mx = mean(x);
  const my = mean(y);
  const cov = x.reduce((s, v, i) => s + (v - mx) * (y[i] - my), 0) / (x.length - 1);
  const theta = cov / variance(x);
  const adjusted = y.map((v, i) => v - theta * (x[i] - mx));
  const split = (a: number[]) => [a.filter((_, i) => treated[i]), a.filter((_, i) => !treated[i])];
  const effectSe = (a: number[]) => {
    const [t, c] = split(a);
    return {
      effect: mean(t) - mean(c),
      se: Math.sqrt(variance(t) / t.length + variance(c) / c.length),
    };
  };
  const raw = effectSe(y);
  const cuped = effectSe(adjusted);
  const rho = cov / Math.sqrt(variance(x) * variance(y));
  return {
    rawEffect: raw.effect,
    rawSe: raw.se,
    cupedEffect: cuped.effect,
    cupedSe: cuped.se,
    theta,
    rho,
    varianceReduction: 1 - variance(adjusted) / variance(y),
  };
}

/** Límites constantes (Pocock) y escalados (tipo O'Brien-Fleming, z_k = c·√(K/k)) para α = 0,05 bilateral. */
export const POCOCK_BOUNDARY: Record<number, number> = {
  1: 1.96,
  2: 2.178,
  3: 2.289,
  5: 2.413,
  10: 2.555,
  20: 2.672,
};
export const OBF_CONSTANT: Record<number, number> = {
  1: 1.96,
  2: 1.978,
  3: 2.012,
  5: 2.041,
  10: 2.087,
  20: 2.125,
};

/** Estadísticos z acumulados de un experimento A/A con `looks` revisiones igualmente espaciadas. */
export function zPath(looks: number, u: () => number): number[] {
  const z: number[] = [];
  let s = 0;
  for (let k = 1; k <= looks; k++) {
    s += randn(u);
    z.push(s / Math.sqrt(k));
  }
  return z;
}

export interface PeekingRates {
  finalOnly: number;
  peeking: number;
  pocock: number;
  obf: number;
}

/** Tasa de falsos positivos de A/A según la regla de parada (todas con α = 0,05 nominal). */
export function peekingRates(looks: number, trials: number, seed: number): PeekingRates {
  const u = rng(seed);
  const pocock = POCOCK_BOUNDARY[looks] ?? 1.96;
  const c = OBF_CONSTANT[looks] ?? 1.96;
  let finalOnly = 0;
  let peeking = 0;
  let pocockHits = 0;
  let obfHits = 0;
  for (let t = 0; t < trials; t++) {
    const z = zPath(looks, u);
    if (Math.abs(z[looks - 1]) > 1.96) finalOnly++;
    if (z.some((v) => Math.abs(v) > 1.96)) peeking++;
    if (z.some((v) => Math.abs(v) > pocock)) pocockHits++;
    if (z.some((v, i) => Math.abs(v) > c * Math.sqrt(looks / (i + 1)))) obfHits++;
  }
  return {
    finalOnly: finalOnly / trials,
    peeking: peeking / trials,
    pocock: pocockHits / trials,
    obf: obfHits / trials,
  };
}

/** Razón de verosimilitud de la prueba secuencial de mezcla (mSPRT) para la media de datos normales. */
export function msprtLambda(n: number, xbar: number, sigma2: number, tau2: number): number {
  return (
    Math.sqrt(sigma2 / (sigma2 + n * tau2)) *
    Math.exp((n * n * tau2 * xbar * xbar) / (2 * sigma2 * (sigma2 + n * tau2)))
  );
}
