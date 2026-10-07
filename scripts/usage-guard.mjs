#!/usr/bin/env node
/**
 * usage-guard — vigila el uso de la ventana de 5 h de Claude Code y obliga a
 * hacer una pausa SIN gastar tokens cuando se acerca al límite.
 *
 * Fuentes de datos (en este orden):
 *  1. `statusline`: Claude Code (≥ 2.1.80) pasa `rate_limits.five_hour.used_percentage` y
 *     `resets_at` por stdin al comando `statusLine`. Es la fuente oficial y no usa credenciales.
 *     El comando `statusline` de este script guarda esos valores en un fichero de estado.
 *  2. `estimate`: si no hay estado fresco, suma los tokens del bloque de 5 h activo leyendo los
 *     transcripts locales (~/.claude/projects/**.jsonl). El porcentaje solo se conoce si has
 *     calibrado el límite (`calibrate <pct>`), porque el plan no expone su tope en local.
 *
 * Comandos:
 *   status [--json]        muestra el uso actual
 *   statusline             (statusLine) lee JSON de stdin, guarda el estado e imprime una línea
 *   hook                   (PreToolUse) deniega herramientas cuando el uso ≥ umbral
 *   wait [--threshold N]   bloquea (sin consumir tokens) hasta que se restablezca la ventana
 *   calibrate <pct>        fija el límite de tokens: pct = el % que muestra /usage ahora mismo
 *   config                 muestra la configuración
 *
 * No hace ninguna petición de red ni lee credenciales.
 */
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const WINDOW_MS = 5 * 60 * 60 * 1000;
export const DEFAULT_THRESHOLD = 95;
const STATE_MAX_AGE_MS = 20 * 60 * 1000;
const ESTIMATE_CACHE_MS = 30 * 1000;
const resetMargin = () => Number(process.env.USAGE_GUARD_MARGIN_MS ?? 30_000);

const dir = () => process.env.USAGE_GUARD_DIR ?? path.join(os.homedir(), '.claude', 'usage-guard');
const projectsDir = () =>
  process.env.USAGE_GUARD_PROJECTS ?? path.join(os.homedir(), '.claude', 'projects');
const file = (name) => path.join(dir(), name);

function readJson(p) {
  try {
    return JSON.parse(fs.readFileSync(p, 'utf-8'));
  } catch {
    return null;
  }
}

function writeJson(p, data) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, JSON.stringify(data, null, 2));
}

export function getConfig() {
  const cfg = readJson(file('config.json')) ?? {};
  return {
    threshold: Number(process.env.USAGE_GUARD_THRESHOLD ?? cfg.threshold ?? DEFAULT_THRESHOLD),
    limitTokens: Number(process.env.USAGE_GUARD_TOKEN_LIMIT ?? cfg.limitTokens ?? 0) || null,
  };
}

// ---------------------------------------------------------------- estimación local

/** Tokens "ponderados" de un mensaje: entrada + salida + creación de caché (la lectura de caché apenas cuenta). */
export function weightedTokens(usage) {
  return (
    (usage.input_tokens ?? 0) +
    (usage.output_tokens ?? 0) +
    (usage.cache_creation_input_tokens ?? 0)
  );
}

/**
 * Agrupa mensajes en bloques de 5 h (como ccusage): un bloque empieza en la hora en punto del
 * primer mensaje y dura 5 h; el primer mensaje posterior abre otro bloque.
 * @param {{ts:number,tokens:number}[]} entries ordenadas por ts
 */
export function computeBlocks(entries) {
  const blocks = [];
  for (const e of entries) {
    const last = blocks[blocks.length - 1];
    if (last && e.ts < last.start + WINDOW_MS) {
      last.tokens += e.tokens;
      last.count += 1;
    } else {
      const start = Math.floor(e.ts / 3_600_000) * 3_600_000;
      blocks.push({ start, end: start + WINDOW_MS, tokens: e.tokens, count: 1 });
    }
  }
  return blocks;
}

export function activeBlock(entries, now) {
  const blocks = computeBlocks(entries);
  const last = blocks[blocks.length - 1];
  return last && now < last.end ? last : null;
}

function* walk(root) {
  let items;
  try {
    items = fs.readdirSync(root, { withFileTypes: true });
  } catch {
    return;
  }
  for (const item of items) {
    const full = path.join(root, item.name);
    if (item.isDirectory()) yield* walk(full);
    else if (item.name.endsWith('.jsonl')) yield full;
  }
}

/** Lee los transcripts recientes y devuelve entradas {ts, tokens} deduplicadas por mensaje. */
export function scanTranscripts(now, root = projectsDir()) {
  // Se miran 2 ventanas atrás para que el encadenado de bloques parta del mismo punto de anclaje.
  const since = now - 2 * WINDOW_MS - 3_600_000;
  const byKey = new Map();
  for (const f of walk(root)) {
    let stat;
    try {
      stat = fs.statSync(f);
    } catch {
      continue;
    }
    if (stat.mtimeMs < since) continue;
    for (const line of fs.readFileSync(f, 'utf-8').split('\n')) {
      if (!line.includes('"usage"')) continue;
      let d;
      try {
        d = JSON.parse(line);
      } catch {
        continue;
      }
      const usage = d?.message?.usage;
      if (d.type !== 'assistant' || !usage || !d.timestamp) continue;
      const ts = Date.parse(d.timestamp);
      if (Number.isNaN(ts) || ts < since) continue;
      const key = `${d.message.id ?? ''}:${d.requestId ?? ''}:${f}`;
      const tokens = weightedTokens(usage);
      const prev = byKey.get(key);
      if (!prev || tokens > prev.tokens) byKey.set(key, { ts, tokens });
    }
  }
  return [...byKey.values()].sort((a, b) => a.ts - b.ts);
}

function estimate(now, cfg) {
  const cached = readJson(file('estimate-cache.json'));
  let block = cached && now - cached.at < ESTIMATE_CACHE_MS ? cached.block : undefined;
  if (block === undefined) {
    block = activeBlock(scanTranscripts(now), now);
    writeJson(file('estimate-cache.json'), { at: now, block });
  }
  if (!block)
    return { source: 'estimate', pct: 0, resetsAt: null, tokens: 0, note: 'sin bloque activo' };
  return {
    source: 'estimate',
    pct: cfg.limitTokens ? (block.tokens / cfg.limitTokens) * 100 : null,
    resetsAt: block.end,
    tokens: block.tokens,
    note: cfg.limitTokens ? undefined : 'sin calibrar: ejecuta `calibrate <pct>`',
  };
}

// ---------------------------------------------------------------- lectura de uso

/** Mejor dato disponible del uso de la ventana de 5 h. `resetsAt` en ms epoch. */
export function readUsage(now = Date.now(), cfg = getConfig()) {
  const state = readJson(file('state.json'));
  if (
    state &&
    typeof state.fiveHourPct === 'number' &&
    now - state.ts < STATE_MAX_AGE_MS &&
    (!state.fiveHourResetsAt || state.fiveHourResetsAt > now)
  ) {
    return {
      source: 'statusline',
      pct: state.fiveHourPct,
      resetsAt: state.fiveHourResetsAt ?? null,
      sevenDayPct: state.sevenDayPct ?? null,
    };
  }
  return estimate(now, cfg);
}

/** @returns {{action:'ok'|'pause'|'unknown', usage:object, threshold:number}} */
export function decide(usage, threshold) {
  if (usage.pct === null || usage.pct === undefined) return { action: 'unknown', usage, threshold };
  return { action: usage.pct >= threshold ? 'pause' : 'ok', usage, threshold };
}

// ---------------------------------------------------------------- hook (PreToolUse)

/** Herramientas que siguen permitidas durante la pausa: guardar el progreso y lanzar la espera. */
export function isAllowedDuringPause(input) {
  const tool = input?.tool_name;
  const args = input?.tool_input ?? {};
  if (tool === 'Bash' || tool === 'PowerShell') {
    const cmd = String(args.command ?? '').trim();
    return /usage-guard\.mjs/.test(cmd) || /^git\s+(add|commit|push|status|diff|log)\b/.test(cmd);
  }
  if (tool === 'Write' || tool === 'Edit') {
    return /PROGRESO\.md$/.test(String(args.file_path ?? '').replace(/\\/g, '/'));
  }
  return false;
}

export function formatTime(ms) {
  return new Date(ms).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
}

export function pauseMessage(d) {
  const reset = d.usage.resetsAt ? ` Se restablece a las ${formatTime(d.usage.resetsAt)}.` : '';
  return (
    `USAGE-GUARD: la ventana de 5 h está al ${d.usage.pct.toFixed(0)} % (umbral ${d.threshold} %).${reset} ` +
    'DETENTE: 1) si hay trabajo sin guardar, actualiza docs/PROGRESO.md y haz commit/push (siguen permitidos); ' +
    '2) lanza `node scripts/usage-guard.mjs wait` con run_in_background: true; 3) termina tu turno SIN más ' +
    'llamadas a herramientas ni texto largo. Cuando la espera termine, el sistema te avisará: entonces ' +
    'continúa desde docs/PROGRESO.md.'
  );
}

// ---------------------------------------------------------------- CLI

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function readStdin() {
  try {
    return fs.readFileSync(0, 'utf-8');
  } catch {
    return '';
  }
}

function beep() {
  if (process.platform !== 'win32') return;
  try {
    spawn(
      'powershell',
      [
        '-NoProfile',
        '-Command',
        '[console]::Beep(880,300); [console]::Beep(1175,300); [console]::Beep(1568,500)',
      ],
      { stdio: 'ignore', detached: true, windowsHide: true },
    ).unref();
  } catch {
    // sin sonido
  }
}

function describe(usage) {
  const pct = usage.pct === null || usage.pct === undefined ? '¿?' : `${usage.pct.toFixed(1)} %`;
  const reset = usage.resetsAt ? ` · se restablece a las ${formatTime(usage.resetsAt)}` : '';
  const tokens =
    usage.tokens !== undefined
      ? ` · ${usage.tokens.toLocaleString('es-ES')} tokens ponderados`
      : '';
  return `Ventana 5 h: ${pct} (fuente: ${usage.source})${reset}${tokens}${usage.note ? ` · ${usage.note}` : ''}`;
}

async function cmdWait(args) {
  const idx = args.indexOf('--threshold');
  const threshold = idx >= 0 ? Number(args[idx + 1]) : getConfig().threshold;
  const started = Date.now();
  let usage = readUsage(started);
  console.log(`[usage-guard] ${describe(usage)}. Umbral: ${threshold} %.`);
  if (usage.pct !== null && usage.pct !== undefined && usage.pct < threshold) {
    console.log(
      '[usage-guard] El uso está por debajo del umbral: no hace falta esperar. Puedes continuar.',
    );
    return;
  }
  let target = usage.resetsAt;
  if (!target) {
    // Sin hora de reinicio conocida: se asume el peor caso (5 h desde ahora) y se vuelve a mirar cada 5 min.
    target = started + WINDOW_MS;
    console.log(
      `[usage-guard] Hora de reinicio desconocida; esperaré como máximo hasta ${formatTime(target)}.`,
    );
  } else {
    console.log(
      `[usage-guard] Esperando hasta las ${formatTime(target)} (+ margen de seguridad). No consumo tokens.`,
    );
  }
  while (Date.now() < target + resetMargin()) {
    await sleep(Math.max(0, Math.min(60_000, target + resetMargin() - Date.now())));
    // Si otra sesión refresca el estado y el uso ya bajó, no hace falta seguir esperando.
    const state = readJson(file('state.json'));
    if (
      state &&
      Date.now() - state.ts < 5 * 60_000 &&
      typeof state.fiveHourPct === 'number' &&
      state.fiveHourPct < threshold - 20 &&
      state.ts > started
    ) {
      break;
    }
  }
  usage = readUsage(Date.now());
  beep();
  writeJson(file('resumed.json'), { at: Date.now() });
  console.log(`[usage-guard] RESTABLECIDO a las ${formatTime(Date.now())}. ${describe(usage)}`);
  console.log(
    '[usage-guard] Puedes continuar: lee docs/PROGRESO.md y sigue desde donde lo dejaste.',
  );
}

function cmdCalibrate(args) {
  const pct = Number(args[0]);
  if (!(pct > 0 && pct <= 100)) {
    console.error(
      'Uso: usage-guard calibrate <pct>   (pct = % de la ventana de 5 h que muestra /usage ahora mismo)',
    );
    process.exit(2);
  }
  const block = activeBlock(scanTranscripts(Date.now()), Date.now());
  if (!block) {
    console.error('No hay bloque de 5 h activo en los transcripts locales; no se puede calibrar.');
    process.exit(2);
  }
  const limitTokens = Math.round(block.tokens / (pct / 100));
  const cfg = readJson(file('config.json')) ?? {};
  writeJson(file('config.json'), { ...cfg, limitTokens });
  console.log(
    `Calibrado: ${block.tokens.toLocaleString('es-ES')} tokens = ${pct} % → límite estimado ${limitTokens.toLocaleString('es-ES')} tokens.`,
  );
  console.log(
    'Recalibra de vez en cuando (el límite real depende del plan, del modelo y de la hora).',
  );
}

async function main() {
  const [cmd, ...args] = process.argv.slice(2);
  const cfg = getConfig();

  if (cmd === 'statusline') {
    let data = {};
    try {
      data = JSON.parse(readStdin() || '{}');
    } catch {
      // stdin vacío o inválido
    }
    const five = data?.rate_limits?.five_hour;
    const seven = data?.rate_limits?.seven_day;
    if (five && typeof five.used_percentage === 'number') {
      writeJson(file('state.json'), {
        ts: Date.now(),
        fiveHourPct: five.used_percentage,
        fiveHourResetsAt: five.resets_at ? five.resets_at * 1000 : null,
        sevenDayPct: seven?.used_percentage ?? null,
        sevenDayResetsAt: seven?.resets_at ? seven.resets_at * 1000 : null,
      });
      const reset = five.resets_at ? ` ↻${formatTime(five.resets_at * 1000)}` : '';
      console.log(
        `5h ${five.used_percentage.toFixed(0)}%${reset}${seven ? ` · 7d ${seven.used_percentage.toFixed(0)}%` : ''}`,
      );
    } else {
      console.log('uso 5h: n/d');
    }
    return;
  }

  if (cmd === 'hook') {
    let input = {};
    try {
      input = JSON.parse(readStdin() || '{}');
    } catch {
      // sin entrada
    }
    const d = decide(readUsage(), cfg.threshold);
    if (d.action === 'pause' && !isAllowedDuringPause(input)) {
      process.stdout.write(
        JSON.stringify({
          hookSpecificOutput: {
            hookEventName: 'PreToolUse',
            permissionDecision: 'deny',
            permissionDecisionReason: pauseMessage(d),
          },
        }),
      );
    }
    return; // exit 0 sin salida = permitir
  }

  if (cmd === 'wait') return cmdWait(args);
  if (cmd === 'calibrate') return cmdCalibrate(args);

  if (cmd === 'config') {
    console.log(JSON.stringify({ dir: dir(), projects: projectsDir(), ...cfg }, null, 2));
    return;
  }

  if (cmd === 'status' || cmd === undefined) {
    const d = decide(readUsage(), cfg.threshold);
    if (args.includes('--json')) console.log(JSON.stringify(d));
    else
      console.log(
        `${describe(d.usage)} → ${d.action === 'pause' ? 'PAUSAR' : d.action === 'ok' ? 'seguir' : 'sin datos suficientes'}`,
      );
    process.exitCode = d.action === 'pause' ? 10 : 0;
    return;
  }

  console.error(`Comando desconocido: ${cmd}`);
  process.exit(2);
}

if (
  process.argv[1] &&
  path.resolve(process.argv[1]) === path.resolve(fileURLToPath(import.meta.url))
) {
  main().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}
