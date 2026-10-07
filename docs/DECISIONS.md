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
