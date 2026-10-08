import { describe, expect, it } from 'vitest';
import { aggregateRate, isSimpson, winner } from '../../src/lib/simpson';

// Conversión de sesiones de Lumen en Madrid / Andalucía: móvil y escritorio.
const mobile: [number, number] = [9175 / 127579, 455 / 26871].map((v) => v * 100) as [
  number,
  number,
];
const desktop: [number, number] = [2280 / 19010, 3319 / 130296].map((v) => v * 100) as [
  number,
  number,
];

describe('aggregateRate', () => {
  it('pondera por la mezcla de estratos', () => {
    expect(aggregateRate([10, 2], 0.5)).toBeCloseTo(6);
    expect(aggregateRate([10, 2], 1)).toBe(10);
    expect(aggregateRate([10, 2], 0)).toBe(2);
  });

  it('acota la mezcla a [0, 1]', () => {
    expect(aggregateRate([10, 2], 2)).toBe(10);
    expect(aggregateRate([10, 2], -1)).toBe(2);
  });
});

describe('winner e isSimpson', () => {
  it('reproduce la paradoja de Lumen (móvil vs escritorio)', () => {
    const shareMobile = 127579 / (127579 + 26871);
    const shareDesktop = 19010 / (19010 + 130296);
    const aggM = aggregateRate(mobile, shareMobile);
    const aggD = aggregateRate(desktop, shareDesktop);
    expect(aggM).toBeCloseTo(6.2, 1);
    expect(aggD).toBeCloseTo(3.8, 1);
    expect(winner(mobile[0], desktop[0])).toBe('B');
    expect(winner(mobile[1], desktop[1])).toBe('B');
    expect(winner(aggM, aggD)).toBe('A');
    expect(isSimpson(mobile, desktop, aggM, aggD)).toBe(true);
  });

  it('con la misma mezcla no hay paradoja', () => {
    const aggM = aggregateRate(mobile, 0.5);
    const aggD = aggregateRate(desktop, 0.5);
    expect(isSimpson(mobile, desktop, aggM, aggD)).toBe(false);
  });

  it('un empate no cuenta como victoria', () => {
    expect(winner(5, 5.001)).toBe('empate');
  });
});
