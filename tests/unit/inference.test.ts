import { describe, expect, it } from 'vitest';
import {
  cupedAnalysis,
  msprtLambda,
  peekingRates,
  meanInterval,
  normalQuantile,
  powerProportions,
  rng,
  sampleSizeProportions,
  simulateCoverage,
  simulateCupedSample,
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

describe('CUPED', () => {
  it('reduce la varianza en torno a 1 − ρ²', () => {
    const r = cupedAnalysis(simulateCupedSample(0.75, 0.2, 20000, 5));
    expect(r.varianceReduction).toBeGreaterThan(0.52);
    expect(r.varianceReduction).toBeLessThan(0.6);
    expect(r.cupedSe).toBeLessThan(r.rawSe);
    expect(r.rho).toBeGreaterThan(0.7);
    expect(r.theta).toBeCloseTo(0.75, 1);
  });
  it('no cambia el efecto estimado y sin correlación apenas reduce el error', () => {
    const r = cupedAnalysis(simulateCupedSample(0, 0.3, 20000, 9));
    expect(Math.abs(r.cupedEffect - r.rawEffect)).toBeLessThan(0.05);
    expect(r.cupedSe / r.rawSe).toBeGreaterThan(0.98);
  });
  it('el efecto estimado se acerca al verdadero', () => {
    const r = cupedAnalysis(simulateCupedSample(0.9, 0.25, 40000, 2));
    expect(r.cupedEffect).toBeGreaterThan(0.2);
    expect(r.cupedEffect).toBeLessThan(0.3);
  });
});

describe('mirar antes de tiempo (peeking)', () => {
  it('parar en el primer p < 0,05 infla los falsos positivos (10 revisiones ≈ 19 %)', () => {
    const r = peekingRates(10, 8000, 11);
    expect(r.finalOnly).toBeGreaterThan(0.04);
    expect(r.finalOnly).toBeLessThan(0.06);
    expect(r.peeking).toBeGreaterThan(0.17);
    expect(r.peeking).toBeLessThan(0.22);
  });
  it('los límites de Pocock y O’Brien-Fleming recuperan el 5 %', () => {
    const r = peekingRates(5, 12000, 3);
    expect(r.pocock).toBeGreaterThan(0.04);
    expect(r.pocock).toBeLessThan(0.06);
    expect(r.obf).toBeGreaterThan(0.04);
    expect(r.obf).toBeLessThan(0.06);
  });
  it('mSPRT: la razón crece con |x̄| y vale ~1 cuando x̄ = 0 con pocos datos', () => {
    expect(msprtLambda(1, 0, 1, 0.25)).toBeCloseTo(Math.sqrt(1 / 1.25), 6);
    expect(msprtLambda(100, 0.5, 1, 0.25)).toBeGreaterThan(msprtLambda(100, 0.1, 1, 0.25));
  });
});
