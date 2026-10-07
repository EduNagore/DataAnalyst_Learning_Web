/**
 * Estado de progreso del alumno (ver PLAN.md §6).
 *
 * Todo vive en localStorage bajo una única clave versionada. Sin backend:
 * exportar/importar es la única forma de llevar el progreso de un
 * dispositivo a otro. Todas las lecturas/escrituras están protegidas con
 * try/catch porque localStorage puede no estar disponible (navegación
 * privada, almacenamiento bloqueado, SSR) o puede lanzar por cuota.
 */
import { atom } from 'nanostores';

export const PROGRESS_STORAGE_KEY = 'daa:progress:v1';
const SCHEMA_VERSION = 1;

export interface LabProgress {
  status: 'started' | 'passed';
  code: string;
  updatedAt: string; // ISO date
}

export interface CaseProgress {
  step: number;
  answers: Record<string, unknown>;
  completed?: string; // ISO date
}

export interface QuizScore {
  best: number;
  last: number;
  attempts: number;
}

export interface SrsCard {
  box: 1 | 2 | 3 | 4 | 5;
  due: string; // ISO date
}

export interface ExamResult {
  date: string; // ISO date
  score: number;
  total: number;
  byModule: Record<string, number>;
}

export interface ProgressState {
  schemaVersion: number;
  lessonsRead: Record<string, string>;
  quizScores: Record<string, QuizScore>;
  labs: Record<string, LabProgress>;
  cases: Record<string, CaseProgress>;
  srs: Record<string, SrsCard>;
  exams: ExamResult[];
}

export function emptyProgress(): ProgressState {
  return {
    schemaVersion: SCHEMA_VERSION,
    lessonsRead: {},
    quizScores: {},
    labs: {},
    cases: {},
    srs: {},
    exams: [],
  };
}

function migrate(data: unknown): ProgressState {
  if (
    typeof data !== 'object' ||
    data === null ||
    !('schemaVersion' in data) ||
    (data as { schemaVersion?: unknown }).schemaVersion !== SCHEMA_VERSION
  ) {
    // Sin migraciones todavía: cualquier versión desconocida se descarta
    // a favor de un estado vacío en lugar de arriesgar datos corruptos.
    return emptyProgress();
  }
  return { ...emptyProgress(), ...(data as Partial<ProgressState>) };
}

function readFromStorage(): ProgressState {
  try {
    const raw = localStorage.getItem(PROGRESS_STORAGE_KEY);
    if (!raw) return emptyProgress();
    return migrate(JSON.parse(raw));
  } catch {
    return emptyProgress();
  }
}

function writeToStorage(state: ProgressState): void {
  try {
    localStorage.setItem(PROGRESS_STORAGE_KEY, JSON.stringify(state));
  } catch {
    // Cuota excedida o almacenamiento no disponible: el progreso de esta
    // sesión sigue funcionando en memoria aunque no se persista.
  }
}

export const progressStore = atom<ProgressState>(emptyProgress());

/** Debe llamarse una vez en el cliente (nunca en SSR) antes de leer el store. */
export function hydrateProgress(): void {
  progressStore.set(readFromStorage());
}

function update(mutator: (draft: ProgressState) => void): void {
  const next = structuredClone(progressStore.get());
  mutator(next);
  progressStore.set(next);
  writeToStorage(next);
}

export function markLessonRead(lessonId: string, isoDate = new Date().toISOString()): void {
  update((draft) => {
    draft.lessonsRead[lessonId] = isoDate;
  });
}

export function recordQuizScore(quizId: string, score: number): void {
  update((draft) => {
    const prev = draft.quizScores[quizId];
    draft.quizScores[quizId] = {
      best: prev ? Math.max(prev.best, score) : score,
      last: score,
      attempts: (prev?.attempts ?? 0) + 1,
    };
  });
}

export function saveLabProgress(labId: string, code: string, status: LabProgress['status']): void {
  update((draft) => {
    draft.labs[labId] = { status, code, updatedAt: new Date().toISOString() };
  });
}

export function saveCaseProgress(
  caseId: string,
  step: number,
  answers: Record<string, unknown>,
  completed?: string,
): void {
  update((draft) => {
    draft.cases[caseId] = { step, answers, completed };
  });
}

export function recordExam(result: ExamResult): void {
  update((draft) => {
    draft.exams.push(result);
  });
}

export function exportProgress(): string {
  return JSON.stringify(progressStore.get(), null, 2);
}

export function importProgress(json: string): { ok: true } | { ok: false; error: string } {
  try {
    const parsed = migrate(JSON.parse(json));
    progressStore.set(parsed);
    writeToStorage(parsed);
    return { ok: true };
  } catch (err) {
    return { ok: false, error: err instanceof Error ? err.message : 'JSON inválido' };
  }
}

export function resetProgress(): void {
  const next = emptyProgress();
  progressStore.set(next);
  writeToStorage(next);
}
