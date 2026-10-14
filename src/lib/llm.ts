/**
 * Lógica pura del playground de LLM (sin red ni DOM): construir el prompt, validar la salida,
 * reintentar con el error y calcular el coste. Es el equivalente en TypeScript de lo que se
 * practica en el módulo «LLMs para datos no estructurados».
 */

export const TEMAS = ['envio', 'pagos', 'devoluciones', 'producto', 'app', 'otro'] as const;
export const CONFIANZAS = ['alta', 'media', 'baja'] as const;

export type Tema = (typeof TEMAS)[number];

export interface Clasificacion {
  tema: Tema;
  confianza: (typeof CONFIANZAS)[number];
}

export interface Llamada {
  respuesta: string;
  tokensEntrada: number;
  tokensSalida: number;
}

/** Una función `prompt -> respuesta` (la real hace una petición; la simulada es determinista). */
export type Cliente = (prompt: string) => Promise<Llamada>;

export interface Resultado {
  texto: string;
  ok: boolean;
  clasificacion: Clasificacion | null;
  intentos: number;
  respuestas: string[];
  tokensEntrada: number;
  tokensSalida: number;
  error: string | null;
}

export const INSTRUCCION_POR_DEFECTO =
  'Clasifica el ticket de atención al cliente en uno de estos temas: ' +
  `${TEMAS.join(', ')}. Responde solo con un objeto JSON con las claves "tema" y "confianza" ` +
  '(alta, media o baja). Si ninguno encaja, usa "otro".';

export function construirPrompt(instruccion: string, texto: string): string {
  return `${instruccion}\nTicket: ${texto}`;
}

/** Aproximación de tokens: un token cada cuatro caracteres (mínimo 1). */
export function contarTokens(texto: string): number {
  return Math.max(1, Math.floor(texto.length / 4));
}

/**
 * Extrae y valida el JSON de una respuesta. Tolera vallas de código y texto alrededor; los valores se
 * comparan sin distinguir mayúsculas. Devuelve la clasificación o el motivo del fallo.
 */
export function parsearYValidar(respuesta: string): {
  datos: Clasificacion | null;
  error: string | null;
} {
  const inicio = respuesta.indexOf('{');
  const fin = respuesta.lastIndexOf('}');
  if (inicio === -1 || fin <= inicio) return { datos: null, error: 'sin_json' };
  let bruto: unknown;
  try {
    bruto = JSON.parse(respuesta.slice(inicio, fin + 1));
  } catch {
    return { datos: null, error: 'json_invalido' };
  }
  if (typeof bruto !== 'object' || bruto === null || Array.isArray(bruto)) {
    return { datos: null, error: 'no_es_objeto' };
  }
  const obj = bruto as Record<string, unknown>;
  if (!('tema' in obj) || !('confianza' in obj)) return { datos: null, error: 'faltan_claves' };
  const tema = String(obj.tema).toLowerCase();
  const confianza = String(obj.confianza).toLowerCase();
  if (!(TEMAS as readonly string[]).includes(tema)) return { datos: null, error: 'tema_invalido' };
  if (!(CONFIANZAS as readonly string[]).includes(confianza)) {
    return { datos: null, error: 'confianza_invalida' };
  }
  return {
    datos: { tema: tema as Tema, confianza: confianza as Clasificacion['confianza'] },
    error: null,
  };
}

/** Pide la clasificación, valida y reintenta (con el error en el prompt) hasta `maxReintentos` veces. */
export async function clasificarTexto(
  cliente: Cliente,
  instruccion: string,
  texto: string,
  maxReintentos = 1,
): Promise<Resultado> {
  let prompt = construirPrompt(instruccion, texto);
  const respuestas: string[] = [];
  let tokensEntrada = 0;
  let tokensSalida = 0;
  let intentos = 0;
  for (;;) {
    let llamada: Llamada;
    try {
      llamada = await cliente(prompt);
    } catch (e) {
      return {
        texto,
        ok: false,
        clasificacion: null,
        intentos: intentos + 1,
        respuestas,
        tokensEntrada,
        tokensSalida,
        error: e instanceof Error ? e.message : String(e),
      };
    }
    intentos += 1;
    respuestas.push(llamada.respuesta);
    tokensEntrada += llamada.tokensEntrada;
    tokensSalida += llamada.tokensSalida;
    const { datos, error } = parsearYValidar(llamada.respuesta);
    if (datos) {
      return {
        texto,
        ok: true,
        clasificacion: datos,
        intentos,
        respuestas,
        tokensEntrada,
        tokensSalida,
        error: null,
      };
    }
    if (intentos > maxReintentos) {
      return {
        texto,
        ok: false,
        clasificacion: null,
        intentos,
        respuestas,
        tokensEntrada,
        tokensSalida,
        error,
      };
    }
    prompt += `\nTu respuesta anterior no es válida: ${error}. Devuelve solo el JSON corregido.`;
  }
}

/** Coste en euros; los precios son € por millón de tokens. */
export function costeEur(
  tokensEntrada: number,
  tokensSalida: number,
  precioEntrada: number,
  precioSalida: number,
): number {
  return (tokensEntrada * precioEntrada + tokensSalida * precioSalida) / 1_000_000;
}

export interface Resumen {
  total: number;
  primera: number;
  trasReintento: number;
  descartadas: number;
  tokensEntrada: number;
  tokensSalida: number;
}

export function resumir(resultados: Resultado[]): Resumen {
  return {
    total: resultados.length,
    primera: resultados.filter((r) => r.ok && r.intentos === 1).length,
    trasReintento: resultados.filter((r) => r.ok && r.intentos > 1).length,
    descartadas: resultados.filter((r) => !r.ok).length,
    tokensEntrada: resultados.reduce((s, r) => s + r.tokensEntrada, 0),
    tokensSalida: resultados.reduce((s, r) => s + r.tokensSalida, 0),
  };
}

const REGLAS: [Tema, RegExp][] = [
  ['app', /\bapp\b|aplicación/i],
  ['pagos', /cobrad|tarjeta|factura|cupón|pag|importe|descuento/i],
  ['devoluciones', /devol|devuel|reembolso/i],
  ['envio', /envío|paquete|pedido lleva|transportista|almacén|entrega/i],
];

/**
 * Cliente simulado y determinista: clasifica con palabras clave y, cada tres textos, su primera
 * respuesta sale mal formada (con vallas y una coma sobrante) para que se vea la validación y el reintento.
 */
export function crearClienteSimulado(): Cliente {
  let consulta = 0;
  const vistos = new Map<string, number>();
  return async (prompt) => {
    const texto = prompt.split('\nTicket: ')[1]?.split('\nTu respuesta anterior')[0] ?? prompt;
    const veces = (vistos.get(texto) ?? 0) + 1;
    vistos.set(texto, veces);
    const tema = REGLAS.find(([, re]) => re.test(texto))?.[0] ?? 'producto';
    consulta += veces === 1 ? 1 : 0;
    const malFormada = veces === 1 && consulta % 3 === 0;
    const respuesta = malFormada
      ? `Claro, aquí tienes:\n\`\`\`json\n{"tema": "${tema}", "confianza": "alta",}\n\`\`\``
      : `{"tema": "${tema}", "confianza": "alta"}`;
    return {
      respuesta,
      tokensEntrada: contarTokens(prompt),
      tokensSalida: contarTokens(respuesta),
    };
  };
}

export type Proveedor = 'simulado' | 'anthropic' | 'openai';

export interface ConfigProveedor {
  proveedor: Proveedor;
  apiKey: string;
  modelo: string;
  baseUrl: string;
}

/** Cliente real. La clave solo vive en memoria y las peticiones salen directamente del navegador. */
export function crearClienteReal(cfg: ConfigProveedor): Cliente {
  if (cfg.proveedor === 'simulado') return crearClienteSimulado();
  return async (prompt) => {
    if (cfg.proveedor === 'anthropic') {
      const r = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'content-type': 'application/json',
          'x-api-key': cfg.apiKey,
          'anthropic-version': '2023-06-01',
          'anthropic-dangerous-direct-browser-access': 'true',
        },
        body: JSON.stringify({
          model: cfg.modelo,
          max_tokens: 300,
          messages: [{ role: 'user', content: prompt }],
        }),
      });
      if (!r.ok)
        throw new Error(`Anthropic respondió ${r.status}: ${(await r.text()).slice(0, 200)}`);
      const data = await r.json();
      const texto = (data.content ?? []).map((b: { text?: string }) => b.text ?? '').join('');
      return {
        respuesta: texto,
        tokensEntrada: data.usage?.input_tokens ?? contarTokens(prompt),
        tokensSalida: data.usage?.output_tokens ?? contarTokens(texto),
      };
    }
    const base = cfg.baseUrl.replace(/\/+$/, '');
    const r = await fetch(`${base}/chat/completions`, {
      method: 'POST',
      headers: { 'content-type': 'application/json', authorization: `Bearer ${cfg.apiKey}` },
      body: JSON.stringify({ model: cfg.modelo, messages: [{ role: 'user', content: prompt }] }),
    });
    if (!r.ok)
      throw new Error(`El servicio respondió ${r.status}: ${(await r.text()).slice(0, 200)}`);
    const data = await r.json();
    const texto = data.choices?.[0]?.message?.content ?? '';
    return {
      respuesta: texto,
      tokensEntrada: data.usage?.prompt_tokens ?? contarTokens(prompt),
      tokensSalida: data.usage?.completion_tokens ?? contarTokens(texto),
    };
  };
}
