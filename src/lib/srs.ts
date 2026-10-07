/**
 * Repaso espaciado con el sistema Leitner (5 cajas, ver PLAN.md §7.2).
 *
 * Caja 1 → 2 → 3 → 4 → 5 al acertar; cualquier fallo vuelve a la caja 1.
 * Intervalos en días desde la última revisión hasta la próxima.
 */
import type { SrsCard } from './progress';

export const LEITNER_INTERVALS_DAYS: Record<SrsCard['box'], number> = {
  1: 1,
  2: 2,
  3: 4,
  4: 8,
  5: 16,
};

const MAX_BOX = 5;
const MIN_BOX = 1;

function addDays(date: Date, days: number): Date {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
}

/**
 * Calcula la siguiente caja y fecha de vencimiento tras responder una
 * pregunta. `now` es inyectable para que los tests sean deterministas.
 */
export function reviewCard(card: SrsCard | undefined, correct: boolean, now = new Date()): SrsCard {
  const currentBox = card?.box ?? MIN_BOX;
  const nextBox = correct
    ? (Math.min(currentBox + 1, MAX_BOX) as SrsCard['box'])
    : (MIN_BOX as SrsCard['box']);
  const due = addDays(now, LEITNER_INTERVALS_DAYS[nextBox]);
  return { box: nextBox, due: due.toISOString() };
}

/** Preguntas cuya fecha de vencimiento ya ha pasado (o es hoy). */
export function dueCards(srs: Record<string, SrsCard>, now = new Date()): string[] {
  return Object.entries(srs)
    .filter(([, card]) => new Date(card.due).getTime() <= now.getTime())
    .map(([questionId]) => questionId)
    .sort((a, b) => new Date(srs[a].due).getTime() - new Date(srs[b].due).getTime());
}
