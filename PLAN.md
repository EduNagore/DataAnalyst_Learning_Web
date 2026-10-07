# PLAN — Data Analyst Academy

Especificación completa para construir y desplegar una web de aprendizaje y práctica para convertirse en un **data analyst de primer nivel** en 2026: SQL, hojas de cálculo, Python, estadística, experimentación, causalidad, visualización, BI, ingeniería analítica, capa semántica e **IA aplicada al análisis** (copilotos, text-to-SQL, analítica agéntica). El objetivo final del usuario es llegar a una empresa con nivel sólido de analista _mid/senior_: teoría + práctica autocorregida + casos reales + portfolio + entrevistas.

Este documento es la **fuente de verdad**. Si algo no está especificado aquí, elige la opción más simple que sea coherente con el resto del plan y documéntala en `docs/DECISIONS.md`.

> **Regla de oro de actualidad**: el curso debe reflejar el estado del arte en el momento de redactar cada lección. La §8 resume lo verificado al crear este plan (2026-10-07), pero **todo dato volátil debe re-verificarse con búsqueda web en fuentes oficiales al redactar**. Nunca fiarse solo de la memoria del modelo.

---

## 1. Objetivos y principios

1. **Teoría estructurada por partes**, de cero a nivel senior, con fuentes primarias citadas en cada lección.
2. **Práctica real y autocorregida en el navegador**: ejercicios **SQL** (DuckDB-WASM) y **Python** (Pyodide con pandas 3, Polars, DuckDB, statsmodels, scikit-learn) sobre un dataset empresarial ficticio y realista; tests tipo test; **casos de análisis guiados** con respuestas numéricas verificables.
3. **Práctica fuera del navegador**: libros Excel descargables con autocomprobación, proyectos locales con herramientas reales (dbt, Power BI, Evidence, marimo, MCP…).
4. **Mentalidad de negocio**: cada técnica se conecta con una decisión de negocio. Un analista top no "saca datos", **recomienda decisiones** con evidencia y comunica la incertidumbre.
5. **IA como parte del oficio**, no como apéndice: cómo usar LLMs y agentes para analizar más rápido **sin perder rigor** (verificación, reproducibilidad, seguridad), y por qué la capa semántica y las métricas bien definidas son la base de la analítica con IA.
6. **Actualizada y fiable**: cada lección tiene `sources`, `lastReviewed` y `volatility`; un workflow mensual detecta contenido caducado y enlaces rotos; existe una página **Radar** con el estado del arte fechado.
7. **100 % estática**: sin backend, sin base de datos, sin claves de API obligatorias. Se despliega en **GitHub Pages** con GitHub Actions.
8. **Idioma**: contenido en **español** (España), manteniendo los términos técnicos en inglés cuando así se usan en la industria (_window functions_, _cohort_, _funnel_, _lift_, _semantic layer_…). La primera vez que aparece un término: "funciones de ventana (_window functions_)". Glosario bilingüe. Preguntas de entrevista disponibles también en inglés.
9. **Localización de hojas de cálculo**: mostrar siempre el nombre de la función en **inglés y en español** (p. ej. `XLOOKUP` / `BUSCARX`), y advertir del separador de argumentos (`,` vs `;`) y del separador decimal en configuraciones regionales españolas.

---

## 2. Stack técnico

> Versiones: usar la **última versión estable** de cada herramienta en el momento de la implementación, fijarla en el lockfile y anotar en `docs/DECISIONS.md` la versión elegida. Las indicadas abajo son las verificadas a 2026-10.

| Capa                         | Elección                                                                                                                      | Motivo                                                                                                                                                                                         |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Framework web                | **Astro 7.x** (`output: 'static'`) + **MDX**                                                                                  | Sitio de contenido; HTML estático; islas interactivas solo donde hacen falta. Revisar guía de migración si la versión mayor cambia.                                                            |
| Componentes interactivos     | **React 19** como islas (`client:visible` / `client:load`)                                                                    | Quizzes, laboratorios, widgets.                                                                                                                                                                |
| Lenguaje                     | **TypeScript** (strict) para la web; **SQL** y **Python** para ejercicios                                                     | Los dos lenguajes del analista.                                                                                                                                                                |
| Estilos                      | **Tailwind CSS 4** (plugin Vite oficial) + `@tailwindcss/typography`                                                          | Rápido, consistente, modo oscuro.                                                                                                                                                              |
| Contenido                    | **Astro Content Collections** con esquemas **Zod 4**                                                                          | Valida frontmatter, quizzes, labs y casos en build.                                                                                                                                            |
| Motor SQL en navegador       | **DuckDB-WASM** (`@duckdb/duckdb-wasm`, versión estable fijada) en un **Web Worker**                                          | SQL analítico real (ventanas, `QUALIFY`, `PIVOT`, `ASOF JOIN`, Parquet por HTTP) sin servidor.                                                                                                 |
| Python en navegador          | **Pyodide 314.x** (Python 3.14) en un **module worker**, desde jsDelivr                                                       | Incluye pandas 3.0, Polars, DuckDB, PyArrow, NumPy, SciPy, statsmodels, scikit-learn, matplotlib, Altair, networkx. Desde la 314 los workers clásicos no están soportados (`pyodide.asm.mjs`). |
| Editor de código             | **CodeMirror 6** (`@uiw/react-codemirror` + `@codemirror/lang-sql` + `@codemirror/lang-python`)                               | Ligero; autocompletado de esquema SQL (tablas/columnas del dataset).                                                                                                                           |
| Gráficos en lecciones y labs | **Vega-Lite** vía `vega-embed` (renderiza también las specs que genera Altair en Python) + **Observable Plot** para widgets   | Gramática de gráficos coherente entre teoría y práctica.                                                                                                                                       |
| Fórmulas                     | `remark-math` + `rehype-katex`                                                                                                | Estadística, intervalos, CUPED, DiD…                                                                                                                                                           |
| Diagramas                    | **Mermaid** en cliente (lazy) dentro de `<Diagram>`                                                                           | ERD del dataset, pipelines, DAGs causales.                                                                                                                                                     |
| Resaltado de código          | Shiki (integrado en Astro), incluye SQL, Python, DAX, M, YAML                                                                 | —                                                                                                                                                                                              |
| Búsqueda                     | **Pagefind** (`astro-pagefind`)                                                                                               | Búsqueda estática.                                                                                                                                                                             |
| Estado / progreso            | `nanostores` + `localStorage` (export/import JSON)                                                                            | Sin backend.                                                                                                                                                                                   |
| Tests web                    | **Vitest** (unit) + **Playwright** (e2e smoke)                                                                                | —                                                                                                                                                                                              |
| Tests de contenido           | **pytest** con CPython 3.14 y las **mismas versiones de paquetes que trae Pyodide** (pandas, polars, duckdb…)                 | Cada solución pasa y cada starter falla.                                                                                                                                                       |
| Calidad                      | ESLint (flat config) + Prettier + `astro check`; **ruff** para Python; **sqlfluff** (dialecto duckdb) para las soluciones SQL | —                                                                                                                                                                                              |
| Gestor de paquetes           | **pnpm**, Node **24 LTS** (`.nvmrc`; comprobar requisito mínimo de Astro); **uv** para Python                                 | —                                                                                                                                                                                              |
| Despliegue                   | **GitHub Pages** vía `withastro/action` + `actions/deploy-pages`                                                              | Requisito del usuario.                                                                                                                                                                         |

### Entorno de desarrollo (Windows 11)

- Node 24 LTS (`nvm-windows` o instalador oficial), `corepack enable` para pnpm.
- Python 3.14 (igual a la versión menor de Pyodide fijada) gestionado con `uv`.
- VS Code con extensiones: Astro, Tailwind CSS IntelliSense, ESLint, Prettier, Python, Ruff, MDX, SQLFluff.
- Scripts multiplataforma (nada de bash-only en `package.json`; usar Node o Python).

---

## 3. Despliegue en GitHub Pages

- Repositorio: `https://github.com/EduNagore/DataAnalyst_Learning_Web`.
- `astro.config.mjs`:
  - `site: 'https://edunagore.github.io'`
  - `base: '/DataAnalyst_Learning_Web'` (nombre del repo; ajustar si cambia)
  - `trailingSlash: 'always'`
- **Todas** las rutas internas y assets se construyen con un helper `url(path)` basado en `import.meta.env.BASE_URL`. Nunca enlaces absolutos `"/..."` a mano. DuckDB-WASM y Pyodide cargan `public/data` y `public/py` usando ese helper.
- Tamaño: los datos publicados (`public/data`) deben sumar **≤ 60 MB** y ningún archivo > 25 MB (Parquet comprimido con ZSTD).
- En GitHub: _Settings → Pages → Source: GitHub Actions_.
- Workflows en `.github/workflows/`:
  1. `ci.yml` (PR y push): install → `astro check` → lint (ESLint, ruff, sqlfluff) → vitest → generación determinista del dataset y verificación de checksum → `pytest` de labs Python y SQL → validación de contenido → build → Playwright smoke contra `astro preview`.
  2. `deploy.yml` (push a `main` + manual): build con `withastro/action` y despliegue con `actions/deploy-pages`. Permisos: `pages: write`, `id-token: write`.
  3. `content-freshness.yml` (cron mensual + manual): `lychee` para enlaces rotos + `scripts/check-freshness.mjs` que lista lecciones con `lastReviewed` > 6 meses o con `volatility: high` > 3 meses, y entradas del Radar con `asOf` > 3 meses; abre/actualiza un issue con la lista.
- **Primera tarea de la Fase 0**: desplegar un "hello world" para validar `base` y el workflow antes de construir nada más.

---

## 4. Arquitectura de la web (mapa de rutas)

```
/                              Inicio: qué es, ruta de aprendizaje, progreso global, "continuar donde lo dejaste"
/ruta/                         Rutas recomendadas (Esencial ~120 h, Completa ~300 h, por perfil: producto, marketing, BI/finanzas)
/teoria/                       Índice de partes y módulos con % completado
/teoria/<modulo>/<leccion>/    Lección (MDX) + TOC + fuentes + mini-quiz + "siguiente"
/practica/                     Hub de práctica
/practica/tests/               Tests por módulo
/practica/tests/<modulo>/
/practica/labs/                Laboratorios (filtros: lenguaje SQL/Python, parte, dificultad, estado)
/practica/labs/<id>/           Lab: enunciado | editor | resultado (tabla/gráfico/consola) | tests | pistas | solución
/practica/sql/                 SQL Playground libre sobre el dataset (explorador de esquema, ERD, historial de consultas)
/practica/casos/               Casos de análisis guiados ("¿por qué cayeron las ventas en marzo?")
/practica/casos/<id>/
/practica/hojas-de-calculo/    Libros Excel descargables con autocomprobación
/practica/examen/              Modo examen: N preguntas aleatorias, temporizador, informe por módulo
/practica/repaso/              Repaso espaciado (Leitner) de preguntas falladas
/proyectos/                    Proyectos de portfolio para hacer en local con herramientas reales
/proyectos/<id>/
/entrevistas/                  Preguntas (ES/EN), SQL cronometrado, casos de producto/métricas, estadística, conductuales
/entrevistas/casos/<caso>/
/datos/                        El dataset "Lumen": historia de la empresa, ERD, diccionario de datos, descargas
/radar/                        Radar del analista: herramientas y técnicas en Adoptar / Probar / Evaluar / Evitar, con fecha
/glosario/                     Glosario ES/EN con enlaces a lecciones
/fuentes/                      Bibliografía global por tema y tipo
/novedades/                    Changelog del curso (qué lecciones se han actualizado y por qué)
/progreso/                     Panel de progreso, export/import JSON, reset
```

Layout común: cabecera (logo, Teoría, Práctica, Proyectos, Entrevistas, Datos, buscador, toggle tema), sidebar con árbol de módulos en teoría, TOC lateral en lecciones, responsive (sidebar colapsable en móvil).

---

## 5. Estructura de archivos

```
DataAnalyst_Learning_Web/
├─ .github/workflows/{ci.yml, deploy.yml, content-freshness.yml}
├─ .nvmrc  .editorconfig  .prettierrc  .sqlfluff  eslint.config.js  tsconfig.json
├─ astro.config.mjs  package.json  pnpm-lock.yaml
├─ pyproject.toml                  # uv: pytest, ruff, pandas, polars, duckdb, numpy, scipy, statsmodels,
│                                  #     scikit-learn, altair, openpyxl (versiones alineadas con Pyodide)
├─ PLAN.md                         # este documento
├─ docs/
│  ├─ CONTENT_GUIDELINES.md        # reglas de redacción, fuentes y formato (ver §9)
│  ├─ SOURCES.md                   # lista curada de fuentes (ver §8)
│  ├─ DATASET.md                   # diseño del dataset, "verdades plantadas" y cómo regenerarlo (ver §7.3)
│  └─ DECISIONS.md                 # decisiones tomadas durante la implementación
├─ data-gen/
│  ├─ generate.py                  # generador determinista (seed fija) del dataset Lumen
│  ├─ config.yaml                  # tamaños, fechas, efectos plantados
│  └─ checksums.json               # hash de cada archivo generado (CI verifica determinismo)
├─ public/
│  ├─ data/
│  │  ├─ lumen/                    # Parquet "limpio" (capa marts) — dataset principal
│  │  ├─ lumen_raw/                # CSV/JSON "sucios" (capa raw) para labs de limpieza
│  │  ├─ lumen_variant/            # variante pequeña con otra seed para tests ocultos
│  │  ├─ extra/                    # datasets pequeños específicos (Anscombe, Simpson, series temporales…)
│  │  └─ workbooks/                # .xlsx descargables (ejercicios + soluciones)
│  └─ py/datakit/                  # librería didáctica Python (ver §7.4), servida a Pyodide
├─ src/
│  ├─ content.config.ts            # colecciones + esquemas Zod
│  ├─ content/
│  │  ├─ modules/<modulo>.yaml     # id, parte, orden, título, descripción, objetivos, horas estimadas
│  │  ├─ lessons/<modulo>/<NN-slug>.mdx
│  │  ├─ quizzes/<modulo>/<NN-slug>.yaml
│  │  ├─ labs/<id>/
│  │  │  ├─ index.mdx              # frontmatter + enunciado
│  │  │  ├─ starter.sql | starter.py
│  │  │  ├─ solution.sql | solution.py
│  │  │  └─ checks.yaml | test_lab.py   # SQL: reglas de comparación; Python: tests (visibles y ocultos)
│  │  ├─ cases/<id>.mdx            # casos de análisis guiados (ver §7.6)
│  │  ├─ workbooks/<id>.mdx        # fichas de los ejercicios Excel
│  │  ├─ projects/<id>.mdx
│  │  ├─ radar/entries.yaml
│  │  ├─ interview/questions.yaml
│  │  ├─ interview/cases/<caso>.mdx
│  │  ├─ changelog/<AAAA-MM-DD>.md
│  │  └─ glossary/terms.yaml
│  ├─ components/
│  │  ├─ layout/ (Header, Sidebar, Toc, Footer, ThemeToggle, Breadcrumbs)
│  │  ├─ content/ (Callout, Diagram, SourceList, KeyTakeaways, Snapshot, Term, ExcelFn, VegaChart, DialectTabs, BusinessContext)
│  │  ├─ quiz/ (Quiz.tsx, Question*.tsx, QuizResult.tsx)
│  │  ├─ lab/ (SqlLab.tsx, PyLab.tsx, Editor.tsx, ResultTable.tsx, ChartOutput.tsx, Console.tsx, TestResults.tsx, SchemaExplorer.tsx)
│  │  ├─ case/ (CaseRunner.tsx, CaseStep.tsx, CaseReport.tsx)
│  │  ├─ widgets/ (ver §10)
│  │  └─ progress/ (ProgressBar, ModuleProgress, ProgressPanel)
│  ├─ layouts/ (BaseLayout.astro, LessonLayout.astro, LabLayout.astro, CaseLayout.astro)
│  ├─ lib/
│  │  ├─ url.ts                    # helper base path
│  │  ├─ progress.ts               # nanostores + localStorage (esquema versionado)
│  │  ├─ quiz.ts                   # corrección, puntuación, barajado con seed, tolerancia numérica
│  │  ├─ srs.ts                    # Leitner (5 cajas)
│  │  ├─ resultCompare.ts          # comparación de result sets SQL (ver §7.4)
│  │  ├─ duckdb/{client.ts, worker.ts}
│  │  └─ pyodide/{client.ts, worker.ts, runner.py}
│  ├─ pages/                       # rutas de §4
│  └─ styles/global.css
├─ projects/                       # código inicial de los proyectos locales (ver §7.7)
├─ scripts/
│  ├─ validate-content.mjs         # quiz ↔ lección, ids únicos, anclas, enlaces internos, nº de fuentes
│  ├─ check-freshness.mjs
│  └─ build-workbooks.py           # genera los .xlsx con openpyxl a partir del dataset
└─ tests/
   ├─ unit/                        # vitest: quiz.ts, srs.ts, progress.ts, url.ts, resultCompare.ts
   ├─ e2e/                         # playwright: navegación, quiz, lab SQL y lab Python pasan, caso guiado
   └─ labs/
      ├─ test_sql_labs.py          # con duckdb (CPython): solution.sql pasa checks; starter.sql no
      └─ test_py_labs.py           # solution.py pasa test_lab.py; starter.py no
```

---

## 6. Esquemas de contenido (Zod)

**Lección** (`lessons`):

```ts
{
  title: string; description: string;
  module: string;            // id del módulo
  order: number;
  level: 'básico' | 'intermedio' | 'avanzado';
  estimatedMinutes: number;
  objectives: string[];      // 3-5 objetivos de aprendizaje
  prerequisites?: string[];  // ids de lecciones
  tools?: string[];          // p.ej. ['duckdb', 'excel', 'power-bi', 'polars']
  volatility: 'low' | 'medium' | 'high';   // high = herramientas, versiones, funciones IA, precios, rankings
  lastReviewed: date;
  sources: { title: string; url: string; type: 'paper'|'docs'|'blog'|'spec'|'book'|'video'|'course'; authors?: string; year: number }[];  // mínimo 2
  relatedLabs?: string[];
  relatedCases?: string[];
}
```

**Quiz** (`quizzes`), un YAML por lección:

```yaml
lesson: sql-avanzado/02-funciones-de-ventana
questions:
  - id: sql2-02-q1 # único global
    type: single # single | multiple | truefalse | order | numeric | sql-output | formula-output | chart-critique
    difficulty: 2 # 1-3
    prompt: '...' # markdown permitido
    code: '...' # opcional: SQL / Python / fórmula Excel / DAX
    table: '...' # opcional: tabla markdown de entrada (para sql-output / formula-output)
    image: '...' # opcional: gráfico a criticar (chart-critique), con alt text obligatorio
    options: ['...', '...'] # single/multiple/order (en order: orden correcto)
    answer: [1] # índices correctos; numeric: [valor]
    tolerance: 0.01 # solo numeric (absoluta o relativa con 'rel:0.02')
    explanation: '...' # por qué la correcta lo es Y por qué las otras no
    ref: '#seccion-ancla'
```

**Lab** (`labs`, frontmatter de `index.mdx`):

```ts
{
  title; description;
  language: 'sql' | 'python';
  part: string; module: string;
  difficulty: 1|2|3; estimatedMinutes: number;
  concepts: string[];
  datasets: string[];          // tablas/archivos de public/data que se cargan
  packages?: string[];         // solo python: paquetes Pyodide extra (polars, duckdb, statsmodels…)
  output?: 'table' | 'chart' | 'console';
  hints: string[];             // se revelan de una en una
  relatedLessons: string[];
  businessQuestion: string;    // la pregunta de negocio que responde el ejercicio
}
```

**Checks de un lab SQL** (`checks.yaml`):

```yaml
compare:
  orderMatters: true # si el enunciado pide ORDER BY
  ignoreColumnNames: false # true = solo por posición
  floatTolerance: 1e-6
  columns: [month, revenue] # opcional: subconjunto de columnas a comparar
hiddenOnVariant: true # re-ejecutar starter y solución contra lumen_variant (anti-hardcode)
assertions: # opcional: SQL extra que debe devolver true
  - name: 'No usa DISTINCT para tapar duplicados'
    kind: query-text-not-contains
    value: 'DISTINCT'
```

**Caso de análisis** (`cases`, frontmatter):

```ts
{
  title; description; difficulty: 1|2|3; estimatedMinutes: number;
  role: 'producto'|'marketing'|'finanzas'|'operaciones'|'bi';
  brief: string;                       // email ficticio del stakeholder
  steps: {
    id: string; prompt: string;        // markdown
    tool: 'sql'|'python'|'reasoning';  // abre un mini-editor o solo pregunta
    answerType: 'numeric'|'single'|'multiple'|'text-self-assessed';
    answer?: number | number[]; tolerance?: string; options?: string[];
    hints: string[]; explanation: string;
  }[];
  rubric: string[];                    // checklist de autoevaluación del informe final
  modelReport: string;                 // informe modelo (se muestra al terminar)
}
```

**Radar** (`radar/entries.yaml`):

```yaml
- id: polars
  name: Polars
  category: herramientas-python # sql-motores | herramientas-python | bi | ingenieria-analitica | ia-analitica | tecnicas
  ring: adoptar # adoptar | probar | evaluar | evitar
  asOf: 2026-10
  summary: '...'
  sources: [{ title, url }]
  relatedLessons: [...]
```

**Progreso** (localStorage, clave `daa:progress:v1`):

```ts
{
  lessonsRead: Record<lessonId, isoDate>;
  quizScores: Record<quizOrLessonId, { best: number; last: number; attempts: number }>;
  labs: Record<labId, { status: 'started' | 'passed'; code: string; updatedAt: isoDate }>;
  cases: Record<caseId, { step: number; answers: Record<string, unknown>; completed?: isoDate }>;
  srs: Record<questionId, { box: 1 | 2 | 3 | 4 | 5; due: isoDate }>;
  exams: {
    date;
    score;
    total;
    byModule: Record<string, number>;
  }
  [];
}
```

---

## 7. Contenido

### 7.1 Teoría — partes, módulos y lecciones

Cada lección: 1.500–3.000 palabras, estructura fija (ver §9). Cada módulo: ≥ 1 diagrama o gráfico, ≥ 1 lab o caso asociado, 3–6 lecciones. Todas las técnicas se ilustran con el dataset **Lumen** (§7.3) cuando sea posible.

**Parte 0 — Fundamentos del oficio**

- **M00 El data analyst en 2026**: tipos de analista (producto, marketing/growth, BI, finanzas/FP&A, operaciones) vs analytics engineer vs data scientist vs data engineer; el ciclo del análisis (pregunta → datos → análisis → decisión → seguimiento); cómo ha cambiado el rol con la IA (copilotos, analítica agéntica, capa semántica como base); qué separa a un analista "top" (criterio, rigor, comunicación, impacto); mapa del stack moderno. **volatility: medium**.
- **M01 Pensamiento analítico y de negocio**: formular la pregunta correcta; árboles de problemas (_issue trees_), MECE, análisis guiado por hipótesis; métricas _North Star_, métricas de entrada/salida, árboles de KPIs, _guardrail metrics_; unit economics (CAC, LTV, payback, margen de contribución); funnels y cohortes como marcos mentales; ley de Goodhart; cómo definir una métrica sin ambigüedad (grano, filtros, ventana temporal, numerador/denominador).
- **M02 Estadística descriptiva y probabilidad**: tipos de variables; tendencia central y dispersión; distribuciones (normal, log-normal, Poisson, binomial, colas pesadas); percentiles y por qué la media engaña (ingresos, latencias); correlación ≠ causalidad; cuarteto de Anscombe y _Datasaurus Dozen_; probabilidad condicional y Bayes; ley de los grandes números y TLC (con simulación).

**Parte I — Herramientas núcleo**

- **M03 Hojas de cálculo modernas**: tablas estructuradas; matrices dinámicas (`FILTER`/`FILTRAR`, `SORT`/`ORDENAR`, `UNIQUE`/`UNICOS`, `XLOOKUP`/`BUSCARX`, `LET`, `LAMBDA`, `GROUPBY`/`AGRUPARPOR`, `PIVOTBY`/`PIVOTARPOR`); tablas dinámicas; Power Query (M) y modelo de datos/Power Pivot; buenas prácticas de modelado en hojas (separar inputs, cálculos y outputs; auditoría de fórmulas); Python en Excel; **Copilot en Excel: Agent Mode y Plan Mode**, Claude for Excel; Google Sheets (Connected Sheets, funciones de IA con Gemini). Verificar los nombres en español de cada función en la documentación oficial de Microsoft. **volatility: high** en la parte de IA.
- **M04 SQL I — Fundamentos**: modelo relacional; `SELECT`/`WHERE`/`GROUP BY`/`HAVING`/`ORDER BY`; orden lógico de ejecución; joins (inner, left, full, cross, self) y la trampa del _fan-out_; `NULL` y lógica trivaluada; `CASE`; tipos, fechas y zonas horarias; subconsultas; `UNION` vs `UNION ALL`.
- **M05 SQL II — Analítico avanzado**: CTEs; funciones de ventana (ranking, `LAG`/`LEAD`, acumulados, medias móviles; marcos `ROWS` vs `RANGE` vs `GROUPS`); `QUALIFY`; `GROUPING SETS`/`ROLLUP`/`CUBE`; `PIVOT`/`UNPIVOT`; CTEs recursivas; _date spine_ y relleno de huecos; _gaps & islands_; sesionización; deduplicación; semi/anti-joins; `ASOF JOIN`; JSON, listas y structs; _friendly SQL_ de DuckDB (`GROUP BY ALL`, `SELECT * EXCLUDE/REPLACE`, `COLUMNS()`); sintaxis _pipe_ (`|>`) de GoogleSQL; diferencias de dialecto (DuckDB, PostgreSQL, BigQuery, Snowflake, T-SQL) con `<DialectTabs>`.
- **M06 SQL III — Rendimiento y modelado de datos**: almacenamiento columnar; `EXPLAIN`/`EXPLAIN ANALYZE`; _predicate pushdown_, particionado y _clustering_; coste en warehouses cloud (bytes escaneados, créditos) y cómo no arruinar a tu empresa con un `SELECT *`; modelado dimensional (Kimball): grano, hechos (transaccionales, snapshot periódico, acumulativo), dimensiones, SCD tipo 1/2, esquema estrella; _One Big Table_; arquitectura medallón (bronze/silver/gold); legibilidad y estilo SQL (convenciones, sqlfluff).
- **M07 Python para análisis**: entorno moderno (uv, ruff, VS Code); notebooks (Jupyter + Jupyter AI, **marimo** reactivo) y reproducibilidad; **pandas 3.0** (dtype `str` por defecto, Copy-on-Write, cambios que rompen código antiguo); **Polars** (expresiones, _lazy_, motor _streaming_; cambios de Polars 2.0); DuckDB desde Python y SQL sobre DataFrames; Apache Arrow como formato común; cuándo usar pandas vs Polars vs DuckDB; Narwhals/Ibis como capas agnósticas (mención). **volatility: high**.
- **M08 Limpieza y calidad de datos**: _tidy data_; valores ausentes (MCAR/MAR/MNAR) y estrategias; outliers (cuándo son error y cuándo son la noticia); duplicados y claves; normalización de texto y categorías; fechas, zonas horarias y codificaciones; _data profiling_; validación (pandera, dbt tests, Great Expectations, Soda); contratos de datos; documentar supuestos.
- **M09 Análisis exploratorio (EDA)**: preguntas antes que gráficos; univariante, bivariante, multivariante; segmentación; paradoja de Simpson; sesgo de supervivencia y de selección; regresión a la media; _base rates_; checklist de EDA reproducible.

**Parte II — Visualización y comunicación**

- **M10 Visualización de datos**: percepción (Cleveland & McGill, atributos preatentivos); elegir el gráfico según la pregunta; gramática de gráficos (Vega-Lite/Altair); color (paletas accesibles, Okabe-Ito, viridis, secuencial/divergente/categórica); anotaciones y títulos que dicen la conclusión; cómo mienten los gráficos (ejes, áreas, doble eje); incertidumbre visual; accesibilidad (alt text, contraste, no depender solo del color); herramientas (Altair, Plotly, matplotlib/seaborn, Observable Plot).
- **M11 Dashboards y BI**: diseño de dashboards (jerarquía, KPI + contexto + comparación, densidad, filtros); dashboards operativos vs estratégicos; **Power BI** (modelo estrella, Power Query, **DAX**: contexto de fila/filtro, `CALCULATE`, inteligencia de tiempo, _calculation groups_, cálculos visuales, funciones definidas por el usuario; RLS; **PBIP + Git, TMDL y formato PBIR**; Copilot; Fabric y Direct Lake); **Tableau** (LOD, Tableau Next sobre Agentforce, Pulse/Concierge); **Looker** (LookML) y Looker Studio; open source (Superset, Metabase, Lightdash); **BI-as-code** (Evidence); criterios de elección. **volatility: high**.
- **M12 Storytelling y comunicación**: principio de la pirámide (Minto), SCR (situación-complicación-resolución); resumen ejecutivo y "BLUF"; memos escritos vs slides; adaptar el mensaje al público; comunicar incertidumbre y límites; recomendaciones accionables; gestión de stakeholders, priorización de peticiones y decir "no"; escritura asíncrona.

**Parte III — Estadística aplicada, experimentación y causalidad**

- **M13 Inferencia estadística**: muestreo; error estándar; intervalos de confianza; bootstrap; contrastes de hipótesis y qué es (y qué no es) un p-valor (declaración de la ASA); errores tipo I/II y potencia; tamaño del efecto; comparaciones múltiples (Bonferroni, Benjamini-Hochberg); tests habituales (t, χ², Mann-Whitney, proporciones); introducción al enfoque bayesiano.
- **M14 Experimentación y A/B testing**: diseño (hipótesis, unidad de aleatorización, métricas primaria/guardrail); cálculo de potencia y MDE; **SRM** (_sample ratio mismatch_); varianza y **CUPED**/CUPAC; el problema del _peeking_ y **tests secuenciales** (mSPRT/inferencia siempre válida, group sequential); análisis bayesiano; métricas de ratio y método delta; efectos novedad/primacía; interferencia, _switchback_ y experimentos por clúster/geo; efectos heterogéneos; ley de Twyman; cultura de experimentación; plataformas (GrowthBook, Statsig, Eppo, Optimizely) **volatility: medium**.
- **M15 Inferencia causal sin experimentos**: DAGs y variables de confusión, colisionadores y mediadores; diferencias en diferencias (incluida DiD moderna con adopción escalonada, Callaway & Sant'Anna); control sintético; regresión discontinua; variables instrumentales; _propensity scores_ y matching; series temporales estructurales bayesianas (CausalImpact); cuándo un análisis observacional basta y cuándo no.
- **M16 Regresión y modelos para analistas**: regresión lineal y logística interpretadas para negocio; interacciones y no linealidades; multicolinealidad; regularización (mención); modelos de árboles y _gradient boosting_ como herramienta exploratoria; interpretabilidad (importancia por permutación, SHAP); validación (train/test, _leakage_); segmentación (RFM, k-means) y sus trampas; cuándo un analista debe modelar y cuándo pasarlo a data science.
- **M17 Series temporales y forecasting**: componentes (tendencia, estacionalidad, festivos); descomposición STL; suavizado exponencial (ETS), ARIMA; modelos estadísticos rápidos (statsforecast/Nixtla); **modelos fundacionales de series temporales** (TimesFM, Chronos, Moirai, TimeGPT) y cuándo aportan; evaluación (MAE, MAPE y sus problemas, MASE, _backtesting_ con origen móvil); intervalos de predicción; detección de anomalías; _forecast_ vs _budget_. **volatility: high** en modelos fundacionales.

**Parte IV — Analítica por dominio**

- **M18 Analítica de producto**: _tracking plan_ y diseño de eventos; funnels; curvas de retención y cohortes; DAU/WAU/MAU y _stickiness_; activación y "aha moment"; _growth accounting_ (nuevos, retenidos, resucitados, perdidos); análisis de features; herramientas (Amplitude, Mixpanel, PostHog); investigación de caídas de métricas (checklist: tracking, estacionalidad, mix, cambios de producto, externos).
- **M19 Analítica de marketing y clientes**: atribución (reglas, _data-driven_) y sus límites; incrementalidad y _geo-lift_; **Marketing Mix Modeling** moderno (Google Meridian, Meta Robyn, PyMC-Marketing); CLV (BG/NBD + Gamma-Gamma); churn y retención; segmentación RFM; privacidad y señal (consentimiento, cookies, modelado de conversiones). **volatility: high** en herramientas y privacidad.
- **M20 Analítica financiera y de operaciones**: lectura de una cuenta de resultados para analistas; unit economics; métricas SaaS/suscripción (MRR/ARR, NRR, GRR, churn de ingresos); análisis de varianzas (precio/volumen/mix); presupuesto vs forecast; operaciones (inventario, rotación, _fill rate_, plazos de entrega, capacidad); pricing y elasticidad (intro).

**Parte V — Stack moderno e ingeniería analítica**

- **M21 El stack de datos moderno**: warehouses y lakehouses (BigQuery, Snowflake, Databricks, Redshift, Microsoft Fabric); formatos de tabla abiertos (Apache Iceberg, Delta Lake, DuckLake); ELT (Fivetran, Airbyte, dlt); orquestación (Airflow 3, Dagster); _reverse ETL_; analítica _local-first_ con DuckDB/MotherDuck; _streaming_ (nociones). **volatility: high**.
- **M22 Ingeniería analítica con dbt**: modelos, `ref`/`source`, capas (staging → intermediate → marts); tests y contratos; documentación y linaje; modelos incrementales y snapshots; _source freshness_; **motor dbt Fusion y dbt Core v2**; alternativas (SQLMesh); Git, _pull requests_, CI para datos y code review de SQL. **volatility: high**.
- **M23 Capa semántica y métricas**: por qué existe (una sola definición de "ingresos"); entidades, dimensiones, medidas, métricas; **MetricFlow** (open source, Apache 2.0); **Open Semantic Interchange (OSI)**; Cube; LookML; modelos semánticos de Power BI; _semantic views_ de Snowflake y _metric views_ de Databricks; por qué la capa semántica es requisito de la analítica con IA; gobierno de métricas. **volatility: high**.
- **M24 Gobierno, privacidad y ética**: RGPD y LOPDGDD para analistas (base legal, minimización, finalidad); anonimización vs seudonimización, k-anonimato, privacidad diferencial (intuición); catálogos y linaje; control de acceso; **AI Act de la UE** en lo que afecta al analista (verificar calendario vigente de obligaciones); sesgos en datos y métricas; ética de la experimentación.

**Parte VI — IA para analistas (estado del arte)**

- **M25 LLMs como copiloto del analista**: cómo funciona un LLM lo justo para usarlo bien (tokens, contexto, alucinaciones, no-determinismo); _prompting_ para análisis (dar esquema, definiciones y ejemplos); análisis con intérpretes de código (ChatGPT, Claude, Gemini); IA en notebooks (Jupyter AI, marimo) y en hojas de cálculo; agentes de código (Claude Code, Codex, Cursor…) para repos de analítica y dbt; **protocolo de verificación**: recalcular cifras clave, comprobar SQL generado, tests, trazabilidad; reproducibilidad; qué datos NO pegar en un chat. **volatility: high**.
- **M26 Text-to-SQL y analítica conversacional**: cómo funciona (_schema linking_, recuperación de contexto, ejemplos, autocorrección); por qué falla (joins ambiguos, grano, definiciones de negocio); la capa semántica como solución; productos (Snowflake Cortex Analyst, Databricks Genie, Copilot en Power BI, Tableau Concierge, ThoughtSpot); benchmarks (Spider 2.0, BIRD) y sus problemas de anotación; cómo evaluar un sistema NL→SQL con un _golden set_ de preguntas y resultados esperados. **volatility: high**.
- **M27 Analítica agéntica y MCP**: qué es un agente; _workflows_ vs agentes; **Model Context Protocol** (host/cliente/servidor, tools/resources) y servidores MCP de datos (dbt, Snowflake, BigQuery, DuckDB/MotherDuck…); diseño seguro (roles de solo lectura, límites de coste, PII, inyección de instrucciones a través de los datos, aprobación humana); evaluar las conclusiones de un agente; por qué los proyectos agénticos sin capa semántica fracasan. **volatility: high**.
- **M28 LLMs para datos no estructurados**: clasificación, extracción y análisis de sentimiento de texto (tickets, reseñas, encuestas) con salidas estructuradas; funciones de IA dentro del SQL del warehouse (verificar nombres vigentes: p. ej. funciones `AI_*` de Snowflake, `AI.GENERATE` de BigQuery, `ai_query` de Databricks); embeddings para agrupar texto; evaluación contra etiquetas humanas (precisión, recall, matriz de confusión, acuerdo inter-anotador); coste y muestreo. **volatility: high**.

**Parte VII — Carrera profesional**

- **M29 Portfolio, carrera y entrevistas**: qué buscan las empresas por nivel (junior/mid/senior); portfolio que convence (3 casos con pregunta de negocio, método, resultado y recomendación); GitHub y write-ups; entrevistas de SQL (cronometradas), de producto/métricas, de estadística, take-homes y conductuales (STAR); certificaciones útiles y su valor real (PL-300, DP-600, Tableau, dbt, Google Data Analytics — verificar vigencia); negociación y primeros 90 días en un equipo de datos.

### 7.2 Tests tipo test

- **Por lección**: 6–10 preguntas (mezcla de tipos y dificultades) al final de la lección.
- **Por módulo**: agrega todas las preguntas del módulo; aprobado ≥ 80 %.
- **Modo examen**: elige partes/módulos, nº de preguntas (20/40/60) y temporizador opcional; informe por módulo con enlaces a repasar.
- **Repaso espaciado**: toda pregunta fallada entra en la caja 1 de Leitner; intervalos 1, 2, 4, 8, 16 días.
- Tipos específicos del oficio: `sql-output` (¿qué devuelve esta consulta sobre esta tabla?), `formula-output` (fórmula Excel), `numeric` (cálculos estadísticos con tolerancia), `chart-critique` (¿qué está mal en este gráfico?).
- Cada explicación justifica la correcta **y** las incorrectas, y enlaza a la sección de la lección.
- Objetivo de volumen: **≥ 800 preguntas** en total.

### 7.3 El dataset "Lumen" (corazón de la práctica)

**Lumen** es una empresa ficticia española de retail omnicanal (tienda online + app + 40 tiendas físicas) con un programa de suscripción "Lumen+". Totalmente ficticia y generada por `data-gen/generate.py` con **seed fija** (determinista; CI verifica checksums). Periodo: 2023-01-01 → 2026-06-30. Moneda EUR, zona horaria Europe/Madrid (con eventos registrados en UTC, a propósito).

**Tablas (capa `lumen/`, Parquet)** — tamaños orientativos:

- `customers` (~60k): alta, canal de adquisición, región/provincia, segmento, consentimiento de marketing.
- `products` (~2k) y `categories`: precio, coste, marca, jerarquía de categoría.
- `stores` (40): ciudad, tamaño, fecha de apertura.
- `orders` (~400k) y `order_items` (~1M): canal, dispositivo, descuento, envío, estado.
- `returns`, `shipments` (con fechas prometida/real), `inventory_snapshots` (semanal).
- `web_sessions` y `events` (muestra ~1,5M eventos): page_view, add_to_cart, checkout, purchase; versión de app.
- `marketing_spend` (diario por canal) y `campaigns`.
- `experiments`, `experiment_assignments`, `experiment_metrics`.
- `subscriptions` (Lumen+): altas, bajas, plan, MRR.
- `support_tickets` (~15k) con **texto libre en español** (para M28) y etiquetas humanas en una muestra.
- `calendar` (festivos nacionales y autonómicos, Black Friday, rebajas).

**Capa `lumen_raw/`** (CSV/JSON sucios) con problemas reales: duplicados, nulos, fechas en formatos mezclados, categorías inconsistentes (`"Madrid"`, `"madrid "`, `"MADRID"`), importes con coma decimal, IDs huérfanos, eventos duplicados por un bug de una versión de app.

**"Verdades plantadas"** (documentadas en `docs/DATASET.md`; la web no las revela salvo en las soluciones) para que labs y casos tengan respuestas verificables:

1. Estacionalidad semanal y anual + picos de Black Friday/Navidad/rebajas.
2. **Paradoja de Simpson** en conversión por dispositivo × región.
3. Un A/B test con **lift real** conocido en conversión y otro con **SRM** provocado por un bug de asignación.
4. Un experimento donde CUPED reduce la varianza de forma apreciable.
5. Un **cambio de precio** en una región en una fecha concreta (para DiD / control sintético).
6. Un **bug de tracking** (eventos duplicados en la app v4.2) que infla una métrica.
7. Retrasos de envío que **causan churn** en Lumen+ (efecto medible).
8. Una campaña con incrementalidad real menor que la atribuida por _last-click_.
9. Caída de ventas en marzo de 2026 explicada por una combinación de rotura de stock + cambio de mix (caso estrella).
10. Tickets de soporte con temas latentes (envío, devoluciones, app, pagos) para clasificación.

**`lumen_variant/`**: mismo esquema, otra seed y ~5 % del tamaño; los tests ocultos re-ejecutan la solución del alumno aquí para impedir respuestas "hardcodeadas".

**`extra/`**: datasets pequeños didácticos (Anscombe, Datasaurus, series temporales de ejemplo, etc.) con licencia compatible y fuente citada.

Página `/datos/`: historia de la empresa, ERD (Mermaid), diccionario de datos (generado desde el esquema), descargas, y advertencia de que es ficticio.

### 7.4 Laboratorios autocorregidos (SQL y Python en el navegador)

**Runtime SQL** (`src/lib/duckdb/worker.ts`)

- Carga DuckDB-WASM solo al abrir un lab SQL o el Playground (lazy, con indicador de progreso). Registra las tablas de `datasets` como vistas sobre los Parquet servidos (`read_parquet(url(...))`).
- Ejecuta la consulta del alumno con límite de filas mostradas (1.000) y timeout de 10 s (cancelar consulta; si no responde, `worker.terminate()` y recrear).
- Corrección: ejecuta `solution.sql` y la del alumno, y compara result sets con `resultCompare.ts` según `checks.yaml` (orden, nombres de columna, tolerancia de floats, subconjunto de columnas). Después repite contra `lumen_variant` si `hiddenOnVariant`. Mensajes didácticos: "Te sobran 12 filas: ¿has comprobado duplicados tras el JOIN?", "La columna 2 difiere en la fila 3: esperado 1.234,50, obtenido 1.250,00".
- Se permite cualquier dialecto que DuckDB acepte; las lecciones indican equivalencias en otros motores.

**Runtime Python** (`src/lib/pyodide/{worker.ts, runner.py}`)

- Pyodide 314.x en **module worker**; carga `pandas` y los `packages` del lab; monta `public/py/datakit` en el FS virtual; ejecuta el código del alumno y luego `test_lab.py` con un mini-runner que devuelve JSON `{name, passed, message, hidden}` por test. Captura stdout/stderr.
- Gráficos: si el código produce un objeto Altair, se serializa a Vega-Lite y se renderiza con `vega-embed`; matplotlib se renderiza a PNG.
- Timeout 20 s (Pyodide es más lento al cargar); carga lazy con indicador de progreso.
- **Atención a versiones**: Pyodide trae versiones concretas (p. ej. Polars puede ir por detrás de la última de PyPI). Los labs se escriben contra las versiones de Pyodide y el CI de pytest fija esas mismas versiones.

**UI común**: enunciado + pregunta de negocio (izquierda) | editor con autocompletado de esquema + botones _Ejecutar_, _Comprobar_, _Pista_, _Reiniciar_, _Ver solución_ (tras 3 intentos o confirmación) | resultado (tabla/gráfico/consola) y tests. Autoguardado en el progreso.

**`datakit` (librería didáctica Python)** — determinista, sin red:

- `datakit.data`: carga de tablas Lumen (Parquet → pandas/Polars) y de `extra/`.
- `datakit.stats`: helpers mínimos para que los labs se centren en el concepto (no sustituyen a scipy/statsmodels).
- `datakit.llm.MockLLM`: LLM simulado con respuestas guionizadas para labs de text-to-SQL/agentes/clasificación (sin red, sin API keys).
- `datakit.testing`: aserciones con mensajes en español (comparar DataFrames con tolerancia, comprobar columnas, tipos, rangos).

**Lista de labs (≥ 70)** — dificultad 1–3. Cada lab parte de una pregunta de negocio de Lumen.

SQL (DuckDB-WASM) — ≥ 40:

1. Primeras consultas: ventas por canal y mes.
2. Filtros con fechas y zonas horarias (UTC → Europe/Madrid).
3. `NULL` en agregaciones y `COALESCE`.
4. Joins: detectar y corregir un _fan-out_ que duplica ingresos.
5. Anti-join: clientes registrados que nunca compraron.
6. `CASE` para segmentar clientes por gasto.
7. Ticket medio, mediana y percentiles por región.
8. Top-N por grupo con `ROW_NUMBER` + `QUALIFY`.
9. Crecimiento mes a mes con `LAG`.
10. Acumulados y medias móviles de 7 días (marcos `ROWS` vs `RANGE`).
11. _Date spine_: días sin ventas también cuentan.
12. Funnel de conversión desde `events`.
13. Sesionización (30 min de inactividad).
14. _Gaps & islands_: rachas de compra.
15. Tabla de cohortes de retención mensual.
16. _Growth accounting_ de clientes (nuevos/retenidos/resucitados/perdidos).
17. `ROLLUP`/`GROUPING SETS` para totales y subtotales.
18. `PIVOT` de ventas por categoría y trimestre.
19. Deduplicación de eventos (bug app v4.2).
20. Limpieza en SQL de `lumen_raw.customers` (trim, mayúsculas, mapeo de regiones).
21. `ASOF JOIN`: precio vigente en el momento del pedido.
22. Slowly Changing Dimension tipo 2: reconstruir el segmento histórico del cliente.
23. Construir una tabla de hechos con el grano correcto.
24. Métricas de suscripción: MRR, altas, bajas, NRR.
25. Análisis de devoluciones por categoría y motivo.
26. Plazos de entrega vs prometido y su relación con la recompra.
27. RFM en SQL.
28. Paradoja de Simpson: conversión agregada vs por segmento.
29. SRM check de un experimento (χ² calculado en SQL).
30. Resultado de un A/B test: conversión, diferencia e IC por aproximación normal.
31. Atribución _last-click_ vs _first-click_ vs lineal.
32. ROAS por canal y semana con gasto diario.
33. Análisis de varianza precio/volumen/mix.
34. Rotación de inventario y roturas de stock.
35. JSON: extraer propiedades de eventos.
36. CTE recursiva: jerarquía de categorías.
37. Consulta optimizada: reescribir para filtrar antes de unir (comparar `EXPLAIN ANALYZE`).
38. Definir una métrica sin ambigüedad: "cliente activo" con ventana de 90 días.
39. Validar un SQL generado por IA (`MockLLM`): encontrar y corregir sus 3 errores.
40. Mini capa semántica: vistas de métricas reutilizables y consulta sobre ellas.
41. Investigación de una caída de métrica (prepara el caso estrella).

Python (Pyodide) — ≥ 30: 42. pandas 3: carga, tipos (`str`), selección y Copy-on-Write. 43. Limpieza completa de `lumen_raw` con pandas (fechas mixtas, coma decimal, categorías). 44. Lo mismo en **Polars** con _lazy_ + expresiones; comparar código. 45. DuckDB desde Python sobre DataFrames. 46. EDA reproducible: perfil de una tabla y 5 hallazgos. 47. Visualización con Altair: el gráfico correcto para 4 preguntas distintas. 48. Arreglar un gráfico engañoso (eje truncado, doble eje, color). 49. Datasaurus/Anscombe: por qué hay que graficar. 50. Simulación del TLC y de intervalos de confianza (cobertura real). 51. Bootstrap del ticket mediano. 52. Potencia y MDE: cuántos usuarios necesita un experimento. 53. Simulación del _peeking_: falsos positivos al mirar cada día. 54. Análisis A/B completo con statsmodels (proporciones, IC, SRM). 55. CUPED: reducción de varianza con datos pre-experimento. 56. Test secuencial (mSPRT simplificado) vs test fijo. 57. Comparaciones múltiples: Bonferroni vs Benjamini-Hochberg. 58. Regresión lineal interpretada para negocio (elasticidad precio). 59. Regresión logística: probabilidad de baja en Lumen+. 60. Diferencias en diferencias del cambio de precio regional. 61. Control sintético simplificado. 62. DAG y confusión: estimar un efecto con y sin ajustar. 63. Segmentación k-means + RFM y sus trampas (escalado, interpretación). 64. Descomposición STL de ventas diarias. 65. Forecast con ETS/ARIMA y _backtesting_ con origen móvil (MASE). 66. Detección de anomalías en métricas diarias. 67. CLV con BG/NBD simplificado. 68. Clasificación de tickets con `MockLLM` + evaluación contra etiquetas humanas (precisión/recall, matriz de confusión). 69. Evaluador de text-to-SQL: ejecutar SQL candidato y comparar resultados con un _golden set_. 70. Guardas de un "agente analista": bloquear SQL que no sea de solo lectura, limitar filas/coste, detectar PII. 71. Informe automatizado: de DataFrame a resumen ejecutivo con cifras verificadas (assert de que cada cifra del texto sale de los datos).

Cada lab: starter con firmas/estructura y comentarios, solución comentada, ≥ 4 tests/checks (≥ 1 oculto) y mensajes de error didácticos.

**SQL Playground** (`/practica/sql/`): consola libre sobre Lumen con explorador de esquema, ERD, ejemplos, historial (localStorage) y exportar resultado a CSV.

**Modo "LLM real" (opcional, Fase 7)**: _playground_ no evaluado donde el usuario pone su propia API key (solo en `localStorage`, con aviso claro) para probar text-to-SQL sobre Lumen y comparar con el resultado correcto. Verificar en la documentación oficial vigente cómo llamar a la API desde el navegador y qué modelos están disponibles. Nunca hay claves en el repo.

### 7.5 Hojas de cálculo (libros descargables)

`scripts/build-workbooks.py` genera con openpyxl ≥ 12 libros `.xlsx` a partir de Lumen, cada uno con hoja de instrucciones, datos, zona de trabajo y **hoja de autocomprobación** (fórmulas que marcan ✔/✘ comparando con valores esperados), más el libro de solución. Temas: limpieza con Power Query, `XLOOKUP`/`BUSCARX`, matrices dinámicas, `LET`/`LAMBDA`, `GROUPBY`/`PIVOTBY`, tablas dinámicas, modelo de datos, análisis de escenarios, previsión, dashboard en Excel, auditoría de un modelo con errores, uso guiado de Copilot/Agent Mode con verificación. Cada ficha (`/practica/hojas-de-calculo/<id>`) explica objetivos, pasos, nombres de funciones ES/EN y errores comunes.

### 7.6 Casos de análisis guiados

≥ 12 casos (`/practica/casos/`) que simulan el trabajo real: un email de un stakeholder, pasos con mini-editor SQL/Python o preguntas de razonamiento, respuestas numéricas autocorregidas, y al final un informe a redactar con rúbrica de autoevaluación + informe modelo. Ejemplos:

1. "Las ventas cayeron un 12 % en marzo: ¿por qué?" (caso estrella, verdad plantada 9).
2. "¿Lanzamos el nuevo checkout?" (A/B con lift real).
3. "El experimento salió espectacular" (SRM: no te fíes).
4. "¿Funcionó la subida de precios en Andalucía?" (DiD).
5. "Marketing quiere duplicar el presupuesto en el canal X" (atribución vs incrementalidad).
6. "¿Por qué se dan de baja de Lumen+?" (churn y envíos).
7. "Las conversiones en app se han disparado" (bug de tracking).
8. "Necesitamos el forecast del Q4" (estacionalidad, festivos, intervalos).
9. "Define 'cliente activo' para el consejo" (definición de métricas).
10. "¿Qué dicen los tickets de soporte?" (LLM + evaluación).
11. "El agente de IA dice que la región Norte va fatal" (verificar conclusiones de IA).
12. "Construye el KPI tree de la empresa" (pensamiento de negocio).

### 7.7 Proyectos de portfolio (en local, con herramientas reales)

Carpeta `projects/<id>/` con `README.md` (objetivos, arquitectura, pasos, criterios de evaluación, extensiones, cómo presentarlo en el portfolio), `pyproject.toml` (uv) cuando aplique, código inicial con TODOs y `.env.example` si hace falta. Página en `/proyectos/<id>/`.

1. **Pipeline analítico end-to-end**: dlt → DuckDB (o MotherDuck) → **dbt** (staging/marts, tests, docs) + **MetricFlow** → informe con **Evidence** desplegado en GitHub Pages.
2. **Dashboard en Power BI** como proyecto **PBIP en Git** (TMDL/PBIR): modelo estrella, medidas DAX, inteligencia de tiempo, RLS, diseño revisado con checklist. Alternativa: Tableau Public o Looker Studio.
3. **Análisis de experimento** completo en un notebook **marimo** (potencia, SRM, CUPED, análisis secuencial, recomendación) publicado como HTML.
4. **Estudio causal**: impacto del cambio de precio con DiD + control sintético + análisis de robustez.
5. **Forecasting de demanda**: statsforecast + un modelo fundacional de series temporales, _backtesting_ y comparación honesta.
6. **Asistente analítico con IA**: servidor **MCP** propio (SDK oficial de Python) sobre DuckDB + capa semántica, con usuario de solo lectura, _golden set_ de 30 preguntas NL con resultados esperados y harness de evaluación.
7. **Analítica de texto**: clasificar tickets con un LLM real, evaluar contra etiquetas, análisis de coste y error.
8. **Portfolio**: web personal con 3 casos (pregunta → método → resultado → recomendación) usando las piezas anteriores.

Las versiones de librerías y APIs de los proyectos deben verificarse contra la documentación oficial vigente en el momento de implementarlos.

### 7.8 Zona de entrevistas

- `questions.yaml`: **≥ 150 preguntas** (SQL, estadística, experimentación, producto/métricas, BI/DAX, Python, IA para análisis, conductuales) con respuesta modelo en ES y EN, etiquetadas por tema y nivel (junior/mid/senior). Vista con "mostrar respuesta" y modo flashcard.
- **SQL cronometrado**: 25 problemas tipo entrevista sobre Lumen (reutiliza el motor de labs) con temporizador y nivel.
- Casos de entrevista (≥ 8): investigar una caída de métrica; diseñar métricas para una feature nueva; diseñar un A/B test; evaluar un lanzamiento sin experimento; definir el dashboard ejecutivo; priorizar peticiones contradictorias; take-home simulado con rúbrica; "¿cómo usarías IA en este análisis y cómo lo validarías?". Cada caso: preguntas de aclaración, marco de respuesta, respuesta modelo, errores típicos, "qué diría un senior".
- Cheat sheets imprimibles: SQL (ventanas, fechas, dialectos), estadística/A/B, DAX, Excel ES/EN, visualización, checklist de investigación de métricas.

### 7.9 Radar del analista

Página `/radar/` estilo _technology radar_ con anillos **Adoptar / Probar / Evaluar / Evitar** y categorías (motores SQL, herramientas Python, BI, ingeniería analítica, IA analítica, técnicas). Cada entrada lleva `asOf`, resumen, fuentes y lecciones relacionadas. Es el lugar donde se refleja explícitamente "lo último" y se revisa cada trimestre (workflow de frescura).

---

## 8. Fuentes de información (fiabilidad y actualidad)

Regla general: **fuentes primarias primero**. Toda afirmación técnica no trivial debe poder rastrearse a una fuente de nivel 1 o 2. Las de nivel 3 están prohibidas como fuente única.

**Nivel 1 — Primarias**

- **Libros de referencia**: Kohavi, Tang & Xu — _Trustworthy Online Controlled Experiments_; Hernán & Robins — _Causal Inference: What If_; Huntington-Klein — _The Effect_; Cunningham — _Causal Inference: The Mixtape_; Hyndman & Athanasopoulos — _Forecasting: Principles and Practice_ (3.ª ed. y la edición en Python); Kimball & Ross — _The Data Warehouse Toolkit_; McKinney — _Python for Data Analysis_ (3.ª ed.); Wickham — "Tidy Data" (JSS 2014) y _R for Data Science_ (2.ª ed., conceptos); Tufte; Cairo — _How Charts Lie_; Munzner — _Visualization Analysis & Design_; Wilkinson — _The Grammar of Graphics_; Knaflic — _Storytelling with Data_; Few — _Information Dashboard Design_; Minto — _The Pyramid Principle_; Bruce, Bruce & Gedeck — _Practical Statistics for Data Scientists_; McElreath — _Statistical Rethinking_; Reis & Housley — _Fundamentals of Data Engineering_; Huyen — _AI Engineering_.
- **Papers**: Cleveland & McGill (1984); Deng et al. (2013, CUPED); Johari et al. ("Always Valid Inference", arXiv 1512.04922); Fabijan et al. y Kohavi et al. sobre SRM y pitfalls de experimentación; declaración de la ASA sobre p-valores (2016); Benjamini & Hochberg (1995); Abadie et al. (control sintético); Callaway & Sant'Anna (2021); Brodersen et al. (2015, CausalImpact); Fader, Hardie & Lee (2005, BG/NBD); Spider 2.0 (Lei et al., ICLR 2025), BIRD, y los estudios de 2026 sobre errores de anotación en benchmarks text-to-SQL; papers de TimesFM y Chronos.
- **Documentación oficial**: DuckDB, PostgreSQL, BigQuery (incl. sintaxis pipe), Snowflake, Databricks, pandas (notas de la 3.0), Polars (blog y guía de migración a 2.0), Apache Arrow, scikit-learn, statsmodels, SciPy, Altair/Vega-Lite, Pyodide, DuckDB-WASM, Microsoft Learn (Excel, Power Query, Power BI, DAX, Fabric, PBIP/TMDL/PBIR, Copilot), Google Sheets, Tableau, Looker, dbt (Fusion, Core, MetricFlow, Semantic Layer, MCP), Open Semantic Interchange, Cube, Model Context Protocol (spec), GrowthBook/Statsig/Eppo, Google Meridian, Meta Robyn, PyMC-Marketing, Nixtla, marimo, Jupyter AI, Evidence, Great Expectations, pandera, Soda, dlt, Airflow, Dagster, Iceberg, Delta Lake; RGPD/AEPD y AI Act (EUR-Lex / Comisión Europea).
- **Plataformas de certificación**: Microsoft Learn (PL-300, DP-600), Tableau, dbt, Google.

**Nivel 2 — Expertos reconocidos y blogs técnicos de empresas**

- SQLBI (Marco Russo & Alberto Ferrari) para DAX y modelado; Ron Kohavi (artículos y cursos); Evan Miller (tamaños de muestra, _peeking_); blogs de experimentación de Netflix, Spotify, Airbnb, Booking, Microsoft ExP, Uber; Benn Stancil; Tristan Handy (dbt Labs); Randy Au; Cassie Kozyrkov; Hamel Husain y Shreya Shankar (evaluación de sistemas con LLM); Simon Willison (seguridad LLM, prompt injection); Hadley Wickham; Andrew Gelman; Rob Hyndman (blog); blogs de MotherDuck, DuckDB Labs, Hex, Mode, Amplitude, PostHog, Snowflake, Databricks; Datawrapper Academy y Flowing Data (visualización); Gartner/Forrester solo para tendencias de mercado y citados con fecha.

**Nivel 3 — No usar como fuente única**: blogs SEO, listados "Top 10 herramientas 2026", Medium/LinkedIn sin autoría experta, contenido generado sin referencias, cifras de salarios sin fuente identificable.

**Snapshot del estado del arte verificado al crear este plan (2026-10-07)** — re-verificar siempre al redactar:

- **Pyodide 314.x** (junio 2026): versionado alineado con Python (314 = Python 3.14); exige _module workers_; paquetes publicables en PyPI (PEP 783). La versión estable 314.0.7 incluye pandas 3.0.2, Polars 1.33.1, DuckDB 1.5.1, PyArrow 22, NumPy 2.4, SciPy 1.18, statsmodels 0.14.6, scikit-learn 1.8, matplotlib 3.10, Altair 6 y networkx.
- **pandas 3.0** (enero 2026): dtype `str` por defecto y Copy-on-Write siempre activo.
- **Polars**: línea 1.4x en 2026; **Polars 2.0** en _release candidate_ (septiembre 2026) con el motor _streaming_ por defecto y API más estricta. Comprobar si ya es estable.
- **DuckDB** 1.5.x; DuckDB-WASM con publicación continua.
- **dbt**: motor Fusion (compilador SQL real); en junio de 2026 el runtime de Fusion se publicó como **dbt Core v2.0 alpha**; **MetricFlow** open source (Apache 2.0); **OSI** (Open Semantic Interchange) publicó su especificación v1.0 a comienzos de 2026.
- **Power BI**: formato **PBIR** por defecto desde enero de 2026; vista **TMDL** disponible; Copilot ampliado; integración con Fabric.
- **Excel**: **Agent Mode** de Copilot GA (web dic. 2025, Windows/Mac ene. 2026) y **Plan Mode** (mayo 2026); Copilot con Python; Claude for Excel como alternativa.
- **Tableau Next** sobre Salesforce Agentforce 360; agente Concierge GA en la versión 2026.1.
- **Text-to-SQL**: Spider 2.0 como benchmark de referencia empresarial; estudios de 2026 reportan tasas altas de errores de anotación en BIRD y Spider 2.0-Snow, lo que cuestiona los leaderboards.
- **Capa semántica + IA**: consenso de la industria en que la analítica agéntica necesita métricas gobernadas (Gartner, feb. 2026, citado por terceros — localizar la fuente primaria antes de citarlo).
- **Notebooks**: marimo (reactivo, en crecimiento) y Jupyter AI 3.x (abril 2026, integra agentes externos vía ACP y MCP).
- **Certificaciones Microsoft**: PL-300 (Power BI) y DP-600 (Fabric Analytics Engineer); DP-500 retirada.
- **Web**: Astro 7.x (7.3.1 en septiembre 2026); Tailwind CSS 4.x.

**Procedimiento al redactar cada lección**

1. Consultar con búsqueda web las fuentes de nivel 1–2 del tema **en el momento de redactar**.
2. Para contenido `volatility: high` (herramientas, versiones, funciones de IA, nombres de productos, benchmarks, precios, normativa): verificar en la fuente oficial, indicar la fecha ("a fecha de AAAA-MM") en un callout `<Snapshot>`, y nunca inventar cifras.
3. Separar conceptos estables (_evergreen_: estadística, SQL, diseño de métricas) de la foto del momento (_snapshot_: productos y versiones).
4. Registrar todas las fuentes en el frontmatter y en `docs/SOURCES.md`; poner `lastReviewed` a la fecha real.
5. Si una afirmación no se puede verificar, eliminarla o marcarla explícitamente como opinión/tendencia citando quién la sostiene.
6. Al actualizar una lección, añadir una entrada en `src/content/changelog/` y, si procede, actualizar el Radar.

---

## 9. Guía de contenido (resumen; detallar en `docs/CONTENT_GUIDELINES.md`)

Estructura de cada lección:

1. **Objetivos** (del frontmatter).
2. **Contexto de negocio** (`<BusinessContext>`): la pregunta real de Lumen que motiva el tema.
3. **Intuición**: el problema que resuelve, con un ejemplo concreto.
4. **Cómo funciona**: explicación técnica, fórmulas (KaTeX), gráfico Vega-Lite o diagrama.
5. **En la práctica**: snippet SQL/Python/Excel/DAX de lectura (con `<DialectTabs>` o `<ExcelFn>` cuando aplique) y enlace al lab o caso.
6. **Trade-offs y cuándo usarlo / cuándo no.**
7. **Errores comunes** (los que cometen analistas reales).
8. **Con IA**: cómo acelerar esta tarea con un LLM/agente y cómo verificar el resultado (cuando aplique).
9. **En una entrevista**: 2–3 preguntas típicas con pistas de respuesta.
10. **Ideas clave** (`<KeyTakeaways>`).
11. **Fuentes** (renderizadas desde el frontmatter).
12. **Mini-quiz** (renderizado desde el YAML).

Estilo: claro, directo, sin relleno; números con formato español (1.234,56 €) en prosa y formato de máquina en código; ejemplos con Lumen; términos en inglés en cursiva la primera vez; sin emojis decorativos. Gráficos: título que expresa la conclusión, ejes etiquetados con unidades, paleta accesible, alt text obligatorio.

---

## 10. Widgets interactivos de teoría

- **DistributionExplorer** (M02): cambiar parámetros y ver media/mediana/percentiles moverse; colas pesadas.
- **CLTSimulator** (M02/M13): muestras repetidas, distribución muestral e IC con su cobertura.
- **JoinVisualizer** (M04): dos tablas pequeñas, tipo de join y filas resultantes (con _fan-out_ resaltado).
- **WindowFrameVisualizer** (M05): ver qué filas entran en `ROWS`/`RANGE` para cada fila.
- **DialectTranslator** (M05): traducir SQL entre dialectos con **sqlglot** en Pyodide (carga lazy).
- **ChartChooser** (M10): pregunta → tipo de gráfico recomendado con ejemplo.
- **PaletteChecker** (M10): simula daltonismo y contraste sobre una paleta.
- **DaxFilterContext** (M11): ver cómo `CALCULATE` modifica el contexto de filtro en un modelo estrella pequeño.
- **PValueSimulator** (M13/M14): el _peeking_ inflando falsos positivos en tiempo real.
- **PowerCalculator** (M14): MDE, potencia, tamaño de muestra y duración del experimento.
- **CupedDemo** (M14): correlación pre/post y reducción de varianza.
- **SimpsonExplorer** (M09): agregar/desagregar y ver invertirse la conclusión.
- **DagPlayground** (M15): dibujar un DAG simple y ver qué variables ajustar.
- **DiDVisualizer** (M15): tendencias paralelas, tratamiento y efecto estimado.
- **CohortHeatmap** (M18): retención por cohorte con filtros.
- **ForecastBacktest** (M17): origen móvil y error por horizonte.
- **TextToSqlInspector** (M26): pregunta → SQL candidato (guionizado) → resultado vs esperado, mostrando dónde falla.

Todos con `client:visible`, accesibles por teclado y respetando `prefers-reduced-motion`.

---

## 11. Calidad, accesibilidad y rendimiento

- Lighthouse ≥ 90 en Performance/Accessibility/Best Practices/SEO en páginas de teoría.
- DuckDB-WASM y Pyodide nunca se cargan fuera de labs, casos, Playground o widgets que los requieran. Mermaid, Vega y widgets en `client:visible`.
- Accesibilidad: navegación por teclado en quizzes, editores y tablas de resultados; `aria-live` en resultados; contraste AA en ambos temas; tablas con cabeceras semánticas; alt text en gráficos.
- SEO: títulos, meta description, Open Graph, `sitemap` (`@astrojs/sitemap`).
- Validación de contenido en CI: todo quiz apunta a una lección existente; ids únicos; anclas `ref` existen; cada lección ≥ 2 fuentes; cada lab pasa con la solución y falla con el starter (en dataset principal y en `lumen_variant`); cada caso tiene respuestas coherentes con el dataset (test que recalcula las respuestas numéricas); dataset determinista (checksums).

---

## 12. Fases de implementación

| Fase                             | Entregable                                                                                                                                                     | Criterio de "hecho"                                                                                       |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| **F0 Setup y despliegue**        | Proyecto Astro + TS + Tailwind + lint + tests vacíos + workflows; hello world desplegado en Pages                                                              | URL pública funciona con `base` correcto; CI en verde.                                                    |
| **F1 Dataset Lumen**             | `data-gen/generate.py` con todas las tablas, capa raw, variante, verdades plantadas, `docs/DATASET.md`, página `/datos/` con ERD y diccionario                 | Generación determinista (checksums); tests que comprueban cada verdad plantada; tamaño dentro de límites. |
| **F2 Núcleo de teoría**          | Layouts, header, sidebar, TOC, tema oscuro, componentes de contenido, Vega-Lite, búsqueda Pagefind, colecciones Zod, progreso; M04 completo como módulo modelo | Navegación completa; lecciones modelo cumplen §9.                                                         |
| **F3 Motor de tests**            | Quiz por lección y módulo (incl. tipos `numeric`, `sql-output`, `formula-output`, `chart-critique`), modo examen, Leitner, panel de progreso                   | Unit tests de `quiz.ts`/`srs.ts`; e2e de un quiz.                                                         |
| **F4 Laboratorios y Playground** | Worker DuckDB-WASM + `resultCompare.ts`, worker Pyodide + `datakit`, UI de lab, SQL Playground; labs 1, 8, 15, 42, 54 de punta a punta; tests de labs en CI    | Un lab SQL y uno Python se resuelven en el sitio desplegado; pytest en verde.                             |
| **F5 Casos guiados**             | Motor de casos + caso estrella (#1) completo                                                                                                                   | Caso resoluble de principio a fin en el sitio desplegado.                                                 |
| **— Pausa de revisión —**        | Resumen al usuario y URL desplegada                                                                                                                            | El usuario valida antes de generar contenido masivo.                                                      |
| **F6 Contenido Partes 0–II**     | M00–M12: lecciones, quizzes, labs SQL/Python asociados, libros Excel, widgets correspondientes                                                                 | Validación de contenido en verde.                                                                         |
| **F7 Contenido Partes III–IV**   | M13–M20: lecciones, quizzes, labs de estadística/experimentación/causalidad/forecasting/dominio, casos 2–8, widgets                                            | Ídem.                                                                                                     |
| **F8 Contenido Partes V–VI**     | M21–M28: lecciones, quizzes, labs de IA (con `MockLLM`), casos 9–12, Radar inicial, playground "LLM real" opcional                                             | Ídem.                                                                                                     |
| **F9 Profesional y extras**      | M29, zona de entrevistas (preguntas, SQL cronometrado, casos), cheat sheets, glosario, fuentes, proyectos en `projects/`, `/novedades/`                        | Ídem.                                                                                                     |
| **F10 Pulido**                   | Lighthouse, accesibilidad, workflow de frescura, README completo (cómo desarrollar, regenerar el dataset, añadir lecciones/labs/casos, desplegar)              | Checklist §11 cumplido.                                                                                   |

Hacer **commit al final de cada fase** (y commits intermedios lógicos) con mensajes claros. Trabajar en ramas por fase y fusionar a `main` cuando la fase esté en verde, para que el despliegue solo ocurra con contenido validado.
