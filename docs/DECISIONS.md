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

**2026-10-07 — `validate-content.mjs` no depende de `astro:content`.**
El script de validación de integridad referencial (quiz → lección, ids únicos, anclas, etc.) parsea `src/content/**` directamente con el paquete `yaml` en vez de usar `astro:content` (que solo existe dentro del runtime/build de Astro). Esto permite ejecutarlo como un paso de CI independiente y rápido. La validación de _tipos_ de frontmatter (Zod) sigue haciéndola `astro check` / `astro build` por separado.
