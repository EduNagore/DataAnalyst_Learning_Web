import { describe, expect, it } from 'vitest';
import { url } from '../../src/lib/url';

// BASE_URL en el entorno de test de Vitest no es el de producción
// (astro.config.mjs solo aplica en el build de Astro), así que probamos el
// contrato del helper -no un valor de base concreto- y lo volvemos a
// comprobar en e2e contra el sitio ya construido con su base real.
describe('url()', () => {
  const base = import.meta.env.BASE_URL ?? '/';
  const normalizedBase = base.endsWith('/') ? base : `${base}/`;

  it('antepone la base al path', () => {
    expect(url('/teoria/')).toBe(`${normalizedBase}teoria/`);
  });

  it('quita la barra inicial del path antes de unirlo a la base', () => {
    expect(url('teoria/')).toBe(url('/teoria/'));
  });

  it('funciona con rutas de archivos de datos sin barra inicial', () => {
    expect(url('data/lumen/orders.parquet')).toBe(`${normalizedBase}data/lumen/orders.parquet`);
  });

  it('no duplica barras entre base y path', () => {
    expect(url('/')).not.toMatch(/\/\//);
  });
});
