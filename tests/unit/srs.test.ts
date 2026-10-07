import { describe, expect, it } from 'vitest';
import { LEITNER_INTERVALS_DAYS, dueCards, reviewCard } from '../../src/lib/srs';

const NOW = new Date('2026-01-01T00:00:00.000Z');

describe('reviewCard', () => {
  it('una pregunta nueva empieza en la caja 1', () => {
    const card = reviewCard(undefined, false, NOW);
    expect(card.box).toBe(1);
  });

  it('acertar sube una caja', () => {
    const card = reviewCard({ box: 2, due: NOW.toISOString() }, true, NOW);
    expect(card.box).toBe(3);
  });

  it('la caja 5 es el máximo', () => {
    const card = reviewCard({ box: 5, due: NOW.toISOString() }, true, NOW);
    expect(card.box).toBe(5);
  });

  it('fallar siempre vuelve a la caja 1', () => {
    const card = reviewCard({ box: 4, due: NOW.toISOString() }, false, NOW);
    expect(card.box).toBe(1);
  });

  it('el vencimiento respeta los intervalos de Leitner', () => {
    const card = reviewCard({ box: 1, due: NOW.toISOString() }, true, NOW);
    expect(card.box).toBe(2);
    const expectedDue = new Date(NOW);
    expectedDue.setDate(expectedDue.getDate() + LEITNER_INTERVALS_DAYS[2]);
    expect(card.due).toBe(expectedDue.toISOString());
  });
});

describe('dueCards', () => {
  it('devuelve solo las preguntas vencidas, ordenadas por fecha', () => {
    const srs = {
      futura: { box: 1 as const, due: '2026-02-01T00:00:00.000Z' },
      vencidaTarde: { box: 1 as const, due: '2025-12-30T00:00:00.000Z' },
      vencidaPronto: { box: 1 as const, due: '2025-12-20T00:00:00.000Z' },
    };
    expect(dueCards(srs, NOW)).toEqual(['vencidaPronto', 'vencidaTarde']);
  });

  it('una pregunta que vence justo hoy cuenta como vencida', () => {
    const srs = { hoy: { box: 1 as const, due: NOW.toISOString() } };
    expect(dueCards(srs, NOW)).toEqual(['hoy']);
  });
});
