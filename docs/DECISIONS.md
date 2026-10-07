# Decisiones de implementación

Registro de decisiones tomadas durante la construcción que no estaban (o no estaban del todo) especificadas en `PLAN.md`, siguiendo la regla de ese documento: "si algo no está especificado, elige la opción más simple y documéntala aquí".

## Fase 0 — Setup y despliegue

**2026-10-07 — TypeScript 6 en vez de 7 para `astro check`.**
Al instalar `@astrojs/check` se resolvió `typescript@7.0.2` (la reescritura en Go) por defecto, pero `astro check` todavía no lo soporta ("astro check does not currently support TypeScript 7.0"). Se fija `typescript` en `^6` explícitamente. Revisar en cada actualización mayor de Astro si ya hay soporte para TS7 y, si lo hay, actualizar.

**2026-10-07 — Hints "`z` is deprecated" en `astro check`.**
`astro check` con TS6 muestra ~20 hints (no errores ni warnings en el recuento final) de que `z` está "deprecated" en `src/content.config.ts`. Viene de los tipos de `astro:content`, que reexportan `zod/v4`; no afecta a la compilación ni al build (`0 errors`). Se ignora por ahora; revisar si una futura versión de Astro o Zod lo corrige.

**2026-10-07 — `pnpm` y los scripts de instalación (`minimumReleaseAge`).**
Este pnpm bloquea por defecto los paquetes publicados muy recientemente y los scripts `postinstall` hasta aprobarlos explícitamente. Se aprobó `esbuild` (`pnpm approve-builds --all`) porque su único script descarga el binario nativo de la plataforma; no se aprobó ningún otro paquete. Si una futura dependencia necesita scripts de instalación, revisar qué hace antes de aprobarlo.

**2026-10-07 — Node 24 LTS, no 22.**
El plan original sugería Node 22 LTS; en el momento de implementar, Node 24 ya es LTS y es la versión usada por el propio scaffold de Astro 7 en este entorno. Se fija `24` en `.nvmrc`.

**2026-10-07 — Sin `uv` disponible en el entorno de desarrollo local.**
El PLAN.md pide `uv` para Python, pero no estaba instalado en la máquina de desarrollo (sí Python 3.11 vía `python`). Se ha escrito `pyproject.toml` y los tests de `tests/labs/` asumiendo `uv` (que es lo que usa `ci.yml` vía `astral-sh/setup-uv`), pero no se han podido ejecutar `uv sync` / `uv run pytest` localmente en esta sesión. **Pendiente**: instalar `uv` en la máquina de desarrollo y verificar `pyproject.toml` localmente antes de la Fase 1 (generación del dataset).

**2026-10-07 — Página `/teoria/<modulo>/` individual pospuesta.**
`/teoria/index.astro` ya enlaza a `/teoria/<modulo-id>/`, pero la página dinámica de módulo (listado de lecciones de ese módulo) se construye en la Fase 2 junto con el layout de lección. Hasta entonces esos enlaces solo aparecerán si existen módulos en la colección (ahora mismo la colección está vacía, así que no son visitables todavía).

**2026-10-07 — `resultCompare.ts` como multiconjunto por defecto.**
Para los checks de labs SQL (`checks.yaml`, `orderMatters`), por defecto (`orderMatters: false`) se compara como multiconjunto (cada fila esperada debe emparejar con una fila real distinta, en cualquier orden) en vez de ordenar ambos lados antes de comparar. Es más robusto ante columnas de tipos mixtos y evita tener que definir un criterio de ordenación canónico para la comparación.

**2026-10-07 — Versiones de las GitHub Actions verificadas por búsqueda web, no de memoria.**
Antes del primer push se verificó con búsqueda web la versión mayor vigente de cada action usada en los workflows, porque las conocidas de memoria estaban desactualizadas:

- `actions/checkout` y `actions/setup-node`: v5 → **v6**.
- `astral-sh/setup-uv`: v7 → **v8.1.0, pinned a versión exacta**. Desde la v8.0.0 ya no publican tags flotantes `@v8`/`@v8.0` (política de seguridad de releases inmutables), así que hay que fijar el patch exacto y actualizarlo a mano cuando se quiera la siguiente versión. **Confirmado funcionando** en el run real (ver más abajo).
- `actions/upload-artifact`: v4 → **v5** (sin confirmar aún con un run que falle, único caso en que se usa).
- `withastro/action`: v4 → **v6** (sin confirmar aún con un run real, ver más abajo).
- `lycheeverse/lychee-action`: se quitó la flag `--exclude-mail` (eliminada en 2.5.0).

**2026-10-07 — `pnpm/setup@v1` falló en el primer run real; revertido a `pnpm/action-setup@v4`.**
La búsqueda web decía que `pnpm/action-setup` ya no era la action recomendada para pnpm v11+ (este proyecto usa pnpm 12) y que `pnpm/setup` era su sucesora. Se probó, se hizo push, y **el job "Web" de `ci.yml` y el job "build" de `deploy.yml` fallaron los dos en el step `Run pnpm/setup@v1`** (confirmado consultando directamente la API de GitHub — `GET /repos/.../actions/runs/{id}/jobs` — no la UI, que al leerla con un fetch no autenticado dio una lectura de "success" que resultó ser incorrecta/fantasma). No se pudieron obtener los logs exactos del step sin `gh`/token, pero la hipótesis más probable es que `pnpm/setup` no exista como action pública en ese path/tag tal y como lo describió la búsqueda.

Se revirtió a `pnpm/action-setup@v4` (sin `version` explícita: lee `packageManager` de `package.json`, que ya fija `pnpm@12.9.1`) + `actions/setup-node@v6` por separado, que es la combinación probada durante años. **Lección**: una búsqueda web puede confirmar que una action _existe_, pero solo un run real confirma que _funciona tal y como se invoca_; para algo tan crítico como el único paso de instalación de dependencias, preferir la opción establecida y de bajo riesgo sobre la "recomendada" por una fuente que no se puede verificar con una ejecución.

El job "Python" de `ci.yml` (que usa `actions/checkout@v6` y `astral-sh/setup-uv@v8.1.0`) **sí completó con éxito** en ambos runs, confirmando esas dos actualizaciones.

**2026-10-07 — `withastro/action@v6` falla de forma consistente; sustituida por build directo.**
Con `pnpm/action-setup` ya arreglado, `deploy.yml` llegó por fin al step de `withastro/action@v6` en dos commits distintos (uno antes y otro después de que el usuario habilitara GitHub Pages) y **falló los dos** (confirmado vía API, no la UI). Mientras tanto, el job "web" de `ci.yml` —que hace `pnpm build` directamente, sin esa action— pasa sin problema en ambos commits. Conclusión: el problema es de la action en sí (entrada/salida que ya no coincide con lo esperado, o incompatibilidad con Astro 7), no del resto del workflow.

Se ha quitado `withastro/action` de `deploy.yml` y se ha sustituido por los mismos tres pasos que ya funcionan en `ci.yml`: `pnpm build` directo + `actions/upload-pages-artifact@v4` + `actions/deploy-pages@v4` (sin cambios). Es más código pero cero dependencia de una action de terceros cuyo contrato no se puede verificar sin gastar un run entero cada vez. **Pendiente de confirmar con el próximo push.**

**2026-10-07 — `validate-content.mjs` no depende de `astro:content`.**
El script de validación de integridad referencial (quiz → lección, ids únicos, anclas, etc.) parsea `src/content/**` directamente con el paquete `yaml` en vez de usar `astro:content` (que solo existe dentro del runtime/build de Astro). Esto permite ejecutarlo como un paso de CI independiente y rápido. La validación de _tipos_ de frontmatter (Zod) sigue haciéndola `astro check` / `astro build` por separado.

## Fase 4 — Laboratorios

**2026-10-07 — DuckDB-WASM desde jsDelivr, vistas sobre Parquet por HTTP.**
`SqlEngine` (`src/lib/duckdb/client.ts`) carga `@duckdb/duckdb-wasm` con los bundles de jsDelivr (versión del paquete instalado) en un Worker propio, registra cada Parquet con `registerFileURL(..., HTTP)` y crea una vista por tabla (`main.<tabla>`, y `variant.<tabla>` para el test oculto). La lectura es por rangos: solo se descargan las columnas y bloques que la consulta necesita. Cancelar una consulta larga = `worker.terminate()` y recrear el motor en la siguiente (DuckDB-WASM no ofrece otra cancelación).

**2026-10-07 — ICU se precarga con `LOAD icu` (verificado en navegador real).**
En DuckDB-WASM, `icu` (zonas horarias) es una extensión que se autocarga en el primer uso y esa primera consulta fallaba (`memory access out of bounds` / `Binder Error`). Se hace `LOAD icu` + `SET TimeZone='UTC'` al arrancar (en `try/catch`: sin red, el resto funciona). Tras esto, tanto `TIMEZONE('Europe/Madrid', TIMEZONE('UTC', ts))` como `(ts AT TIME ZONE 'UTC') AT TIME ZONE 'Europe/Madrid'` funcionan desde la primera consulta. Consecuencia: el primer arranque de un lab SQL necesita internet.

**2026-10-07 — Solo lectura y una sentencia (`sqlGuard.ts`).**
El motor corre en el navegador del propio alumno, así que el riesgo es romper su sesión, no la seguridad de un servidor. Se permiten solo consultas que empiezan por SELECT/WITH/FROM/VALUES/TABLE/DESCRIBE/SUMMARIZE/SHOW/EXPLAIN, una sentencia, sin palabras como DROP/CREATE/ATTACH/COPY/SET/PRAGMA fuera de literales y comentarios (tokenizador de un solo recorrido, porque quitar `--` con regex corrompía literales como `'x; --'`).

**2026-10-07 — Corrección en el cliente: la solución se sirve como JSON, no va en el HTML.**
`/labs-data/<id>.json` (endpoint estático) contiene solución y checks (SQL) o solución y tests (Python) y se descarga solo al pulsar «Comprobar»/«Ver solución». No es secreto (es un sitio estático), solo evita que la solución esté en el HTML de la página. El test oculto (`hiddenOnVariant`) re-ejecuta alumno y solución contra `lumen_variant` cambiando `search_path`.

**2026-10-07 — Pyodide 314.0.7 en module worker; labs Python basados en funciones.**
`PyEngine` (`src/lib/pyodide/`) carga `pyodide.mjs` desde jsDelivr, instala `pandas` y `pyarrow` (+ los `packages` del lab), monta `public/py/` (datakit + `runner.py`) y los Parquet en el FS virtual. `runner.run_lab(código, tests)` ejecuta el código del alumno y los tests `test_*(ns)` (los `test_hidden_*` se marcan ocultos) y devuelve JSON. Los labs piden **funciones** (no variables globales) para que los tests ocultos puedan llamarlas con `lumen_variant` o con datos sintéticos. Timeout 20 s con reinicio del worker.

**2026-10-07 — `tests/labs/` reproduce la corrección con CPython.**
`test_sql_labs.py` (DuckDB de Python sobre los mismos Parquet; compara con semántica de `resultCompare.ts`) y `test_py_labs.py` (mismo `runner.py`/`datakit` que el navegador) comprueban para cada lab: la solución pasa, el starter no, la solución cumple sus propias aserciones de texto (ignorando comentarios), y con `hiddenOnVariant` la solución da un resultado distinto en la variante (si no, el test oculto no protegería nada). Este chequeo cazó una aserción mal diseñada (`time zone` rechazaba la forma `TIMEZONE()`).

**2026-10-07 — Los 30 módulos existen como metadatos (`scripts/gen-modules.py`).**
`/teoria/` muestra el temario completo; los módulos sin lecciones salen como «Próximamente» y no tienen página propia (solo se generan rutas de módulo con ≥ 1 lección). Esto permite que los labs referencien su módulo (`python-analisis`, `experimentacion`) antes de escribir sus lecciones. El script no sobrescribe YAMLs existentes.

**2026-10-07 — Playwright con `workers: 3`.**
Con 7+ workers, `astro preview` se atascaba y `page.goto` daba timeouts (no era un fallo de la web). Los e2e de labs descargan DuckDB/Pyodide de jsDelivr (el primer arranque de Pyodide tarda ~8 s); cada test lleva su propio timeout.
