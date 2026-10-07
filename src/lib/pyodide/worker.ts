/// <reference lib="webworker" />
/**
 * Worker de Pyodide (módulo): carga el intérprete, instala paquetes, monta
 * `datakit` y los datos, y ejecuta código + tests de un lab. Se crea solo al
 * abrir un lab Python (ver PLAN.md §7.4); si excede el timeout, el cliente lo
 * termina y lo recrea.
 */
export interface InitMessage {
  type: 'init';
  indexURL: string;
  packages: string[];
  /** Ficheros de texto para el FS virtual (datakit + runner). */
  textFiles: { path: string; url: string }[];
  /** Ficheros binarios de datos (Parquet/CSV) para el FS virtual. */
  dataFiles: { path: string; url: string }[];
}
export interface RunMessage {
  type: 'run';
  id: number;
  code: string;
  tests: string;
}
export type WorkerOut =
  | { type: 'status'; text: string }
  | { type: 'ready' }
  | { type: 'result'; id: number; payload: string }
  | { type: 'error'; id?: number; message: string };

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let pyodide: any = null;

function post(message: WorkerOut) {
  (self as unknown as Worker).postMessage(message);
}

async function init(msg: InitMessage) {
  post({ type: 'status', text: 'Descargando Python…' });
  const mod = await import(/* @vite-ignore */ `${msg.indexURL}pyodide.mjs`);
  pyodide = await mod.loadPyodide({ indexURL: msg.indexURL });

  post({ type: 'status', text: 'Instalando paquetes (pandas, pyarrow…)' });
  await pyodide.loadPackage(msg.packages);

  post({ type: 'status', text: 'Cargando datos…' });
  const writeBytes = async (path: string, url: string, text: boolean) => {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`No se pudo descargar ${url} (${response.status})`);
    const dir = path.slice(0, path.lastIndexOf('/'));
    pyodide.FS.mkdirTree(dir);
    if (text) pyodide.FS.writeFile(path, await response.text());
    else pyodide.FS.writeFile(path, new Uint8Array(await response.arrayBuffer()));
  };
  await Promise.all([
    ...msg.textFiles.map((f) => writeBytes(f.path, f.url, true)),
    ...msg.dataFiles.map((f) => writeBytes(f.path, f.url, false)),
  ]);
  pyodide.runPython(`import sys\nif '/py' not in sys.path:\n    sys.path.insert(0, '/py')`);
  post({ type: 'ready' });
}

async function run(msg: RunMessage) {
  pyodide.globals.set('_student_code', msg.code);
  pyodide.globals.set('_test_code', msg.tests);
  const payload = pyodide.runPython(
    `import runner\nrunner.run_lab(_student_code, _test_code)`,
  ) as string;
  post({ type: 'result', id: msg.id, payload });
}

self.onmessage = async (event: MessageEvent<InitMessage | RunMessage>) => {
  try {
    if (event.data.type === 'init') await init(event.data);
    else await run(event.data);
  } catch (err) {
    post({
      type: 'error',
      id: event.data.type === 'run' ? event.data.id : undefined,
      message: err instanceof Error ? err.message : String(err),
    });
  }
};
