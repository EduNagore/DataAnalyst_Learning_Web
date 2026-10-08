/**
 * Cliente del worker de Pyodide: arranque perezoso, ejecución con timeout y
 * reinicio automático si el código del alumno no termina (bucle infinito).
 */
import { url } from '../url';
import type { InitMessage, WorkerOut } from './worker';

/** Versión de Pyodide fijada (Python 3.14). Alinear con pyproject.toml al actualizar. */
export const PYODIDE_VERSION = '314.0.7';
const INDEX_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

const DATAKIT_FILES = [
  'datakit/__init__.py',
  'datakit/data.py',
  'datakit/testing.py',
  'datakit/stats.py',
  'datakit/llm.py',
  'runner.py',
];

export interface PyTestResult {
  name: string;
  passed: boolean;
  message: string;
  hidden: boolean;
}
export interface PyRunResult {
  stdout: string;
  error: string | null;
  tests: PyTestResult[];
}

export class PyTimeoutError extends Error {
  constructor(public readonly timeoutMs: number) {
    super(
      `El código superó el límite de ${Math.round(timeoutMs / 1000)} s y se detuvo (¿bucle infinito?).`,
    );
  }
}

export interface PyEngineOptions {
  /** Paquetes de Pyodide además de pandas y pyarrow. */
  packages: string[];
  /** Tablas de `lumen/` (y `lumen_variant/` si hace falta) que se montan en /data. */
  tables: string[];
  withVariant?: boolean;
  extras?: string[];
  raws?: string[];
  onStatus?: (text: string) => void;
}

export class PyEngine {
  private worker: Worker | null = null;
  private ready: Promise<void> | null = null;
  private nextId = 1;
  private pending = new Map<number, { resolve: (v: string) => void; reject: (e: Error) => void }>();

  constructor(private readonly options: PyEngineOptions) {}

  start(): Promise<void> {
    if (this.ready) return this.ready;
    this.ready = new Promise<void>((resolve, reject) => {
      const worker = new Worker(new URL('./worker.ts', import.meta.url), { type: 'module' });
      this.worker = worker;
      worker.onmessage = (event: MessageEvent<WorkerOut>) => {
        const m = event.data;
        if (m.type === 'status') this.options.onStatus?.(m.text);
        else if (m.type === 'ready') resolve();
        else if (m.type === 'result') {
          this.pending.get(m.id)?.resolve(m.payload);
          this.pending.delete(m.id);
        } else if (m.type === 'error') {
          if (m.id !== undefined) {
            this.pending.get(m.id)?.reject(new Error(m.message));
            this.pending.delete(m.id);
          } else reject(new Error(m.message));
        }
      };
      worker.onerror = (e) => reject(new Error(e.message || 'Error en el worker de Python'));

      const dataFiles: InitMessage['dataFiles'] = [
        ...this.options.tables.map((t) => ({
          path: `/data/lumen/${t}.parquet`,
          url: new URL(url(`/data/lumen/${t}.parquet`), location.origin).href,
        })),
        ...(this.options.withVariant
          ? this.options.tables.map((t) => ({
              path: `/data/lumen_variant/${t}.parquet`,
              url: new URL(url(`/data/lumen_variant/${t}.parquet`), location.origin).href,
            }))
          : []),
        ...(this.options.extras ?? []).map((e) => ({
          path: `/data/extra/${e}.csv`,
          url: new URL(url(`/data/extra/${e}.csv`), location.origin).href,
        })),
        ...(this.options.raws ?? []).map((r) => ({
          path: `/data/lumen_raw/${r}.csv`,
          url: new URL(url(`/data/lumen_raw/${r}.csv`), location.origin).href,
        })),
      ];
      const init: InitMessage = {
        type: 'init',
        indexURL: INDEX_URL,
        packages: ['pandas', 'pyarrow', ...this.options.packages],
        textFiles: DATAKIT_FILES.map((f) => ({
          path: `/py/${f}`,
          url: new URL(url(`/py/${f}`), location.origin).href,
        })),
        dataFiles,
      };
      worker.postMessage(init);
    });
    this.ready.catch(() => this.terminate());
    return this.ready;
  }

  async run(code: string, tests = '', timeoutMs = 20_000): Promise<PyRunResult> {
    await this.start();
    const id = this.nextId++;
    const promise = new Promise<string>((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.worker!.postMessage({ type: 'run', id, code, tests });
    });
    let timer: ReturnType<typeof setTimeout> | undefined;
    const timeout = new Promise<never>((_, reject) => {
      timer = setTimeout(() => reject(new PyTimeoutError(timeoutMs)), timeoutMs);
    });
    try {
      return JSON.parse(await Promise.race([promise, timeout])) as PyRunResult;
    } catch (err) {
      if (err instanceof PyTimeoutError) this.terminate();
      throw err;
    } finally {
      clearTimeout(timer);
    }
  }

  terminate(): void {
    this.worker?.terminate();
    this.worker = null;
    this.ready = null;
    for (const p of this.pending.values()) p.reject(new Error('Motor Python reiniciado'));
    this.pending.clear();
  }
}
