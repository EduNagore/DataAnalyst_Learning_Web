import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import * as guard from '../../scripts/usage-guard.mjs';

const H = 3_600_000;
const SCRIPT = path.resolve('scripts/usage-guard.mjs');

describe('computeBlocks / activeBlock', () => {
  it('agrupa en bloques de 5 h anclados a la hora en punto del primer mensaje', () => {
    const t0 = Date.UTC(2026, 9, 7, 6, 46);
    const blocks = guard.computeBlocks([
      { ts: t0, tokens: 100 },
      { ts: t0 + 2 * H, tokens: 50 },
      { ts: t0 + 4.5 * H, tokens: 10 }, // 11:16 < 11:00+... el bloque va de 06:00 a 11:00 → abre otro
    ]);
    expect(blocks).toHaveLength(2);
    expect(blocks[0]).toMatchObject({ start: Date.UTC(2026, 9, 7, 6), tokens: 150, count: 2 });
    expect(blocks[1].start).toBe(Date.UTC(2026, 9, 7, 11));
  });

  it('activeBlock devuelve null si el último bloque ya caducó', () => {
    const t0 = Date.UTC(2026, 9, 7, 6, 0);
    expect(guard.activeBlock([{ ts: t0, tokens: 1 }], t0 + 6 * H)).toBeNull();
    expect(guard.activeBlock([{ ts: t0, tokens: 1 }], t0 + 4 * H)).not.toBeNull();
  });
});

describe('decide', () => {
  it('pausa a partir del umbral', () => {
    expect(guard.decide({ pct: 94.9 }, 95).action).toBe('ok');
    expect(guard.decide({ pct: 95 }, 95).action).toBe('pause');
    expect(guard.decide({ pct: null }, 95).action).toBe('unknown');
  });
});

describe('isAllowedDuringPause', () => {
  it.each([
    [{ tool_name: 'Bash', tool_input: { command: 'node scripts/usage-guard.mjs wait' } }, true],
    [{ tool_name: 'Bash', tool_input: { command: 'git commit -m "x"' } }, true],
    [{ tool_name: 'Bash', tool_input: { command: 'pnpm build' } }, false],
    [{ tool_name: 'Edit', tool_input: { file_path: 'C:\\dev\\x\\docs\\PROGRESO.md' } }, true],
    [{ tool_name: 'Write', tool_input: { file_path: 'src/a.ts' } }, false],
    [{ tool_name: 'WebFetch', tool_input: {} }, false],
  ])('%j → %s', (input, expected) => {
    expect(guard.isAllowedDuringPause(input)).toBe(expected);
  });
});

describe('CLI con directorio de estado temporal', () => {
  let tmp: string;
  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'usage-guard-'));
  });
  afterEach(() => fs.rmSync(tmp, { recursive: true, force: true }));

  const run = (args: string[], input = '') =>
    spawnSync('node', [SCRIPT, ...args], {
      input,
      encoding: 'utf-8',
      env: {
        ...process.env,
        USAGE_GUARD_MARGIN_MS: '0',
        USAGE_GUARD_DIR: tmp,
        USAGE_GUARD_PROJECTS: path.join(tmp, 'sin-transcripts'),
      },
    });

  it('statusline guarda el estado y el hook deniega por encima del umbral', () => {
    const resetsAt = Math.floor(Date.now() / 1000) + 3600;
    const out = run(
      ['statusline'],
      JSON.stringify({
        rate_limits: {
          five_hour: { used_percentage: 97, resets_at: resetsAt },
          seven_day: { used_percentage: 20, resets_at: resetsAt },
        },
      }),
    );
    expect(out.stdout).toContain('5h 97%');

    const denied = run(
      ['hook'],
      JSON.stringify({ tool_name: 'Bash', tool_input: { command: 'pnpm build' } }),
    );
    const parsed = JSON.parse(denied.stdout);
    expect(parsed.hookSpecificOutput.permissionDecision).toBe('deny');
    expect(parsed.hookSpecificOutput.permissionDecisionReason).toMatch(/usage-guard\.mjs wait/);

    const allowed = run(
      ['hook'],
      JSON.stringify({
        tool_name: 'Bash',
        tool_input: { command: 'node scripts/usage-guard.mjs wait' },
      }),
    );
    expect(allowed.stdout).toBe('');
  });

  it('el hook no bloquea con el uso por debajo del umbral ni sin datos', () => {
    run(
      ['statusline'],
      JSON.stringify({
        rate_limits: {
          five_hour: { used_percentage: 40, resets_at: Math.floor(Date.now() / 1000) + 3600 },
        },
      }),
    );
    expect(
      run(['hook'], JSON.stringify({ tool_name: 'Bash', tool_input: { command: 'ls' } })).stdout,
    ).toBe('');
    fs.rmSync(path.join(tmp, 'state.json'));
    expect(
      run(['hook'], JSON.stringify({ tool_name: 'Bash', tool_input: { command: 'ls' } })).stdout,
    ).toBe('');
  });

  it('un estado cuya ventana ya se restableció se ignora (no bloquea)', () => {
    fs.writeFileSync(
      path.join(tmp, 'state.json'),
      JSON.stringify({ ts: Date.now(), fiveHourPct: 99, fiveHourResetsAt: Date.now() - 1000 }),
    );
    expect(
      run(['hook'], JSON.stringify({ tool_name: 'Bash', tool_input: { command: 'ls' } })).stdout,
    ).toBe('');
  });

  it('wait espera hasta la hora de reinicio y avisa cuando se restablece', () => {
    fs.writeFileSync(
      path.join(tmp, 'state.json'),
      JSON.stringify({ ts: Date.now(), fiveHourPct: 99, fiveHourResetsAt: Date.now() + 1500 }),
    );
    const t0 = Date.now();
    const out = run(['wait']);
    expect(out.stdout).toMatch(/RESTABLECIDO/);
    expect(Date.now() - t0).toBeGreaterThanOrEqual(1400);
    expect(Date.now() - t0).toBeLessThan(15_000);
  }, 20_000);

  it('wait no espera si el uso está por debajo del umbral', () => {
    fs.writeFileSync(
      path.join(tmp, 'state.json'),
      JSON.stringify({ ts: Date.now(), fiveHourPct: 30, fiveHourResetsAt: Date.now() + 3_600_000 }),
    );
    const t0 = Date.now();
    const out = run(['wait']);
    expect(out.stdout).toMatch(/no hace falta esperar/);
    expect(Date.now() - t0).toBeLessThan(10_000);
  }, 20_000);
});
