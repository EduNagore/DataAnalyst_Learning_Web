# Data Analyst Academy

Curso gratuito y de código abierto, en español, para llegar a **data analyst de nivel senior**: SQL, hojas de cálculo, Python, estadística, experimentación, causalidad, visualización, BI, ingeniería analítica, capa semántica, IA aplicada al análisis y preparación de entrevistas.

Sitio 100 % estático ([Astro](https://astro.build/)), sin backend. Los laboratorios de SQL y Python se ejecutan y se corrigen **en el navegador** con DuckDB-WASM y Pyodide, sobre un dataset propio ("Lumen", una empresa de retail ficticia). Desplegado en GitHub Pages: <https://edunagore.github.io/DataAnalyst_Learning_Web/>.

La especificación completa — objetivos, stack, arquitectura, esquemas de contenido, temario de los 30 módulos, diseño del dataset, fuentes y fases de implementación — está en **[`PLAN.md`](PLAN.md)**. El estado de cada fase y los hechos verificados de cada módulo están en [`docs/PROGRESO.md`](docs/PROGRESO.md).

## Qué contiene

| Zona                              | Contenido                                                                                                                                             |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Teoría** (`/teoria/`)           | 30 módulos en 8 partes, con lecciones, widgets interactivos, fuentes y `Snapshot` fechados para lo volátil.                                           |
| **Práctica** (`/practica/`)       | Tests por lección y módulo, modo examen, repaso espaciado, más de 120 laboratorios SQL/Python, 12 casos guiados, libros de Excel y un SQL Playground. |
| **Proyectos** (`/proyectos/`)     | 8 proyectos de portfolio para hacer en local, con código inicial, pruebas y criterios de evaluación (`projects/`).                                    |
| **Entrevistas** (`/entrevistas/`) | 150 preguntas ES/EN con flashcards, 25 ejercicios de SQL cronometrados y 8 casos de entrevista.                                                       |
| **Referencia**                    | Radar del analista, cheat sheets imprimibles, glosario bilingüe, fuentes y novedades del curso.                                                       |

## Requisitos

- [Node.js 24 LTS](https://nodejs.org/) (ver `.nvmrc`) con `corepack enable` para `pnpm`.
- [pnpm](https://pnpm.io/) (vía corepack).
- [uv](https://docs.astral.sh/uv/) para la parte Python (generación del dataset, tests de laboratorios).
- [Python 3.13+](https://www.python.org/) — `uv` puede gestionar la versión exacta por ti.

## Desarrollo

```bash
pnpm install
pnpm dev          # servidor de desarrollo en http://localhost:4321/DataAnalyst_Learning_Web/
```

El sitio se despliega bajo el sub-path `/DataAnalyst_Learning_Web/` (ver `astro.config.mjs`). **Todas** las rutas y assets internos deben construirse con el helper `url()` de [`src/lib/url.ts`](src/lib/url.ts) — nunca enlaces absolutos `"/..."` escritos a mano.

### Scripts

| Comando                           | Qué hace                                                                                                                             |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `pnpm dev`                        | Servidor de desarrollo con recarga en caliente.                                                                                      |
| `pnpm build`                      | Build estático de producción en `dist/` (incluye el índice de búsqueda).                                                             |
| `pnpm preview`                    | Sirve el build de `dist/` localmente (lo que verá GitHub Pages).                                                                     |
| `pnpm check`                      | Typecheck de Astro/TypeScript (`astro check`).                                                                                       |
| `pnpm lint` / `pnpm lint:fix`     | ESLint.                                                                                                                              |
| `pnpm format` / `pnpm format:fix` | Prettier.                                                                                                                            |
| `pnpm test` / `pnpm test:watch`   | Tests unitarios (Vitest) de `src/lib/`.                                                                                              |
| `pnpm e2e`                        | Tests de extremo a extremo (Playwright): navegación, quizzes, labs en el navegador, casos, accesibilidad (axe, tema claro y oscuro). |
| `pnpm validate-content`           | Integridad referencial del contenido (quiz↔lección, ids únicos, anclas...).                                                          |
| `pnpm check-freshness`            | Lista lecciones/entradas del Radar caducadas.                                                                                        |

### Parte Python (dataset y laboratorios)

```bash
uv sync
uv run pytest       # tests de labs SQL/Python y de casos (tests/labs/)
uv run ruff check . # lint de los scripts Python
```

Las versiones de pandas/Polars/DuckDB/etc. en `pyproject.toml` están alineadas a propósito con las que trae la versión de **Pyodide** fijada en el worker del navegador (ver `PLAN.md` §8) — si se actualiza Pyodide, hay que revisar y alinear ambas.

### Regenerar el dataset Lumen

El generador determinista vive en `data-gen/` (configuración en `data-gen/config.yaml`, contrato de columnas en `data-gen/lumen/schema_doc.py`). La misma semilla produce siempre los mismos ficheros (`data-gen/checksums.json`). Las tablas Parquet se publican en `public/data/` (límite del sitio: ≤ 60 MB). La documentación del dataset, sus «verdades plantadas» y cómo usarlas está en [`docs/DATASET.md`](docs/DATASET.md).

## Estructura del repositorio

```
src/
├─ content.config.ts     # colecciones de contenido + esquemas Zod
├─ content/
│  ├─ modules/ lessons/ quizzes/   # teoría (MDX) y tests (YAML)
│  ├─ labs/ cases/ workbooks/      # práctica: labs, casos guiados (con .verify.yaml), libros Excel
│  ├─ projects/ interview/         # proyectos de portfolio y zona de entrevistas
│  ├─ radar/ glossary/ cheatsheets/ changelog/
├─ components/            # content, quiz, lab, case, interview, layout, progress
├─ layouts/ pages/ lib/ styles/
public/
├─ data/                  # Lumen (Parquet), variante, versión «sucia» y datos externos
└─ py/                    # runner de Pyodide y paquete `datakit` (también lo usa pytest)
data-gen/                  # generador determinista del dataset
projects/                  # código inicial de los 8 proyectos de portfolio
docs/                      # progreso, decisiones, guía de contenido, fuentes, dataset
scripts/                   # validate-content, check-freshness, usage-guard, build de libros de Excel
tests/                     # unit (Vitest), e2e (Playwright), labs (pytest)
.github/workflows/         # ci.yml, deploy.yml, content-freshness.yml
```

## Cómo añadir contenido

Lee primero [`docs/CONTENT_GUIDELINES.md`](docs/CONTENT_GUIDELINES.md) (estructura obligatoria, estilo, procedimiento de fuentes) y [`docs/DATASET.md`](docs/DATASET.md). Resumen de los pasos y de lo que valida el CI:

- **Lección:** `src/content/lessons/<módulo>/<NN-slug>.mdx` con frontmatter completo (objetivos, fuentes ≥ 2, `lastReviewed`, `volatility`). Lo volátil (versiones, productos, precios, normativa) se verifica en la fuente oficial y se fecha en un `<Snapshot date="AAAA-MM">`. Cada lección tiene su quiz en `src/content/quizzes/<módulo>/<mismo-slug>.yaml`; las anclas `ref` deben existir como encabezado `###`.
- **Laboratorio SQL:** `src/content/labs/<id>/{index.mdx,starter.sql,solution.sql,checks.yaml}`. El CI comprueba que la solución pasa, que el starter **no** pasa y que, con `hiddenOnVariant`, la solución da un resultado distinto en la variante del dataset.
- **Laboratorio Python:** `src/content/labs/<id>/{index.mdx,starter.py,solution.py,test_lab.py}` con al menos un test oculto (`test_hidden_*`). Se ejecuta con el mismo `runner` en CPython (pytest) y en Pyodide (Playwright).
- **Caso guiado:** `src/content/cases/<id>.mdx` + `<id>.verify.yaml` con las consultas que recalculan las respuestas numéricas (las ejecuta `tests/labs/test_cases.py`).
- **Radar, glosario, cheat sheets, novedades:** entradas en `src/content/radar/entries.yaml`, `glossary/terms.yaml`, `cheatsheets/*.mdx` y `changelog/*.md`. Al actualizar una lección, añade una entrada de novedades y, si procede, actualiza el Radar.
- Antes de abrir un PR: `pnpm lint && pnpm format && pnpm test && pnpm validate-content && pnpm build`, y `uv run pytest` si tocaste labs o casos.

## Despliegue

Cada push a `main` ejecuta `deploy.yml` (build estático y `actions/deploy-pages`); en _Settings → Pages_ la fuente debe ser **GitHub Actions**. `ci.yml` valida el contenido, ejecuta los tests y construye el sitio. `content-freshness.yml` (mensual) revisa los enlaces rotos con `lychee` y abre un issue con el contenido caducado (`scripts/check-freshness.mjs`).

## Calidad

Objetivos de calidad (ver `PLAN.md` §11): Lighthouse ≥ 90 en las cuatro categorías, contraste AA en ambos temas, navegación por teclado, sin desbordamiento horizontal en móvil y DuckDB-WASM/Pyodide cargados solo donde se necesitan. Comprobados en octubre de 2026 en las páginas principales (≥ 96 en las cuatro categorías de Lighthouse; 28 comprobaciones de accesibilidad con axe en claro y oscuro dentro de `pnpm e2e`).

## Licencia

**Pendiente de decisión del titular del repositorio.** Propuesta: MIT para el código y CC BY 4.0 para el contenido del curso (textos, ejercicios y dataset sintético «Lumen», que es íntegramente ficticio). Hasta que se añada un fichero `LICENSE`, todos los derechos están reservados por defecto. Las marcas y productos citados pertenecen a sus propietarios; las fuentes enlazadas conservan su propia licencia.
