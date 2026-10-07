# Progreso de implementación

Registro de qué fase del `PLAN.md` está hecha, verificada y pendiente. Se actualiza al terminar cada fase para poder retomar sin releer la conversación. Instrucción del usuario (2026-10-07): continuar fase a fase sin parar hasta agotar tokens; no gastar tokens en vano pero sin perder calidad.

## Resumen rápido

| Fase                                                  | Estado                                          |
| ----------------------------------------------------- | ----------------------------------------------- |
| F0 — Setup y despliegue                               | ✅ Hecha (deploy: ver "Despliegue" abajo)       |
| F1 — Dataset Lumen (+ página `/datos/`)               | ✅ Hecha y verificada                           |
| F2 — Núcleo de teoría + módulo M04                    | ✅ Hecha                                        |
| F3 — Motor de tests (quiz, examen, Leitner, progreso) | ⬜ Siguiente                                    |
| F4 — Laboratorios (DuckDB-WASM, Pyodide, `datakit`)   | ⬜                                              |
| F5 — Casos guiados                                    | ⬜ → luego PAUSA de revisión (la marca el PLAN) |
| F6-F10                                                | ⬜                                              |

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

## Siguiente: F5 — Casos guiados

PLAN §7.6/§6: colección `cases` (Zod ya definida: `title, description, difficulty, estimatedMinutes, role, brief, steps[], rubric[], modelReport`). Motor de casos: `CaseRunner.tsx` (brief del stakeholder → pasos secuenciales; cada paso `tool: sql|python|reasoning` abre un mini-editor SQL/Python o solo pregunta; `answerType: numeric|single|multiple|text-self-assessed` autocorregido; pistas; explicación; informe final con rúbrica de autoevaluación + `modelReport`). Rutas `/practica/casos/` y `/practica/casos/[id]/`; progreso en `progress.cases` (ya existe `saveCaseProgress`). Caso estrella #1 "Las ventas cayeron en marzo" (verdad plantada #10: rotura de stock de Electrónica del 2026-03-01 al 21, `inventory_snapshots` + mix de categoría; ojo: el dataset crece muy deprisa, comparar marzo 2026 con febrero/abril y con la categoría, no con 2025) completo con respuestas numéricas verificadas con DuckDB; después casos 2-3 si hay margen (A/B con lift real; SRM). Test pytest que **recalcule las respuestas numéricas de cada caso** con DuckDB. Tras F5: **PAUSA de revisión** del PLAN (resumen al usuario + URL desplegada); el usuario pidió seguir sin parar, así que continuar con F6 salvo bloqueo.

## Notas para retomar

1. `git status` en `C:\dev\Data_Analyst_Web`; en Windows la herramienta Bash falla con heredocs largos que mezclan comillas: usar la herramienta Write para ficheros largos.
2. Regenerar dataset: `python data-gen/generate.py` (necesita `numpy pandas pyarrow pyyaml`; `duckdb` para verificar).
3. Antes de escribir contenido, releer `docs/CONTENT_GUIDELINES.md`. Verificar toda URL de fuente con `curl -s -o /dev/null -w '%{http_code}'`.
4. El PLAN marca una pausa de revisión tras F5, no antes.
