import { describe, expect, it } from 'vitest';
import {
  meanInterval,
  normalQuantile,
  powerProportions,
  rng,
  sampleSizeProportions,
  simulateCoverage,
  srmTest,
  tCdf,
  tQuantile,
} from '../../src/lib/inference';

describe('distribución t de Student', () => {
  it('coincide con los cuantiles de scipy', () => {
    expect(tQuantile(0.975, 9)).toBeCloseTo(2.26216, 4);
    expect(tQuantile(0.975, 29)).toBeCloseTo(2.04523, 4);
    expect(tQuantile(0.975, 199)).toBeCloseTo(1.97196, 4);
  });
  it('su CDF coincide con scipy.stats.t.cdf', () => {
    expect(tCdf(1.5, 12)).toBeCloseTo(0.92027, 4);
    expect(tCdf(0, 5)).toBeCloseTo(0.5, 10);
  });
});

describe('normalQuantile', () => {
  it('invierte la normal estándar', () => {
    expect(normalQuantile(0.975)).toBeCloseTo(1.959964, 5);
    expect(normalQuantile(0.8)).toBeCloseTo(0.841621, 5);
    expect(normalQuantile(0.5)).toBeCloseTo(0, 8);
  });
});

describe('intervalos de confianza', () => {
  it('calcula media y extremos de una muestra pequeña', () => {
    const r = meanInterval([2, 4, 6, 8, 10], 0.95, 6);
    expect(r.mean).toBe(6);
    // sd = 3,1623; se = 1,4142; t(0,975; 4) = 2,7764
    expect(r.hi - r.mean).toBeCloseTo(3.9265, 3);
    expect(r.hit).toBe(true);
  });
  it('es determinista con la misma semilla', () => {
    const a = simulateCoverage(30, 0.95, 50, 7);
    const b = simulateCoverage(30, 0.95, 50, 7);
    expect(a.coverage).toBe(b.coverage);
  });
  it('con muestras grandes la cobertura se acerca al nivel nominal', () => {
    const r = simulateCoverage(200, 0.95, 1500, 3);
    expect(r.coverage).toBeGreaterThan(0.92);
    expect(r.coverage).toBeLessThan(0.97);
  });
  it('con muestras pequeñas y datos asimétricos cubre por debajo del nivel nominal', () => {
    const r = simulateCoverage(10, 0.95, 1500, 3);
    expect(r.coverage).toBeLessThan(0.93);
  });
});

describe('tamaño de muestra y potencia', () => {
  it('coincide con el cálculo de referencia (5 % → +10 % relativo)', () => {
    expect(sampleSizeProportions(0.05, 0.1)).toBe(31231);
  });
  it('coincide con el cálculo de referencia para el experimento de checkout', () => {
    expect(sampleSizeProportions(0.054, 0.08)).toBe(44582);
  });
  it('la potencia con n = 10.000 por grupo es ≈ 0,354', () => {
    expect(powerProportions(0.05, 0.1, 10000)).toBeCloseTo(0.3542, 3);
  });
  it('la potencia con el n calculado es ≈ 0,80', () => {
    expect(powerProportions(0.05, 0.1, 31231)).toBeCloseTo(0.8, 2);
  });
});

describe('SRM', () => {
  it('detecta el 11.166 / 8.834 del experimento de recomendaciones', () => {
    const r = srmTest(11166, 8834);
    expect(r.chi2).toBeCloseTo(271.9112, 3);
    expect(r.p).toBeLessThan(1e-10);
  });
  it('no alarma con un reparto normal', () => {
    expect(srmTest(10074, 9926).p).toBeGreaterThan(0.1);
  });
});

describe('rng', () => {
  it('produce valores en [0, 1)', () => {
    const u = rng(1);
    for (let i = 0; i < 100; i++) {
      const v = u();
      expect(v).toBeGreaterThanOrEqual(0);
      expect(v).toBeLessThan(1);
    }
  });
});
