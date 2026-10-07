/**
 * Helper de rutas para GitHub Pages.
 *
 * El sitio se despliega bajo un sub-path (`/DataAnalyst_Learning_Web/`, ver
 * astro.config.mjs). Nunca escribas enlaces o assets absolutos a mano
 * (`"/teoria/..."`, `"/data/lumen.parquet"`): usa siempre este helper, que
 * resuelve la ruta relativa a `import.meta.env.BASE_URL`.
 *
 * Esto es imprescindible también para los workers de DuckDB-WASM y Pyodide,
 * que cargan archivos de `public/data` y `public/py` por URL absoluta.
 */

const BASE_URL = import.meta.env.BASE_URL ?? '/';

/**
 * Construye una URL interna respetando el `base` del despliegue.
 *
 * @example url('/teoria/sql-i/01-fundamentos/') // '/DataAnalyst_Learning_Web/teoria/sql-i/01-fundamentos/'
 * @example url('data/lumen/orders.parquet')     // '/DataAnalyst_Learning_Web/data/lumen/orders.parquet'
 */
export function url(path: string): string {
  const base = BASE_URL.endsWith('/') ? BASE_URL : `${BASE_URL}/`;
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  return `${base}${cleanPath}`;
}

/**
 * Igual que `url()`, pero devuelve una URL absoluta (con origen) usando
 * `site` de astro.config.mjs. Necesario cuando un Worker (DuckDB-WASM,
 * Pyodide) necesita una URL completa en vez de relativa al documento.
 */
export function absoluteUrl(path: string): string {
  const site = import.meta.env.SITE ?? '';
  return `${site}${url(path)}`;
}
