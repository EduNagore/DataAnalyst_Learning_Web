/**
 * Corrección y puntuación de quizzes (ver PLAN.md §6 y §7.2).
 *
 * Tipos de pregunta soportados: single, multiple, truefalse, order, numeric,
 * sql-output, formula-output, chart-critique. Los cuatro últimos se evalúan
 * igual que `single`/`numeric` a nivel de datos (el enunciado ya incluye el
 * código/tabla/imagen en markdown); lo que cambia es solo la presentación.
 */

export type QuestionType =
  | 'single'
  | 'multiple'
  | 'truefalse'
  | 'order'
  | 'numeric'
  | 'sql-output'
  | 'formula-output'
  | 'chart-critique';

export interface QuizQuestion {
  id: string;
  type: QuestionType;
  difficulty: 1 | 2 | 3;
  prompt: string;
  options?: string[];
  answer: number[] | number;
  tolerance?: number | string; // numeric: absoluta (0.01) o relativa ('rel:0.02')
  explanation: string;
  ref?: string;
}

export type QuizResponse = number[] | number;

/** Mezcla determinista basada en una semilla (mulberry32), para que el
 * barajado de opciones sea reproducible entre sesiones/tests. */
export function seededShuffle<T>(items: T[], seed: string): T[] {
  let h = 1779033703 ^ seed.length;
  for (let i = 0; i < seed.length; i++) {
    h = Math.imul(h ^ seed.charCodeAt(i), 3432918353);
    h = (h << 13) | (h >>> 19);
  }
  let state = h >>> 0;
  function rand(): number {
    state |= 0;
    state = (state + 0x6d2b79f5) | 0;
    let t = Math.imul(state ^ (state >>> 15), 1 | state);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  }
  const result = [...items];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

function parseTolerance(tolerance: number | string | undefined, expected: number): number {
  if (tolerance === undefined) return 1e-9;
  if (typeof tolerance === 'number') return tolerance;
  const relMatch = /^rel:(-?[\d.]+)$/.exec(tolerance);
  if (relMatch) return Math.abs(expected) * parseFloat(relMatch[1]);
  return parseFloat(tolerance);
}

function arraysEqualAsSets(a: number[], b: number[]): boolean {
  if (a.length !== b.length) return false;
  const sortedA = [...a].sort((x, y) => x - y);
  const sortedB = [...b].sort((x, y) => x - y);
  return sortedA.every((v, i) => v === sortedB[i]);
}

function arraysEqualInOrder(a: number[], b: number[]): boolean {
  return a.length === b.length && a.every((v, i) => v === b[i]);
}

/** Evalúa una respuesta contra la clave de corrección de la pregunta. */
export function checkAnswer(question: QuizQuestion, response: QuizResponse): boolean {
  switch (question.type) {
    case 'numeric': {
      const expected = Array.isArray(question.answer) ? question.answer[0] : question.answer;
      const given = Array.isArray(response) ? response[0] : response;
      if (typeof given !== 'number' || Number.isNaN(given)) return false;
      const tol = parseTolerance(question.tolerance, expected);
      return Math.abs(given - expected) <= tol;
    }
    case 'order': {
      const expected = Array.isArray(question.answer) ? question.answer : [question.answer];
      const given = Array.isArray(response) ? response : [response];
      return arraysEqualInOrder(expected, given);
    }
    case 'multiple': {
      const expected = Array.isArray(question.answer) ? question.answer : [question.answer];
      const given = Array.isArray(response) ? response : [response];
      return arraysEqualAsSets(expected, given);
    }
    case 'single':
    case 'truefalse':
    case 'sql-output':
    case 'formula-output':
    case 'chart-critique':
    default: {
      const expected = Array.isArray(question.answer) ? question.answer[0] : question.answer;
      const given = Array.isArray(response) ? response[0] : response;
      return expected === given;
    }
  }
}

export interface QuizResult {
  score: number; // 0..1
  correctCount: number;
  total: number;
  byQuestion: Record<string, boolean>;
}

/** Puntúa un intento completo de quiz. `responses` puede omitir preguntas
 * sin responder (se cuentan como falladas). */
export function scoreQuiz(
  questions: QuizQuestion[],
  responses: Record<string, QuizResponse>,
): QuizResult {
  const byQuestion: Record<string, boolean> = {};
  let correctCount = 0;
  for (const q of questions) {
    const response = responses[q.id];
    const correct = response !== undefined ? checkAnswer(q, response) : false;
    byQuestion[q.id] = correct;
    if (correct) correctCount++;
  }
  const total = questions.length;
  return { score: total === 0 ? 0 : correctCount / total, correctCount, total, byQuestion };
}

/** Umbral de aprobado por módulo (PLAN.md §7.2: ≥ 80 %). */
export const PASS_THRESHOLD = 0.8;

export function passed(result: QuizResult): boolean {
  return result.score >= PASS_THRESHOLD;
}
