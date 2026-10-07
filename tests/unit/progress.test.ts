import { beforeEach, describe, expect, it } from 'vitest';
import {
  exportProgress,
  hydrateProgress,
  importProgress,
  markLessonRead,
  progressStore,
  recordQuizScore,
  resetProgress,
  saveLabProgress,
} from '../../src/lib/progress';

beforeEach(() => {
  localStorage.clear();
  hydrateProgress();
});

describe('markLessonRead', () => {
  it('registra la fecha de lectura y persiste en localStorage', () => {
    markLessonRead('sql-i/01-fundamentos', '2026-01-01T00:00:00.000Z');
    expect(progressStore.get().lessonsRead['sql-i/01-fundamentos']).toBe(
      '2026-01-01T00:00:00.000Z',
    );

    hydrateProgress(); // simula recargar la página
    expect(progressStore.get().lessonsRead['sql-i/01-fundamentos']).toBe(
      '2026-01-01T00:00:00.000Z',
    );
  });
});

describe('recordQuizScore', () => {
  it('guarda el mejor intento y el número de intentos', () => {
    recordQuizScore('quiz-1', 0.6);
    recordQuizScore('quiz-1', 0.9);
    recordQuizScore('quiz-1', 0.7);

    const score = progressStore.get().quizScores['quiz-1'];
    expect(score.best).toBe(0.9);
    expect(score.last).toBe(0.7);
    expect(score.attempts).toBe(3);
  });
});

describe('saveLabProgress', () => {
  it('guarda el código y el estado del laboratorio', () => {
    saveLabProgress('lab-01', 'SELECT 1', 'started');
    expect(progressStore.get().labs['lab-01']).toMatchObject({
      status: 'started',
      code: 'SELECT 1',
    });

    saveLabProgress('lab-01', 'SELECT 1; -- ok', 'passed');
    expect(progressStore.get().labs['lab-01'].status).toBe('passed');
  });
});

describe('export / import', () => {
  it('importProgress recupera exactamente lo exportado', () => {
    markLessonRead('m00/01', '2026-01-01T00:00:00.000Z');
    recordQuizScore('quiz-1', 1);
    const exported = exportProgress();

    resetProgress();
    expect(progressStore.get().lessonsRead).toEqual({});

    const result = importProgress(exported);
    expect(result.ok).toBe(true);
    expect(progressStore.get().lessonsRead['m00/01']).toBe('2026-01-01T00:00:00.000Z');
    expect(progressStore.get().quizScores['quiz-1'].best).toBe(1);
  });

  it('un JSON inválido no rompe el estado actual y devuelve un error', () => {
    markLessonRead('m00/01');
    const result = importProgress('{ esto no es json');
    expect(result.ok).toBe(false);
    expect(progressStore.get().lessonsRead['m00/01']).toBeDefined();
  });
});

describe('resetProgress', () => {
  it('vacía todo el estado', () => {
    markLessonRead('m00/01');
    recordQuizScore('quiz-1', 1);
    resetProgress();
    expect(progressStore.get()).toMatchObject({ lessonsRead: {}, quizScores: {}, labs: {} });
  });
});
