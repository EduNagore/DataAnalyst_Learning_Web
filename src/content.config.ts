import { defineCollection, z } from 'astro:content';
import { glob, file } from 'astro/loaders';

// ---------------------------------------------------------------------------
// Esquemas compartidos (ver PLAN.md §6)
// ---------------------------------------------------------------------------

const sourceSchema = z.object({
  title: z.string(),
  url: z.string().url(),
  type: z.enum(['paper', 'docs', 'blog', 'spec', 'book', 'video', 'course']),
  authors: z.string().optional(),
  year: z.number().int(),
});

const quizQuestionSchema = z.object({
  id: z.string(),
  type: z.enum([
    'single',
    'multiple',
    'truefalse',
    'order',
    'numeric',
    'sql-output',
    'formula-output',
    'chart-critique',
  ]),
  difficulty: z.union([z.literal(1), z.literal(2), z.literal(3)]),
  prompt: z.string(),
  code: z.string().optional(),
  table: z.string().optional(),
  image: z.string().optional(),
  imageAlt: z.string().optional(),
  options: z.array(z.string()).optional(),
  answer: z.union([z.number(), z.array(z.number())]),
  tolerance: z.union([z.number(), z.string()]).optional(),
  explanation: z.string(),
  ref: z.string().optional(),
});

// ---------------------------------------------------------------------------
// Módulos
// ---------------------------------------------------------------------------

const modules = defineCollection({
  loader: glob({ pattern: '**/*.yaml', base: './src/content/modules' }),
  schema: z.object({
    id: z.string(),
    part: z.string(),
    partOrder: z.number().int(),
    order: z.number().int(),
    title: z.string(),
    description: z.string(),
    objectives: z.array(z.string()),
    estimatedHours: z.number().positive(),
    volatility: z.enum(['low', 'medium', 'high']).default('low'),
  }),
});

// ---------------------------------------------------------------------------
// Lecciones
// ---------------------------------------------------------------------------

const lessons = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/lessons' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    module: z.string(),
    order: z.number().int(),
    level: z.enum(['básico', 'intermedio', 'avanzado']),
    estimatedMinutes: z.number().positive(),
    objectives: z.array(z.string()).min(3).max(6),
    prerequisites: z.array(z.string()).optional(),
    tools: z.array(z.string()).optional(),
    volatility: z.enum(['low', 'medium', 'high']),
    lastReviewed: z.coerce.date(),
    sources: z.array(sourceSchema).min(2),
    relatedLabs: z.array(z.string()).optional(),
    relatedCases: z.array(z.string()).optional(),
  }),
});

// ---------------------------------------------------------------------------
// Quizzes (un YAML por lección)
// ---------------------------------------------------------------------------

const quizzes = defineCollection({
  loader: glob({ pattern: '**/*.yaml', base: './src/content/quizzes' }),
  schema: z.object({
    lesson: z.string(),
    questions: z.array(quizQuestionSchema).min(1),
  }),
});

// ---------------------------------------------------------------------------
// Laboratorios
// ---------------------------------------------------------------------------

const labs = defineCollection({
  loader: glob({ pattern: '**/index.mdx', base: './src/content/labs' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    language: z.enum(['sql', 'python']),
    part: z.string(),
    module: z.string(),
    difficulty: z.union([z.literal(1), z.literal(2), z.literal(3)]),
    estimatedMinutes: z.number().positive(),
    concepts: z.array(z.string()),
    datasets: z.array(z.string()),
    packages: z.array(z.string()).optional(),
    output: z.enum(['table', 'chart', 'console']).default('table'),
    hints: z.array(z.string()),
    relatedLessons: z.array(z.string()),
    businessQuestion: z.string(),
  }),
});

// ---------------------------------------------------------------------------
// Casos de análisis guiados
// ---------------------------------------------------------------------------

const caseStepSchema = z.object({
  id: z.string(),
  prompt: z.string(),
  tool: z.enum(['sql', 'python', 'reasoning']),
  answerType: z.enum(['numeric', 'single', 'multiple', 'text-self-assessed']),
  answer: z.union([z.number(), z.array(z.number())]).optional(),
  tolerance: z.union([z.number(), z.string()]).optional(),
  options: z.array(z.string()).optional(),
  hints: z.array(z.string()),
  explanation: z.string(),
});

const cases = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/cases' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    difficulty: z.union([z.literal(1), z.literal(2), z.literal(3)]),
    estimatedMinutes: z.number().positive(),
    role: z.enum(['producto', 'marketing', 'finanzas', 'operaciones', 'bi']),
    brief: z.string(),
    steps: z.array(caseStepSchema).min(1),
    rubric: z.array(z.string()),
    modelReport: z.string(),
  }),
});

// ---------------------------------------------------------------------------
// Hojas de cálculo descargables
// ---------------------------------------------------------------------------

const workbooks = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/workbooks' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    difficulty: z.union([z.literal(1), z.literal(2), z.literal(3)]),
    estimatedMinutes: z.number().positive(),
    skills: z.array(z.string()),
    functions: z.array(z.object({ en: z.string(), es: z.string() })).optional(),
    commonMistakes: z.array(z.string()),
    downloadUrl: z.string(),
    solutionUrl: z.string(),
  }),
});

// ---------------------------------------------------------------------------
// Proyectos de portfolio
// ---------------------------------------------------------------------------

const projects = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/projects' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    difficulty: z.union([z.literal(1), z.literal(2), z.literal(3)]),
    estimatedHours: z.number().positive(),
    skills: z.array(z.string()),
    tools: z.array(z.string()),
    repoPath: z.string(), // carpeta en /projects/<id>
  }),
});

// ---------------------------------------------------------------------------
// Radar del analista (un único YAML con un array de entradas)
// ---------------------------------------------------------------------------

const radar = defineCollection({
  loader: file('./src/content/radar/entries.yaml'),
  schema: z.object({
    id: z.string(),
    name: z.string(),
    category: z.enum([
      'sql-motores',
      'herramientas-python',
      'bi',
      'ingenieria-analitica',
      'ia-analitica',
      'tecnicas',
    ]),
    ring: z.enum(['adoptar', 'probar', 'evaluar', 'evitar']),
    asOf: z.coerce.date(),
    summary: z.string(),
    sources: z.array(z.object({ title: z.string(), url: z.string().url() })),
    relatedLessons: z.array(z.string()).optional(),
  }),
});

// ---------------------------------------------------------------------------
// Entrevistas
// ---------------------------------------------------------------------------

const interviewQuestions = defineCollection({
  loader: file('./src/content/interview/questions.yaml'),
  schema: z.object({
    id: z.string(),
    topic: z.string(),
    level: z.enum(['junior', 'mid', 'senior']),
    type: z.enum(['conceptual', 'design', 'debugging']),
    promptEs: z.string(),
    promptEn: z.string(),
    answerEs: z.string(),
    answerEn: z.string(),
  }),
});

const interviewCases = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/interview/cases' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    estimatedMinutes: z.number().positive(),
    clarifyingQuestions: z.array(z.string()),
    commonMistakes: z.array(z.string()),
    seniorTake: z.string(),
  }),
});

// ---------------------------------------------------------------------------
// Changelog del curso
// ---------------------------------------------------------------------------

const changelog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/changelog' }),
  schema: z.object({
    date: z.coerce.date(),
    title: z.string(),
    summary: z.string(),
    affects: z.array(z.string()).optional(),
  }),
});

// ---------------------------------------------------------------------------
// Glosario (un único YAML con un array de términos)
// ---------------------------------------------------------------------------

const glossary = defineCollection({
  loader: file('./src/content/glossary/terms.yaml'),
  schema: z.object({
    id: z.string(),
    termEs: z.string(),
    termEn: z.string(),
    definition: z.string(),
    relatedLessons: z.array(z.string()).optional(),
  }),
});

export const collections = {
  modules,
  lessons,
  quizzes,
  labs,
  cases,
  workbooks,
  projects,
  radar,
  interviewQuestions,
  interviewCases,
  changelog,
  glossary,
};
