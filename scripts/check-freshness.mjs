#!/usr/bin/env node
/**
 * Detecta contenido caducado (ver PLAN.md §3 y §8):
 *  - lecciones con `lastReviewed` > 6 meses
 *  - lecciones `volatility: high` con `lastReviewed` > 3 meses
 *  - entradas del Radar con `asOf` > 3 meses
 *
 * Pensado para ejecutarse en el workflow mensual `content-freshness.yml`,
 * que usa su salida para abrir/actualizar un issue de GitHub con `gh`.
 * Sale con código 0 siempre (no es un fallo de CI); el workflow decide qué
 * hacer con la lista.
 */
import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import YAML from 'yaml';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const CONTENT_DIR = path.join(ROOT, 'src', 'content');

const SIX_MONTHS_MS = 1000 * 60 * 60 * 24 * 30 * 6;
const THREE_MONTHS_MS = 1000 * 60 * 60 * 24 * 30 * 3;

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

function parseFrontmatter(raw) {
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/.exec(raw);
  if (!match) return {};
  return YAML.parse(match[1]) ?? {};
}

async function main() {
  const now = new Date();
  const stale = [];

  const lessonFiles = await walk(path.join(CONTENT_DIR, 'lessons'), ['.mdx']);
  for (const file of lessonFiles) {
    const data = parseFrontmatter(await readFile(file, 'utf-8'));
    if (!data.lastReviewed) continue;
    const lastReviewed = new Date(data.lastReviewed);
    const ageMs = now.getTime() - lastReviewed.getTime();
    const limit = data.volatility === 'high' ? THREE_MONTHS_MS : SIX_MONTHS_MS;
    if (ageMs > limit) {
      const rel = path.relative(ROOT, file).replace(/\\/g, '/');
      stale.push(
        `- [ ] **${data.title ?? rel}** (${rel}) — revisada por última vez ${
          data.lastReviewed
        }, volatilidad "${data.volatility ?? 'low'}"`,
      );
    }
  }

  const radarPath = path.join(CONTENT_DIR, 'radar', 'entries.yaml');
  try {
    const entries = YAML.parse(await readFile(radarPath, 'utf-8')) ?? [];
    for (const entry of entries) {
      if (!entry.asOf) continue;
      const ageMs = now.getTime() - new Date(entry.asOf).getTime();
      if (ageMs > THREE_MONTHS_MS) {
        stale.push(`- [ ] **Radar: ${entry.name}** — a fecha de ${entry.asOf}`);
      }
    }
  } catch {
    // sin radar todavía
  }

  if (stale.length === 0) {
    console.log('Sin contenido caducado detectado.');
    return;
  }

  console.log(`## Contenido a revisar (${stale.length})\n`);
  console.log(stale.join('\n'));
}

main();
