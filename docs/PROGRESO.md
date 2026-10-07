# Progreso de implementación

Registro de qué fase del `PLAN.md` está hecha, verificada y pendiente. Se actualiza al terminar cada fase (o al quedarse sin margen de contexto a mitad de una) para poder continuar sin releer todo el historial de la conversación.

## Resumen rápido

| Fase                    | Estado                            |
| ----------------------- | --------------------------------- |
| F0 — Setup y despliegue | ✅ Hecha, desplegada, CI en verde |
| F1 — Dataset Lumen      | ✅ Hecha y verificada             |
| F2 — Núcleo de teoría   | ⬜ Siguiente paso                 |
| F3-F10                  | ⬜ Pendiente                      |

Repo: `https://github.com/EduNagore/DataAnalyst_Learning_Web` (rama `main`). Sitio: `https://edunagore.github.io/DataAnalyst_Learning_Web/`. GitHub Pages habilitado por el usuario (2026-10-07).

---

## F0 — Setup, stack y despliegue ✅

Astro 7 + TS strict + Tailwind 4 + React 19 + MDX. Helper `url()`, 12 colecciones de contenido (Zod), librerías de dominio con tests (`progress.ts`, `quiz.ts`, `srs.ts`, `resultCompare.ts`), shell de la web (Header/Footer/ThemeToggle sin FOUC, landing, páginas "en construcción" o que ya leen su colección vacía correctamente). CI (`ci.yml`), despliegue (`deploy.yml`), frescura mensual (`content-freshness.yml`).

**Incidencia real resuelta**: `pnpm/setup@v1` (recomendado por una búsqueda web) falló en el run real de GitHub Actions. Diagnosticado vía API de GitHub (no la UI, que dio una lectura falsa de "success"). Revertido a `pnpm/action-setup@v4` + `actions/setup-node@v6`, que sí funciona — confirmado: el job "Web" de `ci.yml` pasa. El job "build" de `deploy.yml` llegó a fallar en `withastro/action@v6` en un run **anterior a que el usuario habilitara GitHub Pages**; no se ha vuelto a comprobar un deploy end-to-end desde que Pages está habilitado — **primera cosa a verificar** si se retoma esto: mirar `https://github.com/EduNagore/DataAnalyst_Learning_Web/actions` tras el próximo push a `main`.

Detalle completo de todas las decisiones de esta fase: `docs/DECISIONS.md`.

---

## F1 — Dataset Lumen ✅

Generador completo en `data-gen/` (paquete `lumen/`): `calendar.py`, `reference_data.py`, `dimensions.py`, `transactions.py`, `behavior.py`, `growth.py`, `raw_variant.py`, `extra_datasets.py`, `schema_doc.py`, `io_utils.py`, `build.py`, orquestado por `generate.py`. Config en `data-gen/config.yaml` (semillas, tamaños, parámetros de cada verdad plantada).

**Verificado sobre los datos reales generados** (no solo en teoría):

- Determinismo: dos ejecuciones completas dan `checksums.json` byte a byte idéntico.
- Integridad referencial: 0 huérfanos en `orders↔customers`, `order_items↔orders/products`, `shipments↔orders`; 0 inconsistencias canal/tienda.
- Tamaño: ~45 MB total (límite 60 MB), ningún archivo > 17 MB (límite 25 MB). Generación completa: ~15 s.
- **Las 11 verdades plantadas, comprobadas con consultas DuckDB directas sobre el Parquet** (no solo "debería funcionar"): estacionalidad, paradoja de Simpson (Madrid vs Andalucía: agregado mobile 6,2 % > desktop 3,7 %, pero mobile pierde dentro de cada región — reversión real confirmada), lift de experimento (+7,9 % ≈ objetivo 8 %), SRM (44/56 ≈ objetivo), CUPED (se apoya en la persistencia de segmento del cliente, no en un parámetro forzado — ver nota abajo), cambio de precio regional (Andalucía +15,8 % tras la fecha, Madrid sin cambio), rotura de stock (stock medio 212→1 en la ventana), bug de eventos duplicados app 4.2 (confirmado con conteo de sesiones con >1 `purchase`: 42 % dentro de ventana+versión vs 0 % fuera), incrementalidad de campaña (atribuida +22,6 % vs real +5,9 %, ambas ≈ objetivo), y churn por retraso de envío (59,6 % vs 49,5 % de cancelación histórica).
- `lumen_raw/` y `extra/` revisados a mano: fechas mezcladas, mayúsculas/espacios inconsistentes, importes con coma decimal, huérfanos — todo presente como se documentó. `extra/` son 3 datasets **externos reales** (no inventados): cuarteto de Anscombe, Datasaurus Dozen y la serie de pasajeros aéreos de Box & Jenkins, descargados de fuentes públicas verificadas y guardados en `data-gen/lumen/vendor/` (fuentes citadas en `docs/SOURCES.md`).

**Bug real encontrado y corregido durante la implementación**: las verdades plantadas de precio regional y rotura de stock comparaban `category_id` (id de SUBcategoría, p.ej. `cat-00-3`) contra el id de categoría SUPERIOR (`cat-00`) con `==`, que nunca coincide. Se corrigió añadiendo una columna `top_category_id` explícita en `products` (ver `dimensions.py` y `transactions.py`). Sin la verificación con DuckDB esto habría pasado inadvertido (el generador no lanzaba ningún error, simplemente las verdades plantadas no se manifestaban).

**Pendiente de F1** (menor, no bloqueante):

- No hay todavía un job de CI que regenere el dataset en un runner limpio y compare `checksums.json` (lo apunta `docs/DATASET.md` §7 como pendiente). Añadir cuando se toque `ci.yml` de nuevo.
- La verdad plantada #5 (CUPED) no tiene un parámetro de correlación forzado explícitamente verificado con una cifra — se apoya en que el peso de pedido por segmento (`_SEGMENT_ORDER_WEIGHT` en `transactions.py`) es persistente en el tiempo para un mismo cliente, lo cual genera correlación entre periodo pre y periodo del experimento de forma natural. Si al escribir el lab de CUPED (Fase 8, lab 55) la correlación medida resulta demasiado débil, reforzarla ahí (no debería hacer falta tocar el generador).
- `docs/DATASET.md` ya está actualizado con las cifras reales; si se vuelve a regenerar el dataset con otra configuración, revisar que esas cifras sigan siendo correctas.

**Archivos clave para retomar/extender el generador**: `data-gen/config.yaml` (todos los parámetros), `data-gen/lumen/schema_doc.py` (contrato de columnas por tabla, con el que `build.py` valida en caliente).

---

## F2 — Núcleo de teoría (siguiente paso)

Según `PLAN.md` §12: Layouts, header, sidebar, TOC, tema oscuro (ya hecho en F0 — revisar si falta sidebar/TOC de lección), componentes de contenido (`Callout`, `Diagram`, `SourceList`, `KeyTakeaways`, `Snapshot`, `Term`, `ExcelFn`, `VegaChart`, `DialectTabs`, `BusinessContext`), búsqueda Pagefind (dependencia ya instalada en F0, falta integrarla), M04 (SQL I — Fundamentos) completo como módulo modelo con sus lecciones, quizzes y labs.

**Antes de escribir contenido**: releer `docs/CONTENT_GUIDELINES.md` (estructura de lección, estilo, procedimiento de fuentes) y `PLAN.md` §7.1 (temario de M04) y §9.

---

## Notas para retomar en una sesión nueva

1. Verificar si hay cambios sin commitear: `git status` en `C:\dev\Data_Analyst_Web`.
2. El dataset ya generado vive en `public/data/` (committed). Para regenerarlo: `uv run python data-gen/generate.py` desde la raíz del repo (o `python data-gen/generate.py` si no hay `uv`, con `numpy pandas pyarrow pyyaml duckdb` instalados).
3. Antes de generar contenido en masa, confirmar que el deploy a GitHub Pages funciona de verdad tras habilitar Pages (ver incidencia de F0 arriba).
4. El PLAN.md marca una **pausa de revisión explícita tras la Fase 5** (no antes) — hasta entonces, seguir avanzando fase a fase sin pedir permiso salvo bloqueo real.
