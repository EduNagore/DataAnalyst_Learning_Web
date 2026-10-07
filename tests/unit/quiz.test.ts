import { describe, expect, it } from 'vitest';
import {
  checkAnswer,
  passed,
  scoreQuiz,
  seededShuffle,
  type QuizQuestion,
} from '../../src/lib/quiz';

function q(overrides: Partial<QuizQuestion>): QuizQuestion {
  return {
    id: 'q1',
    type: 'single',
    difficulty: 1,
    prompt: '¿?',
    answer: 0,
    explanation: '...',
    ...overrides,
  };
}

describe('checkAnswer', () => {
  it('single: compara el índice exacto', () => {
    expect(checkAnswer(q({ type: 'single', answer: 2 }), 2)).toBe(true);
    expect(checkAnswer(q({ type: 'single', answer: 2 }), 1)).toBe(false);
  });

  it('truefalse: se trata como single (0=verdadero)', () => {
    expect(checkAnswer(q({ type: 'truefalse', answer: 0 }), 0)).toBe(true);
    expect(checkAnswer(q({ type: 'truefalse', answer: 0 }), 1)).toBe(false);
  });

  it('multiple: ignora el orden de las opciones marcadas', () => {
    const question = q({ type: 'multiple', answer: [1, 3] });
    expect(checkAnswer(question, [3, 1])).toBe(true);
    expect(checkAnswer(question, [1, 2])).toBe(false);
  });

  it('order: exige el mismo orden', () => {
    const question = q({ type: 'order', answer: [2, 0, 1] });
    expect(checkAnswer(question, [2, 0, 1])).toBe(true);
    expect(checkAnswer(question, [0, 1, 2])).toBe(false);
  });

  it('numeric: respeta la tolerancia absoluta', () => {
    const question = q({ type: 'numeric', answer: 10, tolerance: 0.5 });
    expect(checkAnswer(question, 10.4)).toBe(true);
    expect(checkAnswer(question, 10.6)).toBe(false);
  });

  it('numeric: respeta la tolerancia relativa', () => {
    const question = q({ type: 'numeric', answer: 100, tolerance: 'rel:0.05' });
    expect(checkAnswer(question, 104)).toBe(true);
    expect(checkAnswer(question, 106)).toBe(false);
  });

  it('numeric: una respuesta no numérica nunca es correcta', () => {
    const question = q({ type: 'numeric', answer: 10 });
    expect(checkAnswer(question, Number.NaN)).toBe(false);
  });
});

describe('scoreQuiz', () => {
  const questions = [
    q({ id: 'a', type: 'single', answer: 0 }),
    q({ id: 'b', type: 'single', answer: 1 }),
    q({ id: 'c', type: 'single', answer: 2 }),
    q({ id: 'd', type: 'single', answer: 3 }),
    q({ id: 'e', type: 'single', answer: 4 }),
  ];

  it('cuenta las preguntas sin responder como falladas', () => {
    const result = scoreQuiz(questions, { a: 0, b: 1 });
    expect(result.correctCount).toBe(2);
    expect(result.total).toBe(5);
    expect(result.score).toBeCloseTo(0.4);
  });

  it('el umbral de aprobado es 80%', () => {
    const result = scoreQuiz(questions, { a: 0, b: 1, c: 2, d: 3, e: 9 });
    expect(result.score).toBeCloseTo(0.8);
    expect(passed(result)).toBe(true);
  });

  it('por debajo del 80% no aprueba', () => {
    const result = scoreQuiz(questions, { a: 0, b: 1, c: 2, d: 9, e: 9 });
    expect(passed(result)).toBe(false);
  });
});

describe('seededShuffle', () => {
  it('es determinista para la misma semilla', () => {
    const items = ['a', 'b', 'c', 'd', 'e'];
    expect(seededShuffle(items, 'seed-1')).toEqual(seededShuffle(items, 'seed-1'));
  });

  it('no pierde ni duplica elementos', () => {
    const items = [1, 2, 3, 4, 5, 6];
    const shuffled = seededShuffle(items, 'cualquier-semilla');
    expect([...shuffled].sort((a, b) => a - b)).toEqual(items);
  });

  it('semillas distintas suelen dar órdenes distintos', () => {
    const items = [1, 2, 3, 4, 5, 6, 7, 8];
    expect(seededShuffle(items, 'semilla-A')).not.toEqual(seededShuffle(items, 'semilla-B'));
  });
});

import { parseNumberEs, shuffledOrder } from '../../src/lib/quiz';

describe('parseNumberEs', () => {
  it.each([
    ['14,85', 14.85],
    ['28.173', 28173],
    ['1.234,5', 1234.5],
    ['14.85', 14.85],
    ['  18 ', 18],
    ['-3,5', -3.5],
    ['2.275.942,25', 2275942.25],
  ])('interpreta %s como %d', (raw, expected) => {
    expect(parseNumberEs(raw)).toBeCloseTo(expected);
  });

  it.each(['', 'abc', '1,2,3', '12a'])('devuelve NaN para %j', (raw) => {
    expect(parseNumberEs(raw)).toBeNaN();
  });
});

describe('shuffledOrder', () => {
  it('es una permutación determinista de 0..n-1', () => {
    const order = shuffledOrder(5, 'q1');
    expect([...order].sort()).toEqual([0, 1, 2, 3, 4]);
    expect(shuffledOrder(5, 'q1')).toEqual(order);
  });
});
