/** Funciones de distribución sin dependencias (para el widget DistributionExplorer). */

/** Función de error (Abramowitz-Stegun 7.1.26, error máximo ≈ 1,5e-7). */
export function erf(x: number): number {
  const sign = x < 0 ? -1 : 1;
  const ax = Math.abs(x);
  const t = 1 / (1 + 0.3275911 * ax);
  const y =
    1 -
    ((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t - 0.284496736) * t + 0.254829592) *
      t *
      Math.exp(-ax * ax);
  return sign * y;
}

export function normalPdf(x: number, mu: number, sigma: number): number {
  const z = (x - mu) / sigma;
  return Math.exp(-0.5 * z * z) / (sigma * Math.sqrt(2 * Math.PI));
}

export function normalCdf(x: number, mu: number, sigma: number): number {
  return 0.5 * (1 + erf((x - mu) / (sigma * Math.SQRT2)));
}

export function lognormalPdf(x: number, mu: number, sigma: number): number {
  if (x <= 0) return 0;
  return normalPdf(Math.log(x), mu, sigma) / x;
}

export function lognormalCdf(x: number, mu: number, sigma: number): number {
  if (x <= 0) return 0;
  return normalCdf(Math.log(x), mu, sigma);
}

/** log Γ(z) con la aproximación de Lanczos (g = 7). */
export function logGamma(z: number): number {
  const c = [
    0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313,
    -176.61502916214059, 12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6,
    1.5056327351493116e-7,
  ];
  if (z < 0.5) return Math.log(Math.PI / Math.sin(Math.PI * z)) - logGamma(1 - z);
  const zz = z - 1;
  let x = c[0];
  for (let i = 1; i < 9; i++) x += c[i] / (zz + i);
  const t = zz + 7.5;
  return 0.5 * Math.log(2 * Math.PI) + (zz + 0.5) * Math.log(t) - t + Math.log(x);
}

function logFactorial(n: number): number {
  return logGamma(n + 1);
}

export function poissonPmf(k: number, lambda: number): number {
  if (k < 0 || !Number.isInteger(k)) return 0;
  return Math.exp(k * Math.log(lambda) - lambda - logFactorial(k));
}

export function binomialPmf(k: number, n: number, p: number): number {
  if (k < 0 || k > n || !Number.isInteger(k)) return 0;
  if (p === 0) return k === 0 ? 1 : 0;
  if (p === 1) return k === n ? 1 : 0;
  const logC = logFactorial(n) - logFactorial(k) - logFactorial(n - k);
  return Math.exp(logC + k * Math.log(p) + (n - k) * Math.log(1 - p));
}

export interface Moments {
  mean: number;
  variance: number;
  median: number;
}

export function normalMoments(mu: number, sigma: number): Moments {
  return { mean: mu, variance: sigma * sigma, median: mu };
}

export function lognormalMoments(mu: number, sigma: number): Moments {
  const s2 = sigma * sigma;
  return {
    mean: Math.exp(mu + s2 / 2),
    variance: (Math.exp(s2) - 1) * Math.exp(2 * mu + s2),
    median: Math.exp(mu),
  };
}

export function poissonMoments(lambda: number): Moments {
  return { mean: lambda, variance: lambda, median: Math.floor(lambda + 1 / 3 - 0.02 / lambda) };
}

export function binomialMoments(n: number, p: number): Moments {
  return { mean: n * p, variance: n * p * (1 - p), median: Math.round(n * p) };
}
