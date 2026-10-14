import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  INSTRUCCION_POR_DEFECTO,
  clasificarTexto,
  contarTokens,
  costeEur,
  crearClienteReal,
  crearClienteSimulado,
  parsearYValidar,
  resumir,
} from '../../src/lib/llm';

describe('parsearYValidar', () => {
  it('acepta JSON limpio, con vallas y texto alrededor, y normaliza mayúsculas', () => {
    expect(parsearYValidar('{"tema":"pagos","confianza":"alta"}').datos).toEqual({
      tema: 'pagos',
      confianza: 'alta',
    });
    const r = parsearYValidar('Aquí:\n```json\n{"tema": "Envio", "confianza": "MEDIA"}\n```');
    expect(r.datos).toEqual({ tema: 'envio', confianza: 'media' });
  });

  it('detecta cada tipo de fallo', () => {
    expect(parsearYValidar('no sé').error).toBe('sin_json');
    expect(parsearYValidar('{"tema": "app",}').error).toBe('json_invalido');
    expect(parsearYValidar('{"tema": "app"}').error).toBe('faltan_claves');
    expect(parsearYValidar('{"tema": "facturacion", "confianza": "alta"}').error).toBe(
      'tema_invalido',
    );
    expect(parsearYValidar('{"tema": "app", "confianza": "mucha"}').error).toBe(
      'confianza_invalida',
    );
    expect(parsearYValidar('[1, 2]').error).toBe('sin_json');
  });
});

describe('clasificarTexto', () => {
  it('reintenta con el error en el prompt y suma los tokens de todas las llamadas', async () => {
    const prompts: string[] = [];
    const respuestas = ['basura', '{"tema":"envio","confianza":"media"}'];
    const r = await clasificarTexto(
      async (p) => {
        prompts.push(p);
        return { respuesta: respuestas.shift() ?? '', tokensEntrada: 100, tokensSalida: 10 };
      },
      INSTRUCCION_POR_DEFECTO,
      'Mi pedido no llega',
      1,
    );
    expect(r.ok).toBe(true);
    expect(r.intentos).toBe(2);
    expect(r.tokensEntrada).toBe(200);
    expect(r.tokensSalida).toBe(20);
    expect(prompts[1]).toContain('Tu respuesta anterior no es válida: sin_json');
  });

  it('descarta con el motivo cuando se agotan los reintentos y captura los errores de red', async () => {
    const mal = await clasificarTexto(
      async () => ({ respuesta: 'basura', tokensEntrada: 5, tokensSalida: 1 }),
      INSTRUCCION_POR_DEFECTO,
      'x',
      0,
    );
    expect(mal.ok).toBe(false);
    expect(mal.intentos).toBe(1);
    expect(mal.error).toBe('sin_json');
    const red = await clasificarTexto(
      async () => {
        throw new Error('401');
      },
      INSTRUCCION_POR_DEFECTO,
      'x',
    );
    expect(red.ok).toBe(false);
    expect(red.error).toBe('401');
  });
});

describe('cliente simulado, coste y resumen', () => {
  it('clasifica con palabras clave y falla la primera respuesta de cada tercer texto', async () => {
    const cliente = crearClienteSimulado();
    const textos = [
      'La app me ha cobrado dos veces el mismo pedido.',
      'Mi pedido lleva 8 días de retraso y no tengo ninguna noticia del transportista.',
      'He devuelto el artículo pero el estado sigue como pendiente.',
    ];
    const rs = [];
    for (const t of textos) rs.push(await clasificarTexto(cliente, INSTRUCCION_POR_DEFECTO, t, 1));
    expect(rs.map((r) => r.clasificacion?.tema)).toEqual(['app', 'envio', 'devoluciones']);
    expect(rs.map((r) => r.intentos)).toEqual([1, 1, 2]);
    const s = resumir(rs);
    expect(s).toMatchObject({ total: 3, primera: 2, trasReintento: 1, descartadas: 0 });
  });

  it('calcula tokens aproximados y coste por millón de tokens', () => {
    expect(contarTokens('abcdefgh')).toBe(2);
    expect(contarTokens('')).toBe(1);
    expect(costeEur(1_000_000, 500_000, 3, 15)).toBeCloseTo(10.5);
  });
});

describe('clientes reales (con fetch simulado)', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('Anthropic: cabeceras, cuerpo y uso de tokens', async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        content: [{ type: 'text', text: '{"tema":"app","confianza":"alta"}' }],
        usage: { input_tokens: 42, output_tokens: 9 },
      }),
    }));
    vi.stubGlobal('fetch', fetchMock);
    const cliente = crearClienteReal({
      proveedor: 'anthropic',
      apiKey: 'k',
      modelo: 'm',
      baseUrl: '',
    });
    const r = await cliente('hola');
    expect(r).toEqual({
      respuesta: '{"tema":"app","confianza":"alta"}',
      tokensEntrada: 42,
      tokensSalida: 9,
    });
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe('https://api.anthropic.com/v1/messages');
    const headers = init.headers as Record<string, string>;
    expect(headers['x-api-key']).toBe('k');
    expect(headers['anthropic-dangerous-direct-browser-access']).toBe('true');
    expect(JSON.parse(init.body as string)).toMatchObject({
      model: 'm',
      messages: [{ role: 'user', content: 'hola' }],
    });
  });

  it('compatible con OpenAI: URL base sin barra final y errores HTTP', async () => {
    const ok = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        choices: [{ message: { content: '{"tema":"envio","confianza":"baja"}' } }],
        usage: { prompt_tokens: 10, completion_tokens: 5 },
      }),
    }));
    vi.stubGlobal('fetch', ok);
    const cliente = crearClienteReal({
      proveedor: 'openai',
      apiKey: 'k',
      modelo: 'm',
      baseUrl: 'https://x.test/v1/',
    });
    expect((await cliente('hola')).tokensSalida).toBe(5);
    expect((ok.mock.calls[0] as unknown as [string])[0]).toBe('https://x.test/v1/chat/completions');
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => ({ ok: false, status: 401, text: async () => 'no autorizado' })),
    );
    await expect(cliente('hola')).rejects.toThrow('401');
  });
});
