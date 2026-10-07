/**
 * Carga todas las preguntas de quiz con los metadatos que necesitan el
 * examen, el repaso y los tests por módulo (módulo, lección, URL de la
 * explicación). Solo se puede importar desde páginas/endpoints de Astro
 * (usa `astro:content`).
 */
import { getCollection } from 'astro:content';
import type { QuizQuestion } from './quiz';
import { url } from './url';

export interface FullQuestion extends QuizQuestion {
  module: string;
  moduleTitle: string;
  lessonId: string;
  lessonTitle: string;
  /** Enlace a la sección de la lección donde se explica. */
  refUrl: string;
}

export async function loadAllQuestions(): Promise<FullQuestion[]> {
  const [quizzes, lessons, modules] = await Promise.all([
    getCollection('quizzes'),
    getCollection('lessons'),
    getCollection('modules'),
  ]);
  const lessonById = new Map(lessons.map((l) => [l.id, l]));
  const moduleById = new Map(modules.map((m) => [m.data.id, m]));

  const result: FullQuestion[] = [];
  for (const quiz of quizzes) {
    const lesson = lessonById.get(quiz.data.lesson);
    if (!lesson) throw new Error(`Quiz ${quiz.id} apunta a una lección inexistente`);
    const mod = moduleById.get(lesson.data.module);
    const lessonUrl = url(`/teoria/${lesson.data.module}/${lesson.id.split('/').pop()}/`);
    for (const q of quiz.data.questions) {
      result.push({
        ...(q as QuizQuestion),
        module: lesson.data.module,
        moduleTitle: mod?.data.title ?? lesson.data.module,
        lessonId: lesson.id,
        lessonTitle: lesson.data.title,
        refUrl: q.ref ? `${lessonUrl}${q.ref}` : lessonUrl,
      });
    }
  }
  return result;
}
