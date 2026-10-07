import { loadAllQuestions } from '../../lib/questions';

/** Banco de preguntas para el examen y el repaso (se carga en el cliente). */
export async function GET() {
  const questions = await loadAllQuestions();
  return new Response(JSON.stringify(questions), {
    headers: { 'Content-Type': 'application/json' },
  });
}
