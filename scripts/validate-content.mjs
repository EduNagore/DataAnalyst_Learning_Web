#!/usr/bin/env node
/**
 * Valida la integridad referencial del contenido (ver PLAN.md §11):
 *  - todo quiz apunta a una lección existente
 *  - los ids de pregunta son únicos a nivel global
 *  - las anclas `ref` existen como encabezado en la lección referenciada
 *  - cada lección tiene módulo válido y ≥ 2 fuentes
 *  - relatedLabs / relatedCases / relatedLessons apuntan a contenido real
 *  - los ids de labs y casos son únicos
 *
 * No depende de `astro:content` (que solo existe dentro del build de
 * Astro): lee los archivos de `src/content/**` directamente para poder
 * ejecutarse como un paso de CI rápido y aislado. La validación de tipos
 * de frontmatter (Zod) la hace por separado `astro check` / `astro build`.
 */
import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import YAML from 'yaml';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const CONTENT_DIR = path.join(ROOT, 'src', 'content');

const errors = [];
const warnings = [];

function fail(message) {
  errors.push(message);
}

async function walk(dir, extensions) {
  const results = [];
  let entries;
  try {
    entries = await readdir(dir, { withFileTypes: true });
  } catch {
    return results;
  }
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...(await walk(full, extensions)));
    } else if (extensions.some((ext) => entry.name.endsWith(ext))) {
      results.push(full);
    }
  }
  return results;
}

function slugify(heading) {
  return heading
    .toLowerCase()
    .trim()
    .replace(/[`*~]/g, '')
    .replace(/[^\p{L}\p{N}\s_-]/gu, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}

function parseFrontmatter(raw) {
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/.exec(raw);
  if (!match) return { data: {}, body: '' };
  const data = YAML.parse(match[1]) ?? {};
  return { data, body: match[2] ?? '' };
}

function extractHeadingAnchors(body) {
  const anchors = new Set();
  const headingRegex = /^#{1,6}\s+(.+)$/gm;
  let m;
  while ((m = headingRegex.exec(body))) {
    anchors.add(slugify(m[1]));
  }
  return anchors;
}

/** Id de lección = ruta relativa a src/content/lessons sin extensión,
 * p.ej. "sql-avanzado/02-funciones-de-ventana". */
function lessonIdFromPath(filePath) {
  const rel = path.relative(path.join(CONTENT_DIR, 'lessons'), filePath);
  return rel.replace(/\.mdx$/, '').replace(/\\/g, '/');
}

function labIdFromPath(filePath) {
  // src/content/labs/<id>/index.mdx
  const rel = path.relative(path.join(CONTENT_DIR, 'labs'), filePath);
  return path.dirname(rel).replace(/\\/g, '/');
}

function caseIdFromPath(filePath) {
  const rel = path.relative(path.join(CONTENT_DIR, 'cases'), filePath);
  return rel.replace(/\.mdx$/, '').replace(/\\/g, '/');
}

function moduleIdFromYaml(filePath, data) {
  return data.id ?? path.basename(filePath).replace(/\.yaml$/, '');
}

async function main() {
  // --- Módulos ---------------------------------------------------------
  const moduleFiles = await walk(path.join(CONTENT_DIR, 'modules'), ['.yaml', '.yml']);
  const moduleIds = new Set();
  for (const file of moduleFiles) {
    const data = YAML.parse(await readFile(file, 'utf-8')) ?? {};
    const id = moduleIdFromYaml(file, data);
    if (moduleIds.has(id)) fail(`Módulo duplicado: "${id}" (${file})`);
    moduleIds.add(id);
  }

  // --- Lecciones ---------------------------------------------------------
  const lessonFiles = await walk(path.join(CONTENT_DIR, 'lessons'), ['.mdx']);
  const lessons = new Map(); // id -> { data, anchors }
  for (const file of lessonFiles) {
    const raw = await readFile(file, 'utf-8');
    const { data, body } = parseFrontmatter(raw);
    const id = lessonIdFromPath(file);
    if (lessons.has(id)) fail(`Lección duplicada: "${id}"`);
    lessons.set(id, { data, anchors: extractHeadingAnchors(body), file });

    if (data.module && moduleIds.size > 0 && !moduleIds.has(data.module)) {
      fail(`Lección "${id}" referencia el módulo inexistente "${data.module}"`);
    }
    if (Array.isArray(data.sources) && data.sources.length < 2) {
      fail(`Lección "${id}" tiene menos de 2 fuentes`);
    }
    if (data.level && !['básico', 'intermedio', 'avanzado'].includes(data.level)) {
      fail(`Lección "${id}": level "${data.level}" no válido (básico, intermedio o avanzado)`);
    }
    if (data.volatility && !['low', 'medium', 'high'].includes(data.volatility)) {
      fail(`Lección "${id}": volatility "${data.volatility}" no válida (low, medium o high)`);
    }
  }

  // --- Labs ---------------------------------------------------------------
  const labFiles = await walk(path.join(CONTENT_DIR, 'labs'), ['index.mdx']);
  const labIds = new Set();
  for (const file of labFiles) {
    const { data } = parseFrontmatter(await readFile(file, 'utf-8'));
    const id = labIdFromPath(file);
    if (labIds.has(id)) fail(`Lab duplicado: "${id}"`);
    labIds.add(id);
    for (const lessonId of data.relatedLessons ?? []) {
      if (lessons.size > 0 && !lessons.has(lessonId)) {
        fail(`Lab "${id}" referencia la lección inexistente "${lessonId}"`);
      }
    }
  }

  // --- Casos ---------------------------------------------------------------
  const caseFiles = await walk(path.join(CONTENT_DIR, 'cases'), ['.mdx']);
  const caseIds = new Set();
  for (const file of caseFiles) {
    const { data } = parseFrontmatter(await readFile(file, 'utf-8'));
    const id = caseIdFromPath(file);
    if (caseIds.has(id)) fail(`Caso duplicado: "${id}"`);
    caseIds.add(id);
    const stepIds = new Set();
    for (const step of data.steps ?? []) {
      if (stepIds.has(step.id)) fail(`Caso "${id}" tiene un paso con id duplicado: "${step.id}"`);
      stepIds.add(step.id);
    }
  }

  // relatedLabs / relatedCases de las lecciones
  for (const [id, { data }] of lessons) {
    for (const labId of data.relatedLabs ?? []) {
      if (labIds.size > 0 && !labIds.has(labId)) {
        fail(`Lección "${id}" referencia el lab inexistente "${labId}"`);
      }
    }
    for (const caseId of data.relatedCases ?? []) {
      if (caseIds.size > 0 && !caseIds.has(caseId)) {
        fail(`Lección "${id}" referencia el caso inexistente "${caseId}"`);
      }
    }
  }

  // --- Quizzes ---------------------------------------------------------------
  const quizFiles = await walk(path.join(CONTENT_DIR, 'quizzes'), ['.yaml', '.yml']);
  const globalQuestionIds = new Set();
  for (const file of quizFiles) {
    const data = YAML.parse(await readFile(file, 'utf-8')) ?? {};
    const lessonId = data.lesson;
    const lesson = lessons.get(lessonId);
    if (lessons.size > 0 && !lesson) {
      fail(`Quiz "${file}" apunta a la lección inexistente "${lessonId}"`);
    }
    for (const question of data.questions ?? []) {
      if (globalQuestionIds.has(question.id)) {
        fail(`Id de pregunta duplicado a nivel global: "${question.id}" (${file})`);
      }
      globalQuestionIds.add(question.id);

      if (question.ref?.startsWith('#') && lesson) {
        const anchor = question.ref.slice(1);
        if (!lesson.anchors.has(anchor)) {
          warnings.push(
            `Pregunta "${question.id}": el ancla "${question.ref}" no se encontró como encabezado en "${lessonId}" (revisa que el slug coincida).`,
          );
        }
      }
    }
  }

  // --- Resultado ---------------------------------------------------------------
  console.log(
    `Validado: ${moduleIds.size} módulos, ${lessons.size} lecciones, ${labIds.size} labs, ${caseIds.size} casos, ${globalQuestionIds.size} preguntas.`,
  );

  if (warnings.length > 0) {
    console.warn(`\n${warnings.length} aviso(s):`);
    for (const w of warnings) console.warn(`  ⚠ ${w}`);
  }

  if (errors.length > 0) {
    console.error(`\n${errors.length} error(es) de contenido:`);
    for (const e of errors) console.error(`  ✖ ${e}`);
    process.exitCode = 1;
  } else {
    console.log('\n✔ Contenido válido.');
  }
}

main();
