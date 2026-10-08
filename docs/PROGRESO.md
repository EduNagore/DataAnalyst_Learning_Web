# Progreso de implementación

Registro de qué fase del `PLAN.md` está hecha, verificada y pendiente. Se actualiza al terminar cada fase para poder retomar sin releer la conversación. Instrucción del usuario (2026-10-07): continuar fase a fase sin parar hasta agotar tokens; no gastar tokens en vano pero sin perder calidad.

## Resumen rápido

| Fase                                                  | Estado                                           |
| ----------------------------------------------------- | ------------------------------------------------ |
| F0 — Setup y despliegue                               | ✅ Hecha (deploy: ver "Despliegue" abajo)        |
| F1 — Dataset Lumen (+ página `/datos/`)               | ✅ Hecha y verificada                            |
| F2 — Núcleo de teoría + módulo M04                    | ✅ Hecha                                         |
| F3 — Motor de tests (quiz, examen, Leitner, progreso) | ✅ Hecha                                         |
| F4 — Laboratorios (DuckDB-WASM, Pyodide, `datakit`)   | ✅ Hecha                                         |
| F5 — Casos guiados                                    | ✅ Hecha (la pausa de revisión la marca el PLAN) |
| F6 (Contenido Partes 0-II, M00-M12)                   | ✅                                               |
| F7-F10                                                | ⬜                                               |

Repo: `https://github.com/EduNagore/DataAnalyst_Learning_Web` (rama `main`). Sitio: `https://edunagore.github.io/DataAnalyst_Learning_Web/`.

## Despliegue

✅ Funciona: CI y Deploy en verde desde el commit `f5030a0` (tras sustituir `withastro/action` por build directo + `upload-pages-artifact@v4` + `deploy-pages@v4`). Para comprobar un run: API sin caché `https://api.github.com/repos/EduNagore/DataAnalyst_Learning_Web/actions/runs?per_page=4&_cb=N` y `.../runs/{id}/jobs`. NO fiarse de la vista HTML de Actions (dio un "success" falso).

---

## F0 ✅

Astro 7 + TS strict + Tailwind 4 + React 19 + MDX; `url()`; 12 colecciones Zod; libs con tests (`progress`, `quiz`, `srs`, `resultCompare`); shell web; CI/CD. Lecciones aprendidas en `docs/DECISIONS.md` (p. ej. `pnpm/setup@v1` falló; `astro check` no soporta TS7).

## F1 ✅

Generador determinista en `data-gen/` (config en `config.yaml`, contrato de columnas en `lumen/schema_doc.py`). Verificado con DuckDB sobre el Parquet real: determinismo byte a byte, 0 huérfanos, 45 MB (límite 60), y las 11 verdades plantadas. Bug corregido: comparación subcategoría vs categoría superior (`top_category_id`). `extra/` = 3 datasets externos reales. `/datos/` lee `public/data/_schema.json` (ERD Mermaid + diccionario). Detalle en `docs/DATASET.md`.

Pendiente menor: job de CI que regenere el dataset y compare `data-gen/checksums.json`; la correlación CUPED (#5) se apoya en persistencia de segmento, verificar al escribir el lab 55. Nota de realismo: los pedidos crecen mucho (2023: 18k, 2024: 77k, 2025: 168k, 2026-H1: 136k) por la rampa de altas de clientes.

## F2 ✅

- Layout de lección (`LessonLayout.astro`): sidebar de lecciones del módulo, TOC (h2), migas, prev/next, objetivos, fuentes (`SourceList`). Rutas dinámicas `/teoria/[moduleId]/` y `/teoria/[moduleId]/[lesson]/`.
- Componentes (`src/components/content/`): `BusinessContext`, `Callout`, `Snapshot`, `Term`, `KeyTakeaways`, `SourceList`, `ExcelFn`, `DialectTabs.tsx`, `VegaChart.tsx`, `Diagram.tsx` (Mermaid lazy).
- Tailwind typography, KaTeX (`remark-math`+`rehype-katex` vía `unified()` de `@astrojs/markdown-remark` — en Astro 7 los plugins ya no van en `markdown.remarkPlugins`), Shiki doble tema claro/oscuro, Pagefind (`/buscar/`, `data-pagefind-body` en lecciones).
- **M04 completo** (`src/content/modules/sql-i.yaml`): 5 lecciones (`sql-i/01..05`) con cifras reales de Lumen verificadas con DuckDB (p. ej. fan-out: envío 881.019,35 € real vs 2.275.942,25 € tras join) y 30 preguntas de quiz (`src/content/quizzes/sql-i/`). Fuentes: docs oficiales de DuckDB/PostgreSQL, URLs comprobadas con curl.
- `validate-content` OK (1 módulo, 5 lecciones, 30 preguntas), `astro check` 0 errores, lint limpio, unit 40/40, e2e 7/7.
- **Los quizzes aún no se renderizan en la lección** (los construye F3). Los `relatedLabs` de M04 apuntan a ids que crea F4: `sql-primeras-consultas`, `sql-fanout-joins`, `sql-antijoin`, `sql-nulls-coalesce`, `sql-case-segmentos`, `sql-fechas-zonas-horarias`.
- Decisión: sidebar de lección = lecciones del módulo (no los 30 módulos); `/teoria/` ya muestra el árbol completo.

---

## F3 ✅

- `src/components/quiz/`: `Quiz.tsx` (modos lesson/module/exam/review, aprobado ≥ 80 %, corrección con explicación y enlace a la sección, temporizador de examen, `aria-live`), `QuestionView.tsx` (radio/checkbox/orden por clic/numérico con coma decimal), `ExamRunner.tsx` (módulos, 20/40/60, temporizador, informe por módulo), `ReviewRunner.tsx` (Leitner, 20 por sesión), `LessonComplete.tsx`, `BestScore.tsx`, `InlineText.tsx`. `src/components/progress/ProgressPanel.tsx` (progreso por módulo, exámenes, exportar/importar/borrar JSON).
- `src/lib/questions.ts` (carga todas las preguntas con módulo/lección/URL) y endpoint estático `/practica/questions.json` (banco para examen y repaso). Rutas: `/practica/` (hub real), `/practica/tests/` y `/practica/tests/[moduleId]/`, `/practica/examen/`, `/practica/repaso/`, `/progreso/`. El quiz de lección se renderiza al final de cada lección (slot `after` de `LessonLayout`).
- `quiz.ts`: `parseNumberEs` ("14,85", "28.173", "1.234,5"), `shuffledOrder`; `progress.ts`: `recordSrsResult` (fallar → caja 1 con vencimiento +1 día; acertar solo avanza lo que ya estaba en el sistema). Unit 55/55, e2e 10/10 (quiz de lección, examen con informe, repaso). Playwright con `workers: 3` (con más, `astro preview` se atasca y hay timeouts de `goto`).
- Pendiente menor: los tipos `formula-output` y `chart-critique` están soportados en el render pero aún no hay preguntas de esos tipos (llegarán con M03 hojas de cálculo y M10 visualización).

---

## F4 ✅

- **Motor SQL** (`src/lib/duckdb/client.ts`): DuckDB-WASM en Worker, vistas sobre Parquet por HTTP, `variant` para tests ocultos, timeout 10 s con reinicio, 1.000 filas, `LOAD icu` previo. `sqlGuard.ts` (solo lectura), `sqlCheck.ts` (comparación con `resultCompare` + aserciones de texto + test oculto). 75 tests unitarios.
- **Motor Python** (`src/lib/pyodide/`): Pyodide 314.0.7 en module worker; `public/py/runner.py` + `public/py/datakit/{data,testing,stats,llm}.py` (`MockLLM` listo para los labs de IA).
- **UI**: `Editor.tsx` (CodeMirror 6, tema claro/oscuro, autocompletado del esquema), `SqlLab.tsx`, `PyLab.tsx`, `ResultTable.tsx`, `TestResults.tsx`, `LabList.tsx` (filtros lenguaje/dificultad/estado), `Playground.tsx` (esquema, ejemplos, historial, exportar CSV). Rutas `/practica/labs/`, `/practica/labs/[id]/`, `/practica/sql/`, endpoint `/labs-data/[id].json`. Las lecciones muestran «Ponlo en práctica» con sus `relatedLabs`.
- **9 labs**: SQL (7) `sql-primeras-consultas`, `sql-fanout-joins`, `sql-antijoin`, `sql-nulls-coalesce`, `sql-case-segmentos`, `sql-fechas-limites`, `sql-fechas-zonas-horarias`; Python (2) `py-pandas-primeros-pasos` (módulo `python-analisis`), `py-ab-test-statsmodels` (módulo `experimentacion`; SRM + efecto con statsmodels/scipy). Cada uno en `src/content/labs/<id>/` (`index.mdx`, `starter.*`, `solution.*`, `checks.yaml` o `test_lab.py`).
- **Verificado**: `pytest tests/labs` 39/39 (solución pasa, starter no, test oculto protege); e2e en navegador real de SQL (correcto/incorrecto/bloqueo de DROP), Python con pandas+pyarrow+Parquet y con statsmodels, y Playground. `ruff check .` limpio.
- **Los 30 módulos** existen como metadatos (`scripts/gen-modules.py`); `/teoria/` los muestra todos y marca «Próximamente» los que no tienen lecciones.
- Decisiones y hallazgos (ICU, `search_path`, runner, etc.) en `docs/DECISIONS.md` § Fase 4.
- Pendiente menor: labs de la lista del PLAN que dependen de lecciones aún no escritas (se añaden con sus módulos en F6-F8); el job de CI de Playwright descarga DuckDB/Pyodide de jsDelivr (tardará más que antes).

---

## F5 ✅

- `src/components/case/CaseRunner.tsx`: brief del stakeholder → pasos desbloqueados en orden (`tool` sql/python/reasoning con mini-editor y resultado; `answerType` numeric/single/multiple/text-self-assessed autocorregido con `quiz.checkAnswer` y `parseNumberEs`; pistas; «Ver la respuesta» tras 2 fallos) → informe final con rúbrica de autoevaluación e informe modelo. Progreso en `progress.cases` (se conserva al recargar). Rutas `/practica/casos/` (con estado por caso) y `/practica/casos/[id]/`. La colección `cases` ahora admite `datasets` y `packages`.
- **Caso estrella** `src/content/cases/ventas-marzo.mdx` (rol operaciones, 8 pasos): caída −11,47 % → ticket medio −10,74 % con pedidos planos → solo Electrónica cae (−54,71 %) → stock ≈ 1 ud. (0,99) el 9-mar frente a 211 → hipótesis (rotura de stock; demanda/precios/tracking descartadas) → pérdida estimada ≈ 1,61 M€ → recomendación. Sidecar `ventas-marzo.verify.yaml` con una consulta por paso numérico; `tests/labs/test_cases.py` **recalcula las respuestas con DuckDB** (si el dataset cambia, el caso falla en CI).
- e2e (`tests/e2e/casos.spec.ts`): recorrido completo del caso, persistencia tras recargar y ejecución SQL real en un paso.
- Limitación de datos a tener en cuenta en casos futuros: `web_sessions`/`events` y `orders` se generan de forma **independiente** (no cuadran entre sí; p. ej. las sesiones caen un 23 % en marzo por el fin de rebajas pero los pedidos no). No pedir al alumno que reconcilie conversión entre ambas fuentes.
- Casos 2-12 del PLAN: se añaden con sus módulos (F7-F8).

---

## F6 ✅ (Contenido Partes 0-II, M00-M12)

Estado: **M04 ✅, M05 ✅ (5 lecciones, 8 labs), M06 ✅ (3 lecciones, lab SCD2), M07 ✅ (4 lecciones, 3 labs nuevos), M08 ✅ (4 lecciones, 4 labs sobre `lumen_raw`), M09 ✅ (4 lecciones, 3 labs Python + 1 SQL, widget `SimpsonExplorer`, primer uso de `VegaChart` con tema claro/oscuro)**. M00 ✅ (3 lecciones), M01 ✅ (4 lecciones, 4 labs), M02 ✅ (4 lecciones, 4 labs, widget `DistributionExplorer`). M10 ✅ (4 lecciones, 4 labs de especificación Vega-Lite/contraste/factor de mentira, widget `ChartChooser`, test e2e que renderiza todos los gráficos Vega). M11 ✅ (4 lecciones, 3 labs: tarjetas KPI, modelo en estrella, inteligencia de tiempo; hechos de Power BI/Fabric/Looker/Tableau verificados en fuentes oficiales, ver Snapshots). M12 ✅ (3 lecciones, 3 labs: revisar resumen ejecutivo, comunicar cifras, priorización RICE; RICE verificado en Intercom). M03 ✅ (5 lecciones, 2 labs Python: auditoría de fórmulas y tabla dinámica en pandas, 5 libros Excel con autocomprobación generados por `scripts/build-workbooks.py`, páginas `/practica/hojas-de-calculo/`; verificado: nombres ES de función en Microsoft Support, Python en Excel, Copilot/Agent Mode, Claude para Excel, Gemini en Sheets; **`=COPILOT()` retirada el 2026-09-14**). Los libros se prueban sin Excel con la librería `formulas` (`tests/workbooks`); el error «número como texto» solo se ve en Excel real. **F6 completa.**

PLAN §7.1. Por módulo: 3-5 lecciones (estructura de `docs/CONTENT_GUIDELINES.md`), quizzes (6+ preguntas/lección), labs, libros Excel (`scripts/build-workbooks.py`, openpyxl), widgets (JoinVisualizer, WindowFrameVisualizer, ChartChooser, DistributionExplorer, SimpsonExplorer...). Contenido `volatility: high` (M03 IA en Excel, M07 pandas 3/Polars 2.0, M11 Power BI/Tableau): **verificar con búsqueda web antes de escribir** y usar `<Snapshot>`.

**Corrección del dataset (2026-10-08)**: detectado un artefacto del generador (7.094 pedidos apilados el 30-jun-2026, 10× un día normal, por recortar con `np.minimum` los pedidos relocalizados tras el alta). Ahora se descartan al final de `build_lumen` (con líneas, envíos y devoluciones) sin alterar el resto del azar: solo cambia junio-2026. `orders` pasa de 400.000 a **392.906** filas, `order_items` 1.014.555, `shipments` 365.198. Se actualizaron las cifras de SQL I/II y M07, `docs/DATASET.md` y `data-gen/checksums.json`. Los CSV se escriben ahora con LF (checksums idénticos en Windows y Linux). **Al escribir contenido nuevo, usar siempre cifras recalculadas con el dataset actual.**

Soporte `raw:<nombre>` en `datasets` de los labs Python (carga `lumen_raw/<nombre>.csv` en Pyodide; ver `PyLab`/`PyEngine`).

Hechos verificados para M07 (2026-10): pandas 3.0.6 (última; local 3.0.2), Polars **2.0.0 estable el 2026-10-06**, DuckDB 1.5.x; Pyodide trae Polars 1.33.1 (labs usan solo API común 1.x/2.0). Los labs Python se verifican también en Pyodide con `tests/e2e/all-py-labs.spec.ts`. Notas previas: pandas 3.0.2 (str dtype por defecto, Copy-on-Write: la asignación encadenada lanza `ChainedAssignmentError` y no modifica, `pd.col()`, datetime64[us]), Polars 2.0.0 instalado localmente (Pyodide trae 1.33.1), DuckDB 1.5.x.

**Regla de uso (ver `docs/USAGE_GUARD.md`)**: tras cada lección/fase ejecutar `node scripts/usage-guard.mjs status`; al ≥95 % el hook bloquea herramientas: guardar progreso, lanzar `node scripts/usage-guard.mjs wait` en segundo plano y terminar el turno.

## F7 — en curso (Contenido Partes III-IV, M13-M20 + casos 2-8)

Estado: **M13 ✅** (4 lecciones, 4 labs: IC/bootstrap/Wilson, Welch+potencia, comparaciones múltiples, beta-binomial; widget `CoverageExplorer` + `src/lib/inference.ts` con tests vitest). Pendientes: M14 (SRM, CUPED, peeking, caso 2-3), M15, M16, M17, M18, M19, M20 y casos 2-8.

Hechos reales del dataset para F7 (verificados 2026-10-08): `experiment_metrics` son **series diarias por rama** (no hay datos por usuario); `exp-checkout-v2` +7,8 % relativo (t = 5,34, p = 1,8e-6, 29 días), `exp-social-ads-geo-holdout` +5,9 % (último clic dice +22 %), `exp-reco-engine` SRM 11.166/8.834 (χ² = 271,9), `exp-onboarding-flow` y los 11 genéricos son nulos (p ≥ 0,36). No existe una columna pre-experimento por usuario: para CUPED derivar el ingreso previo de `orders`. Los productos tienen tasas de devolución indistinguibles del azar (dispersión 1,13 pp = esperada); el transportista es aleatorio (sin efecto real).

## Notas para retomar

1. `git status` en `C:\dev\Data_Analyst_Web`; en Windows la herramienta Bash falla con heredocs largos que mezclan comillas: usar la herramienta Write para ficheros largos.
2. Regenerar dataset: `python data-gen/generate.py` (necesita `numpy pandas pyarrow pyyaml`; `duckdb` para verificar).
3. Antes de escribir contenido, releer `docs/CONTENT_GUIDELINES.md`. Verificar toda URL de fuente con `curl -s -o /dev/null -w '%{http_code}'`.
4. El PLAN marca una pausa de revisión tras F5, no antes.
