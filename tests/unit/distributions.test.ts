import { describe, expect, it } from 'vitest';
import {
  binomialMoments,
  binomialPmf,
  erf,
  logGamma,
  lognormalCdf,
  lognormalMoments,
  normalCdf,
  normalPdf,
  poissonMoments,
  poissonPmf,
} from '../../src/lib/distributions';

describe('normal', () => {
  it('erf y la cdf coinciden con valores conocidos', () => {
    expect(erf(0)).toBeCloseTo(0, 6);
    expect(erf(1)).toBeCloseTo(0.8427008, 5);
    expect(normalCdf(0, 0, 1)).toBeCloseTo(0.5, 6);
    expect(normalCdf(1.96, 0, 1)).toBeCloseTo(0.975, 3);
  });

  it('la pdf en la media vale 1/(σ√2π)', () => {
    expect(normalPdf(0, 0, 1)).toBeCloseTo(0.3989423, 6);
    expect(normalPdf(5, 5, 2)).toBeCloseTo(0.1994711, 6);
  });
});

describe('log-normal', () => {
  it('con los parámetros de los importes de Lumen: mediana 156,8 y P(x > 500) ≈ 18,2 %', () => {
    const mu = 5.055;
    const sigma = 1.277;
    expect(lognormalMoments(mu, sigma).median).toBeCloseTo(156.8, 0);
    expect(1 - lognormalCdf(500, mu, sigma)).toBeCloseTo(0.182, 2);
  });
});

describe('discretas', () => {
  it('logGamma reproduce factoriales', () => {
    expect(Math.exp(logGamma(5))).toBeCloseTo(24, 6);
    expect(Math.exp(logGamma(11))).toBeCloseTo(3628800, 0);
  });

  it('la pmf de Poisson suma 1 y su media es λ', () => {
    const lambda = 7.5;
    let total = 0;
    let mean = 0;
    for (let k = 0; k < 80; k++) {
      const p = poissonPmf(k, lambda);
      total += p;
      mean += k * p;
    }
    expect(total).toBeCloseTo(1, 8);
    expect(mean).toBeCloseTo(lambda, 6);
    expect(poissonMoments(lambda).variance).toBe(lambda);
  });

  it('la pmf binomial suma 1 y coincide con un caso conocido', () => {
    expect(binomialPmf(2, 5, 0.5)).toBeCloseTo(0.3125, 8);
    let total = 0;
    for (let k = 0; k <= 40; k++) total += binomialPmf(k, 40, 0.3);
    expect(total).toBeCloseTo(1, 8);
    expect(binomialMoments(707, 0.0424).mean).toBeCloseTo(29.98, 1);
  });
});
