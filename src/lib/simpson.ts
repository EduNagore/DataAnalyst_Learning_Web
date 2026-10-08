/** Tasa agregada de un grupo = media de las tasas por estrato ponderada por su mezcla. */
export function aggregateRate(
  ratesByStratum: [number, number],
  shareOfFirstStratum: number,
): number {
  const w = Math.min(Math.max(shareOfFirstStratum, 0), 1);
  return w * ratesByStratum[0] + (1 - w) * ratesByStratum[1];
}

export type Winner = 'A' | 'B' | 'empate';

export function winner(a: number, b: number, epsilon = 0.005): Winner {
  if (Math.abs(a - b) < epsilon) return 'empate';
  return a > b ? 'A' : 'B';
}

/** ¿Hay paradoja? El mismo grupo gana en todos los estratos y pierde en el agregado. */
export function isSimpson(
  ratesA: [number, number],
  ratesB: [number, number],
  aggA: number,
  aggB: number,
): boolean {
  const w0 = winner(ratesA[0], ratesB[0]);
  const w1 = winner(ratesA[1], ratesB[1]);
  const wAgg = winner(aggA, aggB);
  return w0 !== 'empate' && w0 === w1 && wAgg !== 'empate' && wAgg !== w0;
}
