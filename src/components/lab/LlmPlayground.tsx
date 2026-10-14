import { useMemo, useRef, useState } from 'react';
import {
  INSTRUCCION_POR_DEFECTO,
  clasificarTexto,
  costeEur,
  crearClienteReal,
  resumir,
  type Proveedor,
  type Resultado,
} from '../../lib/llm';

interface Props {
  tickets: string[];
}

const input =
  'w-full rounded-md border border-[var(--color-border)] bg-[var(--color-bg-raised)] px-2 py-1.5 text-sm text-[var(--color-text)]';
const btn =
  'rounded-md border border-[var(--color-border)] bg-[var(--color-bg-raised)] px-3 py-1.5 text-sm text-[var(--color-text)] hover:border-[var(--color-accent)] disabled:opacity-50';

const MODELO_POR_DEFECTO: Record<Proveedor, string> = {
  simulado: 'simulado',
  anthropic: '',
  openai: '',
};

export default function LlmPlayground({ tickets }: Props) {
  const [proveedor, setProveedor] = useState<Proveedor>('simulado');
  const [apiKey, setApiKey] = useState('');
  const [modelo, setModelo] = useState('');
  const [baseUrl, setBaseUrl] = useState('https://api.openai.com/v1');
  const [instruccion, setInstruccion] = useState(INSTRUCCION_POR_DEFECTO);
  const [reintentos, setReintentos] = useState(1);
  const [precioIn, setPrecioIn] = useState('3');
  const [precioOut, setPrecioOut] = useState('15');
  const [seleccion, setSeleccion] = useState<boolean[]>(() => tickets.map((_, i) => i < 6));
  const [extra, setExtra] = useState('');
  const [resultados, setResultados] = useState<Resultado[]>([]);
  const [ejecutando, setEjecutando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const cancelar = useRef(false);

  const real = proveedor !== 'simulado';
  const textos = useMemo(() => {
    const base = tickets.filter((_, i) => seleccion[i]);
    const propio = extra
      .split('\n')
      .map((l) => l.trim())
      .filter(Boolean);
    return [...base, ...propio];
  }, [tickets, seleccion, extra]);

  const resumen = useMemo(() => resumir(resultados), [resultados]);
  const coste = costeEur(
    resumen.tokensEntrada,
    resumen.tokensSalida,
    Number(precioIn) || 0,
    Number(precioOut) || 0,
  );

  async function ejecutar() {
    setError(null);
    if (real && (!apiKey.trim() || !modelo.trim())) {
      setError('Introduce la clave de API y el nombre del modelo, o usa el modelo simulado.');
      return;
    }
    if (textos.length === 0) {
      setError('Selecciona al menos un ticket.');
      return;
    }
    cancelar.current = false;
    setEjecutando(true);
    setResultados([]);
    const cliente = crearClienteReal({
      proveedor,
      apiKey: apiKey.trim(),
      modelo: modelo.trim() || MODELO_POR_DEFECTO[proveedor],
      baseUrl,
    });
    const acumulado: Resultado[] = [];
    for (const texto of textos) {
      if (cancelar.current) break;
      const r = await clasificarTexto(cliente, instruccion, texto, reintentos);
      acumulado.push(r);
      setResultados([...acumulado]);
    }
    setEjecutando(false);
  }

  return (
    <div className="space-y-6">
      <div
        className="rounded-lg border-l-4 border-[var(--color-warning)] bg-[var(--color-bg-subtle)] p-4 text-sm text-[var(--color-text)]"
        role="note"
      >
        <p className="font-semibold">Antes de usar un modelo real</p>
        <ul className="mt-1 list-disc space-y-1 pl-5 text-[var(--color-text-muted)]">
          <li>
            La clave se queda <strong>solo en la memoria de esta pestaña</strong>; no se guarda ni
            se envía a este sitio. Las peticiones salen directamente de tu navegador al proveedor.
          </li>
          <li>
            Cualquier script de la página podría leerla: usa una clave{' '}
            <strong>restringida y con límite de gasto</strong> y bórrala después.
          </li>
          <li>
            Los textos que envíes salen del navegador hacia el proveedor:{' '}
            <strong>no escribas datos personales ni confidenciales</strong>. Los tickets de ejemplo
            son sintéticos.
          </li>
          <li>
            Algunos proveedores bloquean las peticiones desde navegadores (CORS): si falla, es una
            limitación del proveedor, no del ejercicio. El modelo simulado funciona sin red.
          </li>
        </ul>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <label className="block text-sm text-[var(--color-text)]">
          Proveedor
          <select
            className={`${input} mt-1`}
            value={proveedor}
            onChange={(e) => {
              setProveedor(e.target.value as Proveedor);
              setResultados([]);
            }}
          >
            <option value="simulado">Modelo simulado (sin red ni clave)</option>
            <option value="anthropic">Anthropic (API de Mensajes)</option>
            <option value="openai">Compatible con OpenAI (chat/completions)</option>
          </select>
        </label>
        {real && (
          <>
            <label className="block text-sm text-[var(--color-text)]">
              Clave de API
              <input
                className={`${input} mt-1`}
                type="password"
                autoComplete="off"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
              />
            </label>
            <label className="block text-sm text-[var(--color-text)]">
              Modelo (copia el nombre exacto de la documentación del proveedor)
              <input
                className={`${input} mt-1`}
                value={modelo}
                onChange={(e) => setModelo(e.target.value)}
              />
            </label>
            {proveedor === 'openai' && (
              <label className="block text-sm text-[var(--color-text)]">
                URL base
                <input
                  className={`${input} mt-1`}
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                />
              </label>
            )}
          </>
        )}
        <label className="block text-sm text-[var(--color-text)]">
          Reintentos con el error en el prompt
          <select
            className={`${input} mt-1`}
            value={reintentos}
            onChange={(e) => setReintentos(Number(e.target.value))}
          >
            <option value={0}>0 (descartar al primer fallo)</option>
            <option value={1}>1</option>
            <option value={2}>2</option>
          </select>
        </label>
        <div className="grid grid-cols-2 gap-3">
          <label className="block text-sm text-[var(--color-text)]">
            € por millón de tokens de entrada
            <input
              className={`${input} mt-1`}
              inputMode="decimal"
              value={precioIn}
              onChange={(e) => setPrecioIn(e.target.value)}
            />
          </label>
          <label className="block text-sm text-[var(--color-text)]">
            € por millón de tokens de salida
            <input
              className={`${input} mt-1`}
              inputMode="decimal"
              value={precioOut}
              onChange={(e) => setPrecioOut(e.target.value)}
            />
          </label>
        </div>
      </div>

      <label className="block text-sm text-[var(--color-text)]">
        Instrucción (se añade «Ticket: …» al final)
        <textarea
          className={`${input} mt-1 min-h-[6rem] font-mono`}
          value={instruccion}
          onChange={(e) => setInstruccion(e.target.value)}
        />
      </label>

      <fieldset>
        <legend className="text-sm font-medium text-[var(--color-text)]">
          Tickets de ejemplo (sintéticos)
        </legend>
        <div className="mt-2 grid gap-1 sm:grid-cols-2">
          {tickets.map((t, i) => (
            <label key={t} className="flex items-start gap-2 text-sm text-[var(--color-text)]">
              <input
                type="checkbox"
                className="mt-1"
                checked={seleccion[i]}
                onChange={(e) =>
                  setSeleccion(seleccion.map((v, j) => (j === i ? e.target.checked : v)))
                }
              />
              <span>{t}</span>
            </label>
          ))}
        </div>
        <label className="mt-3 block text-sm text-[var(--color-text)]">
          Tus propios textos de prueba (uno por línea; no pongas datos personales)
          <textarea
            className={`${input} mt-1 min-h-[4rem]`}
            value={extra}
            onChange={(e) => setExtra(e.target.value)}
          />
        </label>
      </fieldset>

      <div className="flex flex-wrap items-center gap-3">
        <button type="button" className={btn} onClick={ejecutar} disabled={ejecutando}>
          {ejecutando ? 'Clasificando…' : `Clasificar ${textos.length} textos`}
        </button>
        {ejecutando && (
          <button type="button" className={btn} onClick={() => (cancelar.current = true)}>
            Detener
          </button>
        )}
        {error && (
          <p role="alert" className="text-sm text-[var(--color-danger)]">
            {error}
          </p>
        )}
      </div>

      {resultados.length > 0 && (
        <div aria-live="polite">
          <h2 className="text-lg font-semibold text-[var(--color-text)]">Resultado</h2>
          <p className="mt-1 text-sm text-[var(--color-text-muted)]">
            {resumen.total} textos · válidas a la primera: {resumen.primera} · tras reintento:{' '}
            {resumen.trasReintento} · descartadas: {resumen.descartadas} · tokens:{' '}
            {resumen.tokensEntrada} entrada + {resumen.tokensSalida} salida · coste estimado:{' '}
            {coste.toFixed(6)} €{!real && ' (modelo simulado: cifras ficticias)'}
          </p>
          <div className="mt-3 overflow-x-auto">
            <table className="w-full text-left text-sm">
              <caption className="sr-only">Clasificación de cada texto</caption>
              <thead>
                <tr className="border-b border-[var(--color-border)] text-[var(--color-text-muted)]">
                  <th scope="col" className="py-1 pr-3 font-medium">
                    Texto
                  </th>
                  <th scope="col" className="py-1 pr-3 font-medium">
                    Tema
                  </th>
                  <th scope="col" className="py-1 pr-3 font-medium">
                    Confianza
                  </th>
                  <th scope="col" className="py-1 pr-3 font-medium">
                    Intentos
                  </th>
                  <th scope="col" className="py-1 font-medium">
                    Estado
                  </th>
                </tr>
              </thead>
              <tbody>
                {resultados.map((r, i) => (
                  <tr
                    key={`${r.texto}-${i}`}
                    className="border-b border-[var(--color-border)] align-top"
                  >
                    <td className="py-1 pr-3 text-[var(--color-text)]">
                      {r.texto}
                      <details className="mt-1 text-xs text-[var(--color-text-muted)]">
                        <summary className="cursor-pointer">Respuestas del modelo</summary>
                        {r.respuestas.map((x, k) => (
                          <pre key={k} className="mt-1 whitespace-pre-wrap">
                            {x}
                          </pre>
                        ))}
                      </details>
                    </td>
                    <td className="py-1 pr-3 text-[var(--color-text)]">
                      {r.clasificacion?.tema ?? '—'}
                    </td>
                    <td className="py-1 pr-3 text-[var(--color-text)]">
                      {r.clasificacion?.confianza ?? '—'}
                    </td>
                    <td className="py-1 pr-3 text-[var(--color-text)]">{r.intentos}</td>
                    <td className="py-1 text-[var(--color-text)]">
                      {r.ok
                        ? r.intentos > 1
                          ? 'válida tras reintento'
                          : 'válida'
                        : `descartada: ${r.error}`}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
